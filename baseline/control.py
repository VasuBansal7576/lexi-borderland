"""Post-baseline prompt controls; not counted as seven-room episodes."""
import json
from pathlib import Path
from .run import ROOT, SYSTEM, Server, request, parse, write
from borderland.env import BorderlandEnv
from borderland.world import canonical


def main():
    folder = ROOT / "artifacts/model-baseline/interface-controls"
    folder.mkdir(parents=True, exist_ok=True)
    world = json.loads((ROOT / "artifacts/certification-v1/family-0000/phase-0-sigma-0/manifest.json").read_text())
    controls = [
        ("full_manual_explicit_turn", SYSTEM),
        ("concise_current_room", 'You play a tool-driven game. Survive using only the public evidence. Read records before irreversible choices. Return exactly one JSON object with "reason", "tool", "args" using the advertised tool and actual argument values, never schema placeholders. No outside tools are available.'),
    ]
    server, rows = Server(folder), []
    try:
        for name, system in controls:
            env = BorderlandEnv(world=world)
            server.start()
            public = {"ok": True, "result": {}, "observation": env.observe()}
            payload = {"model": "tiny-aya-global-q4_k_m", "temperature": 0, "seed": 42, "max_tokens": 1024,
                       "response_format": {"type": "json_object"}, "messages": [
                           {"role": "system", "content": system},
                           {"role": "user", "content": canonical(public) + '\nYou are currently in ROOM 1, Dead or Alive. Choose your next tool action now. Use real values from this observation; do not copy type descriptions as values.'}]}
            response = request("/v1/chat/completions", payload)
            raw = response["choices"][0]["message"]["content"]
            try:
                action = parse(raw)
            except Exception:
                action = {}
            result = env.step(action)
            row = {"name": name, "scope": "single-turn framing control, not a full episode or an improved success rate",
                   "request": payload, "response": response, "action": action, "output": result.observation}
            rows.append(row)
            print(canonical({"name": name, "raw": raw, "accepted": result.observation["ok"]}), flush=True)
    finally:
        server.stop()
        write(folder / "results.json", rows)


if __name__ == "__main__":
    main()
