# Seven-room solver witness

Success: **True**. Seed 13; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `7544e359bccf91a0fcbf8250abbd4a8d9a25a7e7d47ee6390fb3725056166032`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 369 bytes total; longest line 81 bytes.
Old process 123 exited; new process 124 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,0,1],"phase":3,"delta":1}
{"people":["S","V","I","N"],"sigma":1}
{"mode":"mirror","offsets":[3,13,11]}
{"sectors":[0,1,3,0,2,1,2,2,3]}
{"roles":["V","S"],"source":"e3890","authority":"V"}
{"credentials":["c5989","c4573","c5782","c9671"]}
{"clock":"e5977","circuit":"e5921","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 16000; rival points: 5500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
