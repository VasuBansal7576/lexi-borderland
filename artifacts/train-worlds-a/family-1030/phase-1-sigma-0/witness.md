# Seven-room solver witness

Success: **True**. Seed 1030; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `adea1fc93ac88e1d135b1de11952c2b01371a0485f20b761a69c2bf536369e1e`.

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

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 253 exited; new process 254 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,2,3],"phase":1,"delta":-1}
{"people":["S","V","I","N"],"sigma":0}
{"mode":"echo","offsets":[14,2,4]}
{"sectors":[0,1,2,3,2,1,1,3,0]}
{"roles":["I","N"],"source":"e1970","authority":"V"}
{"credentials":["c5616","c7470","c8904","c4741"]}
{"clock":"e8618","circuit":"e4689","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 20900; rival points: 600.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
