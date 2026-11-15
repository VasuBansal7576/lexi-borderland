# Seven-room solver witness

Success: **True**. Seed 2027; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `5c7cac83c35096cefc7ca616185117ba3c5a9d95a56a0d6e3c359be7383d76cc`.

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

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 230 exited; new process 231 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,2,1],"phase":3,"delta":-1}
{"people":["N","S","I","V"],"sigma":0}
{"mode":"mirror","offsets":[19,18,4]}
{"sectors":[1,3,3,0,0,2,1,3,2]}
{"roles":["I","N"],"source":"e5408","authority":"N"}
{"credentials":["c3196","c4907","c0544","c8923"]}
{"clock":"e6847","circuit":"e2733","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 44/96 after it.
Error, if any: None.

Final allied points: 21000; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
