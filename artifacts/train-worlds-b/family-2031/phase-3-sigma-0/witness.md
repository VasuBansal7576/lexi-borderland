# Seven-room solver witness

Success: **True**. Seed 2031; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `536b9c8352f35e0a8b1503b5ff5045102f5fb732e6673e61575a5fc59967cee2`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 262 exited; new process 263 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,2,1],"phase":3,"delta":1}
{"people":["V","I","S","N"],"sigma":0}
{"mode":"phase-cycle","offsets":[19,20,12]}
{"sectors":[0,0,2,2,3,1,1,3,0]}
{"roles":["N","V"],"source":"e5148","authority":"S"}
{"credentials":["c9718","c1384","c5137","c3074"]}
{"clock":"e5981","circuit":"e4565","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 18000; rival points: 3500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
