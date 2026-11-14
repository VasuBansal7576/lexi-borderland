"""Shared episode machinery: public prompts (identical for teacher data, evaluation and RL), the reference
teacher, and room-start states. Nothing here sends hidden world facts to a policy."""
import copy
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


def target_text(action, knowledge=None):
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
        steps.append({"room": env.room, "messages": messages, "action": action, "knowledge": knowledge,
                      "actions_so_far": [r["action"] for r in env.trace]})
        output = json.loads(target_text(action, knowledge))
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
