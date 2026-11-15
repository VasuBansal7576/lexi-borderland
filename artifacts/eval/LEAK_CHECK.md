# Train/eval leak check (run 2026-11-15)
Eval worlds: artifacts/certification-v2 (64 = 16 families x 4 lock twins). Train worlds: artifacts/train-worlds-a + -b (256).
- seed overlap: 0
- full-manifest hash overlap: 0
- world fingerprint overlap: 0
- latent-structure overlap (k, mapping, mode, offsets, edges, sectors): 0
- family-id overlap: none
- SFT rows (runtime/kaggle-bundle/sft-subset.jsonl) come only from train-worlds-a/b; GRPO states only from train-worlds-b.
