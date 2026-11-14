# Verification record

Status: seven-room implementation, complete legal solver runs, deterministic replay and independent transcript audit passed on 2026-11-13. No trained-model result is claimed.

## Current executable evidence

Commands actually executed from the project folder:

```sh
python3 -m unittest discover -s tests -v > artifacts/tests-v1.txt 2>&1
python3 -m borderland.certify --families 16 --output artifacts/certification-v1
python3 design_checks/audit_certificates.py
```

- **30 tests passed**, recorded in [test output](../artifacts/tests-v1.txt). Coverage includes real process replacement, corrupted notebook lock bits, empty-notebook failure, exact full-episode replay, eight-line atomic limits, old-record inaccessibility, forbidden-tool reward clawback, independent arena fixtures, 800 random arena transition checks and the signed incident-time dependency.
- **64/64 candidate worlds cleared all seven rooms**, forming 16/16 complete balanced families. No failures were discarded. Both initial polarities and all three rival policy families occurred. Each trajectory reproduced every public output, private state hash and reward delta exactly. [Summary](../artifacts/certification-v1/summary.json), [corpus](../artifacts/certification-v1/README.md).
- Every run replaced the worker after Tribunal. The largest notebook was **374/768 bytes**, in exactly eight lines. All runs stayed within 64 calls before and 96 after the wipe. Scores ranged from **0.975625 to 0.97875**. Corpus generation, solving, artifact writing and replay took **78.018 seconds** on this machine; this is not an LLM rollout-speed measurement.
- An independent stdlib-only transcript audit checked **4,604 actions and 1,344 citations** across all 64 runs. All tools were advertised/legal, no trap was called, all cited evidence had been delivered, notebook transfer and fresh-frame transport matched, current source hashes matched the recorded implementation, and independent reward arithmetic agreed. [Audit result](../artifacts/certification-v1/audit.json), [audit source](../design_checks/audit_certificates.py).
- At the memory gate, all four members of each family had identical public non-notebook entry frames. Unit tests compare legal prelock query behavior and enumerate all four route/badge choices: each fixed choice succeeds on exactly one of four worlds. Thus a policy with no retained episode information has a **25% ceiling at that gate** under the balanced distribution. This is not a measured whole-episode success rate for a particular memoryless model.

The [readable witness](../artifacts/certification-v1/family-0000/phase-0-sigma-0/witness.md) shows the actual notebook, per-room call counts, process IDs and final arena ledger. Adjacent files contain all public inputs, solver outputs, evaluator manifest and transition trace. The manifest was never delivered to the policy.

This is a constructive existence proof for the certified worlds. Shared public physics code means replay is not an independent formal proof of the mechanics; hand-specified arithmetic/transition tests provide separate checks. The restricted worker is not claimed to be an OS security boundary against hostile arbitrary code. See [implementation scope](implementation.md).

## Earlier design-only verification

The subsequent [actual Tiny Aya baseline](../artifacts/model-baseline/REPORT.md) records 0/4 unassisted escapes, room2..7 reference-prefix diagnostics, and an actual model-server restart with an empty model notebook. Those observed failures are distinct from the successful reference-solver certificates above. No project training has run.

The following was performed before implementation and remains useful as a separate algebraic check.

## What this check can establish

Run from the project folder:

```sh
python3 design_checks/verify_design.py
```

The script exhaustively checks the two-bit gate's deterministic memoryless policies, exact reward arithmetic and invalidation, a finite set of three-round Balance games, battle point conservation and polarity reversal, an illustrative notebook's storage size, and local Markdown file-link targets. It uses only Python's standard library and writes [results.json](../design_checks/results.json).

The gate check is an algebraic proof under the stated information restrictions. It does not establish that a future implementation has no side channels. The Balance check explores actual finite strategies under the proposed local rules; it does not certify the complete world's resource budget.

## Observed results

The command above exited with code 0. The saved output reports:

- 256 deterministic memoryless policies, each evaluated over 16 balanced lock/challenge cases: best success exactly 1/4. Both relevant bit changes alter the correct action.
- Exact reward arithmetic: ordinary failure at most 0.32; legal success at least 0.95; repeated milestone events add zero; forbidden-tool clawback makes the total exactly zero.
- 96 Balance parameter sets checked with exact dynamic programming: all have a strategy with at least two wins. Exhaustive comparison of 9,261 fixed three-bid sequences found none that wins across all 96 cases.
- 1,740 unequal positive battle-group cases: transfer conserves total points, never makes a group negative, and reversing polarity reverses the winner.
- An illustrative eight-line note uses 465 of 768 allowed bytes, with a longest line of 70 characters. This is a storage example, not proof of full-world memory sufficiency.
- 51 local Markdown file targets exist within the allowed project folder on the post-implementation rerun (27 at the original design check). Fragment-anchor correctness and remote link freshness are not covered by this count.

Review also caught and corrected an overstatement: with only one wipe after R3, R6 information can remain in current context through R7. The core design therefore tests using a temporal amendment; it does not claim to force an R6 notebook edit. A second-wipe maintenance condition is explicitly separate.

## Remaining unverified work

- Solvability of arbitrary uncertified generator seeds, broad diversity and untouched structural holdout splits.
- Semantic correctness of notebook failure attribution.
- A hostile-code/OS isolation audit. The actual model-process restart and first-response cache state are verified in the November14 rerun below.
- AgentTune integration, token masks, learning rate, optimizer steps and reward finalization.
- Actual model success, training gains, inference cost or safety improvement.

These are engineering gates for the next phase, not excuses to relax the original idea. See [implementation order](decisions.md#implementation-order).


## 2026-11-14 — typed tool interface and prompt rerun

The model adapter now supplies strict per-tool JSON schemas, exact keys/types, nested order structures and an eight-line ASCII notebook contract. Current-room prompts replace the misplaced cross-room reminder; a lossless public-history codec preserves observed evidence. All wrong commitments and maintenance traps remain possible. The seven-room engine and rewards are unchanged.

Actual frozen Tiny Aya Q4_K_M: four natural development episodes, 260 schema-valid actions, 0 records read, 0 rooms cleared. Each exhausted its original tool budget repeating `inspect("rules")`. Four synthetic all-tools selection checks passed, including `read_record`, so the grammar did not force that action loop.

Four separately labeled upstream-assisted memory components replayed a legal prefix before the reference notebook. The model received four unrestricted pre-wipe actions, reread a record, and wrote no notebook facts. The evaluator then performed the already-legal exit. Each fresh model process received only the actual eight empty lines and normalized public state; it called `notebook_read` four times without trying `unlock`. All four distinct-PID restarts, zero cached tokens, exact transfers, model-visible prompts and replayed traces passed audit. This is not a test of independent upstream solving or of retention from a useful note.

Verification: 46 tests passed; 64 original source-hash certificates passed (4,604 actions and 1,344 citations); all 292 returned final-run actions were schema-valid; no final-run inference errors. No training occurred. Only this project folder was consulted for project knowledge; the external wiki was not read under the latest folder-only instruction.

Evidence: [measured report](../artifacts/model-interface-v3/REPORT.md), [natural transport audit](../artifacts/model-interface-v3/audit.json), [memory transport audit](../artifacts/model-interface-v3/memory/audit.json), [tests](../artifacts/model-interface-v3/tests.txt), [unchanged engine audit](../artifacts/model-interface-v3/environment-recheck.json), [intermediate failures](../artifacts/model-interface-v2/DEVELOPMENT_NOTES.md).


## 2026-11-14 — paid adapter, budget and loop guards (offline only)

A separate stateless Chat Completions-style adapter now supports exact pre-request dollar/token/call reservations, a durable locked ledger, no retries or argument repair, and a public-state no-progress guard. Timeouts and missing usage keep the reserved cost and halt. Budget/guard stops are explicitly evaluator stops; all original room and reward code is unchanged.

Evidence-driven change: the previous Tiny Aya runs spent 65 calls per episode repeating `inspect("rules")`; the new offline reproduction stops after 4 requests even though the cosmetic clock changes. Alternating passive actions and notebook rewrites cannot bypass the guard. A separate underfunded case makes 0 requests. A 76-action scripted fixture traverses all seven rooms and verifies the notebook-only supplied-context boundary without resetting the ledger. Recorded fake replies are never represented as model success.

Verification: 78 tests pass, including 32 paid-adapter tests with outbound socket/DNS calls forbidden; 64 unchanged environment certificates pass. Saved requests reconstruct exactly from public frames; budgets, source hashes and replay all pass independent audit. No live model, key, paid endpoint, or external wiki was used. Paid API compatibility and current model prices remain unverified. Provider-process/cache deletion is not claimed; the verified boundary is the stateless request payload.

Evidence: [offline report](../artifacts/paid-adapter-offline/REPORT.md), [tests](../artifacts/paid-adapter-offline/tests.txt), [transport and budget audit](../artifacts/paid-adapter-offline/audit.json), [unchanged environment audit](../artifacts/paid-adapter-offline/environment-audit.json), [usage contract](../baseline/paid/README.md).
