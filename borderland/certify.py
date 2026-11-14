"""Certify complete, balanced four-world families using only legal rollouts."""

import argparse
import json
from pathlib import Path
import time

from .run import ROOT, replay, run_episode
from .world import canonical, digest


def certify(start=0, families=16, output="artifacts/certification"):
    destination = Path(output).resolve()
    if not destination.is_relative_to(ROOT):
        raise ValueError("certificates must stay in the project folder")
    destination.mkdir(parents=True, exist_ok=True)
    all_rows, groups, start_time = [], [], time.monotonic()
    for seed in range(start, start + families):
        rows, gate_hashes = [], []
        base_phase = 2 * (seed % 2)
        for phase in (base_phase, base_phase + 1):
            for sigma in (0, 1):
                relative = f"family-{seed:04d}/phase-{phase}-sigma-{sigma}"
                folder = destination / relative
                report, env = run_episode(seed, overrides={"phase": phase, "sigma": sigma}, output=folder)
                replay_result = replay(folder)
                (folder / "replay.json").write_text(json.dumps(replay_result, indent=2) + "\n")
                gate_hash = None
                if report["seal"]:
                    gate = json.loads(canonical(report["seal"]["fresh_input"]))
                    gate["observation"]["notebook"] = []
                    gate_hash = digest(gate)
                    gate_hashes.append(gate_hash)
                row = {"seed": seed, "phase": phase, "sigma": sigma, "success": report["success"],
                       "calls": report["calls"], "score": report["score"], "error": report["error"],
                       "terminal_reason": report["terminal_reason"], "rooms_cleared": report["rooms_cleared"],
                       "fingerprint": report["world_fingerprint"], "gate_projection_hash": gate_hash,
                       "notebook_bytes": report["seal"]["bytes"] if report["seal"] else None,
                       "worker_restart": bool(report["seal"] and report["seal"]["old_pid"] != report["seal"]["new_pid"]),
                       "replay_exact": replay_result["all_outputs_and_state_hashes_match"],
                       "mode": env.world["mode"], "polarity": env.world["delta"],
                       "elapsed_seconds": report["elapsed_seconds"], "artifact": relative}
                rows.append(row)
                all_rows.append(row)
                print(f"family={seed} phase={phase} sigma={sigma} success={row['success']} calls={sum(row['calls'])} error={row['error']}", flush=True)
        balanced = len(gate_hashes) == 4 and len(set(gate_hashes)) == 1
        accepted = all(row["success"] and row["worker_restart"] and row["replay_exact"] for row in rows) and balanced
        groups.append({"seed": seed, "accepted": accepted, "identical_prelock_projection": balanced})
        (destination / "progress.json").write_text(json.dumps({"groups": groups, "worlds": all_rows}, indent=2) + "\n")
    accepted_seeds = [g["seed"] for g in groups if g["accepted"]]
    accepted_rows = [r for r in all_rows if r["seed"] in accepted_seeds]
    summary = {"candidate_families": families, "candidate_worlds": len(all_rows),
               "successful_worlds": sum(r["success"] for r in all_rows),
               "certified_families": len(accepted_seeds), "certified_worlds": len(accepted_rows),
               "uncertified_families": [g["seed"] for g in groups if not g["accepted"]],
               "accepted_seeds": accepted_seeds, "every_attempt_saved": True,
               "filter": "Accept entire four-world family only after all four legal solvers escape, restart, replay exactly and have identical non-notebook prelock observations.",
               "failure_interpretation": "An uncertified world may be feasible; this bounded solver failed to supply a certificate. No rules are relaxed and no failed attempt is deleted.",
               "modes": sorted({r["mode"] for r in accepted_rows}),
               "polarities": sorted({r["polarity"] for r in accepted_rows}),
               "max_notebook_bytes": max((r["notebook_bytes"] or 0 for r in all_rows), default=0),
               "min_score": min((r["score"] for r in accepted_rows), default=None),
               "max_score": max((r["score"] for r in accepted_rows), default=None),
               "elapsed_seconds": round(time.monotonic() - start_time, 3),
               "worlds": all_rows, "groups": groups}
    (destination / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = ["# Certificate corpus", "", f"{len(accepted_rows)} certified worlds in {len(accepted_seeds)} complete balanced families, from {len(all_rows)} candidate worlds.",
             "All attempts, including failures, are retained. A search failure is not an impossibility proof.", "",
             "| Seed | Phase | Registry bit | Legal escape | Calls | Notebook bytes | Exact replay | Witness |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in all_rows:
        lines.append(f"| {row['seed']} | {row['phase']} | {row['sigma']} | {row['success']} | {sum(row['calls'])} | {row['notebook_bytes']} | {row['replay_exact']} | [trace]({row['artifact']}/witness.md) |")
    lines += ["", "[Machine-readable summary](summary.json). These are development certificates, not an untouched ML holdout.", ""]
    (destination / "README.md").write_text("\n".join(lines))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--families", type=int, default=16)
    parser.add_argument("--output", default="artifacts/certification")
    args = parser.parse_args()
    summary = certify(args.start, args.families, args.output)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("worlds", "groups")}, indent=2))


if __name__ == "__main__":
    main()
