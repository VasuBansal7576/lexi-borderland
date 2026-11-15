# Seven-room solver witness

Success: **True**. Seed 1019; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `7d64cfbb09d5e09fb1fdc1b2d8ab15258a3f06b94db74f46169019dcaba9301b`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 20 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 376 bytes total; longest line 81 bytes.
Old process 163 exited; new process 164 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,0,1],"phase":2,"delta":-1}
{"people":["V","N","I","S"],"sigma":1}
{"mode":"phase-cycle","offsets":[17,14,15]}
{"sectors":[2,0,2,3,0,1,0,3,1]}
{"roles":["S","I"],"source":"e6430","authority":"S"}
{"credentials":["c6673","c0241","c7922","c0913"]}
{"clock":"e3974","circuit":"e8531","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.976875. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 44/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
