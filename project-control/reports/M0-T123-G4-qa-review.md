# M0-T123 — G4 QA review (VERBATIM reviewer return; saved by the orchestrator, transport entity-decoding only)

Second full-suite run: **2870 passed, 2 skipped** — identical count (no flakiness across two full runs; launch_seam also deterministic across two runs). All evidence gathered. Here is my G4 report.

---

# G4 QA Gate Report — M0-T123 (Resume-path defect: rotation-ceiling + cwd enforcement seam)

**Gate:** G4 (independent QA) — READ-ONLY
**Reviewer:** qa-engineer (independent; producer = supervisor-resume-path-producer)
**Frozen head:** `10cebf0`; reviewed material identity = work commit `6aada29` (verified ancestor of head; delta head-vs-material is control-plane only)
**Directive regime:** in-regime, `D-024:ALL` (20 rows R327–R346)

## 1. Test reproduction (I ran everything)

Environment: `Python 3.11.9, pytest-8.4.2` (supervisor floor).

| Run | Result | Claim |
|---|---|---|
| `launch_seam --collect-only` | **45 tests collected** | 45 ✓ |
| `launch_seam -q` (run 1) | **45 passed in 15.48s** | 45 ✓ |
| `launch_seam -q` (run 2) | **45 passed in 15.00s** | deterministic ✓ |
| related 12-suite list | **533 passed in 92.93s** | 533 ✓ |
| full `test_agent_supervisor*.py` (run 1) | **2870 passed, 2 skipped in 247.47s** | 2870/2 ✓ |
| full suite (run 2, flakiness) | **2870 passed, 2 skipped in 628.26s** | no nondeterminism ✓ |
| full `--collect-only` | **2872 collected** (= 2870 + 2 skips) | 2872 ✓ |
| fixture-hygiene `test_all_committed_fixtures_free_of_home_prefixes` | **PASSED** | ✓ |
| `modularity_check --check` | **selected 330; failures 0; warnings 10** (launch_seam.py not warned) | 0 failures ✓ |

No flakiness across two full runs and two launch_seam runs.

## 2. Chain arithmetic (requirement 6)

`2814 (T122 baseline, verified in my M0-T122 review) + 56 = 2870`. Breakdown confirmed by `--collect-only`: **launch_seam 45 + session_continuity 7 + loop_turnover 4 = 56** (all three are NEW files). `restart_channel` still **34** (unchanged from T122). The +56 is therefore fully accounted for by the three new files; the modified existing test files (loop/crash/endurance/restart_channel) net-zero test-count change. No hidden drift. **PASS.**

## 3. AS → test adequacy (test bodies read)

| AS | Named test(s) | Genuine? | Notes |
|---|---|---|---|
| AS-1 red/green | `RunnerChokepoint::test_AS1_over_ceiling_resume_refuses_before_launch` (real run_unit, fake exe, 640k → refuse before Popen); `PreDispatchCeilingSeam::test_AS1_pre_fix_path…` (RED: seeded over-ceiling state restored) + `…fixed_seam_sheds…` (GREEN: shed clears session, consumes flag, `over_ceiling_session_shed` audit event) + `…sheds_on_durable_flag_even_when_telemetry_unknown` | **YES** | Fixture faithfully carries the live shape — see §5 |
| AS-2 ceiling matrix | `LaunchSeamUnit::test_AS2_at_threshold_exactly_rotates_never_resumes` (400000→ROTATE), `_above_threshold_rotates` (640224), `_below_threshold_resume_permitted` (399999→None), `_missing_telemetry_fails_closed_never_assumed_below`, `_fresh_launch_has_no_ceiling` | **YES** | Genuine boundary: 399,999 permitted / 400,000 refused; missing telemetry fails closed, not assumed-below |
| AS-3 cwd + Windows forms | `LaunchSeamUnit::test_AS3_*` (drive-case + slash fold, primary-checkout named specifically, mismatch, unbound/empty); `RunnerChokepoint::test_AS3_cwd_primary_checkout/_mismatch`; `FixtureRegression::test_AS3_transcripts_show_the_cwd_isolation_defect` | **YES** (with LOW gap) | `normalize_path` = `normcase(normpath())` folds whole-path case + slashes on Windows → masquerade blocked. UNC/8.3 forms untested (LOW, §6) |
| AS-4 rotation preservation | `PreDispatchCeilingSeam::test_AS4_a_below_ceiling_session_is_not_shed` / `_shed_is_idempotent_second_call_is_noop`; shed freezes old session (`_provider_session_id==""`) + fresh new session | **PARTIAL** | exactly-once + freeze + below-ceiling asserted; the seven R337 properties NOT each individually asserted here — §6 MEDIUM-LOW |
| AS-5 call-site closure + removal | `ReachabilitySweep::test_run_unit_seam_precedes_the_only_worker_popen`, `_the_only_worker_dispatch_popen_is_run_unit_and_it_is_seam_guarded` (dispatcher-set closure), `_run_loop_wires_*`, `_run_wires_the_pre_first_dispatch_ceiling_seam`, `_the_shed_routes_through_the_launch_seam` + **three `test_RED_*`** (AST-prune the seam statement → invariant fails) | **YES** | **Site-granular** (each of the 3 enforcement points has its own RED prune); the `_dispatchers()` set-equality would fail if a new argv+Popen site appeared |
| AS-6 lifecycle + provider failure | `test_AS1_resume_with_unknown_telemetry_fails_closed` (typed `RunnerError`, not crash); `CliWorktreeGate::test_packet_worktree_mismatch_is_a_typed_loop_refusal`; `loop_turnover ActuateResumeTelemetry::*` | **PARTIAL** | Recovery/restart/turnover/continuation covered by the single-chokepoint proof (all route through run_unit→seam), not each end-to-end; concurrent controllers via the pre-existing lock — §6 LOW-MEDIUM |
| AS-7 fixtures | `FixtureRegression::test_AS7_source_hashes_are_the_recorded_baselines` / `_durable_state_reproduces_the_over_ceiling_shape` / `_audit_excerpt_carries_the_defect_values` | **YES** | Hashes match G0 baseline — §5 |
| AS-8 terminal honesty | `FixtureRegression::test_AS8_cycle2_transcript_has_no_terminal_result_record` / `_recovered_terminal_event_is_max_turns_not_a_provider_rejection` | **YES** | Exemplary R343/R344 — §5 |

The `probe_model_launch` classification (non-worker: no checkpoint contract, no resume, no permission broker) is explicitly asserted (`test_the_only_worker_dispatch_popen_is_run_unit…`) and defensible; its cwd is not seam-guarded (LOW, §6).

## 4. R342 12-item matrix (requirement 3)

| # | Matrix item | Named test / mechanism | Coverage |
|---|---|---|---|
| 1 | oversized | `test_AS2_above_threshold_rotates` (640224); runner + shed AS-1 | Direct |
| 2 | exactly-at-threshold | `test_AS2_at_threshold_exactly_rotates_never_resumes` | Direct |
| 3 | below-threshold | `test_AS2_below_threshold_resume_permitted`; `test_AS4_a_below_ceiling_session_is_not_shed` | Direct |
| 4 | missing telemetry | `test_AS2_missing_telemetry_…`; `test_AS1_resume_with_unknown_telemetry_fails_closed`; durable-flag shed | Direct |
| 5 | stale session identities | over-ceiling stale session shed (`…fixed_seam_sheds…` → `_provider_session_id==""`); `SessionTelemetry::test_legacy_record_without_tokens_is_unknown_not_zero` | **Indirect** (LOW) |
| 6 | controller restarts | single-chokepoint proof (restart→start→run_unit→seam); restart_channel suite | **Indirect** (LOW-MED) |
| 7 | recovery starts | `test_AS1_sheds_on_durable_flag_even_when_telemetry_unknown` (the durable flag persists across HALT→restart = the recovery-start shape) | Moderate |
| 8 | Windows paths | `test_AS3_windows_drive_case_and_slashes_still_match` | Direct |
| 9 | cwd mismatch | `test_AS3_unexpected_cwd_fails_closed`; `test_AS3_cwd_mismatch_refuses` | Direct |
| 10 | concurrent controllers | pre-existing single-instance lock (not re-tested here) | **By existing mechanism** (LOW-MED) |
| 11 | provider failure | typed `RunnerError` refusal at launch (over-ceiling/unknown/cwd) — "not a crash" | **As typed-refusal** (LOW-MED) |
| 12 | removal sensitivity | three `test_RED_*` AST-prune | Direct |

Items 5/6/10/11 are covered indirectly or by pre-existing mechanisms rather than dedicated new tests (see §6); the rest are direct.

## 5. Fixture provenance, sanitization, terminal evidence (requirements 2, 4)

- **Source hashes match the G0 baseline** (`M0-T123-G0-readiness.md` recorded BEFORE producer work): journal `a4acb370…`, audit `e80c057c…`, cycle-1 `3a0d1f30…`, cycle-2 `3c918568…` — identical to the fixture `source_sha256` block and the AS-7 test assertions. Sources byte-unchanged by the derivation. ✓
- **Sanitized:** home paths masked to `[HOME]`/`[HOME-SLUG]`, session ids are random UUIDs, and the `runtime_dir_name` path-naming digest is TRUNCATED (disclosed by the producer as a secret-scanner-hygiene edit — a public path digest, not a secret). The fixture-hygiene test passes. No secrets, no full home paths. ✓
- **AS-1 fixture fidelity (live shape):** `rotation_pending=true` + `rotation_pending_reason=context_threshold`; provider session `798d2f00` with `context_tokens_present=false` (unknown telemetry, matching the live record); audit seq24=604772/context_threshold, seq30=`decision_halt_unsafe`, seq34=`owner_explicit_restart`, seq37=`start_command`, seq40=640224/rc1/usage_known, seq42=`unsafe_condition`/missing_checkpoint. **HALTED→owner-restart lineage present.** ✓
- **AS-8 terminal honesty:** rc=1 + no result record recorded; the actual terminal event **recovered** from cycle-2 transcript records 92–95: `max_turns_reached {maxTurns:12, turnCount:13}` with a `nested_memory` attachment loading the primary checkout's rules (corroborating the wrong-cwd re-orientation consuming the turn budget). The prior "probable provider context-limit rejection" inference is explicitly **contradicted and abandoned** — exemplary R343/R344 discipline. ✓

## 6. Coverage gaps (severity-ranked; none blocking)

- **MEDIUM-LOW — AS-4/R337 seven preservation properties not individually asserted in the new pack.** The new AS-4 tests assert exactly-once (idempotent shed), below-ceiling-not-shed, and the freeze (old session → `""`). Checkpoint lineage, task identity, budgets, audit history, branch, and worktree preservation are NOT each asserted by a dedicated new test — they are carried by the pre-existing rotation/turnover suite (green in my 533 run) and the shed is a narrow operation (clears only the session pointer + rotation flag). The evidence-map R337 phrase "AS-4 property tests" is generous. Recommend a per-property preservation assertion for the rotation path in this pack. Not a correctness defect.
- **LOW-MEDIUM — R342 items 5/6/10/11 covered indirectly.** Stale identities (via shed + legacy-telemetry test), controller restarts (via single-chokepoint proof), concurrent controllers (via the unchanged single-instance lock), and provider-failure (as a typed refusal at launch) rely on architecture/pre-existing mechanisms rather than dedicated new tests. Defensible given every worker dispatch provably routes through the one `run_unit` Popen chokepoint, but the matrix items are not each independently exercised.
- **LOW — AS-3 Windows path forms.** Drive-letter case, slash direction, and whole-path case (via `os.path.normcase`) are handled and the primary-checkout masquerade is genuinely blocked; UNC (`\\server\share`) and 8.3 short-name forms are untested (exotic vectors).
- **LOW / observation — `probe_model_launch` cwd not seam-guarded** (classified non-worker; no resume/no work — defensible). And the Windows-path tests depend on `os.path.normcase` host behavior; the Windows sandbox matches the Windows production host, but a POSIX CI runner would fold case/slashes differently (supervisor is Windows-targeted, so not a production concern).

## 7. Verdict rationale

All required suites reproduce exactly at the reviewed identity (45; 533; 2870/2/0 twice; collect 2872), zero failures, no flakiness, modularity clean. The dual-guard seam (400k ceiling with correct at-or-above boundary + fail-closed missing telemetry; Windows-aware cwd binding with the primary-checkout case named specifically) is genuine; AS-5 proves single-seam closure with **site-granular** removal-sensitive AST-prune RED tests plus a dispatcher-set closure that catches any new argv+Popen site; the fixture is faithfully derived read-only (hashes match G0 baseline, sanitized, hygiene test green); the chain arithmetic closes exactly (45+7+4=56); and AS-8's terminal-evidence recovery (max_turns 12/13, context-limit inference abandoned) is exemplary honesty. The findings are coverage-depth observations (recommended hardening), not defects in the delivered behavior, and are flagged for the orchestrator/DCV — the AS-4/R337 per-property assertion and the indirectly-covered R342 items in particular. None falsifies current-state correctness.

VERDICT: PASS
