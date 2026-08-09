---
name: m2-t004-g3-carryforward
description: M2-T004 delta re-review G3+G4 PASS @151f2e5 (D1/C1+C2 closed, PR #5 CI fully green); residual D2-D5 destinations for M2 persistence and M2-T003 reviews
metadata:
  type: project
---

M2-T004 (data-semantics separation + snapshot lineage) — delta re-review 2026-07-17: **G3 PASS + G4 PASS @ 151f2e5** on branch task/M2-T004-data-semantics (supersedes the FAIL @be55a3a). Prior single blocking defect D1 (= G1 C1: two M2-T001 web assertions hard-coding retired 108-column value `missing_noncritical`) corrected to `complete` under a documented orchestrator scope amendment (task packet line 27; correction applied by orchestrator, not producer). C2 closed: affresfar/mnffar documented in builder exclusion category 1 + README mirror; my scripted partition audit against F08 = 19 basis + 5 geometry + 30 cat1 + 8 vintage dates + 35 identity/admin + 3 sanit* + 8 use-area = 108, zero unaccounted. builder.py delta mechanically verified comment-only. PR #5 CI: all 12 checks green at 151f2e5 including formerly red web-e2e; api job stayed green. S1–S5 findings from the original review stand (basis grounded per-column in official 26v1 dictionary; canonical-json-1 hand-verified; fail-loud lineage; stricter idempotency comparisons).

**Why:** future reviews touching the profile builder, contracts 1.2.0, or web completeness UI need to know what is settled vs still open.

**How to apply — non-blocking residuals to enforce later (recorded in on-branch G3 report §2):**
1. D2: `_status_dimensions` unused `result` param (builder.py:403) — drop at next builder edit.
2. D3: `observation_event_id` injectable into `fetch_by_bbl`; enforce per-fetch uniqueness at M2 Supabase persistence.
3. D4: canonical-json-1 is Python-semantics-bound, digest covers PARSED body (cannot byte-verify raw snapshots; duplicate keys collapse); at M2 snapshot persistence store raw bytes + consider raw-bytes digest (intersects [[m1-t002-g3-carryforward]] D2 NaN issue).
4. D5: builder declares contract_version 1.0.0 vs schema 1.2.0 — M2-T003 owns declaration semantics (extends [[m1-t006-g3-carryforward]] item 2); recheck there.
5. Ruff gotcha: lint from services/api, never repo root with --config (phantom I001).
6. Shared-fixture coupling lesson: `apps/web/src/test-support/fixtures.ts` imports contract fixtures cross-package — ANY future fixture-regenerating task must include web tests in its blast-radius check even when apps/web is a forbidden path; flag at G0/G3.
