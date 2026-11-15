# Seven-room solver witness

Success: **True**. Seed 1010; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `aba9d922eb5d74a33d91a194e6a5c2194431b5bba1cfc21725f1d18259f24969`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 14 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 93 exited; new process 94 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":1,"delta":-1}
{"people":["N","I","V","S"],"sigma":0}
{"mode":"echo","offsets":[6,15,1]}
{"sectors":[2,2,0,1,3,0,3,3,1]}
{"roles":["N","V"],"source":"e5406","authority":"V"}
{"credentials":["c5016","c4879","c3289","c7361"]}
{"clock":"e0304","circuit":"e6734","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9784375. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 38/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
