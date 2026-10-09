Create one permanent, reusable project slash command for safely handing the main Claude Code session to a fresh session.

This is a small, bounded operator utility. Do not modify or rewrite the large Fable–Codex implementation directive. Do not begin the larger continuous-loop implementation as part of this task.

The command must be:

    /session-handoff [optional reason]

Implement it as a project skill at:

    .claude/skills/session-handoff/SKILL.md

Required frontmatter:

    name: session-handoff
    description: Safely lands the active main Claude Code session, updates the canonical living handoff, and prints the exact successor-session prompt.
    argument-hint: "[reason]"
    disable-model-invocation: true

Important execution rules:

1. Do not add `context: fork`.
2. Do not specify a sub-agent or background execution.
3. Do not grant broad `allowed-tools`.
4. It must execute inline inside the active main Claude Code/Fable conversation so it can see the current conversation, task, plan, existing sub-agents, decisions, and tool state.
5. Only the owner may invoke it.
6. Use `$ARGUMENTS` as the optional reason for turnover.
7. Do not create a second competing handoff system. Reuse the repository’s existing project-control ledger, supervisor export-handoff machinery, Git state, and canonical `docs/SESSION_HANDOFF.md`.
8. If repository governance requires a small task record for this utility, create the smallest valid record. Do not rewrite the large directive.

When `/session-handoff` is invoked, it must perform this sequence:

A. LAND THE CURRENT SESSION

- Immediately stop starting new work and stop assigning new sub-agents.
- Identify the exact repository root, worktree, branch, HEAD commit, task, campaign, and current lease.
- Inspect all active or recently completed sub-agents.
- Allow a healthy active sub-agent to reach a safe stopping point and return its result.
- Do not kill a productive sub-agent merely because turnover was requested.
- Collect and reconcile every returned result.
- Identify unfinished tests, running commands, pending permission prompts, pending commits, pushes, pull requests, approvals, or other external effects.
- Do not claim the handoff is ready while any important result or external action is ambiguous.

B. SAVE THE ACTUAL WORK

- Update the authoritative task/ledger records only to reflect work that was actually completed.
- Run the minimum appropriate validation needed to establish the present state.
- If the current checkpoint is valid and existing repository policy authorizes it, commit and push the checkpoint.
- Never force a commit of broken or unverified work.
- If changes must remain uncommitted, preserve them and record their exact status in the handoff.
- Do not start another implementation unit while landing.

C. REPLACE THE LIVING HANDOFF

Replace the contents of `docs/SESSION_HANDOFF.md`; do not continuously append to it.

The handoff must contain:

1. Generation time and session identifier.
2. Exact repository root, worktree, branch, and HEAD.
3. Clean or dirty Git status and every changed/untracked file.
4. Active directive, campaign, task, requirements, dependencies, and lease.
5. Original objective of the current task.
6. Work completed, with durable evidence.
7. Work attempted but not completed.
8. Decisions made and the reasons for them.
9. Rejected approaches and failed attempts.
10. Files and important code areas changed.
11. Tests and validation commands run, with exact outcomes.
12. Current sub-agent status, assignment, result, and whether each agent should be resumed or replaced.
13. Outstanding blockers, uncertainties, permissions, approvals, and external effects.
14. Standing owner restrictions that remain in force.
15. The smallest list of authoritative files the successor must read.
16. The exact next action the successor should perform.
17. Conditions that would require the successor to stop or change the plan.
18. A ready-to-copy successor-session prompt.

Do not include secrets, credentials, enormous logs, or the full conversation transcript.

D. VALIDATE THE HANDOFF

Before declaring success:

- Re-read the finished handoff.
- Compare its repository identity against live Git.
- Compare its task state against the authoritative ledger.
- Confirm all sub-agents and pending actions are accounted for.
- Confirm the listed next action follows logically from the completed work.
- Confirm no important state exists only in the conversation.

If anything important remains unsafe or uncertain, print:

    HANDOFF BLOCKED

Then explain exactly what must be resolved. Do not instruct the owner to clear the session.

If everything is reconciled, print:

    HANDOFF READY

Then print:

1. The exact handoff path.
2. The saved commit and push status.
3. The exact command for starting Claude Code from the correct repository root with the repository-approved MCP configuration.
4. A clearly labeled `COPY INTO THE NEW SESSION` prompt.

The generated successor prompt must instruct the next session to:

- Work from durable repository evidence, not assumptions about the old conversation.
- Verify repository root, worktree, branch, HEAD, and effective MCP configuration before making changes.
- Read root `CLAUDE.md`, `docs/SESSION_HANDOFF.md`, the task record, and the authoritative files listed in the handoff.
- Run the project-control status command.
- Reconcile the handoff against live Git and the ledger; live repository evidence and the ledger win if prose is stale.
- Detect stale, missing, duplicated, or already-completed work.
- Report `READY TO RESUME` or `BLOCKED`.
- If ready, continue from the exact next action without repeating completed work or broadening scope.
- Stop for any required owner approval.

Add a safe dry-run mode:

    /session-handoff dry-run

Dry-run must inspect and preview the handoff process without editing, committing, pushing, stopping agents, or changing ledger state.

Test both dry-run and real operation safely. Verify that `/session-handoff` appears in `/skills` and the slash-command autocomplete. Commit and push this utility through the repository’s normal review and validation process.

At completion, report exactly what was created, how it was tested, and whether `/session-handoff` is now ready for use.
