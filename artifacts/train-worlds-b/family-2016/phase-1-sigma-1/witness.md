# Seven-room solver witness

Success: **True**. Seed 2016; interventions {'phase': 1, 'sigma': 1}.
World fingerprint: `d423642593de02b208116d0e5235d4c8e20b1895dd7c9c9efe9e00add1e5eb1e`.

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

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 144 exited; new process 145 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,1,0,2],"phase":1,"delta":-1}
{"people":["I","V","N","S"],"sigma":1}
{"mode":"phase-cycle","offsets":[8,4,5]}
{"sectors":[1,1,0,3,2,3,2,2,0]}
{"roles":["S","I"],"source":"e3194","authority":"V"}
{"credentials":["c9601","c9520","c5391","c6017"]}
{"clock":"e8760","circuit":"e7621","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9778125. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 42/96 after it.
Error, if any: None.

Final allied points: 21000; rival points: 500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
