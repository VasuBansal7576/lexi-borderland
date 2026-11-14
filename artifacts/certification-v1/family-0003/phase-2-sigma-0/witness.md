# Seven-room solver witness

Success: **True**. Seed 3; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `5d007c0994523cde83fe95de67d31075a50c471571bd92dc7f607fc8f163a111`.

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
Old process 87953 exited; new process 87954 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,2,3,0],"phase":2,"delta":-1}
{"people":["I","N","V","S"],"sigma":0}
{"mode":"mirror","offsets":[20,8,11]}
{"sectors":[2,3,0,0,2,1,1,3,1]}
{"roles":["S","I"],"source":"e8044","authority":"I"}
{"credentials":["c0090","c7994","c2925","c7693"]}
{"clock":"e0554","circuit":"e7161","main":"B"}
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
