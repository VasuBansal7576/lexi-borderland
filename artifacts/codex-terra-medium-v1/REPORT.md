# Terra episode at medium effort (live)

2026-11-14, 16:58–17:00 IST. One unassisted episode: native Codex CLI, the user's ChatGPT subscription, `gpt-6.1-terra`, reasoning effort **medium** (6,144-token output cap), certified world `family-0000/phase-0-sigma-0`, 100-call ceiling. Started by the user in Terminal via `run-terra-medium.command`.

## Result
- 24 calls, all completed; 73,313 input + 1,657 output tokens. Ledger not halted.
- Room 1 (Dead or Alive) cleared. Room 2 (Switchboard) cleared — first live model to do so.
- Room 3 (Tribunal): ended at call 24 with `invalid_certification`. Score 0.11. No wipe reached. Exact replay: true.

## Diagnosis (evaluator-side, after the run)
Terra's room-3 answer was **correct**: mapping `{ash:I, birch:V, cedar:N, dusk:S}` and forged credential `c9410` both equal the hidden manifest.
The episode failed only on the citation check (`env.py:376`), which requires evidence tags `clock, glyphs, circuit, identity, registry`.
Terra cited `e1986 (identity), e0883 (clock), e0247 (circuit), e4188 (registry)` — missing `glyphs` (`e8797`, which it had read).

The public rules only say "Certify the identity mapping with actual evidence IDs". The five-tag requirement is not public, and Terra's derivation did not use the glyph record (it read the clock directly). The reference solver avoids this by citing every ID it has collected (`solver.py:226`). Room 6 (`accuse`, `env.py:454`, tags `roles, access, anchor, tamper`) has the same unstated requirement; the solver cites exactly those four.

Conclusion: an environment specification gap, not a model reasoning error. The 64/64 certificate shows feasibility for a policy that knows the hidden citation rule, not for one that only sees the public rules.

## Harness change for this run
`LEXI_TERRA_EFFORT` (default `low`, unchanged behavior) selects effort, output cap and timeouts in `baseline/codex_subscription/bridge.py`; recorded in `live/run-contract.json`. 103/103 tests passed after the change.
