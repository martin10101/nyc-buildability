# EXPANSION-AGENT HOLD NOTICE (owner directive 2026-07-17; G5 M0-T010)

This notice is deliberately unconditioned (no `paths:` frontmatter) so it attaches to every session:
it carries the still-active owner hold on expansion planning. (The 3D/UI *technical* rules are now
path-scoped in `.claude/rules/3d-ui-expansion.md`, loading only under `apps/web/**`.)

## 1. Dispatch-guard invariant (active)

Keep `.claude/hooks/agent_dispatch_guard.py` and its tests in place as a regression backstop; do not
remove or re-scope them without a G5 review. The five expansion agents (`3d-massing-engineer`,
`product-design-director`, `visual-quality-reviewer`, `financial-feasibility-engineer`,
`opportunity-search-engineer`) are dispatchable; dispatchability does not authorize expansion work —
§2 governs planning. Former dispatch-prohibition history:
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

### 2.2 Scoped release — proposal-editor planning + phase-B increments (owner directive D-076, 2026-09-19)

The owner released this hold for the PROPOSAL-EDITOR slice: (a) authoring the phased plan
`docs/PROPOSAL_EDITOR_PHASED_PLAN.md` and (b) contracting that plan's phase-B increments
(flat outline-walls-floors-heights editor over the existing scenario engine) under the
normal gated process, citing `D-076:D-076-R001/R002/R003`. Everything else in this section
still stands — the 19-task pack, the 9 contracts, GDS P1–P8, master-plan changes on the
pack's instruction, and 3D-massing/visual-scene work beyond phase B (which waits for the
plan's named owner-review checkpoint). Record: `project-control/directives/D-076-proposal-editor-planning/`.

### 2.1 Scoped release — lot-outline increment ONLY (owner directive D-040, 2026-09-12)

The owner released this hold for EXACTLY ONE increment: the address-flow lot-outline work
(address-entry design spec "Packet 3") — the MapPLUTO parcel-geometry connector plus
lot-outline rendering on the address confirm card, using MapLibre GL JS per the technical
rules in `.claude/rules/3d-ui-expansion.md`. That work may now be contracted and executed
under the normal gated process (ledger `M<x>-T<n>` IDs, citing
`D-040:D-040-R001`). **Everything else in this section remains SUSPENDED** — 3D massing,
the 19-task pack, the 9 contracts, GDS P1–P8, and any master-plan change on the pack's
instruction. Record: `project-control/directives/D-040-scoped-unblocks/`.

## 3. TASK-ID CONVENTION

Pack task IDs (`3D-xxx` / `UI-xxx` / `COMP-xxx`) are workstream labels only. Ledger tasks
use `M<milestone>-T<number>` (docs/PROJECT_CONTROL_PROTOCOL.md). Never create ledger tasks
under the pack scheme.
