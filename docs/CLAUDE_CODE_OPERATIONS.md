# Claude Code Operations Used by This Pack

The pack uses these Claude Code mechanisms:

- Root `CLAUDE.md` for short permanent instructions and imports
- `.claude/agents/` for project-specific specialist subagents
- `.claude/skills/` for long procedures loaded only when needed
- `.claude/rules/` for scoped instructions
- Project-scoped subagent memory for stable specialist learnings
- Worktree isolation for parallel writing agents
- Optional dynamic workflows for large repeated cross-checks
- Optional hooks after the repository has real build/test commands

Before changing syntax or adopting preview features, verify current official documentation:

- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/hooks-guide
- https://code.claude.com/docs/en/worktrees
- https://code.claude.com/docs/en/workflows
- https://code.claude.com/docs/en/agent-teams

Agent teams remain optional because they may be experimental. The file-based project-control system remains authoritative regardless of Claude execution mode.


## Low-storage execution

Because the owner’s PC has approximately 7 GB free, run Claude Code in a remote development environment such as GitHub Codespaces when the task requires dependencies, builds, browsers, databases, or test tooling. The local machine may hold a small source-only checkout, but cloud execution is the default. Full instructions are in `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`.
