# Seven-room solver witness

Success: **True**. Seed 7; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `e05d8ae4a02355f80e444c687d877347a160682bb5bee4924c3879a184d6f4ff`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 20 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 87548 exited; new process 87549 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,1,2],"phase":3,"delta":-1}
{"people":["N","I","S","V"],"sigma":1}
{"mode":"echo","offsets":[7,9,2]}
{"sectors":[3,1,1,0,2,2,0,1,3]}
{"roles":["N","V"],"source":"e4852","authority":"V"}
{"credentials":["c9272","c3225","c5197","c3798"]}
{"clock":"e9328","circuit":"e3726","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9765625. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 44/96 after it.
Error, if any: None.

Final allied points: 20200; rival points: 1300.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
