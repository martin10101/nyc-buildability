# EXPANSION-AGENT DISPATCH HOLD (owner directive 2026-07-17; G5 M0-T010)

This notice is deliberately unconditioned (no `paths:` frontmatter) so it attaches to
every session — the same always-loaded plane as `.claude/rules/3d-ui-expansion.md`.

## 1. DISPATCH PROHIBITED

The subagents `3d-massing-engineer`, `product-design-director`, `visual-quality-reviewer`,
`financial-feasibility-engineer`, `opportunity-search-engineer` MUST NOT be dispatched by
any session, agent, skill, workflow, or hook until conformance task **M0-T013** is accepted
and blocker **B-007** (`project-control/blockers/B-007-expansion-agent-conformance.json`)
is closed. Their definitions lack the ADR-005 protocol sections; dispatching them under
current session permissions would allow non-orchestrator ledger writes.

This prohibition is machine-enforced: the PreToolUse hook
`.claude/hooks/agent_dispatch_guard.py` (wired in the tracked `.claude/settings.json`)
reads B-007 live and rejects Agent/Task dispatch of these five exact names while the
blocker is open. Do not remove, bypass, or re-scope the hook or this notice; only the
orchestrator retires them, in the same checkpoint that closes B-007 after M0-T013
acceptance (G3 + G5 re-check).

## 2. OWNER-REVIEW HOLD ON EXPANSION PLANNING

`.claude/rules/3d-ui-expansion.md` item 13 ("update the existing master plan and continue
from the first unblocked task") and `CONTINUE_FROM_CURRENT_STATE_PROMPT.md` item 10 are
**SUSPENDED** pending owner review of `docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md`. Do not
contract or start the 19 proposed tasks, do not author the 9 proposed contracts, do not
apply GDS proposals P1–P8, and do not change the master plan or any MASTER_EXECUTION_PLAN
on their instruction. This notice supersedes those passages by owner directive 2026-07-17.
Accepted work stands at the ledger's count; nothing in the expansion pack alters accepted
tasks.

## 3. TASK-ID CONVENTION

Pack task IDs (`3D-xxx` / `UI-xxx` / `COMP-xxx`) are workstream labels only. Ledger tasks
use `M<milestone>-T<number>` (docs/PROJECT_CONTROL_PROTOCOL.md). Never create ledger tasks
under the pack scheme.
