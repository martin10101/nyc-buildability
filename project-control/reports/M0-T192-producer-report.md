# M0-T192 producer report — permanent fix to the research-record review-date check (D-093 R075)

Producer: backend-engineer. Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a59e5da996482917c`.
Contract head reset to `349d3f78ed919759dafba73b6f08ecaf0e607337` ("Wave 23: G0 PASS for M0-T192 at
its contract head; claimed, progress 20"). Two tool files plus this report only; no record file was
edited; `tools/project_control.py` was not run; nothing pushed; ports 3000/3001/8000 untouched.

## What was wrong and what the fix is

`tools/research_record_check.py` `derive()` chose the governing agent review with a **string**
comparison of the `date` field: `max(enumerate(reviews), key=lambda t: (str(t[1].get("date") or ""),
t[0]))`. Because `"2026-10-11"` sorts before `"2026-10-11T02:13Z"`, a date-only entry of a *higher*
revision could sort behind a timed entry of a *lower* revision, so the record read stale (D-093 R075:
"I logged it why cant u fix it permanently?").

Fix (scenarios S1–S5 in `project-control/tasks/M0-T192.json`):

1. The governing review is now the one with the **highest `reviewed_revision`**; ties are broken by
   the **parsed UTC time** (a date-only `YYYY-MM-DD` = the start of that day, 00:00 UTC), then by list
   order. Implemented as `_review_sort_key(index, review)` returning `(revision, timestamp, index)`
   and used by `derive()`'s `max(...)`.
2. A new `_parse_review_instant(value)` accepts only `YYYY-MM-DD`, `YYYY-MM-DDTHH:MMZ` and
   `YYYY-MM-DDTHH:MM:SSZ` (optional fractional seconds), returning a timezone-aware UTC datetime, or
   `None`. Constant `REVIEW_DATE_RE` is the gate; `REVIEW_DATE_FORMS` is the human wording.
3. The **structural check** (`_validate_review`) now refuses any agent review whose `date` is not one
   of those forms, with a message naming the record (the `err` prefix is the record id), the review
   index (`review.agent_reviews[i].date`) and the accepted forms. This is stricter than the former
   lax `_is_date`, which accepted a space separator (`2026-10-11 07:26`) and a bare `YYYY-MM-DD`
   followed by arbitrary text. The now-unused `req_date` parameter was dropped from
   `_validate_review` and its one call site.
4. Return shape of `derive()` (`{"code_current": bool, "review_state": str}`) and all CLI output are
   unchanged. Every committed record (NB-01…NB-06) still passes.

## Files changed (line counts after change)

- `tools/research_record_check.py` — 695 lines (was 657; +46/−4 in the diff). Added `datetime`
  import, `REVIEW_DATE_RE`/`REVIEW_DATE_FORMS`, `_parse_review_instant`, `_review_sort_key`; changed
  the `derive()` selection line; replaced the review-`date` validation with the strict form check.
- `tools/test_research_record_check.py` — 438 lines (was 344; +94). Added classes `GoverningReview`
  (4 tests) and `MalformedReviewDate` (4 tests), plus the `WRONG_SHA` constant.
- `project-control/reports/M0-T192-producer-report.md` — this file.

## Tests added (all pass; expected values worked by hand from the rule, not from a program run)

`GoverningReview`:
- `test_nb01_case_date_only_higher_revision_governs` — the NB-01 shape: timed revision-2 review then
  date-only revision-3 review → revision-3 governs → `current`. (This is the mutation target.)
- `test_same_revision_timed_same_day_governs_over_date_only` — same revision, same day: the timed
  review governs over the date-only (start-of-day) one, proven both ways (whichever carries the
  matching code identity decides `review_state`; here that is always the timed review).
- `test_higher_revision_with_earlier_date_still_governs` — revision 3 dated `2026-10-10` governs over
  revision 2 dated `2026-10-11T23:00Z`: revision dominates the parsed time → `current`.
- `test_date_only_parses_to_start_of_utc_day` — `_parse_review_instant("2026-10-11")` is 00:00:00 UTC
  and strictly before `2026-10-11T00:01Z`.

`MalformedReviewDate`:
- `test_slash_date_is_refused_naming_index_and_forms` — `11/10/2026` refused; message names
  `agent_reviews[0].date` and the accepted forms.
- `test_space_separated_datetime_is_refused` — `2026-10-11 07:26` refused (the old lax check let it
  through).
- `test_malformed_review_date_fails_the_check` — the full `--check` CLI exits 1 and prints `FAIL`.
- `test_every_accepted_form_is_valid` — `2026-10-11`, `...T02:13Z`, `...T07:26:00Z`,
  `...T07:26:00.500Z` all validate clean.

## Self-check outputs (commands and results)

- `python3 tools/test_research_record_check.py` → `Ran 37 tests ... OK`, exit 0 (29 pre-existing +
  8 new).
- `python3 tools/research_record_check.py --check` → `PASS: every record is structurally valid and
  no record claims the Verified label without meeting every condition.`, exit 0.
- `python3 tools/modularity_check.py --check` → `selected 792 files; failures 0; warnings 32`, exit 0
  (no new file flagged; `research_record_check.py` not among the warnings).

Live derive() on the committed records, before and after the change (identical): NB-01 `current`,
NB-02 `current`, NB-03 `current`, NB-04 `current`, NB-05 `stale` (code drift, see below), NB-06
`current`. All six agent-review dates in the committed records are in the accepted forms (verified),
so the new strict check breaks none of them.

## Mutation proof

Reverted only `derive()`'s selection line to the former string comparison
(`key=lambda t: (str(t[1].get("date") or ""), t[0])`) and ran the NB-01-case test:
`test_nb01_case_date_only_higher_revision_governs` FAILED with `AssertionError: 'stale' != 'current'`
(exit 1). Restored the fix (`key=lambda t: _review_sort_key(*t)`, line 526) and the same test passed
(exit 0). The test therefore pins the behavior change, not just the formula.

## What I checked, what I could not, and divergences from the brief's summary (D-093)

I read the research protocol (`docs/RESEARCH_AND_VERIFICATION.md`), the always-loaded rule
(`.claude/rules/research-and-verification.md`), the record format
(`docs/research/evidence-records/README.md`) and the three affected records read-only (NB-01, NB-05,
NB-06). I did not edit any record (forbidden path `docs/research/evidence-records/`). This is a
tooling change to the enforcement check; it changes no property fact, legal reading, calculation
input, result or certainty label, and I opened no external legal source for this change (section 2:
tooling does not need a new zoning investigation). Expected test values come from the rule in the
packet, worked by hand (section 7).

Two things differ from the brief's own summary (the brief instructs reporting these):

1. **The exact defect instance is not reproducing on the committed records at this head.** The
   brief's Section 1 says NB-01's revision-3 review is dated `"2026-10-11"` (date-only). At
   `349d3f78` the committed NB-01 revision-3 review is dated `"2026-10-11T07:26Z"` (timed), so under
   the old string comparison it already sorts last and NB-01 reads `current`. The record was updated
   after R075 was logged. The fix is still the correct permanent one: it makes selection robust to a
   future date-only higher-revision review (exactly the NB-01 shape, which the added test pins) and
   adds the malformed-date refusal.

2. **NB-05 reads `stale`, not `current` as the brief's S4 sub-claim states — and the date fix cannot
   change that.** NB-05's `code_current` is `False`: its stored `implementation.code_identity` no
   longer matches the current files (a real linked-code drift). `review_state` is derived as `stale`
   whenever the governing review's `reviewed_code_identity` does not equal the current code, which is
   the case here regardless of which review is chosen. This drift is unrelated to R075 and to the
   date comparison; it is reported-not-failed (`--check` still exits 0 and the record stays valid),
   and I cannot fix it from this task (it needs a record revision + re-review, and the record file is
   a forbidden path). S4's "it passes" holds (exit 0); the sub-claim "NB-05 reads current" is a
   pre-existing data condition outside this task's scope — flagged for the orchestrator.

I did not run the full api/web suites, `tools/project_control.py`, git push, or CI; those are the
orchestrator's/CI's. I did not independently re-verify the legal readings in the records (out of
scope and not a professional verification; the check certifies nothing about legal correctness).

END-OF-REPORT
