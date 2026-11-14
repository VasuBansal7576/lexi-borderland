# Paid adapter: offline verification

**Implemented and verified offline. 0 real model calls, 0 network calls, $0 credits spent.** Live mode is disabled in the checked-in configuration. No actual provider compatibility or current pricing is claimed.

## Implemented

- A separate stateless HTTPS Chat Completions-style adapter, with typed tool definitions in the prompt and exact action validation before dispatch. JSON-object mode is used; provider-specific decoder-enforced argument schemas are not assumed.
- Pre-request dollar, call-count, cumulative input-token and cumulative output-token admission checks. Each request reserves the full declared provider context ceiling plus capped completion cost using exact decimal arithmetic.
- A durable, exclusively locked ledger shared across runs. Reservations are synced before transport. Reopening preserves totals; changing the pricing/budget contract is refused. Closed ledgers and concurrent reservations cannot bypass accounting.
- No automatic retries, redirects, repair calls, or format fallback. Timeouts, crashes, HTTP errors and missing/invalid usage retain the full reservation and block further calls. Valid usage is charged once even if the response is refused, truncated or malformed. Storage failures stop further transport.
- A public-state loop guard. Repeated room1 rules inspection stops after four requests; changing reason text, alternating passive calls or rewriting notes does not evade it. Newly delivered pages and legitimate time/round progression remain usable.
- Separate evaluator-stop reporting. Budget and loop stops do not change the game's rewards, victory conditions, terminal flags or room mechanics.
- Notebook-only supplied-context handoff at the wipe, with no old conversation/response ID. The ledger survives the wipe. Remote provider cache/process deletion is not claimed.
- Explicit opt-in for live calls; default CLI is preflight. Offline tests do not need or read a real key. Credentials are not saved to artifacts; reflected credentials, including JSON-escaped echoes, are rejected.

## Measured checks

**78 tests passed**, including **32 new paid-adapter tests** that forbid socket connections, DNS and datagram operations. The other 46 existing environment/interface tests still pass.

All **64 original environment certificates** passed unchanged-source checks: 4,604 actions and 1,344 citations. No `borderland/` module was changed.

| Saved offline case | Fake requests | Measured result |
|---|---:|---|
| Repeated rules inspection | 4 | External no-progress stop before request 5; environment itself remains nonterminal |
| Insufficient dollar headroom | 0 | Blocked before transport; no action dispatched |
| Recorded legal all-seven-room fixture | 76 | All seven rooms replay exactly; eight-line note crosses the wipe; post-wipe request has only fresh public state and notebook |

The full-room case supplies recorded legal actions as **fake provider replies**. It tests transport, guards and environment integration; it is not a model solve, training result, or evidence that a paid model will escape. Neither those actions nor a gold notebook are inserted into the model request. The paid CLI itself has no reference-prefix, forced-exit or reference-solver path.

The saved transport audit reconstructed every outward prompt and dispatched action, checked source hashes and budget admission before each fake request, and replayed all traces exactly. Counterfactual tests verify identical blank-notebook messages across four hidden phase/registry twins.

## Budget scope and remaining live gate

The cap is strict **against the declared provider contract and one shared ledger**. Before live use, supply verified model limits and upper token prices; ensure the output cap includes all billable reasoning/completion tokens and that there are no extra request/tool/routing fees. The full context limit must not be understated to fit the budget. Each independent ledger is an independent budget.

A provider that ignores limits, misreports usage, changes pricing, or bills outside that contract can violate the assumptions of any client-side estimate. The adapter stops when a violation is observable; it cannot recall a request already sent. Actual endpoint/model compatibility remains untested because no paid call was authorized or made. A separately authorized, tightly capped compatibility smoke test is still needed before a larger live run.

The shipped prices and model name are **synthetic**. Its sample reservation is $0.016256 per request against a $0.05 simulated cap; neither number is a quote for an actual model. Ledger accounting in the fake runs is simulated, not money spent.

## Evidence and entry point

- [Usage and exact contract](../../baseline/paid/README.md)
- [Full test output](tests.txt)
- [Unchanged environment audit](environment-audit.json)
- [Saved fixture summary](proof/summary.json)
- [Independent request/replay/budget audit](audit.json)
- [Offline preflight](preflight.json)

Run the preflight without credentials or network:

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline.paid \
  --config baseline/paid/offline-example.json
```

All project reads, edits and artifacts stayed in Lexi. The external desktop wiki was not accessed under the folder-only instruction. `proof-initial/` is a superseded development fixture; `proof/` is the final audited artifact set. No training ran and no external service was contacted.
