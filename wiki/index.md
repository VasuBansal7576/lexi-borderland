# Borderland project knowledge

Updated: 2026-11-14. Status: seven-room environment and restricted evidence-only solver implemented. See the implementation and verification records for measured results and remaining training work.

This is a small, local project wiki. All project material stays under `/Users/vasu/Desktop/Lexi`. It is development knowledge; the game-playing model must never receive this directory or its hidden-world specifications.

## Start here

- [Run the environment](../README.md): executable commands and saved proof artifacts.
- [Implementation](implementation.md): module responsibilities, actual memory boundary, concrete design choices and proof limits.
- [Terra rerun with explicit public notation](../artifacts/codex-terra-notation-v1/REPORT.md): room 1 cleared; terminal room-2 circuit arithmetic error at call 14 of 100. Native ChatGPT subscription, 32,906 tokens; no live wipe. Only generic glyph encoding changed; 103 tests, all 64 existing certificates and exact live replay passed.
- [Terra unassisted 100-call-ceiling episode](../artifacts/codex-terra-episode-v1/REPORT.md): ended at call 8, second door bank in room 1. Terra reversed the glyph-difference direction; that direction is implicit in the public format, confounding attribution to model reasoning. No live wipe. 101 tests and exact replay pass; clarify the generic encoding before another evaluation or RL.
- [Native Codex subscription smoke test](../artifacts/codex-subscription-smoke/REPORT.md): GPT-6.1 Terra completed five real calls and five distinct legal evidence reads in room 1; stopped at the call cap. 98 tests and independent replay pass. No live wipe or seven-room completion claim; no OpenCode or API-key fallback used for this run.
- [Isolated OpenCode free bridge](../artifacts/opencode-free-smoke/REPORT.md): 89 tests pass; five IDs verified against a fake endpoint. The first live request hit HTTP 429 free quota, so the sweep stopped after one attempt and zero model actions. No paid fallback; remaining models untested.
- [Paid adapter offline verification](../artifacts/paid-adapter-offline/REPORT.md): durable budgets, loop guards, 78 passing tests, zero external calls; live provider contract remains unverified.
- [Repaired Tiny Aya interface and rerun](../artifacts/model-interface-v3/REPORT.md): typed tools, current-room prompts, 0/4 natural escapes, four audited controlled wipes, empty model notebooks and preserved failures.
- [Actual Tiny Aya baseline](../artifacts/model-baseline/REPORT.md): unassisted failures, all-room assisted probes, verified inference-server wipe and raw model traces.

- [Original idea](../00-IDEA.md): the user's requirements and a historical status report. The old code and run artifacts described there are not present in the current folder inventory, so those claims are not independently verified here.
- [World design](world.md): the causal world, seven-room dependency graph, memory boundary and generation contract.
- [Seven rooms](rooms.md): playable mechanics, tools, completion conditions, rewards and downstream consequences for every room.
- [Tools and rewards](tools-and-rewards.md): action contracts, timing, episode accounting and forbidden-tool semantics.
- [Evaluation](evaluation.md): what would establish memory dependence, causal use, learning and resistance to shortcuts.
- [Anthropic memory research](anthropic-memory.md): the November 6 article, its linked GitHub implementation, limitations and implications for this project.
- [Decisions and open questions](decisions.md): current choices, reasons and the remaining calibration work.
- [Design verification](verification.md): checks actually performed, versus checks that still require the environment.

## Evidence convention

The original idea is a user requirement. These design pages are proposals unless explicitly described as verified. External findings have source links; historical results stay attributed to the original file. A test result needs an actual command and output. An unrun acceptance criterion is never a result.

Keep this index short. Update the relevant page when a decision changes; retain its reason and mark the old decision superseded. Check claims against their underlying source or run artifact before relying on them. A source-linked correction is more valuable than accumulating another summary of the same claim.
