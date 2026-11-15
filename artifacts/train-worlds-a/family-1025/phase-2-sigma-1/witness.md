# Seven-room solver witness

Success: **True**. Seed 1025; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `ef5f1d7f3ad6a982d5a46d081faaebc639a38483255b29b37077db08f8c0d06d`.

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

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 211 exited; new process 212 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,3,1,0],"phase":2,"delta":-1}
{"people":["S","N","I","V"],"sigma":1}
{"mode":"phase-cycle","offsets":[7,19,12]}
{"sectors":[0,1,2,2,2,3,1,0,3]}
{"roles":["N","V"],"source":"e1366","authority":"N"}
{"credentials":["c2085","c3309","c3067","c0040"]}
{"clock":"e6918","circuit":"e9363","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9771875. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
