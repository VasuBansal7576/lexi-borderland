"""Generalisation mixture (Fable plan): two datasets with IDENTICAL rows; A has verified derivation reasons, B has
the same actions/answers with empty reasons (plain-trace control). Sources:
  Borderland (sft-v6 targets, 50% surface-randomised) + DAgger relabels | 6 procedural wipe families (train split)
  tool calling: hermes single-turn + glaive v2 (incl. no-call / ask-for-missing) with argument grounding
  GSM8K train rewritten as checked derivations | aya_dataset multilingual instructions (same in A and B)
usage: python -m train.gen_general <gen_dir> <borderland_rows.jsonl> [dagger_rows.jsonl ...]"""
import json, os, random, re, sys
from collections import Counter
from .wipefam import TRAIN_FAMILIES, make_episode, teacher_steps

RNG = random.Random(2026)
TOOL_SYS = ("You can call these functions (JSON schema):\n{tools}\nReply with exactly one JSON object: "
            '{{"reason": string, "calls": [{{"name": function name, "arguments": object}}]}}. '
            'Use "calls": [] if no listed function fits the request or a required argument is missing.')
MATH_SYS = "Solve the problem. End with a final line 'Answer: <number>'."


def _in_text(v, q):
    if isinstance(v, bool):
        return False
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return len(str(v)) > 0 and str(v).lower() in q


def ground(query, calls, tools=()):
    """Per-argument provenance; every '(user text)' claim is a verified case-insensitive substring of the request."""
    if not calls:
        return None
    q = query.lower()
    schema = {t.get("name"): (t.get("parameters") or {}).get("properties", {}) for t in tools if isinstance(t, dict)}
    parts = []
    for c in calls:
        bits = []
        for k, v in (c.get("arguments") or {}).items():
            spec = schema.get(c["name"], {}).get(k, {}) if isinstance(schema.get(c["name"]), dict) else {}
            if isinstance(v, list) and v and all(_in_text(x, q) for x in v):
                bits.append(f"{k} <- " + ", ".join(f'"{x}"' for x in v) + " (user text)")
            elif not isinstance(v, (list, dict)) and _in_text(v, q):
                bits.append(f'{k} <- "{v}" (user text)')
            elif isinstance(spec, dict) and ("enum" in spec and v in spec["enum"]):
                bits.append(f"{k} = {json.dumps(v)} (schema enum)")
            elif isinstance(spec, dict) and spec.get("default") == v:
                bits.append(f"{k} = {json.dumps(v)} (schema default)")
            else:
                bits.append(f"{k} = {json.dumps(v)[:40]} (inferred from request)")
        parts.append(f"{c['name']}: " + ("; ".join(bits) if bits else "no arguments"))
    return "Request matches " + " | ".join(parts) + "."


def tool_row(tools, query, calls, src, plain, why=None):
    reason = "" if plain else (why or ground(query, calls, tools))
    tgt = json.dumps({"reason": reason, "calls": calls}, separators=(",", ":"), ensure_ascii=False)
    return {"world": src, "room": 0, "source": src, "messages": [
        {"role": "system", "content": TOOL_SYS.format(tools=json.dumps(tools, ensure_ascii=False))},
        {"role": "user", "content": query}, {"role": "assistant", "content": tgt}]}


def hermes(path, n):
    rows = []
    for ex in json.load(open(path)):
        conv = ex["conversations"]
        sysm = next(c["value"] for c in conv if c["from"] == "system"); hum = next(c["value"] for c in conv if c["from"] == "human")
        gpt = next(c["value"] for c in conv if c["from"] == "gpt")
        try:
            blob = max(re.findall(r"<tools>\s*(.*?)\s*</tools>", sysm, re.S), key=len)
            tools = [t.get("function", t) for t in json.loads(blob)]
            calls = [json.loads(x) for x in re.findall(r"<tool_call>\s*(.*?)\s*</tool_call>", gpt, re.S)]
            calls = [{"name": c["name"], "arguments": c.get("arguments", {})} for c in calls]
        except Exception:
            continue
        if calls and len(hum) < 2500:
            rows.append((tools, hum, calls, None))
    RNG.shuffle(rows); return rows[:n]


def glaive(path, n_call, n_nocall):
    calls_rows, nocall = [], []
    for ex in json.load(open(path)):
        if "{" not in ex["system"]:
            continue
        try:
            body = ex["system"].split("-", 1)[1]
            dec, tools, i = json.JSONDecoder(), [], 0
            while True:
                j = body.find("{", i)
                if j < 0: break
                obj, i = dec.raw_decode(body[j:]); i += j; tools.append(obj)
        except Exception:
            continue
        turns = re.split(r"\n\n\n(?=USER:|ASSISTANT:|FUNCTION RESPONSE:)", ex["chat"])
        if len(turns) < 2 or not turns[0].startswith("USER:") or not turns[1].startswith("ASSISTANT:"):
            continue
        q, a = turns[0][5:].strip(), turns[1][10:].replace("<|endoftext|>", "").strip()
        if a.startswith("<functioncall>"):
            m = re.match(r"<functioncall>\s*(\{.*\})\s*$", a, re.S)
            try:
                raw = m.group(1); name = json.loads(raw.split(", \"arguments\"")[0] + "}")["name"]
                args = json.loads(re.search(r"'(\{.*\})'", raw, re.S).group(1)) if "'" in raw else json.loads(raw).get("arguments", {})
                calls_rows.append((tools, q, [{"name": name, "arguments": args}], None))
            except Exception:
                continue
        else:
            why = ("A required argument is missing; ask the user instead of calling." if "?" in a
                   else "No listed function can perform this request.")
            nocall.append((tools, q, [], why))
    RNG.shuffle(calls_rows); RNG.shuffle(nocall)
    return calls_rows[:n_call], nocall[:n_nocall]


def gsm8k(path, n):
    import pandas as pd
    out = []
    for _, r in pd.read_parquet(path).sample(frac=1, random_state=7).iterrows():
        sol, ans = r["answer"].split("####")
        ok = True
        for expr, val in re.findall(r"<<([^=<>]+)=([^<>]+)>>", sol):
            try:
                ok &= abs(eval(expr.replace("^", "**"), {"__builtins__": {}}) - float(val)) < 1e-6
            except Exception:
                ok = False
        if not ok:
            continue
        clean = re.sub(r"<<[^<>]*>>", "", sol).strip()
        out.append((r["question"], clean, ans.strip().replace(",", "")))
        if len(out) >= n:
            break
    return out


def aya(path, n):
    import pandas as pd
    d = pd.read_parquet(path)
    d = d[(d["targets"].str.len() < 500) & (d["inputs"].str.len() < 800)]
    langs = d["language"].value_counts().index[:30]
    per = max(1, n // len(langs)); parts = [d[d["language"] == l].sample(min(per, (d["language"] == l).sum()), random_state=3) for l in langs]
    return [(r["inputs"], r["targets"], r["language"]) for p in parts for _, r in p.iterrows()][:n]


BL_TOOLS = ["read_record", "choose_door", "probe", "set_switch", "energize", "validate_registry", "certify_roster", "notebook_write",
            "notebook_read", "question", "unlock", "survey", "move", "activate_relay", "wait", "submit_bid", "accuse", "revoke",
            "accept_amendment", "allocate_points", "team_step", "settle", "exit_room", "inspect", "status"]
ALT = ["fetch", "pick", "test", "toggle", "power", "verify", "certify", "note", "recall", "ask", "open", "scan", "go", "arm",
       "pause", "bid", "charge", "cancel", "approve", "distribute", "command", "finish", "leave", "look", "state"]


def randomize_borderland(row, rng):
    """Rename every tool consistently (prompt, history, target) and the three output keys."""
    names = {t: f"{a}_{rng.choice(['x', 'op', 'act', 'cmd', 'do'])}{rng.randint(1, 9)}" for t, a in zip(BL_TOOLS, ALT)}
    keys = rng.choice([("thought", "action", "input"), ("why", "call", "params"), ("rationale", "op", "arguments")])
    def sub(text):
        for t, n in names.items():
            text = re.sub(rf"\b{t}\b", n, text)
        return text
    msgs = [dict(m) for m in row["messages"]]
    msgs[0]["content"] = sub(msgs[0]["content"]).replace("Return JSON with reason, tool, args",
                                                          f"Return JSON with {keys[0]}, {keys[1]}, {keys[2]}")
    msgs[1]["content"] = sub(msgs[1]["content"])
    tgt = json.loads(msgs[2]["content"])
    msgs[2]["content"] = json.dumps({keys[0]: tgt["reason"], keys[1]: names.get(tgt["tool"], tgt["tool"]), keys[2]: tgt["args"]},
                                    separators=(",", ":"), ensure_ascii=True)
    return {**row, "messages": msgs, "surface": "randomized"}


def strip_reason(row):
    msgs = [dict(m) for m in row["messages"]]
    c = msgs[-1]["content"]
    try:
        t = json.loads(c)
        k = next(iter(t))           # first key is always the reason field
        t[k] = ""
        msgs[-1]["content"] = json.dumps(t, separators=(",", ":"), ensure_ascii=False)
    except ValueError:              # math text rows: keep only the final answer line
        msgs[-1]["content"] = c.strip().splitlines()[-1]
    return {**row, "messages": msgs}


def main():
    gen, bl_path, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
    raw = os.path.join(gen, "raw")
    A = []
    # Borderland 30%: v6-format teacher rows (room 2 heavy) + DAgger relabels, half surface-randomised
    bl = [json.loads(l) for l in open(bl_path)]; RNG.shuffle(bl)
    r2 = [r for r in bl if r["room"] == 2][:300]; rest = [r for r in bl if r["room"] != 2][:600]
    dag = [json.loads(l) for p in extra for l in open(p)]
    RNG.shuffle(dag); dag = dag[:360]
    for i, r in enumerate(r2 + rest + dag):
        r = {**r, "source": r.get("source", "borderland")}
        A.append(randomize_borderland(r, random.Random(i)) if i % 2 else r)
    # procedural wipe families 30%
    for fam in TRAIN_FAMILIES:
        n = 0; seed = 0
        while n < 210:
            ep = make_episode(fam, seed, twin=seed % 2); seed += 1
            for msgs, tgt in teacher_steps(ep):
                A.append({"world": f"wipe/{fam}/{seed}", "room": 0, "source": f"wipe-{fam}",
                          "messages": msgs + [{"role": "assistant", "content": json.dumps(tgt, separators=(",", ":"))}]}); n += 1
    # tool calling 25%
    hm = hermes(os.path.join(raw, "func-calling-singleturn.json"), 450)
    gc, gn = glaive(os.path.join(raw, "glaive-function-calling-v2.json"), 450, 160)
    for tools, q, calls, why in hm + gc + gn:
        A.append(tool_row(tools, q, calls, "tools", False, why))
    # math + multilingual 15%
    for q, sol, ans in gsm8k(os.path.join(raw, "main/train-00000-of-00001.parquet"), 500):
        A.append({"world": "gsm8k", "room": 0, "source": "gsm8k", "keep_reason": True, "messages": [
            {"role": "system", "content": MATH_SYS}, {"role": "user", "content": q},
            {"role": "assistant", "content": sol + f"\nAnswer: {ans}"}]})
    for inp, tgt, lang in aya(os.path.join(raw, "data/train-00000-of-00001.parquet"), 150):
        A.append({"world": "aya", "room": 0, "source": "aya", "keep_reason": True, "messages": [
            {"role": "user", "content": inp}, {"role": "assistant", "content": tgt}]})
    RNG.shuffle(A)
    for i, r in enumerate(A):
        r["id"] = f"g{i:05d}"
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(os.environ.get("TOK", "CohereLabs/tiny-aya-global"))
    def ntok(r):
        ids = tok.apply_chat_template(r["messages"], tokenize=True)
        return len(ids["input_ids"] if hasattr(ids, "keys") else ids)
    keep, dropped = [], Counter()
    for r in A:
        if ntok(r) <= 6144: keep.append(r)
        else: dropped[r["source"]] += 1
    A = keep
    B = [r if r.get("keep_reason") else strip_reason(r) for r in A]
    print("dropped (both A and B) for length:", dict(dropped))
    for name, rows in (("A", A), ("B", B)):
        with open(os.path.join(gen, f"gen-{name}.jsonl"), "w") as f:
            for r in rows: f.write(json.dumps(r, separators=(",", ":"), ensure_ascii=False) + "\n")
    print(json.dumps({"rows": len(A), "by_source": Counter(r["source"].split("-")[0] if r["source"].startswith("wipe") else r["source"] for r in A),
                      "randomized_borderland": sum(r.get("surface") == "randomized" for r in A)}))


if __name__ == "__main__":
    main()
