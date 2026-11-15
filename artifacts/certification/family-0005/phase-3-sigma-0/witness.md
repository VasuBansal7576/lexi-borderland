# Seven-room solver witness

Success: **True**. Seed 5; interventions {'phase': 3, 'sigma': 0}.
World fingerprint: `dd85680b679404d2b63bf2fff35a15143e39afad7e3563703ac30986b69310f1`.

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

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 87524 exited; new process 87525 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,1,0],"phase":3,"delta":-1}
{"people":["N","V","I","S"],"sigma":0}
{"mode":"mirror","offsets":[20,6,19]}
{"sectors":[2,0,2,3,3,1,0,1,0]}
{"roles":["N","V"],"source":"e8802","authority":"I"}
{"credentials":["c9276","c3610","c4207","c2625"]}
{"clock":"e2460","circuit":"e1804","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
