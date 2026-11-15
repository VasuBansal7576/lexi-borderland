# Seven-room solver witness

Success: **True**. Seed 1004; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `cd3f5651ac9e1d77069e919d65d5ba718a9df79289a07f0db550b832e2b6449e`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 43 exited; new process 44 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,2,1,3],"phase":0,"delta":-1}
{"people":["S","V","N","I"],"sigma":1}
{"mode":"echo","offsets":[0,11,0]}
{"sectors":[0,3,2,2,1,3,3,0,1]}
{"roles":["I","N"],"source":"e2455","authority":"V"}
{"credentials":["c1897","c5241","c5953","c5237"]}
{"clock":"e0504","circuit":"e6380","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
