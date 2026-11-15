"""Shared episode machinery: public prompts (identical for teacher data, evaluation and RL), the reference
teacher, and room-start states. Nothing here sends hidden world facts to a policy."""
import copy
from itertools import product
import json
import sys
from pathlib import Path

from borderland.env import BorderlandEnv
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "borderland"))  # solver uses worker-style imports
from solver import EvidenceSolver  # noqa: E402
from baseline.interface_compact import CompactHistory as PublicHistory
from baseline.interface_v2 import tools_for

ROOT = Path(__file__).resolve().parents[1]
HELDOUT = ROOT / "artifacts/certification-v2"
TRAIN_SETS = ["artifacts/train-worlds-a", "artifacts/train-worlds-b"]

REASONS = {  # Teacher reasons are fixed templates: no hidden facts, no solver internals.
    "read_record": "Read cataloged evidence before committing.",
    "inspect": "Inspect the object to gather public evidence.",
    "status": "Check the current state.",
    "notebook_read": "Check the surviving notebook lines.",
    "notebook_write": "Preserve compact facts and source IDs before the wipe.",
}


def manifests(kind):
    folders = [HELDOUT] if kind == "heldout" else [ROOT / t for t in TRAIN_SETS if (ROOT / t).exists()]
    out = []
    for folder in folders:
        accepted = set(json.loads((folder / "summary.json").read_text())["accepted_seeds"])
        # Only certified families: every attempt is saved on disk, including rejected ones.
        out += [m for m in sorted(folder.glob("family-*/phase-*/manifest.json"))
                if int(m.parent.parent.name.split("-")[1]) in accepted]
    return out


def load_world(path):
    return json.loads(Path(path).read_text())


FACT_KEYS = ["phase", "k", "delta", "aux", "main", "hazard", "mapping", "sigma", "forged", "mode", "offsets",
             "roles", "authority", "culprit", "amendment", "bids"]


def facts_text(knowledge):
    """Facts the evidence-only teacher has derived from delivered public evidence (never hidden state)."""
    out = []
    for key in FACT_KEYS:
        if key in (knowledge or {}):
            v = knowledge[key]
            if isinstance(v, dict):
                v = ",".join(f"{a}:{b}" for a, b in v.items())
            elif isinstance(v, (list, tuple)):
                v = ",".join(str(x) for x in v)
            out.append(f"{key}={v}")
    return " ".join(out)


GLYPH_NAMES = ("A", "B", "C", "D")


def room1_inference(solver, kk, phase):
    """Constructive text for how phase and glyph sectors follow from the CURRENT delivered records (no search)."""
    clock_id, clocks = next((rid, r) for rid, r in solver.records_of("clock_pairs") if r["epoch"] == "current")
    cons_id, cons = next((rid, r) for rid, r in solver.records_of("glyph_constraints") if r["epoch"] == "current")
    smp = clocks["samples"][0]
    ph = (smp["district_mod4"] - smp["wall"]) % 4
    parts = [f"Current clock {clock_id}: wall {smp['wall']} district {smp['district_mod4']}, "
             f"phase=({smp['district_mod4']}-{smp['wall']})%4={ph}."]
    g, o = cons["phase_anchor"]
    known = {g: (ph + o) % 4}
    parts.append(f"Current glyphs {cons_id}: anchor {g},{o} -> K[{g}]=({ph}+{o})%4={known[g]}.")
    changed = True
    while changed:
        changed = False
        for a, b, d in cons["differences"]:
            if a in known and b not in known:
                known[b] = (known[a] - d) % 4; parts.append(f"{a}-{b}={d} -> K[{b}]=({known[a]}-{d})%4={known[b]}."); changed = True
            elif b in known and a not in known:
                known[a] = (known[b] + d) % 4; parts.append(f"{a}-{b}={d} -> K[{a}]=({known[b]}+{d})%4={known[a]}."); changed = True
    missing = [x for x in GLYPH_NAMES if x not in known]
    if len(missing) == 1:
        rest = ({0, 1, 2, 3} - set(known.values())).pop(); known[missing[0]] = rest
        parts.append(f"K[{missing[0]}]={rest} (remaining sector).")
    if ph != phase or [known.get(x) for x in GLYPH_NAMES] != list(kk):
        return None  # not derivable constructively: fall back to the plain derivation
    return " ".join(parts)


PEOPLE_IDX = ("I", "N", "V", "S")


def _bias(p):
    return (p & 1, (p >> 1) & 1, (p & 1) ^ ((p >> 1) & 1))


def _circ(m, x, p):
    b = _bias(p)
    return tuple((sum(a * v for a, v in zip(row, x)) % 2) ^ bb for row, bb in zip(m, b))


def _vec(v):
    return "(" + ",".join(str(int(x)) for x in v) + ")"


def room2_reason(action, k, o, solver):
    sch = next(r for _, r in solver.records_of("schematic"))
    M, p, ch = sch["matrices"], k["phase"], sch["channel_glyphs"]
    t, a = action["tool"], action["args"]
    head = f"phase={p}, bias={_vec(_bias(p))}, channels {','.join(f'{i}={g}' for i, g in enumerate(ch))}."
    if t == "probe":
        parts = [head]
        for i in range(3):
            x = [int(j == i) for j in range(3)]
            o1, o2 = _circ(M[0], x, p), _circ(M[1], x, p)
            if o1 != o2:
                parts.append(f"Channel {i} alone: matrix1 -> {_vec(o1)}, matrix2 -> {_vec(o2)}; they differ, so probe {ch[i]}.")
                return " ".join(parts) if ch[i] == a["channel_id"] else None
            parts.append(f"Channel {i} alone gives {_vec(o1)} under both matrices (no information).")
        return None
    if "matrix" not in k or "probe" not in k:
        return None
    mi = [tuple(map(tuple, m)) for m in M].index(tuple(map(tuple, k["matrix"]))) + 1
    pr = k["probe"]
    sol = lambda tgt: next(x for x in product(range(2), repeat=3) if list(_circ(k["matrix"], x, p)) == list(tgt))
    xa, xm, xh = sol(sch["aux_target"]), sol(sch["main_target"]), sol(sch["forbidden_live_output"])
    if (tuple(xa), tuple(xm), tuple(xh)) != (tuple(k["aux"]), tuple(k["main"]), tuple(k["hazard"])):
        return None
    cur = tuple(int(o["switches"][g]) for g in ch)
    stage = "main" if o["auxiliary_on"] else "auxiliary"
    tgt = xm if o["auxiliary_on"] else xa
    txt = (f"{head} Probe {pr['evidence_id']} output {_vec(pr['output'])} matches matrix{mi}. "
           f"Solve matrix{mi}*x XOR bias: aux {_vec(sch['aux_target'])} needs x={_vec(xa)}, main {_vec(sch['main_target'])} "
           f"needs x={_vec(xm)}, forbidden {_vec(sch['forbidden_live_output'])} is x={_vec(xh)}. "
           f"Switches now {_vec(cur)}, {stage} needs {_vec(tgt)}.")
    if t == "set_switch":
        i = ch.index(a["channel_id"])
        return txt + f" Set channel {i} ({a['channel_id']}) to {str(a['value']).lower()}" + \
            (" (path avoids the forbidden state)." if o["auxiliary_on"] else ".")
    if t == "energize":
        return txt + f" Switches match, energize {a['bus_id']}."
    return None


def room3_reason(action, k, o, solver):
    reg = next(r for _, r in solver.records_of("registry"))
    t, a = action["tool"], action["args"]
    v, r = reg["challenge_examples"][0]
    s = int(v) ^ int(r)
    sig = f"Registry example {int(v)} XOR registry_bit = {int(r)} -> registry_bit={s}."
    if s != k.get("sigma"):
        return None
    if t == "validate_registry":
        c = o["challenge"]
        return sig + f" response=challenge XOR registry_bit={c} XOR {s}={c ^ s} -> {str(bool(c ^ s)).lower()}."
    if t == "certify_roster":
        neg = int(k["delta"] < 0); p = k["phase"]; parts = [f"phase={p}, polarity {'negative' if neg else 'positive'} ({neg})."]
        for alias, tt in sorted(solver.testimonies.items()):
            idx = (tt["seal"] - tt["wall"] - p - neg) % 4
            parts.append(f"{alias}: seal {tt['seal']} wall {tt['wall']} -> ({tt['seal']}-{tt['wall']}-{p}-{neg})%4={idx}={PEOPLE_IDX[idx]}.")
            if PEOPLE_IDX[idx] != a["mapping"].get(alias):
                return None
        bad = []
        for c in reg["credentials"]:
            want = (PEOPLE_IDX.index(c["person"]) + s) % 4
            if c["tag"] != want:
                bad.append(f"{c['id']} ({c['person']}) tag {c['tag']} != ({PEOPLE_IDX.index(c['person'])}+{s})%4={want} -> forged.")
        if len(bad) != 1 or not bad[0].startswith(a["forged_credential_id"]):
            return None
        return sig + " " + " ".join(parts) + " " + bad[0] + " Cite clock, glyphs, probe, testimony, registry."
    return None


def evidence_check(o, solver):
    """Explicit gate (rooms 1-3): what is still unread / unasked, so the model learns WHEN to stop gathering."""
    unread = [r["id"] for r in o.get("records") or [] if r["id"] not in solver.ids]
    asked = getattr(solver, "testimonies", {})
    unasked = [p for p in (o.get("people") or []) if p not in asked] if o.get("room") == 3 else []
    return unread, unasked


def gated_reason(action, k, o, solver):
    t, a = action["tool"], action["args"]
    unread, unasked = evidence_check(o, solver)
    if t == "read_record":
        return f"Evidence check: unread {','.join(unread) or 'none'} -> read {a['record_id']} before committing."
    if t == "question":
        return f"Evidence check: all records read; not yet questioned {','.join(unasked)} -> question {a['person_id']}."
    if unread or unasked:
        return None
    gate = "Evidence check: all records read" + ("and all four questioned" if o.get("room") == 3 else "") + " -> compute. "
    gate = gate.replace("readand", "read and")
    body = None
    if o.get("room") == 2 and t in ("probe", "set_switch", "energize"):
        body = room2_reason(action, k, o, solver)
    elif o.get("room") == 3 and t in ("validate_registry", "certify_roster"):
        body = room3_reason(action, k, o, solver)
    elif o.get("room") == 3 and t == "notebook_write":
        reg = next(r for _, r in solver.records_of("registry"))
        v, r = reg["challenge_examples"][0]; sb = int(v) ^ int(r)
        if sb != k.get("sigma"):
            return None
        body = (f"Registry example {int(v)} XOR registry_bit = {int(r)} -> registry_bit={sb}. Before the wipe, write phase={k['phase']} "
                f"and registry_bit={sb} (stored as sigma), k, rival mode/offsets, roles, credentials and source ids.")
    elif o.get("room") == 1 and t == "choose_door":
        body = None  # handled by the door derivation below (prefixed with the gate)
    elif t == "exit_room":
        body = "Room objectives complete; exit."
    if body is None and t == "choose_door":
        d = derivation(action, k, o, None if o.get("bank", 0) else None)
        p, b, pu, kk = k["phase"], o["bank"], o["pulse"], k["k"]
        inf = room1_inference(solver, kk, p) if b == 0 else None
        ks = ",".join(f"{g}:{v}" for g, v in zip(GLYPH_NAMES, kk)); sec = (p + b + pu) % 4
        tail = f"bank={b} pulse={pu}. sector=(phase+bank+pulse)%4=({p}+{b}+{pu})%4={sec}. Glyph at sector {sec} is {GLYPH_NAMES[kk.index(sec)]}."
        body = f"{inf} So k={ks}; {tail}" if inf else f"Known: phase={p} k={ks} {tail}"
    return gate + body if body else None


def derivation(action, knowledge, obs, solver=None):
    """v2 teacher rationale: for actions whose arguments are computed, show the computation from facts the agent
    holds (evidence-derived knowledge or the surviving notebook) and public observation fields. None otherwise."""
    k, o, t, a = knowledge or {}, obs or {}, action["tool"], action["args"]
    if solver is not None and o.get("room") in (1, 2, 3):
        got = gated_reason(action, k, o, solver)
        if got:
            return got
    try:
        if t == "unlock":
            p, s, pu, c = k["phase"], k["sigma"], o["pulse"], o["challenge"]
            return (f"Known: phase={p} registry_bit(sigma)={s} pulse={pu} challenge={c}. "
                    f"route=(phase%2) XOR pulse=({p}%2) XOR {pu}={p % 2} XOR {pu}={(p % 2) ^ pu}. "
                    f"badge=registry_bit XOR challenge={s} XOR {c}={s ^ c}.")
        if t == "choose_door":
            p, b, pu, kk = k["phase"], o["bank"], o["pulse"], k["k"]
            sec = (p + b + pu) % 4
            glyph = GLYPH_NAMES[kk.index(sec)]
            ks = ",".join(f"{g}:{v}" for g, v in zip(GLYPH_NAMES, kk))
            tail = (f"bank={b} pulse={pu}. sector=(phase+bank+pulse)%4=({p}+{b}+{pu})%4={sec}. "
                    f"Glyph at sector {sec} is {glyph}.")
            if b == 0 and solver is not None:
                inf = room1_inference(solver, kk, p)
                if inf:
                    return f"{inf} So k={ks}; {tail}"
            return f"Known: phase={p} k={ks} {tail}"
        if t == "validate_registry":
            s, c = k["sigma"], o["challenge"]
            return (f"Known: registry_bit(sigma)={s} challenge={c}. response=challenge XOR registry_bit={c} XOR {s}="
                    f"{c ^ s} -> {str(bool(c ^ s)).lower()}.")
        if t == "submit_bid":
            r, bids = o["round"], k["bids"]
            return (f"Known: mode={k['mode']} offsets={','.join(map(str, k['offsets']))} phase={k['phase']} "
                    f"delta={k['delta']}. Winning plan bids={','.join(map(str, bids))}; round={r} -> bid={bids[r]}.")
    except (KeyError, ValueError, IndexError, TypeError):
        return None
    return None


def target_text(action, knowledge=None, obs=None, solver=None):
    reason = derivation(action, knowledge, obs, solver) if obs is not None else None
    if reason is None:
        reason = REASONS.get(action["tool"], "Apply the public rules to the evidence gathered so far.")
        facts = facts_text(knowledge)
        if facts:
            reason = (f"Known: {facts}. " + reason)[:600]
    return json.dumps({"reason": reason, "tool": action["tool"], "args": action["args"]},
                      separators=(",", ":"), ensure_ascii=True)


def teacher_episode(world):
    """Run the evidence-only reference solver; yield (messages, action, env-snapshot-before) per decision.
    The solver is restarted with no memory at the seal, exactly like the certified worker."""
    env = BorderlandEnv(world=world)
    solver, history = EvidenceSolver(), PublicHistory()
    frame = {"ok": True, "result": {}, "observation": env.observe()}
    steps = []
    while not (env.terminated or env.truncated):
        history.add(frame)
        messages = history.messages()
        action = solver.act(json.loads(json.dumps(frame)))  # same JSON wire as the certified worker
        knowledge = json.loads(json.dumps(solver.knowledge, default=list))
        obs = json.loads(json.dumps(frame["observation"]))
        steps.append({"room": env.room, "messages": messages, "action": action, "knowledge": knowledge, "obs": obs,
                      "actions_so_far": [r["action"] for r in env.trace]})
        output = json.loads(target_text(action, knowledge, obs, solver))
        steps[-1]["target"] = json.dumps(output, separators=(",", ":"), ensure_ascii=True)
        history.act(output)
        result = env.step(action)
        if result.info["epoch_changed"]:
            solver, history = EvidenceSolver(), PublicHistory()
            frame = {"ok": True, "result": {}, "observation": env.observe()}
        else:
            frame = result.observation
    return env, steps


def replay_to(world, actions):
    """Deterministically rebuild an environment after a recorded action prefix."""
    env = BorderlandEnv(world=world)
    for a in actions:
        env.step(a)
    return env
