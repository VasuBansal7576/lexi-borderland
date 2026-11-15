# Seven-room solver witness

Success: **True**. Seed 1009; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `5bbf690f0ca38b7e03fa887b4fb77b8876ab64fcc9536a160befc0535f988f16`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 81 exited; new process 82 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,2,1],"phase":2,"delta":-1}
{"people":["V","I","S","N"],"sigma":0}
{"mode":"mirror","offsets":[13,5,11]}
{"sectors":[1,1,3,3,3,2,0,0,2]}
{"roles":["I","N"],"source":"e7083","authority":"V"}
{"credentials":["c5179","c4675","c1873","c9976"]}
{"clock":"e3620","circuit":"e0098","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 18900; rival points: 2600.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
