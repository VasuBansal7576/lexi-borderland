# Seven-room solver witness

Success: **True**. Seed 1029; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `8e2b9db5ee04fe544d62d5fa8a2f8cf067e5cf4fff1994a8813d187534e5f1b8`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 18 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 245 exited; new process 246 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,0,1,3],"phase":3,"delta":1}
{"people":["N","I","S","V"],"sigma":0}
{"mode":"phase-cycle","offsets":[5,6,15]}
{"sectors":[2,1,2,0,1,3,3,3,0]}
{"roles":["S","I"],"source":"e7575","authority":"V"}
{"credentials":["c0585","c8278","c7353","c3245"]}
{"clock":"e7825","circuit":"e2653","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 15500; rival points: 6000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
