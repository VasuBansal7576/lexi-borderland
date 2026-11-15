# Seven-room solver witness

Success: **True**. Seed 2006; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `f5f53fa9fae7a8e5af8703f2f91009da8c4bb95d6df6f6194f93713658daf7da`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 23 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 60 exited; new process 61 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,2,1],"phase":0,"delta":1}
{"people":["N","I","S","V"],"sigma":1}
{"mode":"phase-cycle","offsets":[11,7,1]}
{"sectors":[2,2,1,0,3,2,0,1,3]}
{"roles":["I","N"],"source":"e7533","authority":"I"}
{"credentials":["c1641","c9839","c4914","c7815"]}
{"clock":"e4338","circuit":"e2031","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9759375. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 47/96 after it.
Error, if any: None.

Final allied points: 15000; rival points: 6500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
