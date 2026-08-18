# M0-T070 — Before/after evidence (D-014 AS-12, bounded fixtures only)

No part of this evidence repeats the real A1 run. Everything below comes from
the committed M0-T063-shaped fixture
(`tools/agent_supervisor/fixtures/m0_t063_documented_test_command.json`) and
the test suite, executed on the repair branch at Python 3.11.9 / pytest 8.4.2
(Windows 11). The BEFORE construction is kept **executable forever** as
`M0T063FixtureTests.test_the_pre_fix_construction_reproduces_the_a1_failure`.

## 1. Classification, before vs after (defect A)

Intended command (the packet's first documented test command):
`python tools/test_repo_fingerprint.py`

| construction | tier | reason_code |
|---|---|---|
| BEFORE — `TaskAuthority.from_packet(packet, …)` exactly as pre-fix `_run_loop` called it (no `documented_test_commands`) | **ASK** | `undocumented_command` — the recorded A1 outcome (audit seq 4–6) |
| AFTER — `cli.production_task_authority(packet, …)` (the constructor `_run_loop` now uses) | **AUTO** | `documented_test_command` (existing S4.1 tier, advisory-eligible) |

All 13 adversarial variants stay refused through the AFTER authority:

| variant | classification |
|---|---|
| changed executable (`python3 …`, `pytest …`) | ASK:undocumented_command |
| changed arguments (`-k fingerprint`, `….pyc`) | ASK:undocumented_command |
| appended command (`; python tools/evil.py`) | ASK:undocumented_command |
| appended destructive command (`&& rm -rf .`) | **HARD_DENY**:recursive_or_wildcard_delete |
| pipe into shell (`\| sh`), redirection (`> results.txt`) | ASK:undocumented_command |
| command/backtick substitution (`$(…)`, `` `…` ``) | ASK:undocumented_command |
| undocumented commands (incl. broader pytest, bare interpreter) | ASK:undocumented_command |

## 2. Checkpoint progression, before vs after (bounded)

- BEFORE (recorded, run_M0_T063_A1): PREFLIGHT → worker requested its three
  baseline/test commands → all deferred ASK → worker exited rc 1 → **no
  structured checkpoint**, `no_valid_checkpoint`, PAUSED_RECOVERY. Zero
  checkpoints progressed; the authorized product task could not complete.
- AFTER (bounded proof, no live run): with the identical packet shape now
  carrying its three test suites + pytest form, the loop's own classifier
  (`pol.evaluate`, the function `_run_loop`'s broker consults) returns AUTO
  for exactly those commands — the requests that killed A1 no longer defer,
  so the run does not stop at the first baseline command. The
  `RevokeStatusLifecycleTests` prove the surrounding broker lifecycle
  (defer → revoke → truthful status) on a real journal + audit chain in a
  temp runtime. A live re-run of A1 stays owner-controlled (D-014
  prohibition 4 / "Do not restart A1").

## 3. Revoke/status truthfulness, before vs after (defect B)

| step | BEFORE | AFTER |
|---|---|---|
| pending request queued | `pending-approvals` 1, `status.open_asks` 1 | same (unchanged) |
| `revoke-all` | approval record REVOKED; `queued_asks` row untouched | approval record REVOKED **and** ask row durably resolved (`answer: "revoked: …"`), row preserved |
| `pending-approvals` | 0 | 0 (unchanged) |
| `status` | **still lists the revoked request under open_asks** (live A1 journal shows exactly this) | `open_asks: []`; row absent (resolved durably) — or, for a pre-fix journal that must not be mutated, listed under `resolved_asks` with `actionable: false`, `approval_status: REVOKED` |
| audit chain / journal integrity | ok | ok (asserted in tests) |
| loop-origin asks (rotation pause, model-chain stop) | open | **still open** — reconciliation only touches broker-linked asks |

The pre-fix-journal behavior is proven read-only by
`test_a_pre_fix_journal_reports_revoked_history_without_mutation`, which
rebuilds the exact live A1 shape (unanswered ask + REVOKED record), asserts
`status` shows zero open asks and one labeled revoked-history entry, and then
asserts the journal row is **still unanswered** afterward.

## 4. Bounded runtime/token measurement

Provider token usage is not applicable to this repair (no model call is made
by validation or classification; per D-013 discipline, no token savings are
claimed from estimates). Measured runtime on the fixture (N=2000 iterations,
`time.perf_counter`, same machine as the suites):

- `validate_documented_test_commands(packet)`: **≈0.31 ms/call**
- full `pol.evaluate` of the intended command through the AFTER authority:
  **≈3.7 ms/call**

Both are per-run/per-request one-offs, negligible against a supervised cycle.
The material saving is structural and observed, not estimated: A1 burned a
full worker launch + owner recovery cycle (05:18–05:30Z) without producing a
checkpoint; with the documented-test tier reachable, those three requests do
not stop the run.

## 5. Suite evidence

- New module `tools/test_agent_supervisor_command_authority.py`: **29 passed**
  (0.87 s).
- Full supervisor suite `pytest tools/test_agent_supervisor_*.py`:
  **1557 passed, 2 skipped, 0 failed** (118 s) — re-establishing the
  M0-T039 freeze baseline (≥1165, 0 failures) with the repair applied.
- Project-control + directive-compliance suites: recorded in
  `M0-T070-producer-report.md`.
