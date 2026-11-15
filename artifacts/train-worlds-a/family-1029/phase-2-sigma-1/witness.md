# Seven-room solver witness

Success: **True**. Seed 1029; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `f5bf5425ae5db4a5323692fcedfe61b8794b84694b2a8086c9bf6acd83d4318e`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 19 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 243 exited; new process 244 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,0,1,3],"phase":2,"delta":1}
{"people":["N","I","S","V"],"sigma":1}
{"mode":"phase-cycle","offsets":[5,6,15]}
{"sectors":[2,1,2,0,1,3,3,3,0]}
{"roles":["S","I"],"source":"e7575","authority":"V"}
{"credentials":["c0585","c8278","c7353","c3245"]}
{"clock":"e7825","circuit":"e2653","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.976875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 18000; rival points: 3500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
