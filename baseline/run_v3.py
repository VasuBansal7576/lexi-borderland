"""Real Tiny Aya rerun with typed tools and public-only lossless history."""
import argparse
import hashlib
import json
import time
import urllib.request
import urllib.error

from .run import ROOT, Server, write
from .interface_v3 import SYSTEM, PublicHistory, canonical, response_schema, validate, unpack, PARAMETERS
from borderland.env import BorderlandEnv


def infer(payload):
    # Preserve schema property order: reason, tool, args. The old sorted JSON
    # transport was appropriate for hashes, not for ordered grammar generation.
    req = urllib.request.Request("http://127.0.0.1:18791/v1/chat/completions",
        data=json.dumps(payload, separators=(",", ":")).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"HTTP {error.code}: {error.read().decode()}")


def prepare(source, room=1, memory=False):
    env = BorderlandEnv(world=json.loads((source / "manifest.json").read_text()))
    history = PublicHistory()
    frame = {"ok": True, "result": {}, "observation": env.observe()}
    if room == 1:
        return env, history, frame
    for line in (source / "trace.jsonl").read_text().splitlines():
        row = json.loads(line)
        if (memory and env.room == 3 and row["action"]["tool"] == "notebook_write") or (not memory and env.room == room):
            break
        history.add(frame)
        history.act(row["action"])
        result = env.step(row["action"])
        assert canonical(env.trace[-1]) == canonical(row)
        if result.info["epoch_changed"]:
            history = PublicHistory()
            frame = {"ok": True, "result": {}, "observation": env.observe()}
        else:
            frame = result.observation
    return env, history, frame


def diagnostic_cycle(events):
    if len(events) >= 8 and len(set(events[-8:])) == 1:
        return True
    return any(len(events) >= 4*n and all(events[-n:] == events[-(i+1)*n:-i*n] for i in range(1,4)) for n in range(2,5))


def evaluate(server, name, source, room=1, memory=False):
    folder = server.folder / name
    folder.mkdir(exist_ok=False)
    env, history, frame = prepare(source, room, memory)
    prefix_count = len(env.trace)
    assisted = room != 1
    start_room = env.room
    started = time.monotonic()
    server.start()
    starts_at = len(server.starts)-1
    write(folder / "manifest.json", env.world)
    write(folder / "prefix.json", {"assisted": assisted, "reference_actions": prefix_count,
                                   "source": str(source.relative_to(ROOT)), "memory_probe": memory})
    counts, completions, prompts, protocol_errors = 0, 0, 0, 0
    wipes, errors, cycles, reason = [], [], [], None
    with (folder / "requests.jsonl").open("w") as reqlog, (folder / "responses.jsonl").open("w") as reslog, (folder / "actions.jsonl").open("w") as actlog:
        while not (env.terminated or env.truncated):
            if assisted and not memory and env.room != start_room:
                reason = "diagnostic_room_cleared"
                break
            if memory and env.room == 4 and env.data["unlocked"]:
                reason = "model_notebook_gate_passed"
                break
            if completions >= 32768:
                reason = "generation_budget"
                break
            history.add(frame)
            # This inverse is an executable non-discarding check before inference.
            restored = unpack(history.pack())
            expected = json.loads(json.dumps(history.frames))
            for value in expected:
                value["observation"].pop("tools")
            assert restored == expected, "public history codec lost evidence"
            schema = response_schema(frame["observation"])
            payload = {"model": "tiny-aya-global-q4_k_m", "messages": history.messages(),
                       "temperature": 0, "seed": 42, "max_tokens": min(1024, 32768-completions),
                       "response_format": {"type": "json_schema", "json_schema": {"name": "borderland_action", "strict": True, "schema": schema}},
                       "cache_prompt": True}
            reqlog.write(json.dumps({"index": counts, "server_pid": server.proc.pid, "public_frame": frame, "request": payload}, separators=(",", ":"))+"\n")
            reqlog.flush()
            try:
                response = infer(payload)
            except Exception as error:
                errors.append(str(error))
                reason = "context_overflow" if "context" in str(error).lower() else "inference_error"
                break
            reslog.write(canonical(response)+"\n")
            reslog.flush()
            raw = response["choices"][0]["message"].get("content", "")
            counts += 1
            completions += response["usage"]["completion_tokens"]
            prompts += response["usage"]["prompt_tokens"]
            try:
                output = json.loads(raw)
                validate(output, schema)
                action = {"tool": output["tool"], "args": output["args"]}
            except Exception as error:
                errors.append(type(error).__name__+": "+str(error))
                output, action = {"invalid_raw_output": raw}, {}
            history.act(output)
            old_room = env.room
            result = env.step(action)
            protocol_errors += not result.observation["ok"]
            actlog.write(canonical({"index": counts-1, "room": old_room, "raw": raw, "action": action, "output": result.observation})+"\n")
            actlog.flush()
            print(f"{name} call={counts} room={old_room} tool={action.get('tool')} ok={result.observation['ok']} terminal={env.reason}", flush=True)
            cycles.append(canonical({"action": action, "output": result.observation}))
            if result.info["epoch_changed"]:
                old_pid = server.proc.pid
                server.start()
                history = PublicHistory()
                frame = {"ok": True, "result": {}, "observation": env.observe()}
                wipes.append({"after_request": counts-1, "old_pid": old_pid, "new_pid": server.proc.pid,
                              "notebook": list(env.notebook), "bytes": sum(map(len,env.notebook)), "fresh_frame": frame})
                cycles = []
            else:
                frame = result.observation
            if assisted and not memory and diagnostic_cycle(cycles) and not (env.terminated or env.truncated):
                reason = "diagnostic_no_progress_cycle"
                break
    replay = BorderlandEnv(world=env.world)
    for row in env.trace:
        replay.step(row["action"])
        assert canonical(replay.trace[-1]) == canonical(row)
    (folder / "trace.jsonl").write_text("".join(canonical(r)+"\n" for r in env.trace))
    report = {"name": name, "interface": "typed-v3", "model": "CohereLabs/tiny-aya-global-GGUF", "quantization": "Q4_K_M",
              "assisted_prefix": assisted, "notebook_probe": memory, "prefix_actions": prefix_count,
              "start_room": start_room, "last_room": env.room, "success": env.success,
              "reason": reason or env.reason,
              "rooms_completed_from_entry": [] if memory else sorted(r for r,f in env.flags if f == "clear" and r >= start_room),
              "model_calls": counts, "protocol_errors": protocol_errors, "completion_tokens": completions,
              "summed_prompt_tokens": prompts, "total_calls_including_prefix": env.calls,
              "score_including_prefix": env.score, "integrity": env.integrity, "wipes": wipes,
              "server_starts": server.starts[starts_at:], "errors": errors,
              "elapsed_seconds": round(time.monotonic()-started, 3), "exact_environment_replay": True,
              "world_fingerprint": env.world["fingerprint"],
              "source_hashes": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for parent in (ROOT/'borderland',ROOT/'baseline') for p in sorted(parent.glob('*.py'))},
              "system_sha256": hashlib.sha256(SYSTEM.encode()).hexdigest(),
              "decoding": {"temperature": 0, "seed": 42, "max_tokens": 1024, "context": 8192, "generation_cap": 32768,
                           "grammar": "all advertised tools; typed arguments only; no hidden-state action masking"}}
    write(folder / "report.json", report)
    print("FINISHED "+canonical({k:report[k] for k in ('name','reason','model_calls','last_room','rooms_completed_from_entry')}),flush=True)
    return report


def smoke(server):
    """Syntax tests with no game state or correct game answers."""
    server.start()
    cases = [
        ("submit_bid", "Use the argument bid, not value, and put the number in quotes."),
        ("notebook_write", "Write eight short printable ASCII lines containing arbitrary words, not game facts."),
        ("team_step", "Give a hold order to each of I,N,V,S. This is a synthetic schema test."),
        ("energize", "Put auxiliary|main as the bus_id value."),
    ]
    results = []
    for tool, instruction in cases:
        schema=response_schema({"tools":{tool:{}}})
        payload={"model":"tiny-aya-global-q4_k_m","messages":[{"role":"system","content":"Produce one JSON object with reason, tool, args. Parameter schema: "+json.dumps(PARAMETERS[tool])},{"role":"user","content":instruction}],
                 "temperature":0,"seed":42,"max_tokens":1024,"response_format":{"type":"json_schema","json_schema":{"name":"schema_smoke","strict":True,"schema":schema}}}
        response=infer(payload)
        output=json.loads(response["choices"][0]["message"]["content"])
        validate(output,schema)
        results.append({"tool":tool,"request":payload,"response":response,"schema_valid":True})
        write(server.folder/'smoke.json',results)
        print(canonical({"smoke_tool":tool,"schema_valid":True,"output":output}),flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--suite',choices=('smoke','natural','memory','diagnostic'),default='natural')
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    folder=(ROOT/args.output).resolve()
    if not folder.is_relative_to(ROOT):raise ValueError('stay in project')
    folder.mkdir(parents=True,exist_ok=False)
    server=Server(folder)
    source=ROOT/'artifacts/certification-v1/family-0000/phase-0-sigma-0'
    reports=[]
    try:
        if args.suite=='smoke':smoke(server)
        elif args.suite=='natural':
            for phase,sigma in ((0,0),(0,1),(1,0),(1,1)):
                reports.append(evaluate(server,f'natural-p{phase}-s{sigma}',source.parent/f'phase-{phase}-sigma-{sigma}'))
        elif args.suite=='memory':reports.append(evaluate(server,'model-notebook-probe',source,room=3,memory=True))
        else:
            for room in range(2,8):reports.append(evaluate(server,f'assisted-room-{room}',source,room=room))
    finally:
        server.stop()
        write(folder/'summary.json',reports)


if __name__=='__main__':main()
