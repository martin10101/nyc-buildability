# G4 QA Gate Report — M0-T022 (Owner Mission-Control Dashboard)

_Verbatim independent reviewer return (qa-engineer); transport entities decoded only._
_G4 requires BOTH qa (this) and human-journey to PASS; the G4 gate JSON references this qa half (M4-T004/T005 precedent), with the human-journey PASS on file alongside._

- **Gate ID:** G4 (QA half — test adequacy / regression / determinism)
- **Task ID:** M0-T022 (Owner Mission-Control dashboard — read-only observability over project-control)
- **Reviewer:** qa-engineer (read-only, independent)
- **Producer:** frontend-engineer
- **Result:** PASS
- **Frozen SHA:** `7ea8b0d22a8300938f85452be19b85f8a8cc8e3a` (branch `task/M0-T022-owner-dashboard`; `git status` clean).

## Acceptance criteria reviewed
AS-2, AS-5, AS-6, AS-8, AS-9, AS-10, AS-11, AS-12, AS-15, AS-17, AS-18, plus the product-map contract suite (AS-1 support).

## Steps independently executed
1. `python tools/validate_product_map.py --json` → exit 0, `{"valid": true, "error_count": 0, "task_count": 55, "system_count": 10}`.
2. `python tools/test_product_map.py` → `Ran 13 tests ... OK` (exit 0).
3. `git diff --stat origin/main -- apps/web/package.json apps/web/package-lock.json` → EMPTY (zero new deps).
4. `git diff --name-status <merge-base> HEAD` → change set entirely additive: all lib/dashboard, components/dashboard, app/dashboard, e2e/dashboard.spec.ts, tools/*product_map*, product-map.json+schema are NEW (A); only ci.yml, playwright.config.ts, state.json modified.
5. `git diff --name-status <merge-base> HEAD -- '**/*.test.ts' '**/*.spec.ts' services/api/tests packages/contracts` → NONE modified/deleted (only additions) → existing tests untouched.
6. Independently re-derived the two headline numbers from progress.ts/launch.ts against fixtures.ts.
7. Web vitest/Playwright verified via committed CI evidence + reading the specs (thin-client).

## Expected vs actual (hand-recomputed)
- Engineering (AS-5): sys_a=(100+90)/(100·2)=0.95; sys_b=(100+0)/200=0.5; 50·0.95+50·0.5 = **72.5 → 73%**. Matches.
- Launch (AS-6): sys_a=1/2=0.5 (no cap); sys_b=1/2=0.5 capped to 0.15 (G6 not passed on M1-T001); 50·0.5+50·0.15 = **32.5 → 33%**. Matches; launch<eng verified.
- Cap logic: capStillApplies applies because M1-T001 has no G6 PASS — correct.
- health≠completion (AS-17): sys_b RED (blocked member + open blocker B-900) yet engCompletion===0.5, acceptedCount===1; failing CI drives health.overall==='RED' while engineering/launch.exactPercent unchanged (progress never reads GitHub).
- UNKNOWN never coerced (AS-18/AS-12): unknown member status → system engCompletion=null, dataQuality='unknown', headline percentWhole=null, unverifiedWeight=50, issue task.status.unknown; empty raw → overall unknown, both headlines null, issues>0, no throw.
- Gate independence: producer-recorded G3 excluded from passedGates, present in unmetGates — matches model.ts independence rule.
- Roster contradiction (AS-18): roster listing M0-T002 (awaiting_gate) as accepted → roster.contradiction error, ref M0-T002.
- Blockers (AS-8): only open surface (B-900, not resolved B-901); owner label + affected system resolved.
- Current work: derived from ACTIVE_STATUSES lifecycle, not commits; deterministic primary.
- Activity (AS-10): control-plane event model, deterministic injected "today"; allowedKinds excludes raw-commit kinds.
- Launch blockers (AS-9): deterministic ranks 1..n, kinds derived, not invented.
- GitHub (AS-11): parseHeadSha/parsePrs(mergedOnly)/parseCiRuns correct; stale fallback retains last-known headSha marked stale:true, available:false.
- product-map tests (AS-1): all 13 cases pass.

## Regression / determinism findings
- Zero new deps: package.json + package-lock.json byte-identical to origin/main.
- Additive only: single appended product-map CI job; playwright.config.ts only adds the e2e flag (unset in prod → 404). No existing test/product file modified or deleted (merge-base diff).
- Determinism: pure engine takes nowIso as a param; no Date.now/Math.random in the pure path; GitHub client tests inject fetchImpl+nowMs+noCache and __resetGitHubCache() in beforeEach; fixtures use fixed NOW_ISO + fixed API JSON.
- Stale-base note (non-blocking): the frozen branch was cut from an older main; git diff origin/main shows unrelated deletions (M5-T001, packages/contracts scenario files) purely because main advanced — an orchestrator rebase/merge concern, not a defect in this task (merge-base diff confirms the branch touches none of those files).

## Defects
None blocking.

## Non-blocking observations (test-adequacy enhancements)
1. AS-2: real-ledger smoke asserts structure but no vitest asserts ledgerCounts / per-milestone rollups equal project_control.py status / current_state.py; consider a hardcoded-count assertion on the synthetic fixture.
2. AS-8: no test asserts the specific real open blockers (B-001/B-004/B-010) from the live ledger; synthetic open-vs-resolved covered (moving target).
3. AS-12: missing/empty control-plane unit-tested; a truly malformed JSON routed through loader.server.ts (→ file.unparseable) not exercised in vitest.
4. validator negatives: test_product_map.py lacks explicit negatives for blocker_labels unknown-ref and readiness_cap.on_task dangling-ref (both paths exist and run on the positive path).

## Reviewer conclusion
PASS (qa half of G4). Two progress numbers deterministic and reproduce independent hand-computation; health provably independent of completion; UNKNOWN never coerced; gate independence, roster-contradiction, blocker, current-work, activity, GitHub stale-safety covered with correct expectations. Stdlib validator + 13 unit tests pass on the real 55-task/10-system ledger. Zero new dependencies, CI job additive, existing tests untouched, CI run 29976490909 green on all 11 jobs. Four non-blocking test-adequacy enhancements. G4 acceptance also requires the human-journey-reviewer PASS (on file).

---

## Delta re-review @ b2de479 — PASS (condensed by orchestrator; full verbatim in the reviewer transcript)

The qa-engineer re-reviewed the delta at b2de479 (CI run 29977738748 green). `git diff 7ea8b0d..b2de479` = exactly 3 files (model.ts, engine.test.ts, fixtures.ts). Re-ran `validate_product_map.py --json` (valid, 55/10) and `test_product_map.py` (13/13). Re-derived both headline numbers by hand against the new model + fixtures: **Engineering 72.5→73%, Launch 32.5→33% preserved** (change 3 moves the cap target to the non-accepted M1-T002 to compensate for change 1 making the accepted M1-T001 fully-gated). New test is meaningful (fails under the OLD model) and deterministic. Zero new deps (package.json/lock byte-identical); existing tests untouched; all prior scenarios still hold. **VERDICT: PASS at b2de479** (qa half).
