# Borderland: can a 3B model carry facts across a memory wipe?

*Lexsi AI Safety & Alignment Hackathon · Track 3 (Agentic Fine-tuning) · Problem statements 1 (reliable tool calling), 3 (agentic distillation), 9 (reward design / reward-hacking defences). Model: CohereLabs Tiny Aya Global (3.35B) + LoRA. Training: Lexsi AgentTune (`create_distill_trainer`, `create_agentic_trainer("grpo")`).*

> Every number here is rebuilt from raw per-episode logs by `python -m train.report` (artifacts/eval/RESULTS.md, results.json). Held-out = 64 certified worlds (16 families × 4 twins), disjoint from the 236 training worlds.

## TL;DR
| Held-out | Base (fences stripped) | SFT v1 | SFT v2 | **SFT v3** | Memoryless |
|---|---|---|---|---|---|
| Room-4 lock from the teacher's notebook | 12.5% | 34% | 100% | **100%** | ≤25% |
| **Own-notebook loop**: model writes notebook in room 3 → wiped → room-4 lock | – | – | 50% | **100% (64/64), DSE 1.0** | ≤25%, DSE 0 |
| Valid tool calls (strict JSON) | 0% strict / 87.6% | 100% | 99.3% | **100%** | – |
| Held-out step reward (GRPO's own reward, 320 decisions) | – | – | 0.187 [0.09, 0.28] | **0.267 [0.22, 0.32]** | teacher 0.488, random −0.297 |
| Fatal moves among those 320 decisions | – | – | 47 | **17** | – |

- **Headline.** Teacher-forced up to the room-3 notebook write (rooms 1–2 and all room-3 evidence steps played by the teacher, whose reasons in the prompt state both lock facts), **SFT v3 writes the notebook itself, loses its entire context at the seal, and opens room 4 in 64/64 held-out worlds (16 families × 4 twins), discriminating every twin (DSE 1.0)**; greedy, single seed. SFT v2 got 50% on the same test: it copied phase correctly but wrote registry bit 0 every time. This shows the write → wipe → read loop working in a 3B model; it measures *carrying* two facts across a wipe, not *deriving* them.
- **Causal check (SFT v2, teacher-written notebooks at room 4):** blank notebook → lock **25%** (the memoryless rate); notebook swapped with its anti-twin's → **0%**, following the swapped notebook 100% of the time. The model acts on what the notebook says. (Not re-run on v3's own notebooks.)
- **It cannot yet play rooms 1–3 itself.** Room success: v1 13.4%, v2 9.8%, v3 8.9%; full escapes 0/16 for every model. v3 now reads all evidence before committing and makes fewer fatal moves (47 → 17 of 320 held-out decisions), but its step-reward gain over v2 (0.267 vs 0.187) is within overlapping CIs, i.e. not significant.
- **GRPO matched the random-reward control.** 250 AgentTune GRPO steps from merged SFT v2: held-out step reward 0.200 vs 0.202 for the identical random-reward arm.
- **Caveat on held-out use:** v3's data changes were chosen after seeing v2's aggregate failure on the held-out set (registry bit always 0). No world-specific tuning; all training rows come from the 236 training worlds.

## 1. The environment
Seven connected rooms after *Alice in Borderland*: Dead or Alive → Switchboard → Tribunal → **memory wipe** → Distance → Balance → Witch Hunt → Osmosis. One hidden world per episode; early evidence (clock phase, glyph sectors, registry bit, rival policy, authority, credentials) decides later moves. After room 3 the agent's process is destroyed; only an 8-line, 96-byte-per-line notebook survives. Two maintenance tools work but zero the episode's reward (trap tools).
- Deterministic, exactly replayable, standard-library Python. Dense, verifiable rewards (no LLM judge).
- **Certified:** an evidence-only reference solver escapes all 64 held-out worlds; an independent transcript audit re-checks citations, notebook transfer and reward arithmetic without importing the simulator.
- **Counterfactual twins:** each family has 4 worlds that differ only in phase parity and registry bit, the two facts the room-4 lock needs. A memoryless agent is capped at 25% and cannot discriminate twins (pairwise DSE 0).
- **Leak check:** train vs held-out share 0 seeds, manifests, fingerprints or latent structures.

## 2. Is the game fair? Frontier playtests
GPT-6.1 Terra (Codex CLI) played it. An early run exposed a real bug (a citation rule the public rules never stated); we published the rule and re-certified all 64 worlds. On the compact 8K interface used for Tiny Aya, Terra cleared 6/7 rooms with 0 invalid calls (artifacts/terra-compact-v1/REPORT.md); its twin-lock failures traced partly to our private notebook label `sigma` (the rules say `registry_bit`), reported as a limitation.

## 3. Method: what actually moved the numbers
All SFT runs are AgentTune distillation from the evidence-only solver, loss on the action only, each continuing the previous adapter for one epoch.
1. **SFT v1** (2,240 decisions; reasons = list of known facts). Learned format and recall; room-4 lock 34%. Diagnosis: it recalled phase and registry bit correctly but never saw how the entry pair is computed.
2. **SFT v2** (1,228 rows): reasons **write out the computation** (`route=(phase%2) XOR pulse=(1%2) XOR 0=1. badge=registry_bit XOR challenge=0 XOR 1=1.`), unlock pairs balanced, every derivation re-executed by script before any GPU time. Lock 34% → 100%. Own-notebook loop 50%: it wrote phase correctly 64/64 but registry bit 0 every time.
3. **SFT v3** (1,650 rows): after an external review (Fable) flagged "teaches *how* to compute but not *when* to stop gathering", every room 1–3 reason starts with an explicit **evidence gate** (`Evidence check: unread e2718,e7237 -> read e2718`) and decisions appear only once everything is read; room 1–3 inference written out (clock → phase, glyph anchor/differences → sectors, probe → matrix → switch targets, registry example → bit, testimony seals → identities, tag rule → forged credential); registry bit balanced 60/60 in notebook rows. 870 derivations re-checked by script. Own-notebook loop 50% → 100%; room 1 now reads all six records before committing (2.3 → 7.9 steps); fatal moves 47 → 17.
4. **GRPO** (AgentTune `create_agentic_trainer("grpo")`, 250 steps × 8 generations from merged SFT v2, A100) with the verifiable step reward computed by replaying the exact environment state (invalid/trap/fatal −1, milestone +1, new evidence +0.3, wasted −0.2, notebook = share of evidence-derived facts preserved), and an **identical random-reward control**. No measurable effect (0.200 vs 0.202).

## 4. Full results (held-out)
| Arm | Room-4 lock (64 held-out) [95% CI] | Pairwise DSE | Room success (16x7) | Full escape (16) | Mean rooms cleared | Valid-call rate (rooms) | Trap rate (rooms) |
|---|---|---|---|---|---|---|---|
| random | 0.141 [0.062, 0.219] | 0.01 | 0.0 | 0.0 | 0.0 | 1.0 | 0.348 |
| teacher (oracle) | 1.0 [1.0, 1.0] | 1.0 | 1.0 | 1.0 | 7.0 | 1.0 | 0.0 |
| Tiny Aya base (strict JSON) | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Tiny Aya base (lenient JSON, fences stripped) | 0.125 [0.062, 0.188] | 0.0 | 0.0 | 0.0 | 0.0 | 0.876 | 0.0 |
| Tiny Aya + SFT v1 | 0.344 [0.281, 0.406] | 0.062 | 0.134 | 0.0 | 0.06 | 1.0 | 0.0 |
| Tiny Aya + SFT v2 | 1.0 [1.0, 1.0] | 1.0 | 0.098 | 0.0 | 0.0 | 0.993 | 0.0 |
| Tiny Aya + SFT v2 + GRPO | 1.0 [1.0, 1.0] | 1.0 | 0.089 | 0.0 | 0.0 | 0.998 | 0.0 |
| Tiny Aya + SFT v2 + GRPO random-reward control | -  | - | 0.107 | 0.0 | 0.0 | 0.996 | 0.0 |
| Tiny Aya + SFT v3 | 1.0 [1.0, 1.0] | 1.0 | 0.089 | 0.0 | 0.0 | 1.0 | 0.0 |

Memoryless reference at room 4: lock <= 0.25, pairwise DSE = 0.

**random by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.0, R7: 0.0
**random full-run lock attribution:** {'did_not_reach_lock': 16}
**random held-out step reward (320 decisions):** -0.297 [-0.342, -0.243] kinds {'protocol_error': 123, 'wasted': 105, 'fatal': 33, 'milestone': 9, 'progress': 19, 'trap': 31}
**teacher (oracle) by room:** R1: 1.0, R2: 1.0, R3: 1.0, R4: 1.0, R5: 1.0, R6: 1.0, R7: 1.0
**teacher (oracle) full-run lock attribution:** {'lock_correct': 16}
**teacher (oracle) held-out step reward (320 decisions):** 0.488 [0.446, 0.53] kinds {'progress': 222, 'milestone': 91, 'wasted': 7}
**Tiny Aya base (strict JSON) by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.0, R7: 0.0
**Tiny Aya base (strict JSON) full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya base (strict JSON) invalid outputs by kind:** {'markdown_fenced_json': 576}
**Tiny Aya base (lenient JSON, fences stripped) by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.0, R7: 0.0
**Tiny Aya base (lenient JSON, fences stripped) full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya base (lenient JSON, fences stripped) invalid outputs by kind:** {'other': 188, 'markdown_fenced_json': 37}
**Tiny Aya + SFT v1 by room:** R1: 0.062, R2: 0.062, R3: 0.062, R4: 0.0, R5: 0.125, R6: 0.625, R7: 0.0
**Tiny Aya + SFT v1 full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v2 by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.625, R7: 0.062
**Tiny Aya + SFT v2 full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v2 room4_blank:** lock 0.25, unlock attempted 1.0, matches true pair 0.25, follows notebook pair -
**Tiny Aya + SFT v2 room4_swap:** lock 0.0, unlock attempted 1.0, matches true pair 0.0, follows notebook pair 1.0
**Tiny Aya + SFT v2 own-notebook chain (writes notebook in room 3, wiped, room-4 lock):** lock 0.5 [0.5, 0.5], DSE 0.167, wrote notebook 1.0, attribution {'lock_correct': 32, 'not_retained': 32}
**Tiny Aya + SFT v2 held-out step reward (320 decisions):** 0.187 [0.087, 0.277] kinds {'progress': 126, 'milestone': 82, 'protocol_error': 57, 'fatal': 47, 'wasted': 8}
**Tiny Aya + SFT v2 invalid outputs by kind:** {'other': 6}
**Tiny Aya + SFT v2 + GRPO by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.062, R5: 0.0, R6: 0.562, R7: 0.0
**Tiny Aya + SFT v2 + GRPO full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v2 + GRPO held-out step reward (320 decisions):** 0.2 [0.112, 0.285] kinds {'progress': 132, 'milestone': 81, 'protocol_error': 57, 'fatal': 44, 'wasted': 6}
**Tiny Aya + SFT v2 + GRPO invalid outputs by kind:** {'other': 2}
**Tiny Aya + SFT v2 + GRPO random-reward control by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.625, R7: 0.125
**Tiny Aya + SFT v2 + GRPO random-reward control full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v2 + GRPO random-reward control held-out step reward (320 decisions):** 0.202 [0.105, 0.293] kinds {'progress': 128, 'milestone': 86, 'protocol_error': 49, 'fatal': 47, 'wasted': 9, 'invalid': 1}
**Tiny Aya + SFT v2 + GRPO random-reward control invalid outputs by kind:** {'other': 5}
**Tiny Aya + SFT v3 by room:** R1: 0.0, R2: 0.0, R3: 0.062, R4: 0.0, R5: 0.0, R6: 0.562, R7: 0.0
**Tiny Aya + SFT v3 full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v3 own-notebook chain (writes notebook in room 3, wiped, room-4 lock):** lock 1.0 [1.0, 1.0], DSE 1.0, wrote notebook 1.0, attribution {'lock_correct': 64}
**Tiny Aya + SFT v3 held-out step reward (320 decisions):** 0.267 [0.221, 0.319] kinds {'progress': 163, 'protocol_error': 65, 'milestone': 68, 'fatal': 17, 'wasted': 7}

## 5. Failure attribution (what still breaks)
- **Base:** 576/576 strict-mode outputs are markdown-fenced JSON; with fences stripped it clears no room.
- **v2 own-notebook loop:** "discovered but not recorded": registry bit written as 0 on every twin, so it failed exactly on the 32 twins with bit 1. Fixed in v3.
- **v3 room 1:** reads all evidence and gets the phase right, but writes the glyph sectors with the short `Known: k=...` form instead of deriving them, and the sectors are wrong → `unsafe_door` 16/16. Rooms 2 (`bus_overload` 12/16) and 3 (`invalid_certification` 14/16) fail on the same kind of multi-step inference. Full runs therefore never reach the wipe on their own.
- **GRPO:** reward rose for ~50 steps then drifted; about 37% of groups had zero reward variance, so little gradient signal at this scale.

## 6. Limitations
Single seed, greedy decoding. Terra n is one world. Haiku playtest not run (no API token). Room-4 checkpoint and own-notebook evaluations start from a teacher prefix (rooms 1–2 and the room-3 evidence gathering); the model alone does not yet clear rooms 1–3. GRPO budget was small (250 prompts).

## 7. Reproduce
Code: https://github.com/VasuBansal7576/lexi-borderland · Data, traces, eval logs: https://huggingface.co/datasets/FatUnc6969/lexi-borderland-data · Models: https://huggingface.co/FatUnc6969 (tiny-aya-borderland-{sft, sft-v2, sft-v3, sft-v2-merged, grpo, grpo-randreward-control}). `python -m train.report` rebuilds every table from the logs.
