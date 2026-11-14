"""Evaluate a model (base or +adapter) on held-out worlds: room-start episodes for all 7 rooms + full episodes.
All episodes of a phase step in lockstep; each step is one batched generation call."""
import argparse
import json
import time
from collections import defaultdict
from .episodes import ROOT, manifests, load_world
from .evaluate import teacher_prefix, summarize
from .runner import Episode, run_batch
from .generate import make_generator


def build(worlds, mode, rooms):
    eps = []
    for path in worlds:
        world = load_world(path)
        rel = str(path.relative_to(ROOT))
        if mode == "full":
            eps.append(Episode(world, meta={"world": rel, "mode": "full"}))
        else:
            for r in rooms:
                if r == 1:
                    eps.append(Episode(world, start_room=1, meta={"world": rel, "mode": "rooms"}))
                    eps[-1].start_room, eps[-1].cap = 1, 3 * 12 + 10
                else:
                    env, hist, frame, _ = teacher_prefix(world, r)
                    eps.append(Episode(world, start_room=r, prefix=(env, hist, frame), meta={"world": rel, "mode": "rooms"}))
    return eps


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--adapter", default=None)
    p.add_argument("--backend", default="vllm", choices=["vllm", "hf"])
    p.add_argument("--modes", default="rooms,full")
    p.add_argument("--rooms", default="1,2,3,4,5,6,7")
    p.add_argument("--worlds", default="one-per-family", choices=["one-per-family", "all"])
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--label", required=True)
    p.add_argument("--outdir", default="artifacts/eval")
    p.add_argument("--max-tokens", type=int, default=640)
    a = p.parse_args()
    worlds = manifests("heldout")
    if a.worlds == "one-per-family":
        seen, picked = set(), []
        for w in worlds:
            fam = w.parent.parent.name
            if fam not in seen:
                seen.add(fam); picked.append(w)
        worlds = picked
    worlds = worlds[: a.limit] if a.limit else worlds
    gen = make_generator(a.backend, a.model, adapter=a.adapter, max_tokens=a.max_tokens)
    out = ROOT / a.outdir / a.label
    out.mkdir(parents=True, exist_ok=True)
    report = {"label": a.label, "model": a.model, "adapter": a.adapter, "worlds": len(worlds)}
    for mode in a.modes.split(","):
        t0 = time.time()
        eps = build(worlds, mode, [int(x) for x in a.rooms.split(",")])
        rows = run_batch(eps, gen)
        with (out / f"{mode}.jsonl").open("w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        by = defaultdict(list)
        for r in rows:
            by[r["start_room"]].append(r)
        report[mode] = {"overall": summarize(rows), "by_room": {k: summarize(v) for k, v in sorted(by.items())},
                        "seconds": round(time.time() - t0, 1)}
    (out / "summary.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
