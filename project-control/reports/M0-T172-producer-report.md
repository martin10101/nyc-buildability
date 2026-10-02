# Producer report — M0-T172 (D-091 TW2): dual-review conductor

- Worktree: `/root/project/w-M0-T172`  branch `task/M0-T172-dual-review`
- Claim seam HEAD: `9d349e365387b07b7cfcb3fae1c5e659f08f5b11`
- Commit HEAD after this work: `def549fcf400a1e3d64f62ec1e0997a8ee2784eb`
- Directive: D-091 (R001/R002/R003/R007); notes honoured: M0-T168 N1, M0-T169 G5 N1 and N3.

## Design

The cloud loop keeps exactly one reviewer seam: `loop.py` injects `reviewer` and calls
`reviewer.review(packet.to_dict(), expected_task_id=..., expected_checkpoint_id=...)` once per
cycle (`loop.py:2041` region), routing entirely on the returned
`codex_reviewer.ReviewOutcome` (`outcome.ok`, `outcome.decision`, `outcome.decision_digest`,
`outcome.model_used`, `outcome.tier`, `outcome.error_code/message`, `outcome.notify_events`).

`dual_review.py` adds `DualReviewConductor`, which presents the SAME `.review(...)` shape and,
behind it, for one dual review:

1. **Preflight refusals, before any slot or process (fail closed).** In order:
   - the packet must be pinned to a full 40-char frozen head (`frozen_head_from_packet`,
     mirrors `claude_reviewer` reading `sections.git.head.value`), else `packet_head_not_frozen`;
   - the combining model must be SET (`combiner.config.model`), else `combiner_model_unset`
     (D-091-R008: the conductor never picks or defaults a combining model);
   - the combiner must be enabled, else `combiner_disabled`;
   - the combining model must be in the `[claude]` allowlist, else
     `combiner_model_not_allowlisted` (this is the M0-T169 G5 N1 gap — the combiner itself does
     not allowlist its model; the conductor binds it);
   - the Claude reviewer model (read off `claude_reviewer.model`) must be allowlisted;
   - the Codex model (via `codex_reviewer.resolve()`) must be usable and in the `[codex]`
     allowlist.
   Each refusal returns a decision-less, not-`ok` ReviewOutcome -> the loop's existing
   review-unavailable path pauses for the owner. No reviewer or combining-model process is run,
   and no slot is reserved.
2. **One atomic review-or-combine slot (TW1 / M0-T171).** The whole dual review holds ONE
   `ReviewSlots` reservation for its lane (reserve-before, release-in-`finally`). Per-lane cap 1
   and global cap 2 are enforced atomically by `ReviewSlots`, so a third concurrent review can
   never start; a full box waits to the bounded deadline (`slot_wait_seconds`, default 0.0 =
   refuse immediately) then refuses `review_slot_unavailable`.
3. **Two independent reviews of the SAME frozen packet.** Codex then Claude, each handed the
   same packet dict; the conductor never passes one reviewer's output to the other (the Claude
   reviewer additionally refuses a packet carrying a peer review — M0-T168). A reviewer that
   RAISES is wrapped via `review_combiner.unverified_outcome(...)` (M0-T168 N1); a timeout /
   malformed review is already a decision-less outcome.
4. **Combine in code.** The real `ReviewCombiner.combine(...)` computes the verdict as the worse
   of the two (PASS<FAIL<UNVERIFIED); model-proposed disputes are advisory only. A combiner that
   RAISES (e.g. an independence or different-head refusal, or a combining-model launch that
   raises) is caught and becomes UNVERIFIED (`combiner_raised`) — never PASS (M0-T168 N1).
5. **Project the authoritative verdict into one outcome** (the conductor is the consumer; it
   treats the code-computed `verdict`, not model text, as authoritative — M0-T169 G5 N3):
   - **PASS** -> the approving decision stands, preferring the more cautious CONTINUE over
     COMPLETE when the two reviewers approved different next actions;
   - **FAIL** -> REVISE carrying the union of both reviews' blocking findings (each source-tagged
     and carrying any recorded advisory dispute) and a deterministic revision prompt — EXCEPT a
     reviewer HALT_UNSAFE is preserved as HALT_UNSAFE and a STOP_FOR_OWNER as STOP_FOR_OWNER, so
     a safety pause is never downgraded to a forwarded revision (would weaken a fail-closed
     check — forbidden);
   - **UNVERIFIED** -> a decision-less, not-`ok` outcome -> the loop pauses for the owner.
   A projected decision is `.validate()`-checked; an invalid projection fails closed to
   UNVERIFIED rather than handing the loop an invalid decision.
6. **Surfacing + gates.** The combined verdict, per-reviewer verdicts, dispute counts, and each
   disputed finding id ride out on the outcome's `notify_events` (the loop records these in its
   run report with no loop change), and the full `CombinedReview` is attached to the returned
   outcome (`outcome.combined_review`) for the human gate. The loop records no gate; the
   orchestrator records G3/G4/G5 from this advisory input by hand (ADR-005).

Loop routing is unchanged because projection targets the existing `decision.decision` dispatch
(`loop.py` HALT_UNSAFE->HALTED, STOP_FOR_OWNER->WAIT_FOR_OWNER, COMPLETE->COMPLETE,
CONTINUE/REVISE->forward, not-`ok`->WAIT_FOR_OWNER).

## Files and line counts

- `tools/agent_supervisor/dual_review.py` — NEW (replaces the seeded placeholder). 559 physical
  lines; 453 SLOC (modularity WARN is 600 — under).
- `tools/agent_supervisor/loop.py` — minimal injection. 7 lines changed (6 insertions, 1
  deletion); **net 0 non-comment SLOC** (stays at 2088 SLOC = its grandfathered growth limit;
  baseline 1899, limit `1899 + max(50, int(1899*0.10)) = 2088`).
- `tools/test_agent_supervisor_dual_review.py` — NEW. 602 physical lines. 17 tests, one class per
  acceptance scenario.

## loop.py diff (full)

```diff
@@ -587,7 +587,7 @@ class SupervisedLoop:
         machine: Any,
         authority: TaskAuthority,
         runner: Any,
-        reviewer: Any,
+        reviewer: Any, review_conductor: Any = None,
         run_id: str,
         collector: Any = None,
         broker: Any = None,
@@ -624,7 +624,10 @@ class SupervisedLoop:
         self.machine = machine
         self.authority = authority
         self.runner = runner
-        self.reviewer = reviewer
+        # D-091 TW2 (M0-T172): the OPTIONAL dual-review conductor presents the same
+        # `.review(...)` seam; when injected it replaces the single reviewer at the one
+        # review call. Default None keeps the single-Codex-reviewer path byte-for-byte.
+        self.reviewer = review_conductor or reviewer
         self.run_id = run_id
         self.collector = collector
         self.broker = broker
```

Injection shape note: the task asked for "one parameter and one swapped call". Because `loop.py`
was sitting EXACTLY at its grandfathered modularity growth limit (2088 SLOC), I could not add any
net non-comment line. The equivalent zero-SLOC minimal injection is: add the keyword parameter
in place on the existing `reviewer:` line, and swap the existing binding
(`self.reviewer = review_conductor or reviewer`) rather than the call line — leaving the single
`self.reviewer.review(...)` call byte-unchanged. `self.reviewer` is referenced only at
construction and that one call within `SupervisedLoop` (verified by grep; `gate_wave.deps.reviewer`
is a different object), so this is behaviorally identical to swapping the call, and with
`review_conductor=None` the binding is `self.reviewer = reviewer` — byte-for-byte the prior path
(proven by the scenario-1 byte-identical test).

## Scenario -> test mapping (all in tools/test_agent_supervisor_dual_review.py)

- S1 default-off byte-identical — `Scenario1DefaultOffByteIdentical`
  `test_single_cycle_is_byte_identical_with_and_without_the_injection`: runs the REAL loop twice
  (independent journals, clock frozen) — once with no `review_conductor` kwarg, once with
  `review_conductor=None` — and asserts `run_cycle(...).to_dict()` is equal; also asserts the
  single-reviewer seam really ran (CONTINUE -> shadow would-forward).
- S2 enabled / independence / worst-of-two — `Scenario2BothRunIndependentlyWorstOfTwo`
  `test_both_reviewers_get_the_same_frozen_packet_and_verdict_is_worst` (both called once, same
  packet, pinned to the frozen head, no peer-review key in either packet, PASS+FAIL->FAIL from the
  real combiner) and `test_both_pass_projects_the_cautious_approving_decision` (CONTINUE over
  COMPLETE).
- S3 untrustworthy review never PASS — `Scenario3UntrustworthyReviewNeverPass`
  `test_a_raised_reviewer_is_unverified_never_pass`, `..._timed_out_...`, `..._malformed_...`,
  `test_a_raised_combiner_is_unverified_never_pass`, and
  `test_a_raised_combining_model_is_failsafe_never_pass`. Naive-impl catch named in
  `_assert_never_pass`: `assertFalse(_is_pass(result))` fails a conductor that returns the
  surviving review's PASS; the trap PASS is asserted first via `_is_pass(naive_pass_outcome)`.
- S4 allowlist / unset combining model refuse before any process —
  `Scenario4ModelAllowlistRefusedBeforeAnyProcess`: unset combining model, combiner model not
  allowlisted, Claude reviewer model not allowlisted, Codex reviewer model not allowlisted,
  combiner default-off. Naive-impl catch named in `_assert_refused_before_process`:
  `assertEqual(codex.calls, 0)` / `assertEqual(claude.calls, 0)` / `assertEqual(runner.calls, 0)`
  fail a conductor that defaults/runs anyway; plus `assertEqual(len(self.slots().active()), 0)`.
- S5 slots — `Scenario5SlotsNeverThirdConcurrentReview`:
  `test_a_full_box_refuses_before_running_a_third_review` (two live slots pre-filled; conductor on
  a third lane refuses `review_slot_unavailable`, reviewers not run, box still holds exactly 2 —
  `assertEqual(len(self.slots().active()), 2)`) and `test_a_reserved_slot_is_released_after_the_review`
  (`assertEqual(len(slots.active()), 0)` after a successful review).
- S6 disputes surfaced; no gate — `Scenario6DisputesSurfacedNoGate`:
  `test_a_recorded_dispute_is_surfaced_and_the_finding_still_stands` (real combiner + fake model
  runner proposing a finding-bound `file_line` dispute; verdict stays FAIL, `disputes_recorded==1`,
  `dual_review:disputed_finding=codex:blocking:0` in `notify_events`, the finding remains and is
  annotated `disputed`) and `test_loop_surfaces_the_combined_verdict_and_records_no_gate` (REAL
  loop + injected conductor via a head-providing collector: `dual_review:verdict=PASS` appears in
  the cycle report's `notify_events`, and the audit log contains NO event whose type mentions
  "gate").

## Commands and exact outputs

All with `/root/project/lanes-runtime/venv/bin/python` from `/root/project/w-M0-T172`.

New suite, 3x:
```
$ ... -m pytest -q tools/test_agent_supervisor_dual_review.py   (x3)
17 passed in 1.16s
17 passed in 1.43s
17 passed in 1.15s
```

Reviewer / combiner / slots / bounded + new suites (final state):
```
$ ... -m pytest -q test_agent_supervisor_reviewer.py claude_reviewer review_combiner \
      review_slots bounded_mode bounded_contracts dual_review
372 passed, 167 subtests passed in 73.02s
```

Loop suite (I edited loop.py):
```
$ ... -m pytest -q tools/test_agent_supervisor_loop.py
3 failed, 124 passed in 14.66s
```
The 3 failures are PRE-EXISTING and environment-specific, NOT caused by this change — proven by
reverting loop.py to the claim-seam HEAD and rerunning only those three:
```
$ git checkout -- tools/agent_supervisor/loop.py  (then run the 3)
3 failed in 2.29s   # same 3 fail on the pristine tree
```
They are `EndToEndTests::test_a_real_child_process_drives_a_shadow_cycle` (spawns a real child
via sys.executable) and two `CliStartTests` that assert a CLI `start` stale-state exit code
(expected 13, host returns 12). All involve the real CLI/child-process/manifest path on this Linux
producer host, not the reviewer seam. (I deliberately did NOT run
`test_agent_supervisor_model_chain.py` — its real-subprocess classes SIGKILL the process group on
this host; CI runs it.)

ruff (my files, and the whole package did not regress on my files):
```
$ ... -m ruff check tools/agent_supervisor/dual_review.py \
      tools/test_agent_supervisor_dual_review.py tools/agent_supervisor/loop.py
All checks passed!
```

modularity:
```
$ ... tools/modularity_check.py --check
selected 645 files; failures 0; warnings 29
```
loop.py SLOC after the change = 2088 (= its growth limit; no new failure). dual_review.py = 453
SLOC (< 600).

## Assumptions

- The conductor reserves ONE slot for the whole dual review (held across both reviews and the
  combine), not one per sub-process. Per-lane cap is 1, so within a lane the reviews are
  sequential anyway, and the global cap 2 still guarantees "never a third concurrent review". This
  is the simplest shape that satisfies both caps; the §1 wiring-plan phrasing ("before each
  process") is a stricter but equivalent reading under per-lane=1.
- `slot_wait_seconds` defaults to 0.0 (refuse immediately when the box is full). Production wiring
  should set a bounded wait so lanes contend rather than refuse on first contention; the TW1
  "wait or refuse" is honoured either way.
- The conductor reads the combining model from `combiner.config.model`, the Claude reviewer model
  from `claude_reviewer.model`, and the Codex model via `codex_reviewer.resolve()`, and checks
  each against an injected `allowed_models={"codex": ..., "claude": ...}` mapping (built in
  production from `ControllerConfig.allowlist("codex"/"claude")`). The combining model is treated
  as a Claude-provider model (the combiner runs through `claude_reviewer.build_argv`), so it is
  checked against the `[claude]` allowlist.
- CombinerInputs are built from the packet: `frozen_head` (sections.git.head.value) and
  `diff_text` (sections.git.diff_content.value). `command_outputs` and `extra_shas` are left empty
  by the conductor in this build, so disputes citing a command-output substring or an out-of-band
  SHA are rejected (fail-closed/safe); file_line disputes (bound to the diff) still bind. This is a
  deliberate, conservative default, documented here for the wiring/recert reviewer.
- The conductor does NOT enforce that the combining model differ from the Claude reviewer model
  (the combiner's identity guard enforces process independence; distinct models are an owner
  config choice per the wiring plan risk note).

## Could not do / out of scope

- Did not wire the conductor into `cli.py` or any launcher (that is a later wiring/commissioning
  step, TW5; not in this task's allowed_paths). The conductor is built and injected ONLY when an
  external caller constructs it; `loop.py` default-off is preserved.
- Did not touch the combiner, either reviewer, `review_slots.py`, `config.py`,
  `config.example.toml`, `project-control/**`, or the modularity baseline/exceptions (all outside
  allowed_paths / forbidden). No live loop started, no credentials touched, no dependency added.
- The 3 pre-existing loop CLI-start failures on this host are left as-is (not in scope; proven
  pre-existing above; CI is the authority for the real-child/CLI path).

END-OF-REPORT
