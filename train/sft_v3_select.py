"""SFT v3 data: v2's derivations plus room 1-3 inference written out (clock -> phase, glyph constraints -> sectors,
probe -> matrix -> switch targets, registry examples -> bit, testimony seals -> identities, tag rule -> forged).
Weighted to rooms 1-3 (where the model failed), with reading/questioning rows so it learns to gather evidence first.
Gate before writing: every derivation re-checked against the action (100%), unlock pairs balanced, lengths bounded."""
import json, random, re, sys
from collections import Counter, defaultdict

SRCS, OUT = sys.argv[1:-1], sys.argv[-1]
QUOTA = {(1, "read_record"): 200, (1, "choose_door"): 160, (1, "exit_room"): 70,
         (2, "read_record"): 40, (2, "probe"): 100, (2, "set_switch"): 130, (2, "energize"): 90, (2, "exit_room"): 50,
         (3, "read_record"): 60, (3, "question"): 60, (3, "validate_registry"): 100, (3, "certify_roster"): 130,
         (3, "notebook_write"): 120, (3, "exit_room"): 30, (4, "unlock"): 120, (5, "submit_bid"): 40}
OTHER = 10
ROOM4_OTHER = 20
LATE_OTHER = 25   # rooms 5-7 replay (v5 regressed room 6)
rng = random.Random(11)
buckets = defaultdict(list)
for src in SRCS:
    for line in open(src):
        r = json.loads(line); t = json.loads(r["messages"][-1]["content"])
        buckets[(r["room"], t["tool"])].append(r)


def check(r):
    t = json.loads(r["messages"][-1]["content"]); a, why, tool = t["args"], t["reason"], t["tool"]
    if tool == "unlock":
        m = re.search(r"route=.*=(\d)\. badge=.*=(\d)\.$", why); assert m and (int(m[1]), int(m[2])) == (a["route"], a["badge"]), why
        return (a["route"], a["badge"])
    if tool == "choose_door":
        m = re.search(r"Glyph at sector \d is ([A-D])\.$", why); assert m and m[1] == a["door_id"], why
    if tool == "probe":
        m = re.search(r"so probe ([A-D])\.$", why); assert m and m[1] == a["channel_id"], why
    if tool == "set_switch":
        m = re.search(r"Flip channel (\d) \(([A-D])\) to (true|false) -> switches", why); assert m and m[2] == a["channel_id"] and (m[3] == "true") == a["value"], why
        d = re.search(r"differs at channel\(s\) ([\d,]*)\.", why); assert d and (m[1] in d[1].split(",") or "forbidden, so" in why), why
        pairs = re.findall(r"ch(\d) (\d)(=|!=)(\d)", why); assert len(pairs) == 3 and all((a_ == b_) == (op == "=") for _, a_, op, b_ in pairs), why
        assert sorted(j for j, a_, op, b_ in pairs if op == "!=") == sorted(d[1].split(",")) if d[1] else True, why
    if tool == "energize":
        assert why.endswith(f"-> energize {a['bus_id']}."), why
        e = re.search(r"Compare now (\(\d,\d,\d\)) with target x=(\(\d,\d,\d\)): .* -> all equal", why); assert e and e[1] == e[2], why
    if tool == "validate_registry":
        m = re.search(r"-> (true|false)\.$", why); assert m and (m[1] == "true") == a["response"], why
    if tool == "certify_roster":
        got = dict(re.findall(r"(ash|birch|cedar|dusk): seal \d+ wall \d+ -> \([^)]*\)%4=(?:[-+\d]+=)?\d=([INVS])\.", why))
        assert got == a["mapping"], (got, a["mapping"])
        assert f"Forged {a['forged_credential_id']}." in why and why.count("FORGED") == 1, why
    if tool == "read_record" and r["room"] in (1, 2, 3):
        assert f"-> read {a['record_id']} before committing." in why and why.startswith("Evidence check: unread"), why
    if tool == "question":
        assert why.endswith(f"-> question {a['person_id']}."), why
    if tool == "notebook_write" and r["room"] == 3:
        bit = int(re.search(r"registry_bit=(\d) \(stored as sigma\)", why)[1])
        line = json.loads(a["lines"][1]); assert line["sigma"] == bit, (why, line)
        assert f"phase={json.loads(a['lines'][0])['phase']} " in why, why
        return ("sigma", bit)
    if r["room"] in (1, 2, 3) and tool not in ("read_record", "question"):
        assert why.startswith("Evidence check: all records read"), why
    if tool == "submit_bid":
        m = re.search(r"-> bid=(\d+)\.$", why); assert m and int(m[1]) == a["value"], why
    return None


picked = []
for key, items in buckets.items():
    rng.shuffle(items)
    n = QUOTA.get(key, ROOM4_OTHER if key[0] == 4 else (LATE_OTHER if key[0] >= 5 else OTHER))
    if key == (3, "notebook_write"):  # balance the registry bit the v2 chain always wrote as 0
        by = defaultdict(list)
        for r in items: by[check(r)].append(r)
        items = [r for v in zip(*[by[k] for k in sorted(by)]) for r in v]
    if key == (4, "unlock"):
        by = defaultdict(list)
        for r in items: by[check(r)].append(r)
        per = min(n // 4, min(len(v) for v in by.values())); items = [r for v in by.values() for r in v[:per]]
    picked += items[:n]
for r in picked:
    check(r)
tl = max(len(r["messages"][-1]["content"]) for r in picked)
pl = max(sum(len(m["content"]) for m in r["messages"]) for r in picked)
assert tl / 3.0 < 380, f"target too long {tl}"
assert pl / 3.06 < 6144, f"prompt too long {pl}"
rng.shuffle(picked)
with open(OUT, "w") as f:
    for r in picked: f.write(json.dumps(r, separators=(",", ":")) + "\n")
derived = sum(1 for r in picked if json.loads(r["messages"][-1]["content"])["tool"] in
              ("choose_door", "probe", "set_switch", "energize", "validate_registry", "certify_roster", "unlock", "submit_bid"))
nb = Counter(check(r) for r in picked if r["room"] == 3 and json.loads(r["messages"][-1]["content"])["tool"] == "notebook_write")
print(json.dumps({"notebook_bits": {str(k): v for k, v in nb.items()}, "rows": len(picked), "derived_rows_rechecked": derived, "by_room": dict(sorted(Counter(r["room"] for r in picked).items())),
                  "max_target_chars": tl, "max_total_chars": pl, "worlds": len({r["world"] for r in picked})}))
