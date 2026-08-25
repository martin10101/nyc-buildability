# Session-handoff profile — NYC Buildability (read by /session-handoff; D-026)

Stable, project-specific routing for the `/session-handoff` skill (global or project copy). Every
path below is **relative to the detected Git repository root** (`git rev-parse --show-toplevel` of
the ACTIVE worktree — never a remembered or hard-coded worktree path; each worktree carries its own
checkout of these files).

## Repository identity (the skill MUST verify before following this profile)
- Expected origin: `https://github.com/martin10101/nyc-buildability.git`
- Marker files that must exist at the root: `CLAUDE.md`, `tools/project_control.py`,
  `project-control/directives/index.json`
- If the live origin or markers do not match, this profile does not apply — `HANDOFF BLOCKED`.
- Note: the GitHub repository is **PUBLIC** — never place secrets, credentials, or tokens in any
  committed artifact (gitleaks pre-commit hook is installed; it is not a license to be careless).

## Handoff destination
- `docs/SESSION_HANDOFF.md` — REPLACE its contents (current-only convention; history lives in git).
  Keep the standard authoritative-state preamble at the top. The `context-budget` CI check fails
  above ~4000 tokens — complete but terse.

## Must-read instructions for landing and for the successor
- Root `CLAUDE.md` (operating rules, gates, authority; start-of-session routine).
- `docs/SESSION_HANDOFF.md` (the living handoff itself).
- The active campaign record(s) under `project-control/campaigns/*.json` — see "state overrides
  prose" below.

## Authoritative state (these override handoff prose — "the ledger wins")
- `project-control/` ledger: `state.json`, `tasks/*.json`, `gates/`, `checkpoints/`, `blockers/`,
  `directives/` — plus live git and CI evidence.
- `project-control/campaigns/*.json` — machine-validated campaign records (canonical next-action
  pointers). Read via: `python -m tools.agent_supervisor.campaign_continuity --status`
  (read-only; exit 1 = fail-closed "orientation unavailable", fall back to the ledger + git).
  Mutation only via the module's `advance()` (orchestrator act) — never hand-edit.

## Exact verified commands (read-only unless noted)
- Project-control status: `python tools/project_control.py status`
- Campaign orientation: `python -m tools.agent_supervisor.campaign_continuity --status`
- Supervisor stored-handoff export (only when a supervisor campaign is active):
  `python -m tools.agent_supervisor export-handoff`
- Registry validator (control-plane changes; takes ~4–5 min, run in background):
  `python tools/validate_directive_compliance.py --check`
- Handoff size check: `python tools/context_budget_check.py`

## Safe commit and push policy
- ADR-005: only the main-session orchestrator runs `tools/project_control.py`, git, and `gh`;
  producers stay in scope; reviewers are read-only.
- ADR-006 / D-010 Tier A: ordinary green work commits and pushes to task/control branches without
  owner approval; Tier B needs the named specialist review; Tier D / Section 20 (credentials,
  payment, production, legal) always stops for the owner.
- Never write to a protected/default branch; never force-push; never skip hooks. Never
  force-commit broken or unverified work. Commit messages for supervisor-touching changes must
  cite a `D-024-R###` qualifying-evidence id (supervisor-freeze rule).

## Successor session launch
- Start command (from the ACTIVE worktree root the skill detected):
  `cd <detected-repo-root> && claude`
- MCP-clean requirement (Bootstrap Gate 0, D-024-R125–R128): the session's primary cwd must BE the
  worktree root (added dirs do not count) and `/mcp` must report no servers (or exactly an
  approved allowlist) BEFORE any repository write. On failure: read-only diagnosis only, fresh
  session required.

## Active sub-agents and task leases
- Healthy productive sub-agents finish their bounded assignments — never killed merely for
  turnover; only unresponsive/unsafe agents may be stopped, and stops are recorded.
- Never resume a TaskStop-killed producer (its worktree is gone; it would run git in the primary
  checkout). Never pass `name:` when spawning a producer (read-only guard denies writes).
- Task leases live in the ledger (`tasks/*.json` claimed/worktree fields); one writer per scope;
  releases and transitions only via `tools/project_control.py`.

## Standing owner gates — never crossed automatically
- **NEVER merge PR #241** or any pre-existing PR without separate owner authorization.
- Continuous/autonomous supervisor activation stays behind the owner gate (D-024 §18; R595
  prerequisite unchanged; supervisor SHADOW-ONLY until the owner activates).
- Owner-only actions: credentials/accounts/payment, production approval, legal/zoning sign-off
  (Tier D / Section 20 hard stops).
- Expansion-planning hold (`.claude/rules/expansion-agent-dispatch-hold.md` §2) remains in force.
- Dependency admissions follow `docs/DEPENDENCY_SECURITY_POLICY.md` (no new packages as a side
  effect of anything).
