# Borderland: does a 3B model actually use its memory across a wipe?

*Lexsi AI Safety & Alignment Hackathon, Track 3 (Agentic Fine-tuning). Problem statements: 1 (reliable tool calling), 3 (agentic distillation), 9 (reward design and reward-hacking defences). Model: CohereLabs Tiny Aya Global (3.35B). Training stack: Lexsi AgentTune (`create_distill_trainer`, `create_agentic_trainer("grpo")`).*

> Every number below is rebuilt from raw per-episode logs by `python -m train.report` (artifacts/eval/RESULTS.md). Nothing is copied by hand.

## TL;DR
- **Benchmark.** Borderland is a seven-room text world with one hidden causal state per episode. After room 3 the agent's context is destroyed; only an 8-line notebook (96 bytes/line) survives. Each world has **four counterfactual twins** that differ only in the two facts the room-4 lock depends on, so a memoryless agent is capped at 25% lock success and 0 pairwise discrimination (DSE).
- **Result (held-out, 64 worlds, 16 families).** Tiny Aya base: 0% valid tool calls (strict JSON), 12.5% lock with fences stripped. **SFT v2: lock 64/64 (100%), pairwise DSE 1.0, 99.3% valid calls, 0 trap uses.**
- **Causal proof that the notebook is used.** Same episodes, notebook blanked → lock **25%** (exactly the memoryless rate). Notebook swapped with its anti-twin's → lock **0%**, and the model enters the swapped notebook's pair **100%** of the time.
- **The model's own memory, end to end.** Starting in room 3, SFT v2 writes its own notebook (64/64), is wiped, and opens the lock from it in **50%** of worlds (memoryless ≤25%). Failure attribution explains the rest exactly: it records phase correctly 64/64 but always writes registry bit 0, so it fails precisely on the twins where the bit is 1 ("discovered but not recorded").
- **GRPO is a null result.** 250 AgentTune GRPO steps with the verifiable step reward vs an identical random-reward control: held-out step reward 0.200 vs 0.202 (SFT v2: 0.187), room success 8.9% vs 10.7%. The dense reward did not move the policy at this scale.
- **Honest limits.** The small model cannot yet clear rooms 1–3 on its own (full escape 0/16).

## 1. The environment
Dead or Alive → Switchboard → Tribunal → **memory wipe** → Distance → Balance → Witch Hunt → Osmosis. Facts found early (clock phase, glyph sectors, registry bit, rival policy, authority, credentials) decide correct moves later. Two maintenance "trap" tools work but zero the whole episode's reward.
- Deterministic, exactly replayable, standard-library Python.
- **Certified:** an evidence-only reference solver (no hidden state) escapes all 64 held-out worlds; an independent transcript audit re-checks citations, notebook transfer and reward arithmetic without importing the simulator.
- **Leak check:** 236 training worlds vs 64 held-out share zero seeds, manifests, fingerprints and latent structure (artifacts/eval/LEAK_CHECK.md).

## 2. Is the game fair? Frontier playtests
GPT-6.1 Terra (Codex CLI) played the public game. An early run exposed a real bug: Terra answered room 3 correctly but failed a citation rule the public rules never stated. We published the rule and re-certified all 64 worlds. On the compact 8K interface Tiny Aya uses, Terra cleared 6/7 rooms with 0 invalid calls (artifacts/terra-compact-v1/REPORT.md). Its room-4 twin failures traced partly to our notebook label `sigma` (the public rules say `registry_bit`), which we report as a limitation rather than silently fix.

## 3. Method
1. **Agentic distillation (AgentTune `create_distill_trainer`)**, teacher = the evidence-only solver, loss on the action only.
   - **SFT v1** (2,240 decisions, 1 epoch): learned the format and recalled notebook facts, but its reasons listed facts without the computation. Room-4 lock 34% [28–41%]: barely above memoryless.
   - **Root cause → SFT v2**: teacher reasons now *show the computation* for every computed action (`route=(phase%2) XOR pulse=(1%2) XOR 0=1. badge=registry_bit XOR challenge=0 XOR 1=1.`), computed decisions are oversampled, unlock pairs are balanced 50/50/50/50, and a script re-executes every derivation (100% must equal the action) before any GPU is used. Continued from v1 for 1 epoch (1,228 rows).
2. **GRPO (AgentTune `create_agentic_trainer("grpo")`)** from merged SFT v2 with a verifiable step reward computed by replaying the exact environment state: invalid / trap / fatal −1, milestone +1, new evidence +0.3, wasted step −0.2, notebook write = share of evidence-derived facts preserved. No LLM judge. **Control arm:** identical run with an action-independent random reward.

## 4. Results (held-out)
Room-4 checkpoints start right after the wipe with the teacher's notebook; "own notebook" starts in room 3 before the notebook is written. Step reward = 320 held-out single decisions scored with the GRPO reward (teacher 0.488, random −0.297).

| Arm | Room-4 lock (64) | Pairwise DSE | Own-notebook lock | Room success (16×7) | Valid calls | Held-out step reward |
|---|---|---|---|---|---|---|
| Random | 14.1% | 0.01 | – | 0% | 100%* | −0.297 |
| Teacher (oracle) | 100% | 1.0 | 100% | 100% | 100% | 0.488 |
| Tiny Aya base, strict JSON | 0% | 0 | – | 0% | 0% | – |
| Tiny Aya base, fences stripped | 12.5% | 0 | – | 0% | 87.6% | – |
| + SFT v1 | 34.4% [28–41] | 0.06 | – | 13.4% | 100% | – |
| **+ SFT v2** | **100%** | **1.0** | **50%** | 9.8% | 99.3% | 0.187 [0.09, 0.28] |
| + SFT v2 + GRPO (250 steps) | 100% | 1.0 | – | 8.9% | 99.8% | 0.200 [0.11, 0.29] |
| + SFT v2 + random-reward control | – | – | – | 10.7% | 99.6% | 0.202 [0.11, 0.29] |

\*random picks only schema-valid actions. Memoryless reference: lock ≤25%, DSE 0.

**Notebook interventions (SFT v2, same 64 episodes):** blank notebook → lock 25.0% (memoryless rate); anti-twin notebook → lock 0%, follows the swapped notebook's pair 100%.

## 5. What failed, and why (failure attribution)
- **Base:** 576/576 strict-mode invalid outputs are markdown-fenced JSON; with fences stripped it still clears no room and locks 12.5%.
- **SFT v1:** recalled phase and registry bit correctly but computed the entry pair wrong two times in three; v2's derivation targets fixed this (34% → 100%).
- **SFT v2 in rooms 1–3:** chooses a door after ~2 steps without reading the clock evidence (16/16 `unsafe_door`): oversampling decision rows made it commit early. Full runs therefore never reach the wipe.

## 6. Limitations
- Room-4 numbers start from the teacher-written notebook; the model writing its own notebook end-to-end is not yet demonstrated.
- Single seed, greedy decoding; Terra n is one world.
- Notebook label `sigma` is private notation (hurts base/Terra, not SFT).
- Haiku playtest not run (no Claude API token).

## 7. Reproduce
Code: https://github.com/VasuBansal7576/lexi-borderland · Data, logs, traces: https://huggingface.co/datasets/FatUnc6969/lexi-borderland-data · Models: FatUnc6969/tiny-aya-borderland-{sft, sft-v2, sft-v2-merged, grpo, grpo-randreward-control}.
