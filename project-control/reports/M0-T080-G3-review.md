# M0-T080 G3 code walkthrough (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t080-g3-reviewer (independent). Verdict PASS with 6
important findings (required rework) + 8 minor. G3's I-2 is the SAME defect as G5's must-fix M1
(post-launch identity gate fails open on omitted fields) — independent corroboration. All three
reproduced defects correctly fixed; suite 1833/0/2; modularity clean.

---

# G3 code walkthrough — M0-T080 — VERDICT: PASS

Reviewed identity `8546a2e80e995a6de25abbdea7dc1eaa60b002e1` (material identity `e3bd2a352aa84c7c9b6fc8a978db491051a43eef609b0dc037ecf1e09d74dcce`). No must-fix findings [G3's own classification; G5 independently classified I-2/M1 as must-fix — orchestrator adopts must-fix]. Six important findings recorded as required rework. Read-only throughout.

## Are the three reproduced defects real, and correctly fixed?

All three were real in the pre-change tree at `ccf8806`, confirmed by my own searches. All three are correctly fixed.

**Defect 1 — invented session identity. Real; fixed.** At HEAD the runner reads `session_id` off every stream event, not just system/init (claude_runner.py:1189-1206); first-wins, a second differing id sets RunResult.session_id_conflict, the loop drops the id, clears durable state, audits provider_session_ambiguous (loop.py:1785-1795). `with_resume("prov-session-1")` yields argv token prov-session-1; a sup-rot- key is refused internal_key_as_session_id; empty/untrimmed/None refused bad_resume_rebind; unverified capability refused resume_capability_unverified. rotation.new_session_id genuinely absent (replaced by new_rotation_record_key); complete_rotation carries both identities and refuses identity_conflated.

**Defect 2 — bypassed S11.3. Real; fixed.** All three seams now call _full_turnover; the three direct complete_rotation calls are gone; the only production caller is SeamTurnover.execute, ordering safe-seam → build → verify → persist → rotate → arm; a refusal pauses into PAUSED_RECOVERY. Caveat: assert_ready_checkpoint still has zero production callers (I-4).

**Defect 3 — code-default model chain. Real; fixed.** DEFAULT_ORCHESTRATOR_MODEL_CHAIN, ALLOWED_SUCCESSOR_MODEL_ID, and the two cli.py current_model literals are gone from production code (only docstrings/tests reference the removed names). loop.DEFAULT_MODEL_CHAIN is now ().

## Required checks
- Suite: 1833 passed, 2 skipped, 555 deselected (168.05s), clean tree. Zero failures. Exceeds the >=1165 floor.
- Modularity: 280 files, 0 failures, 5 pre-existing warnings. cli.py 2923/2953, loop.py 2076/2088, rotation.py 648/820 — all under. turnover_wiring.py extraction keeps cli.py under.
- READY gate: _post_rotation_gates at loop.py:2013-2030 runs after checkpoint validation and before COLLECT_EVIDENCE; no-op when no gate armed; model mismatch → stop PAUSED_RECOVERY. Crash-resume fallback correctly ordered.
- Approved-model routing (exercised directly): empty list → approved_models_empty / halted / exit 10 on select and next_after; listed-but-unprobed → model_probe_seam_missing (unsafe); unlisted → model_not_approved even if probe reports available; probe under a different config digest OR CLI version reads as no probe; exhaustion → approved_chain_exhausted naming every attempt; membership exact (case/space/typo variants all fail).
- IPC: assert_caller_allowed (Gate 1 ancestry) still first; the approved-list check is additive at Gate 3 scoped to claude, approved_models_unavailable when no approved surface. Ancestry not weakened.
- Two config spellings: _load_model_chain raises approved_models_conflict when both present and differ (order-sensitive); both keys in _CONTROLLER_ONLY_KEYS.
- Amended tests: no skip/xfail/expectedFailure added. Six removed, each replacement checked; the four inverted model_chain tests are correct inversions; identity_conflated replacement stronger. Two amendments not clean strengthenings (I-5, I-6).
- Deterministic verification records honestly (model_used = deterministic:supervisor-rederivation). What the gate detects is I-1.
- Facade re-exports verified by import (cli.run_orchestrator_watchdog, _build_worker_actuation_channel, _turnover_continuation_lock, _child_survivor_predicate, _orchestrator_exhaustion_event_id; all eleven rotation.* names re-exported from handoff.py).

## Findings — Important (required rework)

**I-1 — S11.3 verification gate cannot refuse anything on the production path.** turnover_seam.py:496-500: execute builds the handoff from `facts` then verifies against the same facts object; every field deterministic_verdict re-derives is copied verbatim by build_handoff, so divergence is structurally impossible. 300-case fuzz through execute with no verifier: zero refusals. The tamper test builds the tampered handoff from a second SeamFacts — unreachable by the production caller. Consequence: the verify step adds no detection beyond validate_handoff completeness + /clear; report §2.3/§3.3's "re-derives from its OWN durable facts" is inaccurate for the production call. Claim-accuracy + coverage, not wrong behavior; will bite when a live verifier or second source is wired.

**I-2 — verify_post_launch fails open on any field the successor leaves empty.** turnover_seam.py:449-468: every comparison guarded by `if expected and observed and observed != expected`. ClaudeCheckpoint.validate() checks only status + usage, so task_id/branch/worktree/starting_sha may be empty on a well-formed checkpoint. A successor reporting them empty satisfies the post-launch identity check regardless of actual task/branch/worktree/SHA. Model axis is backstopped by the runner's per-event expected_model verification (R739); the other four have no backstop. [This is G5's must-fix M1.]

**I-3 — decide_continuity fails open when the recorded session's model is unknown.** session_continuity.py:262: CROSS_MODEL added only when both successor_model and session_model non-empty. A recorded session with model_id="" and a different successor yields mode="resume" with no reasons. record_provider_session writes model_id = current_model or pinned_model; ProviderSession.from_dict returns "" for a record lacking the key, so a partial/older record produces this input. Unreachable today (resume_capability_verified is False everywhere forces reorientation); if ever verified, a silent cross-model resume recorded as clean — the exact class D-023 item 3 prevents. Per CLAUDE.md principle 3 an unknown model should read as impossibility, not "no objection".

**I-4 — rotation.assert_ready_checkpoint still dead, and its new docstring names a caller it lacks.** No production caller at HEAD; turnover_seam.require_ready implements its own gate. The docstring (rotation.py:723-731) claims SeamTurnover is the caller — false. Two READY-gate implementations coexist and disagree (the dead one demands session == expected_session_id, impossible before the successor reports). Report §1.2 lists this among zero-caller surfaces "fixed". A maintainer editing the READY policy in rotation.py changes nothing; wiring a caller would fail closed on every reorientation.

**I-5 — launcher effort pin became a pass-through, adversarial case dropped undisclosed.** turnover_adapters.py:342: effort = str(request.effort or ALLOWED_SUCCESSOR_EFFORT); pre-change pinned ALLOWED_SUCCESSOR_EFFORT unconditionally. The removed test supplied model=claude-fable-5/effort=low and asserted the launcher ignored BOTH; the replacement drops the effort half. Production unaffected (controller builds from successor.effort; resolver passes the constant) and controller-level effort refusal still tested — but the launcher-level defense on an R159-governed value plus an adversarial case were removed without disclosure in §6.2.

**I-6 — a hold-verification test is now self-referential.** test_agent_supervisor_r595_actuation.py:396-399 (NoOtherHoldMovedTests): previously asserted ALLOWED_SUCCESSOR_MODEL_ID == "claude-opus-4-8" (a production invariant); now asserts APPROVED_SUCCESSOR == "claude-opus-4-8", a test-local constant against its own literal — cannot fail. Substantive coverage exists elsewhere (INVALID_MODEL_REFUSED in the controller module), but a reviewer auditing "no owner hold moved" through that class gets a false positive.

## Findings — Minor
M-1 turnover_wiring.py:72-78/:237/:186 stale "always the frozen opus-4-8/xhigh pin" / "opus-worker-" docstrings carried from cli.py, now contradicting the module. M-2 ContinuityDecision.__post_init__ validates none_reasons tuple but not primary none_reason (a free-text none_reason accepted). M-3 report §3.7/§5.2 figures from base 73f5b85 not HEAD (cli.py 2923 not 2902, loop.py 2076 not 2067, suite 1833 not 1783 — all still pass). M-4 doctor model_launch_probes msg + config.example.toml comment say "no recorded probe ⇒ not selectable" — true of ModelRouter but the loop's quota-chain switch (_switch_at_seam) probes via make_launch_probe without consulting/writing ProbeLedger (both do a real exact-id probe, so R013 substance holds). M-5 turnover_adapters.py:267 references a nonexistent test name. M-6 _load_named_model_list optional_key param has one reachable value. M-7 execute calls store_verified_handoff before assert_not_archived (harmless; docstring wider than code). M-8 cli._approved_model_router/_approved_successor_resolver are new private aliases for new public names (surface, not compatibility).

## Adjudication of producer judgment calls (§8): concur with all nine; note the §8.3 disclosure is one-sided (the real risk is I-2's fail-open, not the fail-closed spelling difference). I-3 unreachability is because of judgment call 1.

## Freeze-lane / hold compliance: AD-093 evidence cited in packet + commit; github_flow/policy/process/run_budget absent; remote_approvals only a note string; RUNNABLE_MODES + R595 untouched; no provider contacted; no new dependency.

## Commands run
git rev-parse/log/show/grep (ccf8806 pre-change symbol searches; per-file diffs ccf8806..8546a2e8); pytest -k agent_supervisor (1833/2/0); modularity_check --check + direct source_lines/material_growth_limit; four read-only scratchpad probes (approved-model routing gates; with_resume argv + refusals; 300-case fuzz of SeamTurnover.execute → I-1; ContinuityDecision/decide_continuity edges → I-3/M-2); import checks for every facade re-export.

**Reviewed identity: `8546a2e80e995a6de25abbdea7dc1eaa60b002e1`.**
