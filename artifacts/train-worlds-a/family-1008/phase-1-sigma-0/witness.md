# Seven-room solver witness

Success: **True**. Seed 1008; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `edf65bc3809650b660517714ddf3f18c011258e9b18cb131c45c96cce67361f1`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 24 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 77 exited; new process 78 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,3,0,1],"phase":1,"delta":-1}
{"people":["I","N","V","S"],"sigma":0}
{"mode":"mirror","offsets":[3,18,10]}
{"sectors":[0,1,2,3,1,3,2,3,0]}
{"roles":["I","N"],"source":"e4563","authority":"I"}
{"credentials":["c9135","c8750","c2531","c3976"]}
{"clock":"e9593","circuit":"e7312","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.975625. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 48/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
