# EXPANSION-AGENT HOLD NOTICE (owner directive 2026-07-17; G5 M0-T010)

This notice is deliberately unconditioned (no `paths:` frontmatter) so it attaches to
every session — the same always-loaded plane as `.claude/rules/3d-ui-expansion.md`.

## 1. DISPATCH PROHIBITION — RETIRED 2026-07-17

The former prohibition on dispatching `3d-massing-engineer`, `product-design-director`,
`visual-quality-reviewer`, `financial-feasibility-engineer`, `opportunity-search-engineer`
was RETIRED at M0-T013 acceptance (2026-07-17): all five agent definitions now carry the
ADR-005 protocol sections and conformant frontmatter, verified by G3 + G5 re-check
(project-control/reports/M0-T013-G3-code-review.md and M0-T013-G5-security-recheck.md),
merged at ff24147 with CI green. Blocker B-007 is `resolved`; the PreToolUse hook
`.claude/hooks/agent_dispatch_guard.py` reads that status live and now permits the five
agents. The hook and its tests stay in place as a regression backstop — do not remove or
re-scope them without a G5 review. NOTE: dispatchability does not authorize new expansion
work; section 2 below still governs planning.

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
