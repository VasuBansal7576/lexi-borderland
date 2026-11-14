# Seven-room solver witness

Success: **True**. Seed 1; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `9ff14fbbfd6ee3fd1cc55471e33309575192b180a450ad9dd63a06d6b9979171`.

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

Eight lines; 374 bytes total; longest line 81 bytes.
Old process 23 exited; new process 24 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,3,2,0],"phase":2,"delta":1}
{"people":["I","V","S","N"],"sigma":1}
{"mode":"phase-cycle","offsets":[12,8,19]}
{"sectors":[3,2,3,0,1,2,2,0,1]}
{"roles":["V","S"],"source":"e1602","authority":"I"}
{"credentials":["c5100","c1763","c4384","c6652"]}
{"clock":"e6053","circuit":"e3635","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 13500; rival points: 8000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
