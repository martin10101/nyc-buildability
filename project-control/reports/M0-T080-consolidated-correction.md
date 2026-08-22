# M0-T080 consolidated correction set (one round; no drip-feed)

Issued by the orchestrator after the COMPLETE T080 review set (G3 code, G4 integration, G5
security) at frozen identity `8546a2e8` / material `e3bd2a35`. Verdicts: G3 PASS (6 important),
G4 PASS (3 medium + 4 low), **G5 FAIL (1 must-fix)**. Per D-023-R016/R017 this is ONE
consolidated correction. The producer applies U1–U15 in wt-m0t080; the orchestrator then
re-freezes and re-reviews (full G5 re-pass clearing the must-fix, focused G3 on the fail-open
family, full-tree G4). No acceptance while the must-fix is open.

The through-line of the serious findings is a **fail-open family**: identity/continuity checks
that skip when a value is absent or unknown, instead of treating absent/unknown as a mismatch.
The supervisor writes the expectation down first, so "the successor said nothing" must never
satisfy a gate.

## Must-fix (blocks acceptance)

- **U1 (G5 M1 = G3 I-2) — post-rotation identity gates fail open on omitted fields.**
  `turnover_seam.verify_post_launch` (turnover_seam.py:449-468) and `require_ready` guard every
  comparison with `if expected and observed …`; `ClaudeCheckpoint.validate()` (models.py:173)
  checks only status+usage, so `task_id`/`branch`/`worktree`/`starting_sha`/`claude_session_id`
  may be empty on a well-formed (untrusted) checkpoint. A successor on the wrong task/branch/
  worktree/SHA — or the just-archived session — satisfies both gates by reporting blanks
  (demonstrated live by G5). Fix: an ABSENT/empty identity field the supervisor has an expectation
  for counts as a MISMATCH (fail closed); a READY that clears a gate must carry a non-empty
  `claude_session_id`. The `model` axis is independently backstopped by the R739 per-event
  expected_model stream check — keep that; add the four unbacked axes. Add tests with blank-field
  checkpoints (the current suite only exercises populated-but-wrong values, so it is structurally
  blind to this).

## Important (required rework; blocking-for-acceptance per gate-verdict semantics)

- **U2 (G3 I-3) — cross-model resume recorded as clean resume when the session model is unknown.**
  `decide_continuity` (session_continuity.py:262) adds CROSS_MODEL only when BOTH successor_model
  and session_model are non-empty; a recorded session with `model_id=""` + a different successor
  yields `mode="resume"` with no reasons. Per CLAUDE.md principle 3, unknown ⇒ impossibility, not
  "no objection": treat an unknown/empty recorded model against a known different successor as
  CROSS_MODEL (force reorientation). Test the empty-recorded-model case.
- **U3 (G3 I-1 / G5 I3 / G4 F3) — S11.3 verification is tautological + overstated.** `execute`
  builds the handoff from `facts` then verifies against the same object; `deterministic_verdict`
  re-derives only 6 of 14 fields, so no production divergence is possible. Fix the CLAIM and the
  COVERAGE: (a) make the deterministic verify re-derive from an INDEPENDENT source (re-read the
  git/ledger facts, not the in-memory build input) so it can actually refuse; if a fully
  independent re-derivation is out of scope under freeze, then (b) at minimum correct the docstring
  and producer-report §2.3/§3.3 to state honestly it is a completeness + subset-consistency gate,
  not 14-field independent re-derivation, and do not let `store_verified_handoff`/`verified_by_model`
  imply an independent check. Prefer (a); if (b), say so explicitly with the reason.
- **U4 (G3 I-4) — dead duplicate READY gate with a false docstring.** `rotation.assert_ready_checkpoint`
  has zero production callers; its new docstring (rotation.py:723-731) names SeamTurnover as "the
  production caller" — false — and it disagrees with the live `require_ready` (it demands
  `session == expected_session_id`, impossible before the successor reports). Remove the dead
  duplicate (preferred) or wire it and reconcile the two; either way fix the false docstring and
  the report §1.2 claim that this zero-caller surface was "fixed".
- **U5 (G5 I1) — probe_record treats an unparseable probe result as availability.** A truthy
  non-`ProbeOutcome` return is coerced to `ok=bool(outcome)` and recorded as a successful launch
  probe (`reason_code="probe_shape"`). Latent (no probe seam wired today) but goes live at the
  owner-checkpoint "wire a real probe" step. Fix: a non-`ProbeOutcome` return is `ok=False`
  (fail closed), matching the module's stated rule that an unreadable result proves nothing.
- **U6 (G5 I2) — NO_APPROVED_SUCCESSOR safe stop writes no audit row in the watchdog path.**
  `TurnoverController._no_launch` appends nothing; in `run_orchestrator_watchdog` (standalone under
  the OS scheduler) the only trace is returned JSON, while every other watchdog refusal
  (no_turnover, containment_refused, no_current_model) is hash-chain audited. Add a `_no_launch`
  audit row so "approved list empty / nothing probed / chain spent" leaves durable evidence.
- **U7 (G4 F1) — chain-exhaustion message claims an unearned probe.** The
  `approved_chain_exhausted` message (approved_models.py:421-428) asserts "Every candidate was
  tried by an actual launch probe" even when every attempt's reason_code is
  `model_probe_seam_missing`. Derive the sentence from the attempts' reason codes so it states what
  actually happened (nothing probed vs probed-and-failed). This is the measured-claims discipline
  applied to a refusal message.
- **U8 (G4 F2) — watchdog probe-ledger identity keying bricks the R595 orchestrator path.** The
  watchdog keys its ProbeLedger on `cli_version=""` (never passed) while `start` keys on the real
  `runner.executable_identity()["digest"]`; `orchestrator-watchdog` has no `--claude-executable`.
  Once the owner wires a real probe, a probe recorded by `start` can never satisfy the watchdog's
  identity match → `no_approved_successor` forever. Fix: give the watchdog the same CLI-identity
  source as `start` (accept `--claude-executable` / pass the real cli_version), so the two paths
  share one probe identity. Fail-closed today, but a latent activation-blocker — fix now.
- **U9 (G3 I-5) — launcher effort pin became a pass-through, adversarial case dropped
  undisclosed.** `turnover_adapters.py:342` now does `effort = str(request.effort or
  ALLOWED_SUCCESSOR_EFFORT)`; the removed test asserted the launcher ignored BOTH a caller model
  and a caller effort. Restore the launcher-level effort pin (the R159-governed value) and
  reinstate the adversarial test that passes a non-xhigh effort into a LaunchRequest and asserts it
  is ignored.
- **U10 (G3 I-6) — self-referential hold test.** r595_actuation.py:396-399
  (NoOtherHoldMovedTests) now asserts `APPROVED_SUCCESSOR == "claude-opus-4-8"` — a test-local
  constant against its own literal, which cannot fail — while the test name still claims to guard a
  production invariant. Restore an assertion against the real production value (or delete the
  vacuous assertion and point the class at the real coverage), so "no owner hold moved" is truly
  guarded.
- **U11 (G4 F5) — approved_models_conflict escapes as a traceback.** `load_controller_config` in
  `_run_loop` (cli.py:2669) is outside the typed-refusal except guard, so the new
  `approved_models_conflict` (ConfigError) reaches the operator as a raw traceback exit 1. Extend
  the T079-C5 "a refusal is a report, not a traceback" convention to ConfigError on this path.

## Load-bearing minors (fix while in these files)

- **U12 (G4 F7 / G5 N2) — crash window is fail-OPEN.** `complete_rotation` then `arm_ready_gate`
  are two durable writes; a crash between them leaves a completed rotation with no armed gate, so on
  restart the successor bypasses BOTH the READY gate and the identity check. This is the one
  fail-OPEN window in the change — make the two writes atomic, or make restart treat "a completed
  rotation with no armed gate" as must-re-verify (fail closed), not "no gate". Add the crash-window
  test (AS-43b covers only the armed-gate case).
- **U13 (G4 F4 / G3 M-1) — stale "pinned opus-4-8" claims.** Fix all six
  (turnover_wiring.py:75/:237, cli.py:2570/:2834, worker_turnover.py:19, and especially the
  self-contradicting `--authorize-turnover-actuation` --help text at cli.py:3280).
- **U14 — smaller minors:** G3 M-2 (validate the primary `none_reason`, not only the tuple);
  G4 F6 (scope provider_session_continuity per-run — compare ProviderSession.run_id so run B does
  not archive run A's session); G3 M-4 / G4 (doctor + config.example.toml probe wording accuracy re
  the quota-chain switch that probes without consulting/writing ProbeLedger); G3 N1 (catch LoopError
  in _rotate_at_seam so a failed resume does not leave a durable resume record); G3 M-5 (fix the
  nonexistent test-name reference); G3 M-7 (store_verified_handoff-before-assert_not_archived
  docstring). Report any you defer, with the reason.
- **U15 — report accuracy:** correct the producer-report figures to the reviewed identity (suite
  1833, cli.py 2923, loop.py 2076, census 280) — G4/G3 M-3; and correct the "exit 10/11" claims to
  note they are Refusal-object properties, not watchdog CLI exit codes.

## Owner-decision item (NOT a code correction — bundled to the final checkpoint)

- **Initial-run model pin governance (G5 I4 / G4 §3).** A run's FIRST model is admitted by
  `[claude] allowed_models` with no launch-probe requirement; every later selection is held to
  `[approved_models]` + probe. G4 rules this is NOT an R013 violation (the initial pin is neither a
  turnover, a fallback, nor a substitution). The producer must (a) document the pin's separate
  governance clearly in §2.4 + the doctor text so it is not misrepresented as covered by the
  approved list, and (b) the directive verifier will rule explicitly on whether R013 reaches the
  pin. The owner decision — "should the initial pin ALSO require the approved list + a probe?" — is
  bundled into the single final owner checkpoint (D-023-R034), not decided unilaterally under freeze.

## Re-review contract
After U1–U15, re-run the full supervisor suite (>= 1833/0/2 with new tests) and
`python tools/modularity_check.py --check` (failures 0; mind cli.py's 30-SLOC headroom — extract
before adding). Then the orchestrator re-freezes and dispatches: a full independent G5 re-pass
(must clear U1 and confirm the fail-open family closed), a focused G3 on U1-U4/U9-U10, and a
full-tree G4. Only then G2 re-record, directive verification, acceptance.
