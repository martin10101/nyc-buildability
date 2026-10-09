Make the existing /session-handoff capability globally available while preserving correct project-specific routing.

This is a small, bounded skill improvement. Do not modify the large D-024 implementation directive. If governance requires a small task or owner-instruction record, create only the minimum required record.

Important correction from official Claude Code documentation:

- A personal skill overrides a project skill when both have the same command name.
- Therefore, do not assume the project copy of /session-handoff will win.
- Design the personal/global skill to deliberately load the current repository’s profile.

Implement the following hybrid structure.

1. GLOBAL COMMAND

Create:

C:\Users\MLFLL\.claude\skills\session-handoff\SKILL.md

This must provide:

/session-handoff [optional reason]

Required properties:

- User-invoked only: `disable-model-invocation: true`
- No `context: fork`
- No sub-agent execution for the handoff itself
- No broad `allowed-tools`
- Runs inside the active main Claude Code conversation
- Supports `/session-handoff dry-run`
- Uses `$ARGUMENTS` for the reason or dry-run mode

Claude Code may request permission to write outside the repository. Request access only to this exact directory:

C:\Users\MLFLL\.claude\skills\session-handoff\

Do not request broad access to unrelated user folders.

2. PROJECT PROFILE

Inside the current NYC Buildability repository, create:

.claude/session-handoff-profile.md

This profile must contain only stable, project-specific routing information, including:

- Repository identity and expected origin
- Handoff destination: docs/SESSION_HANDOFF.md
- Root project instructions that must be read
- Authoritative project-control and ledger locations
- The exact verified project-control status command
- The exact verified existing supervisor export-handoff command, if applicable
- The repository’s safe commit and push policy
- MCP-clean launch requirements
- The command used to start the successor session
- Any files whose state overrides handoff prose
- Rules for active sub-agents and task leases
- Standing owner gates that must not be crossed automatically

All file locations in the profile must be relative to the detected Git repository root. Do not hard-code ctl24 or another temporary worktree path.

3. GLOBAL ROUTING BEHAVIOR

Whenever /session-handoff runs:

- Determine the active repository root using live Git evidence.
- Determine the current worktree, branch, HEAD, and origin.
- Never assume the directory from an earlier invocation.
- Look for `<repo-root>/.claude/session-handoff-profile.md`.
- If it exists, read it completely and follow it.
- Verify that the profile matches the current repository identity.
- Resolve every relative path underneath the detected repository root.
- Never write the handoff into a different worktree.
- Never follow a profile whose repository identity does not match.

If no profile exists:

- Look inside the current repository for an existing canonical handoff convention.
- Prefer an already-established handoff file over inventing another one.
- Use plain Git evidence for the generic handoff.
- Do not assume project-control tooling exists.
- If no unambiguous handoff destination exists, return `HANDOFF BLOCKED` and ask the owner where that project should store its handoff.
- If the current directory is not inside a Git repository, do not write anywhere without owner confirmation.

4. EXISTING PROJECT SKILL

Inspect the existing project skill:

.claude/skills/session-handoff/SKILL.md

Do not delete it.

Keep it as the repository-controlled fallback for another computer, cloud environment, or user account that does not have the personal/global skill installed.

Remove duplicated NYC-specific routing details from the procedure only when those details have been safely moved into `.claude/session-handoff-profile.md`. Both the global skill and the project fallback must follow the same project profile so they cannot drift into two different handoff systems.

Preserve all existing safe-landing behavior, including:

- Stop assigning new work
- Reconcile active sub-agents
- Allow healthy sub-agents to reach a safe seam
- Account for tests, Git changes, approvals, and external effects
- Replace rather than endlessly append to docs/SESSION_HANDOFF.md
- Produce HANDOFF READY or HANDOFF BLOCKED
- Print the exact successor launch command
- Print the complete copy-and-paste successor-session prompt

Do not modify the large implementation directive merely because a session handoff occurs.

5. TESTING

Perform these tests without disturbing active implementation work:

- Validate the global SKILL.md frontmatter.
- Confirm /session-handoff is manually invocable only.
- Confirm it does not use forked context.
- Confirm dry-run makes no repository, ledger, Git, or sub-agent changes.
- Run dry-run from the current ctl24 worktree.
- Confirm it detects the actual ctl24 Git root dynamically.
- Confirm it selects `.claude/session-handoff-profile.md`.
- Confirm it resolves the destination to ctl24’s own docs/SESSION_HANDOFF.md.
- Confirm it does not accidentally select another worktree.
- Confirm it prints the exact current worktree in the successor launch command.
- Test the generic fallback in a disposable temporary Git repository with no project-control files.
- Confirm an ambiguous or non-Git location fails safely.
- Confirm the project copy remains available as a fallback when the personal skill is absent.

After implementation, show:

1. Every created or changed file.
2. The resolved skill precedence.
3. Dry-run results from ctl24.
4. Whether a Claude Code restart is required.
5. The exact command I should type thereafter.

Do not begin a real handoff unless I explicitly invoke /session-handoff without dry-run.
