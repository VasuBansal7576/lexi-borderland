# Seven-room solver witness

Success: **True**. Seed 2007; interventions {'phase': 2, 'sigma': 0}.
World fingerprint: `09eed5300cbeff5e8676d6d21ef302cbff685f4b37270f946716e7f4267eb6e5`.

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

Eight lines; 374 bytes total; longest line 81 bytes.
Old process 66 exited; new process 67 started with an empty tool-result envelope and the public room-4 observation.

```text
{"k":[0,3,2,1],"phase":2,"delta":1}
{"people":["N","S","I","V"],"sigma":0}
{"mode":"phase-cycle","offsets":[2,17,12]}
{"sectors":[0,2,3,2,1,3,1,0,0]}
{"roles":["I","N"],"source":"e8881","authority":"N"}
{"credentials":["c3215","c2868","c3279","c1916"]}
{"clock":"e4525","circuit":"e3888","main":"C"}
{"note":"Only observed facts; controller access is separate from arena permits."}
```

## Outcome

Score: 0.978125. Integrity: True. Reason: legal_escape.
Call budget use: 29/64 before the wipe, 41/96 after it.
Error, if any: None.

Final allied points: 21000; rival points: 500.
Allies remaining: 4. Completed arena rounds: 8.
Cache collected: True; positive post-amendment battle round: True.

Inspect [report](report.json), [exact policy inputs](policy-inputs.jsonl), [policy outputs](policy-outputs.jsonl),
[replay trace](trace.jsonl), and [private evaluator manifest](manifest.json). The manifest was never sent to the solver.
