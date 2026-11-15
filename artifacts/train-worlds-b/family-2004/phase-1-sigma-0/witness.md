# Seven-room solver witness

Success: **True**. Seed 2004; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `f96397bb544ebcb2911719e9700359724cf96d5abaa5fdfc6cbee815a3be7ef7`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 21 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 46 exited; new process 47 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,0,1],"phase":1,"delta":-1}
{"people":["V","S","N","I"],"sigma":0}
{"mode":"mirror","offsets":[4,16,17]}
{"sectors":[2,1,0,1,0,3,2,3,2]}
{"roles":["S","I"],"source":"e8215","authority":"S"}
{"credentials":["c4616","c2226","c1566","c1546"]}
{"clock":"e5202","circuit":"e5212","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9765625. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 45/96 after it.
Error, if any: None.

Final allied points: 21000; rival points: 500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
