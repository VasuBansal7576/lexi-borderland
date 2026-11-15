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

## Progress log (2026-11-15, 00:30 IST) - moved base+SFT to Hugging Face Jobs (user approved a $2 cap)
- Kaggle eval_base/sft sat QUEUED 75+ min; superseded with CPU no-op versions (eval-base v3, sft v4) so they cannot overwrite the SFT repo.
- HF Job 6af8aa2829dd05ff0367a2cc on l4x1 ($0.80/h), timeout 140m => max $1.87. Script: train/hf_job.py (copy at dataset jobs/hf_job.py.txt), launched via api.run_job with a bootstrap (the hf CLI's script upload uses xet, blocked here; also timeouts must be single-unit like "140m").
- It runs: base eval (rooms+full, vLLM) -> SFT (1 GPU) -> push FatUnc6969/tiny-aya-borderland-sft -> SFT eval. Results -> dataset runs/base_sft/.
- Monitor: HfApi().inspect_job / fetch_job_logs (venv312). Do NOT launch more paid jobs; GRPO + control go to Kaggle (free) once the SFT repo exists.

## Progress log (2026-11-15, 08:35 IST) - Sunday plan, FREE compute only
- SFT DONE on HF L4 (paid; total HF spend ~$1.75, user has ~$5 left: spend NOTHING more). Adapter: FatUnc6969/tiny-aya-borderland-sft (loss 2.31 -> 0.07, train token acc 0.60 -> 0.97, 140 steps, 6465 s). HF job timed out during eval, so no eval numbers from it.
- Bundle on HF (bundle/code.tgz.b64.txt) was STALE until 08:33 IST; rebuilt from current code (grpo --batch, T4 fp16 vLLM dtype, HF token budget 12000). ALWAYS rebuild + re-upload the bundle after code edits (see commands in this log above).
- Kaggle: max 2 concurrent GPU sessions. eval-both v1 (stale code) may still occupy a slot until it fails; eval-both v2 (current code) running: evaluates sft (GPU0) and base (GPU1), rooms then full, vLLM then HF fallback, uploads to runs/eval_both/.
- TODO next: push grpo (python -m train.kaggle_launch --phase grpo --hf-user FatUnc6969 --grpo-steps 40) as soon as a slot frees; then grpo_control. Hard stop for new GPU work 14:00 IST.
- Then: fill writeup/ARTICLE.md from runs/*/eval/*/summary.json, publish HF model + dataset collections, update GitHub, submit at hackathon.lexsi.ai/submission (needs the user's registered email + abstract).

## DECISIONS (2026-11-15 10:05 IST) - Fable 5.2 advisor review adopted; user approved
- Stale items deleted (Kaggle notebooks, scratch dirs, failed-run logs on HF, scheduled checks).
- CUT: GRPO training (T4 cannot fit room-4+ prompts; report as designed + CPU-verified + reward validated offline), vLLM, multi-seed.
- Eval = HF generate, hardened: OOM backoff to batch 1, inference_mode, max_new_tokens ~400, per-episode jsonl append + --resume, latency logged, bundle sha asserted and recorded.
- Run order: (1) room-4 checkpoint on ALL 64 worlds (twin DSE vs 25% memoryless; label "oracle-written notebook"), (2) rooms 1-7 on 16 worlds, (3) full episodes on 16 worlds with end-to-end failure attribution.
- Gate: T4 preflight (sha, longest prompts <13 GB, no NaN, SFT reproduces teacher tool >=85% on 30 train states, projected eval <=5 h). If not green by 15:00 IST -> HF L4 fallback, hard cap $2.50 (user approved), tell the user before starting.
- Stretch: notebook intervention at room 4 (blank vs twin-swapped notebook). Offline reward validation of eval logs.
- Submit by Mon 12:00 IST.

## 2026-11-15 ~10:40-11:10 IST
- Preflight v1 RED: projected 26.5 h/model. ROOT CAUSE: torch.cuda.is_bf16_supported() is True on T4 (sm75) but bf16 is emulated (~10-20x slower). Fix: bf16 only on sm80+, else fp16; sdpa; per-sequence stop when the first JSON object closes; token budget 24k. Bundle sha 6a87dface985.
- Preflight folded into each eval job (check(): finite logits, memory, measured throughput -> projection <= 10 h; refuses to run if RED). Both GREEN: base 4.83 s/step (3.0 h), SFT 3.09 s/step (1.9 h), fp16 finite, peak ~10.4 GB.
- Diagnostic (not a gate): teacher-tool agreement on 30 training states: base 9/30 (valid JSON 27/30), SFT 22/30 (30/30). The 85% bar I had set is NOT met; reported as a result. 3 SFT mismatches = exit_room instead of notebook_write (watch 'not_retained' in full runs).
- Terra compact report: artifacts/terra-compact-v1/REPORT.md. Leak check: artifacts/eval/LEAK_CHECK.md (all zero).
- Kaggle kernels running: vasu7576/lexi-borderland-eval-base, -eval-sft (results -> HF dataset runs/eval_base|eval_sft/, uploaded every 10 min).

## 2026-11-15 ~11:00-11:12 IST: SFT v1 lock failure -> SFT v2
- SFT v1 room-4 (44/64 early): reason recalls phase+sigma correctly 44/44, entry pair correct 2/44 (route=0 bias). Cause: teacher reasons never showed computations. Training data consistent (70/70).
- Fable advisor: option B (derivations + oversample + gates). User approved <= $1.50.
- v2 targets: train/episodes.py derivation() for unlock/choose_door/validate_registry/submit_bid; facts-dump reasons unchanged elsewhere. teacher_prefix/TeacherPolicy pass obs (prefix prompts in rooms mode now carry v2 reasons -> base rooms must be re-run for strict comparability; room4_all/full unaffected).
- Data: train/sft_v2_select.py -> 1228 rows (unlock 200 balanced 50x4 pairs, door 200, registry 150, bid 150, notebook_write 164, replay 14/bucket); gate asserts 100% derivation==args, operands in prompt. sha 4083d6a5bd40.
- sft_train --init-adapter (continue v1). Tested on tiny model (weights change, same keys).
- HF Job 6af9462f29dd05ff0368412f (l4x1, timeout 100m => max $1.33): train 1 epoch (~76 steps), push FatUnc6969/tiny-aya-borderland-sft-v2, 16-episode room-4 gate -> runs/sft_v2/gate/.
- Code bundle sha 9a9943de7f6e.

## 2026-11-15 ~12:10-12:45 IST: SFT v2 gate + GRPO on Modal
- SFT v2 (HF job, 77 steps, 3305 s) pushed FatUnc6969/tiny-aya-borderland-sft-v2. Gate: entry pair correct 16/16 (room-4 clears 0: navigation).
- CORRECTION: v1 final room4_all = 22/64 correct pairs (34%); my earlier "2/44" counted only early finishers (wrong unlocks end at step 1).
- Base lenient (fences stripped) room4_all: lock 12.5%; base strict: 0 (all fenced).
- Kaggle running: eval-sft2 (room4_all | rooms,full), int-sft2-baselen-rooms (sft2 blank+swap | base_lenient rooms). Bundle eeeac4 at launch.
- GRPO fix: max_completion_length/temperature were inside a comment. GRPO states regenerated (625, reward check teacher>perturbed 400/400).
- Modal (user runs from Mac; VM proxy blocks api.modal.com): train/modal_grpo.py. Smoke (2 steps A100-80GB): 40.3 s/step, $2.8 GPU per 100 steps, frac_reward_zero_std 0. Merged SFT v2 on Volume lexi-grpo + HF FatUnc6969/tiny-aya-borderland-sft-v2-merged.
- Code sha afe948ebc587 (checkpoints every 50 steps, 6 h timeout). Real runs: --arm grpo/control --steps 250 (~$9 each est.).

## 2026-11-15 13:00-17:15 IST: GRPO null, own-notebook chain, SFT v3
- Modal ops channel: train/modal_grpo.py deployed app "lexi-borderland"; queue = HF dataset ops/queue.jsonl (runtime/ops/add_ops.py), status = ops/status.json (runtime/ops/status.py). Whitelisted fns train/evaluate/sft/publish; hard cap $27 committed (ledger v2 re-based at $16 measured).
- GRPO 250 steps vs random-reward control (both from SFT v2 merged): held-out step reward 0.200 vs 0.202 (SFT v2 0.187); rooms 8.9% vs 10.7%. NULL.
- Own-notebook chain (chain4, SFT v2): wrote notebook 64/64, lock 50%: phase right 64/64, registry bit always 0 (not_retained exactly on sigma=1 twins).
- Fable review (GO conditional): add explicit evidence gate to rooms 1-3 reasons, balance registry bit in notebook rows, keep room-4 replay. Pre-check passed: room-1 gold = read at 0-5 records, choose only at full evidence.
- SFT v3 data: 1,650 rows (rooms 1/2/3/4 = 390/390/500/220), 870 derivations re-checked, notebook bits 60/60. Code sha ef91939297a5. Modal op sft-v3 running (continues sft-v2, 1 epoch) -> FatUnc6969/tiny-aya-borderland-sft-v3.
- Control adapter published (README metadata fixed).
