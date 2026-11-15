# Seven-room solver witness

Success: **False**. Seed 1011; interventions {'phase': 3, 'sigma': 1}.
World fingerprint: `9cd997eb9d782349726d3f875584b91f62529a1fe8ea8c7a38e749e8dd3e0189`.

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
| 7 | 1 | False |

## Actual notebook at the wipe

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 103 exited; new process 104 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,0,1,2],"phase":3,"delta":1}
{"people":["V","N","S","I"],"sigma":1}
{"mode":"mirror","offsets":[4,19,1]}
{"sectors":[3,1,2,2,1,3,0,0,2]}
{"roles":["I","N"],"source":"e3061","authority":"I"}
{"credentials":["c2814","c8889","c0572","c8154"]}
{"clock":"e7103","circuit":"e1620","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.3. Integrity: True. Reason: None.
Call budget use: 30/64 before the wipe, 31/96 after it.
Error, if any: ValueError: bounded arena search found no witness; not a proof of impossibility.

Final allied points: 0; rival points: 10000.
Allies remaining: 0. Completed arena rounds: 0.
Cache collected: False; positive post-amendment battle round: False.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
