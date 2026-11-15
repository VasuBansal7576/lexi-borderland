# Seven-room solver witness

Success: **True**. Seed 1014; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `8fd763b7b50548757b9374d6e29f73494a3ce4f70a787d3c76c1a0bb55ab679e`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 17 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 369 bytes total; longest line 81 bytes.
Old process 127 exited; new process 128 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,0,1],"phase":1,"delta":1}
{"people":["S","I","V","N"],"sigma":1}
{"mode":"mirror","offsets":[14,0,18]}
{"sectors":[2,3,1,0,2,0,3,2,1]}
{"roles":["N","V"],"source":"e0164","authority":"N"}
{"credentials":["c0872","c2955","c0527","c5194"]}
{"clock":"e4422","circuit":"e1487","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 16000; rival points: 5500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
