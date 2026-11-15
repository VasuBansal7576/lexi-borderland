# Seven-room solver witness

Success: **True**. Seed 2011; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `78ad958744f79232d8da6f635b0be2048d3d281d856be075f110c9081bbe67ba`.

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

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 104 exited; new process 105 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,1,0],"phase":3,"delta":1}
{"people":["V","I","N","S"],"sigma":1}
{"mode":"echo","offsets":[11,1,19]}
{"sectors":[0,1,3,3,0,1,2,1,2]}
{"roles":["V","S"],"source":"e7215","authority":"S"}
{"credentials":["c8685","c0214","c3057","c2511"]}
{"clock":"e9099","circuit":"e2504","main":"B"}
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
