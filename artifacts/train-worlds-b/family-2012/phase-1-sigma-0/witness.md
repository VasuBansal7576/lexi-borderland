# Seven-room solver witness

Success: **True**. Seed 2012; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `4e7b00ac9c42645ebd32f5196146e24462ba7500500945918a9b87fc3dbdb715`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 18 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 369 bytes total; longest line 81 bytes.
Old process 110 exited; new process 111 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":1,"delta":1}
{"people":["I","S","N","V"],"sigma":0}
{"mode":"mirror","offsets":[16,8,13]}
{"sectors":[0,1,1,2,3,2,3,0,3]}
{"roles":["S","I"],"source":"e1228","authority":"V"}
{"credentials":["c0023","c6282","c8879","c5142"]}
{"clock":"e6548","circuit":"e2236","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 18000; rival points: 3500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
