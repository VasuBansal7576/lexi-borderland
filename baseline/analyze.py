"""Post-run inspection only. Never feeds evaluator answers back to the model."""
import json
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/model-baseline"


def lines(path):
    return [json.loads(s) for s in path.read_text().splitlines()]


def audit(folder):
    report = json.loads((folder / "report.json").read_text())
    requests, responses = lines(folder / "requests.jsonl"), lines(folder / "responses.jsonl")
    actions = lines(folder / "actions.jsonl")
    assert len(actions) == len(responses) == report["model_calls"]
    wiped_indices = {w["after_request"] + 1 for w in report["wipes"]}
    for i, req in enumerate(requests):
        assert hashlib.sha256(req["request"]["messages"][0]["content"].encode()).hexdigest() == report["prompt_sha256"]
        if i and i not in wiped_indices:
            assert req["public_frame"] == actions[i-1]["output"]
        restored = None
        for message in req["request"]["messages"]:
            if message["role"] != "user":
                continue
            wire = json.loads(message["content"])
            if "observation" in wire:
                restored = wire["observation"]
            else:
                assert restored is not None
                restored.update(wire["observation_update"])
                for key in wire["deleted"]:
                    del restored[key]
        assert restored == req["public_frame"]["observation"]
        assert not set(restored) & {"world", "reward", "score", "integrity", "seed", "fingerprint"}
        assert req["request"]["temperature"] == 0
        if i < len(actions):
            assert actions[i]["raw"] == responses[i]["choices"][0]["message"]["content"]
            assert responses[i]["model"] == "tiny-aya-global-q4_k_m"
            assert responses[i]["usage"]["completion_tokens"] > 0
            if actions[i]["action"]:
                decoded = json.loads(actions[i]["raw"])
                assert actions[i]["action"] == {"tool": decoded["tool"], "args": decoded["args"]}
    for wipe in report["wipes"]:
        assert wipe["old_pid"] != wipe["new_pid"]
        assert len(wipe["notebook"]) == 8
        assert all(len(s) <= 96 for s in wipe["notebook"])
        idx = wipe["after_request"] + 1
        if idx < len(requests):
            req = requests[idx]
            assert len(req["request"]["messages"]) == 2
            assert req["server_pid"] == wipe["new_pid"]
            assert req["public_frame"] == wipe["fresh_frame"]
            if idx < len(responses):
                assert responses[idx]["usage"]["prompt_tokens_details"]["cached_tokens"] == 0
    world = json.loads((folder / "manifest.json").read_text())
    tool_counts = Counter(row["action"].get("tool", "invalid JSON") for row in actions)
    last = actions[-1] if actions else None
    try:
        last_rationale = json.loads(last["raw"]).get("reason") if last else None
    except (ValueError, AttributeError):
        last_rationale = None
    inspected = [row["action"]["args"]["record_id"] for row in actions
                 if row["action"].get("tool") == "read_record" and row["output"]["ok"]]
    facts = {"name": report["name"], "assisted": report["assisted_prefix"],
             "notebook_probe": report["notebook_probe"], "start_room": report["start_room"],
             "last_room": report["last_room"], "outcome": report["reason"],
             "rooms_cleared_by_model": report["rooms_cleared_by_model"],
             "rooms_completed_from_room_entry": [] if report["notebook_probe"] else report["rooms_cleared_by_model"],
             "model_calls": report["model_calls"], "tool_counts": dict(tool_counts),
             "records_read_by_model": inspected,
             "protocol_errors": sum(not r["output"]["ok"] for r in actions),
             "last_public_state": last["output"]["observation"] if last else None,
             "completion_tokens": report["completion_tokens"],
             "maximum_prompt_tokens": max((r["usage"]["prompt_tokens"] for r in responses), default=0),
             "actual_wipes": len(report["wipes"]), "last_action": last["action"] if last else None,
             "last_rationale": last_rationale,
             "errors": report["errors"], "transport_audit_passed": True,
             "exact_environment_replay": report["exact_environment_replay"],
             "artifact": str(folder.relative_to(BASE))}
    if report["reason"] == "seal_lock":
        facts["evaluator_only_lock_answer"] = {"route": world["phase"] % 2, "badge": world["sigma"] ^ 1}
        facts["model_notebook"] = report["wipes"][-1]["notebook"] if report["wipes"] else requests[0]["public_frame"]["observation"]["notebook"]
    if report["reason"] == "unsafe_door" and last:
        before = requests[-1]["public_frame"]["observation"]
        sector = (world["phase"] + before["bank"] + before["pulse"]) % 4
        facts["evaluator_only_safe_door"] = "ABCD"[world["k"].index(sector)]
    return facts


def main():
    reports = [audit(p.parent) for p in sorted(BASE.glob("*-v1/*/report.json"))]
    result = {"model": json.loads((ROOT / "models/tiny-aya-global/provenance.json").read_text()),
              "runs": reports,
              "unassisted_escapes": sum(r["outcome"] == "legal_escape" for r in reports if not r["assisted"]),
              "unassisted_attempts": sum(not r["assisted"] for r in reports),
              "all_transport_checks_passed": True}
    (BASE / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
