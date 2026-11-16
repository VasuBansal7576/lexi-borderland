"""Procedural memory-wipe task families (generalisation data + unseen transfer evaluation).

Protocol (identical for every family, surface randomised per episode):
  phase 1: a catalog of documents; the agent reads them with a read tool (some are retired/distractors), then writes
           at most 4 note lines (<=96 chars) with a notes tool. Then its context is wiped.
  phase 2: the agent sees only its notes and a goal, and must call the family's final tool with computed arguments.
Every episode has a solver (exact answer + an explicit derivation) and a counterfactual twin (one fact changed ->
answer changes). Train families: ledger, schedule, lookup, logs, config, budget. Held-out: inventory, access."""
import json, random

TRAIN_FAMILIES = ["ledger", "schedule", "lookup", "logs", "config", "budget"]
HELDOUT_FAMILIES = ["inventory", "access"]

READ_NAMES = ["read_doc", "open_file", "fetch_record", "view_page", "load_note", "get_document"]
NOTE_NAMES = ["write_notes", "save_memo", "store_notes", "record_notes", "keep_notes"]
SCHEMAS = [("reason", "tool", "args"), ("thought", "action", "input"), ("why", "call", "params"), ("rationale", "op", "arguments")]
NAMES = ["Asha", "Bruno", "Chen", "Dara", "Eli", "Fatima", "Goran", "Hana", "Ivo", "Juno", "Kofi", "Lena", "Mateo", "Nia",
         "Omar", "Priya", "Quinn", "Rosa", "Sven", "Tara"]
SERVICES = ["auth", "billing", "search", "cart", "mailer", "gateway", "reports", "sync"]
DEPTS = ["ops", "design", "legal", "sales", "research", "support", "hr", "finance"]
ITEMS = ["bolt", "valve", "sensor", "cable", "filter", "gear", "lens", "pump", "relay", "spring"]
BUILDINGS = ["North Hall", "Dock 4", "Annex B", "Tower 2", "Lab West", "Depot 7"]


def m(rng, xs):
    return rng.choice(xs)


# ---------------------------------------------------------------- families: each returns a spec dict
def fam_ledger(rng, twin=0):
    acct = f"AC-{rng.randint(100, 999)}"
    opening = rng.randint(200, 900)
    txs = [rng.choice([-1, 1]) * rng.randint(10, 150) for _ in range(rng.randint(3, 4))]
    if twin: txs[0] += 37 if txs[0] < 0 else -37
    reserve = rng.choice([50, 100, 150])
    docs = [{"kind": "opening", "account": acct, "opening_balance": opening},
            {"kind": "transactions", "account": acct, "status": "posted", "amounts": txs},
            {"kind": "transactions", "account": acct, "status": "voided", "amounts": [rng.randint(10, 99)]},
            {"kind": "policy", "text": f"Keep a reserve of {reserve} in the account."}]
    bal = opening + sum(txs); pay = bal - reserve
    deriv = (f"balance={opening}" + "".join(f"{'+' if t >= 0 else ''}{t}" for t in txs) + f"={bal}; "
             f"transfer=balance-reserve={bal}-{reserve}={pay}")
    notes = [f"acct {acct} opening {opening}", "posted " + ",".join(map(str, txs)) + " (voided ignored)", f"reserve {reserve}"]
    return {"goal": f"Transfer the largest amount you can out of {acct} while keeping the policy reserve.",
            "final": ("transfer", {"account": acct, "amount": pay}), "docs": docs, "notes": notes, "deriv": deriv}


def fam_schedule(rng, twin=0):
    people = rng.sample(NAMES, 3); dur = rng.choice([1, 2])
    busy = {p: sorted(rng.sample(range(9, 17), rng.randint(2, 4))) for p in people}
    if twin:
        busy[people[0]] = sorted(set(busy[people[0]]) ^ {rng.randint(9, 16)}) or [9]
    def free(h): return all(h2 not in busy[p] for p in people for h2 in range(h, h + dur))
    slot = next((h for h in range(9, 18 - dur) if free(h)), None)
    if slot is None:
        return fam_schedule(rng, twin)
    docs = [{"kind": "calendar", "person": p, "busy_hours": busy[p]} for p in people] + \
           [{"kind": "calendar", "person": people[1], "busy_hours": [9, 10], "status": "outdated"},
            {"kind": "request", "duration_hours": dur, "window": "9-17"}]
    tried = []
    for h in range(9, slot + 1):
        bad = [f"{p}@{h2}" for p in people for h2 in range(h, h + dur) if h2 in busy[p]]
        tried.append(f"{h}:{'free' if not bad else 'busy ' + bad[0]}")
    deriv = f"duration {dur}h; check starts " + ", ".join(tried) + f" -> earliest common start {slot}"
    notes = [f"dur {dur}"] + [f"{p} busy " + ",".join(map(str, busy[p])) for p in people]
    return {"goal": f"Book the earliest {dur}-hour meeting for {', '.join(people)} between 9 and 17.",
            "final": ("book", {"start_hour": slot, "attendees": people}), "docs": docs, "notes": notes, "deriv": deriv}


def fam_lookup(rng, twin=0):
    item = f"{m(rng, ITEMS)}-{rng.randint(10, 99)}"; owner, old = rng.sample(NAMES, 2)
    team = m(rng, DEPTS); bld = rng.sample(BUILDINGS, 2)
    if twin: bld = bld[::-1]
    docs = [{"kind": "registry", "item": item, "owner": owner}, {"kind": "registry", "item": item, "owner": old, "status": "retired"},
            {"kind": "staff", "person": owner, "team": team}, {"kind": "sites", "team": team, "building": bld[0]},
            {"kind": "sites", "team": "other", "building": bld[1]}]
    deriv = f"{item} owner {owner} (current, not retired {old}) -> team {team} -> building {bld[0]}"
    notes = [f"{item} owner {owner}", f"{owner} team {team}", f"{team} at {bld[0]}"]
    return {"goal": f"Deliver {item} to the building of its current owner's team.",
            "final": ("deliver", {"item": item, "building": bld[0]}), "docs": docs, "notes": notes, "deriv": deriv}


def fam_logs(rng, twin=0):
    deploy = rng.randint(10, 40)
    lines = []
    for t in sorted(rng.sample(range(1, 60), 7)):
        lines.append({"t": t, "service": m(rng, SERVICES), "level": rng.choice(["INFO", "WARN", "ERROR"]), "code": rng.randint(100, 599)})
    after = [l for l in lines if l["t"] > deploy and l["level"] == "ERROR"]
    if not after:
        lines.append({"t": deploy + rng.randint(1, 15), "service": m(rng, SERVICES), "level": "ERROR", "code": rng.randint(500, 599)})
        lines.sort(key=lambda l: l["t"])
    if twin: deploy = max(1, deploy - 7)
    first = next(l for l in lines if l["t"] > deploy and l["level"] == "ERROR")
    docs = [{"kind": "deploy", "time": deploy}, {"kind": "log", "lines": lines[:4]}, {"kind": "log", "lines": lines[4:]},
            {"kind": "deploy", "time": deploy + 30, "status": "rolled back"}]
    deriv = f"deploy at t={deploy}; ERROR lines after it in time order: " + \
            ", ".join(f"t{l['t']} {l['service']} {l['code']}" for l in lines if l['t'] > deploy and l['level'] == 'ERROR') + \
            f" -> first is {first['service']} {first['code']}"
    errs = [l for l in lines if l["level"] == "ERROR" and l["t"] > deploy][:3]
    notes = [f"deploy t={deploy}", "errors after deploy " + ";".join(f"t{l['t']} {l['service']} {l['code']}" for l in errs)]
    return {"goal": "Open a ticket for the first ERROR logged after the (non-rolled-back) deploy.",
            "final": ("open_ticket", {"service": first["service"], "code": first["code"]}), "docs": docs, "notes": notes, "deriv": deriv}


def fam_config(rng, twin=0):
    key = m(rng, ["timeout", "cache_size", "retry_wait", "max_upload"])
    unit = {"timeout": ("s", "ms", 1000), "cache_size": ("MB", "KB", 1024), "retry_wait": ("min", "s", 60), "max_upload": ("GB", "MB", 1024)}[key]
    val = rng.randint(2, 30)
    if twin: val += rng.randint(1, 5)
    new_key = f"{key}_{unit[1].lower()}"
    docs = [{"kind": "old_config", key: f"{val}{unit[0]}"}, {"kind": "migration", "old_key": key, "new_key": new_key,
            "unit": unit[1], "rule": f"1 {unit[0]} = {unit[2]} {unit[1]}"}, {"kind": "old_config", key: f"{val + 9}{unit[0]}", "status": "superseded"}]
    nv = val * unit[2]
    deriv = f"{key}={val}{unit[0]}; {new_key}={val}*{unit[2]}={nv}{unit[1]}"
    notes = [f"{key} {val}{unit[0]} (current)", f"new key {new_key}, 1{unit[0]}={unit[2]}{unit[1]}"]
    return {"goal": "Write the current setting into the new config key in the new unit.",
            "final": ("set_config", {"key": new_key, "value": nv}), "docs": docs, "notes": notes, "deriv": deriv}


def fam_budget(rng, twin=0):
    depts = rng.sample(DEPTS, 3)
    budget = {d: rng.randint(5, 20) * 100 for d in depts}; spent = {d: rng.randint(1, budget[d] // 100) * 100 for d in depts}
    if twin: spent[depts[0]] = max(0, spent[depts[0]] - 300)
    cap = rng.choice([300, 500, 800])
    rem = {d: budget[d] - spent[d] for d in depts}
    best = max(depts, key=lambda d: (rem[d], d)); amt = min(cap, rem[best])
    docs = [{"kind": "budget", "dept": d, "budget": budget[d]} for d in depts] + \
           [{"kind": "spend", "dept": d, "spent": spent[d]} for d in depts] + [{"kind": "policy", "max_single_grant": cap}]
    deriv = "remaining " + ", ".join(f"{d} {budget[d]}-{spent[d]}={rem[d]}" for d in depts) + \
            f" -> most is {best} {rem[best]}; grant=min(cap {cap}, {rem[best]})={amt}"
    notes = [", ".join(f"{d} {budget[d]}/{spent[d]}" for d in depts), f"cap {cap}"]
    return {"goal": "Grant extra spend to the department with the most remaining budget, within the single-grant cap.",
            "final": ("grant", {"dept": best, "amount": amt}), "docs": docs, "notes": notes, "deriv": deriv}


def fam_inventory(rng, twin=0):
    item = m(rng, ITEMS); stock = rng.randint(20, 120); use = rng.randint(3, 12); lead = rng.randint(2, 9); safety = rng.randint(5, 30)
    if twin: use += 4
    need = use * lead + safety; qty = max(0, need - stock)
    docs = [{"kind": "stock", "item": item, "on_hand": stock}, {"kind": "usage", "item": item, "per_day": use},
            {"kind": "supplier", "item": item, "lead_days": lead}, {"kind": "policy", "safety_stock": safety},
            {"kind": "stock", "item": item, "on_hand": stock + 40, "status": "last month"}]
    deriv = f"need=per_day*lead+safety={use}*{lead}+{safety}={need}; order=need-on_hand={need}-{stock}={need - stock} -> {qty}"
    notes = [f"{item} on_hand {stock}", f"use {use}/day lead {lead}d safety {safety}"]
    return {"goal": f"Order enough {item} to cover lead time plus safety stock (order 0 if none needed).",
            "final": ("order", {"item": item, "quantity": qty}), "docs": docs, "notes": notes, "deriv": deriv}


def fam_access(rng, twin=0):
    user = m(rng, NAMES); roles = ["viewer", "editor", "admin", "auditor"]
    r = rng.sample(roles, 2); res = m(rng, ["payroll", "repo", "dashboard", "vault"])
    perms = {ro: rng.sample(["read", "write", "delete"], rng.randint(1, 2)) for ro in roles}
    want = rng.choice(["read", "write", "delete"])
    if twin: perms[r[0]] = [p for p in ["read", "write", "delete"] if p not in perms[r[0]]][:2] or ["read"]
    ok = any(want in perms[ro] for ro in r)
    docs = [{"kind": "user", "name": user, "roles": r}, {"kind": "matrix", "resource": res, "permissions": {ro: perms[ro] for ro in roles}},
            {"kind": "request", "user": user, "resource": res, "action": want}, {"kind": "user", "name": user, "roles": ["admin"], "status": "revoked"}]
    deriv = f"{user} roles {r[0]}:{perms[r[0]]}, {r[1]}:{perms[r[1]]}; {want} " + ("allowed" if ok else "not allowed") + f" -> {'grant' if ok else 'deny'}"
    notes = [f"{user} roles {r[0]},{r[1]}", f"{r[0]}={'/'.join(perms[r[0]])} {r[1]}={'/'.join(perms[r[1]])}", f"wants {want} on {res}"]
    return {"goal": f"Decide {user}'s pending access request.",
            "final": ("decide", {"user": user, "resource": res, "decision": "grant" if ok else "deny"}), "docs": docs, "notes": notes, "deriv": deriv}


def fam_bugfix(rng, twin=0):
    """EVAL-ONLY coding family (never trained on): failing test + stack trace + active/legacy configs + runbook rule;
    after the wipe the agent must patch the right file/key with the derived value."""
    svc = m(rng, ["billing", "auth", "search", "upload", "payments", "notify"])
    key = m(rng, ["timeout_ms", "max_retries", "pool_size", "batch_size", "cache_ttl"])
    step = rng.choice([5, 10, 25, 50]); cur = rng.randint(2, 20) * step
    minv = cur + rng.randint(1, 4 * step)
    if twin: minv += rng.randint(step, 3 * step)
    req = -(-minv // step) * step
    legacy_val = req + step * rng.randint(1, 3)
    docs = [{"kind": "ci_log", "text": f"FAILED tests/test_{svc}.py::test_{key} - AssertionError: expected {key} >= {minv}, got {cur}"},
            {"kind": "stack_trace", "text": f"File src/{svc}/client.py line {rng.randint(20, 300)}, in connect: cfg.{key} loaded from config/{svc}.yaml"},
            {"kind": "file", "path": f"config/{svc}.yaml", "content": f"{key}: {cur}"},
            {"kind": "file", "path": f"config/{svc}.legacy.yaml", "content": f"# DEPRECATED, not loaded\n{key}: {legacy_val}"},
            {"kind": "runbook", "text": f"{key} values must be multiples of {step}; always round up to the next multiple."}]
    deriv = (f"test needs {key}>={minv}; runbook: multiples of {step}, round up -> ceil({minv}/{step})*{step}={req}; "
             f"loaded file config/{svc}.yaml (legacy file is deprecated)")
    notes = [f"fix config/{svc}.yaml key {key}", f"need >={minv}, round up to x{step}"]
    return {"goal": "Fix the failing CI test by patching the configuration the service actually loads.",
            "final": ("patch_config", {"file": f"config/{svc}.yaml", "key": key, "value": req}), "docs": docs, "notes": notes, "deriv": deriv}


CODING_FAMILIES = ["bugfix"]
FAMILIES = {f.__name__[4:]: f for f in [fam_ledger, fam_schedule, fam_lookup, fam_logs, fam_config, fam_budget, fam_inventory, fam_access, fam_bugfix]}


# ---------------------------------------------------------------- episode -> surface-randomised conversation
def make_episode(family, seed, twin=0):
    spec = FAMILIES[family](random.Random(f"{family}|{seed}"), twin)   # twins share every draw; only the key fact moves
    srng = random.Random(f"surface|{family}|{seed}")
    read, note = m(srng, READ_NAMES), m(srng, NOTE_NAMES)
    fname, fargs = spec["final"]
    final_name = srng.choice([fname, fname + "_now", "do_" + fname, fname.replace("_", "")])
    schema = m(srng, SCHEMAS)
    ids = [f"{srng.choice('dfkmprx')}{srng.randint(100, 999)}" for _ in spec["docs"]]
    order = list(range(len(spec["docs"]))); srng.shuffle(order)
    docs = {ids[i]: spec["docs"][i] for i in order}
    keys = list(fargs)
    return {"family": family, "seed": seed, "twin": twin, "spec": spec, "read": read, "note": note, "final": final_name,
            "final_args": fargs, "schema": schema, "docs": docs, "catalog": list(docs)}


def system_prompt(ep, phase):
    r, t, a = ep["schema"]
    tools = [f'{ep["read"]}(doc_id) - read one document',
             f'{ep["note"]}(lines: list of <=4 strings, each <=96 chars) - save notes; afterwards your context is wiped and only these notes survive'] \
        if phase == 1 else [f'{ep["final"]}({", ".join(ep["final_args"])}) - perform the task']
    return (f"You are an agent. Reply with exactly one JSON object: {{\"{r}\": string, \"{t}\": tool name, \"{a}\": object}}.\n"
            "Tools:\n- " + "\n- ".join(tools) +
            "\nDocuments marked retired, outdated, voided, superseded, revoked, rolled back or 'last month' are not current.")


def user_prompt(ep, phase, history, notes=None):
    if phase == 1:
        return json.dumps({"task": "Gather what you will need later, then save notes. Later goal: " + ep["spec"]["goal"],
                           "catalog": ep["catalog"], "history": history}, separators=(",", ":"))
    return json.dumps({"task": ep["spec"]["goal"], "your_notes": notes or []}, separators=(",", ":"))


def teacher_steps(ep, plain=False):
    """[(messages, target_json)] for the full episode (phase 1 reads + notes, phase 2 final)."""
    r, t, a = ep["schema"]; out, hist = [], []
    unread = list(ep["catalog"])
    for d in ep["catalog"]:
        why = "" if plain else f"Evidence check: unread {','.join(unread)} -> {ep['read']} {d}."
        msgs = [{"role": "system", "content": system_prompt(ep, 1)}, {"role": "user", "content": user_prompt(ep, 1, list(hist))}]
        out.append((msgs, {r: why, t: ep["read"], a: {"doc_id": d}}))
        hist.append({"did": {ep["read"]: d}, "result": ep["docs"][d]}); unread.remove(d)
    notes = [n[:96] for n in ep["spec"]["notes"]][:4]
    why = "" if plain else "Evidence check: all read. Keep only current facts needed for the goal: " + " | ".join(notes)
    msgs = [{"role": "system", "content": system_prompt(ep, 1)}, {"role": "user", "content": user_prompt(ep, 1, list(hist))}]
    out.append((msgs, {r: why, t: ep["note"], a: {"lines": notes}}))
    msgs = [{"role": "system", "content": system_prompt(ep, 2)}, {"role": "user", "content": user_prompt(ep, 2, None, notes)}]
    why = "" if plain else "From my notes: " + ep["spec"]["deriv"] + "."
    out.append((msgs, {r: why, t: ep["final"], a: ep["final_args"]}))
    return out


def score_final(ep, obj):
    """True iff the final call names the right tool with exactly the right argument values."""
    r, t, a = ep["schema"]
    try:
        return obj[t] == ep["final"] and {k: (sorted(v) if isinstance(v, list) else v) for k, v in obj[a].items()} == \
            {k: (sorted(v) if isinstance(v, list) else v) for k, v in ep["final_args"].items()}
    except Exception:
        return False


def notes_cover_answer(ep):
    """Every string-valued answer argument must be present in the saved notes (numbers may be computed)."""
    text = " ".join(ep["spec"]["notes"])
    vals = [v for v in ep["final_args"].values()]
    flat = [x for v in vals for x in (v if isinstance(v, list) else [v])]
    return all(str(x) in text for x in flat if isinstance(x, str) and x not in ("grant", "deny"))


if __name__ == "__main__":
    import collections
    bad = collections.Counter(); changed = collections.Counter(); long = 0
    for fam in FAMILIES:
        for sd in range(300):
            e0, e1 = make_episode(fam, sd, 0), make_episode(fam, sd, 1)
            changed[fam] += e0["final_args"] != e1["final_args"]
            bad[fam] += not notes_cover_answer(e0)
            long += any(len(n) > 96 for n in e0["spec"]["notes"]) or len(e0["spec"]["notes"]) > 4
            assert score_final(e0, teacher_steps(e0)[-1][1])
    print("twin changes answer (of 300):", dict(changed)); print("notes miss a string answer:", dict(bad), "overlong notes", long)
