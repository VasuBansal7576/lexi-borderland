# Seven-room solver witness

Success: **True**. Seed 2021; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `99f8f56f81afb20059ee8546c59a2ec467f9544c728f308d8323d0160b05b9fb`.

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

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 184 exited; new process 185 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,0,1,3],"phase":3,"delta":-1}
{"people":["V","N","S","I"],"sigma":1}
{"mode":"phase-cycle","offsets":[13,14,0]}
{"sectors":[3,0,2,0,0,1,3,2,1]}
{"roles":["V","S"],"source":"e4756","authority":"S"}
{"credentials":["c4624","c9615","c4026","c8631"]}
{"clock":"e1692","circuit":"e6591","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
