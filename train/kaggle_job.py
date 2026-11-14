"""Runs inside a Kaggle GPU notebook (2x T4). PHASE is set by kaggle_launch.py.
Phases: eval_base | sft (train + eval) | grpo (merge SFT, GRPO, eval) | grpo_control (same with random reward)."""
PHASE = "__PHASE__"
GRPO_STEPS = int("__GRPO_STEPS__")
import glob, json, os, shutil, subprocess, sys, time
W = "/kaggle/working"
BUNDLE = "/kaggle/bundle"
DATA_REPO = "__HF_USER__/lexi-borderland-data"
os.environ["HF_TOKEN"] = "__HF_TOKEN__"  # private notebook only; used for the gated model and result uploads
CODE = "/kaggle/lexi"
BASE = "CohereLabs/tiny-aya-global"
HF_USER = "__HF_USER__"
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
    sh('pip -q uninstall -y torchao 2>&1 | tail -1', check=False)  # Kaggle's torchao 0.10 breaks current PEFT imports
    sh('pip -q install "trl==1.7.1" "transformers>=5.15,<6" "peft>=0.13" datasets accelerate auditkit huggingface_hub 2>&1 | tail -3')
    sh('pip -q install --no-deps "git+https://github.com/Lexsi-Labs/AgentTune@1dfd054ce59e1c1bdd566cb7e5826f836b1c8c2e" 2>&1 | tail -3')
    from huggingface_hub import snapshot_download
    import hashlib, base64
    d = snapshot_download(DATA_REPO, repo_type="dataset", allow_patterns=["bundle/*"], token=os.environ["HF_TOKEN"]) + "/bundle"
    os.makedirs(BUNDLE, exist_ok=True); os.makedirs(CODE, exist_ok=True)
    open(f"{BUNDLE}/code.tgz", "wb").write(base64.b64decode(open(f"{d}/code.tgz.b64.txt").read()))
    for name in ("sft-subset", "grpo-states"):
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


def evaluate(label, model, adapter=None):
    """rooms on GPU0 and full episodes on GPU1, in parallel."""
    out = f"{W}/eval"
    common = f"cd {CODE} && python -m train.eval_model --model {model} --backend hf --outdir {out} --max-tokens 640"
    ad = f" --adapter {adapter}" if adapter else ""
    p1 = subprocess.Popen(f"{common}{ad} --modes rooms --label {label}-rooms > {W}/{label}-rooms.log 2>&1", shell=True,
                          env={**os.environ, "CUDA_VISIBLE_DEVICES": "0"})
    p2 = subprocess.Popen(f"{common}{ad} --modes full --label {label}-full > {W}/{label}-full.log 2>&1", shell=True,
                          env={**os.environ, "CUDA_VISIBLE_DEVICES": "1"})
    codes = [p1.wait(), p2.wait()]
    sh(f"tail -c 3000 {W}/{label}-rooms.log; tail -c 2000 {W}/{label}-full.log", check=False)
    if any(codes):
        raise SystemExit(f"eval failed {codes}")


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
    sh(f"cd {CODE} && python -m train.merge --base {BASE} --adapter {ad} --output {out}")
    return out


def main():
    setup()
    if PHASE == "eval_base":
        evaluate("base", BASE)
    elif PHASE == "sft":
        sh(f"cd {CODE} && python -m train.sft_train --model {BASE} --data {BUNDLE}/sft-subset.jsonl --output {W}/sft-adapter "
           f"--per-bucket 100000 --epochs 1 --lr 1e-4 --batch 1 --accum 16 --max-length 6144 > {W}/sft-train.log 2>&1; "
           f"tail -c 4000 {W}/sft-train.log")
        if not os.path.exists(f"{W}/sft-adapter/adapter_model.safetensors"):
            raise SystemExit("SFT produced no adapter")
        push(f"{W}/sft-adapter", SFT_REPO)
        upload_results("sft trained")
        evaluate("sft", BASE, f"{W}/sft-adapter")
    elif PHASE in ("grpo", "grpo_control"):
        m = merged_sft()
        ctl = " --control" if PHASE == "grpo_control" else ""
        out = f"{W}/{PHASE}-adapter"
        sh(f"cd {CODE} && CUDA_VISIBLE_DEVICES=0 python -m train.grpo_train --model {m} --states {BUNDLE}/grpo-states.jsonl "
           f"--output {out} --steps {GRPO_STEPS} --generations 8 --lr 1e-5 --completion-len 512 --max-prompt-tokens 5600{ctl} "
           f"> {W}/{PHASE}-train.log 2>&1; tail -c 4000 {W}/{PHASE}-train.log")
        if not os.path.exists(f"{out}/adapter_model.safetensors"):
            raise SystemExit("GRPO produced no adapter")
        push(out, CONTROL_REPO if ctl else GRPO_REPO)
        upload_results("grpo trained")
        evaluate(PHASE, m, out)
    print(f"PHASE {PHASE} DONE in {time.time()-T0:.0f}s", flush=True)


try:
    main()
    upload_results("done")
except BaseException as e:
    open(f"{W}/FAILED.txt", "w").write(repr(e))
    upload_results("failed")
    raise
