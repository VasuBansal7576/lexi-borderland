# Seven-room solver witness

Success: **True**. Seed 2015; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `a830d279f10f9c60c2cf28d9f4b2a9aee84daded2b49c29d029aa8a77339d213`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 134 exited; new process 135 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":3,"delta":1}
{"people":["N","V","S","I"],"sigma":0}
{"mode":"mirror","offsets":[7,19,2]}
{"sectors":[1,1,3,2,2,0,3,1,0]}
{"roles":["I","N"],"source":"e9971","authority":"N"}
{"credentials":["c7334","c4578","c0913","c4648"]}
{"clock":"e8157","circuit":"e6473","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 19000; rival points: 2500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
