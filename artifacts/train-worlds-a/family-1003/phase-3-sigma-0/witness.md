# Seven-room solver witness

Success: **True**. Seed 1003; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `0ae9c43e10ffdcb8b2502926756ca970ec6d3c5ce842b8e8db3d4c98c1d921ea`.

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
Old process 37 exited; new process 38 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":3,"delta":-1}
{"people":["I","S","N","V"],"sigma":0}
{"mode":"mirror","offsets":[8,1,5]}
{"sectors":[3,2,1,3,1,0,0,0,2]}
{"roles":["I","N"],"source":"e1410","authority":"N"}
{"credentials":["c0725","c5417","c7027","c1509"]}
{"clock":"e8674","circuit":"e2682","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 21300; rival points: 200.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
