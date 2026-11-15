# Seven-room solver witness

Success: **True**. Seed 1000; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `8ddd8e3849e8b779ac23ed7f8494ccefc62b352d027f8214d39af6b82afe0c63`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 18 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 13 exited; new process 14 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,3,2],"phase":1,"delta":1}
{"people":["N","S","V","I"],"sigma":0}
{"mode":"phase-cycle","offsets":[17,6,7]}
{"sectors":[2,3,3,2,0,3,0,1,1]}
{"roles":["V","S"],"source":"e0228","authority":"N"}
{"credentials":["c1479","c7217","c4519","c2294"]}
{"clock":"e4878","circuit":"e0598","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9775. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 18800; rival points: 2700.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
