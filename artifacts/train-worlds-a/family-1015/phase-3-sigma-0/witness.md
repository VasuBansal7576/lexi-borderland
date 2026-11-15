# Seven-room solver witness

Success: **True**. Seed 1015; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `c44640e8f503289482465ec17558a775e49be1c949a44f07d349aad559e462ef`.

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

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 133 exited; new process 134 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,2,3],"phase":3,"delta":1}
{"people":["S","N","V","I"],"sigma":0}
{"mode":"echo","offsets":[6,19,0]}
{"sectors":[3,0,1,1,3,2,0,2,2]}
{"roles":["N","V"],"source":"e9052","authority":"N"}
{"credentials":["c2883","c2837","c6842","c9443"]}
{"clock":"e4029","circuit":"e2083","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9759375. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 47/96 after it.
Error, if any: None.

Final allied points: 17800; rival points: 3700.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
