# Seven-room solver witness

Success: **True**. Seed 2029; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `cfb926745f1d2919d1f4b4275ee723b3c05d66a2a2151b04c050712289e1b7c0`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 23 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 374 bytes total; longest line 81 bytes.
Old process 242 exited; new process 243 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,2,1,3],"phase":2,"delta":-1}
{"people":["S","V","I","N"],"sigma":0}
{"mode":"phase-cycle","offsets":[12,1,6]}
{"sectors":[1,3,2,3,0,2,0,0,1]}
{"roles":["N","V"],"source":"e4170","authority":"I"}
{"credentials":["c3081","c8606","c1873","c0574"]}
{"clock":"e3034","circuit":"e9271","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9759375. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 47/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
