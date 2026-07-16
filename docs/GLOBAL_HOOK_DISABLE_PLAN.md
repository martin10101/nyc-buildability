# Global `auto-project-setup.sh` hook — inventory and reversible disable plan

Status: **PLAN ONLY — awaiting owner approval. Nothing in `~/.claude/` has been modified.** (Owner directive 2026-07-16: the global hook affects other projects; do not remove or alter until explicitly approved.)

## 1. Inventory (read 2026-07-16)

**Hook file:** `~/.claude/hooks/auto-project-setup.sh` (5,760 bytes)

**Registration:** `~/.claude/settings.json` → `hooks.UserPromptSubmit[0].hooks[0]`:

```json
{ "type": "command", "command": "$HOME/.claude/hooks/auto-project-setup.sh" }
```

**Behavior (verified by reading the script):**
1. Runs on **every user prompt** in **every project** on this machine.
2. Exits immediately if `<project>/.claude/.auto-setup-complete` exists (line 15) — this marker is why the file must never be deleted from this repo (`.gitignore`d; see SESSION_HANDOFF rule).
3. Also exits (after creating the marker) if the project already has `.claude/hooks/` AND `.claude/skills/` AND `.claude/agents/` (lines 20–27). Note: this repo HAS `.claude/skills/` and `.claude/agents/` but NOT `.claude/hooks/`, which is why the marker file is the only thing standing between us and a third reinstall.
4. Otherwise copies the generic Node/Express pack from `~/.claude-infrastructure/.claude` (hooks, skills, agents, commands, settings.json) into the project and runs `npm install` inside `.claude/hooks/` (~35.6 MB observed on the 2026-07-16 reinstall).
5. Source of the pack: `github.com/diet103/claude-code-infrastructure-showcase` (third-party showcase repo, unrelated to this project).

**Other global hooks registered in `~/.claude/settings.json`** (inventoried for completeness; NOT part of this plan):
- `$HOME/.claude/hooks/investigation-board-hook.sh` — UserPromptSubmit, PreToolUse (Read|Edit|Write|MultiEdit|Bash|Task), PostToolUse (…|Glob|Grep), Stop. 602 bytes.
- `$CLAUDE_PROJECT_DIR/.claude/hooks/skill-activation-prompt.sh` — UserPromptSubmit (no-ops here: path doesn't exist in this repo).
- `$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-tracker.sh` — PostToolUse (no-ops here).
- `$CLAUDE_PROJECT_DIR/.claude/hooks/tsc-check.sh` and `trigger-build-resolver.sh` — Stop (no-op here).

Impact on this project today: **disarmed** by the `.claude/.auto-setup-complete` marker only. Two prior misfires quarantined under `_quarantine/`.

## 2. Reversible disable plan (one JSON edit, no file deletions)

When approved, the orchestrator will do exactly this:

1. **Backup:** copy `~/.claude/settings.json` → `~/.claude/settings.json.bak-2026-07-16` (kept indefinitely; also paste the removed block into the acceptance note).
2. **Edit:** remove the single array element
   `{"type": "command", "command": "$HOME/.claude/hooks/auto-project-setup.sh"}`
   from `hooks.UserPromptSubmit[0].hooks` in `~/.claude/settings.json`. Nothing else changes — the script file itself stays on disk untouched, `~/.claude-infrastructure/` stays untouched, all other hooks stay registered.
3. **Verify:** JSON-parse the edited file; diff against the backup to confirm the one-element change; restart a Claude Code session and confirm the hook no longer fires in a scratch directory without a marker file.
4. **Keep the local belt-and-suspenders:** leave `.claude/.auto-setup-complete` in place in this repo regardless — it protects against the hook being re-enabled later.

**Rollback (single step):** `Copy-Item ~/.claude/settings.json.bak-2026-07-16 ~/.claude/settings.json -Force` (or re-insert the removed element). Because the script and `~/.claude-infrastructure/` are never touched, restoring the settings line fully restores prior behavior for all other projects.

**Effect on other projects:** they stop receiving *automatic* pack installation on next prompt; any project already set up (marker present or pack copied) is unaffected. The owner can still install the pack manually in any project with:
`bash ~/.claude/hooks/auto-project-setup.sh` run from that project root (or by copying from `~/.claude-infrastructure/.claude`).

## 3. Decision needed from owner

Reply "approve hook disable" (or edit this file) and the orchestrator will execute §2 verbatim and record the before/after diff as evidence. Until then: no action.
