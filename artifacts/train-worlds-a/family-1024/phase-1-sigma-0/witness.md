# Seven-room solver witness

Success: **True**. Seed 1024; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `1f3374087104c514455824c5a4bc0fbf8ebf792074b91921f9ac3c272b7b5017`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 205 exited; new process 206 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,2,1],"phase":1,"delta":-1}
{"people":["V","N","I","S"],"sigma":0}
{"mode":"phase-cycle","offsets":[10,10,2]}
{"sectors":[0,2,0,2,2,1,3,3,1]}
{"roles":["V","S"],"source":"e1662","authority":"N"}
{"credentials":["c9006","c9170","c5378","c2901"]}
{"clock":"e0744","circuit":"e0401","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9784375. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
