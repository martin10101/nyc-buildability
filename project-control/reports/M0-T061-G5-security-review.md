# M0-T061 (P6) — G5 security review — VERDICT: PASS

Independent read-only security-reviewer return, preserved verbatim (transport decoding only). Reviewer did NOT
produce the code. Reviewed at frozen `HEAD = 77d7162dc8a2b33652f9831968314e56d8a66438`; P6 change = commit
`3c23072` (parent `9239cc3`). Reviewed content verified from the worktree / `git show 77d7162:` (`codex_reviewer.py`,
`policy.py`, `models.py` byte-identical to the main checkout; only `ephemeral_review.py` + `test_agent_supervisor_reviewer.py`
carry P6 changes). Read-only; no git writes. Python 3.11.9.

## Acceptance criteria
- **P6-SC1** silent → exactly one re-dispatch → hard fail-closed STOP w/ recorded reason + visible evidence — PASS (reproduced).
- **P6-SC2** returns on retry → proceeds, no false stop — PASS.
- **P6-SC3** delivered FAIL/BLOCKED (HALT_UNSAFE/STOP_FOR_OWNER) unaffected — PASS.
- **P6-SC4** no downgrade to "proceed"; silence ≠ clean review (3 silent codes + adjudicated) — PASS.
- **P6-SC5** freeze baseline ≥1165/0 + new tests + non-vacuity — PASS (reviewer reran reviewer 81 OK + ephemeral 31 OK;
  full 20-module 1185 OK / 1503 pytest confirmed by orchestrator + G3).

## ⭐ Step 1 — COMPLETE enumeration of every `decision is None` outcome from `CodexReviewer.review()`
`review()` is the sole constructor of `ReviewOutcome`; `decision is not None` only on the success return. `decision is None`
arises in exactly two paths:
- **Path A — model resolution not usable** (`error_code = resolution.reason_code`): `model_not_allowlisted`, `no_selection`,
  `chain_exhausted`, `account_default` — all COULD-NOT-DISPATCH (never ran); NOT in the set; NOT re-dispatched; **each seals
  `ok=False`**. (Advisory-role codes unreachable via primary-role `conduct_ephemeral_review`; `unknown_provider`/`unknown_role`
  RAISE PolicyError → propagate/halt, fail-closed.)
- **Path B — bounded schema retry exhausted** (`error_code = last_error.code`, always the last attempt's code; the literal
  `schema_retry_exhausted` is effectively unreachable/defensive):
  - `review_timeout`, `missing_decision_file`, `provider_rejected_request` → **GENUINE dispatched-SILENCE** → all **IN the set** → re-dispatch→stop. ✓
  - `wrong_field_type`/`not_an_object`/`missing_required_field`/`decision_correlation_mismatch`/… (validate_decision on
    delivered content) → **DELIVERED, self-sealed ok=False** → correctly excluded. ✓

**Explicit fail-open statement:** the only DISPATCHED-but-silent codes are exactly `{review_timeout, missing_decision_file,
provider_rejected_request}` — all three ARE in `SILENT_NO_VERDICT_CODES`. Every other `decision is None` code is a delivered
self-sealed failure or a could-not-dispatch refusal, and **every one seals `ok=False, decision=None`** (guaranteed by
`ReviewOutcome.ok = decision is not None and not error_code`); `project_control.accept` fail-closes on any non-PASS record.
**NO `decision is None` fail-open path remains.** Over-inclusion (parseable-but-non-object JSON → `missing_decision_file` →
re-dispatched) is in the fail-closed direction, not a hole.

## Step 2 — No downgrade to "proceed"
Retry gate is `if redispatch.decision is None:` (value, not code) → ANY no-verdict on retry (even a non-silent code) routes to
`_silent_reviewer_record` (ok=False). Never ok=True. A DELIVERED retry verdict (decision not None ⟹ error_code=="" ⟹ ok=True)
is sealed as the real verdict, tagged `reviewer_redispatched_after_silence`; its VALUE still drives `map_decision_to_tier`
downstream ("proceed" = seal the real verdict, not accept the task). ✓

## Step 3 — Bounded / no infinite retry
Single `if` guard, no loop/recursion; exactly one re-dispatch; a second silence returns the terminal STOP record (no third
dispatch). Each `review()` internally bounded (max_attempts=3) → ≤2×3 launches; attempts=first+redispatch ≤6. ✓

## Step 4 — Visibility / non-repudiation
`_silent_reviewer_record`: ok=False, decision=None, distinct `error_code="reviewer_silent_no_verdict"`,
notify_events=[reviewer_silent_redispatched, reviewer_silent_no_verdict, reviewer_paused_fail_closed], error_message embeds
underlying `[{code}]: {message}`; `.finalize()`-sealed (redaction + digest) + `journal.append` like `_refusal_record`.
Round-trip confirmed (`journal.verify()` True). ✓

## Security/regression/provenance
- **Redaction/secret safety:** underlying reviewer message doubly protected (upstream provider_failure_reason redacts + bounds
  to 600 chars; `finalize()` runs `redact_structure`). No packet echo/secret leak. ✓
- **Injection/SSRF/least-privilege:** P6 adds no external-input/write path; re-dispatch reuses the already guard+budget-passed
  packet; reviewer stays a fresh `--sandbox read-only` process; notify_events/error_code hardcoded. ✓
- **Additivity:** non-silence path keeps `extra_notify=[]` → step-4 seal byte-identical to pre-P6; delivered FAIL/BLOCKED
  untouched; ephemeral suite 31 OK. Additive to accept(), not a duplicate. ✓
- **Scope/freeze:** smallest durable set within allowed_paths; AD-093 qualifying evidence (session-14 four-silent-reviewers /
  d45f330) cited; SHADOW-ONLY (activates nothing; R595 untouched). ✓

## Defects
None (critical/high/medium/low). INFO-1 (pre-existing, not P6): `account_default` empty-allowlist → reviews never run, always
fail closed — safe direction, out of scope. INFO-2 (cosmetic): exhausted-retry `tier.reason_code` literal vs `error_code`
actual — no functional impact (P6 keys off error_code).

## Verdict
**PASS.** The P6 control correctly and completely closes the "gate dispatched, no verdict returned" fail-open; the set is
complete for genuine dispatched-silence; every excluded `decision is None` code fails closed; re-dispatch bounded to one; no
downgrade; terminal STOP sealed/journaled/redacted/notified. Adversarial enumeration found NO residual fail-open path. No
required rework. (Directive compliance recorded separately by the independent directive-compliance-verifier — PASS, empty D-010
set.)
