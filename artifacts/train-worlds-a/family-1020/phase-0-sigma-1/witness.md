# Seven-room solver witness

Success: **True**. Seed 1020; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `7348e2e2b442186f7f87288480ed66da4654bb56b5e08b302249261b3c6c1151`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 10 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 171 exited; new process 172 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,2,1],"phase":0,"delta":-1}
{"people":["N","I","S","V"],"sigma":1}
{"mode":"echo","offsets":[0,17,2]}
{"sectors":[2,3,3,1,2,0,1,0,3]}
{"roles":["S","I"],"source":"e8458","authority":"V"}
{"credentials":["c0611","c8502","c0515","c5039"]}
{"clock":"e7136","circuit":"e6919","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 32/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
