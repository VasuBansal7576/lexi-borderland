# Seven-room solver witness

Success: **True**. Seed 1027; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `434d3bb1e3b64844abc6427582f06f50c537f5551d38721009fae1dad7f03da9`.

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

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 231 exited; new process 232 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,1,2],"phase":3,"delta":1}
{"people":["S","V","N","I"],"sigma":1}
{"mode":"echo","offsets":[20,0,0]}
{"sectors":[1,2,3,0,0,3,2,1,3]}
{"roles":["S","I"],"source":"e9100","authority":"I"}
{"credentials":["c5173","c4133","c7901","c6841"]}
{"clock":"e2538","circuit":"e6460","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.97625. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 46/96 after it.
Error, if any: None.

Final allied points: 15500; rival points: 5500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
