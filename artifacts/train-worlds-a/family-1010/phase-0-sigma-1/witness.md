# Seven-room solver witness

Success: **True**. Seed 1010; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `813c96be9c36199f7e0dca1eb02bad31dd05692f90d9ae3ccc848e9ff5de871a`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 15 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 91 exited; new process 92 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,0,3,2],"phase":0,"delta":-1}
{"people":["N","I","V","S"],"sigma":1}
{"mode":"echo","offsets":[6,15,1]}
{"sectors":[2,2,0,1,3,0,3,3,1]}
{"roles":["N","V"],"source":"e5406","authority":"V"}
{"credentials":["c5016","c4879","c3289","c7361"]}
{"clock":"e0304","circuit":"e6734","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 39/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
