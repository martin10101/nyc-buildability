# NYC BUILDABILITY — AUTONOMY-ACTIVATION HANDOFF (2026-08-19)

EXTERNAL FILE — lives OUTSIDE every Git checkout, per the established
owner-instructed handoff pattern (predecessor:
`NYC_BUILDABILITY_D019_NEXT_SESSION_HANDOFF_2026-08-19.md`).

Written by the outgoing orchestrator session that executed Section 1
(live reconciliation) and Section 2 (conditional PR #240 merge) of the
owner's MASTER HANDOFF / AUTONOMY-READINESS directive, reproduced VERBATIM
in Part D below. This is the canonical control-plane handoff required by
Section 2 of that directive.

A brand-new Claude Code session, started at the repository worktree root,
must be able to continue from this file alone.

---

## PART A — COMPLETED IN THE OUTGOING SESSION (2026-08-19, all verified live)

### A.1 Section 1 reconciliation — every checkpoint fact verified

| Claimed (abbreviated) | Verified live (complete) |
|---|---|
| origin/main `31c50a09…` | `31c50a09bd1671d111f21923c6a2d739f51187dd` (pre-merge) |
| Main accepted count 99 | 99 (`project-control/state.json` at 31c50a09); M0-T076 present, M0-T077 absent |
| D-019/M0-T076 merged+closed | M0-T076 in main's accepted ledger; D-019 directory in registry |
| PR #240 OPEN, accepted, unmerged | OPEN, not draft, MERGEABLE, mergeStateStatus CLEAN at check time |
| PR branch accepted count 100 | 100 (`state.json` at PR head); M0-T077 present |
| Content manifest `f103af3e…` | `f103af3ef1433e58a0352bab74618eb2ef6da1f457e66a6e3310a999d9c3439f` |
| Final reviewed SHA `59556584…` | `59556584499de6618b06ec5819b9bb1170fdbb37` |
| Acceptance commit `9aca2e1…` | `9aca2e1f2d6302ef700faf83342a5386a8f0f303` (== PR head, branch tip) |
| 40/40 green checks | 40/40 pass at PR head (20 contexts × 2 event runs) |
| D-013-R060 PENDING | `status: "pending"` in D-013 requirements.json (untouched) |
| Controller bundle not run | Runbook present, unexecuted: `CONTROLLER_UPDATE_RUNBOOK_2026-08-18.md` |
| Controller untouched | `C:\Program Files\SupervisorConfig\config.toml` sha256 `6AEF12A9F60A6A64D7AF77DE3C071289C35DFE60977239E901DF8D642C3FFFDE`; `C:\SupervisorController\model_selection.toml` sha256 `0E2432C0A25632CCB7EF35392C64DC70BD95FAC16F2E136E54801E2407A66CF4` — both byte-identical to the recorded protected state |
| limited-auto disabled | Unchanged (protected config byte-identical; no activation performed) |
| Directive registry | D-001 … D-020 present; next identifier expected D-021 (RESOLVE FROM LIVE REGISTRY at capture; do not assume) |

Identity binding verified across ALL records: gates M0-T077-G3/G4/G5
(PASS), submission report `project-control/reports/M0-T077.json`, and the
D-020 `verification.json` (verifier `directive-compliance-verifier` ≠
producer `orchestrator`; 34/34 requirements PASS) all bind reviewed SHA
`59556584499de6618b06ec5819b9bb1170fdbb37` and content manifest
`f103af3ef1433e58a0352bab74618eb2ef6da1f457e66a6e3310a999d9c3439f`.

Fresh recomputation at the PR head (`_task_git_identity` /
`frozen_git_identity`, run read-only in clean wt-m0t077 at 9aca2e1):
identity `f103af3ef1433e58a0352bab74618eb2ef6da1f457e66a6e3310a999d9c3439f`
— EXACT MATCH. The post-review delta `59556584..9aca2e1` touches ONLY
`project-control/**` lifecycle records (verification.json, gate records,
report, state.json, task record) — no unreviewed content after acceptance;
reviewed code equals merged code.

### A.2 Section 2 — PR #240 MERGED (all nine owner conditions passed first)

- Merge executed 2026-08-20T00:27Z via `gh pr merge 240 --merge
  --delete-branch` — normal protected-main procedure, NO `--admin`, no
  protection bypass, no history rewrite.
- **New origin/main = merge commit `d8b3899f61efa6620e18a26541ced96020f5bef9`**
  ("Merge pull request #240 from martin10101/task/M0-T077-mcp-default-deny").
- Ancestry proven: `9aca2e1f…` and `59556584…` are both ancestors of the
  new origin/main (`git merge-base --is-ancestor` TRUE for both).
- Main ledger at d8b3899: **100 accepted tasks, M0-T077 present**.
- Remote branch `task/M0-T077-mcp-default-deny` deleted (empty
  `ls-remote --heads` result). Local worktree `wt-m0t077` PRESERVED intact
  at 9aca2e1 (project norm: old task worktrees are retained; nothing
  uncommitted inside it).
- Post-merge CI at d8b3899: ALL workflows completed SUCCESS
  (CI, secret-scan, context-budget).
- `wt-m0t064` (main worktree) fast-forwarded 31c50a09 → d8b3899, clean.
- MCP policy validator run live at merged main: exit 0
  ("MCP default-deny policy intact: claude.ai connectors disabled, empty
  allowlist, audited identifiers denied, .mcp.json servers rejected,
  auto-approval off, pre-existing settings preserved.")

### A.3 What was NOT done (deliberately — directive boundaries honored)

- NO directive capture yet (D-021 capture belongs to the fresh MCP-clean
  session — Section 3 of the directive).
- NO controller code, protected config, or `tools/agent_supervisor/**`
  change of any kind.
- NO D-013-R060 promotion (remains `pending`).
- NO controller-update bundle execution.
- NO NYC application/product work.
- NO global connector or account configuration change.

---

## PART B — DEVIATIONS AND HONEST NOTES

1. **"Working trees are clean" condition — two session-artifact deviations
   in NON-merge-relevant checkouts, both left untouched:**
   - Primary checkout `nyc-development-feasibility-claude-pack` (on old
     control branch `control/session14-m0t055-accept`): uncommitted
     +1-line edit to `.claude/agent-memory/backend-engineer/MEMORY.md`
     plus one untracked agent-memory note
     (`interrupt-resets-shell-to-primary.md`). Claude Code subagent-memory
     auto-writes; no relation to PR #240 content.
   - `ctl` worktree: uncommitted edit to
     `project-control/reports/BATCH-RESUME-2026-08-05.md`, stale since
     ~2026-08-05; it predates the M0-T076 and M0-T077 reconciliations that
     recorded "no discrepancy".
   Both merge-relevant trees (wt-m0t064 = main, wt-m0t077 = PR branch) were
   verified CLEAN; the merge itself was server-side between two verified
   immutable SHAs, so neither artifact could influence merged content. This
   interpretation follows the project's own recorded reconciliation
   convention. The owner may direct cleanup or preservation of these two
   artifacts; nothing was deleted.
2. **Outgoing session was NOT MCP-clean** (started at `C:\Users\MLFLL`,
   ambient claude.ai connectors present) — exactly the condition Section 2
   anticipates. Therefore protected activation work STOPPED after the merge
   and post-merge verification; no D-021 capture and no controller work was
   attempted in this session. Ambient connectors were used for NOTHING
   (no Airtable/Supabase/M365/pencil tool was ever invoked).
3. **Permission-classifier denials mid-session**: several read-only
   `gh`/pipe commands were intermittently denied by the local Claude Code
   permission classifier after the merge; every verification was completed
   through alternate read-only routes (plain `git`, file extraction to
   scratchpad, `gh run list` via bash). No denial was bypassed maliciously;
   no state-changing command was denied.
4. The pre-existing external handoff
   `NYC_BUILDABILITY_D019_NEXT_SESSION_HANDOFF_2026-08-19.md` describes the
   OLDER 98-task/pre-D-019 checkpoint. THIS file supersedes it for
   orientation; the ledger always wins on any conflict.

---

## PART C — NEXT-SESSION STARTUP (fresh, MCP-clean, root-started)

The owner starts the fresh session with ONE command (PowerShell):

```powershell
cd C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t064; claude
```

First message to paste into that session:

> Read C:\Users\MLFLL\Downloads\nyc-zoning\NYC_BUILDABILITY_AUTONOMY_ACTIVATION_HANDOFF_2026-08-19.md
> in full. Prove this session's MCP roster is empty and record the proof.
> Then continue the embedded owner directive (Part D) from Section 3:
> capture it verbatim as the next directive resolved from the live registry
> (expected D-021), decompose, and proceed under its boundaries.

Fresh-session obligations, in order:

1. Re-reconcile live, read-only: `git fetch origin && git status --short &&
   git rev-parse HEAD origin/main` (expect clean, both =
   `d8b3899f61efa6620e18a26541ced96020f5bef9` or a newer sha — if newer,
   read intervening merges first); `python tools/project_control.py status`
   (expect 100 accepted). TRUST THE REPOSITORY over this file.
2. **Prove the MCP roster is empty** (D-020 policy now merged; the session
   was started at the worktree root so project settings apply). Record the
   proof per the M0-T077 fresh-session-proof pattern
   (`project-control/reports/M0-T077-fresh-session-proof.md`). If ANY MCP
   server/tool is present, STOP protected work and report.
3. Capture the Part D directive verbatim under `project-control/directives/`
   via `/directive-compliance`; resolve the identifier from the live
   registry (expected D-021); decompose into atomic requirements; create
   the minimum sequential bounded tasks (one branch + one PR each; freeze
   allowed paths + G0 baseline before each implementation).
4. Then proceed with directive Sections 4–16 under ALL of its boundaries
   (Section 12 prohibitions; owner-present consolidation per Section 13;
   proofs P1–P20 per Section 14; conditional R060 decision per Section 15 —
   R060 stays PENDING until every condition is independently proven).
5. Owner-presence items must be CONSOLIDATED into one checkpoint
   (Section 13) — reconcile `CONTROLLER_UPDATE_RUNBOOK_2026-08-18.md`
   against live state before presenting it.

Key paths:

- Repo root worktree (main): `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t064`
- Primary checkout (on an old control branch; has the two Part B artifacts):
  `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack`
- Merged task worktree (preserved): `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t077`
- Controller runbook: `C:\Users\MLFLL\Downloads\nyc-zoning\CONTROLLER_UPDATE_RUNBOOK_2026-08-18.md`
- Protected live configs (owner-present only):
  `C:\Program Files\SupervisorConfig\config.toml` (sha256 6AEF12A9…FFDE),
  `C:\SupervisorController\model_selection.toml` (sha256 0E2432C0…6CF4)

---

## PART D — THE COMPLETE OWNER DIRECTIVE (VERBATIM)

Captured exactly as received by the outgoing session on 2026-08-19. The
message ended with the trailing fragment `"C:\Users\MLFLL\Downloads\nyc-zoning"`
after the final sentence; it is preserved below.

```
MASTER HANDOFF, OWNER DIRECTIVE, AND CONDITIONAL ACTIVATION AUTHORIZATION
NYC BUILDABILITY — CODEX-LED AUTONOMOUS ENGINEERING READINESS

Read this entire instruction before acting.

This is ONE cohesive owner instruction. It may require several sequential,
bounded control-plane tasks, but it must not be treated as one uncontrolled
mega-task.

Your objective is to take the existing system from its current checkpoint
to AUTONOMY_READY: Codex operating as the lead supervisor, Claude Code
operating as bounded producer/reviewer/verifier workers, automatic context
packet consumption proven live, model routing and controlled turnover
proven, Remote Control proven, and safe continuous operation ready to begin
only when the owner later gives the explicit START command.

Do not begin NYC product implementation during this activation directive.

============================================================
1. RECONCILE THE LIVE CHECKPOINT
============================================================

Treat every identity below as a dated checkpoint. Verify all facts against
the live repository, origin/main, GitHub, task ledger, directive registry,
CI, installed controller, and recorded manifests before acting.

Reported starting state:

- Repository: github.com/martin10101/nyc-buildability
- origin/main:
  31c50a09bd1671d111f21923c6a2d739f51187dd
- Main accepted-task count: 99
- D-019/M0-T076: merged and closed
- PR #240: OPEN, independently accepted, unmerged
- D-020/M0-T077: program-wide MCP default-deny
- PR #240 branch accepted-task count: 100
- Final reviewed M0-T077 content manifest begins:
  f103af3e
- Final reviewed SHA begins:
  59556584
- Acceptance commit begins:
  9aca2e1
- PR #240 reportedly has 40/40 green checks
- D-013-R060: PENDING
- Controller-update bundle: not run
- Automatic context-packet consumption: not enabled
- limited-auto: disabled
- No NYC application implementation is authorized by this directive

Resolve all abbreviated identities to their complete values from the
committed records. Do not rely on the abbreviations as merge identities.

If the live state materially disagrees, STOP and report the discrepancy
without correcting or merging anything.

============================================================
2. CONDITIONAL AUTHORIZATION TO MERGE PR #240
============================================================

I explicitly authorize merging PR #240 only if a fresh read-only check
proves all of the following:

- current PR head is exactly the accepted head recorded by M0-T077;
- the complete content-manifest digest matches every final review,
  submission, gate, and verification record;
- all required CI contexts are green at that exact head;
- the PR is mergeable and clean;
- working trees are clean;
- no unreviewed content appeared after acceptance;
- no global connector or account configuration was changed;
- D-013-R060 remains pending;
- the controller and limited-auto remain untouched.

If every condition passes:

1. Merge through the normal protected-main procedure.
2. Do not bypass protection or rewrite history.
3. Delete/prune the task branch normally.
4. Verify the reviewed head is contained in main.
5. Verify main now contains 100 accepted tasks.
6. Verify post-merge CI is green.
7. Record the final merge and main identities.

If any condition fails, stop.

Because project MCP settings take effect reliably in a fresh process, do
not claim that the session which performed the merge has become MCP-clean.
After merging, perform a controlled handoff to a fresh Claude Code process
started at the repository worktree root. Preserve this complete directive,
the reconciled state, and all identities in the canonical control-plane
handoff.

The fresh process must prove that its MCP roster is empty before protected
activation work continues.

If a safe automatic turnover is not yet available at this bootstrap point,
pause once and give the owner one exact restart/resume command. Do not
continue sensitive controller work inside an ambient-MCP parent session.

============================================================
3. CAPTURE THIS OWNER DIRECTIVE
============================================================

After PR #240 is merged and a fresh root-started session proves the MCP
policy:

- Capture this instruction verbatim as the next valid directive.
- The expected identifier may be D-021, but resolve it from the live
  registry rather than assuming it.
- Decompose it into atomic, independently verifiable requirements.
- Create only the minimum number of sequential bounded tasks necessary.
- Resolve all task identifiers from the live ledger.
- Use one branch and one PR per implementation task.
- Freeze allowed paths and the G0 baseline before each implementation.
- Do not create separate tasks merely to inflate process ceremony.
- Do not combine unrelated controller, runtime, and product changes.

This directive provides conditional merge authorization for readiness tasks
created solely under this directive, but only when:

- producer, reviewer, and directive verifier are independent;
- every applicable requirement passes;
- every blocking review finding is corrected and re-reviewed;
- reviewed code equals merge code;
- all required CI is green;
- forbidden-path changes are empty;
- rollback evidence exists;
- no owner-presence requirement remains outstanding.

If the repository safety mechanism still requires a fresh owner decision,
do not bypass it. Return the exact blocking identity and requested action.

============================================================
4. DEFINITION OF AUTONOMY_READY
============================================================

AUTONOMY_READY means all of the following are proven live:

1. Codex is the lead supervisor.

2. Claude Code workers are launched and controlled by the supervisor for
   bounded producer, reviewer, QA, security, and verification roles.

3. Before any worker starts, the actual context orchestrator prepares a
   sufficient, digest-bound packet containing the exact task requirements,
   relevant code, tests, graph neighborhood, subsystem placement, and
   advisory memory.

4. The worker actually receives and acknowledges that exact packet. Merely
   generating it on disk is not sufficient.

5. Missing or insufficient context prevents the worker from starting.

6. Worker sessions start at a repository worktree root and have zero
   external MCP servers unless a future owner-authorized task explicitly
   grants one.

7. Independent workers use isolated worktrees. Concurrent writers never
   work in the same checkout or on overlapping files.

8. Model selection is based on task evidence, role, complexity, risk, and
   the models actually available to the owner's current accounts.

9. Requested model, resolved model, effort level, fallback event, and
   reason are recorded for every agent.

10. Context exhaustion, model unavailability, provider limits, process
    failure, and machine restart produce a safe checkpoint and controlled
    resume rather than lost or duplicated work.

11. Remote Control exposes the operator session and its managed Claude
    sessions on the owner's phone.

12. The owner has simple PowerShell commands for START, STATUS, STOP,
    RESUME, and EMERGENCY STOP.

13. A bounded run automatically stops at its declared duration, task count,
    safety boundary, or budget boundary.

14. The system remains idle after setup until the owner gives the explicit
    START command.

============================================================
5. LIVE CAPABILITY AND VERSION AUDIT
============================================================

Before modifying controller code, audit and record:

- Windows and PowerShell versions;
- Git and Python versions;
- installed Claude Code executable, version, authentication mode, and
  executable identity;
- installed Codex executable, version, authentication mode, and executable
  identity;
- official supported Claude Remote Control server flags;
- background-session and agent-view support;
- worktree-spawn support;
- resume/respawn support;
- current Claude models actually available to this account;
- current Codex models actually available to this account;
- current model-selection and fallback configuration;
- existing supervisor/controller start, stop, resume, watchdog, and
  turnover behavior;
- exact D-013-R060 wording and acceptance conditions;
- exact controller-update runbook;
- current protected-file/configuration hashes;
- current auto/limited-auto state;
- Windows startup/restart behavior;
- current Remote Control persistence behavior.

Use current official Anthropic and OpenAI documentation as primary sources.
Do not invent model names or rely on stale model assumptions.

Do not silently upgrade Claude Code, Codex, Python, or another machine-wide
tool. If a required capability is unavailable only because the installed
stable version is too old, consolidate that into the single owner-present
checkpoint with the exact upgrade, impact, rollback, and verification.

============================================================
6. PRESERVE AND EXTEND THE EXISTING ARCHITECTURE
============================================================

This is integration and activation, not a rebuild.

Reuse:

- the existing Codex/Claude supervisor;
- task/directive lifecycle;
- context orchestrator;
- context compiler;
- repository index and graph;
- memory graph;
- model-routing evidence;
- turnover adapters;
- manifests;
- gate system;
- status projection;
- controller doctor;
- existing A1 rehearsal;
- existing controller-update runbook.

Do not replace working components with a new framework merely because
Claude Code now offers background sessions, agent teams, workflows, or
Remote Control server mode.

Use native capabilities where they remove custom complexity, but keep Codex
as the lead supervisor and preserve the repository's deterministic
control-plane evidence.

Native Claude cross-session messaging must not be a required Windows
dependency. Use the existing ledger, files, manifests, packet digests, and
controller state as the durable communication channel.

============================================================
7. AUTOMATIC CONTEXT-PACKET CONSUMPTION
============================================================

Close the currently admitted integration gap.

For every supervised task:

1. Resolve the accepted/frozen task contract and applicable directives.
2. Run the canonical context-orchestration entry point.
3. Require a sufficient result.
4. Bind the packet digest, task identity, G0 base, working head, and model
   signals into the worker launch record.
5. Deliver the exact packet to the worker.
6. Require the worker to acknowledge task id and packet digest.
7. Record evidence that the worker used the packet.
8. Refuse launch on stale, insufficient, mismatched, or ungrounded packets.
9. Regenerate only when an input affecting the packet changed.
10. Never fall back silently to a generic handoff prompt.

If this requires changes to tools/agent_supervisor/** or protected
controller code, this directive explicitly authorizes the minimum necessary
delta, subject to frozen scope, independent security review, rollback, and
live verification.

Do not weaken any existing supervision, termination, or digest-binding
control.

============================================================
8. MODEL ROUTING AND FALLBACK
============================================================

Implement or complete a deterministic model policy using only models proven
available live.

At minimum, distinguish:

- inexpensive read-only discovery/indexing;
- routine bounded implementation;
- complex architecture or concurrency work;
- security review;
- legal/numeric critical review;
- directive-compliance verification.

Do not route a critical independent reviewer to a weaker model solely to
save tokens.

Handle two different situations honestly:

A. Native supported fallback:
Use supported Claude fallback configuration only for failure classes it
actually handles.

B. Limits that native fallback does not handle:
Rate limits, plan/credit limits, billing failures, authentication failures,
request-size failures, and transport failures must not be falsely reported
as native fallback successes.

For a recoverable limit:

1. Stop the affected worker safely.
2. Preserve committed and uncommitted state without loss.
3. Produce a compact, evidence-grounded handoff.
4. Select another owner-allowed model only if policy permits it.
5. Start a new isolated worker session.
6. Re-bind the task and context-packet identities.
7. Resume from the recorded checkpoint.
8. Record requested model, actual model, and turnover reason.

Never circumvent account limits.
Never retry forever.
Use bounded retries with backoff.
If no allowed model can continue safely, pause the run and notify the owner.

Any change to protected model-selection configuration is authorized only
when proven necessary for these outcomes. Freeze and review the exact
before/after configuration and preserve immediate rollback.

============================================================
9. REMOTE CONTROL AND SESSION SPAWNING
============================================================

Prefer Claude Code's supported Remote Control server mode with isolated
worktree spawning when the installed version supports it.

Requirements:

- start from the repository root;
- use worktree isolation for on-demand worker sessions;
- set a conservative capacity appropriate for this machine;
- begin with no more than two simultaneous writing workers;
- assign clear, unique session names;
- make operator and worker status visible remotely;
- ensure every spawned worktree contains the merged MCP policy;
- prevent same-directory concurrent writers;
- record session ids, worktrees, tasks, and models;
- clean up completed disposable worktrees safely;
- preserve unfinished worktrees after a crash;
- never delete a worktree containing uncommitted or unpreserved work.

The result need not open a separate visible PowerShell window for every
worker. Managed background or on-demand sessions are acceptable and
preferred when they are visible and controllable from the phone.

Prove, with the owner present once, that:

- the operator session appears on the phone;
- at least one on-demand isolated worker appears;
- the owner can inspect status;
- the owner can send a message;
- the owner can request a new bounded session;
- that new session starts at the correct worktree root;
- its MCP roster is empty.

============================================================
10. CONTINUOUS-RUN OPERATIONS
============================================================

Provide simple, real PowerShell operator commands for:

- START;
- STATUS;
- STOP AFTER CURRENT SAFE POINT;
- RESUME;
- EMERGENCY STOP;
- VIEW LAST HANDOFF;
- VIEW ACTIVE TASKS;
- VIEW MODEL AND TOKEN/USAGE RECORDS.

The START command must require a bounded run envelope containing:

- owner-approved task queue or directive scope;
- maximum run duration;
- maximum task count;
- maximum concurrent workers;
- merge policy;
- external-write policy;
- production-deployment policy.

Safe defaults:

- maximum two writing workers;
- no production deployment;
- no external MCP;
- no Supabase/Airtable/Microsoft 365 writes;
- no controller self-modification during a product run;
- no branch-protection changes;
- owner-gated merge unless the START command explicitly selects a
  separately authorized verified-auto merge policy.

A verified-auto merge policy may merge only tasks already inside the
owner-approved run scope and only after:

- exact reviewed-head identity match;
- independent review PASS;
- independent directive verification PASS;
- every required CI context green;
- no unresolved or unverified requirement;
- no protected or forbidden path outside the task contract;
- no security or secret finding;
- no material legal/numeric uncertainty;
- clean rollback evidence.

The run must stop rather than guess when owner intent is ambiguous.

The supervisor must stop accepting new tasks shortly before the duration
expires, allow active workers to reach a safe checkpoint, preserve state,
and return a consolidated report.

============================================================
11. PERSISTENCE AND RECOVERY
============================================================

Make the operator/control process durable for multi-hour use on Windows.

Requirements:

- persistent supervisor state;
- bounded crash restart with backoff;
- no endless crash loop;
- safe resume after terminal closure;
- safe resume after reboot/login;
- no plaintext credential creation;
- no automatic product work merely because Windows restarted;
- controller may return to READY/IDLE state, but requires an active owner
  run envelope before doing engineering work;
- Remote Control restart/reconnect behavior documented and tested;
- active run keeps the computer awake using the smallest reversible
  mechanism and restores the prior state when stopped;
- logs rotate and remain bounded;
- stale sessions/worktrees are detected without deleting recoverable work.

If Windows Task Scheduler or another machine-level mechanism is necessary,
prepare it through the owner-present controller-update procedure with an
exact backup, installation record, uninstall command, and verification.

============================================================
12. SAFETY BOUNDARIES
============================================================

This directive does not authorize:

- NYC application feature development;
- production deployment;
- writes to production Supabase;
- Airtable or Microsoft 365 access;
- enabling arbitrary MCP servers;
- deletion of owner data;
- destructive Git operations;
- history rewriting;
- branch-protection weakening;
- security-policy weakening;
- secret disclosure;
- uncontrolled recursive agent spawning;
- unlimited concurrency;
- unlimited duration;
- unlimited spending;
- self-created product requirements;
- silent changes to machine-wide developer tools.

The supervisor may work only from an owner-approved task queue.

Sub-agents are encouraged for bounded discovery, implementation analysis,
adversarial review, QA, security review, and requirement verification.
Never permit overlapping writers. Producer, reviewer, and verifier must be
genuinely independent.

============================================================
13. OWNER-PRESENT CONTROLLER UPDATE
============================================================

Use the prepared controller-update bundle:

C:/Users/MLFLL/Downloads/nyc-zoning/CONTROLLER_UPDATE_RUNBOOK_2026-08-18.md

Reconcile it against the live repository and all changes made by this
directive.

Consolidate all actions requiring UAC, login, Remote Control phone
confirmation, or other physical owner presence into one checkpoint.

At that checkpoint, show:

- exact actions;
- exact files/install locations;
- before hashes;
- backup location;
- rollback command;
- expected prompts;
- estimated interruption;
- what the owner must click or confirm.

Then, with the owner present:

1. Stop the supervisor.
2. Back up the controller and configuration.
3. Install only independently reviewed deltas.
4. Bind installed files to reviewed manifests.
5. Run controller verification and doctor.
6. Run the live Claude executable probe.
7. Verify the Codex executable.
8. Verify the root-started MCP roster is empty.
9. Start the digest-bound supervised rehearsal.
10. Test rollback without destroying the successful installation.
11. Verify Remote Control from the owner's phone.

Do not claim completion from repository tests alone.

============================================================
14. REQUIRED LIVE PROOFS
============================================================

Complete all of these before AUTONOMY_READY:

P1. Fresh root-started Claude worker has zero MCP servers.

P2. Supervisor automatically creates a sufficient context packet.

P3. Worker receives and acknowledges the exact packet digest.

P4. Packet contains exact requirements, relevant source, tests, graph
    evidence, and applicable advisory memory.

P5. Stale or insufficient packet prevents launch.

P6. Codex selects and records the intended worker role and model.

P7. Actual resolved model equals an allowed model and is recorded.

P8. A simulated supported model failure follows the configured fallback.

P9. A simulated quota/rate-limit condition checkpoints and turns over
    safely without falsely claiming native fallback.

P10. A fresh worker resumes from the handoff without losing task state.

P11. Producer, reviewer, and verifier remain separate identities.

P12. An isolated worktree worker is visible through Remote Control.

P13. STOP reaches a safe checkpoint and prevents new work.

P14. RESUME continues exactly once without duplicating completed work.

P15. EMERGENCY STOP terminates supervised workers and preserves evidence.

P16. Controller restart returns to READY/IDLE without beginning work.

P17. Required logs, status, packet digests, model decisions, and task
     identities survive restart.

P18. Existing full CI and controller test suites pass.

P19. Rollback procedure is executable and independently checked.

P20. A bounded endurance rehearsal completes at least two meaningful
     lifecycle transitions without creating artificial work merely to keep
     the system busy.

Measure available token, time, context, model, retry, and packet-size data
during the rehearsal. If provider token data is unavailable, continue to
state UNMEASURED rather than estimating it.

============================================================
15. CONDITIONAL D-013-R060 OWNER DECISION
============================================================

This prompt records the following conditional owner decision:

I authorize D-013-R060 promotion only if:

- its exact original acceptance language is satisfied;
- PR #240 is merged and verified;
- all P1-P20 proofs above pass;
- automatic packet consumption is proven live;
- the controller installation matches reviewed manifests;
- rollback is verified;
- MCP default-deny is proven in the live worker;
- no blocking reviewer or verifier finding remains;
- no material claim is unmeasured but represented as measured.

If every condition is independently proven, record and activate R060
through the normal governed procedure.

If any condition fails or remains unverified, R060 must remain PENDING.
Do not interpret this conditional authorization as permission to waive a
proof.

R060 promotion does not itself authorize unlimited-auto, production
deployment, or an actual NYC product run.

============================================================
16. FINAL READY STATE
============================================================

After all readiness tasks and live proofs pass:

- merge only the reviewed readiness changes authorized above;
- verify main is clean, synchronized, and green;
- verify the accepted ledger;
- verify installed-controller manifests;
- leave the supervisor in READY/IDLE;
- leave continuous product work stopped;
- leave no stray writer process;
- preserve the Remote Control operator entry point;
- return the exact one-line PowerShell START command;
- return STATUS, STOP, RESUME, and EMERGENCY STOP commands;
- explain the default run envelope in plain English;
- state exactly what the owner will see on the phone;
- identify any limitation that cannot be eliminated.

Finish with exactly one of:

AUTONOMY_READY_FOR_OWNER_START

or

AUTONOMY_NOT_READY

If not ready, list only genuine blocking failures. Do not create another
general context-improvement program in response. Propose the smallest
targeted correction for each blocker and stop.

Do not begin the NYC R5 pilot until the owner gives the separate START
instruction after AUTONOMY_READY_FOR_OWNER_START."C:\Users\MLFLL\Downloads\nyc-zoning"
```

— End of handoff —
