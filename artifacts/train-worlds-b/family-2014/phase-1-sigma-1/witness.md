# Seven-room solver witness

Success: **True**. Seed 2014; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `1b1e6d2dde7ad4c95af3573e4b182d095c236e31a8d0c511518974004e17feb5`.

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

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 128 exited; new process 129 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,0,3,1],"phase":1,"delta":1}
{"people":["V","N","I","S"],"sigma":1}
{"mode":"mirror","offsets":[11,16,19]}
{"sectors":[2,2,1,0,3,3,0,1,0]}
{"roles":["S","I"],"source":"e2229","authority":"I"}
{"credentials":["c1418","c5972","c7290","c1251"]}
{"clock":"e5995","circuit":"e8366","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9765625. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 44/96 after it.
Error, if any: None.

Final allied points: 17500; rival points: 3500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
