# Seven-room solver witness

Success: **True**. Seed 2019; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `269b2d2aa9b3cd5dc453e1716eaf2a3492961d039f44f0d9e8d0e9868936e180`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 374 bytes total; longest line 81 bytes.
Old process 164 exited; new process 165 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,2,1,3],"phase":2,"delta":1}
{"people":["N","V","I","S"],"sigma":1}
{"mode":"phase-cycle","offsets":[14,16,3]}
{"sectors":[2,0,1,2,0,3,3,3,1]}
{"roles":["V","S"],"source":"e0820","authority":"I"}
{"credentials":["c0903","c3385","c3956","c0255"]}
{"clock":"e7914","circuit":"e4683","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 15000; rival points: 6500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
