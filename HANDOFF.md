# Handoff: autonomous build plan (written 2026-11-14 17:20 IST)

Deadline: Lexsi hackathon submission Nov 15 23:59 AoE = **Nov 16 17:29 IST**. Target submit: Nov 16 11:30 IST. Hard stop for new work: Nov 16 06:00 IST, then publish whatever is verified.

## Decision
Keep and fix the existing 7-room Borderland game; build the training/eval pipeline fresh (none exists in this folder). Idea is NOT watered down: 7 rooms, room-3 wipe, 8-line notebook, two trap tools, counterfactual twins, four ceilings (oracle, memoryless, scripted heuristic, random), failure attribution, Osmosis last. Room-by-room starts are a training curriculum only; full-escape is always reported.

## Model roles (policy)
- Tiny Aya Global (Cohere) = the trained model (required by hackathon).
- Teacher for SFT = the scripted reference solver (our code). NOT Haiku/Terra: Anthropic's Usage Policy and support docs forbid using Claude outputs as training targets; OpenAI terms have a similar restriction.
- Claude Haiku 5.5 (user's Claude subscription via Claude Code headless) and GPT-6.1 Terra (user's ChatGPT subscription via native Codex) = playtesters (fairness gate A) and frontier reference scores in the write-up only.

## Steps and gates (see statechart in chat)
1. Fix game: publish the hidden citation requirements (rooms 3 and 6) in public rules; make solver cite only required evidence; re-certify 64 worlds; tests.
   Gate A: Haiku + Terra playtests fail only from their own mistakes.
2. AgentTune adapter (custom stateful harness, Tiny Aya tool-prompt fallback), room-start curriculum, 48 train / 16 held-out worlds.
   Gate B: one real Tiny Aya rollout on GPU logged + replayable. Fallback: plain TRL.
3. "Before" metrics on held-out worlds with AuditKIT: per-room success, valid tool calls, trap use, citation correctness, room-4 lock vs 25% memoryless ceiling, steps, full-escape rate, failure attribution.
4. SFT warm start on solver trajectories. Gate C: beats base on held-out (else fix data, retry once).
5. GRPO with per-room rewards + trap invalidation + random-reward control. Gate D: beats SFT and control (else ship SFT result honestly).
6. Reward-hack audit (read outputs).
7. Publish: HF model + dataset collections (public, ungated), GitHub repo, HF article, abstract <500 words, submit at hackathon.lexsi.ai/submission/.

## Verified so far (real runs)
- Step 1 DONE (game fix): public citation rules for rooms 3 and 6; solver cites exactly the required sources; 64/64 re-certified (artifacts/certification-v2), audit passes, 103 tests pass. See artifacts/rules-citation-v1/CHANGE.md. Gate A (Haiku + Terra playtest) still pending network/secrets.
- 103/103 tests pass (on a copy outside the mount; the mount forbids deleting temp files).
- Independent certificate audit: 64 worlds, 4,604 actions, 1,344 citations.
- Live Terra (medium effort, 24 calls): rooms 1-2 cleared; room-3 answer correct but failed the unstated 5-tag citation rule. See artifacts/codex-terra-medium-v1/REPORT.md.

## Setup still needed from the user
See runtime/secrets/README.md. Network allowlist changes only apply in a NEW conversation.

## Progress log (2026-11-14, 18:45 IST)
- Gate A PASS (real Terra runs from the Linux VM bridge): v4 = room 3 solved under public rules; v5 = rooms 1-4 cleared incl. live wipe, lost room 5 on its own arithmetic. Reports in artifacts/codex-terra-medium-v4|v5/REPORT.md.
- Bridge: Linux codex 0.169.0 (npm integrity verified), bubblewrap isolation, proxy CONNECT tunnel, resumable chunks (--resume/--pause-after; host kills background jobs after each command), --invalid-action error_frame.
- Compact interface (baseline/interface_compact.py) so every prompt fits Tiny Aya's 8K context (max ~17k chars).
- Data: 236 train worlds (artifacts/train-worlds-a|b, certified, disjoint seeds 1000+/2000+); held-out = 64 worlds of artifacts/certification-v2. SFT data: artifacts/sft-data/train-p*.jsonl (17,098 teacher decisions; reasons carry evidence-derived facts).
- Eval harness: train/evaluate.py (teacher/random), train/eval_model.py (batched, vLLM or HF). Baselines: teacher 100% rooms + 100% full; random 0% rooms, 37% trap rate (artifacts/eval/baselines).
- SFT: train/sft_train.py via AgentTune create_distill_trainer + completion-only factory, length guard, zero-loss guard. CPU smoke-tested.
- GRPO: train/reward.py (verifiable step reward; teacher +0.64 vs random -0.27), train/grpo_data.py (states from train worlds), train/grpo_train.py via AgentTune create_agentic_trainer (config verified). CPU smoke-tested. Control arm: --control.
- Python 3.12 venv for training at $HOME/venv312 (VM-local; recreate with uv if lost).
- BLOCKED ON: runtime/secrets/hf_token, GPU route (HF credits or Kaggle), GitHub repo name, claude_oauth_token (Haiku playtest).

## Progress log (2026-11-14, 22:10 IST) - GPU phase started
- Secrets OK: HF user FatUnc6969 (write, Tiny Aya access, 8192 ctx); Kaggle user vasu7576 (2x T4, phone-verified).
- GitHub: code pushed to https://github.com/VasuBansal7576/lexi-borderland (main) from the cloud session clone.
- Transport: sandbox blocks www.googleapis.com (Kaggle dataset upload) and hf_xet binary uploads. Bundle goes to HF dataset FatUnc6969/lexi-borderland-data/bundle as text chunks + sha256 manifest; notebooks download it with the HF token (embedded only in the private Kaggle notebooks, staged under runtime/kaggle/, gitignored). Notebooks upload results to the same dataset under runs/<phase>/ and adapters to FatUnc6969/tiny-aya-borderland-{sft,grpo,grpo-randreward-control}.
- Launch: `python -m train.kaggle_launch --phase <eval_base|sft|grpo|grpo_control> --hf-user FatUnc6969` (venv $HOME/venv312, KAGGLE_CONFIG_DIR=runtime/secrets). Status: `kaggle kernels status vasu7576/lexi-borderland-<phase>`; logs (when finished): `kaggle kernels logs ...`.
- Running: eval_base (v1), sft (v2; v1 failed on Kaggle's torchao 0.10 -> now uninstalled in setup).
- Next: when sft done -> launch grpo and grpo_control (they pull the SFT adapter from HF). Then compile before/after tables, HF article, abstract, submit.
- Haiku playtest skipped unless the user saves runtime/secrets/claude_oauth_token.
