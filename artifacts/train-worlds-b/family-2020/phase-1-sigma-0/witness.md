# Seven-room solver witness

Success: **True**. Seed 2020; interventions {'phase': 1, 'sigma': 0}.
World fingerprint: `954f936288d7279c2db3c709d44ab7d096c8eaaacb44f8739b13820150510b87`.

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

Eight lines; 375 bytes total; longest line 81 bytes.
Old process 174 exited; new process 175 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,2,3,0],"phase":1,"delta":-1}
{"people":["V","N","S","I"],"sigma":0}
{"mode":"phase-cycle","offsets":[4,11,19]}
{"sectors":[2,0,3,0,1,1,2,2,3]}
{"roles":["V","S"],"source":"e5044","authority":"V"}
{"credentials":["c6886","c0139","c8632","c6130"]}
{"clock":"e2245","circuit":"e0823","main":"B"}
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
