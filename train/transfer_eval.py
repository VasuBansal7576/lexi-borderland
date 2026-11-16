"""Transfer evaluation, identical for every model (base / plain-trace B / derivation A / v5):
  bfcl  : 400 BFCL v3 AST items (simple 120, multiple 100, parallel 80, irrelevance 100), one prompt with one format
          example for all models; strict (whole output is the JSON object) and lenient (first JSON object, fences
          stripped) scoring; Borderland-format bleed counted.
  gsm8k : 500 GSM8K test items; 'Answer: N' (or last number) vs gold.
  wipe  : procedural notes-across-a-wipe episodes, train families on unseen seeds + 2 never-trained families;
          conditions own-notes / blank-notes / twin-swapped-notes.
python -m train.transfer_eval --model M [--adapter A] --tasks bfcl,gsm8k,wipe --label L --outdir D"""
import argparse, json, os, random, re, time
from pathlib import Path
from .gen_general import TOOL_SYS, MATH_SYS
from .wipefam import TRAIN_FAMILIES, HELDOUT_FAMILIES, CODING_FAMILIES, make_episode, system_prompt, user_prompt, score_final

EXAMPLE = '\nExample reply: {"reason": "user asks for the weather in Paris", "calls": [{"name": "get_weather", "arguments": {"city": "Paris"}}]}'
BFCL_REPO = "gorilla-llm/Berkeley-Function-Calling-Leaderboard"


def first_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    i = min([j for j in (t.find("{"), t.find("[")) if j >= 0], default=-1)
    if i < 0:
        return None
    try:
        return json.JSONDecoder().raw_decode(t[i:])[0]
    except ValueError:
        return None


def strict_obj(text):
    try:
        o = json.loads(text.strip()); return o if isinstance(o, dict) else None
    except ValueError:
        return None


def to_calls(o):
    if isinstance(o, dict) and isinstance(o.get("calls"), list):
        return o["calls"], False
    if isinstance(o, dict) and "name" in o:
        return [o], False
    if isinstance(o, dict) and "tool" in o:            # Borderland-format bleed
        return [{"name": o["tool"], "arguments": o.get("args", {})}], True
    if isinstance(o, list):
        return o, False
    return None, False


def norm(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, str): return v.strip().lower()
    if isinstance(v, (list, tuple)): return tuple(norm(x) for x in v)
    if isinstance(v, dict): return tuple(sorted((k, norm(x)) for k, x in v.items()))
    return v


def call_ok(call, gt):
    (gname, gparams), = gt.items()
    if not isinstance(call, dict) or call.get("name") != gname:
        return False
    args = call.get("arguments") or {}
    if isinstance(args, str):
        try: args = json.loads(args)
        except ValueError: return False
    if any(k not in gparams for k in args):
        return False
    for p, allowed in gparams.items():
        if p in args:
            if norm(args[p]) not in [norm(x) for x in allowed if x != ""]:
                return False
        elif "" not in allowed:
            return False
    return True


def bfcl_items(seed=0):
    from huggingface_hub import hf_hub_download
    get = lambda f: [json.loads(l) for l in open(hf_hub_download(BFCL_REPO, f, repo_type="dataset"))]
    items = []
    for cat, n in (("simple", 120), ("multiple", 100), ("parallel", 80), ("irrelevance", 100)):
        qs = get(f"BFCL_v3_{cat}.json")
        gts = {g["id"]: g["ground_truth"] for g in get(f"possible_answer/BFCL_v3_{cat}.json")} if cat != "irrelevance" else {}
        random.Random(seed).shuffle(qs)
        for q in qs[:n]:
            items.append({"id": q["id"], "cat": cat, "query": q["question"][0][-1]["content"], "functions": q["function"],
                          "gt": gts.get(q["id"], [])})
    return items


def score_bfcl(it, raw):
    s = strict_obj(raw); o = s if s is not None else first_json(raw)
    calls, bleed = to_calls(o)
    if calls is None and it["cat"] == "irrelevance" and "{" not in raw:
        calls = []                      # a plain-text refusal is a correct no-call
    def correct(calls):
        if calls is None: return False
        if it["cat"] == "irrelevance": return len(calls) == 0
        if len(calls) != len(it["gt"]): return False
        left = list(it["gt"])
        for c in calls:
            m = next((g for g in left if call_ok(c, g)), None)
            if m is None: return False
            left.remove(m)
        return True
    strict_calls = to_calls(s)[0] if s is not None else None
    ok = correct(calls)
    names = {f["name"] for f in it["functions"]}
    fail = None if ok else ("parse" if calls is None else
                            "schema" if any(not isinstance(c, dict) or c.get("name") not in names for c in calls) else "semantic")
    return {"strict": correct(strict_calls), "lenient": ok, "parsed": calls is not None, "bleed": bleed, "failure": fail}


def gsm_items(n=500):
    import pandas as pd
    from huggingface_hub import hf_hub_download
    d = pd.read_parquet(hf_hub_download("openai/gsm8k", "main/test-00000-of-00001.parquet", repo_type="dataset"))
    d = d.sample(frac=1, random_state=11).head(n)
    return [{"id": f"gsm{i}", "q": r["question"], "gold": float(r["answer"].split("####")[1].strip().replace(",", ""))} for i, r in d.iterrows()]


def score_gsm(it, raw):
    nums = re.findall(r"-?\d[\d,]*\.?\d*", raw)
    try:
        v = float(nums[-1].replace(",", "")); return {"correct": abs(v - it["gold"]) < 1e-6, "answer": v}
    except Exception:
        return {"correct": False, "answer": None}


def wipe_episodes(n_per_fam=16, families=None):
    eps = []
    for fam in families or (TRAIN_FAMILIES + HELDOUT_FAMILIES):
        seed, k = 100000, 0
        while k < n_per_fam:
            e0, e1 = make_episode(fam, seed, 0), make_episode(fam, seed, 1); seed += 1
            if e0["final_args"] == e1["final_args"]:
                continue                      # keep only twins whose answers differ (swap test is informative)
            eps.append((e0, e1)); k += 1
    return eps


def parse_agent(ep, raw):
    r, t, a = ep["schema"]
    o = strict_obj(raw) or first_json(raw)
    if not isinstance(o, dict): return None
    if t not in o and "tool" in o:   # tolerate the generic keys
        o = {r: o.get("reason", ""), t: o.get("tool"), a: o.get("args", {})}
    return o


def run_wipe(gen, eps, max_reads=10):
    """Phase 1 for each episode (model gathers + writes notes), then phase 2 under three note conditions."""
    states = [{"ep": e, "hist": [], "notes": None, "steps": 0} for pair in eps for e in pair]
    live = list(states)
    while live:
        outs = gen([[{"role": "system", "content": system_prompt(s["ep"], 1)},
                     {"role": "user", "content": user_prompt(s["ep"], 1, s["hist"])}] for s in live])
        nxt = []
        for s, raw in zip(live, outs):
            ep = s["ep"]; r, t, a = ep["schema"]; s["steps"] += 1
            o = parse_agent(ep, raw)
            args = o.get(a) if (o and isinstance(o.get(a), dict)) else {}
            if o and o.get(t) == ep["note"]:
                lines = args.get("lines", [])
                s["notes"] = [str(x)[:96] for x in lines][:4] if isinstance(lines, list) else []
                continue
            if o and o.get(t) == ep["read"]:
                d = args.get("doc_id")
                d = d if isinstance(d, str) else str(d)
                s["hist"].append({"did": {ep["read"]: d}, "result": ep["docs"].get(d, "error: no such document")})
            else:
                s["hist"].append({"did": raw[:200], "result": "error: invalid action"})
            if s["steps"] >= max_reads + 2:
                s["notes"] = []; continue
            nxt.append(s)
        live = nxt
    # interventions reuse the MODEL's saved notes: blank = empty, swap = the notes it wrote on the counterfactual twin
    conds = []
    for i in range(0, len(states), 2):
        s0, s1 = states[i], states[i + 1]
        s0["twin"] = s1["ep"]
        for cond, notes in (("own", s0["notes"]), ("blank", []), ("swap", s1["notes"])):
            conds.append((s0, cond, notes))
    outs = gen([[{"role": "system", "content": system_prompt(s["ep"], 2)},
                 {"role": "user", "content": user_prompt(s["ep"], 2, None, notes)}] for s, cond, notes in conds])
    rows = []
    for (s, cond, notes), raw in zip(conds, outs):
        ep = s["ep"]; o = parse_agent(ep, raw)
        rows.append({"family": ep["family"], "heldout_family": ep["family"] in HELDOUT_FAMILIES, "seed": ep["seed"], "cond": cond,
                     "notes": notes, "wrote_notes": bool(s["notes"]), "raw": raw[:600], "correct": score_final(ep, o) if o else False,
                     "follows_twin": score_final(s["twin"], o) if (o and cond == "swap") else None, "phase1_steps": s["steps"]})
    return rows


MMLU_LANGS = ["en", "fr", "de", "es", "ar", "hi", "sw", "yo"]


def mmlu_items(per=25):
    import pandas as pd
    from huggingface_hub import hf_hub_download
    items = []
    for lang in MMLU_LANGS:
        d = pd.read_parquet(hf_hub_download("CohereLabs/Global-MMLU-Lite", f"{lang}/test-00000-of-00001.parquet", repo_type="dataset"))
        d = d.sample(frac=1, random_state=5).head(per)
        for i, r in d.iterrows():
            q = (f"{r['question']}\nA. {r['option_a']}\nB. {r['option_b']}\nC. {r['option_c']}\nD. {r['option_d']}\n"
                 "Answer with the letter of the correct option.")
            items.append({"id": f"{lang}{i}", "lang": lang, "q": q, "gold": str(r["answer"]).strip().upper()})
    return items


def score_mmlu(it, raw):
    u = raw.strip().upper()
    m = re.search(r"ANSWER(?: IS)?\s*[:\-]?\s*\(?([ABCD])\b", u) or re.match(r"\(?([ABCD])[\).:\s]", u + " ") or re.search(r"\b([ABCD])\b", u)
    return {"correct": bool(m) and m.group(1) == it["gold"], "answer": m.group(1) if m else None}


def boot(vals, n=1000, seed=0):
    rng = random.Random(seed); m = len(vals)
    if not m: return [None, None]
    xs = sorted(sum(vals[rng.randrange(m)] for _ in range(m)) / m for _ in range(n))
    return [round(xs[25], 3), round(xs[974], 3)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True); p.add_argument("--adapter", default=None)
    p.add_argument("--tasks", default="bfcl,gsm8k,mmlu,wipe"); p.add_argument("--label", required=True)
    p.add_argument("--outdir", default="artifacts/eval/transfer"); p.add_argument("--limit", type=int, default=None)
    p.add_argument("--token-budget", type=int, default=24000)
    a = p.parse_args()
    from .generate import HFGenerator
    out = Path(a.outdir) / a.label; out.mkdir(parents=True, exist_ok=True)
    summary = {"label": a.label, "model": a.model, "adapter": a.adapter}
    if "bfcl" in a.tasks:
        gen = HFGenerator(a.model, adapter=a.adapter, max_tokens=640, token_budget=a.token_budget)
        items = bfcl_items()[: a.limit]
        outs = gen([[{"role": "system", "content": TOOL_SYS.format(tools=json.dumps(it["functions"])) + EXAMPLE},
                     {"role": "user", "content": it["query"]}] for it in items])
        rows = [{**{k: it[k] for k in ("id", "cat")}, "raw": raw[:800], **score_bfcl(it, raw)} for it, raw in zip(items, outs)]
        with open(out / "bfcl.jsonl", "w") as f:
            for r in rows: f.write(json.dumps(r) + "\n")
        summary["bfcl"] = {k: {"n": len(rs), "strict": round(sum(r["strict"] for r in rs) / len(rs), 3),
                               "lenient": round(sum(r["lenient"] for r in rs) / len(rs), 3),
                               "lenient_ci": boot([r["lenient"] for r in rs]), "bleed": sum(r["bleed"] for r in rs)}
                           for k, rs in [("all", rows)] + [(c, [r for r in rows if r["cat"] == c]) for c in ("simple", "multiple", "parallel", "irrelevance")] if rs}
        del gen
    if "gsm8k" in a.tasks:
        gen = HFGenerator(a.model, adapter=a.adapter, max_tokens=512, token_budget=a.token_budget, stop_json=False)
        items = gsm_items()[: a.limit]
        outs = gen([[{"role": "system", "content": MATH_SYS}, {"role": "user", "content": it["q"]}] for it in items])
        rows = [{"id": it["id"], "gold": it["gold"], "raw": raw[:1200], **score_gsm(it, raw)} for it, raw in zip(items, outs)]
        with open(out / "gsm8k.jsonl", "w") as f:
            for r in rows: f.write(json.dumps(r) + "\n")
        summary["gsm8k"] = {"n": len(rows), "acc": round(sum(r["correct"] for r in rows) / len(rows), 3), "ci": boot([r["correct"] for r in rows])}
        del gen
    if "mmlu" in a.tasks:
        gen = HFGenerator(a.model, adapter=a.adapter, max_tokens=24, token_budget=a.token_budget, stop_json=False)
        items = mmlu_items()[: a.limit]
        outs = gen([[{"role": "user", "content": it["q"]}] for it in items])
        rows = [{"id": it["id"], "lang": it["lang"], "gold": it["gold"], "raw": raw[:200], **score_mmlu(it, raw)} for it, raw in zip(items, outs)]
        with open(out / "mmlu.jsonl", "w") as f:
            for r in rows: f.write(json.dumps(r) + "\n")
        summary["mmlu"] = {"n": len(rows), "acc": round(sum(r["correct"] for r in rows) / len(rows), 3), "ci": boot([r["correct"] for r in rows])}
        del gen
    if "wipecode" in a.tasks:
        gen = HFGenerator(a.model, adapter=a.adapter, max_tokens=320, token_budget=a.token_budget)
        rows = run_wipe(gen, wipe_episodes(48, CODING_FAMILIES)[: a.limit])
        with open(out / "wipecode.jsonl", "w") as f:
            for r in rows: f.write(json.dumps(r) + "\n")
        summary["wipecode"] = {c: {"n": len(rs), "acc": round(sum(r["correct"] for r in rs) / len(rs), 3), "ci": boot([r["correct"] for r in rs]),
                                   "wrote_notes": round(sum(r["wrote_notes"] for r in rs) / len(rs), 3)}
                               for c in ("own", "blank", "swap") for rs in [[r for r in rows if r["cond"] == c]] if rs}
        del gen
    if "wipe" in a.tasks.split(","):
        gen = HFGenerator(a.model, adapter=a.adapter, max_tokens=320, token_budget=a.token_budget)
        eps = wipe_episodes()[: a.limit]
        rows = run_wipe(gen, eps)
        with open(out / "wipe.jsonl", "w") as f:
            for r in rows: f.write(json.dumps(r) + "\n")
        summ = {}
        for split, keep in (("train_families_unseen_seeds", lambda r: not r["heldout_family"]), ("heldout_families", lambda r: r["heldout_family"])):
            for cond in ("own", "blank", "swap"):
                rs = [r for r in rows if keep(r) and r["cond"] == cond]
                if rs:
                    summ[f"{split}/{cond}"] = {"n": len(rs), "acc": round(sum(r["correct"] for r in rs) / len(rs), 3),
                                               "ci": boot([r["correct"] for r in rs]),
                                               "wrote_notes": round(sum(r["wrote_notes"] for r in rs) / len(rs), 3)}
                    if cond == "swap":
                        summ[f"{split}/{cond}"]["follows_twin"] = round(sum(bool(r["follows_twin"]) for r in rs) / len(rs), 3)
        summary["wipe"] = summ
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
