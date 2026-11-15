"""Build the agentic-distillation SFT dataset from reference-solver episodes (teacher = our own solver).
One row per decision: chat messages (system, user = exact public prompt) + assistant = action JSON."""
import argparse
import hashlib
import json
from collections import Counter
from .episodes import manifests, load_world, teacher_episode, target_text, ROOT


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--split", default="train", choices=["train", "heldout"])
    p.add_argument("--output", default="artifacts/sft-data/train.jsonl")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--offset", type=int, default=0)
    a = p.parse_args()
    paths = manifests(a.split)[a.offset: (a.offset + a.limit) if a.limit else None]
    out = ROOT / a.output
    out.parent.mkdir(parents=True, exist_ok=True)
    rooms, tools, chars, ok = Counter(), Counter(), [], 0
    with out.open("w") as f:
        for path in paths:
            world = load_world(path)
            env, steps = teacher_episode(world)
            if not env.success:
                raise RuntimeError(f"teacher failed on {path}")
            ok += 1
            for i, s in enumerate(steps):
                row = {"world": str(path.relative_to(ROOT)), "step": i, "room": s["room"],
                       "messages": s["messages"] + [{"role": "assistant", "content": target_text(s["action"], s["knowledge"], s.get("obs"))}]}
                f.write(json.dumps(row, separators=(",", ":")) + "\n")
                rooms[s["room"]] += 1; tools[s["action"]["tool"]] += 1
                chars.append(sum(len(m["content"]) for m in row["messages"]))
    chars.sort()
    stats = {"worlds": ok, "rows": len(chars), "rows_per_room": dict(sorted(rooms.items())),
             "tools": dict(tools.most_common()), "chars_p50": chars[len(chars)//2], "chars_p95": chars[int(len(chars)*.95)],
             "chars_max": chars[-1], "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}
    (out.with_suffix(".stats.json")).write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
