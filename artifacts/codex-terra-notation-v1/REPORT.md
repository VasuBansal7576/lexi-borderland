# Terra rerun after public notation clarification

2026-11-14. One unassisted episode using native Codex, the user's ChatGPT subscription, and `gpt-6.1-terra` at low reasoning effort. The 100-call ceiling remained enforced. The episode ended after **14 calls** with **`bus_overload` in room 2**. Room 1 was cleared. No further live calls were made.

## What changed

Only `baseline/public_rules.txt` changed runtime behavior. The room-1 manual now explicitly defines `differences: [a,b,d]` as `(K[a]-K[b]) mod 4 = d`, and `phase_anchor: [g,o]` as `(K[g]-phase) mod 4 = o`. These are fixed encoding conventions, with no sampled values, door answers or worked solutions. The seven rooms, generator, rewards, evidence, action schemas, wipe and eight-line notebook were unchanged.

See [version notes](../../baseline/PUBLIC_NOTATION_V1.md), [change record](notation-change.json) and [preserved previous manual](public-rules-before.txt). Previous results remain observations under the previous wording.

## Observed trajectory

| Calls | Result |
| --- | --- |
| 1–2 | Read the glyph constraints and a retired inventory record. |
| 3–5 | Passed all three room-1 door banks. |
| 6 | Exited room 1. |
| 7–9 | Read the Switchboard schematic and used both permitted probes. |
| 10–11 | Set a switch and successfully energized the auxiliary bus. |
| 12–13 | Changed switches while planning the main-bus output incorrectly. |
| 14 | Energized the main bus at the wrong output; terminal overload. |

Room 1's choices followed a valid relative mapping: the unknown phase cancels in the door equation. Not reading the clock was therefore a legitimate deduction, not access to hidden state. In room 2, the two probes uniquely identify the matrix and zero bias using delivered evidence alone.

The circuit failure is arithmetic. Terra correctly identified the second matrix, but with all three channels on claimed output `110`. The public matrix gives `010`: enabling the final channel toggles both the first and third bits, not just the third. The first incorrect prediction appears in call 12, and is repeated before the fatal commitment in call 14. This diagnosis uses only the delivered schematic, probe outputs and switch states; no hidden manifest or reference solver. It was computed after the episode and never fed back to the model. See [diagnosis](diagnosis.json) and [saved actions](live/actions.json).

## Memory and budget limits

The model wrote no notebook entries: all eight lines remained empty. The episode ended before room 3 and the wipe; rooms 3–7 and post-wipe memory performance were not measured. The wipe implementation and notebook restrictions remain intact, with offline regression coverage. This is not an all-room success or a demonstrated memory failure.

Usage was **31,859 input tokens + 1,047 output tokens = 32,906 total tokens** across 14 completed calls. The remaining 86 calls were not spent. The [ledger](live-ledger.json) is sealed with `episode_finished:bus_overload`. No OpenCode, paid API-key fallback or retries were used. Token counts do not establish a dollar charge or the remaining subscription allowance.

## Verification

- [103 unit tests passed](tests.txt), including exact prompt-difference checks, identical generic notation across 64 worlds, and the fresh post-wipe request boundary.
- [All 64 existing environment certificates passed](environment-audit.json): 4,604 actions and 1,344 evidence citations checked against unchanged environment sources.
- [Independent live audit passed](live/audit.json): all 14 requests matched reconstructed public payloads, with no coding tools; 14 fresh threads and state directories; exact environment replay.
- The [run contract](live/run-contract.json) pins model, limits and source hashes. Runtime sources remained unchanged throughout this episode. The only runtime change relative to the previous episode was the public notation clarification.

This single episode at low reasoning effort supports a specific failure diagnosis, not an overall model-performance estimate or readiness for RL training. No training was performed. Work and evidence stayed inside Lexi; the external topic wiki was not consulted under the user's folder-only restriction.
