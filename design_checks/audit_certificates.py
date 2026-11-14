"""Independent transport/provenance audit: stdlib only, no simulator imports."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "artifacts/certification-v2"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def read_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def audit(folder):
    report = json.loads((folder / "report.json").read_text())
    trace = read_lines(folder / "trace.jsonl")
    inputs = read_lines(folder / "policy-inputs.jsonl")
    outputs = read_lines(folder / "policy-outputs.jsonl")
    assert report["success"] and report["integrity"]
    assert report["rooms_cleared"] == list(range(1, 8))
    assert len(trace) == len(inputs) == len(outputs)
    for name, expected in report["implementation_hashes"].items():
        actual = hashlib.sha256(canonical((ROOT / "borderland" / name).read_text()).encode()).hexdigest()
        assert actual == expected, (name, "source changed since certificate")
    seal = report["seal"]
    assert seal["old_pid"] != seal["new_pid"]
    assert len(report["workers"]) == 2
    for worker in report["workers"]:
        assert worker["private_modules_loaded"] == []
        assert worker["private_read_probes_blocked"] == ["world.py", "00-IDEA.md"]
    assert len(seal["notebook"]) == 8
    assert all(len(s) <= 96 and all(32 <= ord(c) <= 126 for c in s) for s in seal["notebook"])
    assert sum(map(len, seal["notebook"])) <= 768
    delivered, coverage = set(), {}
    citation_count = 0
    for index, (row, frame, response) in enumerate(zip(trace, inputs, outputs)):
        assert set(frame) == {"ok", "result", "observation"}
        assert row["action"] == response["action"]
        action = row["action"]
        assert not action["tool"].startswith("maintenance.")
        assert action["tool"] in frame["observation"]["tools"]
        assert not set(frame["observation"]) & {"seed", "reward", "score", "fingerprint", "integrity", "private"}
        if index == seal["after_action"] + 1:
            assert frame == seal["fresh_input"]
            assert frame["result"] == {} and frame["observation"]["room"] == 4
            assert frame["observation"]["notebook"] == seal["notebook"]
        elif index:
            assert frame == trace[index - 1]["policy_output"]
        args = action["args"]
        cited = args.get("evidence_ids", [])
        if action["tool"] == "accept_amendment":
            cited = cited + [args["record_id"]]
        assert set(cited) <= delivered, (index, "unseen citation")
        citation_count += len(cited)
        result = row["policy_output"]["result"]
        if action["tool"] == "read_record" and "text" in result:
            rid = result["evidence_id"]
            seen = coverage.setdefault(rid, set())
            end = args["offset"] + len(result["text"])
            seen.update(range(args["offset"], end))
            if result["next_offset"] is None and seen == set(range(end)):
                delivered.add(rid)
        elif "evidence_id" in result:
            delivered.add(result["evidence_id"])
        if "receipt" in result:
            delivered.add(result["receipt"]["evidence_id"])
    prior_writes = [r["action"]["args"]["lines"] for r in trace[:seal["after_action"] + 1]
                    if r["action"]["tool"] == "notebook_write"]
    assert prior_writes[-1] == seal["notebook"]
    expected_units = 7 * 160 + 1920 + 160 - len(trace)
    assert report["score_units"] == expected_units
    assert sum(r["private"]["reward_delta_units"] for r in trace) == expected_units
    return {"steps": len(trace), "citations_checked": citation_count, "notebook_bytes": seal["bytes"]}


def main():
    summary = json.loads((CORPUS / "summary.json").read_text())
    rows = [audit(CORPUS / row["artifact"]) for row in summary["worlds"]]
    result = {"worlds_audited": len(rows), "all_passed": True,
              "steps_checked": sum(r["steps"] for r in rows),
              "citations_checked": sum(r["citations_checked"] for r in rows),
              "max_notebook_bytes": max(r["notebook_bytes"] for r in rows),
              "checks": ["current source hashes", "legal advertised tools", "no maintenance actions",
                         "delivered citation provenance", "exact policy transport",
                         "actual process restart", "exact eight-line transfer", "independent score arithmetic"]}
    (CORPUS / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
