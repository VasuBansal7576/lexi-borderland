# Seven-room solver witness

Success: **True**. Seed 10; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `8bfccbfc843f681466db13b8433271e7aa9080b460a2214a7c065efaaf561856`.

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

Eight lines; 368 bytes total; longest line 81 bytes.
Old process 88053 exited; new process 88056 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[2,1,0,3],"phase":0,"delta":-1}
{"people":["N","V","S","I"],"sigma":1}
{"mode":"mirror","offsets":[9,4,5]}
{"sectors":[3,1,2,0,1,2,0,0,3]}
{"roles":["S","I"],"source":"e0027","authority":"I"}
{"credentials":["c2011","c6320","c0632","c9233"]}
{"clock":"e7140","circuit":"e7971","main":"A"}
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
