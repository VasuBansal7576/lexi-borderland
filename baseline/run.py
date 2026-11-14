"""Frozen-weight local LLM evaluation. Never substitutes reference actions."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request
import urllib.error

from borderland.env import BorderlandEnv, NAMES
from borderland.world import canonical, digest

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = (ROOT / "baseline/public_rules.txt").read_text()
BASE = "http://127.0.0.1:18791"


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def request(route, value=None, timeout=300):
    req = urllib.request.Request(BASE + route, data=None if value is None else canonical(value).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"HTTP {error.code}: {error.read().decode()}")


class Server:
    def __init__(self, folder):
        self.folder, self.proc, self.log = folder, None, None
        self.starts = []

    def start(self):
        self.stop()
        runtime = ROOT / "runtime"
        for child in ("tmp", "cache", "hf"):
            (runtime / child).mkdir(parents=True, exist_ok=True)
        args = ["/opt/homebrew/bin/llama-server", "--model", str(ROOT / "models/tiny-aya-global/model.gguf"),
                "--alias", "tiny-aya-global-q4_k_m", "--ctx-size", "8192", "--parallel", "1",
                "--cache-ram", "0", "--no-context-shift", "--host", "127.0.0.1", "--port", "18791",
                "--no-webui", "--no-agent", "--offline", "--threads", "4"]
        env = {"PATH": "/usr/bin:/bin:/opt/homebrew/bin", "TMPDIR": str(runtime / "tmp"),
               "XDG_CACHE_HOME": str(runtime / "cache"), "HF_HOME": str(runtime / "hf"),
               "LLAMA_CACHE": str(runtime / "cache"), "METAL_CACHE_DIR": str(runtime / "cache")}
        self.log = (self.folder / f"server-{len(self.starts)}.log").open("w")
        self.proc = subprocess.Popen(args, cwd=ROOT, env=env, stdout=self.log, stderr=subprocess.STDOUT)
        record = {"pid": self.proc.pid, "args": args}
        self.starts.append(record)
        write(self.folder / "server-starts.json", self.starts)
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError("model server exited; inspect server log")
            try:
                if request("/health", timeout=2).get("status") == "ok":
                    return record
            except Exception:
                pass
            time.sleep(.25)
        raise TimeoutError("model server startup timed out")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        if self.log:
            self.log.close()


class Conversation:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM}]
        self.previous = None

    def observe(self, frame):
        obs = frame["observation"]
        if self.previous is None or obs["room"] != self.previous["room"]:
            compact = frame
        else:
            compact = {"ok": frame["ok"], "result": frame["result"],
                       "observation_update": {k: v for k, v in obs.items() if self.previous.get(k) != v},
                       "deleted": [k for k in self.previous if k not in obs]}
        self.messages.append({"role": "user", "content": canonical(compact)})
        self.previous = copy.deepcopy(obs)

    def assistant(self, text):
        self.messages.append({"role": "assistant", "content": text})


def parse(text):
    value = json.loads(text)
    if not isinstance(value, dict) or set(value) - {"reason", "tool", "args"}:
        raise ValueError("expected reason/tool/args JSON object")
    return {"tool": value["tool"], "args": value["args"]}


def stalled(events):
    """Diagnostic-only stop, not an environment loss or a rule modification."""
    return len(events) >= 8 and len(set(events[-8:])) == 1


def fixture(folder, room, notebook_probe=False):
    """Evaluator-only replay of a saved legal prefix, explicitly marked assisted."""
    world = json.loads((folder / "manifest.json").read_text())
    rows = [json.loads(line) for line in (folder / "trace.jsonl").read_text().splitlines()]
    env, chat = BorderlandEnv(world=world), Conversation()
    frame = {"ok": True, "result": {}, "observation": env.observe()}
    for row in rows:
        if notebook_probe:
            if env.room == 3 and row["action"]["tool"] == "notebook_write":
                break
        elif env.room == room:
            break
        chat.observe(frame)
        chat.assistant(canonical(row["action"]))
        result = env.step(row["action"])
        assert canonical(env.trace[-1]) == canonical(row), "reference fixture replay mismatch"
        if result.info["epoch_changed"]:
            chat = Conversation()
            frame = {"ok": True, "result": {}, "observation": env.observe()}
        else:
            frame = result.observation
    return env, chat, frame


def evaluate(server, name, world_folder, *, room=1, assisted=False, notebook_probe=False):
    folder = server.folder / name
    folder.mkdir(parents=True, exist_ok=False)
    if assisted:
        env, chat, frame = fixture(world_folder, room, notebook_probe)
    else:
        env = BorderlandEnv(world=json.loads((world_folder / "manifest.json").read_text()))
        chat, frame = Conversation(), {"ok": True, "result": {}, "observation": env.observe()}
    initial = len(env.trace)
    start_room = env.room
    server.start()
    starts_at = len(server.starts) - 1
    start = time.monotonic()
    wipes, completion_tokens, prompt_tokens, errors = [], 0, 0, []
    reason, requests, stall_events = None, 0, []
    write(folder / "manifest.json", env.world)
    write(folder / "prefix.json", {"assisted": assisted, "source": str(world_folder.relative_to(ROOT)),
                                   "replayed_actions": initial, "notebook_probe": notebook_probe})
    with (folder / "requests.jsonl").open("w") as req_log, (folder / "responses.jsonl").open("w") as res_log, (folder / "actions.jsonl").open("w") as actions:
        while not (env.terminated or env.truncated):
            if assisted and not notebook_probe and env.room != start_room:
                reason = "diagnostic_room_cleared"
                break
            if notebook_probe and env.room == 4 and env.data["unlocked"]:
                reason = "notebook_gate_passed"
                break
            if completion_tokens >= 32768:
                reason = "generation_budget"
                break
            chat.observe(frame)
            payload = {"model": "tiny-aya-global-q4_k_m", "messages": chat.messages,
                       "temperature": 0, "seed": 42, "max_tokens": min(1024, 32768-completion_tokens),
                       "response_format": {"type": "json_object"}, "cache_prompt": True}
            req_log.write(canonical({"index": requests, "server_pid": server.proc.pid, "public_frame": frame, "request": payload}) + "\n")
            req_log.flush()
            try:
                response = request("/v1/chat/completions", payload)
            except Exception as error:
                errors.append(str(error))
                reason = "context_overflow" if "context" in str(error).lower() else "inference_error"
                break
            res_log.write(canonical(response) + "\n")
            res_log.flush()
            requests += 1
            usage = response.get("usage", {})
            completion_tokens += usage.get("completion_tokens", 0)
            prompt_tokens += usage.get("prompt_tokens", 0)
            text = response["choices"][0]["message"].get("content", "")
            chat.assistant(text)
            try:
                action = parse(text)
            except Exception as error:
                errors.append(type(error).__name__ + ": " + str(error))
                action = {}  # ordinary invalid environment call; charged to budget
            old_room = env.room
            result = env.step(action)
            actions.write(canonical({"index": requests-1, "room": old_room, "raw": text,
                                     "action": action, "output": result.observation}) + "\n")
            actions.flush()
            print(f"{name} call={requests} room={old_room} tool={action.get('tool')} ok={result.observation.get('ok')} terminal={env.reason}", flush=True)
            stall_events.append(canonical({"action": action, "output": result.observation}))
            if result.info["epoch_changed"]:
                old_pid = server.proc.pid
                server.start()  # kills all model KV state, not just client messages
                chat = Conversation()
                frame = {"ok": True, "result": {}, "observation": env.observe()}
                wipes.append({"after_request": requests-1, "old_pid": old_pid, "new_pid": server.proc.pid,
                              "notebook": list(env.notebook), "fresh_frame": frame,
                              "bytes": sum(map(len, env.notebook))})
            else:
                frame = result.observation
            if assisted and not notebook_probe and stalled(stall_events) and not (env.terminated or env.truncated):
                reason = "diagnostic_stall_eight_identical_transitions"
                break
    report = {"name": name, "model": "CohereLabs/tiny-aya-global-GGUF", "quantization": "Q4_K_M",
              "assisted_prefix": assisted, "notebook_probe": notebook_probe, "start_room": start_room,
              "last_room": env.room, "success": env.success, "reason": reason or env.reason,
              "rooms_cleared_by_model": sorted(r for r, f in env.flags if f == "clear" and r >= start_room),
              "model_calls": requests, "total_calls_including_prefix": env.calls,
              "completion_tokens": completion_tokens, "summed_prompt_tokens": prompt_tokens,
              "score_including_prefix": env.score, "integrity": env.integrity, "wipes": wipes,
              "server_starts": server.starts[starts_at:], "errors": errors,
              "elapsed_seconds": round(time.monotonic()-start, 3), "world_fingerprint": env.world["fingerprint"],
              "source_hashes": {str(p.relative_to(ROOT)): digest(p.read_text()) for p in sorted((ROOT / "borderland").glob("*.py"))},
              "prompt_sha256": hashlib.sha256(SYSTEM.encode()).hexdigest(),
              "decoding": {"temperature": 0, "seed": 42, "max_tokens": 1024, "context": 8192,
                           "episode_generation_cap": 32768, "format": "JSON object grammar; no action-answer constraint"}}
    report["diagnostic_stall_guard"] = 8 if assisted and not notebook_probe else None
    # Verify complete trajectory including the reference prefix, without model calls.
    replay = BorderlandEnv(world=env.world)
    for row in env.trace:
        replay.step(row["action"])
        assert canonical(replay.trace[-1]) == canonical(row)
    report["exact_environment_replay"] = True
    (folder / "trace.jsonl").write_text("".join(canonical(r)+"\n" for r in env.trace))
    write(folder / "report.json", report)
    print("FINISHED " + canonical({k: report[k] for k in ("name", "reason", "last_room", "rooms_cleared_by_model", "model_calls")}), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("smoke", "natural", "diagnostic", "memory"), default="natural")
    parser.add_argument("--output", default="artifacts/model-baseline/run-v1")
    args = parser.parse_args()
    folder = (ROOT / args.output).resolve()
    if not folder.is_relative_to(ROOT):
        raise ValueError("output must be inside the project")
    folder.mkdir(parents=True, exist_ok=True)
    server = Server(folder)
    witness = ROOT / "artifacts/certification-v1/family-0000/phase-0-sigma-0"
    reports = []
    try:
        if args.suite == "smoke":
            server.start()
            response = request("/v1/chat/completions", {"model": "tiny-aya-global-q4_k_m",
                "messages": [{"role": "user", "content": "Return JSON with the key ready and boolean true."}],
                "max_tokens": 32, "temperature": 0, "response_format": {"type": "json_object"}})
            write(folder / "smoke.json", response)
            print(canonical(response), flush=True)
        elif args.suite == "natural":
            for phase, sigma in ((0, 0), (0, 1), (1, 0), (1, 1)):
                source = witness.parent / f"phase-{phase}-sigma-{sigma}"
                reports.append(evaluate(server, f"natural-p{phase}-s{sigma}", source))
        elif args.suite == "diagnostic":
            for room in range(2, 8):
                reports.append(evaluate(server, f"assisted-room-{room}", witness, room=room, assisted=True))
        else:
            reports.append(evaluate(server, "model-notebook-probe", witness, room=3, assisted=True, notebook_probe=True))
    finally:
        server.stop()
        write(folder / "summary.json", reports)


if __name__ == "__main__":
    main()
