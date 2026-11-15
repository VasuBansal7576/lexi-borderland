# Seven-room solver witness

Success: **True**. Seed 2026; interventions {'phase': 0, 'sigma': 0}.
World fingerprint: `36ec9fd22ca98d88988d3b96c19c9eaa26e3dbf97e37cbc97d4f71ed0d9c9c6a`.

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

Eight lines; 371 bytes total; longest line 81 bytes.
Old process 218 exited; new process 219 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,1,0],"phase":0,"delta":-1}
{"people":["S","V","I","N"],"sigma":0}
{"mode":"mirror","offsets":[12,14,10]}
{"sectors":[2,2,1,2,3,0,1,3,0]}
{"roles":["I","N"],"source":"e7008","authority":"I"}
{"credentials":["c0025","c5456","c8277","c6883"]}
{"clock":"e8975","circuit":"e5739","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
