# Seven-room solver witness

Success: **True**. Seed 1005; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `122634cb62138e475c4d2b5f9cd5db3c0e28a321f4556efa2dc72392409e4d1f`.

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

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 53 exited; new process 54 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":3,"delta":1}
{"people":["I","N","S","V"],"sigma":0}
{"mode":"echo","offsets":[1,0,16]}
{"sectors":[0,3,1,0,2,3,2,2,1]}
{"roles":["I","N"],"source":"e5980","authority":"N"}
{"credentials":["c3401","c5725","c9327","c8771"]}
{"clock":"e6463","circuit":"e5397","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9775. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 18000; rival points: 3000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
