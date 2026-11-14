# Seven-room solver witness

Success: **True**. Seed 0; interventions {'phase': 0, 'sigma': 0}.
World fingerprint: `a06a46c36d3d2be2221375038ed8152e7c1df809cfc927b57cc43273409bc47e`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 23 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 371 bytes total; longest line 81 bytes.
Old process 87898 exited; new process 87899 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,1,2],"phase":0,"delta":-1}
{"people":["I","V","N","S"],"sigma":0}
{"mode":"mirror","offsets":[16,10,18]}
{"sectors":[3,1,2,1,2,0,0,2,3]}
{"roles":["V","S"],"source":"e7041","authority":"I"}
{"credentials":["c7008","c3531","c7128","c1519"]}
{"clock":"e0883","circuit":"e0247","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.97625. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 47/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
