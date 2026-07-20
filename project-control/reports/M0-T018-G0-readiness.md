# G0 Definition-of-Ready — M0-T018 (orchestrator, administrative)

**Task:** Backend production dependency parity and Python supply-chain enforcement
**Reviewer:** orchestrator (administrative) · **Result:** PASS · **Date:** 2026-07-20

G0 readiness confirmed before dispatch (owner directive 2026-07-20, P0):

1. **Objective unambiguous** — packet `project-control/tasks/M0-T018.json` with confirmed on-main defects (requirements.txt omits/mislabels runtime jsonschema; pyproject already lists it; Render installs requirements.txt while CI installs pyproject; starlette 0.46.2 = 7 findings; lazy jsonschema import at contract.py:231) and a verified-but-recheck target set.
2. **Dependencies** — none (foundational P0). Must be accepted before M0-T019, M2-T013, M2-T014.
3. **File scope exclusive** — requirements(.txt/.in/lock), pyproject metadata alignment, render.yaml install ref, .github/workflows/**, services/api/scripts/**, own report. No app/** behavior change permitted.
4. **Inputs/outputs defined** — packet inputs (current pins, pyproject, contract.py:231, render.yaml/ci.yml, a valid profile fixture) and the 7 required outcomes.
5. **Acceptance scenarios exist** — DP-S1..DP-S9 (parity, determinism, positive+negative exact-install proof, API suite on prod tree, pip-audit zero blocking, release-age, scheduled audit, regression).
6. **Required gates assigned** — G0, G2 (producer self-check), G3/G4 (code-reviewer), G5 (security-reviewer). Producer (cloud-architect) ≠ reviewers.
7. **Execution & disk** — GitHub Actions (clean Python 3.12) authoritative for the exact-install proof; bounded temp venvs cleaned up locally; low-storage policy honored.
8. **Cleanup/storage routing** — no durable artifacts on the owner PC; all output source in Git.

Ready-to-start criteria met. Dispatched to cloud-architect in isolated worktree.
