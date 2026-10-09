---
paths:
  - "services/api/app/drawings/**"
  - "services/api/app/cad/**"
  # Add the server report template/export paths when a server report exists (today the report is the
  # web ReportView, covered by .claude/rules/frontend-web.md).
---
# Drawings, CAD sheets and report presentation — loads only when editing those paths

- Read `docs/design/ARCHITECT_PRESENTATION_CONTRACT.md` (sections 6 and 7) before changing a drawing, sheet or report.
- Draw only from the canonical results and geometry contracts: no stand-in shape, never a stretched outline.
- Keep the current status meaning (screen: D-090 row R641; PDF: the six labels, rows R779 to R799). Presentation
  never raises a label or turns a withheld result into a number.
- Render the affected screen or PDF output and look at every view or page before a checkpoint.
- Record that evidence through the existing gate. No new skill, hook or watcher.
