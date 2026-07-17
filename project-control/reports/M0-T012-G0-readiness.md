# M0-T012 — G0 definition-of-ready (orchestrator)

- **Task:** CI hygiene — pin all GitHub Actions to reviewed immutable commit SHAs
- **Date:** 2026-07-17
- **Origin:** Owner directive 2026-07-17 ("narrowly scoped CI SHA-pinning hygiene task… Do not mix unrelated formatting, ruff cleanup, dependency updates or functional changes"). Debt recorded by M0-T005-R1 G5 and M2-T001 G5 F1. Must land before any repo/CI secret (B-001/B-002).

| G0 item | Status |
| --- | --- |
| Objective unambiguous | YES — exactly 11 `uses:` lines across two files; four official actions; same-major latest release; secret-scan.yml comment style |
| Dependencies accepted | YES — M2-T001 accepted (its web jobs are among the refs being pinned) |
| File scope exclusive | YES — two workflow files + producer report; no other active tasks |
| Inputs/outputs/scenarios | YES — S1–S6 in packet (incl. annotated-tag dereference proof and branch-CI regression proof) |
| Credentials | NONE — gh api on public repos; no secrets |
| Gates | G0 (this), G2, G3 (security-reviewer — this is CI-security work), G4 (CI green post-merge) |
| Execution location / disk | Owner PC KB-scale edits; disk verified 7.77 GB free (above the 4 GB floor — restored since session start; owner said proceed); CI proof on the task branch; worktree removed after acceptance |
| Cleanup | worktree + branch removal at acceptance; no artifacts |

**No production deployment, no credentials, no dependency changes involved.**

## Result

**G0 PASS** — claiming for backend-engineer, worktree `.claude/worktrees/M0-T012`, branch `task/M0-T012-sha-pinning`.
