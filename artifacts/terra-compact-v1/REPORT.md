# Terra on the compact interface (the exact prompts Tiny Aya sees)

**What this is.** GPT-6.1 Terra was run through the user's Codex subscription (native codex 0.169.0, Linux, bwrap) on the
compact interface (`baseline/interface_compact.py`), which is the 8K-token view used for Tiny Aya training and eval.
The world is held-out `artifacts/certification-v2/family-0000`. It ran single-room checkpoint episodes for rooms 1–7
(world phase-0-sigma-0) and room 4 on the other three lock twins. Invalid actions get an error frame rather than ending
the episode. Total cost was 96 model calls (ledger: `ledger.json`, raw calls: `calls/`, actions/results: `state.json`).

**Purpose.** This checks that the compact prompts Tiny Aya is trained and scored on can be solved, and that a
failure comes from a reasoning mistake rather than missing information.

## Results

| Episode | Outcome | Steps | Invalid | Trap |
|---|---|---|---|---|
| Room 1 Dead or Alive | success | 10 | 0 | no |
| Room 2 Switchboard | success | 9 | 0 | no |
| Room 3 Tribunal | **fail: invalid_certification** | 7 | 0 | no |
| Room 4 Distance (phase 0, sigma 0) | success | 14 | 0 | no |
| Room 5 Balance | success (2/3 rounds) | 6 | 0 | no |
| Room 6 Witch Hunt | success | 8 | 0 | no |
| Room 7 Osmosis | **legal_escape** (score 0.975) | 16 | 0 | no |
| Room 4 twin phase 0, sigma 1 | **fail: seal_lock** | 3 | 0 | no |
| Room 4 twin phase 1, sigma 0 | success | 21 | 0 | no |
| Room 4 twin phase 1, sigma 1 | **fail: seal_lock** | 2 | 0 | no |

There were zero invalid calls and zero trap-tool uses across all 96 calls. Rooms 1–7 passed 6 of 7 times, and the lock
opened in 2 of the 4 room-4 twins.

## Failure analysis

* **Room 3 is Terra's own error.** It cited the right five evidence sources (the public citation rule works) and named
  the forged credential correctly. It then chose the wrong candidate mapping from the testimony seal arithmetic.
* **Room 4, sigma-1 twins: the notebook label is partly our fault.** The teacher-written notebook stores the registry
  bit as `"sigma":1` on the line `{"people":[...],"sigma":1}`. The public rules only use the name `registry_bit`. In
  both failures Terra read that line as "I with registry value 0" and used the wrong badge. In the sigma-0 twins the
  misreading happened to give the right badge. The information was in the notebook, but under a name the public rules
  never define.
  * **Consequence for the results:** room-4 checkpoint episodes start from this oracle notebook, so the room-4 lock
    numbers measure whether a model can use *this* notebook format. SFT saw that format in training. The base model
    and Terra did not. This is stated in the write-up as a limitation. Fixing it means regenerating the SFT data and
    retraining, which was not possible within the budget.

## Reading

The compact interface is playable by a frontier model with no invalid calls. The one unambiguous reasoning failure
(room 3) and the label confusion (room 4) are both specific and attributable, and neither is a crash or a missing
observation. n is small (one world, one sample per episode), so these are fairness/sanity checks, not benchmark scores.
