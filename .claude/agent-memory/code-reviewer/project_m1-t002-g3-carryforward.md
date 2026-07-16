---
name: m1-t002-g3-carryforward
description: M1-T002 PLUTO SODA connector G3 PASS (2026-07-16, commit 9e22839); D1 record-bbl misclassification + D2 NaN/Infinity + confidence-1.0 guidance to enforce at property-profile API review
metadata:
  type: project
---

M1-T002 (pluto-soda connector) G3 reviewed 2026-07-16: **PASS** at commit `9e22839` (worktree `.claude/worktrees/M1-T002`). 87 tests re-run first-hand; all S1-S8 reproduced; S3a deviation (9999999999 rejected client-side, 5999999999 used for live no-match) APPROVED as the only contract-consistent reading. Report: `project-control/reports/M1-T002-G3-review.md`.

Non-blocking findings to verify fixed or carried at the property-profile API task (and at merge):
1. **D1 (Medium)** `pluto_soda.py:614` — unparseable record-level `bbl` escapes as `BBLValidationError` (validation_error) instead of `SchemaDriftError`; downstream must not see validation_error for source corruption. Check patched before/at property-profile API.
2. **D2 (Low)** `_normalize_value` accepts "NaN"/"Infinity" → nan/inf facts with no drift signal; non-RFC JSON downstream.
3. **D3 (Low)** `retrieved_at` stamped pre-request (skew up to ~31.5 s with retries).
4. **F5** `urllib_transport` error translation untested; **F6** `importorskip("jsonschema")` lets contract validation silently skip in a misconfigured CI.
5. **F7 guidance**: every fact has `confidence: 1.0` — property-profile/conflict engine must never map that to a coverage label (PRD §12).
6. `build_page_url`/F14 change-file are unconsumed hooks for the M2 bulk task; OQ-4/OQ-10 remain open per [[m1-t001-g3-carryforward]].
7. Fixture-proven Socrata facts for future SoQL writers: checkbox columns are JSON booleans (`splitzone=true`; `='Y'` → non-drift 400 `query.soql.type-mismatch`); full records decimal-serialize `bbl`/`appbbl` (hazard broader than $select).

**Why:** PASS follows the M0-T005/M0-T009/M1-T001 precedent (typed-safe residuals recorded in memory, no fabrication paths, all scenarios green); D1/D2 recommended as immediate small patches.
**How to apply:** first checks when reviewing the property-profile API (Priority 3), the drift-monitor job, or the M2 mappluto-bulk importer; verify D1/D2 patch status before approving any consumer of the error taxonomy.
