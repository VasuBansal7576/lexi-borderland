# Gate A playtest: Terra on the fixed game (public citation rules)

2026-11-14 ~17:45 IST. gpt-6.1-terra via the user's ChatGPT subscription, native Codex CLI 0.169.0 (official linux-arm64 build, npm integrity verified), run from the Cowork Linux VM through the relay (bubblewrap file isolation; egress via the sandbox proxy CONNECT tunnel). Medium effort, 100-call cap, certified world family-0000/phase-0-sigma-0, resumable 120 s chunks. Invalid-action policy: halt (original).

Result: 24 actions, rooms 1 and 2 cleared, Room 3 registry validated and roster certified **correctly with the public five-source citation rule** (score 0.12 at stop). Call 25 was a notebook_write whose 5th line was 97 bytes (limit 96) -> invalid_model_action, episode halted before the wipe. Exact replay: true.

Gate A verdict: PASS. Every failure so far is the model's own (v1: missing citation was due to an unstated rule, now public; v4: line length). No environment fault found.
