# Budgeted paid-API adapter

This adapter is implemented and tested **offline**. No provider has been contacted, no real API key is needed for tests, and no credits were spent. The checked-in configuration is deliberately non-live and uses a nonexistent endpoint plus synthetic prices.

The existing local Tiny Aya runner stays unchanged. The paid runner is a separate command:

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline.paid \
  --config baseline/paid/offline-example.json
```

That command is a **preflight only**: it prints reservation limits and public-message byte size, reads no API credential, opens no ledger, and makes no HTTP request. Bytes are not presented as a token estimate.

To exercise the guarded runner with a fake, deliberately looping policy, use new artifact names:

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline.paid \
  --config baseline/paid/offline-example.json --offline-demo \
  --output artifacts/my-paid-offline-demo \
  --ledger artifacts/my-paid-offline-ledger.json
```

No actual model is used. Ledger costs in this mode are simulated accounting values, not money spent.

## What is supported

A stateless HTTPS **Chat Completions-style JSON contract**: one text completion, JSON-object response mode, explicit output-token cap, no streaming, no remote tools, and `store=false`. Providers must support these exact fields and the standard `choices`/`usage` response shape. The output-limit field is configured as either `max_tokens` or `max_completion_tokens`.

This is not a verified integration with every provider, the Responses API, or Anthropic's native Messages API. It has no SDK dependency. Since provider-specific strict JSON Schema subsets differ, it sends readable typed tool definitions in the existing public prompt and validates the returned action against the exact current-room schema **before dispatch**. It does not silently fall back to another format, repair arguments, or spend another call asking for a correction. This differs from llama.cpp's decoder-enforced argument grammar; invalid paid-model output stops the evaluation after the first response.

The live transport requires **both** `--live` and `live_enabled: true` in a separate configuration. It reads only the explicitly named API-key environment variable, never searches local credential files, and never writes the key to artifacts. Do not put a secret into the config or command line. Redirects, implicit proxies, and automatic retries are disabled. Each request has a fresh client request ID; there is no previous-response or conversation ID.

## Budget contract

A single shared ledger enforces four limits before every request:

1. Total request count, including ambiguous failed attempts.
2. Cumulative input tokens, including outstanding reservations.
3. Cumulative output tokens, including outstanding reservations.
4. A dollar ceiling using exact decimal arithmetic.

The reservation is:

```
(provider full context window × input upper price
 + requested output limit × output upper price) / 1,000,000
```

This deliberately reserves the full provider-enforced input ceiling, not a character heuristic. It may refuse a request whose expected cost would have fit. After valid usage arrives, the ledger replaces that reservation with reported input/output tokens at the configured upper rates. It assumes no cached-input discount. The request output cap must include all billable completion/reasoning tokens under the chosen provider's contract.

**A live configuration must supply verified values:** the exact model/endpoint, its full enforced context window, supported output-limit parameter, and upper input/output rates across applicable pricing tiers. `context_window` is not a knob to lower just to make a request affordable. This adapter assumes token-only billing, accurate usage totals, and no extra fixed, tool, or routing fees. Do not enable it for a provider that does not satisfy that contract. No live pricing is embedded or claimed to have been checked.

The software guarantees admission against that declared contract; it cannot guarantee an invoice if the provider violates its token limits, omits billable usage, changes prices, or has charges outside the contract. Usage above the declared limits is recorded and halts the ledger immediately, but an already-sent request cannot be recalled. The actual provider/model still needs a separately authorized, tightly capped compatibility smoke test before a larger run.

A reservation is persisted with an atomic replacement and filesystem sync **before transport**. The ledger is exclusively locked for the runner's lifetime, with thread-safe reservations. Reopening it preserves spend and counts; a changed configuration is rejected. A pending request after a crash, timeout, HTTP error, missing usage, or malformed usage retains its full reservation and blocks further requests. There is no automatic refund, retry, or reconciliation. Refused/truncated/invalid responses with valid usage are charged once and stop. Storage failures stop before further network activity.

Use the **same ledger path** for runs sharing one budget. A different path is a separate budget, not an account-wide limit. Do not delete/reset a ledger to evade a cap. Ambiguous charges require checking provider billing before any deliberate reconciliation. The current runner does not automatically resume a partially played episode.

## Loop guard and unchanged game

The default spending guard stops after three consecutive actions with neither newly delivered public evidence nor visible task-state progress. The first rules inspection is new evidence, so the observed room-1 rules loop stops after **four requests**, before a fifth paid request. Changing reasoning text, alternating passive tools, or rewriting notebooks does not reset it. It ignores room1's cosmetic inspection clock; legitimate Distance waits and arena rounds remain progress. Newly read pages and different testimony can reset it. Errors do not become progress just because time passed.

This is an **external evaluator stop**, recorded separately from game death, truncation, reward, or victory. It may censor an inefficient policy that a full-budget benchmark would have continued. It does not change room mechanics, substitute a next action, choose a safe answer, alter rewards, restrict wrong commitments, or disable the maintenance traps. The global call/token/dollar caps bound runs even when a changing state prevents loop detection.

The paid CLI starts a natural episode in room1. It has no reference prefix, reference notebook, forced exit, or reference-solver fallback. All seven original rooms remain intact.

## Wipe and information boundary

The runner sends only fixed public instructions, the current public observation, and the lossless history of legal tool-visible frames. Manifests, private traces, reward ledgers, billing counters, and guard internals are evaluator artifacts and never enter the model messages.

At the room3 exit it discards the entire supplied history and guard history. The next request contains only the actual eight notebook lines, normalized fresh room4 state, and fixed public instructions. Budget accounting **does not reset**. No previous response/conversation ID is reused. This verifies the API request boundary; it does **not** claim remote provider cache deletion or a provider-process restart. The prompt explicitly describes this distinction.

## Offline verification

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 design_checks/audit_certificates.py
```

The paid-adapter tests replace socket connection, DNS and datagram operations with failures and assert no such operation was attempted. Provider responses and HTTP openers are fakes, including tests of authentication headers and errors. The all-seven-room integration fixture uses recorded legal actions as **fake provider replies**; it proves harness behavior, not LLM success. No gold actions or notes are inserted into the prompts. A separate counterfactual check verifies identical blank-notebook post-wipe messages across hidden twins.

See the [saved offline report](../../artifacts/paid-adapter-offline/REPORT.md), [test output](../../artifacts/paid-adapter-offline/tests.txt), and [scripted proof summary](../../artifacts/paid-adapter-offline/proof/summary.json). All project work and artifacts stay in Lexi; the external desktop wiki was not read under the folder-only restriction.
