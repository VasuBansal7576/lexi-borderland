# Seven-room solver witness

Success: **True**. Seed 2023; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `43cbea809d738375e57d752178380b88b5ec40051ca13b6e07d6da433d849e63`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 196 exited; new process 197 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,1,2],"phase":2,"delta":1}
{"people":["S","V","I","N"],"sigma":1}
{"mode":"echo","offsets":[15,10,18]}
{"sectors":[1,1,0,3,2,0,1,3,2]}
{"roles":["V","S"],"source":"e7267","authority":"N"}
{"credentials":["c4259","c2976","c1700","c7634"]}
{"clock":"e9676","circuit":"e0251","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 19100; rival points: 2400.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
