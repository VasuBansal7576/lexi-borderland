# Seven-room solver witness

Success: **True**. Seed 1018; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `443d4d040feeec291d4a71b88c22cb325096fd06a7543cf74e14dcfa9ed8cd6f`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 376 bytes total; longest line 81 bytes.
Old process 157 exited; new process 158 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,3,2],"phase":1,"delta":-1}
{"people":["I","S","V","N"],"sigma":0}
{"mode":"phase-cycle","offsets":[14,15,14]}
{"sectors":[3,1,0,2,0,2,1,0,3]}
{"roles":["V","S"],"source":"e4837","authority":"I"}
{"credentials":["c2186","c2368","c9807","c0189"]}
{"clock":"e3275","circuit":"e5700","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
