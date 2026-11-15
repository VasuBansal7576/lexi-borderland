# Seven-room solver witness

Success: **True**. Seed 1031; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `c82d748d4368f4089ce7a1e0ecb6bd5a8f450f56a18bf7d3673191521a6b1b89`.

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

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 259 exited; new process 260 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,1,3,2],"phase":2,"delta":-1}
{"people":["I","S","V","N"],"sigma":1}
{"mode":"phase-cycle","offsets":[2,2,7]}
{"sectors":[1,0,1,2,0,3,0,3,2]}
{"roles":["N","V"],"source":"e5714","authority":"V"}
{"credentials":["c4509","c7097","c3083","c8649"]}
{"clock":"e8471","circuit":"e0936","main":"D"}
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
