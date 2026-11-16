"""Assert the A/B pair is identical except the reason field: same ids/order, prompts, actions/answers; aya and
gsm8k byte-identical; every '(user text)' grounding claim true; every arithmetic step in A reasons correct."""
import json, re, sys
from collections import Counter


def load(p): return [json.loads(l) for l in open(p)]


def dictobj(c):
    try:
        t = json.loads(c); return t if isinstance(t, dict) else None
    except ValueError:
        return None


def main(pa, pb):
    A, B = load(pa), load(pb)
    assert [r["id"] for r in A] == [r["id"] for r in B], "ids/order differ"
    stats = Counter()
    for a, b in zip(A, B):
        assert a["messages"][:-1] == b["messages"][:-1], ("prompt differs", a["id"])
        ca, cb = a["messages"][-1]["content"], b["messages"][-1]["content"]
        if a.get("keep_reason"):
            assert ca == cb, ("keep_reason row differs", a["id"]); stats["identical_rows"] += 1; why = ""
        else:
            ta, tb = dictobj(ca), dictobj(cb); assert ta is not None and tb is not None, a["id"]
            k = list(ta)[0]
            assert list(ta) == list(tb) and tb[k] == "" and {x: y for x, y in ta.items() if x != k} == {x: y for x, y in tb.items() if x != k}, a["id"]
            why = ta[k] or ""; stats["paired_rows"] += 1
        if a["source"] == "tools":
            q = a["messages"][-2]["content"].lower()
            for grp in re.findall(r'<- ((?:"[^"]*"(?:, )?)+) \(user text\)', why):
                for v in re.findall(r'"([^"]*)"', grp):
                    stats["grounding_claims"] += 1; assert v.lower() in q, (a["id"], v)
        for expr, val in re.findall(r"=([\d+\-*/ ()]+?)=(-?\d+)\b", why):
            if re.search(r"\d[+\-*/]\d", expr.replace(" ", "")):
                stats["arith_steps"] += 1; assert eval(expr) == int(val), (a["id"], expr, val)
    print(json.dumps(dict(stats)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
