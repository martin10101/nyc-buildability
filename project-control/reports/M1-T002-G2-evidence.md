# M1-T002 — G2 producer self-check evidence (orchestrator-verified)

- **Task:** M1-T002 — PLUTO SODA connector
- **Gate:** G2 (producer self-check; permits submission only, does not accept)
- **Recorded by:** orchestrator (tool rejects reviewer==producer; producer = backend-engineer)
- **Date:** 2026-07-16
- **Producer evidence:** `.claude/worktrees/M1-T002` commit `9e22839` on `task/M1-T002-pluto-soda-connector`; full return packet at `project-control/reports/M1-T002-producer-report.md` (in the worktree commit).

## Producer-run commands (from the return packet, first-hand in producer sandbox)

```
python -m pytest tests -q                      → 87 passed in 0.79s
python .github/scripts/validate_contracts.py   → Checked 6 schema file(s); 0 failure(s). EXIT=0
python -m ruff check app/connectors tests/connectors → All checks passed!
```

## Orchestrator independent re-run (2026-07-16, worktree, local)

```
cd .claude/worktrees/M1-T002/services/api
python -m pytest tests -q            → 87 passed in 4.11s
python ../../.github/scripts/validate_contracts.py → Checked 6 schema file(s); 0 failure(s).
```

Both match the producer's claims. Scenarios S1–S8 all reported PASS with per-scenario evidence in the producer report; 19 live KB-scale fixture-capture requests logged with URLs/timestamps/bytes.

## Producer disclosures carried to reviewers

1. **S3a deviation:** packet's BBL `9999999999` violates the accepted contract pattern `^[1-5][0-9]{9}$` (borough 9) → connector rejects client-side; no-match path proven with live `5999999999` (F3b) instead. G1/G3 to confirm this adjudication.
2. `effective_date: null` on all facts; per-input vintages carried verbatim in `input_vintages` (no official per-field mapping exists).
3. Additive fact keys (`dataset_id`, `request_url`, `input_vintages`) rely on source_fact v1 allowing additional properties — schema untouched, validation green.
4. New API knowledge fixture-proven: Socrata checkbox columns are JSON booleans (`splitzone=true`, not `'Y'`); `bbl`/`appbbl` decimal-serialize in full records too; SODA omits nulls even under `$select`.
5. `jsonschema>=4.21,<5` added to services/api **dev extra only**; runtime is stdlib urllib (zero new runtime deps).
6. Temp capture dir `%TEMP%\pluto_cap` (~0.5 MB, outside repo) — producer's delete was denied; orchestrator cleanup pending.
