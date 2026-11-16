"""Kaggle GPU job (2x T4, fp16). Set at launch: PHASE, EXPECTED_SHA (sha256 of code.tgz), HF token.
Phases:
  preflight - check() for base and SFT only.
  every eval phase first runs check() on its own model (finite logits, memory, throughput -> projection <= 10 h,
              teacher-tool agreement on 30 training states recorded as a diagnostic) and refuses to run if RED.
  int_sft - notebook interventions for SFT at room 4 (GPU0 blank notebook, GPU1 anti-twin notebook), same check().
  eval_base / eval_sft - crash-safe evaluation (GPU0: room4_all on 64 worlds; GPU1: rooms then full on 16 worlds);
              results uploaded every 10 minutes and at the end."""
PHASE = "__PHASE__"
EXPECTED_SHA = "__EXPECTED_SHA__"
import base64, glob, hashlib, json, os, subprocess, sys, threading, time
os.environ["HF_TOKEN"] = "__HF_TOKEN__"  # private notebook only
W, BUNDLE, CODE = "/kaggle/working", "/kaggle/bundle", "/kaggle/lexi"
BASE = "CohereLabs/tiny-aya-global"
DATA_REPO = "FatUnc6969/lexi-borderland-data"
SFT_REPO = "FatUnc6969/tiny-aya-borderland-sft"
T0 = time.time()


def log(*a):
    print(f"[{time.time()-T0:6.0f}s]", *a, flush=True)


def sh(cmd, check=True, env=None):
    log("+", cmd)
    r = subprocess.run(cmd, shell=True, env={**os.environ, **(env or {})})
    if check and r.returncode:
        raise SystemExit(f"FAILED rc={r.returncode}: {cmd}")
    return r.returncode


def setup():
    sh("pip -q uninstall -y torchao 2>&1 | tail -1", check=False)  # Kaggle's torchao breaks current PEFT imports
    sh('pip -q install "transformers>=5.15,<6" "peft>=0.13" huggingface_hub accelerate 2>&1 | tail -2')
    if PHASE.startswith("grpo"):
        sh('pip -q install "trl==1.7.1" datasets rich jinja2 pyyaml pydantic 2>&1 | tail -2')
        sh("pip -q install --no-deps 'git+https://github.com/Lexsi-Labs/AgentTune@1dfd054ce59e1c1bdd566cb7e5826f836b1c8c2e' 2>&1 | tail -2")
        sh('python -c "import trl, agenttune; print(trl.__version__)"')
    from huggingface_hub import snapshot_download
    d = snapshot_download(DATA_REPO, repo_type="dataset", allow_patterns=["bundle/*"], token=os.environ["HF_TOKEN"]) + "/bundle"
    os.makedirs(BUNDLE, exist_ok=True); os.makedirs(CODE, exist_ok=True)
    raw = base64.b64decode(open(f"{d}/code.tgz.b64.txt").read())
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_SHA:
        raise SystemExit(f"STALE CODE: bundle sha {sha[:12]} != expected {EXPECTED_SHA[:12]}")
    open(f"{BUNDLE}/code.tgz", "wb").write(raw)
    want = {l.split()[2]: l.split()[1] for l in open(f"{d}/MANIFEST.sha256.txt") if l.startswith("orig ")}
    for name, h in want.items():
        if name == "code.tgz":
            continue
        stem = name.rsplit(".", 1)[0]
        with open(f"{BUNDLE}/{name}", "w") as out:
            for part in sorted(glob.glob(f"{d}/{stem}.part*.txt")):
                out.write(open(part).read())
        assert hashlib.sha256(open(f"{BUNDLE}/{name}", "rb").read()).hexdigest() == h, f"checksum {name}"
    sh(f"tar xzf {BUNDLE}/code.tgz -C {CODE}")
    os.environ["PYTHONPATH"] = CODE
    log("code sha verified", sha[:12])


def upload(tag):
    try:
        from huggingface_hub import HfApi
        HfApi(token=os.environ["HF_TOKEN"]).upload_folder(folder_path=W, repo_id=DATA_REPO, repo_type="dataset",
            path_in_repo=f"runs/{PHASE}", commit_message=f"{PHASE}: {tag}", allow_patterns=["*.json", "*.jsonl", "*.log", "*.txt"])
        log("uploaded", tag)
    except Exception as e:
        log("upload failed", e)


def check(name, adapter):
    """In-job gate on the exact eval stack (same dtype, generator, prompts): finite logits on the longest prompt,
    peak memory, throughput on a realistic batch, and tool agreement with the teacher on 30 training states."""
    import torch
    sys.path.insert(0, CODE)
    from train.generate import HFGenerator
    from train.eval_model import plan, make_episode
    eps = [make_episode(w, r, "rooms") for w, r in plan("rooms") if r in (6, 7)][:4] + \
          [make_episode(w, r, "room4_all") for w, r in plan("room4_all")][:8]
    msgs = [e.messages() for e in eps]
    g = HFGenerator(BASE, adapter=adapter, max_tokens=400)
    lens = [len(g.tok.apply_chat_template(m, tokenize=True, add_generation_prompt=True)["input_ids"]) for m in msgs]
    longest = max(range(len(msgs)), key=lambda i: lens[i])
    enc = g.tok(g.tok.apply_chat_template(msgs[longest], tokenize=False, add_generation_prompt=True),
                return_tensors="pt", add_special_tokens=False).to("cuda")
    with torch.inference_mode():
        logits = g.model(**enc).logits[0, -1].float()
    rep = {"gpu": torch.cuda.get_device_name(0), "dtype": g.dtype, "logits_finite": bool(torch.isfinite(logits).all()),
           "longest_prompt_tokens": lens[longest]}
    t = time.time(); outs = g(msgs); dt = time.time() - t
    rep.update({"batch": len(msgs), "batch_seconds": round(dt, 1), "sec_per_episode_step": round(dt / len(msgs), 2),
                "new_tokens": g.new_tokens, "peak_gb": round(g.peak_gb, 2), "oom_retries": g.oom_retries,
                "sample_output": outs[longest][:300]})
    rows = [json.loads(l) for l in open(f"{BUNDLE}/sft-subset.jsonl")][:30]
    preds = g([r["messages"][:-1] for r in rows])
    def tool(x):
        try:
            x = x[x.index("{"):]
            return json.JSONDecoder().raw_decode(x)[0]["tool"]
        except Exception:
            return None
    pairs = [(tool(p), json.loads(r["messages"][-1]["content"])["tool"]) for p, r in zip(preds, rows)]
    rep.update({"teacher_tool_match_30": sum(a == b for a, b in pairs), "valid_json_30": sum(a is not None for a, _ in pairs),
                "mismatches": [[a, b] for a, b in pairs if a != b]})
    # per model ~4,500 episode-steps (room4_all 64x~25, rooms 112x~12, full 16x~70), split over 2 GPUs
    rep["projected_eval_hours"] = round(4500 * rep["sec_per_episode_step"] / 2 / 3600, 1)
    rep["gates"] = {"logits_finite": rep["logits_finite"], "memory_ok": rep["peak_gb"] < 14.0,
                    "projected_le_10h": rep["projected_eval_hours"] <= 10.0}
    rep["GREEN"] = all(rep["gates"].values())
    del g; torch.cuda.empty_cache()
    json.dump(rep, open(f"{W}/check-{name}.json", "w"), indent=1)
    log("CHECK", name, json.dumps(rep)[:600])
    upload(f"check {name}")
    return rep


def preflight():
    from huggingface_hub import snapshot_download
    check("base", None); check("sft", snapshot_download(SFT_REPO, token=os.environ["HF_TOKEN"]))


def run_specs(specs, lenient=(), do_check=True):
    """specs: [(gpu, label, adapter, modes)]; labels in `lenient` get --lenient-json. Each model is checked once (in-job gate) before any eval starts."""
    checked = {}
    for _, label, adapter, _ in (specs if do_check else []):
        if label not in checked:
            checked[label] = check(label, adapter)
            if not checked[label]["GREEN"]:
                raise SystemExit(f"CHECK RED for {label}, not evaluating: {checked[label]['gates']}")
    stop = threading.Event()
    def pump():
        while not stop.wait(600):
            upload("progress")
    threading.Thread(target=pump, daemon=True).start()
    procs = []
    for gpu, label, adapter, modes in specs:
        ad = f" --adapter {adapter}" if adapter else ""
        cmd = (f"cd {CODE} && {sys.executable} -m train.eval_model --policy hf --model {BASE}{ad} --outdir {W}/eval "
               f"--label {label} --max-tokens 400 --bundle-sha {EXPECTED_SHA[:12]} --modes {modes} "
               f"{'--lenient-json ' if label in lenient else ''}"
               f"> {W}/{label}-gpu{gpu}.log 2>&1")
        procs.append(subprocess.Popen(cmd, shell=True, env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)}))
    rc = [p.wait() for p in procs]
    stop.set()
    log("eval rc", rc)
    sh(f"tail -c 1500 {W}/*-gpu*.log", check=False)


def grpo_pair(sft_repo, steps):
    """GRPO (GPU0) and the matched random-reward control (GPU1) from the same merged SFT checkpoint, fp16 on T4."""
    merged = "/kaggle/tmp/sft-merged"
    sh(f"cd {CODE} && {sys.executable} -m train.merge --base {BASE} --adapter {repo(sft_repo)} --output {merged}")
    stop = threading.Event()
    def pump():
        while not stop.wait(600):
            upload("progress")
    threading.Thread(target=pump, daemon=True).start()
    procs = []
    for gpu, arm in ((0, "grpo4"), (1, "control4")):
        flag = " --control" if arm == "control4" else ""
        cmd = (f"cd {CODE} && {sys.executable} -m train.grpo_train --model {merged} --states {BUNDLE}/grpo-states-v4.jsonl "
               f"--output {W}/{arm} --steps {steps} --generations 8 --batch 4 --lr 1e-5 --completion-len 400 "
               f"--temperature 1.0 --max-prompt-tokens 5000 --save-steps 25{flag} > {W}/{arm}.log 2>&1")
        procs.append(subprocess.Popen(cmd, shell=True, env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu),
                                                             "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}))
    rc = [p.wait() for p in procs]
    stop.set(); log("grpo rc", rc)
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ["HF_TOKEN"])
    for arm, rid in (("grpo4", "FatUnc6969/tiny-aya-borderland-grpo-sft5"), ("control4", "FatUnc6969/tiny-aya-borderland-grpo-sft5-randreward-control")):
        if os.path.exists(f"{W}/{arm}/adapter_model.safetensors"):
            open(f"{W}/{arm}/README.md", "w").write(f"---\nbase_model: {sft_repo}\nlibrary_name: peft\n---\n# {arm}\nGRPO arm ({arm}) on top of {sft_repo} merged into Tiny Aya Global.\n")
            api.create_repo(rid, exist_ok=True, private=False)
            api.upload_folder(folder_path=f"{W}/{arm}", repo_id=rid, ignore_patterns=["checkpoint-*/*"])
    sh(f"tail -c 1500 {W}/grpo4.log {W}/control4.log", check=False)


def run_transfer(specs):
    """specs: [(gpu, label, adapter_or_None, tasks)] -> train.transfer_eval on each GPU in parallel."""
    stop = threading.Event()
    def pump():
        while not stop.wait(600):
            upload("progress")
    threading.Thread(target=pump, daemon=True).start()
    procs = []
    for gpu, label, adapter, tasks in specs:
        ad = f" --adapter {adapter}" if adapter else ""
        cmd = (f"cd {CODE} && {sys.executable} -m train.transfer_eval --model {BASE}{ad} --tasks {tasks} --label {label} "
               f"--outdir {W}/transfer > {W}/{label}-gpu{gpu}.log 2>&1")
        procs.append(subprocess.Popen(cmd, shell=True, env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)}))
    rc = [p.wait() for p in procs]
    stop.set(); log("transfer rc", rc)
    sh(f"tail -c 2500 {W}/*-gpu*.log", check=False)


def run_full(specs, bl_modes="rooms,full,chain4,room4_blank,room4_swap"):
    """specs: [(gpu, label, adapter)] -> per GPU, sequentially: transfer suite, then Borderland held-out suite."""
    stop = threading.Event()
    def pump():
        while not stop.wait(600):
            upload("progress")
    threading.Thread(target=pump, daemon=True).start()
    procs = []
    for gpu, label, adapter in specs:
        ad = f" --adapter {adapter}" if adapter else ""
        cmd = (f"cd {CODE} && {sys.executable} -m train.transfer_eval --model {BASE}{ad} --tasks bfcl,gsm8k,mmlu,wipe,wipecode "
               f"--label {label} --outdir {W}/transfer > {W}/{label}-xfer-gpu{gpu}.log 2>&1; "
               f"{sys.executable} -m train.eval_model --policy hf --model {BASE}{ad} --outdir {W}/eval --label {label} "
               f"--max-tokens 400 --bundle-sha {EXPECTED_SHA[:12]} --modes {bl_modes} > {W}/{label}-bl-gpu{gpu}.log 2>&1")
        procs.append(subprocess.Popen(cmd, shell=True, env={**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu)}))
    rc = [p.wait() for p in procs]
    stop.set(); log("full rc", rc)
    sh(f"tail -c 2000 {W}/*-gpu*.log", check=False)


def evaluate(label, adapter, gpu0="room4_all", gpu1="rooms,full"):
    run_specs([(0, label, adapter, gpu0), (1, label, adapter, gpu1)])


def repo(name):
    from huggingface_hub import snapshot_download
    return snapshot_download(name, token=os.environ["HF_TOKEN"])


SFT2_REPO = "FatUnc6969/tiny-aya-borderland-sft-v2"


try:
    setup()
    if PHASE == "preflight":
        preflight()
    elif PHASE == "eval_base":
        evaluate("base", None)
    elif PHASE == "eval_sft":
        from huggingface_hub import snapshot_download
        evaluate("sft", snapshot_download(SFT_REPO, token=os.environ["HF_TOKEN"]))
    elif PHASE == "int_sft":
        from huggingface_hub import snapshot_download
        evaluate("sft", snapshot_download(SFT_REPO, token=os.environ["HF_TOKEN"]), gpu0="room4_blank", gpu1="room4_swap")
    elif PHASE == "xfer_base_v5":
        run_transfer([(0, "base", None, "bfcl,gsm8k,mmlu,wipe"), (1, "v5", repo("FatUnc6969/tiny-aya-borderland-sft-v5"), "bfcl,gsm8k,mmlu,wipe")])
    elif PHASE == "wipe_base_v5":
        run_transfer([(0, "base", None, "wipe"), (1, "v5", repo("FatUnc6969/tiny-aya-borderland-sft-v5"), "wipe")])
    elif PHASE == "wipecode_all":
        run_transfer([(0, "base", None, "wipecode"), (1, "genA", repo("FatUnc6969/tiny-aya-borderland-genA"), "wipecode")])
        run_transfer([(0, "genB", repo("FatUnc6969/tiny-aya-borderland-genB"), "wipecode"), (1, "v5", repo("FatUnc6969/tiny-aya-borderland-sft-v5"), "wipecode")])
    elif PHASE == "scale_A":
        a = repo("FatUnc6969/tiny-aya-borderland-genA")
        def one(gpu, sc):
            lab = f"genA-s{int(sc*100)}"
            return (f"cd {CODE} && LORA_SCALE={sc} {sys.executable} -m train.transfer_eval --model {BASE} --adapter {a} --tasks gsm8k,bfcl,mmlu "
                    f"--label {lab} --outdir {W}/transfer > {W}/{lab}-xfer-gpu{gpu}.log 2>&1; LORA_SCALE={sc} {sys.executable} -m train.eval_model "
                    f"--policy hf --model {BASE} --adapter {a} --outdir {W}/eval --label {lab} --max-tokens 400 --bundle-sha {EXPECTED_SHA[:12]} "
                    f"--modes chain4 > {W}/{lab}-bl-gpu{gpu}.log 2>&1")
        stop = threading.Event()
        threading.Thread(target=lambda: [upload("progress") for _ in iter(lambda: stop.wait(600), True)], daemon=True).start()
        ps = [subprocess.Popen(one(g, sc), shell=True, env={**os.environ, "CUDA_VISIBLE_DEVICES": str(g)}) for g, sc in ((0, 0.5), (1, 0.75))]
        log("scale rc", [p.wait() for p in ps]); stop.set()
    elif PHASE == "eval_A1":
        run_full([(0, "genA", repo("FatUnc6969/tiny-aya-borderland-genA"))])
    elif PHASE == "eval_B1":
        run_full([(0, "genB", repo("FatUnc6969/tiny-aya-borderland-genB"))])
    elif PHASE == "wipe_base_v5b":
        run_transfer([(0, "base", None, "wipe,wipecode"), (1, "v5", repo("FatUnc6969/tiny-aya-borderland-sft-v5"), "wipe,wipecode")])
    elif PHASE == "eval_AB":
        run_full([(0, "genA", repo("FatUnc6969/tiny-aya-borderland-genA")), (1, "genB", repo("FatUnc6969/tiny-aya-borderland-genB"))])
    elif PHASE == "dagger5":
        os.environ["DAGGER_WORLDS"] = "48"
        v5 = repo("FatUnc6969/tiny-aya-borderland-sft-v5")
        run_specs([(0, "dag5a", v5, "dagger0of2"), (1, "dag5b", v5, "dagger1of2")], do_check=False)
    elif PHASE == "grpo5":
        grpo_pair("FatUnc6969/tiny-aya-borderland-sft-v5", steps=120)
    elif PHASE == "grpo4":
        grpo_pair("FatUnc6969/tiny-aya-borderland-sft-v4", steps=150)
    elif PHASE == "eval_sft4":
        run_specs([(0, "sft4", repo("FatUnc6969/tiny-aya-borderland-sft-v4"), "room4_all"),
                   (1, "sft4", repo("FatUnc6969/tiny-aya-borderland-sft-v4"), "steps")])
    elif PHASE == "eval_sft2":
        evaluate("sft2", repo(SFT2_REPO))
    elif PHASE == "int_sft2_baselen_rooms":
        # GPU0: SFT v2 notebook interventions; GPU1: base, lenient JSON arm, rooms
        run_specs([(0, "sft2", repo(SFT2_REPO), "room4_blank,room4_swap"), (1, "base_lenient", None, "rooms")],
                  lenient=("base_lenient",))
    elif PHASE == "baselen_rest":
        run_specs([(0, "base_lenient", None, "room4_all"), (1, "base_lenient", None, "full")], lenient=("base_lenient",))
    upload("done")
except BaseException as e:
    open(f"{W}/FAILED.txt", "w").write(repr(e)); upload("failed"); raise
