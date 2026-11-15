# Seven-room solver witness

Success: **False**. Seed 2008; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `edd1a890ae7060bd4442d2815dd63170f3251f8534bafcf2309f789bfdbb2d12`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 0 | False |
| 6 | 0 | False |
| 7 | 0 | False |

## Actual notebook at the wipe

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 76 exited; new process 77 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,1,0,2],"phase":0,"delta":-1}
{"people":["I","V","N","S"],"sigma":1}
{"mode":"phase-cycle","offsets":[3,17,20]}
{"sectors":[0,1,0,2,3,0,3,1,2]}
{"roles":["I","N"],"source":"e5661","authority":"N"}
{"credentials":["c4554","c2825","c6640","c6905"]}
{"clock":"e9995","circuit":"e5181","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.2. Integrity: True. Reason: None.
Call budget use: 31/64 before the wipe, 16/96 after it.
Error, if any: ValueError: no winning Balance sequence in inferred model.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
