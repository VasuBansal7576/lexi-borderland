# Seven-room solver witness

Success: **True**. Seed 1028; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `394fb81db16335b2c8588cb2e9bf706d527ce389a28f703762483b798e097716`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 18 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 374 bytes total; longest line 81 bytes.
Old process 239 exited; new process 240 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":1,"delta":-1}
{"people":["V","S","I","N"],"sigma":1}
{"mode":"phase-cycle","offsets":[0,19,1]}
{"sectors":[2,1,3,0,1,3,0,2,2]}
{"roles":["N","V"],"source":"e0894","authority":"S"}
{"credentials":["c3631","c2049","c9284","c7093"]}
{"clock":"e8962","circuit":"e9065","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9775. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
