"""Build the generalisation table (base / v5 / A / B [/ A at lower LoRA strength]) from raw per-item logs on HF.
python -m train.xfer_report  -> artifacts/eval/TRANSFER.md, transfer.json"""
import json, os, random, collections
from huggingface_hub import HfApi, hf_hub_download

R = "FatUnc6969/lexi-borderland-data"
ARMS = {"base": ["xfer_base_v5", "wipe_base_v5b"], "v5": ["xfer_base_v5", "wipe_base_v5b"], "genA": ["eval_A1"], "genB": ["eval_B1"],
        "genA-s50": ["scale_A"], "genA-s75": ["scale_A"]}
NAMES = {"base": "Base Tiny Aya", "v5": "v5 (Borderland-only SFT)", "genA": "**A: verified derivations**", "genB": "B: plain traces (control)",
         "genA-s50": "A @ LoRA x0.5", "genA-s75": "A @ LoRA x0.75"}


def boot(v, n=2000, seed=0):
    rng = random.Random(seed); m = len(v)
    xs = sorted(sum(v[rng.randrange(m)] for _ in range(m)) / m for _ in range(n)); return [round(xs[50], 3), round(xs[1949], 3)]


def paired(a, b, n=2000, seed=0):
    ids = sorted(set(a) & set(b)); rng = random.Random(seed); m = len(ids)
    d = [a[i] - b[i] for i in ids]
    xs = sorted(sum(d[rng.randrange(m)] for _ in range(m)) / m for _ in range(n))
    return round(sum(d) / m, 3), [round(xs[50], 3), round(xs[1949], 3)]


def main():
    files = HfApi().list_repo_files(R, repo_type="dataset")
    get = lambda f: [json.loads(l) for l in open(hf_hub_download(R, f, repo_type="dataset", force_download=True))]
    res, per = {}, {}
    for arm, runs in ARMS.items():
        for task in ("bfcl", "gsm8k", "mmlu", "wipe", "wipecode"):
            f = next((f"runs/{r}/transfer/{arm}/{task}.jsonl" for r in runs if f"runs/{r}/transfer/{arm}/{task}.jsonl" in files), None)
            if not f: continue
            rows = get(f)
            if task in ("bfcl",):
                ok = {r["id"]: float(r["lenient"]) for r in rows}
                res[(arm, task)] = {"acc": round(sum(ok.values()) / len(ok), 3), "ci": boot(list(ok.values())), "n": len(ok),
                                    "by_cat": {c: round(sum(float(r["lenient"]) for r in rows if r["cat"] == c) / max(1, sum(r["cat"] == c for r in rows)), 3)
                                               for c in ("simple", "multiple", "parallel", "irrelevance")}}
                per[(arm, task)] = ok
            elif task in ("gsm8k", "mmlu"):
                ok = {r["id"]: float(r["correct"]) for r in rows}
                res[(arm, task)] = {"acc": round(sum(ok.values()) / len(ok), 3), "ci": boot(list(ok.values())), "n": len(ok)}
                per[(arm, task)] = ok
            else:
                for split in ("train", "held"):
                    for cond in ("own", "blank", "swap"):
                        rs = [r for r in rows if r["cond"] == cond and (r.get("heldout_family", False) == (split == "held"))]
                        if not rs: continue
                        k = (arm, f"{task}-{split}-{cond}")
                        res[k] = {"acc": round(sum(r["correct"] for r in rs) / len(rs), 3), "ci": boot([float(r["correct"]) for r in rs]), "n": len(rs)}
                        if cond == "swap": res[k]["follows_twin"] = round(sum(bool(r["follows_twin"]) for r in rs) / len(rs), 3)
                        per[k] = {f'{r["family"]}-{r["seed"]}': float(r["correct"]) for r in rs}
    diffs = {}
    for task in ("bfcl", "gsm8k", "mmlu", "wipe-train-own"):
        for x, y in (("genA", "genB"), ("genA", "base"), ("genB", "base")):
            if (x, task) in per and (y, task) in per:
                diffs[f"{x}-{y}:{task}"] = paired(per[(x, task)], per[(y, task)])
    arms = [a for a in ARMS if any(k[0] == a for k in res)]
    cell = lambda a, t: (f"{res[(a, t)]['acc'] * 100:.1f} [{res[(a, t)]['ci'][0] * 100:.0f}, {res[(a, t)]['ci'][1] * 100:.0f}]" if (a, t) in res else "–")
    lines = ["| Model | BFCL AST (400) | GSM8K (500) | Global-MMLU-Lite 8 lang (200) | Wipe tasks, own notes (96) | blank notes | swapped notes: follows twin | Unseen wipe families (32) | Coding wipe, unseen (48) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for a in arms:
        sw = res.get((a, "wipe-train-swap"), {}).get("follows_twin")
        lines.append(f"| {NAMES[a]} | {cell(a, 'bfcl')} | {cell(a, 'gsm8k')} | {cell(a, 'mmlu')} | {cell(a, 'wipe-train-own')} | {cell(a, 'wipe-train-blank')} | "
                     f"{'–' if sw is None else f'{sw * 100:.0f}%'} | {cell(a, 'wipe-held-own')} | {cell(a, 'wipecode-train-own')} |")
    lines += ["", "BFCL by category (simple / multiple / parallel / irrelevance):"]
    for a in arms:
        if (a, "bfcl") in res:
            c = res[(a, "bfcl")]["by_cat"]; lines.append(f"- {NAMES[a]}: " + " / ".join(f"{c[k] * 100:.0f}%" for k in ("simple", "multiple", "parallel", "irrelevance")))
    lines += ["", "Paired differences (mean, 95% bootstrap CI over the same items):"] + [f"- {k}: {v[0] * 100:+.1f} pts [{v[1][0] * 100:+.1f}, {v[1][1] * 100:+.1f}]" for k, v in diffs.items()]
    os.makedirs("artifacts/eval", exist_ok=True)
    open("artifacts/eval/TRANSFER.md", "w").write("\n".join(lines) + "\n")
    json.dump({"results": {f"{a}|{t}": v for (a, t), v in res.items()}, "paired": diffs}, open("artifacts/eval/transfer.json", "w"), indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
