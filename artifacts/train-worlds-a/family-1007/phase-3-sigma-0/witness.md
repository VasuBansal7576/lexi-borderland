# Seven-room solver witness

Success: **True**. Seed 1007; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `c0575f814fb7e4b9f27c0461c63f99e3cb2ac96b4c3024d1216d2969deb3716c`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 19 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 372 bytes total; longest line 81 bytes.
Old process 69 exited; new process 70 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,1,3,0],"phase":3,"delta":1}
{"people":["N","I","V","S"],"sigma":0}
{"mode":"phase-cycle","offsets":[6,4,3]}
{"sectors":[1,3,2,3,1,0,0,3,2]}
{"roles":["V","S"],"source":"e0605","authority":"S"}
{"credentials":["c4922","c8437","c9466","c8304"]}
{"clock":"e9645","circuit":"e1839","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.976875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 16500; rival points: 5000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
