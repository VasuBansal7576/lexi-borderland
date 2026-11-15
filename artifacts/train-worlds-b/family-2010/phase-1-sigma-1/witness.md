# Seven-room solver witness

Success: **False**. Seed 2010; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `f1545d3c033d481cd4544bd452070b53e19ed0336f6cea2eff85bcf32f9046f1`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 9 | True |
| 3 | 12 | True |
| 4 | 14 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 1 | False |

## Actual notebook at the wipe

Eight lines; 366 bytes total; longest line 81 bytes.
Old process 96 exited; new process 97 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,0,3,1],"phase":1,"delta":1}
{"people":["I","N","S","V"],"sigma":1}
{"mode":"echo","offsets":[13,2,4]}
{"sectors":[3,3,0,2,3,0,1,2,1]}
{"roles":["V","S"],"source":"e9843","authority":"V"}
{"credentials":["c4163","c5293","c5961","c8974"]}
{"clock":"e5827","circuit":"e1523","main":"A"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.3. Integrity: True. Reason: None.
Call budget use: 31/64 before the wipe, 28/96 after it.
Error, if any: ValueError: bounded arena search found no witness; not a proof of impossibility.

Final allied points: 0; rival points: 10000.
Allies remaining: 0. Completed arena rounds: 0.
Cache collected: False; positive post-amendment battle round: False.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
