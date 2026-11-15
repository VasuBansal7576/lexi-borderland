# Seven-room solver witness

Success: **True**. Seed 1011; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `decc4b5e5a7a18ac84d86b87a31fe8cd7ddbe7c3703477b4f3879f556ffd077d`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 16 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 97 exited; new process 98 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,1,2],"phase":2,"delta":1}
{"people":["V","N","S","I"],"sigma":0}
{"mode":"mirror","offsets":[4,19,1]}
{"sectors":[3,1,2,2,1,3,0,0,2]}
{"roles":["I","N"],"source":"e3061","authority":"I"}
{"credentials":["c2814","c8889","c0572","c8154"]}
{"clock":"e7103","circuit":"e1620","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 18300; rival points: 2700.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
