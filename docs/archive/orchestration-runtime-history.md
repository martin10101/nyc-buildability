# ARCHIVED — orchestration runtime-version history

> Historical only. Runtime tool surfaces (agent-team creation/teardown, version gates) change between
> Claude Code releases. Do not treat any version number below as current. The live policy
> (`.claude/ORCHESTRATION_POLICY.md`) describes mechanisms without pinning versions; the runtime's own
> tool descriptions are the source of truth for exact tool names.

## Runtime notes captured during setup (2026-07-20 → 2026-07-21)

- Agent-orchestration setup landed as a config-only change (branch `control/agent-orchestration-setup`,
  merged via PR #68). Agent-team *settings keys* were pre-staged in user `settings.json`
  (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, `teammateMode: in-process`).
- At setup time the global npm CLI on PATH was `2.0.11`; the active IDE-extension runtime was later
  observed as `2.1.215` (env `AI_AGENT=claude-code_2-1-215_agent`). The npm CLI on PATH is not what
  the IDE extension session runs.
- Agent-team coordination tool names varied by release: earlier notes referenced
  `TeamCreate`/`TeamDelete`; the 2.1.215 IDE runtime had no separate `TeamCreate`/`TeamDelete` tool —
  teammates were spawned as named agents (Agent tool) and torn down with `TaskStop`. Because this
  surface drifts, the live policy no longer names a specific create/delete tool or version baseline.
- In-process agent-team runtime state (files under `~/.claude/teams/` and `~/.claude/tasks/`) does not
  survive a conversation resume/restart/compaction; agent *definitions* in `.claude/agents/`, the
  policy, and the `project-control/` ledger are the durable layer.
