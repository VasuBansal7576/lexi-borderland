# Seven-room solver witness

Success: **True**. Seed 2014; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `b917af423290f5c1b8f1440f1257863a7e48d56dad4948827511aae7e4575389`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 21 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 124 exited; new process 125 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,0,3,1],"phase":0,"delta":1}
{"people":["V","N","I","S"],"sigma":1}
{"mode":"mirror","offsets":[11,16,19]}
{"sectors":[2,2,1,0,3,3,0,1,0]}
{"roles":["S","I"],"source":"e2229","authority":"I"}
{"credentials":["c1418","c5972","c7290","c1251"]}
{"clock":"e5995","circuit":"e8366","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.97625. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 45/96 after it.
Error, if any: None.

Final allied points: 15000; rival points: 6500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
