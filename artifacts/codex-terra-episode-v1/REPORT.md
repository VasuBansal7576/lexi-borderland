# Terra unassisted episode — November 14, 2026

**The episode ended at call 8 in room 1, on the second door bank.** It did not reach the memory wipe. The immediate error was a reversed glyph-difference interpretation, but the public record format leaves subtraction direction implicit. This is a specification gap that confounds attributing the failure solely to model reasoning.

## Run contract and result

- Native official Codex CLI, ChatGPT subscription, exact model `gpt-6.1-terra`, low reasoning effort.
- One fresh, unassisted episode on the same certified world as the earlier smoke test. No reference actions, gold notes, answer repairs or forced transitions.
- Authorized ceiling: 100 actual inference attempts. **Used: 8**, all completed. No retries, API-key fallback, OpenCode execution, provider errors or output truncation.
- Existing 1,024-output-token and 64,000-public-request-byte limits, original room tool budgets and three-stall external loop guard retained.
- **14,367 input tokens + 448 output tokens = 14,815 total.** These are reported tokens, not an estimate of subscription dollars or remaining allowance.
- Terminal reason: `unsafe_door`, not the spending cap or loop guard. Integrity remained true. Score: 0.01.
- The live ledger was sealed after the episode with `episode_finished:unsafe_door`. The unused 92-call allowance is not being used for another episode. No training or rerun was started.

## Progress

| Room | Result |
|---|---|
| 1 — Dead or Alive | Read all six records; passed bank 0; died at bank 1 |
| 2 — Switchboard | Not reached |
| 3 — Tribunal | Not reached |
| 4 — Distance | Not reached |
| 5 — Balance | Not reached |
| 6 — Witch Hunt | Not reached |
| 7 — Osmosis | Not reached |

Calls 1–6 read six different catalog records, including the current clock and glyph constraints and distinguishable retired distractors. Call 7 chose D and passed the first bank. Call 8 chose C and made a fatal commitment at the next bank. All eight responses were valid JSON actions matching the advertised tool schema. An action's `ok=true` reports successful dispatch; it does not mean the commitment was safe.

No notebook writes occurred. Its final contents were **eight empty lines**, saved in [notebook.json](notebook.json). There were zero wipes and zero post-wipe decisions. Notebook compression, delayed recall and rooms 2–7 remain unmeasured.

## Why it died, and the specification problem

The delivered glyph record contains:

```json
{"differences":[["A","B",1],["B","C",2],["C","D",3]],"phase_anchor":["A",0]}
```

The current clock record identifies phase 0. The public rules require a bijection between glyphs and sectors, but neither the public rules nor this record explicitly defines the direction of each `differences` triple.

The generator and reference solver implement `(K[a] - K[b]) mod 4 = d` for `[a,b,d]`. Terra instead used `(K[b] - K[a]) mod 4 = d`:

| Interpretation | A | B | C | D | Bank 0 prediction | Bank 1 prediction |
|---|---:|---:|---:|---:|---|---|
| Implemented first minus second | 0 | 3 | 1 | 2 | D | B |
| Terra's second minus first | 0 | 1 | 3 | 2 | D | C |

Both interpretations produce a unique mapping under their respective convention. Both predict D at bank 0, so passing that bank does not disambiguate them. At bank 1, the visible pulse was 2 and the required sector was `(0+1+2) mod 4 = 3`. Terra correctly evaluated that equation but selected C using its reversed mapping. Under the implemented convention, sector 3 maps to B.

This is **not a changing-clock or pulse-timing bug**: the displayed pulse matches the bank's fixed pulse used by the environment. It is also not a missing-record or malformed-tool failure. The model had read all catalog records.

The two-convention diagnostic enumerates mappings using only the saved public records and observations. The implementation convention was identified by evaluator-only source inspection **after the run**. Nothing from that diagnosis was sent to the model. See [diagnosis.json](diagnosis.json) and [diagnostic script](../../evaluations/diagnose_terra_room1.py).

## Next step before training

Explicitly document the generic record semantics in the public interface:

- `[a,b,d]` means `(K[a] - K[b]) mod 4 = d`.
- A phase anchor `[g,o]` means `(K[g] - phase) mod 4 = o`.

These explain the data format without supplying a world's mapping or safe doors. Preserve the recorded failure, version that wording change, and then run another separately authorized episode. No prompt, room or rule was changed during or after this live run. One low-reasoning episode with this ambiguity cannot establish Terra's general solving ability or a memory-training target.

## Verification and artifacts

- [101 passing tests](tests.txt), including exact 100-attempt enforcement and refusal to raise an existing ledger's limit.
- [Offline actual-client test](offline/audit.json): the larger allowance did not weaken the loop guard; a repeated fake inspection stopped at four calls, with no external inference.
- [Live independent audit](live/audit.json): eight exact public-only payloads, eight fresh native threads/state directories, no coding tools, immutable source hashes, and exact environment replay.
- [64-world certificate audit](environment-audit.json): unchanged environment and solver certificates still pass. This checks implementation consistency and legal evidence provenance; it does not prove that every record's natural-language semantics are explicit. The present run exposed that limitation.
- [Run contract](live/run-contract.json), [sealed attempt ledger](live-ledger.json), [raw actions and model rationales](live/actions.json), [episode report](live/report.json).

All work and local inspection stayed inside Lexi. The external topic wiki was not accessed under the folder-only restriction. Model-facing messages excluded this report, diagnosis, hidden manifests, source files and prior run artifacts.
