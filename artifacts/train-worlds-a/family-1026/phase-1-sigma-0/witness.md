# Seven-room solver witness

Success: **True**. Seed 1026; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `93620e5e5c044f881d939e5fdbe4f34dfe8d0f167ed7b68d54c7993def616dff`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 20 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 374 bytes total; longest line 81 bytes.
Old process 221 exited; new process 222 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,1,3,0],"phase":1,"delta":1}
{"people":["S","N","I","V"],"sigma":0}
{"mode":"phase-cycle","offsets":[19,1,18]}
{"sectors":[3,2,1,1,2,0,0,3,3]}
{"roles":["I","N"],"source":"e0124","authority":"S"}
{"credentials":["c0775","c6102","c2082","c9396"]}
{"clock":"e7464","circuit":"e8413","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 44/96 after it.
Error, if any: None.

Final allied points: 20200; rival points: 1300.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
