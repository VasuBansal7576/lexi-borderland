# Teach the working, not the transcript: a 3B model that survives its own memory wipe

*Lexsi AI Safety & Alignment Hackathon · Track 3 (Agentic Fine-tuning). Model: CohereLabs Tiny Aya Global (3.35B) + one LoRA. Training: Lexsi AgentTune (`create_distill_trainer`; `create_agentic_trainer("grpo")` for the GRPO ablation).*

> Every number below is rebuilt from raw per-item logs (`python -m train.report`, `python -m train.xfer_report` → artifacts/eval/RESULTS.md, TRANSFER.md). Greedy decoding, single seed, 95% bootstrap CIs; A−B differences are paired over identical items.

## TL;DR
Coding agents run out of context all the time: the context is compacted and the agent must continue from its own summary. Fine-tuning on raw agent traces almost never teaches *that* moment. We built an environment that forces it, then ran a clean ablation: **two LoRAs trained from base Tiny Aya on the identical 4,003 rows, identical hyper-parameters; the only difference is whether each target carries a machine-verified derivation (A) or just the action (B, = ordinary trace fine-tuning).**

| Held-out | Base | v5 (Borderland-only SFT) | **A: verified derivations** | B: plain traces |
|---|---|---|---|---|
| **Own notebook → memory wipe → open the lock** (64 worlds, chance 25%) | – | 100%* | **90.6%** [77, 100], twin discrimination 0.88 | 21.9% [14, 28] (below chance) |
| …with the notebook swapped for its twin's: follows the notebook | – | – | **100%** | 48% |
| Borderland room success (16 worlds × 7 rooms) | 0% | 33% | **38.4%** | 6.2% |
| Full games: rooms cleared from scratch (mean) | 0 | 1.0 | **2.1** (5/16 reach and open the lock) | 0 |
| Memory-wipe tasks, 6 trained task types, unseen instances (own notes) | 2.1% [0, 5] | | **62.5%** [53, 72] | 52.1% [43, 62] |
| ↳ same, notes blanked | 4.2% | | 3.1% | 3.1% |
| Tool calling, BFCL v3 AST (400) | 44.5% [39, 49] | 26.5% | 54.5% [50, 59] | **67.0%** [62, 72] |
| Maths, GSM8K test (500) | **74.8%** [71, 78] | 72.4% | 57.6% | 60.0% |
| Multilingual knowledge, Global-MMLU-Lite 8 languages (200) | 50.5% | 52.5% | **54.5%** | 51.0% |

![A vs B vs base](fig_ab.svg)

\*v5 is a Borderland specialist continued over six SFT rounds; its chain number comes from a teacher-played prefix of rooms 1–2.

**What this shows**
1. **Verified derivations are what make memory work.** Same rows, same steps: A writes a notebook it can act on after the wipe in 91% of held-out worlds; B, trained on the bare actions, writes notebooks too (100% of the time) but cannot use them (22%, i.e. no better than guessing; 50/64 failures are "fact not retained"). A is causally dependent on its notebook: blank it → chance (25%); swap in the twin world's notebook → it follows the swapped notebook 100% of the time. On the procedural note-taking tasks (base 2.1%) A reaches 62.5% and beats B by **+10.4 pts [+3.1, +18.8]** (paired).
2. **Mixing general data fixes the "specialist collapse" of trace fine-tuning.** Our Borderland-only model (v5) lost 18 pts of tool calling vs base; both mixed models beat base on BFCL (A +10.0 [+2.8, +17.2], B +22.5 [+16.0, +29.0]) and keep multilingual knowledge (A +4.0).
3. **A derivation must be real computation to help.** Where our "reason" was a fixed provenance template rather than working (tool calls: `Request matches f: city <- "Paris" (user text)`), A learned to always claim a match and to copy raw text into arguments: BFCL irrelevance 21% vs B 41% vs base 80%, and A − B = −12.5 pts on BFCL. Where the reason is real working (Borderland arithmetic, note-taking), A wins decisively.
4. **Cost we did not avoid:** GSM8K fell ~15–17 pts for both A and B. Cause found in the outputs: the 500 GSM8K training solutions are short dataset-style chains, so the model now answers in 2–3 lines instead of base's careful step-by-step (mean answer 239 vs 573 characters). Turning the adapter down does not fix it: A at LoRA strength x0.75 / x0.5 scores 59.0% / 60.6% on GSM8K (BFCL 51.5% / 52.5%, Global-MMLU-Lite 54.0% / 55.5%), so the regression is a learned behaviour (terse answers), not an over-strong adapter; the fix is longer worked solutions in the training mix (not done in this submission).
5. **Not yet general:** on two *never-trained* note-taking task types and a held-out coding bug-fix wipe task (stack trace + stale config → patch after the wipe), all models are near 0% (A 6.2%, B 0%; coding A 0%, B 2%). The skill is learned per task type; it does not yet transfer to new ones.

## 1. Why this matters for coding agents
An agent that works for hours will lose its context: compaction, a crash, a hand-off. What survives is whatever it wrote down. Two things must go right: it has to **record the facts that matter later** before it knows exactly how they will be used, and **act on its notes, not on a guess**, after the reset. Day-to-day coding-agent traces contain this moment rarely and never verify it. Borderland makes it the bottleneck and makes it measurable with counterfactual twins.

## 2. Environments
**Borderland** (7 rooms after *Alice in Borderland*): Dead or Alive → Switchboard → Tribunal → **memory wipe** → Distance → Balance → Witch Hunt → Osmosis. Early evidence (clock phase, glyph sectors, registry bit, …) decides later moves; after room 3 the agent is destroyed and only an 8-line notebook survives. Trap tools zero the reward. Deterministic, standard-library Python, dense verifiable rewards (no LLM judge). An evidence-only reference solver escapes all 64 held-out worlds; an independent audit re-checks every transcript. **Counterfactual twins:** each of 16 held-out families has 4 worlds differing only in the two facts the room-4 lock needs, so a memoryless agent is capped at 25% and cannot discriminate twins. 236 training worlds, 0 overlap (seeds, fingerprints, latent structure).

**Procedural wipe tasks** (train/wipefam.py): read documents (with retired/outdated distractors) → save ≤4 notes of ≤96 chars → context wiped → make the final call from notes only. Six trained task types (ledger, schedule, lookup, logs, config, budget), two never-trained types (inventory, access) and an eval-only coding type (failing CI test + stack trace + active vs deprecated config + runbook rounding rule → `patch_config`). Tool names, output keys and document ids are randomised per episode; evaluation uses only twins whose correct answer differs.

## 3. Method
- **Data (4,003 rows, identical for A and B):** Borderland 900 (half with all 25 tool names and output keys renamed), 121 DAgger rows (v5 rolled out on training worlds; the evidence-only teacher labels every state where v5 deviated, kept only if the teacher action is legal and non-fatal from that exact state), procedural wipe tasks 1,272, tool calling 1,060 (Hermes function-calling + Glaive, incl. 160 no-call / ask-for-missing), GSM8K train 500 (identical worked solutions in A and B), Aya multilingual 150 (identical).
- **A vs B:** B's targets are A's with the reason emptied. A script asserts identical ids, order, prompts, actions and non-reason content for every row; all 2,817 "(user text)" provenance claims are true substrings of the request; 512 arithmetic steps in A's reasons are re-executed (0 errors).
- **Derivations (Borderland):** every computation written out and checked: clock → phase with explicit mod, glyph anchor/differences → sectors, probe → matrix → bitwise switch solve with element-wise comparison, registry bit from the example, forged credential by tag rule, explicit evidence gate (`Evidence check: unread e2718 -> read e2718`), explicit exit conditions, and the lock pair `route=(phase%2) XOR pulse`, `badge=registry_bit XOR challenge`.
- **Training:** AgentTune distillation (completion-only loss), LoRA r32/α64 on attention+MLP, lr 1e-4 cosine, effective batch 16, 2 epochs, max 6,144 tokens (0 rows dropped), from base, A100 ~63 min each.
- **Evaluation:** identical prompts and budgets for every model; BFCL scorer validated on gold (400/400) and on deliberately wrong calls (wrong function / extra arg / wrong value / duplicated calls rejected 300/300; missing arg 299/300); GSM8K last-number extraction for all; base gets one format example; strict and lenient (fence-stripped) JSON both reported.
- **Process:** one implementation review by Fable 5.2 and Astra 6 (high) before any compute spend; all blocking fixes applied (paired length filtering, fair GSM8K control, per-element provenance, negative scorer tests, model-written notes in the swap test, multilingual retention check).

## 4. How we got here (Borderland specialist, v1 → v6)
Each round fixed one diagnosed failure: v1 (facts only) lock 34% → v2 (write the lock computation) 100% → v3 (evidence gate; registry bit balanced) own-notebook loop 50% → 100% → v4 (derive at every bank, explicit mod) → v5 (explicit exit conditions; room 1 100%) → v6 (element-wise switch comparison; room 2 0% → 62.5%, rooms 51%, 8/16 full games reach and open the lock). GRPO (250 steps × 8 generations, verifiable step reward) vs an identical random-reward control: no measurable difference (0.200 vs 0.202 step reward), reported as a null result.

## 5. Failure analysis
- **A, tool calls:** template reasons → over-calling (irrelevance 21%), raw-text arguments (`"C# major"` for `C sharp`; `"C, F, G"` as a string, not a list), duplicated parallel calls. Lesson: provenance templates are not derivations.
- **A and B, GSM8K:** brevity inherited from short training solutions (see TL;DR 4).
- **B, Borderland:** valid calls 99.8%, notebook always written, but the facts are not the right ones or not used: 50/64 chain failures are `not_retained`; room 1 and 2 success 0%.
- **Everyone:** rooms 4 and 7 (Distance, Osmosis) at 0% in single-room mode; no full escape yet.

## 6. Limitations
Single seed and greedy decoding; one training run per arm (no seed variance); the A/B difference is measured on our environments plus BFCL/GSM8K/MMLU, not on SWE-style coding benchmarks; the coding wipe task is synthetic and eval-only; GSM8K regression unresolved (not recovered by lower adapter strength); Terra/frontier playtest is a single world.

## 7. Reproduce
Code: https://github.com/VasuBansal7576/lexi-borderland · Data, traces, all per-item eval logs: https://huggingface.co/datasets/FatUnc6969/lexi-borderland-data · Models: https://huggingface.co/FatUnc6969/tiny-aya-borderland-genA (A), …-genB (B), …-sft-v6 (specialist). `python -m train.gen_general` rebuilds the data, `python -m train.check_pair` re-verifies it, `python -m train.transfer_eval` and `python -m train.eval_model` rerun every evaluation.
