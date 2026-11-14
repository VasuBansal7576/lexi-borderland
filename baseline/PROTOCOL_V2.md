# Typed interface rerun

Frozen before the gameplay rerun. The original `borderland/` engine, rules, rewards, candidate worlds, reference certificates and v1 baseline artifacts are unchanged.

## What changed

- The decoder receives a JSON Schema union over **every currently advertised tool**, with exact argument keys/types, public enums and ranges, numeric node-ID strings, nested roster/order objects, and eight printable ASCII notebook strings of <=96 characters. The model also sees the typed definitions and descriptions. This uses llama.cpp JSON-schema-constrained output, not a claim that Tiny Aya has native tool-calling training.
- All door choices, both values of each entry bit, all21 bids, premature exit/settlement calls, wrong citations and both maintenance traps remain representable. Arithmetic sums, circuit correctness, identity truth, edge availability, evidence sufficiency, authorization and victory remain engine decisions. No private fact or solver selects/masks an action. Generic canonical IDs are public constants, not inferred identities.
- The prompt foregrounds the current room, asks for one next action, explains how to recover from errors, and reminds the model to preserve its own facts before exiting room3. It gives fixed public laws for the current room, instead of flooding the first turn with every future-room law. No sampled value, correct action, source-priority judgment or example notebook is supplied.
- The epoch-local conversation is encoded as a single public transcript: exact results stored once, deltas for repeated state fields, exact duplicate events run-length encoded, and full current state placed last. Canonical record JSON text is displayed as a parsed object and has an exact inverse. Each inference request checks that the transcript reconstructs every original public frame except static tool signatures (which are separately typed). Model reasoning/actions remain in the transcript. No summary, inference or automatic notebook write is performed.
- At the seal, the server process is killed/restarted and the entire transcript codec is discarded. Only the actual eight notebook lines cross to the new process with the normalized public state and fixed instructions. No pre-wipe evidence cache, ledger, action or reasoning survives.

## What stays fixed

Same official Tiny Aya Global Q4_K_M weights/checksum, same llama.cpp runtime, temperature0, seed42, 1,024 output tokens/action, 32,768 generated tokens/run, native8,192 context, original64/96 game call budgets and all seven rooms. No SFT or RL. No answer repair, alternate action substitution, model-specific reward change or hidden context truncation. Syntax constraints are an explicit experimental change; distinguish protocol validity from task success.

Natural rerun: same four paired certified development worlds (one family, phase0/1 and registry0/1), all attempts saved. Fatal losses stop. If natural runs fail before the wipe, run a separate legal-prefix notebook probe that stops before the reference notebook is written; the model chooses its own note/actions and faces the actual wipe. This probe is assisted upstream, not a full-run success. Compare later-room behavior using the same legal reference-prefix room2..7 diagnostics, clearly separate from unassisted results.

Room diagnostics stop on eight identical transitions or four repetitions of a two-, three- or four-step exact transition cycle. This is an evaluator stall, not a terminal game loss. Natural episodes and the notebook probe retain their full budgets.

Before gameplay:42 tests passed, all64 unchanged reference certificates passed their audit, and real-model schema smoke tests passed for bidding, notebook writing, team orders and bus energizing. Those smoke prompts contained no episode state or correct game answers and are not gameplay results.

The public adapter `interface_v2.py` imports no environment, generator or solver. Its schema construction depends only on advertised tool names. Tests check all reference-witness actions remain representable, all wrong door/bit/bid choices and traps remain available, exact transcript reconstruction, and identical blank-notebook gate prompts across counterfactual twins.

Primary runtime reference: [llama.cpp JSON Schema grammar support](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md). The schema constrains output but is not automatically injected into the prompt; this adapter supplies readable definitions explicitly.

## Pre-inference serialization correction

After the four natural runs, the memory-prefix preflight detected a circuit result represented internally as a Python tuple versus a JSON array on the wire. It aborted before any inference request. Normalize each public frame through JSON at the codec boundary; no values or prompt semantics change. Add a regression using the full memory-prefix fixture. Initial adapter sources are preserved under `artifacts/model-interface-v2/source-initial/`; audit checks both the original source hashes and the corrected version. The empty `memory/` attempt is an aborted harness preflight, not a model failure. The actual probe uses a new output directory.

The first normalization version sorted keys, which also reordered the public tool catalog; its two-call `memory-json` probe is retained with its source under `source-json-normalization`. The final normalization preserves insertion order. Audits compare all public content and retain exact raw requests plus source revisions. Since the first probe passed the lock with an empty notebook, run all four phase/registry counterparts using the final adapter to measure that apparent pass against the known25% memoryless ceiling. These remain upstream-assisted diagnostics, not unassisted room3 solutions or escapes.

## Controlled boundary diagnostic

The final-ordering free-action memory diagnostic repeatedly rewrote the same generic486-byte notebook in room3 without choosing exit. It was externally stopped after six completed model actions; its requests/responses and reconstructed exact trace remain under `memory-balanced/memory-p0-s0`, explicitly marked evaluator-stopped rather than terminal loss. An in-flight request was cancelled, not credited as a model response.

To measure behavior across the wipe despite that pre-exit loop, the separate `fixed-wipe` component check gives the same legal upstream prefix and one unrestricted model action. It preserves exactly the model's resulting notebook. If the model has not exited, the evaluator performs **only** the already-legal room3 exit, records that action as evaluator-owned, and claims no model credit for it. The server and transcript codec are then destroyed/restarted; the model receives its own notebook and fresh room4 state and chooses up to four actions. No correct note, gate bits, repaired action or extra fact is supplied. All four phase/registry counterparts are tested. This is a controlled retention diagnostic, never an unassisted room3 solution or full escape. The natural episodes remain unchanged and complete.
