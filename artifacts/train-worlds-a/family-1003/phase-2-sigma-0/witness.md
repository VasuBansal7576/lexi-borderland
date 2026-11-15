# Seven-room solver witness

Success: **True**. Seed 1003; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `14936f6fe07bf80ca4bdc0b679a0123185232164b73f7f83d6d4342ea962d5d9`.

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

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 33 exited; new process 34 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":2,"delta":-1}
{"people":["I","S","N","V"],"sigma":0}
{"mode":"mirror","offsets":[8,1,5]}
{"sectors":[3,2,1,3,1,0,0,0,2]}
{"roles":["I","N"],"source":"e1410","authority":"N"}
{"credentials":["c0725","c5417","c7027","c1509"]}
{"clock":"e8674","circuit":"e2682","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 20700; rival points: 300.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
