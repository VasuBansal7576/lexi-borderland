# What would prove the environment works

Design v0.1. These are acceptance criteria, not measured results. The original file's report of no verified GRPO improvement remains the only historical model status available here.

## Validate the game before training

The game must be both difficult and learnable. For each accepted generator family, verify full-state solvability, observation-legal solvability, notebook feasibility, deterministic replay, counterfactual action changes and resource-budget feasibility. Random seeds alone are not sufficient tests of an unimplemented generator.

Before model work, implement exhaustive checks on reduced finite instances and sampled property checks on full instances. A target development batch is 1,000 accepted worlds plus all members of their seal quartets; publish the actual sample size, rejection reasons and rates. This is a planned minimum development check, not a statistical guarantee about all possible worlds.

Check the observable projection at the seal byte-for-byte across matched worlds, including tool schemas, IDs, clocks, inventory, timers and errors. Audit all reachable pre-unlock tool responses. Equal opening prompts alone do not rule out a later side channel.

The four baseline references requested in the original idea are:

| Reference | Access and purpose |
| --- | --- |
| Oracle | Full W and exact transition model: attainable score and solver feasibility. Also report an observation-legal evidence solver with the notebook cap; otherwise the oracle can hide an information deficit. |
| Memoryless | Same model with no notebook and no earlier history after the seal; also compute the theoretical 1/4 seal-lock ceiling under the certified balanced distribution. |
| Scripted heuristic | A declared, frozen policy using local rules, recency or shortest-path heuristics. Useful shortcut reference; it is not an upper bound on every possible script. |
| Random | Uniform over schema-valid currently exposed actions, with an explicit stopping policy. Report its tool budget and handling of maintenance tools. |

'Four ceilings' in the original idea is interpreted as four reference points; only a proven optimum or bound is literally a ceiling. A sophisticated scripted solver can be an oracle.

## Dependency exploitation is the headline

Every generated dependency probe names an early evidence source, a later decision, correct action sets and a minimal sufficient evidence set. The private solver supplies these; the player never sees them.

For a counterfactual pair (w,w′), change exactly one exogenous root value, propagate all its consequences consistently, and hold unrelated random streams fixed. Designated downstream decisions must have disjoint correct action sets A and A′. If the changed root legitimately changes several documents, that is still a one-root intervention; do not edit one sentence while leaving the rest of the world inconsistent.

**Pairwise dependency exploitation (DSE):** fraction of pairs on which the model chooses a correct action in both w and w′ at the designated decision. Merely changing its answer is insufficient. Score each root family and dependency length separately, then macro-average; a frequently sampled easy root must not dominate.

Publish two versions:

- End-to-end DSE: start both worlds at room 1. A failed prerequisite or failure to reach the decision is a miss.
- Checkpoint DSE: restart at a canonical target state with only legally acquired notebook/state. This isolates downstream use from exploration. State exactly whether notes are model-written or oracle-produced; do not mix them.

For paired decisions with two disjoint equally likely actions, independent random choices can get both right by chance. Report the appropriate random reference for the actual action sets, not a universal chance subtraction.

Additional causal checks: remove the relevant notebook fact, replace it with its twin value, shuffle unrelated facts, and paraphrase surface wording. A useful causal policy should be sensitive to the relevant value and comparatively invariant to irrelevant or stylistic changes. Report false sensitivity as well as correct sensitivity. These are behavioral interventions, not proof of the model's hidden reasoning process.

## The scorecard

1. Legal full escape rate, with uncertainty intervals.
2. End-to-end and checkpoint DSE, by root and dependency length.
3. Per-room conditional clear rate and unconditional reach/clear rate; do not hide earlier failures by reporting survivors only.
4. Tool schema error rate and failed/duplicate tool calls.
5. Calls and tokens per successful escape, plus all-attempt cost and wall time.
6. Forbidden-tool usage and invalid-display-escape rate; separate clean and injected conditions.
7. Stale-rule errors before/after the R6 amendment, including applying the new rule too early.
8. Training reward, reported separately from all the above.

A high reward with unchanged true escape is a failed thesis, not a win. A low cheating rate from a model that does nothing is not useful safety. Report successful legal behavior alongside violations.

## Failure attribution without pretending to read minds

Log evidence exposure and notebook versions. For a failed certified decision, classify operationally:

- **Not discovered:** no complete sufficient evidence set was delivered before its deadline.
- **Discovered, not retained correctly:** a sufficient set was delivered but the necessary content is absent, incorrect or stale in the notebook at the seal or later decision.
- **Available, action wrong:** sufficient correct information is present in the allowed context/notebook, but the chosen downstream action is incorrect. This is the measurable counterpart of 'recorded but not used'; it may also reflect reasoning, arithmetic or planning failure.

For no-seal decisions, 'retained' refers to the allowed current context. Support alternative sufficient evidence sets. Do not assume the model understood a tool result merely because it was delivered.

Free-text notebook semantics are not reliably classified by a substring search. Use exact deterministic checks for structured facts when possible; otherwise a pinned rubric and human-reviewed sample, with ambiguous cases marked unknown. A read-only diagnostic probe may ask what a note means in a forked replay, but its answer must not feed the original episode. Show agreement/error rates for any automatic annotator.

Protocol errors, simulator bugs, unsupported actions, context overflow and earlier irreversible resource mistakes are separate categories; do not force them into memory failure. Report all categories and unknowns. Give representative traces with original observations and notes, not just a model-written explanation of its mistake.

## Prove post-training improvement

Evaluate base model, SFT-only and SFT+GRPO on the same frozen holdout, with identical inference settings, context budget, notebook budget, tools, episode caps and decoding policy. A stronger SFT checkpoint is the starting point for both the real-reward and random-reward RL runs.

Use at least three training random seeds when compute permits; disclose fewer. Use paired comparisons over worlds and bootstrap confidence intervals clustered by world/twin family. A proposed final battery is 256 independent world families, each with the required counterfactual variants; calibrate sample size on development data and report uncertainty instead of treating this number as guaranteed power.

Controls:

- Shuffled-reward control: within a prompt group, randomly permute finalized rewards across the corresponding trajectories using an independent RNG. This preserves the group's empirical reward distribution while destroying action/reward alignment in expectation. Also log zero-variance groups where permutation changes nothing.
- SFT-only at the exact same pre-RL checkpoint.
- Full transcript, capped notebook, empty notebook and oracle notebook variants, clearly separated.
- Frozen notebook policy versus learned notebook-writing actions, if affordable.
- Progress reward versus terminal-only reward.
- Clean tool/document text versus paired injected text, with identical W.

Keep training roots, validation roots and test roots disjoint by canonical latent-world fingerprint, not merely seed number. Keep every counterfactual family within one split. Also reserve structural compositions: unseen combinations of controller family, topology motif, alias scheme and opponent policy. New random IDs alone do not establish generalization.

Seeds named in the old idea file, including 9000, are historical/development only. Do not resurrect them as fresh holdout. Any failed test that is inspected to change the design becomes development data; draw a new final holdout under the frozen protocol.

## Make learning possible without softening the final task

Use solver-generated legal demonstrations to teach tool syntax and evidence-driven behavior, then train on checkpoint subproblems and full episodes. Demonstrations must be generated from observable evidence; an oracle that silently knows W creates imitation targets the student cannot reproduce.

Monitor within-group reward variance and the fraction of groups with identical rewards. GRPO's relative-advantage signal vanishes for identical-reward groups; DAPO explicitly discusses this failure mode and dynamic sampling. This motivates instrumenting the signal, not assuming that a named RL algorithm will learn from an all-failure batch. [Primary paper, section 3.2](https://arxiv.org/html/2503.14476v1)

If every trajectory fails at the same point, diagnose observation rendering, syntax, context, reward and curriculum. Never silently remove dependencies, leak the answer, expand the official notebook or switch to a forgiving test and retain the same headline.

Verify nonzero learning rates, actual optimizer updates, gradient flow through pre-seal notebook actions, correct action masks and correct seed propagation. Recompute rewards from saved simulator events independently. Read successful and high-reward failed trajectories for hacks. The original status file reports previous failures in exactly these areas, but those old implementations are unavailable for inspection here.

## Memory system ablation is a separate question

The development wiki in this folder is not the player's external memory. It may help us maintain the code and evidence, but it is never an allowed source during game evaluation.

If a later research question compares wiki memory to eight-line notes, introduce a separately named benchmark condition. Match storage/read budgets or report the difference, freeze source access, and forbid test-answer accumulation across worlds. Full transcript search after the seal is a different information regime; it cannot be presented as solving the original sealed task.
