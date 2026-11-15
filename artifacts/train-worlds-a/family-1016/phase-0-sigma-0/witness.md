# Seven-room solver witness

Success: **True**. Seed 1016; interventions {'phase': 0, 'sigma': 0}.
World fingerprint: `79e61b6a7b8740225e89483f1ef696744ad4a3583d5cd06caf80849e546c869d`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 137 exited; new process 138 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,2,1,3],"phase":0,"delta":-1}
{"people":["I","N","S","V"],"sigma":0}
{"mode":"phase-cycle","offsets":[5,9,1]}
{"sectors":[2,0,3,3,1,0,1,2,1]}
{"roles":["N","V"],"source":"e0815","authority":"V"}
{"credentials":["c0294","c2533","c3237","c9911"]}
{"clock":"e0174","circuit":"e7808","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 13500; rival points: 7500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
