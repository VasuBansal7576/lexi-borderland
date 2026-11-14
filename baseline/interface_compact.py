"""Compact public interface for 8K-context models (Tiny Aya). Same game, same evidence, same memory boundary.

Versus interface_v3, the prompt keeps every result delivered since the last wipe (all evidence stays visible) and the
full current-room log, but drops earlier rooms' step-by-step state diffs and free-text reasons, other rooms' rule text
(already fixed and public) and verbose tool schemas. Validation still uses the full response schema."""
import copy
import json
from .interface_v2 import LAWS, PARAMETERS, DESCRIPTIONS, decode_record_text, canonical
from .interface_v3 import PublicHistory, ROOM_REQUEST, SYSTEM


def compact_tools(observation):
    return {name: {"does": DESCRIPTIONS[name], "args": PARAMETERS[name].get("properties", {})}
            for name in observation["tools"]}


class CompactHistory(PublicHistory):
    def messages(self):
        obs = copy.deepcopy(self.frames[-1]["observation"])
        room = obs["room"]
        tools = compact_tools(obs)
        for key in ("tools", "rules"):
            obs.pop(key, None)
        evidence, seen = [], set()
        for frame in self.frames:
            if not frame["ok"]:
                continue
            r = decode_record_text(frame["result"])
            if not r or set(r) <= {"event"}:
                continue
            key = canonical(r)
            if key not in seen:
                seen.add(key); evidence.append(r)
        start = max(i for i, f in enumerate(self.frames) if i == 0 or self.frames[i - 1]["observation"]["room"] != f["observation"]["room"])
        log = []
        for i in range(start + 1, len(self.frames)):
            out = self.actions[i - 1]
            step = {"did": {k: out[k] for k in ("tool", "args") if k in out} if "invalid_output" not in out else "invalid output",
                    "ok": self.frames[i]["ok"], "result": decode_record_text(self.frames[i]["result"])}
            log.append(step)
        content = {"instruction": f"You are CURRENTLY in room {room}: {self.frames[-1]['observation']['name']}. Choose ONE next action.",
                   "room_laws": LAWS[room], "tools": tools,
                   "evidence_since_last_wipe": evidence, "this_room_log": log, "current_state": obs,
                   "respond_now": ROOM_REQUEST[room] + " Return reason, tool, args. Do not copy the state or invent IDs."}
        return [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(content, separators=(",", ":"), ensure_ascii=True)}]
