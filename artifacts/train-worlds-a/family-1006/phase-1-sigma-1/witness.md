# Seven-room solver witness

Success: **True**. Seed 1006; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `3d9cd4622e0ed3de97db8d7a58be083867484be53fc68b0c82dca3b29f2dd991`.

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

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 63 exited; new process 64 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,2,3,1],"phase":1,"delta":-1}
{"people":["I","S","V","N"],"sigma":1}
{"mode":"echo","offsets":[5,10,5]}
{"sectors":[3,2,3,1,1,3,2,0,0]}
{"roles":["S","I"],"source":"e7352","authority":"S"}
{"credentials":["c2061","c1923","c1763","c9617"]}
{"clock":"e4311","circuit":"e2024","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.976875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 21000; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
