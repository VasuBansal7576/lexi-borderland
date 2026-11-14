"""Local launcher: (re)build the private Kaggle datasets and push one phase notebook."""
import argparse, json, os, shutil, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "runtime/secrets"
STAGE = ROOT / "runtime/kaggle"


def sh(c):
    print("+", c, flush=True); subprocess.run(c, shell=True, check=True)


def user():
    return json.loads((SECRETS / "kaggle.json").read_text())["username"]


def dataset(slug, files, title):
    d = STAGE / slug
    d.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy(f, d / Path(f).name)
    meta = {"title": title, "id": f"{user()}/{slug}", "licenses": [{"name": "CC0-1.0"}]}
    (d / "dataset-metadata.json").write_text(json.dumps(meta))
    exists = subprocess.run(f"kaggle datasets status {user()}/{slug}", shell=True, capture_output=True, text=True).returncode == 0
    if exists:
        sh(f"kaggle datasets version -p {d} -m update -q")
    else:
        sh(f"kaggle datasets create -p {d} -q")  # private by default


def kernel(phase, hf_user, grpo_steps):
    d = STAGE / f"k-{phase}"
    d.mkdir(parents=True, exist_ok=True)
    src = (ROOT / "train/kaggle_job.py").read_text().replace("__PHASE__", phase).replace("__HF_USER__", hf_user) \
        .replace("__GRPO_STEPS__", str(grpo_steps)).replace("__HF_TOKEN__", (SECRETS / "hf_token").read_text().strip())
    (d / "job.py").write_text(src)
    slug = f"lexi-borderland-{phase.replace('_', '-')}"
    meta = {"id": f"{user()}/{slug}", "title": slug, "code_file": "job.py", "language": "python", "kernel_type": "script",
            "is_private": True, "enable_gpu": True, "enable_internet": True, "enable_tpu": False,
            "dataset_sources": [], "competition_sources": [],
            "kernel_sources": [], "model_sources": [], "machine_shape": "NvidiaTeslaT4"}
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=1))
    sh(f"kaggle kernels push -p {d}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--datasets", action="store_true")
    p.add_argument("--phase", default=None)
    p.add_argument("--hf-user", required=True)
    p.add_argument("--grpo-steps", type=int, default=60)
    a = p.parse_args()
    os.environ["KAGGLE_CONFIG_DIR"] = str(SECRETS)
    if a.datasets:
        b = ROOT / "runtime/kaggle-bundle"
        dataset("lexi-bundle", [b / "code.tgz", b / "sft-subset.jsonl", b / "grpo-states.jsonl"], "lexi-bundle")
        dataset("lexi-secret", [SECRETS / "hf_token"], "lexi-secret")
    if a.phase:
        kernel(a.phase, a.hf_user, a.grpo_steps)


if __name__ == "__main__":
    main()
