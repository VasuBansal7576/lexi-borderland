# Seven-room solver witness

Success: **True**. Seed 2008; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `dc0c235d6002b74f0cffd9ff752ef82d39ee9c3a44273896f55f0c55b52a23d7`.

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

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 80 exited; new process 81 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,1,0,2],"phase":1,"delta":-1}
{"people":["I","V","N","S"],"sigma":1}
{"mode":"phase-cycle","offsets":[3,17,20]}
{"sectors":[0,1,0,2,3,0,3,1,2]}
{"roles":["I","N"],"source":"e5661","authority":"N"}
{"credentials":["c4554","c2825","c6640","c6905"]}
{"clock":"e9995","circuit":"e5181","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 39/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
