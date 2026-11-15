# Seven-room solver witness

Success: **True**. Seed 2; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `9b2cba26af4943bb4320c27379443f5b47d05555a0d2b27cc1560cc5e44c87e5`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 24 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 87484 exited; new process 87485 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,3,0,1],"phase":1,"delta":1}
{"people":["S","N","V","I"],"sigma":0}
{"mode":"echo","offsets":[17,7,18]}
{"sectors":[1,2,3,1,3,0,2,0,2]}
{"roles":["V","S"],"source":"e3466","authority":"S"}
{"credentials":["c0598","c8079","c9569","c7750"]}
{"clock":"e5422","circuit":"e3089","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.975625. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 48/96 after it.
Error, if any: None.

Final allied points: 17000; rival points: 4500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
