"""AgentTune GRPO (+ matched random-reward control) on Modal, starting from the merged SFT v2 policy.

Run from the Lexi folder on your Mac (needs `pip install modal` and `modal token new` once):
    modal run train/modal_grpo.py --arm smoke            # 2 GRPO steps: memory, sec/step, $ estimate
    modal run --detach train/modal_grpo.py --arm grpo --steps 200
    modal run --detach train/modal_grpo.py --arm control --steps 200
Everything (code, data, adapters) moves through the HF dataset/model repos, so results are visible without Modal access.
Checkpoints and the merged SFT v2 model live on the Modal Volume `lexi-grpo`.

Hands-off mode (one command, then Claude drives it through the HF dataset):
    modal deploy train/modal_grpo.py
A CPU cron (`ops_tick`, every 2 min) reads ops/queue.jsonl from the HF dataset, spawns only whitelisted functions
(train / evaluate) with type-checked arguments, enforces a hard spend cap, supports cancel, and writes ops/status.json."""
import os
import modal

AGENTTUNE = "git+https://github.com/Lexsi-Labs/AgentTune@1dfd054ce59e1c1bdd566cb7e5826f836b1c8c2e"
image = (modal.Image.debian_slim(python_version="3.12").apt_install("git")
         .pip_install("torch", "transformers>=5.15,<6", "trl==1.7.1", "peft>=0.13", "datasets", "accelerate",
                      "huggingface_hub", "rich", "jinja2", "pyyaml", "pydantic", "requests")
         .run_commands(f"pip install --no-deps '{AGENTTUNE}'"))
app = modal.App("lexi-borderland", image=image)
OPS = modal.Dict.from_name("lexi-ops", create_if_missing=True)
vol = modal.Volume.from_name("lexi-grpo", create_if_missing=True)
HF_SECRET = modal.Secret.from_dict({"HF_TOKEN": open("runtime/secrets/hf_token").read().strip()}) if modal.is_local() \
    else modal.Secret.from_dict({})

BASE = "CohereLabs/tiny-aya-global"
DATA_REPO = "FatUnc6969/lexi-borderland-data"
SFT2 = "FatUnc6969/tiny-aya-borderland-sft-v2"
MERGED_REPO = "FatUnc6969/tiny-aya-borderland-sft-v2-merged"
OUT_REPO = {"grpo": "FatUnc6969/tiny-aya-borderland-grpo", "control": "FatUnc6969/tiny-aya-borderland-grpo-randreward-control",
            "smoke": None}
GPU_PER_HOUR = 2.50  # A100 80GB list price, GPU only (CPU/RAM extra)


def sh(cmd):
    import subprocess, time
    t = time.time(); print("+", cmd, flush=True)
    r = subprocess.run(["bash", "-o", "pipefail", "-c", cmd])
    print(f"  rc={r.returncode} in {time.time()-t:.0f}s", flush=True)
    if r.returncode:
        raise SystemExit(f"FAILED: {cmd}")


def setup(expected_sha):
    import base64, glob, hashlib
    from huggingface_hub import snapshot_download
    d = snapshot_download(DATA_REPO, repo_type="dataset", allow_patterns=["bundle/*"]) + "/bundle"
    raw = base64.b64decode(open(f"{d}/code.tgz.b64.txt").read())
    sha = hashlib.sha256(raw).hexdigest()
    if sha != expected_sha:
        raise SystemExit(f"STALE CODE {sha[:12]} != {expected_sha[:12]}")
    os.makedirs("/code", exist_ok=True); os.makedirs("/data", exist_ok=True)
    open("/data/code.tgz", "wb").write(raw)
    want = {l.split()[2]: l.split()[1] for l in open(f"{d}/MANIFEST.sha256.txt") if l.startswith("orig ")}
    for name, h in want.items():
        if name == "code.tgz":
            continue
        stem = name.rsplit(".", 1)[0]
        with open(f"/data/{name}", "w") as out:
            for part in sorted(glob.glob(f"{d}/{stem}.part*.txt")):
                out.write(open(part).read())
        assert hashlib.sha256(open(f"/data/{name}", "rb").read()).hexdigest() == h, f"checksum mismatch {name}"
    sh("tar xzf /data/code.tgz -C /code")
    os.environ["PYTHONPATH"] = "/code"
    print("code + data verified", sha[:12], flush=True)


@app.function(gpu="A100-80GB", volumes={"/vol": vol}, secrets=[HF_SECRET], timeout=6 * 3600)
def train(arm: str, steps: int, expected_sha: str, generations: int = 8, lr: float = 1e-5):
    import json, sys, time, torch
    from huggingface_hub import HfApi, snapshot_download
    t0 = time.time()
    setup(expected_sha)
    merged = "/vol/sft2-merged"
    if not os.path.exists(f"{merged}/config.json"):
        sh(f"cd /code && {sys.executable} -m train.merge --base {BASE} --adapter {snapshot_download(SFT2)} --output {merged}")
        vol.commit()
        api = HfApi(); api.create_repo(MERGED_REPO, exist_ok=True, private=False)
        api.upload_folder(folder_path=merged, repo_id=MERGED_REPO, commit_message="SFT v2 merged into Tiny Aya Global (fp16)")
    out = f"/vol/{arm}-{steps}"
    flag = " --control" if arm == "control" else ""
    t1 = time.time()
    sh(f"cd /code && {sys.executable} -m train.grpo_train --model {merged} --states /data/grpo-states-v2.jsonl "
       f"--output {out} --steps {steps} --generations {generations} --batch 4 --lr {lr} --completion-len 320 "
       f"--temperature 1.0 --max-prompt-tokens 6000 --save-steps 50{flag} 2>&1 | tee /vol/{arm}-{steps}.log")
    train_s = time.time() - t1
    vol.commit()
    log = json.load(open(f"{out}/train_log.json"))
    hist = log["log_history"]
    rewards = [h["reward"] for h in hist if "reward" in h]
    summary = {"arm": arm, "steps": steps, "generations": generations, "lr": lr, "gpu": torch.cuda.get_device_name(0),
               "train_seconds": round(train_s), "sec_per_step": round(train_s / steps, 1),
               "total_seconds": round(time.time() - t0),
               "gpu_cost_estimate_usd": round((time.time() - t0) / 3600 * GPU_PER_HOUR, 2),
               "projected_gpu_usd_per_100_steps": round(train_s / steps * 100 / 3600 * GPU_PER_HOUR, 2),
               "reward_first10_mean": round(sum(rewards[:10]) / max(1, len(rewards[:10])), 3) if rewards else None,
               "reward_last10_mean": round(sum(rewards[-10:]) / max(1, len(rewards[-10:])), 3) if rewards else None,
               "code_sha": expected_sha[:12]}
    json.dump(summary, open(f"{out}/modal_summary.json", "w"), indent=1)
    api = HfApi()
    api.upload_folder(folder_path=out, repo_id=DATA_REPO, repo_type="dataset", path_in_repo=f"runs/modal_{arm}_{steps}",
                      allow_patterns=["*.json"], commit_message=f"modal {arm} {steps} steps")
    api.upload_file(path_or_fileobj=f"/vol/{arm}-{steps}.log", path_in_repo=f"runs/modal_{arm}_{steps}/train.log",
                    repo_id=DATA_REPO, repo_type="dataset")
    if OUT_REPO.get(arm):
        clean_readme(out, MERGED_REPO, f"GRPO ({arm}) LoRA on top of {MERGED_REPO}.")
        api.create_repo(OUT_REPO[arm], exist_ok=True, private=False)
        api.upload_folder(folder_path=out, repo_id=OUT_REPO[arm], commit_message=f"GRPO {arm} {steps} steps from SFT v2",
                          ignore_patterns=["checkpoint-*/*"])
        api.upload_folder(folder_path=out, repo_id=DATA_REPO, repo_type="dataset", path_in_repo=f"runs/modal_{arm}_{steps}",
                          allow_patterns=["checkpoint-*/trainer_state.json"], commit_message=f"modal {arm} checkpoints state")
    print(json.dumps(summary, indent=1), flush=True)
    return summary



def clean_readme(folder, base, note):
    import glob as g
    for f in g.glob(f"{folder}/README.md"):
        os.remove(f)
    open(f"{folder}/README.md", "w").write(f"---\nbase_model: {base}\nlibrary_name: peft\ntags: [borderland, lexsi-hackathon, agenttune]\n---\n\n"
                                         f"# {os.path.basename(folder)}\n\n{note}\n\nSee https://github.com/VasuBansal7576/lexi-borderland\n")


@app.function(volumes={"/vol": vol}, secrets=[HF_SECRET], timeout=1800)
def publish(src: str, repo: str, base: str, note: str):
    from huggingface_hub import HfApi
    vol.reload()
    clean_readme(src, base, note)
    api = HfApi(); api.create_repo(repo, exist_ok=True, private=False)
    api.upload_folder(folder_path=src, repo_id=repo, ignore_patterns=["checkpoint-*/*"], commit_message=f"publish {src}")
    return {"published": repo}


@app.function(gpu="A100-80GB", volumes={"/vol": vol}, secrets=[HF_SECRET], timeout=3 * 3600)
def sft(name: str, data: str, init_repo: str, expected_sha: str, epochs: float = 1.0, lr: float = 1e-4, max_steps: int = -1):
    """AgentTune distillation (train.sft_train) continuing an existing LoRA; pushes FatUnc6969/tiny-aya-borderland-<name>."""
    import json, sys, time
    from huggingface_hub import HfApi, snapshot_download
    t0 = time.time(); setup(expected_sha)
    init = snapshot_download(init_repo) if init_repo else ""
    out = f"/vol/{name}"
    import threading
    stop = threading.Event()
    def committer():                      # persist intermediate checkpoints even if the container dies
        while not stop.wait(600):
            try: vol.commit()
            except Exception as e: print("commit failed", e, flush=True)
    threading.Thread(target=committer, daemon=True).start()
    sh(f"cd /code && {sys.executable} -m train.sft_train --model {BASE} --data /data/{data} --output {out}"
       f"{' --init-adapter ' + init if init else ''} "
       f"--per-bucket 100000 --epochs {epochs} --lr {lr} --batch 1 --accum 16 --max-length 6144 --max-steps {max_steps} "
       f"--save-steps 100 2>&1 | tee /vol/{name}.log")
    stop.set(); vol.commit()
    repo = f"FatUnc6969/tiny-aya-borderland-{name}"
    clean_readme(out, BASE, f"LoRA for Tiny Aya Global, {'continued from ' + init_repo if init_repo else 'trained from the base model'} on {data} (Borderland generalisation mixture, AgentTune distillation).")
    api = HfApi(); api.create_repo(repo, exist_ok=True, private=False)
    api.upload_folder(folder_path=out, repo_id=repo, commit_message=f"{name} from {init_repo}")
    api.upload_file(path_or_fileobj=f"/vol/{name}.log", path_in_repo=f"runs/modal_{name}/train.log", repo_id=DATA_REPO, repo_type="dataset")
    api.upload_file(path_or_fileobj=f"{out}/train_log.json", path_in_repo=f"runs/modal_{name}/train_log.json", repo_id=DATA_REPO, repo_type="dataset")
    return {"name": name, "seconds": round(time.time() - t0)}


@app.function(gpu="A100-80GB", volumes={"/vol": vol}, secrets=[HF_SECRET], timeout=4 * 3600)
def evaluate(label: str, modes: str, expected_sha: str, model: str = "/vol/sft2-merged", adapter: str = "",
             lenient: bool = False, token_budget: int = 120000):
    """Held-out eval on Modal (same eval_model.py as Kaggle). Partial results uploaded every 10 min."""
    import sys, threading, time
    from huggingface_hub import HfApi, snapshot_download
    setup(expected_sha)
    vol.reload()
    if model.startswith("hf:"):
        model = snapshot_download(model[3:])
    if adapter.startswith("hf:"):
        adapter = snapshot_download(adapter[3:])
    out = f"/data/eval"
    api, stop = HfApi(), threading.Event()
    def push(tag):
        try:
            api.upload_folder(folder_path=out, repo_id=DATA_REPO, repo_type="dataset", path_in_repo="runs/modal_eval",
                              allow_patterns=["*.jsonl", "*.json", "*.log"], commit_message=f"modal eval {label} {modes}: {tag}")
        except Exception as e:
            print("upload failed", e, flush=True)
    os.makedirs(f"{out}/{label}", exist_ok=True)
    def pump():
        while not stop.wait(600):
            push("progress")
    threading.Thread(target=pump, daemon=True).start()
    ad = f" --adapter {adapter}" if adapter else ""
    sh(f"cd /code && {sys.executable} -m train.eval_model --policy hf --model {model}{ad} --outdir {out} --label {label} "
       f"--modes {modes} --max-tokens 400 --token-budget {token_budget} --bundle-sha {expected_sha[:12]}"
       f"{' --lenient-json' if lenient else ''} 2>&1 | tee {out}/{label}/{modes.replace(',', '+')}.log")
    stop.set(); push("done")
    return {"label": label, "modes": modes}


COST_PER_HOUR = 3.2      # A100 80GB + CPU/RAM, conservative
CAP_USD = 33.0           # ledger counts $3.2/h vs ~$2.75/h real (A100 + CPU/RAM): 33 ledger ~= $28.4 real of the $30 credit
PRIOR_USD = 8.0          # smoke + the hand-launched GRPO run
LEDGER_V2_USD = 16.0     # v2 accounting (2026-11-15 16:45 IST): everything finished so far, measured, rounded up
FUNCS = {"train": {"arm": str, "steps": int, "expected_sha": str, "generations": int, "lr": float},
         "sft": {"name": str, "data": str, "init_repo": str, "expected_sha": str, "epochs": float, "lr": float, "max_steps": int},
         "publish": {"src": str, "repo": str, "base": str, "note": str},
         "evaluate": {"label": str, "modes": str, "expected_sha": str, "model": str, "adapter": str, "lenient": bool,
                      "token_budget": int}}


@app.function(secrets=[HF_SECRET], schedule=modal.Period(minutes=2), timeout=300)
def ops_tick():
    import json, time
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    try:
        q = open(hf_hub_download(DATA_REPO, "ops/queue.jsonl", repo_type="dataset", force_download=True)).read()
    except Exception as e:
        print("no queue", e); return
    state = OPS.get("state", {"spent": PRIOR_USD, "ops": {}})
    changed = False
    if state.get("ledger") != 2:  # re-base on measured cost; running ops keep their reservation
        state["spent"] = LEDGER_V2_USD + sum(r.get("committed_usd", 0) for r in state["ops"].values() if r.get("state") == "running")
        state["ledger"] = 2; changed = True
    for line in q.splitlines():
        if not line.strip():
            continue
        op = json.loads(line); oid = op["id"]
        if oid in state["ops"]:
            rec = state["ops"][oid]
            if op.get("cancel") and rec.get("call_id") and rec["state"] == "running":
                modal.FunctionCall.from_id(rec["call_id"]).cancel(); rec["state"] = "cancelled"; changed = True
            continue
        fn, kw = op.get("fn"), op.get("kwargs", {})
        bad = fn not in FUNCS or any(k not in FUNCS[fn] or not isinstance(v, FUNCS[fn][k]) for k, v in kw.items())
        cost = float(op.get("max_hours", 99)) * COST_PER_HOUR
        if bad:
            state["ops"][oid] = {"state": "rejected", "why": "not whitelisted / bad args"}
        elif state["spent"] + cost > CAP_USD:
            state["ops"][oid] = {"state": "rejected", "why": f"cap: committed {state['spent']:.2f} + {cost:.2f} > {CAP_USD}"}
        else:
            call = {"train": train, "evaluate": evaluate, "sft": sft, "publish": publish}[fn].spawn(**kw)
            state["spent"] += cost
            state["ops"][oid] = {"state": "running", "call_id": call.object_id, "fn": fn, "kwargs": kw,
                                 "committed_usd": cost, "started": time.time()}
        changed = True
    for oid, rec in state["ops"].items():
        if rec.get("state") == "running":
            try:
                rec["result"] = modal.FunctionCall.from_id(rec["call_id"]).get(timeout=0); rec["state"] = "done"; changed = True
                rec["finished"] = time.time()
                if state.get("ledger") == 2 and rec.get("started", 0) > 1794738000:  # ops launched under ledger v2
                    actual = (rec["finished"] - rec["started"]) / 3600 * COST_PER_HOUR
                    state["spent"] += actual - rec.get("committed_usd", 0); rec["actual_usd_est"] = round(actual, 2)
            except TimeoutError:
                pass
            except Exception as e:
                rec["state"] = "failed"; rec["error"] = repr(e)[:500]; changed = True
    OPS["state"] = state
    if state.get("cap") != CAP_USD:
        state["cap"] = CAP_USD; state["app_version"] = "gen-v1"; changed = True
    if changed or int(time.time()) % 1800 < 120:
        state["tick"] = time.time()
        api.upload_file(path_or_fileobj=json.dumps(state, indent=1, default=str).encode(), path_in_repo="ops/status.json",
                        repo_id=DATA_REPO, repo_type="dataset", commit_message="ops status")

@app.local_entrypoint()
def main(arm: str = "smoke", steps: int = 0, generations: int = 8):
    import hashlib
    assert arm in ("smoke", "grpo", "control"), arm
    steps = steps or (2 if arm == "smoke" else 200)
    sha = hashlib.sha256(open("runtime/kaggle-bundle/code.tgz", "rb").read()).hexdigest()
    print(f"arm={arm} steps={steps} code={sha[:12]}")
    print(train.remote(arm, steps, sha, generations))
