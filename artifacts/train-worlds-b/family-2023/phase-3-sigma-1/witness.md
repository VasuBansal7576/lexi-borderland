# Seven-room solver witness

Success: **True**. Seed 2023; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `b1a8fb8fa41d72d12ef771e5e87c12c2aeecb19dd2df5ea3ed0a2d6e7c6b8a6e`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 200 exited; new process 201 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,1,2],"phase":3,"delta":1}
{"people":["S","V","I","N"],"sigma":1}
{"mode":"echo","offsets":[15,10,18]}
{"sectors":[1,1,0,3,2,0,1,3,2]}
{"roles":["V","S"],"source":"e7267","authority":"N"}
{"credentials":["c4259","c2976","c1700","c7634"]}
{"clock":"e9676","circuit":"e0251","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 19500; rival points: 2000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
