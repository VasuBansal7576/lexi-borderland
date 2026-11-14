# OpenCode free smoke test — November 14, 2026

The isolated bridge is implemented and verified. **The live sweep was blocked by OpenCode's free quota on its first request. No model produced a game action.** This is a provider-limit result, not a reasoning failure or a seven-room completion result.

| Requested model | Pinned ID | Actual upstream attempts | Outcome |
|---|---|---:|---|
| Inkling 2 Small Free | `inkling-2-small-free` | 1 | HTTP 429, `FreeUsageLimitError`; zero actions |
| LongCat 2.5 Free | `longcat-2.5-free` | 0 | Not attempted after quota stop |
| Nemotron 3.5 Super VL Free | `nemotron-3.5-super-vl-free` | 0 | Not attempted after quota stop |
| GLM-5.3-Flash Free | `glm-5.3-flash-free` | 0 | Not attempted after quota stop; repeated user entry deduplicated |
| MiniMax M3.1 Flash Free | `minimax-m3.1-flash-free` | 0 | Not attempted after quota stop |

The response at approximately 14:32:10 IST included `Retry-After: 53870`, corresponding to **November 15, 2026, approximately 05:30 IST**. That is the provider's earliest retry hint, not a guarantee of availability. No retry or scheduled run was created. The live ledger is persistently halted across all models. We did not use another account, paid credentials, a paid model or any fallback.

The error response does not include billing usage. There were **zero paid requests** and no generated completion; we do not invent a usage total for the rejected request. The bridge requires a successful response to explicitly report cost zero and free billing before continuing.

## What was built

- Official OpenCode 2.2.7 ARM64 client installed only inside this project, with npm archive integrity verified. The existing personal OpenCode installation, credentials and session were not read or reused.
- A fresh private server, session and state directory per action. The client can read its own state and official executable, while macOS denies the rest of user/project content, previous call states and writes outside its state. It can connect only to its private control port and the local relay.
- The same public game messages as the existing harness, checked byte-content-wise after JSON decoding at the relay. No coding tools, ambient project instructions, solver data, hidden answers, reference actions or action repairs enter the live request.
- Exact free-model allowlist, signed-out authentication only, no redirects or retries, one admitted request per client process, five per model and 25 total. Each attempt has a 64,000-byte request ceiling and 1,024-token completion cap. The complete request is recorded before forwarding and the attempt is durably reserved before it can consume quota.
- Existing public-evidence loop guard and unchanged seven-room environment. The room-3 wipe discards public history; the notebook remains exactly eight ASCII lines, each at most 96 bytes. Fresh local state prevents access to earlier transcripts. No provider-side cache deletion is claimed.

## Verified evidence

- **89 unit tests pass**, including paid-adapter regressions, per-model/global call caps, pending-attempt accounting, persistent quota halt, exact-prompt validation, paid aliases and external-tool rejection, output limits and free-usage verification. See [test output](tests.txt).
- The **actual official client** passed offline tests for all five model IDs: 20 fake requests total, 20 distinct sessions/state directories, exact outward public messages and exact environment replay. A deliberately repeated inspection stopped after four calls per model. These are transport/guard fixtures, **not real model outputs**. See [offline audit](offline-v1/audit.json).
- Actual OS probes allowed the current-state canary but denied game-source reads, another call's state, outside writes and an unapproved local port. A second request was rejected before forwarding. See [boundary checks](boundaries/report.json).
- An actual-client post-wipe test forwarded the eight-line notebook and one fresh post-wipe frame to a **fake** endpoint. Its frame came from an existing offline scripted fixture; it was never sent to a real model. Live wipe performance remains unmeasured.
- The live request was independently reconstructed from the initial public observation, and its payload hash matches the durable ledger. It contained no hidden solution. See [live audit](live-v1/audit.json).
- The existing 64-world certificate audit verifies unchanged environment source, legal tools, evidence provenance and notebook transfer. See [environment audit](environment-audit.json).

The live-run bridge source and hashes were preserved before adding the persistent global quota-halt guard: [run source hashes](live-v1/source-hashes-at-run.json), [bridge at run](live-v1/bridge-at-run.py). The final guard's test and current source hashes are recorded separately in the audit artifacts.

## Raw records and next run

- [Provider quota response](live-v1/inkling-2-small-free/call-01/response.sse), [HTTP status and retry header](live-v1/inkling-2-small-free/call-01/upstream.json)
- [Durable live ledger](live-ledger.json), [episode report](live-v1/inkling-2-small-free/report.json)
- [Bridge usage and isolation contract](../../baseline/opencode_free/README.md)

The five-call-per-model live comparison remains outstanding until free service is available. Do not reset the ledger, rotate identities, or use paid fallback to bypass this stop. No RL training was started. A five-call smoke test cannot establish completion of all seven rooms, even when the provider is available.

Only project-local knowledge was read; the external topic wiki was not consulted because this request explicitly restricted local access to this folder.

Official sources checked: [free model catalog](https://opencode.ai/docs/console/models/), [client-only free inference and billing fields](https://opencode.ai/docs/console/api/inference/), [supported provider proxy and request overrides](https://opencode.ai/docs/providers/).
