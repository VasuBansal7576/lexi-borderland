# Seven-room solver witness

Success: **True**. Seed 2006; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `aadcd783406893ae14211e08edb8be09de379ac8a314bc9ec7cb90f2cfd6e896`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 22 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 62 exited; new process 63 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,2,1],"phase":1,"delta":1}
{"people":["N","I","S","V"],"sigma":0}
{"mode":"phase-cycle","offsets":[11,7,1]}
{"sectors":[2,2,1,0,3,2,0,1,3]}
{"roles":["I","N"],"source":"e7533","authority":"I"}
{"credentials":["c1641","c9839","c4914","c7815"]}
{"clock":"e4338","circuit":"e2031","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.97625. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 46/96 after it.
Error, if any: None.

Final allied points: 17500; rival points: 4000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
