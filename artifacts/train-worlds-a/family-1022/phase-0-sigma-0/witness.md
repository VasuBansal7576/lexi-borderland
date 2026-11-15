# Seven-room solver witness

Success: **True**. Seed 1022; interventions {'phase': 0, 'sigma': 0}.
World fingerprint: `e9810437c7710fe63dc818cfde1b16c59919d0f7d37e3676cc49c16583978184`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 369 bytes total; longest line 81 bytes.
Old process 185 exited; new process 186 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,2,1],"phase":0,"delta":-1}
{"people":["I","S","V","N"],"sigma":0}
{"mode":"echo","offsets":[16,20,11]}
{"sectors":[0,1,3,1,3,2,2,0,0]}
{"roles":["N","V"],"source":"e0966","authority":"V"}
{"credentials":["c5653","c9902","c3263","c5019"]}
{"clock":"e6960","circuit":"e6404","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
