# Tiny Aya after tool and prompt repairs

**Unassisted: 0/4 escapes.** The final-prompt runs made 260 model calls and read 0 records. All stopped in room 1. The separate upstream-assisted memory component completed 4 real server wipes and passed 0/4 gates. These are development-world diagnostics, not held-out results.

## What was repaired

- Exact typed arguments and required keys for every advertised tool, including nested team orders and eight ASCII notebook lines of at most 96 bytes each. All wrong choices and both maintenance traps remain representable; no hidden-state action masking.
- Current-room public laws and next-action instructions. Removed the misplaced room 3 reminder after the wipe; clarified clock versus phase, glyph versus sector, record reading and notebook versus evidence.
- Lossless public-history packing with an independently checked inverse, keeping exact evidence visible without inserting an evaluator summary. No action repair, gold notebook, answer injection or automatic evidence reading.
- Actual server destruction/restart and empty conversation at the seal. Only the model-written notebook crosses with normalized public state and fixed public instructions.

The entire `borderland/` engine, all seven rooms, rewards, budgets, maps and arena mechanics remain unchanged. The model remains official Tiny Aya Global Q4_K_M, frozen weights, temperature 0 / seed 42, 1,024 tokens/action and 8,192 context. No RL or SFT ran.

## Unassisted final-prompt episodes

| Phase / registry | Model calls | Records read | Stop | Cleared rooms |
|---|---:|---:|---|---|
| p0-s0 | 65 | 0 | tool_budget | [] |
| p0-s1 | 65 | 0 | tool_budget | [] |
| p1-s0 | 65 | 0 | tool_budget | [] |
| p1-s1 | 65 | 0 | tool_budget | [] |

Schema-invalid returned outputs: 0. The engine's separate `protocol_errors` counter is not a schema-validity measure; terminal budget exhaustion is recorded as `tool_budget`.

Representative actual output:

```json
{
  "reason": " glyphs A,B,C,D map bijectively to sectors 0..3. Current glyph constraints are not decoded yet.",
  "tool": "inspect",
  "args": {
    "object_id": "rules"
  }
}
```

The measured failure is evidence-acquisition/progress control: valid calls repeatedly inspect fixed rules instead of fetching the listed records. The prompt says how to read records, but the policy does not do it. No natural episode reaches room 2 or the memory seal; this run cannot establish independent performance in rooms 2–7.

## Model notebook and real wipe

This component starts from a legal upstream reference trajectory **before the reference notebook is written**. It includes successful earlier actions, so it is assisted upstream. Tiny Aya gets up to four unrestricted actions. If it does not exit, the evaluator performs only the already-legal exit, explicitly records ownership, and gives the model no credit for it. After process destruction/restart, Tiny Aya receives its own exact notebook and fresh room 4 public state, with up to four actions. No reference notebook or correct gate bits are supplied.

| Phase / registry | Model calls | Notebook bytes | Evaluator exit | New PID | Gate passed | Stop |
|---|---:|---:|---|---|---|---|
| 0 / 0 | 8 | 0 | True | 96282 → 96352 | False | component_step_cap |
| 0 / 1 | 8 | 0 | True | 96370 → 96448 | False | component_step_cap |
| 1 / 0 | 8 | 0 | True | 96473 → 96562 | False | component_step_cap |
| 1 / 1 | 8 | 0 | True | 96593 → 96653 | False | component_step_cap |

**Notebook preparation failed within this component cap:** all four notebooks contained eight empty lines. This tests preparation behavior under the stated four-action boundary; it does not establish how well Tiny Aya would use a useful self-written note. The completed room 3 flags were public, but the model repeatedly described the objectives as incomplete.

### Actual notebook: phase 0 / registry 0

Eight empty lines (0 bytes).

Actual post-wipe actions: notebook_read, notebook_read, notebook_read, notebook_read.

### Actual notebook: phase 0 / registry 1

Eight empty lines (0 bytes).

Actual post-wipe actions: notebook_read, notebook_read, notebook_read, notebook_read.

### Actual notebook: phase 1 / registry 0

Eight empty lines (0 bytes).

Actual post-wipe actions: notebook_read, notebook_read, notebook_read, notebook_read.

### Actual notebook: phase 1 / registry 1

Eight empty lines (0 bytes).

Actual post-wipe actions: notebook_read, notebook_read, notebook_read, notebook_read.

A passed gate alone does not demonstrate memory: a memoryless guess can pass one of four paired worlds. Inspect the actual note content and paired results before claiming retention. Evaluator-assisted exits and runtime errors are never counted as autonomous success.

## Verification and scope

- 46 tests passed. The 64 unchanged reference certificates passed: 4,604 actions, 1,344 citations and original source hashes.
- 0 schema-invalid outputs across the final natural/memory runs. Synthetic all-tools selection checks: 4/4 correct. These are interface tests, not game success.
- Every final-run request was reconstructed from public frames, every output matched its dispatched action, every trace replayed exactly, and source hashes matched. Wipe audits check distinct PIDs, no old history, exact notebook transfer and zero cached tokens on the first post-wipe response.
- The blank-notebook prompt and action schema are identical across the four hidden twins. The adapter imports no hidden-world generator or reference solver.
- Only this project folder was inspected for project data. The external wiki was not read under the folder-only restriction.
- Four paired worlds from one development family are not an estimate of generalization. These prompts were revised after inspecting earlier failures. No claim is made that the policy can solve all seven rooms or that RL will fix it.

## Reproduce and inspect

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline --suite natural --output artifacts/my-typed-rerun
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 evaluations/audit_v3.py
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 evaluations/audit_memory_v3.py
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m unittest discover -s tests -v
```

The memory runner `evaluations/memory_v3.py` saves to a fresh fixed output path and refuses overwrite. Change that output path for a new run. Do not run two local inference suites simultaneously on port 18791.

- [Offline action viewer](viewer.html), [natural audit](audit.json), [memory audit](memory/audit.json), [tests](tests.txt), [unchanged environment audit](environment-recheck.json).
- [Final protocol](../../baseline/PROTOCOL_V3.md), [typed interface protocol](../../baseline/PROTOCOL_V2.md).
- [Intermediate v2 trials, including harness/runtime failures](../model-interface-v2/DEVELOPMENT_NOTES.md).
- [Original baseline](../model-baseline/REPORT.md).
