---
name: architect-print-and-a11y-facts
description: Verified facts about what the architect property brief prints and which regions announce state (for ledger/print/a11y work on apps/web)
metadata:
  type: project
---

Verified at a57bb8de (2026-09-24), re-check before relying on them:

- ReportView's print lifecycle opens EVERY non-raw `<details>` inside `.architect-report` (nested ones too). Only `.architect-raw` (CapturedRecord) waits for the audit appendix. So ProvenanceDisclosure's nested "Full captured source record" JSON prints by default.
- Print CSS hides `.architect-topbar/.architect-nav/.architect-property-header/.architect-inspector` and buttons INSIDE `.architect-report` only. Scenario/evaluation failure cards on view=report sit outside the report, so they print (Retry button too).
- The brief mounts shared legacy primitives (FactsTable, ZoningSection, OpenIssues sections, CoverageLegend, ScenarioConstraints/Assumptions). "Legacy route" labels on those are wrong.
- Buttons that reveal content (e.g. MissingInputsSection "Show n more") mean that content is absent on paper.
- Architect workspace has no scenario announcer: scenario failures are silent. Only the property announcer and the rule-eval announcer exist there.
- The internal-build banner in the architect shell is inside a collapsed details that is display:none at <=700px and in print.

**Why:** M5-T080 G3/HJ reviews failed the ledger for print/a11y claims made without reading ReportView and architect.css.
**How to apply:** For any print or announcement claim, cite ReportView.tsx and architect.css lines. Do not infer print behaviour from the component name.
