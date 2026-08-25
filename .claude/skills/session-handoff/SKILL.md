---
name: session-handoff
description: Safely lands the active main Claude Code session, updates the canonical living handoff, and prints the exact successor-session prompt.
argument-hint: "[reason]"
disable-model-invocation: true
---

# /session-handoff — land the main session and hand off safely (repository fallback copy)

Owner-only operator utility. This is the REPOSITORY-CONTROLLED FALLBACK copy (D-025/D-026): it exists so machines, cloud environments, or accounts WITHOUT the personal ~/.claude/skills/session-handoff skill still have the command. When the personal skill is installed it OVERRIDES this copy (official precedence: personal wins on name collision) - both copies follow the identical procedure below and the SAME repository profile (.claude/session-handoff-profile.md), so precedence never changes behavior. It runs **inline in this main conversation** — you are the active
session; use your live knowledge of the current task, plan, sub-agents, decisions, and tool state
together with durable repository evidence. Never delegate this procedure to a sub-agent, a fork, or
a background task. Never invent a second handoff system: reuse whatever the current repository
already treats as canonical.

`$ARGUMENTS` is the optional turnover reason — record it verbatim in the handoff header. If
`$ARGUMENTS` is exactly `dry-run`, follow **DRY-RUN** below instead of the real sequence.

## R. RESOLVE THE REPOSITORY — always first, always live

1. Determine where you actually are, from live Git evidence only — never from memory of an earlier
   invocation: `git rev-parse --show-toplevel` (the ACTIVE worktree root), `git rev-parse
   --abbrev-ref HEAD`, `git rev-parse HEAD`, `git remote get-url origin` (may be absent),
   `git worktree list`.
2. **Not inside a Git repository?** Write NOTHING anywhere. Print `HANDOFF BLOCKED`, state the
   actual directory, and ask the owner where (or whether) to record a handoff.
3. **Profile lookup:** check `<repo-root>/.claude/session-handoff-profile.md` (repo-root = the
   show-toplevel result from step 1). If it exists, read it COMPLETELY and follow it:
   - Verify the profile matches the current repository identity (its stated expected origin and/or
     marker files vs the live origin URL and tree). **Never follow a profile whose identity does
     not match** — print `HANDOFF BLOCKED` with the exact mismatch instead.
   - Resolve EVERY relative path in the profile underneath the detected repo root — never under a
     hard-coded or remembered path, and **never write the handoff into a different worktree** than
     the one resolved in step 1 (each worktree has its own checkout of the handoff file).
4. **No profile?** Use the generic convention search, in order: an existing, clearly canonical
   handoff file (e.g. `docs/SESSION_HANDOFF.md`, `HANDOFF.md`, `docs/HANDOFF.md` — something the
   repo's own instructions reference); otherwise treat the repository's README/CLAUDE.md-named
   conventions as the guide. Prefer an already-established file over inventing one. Use plain Git
   evidence for the handoff content; do NOT assume any project-control tooling exists. If no
   unambiguous destination exists, print `HANDOFF BLOCKED` and ask the owner where this project
   should store its handoff — do not guess.

## DRY-RUN (`/session-handoff dry-run`)

Strictly read-only: run only inspection commands (the step-R git commands, profile read, status
commands the profile names as read-only). Do **not** edit any file, commit, push, stop or message
any agent, or change any ledger/task state. Print a preview: the resolved repo root/worktree/
branch/HEAD/origin, which profile (or fallback convention) was selected and why, the resolved
handoff destination path, active sub-agents and what would happen to each, pending external
effects, what the real run would commit, and whether it would print `HANDOFF READY` or
`HANDOFF BLOCKED` (with reasons). End with `DRY-RUN ONLY — nothing was changed.`

## A. LAND THE CURRENT SESSION

1. Immediately stop starting new work and stop assigning new sub-agents; begin no new
   implementation unit for the rest of this procedure.
2. Record exactly: repo root, worktree, branch, HEAD, origin (from step R), plus the active
   task/campaign/lease state from whatever authoritative sources the profile names (or plain Git
   if none).
3. Inspect every active or recently completed sub-agent. A **healthy, productive** agent finishes
   its already-bounded assignment — do not kill it merely because turnover was requested; wait for
   its natural completion or safe checkpoint. Only an unresponsive or unsafe agent may be stopped,
   and that stop must be recorded in the handoff.
4. Collect and reconcile every returned sub-agent result into durable state.
5. Enumerate everything in flight: unfinished tests, running commands, pending permission prompts,
   uncommitted changes, unpushed commits, PRs awaiting action, approvals, and any external effect
   whose outcome is unconfirmed. While anything important is ambiguous, the handoff is **not**
   ready.

## B. SAVE THE ACTUAL WORK

1. Update the repository's authoritative records (as the profile defines them) to reflect **only
   work that actually completed** — never round up.
2. Run the minimum validation that establishes the present state (the profile's named checks, or
   the tests relevant to what changed). Record exact commands and outcomes.
3. Commit and push only if the checkpoint is valid AND the repository's stated commit/push policy
   (profile) authorizes it. **Never force-commit broken or unverified work.** If changes must stay
   uncommitted, leave them untouched and record each file and why in the handoff.

## C. REPLACE THE LIVING HANDOFF

**Replace** the contents of the resolved destination file (current-only; history lives in git;
honor any size budget the repository enforces). Include: generation time + session id + reason
(`$ARGUMENTS`); exact root/worktree/branch/HEAD; full dirty-file enumeration; active authority/
campaign/task/lease state; original objective; work completed with durable evidence; work
attempted-not-completed; decisions + reasons; rejected approaches; files changed; validation
commands + exact outcomes; per-sub-agent status and resume-or-replace recommendation; outstanding
blockers/permissions/effects; standing restrictions in force; the smallest authoritative-files
list; the exact next action; stop/change conditions; and the ready-to-copy successor prompt (F).
Exclude secrets, credentials, tokens, enormous logs, and the conversation transcript.

## D. VALIDATE, then print exactly one of:

Re-read the finished handoff; compare its identity block against live Git; compare its task state
against the repository's authoritative records (they win); confirm every sub-agent and pending
action is accounted for; confirm the next action follows from the completed work; confirm no
important state exists only in this conversation.

If anything important is unsafe or uncertain — print `HANDOFF BLOCKED` and explain precisely what
must be resolved (never tell the owner to clear the session). Otherwise print `HANDOFF READY`
followed by: (1) the exact handoff path; (2) the saved commit SHA(s) and push status (or exact
uncommitted files and why); (3) the exact clean-start command **using the live worktree root from
step R** plus the repository's launch requirements from the profile (e.g. MCP posture); (4) a
clearly labeled `COPY INTO THE NEW SESSION` prompt.

## F. Successor prompt (generate with live values)

Instruct the successor to: work from durable repository evidence, not assumptions about the old
conversation; verify repo root, worktree, branch, HEAD, and the effective launch requirements
before any change; read the repository's root instructions, the handoff, and the authoritative
files it lists; run the profile's named status command(s) if any; reconcile the handoff against
live Git and the authoritative records (they win over prose); detect stale/duplicated/completed
work; report `READY TO RESUME` or `BLOCKED`; if ready, continue from the exact next action without
repeating work or broadening scope; stop for anything requiring owner approval.
