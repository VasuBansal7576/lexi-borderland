# Seven-room solver witness

Success: **True**. Seed 6; interventions {'phase': 0, 'sigma': 0}.
World fingerprint: `0101b8c3274ecb00e92e4e9eeb40999c58d8123213a4e5f23448ff70c8737006`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 87997 exited; new process 87998 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,3,2],"phase":0,"delta":1}
{"people":["I","N","S","V"],"sigma":0}
{"mode":"echo","offsets":[9,15,6]}
{"sectors":[1,1,2,0,2,3,2,0,3]}
{"roles":["I","N"],"source":"e7679","authority":"S"}
{"credentials":["c6482","c4433","c7840","c1699"]}
{"clock":"e9982","circuit":"e9974","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 12000; rival points: 9500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
