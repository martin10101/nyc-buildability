---
name: claude-execution-surface-review
description: How to review .claude/rules and .claude/agents merges as active execution surfaces (M0-T010 G5 method)
metadata:
  type: project
---

Method for G5 review of `.claude/` execution-surface merges (first used M0-T010, 2026-07-17):

- `.claude/rules/*.md` WITH `paths:` frontmatter attach only when a matching file is touched (observed live: `project-control.md` content was injected as a system-reminder immediately after reading `project-control/tasks/M0-T010.json`). A rules file WITHOUT frontmatter attaches unconditionally to every session — treat it as an always-on standing instruction to the orchestrator.
- `.claude/agents/*.md` auto-register as dispatchable subagent types on checkout (and even mid-session after a merge). CORRECTED 2026-07-17: agent-type dispatch CAN be machine-blocked — a PreToolUse hook on `Agent|Task` in tracked `.claude/settings.json` (`.claude/hooks/agent_dispatch_guard.py`, reads blocker JSON live, exit 2 blocks) fired live in-session against a real dispatch. Hook-level enforcement supersedes the earlier "prompt-level only" conclusion; pair it with the always-loaded counter-notice + blocker for defense in depth.
- `tools/project_control.py` does NOT enforce orchestrator-only invocation (ADR-005 regression note: "producer can claim/progress/submit"); the only guardrails it enforces are no-self-100% and no-self-gate. ADR-005 compliance otherwise rests entirely on protocol text embedded in each agent definition — so an agent file lacking the protocol section is a real escalation surface, not a style gap.
- Check `.claude/settings.local.json` permission posture every time — it changes: bypassPermissions was REMOVED 2026-07-17 (G5 M0-T010 correction 6, owner-approved; see docs/SESSION_HANDOFF.md "Permission posture"), replaced by allow (git add/commit/merge, ledger claim/progress/submit/gate) / ask (push, accept, checkpoint, deletes, network, gh mutations) / deny (credential files). Owner further directed a move to Auto mode 2026-07-17 (mid-M0-T013-G5, via tool-rejection channel). Severity of missing protocol sections scales with the live posture at review time.

**How to apply:** for any merge adding files under `.claude/`, review (1) frontmatter attachment scope, (2) auto-registration payload, (3) standing instructions that could drive unattended continuation, (4) whether embedded ADR-005 protocol text is present, before secrets/content review.
