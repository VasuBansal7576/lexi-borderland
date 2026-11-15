# Seven-room solver witness

Success: **False**. Seed 1017; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `028708a681fafff5110b44459786647830c4eb89911ae6128e0a9c2c65f0cecc`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 19 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 1 | False |

## Actual notebook at the wipe

Eight lines; 365 bytes total; longest line 81 bytes.
Old process 145 exited; new process 146 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,1,0],"phase":2,"delta":1}
{"people":["N","V","S","I"],"sigma":0}
{"mode":"echo","offsets":[3,2,6]}
{"sectors":[3,1,0,1,2,0,2,3,3]}
{"roles":["I","N"],"source":"e5392","authority":"I"}
{"credentials":["c9580","c2780","c5952","c8976"]}
{"clock":"e4675","circuit":"e5919","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.3. Integrity: True. Reason: None.
Call budget use: 30/64 before the wipe, 33/96 after it.
Error, if any: ValueError: bounded arena search found no witness; not a proof of impossibility.

Final allied points: 0; rival points: 10000.
Allies remaining: 0. Completed arena rounds: 0.
Cache collected: False; positive post-amendment battle round: False.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
