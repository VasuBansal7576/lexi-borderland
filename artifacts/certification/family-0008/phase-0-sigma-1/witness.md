# Seven-room solver witness

Success: **True**. Seed 8; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `b5eb9a75882bfcf5499535a2f7c5b04dfb5a7f58bf64c8dfc1ca6e89bb5471e1`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 19 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 87556 exited; new process 87557 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,3,1,0],"phase":0,"delta":-1}
{"people":["I","V","N","S"],"sigma":1}
{"mode":"mirror","offsets":[10,5,20]}
{"sectors":[2,2,2,3,1,0,1,0,3]}
{"roles":["S","I"],"source":"e9828","authority":"N"}
{"credentials":["c0880","c5277","c0744","c0074"]}
{"clock":"e3963","circuit":"e2146","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.976875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
