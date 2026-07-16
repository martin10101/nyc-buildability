# M1-T005 — G0 Definition-of-Ready Review

- **Task:** M1-T005 — Property-profile API v1: GET /api/v1/properties/{bbl}
- **Gate:** G0
- **Reviewer:** orchestrator
- **Date:** 2026-07-16
- **Verdict:** PASS

| G0 criterion | Evidence |
|---|---|
| Objective unambiguous | Owner Priority 3 spec + S1–S8 scenarios; response bound to accepted contracts; explicit no_match/conflict/unavailable/drift states; G5 F1–F4 hardening enumerated as in-scope items |
| Dependencies accepted | M1-T002 accepted 2026-07-16 (all gates); M0-T009 contracts v1 on main; M0-T004 FastAPI skeleton + CI |
| File scope exclusive | services/api/app/api|profile/** are new; main.py mount + pluto_soda.py hardening are exclusive to this task (no other active task in services/api); bbl.py and pluto fixtures frozen (forbidden) |
| Inputs and outputs defined | Packet lists connector, contracts, and the three reviewer carry-forward reports as inputs; six concrete outputs |
| Acceptance scenarios exist | S1–S8 incl. security scenario S7 (the four G5 findings) and regression S8 |
| Source documentation available | All in-repo (accepted research + reviews); no external research needed |
| Credentials | None; endpoint explicitly internal/dev (no auth until M0-T007/T008 unblock) — recorded as a G5 condition |
| Gates assigned | G0/G2/G3/G4/G5; producer backend-engineer; reviewers code-reviewer + security-reviewer |
| Execution location + disk | Worktree `.claude/worktrees/M1-T005`; source-only; tests offline; CI runs the suite; disk floor respected (no installs) |
| Cleanup / durable routing | Worktree + branch removed after acceptance; durable output committed source |

Constraint reaffirmed: if property_profile.schema.json v1 lacks a required field, the producer STOPS and reports (contract changes are a separate gated task; PRD 32.3 one-canonical-contract rule).
