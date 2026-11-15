"""Scorecard from saved episode rows (wiki/evaluation.md): per-room success, tool-call validity, traps, steps, latency,
room-4 lock across counterfactual twins (pairwise dependency exploitation), and failure attribution at the lock."""
import itertools, json, random, re
from collections import defaultdict
from .episodes import ROOT

_WORLD = {}


def world(path):
    if path not in _WORLD:
        _WORLD[path] = json.loads((ROOT / path).read_text())
    return _WORLD[path]


def family(path):
    return path.split("/family-")[1].split("/")[0]


def boot_ci(groups, stat, n=1000, seed=0):
    """Bootstrap over families (cluster bootstrap). groups: {family: [rows]}; stat(list_of_rows) -> float."""
    rng = random.Random(seed); keys = sorted(groups); vals = []
    for _ in range(n):
        sample = [r for k in (rng.choice(keys) for _ in keys) for r in groups[k]]
        vals.append(stat(sample))
    vals.sort()
    return [round(vals[int(.025 * n)], 3), round(vals[int(.975 * n) - 1], 3)]


def basic(rows):
    n = len(rows); steps = sum(r["steps"] for r in rows)
    return {"episodes": n, "success_rate": round(sum(r["success"] for r in rows) / n, 3) if n else None,
            "valid_call_rate": round(1 - sum(r["invalid"] for r in rows) / steps, 3) if steps else None,
            "trap_rate": round(sum(r["trap_used"] for r in rows) / n, 3) if n else None,
            "mean_steps": round(steps / n, 2) if n else None,
            "sec_per_step": round(sum(r.get("seconds", 0) for r in rows) / steps, 2) if steps else None}


def lock_ok(r):
    return bool(r["unlock_attempted"] and not r["lock_failed"])


def room4_scorecard(rows):
    fam = defaultdict(list)
    for r in rows:
        fam[family(r["world"])].append(r)
    def lock_rate(rs): return sum(lock_ok(r) for r in rs) / len(rs) if rs else 0
    def dse(rs):
        by = defaultdict(list)
        for r in rs: by[family(r["world"])].append(lock_ok(r))
        per = [sum(a and b for a, b in itertools.combinations(v, 2)) / max(1, len(list(itertools.combinations(v, 2))))
               for v in by.values() if len(v) >= 2]
        return sum(per) / len(per) if per else 0
    out = basic(rows)
    out.update(lock_success=round(lock_rate(rows), 3), lock_ci95=boot_ci(fam, lock_rate),
               pairwise_dse=round(dse(rows), 3), pairwise_dse_ci95=boot_ci(fam, dse),
               room4_clear=out.pop("success_rate"), families=len(fam),
               references={"oracle_lock": 1.0, "memoryless_lock_ceiling": 0.25, "memoryless_pairwise_dse": 0.0},
               note="checkpoint episodes start at room 4 with the teacher-written (oracle) notebook")
    return out


PHASE = re.compile(r'phase"?\s*[=:]\s*(-?\d)', re.I)
SIGMA = re.compile(r'(?:sigma|registry[_ ]?bit|bit)"?\s*[=:]\s*(\d)', re.I)


def attribution(r):
    """End-to-end (model-written notebook). Exact checks only; ambiguous -> unknown."""
    if not r["unlock_attempted"]:
        return "did_not_reach_lock"
    if lock_ok(r):
        return "lock_correct"
    w = world(r["world"]); tags = w["tags"]; got = set(r["delivered"])
    has = lambda t: any(t in tags.get(i, []) for i in got)
    if not ((has("clock") or has("glyphs")) and has("registry")):
        return "not_discovered"
    text = " ".join(r["notebook"])
    ph, sg = PHASE.findall(text), SIGMA.findall(text)
    if not ph or not sg:
        return "not_retained"
    if int(ph[-1]) != w["phase"] or int(sg[-1]) != w["sigma"]:
        return "not_retained"
    return "available_action_wrong"


def intervention_card(rows):
    card = room4_scorecard(rows)
    card["note"] = ("room-4 checkpoint after the wipe with the surviving notebook replaced: blank (memoryless) or the "
                    "anti-twin's teacher notebook (both entry bits differ)")
    att = [r for r in rows if r.get("unlock_args")]
    pair = lambda r: [r["unlock_args"].get("route"), r["unlock_args"].get("badge")]
    card["unlock_attempt_rate"] = round(len(att) / len(rows), 3) if rows else None
    card["matches_true_pair"] = round(sum(pair(r) == r["true_pair"] for r in att) / len(att), 3) if att else None
    if any("notebook_pair" in r for r in rows):
        card["follows_notebook_pair"] = round(sum(pair(r) == r["notebook_pair"] for r in att) / len(att), 3) if att else None
    return card


def steps_card(rows):
    n = len(rows); by = defaultdict(list)
    for r in rows: by[r.get("teacher_tool")].append(r["step_reward"])
    kinds = defaultdict(int)
    for r in rows: kinds[r["reward_kind"]] += 1
    groups = defaultdict(list)
    for r in rows: groups[family(r["world"])].append(r)
    mean = lambda rs: sum(x["step_reward"] for x in rs) / len(rs)
    return {"states": n, "mean_step_reward": round(mean(rows), 3),
            "mean_step_reward_ci95": boot_ci(dict(groups), mean),
            "reward_kinds": dict(kinds), "by_teacher_tool": {k: round(sum(v) / len(v), 3) for k, v in sorted(by.items())},
            "note": "held-out single decisions after a teacher prefix, scored with the GRPO step reward"}


def chain_card(rows):
    card = room4_scorecard(rows)
    card.pop("room4_clear", None)
    card["note"] = "model writes its own notebook in room 3, is wiped, then must open the room-4 lock from it"
    card["wrote_notebook"] = round(sum(any((x.get("action") or {}).get("tool") == "notebook_write" for x in r["log"])
                                       for r in rows) / len(rows), 3)
    card["reached_room4"] = round(sum(r["wipes"] >= 1 for r in rows) / len(rows), 3)
    att = defaultdict(int)
    for r in rows: att[attribution(r)] += 1
    card["lock_attribution"] = dict(att)
    return card


def scorecard(rows_by_mode):
    out = {}
    for m in ("chain4", "chain4_blankwrite"):
        if rows_by_mode.get(m):
            out[m] = chain_card(rows_by_mode[m])
    if rows_by_mode.get("steps"):
        out["steps"] = steps_card(rows_by_mode["steps"])
    for m in ("room4_blank", "room4_swap"):
        if rows_by_mode.get(m):
            out[m] = intervention_card(rows_by_mode[m])
    if rows_by_mode.get("room4_all"):
        out["room4_all"] = room4_scorecard(rows_by_mode["room4_all"])
    if rows_by_mode.get("rooms"):
        by = defaultdict(list)
        for r in rows_by_mode["rooms"]: by[r["start_room"]].append(r)
        out["rooms"] = {"overall": basic(rows_by_mode["rooms"]), "by_room": {k: basic(v) for k, v in sorted(by.items())}}
    if rows_by_mode.get("full"):
        rows = rows_by_mode["full"]; b = basic(rows)
        b["escape_rate"] = b.pop("success_rate")
        b["mean_rooms_cleared"] = round(sum(len(r["rooms_cleared"]) for r in rows) / len(rows), 2)
        att = defaultdict(int)
        for r in rows: att[attribution(r)] += 1
        b["lock_attribution"] = dict(att)
        out["full"] = b
    return out
