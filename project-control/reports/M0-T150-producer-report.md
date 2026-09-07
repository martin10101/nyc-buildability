# M0-T150 producer report - supervisor management-layer design (D-033-R001/R002/R008)

Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t150`, branch
`task/M0-T150-management-layer-design`, base `9b03da5f`. Producer edits only
(two files: `docs/SUPERVISOR_MANAGEMENT_LAYER_DESIGN.md` and this report); the
orchestrator commits and integrates. Worktree guard: `git rev-parse
--show-toplevel` printed `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t150` (PASS).

## Packet-file discrepancy (disclosed)

`project-control/tasks/M0-T150.json` does NOT exist in this worktree - the
latest task file present is `M0-T149.json`
(`find . -iname '*M0-T150*'` returned nothing; `ls project-control/tasks/`
tops out at M0-T149). I proceeded from directive D-033
(`project-control/directives/D-033-supervisor-management-layer/`, the authority
named in my brief) plus the S1-S4 scenario descriptions given in the dispatch
prompt. The directive requirements, manifest, and verification files are all
present and were read in full. If the orchestrator intended a materialized
M0-T150 packet with different allowed_paths or acceptance scenarios, this design
should be re-checked against it before gating; nothing I read contradicts the
brief.

## What I read (all in-worktree, base 9b03da5f)

- Directive D-033: `source-001.md`, `requirements.json` (R001-R008),
  `manifest.json`, `verification.json`. R001/R002/R008 are mine; R003/R004 fed
  by the design; R005/R006/R007 constraints honored.
- `tools/agent_supervisor/loop.py` - the state machine: the
  START_CLAUDE -> ... -> CODEX_REVIEW -> VALIDATE_DECISION -> POLICY_CHECK ->
  FORWARD_PROMPT flow; the decision handlers (`COMPLETE` at 2174,
  `STOP_FOR_OWNER` 2136, `REVISE`+revision breaker 2189, HARD_DENY/HALT 2101);
  `_collect` 2400; `forward_exactly_once` 2472; `_send_forward` 2356;
  `_resume_approved_forward` 2644; the breaker wiring 2018-2039.
- `tools/agent_supervisor/cli.py` - `production_task_authority` 2622; `_run_loop`
  2643 (launch bindings, `next_task.plan_close_run` at 2689 closing COMPLETE to
  IDLE, sizing, model resolution); `bounded_mode_gate` import; the status/
  recovery flags disclosing `limited_auto_enabled`.
- `tools/agent_supervisor/policy.py` - tiers AUTO/NOTIFY/ASK/HARD_DENY;
  unclassifiable -> ASK; the synchronous-stop list.
- `tools/agent_supervisor/evidence.py` (via `M0-T148-producer-report.md`) -
  `run_command`/`collect_command_transcripts`/`collect_completeness`, the M0-T148
  packet-completeness sections, `DEFAULT_COMMAND_TIMEOUT_SECONDS`, digest binding.
- `tools/agent_supervisor/ephemeral_review.py` - the fresh read-only reviewer
  process pattern, `REVIEWER_ROLE`, independence proof, role honesty.
- `tools/agent_supervisor/claude_runner.py` - `RunnerConfig`/`build_argv`,
  `REQUIRED_PERMISSION_MODE` enforcement.
- `tools/agent_supervisor/next_task.py` - `plan_close_run` 109,
  `record_advancement` 187 (exactly-once CAS), `select_next_packet`.
- `tools/agent_supervisor/start_gate.py` - `bounded_mode_gate` 62,
  `seal_owner_gate_refusal`, the durable owner-enable precedent.
- `tools/project_control.py` - the module docstring's ACCEPT PRECONDITIONS
  (48-60) and LIFECYCLE-AWARE ACCEPTANCE / CONTROL-PLANE CONTENT IDENTITY /
  ATOMIC WRITES sections; `submit` 1028, `gate` 1076 (gate classes + role +
  identity stamp), `accept` 1191 (every precondition), `_task_git_identity` 375.
- `tools/directive_registry.py` - `frozen_git_identity` 1554,
  `task_verification_result` 761 (producer!=verifier, reviewed_sha compare 1004),
  `content_manifest` / `material_digest`.
- `.claude/hooks/readonly_agent_guard.py` - the fail-closed read-only spawn
  guard; `.claude/rules/supervisor-freeze.md` - AD-093 qualifying evidence +
  D-024 recognition precedent + gates + suite-baseline duty.
- Precedents: `M0-T148-producer-report.md` and
  `D-032-pl04-packet-collection-convergence.md` (packet-contract history).

## Key design decisions and rationale

1. **The controller is the deterministic host; the loop's COMPLETE is the seam.**
   The single most important finding: the loop TODAY stops at COMPLETE and
   `next_task.plan_close_run` only closes it to IDLE - both explicitly annotated
   "NEVER merges, accepts, deploys, or crosses an owner gate" (loop.py:2174,
   cli.py:2689). The entire gate-wave + acceptance work D-033 wants is exactly
   the gap between COMPLETE and the next dispatch. So the design ADDS a new
   post-COMPLETE stage rather than repurposing any existing state, and treats
   this gap as the load-bearing seam.

2. **Reuse existing bounded-session machinery, invent no provider path.** Gate
   reviewers are `ephemeral_review.conduct_ephemeral_review` dispatches (fresh,
   read-only, independence-proofed) with per-gate contracts; G2 is
   controller-run command capture (`evidence.run_command`), not a reviewer.

3. **Every gate/accept precondition is the existing project_control code,
   unchanged.** The controller INVOKES `gate()`/`accept()`; it does not
   reimplement them. This keeps the fail-closed guards (self-check never
   satisfies independent, reviewer!=producer, deps accepted, zero open blockers,
   directive verification at content identity, producer!=verifier) exactly where
   they already live and already have tests.

4. **The DCV row must come from an independent verifier SESSION, not the
   controller.** The controller can transcribe verification rows but cannot
   author the judgments; a distinct read-only `directive-compliance-verifier`
   session produces them, so `producer != verifier` holds by construction and
   the controller stays a mechanical recorder.

5. **The switch mirrors `--owner-enable-bounded-auto` exactly** (per-launch,
   default-OFF, durable journal record, structured refusal if reached
   un-enabled) so switch-off is provably today's behavior and the precedent's
   review history transfers.

6. **The controller committer identity (Section 3.5 / item I4) is flagged as the
   most sensitive seam** - it is a genuine ADR-005 authority extension (git is
   orchestrator-only today), switch-gated, scoped to control-plane + task-branch
   integration, structurally push/deploy-incapable via the read-only guard +
   push_policy. Deliberately isolated into implementation task T-C and mapped to
   Stage 3.

7. **Four seams the code LACKS are named explicitly (I1-I4)** rather than assumed
   as existing APIs, per the brief's constraint.

## Open questions for reviewers

1. Should the independent verifier session (Section 3.3) be the SAME dispatch as
   one of the gate reviewers (e.g. fold DCV into a G-class review) or strictly a
   separate session? I designed it separate for a clean producer!=verifier
   story; a reviewer may prefer folding it into G4 to save a dispatch.
2. The controller committer identity (I4) extends ADR-005 git authority. Is a
   distinct committer identity acceptable in principle, or should Stage 3 instead
   leave the commit to a still-human step and only automate accept()+advance?
   This is an owner/architecture call the design surfaces but does not decide.
3. loop.py sits at its modularity ceiling (M0-T148 report: measured SLOC 2088 ==
   limit, zero headroom). The design mandates the new gate-wave stage be a NEW
   module. Reviewers should confirm the minimal loop.py/cli.py wiring stays under
   the ceiling or that a decomposition task precedes T-A.
4. Is the missing `project-control/tasks/M0-T150.json` packet an orchestrator
   oversight, or is this design expected to live purely under the D-033-BOOTSTRAP
   sentinel with rows accruing as T-A..T-C are produced (the pattern
   `verification.json` describes)? Confirm before the gate.

## Anything I could not determine from the code

- I could not confirm the exact reviewer-verdict output schema for G3/G4/G5 gate
  sessions because none exists yet (I2/I3 are unbuilt); the design specifies it
  reuses the codex reviewer's bounded-retry-then-fail-closed discipline and a
  constrained PASS/FAIL/BLOCKED verdict, but the concrete schema is an
  implementation-task deliverable, not an existing artifact I could cite.
- I did not run any tests or tooling; this is a design-only task and I modified
  no code. No self-check command output is applicable. (No commands beyond the
  read-only git/grep inspection above were run.)

## Acceptance-scenario -> design-section map

| Scenario | Satisfied by |
|---|---|
| S1 gate waves (independence + gate classes preserved; G2 never independent) | Sections 2 and 4 |
| S2 acceptance (all accept() preconditions; DCV from independent verifier; identity stamp; committer + advance) | Sections 3 and 4 |
| S3 not-automatable set + exact refusal behavior | Section 5 |
| S4 default-OFF switch + staged R595 package (safeguards, rollback, owner command shapes) | Sections 6 and 7 |
| D-033-R008 motivation (no new long-lived-chat dependence) | Section 1 |
| D-033-R005 (no activation; holds intact) / R006 (separation; G6/owner never automatable) / R007 (freeze-lane citation) | Sections 5, 6, 7 / 4, 5 / 9 |
