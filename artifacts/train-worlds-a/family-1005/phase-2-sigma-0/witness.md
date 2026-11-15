# Seven-room solver witness

Success: **True**. Seed 1005; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `6e5b131c20bd291719a1afc5c49c49f3fae72874b8b9eafe54dd69fdb84334d5`.

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

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 49 exited; new process 50 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":2,"delta":1}
{"people":["I","N","S","V"],"sigma":0}
{"mode":"echo","offsets":[1,0,16]}
{"sectors":[0,3,1,0,2,3,2,2,1]}
{"roles":["I","N"],"source":"e5980","authority":"N"}
{"credentials":["c3401","c5725","c9327","c8771"]}
{"clock":"e6463","circuit":"e5397","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 19000; rival points: 2500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
