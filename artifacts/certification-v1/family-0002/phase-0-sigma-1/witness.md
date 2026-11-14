# Seven-room solver witness

Success: **True**. Seed 2; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `3ccf2e73478d1cc55f54ada3a6349f363399e6d57f215f49f61e0b48efd66573`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 19 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 87945 exited; new process 87946 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,3,0,1],"phase":0,"delta":1}
{"people":["S","N","V","I"],"sigma":1}
{"mode":"echo","offsets":[17,7,18]}
{"sectors":[1,2,3,1,3,0,2,0,2]}
{"roles":["V","S"],"source":"e3466","authority":"S"}
{"credentials":["c0598","c8079","c9569","c7750"]}
{"clock":"e5422","circuit":"e3089","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 18500; rival points: 3000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
