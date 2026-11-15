# Seven-room solver witness

Success: **True**. Seed 2000; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `193c7ccc12cc48610bd5f6762727ac694f572bde4986ff0a7706cb8d9670b49a`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 19 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 14 exited; new process 15 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,3,2,0],"phase":1,"delta":-1}
{"people":["S","V","I","N"],"sigma":0}
{"mode":"echo","offsets":[5,1,15]}
{"sectors":[1,1,3,1,2,0,3,0,2]}
{"roles":["I","N"],"source":"e0437","authority":"N"}
{"credentials":["c4867","c6845","c0470","c1308"]}
{"clock":"e0594","circuit":"e6421","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 17500; rival points: 4000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
