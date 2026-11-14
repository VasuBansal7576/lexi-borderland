# Decisions and open questions

As of 2026-11-13. These are working design decisions, not user approval of every invented mechanic.

| Decision | Reason / evidence |
| --- | --- |
| Seven connected rooms; Osmosis last | Explicit original requirement; the other six adaptations are proposed here |
| One deterministic causal manifest per episode | Needed for reproducible outcomes, counterfactual interventions and verifiable rewards |
| Full-information and observation-legal solver certificates | Full information alone does not prove the player could acquire the answer |
| Exact context wipe after R3 | Original requirement; physical carryover normalized to close hidden memory channels |
| Eight lines, 96 printable ASCII characters each | Concrete implementation of the notebook requirement; final capacity requires solver feasibility validation |
| Explicitly bounded storage, no rewarded note format | Makes compression measurable without paying for fact-shaped text |
| Four-way indistinguishable lock at R4 entry | Establishes a provable memoryless ceiling on a balanced test distribution |
| R6 changes a rule's effective interval | Tests maintenance and provenance, not just verbatim recall |
| Headless symbolic simulator, no generative NPC judging | Fast, reproducible environment semantics; model inference remains the likely bottleneck |
| Dense 0.05 per room; 0.60 legal escape; at most 0.05 success-only efficiency | Legal completion dominates ordinary partial progress; inspect shaping with an ablation |
| Forbidden tools invalidate earlier rewards as well | Required by the original idea's 'zero the episode' rule |
| Lightweight local project wiki | Preserve decisions/evidence across a long build without requiring a hosted memory system |

## Deliberately unresolved until executable prototypes

1. **Generator feasibility and diversity.** Can all four lock twins support the full seven-room observation-legal solution without a high rejection rate or a constant winning script? Implement a certificate-producing generator and measure this first.
2. **Osmosis search cost.** Four allied units and simultaneous opponent policies create a large planning space. Measure exact search with state memoization and dominance pruning on the nine-node, eight-round domain. Reduce redundant state representation if needed; do not silently remove causal dependencies to make the solver pass.
3. **Notation capacity.** The sample notebook proves only that one compact representation fits, not that every world does. Generate and verify a legal memory strategy for each accepted world, including room 6 updates.
4. **Difficulty for Tiny Aya.** Full environment difficulty stays fixed once the final evaluation is frozen. Training curriculum, demonstration quality and probe distribution must be empirically tuned on development data.
5. **Budgets and numerical targets.** 160 calls, 8 arena rounds, 11,000 settlement points and 96 characters per line are proposed constants. Freeze after development calibration; report any change explicitly.
6. **Training adapter.** Audit the actual AgentTune version selected later, especially segmented contexts, action masks and terminal reward correction. Its existence is not proof our seal is supported correctly.
7. **Free-text attribution.** Determine the measured reliability of the notebook-content annotator before using its labels as a headline.
8. **Safety scope.** Two explicit forbidden tools test constrained rule adherence. General prompt-injection robustness needs varied attacks and legitimate look-alike tasks; this project must not overclaim.

## Implementation order

1. Define simulator state, manifests, public projection and the seal; implement the four-world lock test and attack its side channels.
2. Build the connected seven-room transition system and offline certificates. Work through one complete manually inspectable world before scaling generation.
3. Add finalized reward accounting and replay. Verify every milestone, terminal case, repeat action and forbidden-tool invalidation.
4. Freeze a development distribution and establish the four baseline references, notebook feasibility and counterfactual dependencies.
5. Integrate exact model rollouts, then SFT and GRPO. Establish real weight updates and held-out improvement before creating a success demo.

This turn stops at the requested design, plus limited executable checks of its mathematical subcontracts. No training, cloud service, GPU job, model download or external publication is started.
