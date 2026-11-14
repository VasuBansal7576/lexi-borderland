# Seven-room solver witness

Success: **True**. Seed 6; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `24cc03093322a1bc46be48ee3b45c2efe1b5e33d05a50440575f099389451d2e`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 14 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 88003 exited; new process 88004 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,3,2],"phase":1,"delta":1}
{"people":["I","N","S","V"],"sigma":0}
{"mode":"echo","offsets":[9,15,6]}
{"sectors":[1,1,2,0,2,3,2,0,3]}
{"roles":["I","N"],"source":"e7679","authority":"S"}
{"credentials":["c6482","c4433","c7840","c1699"]}
{"clock":"e9982","circuit":"e9974","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.97875. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 38/96 after it.
Error, if any: None.

Final allied points: 15000; rival points: 6500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
