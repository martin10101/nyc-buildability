# M0-T192 reviews (every return kept unchanged)

- G3 code-reviewer at 2a7cc7f0: PASS (three advisories, no action); carry to c9e292a7 confirmed.
- G4 qa-engineer at 2a7cc7f0: PASS with one advisory (no test pinned the non-Z offset refusal); the builder added it (c9e292a7, test-only); delta PASS (the reviewer's mutation now fails the new test).
- G5 security-reviewer at 2a7cc7f0: PASS (two low advisories); carry to c9e292a7 confirmed.

## G3

<!-- saved unchanged by save_return.py from agent-a643a490553053c1f.jsonl, entry 2026-10-11T08:02:19.722Z, sha256 2ebe3b01e093acdda7bd8a860981c56b55aa2a2327957bd9a11ffd129702ae9d -->
# Gate report — M0-T192 — G3 (code-reviewer) — VERDICT: PASS

Task: M0-T192 "D-093 R075: research-record check chooses the governing review by revision and parsed time; refuse malformed review dates." In-regime (directive_refs D-093-R075). Frozen head `2a7cc7f03cebf90744feedfd94f2e19fd01958af` on `task/wave23-density-zoning-lot` in `/root/project/w-wave20` (worktree HEAD == frozen SHA; `tools/research_record_check.py` and `tools/test_research_record_check.py` working-tree-clean vs HEAD). Python 3.12.3.

## What I verified independently (not from the producer report)

**1. Selection key (REQUIRED — satisfied).** `derive()` line now reads `max(enumerate(reviews), key=lambda t: _review_sort_key(*t))[1]`. `_review_sort_key(index, review)` returns `(reviewed_revision, parsed-UTC-timestamp, index)` with `rev=-1` for non-int/bool and `ts=-inf` for unparseable. `max` therefore selects highest revision, then latest parsed time, then latest list index — exactly the packet rule (revision → parsed time → order) and the same index-tiebreak direction as the old `(str(date), index)` key. Old key removed. In-memory mutation proof reproduced: for the NB-01 shape (rev-2 `2026-10-11T02:13Z` / rev-3 `2026-10-11`, record revision 3), the OLD string key selects idx 0 (rev 2) → `stale`; the NEW key selects idx 1 (rev 3) → `current`. So `test_nb01_case_date_only_higher_revision_governs` genuinely pins the behavior change, not just a formula.

**2. Date parser (REQUIRED — satisfied).** `REVIEW_DATE_RE = ^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?Z)?$`; `_parse_review_instant` returns tz-aware UTC or None. I exercised it directly: `2026-10-11`→00:00:00 UTC (== `...T00:00:00Z`), `...T02:13Z`, `...T07:26:00Z`, `...T07:26:00.500Z` all parse; `2026-10-11 07:26` (space), `11/10/2026` (slash), `2026-10-11T07:26` (no Z), `...+00:00` (offset), `2026-13-40` (bad m/d via ValueError), `""` all → None. Accepted-forms-only, tz-aware UTC, date-only=00:00 UTC, fractional seconds: all correct.

**3. Structural refusal message (REQUIRED — satisfied).** `_validate_review` now emits, via the `err` closure that prefixes `{record_id}:`, `key 'review.agent_reviews[i].date' value <x> is not an accepted review date; use one of: <REVIEW_DATE_FORMS>`. Message names the record id, the review index, and the accepted forms. `cmd_check` collects `validate_record` errors → any malformed date yields FAIL/exit 1 regardless of the derive() line printed (confirmed: `test_malformed_review_date_fails_the_check` passes; S3 met).

**4. derive() shape / CLI unchanged (REQUIRED — satisfied).** Return stays `{"code_current": bool, "review_state": str}`. Diff touches only: `datetime` import, two new constants, two new helpers, the `_validate_review` signature + its one call site (dropped the now-unneeded `req_date` param — `req_date` is still used by `last_changed`, evidence, and freshness, so no dead code), the review-date validation line, and the `derive()` selection line. No print/CLI/promotion logic changed. `--check` output format unchanged.

**5. Every committed record passes; no unintended state change (REQUIRED — satisfied).** `python3 tools/research_record_check.py --check` → exit 0, PASS; all six records read `code_current=True review_state=current` (NB-01…NB-06). I compared old-string vs new-sort governing-review index on each committed record: identical selection for all six (NB-01 gov idx 2, NB-05 gov idx 2, others single-review). So the fix changes no committed record's derived state; the behavior change only manifests in the date-only-higher-revision shape, which no committed record currently has.

**6. Modularity (REQUIRED — satisfied).** `python3 tools/modularity_check.py --check` → exit 0; `research_record_check.py` not among the 32 warnings. +~38 net lines of two small cohesive helpers within the module's existing responsibility (review-state validation/derivation); no responsibility mixing, no giant function.

**7. Scope (REQUIRED — satisfied).** The M0-T192 builder commit `3aa81c908` touches exactly the three allowed paths (`tools/research_record_check.py`, `tools/test_research_record_check.py`, `project-control/reports/M0-T192-producer-report.md`). The other files in `349d3f78..2a7cc7f0` (NB-05 record, `M5-T158` gate/task files, `state.json`) all belong to disjoint peer task `M5-T158` committed in the shared worktree — not this task.

**Tests.** `python3 tools/test_research_record_check.py` → `Ran 37 tests ... OK`, exit 0 (29 pre-existing + 8 new: GoverningReview ×4, MalformedReviewDate ×4). New tests state expected values by hand from the rule.

**Directive D-093-R075 (code-level).** Every sub-clause is met in code: selection independent of date form; same-day date-only never makes a newer review read older; highest reviewed revision governs, ties by parsed time then order; rejects dates that are neither a date nor a UTC date-and-time; NB-01-case test present and reads `current`. (`directive-compliance-verifier` owns the recorded verdict; this G3 pass is the code view.)

## What I could not check (out of G3 scope / environment)
- **Control-plane CI job** (named in the requirement's `required_harness`): CI is the orchestrator's/CI's to run on the accepted head; not reproducible read-only here.
- **Backlog DB-238 update**: an orchestrator-at-merge action (packet `path_notes`), not a builder code change — not in this diff and not a G3 finding.
- I did not re-verify legal readings in the records (not a professional verification; the tool certifies nothing about legal correctness — out of scope per D-093).

## Observations (ADVISORY, non-blocking)
- **A1.** `review.professional_review.date` is still validated only by `req_str` (non-empty string), not the strict review-date form. This conforms to the packet (scope is agent-review dates, which drive selection); noting only that the strict refusal does not extend to the professional-review date.
- **A2.** Producer report divergence #2 (NB-05 reads `stale`) no longer holds at the frozen head: peer `M5-T158` commits in the same range updated NB-05's code identities and added a revision-3 review, so NB-05 now reads `current`. Informational — the report was written at the contract base `349d3f78` before those peer commits; not a defect.
- **A3.** The fractional-seconds regex allows any digit count; `datetime.fromisoformat` handles it on Python 3.11+ (CI/dev here is 3.12.3). On <3.11 a 1–2-digit fraction would be refused. Not material at current runtimes.

## Verdict
PASS. No REQUIRED findings. Fix is correct, behavior-preserving on all committed records, test-pinned with a reproduced red/green mutation, in-scope, and modular.

END-OF-REPORT


## G3 carry

<!-- saved unchanged by save_return.py from agent-a643a490553053c1f.jsonl, entry 2026-10-11T08:07:36.433Z, sha256 a0d7a439749527873c5ac54c66c59e8bcfb18234dbbb1a9184f84962d66e7b6f -->
Confirmed. `git diff --stat 2a7cc7f0..c9e292a7` touches only `tools/test_research_record_check.py` (+11) and `project-control/reports/M0-T192-producer-report.md` (+2). The production file `tools/research_record_check.py` diff between the two heads is EMPTY — unchanged. The added test `test_non_z_utc_offset_is_refused_naming_index_and_forms` asserts that `2026-10-11T07:26:00+00:00` and `2026-10-11T07:26-05:00` are refused (only a `Z` suffix accepted), which matches the already-reviewed `REVIEW_DATE_RE` behavior I independently verified (non-Z offsets return None → refused). Suite at c9e292a7: `Ran 38 tests ... OK`, exit 0 (was 37; +1 offset test). My G3 PASS verdict carries unchanged to c9e292a7 — no production-code change, strengthened test coverage only. END-OF-REPORT


## G4

<!-- saved unchanged by save_return.py from agent-a282834e661ff048c.jsonl, entry 2026-10-11T08:04:24.315Z, sha256 d2967b16b4b929c51c84491f9e0d6b5afbde3f67a2d7d502ea17f64785c2245b -->
# G4 (qa-engineer) gate report — M0-T192 (D-093 R075)

Task: tools/research_record_check.py must choose the governing agent review by highest reviewed_revision, then parsed UTC time (date-only = start of day), then order; refuse malformed review dates.
Frozen head reviewed: 2a7cc7f03cebf90744feedfd94f2e19fd01958af (task/wave23-density-zoning-lot).
Method: `git archive` of the frozen head extracted to /tmp; all commands run there. Read-only; no git/project_control/gh; ports 3000/3001/8000 untouched.

## VERDICT: PASS (one ADVISORY test-coverage gap)

## Commands and outputs (frozen export)
- `python3 tools/test_research_record_check.py` -> `Ran 37 tests ... OK`, exit 0.
- `python3 tools/research_record_check.py --check` -> exit 0; `PASS`. All 6 records structurally valid; NB-01, NB-02, NB-03, NB-04, NB-05, NB-06 all read `code_current=True review_state=current`.
- `python3 tools/modularity_check.py --check` -> could not run in the /tmp export (`git ls-files` exit 128: export is not a git repo). Not re-runnable here; see "could not check".

## Scenario verification (expected results worked by hand, then confirmed)
- S1 NB-01 shape — `GoverningReview.test_nb01_case_date_only_higher_revision_governs`. By hand: rev3 date-only "2026-10-11" (key (3, 00:00, 1)) beats rev2 timed "2026-10-11T02:13Z" (key (2, 02:13, 0)) -> rev3 governs, matches rev+code -> current. Old string key picked "...T02:13Z" (rev2) -> stale. Test pins current. Load-bearing (see mutation B).
- S2 same-revision date-only vs timed — `test_same_revision_timed_same_day_governs_over_date_only` (+ `test_date_only_parses_to_start_of_utc_day`). By hand: within rev2, timed 09:00Z (key ts) beats date-only start-of-day regardless of list order; proven both ways (matching code identity on timed -> current; on date-only -> stale). Load-bearing (mutation A).
- Higher revision, earlier date — `test_higher_revision_with_earlier_date_still_governs`: rev3 @2026-10-10 beats rev2 @2026-10-11T23:00Z -> current. Load-bearing (mutation B).
- S3 malformed refused — `test_slash_date_is_refused_naming_index_and_forms`, `test_space_separated_datetime_is_refused`, `test_malformed_review_date_fails_the_check` (CLI exit 1 + FAIL). Slash and space forms refused, message names `agent_reviews[0].date` and the accepted forms. Load-bearing (mutation C).
- S4 every committed record passes; NB-01/05/06 current — confirmed by `--check` at the frozen head (exit 0, all current).
- S5 existing tests unchanged — the test diff (349d3f78..2a7cc7f0) is additive only (classes GoverningReview, MalformedReviewDate, WRONG_SHA const); no prior test modified; all 37 pass. No test pinned the old string comparison, so S5's "except..." clause is vacuous — consistent.
- Every accepted form valid — `test_every_accepted_form_is_valid` (date-only, ...T02:13Z, ...:SSZ, ...fractionalZ).

## My own mutations (on a separate copy; frozen export left pristine, re-verified 37 OK)
- A) date-only parsed as END of day -> FAIL: test_date_only_parses_to_start_of_utc_day, test_same_revision_timed_same_day_governs_over_date_only (2 fails).
- B) drop reviewed_revision from the sort key `(0, ts, index)` -> FAIL: test_nb01_case..., test_higher_revision... (2 fails).
- C) loosen REVIEW_DATE_RE to accept a space separator / optional Z -> FAIL: test_space_separated_datetime_is_refused, test_malformed_review_date_fails_the_check (2 fails).
- D) loosen REVIEW_DATE_RE to accept `+HH:MM`/`-HH:MM` offsets -> ALL 37 tests still OK. Direct probe: `_parse_review_instant("2026-10-11T07:26:00+00:00")` parses; regex matches "+05:00". This proves the "non-Z offset is refused" behavior is correct in the frozen code but UNPINNED by any test.

## Findings
1. ADVISORY (tools/test_research_record_check.py, class MalformedReviewDate ~L405-434): no regression test pins "a non-Z UTC offset review date is refused." My G4 brief enumerates "non-Z offset" among the malformed forms to confirm has a test; the slash and space-separated forms are both covered and load-bearing, but mutation D (regex accepting +/-HH:MM) leaves the whole suite green. The implementation at the frozen head is correct (REVIEW_DATE_RE requires a literal `Z`; a `+00:00` form is refused — verified). Recommend adding e.g. `test_non_z_offset_is_refused("2026-10-11T07:26:00+00:00")`. Does NOT block: packet scenario S3's named examples are satisfied and tested, and the behavior is correct; this is a missing regression guard against a future loosening, not a defect.

## What I could not check (with reasons)
- modularity_check: not runnable in the /tmp archive export (no .git). Producer reports `failures 0; warnings 32`, research_record_check not among warnings; file is 695 lines, a cohesive single-responsibility module with two small added helpers (_parse_review_instant, _review_sort_key) and a regex constant. Defer modularity confirmation to G3/code-reviewer and to the CI control-plane job at the accepted head.
- Full api/web suites, CI, project_control, git — orchestrator/CI scope; I am read-only.
- Legal correctness of the records' readings — out of scope; nothing here is a professional verification.

## Notes for the orchestrator
- NB-05 reads `current` at the frozen review head (2a7cc7f0), so S4's "NB-01, NB-05, NB-06 read current" holds as reviewed. The producer report (written at the earlier contract head 349d3f78) correctly flagged NB-05 as `stale` there due to linked-code drift; a later wave-23 commit on this branch resolved the drift (NB-05 code_current=True now). The date fix itself does not touch records. Confirm the accepted head is 2a7cc7f0 (where S4 fully holds), not 349d3f78.
- The real committed NB-01 (rev3 timed "2026-10-11T07:26Z") does not trigger the original string-sort bug at this head; the added test faithfully reproduces the problematic date-only-higher-revision shape the directive describes, so the regression is pinned regardless.
- Producer report is accurate against the diff: `derive()` selection line changed to `_review_sort_key`; `req_date` dropped from `_validate_review` (one call site); strict REVIEW_DATE_RE replaces lax `_is_date` for review dates. CLI output and derive() return shape unchanged.

END-OF-REPORT


## G4 delta

<!-- saved unchanged by save_return.py from agent-a282834e661ff048c.jsonl, entry 2026-10-11T08:07:46.410Z, sha256 c701cbaac5d38c59643dd10e8da3640f46131c8a640ec5e6c90925436673eec0 -->
# G4 delta verdict — M0-T192 non-Z-offset test (head c9e292a7)

## DELTA VERDICT: PASS — advisory gap closed, no new concerns

Verified read-only against a fresh /tmp archive export of c9e292a7e07bd8906e4e7a0426797101be6b3003.

- Production file unchanged: `git diff 2a7cc7f0..c9e292a7 -- tools/` touches only `tools/test_research_record_check.py` (+11) and the producer report (+2). `tools/research_record_check.py` is absent from the diff (test-only change, as stated).
- Clean suite: `python3 tools/test_research_record_check.py` -> `Ran 38 tests ... OK` (37 + the new one).
- New test inspected: `MalformedReviewDate.test_non_z_utc_offset_is_refused_naming_index_and_forms` asserts both "2026-10-11T07:26:00+00:00" (UTC offset) and "2026-10-11T07:26-05:00" (non-UTC offset) are refused, naming `agent_reviews[0].date` and the accepted forms ("YYYY-MM-DDTHH:MMZ"). This is exactly the behavior my advisory flagged as unpinned.
- Mutation D re-run on the new head (REVIEW_DATE_RE loosened to accept `(Z|[+-]\d{2}:\d{2})`): suite now reports `FAILED (failures=1)` with the single failure being the new test. On the frozen head the same mutation left all tests green; the gap is now closed. Mutation applied to a throwaway copy; the export was left pristine.

The new test is load-bearing and correctly scoped. No production behavior changed; the full gate PASS on M0-T192 stands and this delta strengthens S3 coverage.

END-OF-REPORT


## G5

<!-- saved unchanged by save_return.py from agent-a3b46391f658bbe8a.jsonl, entry 2026-10-11T08:01:24.694Z, sha256 1af8ff0c275deebcd2a965693675af66aaac9a7f4e88b07fd6ad2f635d3e3203 -->
# G5 Security Gate Report — M0-T192 (D-093 R075)

Task: M0-T192 "research-record check chooses the governing review by revision then parsed UTC time; refuse malformed review dates"
Directive: D-093 R075. Frozen head: `2a7cc7f03cebf90744feedfd94f2e19fd01958af` (task/wave23-density-zoning-lot, /root/project/w-wave20).
Reviewer: security-reviewer (read-only). Gate: G5.

## VERDICT: PASS

No critical/high/medium security findings. Two low/advisory notes below. All G5 checks in the brief verified independently at the frozen head.

## Scope verified (the M0-T192 change)
The task commit `3aa81c908` touched exactly its three allowed paths: `tools/research_record_check.py` (+46/-5), `tools/test_research_record_check.py` (+94), `project-control/reports/M0-T192-producer-report.md`. No `.github/`, `.claude/`, hooks, settings, or any other governance file.
Note: the range `349d3f78..2a7cc7f0` also contains disjoint peer commits for a DIFFERENT task (M5-T158: NB-05 record, M5-T158 gates/task, state.json). Those are outside M0-T192's allowed_paths and are not attributable to this task (confirmed by per-commit `git show --stat`). Reviewed only the M0-T192 diff.

## G5 checks (each independently reproduced)

1. No eval / dynamic execution / network / file-write (PASS). `grep -nE "eval|exec|compile|os.system|subprocess|__import__|pickle|yaml|input\(|open\(|requests|urllib|socket"` on the production file at the frozen head returns only the regex literal line. Production code only reads files (`path.read_bytes()`), parses JSON, hashes (sha256), and regex-matches. No writes, no shell, no network.

2. No regex catastrophic backtracking / ReDoS (PASS). New pattern `REVIEW_DATE_RE = ^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?Z)?$` has no overlapping/ambiguous nested quantifiers; the only variable part `(\.\d+)?` is followed by a literal `Z`/`$`. Timed probe against hostile inputs up to 1.1M chars (long fractional runs, repeated near-matches, valid-prefix+junk tail): all complete in <16ms, most in microseconds — linear, no exponential blowup. The pre-existing `_is_date` regex is unchanged and trivial (`re.match`, fixed form).

3. Bounded input (PASS). Input is the committed JSON records under `docs/research/evidence-records/` (6 records); CI runs the check on repository files. `datetime.fromisoformat` runs only on strings already matched by the anchored short-form regex. Even an untrusted `--records-dir` is safe: the regex is linear and parsing is bounded.

4. Stdlib-only imports / no new package (PASS). Imports: argparse, hashlib, json, re, sys, datetime, pathlib. The only ADDED import is `from datetime import datetime, timezone` — both stdlib. No new third-party dependency; the dependency-security age/advisory gate (CLAUDE.md §15) is not triggered.

5. Stricter refusal cannot be bypassed to claim Verified; promotion rule unchanged (PASS). The diff does NOT touch `promotion_refusals`, `OWNER_C1_ANSWERED`, `C1_REFUSAL`, or `NON_PROMOTABLE_STATUSES` (verified by grepping the diff). In full source, `promotion_refusals()` still unconditionally appends `C1_REFUSAL` while `OWNER_C1_ANSWERED is False` (it is), so NO record can ever be labelled Verified regardless of review-state; the independent-review, professional-review, code-current, and conflicts/conditions refusals all remain. The date fix only changes `derive()`'s governing-review selection (`review_state`). Even if that flips a record to `review_state=current`, the unconditional C1 refusal (plus the other refusals) still blocks Verified — no bypass path exists. The new strict date check is fail-closed: a malformed review date is a structural error (FAIL), and in `promotion_refusals` a structurally-invalid record short-circuits with a refusal (`continue`) before any derive-based check. This tightens, never loosens, the Verified gate.

## Independent reproduction (commands and results, run in /root/project/w-wave20)
- `git diff 2a7cc7f0 -- tools/research_record_check.py tools/test_research_record_check.py` → empty (disk == frozen head).
- `python3 tools/test_research_record_check.py` → `Ran 37 tests ... OK` (exit 0), incl. the 8 new GoverningReview/MalformedReviewDate tests.
- `python3 tools/research_record_check.py --check` → PASS, exit 0; all six records NB-01..NB-06 read `code_current=True review_state=current`.
- Regex timing probe (python3 -c) → all hostile inputs non-matching in <16ms, linear.
- Fail-closed parse probe: `_parse_review_instant` returns None for `2026-13-45`, `2026-02-30`, `2026-10-11T25:99Z` (out-of-range calendar/time values that the loose regex admits but `fromisoformat` rejects) → such records are refused. `2026-10-11` → 00:00:00+00:00 (start-of-day, correct).
- `python3 tools/modularity_check.py --check` → `selected 792 files; failures 0; warnings 32`; `research_record_check.py` is NOT among the warnings (grew 657→695 lines, no new oversized-file concern).

## Findings
- F1 (LOW / ADVISORY): `REVIEW_DATE_RE` admits numerically out-of-range dates/times (e.g. `2026-13-45`); correctness is recovered by `datetime.fromisoformat`, which returns None → the record is refused (fail-closed). No security impact; the defense-in-depth is a bonus. No action required.
- F2 (LOW / ADVISORY, orchestrator awareness): the review range contains disjoint M5-T158 peer commits (control-plane files: gates, state.json, NB-05). They are outside this task's scope and belong to another task. One side effect: at the frozen head NB-05 reads `current` (the peer commit refreshed its code identities and added a revision-3 review), which incidentally resolves the producer report's divergence #2 — the producer report was authored at the earlier commit `3aa81c908` before the peer commit landed. No action for M0-T192.

## What I could not check
- Full CI run and the api/web suites (CI/orchestrator responsibility). I ran the two documented test commands plus the modularity check locally; all pass at the frozen head.
- Legal correctness of record contents (out of G5 scope; the tool certifies nothing about legal correctness, and the diff changes no legal reading/fact/calculation input/label — only enforcement tooling).

END-OF-REPORT


## G5 carry

<!-- saved unchanged by save_return.py from agent-a3b46391f658bbe8a.jsonl, entry 2026-10-11T08:07:29.054Z, sha256 2b58bf42648253f79e87eae5cf2b6e15a534db63619db375dedb53ae95540d05 -->
# G5 delta confirmation — M0-T192 @ c9e292a7

Verified `git diff --stat 2a7cc7f0..c9e292a7` touches only two packet-allowed paths: `tools/test_research_record_check.py` (+11) and `project-control/reports/M0-T192-producer-report.md` (+2). Test-only.

- Production file unchanged: `git diff 2a7cc7f0..c9e292a7 -- tools/research_record_check.py` is empty. My G5 security analysis (no eval/network/write, no ReDoS, stdlib-only, promotion/Verified rule untouched) carries unchanged.
- No governance, CI, hooks, or settings file changed (no `.github/`, `.claude/`, state.json, gates, config).
- The added test `test_non_z_utc_offset_is_refused_naming_index_and_forms` only tightens expectations (refuses non-Z offsets like `+00:00`/`-05:00`) — no behavior change to production.
- Suite reruns green at c9e292a7: `Ran 38 tests ... OK` (exit 0), the 37 prior + 1 new.

Verdict: PASS carries to `c9e292a7e07bd8906e4e7a0426797101be6b3003`.

END-OF-REPORT
