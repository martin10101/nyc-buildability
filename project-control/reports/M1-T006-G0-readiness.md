# M1-T006 — G0 definition-of-ready (orchestrator)

- **Task:** Property-profile contract v1.1 (additive) — coverage_status / data_completeness / reproducibility documentation + district provenance linkage
- **Date:** 2026-07-16
- **Reviewer:** orchestrator (G0 is the orchestrator's readiness gate)
- **Origin:** M1-T005 G3 adjudication #1 (mandatory before Priority 4) + defects D2 (additive keys undocumented) and D4 (district strings lack direct provenance linkage). Owner directive 2026-07-16 confirmed scope: coverage_status, data_completeness, reproducibility documentation, district-level provenance linkage, backward compatibility, valid+invalid fixtures, additive-change validation, complete provenance-reference testing.

## Checklist

| G0 item | Status |
| --- | --- |
| Objective unambiguous | YES — additive 1.1.0 of `property_profile.schema.json`; exact emitted shapes are ground-truthed in `services/api/app/profile/builder.py` (read-only input) |
| Dependencies accepted | YES — M1-T005 accepted (CP-0009); contract package accepted at M0-T004; no mocks needed |
| File scope exclusive | YES — no active tasks; scope `packages/contracts/**` + `.github/scripts/validate_contracts.py` (+ its tests); `services/**` forbidden |
| Inputs/outputs defined | YES — task packet `inputs`/`outputs` |
| Acceptance scenarios | YES — S1–S8 in packet (primary, backward-compat regression, boundary enums, missing/null, referential integrity, ground-truth conformance, suite regression, schema-sanity) |
| Source documentation | YES — PRD §12 (coverage/data-completeness), §9/§19 (provenance), §32.3 (canonical profile); M1-T005-G3-review.md; builder.py |
| Credentials | NONE required — no network, no secrets, no cloud resources |
| Gates assigned | G0 (this), G2 producer self-check, G3 independent code-reviewer, G4 CI after merge |
| Execution location / disk | Owner PC, KB-scale text edits + pytest; <1 MB; authoritative validation in GitHub Actions; no installs; cleanup: none beyond git-ignored pytest cache |
| Low-storage budget | WITHIN budget (disk is pre-existing below floor at ~2.27 GB; this task adds KBs; no heavy local work) |

## Explicit confirmations for the owner (directive 5)

- **No production deployment is introduced or modified** — `render.yaml`, workflows, and services are forbidden paths; this task changes JSON Schema files, fixtures, the fixture validator, and the contracts README only.
- **No credentials are introduced, required, or touched** — no secrets, tokens, or environment variables are involved; the secret scanner runs as usual in CI.

## Result

**G0 PASS** — task is ready; claiming for backend-engineer with worktree isolation per PROJECT_CONTROL_PROTOCOL (branch `task/M1-T006-contract-v1-1`, worktree `.claude/worktrees/M1-T006`).
