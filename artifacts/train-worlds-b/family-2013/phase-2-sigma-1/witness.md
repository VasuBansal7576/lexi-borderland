# Seven-room solver witness

Success: **True**. Seed 2013; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `b1dc1284df1f7332208eba23852486d6ea6a2e4f14d749ead9e337dccb80aeda`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 20 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 116 exited; new process 117 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,0,1,3],"phase":2,"delta":-1}
{"people":["I","S","V","N"],"sigma":1}
{"mode":"echo","offsets":[12,6,10]}
{"sectors":[1,0,3,0,1,2,3,2,3]}
{"roles":["N","V"],"source":"e7254","authority":"N"}
{"credentials":["c8717","c8876","c7257","c4505"]}
{"clock":"e2078","circuit":"e1992","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9765625. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 44/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
