# M1-T007 — G0 definition-of-ready (orchestrator)

- **Task:** Official-source research — DOB NOW Open Data family
- **Date:** 2026-07-17
- **Origin:** PRD §8.1 mandatory family; owner directive 2026-07-17 ("DOB NOW research may proceed in a separate parallel slot, but it must not delay the Confirm-screen critical path"). Launched in the parallel slot precisely while the critical path is blocked on the owner-supplied expansion ZIP.

| G0 item | Status |
| --- | --- |
| Objective unambiguous | YES — one source family, research-only, registry-draft + OQ deliverables per the accepted M1-T001/T003/T004 pattern |
| Dependencies accepted | YES — M1-T001 (source-registry framework research) accepted |
| File scope exclusive | YES — docs/research/M1-T007-* + fixtures subdir + own report; no overlap with any active task (none active) |
| Inputs/outputs/scenarios | YES — S1–S6 in packet (live-verified IDs, evidence-backed join semantics, freshness cross-check, explicit rule-outs, PRD §8.2 completeness, no scope creep) |
| Credentials | NONE — public Socrata endpoints, tokenless (rate-limited but sufficient for research); optional app token remains HUMAN_ACTIONS §7 |
| Gates | G0 (this), G1 (data-contract-verifier — source/data-contract gate for research claims), G3 (independent walkthrough of the research doc against live sources) |
| Execution location / disk | Network + KB-scale text; worktree `.claude/worktrees/M1-T007`; disk 7.77 GB free (above floor) |
| Cleanup | worktree removed at acceptance; fixtures are KB-scale committed evidence |

**No production deployment, no credentials, no code changes.** Parallel-slot rule embedded as a packet risk: this task yields to the Confirm-screen critical path at any moment.

## Result

**G0 PASS** — claiming for official-source-researcher, worktree `.claude/worktrees/M1-T007`, branch `task/M1-T007-dob-now-research`.
