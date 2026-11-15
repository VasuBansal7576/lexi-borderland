# Seven-room solver witness

Success: **True**. Seed 2030; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `9729f521ac55d7def39b24f4c44845dd8631b6e1fdab396f33c30c2c81cee191`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 18 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 367 bytes total; longest line 81 bytes.
Old process 256 exited; new process 257 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,2,1,0],"phase":1,"delta":1}
{"people":["I","N","S","V"],"sigma":1}
{"mode":"echo","offsets":[19,7,16]}
{"sectors":[3,3,1,2,0,0,2,1,2]}
{"roles":["S","I"],"source":"e9952","authority":"S"}
{"credentials":["c5177","c2089","c2578","c1933"]}
{"clock":"e2776","circuit":"e4466","main":"B"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 17000; rival points: 4500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
