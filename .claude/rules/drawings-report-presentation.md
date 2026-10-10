---
paths:
  - "services/api/app/drawings/**"
  - "services/api/app/cad/**"
  # The program's report generator lives in services/api/app/drawings/report/ (D-090 source-081,
  # 2026-10-10), covered by the line above; the web report preview is covered by frontend-web.md.
---
# Drawings, CAD sheets and report presentation — loads only when editing those paths

- Read `docs/design/ARCHITECT_PRESENTATION_CONTRACT.md` (sections 6 and 7) before changing a drawing, sheet or report.
- The report follows the contract's page types (change of 2026-10-10): four architect questions in order, evidence last;
  A4 only; no notes column; shared limitations once; 'Scheduled floor area: N sq ft; site fit unverified'; no developer words.
- Draw only from the canonical results and geometry contracts: no stand-in shape, never a stretched outline.
- Keep the current status meaning (screen: D-090 row R641; PDF: the six labels, rows R779 to R799). Presentation
  never raises a label or turns a withheld result into a number.
- Render the affected screen or PDF output and look at every view or page before a checkpoint.
- Record that evidence through the existing gate. No new skill, hook or watcher.
