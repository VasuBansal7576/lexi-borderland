# Seven-room solver witness

Success: **True**. Seed 1000; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `2ffa8462f7a21c20eb31228c9710cd703f3a0cd5da9be16e5d7640b1a9eda8b4`.

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

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 11 exited; new process 12 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,3,2],"phase":0,"delta":1}
{"people":["N","S","V","I"],"sigma":1}
{"mode":"phase-cycle","offsets":[17,6,7]}
{"sectors":[2,3,3,2,0,3,0,1,1]}
{"roles":["V","S"],"source":"e0228","authority":"N"}
{"credentials":["c1479","c7217","c4519","c2294"]}
{"clock":"e4878","circuit":"e0598","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 40/96 after it.
Error, if any: None.

Final allied points: 17000; rival points: 4000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
