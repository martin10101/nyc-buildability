# M0-T123 — Directive-compliance verification (VERBATIM verifier return; saved by the orchestrator, transport entity-decoding only)

All 20 rows verified against primary evidence I personally reproduced. Modularity is clean (exit 0, no failures on changed files; launch_seam.py 338 SLOC). Here is my DCV report.

---

# DCV REPORT — M0-T123 (resume-path defect class fix), D-024 Amendment 19

**Reviewed head:** `a71bd65` (confirmed `git rev-parse HEAD` = a71bd65954e8159808be9dcbbef27299654b3f88; branch `control/D-024-fable-codex-loop`).
**Material identity verified:** work `6aada29` (launch_seam.py NEW 338 SLOC + claude_runner/cli/loop/loop_turnover/session_continuity edits + tests + fixture) → hardening `16e1b3b` (claude_runner unwrap + 19 launch-seam tests + report §11). `git diff --stat 16e1b3b a71bd65 -- tools/` is EMPTY, so the code/test identity at HEAD equals the gate-reviewed identity `16e1b3b`.
**CI on pushed tip a71bd65:** 20/20 check-runs `success` (all green, incl. supervisor-bridge). No failures, none running.
**Producer model identity:** `agent-afd9fa16` transcript grep = **451 "model":"claude-opus-4-8"**, zero other id (re-grepped personally).

## Per-requirement verdicts (20/20)

**R327 — PASS.** The S16.7 disposition is recorded verbatim in `source-019-amendment.md` (VERBATIM block p1: "I disposition the cumulative S16.7 owner-touch excess as an accepted measurement of this failed activation campaign only"); referenced in the packet.

**R328 — PASS.** Nothing granted was exercised: the preserved journal is byte-identical to the G0 baseline (I re-hashed `supervisor_journal.sqlite3` = `a4acb370f3a23fd5…` READ-ONLY, matches), proving no budget reset/increase and no restart/clear-recovery ran; the diff contains no budget/policy/journal-surface change.

**R329 — PASS.** Complete touch history preserved: journal `a4acb370…` + audit `e80c057cabc24478…` byte-identical to the G0 baselines (both re-hashed by me at `…/33dfa57d…/`); no touch record altered/removed.

**R330 — PASS.** Ledger check: only `M0-T123` (awaiting_gate) and `M0-T124` (backlog, deps `["M0-T123"]`, producer null — held) were created since the window opened (05:53:54/05:53:55). No other work started. Qualifying evidence `M0-T107-cycle2-live-journey.md` cited.

**R331 — PASS.** Both live-reproduced dimensions closed in ONE seam `launch_seam.py`: the 400k ceiling guard (`evaluate_ceiling`) and the cwd guard (`evaluate_cwd`/`evaluate_packet_worktree_binding`); root-cause traces with file:line for both in producer report §1 (loop.py ceiling-never-evaluated; cli.py:2642 worktree defaults to primary checkout).

**R332 — PASS.** `claude_runner.run_unit` calls `launch_seam.enforce_launch` **UNCONDITIONALLY** at line 1224 before the sole `subprocess.Popen` at line 1261 (no `if expected_worktree:` wrapper — confirmed by reading the code and by `test_R332_seam_is_not_nested_under_an_expected_worktree_guard` + the anti-re-wrap RED). The dispatcher-set closure test (`test_the_only_worker_dispatch_popen_is_run_unit_and_it_is_seam_guarded`) mechanically proves the only worker-argv+Popen sites are `{run_unit (seam-guarded), probe_model_launch (non-worker probe)}`. CLI gate + pre-first-dispatch shed also route through the seam.

**R333 — PASS.** `evaluate_ceiling`: `if tokens >= int(ceiling): ROTATE(over_ceiling_resume_forbidden)` — at-or-above is never resumed. `test_AS2_at_threshold_exactly_rotates_never_resumes` (exactly-400k) + `test_AS1_over_ceiling_resume_refuses_before_launch` (the live 640k shape) pass.

**R334 — PASS.** Over-ceiling → `ROTATE` (loop sheds to a fresh session at the safe seam via `_rotate_over_ceiling_before_first_dispatch`) or, at the runner chokepoint which cannot rotate, `enforce_or_raise` fails closed before Popen. AS-1 RED/GREEN pair on the seeded cycle-2 shape passes.

**R335 — PASS.** `evaluate_cwd` binds cwd to `expected_worktree` (RunnerConfig) and `evaluate_packet_worktree_binding` binds to the packet's declared worktree; Windows-aware (`normalize_path` folds drive case + slashes). `test_AS3_windows_drive_case_and_slashes_still_match`, `test_unc_matching_worktree`, `test_8_3_short_name_cwd_fails_closed` pass.

**R336 — PASS.** Primary-checkout/unexpected-cwd fail closed pre-provider with typed refusals (`CWD_PRIMARY_CHECKOUT`/`CWD_MISMATCH`); `test_AS3_cwd_primary_checkout_refuses_before_launch` + `FixtureRegression::test_AS3_transcripts_show_the_cwd_isolation_defect` (the live cycle-2 `…\ctl24` cwd) pass.

**R337 — PASS.** All seven owner-named properties individually asserted (I read the test bodies): `test_R337_checkpoint_lineage_preserved`, `_task_identity_preserved`, `_branch_and_worktree_preserved` (both branch + worktree), `_budgets_untouched` (durable diff == exactly `{provider_session, 2 rotation keys}`, `touches.report()` unchanged), `_audit_history_verifies_and_only_grows` (chain verifies before+after, prior records strict subset, exactly one shed appended), `_exactly_once_succession` (one shed, real session id `798d2f00` captured, distinct successor). Genuine snapshot-before/after, not vacuous.

**R338 — PASS.** After rotation the old oversized session (`798d2f00`) is shed and never resumed (runner refuses `--resume` of it); the new session identity is distinct (`loop._provider_session_id == ""` → fresh). `test_AS4_shed_is_idempotent` + the exactly-once succession test confirm; the shed captures the frozen session id and yields a distinct successor.

**R339 — PASS.** Every worker-launch/resume call site enumerated mechanically (`_dispatchers()` scans package ASTs for functions that BOTH `build_argv` and `Popen`) with the same-seam proof: the set is exactly `{run_unit, probe_model_launch}`, run_unit routes through `enforce_launch` and appends the checkpoint contract, the probe does neither — a proof from code, not a hand list.

**R340 — PASS.** Deterministic bypass-sensitive reachability test: AST-prune site-granular REDs (`test_RED_removing_the_seam_statement_uncovers_run_unit`, `_run_loop_without_the_gate_is_a_bypass`, `_run_without_the_shed_statement_is_a_bypass`) + anti-re-wrap RED (`test_RED_re_wrapping_the_seam_under_the_guard_is_detected`) — I read the pruner (`_strip_stmts` removes whole statements and re-parses valid Python). GREEN on the fixed tree: **64 passed** (I ran it).

**R341 — PASS.** Fixture `source_sha256` == G0 baselines == my own READ-ONLY re-hash of all four preserved sources: journal `a4acb370…`, audit `e80c057c…`, cycle-1 transcript `3a0d1f30…` (under the `wt-m0t107` slug), cycle-2 transcript `3c918568…` (under the `ctl24` slug) — every one matches exactly; `test_AS7_source_hashes_are_the_recorded_baselines` asserts them. Sources unwritten (read-only).

**R342 — PASS.** All 12 matrix items have direct named tests: oversized (`test_AS2_above_threshold`/AS1 640k), exactly-at-400k (`test_AS2_at_threshold_exactly`), below (`test_AS2_below_threshold`), missing telemetry (`test_AS2_missing_telemetry_fails_closed`), stale session identities (`MatrixR342StaleSessionIdentity` ×2), controller restarts (`MatrixR342ControllerRestart`), recovery starts (`test_AS1_sheds_on_durable_flag`), Windows paths (`test_AS3_windows…` + UNC + 8.3), cwd mismatch (`test_AS3_unexpected_cwd`/`test_AS3_cwd_mismatch_refuses`), concurrent controllers (`MatrixR342ConcurrentControllers` ×2), provider failure (`MatrixR342ProviderFailureAtLaunch` ×2), removal sensitivity (`test_RED_*` + sweep). The four hardening additions present by name; the honest OSError limitation is framed (the raw missing-exe Popen asserts true `FileNotFoundError` + zero children rather than a false pass).

**R343 — PASS.** rc=1 + missing result recorded honestly (producer report §6); I personally confirmed the cycle-2 transcript (`798d2f00`) has **0 `type:result` records**.

**R344 — PASS.** The context-limit rejection hypothesis is contradicted and abandoned (report §6); the terminal event is RECOVERED from primary evidence — I grepped the cycle-2 transcript myself: `max_turns_reached` with `"maxTurns":12`, `"turnCount":13`. The count corrections (46→45 attribution, 2869→2870 early measure) are disclosed with explanations in report §8.

**R345 — PASS.** No live-loop restart / clear-recovery / journal edit / budget reset anywhere: the preserved journal is byte-identical (`a4acb370…`), and PR #241 is untouched (`gh pr view 241` → state OPEN, title unchanged "…DO NOT MERGE until owner authorizes").

**R346 — PASS.** G0 PASS (orchestrator, 1a286c8), G2 PASS (orchestrator, 6aada29), **G3/G4/G5 PASS (code-reviewer/qa-engineer/security-reviewer, all @16e1b3b)** — producer `supervisor-resume-path-producer` ≠ reviewers. Three delta attestations on file (G3/G4/G5 "DELTA VERDICT: PASS"). Mutation proof = the AST-prune site-granular REDs + anti-re-wrap (verified). Full suite **2889 passed / 2 skipped / 0 failed** independently reproduced by the G4 reviewer's OWN run (attestation §Production-unwrap, exit 0) in addition to the orchestrator; I reproduced launch_seam 64/64 and modularity `--check` exit 0 (no failures on changed files; launch_seam.py 338 SLOC). CI 20/20 green on a71bd65. Frozen-identity recertification + manifest verification + R276 preflight are correctly deferred to M0-T124 (held). DCV = this pass.

## Discrepancies between claims and evidence
None material. Every hash, count, AST invariant, and terminal-event claim I reproduced matched the reports and fixture exactly (four source hashes, 64-test run, dispatcher-closure, max_turns_reached 13/12, 0 result records, journal byte-identity, CI 20/20, model identity 451/451). The report itself self-discloses the count corrections (46→45, 2869→2870) with explanations — honest disclosures, not defects. R347 (afterward-STOP / live-start package for a separate owner decision) binds M0-T124, not this task's applicable set, and M0-T124 is correctly held (backlog, deps [M0-T123]).

DCV VERDICT: ALL PASS
