# Seven-room solver witness

Success: **True**. Seed 1023; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `99e3c8cc53ddb06abea9cc1e1820f7936f32bf2181ef2733c124fa895b7f7af9`.

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

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 193 exited; new process 194 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,2,3,1],"phase":2,"delta":1}
{"people":["N","I","S","V"],"sigma":0}
{"mode":"phase-cycle","offsets":[13,17,10]}
{"sectors":[2,3,0,2,2,3,1,0,1]}
{"roles":["I","N"],"source":"e7013","authority":"S"}
{"credentials":["c6835","c4834","c7527","c1926"]}
{"clock":"e0283","circuit":"e0001","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 19300; rival points: 2200.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
