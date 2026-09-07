# Supervisor management-layer design - controller-run gate waves and acceptance

Directive: D-033 (owner, 2026-09-07),
`project-control/directives/D-033-supervisor-management-layer/`.
This document is the reviewed DESIGN for D-033-R001 (gate waves), D-033-R002
(acceptance), and the D-033-R008 motivation row; it also feeds D-033-R003
(implementation switch), D-033-R004 (staged activation package), and records the
D-033-R005/R006/R007 constraints. It is design only: no `tools/agent_supervisor`
code is modified by this task. Every code reference below was read in the
`wt-m0t150` worktree at base `9b03da5f`; where a needed seam does not exist yet
it is called out explicitly as an implementation-task item (Section 9), never
invented as an existing API.

Vocabulary used throughout:

- **Controller** = the certified `tools/agent_supervisor` process (its CLI in
  `cli.py` + the `SupervisedLoop` in `loop.py`), the deterministic host D-033
  designates for mechanical Tier-A management. It is a DISTINCT identity from
  both the worker (producer) session and any reviewer session.
- **Worker session** = the dispatched Claude producer that edits files in its
  isolated worktree and returns a checkpoint. Orchestrator-only git means its
  deliverables stay uncommitted/untracked for the task's whole life
  (`D-032-pl04-packet-collection-convergence.md` section 4).
- **Reviewer session** = a fresh, read-only provider process that returns a
  schema-bound verdict and writes nothing.
- **Orchestrator** = today's main chat session that manually performs the
  Tier-A ledger chain. D-033 moves the MECHANICAL parts of that role into the
  controller behind an owner-gated switch; the human-only parts stay with the
  owner (Section 5).

---

## 1. Context and goal (D-033-R008)

### 1.1 Why this exists

The orchestrator chat session is currently the management layer: after a worker
finishes a task it manually dispatches gate reviewers, records
`project-control/gates/*.json`, assembles the directive verification rows, runs
`python tools/project_control.py accept`, commits, and dispatches the successor.
Every one of those steps accretes context into one long-lived chat session.
Section 84 of `SESSION_HANDOFF` and the memory record
`orchestrator-rotation-ceiling` document the consequence: an absolute
rotate-at-seam ceiling (~400k tokens) that forces a session handoff regardless
of model window. The management work itself is almost entirely mechanical and
deterministic - reading durable ledger state, comparing gate records, invoking a
CLI with fixed preconditions - yet it is trapped inside a growing conversation.

### 1.2 Steady-state operator model

The target model separates two planes:

- **Production + verification plane (unattended, durable-state-driven).** The
  loop runs the worker; on a terminal checkpoint the controller runs the gate
  wave (Section 2) and the acceptance chain (Section 3) and advances the queue.
  Every input it reads is durable repository state: the task packet, the frozen
  evidence packet, `project-control/gates/`, `project-control/blockers/`, the
  directive registry, and the durable journal. It holds NO conversational
  memory between tasks; `next_task.record_advancement` (an exactly-once CAS on a
  durable key, `next_task.py:187`) is the only cross-task state.
- **Exception plane (short fresh sessions).** Convergences, blockers, owner
  escalations, and G6 legal approvals happen in SHORT FRESH sessions that read
  only durable state (`/deficit-convergence`, `/replan-project`, the blocker and
  directive files). A fresh session reconstructs everything it needs from
  `project-control/` + git + the audit journal; nothing depends on a prior
  chat's context.

The design's load-bearing invariant for D-033-R008: **no step introduces a new
dependence on long-lived chat context.** The controller's decisions are a pure
function of durable state and its own audit journal. Any human touch is an
explicit park-and-ask (Section 5 / Section 8) that a fresh session can pick up
from the durable record alone - exactly the property the supervised loop already
has for forwarding (`_resume_approved_forward`, `loop.py:2644`, reconstructs an
approved forward across a process boundary from the journal with no live object).

---

## 2. Gate-wave engine (D-033-R001)

### 2.1 The seam that exists today

The loop's terminal for a finished unit is the `COMPLETE` decision. In
`loop.py:2174` a `COMPLETE` verdict transitions to the `COMPLETE` state and
returns `stop("stage_complete", ...)`; its own audit note states COMPLETE
"never merges, accepts, deploys, or closes an owner gate." `next_task.plan_close_run`
(`next_task.py:109`) then closes that COMPLETE run to IDLE so the next task can
start, and its call site in `cli.py:2689` repeats: "Closing NEVER merges,
accepts, deploys, or crosses an owner gate; it only returns the checkout to
IDLE." **So nothing between COMPLETE and the next worker dispatch runs a gate
wave or an acceptance today.** That gap is precisely the orchestrator's manual
work, and it is what D-033-R001/R002 move into the controller.

### 2.2 What the gate-wave engine adds

A new post-COMPLETE stage in the controller (implementation item I1, Section 9):
after a worker's terminal checkpoint on a task whose packet declares
`required_gates`, the controller runs a **gate wave** - one dispatch per
required independent gate - before it closes the run to IDLE.

Reviewer dispatch reuses the existing bounded-session machinery, not a new
provider path:

- `ephemeral_review.conduct_ephemeral_review` already launches ONE fresh,
  read-only reviewer process per review, records a `ReviewRecord` distinguishing
  the read-only `reviewer` role from a writable `worker` (`ephemeral_review.py:20`,
  `REVIEWER_ROLE = "reviewer"`), and stamps an independence proof
  (`_independence_proof`, distinct packet digest, `ephemeral_review.py:146`).
  The gate-wave dispatcher is a thin wrapper that runs this once per gate with a
  per-gate contract.
- `claude_runner.build_argv` (`claude_runner.py:346`) builds the worker/reviewer
  argv; `RunnerConfig.permission_mode` defaults to `REQUIRED_PERMISSION_MODE`
  and `build_argv` refuses any other mode unless explicitly set
  (`claude_runner.py:355`). Reviewer sessions launch with the read-only posture
  and are additionally boxed by the `readonly_agent_guard` hook (Section 4).

### 2.3 Per-gate contracts (gate classes are preserved)

The existing gate CLASSES in `project_control.py` are honored exactly; the
controller does not invent a gate taxonomy:

- **G2 (self-check) is controller-run command capture, NOT a reviewer session.**
  `evidence.EvidenceCollector.run_command` / `collect_command_transcripts`
  (built in M0-T148, `evidence.py`, per `M0-T148-producer-report.md`) already
  execute the packet's documented test commands via `process.run` in the worker
  worktree and record argv/exit/digest-bound transcripts. G2 evidence is that
  transcript set. `project_control.gate()` classifies G2 as a `SELF_CHECK_GATES`
  member and REQUIRES `reviewer == "orchestrator"`, role `self_check`
  (`project_control.py:1086`). The controller records G2 with the reserved
  `orchestrator` label. Because `accept()` rejects any independent gate whose
  record role is `self_check` (`project_control.py:1214`), G2 can never satisfy
  an independent gate - the invariant D-033-R001 names explicitly.
- **G3/G4/G5 are independent reviewer sessions.** Each is one
  `conduct_ephemeral_review` dispatch with a gate-specific prompt contract
  (G3 code review, G4 acceptance-scenario/product review, G5 security) and a
  schema-constrained verdict. The reviewer output schema is the constrained
  `PASS | FAIL | BLOCKED` verdict plus findings; it reuses the same
  bounded-retry-then-fail-closed discipline the codex reviewer uses
  (`schema_retry_exhausted` -> unavailable, `loop.py:2050`), so a reviewer that
  cannot produce a schema-valid verdict is UNAVAILABLE (park), never a silent
  pass.
- **G0/G7 remain administrative** (`ADMINISTRATIVE_GATES`, recorded by
  `orchestrator`, `project_control.py:1092`). Under the switch the controller
  holds the `orchestrator` procedural label for these; they are not part of the
  automatable review wave and the readiness/release decision stays exactly as
  ADR-005 defines it.

### 2.4 How a verdict becomes a ledger gate record

The reviewer session writes nothing. The controller (deterministic process)
translates the schema-bound verdict into a gate record by invoking the same
code path a human orchestrator uses: `project_control.gate()`
(`project_control.py:1076`). That function:

- writes `project-control/gates/<task>-<gate>.json` with
  `{task_id, gate_id, reviewer, role, result, report_file, reviewed_at}`
  (`project_control.py:1125`);
- for an independent gate REQUIRES `reviewer != RESERVED_ORCHESTRATOR`
  (`:1104`), `reviewer != producer` (`:1109`), and `reviewer in reviewer_agents`
  (`:1115`), assigning `role = "independent_review"`;
- for an in-regime task stamps `content_manifest_sha256` and `reviewed_sha`
  via `_task_git_identity` -> `frozen_git_identity` (`:1130`, identity impl
  `directive_registry.py:1554`), so acceptance can later detect a stale
  post-review edit.

The IDENTITY the record carries is the reviewer session's own agent identity
(the value the controller passes as `--reviewer`), which MUST be the identity
under which the reviewer process ran (implementation item I2 binds these: the
controller records the reviewer session identity at dispatch and passes that
exact string to `gate()`; a mismatch fails closed). The gate report file is the
reviewer's captured verdict written to `project-control/reports/` by the
controller from the session output (the reviewer did not write it; the
controller transcribes the bounded verdict, digest-bound, exactly as M0-T148
transcribes command transcripts).

### 2.5 Reviewer-identity separation (enforcement)

Two mechanisms enforce "a reviewer session is a DIFFERENT identity from the
producer and is read-only":

1. **Read-only at the tool layer.** `.claude/hooks/readonly_agent_guard.py`
   (wired as a PreToolUse hook in tracked `.claude/settings.json`) DENIES every
   file-mutation tool and every repo/GitHub/control-plane-mutating Bash/PowerShell
   command for any spawned identity that is in `READ_ONLY_AGENTS` or is not a
   known write-authorized roster identity; an unidentifiable or named spawn fails
   CLOSED (`readonly_agent_guard.py:13-25`). Reviewer sessions run under a
   read-only reviewer identity, so the guard denies any write they attempt.
   (Design note carried from memory `named-spawns-are-readonly`: a WRITE-capable
   producer must be spawned UNNAMED to resolve its roster identity; reviewers are
   the opposite - they must NOT resolve to a write-authorized identity.)
2. **Different identity from the producer at the ledger layer.** `gate()`
   refuses `reviewer == producer` for independent gates (`project_control.py:1109`)
   and `accept()` re-checks it (`:1220`). Implementation item I2 adds the
   controller-side check: the reviewer session identity recorded at dispatch must
   differ from the worker/producer session identity recorded for the task; if
   equal, the wave refuses to record and parks (negative test: Section 4).

### 2.6 FAIL / BLOCKED handling

- **FAIL on an independent gate**: `gate()` moves an `awaiting_gate` task to
  `rework` (`project_control.py:1151`). The controller forwards the reviewer's
  findings to the WORKER as a rework prompt through the existing forward path
  (`build_forwarded_prompt` + `forward_exactly_once`, `loop.py:2225`/`2472`),
  i.e. rework flows forward to the same worker in the same durable-outbox,
  exactly-once shape the loop already uses. This is bounded by
  `consecutive_revision_loops` (`loop.py:2189`) exactly as content REVISE is, so
  a gate that keeps failing trips the breaker and parks for the owner rather than
  looping.
- **BLOCKED on any gate**: `gate()` moves the task to `blocked`
  (`project_control.py:1154`). The controller stops the wave and parks: a
  BLOCKED gate is an owner/exception-plane event (Section 5), never a degrade.

---

## 3. Acceptance engine (D-033-R002)

### 3.1 The Tier-A chain the controller executes

Under ADR-006 Tier A, ordinary acceptance after required checks pass proceeds
without per-merge owner approval. The controller executes the same chain the
orchestrator runs today: `submit` (if not already at `awaiting_gate`) -> gate
records (Section 2) -> `accept` -> queue advance. It invokes the real
`project_control.py` subcommands; it does not reimplement their logic.

### 3.2 Every accept() precondition is preserved

`accept()` (`project_control.py:1191`) fails closed on ALL of the following, and
the controller changes NONE of them - it only supplies inputs and must pass the
same checks:

1. `--agent orchestrator` label (`:1192`). The controller holds this procedural
   label; the tool cannot verify the label, so the REAL separation lives in the
   gate-record roles and the verification rows, not the label (Section 4).
2. `status == awaiting_gate` (`:1198`).
3. every `required_gates` entry has a `PASS` record, and for `INDEPENDENT_GATES`
   the record is not `self_check` and its `reviewer != producer` (`:1207-1222`).
4. every dependency task is `accepted` (`:1223-1233`).
5. zero open blocker records referencing the task; unreadable or status-missing
   blocker files fail closed (`:1234-1246`).
6. for an in-regime task: `_directive_accept_reasons` (`:1253`) requires valid
   directive references, a matching git-canonical content identity, a matching
   reviewed COMMIT, and independent PER-TASK verification of every applicable
   requirement at that identity (the DCV row). `_task_git_identity` ->
   `frozen_git_identity` supplies the content identity; `reviewed_sha` is
   ACTUALLY compared (`directive_registry.py:1004`, D-004-R630).

The `producer != verifier` rule is enforced inside the verification-row check:
`task_verification_result` (`directive_registry.py:761`) rejects rows whose
verifier is the producer, plus duplicate/extra/cross-task/stale rows, all fail
closed.

### 3.3 The DCV row must come from an INDEPENDENT verifier session

This is the sharpest constraint and the reason the controller cannot simply
"accept". The directive verification rows in the task's `verification.json`
(and the directive registry) must be authored by a `directive-compliance-verifier`
identity that is NOT the producer and NOT the controller acting as producer.
The design:

- After the gate wave passes, the controller dispatches ONE read-only
  verifier session (same bounded machinery as the reviewers) whose contract is:
  read the frozen evidence packet + the applicable directive requirement set
  (derived by `evaluate_task_refs`, the resolver, see memory
  `directive-selective-citation-guard`) and emit the schema-constrained
  verification rows (PASS / justified NOT_APPLICABLE) at the reviewed content
  identity.
- The controller transcribes those rows into the verification file and stamps
  each with the verifier identity + `reviewed_sha` = the content identity the
  reviewer saw. `accept()` then re-derives applicability and checks every row
  independently; a selective-citation gap fails closed (memory
  `directive-selective-citation-guard`; `_directive_accept_reasons`).
- Because the verifier session is a distinct read-only identity, the
  `producer != verifier` precondition holds by construction, and the controller
  is neither producer nor verifier - it is the mechanical recorder.

The evidence-map assembly (the big `verification.json` built from journalled
agent outputs, worst-of dedup, per memory `in-regime-accept-mechanics`) is the
controller's transcription job, but the JUDGMENTS in it are the independent
verifier's. The 64k agent-output ceiling and worst-of-not-last-wins dedup rules
from that memory are implementation constraints on the transcription seam.

### 3.4 Content-identity stamping

Every stamp - on the gate records, on the submit report, and on the verification
rows - uses the one shared implementation `frozen_git_identity`
(`directive_registry.py:1554`) through `_task_git_identity`
(`project_control.py:375`). A purely lifecycle-bookkeeping control-plane edit
does not move the identity by design (`project_control.py:92-104`), so the
controller's own status writes between submit and accept do not invalidate the
reviewed identity. The reviewed_sha the controller passes at accept MUST equal
live HEAD of the reviewed content (memory `in-regime-accept-mechanics`: "gate
needs reviewed_sha==HEAD"); implementation item I3 makes the controller re-stamp
if the integration commit moved HEAD, and re-gate rather than accept against a
stale identity.

### 3.5 Who commits, and queue advance

Today the orchestrator integrates git (ADR-005). Under the switch the controller
becomes a DISTINCT committer identity that commits the accepted task's control-
plane transition (status, gate records, verification rows) citing the run-id in
the commit trailer, so provenance ties every managed acceptance to its supervised
run. This is a genuine authority extension and is the most sensitive seam
(implementation item I4); it is OFF unless the switch is on, and even then it is
scoped to control-plane + accepted task-branch integration under Tier A - never a
push, deploy, PR #241, or anything in Section 5. After a recorded acceptance the
controller advances via `next_task.record_advancement` (exactly-once CAS,
`next_task.py:187`) + `select_next_packet` and dispatches the successor worker;
a crash at the advancement boundary can neither double-advance nor lose the
advancement (`next_task.py` module docstring, points 1-3).

---

## 4. Separation-of-duties enforcement (D-033-R006)

For each ADR-005 authority rule, the machine enforcement under controller
execution and the negative test that catches its loss:

| ADR-005 rule | Machine enforcement | Negative / mutation test |
|---|---|---|
| A producer never records its own independent gate | `gate()` refuses `reviewer == producer` for `INDEPENDENT_GATES` (`project_control.py:1109`); reviewer must be in `reviewer_agents` (`:1115`) | Drive the wave with the reviewer identity set equal to the worker/producer identity -> `gate()` refuses; the wave parks. Mutation: delete the `reviewer == producer` guard -> the negative test must fail. |
| A reviewer session writes nothing | `readonly_agent_guard.py` denies every mutation tool + repo/GH/control-plane Bash/PowerShell for read-only / unknown / named identities, fail-closed on unparseable payloads (`:27-54`) | Have the reviewer session attempt a Write and a `git commit` -> both DENY (exit 0, `permissionDecision == deny`). Mutation: add the reviewer identity to the write-authorized roster -> the deny test must fail. |
| A self-check never satisfies an independent gate | `accept()` rejects an independent gate whose record role is `self_check` (`project_control.py:1214`) | Record G3 as a `self_check` record, then accept -> refused with "a self_check record can never satisfy it". Mutation: relax the role check -> accept wrongly succeeds; test catches it. |
| G2 never satisfies an independent gate | G2 is a `SELF_CHECK_GATES` member; `gate()` forces `reviewer == orchestrator`, role `self_check` (`:1086`) | Try to record G2 with a non-orchestrator reviewer or as `independent_review` -> refused. |
| The codex/gate reviewer never gains ledger-write or integration authority | Reviewer runs under the read-only guard; only the controller (distinct identity) calls `gate()`/`accept()`; `ephemeral_review` records role `reviewer`, never `worker`, for a review dispatch (`ephemeral_review.py:20`) | Reviewer session attempts to invoke `project_control.py gate`/`accept` -> denied by the guard as a control-plane mutation. |
| The producer/controller cannot accept its own review | `accept()` requires independent gates with `reviewer != producer` and directive rows with `verifier != producer` (`project_control.py:1220`, `directive_registry.py:761`); the reserved `orchestrator` cannot record an independent gate (`:1104`) | Set the verifier row author = producer -> `task_verification_result` fails closed. Mutation: drop the verifier-not-producer check -> test catches it. |
| Controller is neither producer nor independent reviewer | Controller holds the `orchestrator` procedural label (records G2/G0/G7 + runs accept) but is BLOCKED from independent gates because `reviewer == RESERVED_ORCHESTRATOR` is refused for independent gates (`:1104`) | Attempt to have the controller record G3 itself (reviewer=orchestrator) -> refused; an independent reviewer identity is required. |

Mutation-test plan: each enforcement above ships with a red/green pair - a
positive test proving the legitimate path records/accepts, and a mutation test
that removes exactly the guard line and asserts the negative test flips from
DENY to ALLOW (i.e. the guard is load-bearing). This mirrors the M0-T148
"redaction is load-bearing" mutation test (`M0-T148-producer-report.md`, S5).
The suite re-baseline duty from `supervisor-freeze.md` section 4 applies: the
`tools/agent_supervisor` tree hash changes, so the freeze baseline (>= 1165
tests, 0 failures) is re-established under G0/G2/G3/G5.

---

## 5. Not automatable (S3 / D-033-R006 / D-033-R005)

The controller REFUSES and parks (owner ask, never degrade) when the queue meets
any of these; each is an exception-plane hand-off, and the refusal is a durable
park a fresh session can pick up:

- **G6 qualified-human legal / zoning approval.** Never dispatched to a reviewer
  session. A task whose `required_gates` include G6 stops at the gate wave: the
  controller records no G6 and parks with an owner ask ("G6 requires a qualified
  human"). CLAUDE.md permanent principle 1 + Tier D / Section 20.
- **Owner-only actions.** Credentials, paid-account creation, payments,
  verification codes, production approval - the `owner-escalation-boundary`
  set. The policy engine already routes these to `HARD_DENY`/`ASK`
  (`policy.py`, `HARD_DENY_ARGUMENTS`, blocking ASK classes); the controller
  honors the verdict and parks exactly as the loop parks a `STOP_FOR_OWNER`
  decision (`loop.py:2136`).
- **Pushes / deploys / PR #241 under current holds.** `push_policy` gates every
  push/privileged-workflow/deploy path to ASK with NO push (`cli.py:_check_push_policy`,
  `:834`); PR #241 stays unmerged (memory `d021-m5t002-product-resume`). The
  controller's committer identity (Section 3.5) is scoped to control-plane +
  task-branch integration and is structurally incapable of push/deploy because
  the guard and push_policy deny it.
- **Tier D / Section 20 hard stops.** Unchanged and owner-only (CLAUDE.md
  authority section; `d-010` autonomy tiers). The controller never crosses them.

Refusal behavior is uniform: transition to a WAIT/PAUSED park state, emit one
owner touch (`TOUCH_BLOCKING_ASK` / `TOUCH_SYNCHRONOUS_STOP`, `loop.py:779`),
persist the durable ask, and STOP the wave/queue. It never continues past an
un-automatable item and never lowers a gate to make the queue move (D-033-R005
prohibition: nothing here activates automated merging/acceptance/continuation
beyond the switched-on Tier-A scope).

---

## 6. Activation switch (D-033-R003 feed)

### 6.1 Design (default OFF, owner-gated, per-launch, durable)

The switch follows the proven bounded-mode precedent exactly. Today
`--owner-enable-bounded-auto` is a per-launch input; `bounded_mode_gate`
(`start_gate.py:62`) refuses the unattended `limited-auto` mode BY NAME unless
the owner supplied it (`cli.py:1187`), and `LoopConfig.__post_init__`
(`loop.py:314`) raises `LimitedAutoRefused` if a `limited-auto` config is even
CONSTRUCTED without the owner enable. The managed-tier-A capability adds an
analogous switch:

- **Config surface**: a new default-false flag, e.g.
  `owner_enabled_managed_tier_a`, mirrored in the durable flags block the status
  command already prints (`cli.py:1534` shows `limited_auto_enabled: False`).
- **Per-launch flag**: `--owner-enable-managed-tier-a`, honored ONLY at
  `cmd_start`, exactly like `--owner-enable-bounded-auto`. A start without it
  runs today's behavior: the loop stops at COMPLETE, closes to IDLE, and does
  NO gate wave / acceptance / commit / advance.
- **Durable journal record**: enabling writes a durable journal record (as
  `bounded_mode_gate` seals its enable), so `cmd_recovery_status` /
  `cmd_status` disclose it and a crash-resume does not silently re-enable.
- **A refusal gate** parallel to `bounded_mode_gate`: if the managed-tier-A code
  path is reached without the owner enable, it is a structured refusal
  (typed code + message), never a silent no-op.

### 6.2 Switch-off == today's behavior, byte-for-byte

With the switch off, the controller takes the EXACT current path: `COMPLETE` ->
`plan_close_run` -> IDLE, no new stage entered. The proof obligation (D-033-R003
required_harness): a negative/mutation acceptance scenario that runs a full
task to COMPLETE with the switch OFF and asserts (a) no gate record was written
by the controller, (b) no `accept()` was invoked, (c) no commit was made, (d)
the journal/audit event sequence is identical to the pre-change baseline. The
mutation half removes the switch check and asserts the OFF scenario now wrongly
performs a wave - i.e. the switch is load-bearing. This is the same shape as the
existing `_check_loop_modes` guard test that a bounded enable is refused for a
non-owner-gated mode (`cli.py:1186`).

---

## 7. Staged R595 activation outline (D-033-R004 feed, S4)

Presentation only - activation stays owner-only (D-033-R005; R595 pre-activation
prerequisite in `M0-T036-ACTIVATION-CHECKLIST.md`, unchanged). Three stages,
each strictly additive; each stage's switch is a separate owner enable so the
owner can stop at any stage.

### Stage 1 - gate waves only (orchestrator still accepts)

- **Adds**: controller runs the gate wave (Section 2) and records gate records;
  the orchestrator still runs `accept()` and integrates.
- **Entry evidence**: D-033-R003 implementation accepted; the OFF==today proof
  (Section 6.2); the separation mutation suite (Section 4) green; freeze
  baseline re-established.
- **Per-stage safeguards**: reviewer sessions read-only-guarded; G2 stays
  self-check; FAIL routes to worker rework under the revision breaker; BLOCKED
  parks. No acceptance, no commit, no advance by the controller.
- **Rollback**: owner drops the stage-1 enable; the next launch reverts to
  COMPLETE->IDLE. What survives: all gate records already written (they are
  durable ledger state and remain valid inputs for a human accept).
- **Owner command shape**:
  `python -m tools.agent_supervisor start ... --owner-enable-managed-gate-waves`

### Stage 2 - + acceptance on governance-class tasks

- **Adds**: after a green wave, the controller dispatches the independent
  verifier session (Section 3.3) and runs `accept()` for GOVERNANCE-class tasks
  (control-plane / directive-bookkeeping tasks whose blast radius is the ledger),
  still leaving product-code acceptance to the orchestrator.
- **Entry evidence**: Stage 1 run live and clean over N tasks (owner-set N);
  the DCV-row independent-verifier seam accepted with its own producer!=verifier
  negative test; a live dry-run of `accept()` using `_directive_accept_reasons`
  showing every precondition evaluated (memory `in-regime-accept-mechanics`
  dry-run pattern).
- **Safeguards**: the full accept() precondition set (Section 3.2) is
  unmodified; the controller commits control-plane only, citing run-id; the
  breaker/park behavior of Stage 1 carries forward.
- **Rollback**: owner drops the stage-2 enable; the controller reverts to Stage 1
  (waves only). Survives: recorded acceptances (immutable, durable) and the
  verification rows.
- **Owner command shape**:
  `... --owner-enable-managed-gate-waves --owner-enable-managed-acceptance=governance`

### Stage 3 - + queue advance / full Tier-A

- **Adds**: acceptance for all Tier-A task classes plus `next_task`
  queue-advance + successor dispatch, i.e. the full steady-state operator model
  (Section 1.2).
- **Entry evidence**: Stage 2 live and clean over M tasks; the exactly-once
  advancement crash tests (`next_task.py` R388 family) re-run green at the
  frozen candidate; the committer-identity seam (Section 3.5) accepted with its
  push/deploy-impossible negative tests.
- **Safeguards**: Section 5 refusals remain hard; Tier B still routes to the
  named specialist; Tier C/D unchanged; the run budget + all wired breakers
  bound the unattended run exactly as bounded-auto forwarding is bounded today.
- **Rollback**: owner drops the stage-3 enable -> reverts to Stage 2; the
  durable advancement records survive so no task is re-run or lost.
- **Owner command shape**:
  `... --owner-enable-managed-tier-a` (the umbrella enable, implying stages 1-2).

Every stage's activation is a fresh owner-typed launch command; none is
self-activating, and R595/Option-A itself remains the owner-only gate that this
package only PRESENTS.

---

## 8. Failure modes and refusals

Each is fail-closed; none degrades a gate or acceptance.

- **Reviewer session crash / timeout**: treated as UNAVAILABLE, not FAIL - the
  same distinction the loop draws (`loop.py:2045`, an unavailable reviewer is
  not an invalid output). The wave parks with an owner ask ("review unavailable"),
  never records a PASS. `DEFAULT_COMMAND_TIMEOUT_SECONDS = 300.0` bounds a G2
  capture; a timeout is recorded `timed_out=True`, never success
  (`M0-T148-producer-report.md`, S14).
- **Invalid verdict schema**: bounded retry, then `schema_retry_exhausted` ->
  UNAVAILABLE + park; the `consecutive_invalid_outputs` breaker
  (`loop.py:2050`) bounds a livelocking reviewer.
- **Gate-record write conflict**: `project_control.py` writes are atomic
  (serialize -> temp -> `os.replace`, docstring "ATOMIC WRITES", `:123`);
  concurrent writers never corrupt a file, last-writer-wins. The controller
  serializes its own wave (one gate at a time) so no two controller writers race
  a single gate file. A pre-existing gate file is preserved into `history`
  (`project_control.py:1142`).
- **Ledger drift between dispatch and accept** (HEAD moved after review): the
  content-identity stamp catches it - `reviewed_sha` no longer matches, so
  `accept()` fails closed on the stale identity (`directive_registry.py:1004`).
  The controller re-stamps and re-gates rather than accepting stale (item I3).
- **Breaker interactions**: the gate wave ticks the same model-call /
  external-write breakers a review dispatch ticks (`loop.py:2030-2039`); a trip
  parks BEFORE the reviewer is contacted, exactly as content review does.
- **Packet-size limits**: the evidence packet already fails visible at the
  `DEFAULT_PACKET_BYTES` cap -> `STOP_FOR_OWNER` (`M0-T148-producer-report.md`,
  bounds section); the wave inherits that honest backstop - an over-cap packet
  parks rather than sending a truncated review surface.

---

## 9. Implementation plan (D-033-R003, 2-4 tasks; D-033-R007 freeze lane)

Each task cites the specific D-033-R### as AD-093 qualifying evidence in BOTH
the packet and the commit message (`supervisor-freeze.md` section 3), and the
first task also amends `supervisor-freeze.md` section 2 to RECOGNIZE D-033 as
qualifying evidence, mirroring the D-024/M0-T086 recognition already recorded
there (D-033-R007 required_evidence). All tasks run under G0/G2/G3/G5 with the
suite re-baseline (`supervisor-freeze.md` section 4).

- **T-A - Gate-wave engine + switch scaffold (cites D-033-R001, D-033-R003, D-033-R007).**
  Scope: new post-COMPLETE gate-wave stage; per-gate reviewer dispatch wrapper
  over `ephemeral_review`/`claude_runner`; verdict -> `project_control.gate()`
  recorder (item I1, I2); the `--owner-enable-managed-gate-waves` switch +
  refusal gate + durable record; the OFF==today proof; the section-4 mutation
  suite for the reviewer-not-producer and reviewer-read-only invariants; the
  freeze-rule D-033 recognition amendment.
  Allowed paths: `tools/agent_supervisor/` (new module + minimal `loop.py`/`cli.py`
  wiring - NOTE loop.py sits at its modularity ceiling per M0-T148, so the new
  stage MUST be a new module, not loop.py growth), `.claude/rules/supervisor-freeze.md`,
  tests, `project-control/reports/`.
- **T-B - Acceptance engine + independent-verifier seam (cites D-033-R002, D-033-R006).**
  Scope: independent verifier-session dispatch; verification-row transcription
  (worst-of dedup, 64k ceiling) into the task verification file; controller
  `accept()` invocation preserving every precondition; the producer!=verifier and
  self-check-never-satisfies mutation tests; the content-identity re-stamp on
  HEAD drift (item I3). Depends on T-A.
  Allowed paths: `tools/agent_supervisor/`, tests, `project-control/reports/`.
- **T-C - Controller committer identity + queue advance (cites D-033-R002, D-033-R005).**
  Scope: the distinct committer identity scoped to control-plane + task-branch
  integration, citing run-id (item I4); wiring `next_task.record_advancement` +
  successor dispatch; push/deploy-impossible negative tests; Section 5 refusal
  tests. Depends on T-B. This is the most sensitive task (git authority
  extension) and is the natural Stage-3 gate.
  Allowed paths: `tools/agent_supervisor/`, tests, `project-control/reports/`.
- **T-D (optional, only if T-A exceeds a bounded size) - staged activation
  package document (cites D-033-R004).** Scope: the owner-facing
  `project-control/reports/` package doc formalizing Section 7 with the exact
  per-stage owner commands. Presentation only.

### Seams the current code LACKS (must be built, not assumed)

- **I1**: no post-COMPLETE gate-wave stage exists; the loop stops at COMPLETE
  and `next_task.plan_close_run` only closes to IDLE (verified `loop.py:2174`,
  `cli.py:2689`).
- **I2**: no bridge from a reviewer-session verdict to a `project_control.gate()`
  write, and no controller-side check binding the recorded `--reviewer` to the
  reviewer session's actual identity and asserting it differs from the producer
  session identity.
- **I3**: no controller call to `accept()` and no independent-verifier-session
  dispatch / verification-row transcription; `accept()` today is only ever a
  human-invoked CLI.
- **I4**: no controller committer identity; git integration is orchestrator-only
  (ADR-005), so a controller that commits is a new, switch-gated authority
  extension.
- G2 command capture (`evidence.run_command`) exists but is NOT wired to WRITE a
  G2 gate record; that wiring is part of I1.

---

## Acceptance-scenario mapping (S1-S4)

- **S1 (supervisor-run gate waves designed, independence + gate classes
  preserved, G2 never independent)** -> Sections 2, 4.
- **S2 (supervisor-run acceptance designed, every accept() precondition
  preserved, DCV row from an independent verifier, identity stamping,
  committer + advance)** -> Sections 3, 4.
- **S3 (not-automatable set enumerated with exact refusal behavior)** -> Section 5.
- **S4 (owner-gated default-OFF switch + staged R595 activation package with
  per-stage safeguards, rollback, and owner command shapes)** -> Sections 6, 7.

All requirement constraints held: D-033-R005 (no activation; all holds intact) -
Sections 5, 6, 7 present only; D-033-R006 (separation machine-enforced, G6/owner
never automatable) - Sections 4, 5; D-033-R007 (D-033-R### freeze-lane citation
+ recognition amendment) - Section 9; D-033-R008 (no new long-lived-chat
dependence) - Section 1.
