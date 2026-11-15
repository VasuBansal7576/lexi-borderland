# Seven-room solver witness

Success: **True**. Seed 2009; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `fa8aafd22a6fd32a2d83c6ebc390701036c303e774389dde71c6b1d71cc0732e`.

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
Old process 86 exited; new process 87 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,2,3,1],"phase":3,"delta":-1}
{"people":["I","N","S","V"],"sigma":0}
{"mode":"mirror","offsets":[3,17,18]}
{"sectors":[3,3,1,2,1,2,1,0,0]}
{"roles":["S","I"],"source":"e4318","authority":"S"}
{"credentials":["c3326","c1811","c5130","c9762"]}
{"clock":"e9133","circuit":"e9395","main":"B"}
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
