# Seven-room solver witness

Success: **True**. Seed 2016; interventions {'phase': 0, 'sigma': 1}.
World fingerprint: `7e24478dbd4e68cf406a1d38c2bd1f16fda768ce294ad3a7e27d2990c0204738`.

The solver ran in isolated interpreters, without the generator, environment, seed, private manifest or filesystem access.
This proves existence of a legal solver trajectory for this world, not LLM learning or universal solvability.

| Room | Tool calls | Cleared |
| --- | ---: | --- |
| 1 | 10 | True |
| 2 | 7 | True |
| 3 | 12 | True |
| 4 | 19 | True |
| 5 | 4 | True |
| 6 | 9 | True |
| 7 | 11 | True |

## Actual notebook at the wipe

Eight lines; 373 bytes total; longest line 81 bytes.
Old process 140 exited; new process 141 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[3,1,0,2],"phase":0,"delta":-1}
{"people":["I","V","N","S"],"sigma":1}
{"mode":"phase-cycle","offsets":[8,4,5]}
{"sectors":[1,1,0,3,2,3,2,2,0]}
{"roles":["S","I"],"source":"e3194","authority":"V"}
{"credentials":["c9601","c9520","c5391","c6017"]}
{"clock":"e8760","circuit":"e7621","main":"D"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.9775. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 43/96 after it.
Error, if any: None.

Final allied points: 18500; rival points: 3000.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
