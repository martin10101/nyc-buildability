# M0-T080 G3 focused re-review, round 2 (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t080-g3-rereview (independent). Verdict PASS — all six
round-1 findings resolved — with four residuals (R-1 important-latent, R-2 medium-live, R-3/R-4
low doc-accuracy, R-5/R-6 infra/nit). R-1 and R-2 are the fail-open family and feed a round-3
micro-correction before acceptance.

---

# G3 focused re-review — M0-T080 round 2 — VERDICT: PASS

All six of my round-1 findings are correctly resolved. I re-derived each against the corrected source and ran the specific tests. Four residual findings, none reverses a round-1 fix; two are latent/edge in the fail-open family and should be recorded as blocking before the surfaces they affect are wired.

## Required checks
- Suite: pytest -k agent_supervisor → 1854 passed, 2 skipped, 555 deselected, 0 failed (377.97s). Matches exactly.
- Modularity: 280 files, 0 failures, 5 pre-existing warnings.
- No test weakened. Zero skip/xfail added. +25 new test defs, −4 removed, net +21 (1833→1854). The 4 removals are all dead-gate or self-referential (3 deleted rotation tests call assert_ready_checkpoint directly — dead-gate only; the 4th is the vacuous I-6 assertion, replaced 1:1).
- cli.py 2898/2953 (55 free); import succeeds; every facade name resolves; 15 dropped imports none referenced as cli.<name>. loop.py 2080/2088, rotation.py 623/820, census 280.

## The six round-1 findings — all resolved
**I-1 (U3) — resolved, honestly.** Two distinct labels (deterministic:supervisor-consistency vs -independent-rederivation, turnover_seam.py:56-61). Verdict carries a scope block naming the 6 value-checked + 8 not-re-derived fields (6+8=14; the 8 all originate in the worker checkpoint where the supervisor holds no second copy). Report §2.3/§3.3 retract the overstatement plainly. The FactSource seam exists, refuses on divergence, refuses-not-downgrades on raise (handoff_fact_source_failed), NOT production-wired (SeamTurnover constructed only at loop.py:1005 passing no fact_source), stated with reason. JUDGMENT: (b)+built-(a) is right; I would have refused production wiring under this lane — the only independent source is repo I/O inside the rotation seam, which performs none today; adding subprocess git is new behaviour with new failure modes (slow/absent git newly blocking a rotation), a freeze-§1/§2 violation. See R-1: the built (a)-arm has its own fail-open to close before wiring.

**I-2 (U1) — resolved for the four axes.** verify_post_launch: blank AND wrong both refuse on task_id/branch/worktree/starting_sha; omission message distinct ("successor reported NOTHING"); all-correct still passes. require_ready refuses ready_without_session_id on blank claude_session_id; tests call validate() first to prove well-formed. Producer also closed a RESUME gate with no provider_session_id (resume_gate_without_session); the old satisfied_by="(no session id reported)" fallback is gone. One axis remains — R-2.

**I-3 (U2) — resolved.** Full model matrix through decide_continuity with resume_capability_verified=True: all five unknown-or-differing combos → reorientation with cross_model; only known-equals-known resumes; both-unknown covered.

**I-4 (U4) — resolved.** assert_ready_checkpoint gone (hasattr False), false docstring gone, report §1.2 corrected ("was wrong"). Exactly one READY gate (live require_ready); replacement test asserts both halves.

**I-5 (U9) — resolved.** turnover_adapters.py:392 effort = ALLOWED_SUCCESSOR_EFFORT unconditional; adversarial test reinstated and stronger (four smuggled efforts, asserts pin holds on invocation + env var + never reaches argv).

**I-6 (U10) — resolved.** Assertion targets turnover_controller.ALLOWED_SUCCESSOR_EFFORT (the only definition, turnover_controller.py:73); also asserts ALLOWED_SUCCESSOR_MODEL_ID absent and no default model/effort in the context dataclass.

## Other corrections judged
**U12 correct** — order persist→arm→complete; crash-window test injects a raising complete_rotation and asserts restart view (gate armed, no rotation record, pending, non-READY refused). Fail-closed by construction. Behaviour change: a crash in this window now pauses for attention.
**U11 correct** — handler after LoopError/BudgetError clauses; ConfigError subclasses ValueError so not shadowed; test drives real cli.main, asserts no traceback + nonzero exit + approved_models_conflict.
**U13 correct, verified live** — start --help "next OWNER-APPROVED, live-probed model" no pin claim; orchestrator-watchdog --help carries --claude-executable; no opus-4-8 in production source except past-tense module-docstring narrative.

## Residual findings
**R-1 — Important, latent (blocks wiring the U3 (a)-arm). turnover_seam.py:261-267, 287-302, 328-342.** A FactSource returning {} / None / a partial mapping produces a check WEAKER than no fact source, stamped with the STRONGER label. `independent = dict(fact_source() or {})` turns None/{} into "an independent source that agrees about nothing"; because `independent is not None` the code replaces the facts baseline wholesale (omitted keys skipped, not falling back to the consistency check) AND records model_used=deterministic:supervisor-independent-rederivation. Demonstrated: a wrong-branch handoff is caught (verified=False) with no fact source, and PASSES (verified=True, labelled independent) with a fact source returning {}. The scope.value_checked list still names all six, so the scope block itself overstates. The I-1 defect class reproduced inside the fix for I-1. Unreachable today; a soft-failing real impl (git rev-parse wrapper returning {} when git absent) hits it immediately. Fix: treat empty/None as a refusal like a raise, or require the five keys, or overlay independent values over the baseline and report only keys actually compared.

**R-2 — Medium, LIVE. turnover_seam.py:583, docstring :545-556.** The model axis is the one surviving `if expected and observed` guard, and the docstring justifying the carve-out asserts a backstop that does not cover the invoked case. It claims "A stream that reported no model at all is caught there, not here." It is NOT: claude_runner.inspect_stream sets model_mismatch=True only when an event reports a model DIFFERING from expected_model (claude_runner.py:692); a stream carrying no model yields observed=[] and mismatch=False, and nothing requires observed_models non-empty. Confirmed end-to-end: observed_models=() and run_result=None both return ok=True from verify_post_launch. The R739 backstop is real for divergence, absent for silence. Round-1 I-2 scoped to the four unbacked axes (properly closed), so this does not reverse the fix — but the fail-open family is not fully closed, and the code documents the gap as covered.

**R-3 — Low. loop.py:1000-1003.** The retracted claim survives verbatim where a reader wiring the seam looks: "with none injected the supervisor verifies DETERMINISTICALLY by re-deriving every field from its own durable facts" — the exact wording U3 corrected elsewhere. Companion: the section banner at turnover_seam.py:223 still frames it as "the supervisor's own re-derivation".

**R-4 — Low, report accuracy. Producer report line 122 (§2.3).** The SeamTurnover.execute row still describes "persist → rotate → arm READY", which U12 inverted; U15 should have caught it.

**R-5 — Informational.** loop.py 2080/2088 — 8 SLOC headroom; next edit must extract first.

**R-6 — Nit.** assert_ready_checkpoint still in module-docstring prose (turnover_seam.py:10,24; session_continuity.py:21) — past-tense history, reads correctly, but greps to a nonexistent function.

## Reviewed identity: de4d5505cb217c8ed7d84456bcc6ee994f39ed73 (round-2 task commit 31e6b87; read-only, no writes/mutations/project_control.py).
## Commands: git log/rev-parse/status/show --stat; per-file diff 8546a2e8..31e6b87 across 17 files; --numstat + grep counts of test defs/skips; git show 8546a2e8:rotation.py; pytest -k agent_supervisor (1854/0/2); pytest -v spot-check of 10 new U-tests (all pass); modularity_check --check/--report + census/baseline of 6 files; start/orchestrator-watchdog --help; import probe of every facade + handoff/rotation re-exports; two scratchpad probes (FactSource empty/partial/None → R-1; decide_continuity matrix → I-3; verify_post_launch every axis → I-2; model-axis silence → R-2).
