# Results (rebuilt from raw per-episode logs by `python -m train.report`)

| Arm | Room-4 lock (64 held-out) [95% CI] | Pairwise DSE | Room success (16x7) | Full escape (16) | Mean rooms cleared | Valid-call rate (rooms) | Trap rate (rooms) |
|---|---|---|---|---|---|---|---|
| random | 0.141 [0.062, 0.219] | 0.01 | 0.0 | 0.0 | 0.0 | 1.0 | 0.348 |
| teacher (oracle) | 1.0 [1.0, 1.0] | 1.0 | 1.0 | 1.0 | 7.0 | 1.0 | 0.0 |
| Tiny Aya base (strict JSON) | 0.0 [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Tiny Aya base (lenient JSON, fences stripped) | 0.125 [0.062, 0.188] | 0.0 | 0.0 | 0.0 | 0.0 | 0.876 | 0.0 |
| Tiny Aya + SFT v1 | 0.344 [0.281, 0.406] | 0.062 | 0.134 | 0.0 | 0.06 | 1.0 | 0.0 |
| Tiny Aya + SFT v2 | 1.0 [1.0, 1.0] | 1.0 | 0.098 | 0.0 | 0.0 | 0.993 | 0.0 |
| Tiny Aya + SFT v2 + GRPO | 1.0 [1.0, 1.0] | 1.0 | 0.089 | 0.0 | 0.0 | 0.998 | 0.0 |
| Tiny Aya + SFT v2 + GRPO random-reward control | -  | - | 0.107 | 0.0 | 0.0 | 0.996 | 0.0 |
| Tiny Aya + SFT v3 | 1.0 [1.0, 1.0] | 1.0 | 0.089 | 0.0 | 0.0 | 1.0 | 0.0 |

Memoryless reference at room 4: lock <= 0.25, pairwise DSE = 0.

**random by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.0, R7: 0.0
**random full-run lock attribution:** {'did_not_reach_lock': 16}
**random held-out step reward (320 decisions):** -0.297 [-0.342, -0.243] kinds {'protocol_error': 123, 'wasted': 105, 'fatal': 33, 'milestone': 9, 'progress': 19, 'trap': 31}
**teacher (oracle) by room:** R1: 1.0, R2: 1.0, R3: 1.0, R4: 1.0, R5: 1.0, R6: 1.0, R7: 1.0
**teacher (oracle) full-run lock attribution:** {'lock_correct': 16}
**teacher (oracle) held-out step reward (320 decisions):** 0.488 [0.446, 0.53] kinds {'progress': 222, 'milestone': 91, 'wasted': 7}
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
**Tiny Aya + SFT v2 own-notebook chain (writes notebook in room 3, wiped, room-4 lock):** lock 0.5 [0.5, 0.5], DSE 0.167, wrote notebook 1.0, attribution {'lock_correct': 32, 'not_retained': 32}
**Tiny Aya + SFT v2 held-out step reward (320 decisions):** 0.187 [0.087, 0.277] kinds {'progress': 126, 'milestone': 82, 'protocol_error': 57, 'fatal': 47, 'wasted': 8}
**Tiny Aya + SFT v2 invalid outputs by kind:** {'other': 6}
**Tiny Aya + SFT v2 + GRPO by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.062, R5: 0.0, R6: 0.562, R7: 0.0
**Tiny Aya + SFT v2 + GRPO full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v2 + GRPO held-out step reward (320 decisions):** 0.2 [0.112, 0.285] kinds {'progress': 132, 'milestone': 81, 'protocol_error': 57, 'fatal': 44, 'wasted': 6}
**Tiny Aya + SFT v2 + GRPO invalid outputs by kind:** {'other': 2}
**Tiny Aya + SFT v2 + GRPO random-reward control by room:** R1: 0.0, R2: 0.0, R3: 0.0, R4: 0.0, R5: 0.0, R6: 0.625, R7: 0.125
**Tiny Aya + SFT v2 + GRPO random-reward control full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v2 + GRPO random-reward control held-out step reward (320 decisions):** 0.202 [0.105, 0.293] kinds {'progress': 128, 'milestone': 86, 'protocol_error': 49, 'fatal': 47, 'wasted': 9, 'invalid': 1}
**Tiny Aya + SFT v2 + GRPO random-reward control invalid outputs by kind:** {'other': 5}
**Tiny Aya + SFT v3 by room:** R1: 0.0, R2: 0.0, R3: 0.062, R4: 0.0, R5: 0.0, R6: 0.562, R7: 0.0
**Tiny Aya + SFT v3 full-run lock attribution:** {'did_not_reach_lock': 16}
**Tiny Aya + SFT v3 own-notebook chain (writes notebook in room 3, wiped, room-4 lock):** lock 1.0 [1.0, 1.0], DSE 1.0, wrote notebook 1.0, attribution {'lock_correct': 64}
**Tiny Aya + SFT v3 held-out step reward (320 decisions):** 0.267 [0.221, 0.319] kinds {'progress': 163, 'protocol_error': 65, 'milestone': 68, 'fatal': 17, 'wasted': 7}
