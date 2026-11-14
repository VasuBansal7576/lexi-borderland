"""Run and replay an evidence-only seven-room certificate, entirely locally."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import select
import subprocess
import sys
import time

from .env import BorderlandEnv
from .world import canonical, digest


ROOT = Path(__file__).resolve().parents[1]


class Worker:
    def __init__(self):
        self.proc = subprocess.Popen([sys.executable, "-I", "-S", str(ROOT / "borderland" / "worker.py")],
            cwd=ROOT, env={"PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        self.hello = self.receive(30)

    def receive(self, timeout=300):
        ready, _, _ = select.select([self.proc.stdout], [], [], timeout)
        if not ready:
            raise TimeoutError("solver exceeded per-action compute limit")
        line = self.proc.stdout.readline()
        if not line:
            error = self.proc.stderr.read() if self.proc.poll() is not None else "worker closed stdout"
            raise RuntimeError(error)
        return json.loads(line)

    def ask(self, message):
        self.proc.stdin.write(canonical(message) + "\n")
        self.proc.stdin.flush()
        return self.receive()

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        for pipe in (self.proc.stdout, self.proc.stderr):
            pipe.close()


def run_episode(seed=0, *, overrides=None, output=None, progress=False):
    source_hashes = {p.name: digest(p.read_text()) for p in sorted((ROOT / "borderland").glob("*.py"))}
    env = BorderlandEnv(seed, overrides=overrides)
    worker = Worker()
    workers = [worker.hello]
    policy_inputs = []
    policy_outputs = []
    message = {"ok": True, "result": {}, "observation": env.observe()}
    start = time.monotonic()
    seal = None
    error = None
    previous_room = None
    try:
        while not env.terminated and not env.truncated:
            if progress and env.room != previous_room:
                print(f"seed={seed} room={env.room} calls={sum(env.calls)} elapsed={time.monotonic()-start:.1f}s", flush=True)
                previous_room = env.room
            policy_inputs.append(message)
            response = worker.ask(message)
            policy_outputs.append(response)
            if "error" in response:
                error = response["error"]
                break
            if response.get("action") is None:
                error = "policy stopped before terminal state"
                break
            result = env.step(response["action"])
            if result.info["epoch_changed"]:
                old_pid = worker.hello["pid"]
                worker.close()
                # Do not forward the previous response, reward, index or context.
                worker = Worker()
                workers.append(worker.hello)
                message = {"ok": True, "result": {}, "observation": env.observe()}
                seal = {"after_action": len(env.trace) - 1, "old_pid": old_pid, "new_pid": worker.hello["pid"],
                        "notebook": list(env.notebook), "bytes": sum(map(len, env.notebook)),
                        "maximum_line_bytes": max(map(len, env.notebook)), "fresh_input": message}
            else:
                message = result.observation
    except Exception as exc:
        error = type(exc).__name__ + ": " + str(exc)
    finally:
        worker.close()
    report = {"seed": seed, "overrides": overrides or {}, "world_fingerprint": env.world["fingerprint"],
              "implementation_hashes": source_hashes, "python_version": sys.version.split()[0],
              "success": env.success, "error": error, "terminal_reason": env.reason,
              "rooms_cleared": sorted(r for r, flag in env.flags if flag == "clear"),
              "calls": env.calls, "score": env.score, "score_units": env.score_units,
              "integrity": env.integrity, "seal": seal, "workers": workers,
              "elapsed_seconds": round(time.monotonic() - start, 4),
              "final_arena": asdict(env.arena) if env.arena else None,
              "last_diagnostics": policy_outputs[-1].get("diagnostics", {}) if policy_outputs else {}}
    if output:
        folder = Path(output).resolve()
        if not folder.is_relative_to(ROOT):
            raise ValueError("artifacts must remain inside this project")
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "manifest.json").write_text(canonical(env.world) + "\n")
        (folder / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        (folder / "trace.jsonl").write_text("".join(canonical(e) + "\n" for e in env.trace))
        (folder / "policy-inputs.jsonl").write_text("".join(canonical(e) + "\n" for e in policy_inputs))
        (folder / "policy-outputs.jsonl").write_text("".join(canonical(e) + "\n" for e in policy_outputs))
        (folder / "witness.md").write_text(witness_markdown(report, env.trace))
    return report, env


def witness_markdown(report, trace):
    counts = {r: 0 for r in range(1, 8)}
    room = 1
    for row in trace:
        counts[room] += 1
        room = row["policy_output"]["observation"]["room"]
    lines = ["# Seven-room solver witness", "", f"Success: **{report['success']}**. Seed {report['seed']}; interventions {report['overrides']}.",
             f"World fingerprint: `{report['world_fingerprint']}`.", "",
             "The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.",
             "This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.", "",
             "| Room | Tool calls | Cleared |", "| --- | ---: | --- |"]
    for r, count in counts.items():
        lines.append(f"| {r} | {count} | {r in report['rooms_cleared']} |")
    if report["seal"]:
        seal = report["seal"]
        lines += ["", "## Actual notebook at the wipe", "",
                  f"Eight lines; {seal['bytes']} bytes total; longest line {seal['maximum_line_bytes']} bytes.",
                  f"Old process {seal['old_pid']} exited; new process {seal['new_pid']} started with an empty tool-result envelope and the public room-4 observation.",
                  "", "```text", *seal["notebook"], "```"]
    lines += ["", "## Outcome", "", f"Score: {report['score']}. Integrity: {report['integrity']}. Reason: {report['terminal_reason']}.",
              f"Call budget use: {report['calls'][0]}/64 before the wipe, {report['calls'][1]}/96 after it.",
              f"Error, if any: {report['error']}.", ""]
    if report["final_arena"]:
        arena = report["final_arena"]
        lines += [f"Final allied points: {sum(arena['ap'])}; rival points: {sum(arena['bp'])}.",
                  f"Allies remaining: {sum(p > 0 for p in arena['ap'])}. Completed arena rounds: {arena['round'] - 1}.",
                  f"Cache collected: {arena['collected']}; positive post-amendment battle round: {arena['post_transfer']}.", ""]
    lines += ["Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),",
              "[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.", ""]
    return "\n".join(lines)


def replay(folder):
    folder = Path(folder).resolve()
    if not folder.is_relative_to(ROOT):
        raise ValueError("only project artifacts may be replayed")
    world = json.loads((folder / "manifest.json").read_text())
    env = BorderlandEnv(world=world)
    rows = [json.loads(line) for line in (folder / "trace.jsonl").read_text().splitlines()]
    for index, row in enumerate(rows):
        result = env.step(row["action"])
        actual = env.trace[-1]
        if canonical(actual) != canonical(row):
            raise AssertionError(f"replay mismatch at step {index}: {row['action']['tool']}")
    report = json.loads((folder / "report.json").read_text())
    assert env.score_units == report["score_units"]
    assert env.success == report["success"]
    return {"replayed_steps": len(rows), "all_outputs_and_state_hashes_match": True,
            "success": env.success, "score": env.score}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", default="artifacts/witness")
    parser.add_argument("--replay")
    parser.add_argument("--phase", type=int)
    parser.add_argument("--sigma", type=int)
    args = parser.parse_args()
    if args.replay:
        print(json.dumps(replay(args.replay), indent=2))
        return
    overrides = {k: v for k, v in (("phase", args.phase), ("sigma", args.sigma)) if v is not None}
    report, _ = run_episode(args.seed, overrides=overrides, output=args.output, progress=True)
    print(json.dumps({k: v for k, v in report.items() if k not in ("seal", "workers", "last_diagnostics")}, indent=2))
    if not report["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
