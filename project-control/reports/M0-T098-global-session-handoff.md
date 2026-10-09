# M0-T098 producer report — hybrid global/project /session-handoff (D-026)

Producer: orchestrator (main session, ctl24). Date: 2026-08-25.

## What was built

1. **Global personal skill** `C:\Users\MLFLL\.claude\skills\session-handoff\SKILL.md` (outside the
   repo — only that exact directory touched, per D-026-R007; sha256 recorded below). Fully generic:
   no NYC-specific content. New section **R (RESOLVE THE REPOSITORY)** runs first on every
   invocation: live-git root/worktree/branch/HEAD/origin detection (never a remembered directory);
   profile lookup at `<repo-root>/.claude/session-handoff-profile.md` with **identity verification**
   (expected origin + marker files vs live) and repo-root-relative resolution; never writes into a
   different worktree; identity mismatch → `HANDOFF BLOCKED`. No-profile fallback: established-
   convention search (prefer an existing canonical handoff file; plain git evidence; no
   project-control assumption), ambiguous → `HANDOFF BLOCKED` + ask owner; non-git location →
   write nothing without owner confirmation. All D-025 safe-landing behavior preserved
   (stop-new-work, sub-agent care, effect reconciliation, REPLACE semantics, READY/BLOCKED
   contract with the 4 print items, successor prompt), generalized to profile-defined authorities.
2. **Project profile** `.claude/session-handoff-profile.md`: stable NYC routing only — repository
   identity (expected origin + 3 marker files; PUBLIC-repo caution), destination
   `docs/SESSION_HANDOFF.md` (REPLACE + ~4000-token budget), must-read instructions, authoritative
   ledger + campaign-record locations with "state overrides prose" rules, exact verified commands
   (`python tools/project_control.py status`, `python -m tools.agent_supervisor.campaign_continuity
   --status`, `python -m tools.agent_supervisor export-handoff`, validator, budget check), ADR-005/
   ADR-006 commit/push policy, Bootstrap Gate 0 MCP-clean launch requirements, successor start
   command (`cd <detected-repo-root> && claude`), sub-agent/lease rules, standing owner gates
   (PR #241, activation gate, Tier D, expansion hold, dependency policy). **Every path is
   repo-root-relative; no ctl24 or other worktree path is hard-coded** (grep-verified).
3. **Project skill slimmed into the repository fallback** `.claude/skills/session-handoff/SKILL.md`
   (NOT deleted): D-025 frontmatter preserved byte-identical; intro states the fallback role and
   the personal-overrides-project precedence; **the procedure body from section R onward is
   byte-identical to the global skill** (verified programmatically), and both follow the same
   profile — structural zero-drift.

## Resolved skill precedence
Per official docs (owner correction): **personal overrides project** on a name collision. After
the personal skill loads, `/session-handoff` always executes the GLOBAL copy; the project copy
serves machines/accounts without it. Because the two procedure bodies are identical and both route
through the same profile, precedence never changes behavior.

## Test evidence (D-026 §5, all executed; nothing disturbed active work)

- **Frontmatter validation (both copies):** exactly the four required keys
  (name/description/argument-hint/disable-model-invocation: true); no `context:`, no `agent:`, no
  `allowed-tools`; `$ARGUMENTS` + dry-run + READY/BLOCKED + COPY-INTO + DRY-RUN-ONLY + profile +
  show-toplevel strings all present. Manually-invocable-only = `disable-model-invocation: true`;
  no forked context = no `context:` key (verified).
- **Dry-run from ctl24 (live, read-only):** step R detected root `C:/Users/MLFLL/Downloads/
  nyc-zoning/ctl24` dynamically (git show-toplevel), branch `control/D-024-fable-codex-loop`,
  HEAD `a8cefe0`, origin `https://github.com/martin10101/nyc-buildability.git`; profile FOUND at
  the detected root; identity VERIFIED (origin match + markers `CLAUDE.md`,
  `tools/project_control.py`, `project-control/directives/index.json`); destination resolved to
  **ctl24's own** `docs/SESSION_HANDOFF.md` (exists in this worktree). No repository, ledger, git,
  or sub-agent state changed by the dry-run (inspection commands only).
- **No cross-worktree selection:** `git -C ctl23 rev-parse --show-toplevel` → `ctl23` — each
  invocation resolves under its OWN show-toplevel; the destination is always
  `<show-toplevel>/docs/SESSION_HANDOFF.md`, so a cross-worktree write path does not exist. The
  successor launch command prints the live detected root (`cd <detected-repo-root> && claude`).
- **Generic fallback (disposable temp repo, no project-control, no profile):** convention search
  found no `docs/SESSION_HANDOFF.md`/`HANDOFF.md`/instruction reference → procedure result
  `HANDOFF BLOCKED` (ask owner); zero files written (git status clean).
- **Established-convention preference (temp repo WITH `HANDOFF.md`):** the existing file is
  selected under its own root; nothing invented.
- **Non-git location:** `git rev-parse --show-toplevel` → `fatal: not a git repository` →
  procedure result `HANDOFF BLOCKED`, write nothing without owner confirmation.
- **Profile identity mismatch (temp repo + planted profile claiming a different origin/markers):**
  live origin absent + markers missing vs profile claims → profile NOT followed, `HANDOFF BLOCKED`
  with the exact mismatch.
- **Project copy fallback availability:** the repo-tracked skill remains present with valid
  frontmatter; on a machine without `~/.claude/skills/session-handoff` it is the only `/session-
  handoff` and loads normally (standard project-skill registration, proven for this repo since
  D-025).

## Restart requirement (truthful)
Skills are loaded at session start. The **global** skill is new in this session, so it appears in
`/skills` (and takes precedence) from the **next Claude Code session/restart**. Until then, the
project copy — already registered — serves identically (identical body + same profile).

## File identities
- global skill: sha256 504fabbb301a4764... (7746 bytes) (file lives outside the repo; content mirrored
  by the project fallback body from §R onward, which IS repo-tracked).
- No real handoff was run: this task changed no `docs/SESSION_HANDOFF.md` content (D-026-R027).

## Limitations
- The global skill's behavior on OTHER repositories is convention-based by design (their profiles
  don't exist yet); the BLOCKED-and-ask path is the safe default.
- Frontmatter `allowed-tools` narrowing was deliberately NOT added (owner spec lists "no broad
  allowed-tools" — omitting the key inherits the session's ordinary permission flow, matching the
  D-025 precedent).
