# Retained v2 development trials

These are intermediate adapter trials. The final prompt-corrected rerun is in `../model-interface-v3/`.

- `smoke/`: four real-model constrained syntax checks passed. No episode answers were used.
- `natural/`: four unassisted episodes, five calls each. Every action was schema-valid. All four repeatedly inspected rules then chose unsafe door C without reading any record. Zero escapes.
- `memory/`: pre-inference harness assertion found tuple/list JSON normalization; no model action occurred.
- `memory-json/`: two model actions with a temporary key-sorting normalization. It exited with an empty notebook and guessed a correct pair in the single phase0/registry0 world after a real restart. This is not evidence of useful memory.
- `memory-balanced/memory-p0-s0/`: insertion-order-preserving adapter. Six generic notebook writes, then an explicit evaluator interruption; one in-flight request cancelled. Not a terminal game loss. Other twins were not run in this suite.
- `fixed-wipe/`: two completed controlled probes, p0/s0 and p0/s1. Each retained the model's486-byte generic notebook, evaluator performed a legal exit, and a fresh model process rewrote notes four times without unlocking. The p1/s0 attempt then failed at its first inference with HTTP500: `The model produced output that does not match the expected peg-native format`. No successful response/action for that attempt; p1/s1 was not reached. Do not describe this as a completed four-world sweep.

V2's final request mistakenly repeated the room3 notebook reminder in later rooms. V3 corrects that and distinguishes observed evidence from notebook contents. Retain v2 results as development history, not pooled final-prompt performance.

The source snapshots preserve the initial adapter and temporary JSON normalization. `audit.json` and `viewer.html` cover six ordinary reports (28 completed model actions). The custom fixed-boundary probes have their own `memory-check.json` files and runner assertions; they are not included in that ordinary-report audit.
