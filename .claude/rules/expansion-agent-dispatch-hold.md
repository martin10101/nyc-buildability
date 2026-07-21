# EXPANSION-AGENT HOLD NOTICE (owner directive 2026-07-17; G5 M0-T010)

This notice is deliberately unconditioned (no `paths:` frontmatter) so it attaches to every session:
it carries the still-active owner hold on expansion planning. (The 3D/UI *technical* rules are now
path-scoped in `.claude/rules/3d-ui-expansion.md`, loading only under `apps/web/**`.)

## 1. Dispatch-guard backstop (former prohibition RETIRED 2026-07-17)

The former prohibition on dispatching the five expansion agents (`3d-massing-engineer`,
`product-design-director`, `visual-quality-reviewer`, `financial-feasibility-engineer`,
`opportunity-search-engineer`) was **retired 2026-07-17** at M0-T013 acceptance (blocker B-007
resolved); the `.claude/hooks/agent_dispatch_guard.py` guard now permits them. **Keep the guard and
its tests in place as a regression backstop — do not remove or re-scope them without a G5 review.**
Dispatchability does not authorize expansion work; §2 governs planning. Full retired text:
`docs/archive/expansion-agent-dispatch-prohibition-retired-2026-07-17.md`.

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
