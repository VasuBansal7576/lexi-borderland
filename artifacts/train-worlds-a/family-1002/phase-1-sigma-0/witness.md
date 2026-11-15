# Seven-room solver witness

Success: **True**. Seed 1002; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `5af76004319aeb5be0afb2523380622ef311505bf84eb2ca06a0de72a61115c8`.

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

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 29 exited; new process 30 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":1,"delta":1}
{"people":["S","V","I","N"],"sigma":0}
{"mode":"mirror","offsets":[17,19,11]}
{"sectors":[0,3,1,0,2,2,1,3,0]}
{"roles":["I","N"],"source":"e8639","authority":"I"}
{"credentials":["c6030","c9162","c2765","c4498"]}
{"clock":"e5045","circuit":"e7834","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.976875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 18500; rival points: 3000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
