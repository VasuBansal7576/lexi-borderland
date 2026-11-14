# Seven-room solver witness

Success: **True**. Seed 11; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `13830e15c9b0ad9de153bd7f388656f34fa465c4a2a9a70bf99ce5540dd70ad3`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 20 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 369 bytes total; longest line 81 bytes.
Old process 88063 exited; new process 88064 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,2,3],"phase":2,"delta":-1}
{"people":["N","V","I","S"],"sigma":0}
{"mode":"mirror","offsets":[4,17,9]}
{"sectors":[1,1,0,3,2,1,0,2,3]}
{"roles":["N","V"],"source":"e7981","authority":"I"}
{"credentials":["c8354","c9687","c7236","c4775"]}
{"clock":"e0686","circuit":"e6595","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.976875. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 44/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
