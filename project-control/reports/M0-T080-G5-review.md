# M0-T080 G5 security review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t080-g5-reviewer (independent). Verdict FAIL — one
must-fix (M1). Drives the consolidated T080 correction round once G3/G4 are in.

---

# G5 adversarial security review — M0-T080 (session/model turnover + owner-approved model routing)

**VERDICT: FAIL** — one must-fix. The R013 model-authority core (brief item 1) held up under attack. The session-identity guarantee (brief item 3's post-launch check) did not: I defeated it with a 20-line script against the real code at the frozen HEAD.

Reviewed identity: **8546a2e80e995a6de25abbdea7dc1eaa60b002e1** (material identity e3bd2a352aa84c7c9b6fc8a978db491051a43eef609b0dc037ecf1e09d74dcce). Tree clean and unmodified; nothing written inside the repository.

## MUST-FIX

### M1. The post-rotation identity gates are defeated by an OMITTED identity, not just a matching one

`turnover_seam.verify_post_launch` guards every comparison with `if expected and observed`, and `require_ready` guards its archived-session and resumed-session checks with `if session and …`. Everything on the observed side comes from `ClaudeCheckpoint`, whose own docstring says it is untrusted worker content, and whose `validate()` (`models.py:173`) checks only `status` and `usage` — `task_id`, `branch`, `worktree`, `starting_sha`, and `claude_session_id` may all be empty strings. Nothing else in the loop compares those fields to the authority; I searched for a pre-existing binding gate and there is none.

Demonstrated against the frozen code: with a reorientation gate armed for task `M0-T080` / branch `task/x` / worktree `C:/wt` / model `approved-model-A`, a checkpoint reporting `status="READY"` and blanks in all five identity fields yields `READY gate: PASSED` and `post-launch ok: True | mismatches: []`.

**Attack / consequence:** a successor on the wrong model, in the wrong worktree, on the wrong task, started from the wrong SHA — or literally the session the rotation just archived — satisfies both gates and the run forwards. The cheapest evasion of the new check is to say nothing rather than to lie. AS-18 (impostor), AS-20 (post-launch), AS-37 (model mismatch) and AS-38 (wrong worktree) all exercise populated-but-wrong values only, so the suite is structurally blind to it. This is the central new guarantee of deliverable 2 and of D-023 item 2.

**Fix direction:** an absent identity field must count as a mismatch — the supervisor wrote the expectation down first, and this module's own posture elsewhere is that an unprovable state is a refusal — and a READY that clears a gate must carry a non-empty `claude_session_id`. One axis resists this: `model`. `observed_models` comes from `RunResult` (supervisor-parsed off the stream, not worker-authored), and the pre-existing R739 `expected_model` stream verification backs it independently.

## IMPORTANT

### I1. `ModelRouter.probe_record` treats an unparseable probe result as proof of availability
A probe seam returning any truthy non-`ProbeOutcome` value is coerced to `ok=bool(outcome)` and recorded as a successful live launch probe with `reason_code="probe_shape"`. Verified: a probe returning the string `"sure, it launched"` made a listed model selectable. The one fail-open in a module whose stated rule is that an unreadable result proves nothing. Not reachable today (cli.py wires no probe seam), so latent: it goes live at exactly the owner-checkpoint act the design anticipates ("wire a real probe"). Fix: a non-`ProbeOutcome` return is `ok=False`.

### I2. The `NO_APPROVED_SUCCESSOR` safe stop writes no hash-chained audit row
`TurnoverController._no_launch` appends nothing. Unlike `BLOCKED_SURVIVOR` and the two other safe stops, the new status has no record of its own. In the loop path the transition + owner touch capture it; in `run_orchestrator_watchdog` (standalone under the OS scheduler) the only trace is the returned JSON. Every other watchdog refusal is audited, so "approved list empty / nothing probed / chain spent" is the single turnover refusal with no durable audit evidence. (Chain-exhaustion IS audited in the loop path via CHAIN_EXHAUSTED_STOP, not the watchdog path.)

### I3. Deterministic verification is tautological as wired
`SeamTurnover.execute` builds the handoff from `facts` then verifies it against the same `facts` two lines later, so `deterministic_verdict` cannot produce a finding in the production path; AS-12 tampers outside `execute`. Labelling is honest (`deterministic:supervisor-rederivation`) and `validate_handoff` (completeness + `/clear` refusal) is a real gate that runs. But what `store_verified_handoff` records as verified could not have failed. Not a weakening (there was no verification before); flagged so nobody reads `verified_by_model` as an independent check.

### I4. The approved-list guarantee does not cover the pinned model
`loop._actuate_model` permits `model == self.pinned_model` as an explicit escape from the chain check; `pinned_model = selection.selection("claude").primary`, validated against `[claude] allowed_models` (a different owner list) with no probe record. So `[approved_models]` + live probe governs substitutions and turnover successors only. Arguably correct (the pin is not a substitution), but §2.4's "one object every selection act asks" and the doctor text both omit it. The directive verifier should rule explicitly on whether R013 reaches the pin.

## MINOR
- N1. `loop_turnover.full_turnover` calls `actuate_resume` after `execute` stored the handoff / wrote `last_rotation` continuity_mode=resume / armed the gate; it raises `LoopError` which `_rotate_at_seam` does not catch (only `SeamTurnoverError`), so the run aborts leaving a durable record of a resume that never launched. Fail-closed but contradicts "a refusal leaves the run where it was".
- N2. `complete_rotation` and `arm_ready_gate` are two journal writes in `execute`; a crash between leaves rotation recorded with no gate armed → on restart `armed_gate()` is None, successor neither READY-gated nor identity-checked.
- N3. A fresh probe reporting a CLI version different from the ledger's binding authorizes the selection anyway (probe_record returns the new record without re-checking matches()); writes a record that can never authorize again.
- N4. Effort lost its policy-layer pin (controller compares requested_effort to successor.effort not ALLOWED_SUCCESSOR_EFFORT; ApprovedSuccessor validates only model_id). Low impact (every --effort argv form is hard-denied) but the invariant now has no policy-layer enforcement point.

Informational, pre-existing, not T080: `cli.cmd_export_handoff` rebuilds HandoffVerification(True,…) from the journal without re-comparing the digest; `handoff.assert_review_model_used` skips the model-identity check when review_model is empty (unreachable today, no verifier wired).

## What held up under attack
1. Silent/unlisted model substitution — NO route found. DEFAULT_ORCHESTRATOR_MODEL_CHAIN / ALLOWED_SUCCESSOR_MODEL_ID genuinely gone (grep: only docstrings/comments/history/negative tests). Absent [approved_models] ⇒ empty ⇒ typed halted refusal, never a fallback; config.example.toml ships placeholders. Both spellings → one field; disagreement = approved_models_conflict. approved_models/model_chain added to _CONTROLLER_ONLY_KEYS (closes settings-fallback). Probe records bound to config digest AND CLI identity; production wires NO probe seam so nothing selectable without a pre-recorded matching success. TurnoverController requires an injected SuccessorResolver (no default). IPC ordering confirmed in code: ancestry gate (:684) before approved-list gate (:703), additive. Codex allowed_models untouched.
2. Session identity — sound apart from M1. with_resume refuses sup- prefix / padded / empty; complete_rotation refuses identity_conflated; rotation key is sup-rot- prefixed. Captured id reaches argv as one token through assert_argv_safe (scans every element). First-wins capture with session_id_conflict audits provider_session_ambiguous. Residual is M1's blank-field path.
3. Handoff integrity — verify_handoff binds the reviewed digest; model_used honest; READY gate blocks forwarding before evidence/review/forward; model-mismatch stop real+audited. Caveats I3 + M1.
4. R033/R595 — clean. No new/expedited approval path; RUNNABLE_MODES unchanged; only new flag is --config on orchestrator-watchdog (restricts). remote_approvals change is one note string. Bounded mode not enabled.
5. Containment — untouched (process.py absent from diff; also policy.py/github_flow.py/run_budget.py). R595 actuation moved verbatim into turnover_wiring.py; both channels still gate on the job-object precondition.
6. Supply chain — clean. Six new modules stdlib + intra-package only; zero third-party/framework hits; no dependency manifest changed.
7. Audit — new events go through the hash-chained log. Gaps: I2, and a rejected IPC model change raises IpcError out of Gate 3 without a row (pre-existing rule-4 behaviour the new check inherits; Gates 2/4/5 audit).
8. Regression — 1833 passed / 2 skipped / 555 deselected / 0 failed (179.69s). No skip/xfail/mark added. 82 added, 6 removed each with a stronger replacement. The four inverted model_chain tests are genuinely stronger; the ipc ancestry test is stronger (drives the real endpoint, requires worker_origin_denied first).

## Commands run
git rev-parse/status/log; git diff --stat ccf8806 8546a2e + per-file diffs; git grep for the removed constants, model-id literals, RUNNABLE_MODES, owner_enable/activation/R595, third-party/framework names, probe/argv/allowlist/pinned_model; full reads of the six new modules + producer report; pytest -k agent_supervisor (1833/2/0); two read-only scratchpad probes (probe_gate.py on require_ready/verify_post_launch; probe_router.py on ModelRouter.select). No repo writes, no git mutations, no project_control.py.
