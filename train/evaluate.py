"""Episode evaluation for any policy on the Borderland environment, with the compact public interface.

Modes: full episodes from the start, and room-start episodes (the evidence-only teacher plays up to room r with its
public outputs as history, then the policy plays room r). Invalid outputs return an error frame (3 in a row end the
episode). Every number comes from the environment's own ledger; nothing is judged by a model."""
import argparse
import json
import random
import time
from pathlib import Path

from borderland.env import BorderlandEnv
from baseline.interface_compact import CompactHistory
from baseline.interface_v2 import response_schema, validate, PARAMETERS
from baseline.paid.client import strict_json
from baseline.paid.guard import LoopGuard
from baseline.paid.run import explain_invalid
from .episodes import ROOT, manifests, load_world, target_text, EvidenceSolver

TEACHER_ROOM_STEPS = {1: 12, 2: 9, 3: 14, 4: 22, 5: 5, 6: 11, 7: 13}  # typical teacher steps per room


class TeacherPolicy:
    """Evidence-only reference solver (oracle ceiling). Reset at every wipe, like the certified worker."""
    name = "teacher"
    def __init__(self): self.reset()
    def reset(self): self.solver = EvidenceSolver()
    def adopt(self, solver): self.solver = solver
    def __call__(self, messages, frame):
        action = self.solver.act(json.loads(json.dumps(frame)))
        return target_text(action, json.loads(json.dumps(self.solver.knowledge, default=list)))


class RandomPolicy:
    """Random-floor baseline: a random available tool with schema-shaped arguments built from visible IDs."""
    name = "random"
    def __init__(self, seed=0): self.rng = random.Random(seed)
    def reset(self): pass
    def _value(self, schema, ids):
        t = schema.get("type")
        if "enum" in schema: return self.rng.choice(schema["enum"])
        if t == "string": return self.rng.choice(ids) if ids else "x"
        if t == "integer": return self.rng.randint(schema.get("minimum", 0), min(schema.get("maximum", 20), 20))
        if t == "boolean": return self.rng.random() < .5
        if t == "array":
            n = schema.get("minItems", 1)
            return [self._value(schema.get("items", {}), ids) for _ in range(n)]
        if t == "object":
            return {k: self._value(v, ids) for k, v in schema.get("properties", {}).items() if k in schema.get("required", [])}
        return None
    def __call__(self, messages, frame):
        obs = frame["observation"]; text = json.dumps(obs)
        import re
        ids = sorted(set(re.findall(r'"(e\d{4}|c\d{4})"', text))) + [str(x) for x in range(9)] + list(obs.get("people", []))
        tool = self.rng.choice(sorted(obs["tools"]))
        return json.dumps({"reason": "random", "tool": tool, "args": self._value(PARAMETERS[tool], ids) or {}})


def teacher_prefix(world, start_room):
    """Teacher plays until it first stands in start_room. Returns env, history (public), frame."""
    env = BorderlandEnv(world=world)
    solver, history = EvidenceSolver(), CompactHistory()
    frame = {"ok": True, "result": {}, "observation": env.observe()}
    while env.room != start_room:
        history.add(frame)
        action = solver.act(json.loads(json.dumps(frame)))
        history.act(json.loads(target_text(action, json.loads(json.dumps(solver.knowledge, default=list)))))
        result = env.step(action)
        if result.info["epoch_changed"]:
            solver, history = EvidenceSolver(), CompactHistory()
            frame = {"ok": True, "result": {}, "observation": env.observe()}
        else:
            frame = result.observation
        if env.terminated or env.truncated:
            raise RuntimeError("teacher prefix ended early")
    return env, history, frame, solver


def play(world, policy, *, start_room=None, step_cap=None, stall_limit=5, log=None):
    if start_room in (None, 1):
        env, history = BorderlandEnv(world=world), CompactHistory()
        frame = {"ok": True, "result": {}, "observation": env.observe()}
    else:
        env, history, frame, prefix_solver = teacher_prefix(world, start_room)
    policy.reset()
    if start_room and start_room > 1 and hasattr(policy, "adopt"):
        policy.adopt(prefix_solver)  # the oracle keeps the teacher's own epoch knowledge
    if start_room and start_room > 1 and hasattr(policy, "prime"):
        policy.prime(history)
    guard = LoopGuard(stall_limit)
    steps = invalid = consecutive = 0
    stop = None
    room0 = env.room
    cap = step_cap or (3 * TEACHER_ROOM_STEPS[room0] + 10 if start_room else 400)
    while not (env.terminated or env.truncated):
        if start_room and env.room != room0:
            stop = "room_exit"; break
        if steps >= cap:
            stop = "step_cap"; break
        history.add(frame)
        messages = history.messages()
        raw = policy(messages, frame)
        steps += 1
        try:
            output = strict_json(raw)
            validate(output, response_schema(frame["observation"]))
        except Exception:
            invalid += 1; consecutive += 1
            detail = explain_invalid(raw, frame["observation"]) or "invalid output"
            history.act({"invalid_output": raw[:1500]})
            frame = {"ok": False, "result": {"error": "invalid_action", "detail": detail}, "observation": frame["observation"]}
            if log is not None: log.append({"room": env.room, "raw": raw, "invalid": detail})
            if consecutive >= 3:
                stop = "repeated_invalid_actions"; break
            continue
        consecutive = 0
        history.act(output)
        action = {"tool": output["tool"], "args": output["args"]}
        before = frame
        result = env.step(action)
        if log is not None: log.append({"room": before["observation"]["room"], "raw": raw, "action": action, "ok": result.observation["ok"]})
        if result.info["epoch_changed"]:
            history = CompactHistory(); guard.reset(); policy.reset()
            frame = {"ok": True, "result": {}, "observation": env.observe()}
        else:
            frame = result.observation
            if guard.observe(before, action, frame) and not (env.terminated or env.truncated):
                stop = "no_progress"; break
    cleared = sorted({r for r, flag in env.flags if flag == "clear"})
    return {"start_room": start_room or 1, "success": (room0 in cleared) if start_room else env.success,
            "rooms_cleared": cleared, "last_room": env.room, "steps": steps, "invalid": invalid,
            "trap_used": not env.integrity, "score": env.score,
            "stop": stop or env.reason, "notebook": list(env.notebook)}


def summarize(rows):
    n = len(rows)
    agg = lambda k: sum(1 for r in rows if r[k]) / n if n else 0
    return {"episodes": n, "success_rate": agg("success"), "trap_rate": agg("trap_used"),
            "mean_steps": sum(r["steps"] for r in rows) / n, "invalid_rate": sum(r["invalid"] for r in rows) / max(1, sum(r["steps"] for r in rows)),
            "mean_score": sum(r["score"] for r in rows) / n}


def make_policy(name, **kw):
    if name == "teacher": return TeacherPolicy()
    if name == "random": return RandomPolicy(kw.get("seed", 0))
    if name.startswith("hf:"):
        from .policy_hf import HFPolicy
        return HFPolicy(name[3:], adapter=kw.get("adapter"))
    raise ValueError(name)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--policy", required=True)
    p.add_argument("--adapter", default=None)
    p.add_argument("--mode", choices=["full", "rooms"], default="rooms")
    p.add_argument("--rooms", default="1,2,3,4,5,6,7")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    policy = make_policy(a.policy, adapter=a.adapter)
    worlds = manifests("heldout")[a.offset:(a.offset + a.limit) if a.limit else None]
    out = ROOT / a.output; out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    with out.open("a") as f:
        for path in worlds:
            world = load_world(path)
            starts = [None] if a.mode == "full" else [int(x) for x in a.rooms.split(",")]
            for r in starts:
                log = []
                res = play(world, policy, start_room=r, log=log)
                res.update(world=str(path.relative_to(ROOT)), policy=a.policy, adapter=a.adapter, mode=a.mode)
                res["log"] = log
                f.write(json.dumps(res) + "\n"); f.flush(); rows.append(res)
    by_room = {}
    for r in rows:
        by_room.setdefault(r["start_room"], []).append(r)
    print(json.dumps({"overall": summarize(rows), "by_room": {k: summarize(v) for k, v in sorted(by_room.items())},
                      "seconds": round(time.time() - t0, 1)}, indent=1))


if __name__ == "__main__":
    main()
