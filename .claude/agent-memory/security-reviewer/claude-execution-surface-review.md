---
name: claude-execution-surface-review
description: How to review .claude/rules and .claude/agents merges as active execution surfaces (M0-T010 G5 method)
metadata:
  type: project
---

Method for G5 review of `.claude/` execution-surface merges (first used M0-T010, 2026-07-17):

- `.claude/rules/*.md` WITH `paths:` frontmatter attach only when a matching file is touched (observed live: `project-control.md` content was injected as a system-reminder immediately after reading `project-control/tasks/M0-T010.json`). A rules file WITHOUT frontmatter attaches unconditionally to every session — treat it as an always-on standing instruction to the orchestrator.
- `.claude/agents/*.md` auto-register as dispatchable subagent types on checkout; nothing in the repo can machine-block dispatch of a specific agent type (permissions deny rules are tool/path-scoped, not agent-type-scoped). Dispatch prohibitions are therefore prompt-level only: always-loaded rules-file counter-notice + blocker JSON (read at session start per CLAUDE.md routine) is the strongest available control.
- `tools/project_control.py` does NOT enforce orchestrator-only invocation (ADR-005 regression note: "producer can claim/progress/submit"); the only guardrails it enforces are no-self-100% and no-self-gate. ADR-005 compliance otherwise rests entirely on protocol text embedded in each agent definition — so an agent file lacking the protocol section is a real escalation surface, not a style gap.
- Check `.claude/settings.local.json` permission posture every time: this project runs `defaultMode: bypassPermissions` with blanket `Bash/git/gh/python` allows, so any dispatched agent with Bash runs ledger/git/network commands unprompted. Severity of missing protocol sections scales with this.

**How to apply:** for any merge adding files under `.claude/`, review (1) frontmatter attachment scope, (2) auto-registration payload, (3) standing instructions that could drive unattended continuation, (4) whether embedded ADR-005 protocol text is present, before secrets/content review.
