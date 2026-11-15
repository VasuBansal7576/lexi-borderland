# Seven-room solver witness

Success: **True**. Seed 1012; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `ac14f7cf29870484c5ff29dbed9756b9876d64f01c3652cfed92867a1ee46ae7`.

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

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 109 exited; new process 110 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,2,1],"phase":1,"delta":1}
{"people":["N","V","S","I"],"sigma":0}
{"mode":"phase-cycle","offsets":[16,10,13]}
{"sectors":[1,2,3,2,3,0,2,1,0]}
{"roles":["V","S"],"source":"e8139","authority":"V"}
{"credentials":["c4487","c6259","c0289","c8296"]}
{"clock":"e0610","circuit":"e7107","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9775. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 17500; rival points: 4000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
