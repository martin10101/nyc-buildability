---
name: session-handoff
description: Safely lands the active main Claude Code session, updates the canonical living handoff, and prints the exact successor-session prompt.
argument-hint: "[reason]"
disable-model-invocation: true
---

# /session-handoff — land the main session and hand off safely

Owner-only operator utility (D-025). It runs **inline in this main conversation** — you are the
active session; use your live knowledge of the current task, plan, sub-agents, decisions, and tool
state together with durable repository evidence. Never delegate this procedure to a sub-agent, a
fork, or a background task. There is **one** handoff system: the `project-control/` ledger, git,
the supervisor's durable machinery, and the canonical `docs/SESSION_HANDOFF.md`. Do not invent a
second one.

`$ARGUMENTS` is the optional turnover reason — record it verbatim in the handoff header. If
`$ARGUMENTS` is exactly `dry-run`, follow **DRY-RUN** below instead of the real sequence.

## DRY-RUN (`/session-handoff dry-run`)

Strictly read-only: run only inspection commands (`git status`, `git rev-parse`, ledger reads,
`python tools/project_control.py status`). Do **not** edit any file, commit, push, stop or message
any agent, or change ledger state. Print a preview: the identity block (root/worktree/branch/HEAD),
active task/campaign/lease, active sub-agents and what would happen to each, pending external
effects, what the real run would commit, the SESSION_HANDOFF sections it would write, and whether
the real run would print `HANDOFF READY` or `HANDOFF BLOCKED` (with reasons). End the preview with
`DRY-RUN ONLY — nothing was changed.`

## A. LAND THE CURRENT SESSION

1. Immediately stop starting new work and stop assigning new sub-agents. Do not begin another
   implementation unit for the rest of this procedure.
2. Identify and record exactly: repository root (`git rev-parse --show-toplevel`), worktree
   (`git worktree list`), branch, HEAD SHA, the active directive/campaign, the claimed task(s) and
   current lease (ledger task files + `python tools/project_control.py status`). If a supervisor
   campaign is active, also read `python -m tools.agent_supervisor status` and, when a verified
   handoff exists, `python -m tools.agent_supervisor export-handoff`.
3. Inspect every active or recently completed sub-agent. A **healthy, productive** agent finishes
   its already-bounded assignment and returns its result — do not kill it merely because turnover
   was requested; wait for its natural completion or safe checkpoint. Only an unresponsive or
   unsafe agent may be stopped, and that stop must be recorded in the handoff.
4. Collect and reconcile every returned sub-agent result into durable state (ledger, reports,
   files) — not just this conversation.
5. Enumerate everything in flight: unfinished tests, running commands, pending permission prompts,
   uncommitted changes, unpushed commits, open PRs awaiting action, pending approvals, and any
   external effect whose outcome is unconfirmed. Anything ambiguous must be resolved or explicitly
   journaled as ambiguous-for-reconciliation. While any important result or external action is
   ambiguous, the handoff is **not** ready.

## B. SAVE THE ACTUAL WORK

1. Update the authoritative ledger records (`tools/project_control.py` lifecycle, task files,
   reports) to reflect **only work that actually completed** — never round up.
2. Run the minimum validation that establishes the present state: the test/check commands relevant
   to what changed this session (e.g. `python tools/validate_directive_compliance.py --check` when
   control-plane files changed — note it takes minutes; targeted test files for touched code).
   Record exact commands and outcomes.
3. If the checkpoint is valid and existing policy authorizes it (Tier A ordinary work under ADR-006
   / D-010), commit and push it under the normal commit rules. **Never force-commit broken or
   unverified work.** If changes must stay uncommitted, leave them in place untouched and record
   each file and why it is uncommitted in the handoff.

## C. REPLACE THE LIVING HANDOFF

**Replace** the contents of `docs/SESSION_HANDOFF.md` (current-only convention — history lives in
git; the `context-budget` CI check fails above ~4000 tokens, so be complete but terse). Keep the
standard authoritative-state preamble at the top, then write:

1. Generation time (UTC) + session identifier + turnover reason (`$ARGUMENTS`).
2. Exact repository root, worktree, branch, HEAD SHA.
3. Clean/dirty git status with **every** changed/untracked file.
4. Active directive(s), campaign, task(s), applicable requirements, dependencies, lease holder.
5. The original objective of the current task.
6. Work completed, each item with durable evidence (commit SHA, report path, test output).
7. Work attempted but not completed.
8. Decisions made and why.
9. Rejected approaches and failed attempts (so the successor does not repeat them).
10. Files and important code areas changed.
11. Tests/validation commands run with exact outcomes.
12. Each sub-agent: status, assignment, result, and resume-or-replace recommendation
    (never recommend resuming a TaskStop-killed producer).
13. Outstanding blockers, uncertainties, pending permissions/approvals, external effects.
14. Standing owner restrictions still in force (e.g. never merge PR #241; owner-gated activation;
    active holds).
15. The smallest list of authoritative files the successor must read.
16. The exact next bounded action.
17. Conditions that would require the successor to stop or change the plan.
18. A ready-to-copy successor-session prompt (see F).

Exclude secrets, credentials, tokens, enormous logs, and the conversation transcript.

## D. VALIDATE THE HANDOFF

Before declaring success: re-read the finished file; compare its identity block against live git;
compare its task state against the ledger (the ledger wins); confirm every sub-agent and pending
action is accounted for; confirm the next action follows logically from the completed work; confirm
no important state exists only in this conversation.

If anything important is unsafe or uncertain, print exactly:

    HANDOFF BLOCKED

then explain precisely what must be resolved. Do **not** tell the owner to clear the session — the
point of blocking is that this session still holds state that must be landed first.

## E. If everything is reconciled, print exactly:

    HANDOFF READY

followed by:

1. the exact handoff path (`docs/SESSION_HANDOFF.md`);
2. the saved commit SHA(s) and push status (or the exact uncommitted files and why);
3. the exact clean-start command using the **live** values, e.g.
   `cd <repository-root> && claude` — from the correct repository root so the project's
   default-deny MCP policy governs; if the repository's approved launch design specifies explicit
   MCP flags (installed equivalents of `--strict-mcp-config` + explicit MCP config), include them
   exactly as approved; the successor must see an empty (or exactly-allowlisted) `/mcp` list;
4. a clearly labeled `COPY INTO THE NEW SESSION` prompt (see F).

## F. Successor prompt (generate with live values)

The `COPY INTO THE NEW SESSION` prompt must instruct the successor to:

- work from durable repository evidence, not assumptions about the old conversation;
- verify repository root, worktree, branch, HEAD, and the effective MCP configuration (`/mcp`)
  before making any change;
- read root `CLAUDE.md`, `docs/SESSION_HANDOFF.md`, the active task record(s), and the
  authoritative files listed in the handoff;
- run `python tools/project_control.py status`;
- reconcile the handoff against live git and the ledger — live evidence and the ledger win over
  stale prose;
- detect stale, missing, duplicated, or already-completed work before acting;
- report `READY TO RESUME` or `BLOCKED` (with the exact discrepancy);
- if ready, continue from the exact next action without repeating completed work or broadening
  scope;
- stop for any action that requires owner approval.
