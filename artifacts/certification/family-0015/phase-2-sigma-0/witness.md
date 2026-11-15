# Seven-room solver witness

Success: **True**. Seed 15; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `9698e95b0a64bc2540d99558328ce56f29f2b7d53c5ec5c825a139fb4d6a2347`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 19 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 87664 exited; new process 87665 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,0,1],"phase":2,"delta":-1}
{"people":["I","V","N","S"],"sigma":0}
{"mode":"mirror","offsets":[3,6,1]}
{"sectors":[3,3,1,1,0,2,2,3,0]}
{"roles":["S","I"],"source":"e2837","authority":"V"}
{"credentials":["c2026","c0767","c7445","c2036"]}
{"clock":"e1667","circuit":"e6806","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9775. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 17000; rival points: 4500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
