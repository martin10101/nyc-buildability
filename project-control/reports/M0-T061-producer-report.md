# M0-T061 (P6) — Producer report: silent-reviewer detection → one controlled re-dispatch → hard fail-closed PAUSE/STOP

Activation-checklist defect P6: under unattended actuation a DISPATCHED reviewer that
returns NOTHING must never be indistinguishable from a clean review ("absent evidence
treated as passing evidence"). The supervisor reviewer-gate must treat "gate dispatched,
no verdict returned" as: bounded detection → EXACTLY ONE controlled re-dispatch → then a
hard fail-closed PAUSE/STOP with a recorded reason and visible evidence. Additive to
`project_control.accept`.

## SAFETY GUARD / worktree
- `git rev-parse --show-toplevel` = `.../.claude/worktrees/agent-add180fff8a013701` (contains `.claude/worktrees/agent-`). ✓
- `git rev-parse --abbrev-ref HEAD` = `worktree-agent-add180fff8a013701` (starts with `worktree-agent-`). ✓
- Re-based my OWN worktree to the integration baseline: `git reset --hard 4083d2c…` → `git rev-parse HEAD` = `4083d2c11c842cb3b2c111de03e9b2810c88bab6`. Base suite `test_agent_supervisor_reviewer` + `test_agent_supervisor_ephemeral_review` = 105 tests, OK.

## 1. Module(s)/functions changed; before/after behavior

### `tools/agent_supervisor/ephemeral_review.py` (IN scope)
The verdict-consuming seam is `conduct_ephemeral_review` (step 3, the single call site of
`reviewer.review()` in this module). Two additions:

- New module constant `SILENT_NO_VERDICT_CODES = {"review_timeout",
  "missing_decision_file", "provider_rejected_request"}` — the reviewer `error_code`s
  that mean the DISPATCHED reviewer returned NOTHING adjudicable (timed out / no decision
  file / provider rejected the turn). These are exactly the codes emitted by
  `codex_reviewer.CodexReviewer.review()`: the timeout branch sets `review_timeout`;
  `no_decision_error()` returns `missing_decision_file` or `provider_rejected_request`.
- New helper `_silent_reviewer_record(...)` — builds a durable, sealed, journaled hard
  fail-closed PAUSE/STOP `ReviewRecord`, sealed exactly like `_refusal_record` (redact →
  digest via `.finalize()`, appended to the journal).

**Before:** step 3 ran `reviewer.review(...)` once and sealed whatever came back. A
no-output/timeout reviewer produced a record with `ok=False, decision=None` and the raw
underlying `error_code` (e.g. `review_timeout`) passed through — no retry, no distinct
"the gate was dispatched but returned nothing" marker.

**After (timeout→retry→STOP):**
1. First dispatch.
2. If `outcome.decision is None AND outcome.error_code in SILENT_NO_VERDICT_CODES` →
   EXACTLY ONE controlled re-dispatch of the same packet (a fresh read-only process).
3. If the re-dispatch STILL returns `decision is None` → return
   `_silent_reviewer_record(...)`: `ok=False`, `decision=None`, distinct
   `error_code="reviewer_silent_no_verdict"`, `notify_events=["reviewer_silent_redispatched",
   "reviewer_silent_no_verdict", "reviewer_paused_fail_closed"]`, carrying the underlying
   outcome's failure code/message and usage, `attempts = first.attempts + redispatch.attempts`.
   Sealed + journaled.
4. If the re-dispatch DELIVERS a verdict → proceed normally, tagging the sealed record's
   `notify_events` with `reviewer_redispatched_after_silence` (recovered-from-silence stays
   visible but is NOT a stop).

**Distinct error_code / sealing / journaling / notify:** the terminal record uses the
distinct `error_code="reviewer_silent_no_verdict"` (never a delivered verdict's code, never
`ok=True`). It is built with the same `ReviewRecord(...).finalize()` seal (redaction pass +
`record_digest`) and, when a `journal` is supplied, appended via `ReviewJournal.append` like
every other durable record. Visibility is carried by the three `notify_events`.

### Deliberate discriminator narrowing (verified adjustment of the prior analysis)
The prior analysis proposed the broad discriminator `outcome.decision is None` and listed
"exhausted" as silence. I confirmed the seam independently and **adjusted**: a broad
`decision is None` also captures `schema_retry_exhausted`, which the gate-reviewed (G3 M-2)
test `test_agent_supervisor_ephemeral_review.test_a_failed_review_still_seals_a_verifiable_record`
deliberately pins to seal with `error_code="schema_retry_exhausted"`, `attempts=3`. Relabeling
that would (a) overturn a reviewed invariant and (b) break the mandated-green ephemeral suite —
which is out of my allowed_paths to fix. More importantly it is the WRONG semantics: an
exhausted / validation-adjudicated outcome is the reviewer's OWN bounded retry DELIVERING
output and fail-closing it into a distinct sealed `ok=False` record — that is not "absent
evidence treated as passing evidence." The P6 defect is specifically a reviewer that "returns
NOTHING" / "bounded-timeout". So the discriminator is `decision is None AND error_code in
SILENT_NO_VERDICT_CODES`, which:
- re-dispatches + hard-fails the genuine no-output silence (SC1/SC4-silent),
- leaves the already-adjudicated `schema_retry_exhausted`/validation no-verdict fail-closed
  and unrelabeled (still `ok=False`, never downgraded — SC4-adjudicated), preserving the
  ephemeral suite's green G3 M-2 invariant IN SCOPE,
- leaves DELIVERED FAIL/BLOCKED verdicts (HALT_UNSAFE/STOP_FOR_OWNER) untouched (SC3).

`codex_reviewer.py` and `review_cadence.py` (both allowed but not required): unchanged. The
review-cadence policy is a separate concern (whether to review), not verdict consumption.
`loop.py:1813` (the other `reviewer.review()` consumer) is OUT of scope and untouched.

## 2. Grep evidence the seam is inside the allowed set
`Grep "conduct_ephemeral_review|\.review\(|reviewer\.review"` over `tools/agent_supervisor`:
```
ephemeral_review.py:41   (comment)
ephemeral_review.py:225  def conduct_ephemeral_review(
ephemeral_review.py:289  outcome = reviewer.review(        <-- the in-scope verdict-consuming seam
loop.py:1813             outcome = self.reviewer.review(   <-- OUT of scope, untouched
```
`Grep "conduct_ephemeral_review"` over `tools`: only `ephemeral_review.py` (definition) and
`test_agent_supervisor_ephemeral_review.py` (tests). `conduct_ephemeral_review` is NOT called
from `loop.py`; the in-scope change is fully contained.

## 3. git diff --stat
```
 tools/agent_supervisor/ephemeral_review.py |  95 ++++++++++++++-
 tools/test_agent_supervisor_reviewer.py    | 185 +++++++++++++++++++++++++++++
 2 files changed, 279 insertions(+), 1 deletion(-)
```
Key hunks: `SILENT_NO_VERDICT_CODES` constant; `_silent_reviewer_record` helper; the step-3
detect→re-dispatch→STOP block; and step-4 `notify_events=list(outcome.notify_events) + extra_notify`.

## 4. Freeze-baseline + new tests + ephemeral suite
20-module freeze suite (single command, Python 3.11.9):
```
Ran 1182 tests in 122.913s
OK (skipped=2)
```
1182 = 1175 base + 7 new P6 tests (≥ 1165 required; 0 failures; 2 skipped).

New tests (`tools/test_agent_supervisor_reviewer.py`, class `P6SilentReviewerRedispatch`):
- `test_sc1_silent_reviewer_redispatches_once_then_hard_fails_closed` (P6-SC1)
- `test_sc1_hard_fail_record_is_journaled_and_round_trips` (P6-SC1 durability)
- `test_sc2_silent_then_verdict_on_retry_proceeds_normally` (P6-SC2)
- `test_sc3_delivered_halt_unsafe_is_not_redispatched` (P6-SC3)
- `test_sc3_delivered_stop_for_owner_is_not_redispatched` (P6-SC3)
- `test_sc4_persistent_no_output_silence_never_downgrades_to_proceed` (P6-SC4, 3 sub-codes)
- `test_sc4_adjudicated_no_verdict_stays_fail_closed_without_redispatch` (P6-SC4 boundary:
  exhausted/validation stay fail-closed, no re-dispatch, no relabel)

Separate ephemeral_review suite (exercises the edited module, NOT in the 20-module set):
```
Ran 31 tests in 0.701s
OK
```
Stays green — the narrowed discriminator preserves the G3 M-2 `schema_retry_exhausted` seal.

## 5. Non-vacuity (revert/restore)
Temporarily neutralized the guard (`if False and outcome.decision is None and …`), kept the
new tests, re-ran `P6SilentReviewerRedispatch`:
```
Ran 7 tests ... FAILED (failures=6)
 SC1 (both)      -> FAIL   (no re-dispatch; no reviewer_silent_no_verdict record)
 SC2             -> FAIL   (silent first dispatch never recovers -> not ok/CONTINUE)
 SC4-silent (x3) -> FAIL   (calls==1 not 2; error_code != reviewer_silent_no_verdict)
 SC3 (x2)        -> ok     (delivered verdicts are guard-independent by design)
 SC4-adjudicated -> ok     (exhausted/validation never re-dispatch anyway; guard-independent)
```
The SC3 / SC4-adjudicated passes under neutralization correctly prove those scenarios exercise
the untouched paths; SC1/SC2/SC4-silent prove the guard is load-bearing. Restored the guard;
full suites green again (20-module 1182 OK; ephemeral 31 OK).

## 6. `git diff --name-only 4083d2c HEAD`
```
tools/agent_supervisor/ephemeral_review.py
tools/test_agent_supervisor_reviewer.py
project-control/reports/M0-T061-producer-report.md
```
All within allowed_paths.

## 7. HEAD sha
Recorded post-commit in the return summary.
