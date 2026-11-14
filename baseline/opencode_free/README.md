# Isolated free OpenCode bridge

Uses the official OpenCode 2.2.7 macOS ARM64 client downloaded inside this project. It does not use the existing installation, account, plugins, background server or credentials. All five requested aliases are pinned to their `-free` IDs; the duplicate GLM request is one model.

The runner is a five-call smoke test per model (25 attempts maximum), not an all-room success evaluation. It uses the unchanged seven-room environment, the existing public interface, and the existing external loop guard. There are no reference actions, gold notes, action repairs or assisted prefixes in the live path.

## Boundaries

- Each action starts a fresh private control server, session, working directory and XDG state. Only the current public-history messages are forwarded. After the room-3 wipe, that history is reset and only the environment's eight-line notebook survives. This does not claim deletion of provider-side caches.
- macOS `sandbox-exec` blocks reads of other user/project content and prior call states. Only the downloaded executable and the current call's state are readable within user storage. Writes are limited to that state. Network access is limited to two local ports: the private control server and guarded relay.
- The relay compares the complete outgoing messages with the public messages, rejects coding tools, requires signed-out `Bearer public`, and forwards the real client's existing headers through the documented provider endpoint override. It does not synthesize a client identity or bypass a provider denial.
- Only the five exact free aliases are accepted. No account keys are inherited. Title, summary, compaction, warming, integrations, skills, MCP, web search and coding tools are disabled. A fixed title prevents title generation. The relay blocks additional requests even if the client tries them.
- A durable, locked ledger reserves an attempt before sending. Five per model, 25 total; 64,000 request bytes and 1,024 completion tokens per attempt. Byte limits are not token estimates. Responses are capped at 2 MB. There are no HTTP redirects, retries, repairs or model substitutions. Timeouts remain spent.
- HTTP 429 persistently halts every model. Successful responses must explicitly report zero cost and `billing_source=free`. Missing usage, truncation, invalid JSON, tool calls, or provider errors stop that model.

OpenCode's normal system/environment additions are excluded through its documented request-body overrides. The relay independently verifies this exact payload. The official client is retained because free models are restricted to use within OpenCode.

## Verification and use

Run offline tests from this folder:

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m unittest discover -s tests
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline.opencode_free \
  --output artifacts/your-fresh-offline-run --ledger artifacts/your-offline-ledger.json
```

Offline mode launches the actual client against a local fake provider. It cannot call the upstream endpoint. macOS may require running the outer process outside another sandbox so it can install its own restrictive sandbox.

Live execution additionally requires `--live`. Keep the persistent ledger across attempts. Do not reset a live ledger to work around a quota stop. There is no automatic retry or scheduled resume. The November 14 sweep's ledger is halted because OpenCode reported an exhausted free allowance; see `artifacts/opencode-free-smoke/REPORT.md`.

`evaluations/audit_opencode.py` reconstructs every public prompt from the initial world and raw model actions, verifies request hashes against the attempt ledger, checks unique sessions/state directories, and replays the environment. `evaluations/verify_opencode_boundaries.py` checks actual OS denials, an actual-client post-wipe fixture, and rejection of duplicate requests. Its post-wipe data is an offline evaluator fixture, never evidence of a model solving room 3.

Official references checked November 14, 2026: [models](https://opencode.ai/docs/console/models/), [inference restrictions and usage](https://opencode.ai/docs/console/api/inference/), [provider proxy and body settings](https://opencode.ai/docs/providers/), [agents](https://opencode.ai/docs/agents/), [policies](https://opencode.ai/docs/policies/).
