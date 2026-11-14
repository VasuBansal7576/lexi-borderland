# Terra full-chain playtest (fixed game, error-frame policy)

2026-11-14 ~18:00 IST. gpt-6.1-terra, user's ChatGPT subscription, native Codex CLI (Linux VM bridge), medium effort, 100-call cap, certified world family-0000/phase-0-sigma-0, resumable chunks, invalid_action=error_frame.

Result: 43 actions (43 model calls, 135,267 input + 4,074 output tokens), 0 invalid outputs. Rooms 1-3 cleared, **real memory wipe after room 3** (fresh request history; only the model's own 8 notebook lines carried over), **room 4 (Distance) cleared from the notebook alone**, ended in room 5 (Balance) with `balance_loss`. Score 0.21. Exact replay: True.

Model's own notebook at the wipe:
    Phase=0 from current clock_pairs e0883; signed probe e0247 gives polarity -1.
    Glyphs e8797: A=0 B=3 C=1 D=2. Circuit e2189: second matrix.
    Roster e4188/e1986: ash=I, birch=V, cedar=N, dusk=S.
    Registry e4188: bit=0; forged credential c9410 belongs to V; V's valid credential c7128.
    Roles e7041: authority I; controller operators V,S; arena permits separate.
    Practice e4558: three rivals are mirror family; offsets 16,10,18 respectively.
    District plan e0567 nodes 0:B 1:C 2:D 3:C 4:D 5:A 6:A 7:D 8:B.
    Plan e0567 links 6-8,3-8,6-7,5-8,0-3,5-7,0-5.

Diagnosis (evaluator-side, after the run): the environment's bids and targets match the public rules exactly. Terra's errors: round 1 it computed the mirror rival bid as 6 where (20-10+16) mod 21 = 5; round 3 it switched to a formula not in the rules ((offset-previous-1) mod 21). Its post-wipe read of the room-3 practice record returned `inaccessible`, which is the designed memory boundary (only notebook lines survive).

Gate A verdict: PASS. A frontier model can legally play the public game through the wipe; every failure so far is the model's own.
