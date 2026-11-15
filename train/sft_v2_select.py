"""SFT v2 data: continue from the v1 adapter on a set weighted to computed decisions, every derivation re-checked.
Gate (all must hold, else no file is written): every derivation's computed values equal the action args (100%),
room-4 operands are literally present in the prompt (notebook + observation), unlock pairs are balanced,
targets fit the generation cap, prompts fit the context."""
import json, random, re, sys
from collections import Counter, defaultdict

SRC, OUT = sys.argv[1], sys.argv[2]
QUOTA = {"unlock": 200, "choose_door": 200, "validate_registry": 150, "submit_bid": 150}
NOTEBOOK_R3, OTHER_PER_BUCKET = 150, 14
rng = random.Random(7)
buckets = defaultdict(list)
for line in open(SRC):
    r = json.loads(line)
    t = json.loads(r["messages"][-1]["content"])
    key = t["tool"] if t["tool"] in QUOTA else ("nb3" if (t["tool"] == "notebook_write" and r["room"] == 3) else (r["room"], t["tool"]))
    buckets[key].append(r)


def check(r):
    t = json.loads(r["messages"][-1]["content"]); a, why = t["args"], t["reason"]
    prompt = r["messages"][1]["content"]
    if t["tool"] == "unlock":
        m = re.search(r"route=.*=(\d)\. badge=.*=(\d)\.$", why); assert m, why
        assert (int(m[1]), int(m[2])) == (a["route"], a["badge"]), (why, a)
        p = int(re.search(r"phase=(\d)", why)[1]); s = int(re.search(r"sigma\)=(\d)", why)[1])
        assert f'"phase":{p}' in prompt.replace(" ", "") or f'\\"phase\\":{p}' in prompt, "phase not in prompt"
        assert f'"sigma":{s}' in prompt.replace(" ", "") or f'\\"sigma\\":{s}' in prompt, "sigma not in prompt"
        return (a["route"], a["badge"])
    if t["tool"] == "choose_door":
        m = re.search(r"Glyph at sector \d is ([A-D])\.$", why); assert m and m[1] == a["door_id"], (why, a)
    if t["tool"] == "validate_registry":
        m = re.search(r"-> (true|false)\.$", why); assert m and (m[1] == "true") == a["response"], (why, a)
    if t["tool"] == "submit_bid":
        m = re.search(r"-> bid=(\d+)\.$", why); assert m and int(m[1]) == a["value"], (why, a)
    if t["tool"] in QUOTA:
        assert "Apply the public rules" not in why, "derivation missing"
    return None


picked = []
for k, n in QUOTA.items():
    items = buckets[k]; rng.shuffle(items)
    if k == "unlock":  # balance the four (route, badge) pairs
        by = defaultdict(list)
        for r in items: by[check(r)].append(r)
        m = min(len(v) for v in by.values()); per = min(n // 4, m)
        items = [r for v in by.values() for r in v[:per]]
    picked += items[:n]
nb = buckets["nb3"]; rng.shuffle(nb); picked += nb[:NOTEBOOK_R3]
for k, items in buckets.items():
    if isinstance(k, tuple):
        rng.shuffle(items); picked += items[:OTHER_PER_BUCKET]
for r in picked:
    check(r)
tlen = max(len(r["messages"][-1]["content"]) for r in picked)
plen = max(sum(len(m["content"]) for m in r["messages"]) for r in picked)
assert tlen / 3.0 < 300, f"target too long {tlen} chars"
assert plen / 3.06 < 6144, f"prompt too long {plen} chars"
rng.shuffle(picked)
pairs = Counter(check(r) for r in picked if json.loads(r["messages"][-1]["content"])["tool"] == "unlock")
with open(OUT, "w") as f:
    for r in picked: f.write(json.dumps(r, separators=(",", ":")) + "\n")
print(json.dumps({"rows": len(picked), "by_tool": Counter(json.loads(r["messages"][-1]["content"])["tool"] for r in picked).most_common(),
                  "unlock_pairs": {str(k): v for k, v in pairs.items()}, "max_target_chars": tlen, "max_total_chars": plen,
                  "worlds": len({r["world"] for r in picked})}, indent=0))
