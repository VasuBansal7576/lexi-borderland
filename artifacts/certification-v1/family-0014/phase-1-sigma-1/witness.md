# Seven-room solver witness

Success: **True**. Seed 14; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `2770b6f05c2a2f050f0c5505ebc00424e796a8260cc45b07024f95299edb1500`.

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

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 88112 exited; new process 88113 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,0,3,1],"phase":1,"delta":-1}
{"people":["S","N","I","V"],"sigma":1}
{"mode":"echo","offsets":[1,17,20]}
{"sectors":[2,2,1,3,0,3,1,0,1]}
{"roles":["N","V"],"source":"e7905","authority":"N"}
{"credentials":["c8811","c2723","c1870","c8231"]}
{"clock":"e5796","circuit":"e0403","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
