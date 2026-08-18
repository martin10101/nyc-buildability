# M0-T072 G5 security review — condensed verdict record (round 1)

CONDENSED transcription by the orchestrator (report-preservation rule): captures
the reviewer's verdict and every SEC finding; the full verbatim return is in the
session task-notification record. NOT labeled verbatim. Reviewer: independent
security-reviewer subagent, read-only. Round-1 verdict evolved BLOCKED (moving
target) → FAIL at `ec8bc58`; both are closed in the rework at `be3a599`.

## Verdict: BLOCKED, then FAIL at ec8bc58 — all blocking items closed at be3a599

- **SEC-CRITICAL (process):** G5 was dispatched against an unheld head — the
  worktree advanced and production files were edited mid-review. FIX: the
  orchestrator now holds the worktree for the review window and re-dispatches at
  a single frozen identity (this re-review is at held `be3a599`).
- **SEC-MAJOR (open at ec8bc58, CLOSED at be3a599):** manifest coverage-downgrade
  bypass — a self-consistent manifest with `patterns: []` passed the production
  check leaving all package files unverified. Closed by `manifest_patterns_mismatch`
  + folding `patterns` into the recorded digest; regression test
  `test_patterns_mismatch_fails_closed` added (the SEC-MINOR-3 "fix ships without a
  test" item is thereby also closed).
- **SEC-MINOR items:** record-manifest `--out` could target the protected config
  (closed — refuses out==config and excluded basenames, verifies before write);
  malformed manifest tracebacks (closed — `manifest_unreadable` fail-closed);
  doctor exit-0/`--manifest`-less surfaces documented; TOCTOU + `require_verified`
  zero-callers noted as pre-existing, outside D-017-R039..R053 scope.
- **Separate defect-lane recommendation (outside this task):** the
  `Authenticated Users: Modify` ACL on `C:\SupervisorController\tools\agent_supervisor`
  is what makes the SEC-MAJOR attack class trivial; the reviewer recommends a
  separate defect-lane item — the orchestrator records this as a follow-up
  (does NOT block M0-T072, which is repository code; the ACL is an owner-present
  live-host hardening step handled in the Stage 2 runbook §7 hardening option).

**Verified clean:** protected config byte-identical (`6aef12a9…`), no write path;
model_selection.toml exclusion intact; `doctor --live` sole provider-contact path
(now also gated on a passing manifest check); no secrets; recorded manifest leaks
no absolute path; runbook free of `/MIR` and `/PURGE`; qualifying evidence cited
in packet and commit.
