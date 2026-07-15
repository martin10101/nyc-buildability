# G0 Readiness — M0-T005 Secrets policy, .env.example, secret-scanning CI check

Date: 2026-07-15. Recorded by orchestrator.

- Objective unambiguous: yes (packet `project-control/tasks/M0-T005.json`).
- Dependencies: M0-T004 accepted 2026-07-15.
- File scope exclusive: yes — all outputs are NEW files (docs/SECRETS_POLICY.md, services/api/.env.example, apps/web/.env.example, .github/scripts/secret_scan.py, .github/workflows/secret-scan.yml). Verified disjoint from M0-T006 rework (ci.yml, ADRs, render.yaml, runbook) and M0-T009 (contracts, validate_contracts.py, disclaimer, root README).
- Inputs/outputs defined: yes; ADR-002 secret placement table + M0-T004 G5 report supply the secret inventory and pattern classes.
- Acceptance scenarios: S1–S6 defined (clean pass, seeded-credential fail, false-positive boundary, .env.example completeness, workflow security incl. SHA pinning, regression/runtime).
- Source documentation: in-repo; no external API claims required (repo-local stdlib scanner — deliberately no external/paid scanning action, so no license or credential dependency).
- Credentials: none required.
- Gates: G0, G2, G3, G5; reviewers security-reviewer + code-reviewer (distinct from producer backend-engineer).
- Execution location and disk: isolated worktree on owner PC; text-only, < 1 MB; no installs. Cleanup: worktree removed after merge; ≥ 4 GB free preserved.
- Durable storage: outputs committed to GitHub by orchestrator.

G0 result: PASS — task may proceed.
