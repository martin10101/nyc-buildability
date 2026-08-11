# M0-T061 (P6) — G2 producer self-check — VERDICT: PASS

Recorded by `orchestrator` (role self_check). Producer evidence (backend-engineer, worktree `agent-add180…`),
integrated onto `control/session15-acceptance` by cherry-pick at HEAD `3c23072` (producer commit `e24b0102`;
byte-identical deliverable), re-based to head `77d7162` for review. Independent confirmation is G3 code-review +
G5 security-review; empty-set D-010 DCV row at accept.

## Deliverable → evidence
- **Silent-reviewer fail-closed (activation-checklist P6).** In `ephemeral_review.conduct_ephemeral_review`
  (the in-scope verdict-consuming seam; the other consumer `loop.py:1813` is out of scope and untouched): after
  the first `reviewer.review()`, if `outcome.decision is None AND outcome.error_code in SILENT_NO_VERDICT_CODES`
  ({`review_timeout`, `missing_decision_file`, `provider_rejected_request`}) → EXACTLY ONE controlled
  re-dispatch → if still silent, `_silent_reviewer_record` seals a DISTINCT hard fail-closed PAUSE/STOP record
  (`ok=False`, `decision=None`, `error_code="reviewer_silent_no_verdict"`, visible `notify_events`
  [`reviewer_silent_redispatched`, `reviewer_silent_no_verdict`, `reviewer_paused_fail_closed`], carrying the
  underlying failure code/message/usage), journaled like `_refusal_record`. A delivered verdict on retry proceeds
  normally, tagged `reviewer_redispatched_after_silence`.
- **Correct narrowing (producer judgment):** `schema_retry_exhausted` and per-decision validation codes are
  DELIBERATELY EXCLUDED from `SILENT_NO_VERDICT_CODES` — they mean the reviewer DELIVERED output that its own
  bounded schema retry already adjudicated into a distinct sealed `ok=False` record (the gate-reviewed G3 M-2
  invariant in `test_agent_supervisor_ephemeral_review`), i.e. not "absent evidence". This avoids relabeling a
  delivered failure as silence and keeps the out-of-scope ephemeral suite green.

## Test evidence
- **M0-T039 freeze baseline (20-module unittest):** `Ran 1185 tests … OK (skipped=2)`, 0 failures, Python 3.11.9
  (base 1178 post-P1 + 7 new P6 tests). ≥1165 satisfied.
- **Separate `test_agent_supervisor_ephemeral_review`** (exercises the edited module; NOT in the 20-module set):
  `Ran 31 tests … OK` (stays green — the narrowing preserves the G3 M-2 invariant).
- **CI supervisor-bridge parity (full pytest `tools/test_agent_supervisor_*.py`):** `1503 passed, 2 skipped`.
- **Lint:** `ruff 0.13.0` reports one pre-existing `F401 'os' imported but unused` in
  `test_agent_supervisor_reviewer.py:30` — the `os.` uses are inside the `FAKE_CODEX = textwrap.dedent(...)`
  embedded-script STRING, so the module-level import is dead; this is **pre-existing** (identical F401 at base
  `4083d2c`), **not introduced by P6** (P6's diff to that file is +185/−0, no import changes). CI's ruff runs
  only in `services/api` (`working-directory: services/api`), so `tools/` is not CI-ruff-checked; no new lint.
- **Non-vacuity (producer, reproduced):** neutralizing the re-dispatch/STOP guard makes P6-SC1(×2)/SC2/SC4-silent(×3)
  FAIL (6 failures) while SC3(×2) + SC4-adjudicated (guard-independent paths) stay OK; restoring → all green.

## Scope discipline
`git diff --name-only 4083d2c e24b0102` = exactly `tools/agent_supervisor/ephemeral_review.py`,
`tools/test_agent_supervisor_reviewer.py`, `project-control/reports/M0-T061-producer-report.md`
(`codex_reviewer.py`/`review_cadence.py` allowed but untouched). Supervisor-freeze respected; the seam is
in-scope (no `loop.py`/`claude_runner.py` edit).

## Verdict
Scoped P6 correction implemented, fail-closed, covered, non-vacuous, with a correct silence/adjudicated-failure
distinction. **PASS** (self_check; independent confirmation is G3 + G5).
