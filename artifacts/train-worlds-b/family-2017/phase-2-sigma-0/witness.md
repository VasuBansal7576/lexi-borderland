# Seven-room solver witness

Success: **True**. Seed 2017; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `3cd059b889cdbf00898102235dc381ee589873bf5aab0fdd7140592a67aeb00f`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 10 | True |
| 3 | 12 | True |
| 4 | 21 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 369 bytes total; longest line 81 bytes.
Old process 146 exited; new process 147 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,1,2],"phase":2,"delta":-1}
{"people":["N","S","I","V"],"sigma":0}
{"mode":"echo","offsets":[14,19,15]}
{"sectors":[0,1,1,0,3,3,3,2,2]}
{"roles":["S","I"],"source":"e6067","authority":"I"}
{"credentials":["c3833","c7876","c8553","c8236"]}
{"clock":"e6006","circuit":"e3765","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9759375. Integrity: True. Reason: legal_escape.
Call budget use: 32/64 before the wipe, 45/96 after it.
Error, if any: None.

Final allied points: 19000; rival points: 2500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
