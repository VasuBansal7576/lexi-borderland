# Seven-room solver witness

Success: **True**. Seed 12; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `5042616ef0a3ae0df22a9747743630fcc654f58739e4d32c4f1098d670a2d9b0`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 18 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 87627 exited; new process 87629 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,2,3],"phase":1,"delta":1}
{"people":["N","I","V","S"],"sigma":1}
{"mode":"echo","offsets":[2,2,14]}
{"sectors":[2,2,3,3,2,1,0,0,1]}
{"roles":["N","V"],"source":"e3034","authority":"S"}
{"credentials":["c8751","c7171","c1820","c7289"]}
{"clock":"e9823","circuit":"e3784","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 12000; rival points: 9500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
