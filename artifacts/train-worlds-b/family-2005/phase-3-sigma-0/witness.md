# Seven-room solver witness

Success: **True**. Seed 2005; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `717cd0fadedd3a9422f0d741d8034d12fd8bcf7e8b3edbf8eaabf92a7a1534ea`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 15 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 374 bytes total; longest line 81 bytes.
Old process 54 exited; new process 55 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,3,2],"phase":3,"delta":1}
{"people":["V","N","S","I"],"sigma":0}
{"mode":"phase-cycle","offsets":[20,3,14]}
{"sectors":[2,1,0,3,3,3,1,0,2]}
{"roles":["V","S"],"source":"e3328","authority":"N"}
{"credentials":["c9255","c6014","c9911","c2618"]}
{"clock":"e9861","circuit":"e4571","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9784375. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 39/96 after it.
Error, if any: None.

Final allied points: 19000; rival points: 2500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
