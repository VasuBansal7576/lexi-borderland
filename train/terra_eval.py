"""Frontier reference on the EXACT compact prompts Tiny Aya sees: GPT-6.1 Terra via the user's ChatGPT subscription
(native Codex bridge), room-start episodes on held-out worlds. Resumable: every model output is saved; each chunk
rebuilds episodes by deterministic replay of saved outputs, then continues until the time budget is spent."""
import argparse, json, os, time
from pathlib import Path
from .episodes import ROOT, manifests, load_world
from .evaluate import teacher_prefix, summarize
from .runner import Episode


def build(world_path, room):
    world = load_world(world_path)
    if room == 1:
        e = Episode(world, start_room=1); e.start_room, e.cap = 1, 46
        return e
    env, hist, frame, _ = teacher_prefix(world, room)
    return Episode(world, start_room=room, prefix=(env, hist, frame))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="artifacts/terra-compact-v1")
    p.add_argument("--worlds", type=int, default=2)
    p.add_argument("--rooms", default="1,2,3,4,5,6,7")
    p.add_argument("--seconds", type=int, default=120)
    p.add_argument("--max-calls", type=int, default=100)
    a = p.parse_args()
    out = ROOT / a.out; out.mkdir(parents=True, exist_ok=True)
    state_f = out / "state.json"
    if state_f.exists():
        state = json.loads(state_f.read_text())
    else:
        allw = [str(w.relative_to(ROOT)) for w in manifests("heldout")]
        fam0 = [w for w in allw if "/family-0000/" in w]  # one world (rooms 1-7) + its 3 lock twins at room 4
        eps = [{"world": fam0[0], "room": r, "raws": []} for r in range(1, 8)]
        eps += [{"world": w, "room": 4, "raws": []} for w in fam0[1:]]
        state = {"episodes": eps}
        state_f.write_text(json.dumps(state))
    from baseline.codex_subscription.bridge import Ledger, Client
    ledger = Ledger(str((out / "ledger.json").relative_to(ROOT)), live=True, max_calls=a.max_calls)
    client = Client(ledger, str((out / "calls").relative_to(ROOT)), live=True)
    client.calls = len([d for d in (out / "calls").glob("call-*")]) if (out / "calls").exists() else 0
    (out / "calls").mkdir(exist_ok=True)
    t0 = time.time()
    try:
        for ep in state["episodes"]:
            e = build(ROOT / ep["world"], ep["room"])
            for raw in ep["raws"]:          # deterministic replay of saved Terra outputs
                if e.done: break
                e.messages(); e.feed(raw)
            while not e.done and time.time() - t0 < a.seconds:
                raw = client.complete(e.messages())
                ep["raws"].append(raw); state_f.write_text(json.dumps(state))
                e.feed(raw)
            ep["result"] = {k: v for k, v in e.result().items() if k != "log"} if e.done else None
            state_f.write_text(json.dumps(state))
            if time.time() - t0 >= a.seconds:
                break
    finally:
        ledger.close()
    done = [ep["result"] for ep in state["episodes"] if ep.get("result")]
    print(json.dumps({"finished": len(done), "total": len(state["episodes"]), "calls": client.calls,
                      "summary": summarize(done) if done else None,
                      "by_room": {ep["room"]: (ep["result"] or {}).get("success") for ep in state["episodes"] if ep.get("result")}}))


if __name__ == "__main__":
    main()
