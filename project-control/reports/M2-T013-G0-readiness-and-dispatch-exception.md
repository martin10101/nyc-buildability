# M2-T013 — G0 Readiness + Owner-Authorized Dispatch Exception

**Task:** M2-T013 Production spatial-intersection engine with explicit uncertainty model
**Recorded by:** orchestrator (lead session) · **Date:** 2026-07-21
**Branch:** `task/M2-T013-spatial` · **Worktree:** `.claude/worktrees/M2-T013-spatial`
**Base:** `f433c2c` (origin/main; CI + secret-scan both green 2026-07-21T04:27Z)

## 1. Owner authorization (2026-07-21)

The owner approved a **narrow, task-specific sequencing exception** lifting M2-T013's
`M0-T019` dependency **for implementation only**. This is NOT a general dependency or
hold release. Verbatim scope preserved from the owner directive:

- Authorize dispatch + implementation of M2-T013 now, implemented **directly in the lead
  session** (no producer agent — there is no concurrent second eligible task, so a separate
  producer would only duplicate context and tokens without adding parallelism).
- Preserve every other control: the planning-report review hold, the G6 human gate, the
  survey/rules holds, the B-001 Supabase credential blocker, and all other dependencies/holds.
- Do **not** merge or accept M2-T013 before its dependencies and final integration
  conditions are satisfied. If implementation finishes while M0-T019 remains unresolved,
  freeze the candidate SHA and report — never bypass acceptance controls.

## 2. Why M2-T013 is technically independent of M0-T019

M0-T019 is a **frontend** dependency-security upgrade (Next/React tree + npm policy). M2-T013
is a **backend** Python spatial engine. There is **no import relationship and zero file
overlap**:

| | M0-T019 (frozen, PR #64 @ 3908082) | M2-T013 (this task) |
|---|---|---|
| Layer | `apps/web/**` frontend + `.github/workflows/**` + `CLAUDE.md` + `docs/DEPENDENCY_SECURITY_POLICY.md` | `services/api/app/spatial/**` backend |
| Language | JS/TS (npm) | Python (shapely 2.0.7 / GEOS 3.11.4) |
| M0-T019's 11 files | package.json, package-lock.json, .npmrc, 3× workflow/CI, DEPENDENCY_SECURITY_POLICY.md, CLAUDE.md, M0-T019 report, dependency_age_gate.mjs, scripts/tests | **none touched** |

M2-T013 runs on `main`'s current backend, which does not include and does not need
M0-T019's frontend patch. When M0-T019 eventually merges, the two diffs are disjoint → no
conflict.

## 3. Exact non-overlapping file scopes (this task)

**Allowed (per packet):**
- `services/api/app/spatial/**` (new module)
- `services/api/tests/spatial/**` (new tests + fixtures by reference)
- `docs/research/**` (V1/V2 accuracy-evidence extracts, small, retrieval-dated)
- `project-control/reports/M2-T013-*` (this task's own control/report artifacts)

**Forbidden (per packet):** `services/api/app/profile/**`, `_contract_schemas/**`,
`packages/contracts/**` (NO contract change — M2-T012 integrates), `services/api/app/connectors/**`
(read-only consumption; no edits), `apps/web/**`, any `Verified` labeling, any share
renormalization / sliver suppression / uncertainty collapse, `project-control/**` except own report.

## 4. G0 readiness checklist (docs/GATES_AND_CHECKPOINTS.md)

- **Objective unambiguous:** yes — production per-(lot,district) intersection with the
  owner-approved uncertainty model (advisory C1–C4 + coverage-family invariants).
- **Dependencies:** `M2-T011` accepted, `M0-T018` accepted, `M0-T019` **sequencing-exception
  authorized for implementation** (acceptance still blocked). Consumes accepted connector
  domain models (M2-T007 zoning-features, M2-T008 ZTLDB, M2-T009 MapPLUTO geometry) read-only.
- **File scope exclusive:** yes (§3); disjoint from the only other active task (M0-T019).
- **Inputs/outputs defined:** yes (packet).
- **Acceptance scenarios exist:** yes — SI-S1..S12 + SI-CF1..CF7 in the packet; implemented
  as the `services/api/tests/spatial/**` pack.
- **Source docs available:** approved policy advisory
  `project-control/reports/M2-T013-geospatial-policy-advisory.md`; V1/V2 official metadata
  fetched + cited in-task (honest `assumed` finding recorded where officials publish none).
- **Required gates assigned:** G0, G1, G2, G3, G4 — reviewers data-contract-verifier,
  code-reviewer, geospatial-engineer (all ≠ producer). Launched once, at the frozen SHA.
- **Execution location + disk:** local checkout + local pytest (shapely/GEOS/pytest already
  present, exact pins) + CI; committed fixture reuse + small metadata extracts; negligible
  disk footprint, well within the owner PC budget. No large/persistent local artifacts.
- **Cleanup:** no temp files beyond pytest's own; no downloads retained.

## 5. Integration precondition (recorded for final review)

Before final M2-T013 review/integration: reconcile the latest `origin/main` (including
M0-T019 if merged by then), prove M2-T013 scope remains clean and disjoint, run the complete
required tests, and freeze one candidate SHA. Reviewers run once at that frozen SHA.

**G0 verdict:** PASS (administrative readiness). Acceptance remains blocked pending
dependencies + owner authorization.
