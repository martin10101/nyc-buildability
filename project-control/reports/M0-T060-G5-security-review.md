# M0-T060 (P3) — G5 security review — VERDICT: PASS

Independent read-only security-reviewer return, preserved verbatim (transport decoding only). Reviewer did NOT
produce the code. Reviewed SHA `a9eb1b7f9e2eb79fc8652d5e1c6cef45126be021` (== HEAD). Deliverable diff
`20b82ea..a9eb1b7` — loop.py (+38), test_agent_supervisor_loop.py (+52), producer report. Purely additive.
Python 3.11.9.

## VERDICT: PASS
No critical/high/medium findings. One LOW/informational defense-in-depth note (out of P3 scope, non-blocking).
The fail-open is closed: no degraded-containment cycle (by the achieved-kind definition criterion (2) specifies)
can proceed.

## Step 1 — Completeness of the fail-closed set (enumeration)
`run_result.containment` = `container.report().kind` (claude_runner.py:1261); `.kind` ∈:
- `"job_object"` (process.py:550) → **PROCEEDS** (only value that does).
- `"taskkill"` (process.py:545/553/572 — incl the honest `adopt()` degrade when the Job Object can't be
  created/assigned = the criterion (2) scenario) → **STOPS**.
- `"process_group"` (process.py:542, non-Windows) → **STOPS**.
- `""` (dataclass default, claude_runner.py:924, missing attr) → **STOPS** (fail-closed).
- any other string (not producible today) → **STOPS** (exact-constant compare).
`achieved != CONTAINMENT_JOB_OBJECT` against the imported exact constant → anything not provably job-strength
fails closed. **No value wrongly PROCEEDS.**

## Step 2 — No bypass via ordering
`run_unit` called once (1669); `CHECKPOINT_RECEIVED` transition once (1785); the guard (1762-1782) sits
UNCONDITIONALLY between them (no mode/flag gate; supervised and shadow alike). Every earlier return
(resource-gauge 1641, breaker 1657, ambiguous_effect 1715, worker-turnover 1739, no_valid_checkpoint 1745) is a
STOP, never a proceed. **Critically `RunResult.ok` (claude_runner.py:963) checks checkpoint/exit/timeout/graceful-
close but NOT containment** — so a valid-checkpoint + clean-exit + degraded-containment unit has ok=True, is NOT
caught by the `if checkpoint is None or not run_result.ok:` block, and reaches the guard (the dangerous case) →
stops. `run()` (2442-2447) breaks the loop on `result.stopped`; PAUSED_RECOVERY ∉ CYCLE_ENTRY_STATES → no silent
re-entry (owner intervention required). No alternate executor consumes containment. **No path lets a degraded
cycle reach PROCEED/forward without passing the guard.**

## Step 3 — Fail direction
`str(getattr(run_result,"containment","") or "")` → `""` for missing/None → `"" != "job_object"` → STOP; reason
renders `'unknown'`. Correct fail-closed on ambiguity.

## Step 4 — No downgrade / no new surface
Reason interpolates `achieved` (bounded internal constant, `!r`) + `fallback` (`containment_fallback_reason`,
internal ProcessError text — never credentials/env/secrets) into a DATA field (reason/detail), not a shell/SQL/
template sink. Plain f-string. No injection, no secret leak, no redaction concern. The STOP is a hard
CLAUDE_RUNNING → PAUSED_RECOVERY (unsafe_condition) with a synchronous owner touch — not a silent continue, not a
retry loop.

## Step 5 — Consistency with criterion (1)
Criterion (1) (host default containment) lives in cli.py `_check_containment_default()` / `containment_precondition()`
— **cli.py untouched**. P3 adds criterion (2) purely additively in loop.py, placed after the S14 reconciliation so
it masks no paramount stop. No existing stop weakened/reordered.

## Reproduction (read-only)
`AchievedContainmentTests` → 3 passed; loop.py → 106 passed; full supervisor `pytest -k supervisor` → **1509
passed, 2 skipped**, 0 failures (adversarial ambiguous-effect test passes → not masked). Non-vacuous:
`stopped == "containment_degraded"` is set only by this guard.

## Findings
Critical/High/Medium: none. **LOW/informational (out of P3 scope; non-blocking):** the guard gates on achieved
KIND only, not on `ContainmentReport.verified_in_job`. A container reporting kind==job_object with
verified_in_job==False (assign succeeded but the kernel IsProcessInJob proof didn't confirm, or the child exited
before the proof) would PROCEED. NOT the criterion (2) scenario (honest taskkill degrade, caught here), a
near-impossible kernel state, and gating on it risks false-positive stops for fast-exiting units — appropriately
left to future hardening. loop.py:1763 (checks kind) vs process.py:576/607 (verified_in_job recorded, not gated).
**Carried forward as an optional M0-T056 hardening consideration.** N/A axes: cross-tenant/service-role/storage/
SSRF/upload/prompt-injection (containment-only change); least-privilege STRENGTHENED.

## Explicit fail-open statement
By the achieved-containment-KIND definition criterion (2) specifies, NO degraded-containment cycle can proceed
without stopping. The pre-existing fail-open (achieved containment merely recorded and ignored) is closed. The
single `verified_in_job` edge is a documented non-blocking, out-of-scope defense-in-depth note. **VERDICT: PASS.**
