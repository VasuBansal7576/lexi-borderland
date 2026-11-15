# Seven-room solver witness

Success: **True**. Seed 2003; interventions {'phase': 2, 'sigma': 1}.
World fingerprint: `12cc1ff1db320ddd38278c155eff22030e683c5abb97a066a6c2196c2e785688`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 8 | True |
| 3 | 12 | True |
| 4 | 15 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 370 bytes total; longest line 81 bytes.
Old process 36 exited; new process 37 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[1,3,2,0],"phase":2,"delta":-1}
{"people":["N","V","S","I"],"sigma":1}
{"mode":"mirror","offsets":[18,4,14]}
{"sectors":[2,0,0,3,1,2,1,3,3]}
{"roles":["S","I"],"source":"e0246","authority":"I"}
{"credentials":["c8990","c0218","c2159","c3420"]}
{"clock":"e9291","circuit":"e8087","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9784375. Integrity: True. Reason: legal_escape.
Call budget use: 30/64 before the wipe, 39/96 after it.
Error, if any: None.

Final allied points: 21500; rival points: 0.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
