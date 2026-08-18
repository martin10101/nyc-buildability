VERDICT: PASS

# Independent directive-compliance verification — M0-T070 under D-014

Verifier: directive-compliance-verifier (independent, read-only; producer = orchestrator).
Frozen head `6aae5857fdcdf55f5197e542013bdc81f8035d14` (verified: `git -C wt-m0t070 rev-parse HEAD` == 6aae585). All 30 evidence-map rows evaluated against primary repository evidence (the diff `de2f224..6aae585`, source files, test files, and test execution). Producer reports were treated as unverified claims.

**Reproduced harness results (read-only, from wt-m0t070):**
- `python -m pytest tools/test_agent_supervisor_command_authority.py -q` → **29 passed** (all named classes present, listed below)
- Full supervisor suite `pytest tools/test_agent_supervisor_*.py` → **1557 passed, 2 skipped, 0 failed** (125s) — M0-T039 freeze baseline (≥1165) re-established
- `tools/test_directive_compliance.py` → OK, exit 0; `tools/test_project_control.py` → all 23 groups passed, exit 0; `tools/test_directive_reminder.py` → 12 tests OK, exit 0
- `python tools/validate_directive_compliance.py --check` → exit 0 (registry VALID)
- Source digest: `sha256(source-001.md)` = `7628740e1a19…596f6` == manifest `content_digest_sha256` ✓

**Defects confirmed from source (root cause):** Defect A — baseline `cli.py:_run_loop` (de2f224 line 2487) called `TaskAuthority.from_packet(...)` without `documented_test_commands`, while `from_packet` (policy.py line 892) accepts that kwarg defaulting to `()`; the documented-test AUTO tier was unreachable in production. Defect B — baseline `broker.revoke_all` (lines 665-688) flips approval records to REVOKED but never touches `queued_asks`, and `cmd_status` read `open_asks()` (`WHERE answered_at_utc=''`) unconditionally, so revoked requests stayed "open." Both are real.

| id | status | primary evidence |
|---|---|---|
| D-014-R009 | PASS | commit 6aae585 adds exactly one task (`project-control/tasks/M0-T070.json`); branch `task/M0-T070-supervisor-authority-repair`; worktree wt-m0t070 |
| D-014-R010 | PASS | `M0-T070-incident-evidence.md` (85 lines, audit seq 4-6 + read-only journal facts) + bounded packet `M0-T070.json` both committed |
| D-014-R012 | PASS | full diff `de2f224..6aae585` is within wt-m0t070 allowed_paths + control-plane; session15-acc clean; wt-m0t063 `status --porcelain` empty |
| D-014-R013 | PASS | tests reproduced above; independent gates (this review + G3/G5) in progress |
| D-014-R014 | PENDING-EXTERNAL | commit 6aae585 exists locally; push + PR are external acts not verifiable from read-only local checkout |
| D-014-R015 | PENDING-EXTERNAL | nothing merged (head only on `task/M0-T070…`; origin/main still 5c71fe0); stop-before-merge + return are ongoing/future acts |
| D-014-R016 | PASS | no `tools/repo_*.py` in diff; wt-m0t063 clean at de2f224; nothing merged; no protected-config write; policy strengthened not weakened |
| D-014-R017 | PASS | `schemas/task_packet_commands.schema.json` + `policy.validate_documented_test_commands` (line 881) + `SchemaValidatorLockstepTests` (4 tests pass) |
| D-014-R018 | PASS | `cli.production_task_authority` used by `_run_loop` (cli.py line 2544); `ProductionWiringTests.test_production_authority_carries_the_packet_commands` passes |
| D-014-R019 | PASS | `validate_documented_test_commands` raises PolicyError on every malformation; `ValidatorFailClosedTests` (8 tests) pass |
| D-014-R020 | PASS | `M0T063FixtureTests.test_every_intended_command_is_auto_documented_test` passes; existing S4.1 tier, reason_code `documented_test_command`, advisory-eligible |
| D-014-R021 | PASS | `test_every_altered_or_injected_variant_is_never_auto` (13 variants ASK/HARD_DENY) + `test_a_command_outside_the_task_authority_is_not_auto` pass |
| D-014-R022 | PASS | `NoBroadGrantTests` (3 pass); diff grep shows no allowlist/settings-bypass/always-allow; cap `MAX_DOCUMENTED_TEST_COMMANDS=16`; closed char profile |
| D-014-R023 | PASS | AST pin asserts `_run_loop` calls `production_task_authority`, NOT `from_packet`/`TaskAuthority` + validator-in-path AST test pass |
| D-014-R024 | PASS | `broker.revoke_all`→`journal.resolve_ask("ask_"+id)` (UPDATE, never DELETE, durable_state.py line 619); `cmd_status` read-time reconcile; history-preservation test passes |
| D-014-R025 | PASS | `RevokeStatusLifecycleTests`: pending→open, revoke_all→revoked, pending-approvals→0, status open_asks `[]`, pre-fix journal read-only labeling, audit_chain_ok/journal_ok asserted — all pass |
| D-014-R026 | PASS | `fixtures/m0_t063_documented_test_command.json` (4 intended_auto + 13 must_not_auto) + `M0T063FixtureTests` prove intended AUTO / variants not |
| D-014-R027 | PASS | reproduced: supervisor 1557 passed / 0 failed; DCV/PC/DR suites exit 0; validator VALID |
| D-014-R028 | PASS | `M0-T070-before-after-evidence.md` (no A1 re-run); executable BEFORE test `test_the_pre_fix_construction_reproduces_the_a1_failure` passes |
| D-014-R029 | PASS | `config.toml` path appears only in verbatim directive text; no code writes it; not in repo |
| D-014-R030 | PASS | `model_selection.toml` appears only in verbatim directive text; no code writes it |
| D-014-R031 | PASS | DB not opened by verifier; `resolve_ask` called ONLY by `revoke_all` (grep: broker.py:684), not run against A1; `cmd_status` read-only; incident report documents `mode=ro&immutable=1` |
| D-014-R032 | PASS | `git -C wt-m0t063 status --porcelain` empty; `git -C wt-m0t063 rev-parse HEAD` == de2f224 |
| D-014-R033 | PASS | validator fails closed (PolicyError refuses run); no classification tier changed; adversarial variants remain ASK/HARD_DENY (tests) |
| D-014-R034 | PASS | nothing merged (`git branch --contains 6aae585` = task branch only); `C:\SupervisorController` absent from repo/diff |
| D-014-R035 | PASS (with discrepancy — see below) | `git -C wt-m0t070 reflog` shows 3× "reset: moving to HEAD" (all to de2f224); HEAD never moved off de2f224 until the single commit 6aae585; no force/clean; wt-m0t063 + runtime evidence intact |
| D-014-R036 | PASS | diff `--name-only` has no `repo_fingerprint`/`repo_index`/`code_graph`/`context_pack` files |
| D-014-R037 | PASS | rollback scoped to branch + wt-m0t070 removal only, A1/runtime untouched — documented in `M0-T070-G0-contract-review.md` and producer report |
| D-014-R038 | PENDING-EXTERNAL | SUPERVISOR_REPAIR_PR_READY return + PR body are live acts not present at this head; no dedicated committed return-report file exists (see discrepancy 2) |
| D-014-R039 | PASS | wt-m0t063 clean at de2f224; reflog shows no supervisor start/resume/revoke against wt-m0t063 in the D-014 session window (all wt-m0t063 activity predates 01:42) |

Named test classes verified present AND passing (unittest -v): `SchemaValidatorLockstepTests` (4), `ValidatorFailClosedTests` (8), `ProductionWiringTests` (5), `M0T063FixtureTests` (5), `NoBroadGrantTests` (3), `RevokeStatusLifecycleTests` (5) = 29 tests. Schema/validator/profile confirmed matching by reading both: schema `maxItems 16 / maxLength 512 / pattern ^[A-Za-z0-9][A-Za-z0-9 ._/:=@+,*?\[\]-]*$` equals `policy.MAX_DOCUMENTED_TEST_COMMANDS` / `MAX_DOCUMENTED_TEST_COMMAND_CHARS` / `_DOCUMENTED_COMMAND_PROFILE.pattern`.

**Discrepancies between producer claims and primary evidence:**

1. **R035 reflog claim is factually inaccurate (material to note; not a substantive breach).** The evidence-map stated the "git reflog of wt-m0t070 shows worktree add + commits only." Primary evidence contradicts this: the reflog contains **three** `reset: moving to HEAD` entries (2026-08-18 01:42:51, 02:18:37, 02:18:52), each resolving to the base de2f224 before the single commit 6aae585. These are non-destructive no-ops — HEAD never moved backward, no history was rewritten, no force/clean occurred, and wt-m0t063 + runtime evidence are provably intact — consistent with `git stash push`'s internal `reset --hard`. I rule R035 PASS on the prohibition's protected interest (no destructive cleanup/history rewrite/evidence loss). However, if the owner enforces R035 as a strict literal ban on any `git reset` invocation, the reflog is primary evidence that `git reset` (or a stash that wraps it) was used, and the producer's "commits only" characterization should be corrected. Flagging for orchestrator/owner adjudication.

2. **R038 has no dedicated committed return-report file.** The requirement's `required_evidence` is a "committed return report copy under project-control/reports/." The committed report set at the reviewed head lacks a `SUPERVISOR_REPAIR_PR_READY` return document. Marked PENDING-EXTERNAL; the committed-copy sub-requirement remains open for the return cycle.

3. **Minor (non-blocking):** `M0-T070-G0-contract-review.md` line 25 calls the fixture a "new replay-corpus fixture," but the fixture is committed at `tools/agent_supervisor/fixtures/m0_t063_documented_test_command.json` (NOT in `replay_corpus/`), which the producer report correctly states. Documentation wording inconsistency only; the fixture location and content are correct.

**Prohibited-action evidence:** nothing merged/accepted/activated — head 6aae585 is contained only by `task/M0-T070-supervisor-authority-repair`; origin/main remains 5c71fe0; `C:\SupervisorController` and the two protected `.toml` paths are absent from the repo/diff; the live A1 runtime DB was not opened by this review and no code path in the diff writes to it outside the un-executed `revoke_all`.

**Overall:** every verifiable requirement is PASS; the only non-PASS rows are the three genuinely external acts (R014 push/PR, R015 stop-before-merge/return, R038 return message), correctly PENDING-EXTERNAL at this head. Verdict: **PASS**, subject to the orchestrator recording discrepancies 1 and 2 (R035 evidence-map wording correction; R038 committed-return-copy owed at the return cycle).

---

*Orchestrator post-verification actions (recorded 2026-08-18, after this report): discrepancy 1 — the evidence-map R035 row was corrected to describe the three stash-internal no-op reset entries transparently, and the matter is disclosed for owner adjudication in the return report; discrepancy 2 — the committed return copy is delivered as `project-control/reports/M0-T070-return-report.md` in the return cycle; discrepancy 3 — the G0 wording slip is noted in the return report (the recorded G0 gate artifact itself is left unedited).*
