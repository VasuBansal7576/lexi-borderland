# Seven-room solver witness

Success: **True**. Seed 9; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `0bc8ae308bb5549cfd30f83f46abe8224b6667c1cbc106b00c07a5025fcfa494`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 15 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 372 bytes total; longest line 81 bytes.
Old process 87566 exited; new process 87567 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,1,2,0],"phase":2,"delta":1}
{"people":["I","S","N","V"],"sigma":0}
{"mode":"phase-cycle","offsets":[9,5,5]}
{"sectors":[2,1,0,3,3,2,0,0,1]}
{"roles":["S","I"],"source":"e7737","authority":"N"}
{"credentials":["c9585","c9278","c6840","c6510"]}
{"clock":"e7055","circuit":"e1132","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 39/96 after it.
Error, if any: None.

Final allied points: 17500; rival points: 4000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
