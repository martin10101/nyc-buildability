# M0-T005-R1 — G0 Definition-of-Ready Review

- **Task:** M0-T005-R1 — Secret scanner hardening (G3/G5 defect burn-down)
- **Gate:** G0
- **Reviewer:** orchestrator
- **Date:** 2026-07-16
- **Verdict:** PASS

| G0 criterion | Evidence |
|---|---|
| Objective unambiguous | 11 numbered fix items in the packet objective, each traced to a G3 defect (D1–D7) or G5 finding (M0-T005 F1, M0-T009 F2/F3, RefResolver item 10) with file:line references in the input reports |
| Dependencies accepted | M0-T005 accepted 2026-07-16; M0-T009 accepted 2026-07-16 (its G5 findings folded in as items 10–11) |
| File scope exclusive | `.github/scripts/secret_scan.py`, `.github/scripts/validate_contracts.py`, `docs/SECRETS_POLICY.md` — disjoint from M1-T002 (services/api/**). No other active task touches these files. Workflows explicitly forbidden |
| Inputs and outputs defined | Packet lists the two G3/G5 review reports, policy §2, and current scripts as inputs; hardened scripts + one policy sentence + producer report as outputs |
| Acceptance scenarios exist | S1–S6 (normal, planted-fixture detection incl. UTF-16, pragma boundary, .env.example ambiguity, failure exit codes/injection, 9-class regression) |
| Source documentation available | project-control/reports/M0-T005-G3-review.md and M0-T005-G5-security-review.md in repo with desk-test reproductions |
| Credentials | None needed (all fixtures are fake values) |
| Gates assigned | G0/G2/G3/G5; producer backend-engineer; reviewers code-reviewer + security-reviewer |
| Execution location + disk | Worktree `.claude/worktrees/M0-T005-R1`; pure-stdlib Python scripts, KB-scale; scanner run takes <1s locally; free disk 2.27 GB (below floor) — no installs, no large fixtures |
| Cleanup / durable routing | Worktree + branch removed after acceptance; durable output is committed source only; temporary planted-fixture files must be created under the worktree and removed by test teardown |

Note: G5 condition from M0-T005 stands — this task must land before any real credential enters the repository or M0 exits.
