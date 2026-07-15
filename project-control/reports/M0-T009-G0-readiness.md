# G0 Readiness — M0-T009 Canonical contracts v1

Date: 2026-07-15. Recorded by orchestrator.

- Objective unambiguous: yes — v1 contracts for property profile, source fact/provenance, coverage status, analysis state (PRD 32.3/32.1/9/12) + remediation of M0-T004 G3 defects D1/D2/D3 and doc defects D4/D5 (packet `project-control/tasks/M0-T009.json`).
- Dependencies: M0-T004 accepted 2026-07-15 (all gates). No mocks needed.
- File scope exclusive: yes — packages/contracts/**, .github/scripts/validate_contracts.py, apps/web/src/lib/disclaimer.ts, README.md. Verified zero overlap with the only other active writing task (M0-T006 rework: docs/adr/**, render.yaml, docs/DEPLOYMENT_AND_ROLLBACK.md, .github/workflows/ci.yml). ci.yml explicitly excluded from M0-T009.
- Inputs/outputs defined: yes (packet).
- Acceptance scenarios: S1–S6 defined (normal, provenance-completeness, real-data enums, boundary, invalid-input, regression).
- Source documentation available: PRD sections in repo; M0-T002 research in docs/research/ for D2 enum grounding.
- Credentials: none required (schema/doc work only).
- Gates assigned: G0, G2, G3, G4, G5; reviewers code-reviewer, qa-engineer, security-reviewer (all distinct from producer backend-engineer).
- Execution location and disk: producer runs in a Claude-managed isolated worktree on the owner PC; text-only edits, expected < 1 MB; no installs, no datasets; validation via existing local Python (stdlib + already-present jsonschema/pyyaml if available — producer must check and fall back to CI for anything requiring installs). Cleanup: worktree removed after merge; ≥ 4 GB free preserved.
- Durable storage: all outputs committed to GitHub via orchestrator integration.

G0 result: PASS — task may proceed.
