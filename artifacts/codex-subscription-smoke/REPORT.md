# GPT-6.1 Terra — native ChatGPT subscription smoke test

**Five live calls completed successfully using the official Codex client and the user's ChatGPT subscription.** No OpenCode client or paid API-key fallback was used for this run. The model stayed in room 1 while reading evidence; the evaluator stopped at the authorized five-call limit. There was no model death, invalid action, provider failure or loop-guard stop.

| Call | Model action | Observed outcome |
|---|---|---|
| 1 | Read catalog record `e8797` | Current glyph constraints, complete record |
| 2 | Read catalog record `e9634` | Retired inventory, complete record |
| 3 | Read catalog record `e7260` | Current district-clock notice, complete record |
| 4 | Read catalog record `e0883` | Current clock calibration pairs, complete record |
| 5 | Read catalog record `e0567` | District plan and transit links, complete record |

All five actions passed the independent typed-action validator and returned `ok=true`. The fifth model rationale inferred the clock phase from records it had actually read, then chose to investigate another record before committing. These were five distinct evidence reads, unlike the repeated rules inspection observed in the earlier Tiny Aya runs. This small sample establishes that the interface works for Terra; it does not establish superior overall performance.

## Limits and measured usage

- Exact requested model: `gpt-6.1-terra`, low reasoning effort.
- Five actual upstream requests, five completed responses, five legal actions; zero retries or extra model calls.
- **8,005 input tokens, 238 output tokens, 8,243 total tokens**, as reported by the provider. Output includes 10 reasoning tokens. No cached input was reported.
- Each request carried a 1,024-output-token cap. Every completion stayed below it. Public-request byte cap: 64,000.
- Stop: `five_call_limit`. Final room: 1, Dead or Alive. Environment remained active, integrity true, score 0. No room had yet been completed.
- No API key was used. This consumed ChatGPT/Codex subscription allowance. The response does not provide a dollar charge or remaining plan allowance, so neither is estimated here.

## What this does and does not prove

The native subscription route works. All five outgoing requests reconstruct exactly from the initial public observation and the model's own preceding actions. No hidden generator state, solver hints, gold notebook, forced prefix, wiki or project source was sent to the model. Each request used a fresh native thread and state directory. The unchanged environment replays exactly.

**No live wipe occurred, and rooms 2–7 were not reached.** This smoke test therefore does not establish seven-room success, notebook quality, post-wipe memory use or RL readiness. The run stopped because of the user-authorized call budget, not because we observed Terra fail to solve room 1. No training was started.

The actual native client also passed an offline post-wipe test containing exactly the eight-line notebook and one fresh public frame. That frame came from an existing scripted evaluator fixture and was delivered only to a fake endpoint. It is not a claim that Terra wrote those notes or solved earlier rooms.

## Verification

- [98 passing tests](tests.txt), including subscription-auth enforcement, exact prompt normalization, model pinning, five-attempt accounting, pending-attempt refusal, quota/error stops and output limits.
- [Live independent audit](live-v1/audit.json): five public-only requests, five unique native threads, five unique state directories and exact environment replay.
- [Offline actual-client audit](offline-v1/audit.json): fake repeated evidence policy stopped by the external loop guard after four calls.
- [Actual OS and wipe checks](boundaries/report.json): project-source and master-credential reads denied, outside writes denied, other local ports denied, duplicate request blocked, temporary per-call credentials removed.
- [64-world certificate audit](environment-audit.json): all original checks pass. No room, rule, reward, tool budget, notebook constraint or hidden-world generator was changed.
- [Source hashes captured before live calls](source-hashes-before-live.json).

Raw records: [attempt ledger](live-ledger.json), [actions](live-v1/actions.json), [episode report](live-v1/report.json), and per-call `public-messages.json`, `native-request.json`, `request.json`, `response.sse`, `cli.jsonl` and `verified.json` under `live-v1/call-01` through `call-05`. No credentials are included in those artifacts.

Implementation: [native bridge guide](../../baseline/codex_subscription/README.md).

Only project-local knowledge was used. The external topic wiki was not accessed because of the folder-only restriction. The earlier pending OpenCode login restart was rejected by automatic approval review after the user revoked OpenCode use; it was not retried. The user subsequently completed a separate native Codex sign-in.
