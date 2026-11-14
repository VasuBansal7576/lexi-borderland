# Tiny Aya baseline: fails before useful seven-room play

Actual local inference completed with **Cohere Tiny Aya Global, official Q4_K_M GGUF**. No project SFT or RL was performed. The model file's SHA-256 matches the official release. All downloads, prompts, caches configured by the runner and artifacts are inside this project; existing installed Python and llama.cpp executables provide the runtime.

**Unassisted result: 0/4 full escapes, zero rooms cleared.** All four paired development worlds ended in room 1 after exhausting the 64-call pre-wipe budget. Each run made 65 model requests: the last request triggered the budget stop without executing its proposed action. They are four members of one counterfactual family, not four independent world families or a general model-success estimate.

The first action was an invalid `exit_room` call. It then repeatedly wrote `A`, `B`, `C`, `D`, `E`, `F`, `G`, `H` into the notebook. It never read a record or chose a door. This is an acquisition/control failure, not evidence that the seven-room reasoning task is unsolvable.

## Where each room broke

Because the unassisted model never reached room 2, rooms 2–7 were tested separately from **legal reference prefixes**, with only the public history since the last wipe and the reference notebook. These are assisted diagnostics, not an uninterrupted model journey. No model action was replaced with a solver action after handoff.

| Room | Scope | Actual behavior | Stop / interpretation |
| --- | --- | --- | --- |
| 1 · Dead or Alive | Four unassisted episodes | Repeated meaningless notebook writes; no evidence reads or door commitments | Tool budget; evidence never acquired |
| 2 · Switchboard | Reference prefix through room 1; 5 model calls | Invalid probe/switch/bus arguments, including literal `auxiliary\|main`; then energized `main` without solving the circuit or reading its schematic | **Fatal bus overload**; four protocol errors before fatal commitment |
| 3 · Tribunal | Reference prefix through room 2; 21 model calls | Cycled through the same four records; never questioned witnesses or committed a registry/roster answer | Context overflow at 8,285 requested tokens vs 8,192 capacity; partial evidence acquisition and repeated reading, not a terminal game loss |
| 4 · Distance | Reference notebook after the seal; 75 model calls | Alternated `move(destination_id="exit")` while locked and `inspect(junction_id="exit")`, which has the wrong argument name; never called `unlock` | Context overflow at 8,225 tokens; facts were available, but tool use/action selection failed |
| 5 · Balance | Legal reference prefix through Distance; 8 model calls | Repeated `submit_bid({"bid":15})` instead of the required `{"value":15}` | Diagnostic stall after eight identical rejected transitions; no bid round actually played |
| 6 · Witch Hunt | Legal reference prefix through Balance; 9 model calls | Tried `accuse({"person_id":"ash"})` without evidence IDs, then repeated `exit_room` | Diagnostic stall; no valid accusation or revocation |
| 7 · Osmosis | Legal reference prefix through Witch Hunt; 4 model calls | First emitted a large modified observation inside `args` with no `tool`; then repeated `exit_room` | Context overflow at 8,213 tokens; no allocation, team step or arena round executed |

The two diagnostic stalls are evaluator stops in recoverable game states. They are not reported as fatal game defeats. The eight-identical-transition guard was introduced before the room diagnostics, after the unassisted runs demonstrated repeated loops. Alternating loops did not trigger that guard and ran until context exhaustion. No game rule, reward, evidence requirement or notebook size was relaxed.

## Actual wipe and model-written memory test

A separate probe replayed legal evidence through room 3's objectives, **stopping before the reference notebook write**. Tiny Aya then chose `exit_room` immediately. It did not write any notebook content: all eight lines were empty.

The inference server was terminated (PID 91839) and restarted (PID 91861). The first post-wipe request contained exactly two chat messages: the fixed public rules and the fresh room-4 public frame. It contained no earlier transcript or result, and its inference response reported **zero cached prompt tokens**. The notebook was eight empty strings, zero bytes.

Tiny Aya repeatedly attempted malformed `exit_room` calls in room 4, including a claimed `junction_id` argument. After 63 total model calls in this probe, it exceeded the native context limit. The stored report's room-3 completion flag means that the model exited a room whose objectives the reference prefix had already completed; it is **not** an independent model solution to Tribunal.

Operational attribution: the required evidence had been delivered, but was not retained in the notebook. Post-wipe tool-protocol failures are also present. Since the correct-reference-notebook Distance probe also failed, these results do not isolate memory omission as the sole cause of failure.

## Prompt controls and what to do before RL

Two additional single-turn framing controls were run after the baseline; they are not included in its success rate:

- Full public manual plus an explicit current-room instruction: chose door `A` immediately without evidence; the unchanged environment returned a fatal commitment (safe door was `D`).
- Concise current-room instructions plus the same observation: called `inspect(object_id="door")`; the environment rejected the inaccessible object. No hidden answer or reference action was supplied.

These limited controls did not establish a working interface. They do not exhaust prompt optimization. The model also receives human-readable tool signatures, and several outputs copy those descriptors literally. Before GRPO, validate a proper typed tool interface and clear per-turn instructions, establish a supervised tool-use/evidence-acquisition baseline, and address context growth without weakening the eight-line seal. In particular, the Osmosis checkpoint already used 7,344 prompt tokens before the model's first response, leaving little room for continued play.

Keep this exact baseline intact. Future comparisons should pin the model/quantization, prompt, tool adapter, decoding, context policy and worlds. Greedy failures here do not measure reward variance under a stochastic training sampler. No training benefit, optimal prompt, broad small-model capability ceiling or untouched holdout result is claimed.

## Evidence and verification

- **11 episode/probe runs, 445 actual model responses/actions and 24,371 completion tokens**, plus two separate one-turn prompt controls.
- **35 tests passed.** Original environment tests remain passing; new tests check lossless observation deltas, no action repair, sealed reference handoffs, absence of the reference note in the memory probe, and the diagnostic stall guard.
- All 11 game trajectories replay exactly, including their legal reference prefixes. The independent transport audit checks every reconstructed public state, model response/action correspondence, fixed prompt hash, post-wipe message count, distinct server PIDs and zero cached prompt tokens after restart.
- The original **64/64 reference certificates still pass** their source-hash and transcript audit. The game was not altered to accommodate the model.
- Temperature 0, inference seed 42, JSON-object grammar only, 1,024 output tokens/action, 32,768 generated tokens/run, native 8,192 context; no silent context trimming, answer repair or solver fallback. An API context failure remains a runtime limit rather than a game defeat.

Inspect the [offline action viewer](viewer.html), [machine-readable analysis](analysis.json), [test output](tests.txt), [prompt controls](interface-controls/results.json), [unchanged environment recheck](environment-certificate-recheck.json), [model provenance](../../models/tiny-aya-global/provenance.json), and [declared protocol](../../baseline/PROTOCOL.md).

Representative runs: [unassisted room-1 failure](natural-v1/natural-p0-s0/report.json), [actual wipe](memory-v1/model-notebook-probe/report.json), [Switchboard fatal error](diagnostic-v1/assisted-room-2/report.json), [Osmosis probe](diagnostic-v1/assisted-room-7/report.json). Each run folder also contains exact `requests.jsonl`, raw `responses.jsonl`, readable `actions.jsonl`, `trace.jsonl` and its private evaluator manifest. Manifests were never sent to the model.

Reproduce with `python3 -m baseline.run --suite natural --output artifacts/model-baseline/new-natural`, followed by separately named `--suite memory` and `--suite diagnostic` outputs. Do not reuse an existing run directory. Run `python3 -m baseline.control` for the separate framing controls. The analysis/viewer scripts summarize the saved `*-v1` corpus.

Primary model/runtime sources: [official GGUF release](https://huggingface.co/CohereLabs/tiny-aya-global-GGUF), [Tiny Aya model card and native context](https://huggingface.co/CohereLabs/tiny-aya-global), [llama.cpp server documentation](https://github.com/ggml-org/llama.cpp/tree/master/tools/server).
