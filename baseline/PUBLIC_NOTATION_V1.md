# Public record notation clarification — 2026-11-14

The first full Terra attempt exposed an implicit glyph-record convention. The fixed room-1 laws now define the two generic encodings already implemented by the generator:

- `differences: [a,b,d]` encodes `(K[a]-K[b]) mod 4 = d`.
- `phase_anchor: [g,o]` encodes `(K[g]-phase) mod 4 = o`.

`K[g]` means the sector assigned to glyph `g`; modulo-four results are 0 through 3. No sampled mapping, phase, record ID, door choice, worked solution or solver output is included.

Only `baseline/public_rules.txt` changes the model-facing request. All room-2-through-7 laws, observations, evidence, action schemas, prompts and history codec remain unchanged. The room-1 explanation is fixed across worlds and is not carried into a fresh room-4 request after the wipe. No file in `borderland/` was changed.

The original text is preserved in `artifacts/codex-terra-notation-v1/public-rules-before.txt`; previous live traces and verdicts are retained. Their recorded prompt hashes identify the old wording and should not be treated as runs under this wording revision. The new run records the revised source hash in its contract.

Regression verification compares the entire initial public request with the prior run, permits only the two symbolic notation definitions, checks identical wording across 64 worlds, and checks the fresh post-wipe history. Existing environment and notebook tests remain applicable.
