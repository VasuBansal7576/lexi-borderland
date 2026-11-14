# Seven-room solver witness

Success: **True**. Seed 4; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `3120ae58e3dc683645e941970f19d8419e00898877492e63ff9438ba4cb8159a`.

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

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 87974 exited; new process 87977 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,3,0,1],"phase":0,"delta":-1}
{"people":["I","S","N","V"],"sigma":1}
{"mode":"echo","offsets":[20,5,1]}
{"sectors":[1,3,2,0,1,2,2,0,3]}
{"roles":["N","V"],"source":"e6712","authority":"S"}
{"credentials":["c1323","c7141","c9850","c2047"]}
{"clock":"e9080","circuit":"e0234","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 21000; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
