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


GLYPH_NAMES = ("A", "B", "C", "D")


def derivation(action, knowledge, obs):
    """v2 teacher rationale: for actions whose arguments are computed, show the computation from facts the agent
    holds (evidence-derived knowledge or the surviving notebook) and public observation fields. None otherwise."""
    k, o, t, a = knowledge or {}, obs or {}, action["tool"], action["args"]
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
            return (f"Known: phase={p} k={ks} bank={b} pulse={pu}. sector=(phase+bank+pulse)%4=({p}+{b}+{pu})%4={sec}. "
                    f"Glyph at sector {sec} is {glyph}.")
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


def target_text(action, knowledge=None, obs=None):
    reason = derivation(action, knowledge, obs) if obs is not None else None
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
        output = json.loads(target_text(action, knowledge, obs))
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
