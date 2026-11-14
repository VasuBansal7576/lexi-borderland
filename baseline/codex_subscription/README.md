# Native Codex subscription bridge

This runner uses the **official Codex CLI 0.169.0**, `gpt-6.1-terra`, and native ChatGPT sign-in. It does not launch or depend on OpenCode. The official ARM64 npm package was downloaded inside Lexi and verified against its registry SHA-512 integrity value.

The user completed native device authorization. The login cache lives in `runtime/codex-subscription/native-auth/state/auth.json`, with private file permissions and a runtime `.gitignore`. It must never be printed, committed or sent to a model. No global Codex credentials or personal configuration are read. The `CODEX_HOME` environment setting points the native client to its project-local state directory.

Each decision starts an ephemeral native Codex process with a fresh state directory. Only a temporary copy of the subscription login is supplied, and it is removed after the call. The model process can read its own state and official executable; macOS denies other user/project data, the master login cache and earlier call directories. Network access is limited to the local relay. API-key environment variables are absent, `forced_login_method=chatgpt` is set, and the adapter rejects an API-key login.

The relay uses Codex's supported custom-provider configuration with `requires_openai_auth=true`. It checks the selected model, native public prompt and subscription credential. It then constructs the outgoing request **only** from the existing public game messages, removing native coding tools, skills and environment boilerplate. The destination is fixed to `https://chatgpt.com/backend-api/codex/responses`. There is no API-key endpoint or fallback route.

Limits: five actual upstream attempts by default, or an explicitly selected `--max-calls` budget from 1 through 100. The selected budget is fixed in the durable ledger and cannot be changed when reopening it. Each native process gets one attempt, with no retries, 64,000 public-request bytes, 1,024 completion tokens, a 60-second HTTP timeout and an 85-second native process timeout. Failed or interrupted attempts remain spent. Truncation, invalid actions, authentication errors and quota failures stop the run. Subscription consumption is reported as returned token usage; the adapter does not infer dollars or the user's remaining plan allowance.

The existing seven-room environment and public-evidence loop guard are reused unchanged. At the room-3 wipe, only the legal eight-line notebook survives in a freshly constructed history. A new local state directory prevents transcript access. This makes no claim about deletion of provider-side caches.

From Lexi, offline mode uses fake credentials and a local fake endpoint, with external networking denied:

```sh
PYTHONPYCACHEPREFIX="$PWD/runtime/pycache" python3 -m baseline.codex_subscription \
  --output artifacts/a-fresh-offline-run --ledger artifacts/an-offline-ledger.json
```

Live mode additionally requires `--live` and a native ChatGPT login. Reuse the live ledger for the same authorized budget; do not replace it to get around its limit. The completed November 14 smoke test exhausted its five-call allowance. The user subsequently authorized a separate, single unassisted episode with `--max-calls 100`; it uses a new ledger under `artifacts/codex-terra-episode-v1` and preserves the smoke-test ledger. The runner records its immutable source hashes and settings in `run-contract.json` before the episode starts.

Verification: `tests/test_codex_subscription.py`, `evaluations/verify_codex_boundaries.py`, and `evaluations/audit_codex_subscription.py`. See the [measured result](../../artifacts/codex-subscription-smoke/REPORT.md).

Official references: [ChatGPT authentication](https://learn.chatgpt.com/docs/auth), [non-interactive native Codex](https://learn.chatgpt.com/docs/non-interactive-mode), [configuration](https://learn.chatgpt.com/docs/config-file/config-reference), [Terra availability](https://openai.com/index/introducing-gpt-6-1-terra/).
