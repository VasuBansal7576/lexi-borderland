# Seven-room solver witness

Success: **True**. Seed 1013; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `3fcef16b69bf2c8947aad1f02ffec9c919d95460ddadd96fac756b1bb7ad4e15`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 374 bytes total; longest line 81 bytes.
Old process 119 exited; new process 120 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,2,0,3],"phase":3,"delta":1}
{"people":["N","V","I","S"],"sigma":1}
{"mode":"phase-cycle","offsets":[19,16,3]}
{"sectors":[1,1,3,0,3,0,1,2,2]}
{"roles":["N","V"],"source":"e6571","authority":"N"}
{"credentials":["c0495","c1054","c8945","c5988"]}
{"clock":"e0912","circuit":"e0168","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 19300; rival points: 2200.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
