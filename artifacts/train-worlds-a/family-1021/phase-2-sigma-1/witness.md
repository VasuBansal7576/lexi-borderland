# Seven-room solver witness

Success: **True**. Seed 1021; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `d01fc9adcc0d6335fcad1396fc3cada0adb988e2b4af760a19207c61153df02f`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 15 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 179 exited; new process 180 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,1,2,0],"phase":2,"delta":1}
{"people":["V","S","I","N"],"sigma":1}
{"mode":"phase-cycle","offsets":[20,3,5]}
{"sectors":[2,0,1,3,1,2,0,2,3]}
{"roles":["I","N"],"source":"e4544","authority":"N"}
{"credentials":["c9853","c9154","c9629","c1146"]}
{"clock":"e9695","circuit":"e4848","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 39/96 after it.
Error, if any: None.

Final allied points: 19400; rival points: 2100.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
