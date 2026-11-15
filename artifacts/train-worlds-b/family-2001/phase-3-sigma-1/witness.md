# Seven-room solver witness

Success: **True**. Seed 2001; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `dafda42e7b78e2d08eea2a8080eeff6bc1b34b7cae5ddbbd89a350f5d7cfe71e`.

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

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 24 exited; new process 25 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,1,0,2],"phase":3,"delta":1}
{"people":["S","V","I","N"],"sigma":1}
{"mode":"echo","offsets":[3,3,18]}
{"sectors":[3,2,1,1,2,0,1,3,0]}
{"roles":["I","N"],"source":"e0906","authority":"N"}
{"credentials":["c4721","c6673","c0087","c8143"]}
{"clock":"e2661","circuit":"e9161","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 14000; rival points: 7500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
