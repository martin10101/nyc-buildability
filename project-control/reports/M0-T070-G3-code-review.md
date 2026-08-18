VERDICT: PASS

# G3 Code Review — M0-T070 (Supervisor corrective repair, directive D-014)

**Reviewer:** code-reviewer (independent, read-only)
**Worktree:** C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t070
**Frozen HEAD:** 6aae5857fdcdf55f5197e542013bdc81f8035d14 (base de2f224) — verified match.
**Scope reviewed:** `git diff de2f224..6aae5857 -- tools/` (7 files, all in `allowed_paths`) + directive D-014 requirements + evidence reports.

## Summary

Both source-confirmed defects are repaired correctly, minimally, and fail-closed. Defect A (production `_run_loop` never supplied `documented_test_commands`, so the S4.1 AUTO tier was unreachable) is fixed by a new `production_task_authority` constructor that routes the packet through a deterministic fail-closed validator, plus an AST guard that makes the exact regression a test failure. Defect B (revoke-all left `queued_asks` rows unresolved, so `status` kept listing revoked requests as open) is fixed on both the write path (`revoke_all` → `resolve_ask`, rows preserved as history) and the read path (`cmd_status` reconciles ask rows against approval-record state at read time, genuinely read-only). All 29 new tests pass; the full supervisor suite reproduces the M0-T039 freeze baseline exactly (1557 passed, 2 skipped, 0 failed). No contract is broken and no forbidden path, external config, or the A1 runtime DB is touched.

## Reproduction (independently executed from the worktree)

- `python -m pytest tools/test_agent_supervisor_command_authority.py -q` → **29 passed** (Python 3.11.9).
- `python -m pytest tools/test_agent_supervisor_*.py -q` → **1557 passed, 2 skipped in 142s** — matches the producer claim and exceeds the ≥1165/0 freeze baseline.
- Root cause confirmed: `project-control/tasks/M0-T063.json` contains **no** `documented_test_commands` field (grep count 0), and pre-fix `_run_loop` built `TaskAuthority.from_packet(...)` without that kwarg (diff line 138).

## Findings (ordered by severity)

### F1 — LOW (comment/test-naming honesty; bounded latitude, not an AS-6 violation)
`NoBroadGrantTests.test_no_wildcard_program_can_be_documented` (tools/test_agent_supervisor_command_authority.py:691-695) asserts only that entries whose **first character** is a wildcard (`"* tools/test.py"`, `"? tools/test.py"`, `"*"`) are rejected. They are rejected solely because `_DOCUMENTED_COMMAND_PROFILE` (policy.py:872-873) requires a leading `[A-Za-z0-9]`. A program token with a wildcard **after** a leading alphanumeric — e.g. `py* tools/test.py` or `python? tools/test.py` — passes the profile, passes `parse_command` (no shell metacharacter, single segment), and at classification time `_shape_matches` (policy.py:838-852) does `fnmatch("python", "py*") → True`, broadening the executable match. So the field admits a slightly-wider-than-literal executable shape, and the test name overstates ("no wildcard program").

Why this is not a blocker: the latitude is bounded per task (≤16 entries via `MAX_DOCUMENTED_TEST_COMMANDS`, single non-metacharacter segment, exact remaining-token match) and is inherited from the **pre-existing** shared `_shape_matches`/standing-grant mechanism, not introduced by this diff. It is not a general Bash allowlist, broad executable grant, settings bypass, or always-allow — the actual targets of AS-6 (D-014-R022). Recommend a non-blocking follow-up: either forbid `*`/`?` inside the program (first) token in the validator, or rename the test to state the real guarantee ("a wildcard cannot be the program's first character").

### F2 — INFO (implicit prefix contract; correct today)
The read-time reconciliation is coupled to the literal `ask_` id prefix (cli.py:1361; mirrored in broker.py:684 which reconstructs `ask_<request_id>` from `approval/<request_id>`). This is safe now: `ApprovalBroker.defer` is the only minter of `ask_`-prefixed ids (broker.py:518), while loop-origin asks use `rotation_pause/<run>/<cycle>` and `model_chain_exhausted/<run>/<cycle>` (loop.py:1361, 1513) — neither starts with `ask_`, so they correctly stay open (verified by `test_a_loop_origin_ask_without_approval_record_stays_open`). A future ask source adopting the `ask_` prefix without a matching `approval/` record would still fail safe (stays open); only one carrying a colliding non-pending `approval/` record could be hidden, and none exists. Worth a one-line note for future maintainers; no action required.

### F3 — INFO (intended behavior broadening beyond revoke; not a regression)
Because `approve_once`/`deny_request` (broker.py:610+, 642+) also never resolved the `queued_asks` row, the read-time reconciliation now moves **any** non-`PENDING_OWNER` broker ask (APPROVED_ONCE / DENIED / CONSUMED / REVOKED / INVALIDATED) out of `open_asks` into the new `resolved_asks` (cli.py:1363-1370). This is correct — an already-answered request is not an actionable owner question — and is not a regression, since those rows were already unresolved before the fix. No in-tree consumer depends on the old `open_asks` contents: a repo-wide search finds the status JSON is consumed only by the CLI operator view and the new tests (no dashboard/project-control parser reads `open_asks`). Recording as an intended, additive change (new `resolved_asks` key; filtered `open_asks`).

### F4 — INFO (non-code; working-tree state for the orchestrator)
At the frozen SHA the reviewed **code** tree (tools/) matches 6aae5857 exactly, but the working tree carries uncommitted control-plane churn: `state.json` (only `updated_at` bumped), `tasks/M0-T070.json` (re-serialized to 1-space indent, only `updated_at` changed — `allowed_paths`/scope substantively identical to HEAD), and untracked `reports/M0-T070-evidence-map.json` + `reports/M0-T070.json`. None touch code under review. Flagging so the orchestrator reconciles these before an accept stamps material identity; `reviewed_sha == HEAD` holds for the code.

### Positive confirmations (not defects)
- Malformed field **refuses the run**: `production_task_authority` calls `validate_documented_test_commands(packet)` (cli.py:2531) which raises `PolicyError` on wrong container/entry type, empty/padded, oversize, duplicate, out-of-profile chars, or anything `parse_command` flags (substitution/metacharacter/multi-segment/parse error) — policy.py:881-937. `_run_loop` invokes it at construction (cli.py:2544), so a bad packet stops before any worker launch. Double-gated: `_auto_test_command` independently bails on `has_substitution`/`has_metacharacter` and requires an exact `_shape_matches` (policy.py:1424-1431).
- Read path is genuinely read-only: `cmd_status` performs only SELECT-backed reads (`all_state`, `open_asks`) and mutates only fresh in-memory `to_dict()` dicts (models.py:99-100 returns a new `asdict`); no journal write. Proven by `test_a_pre_fix_journal_reports_revoked_history_without_mutation` (row still unanswered after status), satisfying prohibition 3 for the un-mutatable A1 DB.
- `resolve_ask` (durable_state.py:619-638) UPDATEs (never DELETEs), preserving `request_digest`/`question`; transaction-safe (`BEGIN IMMEDIATE`/`COMMIT`/`ROLLBACK` on the `isolation_level=None` autocommit connection, matching the existing `enqueue_outbound` pattern); idempotent via `rowcount` + `WHERE answered_at_utc=''` (proven by `test_resolve_ask_is_idempotent_and_reports_misses`).
- The AST wiring test (test file:577-599) is robust: it fails if `_run_loop` calls anything named `from_packet` or `TaskAuthority`, or omits `production_task_authority` — making the precise original defect a test failure.
- No scope excess in code: the tools/ diff is exactly the 7 `allowed_paths` files; no `forbidden_paths` entry (`repo_fingerprint.py`, `code_graph/`, `.github/`, `services/`, `apps/`, `.claude/`) is touched; the external prohibited config files and A1 SQLite DB are not in the diff.

## Explicit answers to the required questions

1. **Does the wiring fix make the documented-test tier reachable in production?** YES. `_run_loop` now builds authority via `production_task_authority` (cli.py:2544), which passes `documented_test_commands=validate_documented_test_commands(packet)` into `from_packet` (cli.py:2531). The intended M0-T063 command classifies AUTO `documented_test_command` through that authority (verified: `test_the_intended_command_evaluates_auto_through_that_authority` and `test_every_intended_command_is_auto_documented_test`), and the AST guard prevents silent regression.

2. **Can any malformed packet entry gain AUTO?** NO. Every malformation class raises `PolicyError` (fail closed) and never reaches classification; even if it did, `_auto_test_command` re-checks substitution/metacharacters and requires an exact token match. Distinction: a *well-formed* wildcard-in-program shape (F1) is a bounded design latitude, not a malformation, and still cannot become a general allowlist.

3. **Does status reconciliation ever hide a genuinely-open owner question?** NO. An ask leaves `open_asks` only if its `approval/<id>` record exists **and** its status is not `PENDING_OWNER` (cli.py:1363) — i.e., the owner already answered/revoked it. All loop-origin asks (no approval record) and all still-`PENDING_OWNER` broker asks remain in `open_asks`. No id collision hides a live question (F2). Resolved entries are still displayed (labeled `actionable:false`), not dropped.

4. **Is historical evidence preserved after revoke-all?** YES. `revoke_all` sets the approval record to `REVOKED` and calls `resolve_ask` which UPDATEs the `queued_asks` row (answer `"revoked: <reason>"`) without deleting it; `request_digest`, the question, the REVOKED record, and the audit chain all survive (`test_the_revoked_ask_row_is_preserved_history_not_deleted`, `test_pending_then_revoke_all_then_zero_and_no_open_ask`).

5. **Any scope excess?** None in code — tools/ changes are exactly the 7 `allowed_paths` files; no forbidden path, external config, or A1 DB touched. Remaining diff files (D-014 directive capture, `directives/index.json`, `gates/M0-T070-G0.json`, `state.json`, `tasks/M0-T070.json`, `M0-T070-G0-contract-review.md`) are orchestrator control-plane artifacts consistent with the control lifecycle. Uncommitted working-tree files (F4) are gate-prep, outside code scope.

## Verdict
**PASS.** The repair correctly and minimally fixes both defects, preserves and strengthens fail-closed behavior, adds adequate tests that pin AS-1..AS-10 (including a durable AST wiring guard), and re-establishes the full supervisor freeze baseline with zero failures and no contract breakage. F1 is a low-severity, non-blocking follow-up (validator latitude / test naming); F2–F4 are informational. (Note: the requirement-by-requirement directive-compliance verification of D-014-R001..R039 is the separate `directive-compliance-verifier` pass, not this G3 code review.)
