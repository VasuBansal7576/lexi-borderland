# Borderland: teaching a 3B model to remember across a memory wipe

*Lexsi AI Safety & Alignment Hackathon, Track 3 (Agentic Fine-tuning). Problem statements: 1 (reliable tool calling with RL), 3 (agentic distillation), 9 (reward design and reward-hacking defences).*

> Every number in this article comes from a logged run linked below. Cells marked **TBD** are filled only from those logs.

## The environment
Seven connected rooms inspired by *Alice in Borderland*: Dead or Alive -> Switchboard -> Tribunal -> **memory wipe** -> Distance -> Balance -> Witch Hunt -> Osmosis. One hidden world is sampled per episode; each room reveals evidence about it, and later correct moves depend on earlier facts. After room 3 the agent's context is destroyed; only an 8-line, 96-byte-per-line notebook it wrote itself survives. Two maintenance tools work but zero the whole episode (trap tools).

- Deterministic, exactly replayable, standard-library Python.
- 64 held-out worlds (16 families x 4 lock variants) certified solvable by an evidence-only reference solver; a four-way lock at room 4 gives a memoryless agent at most 25%.
- 236 training worlds from disjoint seeds.

## Is the game fair? (frontier playtests)
GPT-6.1 Terra (user's ChatGPT subscription, native Codex CLI) played the public game:
- v1 exposed a real bug: Terra answered room 3 correctly but failed a citation rule the public rules never stated. We published the rule (difficulty unchanged) and re-certified all 64 worlds.
- v5: rooms 1-3 cleared, real wipe, room 4 cleared from its own notebook, lost room 5 on its own arithmetic. No environment fault found.

## Method
1. **Agentic distillation (SFT)** with AgentTune `create_distill_trainer`: teacher = our evidence-only solver (not an API model). 2,240 stratified decisions; loss on the action only; reasons carry evidence-derived facts.
2. **GRPO** with AgentTune `create_agentic_trainer`: verifiable step reward computed by replaying the exact environment state (invalid/trap/fatal -1, milestone +1, new evidence +0.3, wasted step -0.2, notebook = share of evidence-derived facts preserved). No LLM judge.
3. **Control arm**: identical GRPO with an action-independent random reward.

## Metrics (held-out worlds, AuditKIT-style scoring from environment ledgers)
| Metric | Why |
|---|---|
| Room success rate (per room, room-start episodes) | does the policy solve each room given a correct prefix |
| Full-escape rate | the real task |
| Valid tool-call rate | PS1 reliability |
| Trap-tool rate | safety / reward hacking |
| Room-4 lock success vs 25% memoryless ceiling | does memory across the wipe work |
| Steps per room | PS2 efficiency |

## Results
| Policy | Room success | Full escape | Invalid rate | Trap rate |
|---|---|---|---|---|
| Random | 0% | 0% | - | 37% |
| Reference solver (oracle) | 100% | 100% | 0% | 0% |
| Tiny Aya Global (base) | TBD | TBD | TBD | TBD |
| + SFT | TBD | TBD | TBD | TBD |
| + SFT + GRPO | TBD | TBD | TBD | TBD |
| + SFT + GRPO (random-reward control) | TBD | TBD | TBD | TBD |

## Limitations
TBD after results. Compact 8K interface (same game and evidence, shorter history) is used for Tiny Aya; frontier playtests used the full interface.

## Reproduce
Code: https://github.com/VasuBansal7576/lexi-borderland · Data/logs: https://huggingface.co/datasets/FatUnc6969/lexi-borderland-data
