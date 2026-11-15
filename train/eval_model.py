"""Crash-safe evaluation on held-out worlds. Modes (run in this order):
  room4_all: room-4 checkpoint on ALL 64 held-out worlds (twins) -> lock success, pairwise DSE
  rooms:     room-start episodes for rooms 1-7 on one world per family (16)
  full:      full episodes on one world per family (16) -> escape rate, failure attribution
Every finished episode is appended to <label>/<mode>.jsonl immediately; --resume skips finished keys."""
import argparse, hashlib, json, time
from pathlib import Path
from .episodes import ROOT, manifests, load_world, target_text, EvidenceSolver
from .evaluate import teacher_prefix, RandomPolicy
from .runner import Episode, run_batch
from .metrics import scorecard


def worlds(kind):
    allw = manifests("heldout")
    if kind == "all":
        return allw
    seen, picked = set(), []
    for w in allw:
        if w.parent.parent.name not in seen:
            seen.add(w.parent.parent.name); picked.append(w)
    return picked


INTERVENTIONS = ("room4_blank", "room4_swap")


def plan(mode):
    if mode == "room4_all" or mode in INTERVENTIONS:
        return [(w, 4) for w in worlds("all")]
    if mode == "rooms":
        return [(w, r) for w in worlds("one") for r in range(1, 8)]
    return [(w, None) for w in worlds("one")]


def make_episode(path, room, mode):
    world = load_world(path); rel = str(path.relative_to(ROOT))
    meta = {"world": rel, "mode": mode, "key": f"{mode}|{rel}|{room}"}
    if room in (None, 1):
        e = Episode(world, meta=meta)
        if room == 1:
            e.start_room, e.cap = 1, 46
        e.teacher_solver = EvidenceSolver()
    else:
        env, hist, frame, solver = teacher_prefix(world, room)
        if mode in INTERVENTIONS:
            # Causal test of the notebook: same world and prompt format, only the surviving notebook changes.
            # blank -> memoryless (lock <= 25%); swap -> the anti-twin's notebook (both entry bits differ), so a
            # policy that reads its notebook should fail, and follow_rate measures how often it used it.
            assert env.room == 4 and env.epoch >= 1, "intervention must start right after the wipe"
            meta["true_pair"] = [world["phase"] % 2, world["sigma"] ^ 1]
            if mode == "room4_blank":
                env.notebook = [""] * 8
            else:
                twin = anti_twin(path)
                tenv = teacher_prefix(load_world(twin), 4)[0]
                env.notebook = list(tenv.notebook)
                tw = load_world(twin)
                meta["notebook_from"] = str(twin.relative_to(ROOT)); meta["notebook_pair"] = [tw["phase"] % 2, tw["sigma"] ^ 1]
            frame = {"ok": True, "result": {}, "observation": env.observe()}
        e = Episode(world, start_room=room, prefix=(env, hist, frame), meta=meta)
        e.teacher_solver = solver
    e.seen_wipes = 0
    return e


def anti_twin(path):
    w = load_world(path)
    for sib in sorted(path.parent.parent.glob("*/manifest.json")):
        t = load_world(sib)
        if t["phase"] % 2 != w["phase"] % 2 and t["sigma"] != w["sigma"]:
            return sib
    raise RuntimeError(f"no anti-twin for {path}")


class TeacherPolicy:
    def __call__(self, eps):
        outs = []
        for e in eps:
            e.messages()
            if e.wipes != e.seen_wipes:
                e.teacher_solver, e.seen_wipes = EvidenceSolver(), e.wipes
            a = e.teacher_solver.act(json.loads(json.dumps(e.frame)))
            outs.append(target_text(a, json.loads(json.dumps(e.teacher_solver.knowledge, default=list)), e.frame["observation"]))
        return outs


class RandPolicy:
    def __init__(self): self.p = RandomPolicy(0)
    def __call__(self, eps):
        outs = []
        for e in eps:
            e.messages(); outs.append(self.p(None, e.frame))
        return outs


def lenient_extract(raw):
    """Lenient arm only: keep the first top-level JSON object (drops markdown fences / surrounding prose).
    The strict arm is the default; lenient results are always reported separately and labelled as such."""
    i = raw.find("{")
    if i < 0:
        return raw
    try:
        obj, end = json.JSONDecoder().raw_decode(raw[i:])
        return raw[i:i + end]
    except ValueError:
        return raw


class ModelPolicy:
    def __init__(self, gen, lenient=False): self.gen = gen; self.t0 = time.time(); self.steps = 0; self.lenient = lenient
    def __call__(self, eps):
        t = time.time(); outs = self.gen([e.messages() for e in eps]); self.steps += len(eps)
        if self.lenient:
            outs = [lenient_extract(o) for o in outs]
        print(f"[{time.time()-self.t0:7.0f}s] live={len(eps)} round={time.time()-t:5.1f}s steps={self.steps} "
              f"new_tok={self.gen.new_tokens} peak={self.gen.peak_gb:.1f}GB oom={self.gen.oom_retries}", flush=True)
        return outs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--policy", default="hf", choices=["hf", "teacher", "random"])
    p.add_argument("--model"); p.add_argument("--adapter", default=None)
    p.add_argument("--modes", default="room4_all,rooms,full")
    p.add_argument("--label", required=True); p.add_argument("--outdir", default="artifacts/eval")
    p.add_argument("--max-tokens", type=int, default=400)
    p.add_argument("--token-budget", type=int, default=24000, help="prompt+generation tokens per generate() chunk")
    p.add_argument("--limit", type=int, default=None, help="max episodes per mode (tests)")
    p.add_argument("--bundle-sha", default="local")
    p.add_argument("--lenient-json", action="store_true", help="separately-labelled arm: strip fences around the JSON")
    a = p.parse_args()
    out = Path(a.outdir) if Path(a.outdir).is_absolute() else ROOT / a.outdir
    out = out / a.label; out.mkdir(parents=True, exist_ok=True)
    gen = None
    if a.policy == "hf":
        from .generate import HFGenerator
        gen = HFGenerator(a.model, adapter=a.adapter, max_tokens=a.max_tokens, token_budget=a.token_budget)
        policy = ModelPolicy(gen, lenient=a.lenient_json)
    else:
        policy = TeacherPolicy() if a.policy == "teacher" else RandPolicy()
    rows_by_mode, timing = {}, {}
    for mode in a.modes.split(","):
        f = out / f"{mode}.jsonl"
        done = {json.loads(l)["key"]: json.loads(l) for l in open(f)} if f.exists() else {}
        todo = [(w, r) for w, r in plan(mode) if f"{mode}|{w.relative_to(ROOT)}|{r}" not in done][: a.limit]
        t0 = time.time()
        eps = [make_episode(w, r, mode) for w, r in todo]
        def save(e):
            with f.open("a") as fh:
                fh.write(json.dumps(e.result()) + "\n")
        if eps:
            run_batch(eps, policy, on_done=save)
        rows_by_mode[mode] = [json.loads(l) for l in open(f)] if f.exists() else []
        timing[mode] = round(time.time() - t0, 1)
        summary = {"label": a.label, "policy": a.policy, "model": a.model, "adapter": a.adapter,
                   "bundle_sha": a.bundle_sha, "max_new_tokens": a.max_tokens, "decoding": "greedy", "lenient_json": getattr(a, "lenient_json", False),
                   "seconds": timing, "peak_gpu_gb": round(getattr(gen, "peak_gb", 0.0), 2),
                   "oom_retries": getattr(gen, "oom_retries", 0), "dtype": getattr(gen, "dtype", None),
                   "new_tokens": getattr(gen, "new_tokens", 0), "scorecard": scorecard(rows_by_mode)}
        (out / f"summary-{a.modes.replace(',', '+')}.json").write_text(json.dumps(summary, indent=1))
        print(json.dumps({mode: summary["scorecard"].get(mode)}, indent=1), flush=True)


if __name__ == "__main__":
    main()
