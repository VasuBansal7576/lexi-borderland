"""Finite checks of the proposed design's subcontracts, NOT an environment test.

Run from the project root with Python's standard library only.
No model, network, credentials or files outside this project are used by this script.
"""

from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[1]


def check_lock():
    bits = list(product(range(2), repeat=2))
    best = Fraction(0)
    # A deterministic memoryless policy maps the four visible challenges to
    # one of four actions. Randomized policies are mixtures of these policies.
    for policy in product(bits, repeat=4):
        correct = 0
        for observation_index, (pulse, challenge) in enumerate(bits):
            for phase_parity, sigma in bits:
                expected = (phase_parity ^ pulse, sigma ^ challenge)
                correct += policy[observation_index] == expected
        best = max(best, Fraction(correct, 16))
    assert best == Fraction(1, 4)
    for pulse, challenge in bits:
        for phase_parity, sigma in bits:
            action = (phase_parity ^ pulse, sigma ^ challenge)
            assert action != ((1 - phase_parity) ^ pulse, sigma ^ challenge)
            assert action != (phase_parity ^ pulse, (1 - sigma) ^ challenge)
    return {
        "deterministic_policies_enumerated": 256,
        "balanced_cases_per_policy": 16,
        "maximum_memoryless_success": str(best),
        "two_bit_memory_success": "1",
        "scope": "Algebraic lock only; see implementation tests for observation-interface checks.",
    }


def check_rewards():
    # Units are exact fractions, avoiding a float rounding claim about zero.
    partial_values = [
        Fraction(5 * cleared + milestones, 100)
        for cleared in range(7)
        for milestones in range(3)
    ]
    assert max(partial_values) == Fraction(32, 100)
    successful_values = [
        Fraction(35, 100) + Fraction(60, 100)
        + Fraction(5, 100) * (1 - Fraction(calls, 160))
        for calls in range(161)
    ]
    assert min(successful_values) == Fraction(95, 100)
    assert max(successful_values) == 1
    assert min(successful_values) > max(partial_values)
    for paid in partial_values:
        clawback = -paid
        assert paid + clawback == 0
    # Ledger flags are sets: repeated event delivery cannot pay again.
    events = [(i, kind) for i in range(7) for kind in ("m1", "m2", "clear")]
    seen = set()
    paid = Fraction(0)
    for event in events + events:
        if event not in seen:
            paid += Fraction(3 if event[1] == "clear" else 1, 100)
            seen.add(event)
    assert paid == Fraction(35, 100)
    return {
        "max_ordinary_failure_score": str(max(partial_values)),
        "minimum_success_score": str(min(successful_values)),
        "maximum_success_score": str(max(successful_values)),
        "duplicate_milestone_payment": "0",
        "forbidden_tool_total_after_clawback": "0",
        "scope": "Proposed formula and ledger algebra; trainer integration untested.",
    }


def opponent_bid(mode, previous, offset, phase, round_index):
    if mode == "echo":
        return (previous + offset) % 21
    if mode == "mirror":
        return (20 - previous + offset) % 21
    return (3 * round_index + phase + offset) % 21


def round_win(a, b, c, numerator):
    target = numerator * (a + b + c) // 15
    return int(abs(a - target) < min(abs(b - target), abs(c - target)))


def check_balance():
    cases = []
    offset_pairs = [(0, 4), (2, 5), (1, 13), (8, 16)]
    for mode, phase, numerator, offsets in product(
        ("echo", "mirror", "phase-cycle"), range(4), (3, 4), offset_pairs
    ):
        def wins(round_index, previous, a):
            b, c = [opponent_bid(mode, previous, o, phase, round_index) for o in offsets]
            return round_win(a, b, c, numerator)

        @lru_cache(None)
        def solve(round_index, previous):
            if round_index == 3:
                return 0, ()
            candidates = []
            for a in range(21):
                rest, sequence = solve(round_index + 1, a)
                candidates.append((wins(round_index, previous, a) + rest, (a,) + sequence))
            return max(candidates, key=lambda item: (item[0], tuple(-x for x in item[1])))

        max_wins, sequence = solve(0, 10)
        constant_wins = []
        for a in range(21):
            constant_wins.append(sum(wins(r, 10 if r == 0 else a, a) for r in range(3)))
        cases.append({
            "mode": mode, "phase": phase, "q": f"{numerator}/5",
            "offsets": offsets, "maximum_wins": max_wins,
            "winning_sequence": sequence, "constant_wins": constant_wins,
        })
    accepted = [c for c in cases if c["maximum_wins"] >= 2]
    assert accepted, "No tested Balance instance is feasible."
    assert {c["mode"] for c in accepted} == {"echo", "mirror", "phase-cycle"}
    universal_constants = [a for a in range(21) if all(c["constant_wins"][a] >= 2 for c in accepted)]
    assert not universal_constants, f"Universal repeated bid shortcut: {universal_constants}"
    universal_sequences = []
    for sequence in product(range(21), repeat=3):
        for case in accepted:
            previous = 10
            total = 0
            numerator = int(case["q"].split("/")[0])
            for r, a in enumerate(sequence):
                b, c = [opponent_bid(case["mode"], previous, o, case["phase"], r) for o in case["offsets"]]
                total += round_win(a, b, c, numerator)
                previous = a
            if total < 2:
                break
        else:
            universal_sequences.append(sequence)
    assert not universal_sequences, f"Universal fixed-sequence shortcut: {universal_sequences}"
    return {
        "candidate_parameter_sets": len(cases),
        "locally_feasible_parameter_sets": len(accepted),
        "infeasible_parameter_sets": len(cases) - len(accepted),
        "universal_successful_constant_bids": universal_constants,
        "fixed_sequences_checked": 21 ** 3,
        "universal_successful_fixed_sequences": universal_sequences,
        "witnesses": [{k: v for k, v in c.items() if k != "constant_wins"} for c in accepted[:4]],
        "scope": "Exact three-round local game, not full-world or arena feasibility.",
    }


def check_battle():
    count = 0
    for left, right, polarity in product(range(100, 3100, 100), range(100, 3100, 100), (-1, 1)):
        if left == right:
            continue
        left_wins = left > right if polarity == 1 else left < right
        assert left_wins != (left > right if polarity == -1 else left < right)
        loser = right if left_wins else left
        transfer = min(1000, loser)
        new_left = left + transfer if left_wins else left - transfer
        new_right = right - transfer if left_wins else right + transfer
        assert new_left >= 0 and new_right >= 0
        assert new_left + new_right == left + right
        count += 1
    return {
        "unequal_positive_group_cases": count,
        "point_conservation": True,
        "polarity_reverses_winner": True,
        "scope": "Single battle totals; see implementation tests and certificates for full arena checks.",
    }


def check_notebook():
    sample = [
        "K:A0,B2,C3,D1;phi=1;clock=district-wall+1;src=e1,e2",
        "delta0=+1;aux before main;power indicator=delta0;src=e7",
        "sigma=0;Iris=I;Nox=N;Vale=V;Sol=S;authorized=I,N,V,S;src=e12",
        "rivals=mirror;offsets=2,5,8;initial_bid=10;src=e15",
        "controller access=I,N;V=transit;S=registry;src=e13",
        "incident:clock corrected;N at west relay;I at east;src=e14,e16",
        "R4+later: replace with actual route/resource strategy when observed",
        "R6+later: record authenticated delta change and exact activation round",
    ]
    assert len(sample) == 8
    assert all(all(32 <= ord(ch) <= 126 for ch in line) for line in sample)
    assert all(len(line.encode("ascii")) <= 96 for line in sample)
    size = sum(len(line.encode("ascii")) for line in sample)
    assert size <= 768
    return {
        "illustrative_note_bytes": size,
        "maximum_line_bytes": max(map(len, sample)),
        "budget_bytes": 768,
        "scope": "Capacity example only; values are illustrative, not a solved seven-room fixture.",
    }


def check_links():
    count = 0
    for path in ROOT.joinpath("wiki").glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            relative = target.split("#", 1)[0]
            destination = (path.parent / relative).resolve()
            assert destination.is_relative_to(ROOT), f"Link outside folder: {path}: {target}"
            assert destination.exists(), f"Broken file link: {path}: {target}"
            count += 1
    return {"local_file_links_checked": count, "scope": "File targets, not Markdown fragment anchors."}


def main():
    results = {
        "status": "limited_design_checks_passed",
        "environment_implementation_checked_by_this_script": False,
        "model_training_run": False,
        "lock": check_lock(),
        "rewards": check_rewards(),
        "balance": check_balance(),
        "battle": check_battle(),
        "notebook": check_notebook(),
        "links": check_links(),
    }
    output = ROOT / "design_checks" / "results.json"
    output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
