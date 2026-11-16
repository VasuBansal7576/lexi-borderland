| Model | BFCL AST (400) | GSM8K (500) | Global-MMLU-Lite 8 lang (200) | Wipe tasks, own notes (96) | blank notes | swapped notes: follows twin | Unseen wipe families (32) | Coding wipe, unseen (48) |
|---|---|---|---|---|---|---|---|---|
| Base Tiny Aya | 44.5 [39, 49] | 74.8 [71, 78] | 50.5 [44, 57] | 2.1 [0, 5] | 4.2 [1, 8] | 1% | 3.1 [0, 9] | 0.0 [0, 0] |
| v5 (Borderland-only SFT) | 26.5 [22, 31] | 72.4 [68, 76] | 52.5 [45, 60] | – | – | – | – | 0.0 [0, 0] |
| **A: verified derivations** | 54.5 [50, 59] | 57.6 [53, 62] | 54.5 [48, 61] | 62.5 [53, 72] | 3.1 [0, 7] | 53% | 6.2 [0, 16] | 0.0 [0, 0] |
| B: plain traces (control) | 67.0 [62, 72] | 60.0 [56, 64] | 51.0 [44, 57] | 52.1 [43, 62] | 3.1 [0, 7] | 46% | 0.0 [0, 0] | 2.1 [0, 6] |
| A @ LoRA x0.5 | 52.5 [48, 57] | 60.6 [56, 65] | 55.5 [48, 62] | – | – | – | – | – |
| A @ LoRA x0.75 | 51.5 [47, 56] | 59.0 [54, 63] | 54.0 [47, 60] | – | – | – | – | – |

BFCL by category (simple / multiple / parallel / irrelevance):
- Base Tiny Aya: 33% / 31% / 34% / 80%
- v5 (Borderland-only SFT): 4% / 11% / 4% / 87%
- **A: verified derivations**: 79% / 68% / 42% / 21%
- B: plain traces (control): 86% / 77% / 59% / 41%
- A @ LoRA x0.5: 80% / 78% / 22% / 18%
- A @ LoRA x0.75: 85% / 79% / 14% / 14%

Paired differences (mean, 95% bootstrap CI over the same items):
- genA-genB:bfcl: -12.5 pts [-16.8, -8.0]
- genA-base:bfcl: +10.0 pts [+2.8, +17.2]
- genB-base:bfcl: +22.5 pts [+16.0, +29.0]
- genA-genB:gsm8k: -2.4 pts [-5.6, +0.8]
- genA-base:gsm8k: -17.2 pts [-22.0, -12.2]
- genB-base:gsm8k: -14.8 pts [-19.6, -10.0]
- genA-genB:mmlu: +3.5 pts [-1.0, +8.0]
- genA-base:mmlu: +4.0 pts [+0.0, +8.0]
- genB-base:mmlu: +0.5 pts [-4.0, +5.0]
- genA-genB:wipe-train-own: +10.4 pts [+3.1, +18.8]
- genA-base:wipe-train-own: +60.4 pts [+51.0, +69.8]
- genB-base:wipe-train-own: +50.0 pts [+39.6, +60.4]
