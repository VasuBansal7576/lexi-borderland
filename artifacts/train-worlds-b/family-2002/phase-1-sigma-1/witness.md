# Seven-room solver witness

Success: **True**. Seed 2002; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `20c81c8089873d8be584970481e847593e7745ae4d7389c2683fe44d75c86c56`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 20 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 365 bytes total; longest line 81 bytes.
Old process 32 exited; new process 33 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,3,0,2],"phase":1,"delta":1}
{"people":["S","N","I","V"],"sigma":1}
{"mode":"echo","offsets":[7,3,3]}
{"sectors":[1,0,2,0,3,2,3,1,3]}
{"roles":["N","V"],"source":"e1743","authority":"S"}
{"credentials":["c3920","c8036","c2073","c1649"]}
{"clock":"e3201","circuit":"e0601","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9765625. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 44/96 after it.
Error, if any: None.

Final allied points: 15500; rival points: 6000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
