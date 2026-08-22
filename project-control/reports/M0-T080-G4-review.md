# M0-T080 G4 integration/regression review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t080-g4-reviewer (independent). Verdict PASS with 7
findings (3 medium, 4 low). Full tree 2387 passed / 3 skipped / 0 failed. Findings folded into
the consolidated T080 correction; F2 (watchdog probe-ledger identity) and F1 (unearned exhaustion
claim) are the load-bearing ones.

---

# G4 Integration/Regression Review — M0-T080 — VERDICT: PASS

M0-T080 rebases cleanly onto accepted M0-T079, the whole tools/ tree is green, both CLI extractions coexist, and every fail-closed claim reachable from a real CLI holds. No regressions, no blocking defects. Seven non-blocking findings; three deserve attention before acceptance (two are false-evidence claims in operator-facing text; one silently disables the R595 orchestrator path the moment the owner wires a real probe).

Correction to the brief up front: a `start` with an EMPTY approved_models does NOT yield a typed refusal — it dispatches (section 3). Not a directive violation, but the brief's expectation is not what the code does.

## 1. Full-tree suite
python -m pytest tools/ -q --no-header → 2387 passed, 3 skipped in 1745.42s, exit 0. Zero failures. Both tree-sensitive smoke tests passed inside the run and again in isolation (25 passed in 31.74s). Another agent wrote the G5/G3 report files into the tree mid-run, but git diff / git diff HEAD were 0 bytes throughout (report files are untracked, not modifications), and with an empty committed diff the context-pack byte-bound mechanism never triggered — no flake classification needed. Supervisor block: 1833 passed, 2 skipped, 555 deselected — exceeds the >=1165 freeze floor.

## 2. Composition with accepted M0-T079
Both extractions coexist: cli.py imports start_gate (T079 run_dispatched) and turnover_wiring (T080 R595 actuation); cli.run_dispatched is start_gate.run_dispatched; run_orchestrator_watchdog / _build_worker_actuation_channel and other pre-split private names preserved as aliases; all 17 supervisor modules import in one process. T080 touched no T079 file (start_gate/run_budget/recovery/policy/process/github_flow/locking empty diff vs ccf8806). Inside loop.py the T079 bounded-mode owner gate is byte-untouched (no diff line mentions owner_enabled_bounded_auto/RUNNABLE_MODES/OWNER_GATED_MODES/LimitedAutoRefused). Bounded+recovery+recovery-probes+all five turnover+rotation+model_chain+start_reentry+r595 together: 480 passed. Modularity: 280 files, 0 failures, 5 pre-existing warnings; cli.py 2923/2953, loop.py 2076/2088, rotation.py 648/820, claude_runner.py 1300/1383, model_change_ipc.py 677/701 — all under. cli.py has 30 SLOC headroom (next change touching it likely needs an extraction).

## 3. Real CLI journeys (subprocess, temp checkout, no provider)
doctor --json reports routing state both ways: empty config → "approves NO models ... every model-selection act ... will stop safely with a typed refusal", model_launch_probes "recorded probes: (none)"; populated → names ['claude-opus-4-8','claude-opus-4-7'], source file, config identity digest, still no selectable model (nothing probed). Typed exit codes observable at start: a journal naming an effective model outside the approved chain refused exit 11 (unsafe), dispatched:false, zero provider calls — with populated AND empty approved lists. Watchdog fails closed over a genuinely pre-T080 journal: without --current-model it refuses naming the remedy; with one + empty approved list returns no_approved_successor, launches nothing, does not consume the dedup key. Runtime-file escalation blocked for both spellings (controller_key_in_runtime_file).

THE ONE THAT CAME BACK DIFFERENTLY: a start with EMPTY [approved_models] does NOT refuse — it dispatched (dispatched:true, provider_calls_made:2, real process on claude-opus-4-8). That id is not a code default — it is the model_selection.toml primary validated against the immutable config's [claude] allowed_models. Reading D-023-R013 verbatim, the prohibition is scoped to "context/session turnover and model-quota fallback ... no silent or unlisted model substitution", and a run's initial pin is neither turnover, fallback, nor substitution — so NOT a violation. But it means a run's FIRST model is admitted by [claude] allowed_models with no launch-probe requirement, while every LATER selection is held to [approved_models] + probe. Whether the initial pin should also be held to the approved list is an owner decision.

## 4. Cross-tree census
Every census-sensitive non-supervisor module passes individually (modularity_check 24, subsystem_resolver 21, product_map 13, repo_fingerprint 14 +1 skip, code_graph 36, repo_views 26, repo_index_assembly 7, repo_index_baseline 7, repo_index_cache 13, repo_index_incremental 25, context_pack_index 8). The six new modules did not disturb the repo-index/subsystem census. Controller manifest round-trips (manifest_binding ok:true).

## 5. Crash/rotation suites individually
crash 32, endurance 94, adversarial 93, invariants 46, rotation 75, turnover_controller 16, turnover_adapters 17, turnover_integration 12, turnover_live_seam 67, turnover_live_signal 10, model_chain 24, model_turnover 25, ipc 42 — all green. Confirmed RotationLedger.complete_rotation has exactly ONE production caller (turnover_seam.py:516) and all three loop seams route through _full_turnover.

## 6. Backward compatibility
ProviderSession.from_dict → None for absent/unreadable; ProbeRecord.from_dict → None on garbage; ProbeLedger.recorded → None on config-identity/CLI-version mismatch. Nothing crashes, nothing defaults. Over a real pre-T080 journal the watchdog produced a typed refusal and start neither crashed nor invented a model id.

## 7. Skips
Two in the supervisor block (both pre-existing conditional platform skips: policy.py:449 symlink privilege; process.py:448 POSIX-only guard); the diff adds no skip/xfail/expectedFailure. The third full-tree skip is repo_fingerprint.py:148 (symlinks), pre-existing and outside the supervisor block.

## Findings

**F1 — MEDIUM, evidence honesty. approved_models.py:421-428.** The approved_chain_exhausted message asserts "Every candidate was tried by an actual launch probe" unconditionally, including when no probe seam is wired and nothing was tried. Reproduced live: the sentence printed while every attempts entry carried reason_code: model_probe_seam_missing. An operator concludes the models were launch-tested and failed to come up when nothing was attempted — the exact unearned-evidence class this task removes. Derive the sentence from the attempts list.

**F2 — MEDIUM, forward-looking. cli.py:2620-2628 vs cli.py:2789.** The orchestrator watchdog never passes cli_version to run_orchestrator_watchdog, so its ProbeLedger is keyed on cli_version="" and orchestrator-watchdog has no --claude-executable flag. The start worker channel keys the same ledger on runner.executable_identity()["digest"]. Consequence: the moment the owner wires a real launch probe (the documented activation step), a probe recorded by start can never satisfy the watchdog's identity match, so the orchestrator layer returns no_approved_successor forever — the R595 orchestrator path permanently unable to turn over after the owner has done everything the docs ask. Fails closed, so safe; invisible today (no probe seam wired).

**F3 — MEDIUM, evidence accuracy. turnover_seam.py:216-250; report §3.3.** Both docstring and report ("re-derives every load-bearing field") overstate: deterministic_verdict re-derives 6 of Handoff's 14 fields (task_and_stage, branch, worktree, exact_next_action, authoritative_shas["HEAD"], forbidden_scope); not compared: completed_work, changed_files, tests_and_ci, pull_request_state, reviews_and_findings, open_blockers, owner_gates, evidence_digests. Since build_handoff fills all 14 from the same SeamFacts the verifier reads, this is a self-consistency check over a subset, not independent verification. validate_handoff enforces non-emptiness on the other eight; tamper window in-process; functional risk low — the overstated claim is the finding.

**F4 — LOW, operator-facing accuracy.** Six stale "pinned opus-4-8" claims survive in code T080 moved/edited: turnover_wiring.py:75/:237, cli.py:2570/:2834, worker_turnover.py:19, and cli.py:3280 — the --help text for --authorize-turnover-actuation reads "WORKER-layer Fable->opus-4-8 turnover" then two sentences later "on the next OWNER-APPROVED, live-probed model", contradicting itself in rendered help. §2.5 of the report corrects precisely this class in remote_approvals.py, so the standard is established.

**F5 — LOW, pre-existing shape, newly reachable. cli.py:2669.** load_controller_config in _run_loop sits outside the except (LoopError, IllegalTransitionError, BudgetError, BreakerError) guard, so T080's new approved_models_conflict reaches the operator as a raw traceback exit 1, not a typed refusal. Pre-existing (the removed empty_model_chain error took the same path) and exit 1 is the documented legacy_halt — but M0-T079 C5 extended "a refusal is a report not a traceback" to BudgetError/BreakerError for exactly this reason; ConfigError is the remaining gap T080's new code now exercises.

**F6 — LOW, provenance. session_continuity.py:236 and loop.py:944.** The durable provider_session_continuity key is per-checkout not per-run, and decide_continuity ignores ProviderSession.run_id though the record carries it. loop.__init__ restores _provider_session_id regardless of which run wrote it; a mandatory pre-dispatch rotation can fire before the new run completes a unit, so run B's first rotation record can name run A's provider session as previous_provider_session_id and archive it. Benign today (archiving only forbids future resumes; resume unreachable) but records a cross-run provenance that is not true, in a change whose purpose is that recorded identities are real.

**F7 — LOW, crash window. turnover_seam.py:516 then :530.** complete_rotation and arm_ready_gate are two separate durable writes; a crash between leaves a durably completed rotation with no armed gate, so on restart require_ready returns early on gate is None and post_rotation_gates finds armed is None — the successor's first checkpoint bypasses both the READY gate and the post-launch identity check. That is fail-OPEN in one narrow window, unlike everything else. Not a regression (no gate existed before T080); AS-43b covers the adjacent armed-gate window.

Not findings, for the ledger: producer report numbers were pre-reconciliation (1833 vs 1783 reported; cli.py 2923 vs 2902; loop.py 2076 vs 2067; census 280 vs 272) — all in the safe direction; 272→280 is the new modules entering the census (resolves producer risk 7). Watchdog refusals exit 0 with refused:true in the payload, so AS-21's typed ModelRoutingError exit codes are a property of the Refusal object, not of that CLI journey — unchanged from pre-T080.

## Reviewed identity
HEAD 8546a2e80e995a6de25abbdea7dc1eaa60b002e1; tools/agent_supervisor tree hash 1ed44affeca331662b09dac0e418a788d59be09e; 0 tracked modifications (read-only; journeys against temp dirs; no git mutation; no project_control.py).

## Commands run
git rev-parse/status/log; git diff --stat + per-file diffs ccf8806..HEAD; git show ccf8806:cli.py; pytest full tree (2387/3/0); pytest -k agent_supervisor (1833/2); the two smoke tests in isolation (25); 480-test composition run; per-module crash/rotation runs; cross-tree census modules; modularity_check --check + --report --json; doctor/start/orchestrator-watchdog subprocess journeys (empty/approved/conflict configs) + --help; import smoke (17 modules, facade aliases, removed constants); SLOC vs modularity_baseline; ModelRouter.next_after adversarial probe (exhaustion message vs attempts); load_model_selection runtime-file escalation.
