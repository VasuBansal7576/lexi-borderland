# Seven-room solver witness

Success: **True**. Seed 2025; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `505d69b2f3959ba3c817766ca5f3fc9f853f3c77ebb8cb033a0ea00bdbdf2e4d`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 376 bytes total; longest line 81 bytes.
Old process 210 exited; new process 211 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,2,1],"phase":2,"delta":-1}
{"people":["N","V","S","I"],"sigma":0}
{"mode":"phase-cycle","offsets":[17,16,15]}
{"sectors":[3,1,0,2,2,3,0,1,2]}
{"roles":["V","S"],"source":"e1697","authority":"V"}
{"credentials":["c5746","c9656","c4937","c9690"]}
{"clock":"e9999","circuit":"e7178","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9775. Integrity: True. Reason: legal_escape.
Call budget use: 31/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
