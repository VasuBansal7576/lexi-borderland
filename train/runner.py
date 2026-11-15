"""Steppable episode runner so many episodes can share one batched generation call (vLLM or HF)."""
import json
from borderland.env import BorderlandEnv
from baseline.interface_compact import CompactHistory
from baseline.interface_v2 import response_schema, validate
from baseline.paid.client import strict_json
from baseline.paid.guard import LoopGuard
from baseline.paid.run import explain_invalid

TEACHER_ROOM_STEPS = {1: 12, 2: 9, 3: 14, 4: 22, 5: 5, 6: 11, 7: 13}


class Episode:
    def __init__(self, world, *, start_room=None, prefix=None, step_cap=None, stall_limit=5, meta=None):
        """prefix: optional (env, history, frame) from a teacher prefix for room-start episodes."""
        if prefix is None:
            self.env, self.history = BorderlandEnv(world=world), CompactHistory()
            self.frame = {"ok": True, "result": {}, "observation": self.env.observe()}
        else:
            self.env, self.history, self.frame = prefix
        self.start_room = start_room if (start_room or 1) > 1 else None
        self.room0 = self.env.room
        self.cap = step_cap or (3 * TEACHER_ROOM_STEPS[self.room0] + 10 if self.start_room else 400)
        self.guard = LoopGuard(stall_limit)
        self.steps = self.invalid = self.consecutive = 0
        self.stop, self.log, self.meta = None, [], meta or {}
        self.done = False
        self.wipes = 0
        self._check_end()
        self.pending_messages = None

    def _check_end(self):
        env = self.env
        if env.terminated or env.truncated:
            self.done = True
        elif self.start_room and env.room != self.room0:
            self.done, self.stop = True, "room_exit"
        elif self.steps >= self.cap:
            self.done, self.stop = True, "step_cap"

    def messages(self):
        """Messages for the next decision (call once per step, then feed())."""
        self.history.add(self.frame)
        self.pending_messages = self.history.messages()
        return self.pending_messages

    def feed(self, raw):
        env = self.env
        self.steps += 1
        obs = self.frame["observation"]
        try:
            output = strict_json(raw)
            validate(output, response_schema(obs))
        except Exception:
            self.invalid += 1; self.consecutive += 1
            detail = explain_invalid(raw, obs) or "invalid output"
            self.history.act({"invalid_output": raw[:1500]})
            self.frame = {"ok": False, "result": {"error": "invalid_action", "detail": detail}, "observation": obs}
            self.log.append({"room": env.room, "raw": raw, "invalid": detail})
            if self.consecutive >= 3:
                self.done, self.stop = True, "repeated_invalid_actions"
            else:
                self._check_end()
            return
        self.consecutive = 0
        self.history.act(output)
        action = {"tool": output["tool"], "args": output["args"]}
        before = self.frame
        result = env.step(action)
        self.log.append({"room": obs["room"], "raw": raw, "action": action, "ok": result.observation["ok"]})
        if result.info["epoch_changed"]:
            self.wipes += 1
            self.history = CompactHistory(); self.guard.reset()
            self.frame = {"ok": True, "result": {}, "observation": env.observe()}
        else:
            self.frame = result.observation
            if self.guard.observe(before, action, self.frame) and not (env.terminated or env.truncated):
                self.done, self.stop = True, "no_progress"
                return
        self._check_end()

    def result(self):
        env = self.env
        cleared = sorted({r for r, flag in env.flags if flag == "clear"})
        return {**self.meta, "start_room": self.start_room or 1,
                "success": (self.room0 in cleared) if self.start_room else env.success,
                "rooms_cleared": cleared, "last_room": env.room, "steps": self.steps, "invalid": self.invalid,
                "trap_used": not env.integrity, "score": env.score, "wipes": self.wipes,
                "stop": self.stop or env.reason, "notebook": list(env.notebook), "log": self.log,
                "reason": env.reason, "delivered": sorted(env.delivered),
                "unlock_attempted": any((x.get("action") or {}).get("tool") == "unlock" for x in self.log),
                "lock_failed": env.reason == "seal_lock",
                "unlock_args": next(((x["action"]["args"]) for x in self.log if (x.get("action") or {}).get("tool") == "unlock"), None), "seconds": round(getattr(self, "seconds", 0.0), 2)}


def run_batch(episodes, policy, on_done=None, max_rounds=1000):
    """policy(list_of_live_episodes) -> list of raw texts (call ep.messages() inside). on_done(ep) fires once per
    finished episode so callers can persist results immediately (crash-safe)."""
    import time
    for _ in range(max_rounds):
        live = [e for e in episodes if not e.done]
        if not live:
            break
        t = time.time()
        outs = policy(live)
        dt = (time.time() - t) / max(1, len(live))
        for e, raw in zip(live, outs):
            e.seconds = getattr(e, "seconds", 0.0) + dt
            e.feed(raw)
            if e.done and on_done:
                on_done(e)
    return [e.result() for e in episodes]
