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
    with open("/data/grpo-states-v2.jsonl", "w") as out:
        for part in sorted(glob.glob(f"{d}/grpo-states-v2.part*.txt")):
            out.write(open(part).read())
    want = {l.split()[2]: l.split()[1] for l in open(f"{d}/MANIFEST.sha256.txt") if l.startswith("orig ")}
    got = hashlib.sha256(open("/data/grpo-states-v2.jsonl", "rb").read()).hexdigest()
    assert got == want["grpo-states-v2.jsonl"], "grpo states checksum mismatch"
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
        api.create_repo(OUT_REPO[arm], exist_ok=True, private=False)
        api.upload_folder(folder_path=out, repo_id=OUT_REPO[arm], commit_message=f"GRPO {arm} {steps} steps from SFT v2",
                          ignore_patterns=["checkpoint-*/*"])
        api.upload_folder(folder_path=out, repo_id=DATA_REPO, repo_type="dataset", path_in_repo=f"runs/modal_{arm}_{steps}",
                          allow_patterns=["checkpoint-*/trainer_state.json"], commit_message=f"modal {arm} checkpoints state")
    print(json.dumps(summary, indent=1), flush=True)
    return summary



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
CAP_USD = 27.0           # hard cap on everything launched through the queue (incl. runs launched by hand)
PRIOR_USD = 8.0          # smoke + the hand-launched GRPO run
FUNCS = {"train": {"arm": str, "steps": int, "expected_sha": str, "generations": int, "lr": float},
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
            call = (train if fn == "train" else evaluate).spawn(**kw)
            state["spent"] += cost
            state["ops"][oid] = {"state": "running", "call_id": call.object_id, "fn": fn, "kwargs": kw,
                                 "committed_usd": cost, "started": time.time()}
        changed = True
    for oid, rec in state["ops"].items():
        if rec.get("state") == "running":
            try:
                rec["result"] = modal.FunctionCall.from_id(rec["call_id"]).get(timeout=0); rec["state"] = "done"; changed = True
            except TimeoutError:
                pass
            except Exception as e:
                rec["state"] = "failed"; rec["error"] = repr(e)[:500]; changed = True
    OPS["state"] = state
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
