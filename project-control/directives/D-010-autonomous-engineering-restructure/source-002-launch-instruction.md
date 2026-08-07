FRESH PRIMARY ORCHESTRATOR — AUTONOMOUS ENGINEERING V2

You are the only active primary orchestrator.

The binding owner-directive intake file is:

.claude/OWNER_DIRECTIVE_AUTONOMOUS_ENGINEERING_v2.md

KNOWN STARTING STATE

- PR #154 is merged.
- M0-T036 is accepted, merged, and SHADOW-ONLY.
- Remote main merge SHA is:
  cec785f97ac1037df1fb2e1b114260eb106b7de0
- R595 remains a mandatory prerequisite before any activation.
- No separate M0-T019 Claude session is currently running.
- M0-T019, D-009, M2-T014, and their worktrees may contain existing unfinished repository state, but they are not owned by an active peer session.
- The current primary checkout may still be on:
  task/M0-T036-supervisor-bridge
  at 57ccb44.
- docs/SESSION_HANDOFF.md may contain a valid uncommitted post-merge update.
- Other intentional or pre-existing uncommitted files may remain.

Do not trust these statements without independently reconciling repository reality.

PHASE 0 — READ-ONLY RECONCILIATION

Before modifying anything:

1. Read CLAUDE.md completely.
2. Read .claude/OWNER_DIRECTIVE_AUTONOMOUS_ENGINEERING_v2.md completely.
3. Read docs/SESSION_HANDOFF.md completely.
4. Run:
   - python tools/project_control.py status
   - python tools/current_state.py if present
   - git status --short --branch
   - git worktree list
   - git branch --all
   - git log --oneline --decorate -30
   - git fetch --prune if repository policy permits it
5. Inspect:
   - current checkout and branch;
   - local HEAD;
   - origin/main;
   - all worktrees;
   - all uncommitted and untracked files;
   - open pull requests;
   - GitHub CI;
   - active tasks;
   - blockers and gates;
   - pending external effects;
   - running Claude, Codex, Git, test, and writable child processes.

RECONCILE SPECIFICALLY

- PR #154 and main SHA cec785f97ac1037df1fb2e1b114260eb106b7de0;
- M0-T036 accepted/merged/shadow-only state;
- R593 accepted residual;
- R595 mandatory pre-activation rehearsal;
- the uncommitted docs/SESSION_HANDOFF.md update;
- D-009 amendment 1;
- M0-T019;
- M2-T014;
- control/D-009-depsec-and-m0t019-dispatch;
- ctl, t19x, t19, and t14 worktrees;
- the five reviewer-agent model flips;
- backend-engineer agent-memory files;
- all .shm, .npmrc, .bak, prior directive drafts, and other untracked files.

There is no active M0-T019 peer session. Treat all M0-T019-related branches and worktrees as dormant repository state that must be reconciled, not as work currently owned by another running agent.

Do not delete, reset, stash, clean, move, revert, commit, merge, rebase, or switch the current checkout until ownership and purpose are proven.

PRESERVE THE UNCOMMITTED HANDOFF UPDATE

The post-merge SESSION_HANDOFF.md change may be valid but uncommitted.

1. Inspect its exact diff.
2. Do not discard it.
3. Do not mix it into unrelated work.
4. Verify it against the actual merged repository state.
5. Preserve it through a dedicated bounded task and normal PR if it remains accurate.

CLEAN ORCHESTRATION WORKTREE

After reconciliation, establish one clean orchestration worktree based on the verified origin/main SHA.

Do not delete or repurpose existing worktrees.

Keep the original checkout intact until every uncommitted file has been classified and preserved.

DIRECTIVE CAPTURE

Invoke the repository’s directive-compliance workflow.

Capture .claude/OWNER_DIRECTIVE_AUTONOMOUS_ENGINEERING_v2.md as one canonical owner directive.

Use AD-001 through AD-096 as the normative atomic requirements.

Preserve all explanatory sections as binding design intent.

Do not manufacture hundreds of artificial requirements from explanatory prose.

After canonical capture is independently verified:

- make the project-control directive copy authoritative;
- retain the intake file until a dedicated cleanup decision proves it can be removed;
- do not leave two competing authoritative copies.

TASK ARCHITECTURE

Create:

1. one parent initiative;
2. bounded dependency-ordered implementation tasks;
3. exact allowed and forbidden paths;
4. tests and acceptance evidence;
5. rollback points;
6. AD-001 through AD-096 traceability;
7. a clear division between:
   - minimum autonomy work;
   - non-blocking supervisor backlog;
   - NYC product work.

Do not create one enormous task.
Do not create one enormous pull request.
Do not perform a big-bang refactor.
Do not begin general legacy cleanup.

MINIMUM AUTONOMY CEILING

Only the minimum control capabilities identified in the directive may block product work.

R595 must occur before activation, but it must not become an open-ended supervisor-development project.

After minimum autonomy is proven and two real product tasks complete:

- freeze nonessential supervisor expansion;
- enforce the 80/20 product-capacity rule;
- automatically resume the NYC product dependency chain.

CODEX MODE

Codex is ephemeral by default:

fresh read-only process
→ bounded context packet
→ one structured review decision
→ durable record
→ process exits

Do not keep Codex alive as a second giant persistent conversation.

SUBAGENTS

You are the sole primary orchestrator.

Use child agents only when:

- tasks are bounded;
- writing scopes do not overlap;
- each writer has an isolated worktree;
- reviewers are read-only;
- maximum inference-agent concurrency is two;
- maximum nesting depth is one;
- every child is tracked.

If internal child agents are unavailable, execute sequentially.

Do not ask the owner to coordinate independent writer terminals.

EXECUTION

After reconciliation and canonical directive capture, begin the first dependency-valid bounded task automatically.

Do not stop for routine approval of planning, task splitting, branches, worktrees, ordinary code, tests, commits, task-branch pushes, pull requests, corrections, CI reruns, or continuation.

Stop only for a genuine Section 20 hard-stop condition.

Before any session rotation:

- freeze dispatch;
- finish the current bounded unit;
- collect and close all children;
- verify no writable process remains;
- reconcile Git and external effects;
- update project control and SESSION_HANDOFF;
- create a digest-verified handoff;
- confirm active_children is empty;
- then stop.

Proceed now with read-only reconciliation.
Then preserve the post-merge handoff update.
Then establish the clean orchestration worktree.
Then capture the directive canonically.
Then create the bounded task structure.
Then begin the first dependency-valid implementation task automatically.
