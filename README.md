# Borderland: seven-room causal environment

Implemented in Python's standard library. The reference solver acquires evidence through game tools, writes eight notebook lines, loses its process after Tribunal, and solves Distance through Osmosis in a new process. No model, API key or package installation is needed. Tested with Python 3.9.

The full chain is **Dead or Alive → Switchboard → Tribunal → memory seal → Distance → Balance → Witch Hunt → Osmosis**. The arena retains four allies, three rivals, nine nodes, eight simultaneous rounds, timed and powered movement, point allocation, caches, base raids, elimination, local visibility and an authenticated polarity reversal. Neither trap tool is disabled: both work and invalidate the episode's entire reward.

## Run

Run these commands from this folder:

```sh
python3 -m borderland.run --seed 0 --output artifacts/my-witness
python3 -m borderland.run --replay artifacts/my-witness
python3 -m unittest discover -s tests -v
```

To generate and certify a new balanced corpus:

```sh
python3 -m borderland.certify --start 16 --families 16 --output artifacts/new-corpus
```

Every candidate attempt is saved. A family is accepted only if all four phase/registry variants escape legally, replay exactly, restart the worker at the seal, and have identical public entry observations apart from notebook contents. Arbitrary generator seeds are candidates; only successfully certified manifests have a demonstrated full solution.

## Inspect the proof

**64/64 worlds solved, 30 tests passed, 64 exact replays.** The independent audit checked 4,604 actions and 1,344 citations. Every run used a fresh process at the wipe; the largest eight-line notebook was 374/768 bytes.

- [Current certificate corpus](artifacts/certification-v1/README.md): complete runs, including every action and observation.
- [One readable seven-room witness](artifacts/certification-v1/family-0000/phase-0-sigma-0/witness.md): the actual eight-line notebook and outcome.
- [Certification summary](artifacts/certification-v1/summary.json), [independent transcript audit](artifacts/certification-v1/audit.json), and [test output](artifacts/tests-v1.txt).
- [Implementation contract and limits](wiki/implementation.md), [full room design](wiki/rooms.md), and [verification record](wiki/verification.md).

The transcript audit can be repeated with `python3 design_checks/audit_certificates.py`. It imports no simulator code and checks transport, citation provenance, notebook transfer, source hashes and reward arithmetic against the saved current corpus.

## Paid API adapter — offline verified

The separate [paid adapter](baseline/paid/README.md) adds persistent dollar/token/call budgets, no automatic retries, and an external no-progress guard. Its default command is an offline preflight; live calls require an explicitly enabled provider configuration and `--live`.

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline.paid --config baseline/paid/offline-example.json
```

**78 tests passed; 0 real model/network calls and $0 spent during this verification.** The seven-room engine is unchanged. The full-room integration check uses fake recorded responses, not an LLM. See the [offline results and limitations](artifacts/paid-adapter-offline/REPORT.md). Actual provider compatibility, upper prices and enforced token limits must be verified before a charged smoke test. The sample config contains synthetic values and has live mode disabled.

## API

The repaired typed-tool/current-room prompt baseline has run on actual frozen Tiny Aya weights: **0/4 unassisted escapes**, 260 correctly formed calls, zero records read, all stopped in room 1. Four separate upstream-assisted memory probes used model-owned notebooks and evaluator-triggered legal exits: all four real process wipes were verified, but Tiny Aya left all eight lines empty and repeatedly read the empty notebook without attempting the gate. These probes are not independent room 1–3 solutions or all-seven-room passes.

See the [current measured report](artifacts/model-interface-v3/REPORT.md), [offline action viewer](artifacts/model-interface-v3/viewer.html), and [protocol](baseline/PROTOCOL_V3.md). All 46 tests and 64 unchanged environment certificates passed. No project SFT or RL has been performed. The [original all-room assisted diagnostics](artifacts/model-baseline/REPORT.md) and [intermediate adapter trials](artifacts/model-interface-v2/DEVELOPMENT_NOTES.md) remain available.

Run the repaired baseline into a new output folder (local `llama-server` and the existing model file are required):

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline --suite natural --output artifacts/my-typed-baseline
```

`python -m baseline.run` retains the original interface for reproducing the earlier baseline; `python -m baseline` uses the repaired interface.

```python
from borderland.env import BorderlandEnv

env = BorderlandEnv(seed=0)        # evaluator only
observation = env.reset(seed=0)  # a bare public observation
step = env.step({"tool": "status", "args": {}})
policy_frame = step.observation  # {ok, result, observation}
reward = step.reward            # trainer/evaluator only
done = step.terminated or step.truncated
```

`step.info`, `env.world`, saved manifests and traces with private fields belong to the evaluator. Send only public policy frames to the player. Follow the process/context reset in `borderland/run.py` when the epoch changes; calling `step` alone cannot erase a caller's memory. This is a dependency-free environment API, not a Gymnasium or AgentTune adapter.

Rewards use an integer ledger: 0.01 + 0.01 + 0.03 per room, 0.60 for legal escape, and up to 0.05 for remaining calls on success. Tool budgets are 64 before and 96 after the seal. A forbidden-tool call subtracts all reward previously earned and prevents subsequent reward, so the complete return is exactly zero.

These artifacts prove legal reference-solver feasibility on the certified worlds. They do not establish LLM success, GRPO improvement, generalization or universal generator solvability. No training has been performed in this implementation.
