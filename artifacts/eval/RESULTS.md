# Results (rebuilt from raw per-episode logs by `python -m train.report`)

| Arm | Room-4 lock (64 held-out) [95% CI] | Pairwise DSE | Room success (16x7) | Full escape (16) | Mean rooms cleared | Valid-call rate (rooms) | Trap rate (rooms) |
|---|---|---|---|---|---|---|---|
| random | 0.141 [0.062, 0.219] | 0.01 | 0.0 | 0.0 | 0.0 | 1.0 | 0.348 |
| teacher (oracle) | 1.0 [1.0, 1.0] | 1.0 | 1.0 | 1.0 | 7.0 | 1.0 | 0.0 |
| Tiny Aya base (strict JSON) | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Tiny Aya base (lenient JSON, fences stripped) | 0.125 [0.062, 0.188] | 0.0 | 0.0 | 0.0 | 0.0 | 0.876 | 0.0 |
| Tiny Aya + SFT v1 | 0.344 [0.281, 0.406] | 0.062 | 0.134 | 0.0 | 0.06 | 1.0 | 0.0 |
| Tiny Aya + SFT v2 | 1.0 [1.0, 1.0] | 1.0 | 0.098 | 0.0 | 0.0 | 0.993 | 0.0 |

Memoryless reference at room 4: lock <= 0.25, pairwise DSE = 0.

**random by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.0, R7: 0.0
**random full-run lock attribution:** {'did_not_reach_lock': 16}
**teacher (oracle) by room:** R1: 1.0, R2: 1.0, R3: 1.0, R4: 1.0, R5: 1.0, R6: 1.0, R7: 1.0
**teacher (oracle) full-run lock attribution:** {'lock_correct': 16}
**Tiny Aya base (strict JSON) by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.0, R7: 0.0
**Tiny Aya base (strict JSON) full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya base (strict JSON) invalid outputs by kind:** {'markdown_fenced_json': 576}
**Tiny Aya base (lenient JSON, fences stripped) by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.0, R7: 0.0
**Tiny Aya base (lenient JSON, fences stripped) full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya base (lenient JSON, fences stripped) invalid outputs by kind:** {'other': 188, 'markdown_fenced_json': 37}
**Tiny Aya + SFT v1 by room:** R1: 0.062, R2: 0.062, R3: 0.062, R4: 0.0, R5: 0.125, R6: 0.625, R7: 0.0
**Tiny Aya + SFT v1 full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v2 by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.625, R7: 0.062
**Tiny Aya + SFT v2 full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v2 room4_blank:** lock 0.25, unlock attempted 1.0, matches true pair 0.25, follows notebook pair -
**Tiny Aya + SFT v2 room4_swap:** lock 0.0, unlock attempted 1.0, matches true pair 0.0, follows notebook pair 1.0
**Tiny Aya + SFT v2 invalid outputs by kind:** {'other': 6}
