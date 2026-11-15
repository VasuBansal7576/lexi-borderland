# /// script
# requires-python = ">=3.12"
# dependencies = ["trl==1.7.1", "transformers>=5.15,<6", "peft>=0.13", "datasets", "accelerate", "auditkit",
#                 "huggingface_hub", "torch", "uv", "requests", "rich", "jinja2", "pyyaml", "pydantic"]
# ///
"""Hugging Face Jobs variant of kaggle_job.py (single L4). Launched with `hf jobs uv run`; HF_TOKEN comes from --secrets.
Phases: eval_base | sft (train + eval) | grpo (merge SFT, GRPO, eval) | grpo_control (same with random reward)."""
PHASE = "base_sft"
GRPO_STEPS = 60
import glob, json, os, shutil, subprocess, sys, time
W = "/tmp/out"
BUNDLE = "/tmp/bundle"
DATA_REPO = "FatUnc6969/lexi-borderland-data"
os.makedirs(W, exist_ok=True)
CODE = "/tmp/lexi"
BASE = "CohereLabs/tiny-aya-global"
HF_USER = "FatUnc6969"
SFT_REPO = f"{HF_USER}/tiny-aya-borderland-sft"
GRPO_REPO = f"{HF_USER}/tiny-aya-borderland-grpo"
CONTROL_REPO = f"{HF_USER}/tiny-aya-borderland-grpo-randreward-control"
T0 = time.time()


def sh(cmd, env=None, check=True):
    print(f"[{time.time()-T0:7.0f}s] + {cmd}", flush=True)
    r = subprocess.run(cmd, shell=True, env={**os.environ, **(env or {})})
    if check and r.returncode:
        raise SystemExit(f"FAILED ({r.returncode}): {cmd}")
    return r.returncode


def setup():
    sh(f"{sys.executable} -m uv pip install -q --python {sys.executable} --no-deps "
       "'git+https://github.com/Lexsi-Labs/AgentTune@1dfd054ce59e1c1bdd566cb7e5826f836b1c8c2e'")
    from huggingface_hub import snapshot_download
    import hashlib, base64
    d = snapshot_download(DATA_REPO, repo_type="dataset", allow_patterns=["bundle/*"], token=os.environ["HF_TOKEN"]) + "/bundle"
    os.makedirs(BUNDLE, exist_ok=True); os.makedirs(CODE, exist_ok=True)
    open(f"{BUNDLE}/code.tgz", "wb").write(base64.b64decode(open(f"{d}/code.tgz.b64.txt").read()))
    for name in ("sft-subset", "grpo-states", "sft-v2"):
        with open(f"{BUNDLE}/{name}.jsonl", "w") as out:
            for part in sorted(glob.glob(f"{d}/{name}.part*.txt")):
                out.write(open(part).read())
    want = {l.split()[2]: l.split()[1] for l in open(f"{d}/MANIFEST.sha256.txt") if l.startswith("orig ")}
    for name, h in want.items():
        got = hashlib.sha256(open(f"{BUNDLE}/{name}", "rb").read()).hexdigest()
        assert got == h, f"bundle checksum mismatch {name}"
    print("bundle verified", sorted(want), flush=True)
    sh(f"tar xzf {BUNDLE}/code.tgz -C {CODE}")
    os.environ["PYTHONPATH"] = CODE
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    sh('python -c "import torch,transformers,trl,peft,agenttune;print(torch.__version__,torch.cuda.device_count(),transformers.__version__,trl.__version__,peft.__version__)"')


VLLM_PY = None


def vllm_env():
    """Separate venv so vLLM's pins never touch the training stack. Returns python path or None."""
    global VLLM_PY
    if VLLM_PY is None:
        ok = sh("pip -q install uv 2>&1 | tail -1 && uv venv -q -p 3.12 /kaggle/vllm-env && "
                "VIRTUAL_ENV=/kaggle/vllm-env uv pip install -q vllm 2>&1 | tail -3 && "
                "/kaggle/vllm-env/bin/python -c 'import vllm,torch;print(\"vllm\",vllm.__version__,torch.__version__)'", check=False)
        VLLM_PY = "/kaggle/vllm-env/bin/python" if ok == 0 else ""
    return VLLM_PY


def evaluate(label, model, adapter=None):
    """rooms then full episodes on the single GPU. vLLM first (without the training allocator setting, which breaks
    vLLM's memory profiling), HF generate as fallback. Never aborts the job."""
    out = f"{W}/eval"
    ad = f" --adapter {adapter}" if adapter else ""
    env = {k: v for k, v in os.environ.items() if k != "PYTORCH_CUDA_ALLOC_CONF"}
    py = vllm_env()
    for mode in ("rooms", "full"):
        rc = 1
        if py:
            rc = subprocess.run(f"cd {CODE} && {py} -m train.eval_model --model {model}{ad} --backend vllm --outdir {out} "
                                f"--max-tokens 640 --modes {mode} --label {label}-{mode} > {W}/{label}-{mode}.log 2>&1",
                                shell=True, env=env).returncode
        if rc:
            print(f"vLLM eval {label}-{mode} failed (rc={rc}); falling back to HF generate", flush=True)
            rc = subprocess.run(f"cd {CODE} && {sys.executable} -m train.eval_model --model {model}{ad} --backend hf "
                                f"--outdir {out} --max-tokens 640 --modes {mode} --label {label}-{mode} "
                                f"> {W}/{label}-{mode}-hf.log 2>&1", shell=True, env=env).returncode
        print(f"EVAL {label}-{mode} rc={rc}", flush=True)
        sh(f"tail -c 1500 {W}/{label}-{mode}*.log", check=False)
        upload_results(f"{label}-{mode} rc={rc}")


def push(folder, repo):
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ["HF_TOKEN"])
    api.create_repo(repo, exist_ok=True, private=False)
    api.upload_folder(folder_path=folder, repo_id=repo, commit_message=f"{PHASE} from Kaggle")
    print("pushed", repo, flush=True)


def upload_results(tag):
    try:
        from huggingface_hub import HfApi
        HfApi(token=os.environ["HF_TOKEN"]).upload_folder(folder_path=W, repo_id=DATA_REPO, repo_type="dataset",
            path_in_repo=f"runs/{PHASE}", commit_message=f"{PHASE}: {tag}",
            ignore_patterns=["*-adapter/*", "*.safetensors", "*.bin", "*.pt", "checkpoint-*/*"])
        print("results uploaded:", tag, flush=True)
    except Exception as e:
        print("result upload failed:", e, flush=True)


def merged_sft():
    from huggingface_hub import snapshot_download
    ad = snapshot_download(SFT_REPO, token=os.environ["HF_TOKEN"])
    out = "/kaggle/tmp/sft-merged"
    sh(f"cd {CODE} && {sys.executable} -m train.merge --base {BASE} --adapter {ad} --output {out}")
    return out


def main():
    setup()
    sh(f"cd {CODE} && CUDA_VISIBLE_DEVICES=0 {sys.executable} -m train.sft_train --model {BASE} --data {BUNDLE}/sft-subset.jsonl "
       f"--output {W}/sft-adapter --per-bucket 100000 --epochs 1 --lr 1e-4 --batch 1 --accum 16 --max-length 6144 "
       f"> {W}/sft-train.log 2>&1; tail -c 3000 {W}/sft-train.log", check=False)
    if not os.path.exists(f"{W}/sft-adapter/adapter_model.safetensors"):
        raise SystemExit("SFT produced no adapter")
    push(f"{W}/sft-adapter", SFT_REPO)
    upload_results("sft trained")
    evaluate("sft", BASE, f"{W}/sft-adapter")
    evaluate("base", BASE)
    print(f"PHASE {PHASE} DONE in {time.time()-T0:.0f}s", flush=True)


SFT_V2_REPO = f"{HF_USER}/tiny-aya-borderland-sft-v2"


def main_sft_v2():
    """Continue SFT v1 on derivation-bearing data (sft-v2.jsonl, 1 epoch), push, then a 16-episode room-4 gate."""
    setup()
    from huggingface_hub import snapshot_download
    v1 = snapshot_download(SFT_REPO, token=os.environ["HF_TOKEN"])
    sh(f"cd {CODE} && CUDA_VISIBLE_DEVICES=0 {sys.executable} -m train.sft_train --model {BASE} --data {BUNDLE}/sft-v2.jsonl "
       f"--output {W}/sft-adapter --init-adapter {v1} --per-bucket 100000 --epochs 1 --lr 1e-4 --batch 1 --accum 16 "
       f"--max-length 6144 > {W}/sft-train.log 2>&1; tail -c 3000 {W}/sft-train.log", check=False)
    if not os.path.exists(f"{W}/sft-adapter/adapter_model.safetensors"):
        raise SystemExit("SFT v2 produced no adapter")
    shutil.copy(f"{W}/sft-adapter/train_log.json", f"{W}/train_log.json")
    push(f"{W}/sft-adapter", SFT_V2_REPO)
    upload_results("sft v2 trained")
    env = {k: v for k, v in os.environ.items() if k != "PYTORCH_CUDA_ALLOC_CONF"}
    rc = subprocess.run(f"cd {CODE} && {sys.executable} -m train.eval_model --policy hf --model {BASE} --adapter {W}/sft-adapter "
                        f"--outdir {W}/gate --label sft-v2 --modes room4_all --limit 16 --max-tokens 400 > {W}/gate.log 2>&1",
                        shell=True, env=env).returncode
    sh(f"tail -c 2500 {W}/gate.log", check=False)
    print(f"GATE rc={rc}; PHASE {PHASE} DONE in {time.time()-T0:.0f}s", flush=True)


try:
    main_sft_v2() if PHASE == "sft_v2" else main()
    upload_results("done")
except BaseException as e:
    open(f"{W}/FAILED.txt", "w").write(repr(e))
    upload_results("failed")
    raise
