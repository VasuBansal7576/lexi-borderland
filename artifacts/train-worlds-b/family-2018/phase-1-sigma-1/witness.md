# Seven-room solver witness

Success: **True**. Seed 2018; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `45493b3e309b5e38a33be8b8f67422911eeded0cbef2d478ac4aed7777ca7af8`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 18 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 160 exited; new process 161 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,1,3,0],"phase":1,"delta":1}
{"people":["S","V","N","I"],"sigma":1}
{"mode":"phase-cycle","offsets":[9,19,1]}
{"sectors":[2,3,0,1,0,3,2,0,1]}
{"roles":["V","S"],"source":"e0596","authority":"I"}
{"credentials":["c7654","c7337","c6614","c3503"]}
{"clock":"e3083","circuit":"e1914","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 15500; rival points: 6000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
