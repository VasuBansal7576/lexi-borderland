"""Build GRPO states from teacher trajectories on TRAIN worlds (never held-out). One row per state:
prompt (exact public messages), world, action prefix to rebuild the env, and evidence-derived facts for notebook steps."""
import argparse
import json
import random
from collections import Counter
from .episodes import ROOT, manifests, load_world, teacher_episode, facts_text, target_text

HARD = {"choose_door", "set_switch", "energize", "probe", "validate_registry", "certify_roster", "notebook_write",
        "unlock", "activate_relay", "submit_bid", "accuse", "revoke", "accept_amendment", "allocate_points",
        "team_step", "settle", "exit_room", "question"}


def notebook_facts(knowledge):
    """Values a good notebook must preserve (all derived from delivered public evidence)."""
    f = []
    k = knowledge or {}
    for key in ("phase", "delta", "sigma"):
        if key in k: f.append(f"{k[key]}")
    if "k" in k: f.append(",".join(str(x) for x in k["k"]))
    for key in ("forged", "roles_id", "clock_id", "mode"):
        if key in k: f.append(str(k[key]))
    if "mapping" in k: f += [f"{a}" for a in k["mapping"].values()]
    if "offsets" in k: f.append(",".join(str(x) for x in k["offsets"]))
    if "probe" in k and isinstance(k["probe"], dict) and "evidence_id" in k["probe"]: f.append(k["probe"]["evidence_id"])
    return sorted(set(f))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="artifacts/grpo-data/states.jsonl")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--easy-keep", type=float, default=0.15)
    a = p.parse_args()
    rng = random.Random(7)
    out = ROOT / a.output; out.parent.mkdir(parents=True, exist_ok=True)
    tools = Counter()
    with out.open("a") as f:
        for path in manifests("train")[a.offset:(a.offset + a.limit) if a.limit else None]:
            env, steps = teacher_episode(load_world(path))
            for s in steps:
                tool = s["action"]["tool"]
                if tool not in HARD and rng.random() > a.easy_keep:
                    continue
                row = {"prompt": s["messages"], "world": str(path.relative_to(ROOT)),
                       "prefix": json.dumps(s["actions_so_far"], separators=(",", ":")),
                       "facts": json.dumps(notebook_facts(s["knowledge"]) if tool == "notebook_write" else []),
                       "room": s["room"], "teacher_tool": tool, "teacher": target_text(s["action"], s["knowledge"])}
                f.write(json.dumps(row, separators=(",", ":")) + "\n"); tools[tool] += 1
    print(json.dumps(dict(tools.most_common())))


if __name__ == "__main__":
    main()
