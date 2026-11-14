# Public citation rules (2026-11-14)

Reason: a live Terra episode (artifacts/codex-terra-medium-v1) answered Room 3 correctly but failed an evidence-coverage check that the public rules never stated. Room 6 had the same hidden requirement.

Change (baseline/public_rules.txt only; env, generator, rewards unchanged):
- Room 3: certify_roster must cite the current clock_pairs record, the current glyph_constraints record, one signed probe result, one testimony and the registry record.
- Room 6: accuse must cite the Tribunal roles record, the relay activation receipt, the Balance incident receipt and the tamper record.
Difficulty is not reduced: both requirements were already enforced; they are now disclosed. The Room 6 roles record is read before the wipe, so its ID must survive in the 8-line notebook.

Solver: borderland/solver.py now cites exactly the five public Room-3 sources (tribunal_citations) instead of every ID it had collected, proving the public rule is sufficient.

Verification (real runs, copy outside the mount):
- 103/103 tests pass.
- Re-certification: 64/64 worlds, 16/16 families (artifacts/certification-v2); all 64 manifests byte-identical to certification-v1; all 64 certify_roster calls cite exactly 5 IDs.
- Independent audit (design_checks/audit_certificates.py, now pointing at v2): all passed, 4,604 steps, 640 citations.
