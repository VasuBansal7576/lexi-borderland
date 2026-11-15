# Seven-room solver witness

Success: **True**. Seed 0; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `5128fd6c9ae97160770583770540ec6376621a699708296c3a10f3532182af14`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 371 bytes total; longest line 81 bytes.
Old process 87450 exited; new process 87451 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,1,2],"phase":1,"delta":-1}
{"people":["I","V","N","S"],"sigma":1}
{"mode":"mirror","offsets":[16,10,18]}
{"sectors":[3,1,2,1,2,0,0,2,3]}
{"roles":["V","S"],"source":"e7041","authority":"I"}
{"credentials":["c7008","c3531","c7128","c1519"]}
{"clock":"e0883","circuit":"e0247","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9784375. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 20800; rival points: 700.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
