# Seven-room solver witness

Success: **True**. Seed 1023; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `eeda5d13f918ac618b9e7fa036ba983e5337607fb9ce44cde648eb4b710b1a11`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 18 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 199 exited; new process 200 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,2,3,1],"phase":3,"delta":1}
{"people":["N","I","S","V"],"sigma":1}
{"mode":"phase-cycle","offsets":[13,17,10]}
{"sectors":[2,3,0,2,2,3,1,0,1]}
{"roles":["I","N"],"source":"e7013","authority":"S"}
{"credentials":["c6835","c4834","c7527","c1926"]}
{"clock":"e0283","circuit":"e0001","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9775. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 15500; rival points: 6000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
