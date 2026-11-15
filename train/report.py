"""Pull eval logs from the HF dataset and rebuild every scorecard locally from the raw per-episode rows.
   python -m train.report [--no-pull]   -> artifacts/eval/RESULTS.md + artifacts/eval/results.json"""
import argparse, json, os, re
from collections import Counter
from pathlib import Path
from .metrics import scorecard

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/eval"
REPO = "FatUnc6969/lexi-borderland-data"
MODES = ("room4_all", "rooms", "full", "room4_blank", "room4_swap", "steps", "chain4")


def pull():
    from huggingface_hub import HfApi, hf_hub_download
    for f in HfApi().list_repo_files(REPO, repo_type="dataset"):
        if f.startswith(("runs/eval_", "runs/int_", "runs/baselen", "runs/modal_eval")):
            hf_hub_download(REPO, f, repo_type="dataset", force_download=True, local_dir=OUT / "kaggle")


def load(label_dirs):
    rows = {}
    for d in label_dirs:
        for m in MODES:
            f = d / f"{m}.jsonl"
            if f.exists():
                seen = {}
                for l in open(f):
                    r = json.loads(l); seen[r["key"]] = r   # resume-safe: last row per key
                rows[m] = list(seen.values())   # a later directory supersedes an earlier one for the same mode
    return rows


FENCE = re.compile(r"^\s*```(?:json)?\s*\{", re.S)


def invalid_kinds(rows):
    c = Counter()
    for r in rows:
        for x in r.get("log", []):
            if "invalid" in x:
                raw = x["raw"]
                c["markdown_fenced_json" if FENCE.match(raw) else "other"] += 1
    return dict(c)


def main():
    a = argparse.ArgumentParser(); a.add_argument("--no-pull", action="store_true"); a = a.parse_args()
    if not a.no_pull:
        pull()
    arms = {"random": [OUT / "ref-random", OUT / "ref-steps/random"], "teacher (oracle)": [OUT / "ref-teacher", OUT / "ref-steps/teacher"],
            "Tiny Aya base (strict JSON)": [OUT / "kaggle/runs/eval_base/eval/base"],
            "Tiny Aya base (lenient JSON, fences stripped)": [OUT / "kaggle/runs/int_sft2_baselen_rooms/eval/base_lenient",
                                                              OUT / "kaggle/runs/baselen_rest/eval/base_lenient"],
            "Tiny Aya + SFT v1": [OUT / "kaggle/runs/eval_sft/eval/sft"],
            "Tiny Aya + SFT v2": [OUT / "kaggle/runs/eval_sft2/eval/sft2", OUT / "kaggle/runs/int_sft2_baselen_rooms/eval/sft2",
                                  OUT / "kaggle/runs/modal_eval/sft2"],
            "Tiny Aya + SFT v2 + GRPO": [OUT / "kaggle/runs/modal_eval/grpo"],
            "Tiny Aya + SFT v2 + GRPO random-reward control": [OUT / "kaggle/runs/modal_eval/control"],
            "Tiny Aya + SFT v3": [OUT / "kaggle/runs/modal_eval/sft3"]}
    res = {}
    for arm, dirs in arms.items():
        rows = load(dirs)
        if not rows:
            continue
        card = scorecard(rows)
        card["episodes_by_mode"] = {m: len(v) for m, v in rows.items()}
        card["invalid_kinds"] = invalid_kinds([r for v in rows.values() for r in v])
        res[arm] = card
    (OUT / "results.json").write_text(json.dumps(res, indent=1))
    L = ["# Results (rebuilt from raw per-episode logs by `python -m train.report`)", "",
         "| Arm | Room-4 lock (64 held-out) [95% CI] | Pairwise DSE | Room success (16x7) | Full escape (16) | Mean rooms cleared | Valid-call rate (rooms) | Trap rate (rooms) |",
         "|---|---|---|---|---|---|---|---|"]
    g = lambda d, *k: (lambda v: v)(__import__("functools").reduce(lambda x, y: (x or {}).get(y), k, d))
    for arm, c in res.items():
        r4 = c.get("room4_all", {}); ro = g(c, "rooms", "overall") or {}; fu = c.get("full", {})
        ci = r4.get("lock_ci95")
        L.append(f"| {arm} | {r4.get('lock_success', '-')} {ci if ci else ''} | {r4.get('pairwise_dse', '-')} | "
                 f"{ro.get('success_rate', '-')} | {fu.get('escape_rate', '-')} | {fu.get('mean_rooms_cleared', '-')} | "
                 f"{ro.get('valid_call_rate', '-')} | {ro.get('trap_rate', '-')} |")
    L += ["", "Memoryless reference at room 4: lock <= 0.25, pairwise DSE = 0.", ""]
    for arm, c in res.items():
        if c.get("rooms"):
            L.append(f"**{arm} by room:** " + ", ".join(f"R{k}: {v['success_rate']}" for k, v in c["rooms"]["by_room"].items()))
        if c.get("full"):
            L.append(f"**{arm} full-run lock attribution:** {c['full'].get('lock_attribution')}")
        for m in ("room4_blank", "room4_swap"):
            if c.get(m):
                x = c[m]
                L.append(f"**{arm} {m}:** lock {x['lock_success']}, unlock attempted {x['unlock_attempt_rate']}, "
                         f"matches true pair {x['matches_true_pair']}, follows notebook pair {x.get('follows_notebook_pair', '-')}")
        if c.get("chain4"):
            x = c["chain4"]
            L.append(f"**{arm} own-notebook chain (writes notebook in room 3, wiped, room-4 lock):** lock {x['lock_success']} "
                     f"{x['lock_ci95']}, DSE {x['pairwise_dse']}, wrote notebook {x['wrote_notebook']}, "
                     f"attribution {x['lock_attribution']}")
        if c.get("steps"):
            L.append(f"**{arm} held-out step reward (320 decisions):** {c['steps']['mean_step_reward']} "
                     f"{c['steps']['mean_step_reward_ci95']} kinds {c['steps']['reward_kinds']}")
        if c.get("invalid_kinds"):
            L.append(f"**{arm} invalid outputs by kind:** {c['invalid_kinds']}")
    (OUT / "RESULTS.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
