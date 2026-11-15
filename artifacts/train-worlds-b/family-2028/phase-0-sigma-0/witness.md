# Seven-room solver witness

Success: **True**. Seed 2028; interventions {'phase': 0, 'sigma': 0}.
World fingerprint: `d8a741daba2d6797fe3c5ed79b2fbf592decccd45e9ac95b4d9e05b330c73b3b`.

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

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 234 exited; new process 235 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,3,1,0],"phase":0,"delta":-1}
{"people":["V","I","N","S"],"sigma":0}
{"mode":"mirror","offsets":[0,19,12]}
{"sectors":[1,1,2,3,0,3,0,2,2]}
{"roles":["I","N"],"source":"e9600","authority":"N"}
{"credentials":["c1593","c5168","c3794","c3338"]}
{"clock":"e0358","circuit":"e0984","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
