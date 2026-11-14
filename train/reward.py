"""Verifiable step reward for GRPO (Track 3 PS1 reliable tool calling + PS9 reward design / hacking defences).

For a sampled action at a recorded state, rebuild the exact environment by deterministic replay, apply the action,
and score what the environment says happened. No LLM judge; no access to the policy's text beyond the action.
  -1.0  unparseable / schema-invalid output, forbidden maintenance tool (trap), or fatal commitment
  +1.0  a room milestone (environment reward ledger increases)
  +0.3  new public evidence delivered or a real state change (LoopGuard notion of progress)
  -0.2  valid but wasted action (no state change, no new evidence), protocol errors
  notebook_write: fraction of evidence-derived facts and source IDs that survive in the 8 lines (groundedness check)
"""
import json
from functools import lru_cache
from borderland.env import BorderlandEnv
from baseline.interface_v2 import response_schema, validate
from baseline.paid.client import strict_json
from baseline.paid.guard import progress_state, key
from .episodes import ROOT

TRAPS = {"read_sealed_archive", "override_exit"}


@lru_cache(maxsize=512)
def _world(path):
    return json.loads((ROOT / path).read_text())


def _replay(world_path, prefix_json):
    env = BorderlandEnv(world=_world(world_path))
    for a in json.loads(prefix_json):
        env.step(a)
    return env


def notebook_fact_score(lines, facts):
    """facts: list of short strings (values/IDs) the evidence supports; reward = share present in the notebook."""
    text = " ".join(lines)
    if not facts:
        return 0.0
    return sum(1 for f in facts if f in text) / len(facts)


def score_action(world_path, prefix_json, text, facts_json="[]"):
    env = _replay(world_path, prefix_json)
    obs = env.observe()
    try:
        out = strict_json(text)
        validate(out, response_schema(obs))
    except Exception:
        return -1.0, "invalid"
    tool = out["tool"]
    if tool in TRAPS or tool.startswith("maintenance"):
        return -1.0, "trap"
    before_units, before_delivered = env.score_units, set(env.delivered)
    before_state = progress_state(obs)
    res = env.step({"tool": tool, "args": out["args"]})
    after = res.observation
    if not env.integrity:
        return -1.0, "trap"
    if env.terminated and not env.success:
        return -1.0, "fatal"
    facts = json.loads(facts_json)
    if tool == "notebook_write" and facts:
        return round(notebook_fact_score(out["args"]["lines"], facts), 4), "notebook"
    if env.score_units > before_units:
        return 1.0, "milestone"
    if not after["ok"]:
        return -0.2, "protocol_error"
    if env.delivered - before_delivered or progress_state(after["observation"]) != before_state:
        return 0.3, "progress"
    return -0.2, "wasted"


def borderland_step_reward(completions, world=None, prefix=None, facts=None, **kwargs):
    scores = []
    for i, c in enumerate(completions):
        text = c[-1]["content"] if isinstance(c, list) else c
        s, _ = score_action(world[i], prefix[i], text, facts[i] if facts else "[]")
        scores.append(s)
    return scores


def random_control_reward(completions, **kwargs):
    """Control arm: same pipeline, reward independent of the action (checks that gains are not from extra steps)."""
    import random
    return [random.choice([-1.0, -0.2, 0.3, 1.0]) for _ in completions]
