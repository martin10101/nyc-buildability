# D-090 source-079 (amendment): the design handoff for the architect-facing website and PDF (read it all, implement it, remake the test PDF)

Captured 2026-10-09 by the orchestrator (Claude Code session 013RaGmCmULdpmjCy58qBeMY, model claude-opus-5-5). A script copied the raw text from the saved session transcript under `~/.claude/projects/-root-project-nyc-buildability/`; nothing was retyped, and every quoted fragment below was cut out of the message by the script.

| What | Transcript | Line | Entry uuid | Timestamp | Stored as | Raw-text SHA-256 |
|---|---|---|---|---|---|---|
| the message | `f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7.jsonl` | 4480 | none | 2026-10-09T21:38:56.972Z | queue entry holding the typed text | `2ecba6a1d61e318cb2fb57877eea2fa7167ba5ec28b38d46db428c50dc43edc6` |
| the message | `f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7.jsonl` | 4482 | `326af07e-185f-49bf-9331-b1d0ad39aac2` | 2026-10-09T21:38:57.074Z | user line holding the message as delivered | `2ecba6a1d61e318cb2fb57877eea2fa7167ba5ec28b38d46db428c50dc43edc6` |

Context. The owner attached a design package (a zip of seventeen files) with one sentence. Its main file, CLAUDE_DESIGN_IMPLEMENTATION_BRIEF.md, is quoted whole below and governs the presentation work; its START_HERE.md asks that the brief be treated as the owner's instruction to improve both the website and the PDF through the existing workflow. At capture, wave 19 (tasks M5-T146 and M5-T147) was under correction after its walkthrough failed (the server builder running).

## Owner message (verbatim)

Transcript timestamp 2026-10-09T21:38:56.972Z. 209 characters; the digest is of the raw text.

> @"/root/.claude/uploads/f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7/86e0b80b-NYC_Buildability_Design_Handoff.zip" Open and read everything from a to z then implement it then remake the test pdf with the new approach 

## Attached brief (verbatim)

The owner's attached brief `CLAUDE_DESIGN_IMPLEMENTATION_BRIEF.md`, copied whole by the script from the unpacked package. The file's raw-text SHA-256 is `3faa7d1f9e1ea50d27421001b6dd4fb3c19a0c55f4b2955270333fbfb81949f1` (43128 characters).

- Package: `86e0b80b-NYC_Buildability_Design_Handoff.zip` as uploaded by the owner (759193 bytes, SHA-256 `5fbca7afc50eb387cae3f0cb9a4694f76752894b3ad2c883c3491f7b0d8be5a6`), unpacked unchanged into the session folder `/root/project/lanes-runtime/owner-docs/session-2026-10-09a/design-handoff/`. Its seventeen files, each read in full by the orchestrator on 2026-10-09:
- `CLAUDE_DESIGN_IMPLEMENTATION_BRIEF.md` (43286 bytes, SHA-256 `3faa7d1f9e1ea50d27421001b6dd4fb3c19a0c55f4b2955270333fbfb81949f1`)
- `START_HERE.md` (2941 bytes, SHA-256 `01e740a4eec51aaf8c5d8e30979ae9e8353d6026f424f12ecf07a8bd1a2a3481`)
- `evidence/Architect_Design_Reference.pdf` (110649 bytes, SHA-256 `73857cc39dfb25b54a2722a9fd8556e2516e0b12c7a7ca6454424a4b53fed126`)
- `evidence/VISUAL_REVIEW.md` (1504 bytes, SHA-256 `517ab1b0d5c7efeea1fb49a5a2713bb13e5cfa6cf84cc5579028112ea334bf3b`)
- `evidence/desktop-reference.png` (151028 bytes, SHA-256 `c98950009fa5574fdc6da4fd6412e1ed838eaaedf8ce55274f48072a2007521e`)
- `evidence/pdf-page-1.png` (114346 bytes, SHA-256 `838f9f297a205e996df209346654e21c2ad7eb87e9e67477681743e7da5bd5d9`)
- `evidence/pdf-page-2.png` (129324 bytes, SHA-256 `772f3d13ea3fb01b9d1655d9a670f7f65fb14eb225de1f7c0703289f1449e4ad`)
- `evidence/pdf-page-3.png` (149270 bytes, SHA-256 `470493aefaa44b4c2969d14a8017f9b4bbf564e3d0c01dab38c8a869a63bb2a9`)
- `evidence/pdf-validation.json` (2189 bytes, SHA-256 `8fcc8713cdbf3fcba548aad5f3b7f1f7004b53cd4beddea9ef1f2af1b01187ee`)
- `evidence/phone-reference.png` (145218 bytes, SHA-256 `8236c004fb2e938cc2c85bf62c1fda31e753dc5a50a1173d0cc2ed04621b6ff6`)
- `evidence/validation.json` (7984 bytes, SHA-256 `1ca843a38c591711e705e9deddbe0210fadb66d109246baca8b81cd0659f1022`)
- `manifest.json` (1743 bytes, SHA-256 `661d89adf7a586f0f2034d1e00f2491eebf38067f9c8ac2c3c7f97dd36586020`)
- `reference/reference.css` (15850 bytes, SHA-256 `cb7f8b26e881cf3563122d92c906ac8aee44188278e3e3ada56579309cd0d227`)
- `reference/reference.html` (10826 bytes, SHA-256 `e9c9bfe659b1fa432dd28da7bdc74806c2c7a25cd8fcfbe72ec92ab0c20abc6a`)
- `reference/reference.js` (3393 bytes, SHA-256 `ef0952e37fe3a1b828a56e6b5e023e398630a67ce8d8b8146be27abc9fca83ea`)
- `reference/validate-pdf.py` (2441 bytes, SHA-256 `1ba06adae038aab1b2115ac9e3d6e40ad6c8ae302ca1f0638e93129e3ac8f156`)
- `reference/validate-reference.cjs` (5168 bytes, SHA-256 `ed0a089bee5a1e5c2ec68af472ca62f403666be18cc779c0ae793ed12638ffa7`)

> # NYC Buildability: architect-facing website and PDF
>
> **Owner implementation directive · prepared 9 October 2026**
>
> Claude: read this entire brief, inspect the accompanying reference code and rendered examples, and implement the applicable work through the project's existing controlled workflow. Begin the work; do not respond with another general design proposal. Preserve the current product scope, calculation authority, security requirements and production activation holds.
>
> The objective is to save an architect time. The first screen and first report page must make the useful answer, its basis and its material limitations understandable quickly. The full evidence must remain available. A shorter-looking report is not a success if it hides an important condition, omits required scope, or presents an unsupported building as feasible.
>
> This is a concrete presentation contract and implementation assignment, not a request to copy a competitor's numbers or turn a three-page example into the entire product.
>
> ## 1. Start from the current program
>
> The supplied handoff and test PDF are snapshots. They are not proof that a capability is still missing. This brief was informed by all 88 pages of the competitor sample and all 17 pages of the test assembly, plus the repository's design instructions and relevant source files. Do not repeat the historical audit before doing useful work.
>
> Repository inspected: `martin10101/nyc-buildability`, integration branch `candidate/D-024-mrl-option-b`. A branch-head read during preparation returned `067592499551d5a3e26c2e1cd8cd8e8d17280257`. Individual file reads occurred during a moving branch and are not a frozen checkout audit. Recheck the active branch, current task, current owner directives and actual route wiring before editing. Never infer current completion from a stale handoff or component comment.
>
> Read the relevant parts of:
>
> - `CLAUDE.md`, `AGENTS.md`, and applicable `.claude/rules/`.
> - `docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`, especially the single-dashboard flow, three answers, drawings/report and label-on-the-box rules.
> - `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md`, including its supersession note and anti-clutter rules.
> - `docs/SESSION_HANDOFF.md` and the existing project-control state for the authorized task.
> - `docs/plans/FEASIBILITY_REPORT_SECTION_MAP_2026-10-06.md` and current report work orders.
> - The latest applicable owner directives. Newer owner decisions already supersede some older rules about draft output, professional review, estimates and local testing. Do not resurrect superseded restrictions.
>
> Use `/directive-compliance` and the existing task/gate process as required by this repository. Record this directive once and map its requirements to implementation evidence in the existing mechanism. Do not build a second governance system or a new collection of status documents.
>
> ### What needs correcting
>
> The sample's primary problem is information hierarchy. It puts implementation explanations, status definitions, repeated caveats and technical evidence in the architect's reading path. Typography, tables and pagination then make that hierarchy harder to scan. “Make it prettier” or “be concise” does not specify the remedy.
>
> Correct these mechanisms:
>
> | Observed pattern in the test assembly | Required presentation behavior |
> |---|---|
> | Pages 1–2 explain assembly, versions and internal state mapping before useful results | Lead with the property and the three answers. Put development status in the owner's progress report and source metadata in evidence. |
> | Pages 5–6 use long prose inside narrow table cells | Use concise metric rows. Put reason, effect and next requirement in a separate open-items table. |
> | Labels and explanations repeat across sections | State shared context once; retain a local exception only where it changes that result. |
> | A floor schedule can look like proof of a fitted building | Distinguish allowance, envelope and achieved option. Explicitly state when site fit is unverified. |
> | Eleven scenarios appear without eleven worked outcomes | Compare available results and mark unavailable outcomes honestly. Do not repeat a baseline number as though every option was evaluated. |
> | Tiny drawing notes and crowded dimensions | Reserve label space, recompose the drawing, or use a larger/detail sheet. Never solve overflow by shrinking meaning. |
> | QA records and developer backlog enter the client report | Keep build evidence in the existing developer workflow. Translate a missing capability into its effect on the architect's answer. |
>
> These are snapshot observations, not a claim that the current code still has every defect. Preserve fixes already made.
>
> ## 2. The architect's reading order
>
> Organize the experience around these questions, in this order:
>
> 1. **Which property and site selection am I reviewing?** Address, block/lot(s), district/overlay, selected lots and measurement basis.
> 2. **What is the floor-area allowance?** Program, allowance and the assumption that materially affects it.
> 3. **What is the permitted envelope?** Heights, setbacks, yards and coverage, with a drawing only where supported.
> 4. **What building option has actually been generated?** Achieved area, floor count, height, footprint and the binding constraint. Clearly distinguish an illustrative schedule from a fitted option.
> 5. **What changes between options?** Same site, assumptions and units; gains and trade-offs together.
> 6. **What needs resolving, and what would it change?** A short prioritized list.
> 7. **How was this derived?** Inputs, formula, source and rule applicability, available on demand and in the report evidence.
>
> The design target is that an unfamiliar architect can identify the property, main result and most important unresolved issue in about ten seconds. This is a usability target to test with a person, not a claim that screenshots prove comprehension.
>
> Do not set an arbitrary maximum page count for the complete report. Optimize the reading path: a useful first page, concise comparisons, repeatable scenario sheets, and navigable evidence. Useful material may require more pages; repetitive material does not.
>
> ## 3. Website composition
>
> Keep the existing **single dashboard with floating tools**. Do not introduce a new seven-page navigation system, move the user to another route just to inspect a map, or replace the app with this offline reference.
>
> ### Desktop
>
> - Keep property search and confirmed identity together. Use a compact header, not a marketing hero.
> - Keep the three answers together in the left results area. Give the selected map/diagram a coordinated right area. Start near a 44:56 split, with a 320 px minimum results column; adapt to the existing shell.
> - The active property, lot selection and scenario must remain apparent when a tool opens.
> - Use one strip with at most three short context items. Open shared notices and evidence from that strip.
> - Show at most three important notices at once; group additional notices behind a meaningful count. A condition that changes a number stays attached to that number.
> - Put detailed comparison, site facts, calculation evidence, report preview and map enlargement in the existing tool surfaces. Use one active modal/floating tool at a time; avoid stacked dialogs.
> - Keep A/B comparisons on the same site and measurement basis. Show differing assumptions explicitly. Changing an input must invalidate or refresh every dependent result and export.
> - Retain the owner's existing-building display preference. The visual layer may start hidden without changing whether an existing building is kept in the calculation. Never couple a display toggle to a legal calculation input.
> - Use the existing controlled availability of 3D and other features. Do not activate held functionality just to match a mockup.
>
> ### Tablet and phone
>
> - Below the width where both columns remain legible, stack results before the map/diagram. Use 1,000 px as a starting breakpoint, then validate actual content; do not use device names as a substitute for layout checks.
> - At 320–700 px, use one column with 16 px internal padding. Keep identity, the main answer and its exception above secondary tools.
> - Never hide a material limitation because the screen is narrow.
> - Comparisons may become stacked option summaries with a detailed table behind them. Keep identical row order, names and units. If a genuinely two-dimensional data table must scroll, confine scrolling to a labeled region; ordinary text must reflow.
> - Long addresses wrap. Important values and labels do not ellipsize. Menus, toolbars and buttons wrap or reorganize without covering content.
> - Editing assumptions uses labeled numeric inputs with units, bounds and reset. A slider, if useful, supplements the input; it does not replace it.
> - Focus moves into an opened tool, stays within a modal, closes on Escape, and returns to its opener. Background content must not remain operable through a modal.
>
> The supplied HTML demonstrates content hierarchy, responsive sizing, a comparison and a drawing dialog. Its anchor links stand in for the production dashboard's existing floating tools. Do not copy its continuous three-sheet screen layout as the application's navigation.
>
> ## 4. Writing and disclosure rules
>
> For each result, use this order: **label → value and unit, or unavailable state → material exception → details action**.
>
> Use these editorial budgets as defaults, not as truncation rules:
>
> | Element | Working budget |
> |---|---|
> | Metric label | 2–6 plain words; usually one line, sometimes two |
> | Local exception | One sentence, normally no more than 18 words |
> | Option summary | 3–5 comparable metrics, one advantage, one limitation |
> | Decision-summary paragraph | Up to 45 words |
> | Open-item row | Issue, effect and needed next; normally one short sentence in each cell |
> | Deeper explanation | Conclusion first; then necessary support, formula and source |
>
> If a complete explanation will not fit, move its supporting detail to the evidence surface and retain the qualifying fact beside the result. Never cut off the qualification itself.
>
> Examples:
>
> - Main row: **Legal dwelling-unit limit: Not available.** Local reason: **Density-area applicability is unresolved.** Details explain what evidence is missing and which rule it affects.
> - Main row: **Building option: Site fit not verified.** Details: the schedule has three floors, but the rear yard and placement have not been established.
> - Input conflict: **Lot area differs by source.** Show the two values and their sources together. Explain which calculation uses which basis.
>
> Avoid “the system has not yet implemented the functionality necessary to…” in user-facing copy. Prefer “Setback calculation is not available” and explain its effect. Do not make the architect responsible for developer work: “complete the calculation” belongs to the team; “provide a survey” may be a property-information requirement.
>
> Keep implementation identifiers, merge status, routes, contract versions, task numbers and test outcomes out of the architect's main view and client report. Technical IDs can remain in a compact diagnostic/evidence export where useful for support.
>
> ### Status meaning is not a styling decision
>
> The supplied PDF describes six owner labels: Verified, Provisional, Illustrative, Conditional, Pending verification and Unresolved. It also states that its mapping is provisional and that owner question C1 remains open. Older design documents use different language.
>
> Find the latest owner decision and canonical mapping before modifying labels. Preserve the existing data distinctions and any owner-approved wording. Use a compact label, a relevant symbol where useful and a short reason; color is secondary. “Verified” is never a synonym for “merged,” “arithmetic matches,” or “a source link exists.” Do not relabel a withheld value as conditional in order to show it. Conversely, do not hide a permitted preliminary result because an obsolete document required a professional sign-off.
>
> If C1 or a material mapping question is still unanswered, append it to the **existing active owner questionnaire**. Continue layout and other unblocked work using current authorized behavior. Do not invent the answer.
>
> ## 5. Visual specifications
>
> These are proposed project design choices, not rules imposed by an external standard. Reconcile them with any newer approved branding. Use a single shared token source and component styles; do not scatter magic numbers through TSX, SVG and PDF templates.
>
> ### Typography
>
> Use one legible sans-serif family for product UI and report body. Prefer the existing licensed, bundled font if it works at the required sizes. The reference uses `Arial, Helvetica, sans-serif` to avoid a network font dependency. If standardizing on an open-source family such as Inter, bundle approved font files, embed the PDF font and test with those exact files. Do not add decorative calligraphy. Monospace is for code/identifiers when actually needed, not every number and label.
>
> | Role | Screen | Printed A4/Letter |
> |---|---|---|
> | Property title | 28–30 px; 1.2 line height; 700 | 22–23 pt |
> | Headline value | 36–44 px; 1.1; 700 | 28–32 pt |
> | Section title | 18–20 px; 1.3; 600/700 | 12–14 pt |
> | Body | 16 px; 1.45–1.55 | 10.5–11 pt; 1.35–1.45 |
> | Compact result/table text | 14–15 px; at least 1.35 | 9.5–10 pt |
> | Source note / footer | 13–14 px | 8.5–9 pt; never for the main conclusion |
> | Drawing labels at final displayed size | At least 14 px | At least 8.5 pt; prefer 9.5 pt |
>
> Use tabular numerals and right alignment for numerical columns. Align text and explanatory headers left. Put units in the header or beside the value consistently. Show `20,150 sq ft`, not `20150.000000 SF`. Keep full precision internally; display rounding must not drive calculation. Identify derived estimates as estimates and retain their assumptions.
>
> ### Geometry of the layout
>
> - Spacing scale: **4, 8, 12, 16, 24, 32, 48 px**.
> - Desktop shell maximum width: approximately **1,360 px**; outer padding 28–32 px. Use additional width for the drawing when the actual product needs it.
> - Panel padding: 24–32 px desktop, 16–20 px mobile. Desktop column gap: 24–32 px.
> - Control height: **44 px** minimum as the project target. Inline links inside text follow accessible text-link conventions.
> - Control radius: **6 px**; major panel radius: 8 px. Borders normally 1 px. Use dividers instead of a box around every sentence.
> - Reserve strong shadows for overlays; ordinary report/table content needs no shadow.
> - Body line length: roughly 55–80 characters where practical. Dense evidence tables can use wider layouts, with deliberate column widths.
> - Use natural height for variable text. No fixed-height text cards, absolute positioning of paragraphs, `overflow:hidden` to conceal problems, or forced line breaks just to fit one address.
>
> ### Palette
>
> | Role | Reference token |
> |---|---|
> | Main ink | `#182B3A` |
> | Supporting text | `#52616C` |
> | Action / selection | `#18577A` |
> | Page background | `#F2F5F6` |
> | Content surface | `#FFFFFF` |
> | Quiet divider | `#D8E0E5` |
> | Selected/context surface | `#EEF4F7` |
> | Caution text / surface | `#795318` / `#FBF4E7` |
>
> Check actual foreground/background combinations; a token list alone does not prove contrast. Aim for WCAG 2.2 AA: 4.5:1 for ordinary text, 3:1 for qualifying large text, and the relevant 3:1 requirements for essential non-text boundaries. Quiet dividers are not substitutes for visible interactive-control boundaries. Show a visible keyboard focus indicator. Respect reduced motion.
>
> ## 6. Charts, drawings, maps and photography
>
> Choose a visual because it answers a spatial or numerical question. Do not add decoration to fill a page.
>
> ### Numerical comparisons
>
> - Use aligned tables for precise multi-metric comparison; horizontal bars for a small set of comparable quantities; a floor stack for floor-by-floor relationships.
> - Bars start at zero and use the same scale for competing options. Put units and direct values on the chart. Do not compare gross building area with zoning floor area as though they were the same quantity.
> - Allowance and achieved area must have distinct labels and visual treatments. Unknown is not a zero-height bar. “Not applicable” is not “not assessed.”
> - Use a range only where the underlying result is a range. State the assumption behind an estimate.
> - Never use 3D bar charts, gauges for legal certainty, unexplained radar scores, decorative pie charts or a “confidence percentage” invented by the UI.
> - A chart cannot be the only way to obtain essential values. Provide the equivalent table or text.
> - Short sentence-case title, horizontal labels and restrained gridlines. Drawings use a generated legend containing only items actually present.
>
> ### Spatial drawings
>
> Use the existing server drawing kit and geometry contracts. The screen and PDF should embed the same canonical SVG drawing or reproduce it from the same validated geometry and style table. DXF retains the same geometry and dimensional basis. Do not trace a picture or create a pleasant rectangle that substitutes for the actual lot.
>
> The floor-stack graphic in the supplied reference is deliberately **unscaled horizontally** and explicitly illustrative. It only depicts the sample's reported three ten-foot floors. It must never be used as the site's footprint, permitted envelope or proof of site fit.
>
> For actual site plans, provide: selected lot outline, adjoining context needed for interpretation, street names/widths, north arrow, real scale bar, dimensions, yards/setbacks and a compact legend. Include source, date and measurement basis. If context is missing, state that limitation instead of presenting an isolated polygon as a complete location map.
>
> For actual sections, show ground/reference plane, floor elevations, base height, maximum height and relevant setbacks. Separate legal limits from the selected building. For massing, use a consistent axonometric camera, shared scale across option comparisons and restrained use colors. Derive each plate and its height from the result, not a generic building model.
>
> Line-weight starting points at final print size: context 0.25–0.35 pt; secondary geometry 0.5 pt; primary lot/building outline 0.9–1.2 pt; important cut/ground line 1.2–1.5 pt. Preserve hierarchy in monochrome. Use hatching as well as fill color for yards, exclusions and other critical distinctions.
>
> Label placement is a layout algorithm, not wishful SVG text:
>
> 1. Measure label bounds using the actual font and final display scale.
> 2. Reserve a label gutter and dimension lanes outside geometry.
> 3. Test candidate label positions against other labels, the drawing frame and protected geometry.
> 4. Move the label with a leader when needed; prefer short labels and a keyed detail table.
> 5. If collisions remain, create a detail view or a larger drawing sheet. Fail the visual check rather than shrinking labels below the minimum or suppressing dimensions silently.
>
> Coordinate-system labels must describe the actual data. Do not label local drawing feet as EPSG:2263 without the documented transform. Never stretch the tax-map outline to match a recorded lot area. Preserve both sources and explain the chosen calculation basis.
>
> ### Photography
>
> Use actual, licensed site/aerial/street imagery only when it helps the architect understand access, context or surroundings. Include source/date and mark the subject property. Prefer one useful contextual image over a collage. Do not use stock buildings, AI-generated streets or photorealistic proposed façades in a zoning feasibility report: they imply facts or design work that the program has not established. No photographs are needed in the numerical summary when a precise diagram is more useful.
>
> ## 7. PDF architecture and pagination
>
> Use the same result revision, scenario identity, source basis, presentation vocabulary and diagram assets as the website. PDF is a deliberately composed document, not a screenshot of the dashboard and not a dump of every component's expanded state.
>
> Default to A4 portrait with **14 mm margins**. If Letter is offered, explicitly compose and test it; do not rely on a printer's “fit” option. Use landscape/detail sheets when an actual drawing or comparison needs them.
>
> | Section | Reader purpose | Composition |
> |---|---|---|
> | Decision brief | Understand the property and answer immediately | Identity, three answers, one useful visual, most important open items; no empty ceremonial cover |
> | Site and context | Understand the actual parcel and constraints | Location/zoning context and dimensioned site plan, with legible legends |
> | Option comparison | See differences quickly | Same metrics and basis across options; qualifying conditions and unavailable results explicit |
> | Scenario sheet(s) | Understand one supported option | Plan/section/massing, achieved vs allowed area, floor schedule and binding constraints |
> | Calculation/evidence | Reproduce and inspect the result | Inputs, formula, rule applicability, compact source references and provenance |
> | Assumptions/open items | Know what can change the conclusion | Group shared assumptions once; identify effect and required next input/check |
>
> Follow the full existing report section map. Do not remove an entire promised section merely because it is currently unsupported: show its concise unavailable state or include it in the coverage inventory, with its material effect visible in the summary when necessary. Avoid a mostly blank page for every missing calculation.
>
> Use running property/scenario identity, actual page numbers, bookmarks and useful internal cross-references. Keep the overall preliminary label compact. Preserve any latest required notice wording; consolidate standing notices according to the current owner directive rather than repeating a legal paragraph beside every value.
>
> Repeat table headers after a page break. Keep headings with the first content row and captions with their figure. A normal row should not split; a row longer than one page needs a different content structure. Avoid both isolated headings and enormous blank areas caused by applying `break-inside:avoid` to an entire long section.
>
> Reserve header/footer space in the page template. Do not position a footer over flowing content. Use the chosen converter's running page furniture for production, not the prototype's simple fixed-length sheet footer. Do not impose the prototype's three-page count on dynamic reports.
>
> Keep text selectable, fonts embedded and diagrams vector where possible. Do not rasterize the whole page to disguise layout problems. Generate accessible structure where the converter supports it, and test reading order; “tagged PDF” is not by itself proof of PDF accessibility.
>
> The reference initially produced five pages because two sections overflowed. Its final version uses three pages after spacing was corrected without reducing the type scale. Production acceptance must catch this class of defect with long and partial-data reports too.
>
> ## 8. Implementation locations and shared model
>
> Trace the current production/preview entry points first. The following locations were present when this brief was prepared; inspect current ownership before changing them.
>
> | Responsibility | Existing places to inspect |
> |---|---|
> | Shared design tokens | `apps/web/src/app/globals.css` |
> | Dashboard composition and floating tools | `apps/web/src/components/architect/workspace/DashboardEntry.tsx`, `DashboardPanels.tsx`, `DashboardTools.tsx`, `FloatingWorkspaceWindow.tsx`; `apps/web/src/app/dashboard/dashboard.css` |
> | Results wiring and views | `apps/web/src/components/architect/ResultsPanel.tsx`, `results-panel.css`, `answers/ThreeAnswersPanel.tsx`, `AnswerCard.tsx`, `ResultsStatusStrip.tsx`, `ScopeSummary.tsx`, `three-answers.css` |
> | Report and evidence presentation | `apps/web/src/components/architect/ReportView.tsx`, `ReportSources.tsx`, `CalculationEvidence.tsx`, `EvidenceInspector.tsx` |
> | Contract and presentation adapters | `packages/contracts/**`, `apps/web/src/lib/results-api.ts`, `results-contract-checks.ts`, `apps/web/src/lib/architect/three-answers.ts` |
> | Geometry and drawing kit | `services/api/app/drawings/kit/` including `model.py`, `styles.py`, `labels.py`, `sheet.py`, `site_plan.py`, `massing.py`, `svg.py` |
> | Context maps and existing PDF sheet | `services/api/app/drawings/maps/`, `services/api/app/cad/pdf_sheet_writer.py` |
> | Existing UI checks | `apps/web/e2e/results.spec.ts`, `results.flag-on.spec.ts`, `apps/web/src/test-support/results-fixtures.ts`, existing Playwright config |
>
> Find the actual report assembly path and converter; this list is not a declaration that `ReportView.tsx` already produces the server PDF. Do not create a competing exporter merely because it is easy to print the prototype.
>
> Keep one canonical calculation result. Add a thin presentation adapter only where needed. It may format numbers and group reasons, but it must not decide law, recalculate zoning in JSX or invent missing geometry.
>
> Conceptual requirements for that adapter, mapped onto existing types rather than a new competing schema:
>
> ```ts
> // Sketch of presentation concerns, not a replacement for packages/contracts.
> type PresentedMetric = {
>   id: string;
>   label: string;
>   display: string;            // Formatted value + unit, or authorized unavailable text.
>   resultKind: "allowance" | "envelope" | "achieved" | "estimate";
>   statusLabel: string;        // From the current canonical mapping; never inferred by CSS.
>   localException?: string;
>   evidenceKey: string;
>   resultRevision: string;
> };
> ```
>
> Distinguish `0`, missing, not applicable, not assessed, failed check and unavailable. Never use `value || 0`. Keep measured/source-backed, assumed and calculated values distinguishable. Store scenario objective, program and assumptions with the scenario. Screen and export must use the same revision; prevent stale export when property/scenario inputs change.
>
> The reference package contains working `reference.html`, `reference.css`, `reference.js` and `validate-reference.cjs`. Read and adapt their layout patterns; do not import the sample constants into production. Its JavaScript deliberately performs only demonstration rendering. Production numbers and labels must come from the current contracts.
>
> Consolidate shared type, spacing, color and status tokens. If Python and CSS need separate generated token files, generate them from one small neutral source and check their parity. Do not introduce a framework, chart library, PDF converter or font service without a concrete need and the existing dependency/security approval process. Prefer the installed stack.
>
> ## 9. Work sequence
>
> 1. **Reconcile and preserve:** identify active route/export paths, latest status mapping, current authorized work and the existing owner questionnaire. Save the canonical design contract and compact instruction pointers described below. Carry forward existing fixes.
> 2. **Establish shared presentation:** tokens, metric formatting, status/reason presentation, result identity and provenance hooks. Keep computation untouched unless a separately authorized correctness fix is needed.
> 3. **Finish one complete website slice:** real property → three answers → details → one comparison → actual data states, including a partial-data case. Inspect desktop and phone renders. Do not stop at disconnected components.
> 4. **Finish the corresponding PDF slice:** same data revision and SVGs, clean page one, comparison, scenario/detail and evidence treatment. Generate and visually inspect every page.
> 5. **Apply the same system to remaining supported report sections and website tools:** use the existing full-scope section map. Do not expand unrelated product features or abandon unfinished promised scope.
> 6. **Run bounded acceptance and independent review:** reuse existing tests and gates, fix concrete findings, and retain evidence for the reviewed revision. Respect the current local-test and CI policy; do not copy an obsolete blanket ban from an old plan.
> 7. **Record the exact next step and deliver the actual outputs:** website route or preview, exported PDF, screenshots, changed files and remaining issues. “Components implemented” is not “the architect can use it.”
>
> Do not spend a session creating a large design-document bureaucracy. Make the required persistence changes, implement the first visible slice, and show the result. Continue through the remaining authorized work.
>
> ## 10. Persist the design across sessions
>
> Use version-controlled repository files as the durable source. Conversation history and automatic memory may assist, but they are not the presentation contract.
>
> ### Canonical placement
>
> Save the adopted contract at `docs/design/ARCHITECT_PRESENTATION_CONTRACT.md`. The owner may give you this file under a different filename; preserve its origin and adoption date. Incorporate later approved changes there rather than creating `v2`, `final-final` and competing policies.
>
> Update the active routing in `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md` and `.claude/rules/frontend-web.md` to reference the contract. Set aside conflicting older presentation sections with precise pointers; preserve historical files in accordance with repository rules. Do not silently delete product requirements or change the single-dashboard plan.
>
> Add a short pointer in `CLAUDE.md`, for example:
>
> > For architect-facing website, report, drawing or PDF work, read `docs/design/ARCHITECT_PRESENTATION_CONTRACT.md` before implementation. Use the current result/status contracts and existing acceptance gates. Carry the contract version, evidence path, unresolved question IDs and next visible action into the normal session handoff.
>
> Do not paste this entire brief into `CLAUDE.md` or import every historical design document into every session. Keep the always-loaded instruction short; read detail on demand.
>
> Extend the existing frontend rule with the same routing. For backend report/drawing paths, extend the relevant existing rule or add one small path-scoped rule if no suitable rule exists. Example routing file:
>
> ```yaml
> ---
> paths:
>   - "services/api/app/drawings/**"
>   - "services/api/app/cad/**"
>   # Add the actual report template/export paths after tracing the current implementation.
> ---
> ```
>
> The rule body should say: read the presentation contract; use canonical results/geometry; preserve current status meaning; render and inspect affected screen/PDF output; record evidence through the existing gate. Keep it short. Do not create a new skill, hook, watcher or enforcement daemon for this.
>
> In the normal `docs/SESSION_HANDOFF.md` update, add a compact design entry containing:
>
> - Adopted contract path and git revision.
> - Last implemented and visually checked surface/export, with evidence paths and exact revision.
> - Remaining acceptance failures or checks not run.
> - Active owner-questionnaire path and unresolved question IDs.
> - The next concrete visible action, including any hold that actually applies.
>
> Use the existing ledger for task state. Do not duplicate status in another design ledger. Ensure the receiving session/worktree has the commit containing these pointers; a handoff on an unmerged branch must name that branch explicitly. At the start of a fresh session, confirm the contract and relevant scoped rule are available before resuming. Loading instructions into context is helpful, but tests and review provide the implementation evidence.
>
> ## 11. Questions: use the existing MD questionnaire
>
> Find the **active owner questionnaire already used by this program**, including the C1 reference from the sample. It may be in the current session's owner-documents directory rather than the committed repository. Inspect current handoff/directive references and existing questionnaire files before creating anything.
>
> `docs/ARCHITECT_REVIEW_QUESTIONS.md` is an existing running architect/professional question list with a product-validation section. It is not automatically the same as the owner's current MD questionnaire. Use it for its established purpose; do not redirect owner implementation decisions there by assumption. Do not revive its older professional-review blocking language where later directives supersede it.
>
> Append material questions to the correct existing file and preserve numbering, answered decisions and links. If the active questionnaire cannot be located, report that specific missing path and continue unblocked implementation; do not create a competing questionnaire silently.
>
> Use the established format, or add this compact structure within it:
>
> ```md
> ### [existing sequence] Short decision question
> Status: Open
> Why this matters: [one sentence about the architect's result or workflow]
> Existing decision checked: [reference, or none found]
> A. [option and consequence]
> B. [option and consequence]
> Recommendation: [choice and reason]
> Blocks: [specific component/behavior, or nothing]
> Safe work continuing: [specific work]
> Owner answer: [leave blank]
> Implementation/evidence link: [fill after the answer is implemented]
> ```
>
> Ask only when the answer affects meaning, scope or a genuine product choice. Do not ask the owner to choose every margin, border or font weight. Do not re-ask settled decisions. Likely matters to check against existing answers include the six-label mapping, the primary optimization objective, approved print sizes, and any actual conflict between the report scope and current owner intent. A developer's unfinished calculation is a task, not a question the architect must answer.
>
> ## 12. Acceptance contract: evidence, not self-certification
>
> Use these IDs in the existing directive/evidence process. Report each as **PASS, FAIL, NOT RUN or NOT APPLICABLE with a reason**. A screenshot alone does not establish correctness; a passing unit test does not establish visual quality.
>
> | ID | Acceptance requirement | Required evidence |
> |---|---|---|
> | UX-01 | Property, site selection, program and result scope are identifiable immediately | Desktop and phone captures; human walkthrough observations |
> | UX-02 | Allowance, envelope and achieved option are distinguishable; estimates remain separate | Populated and partial-data cases, screenshot plus semantic assertion |
> | UX-03 | No result is promoted from unknown/withheld to a number or from draft to verified by presentation | State tests using canonical contracts and current mapping |
> | UX-04 | Shared notices appear once; material local exceptions remain visible | Disclosure inventory and review of each affected surface |
> | UX-05 | Screen, comparison, drawings and PDF use matching property/scenario/revision/basis | Cross-output identity and value checks; stale-response scenario |
> | UX-06 | A/B comparisons use consistent units and site assumptions, with differences explicit | At least two genuinely different supported scenarios; unresolved case |
> | UX-07 | No clipped text, unintended horizontal page scrolling, overlapping labels or obscured controls | Captures and DOM checks at 320, 390, 768, 1,024, 1,440 and 1,920 px |
> | UX-08 | Long labels, long addresses, large/small values and text expansion remain readable | Stress fixtures, 200% zoom and text-spacing checks |
> | UX-09 | Keyboard, focus, modal return, accessible names, status announcements and contrast work | Actual keyboard walkthrough; targeted automated accessibility checks; manual findings |
> | UX-10 | Drawings match real geometry and metrics; labels remain legible at final output size | Canonical geometry/metric comparison, collision checks, visual inspection |
> | UX-11 | Every generated PDF page is readable and correctly paginated | Rendered page images; page-by-page review; font, boundary and content checks |
> | UX-12 | Full required report scope is retained with honest availability | Section inventory mapped to current report section map |
> | UX-13 | No development log, raw error, task ID or internal schema jargon appears in ordinary architect content | Content review of populated, loading, empty, partial and error states |
> | UX-14 | Conditional gains and unavailable alternatives are not represented as computed feasible outcomes | Comparison fixtures and independent review of meaning |
> | UX-15 | A fresh session finds the adopted design and resumes the right work | Committed routing/contract, handoff entry and receiving-session orientation check |
> | UX-16 | Final claims match actual completion and existing gates | Evidence on the reviewed revision; independent review; remaining failures explicit |
>
> Minimum meaningful state coverage:
>
> - Normal supported result; currently incomplete benchmark result.
> - No geometry; conflicting site areas; unknown street width; unresolved eligibility.
> - Existing building retained but existing **zoning** floor area missing. City-recorded gross area is not a substitute.
> - Exact zero vs unavailable; very large numbers; long names and multiple lots.
> - Optional add-on off/on, an approval-dependent option, and a combination where gains overlap.
> - Failed fetch, partial fetch, changed property during a request and stale result/export prevention.
> - A short report and a long report with repeated headers and multiple scenario sheets.
>
> Use independently established expected values for correctness tests, including existing reviewed reference cases. Do not “prove” correctness by asserting that two copies of the same incorrect fixture match. Screenshot baselines must be visually reviewed before approval; never update every baseline simply to make the test pass.
>
> For PDFs, render **every page**, including appendices. Check at normal reading size and in grayscale. Confirm text is selectable, sources readable, page numbers correct, and tables/drawings agree. Inspect extracted text and font sizes as supporting checks, not a replacement for viewing the pages. Do not silently scale the whole report to fit.
>
> Respect existing producer/reviewer separation. Use the established independent visual-quality and human-journey review process; do not introduce extra agent orchestration or claim that the producing agent's own checklist is independent review. Run expensive suites in the currently authorized environment and only as required by the gate or a concrete remaining risk.
>
> ### What was actually checked in this reference package
>
> The supplied reference was rendered in Chromium. The included script checks six viewport widths, drawing-label size, the enlarge dialog, Escape and focus return, the comparison link, a long-address case and browser errors. The exported PDF was rendered and visually reviewed page by page. `evidence/validation.json` records the script's scope and results; `evidence/pdf-validation.json` records additional print checks.
>
> These are checks of the **standalone reference**, not the production application. They do not establish zoning correctness, full accessibility conformance, real-user comprehension, production API wiring or the production PDF converter. The actual implementation must satisfy the acceptance contract on its own outputs.
>
> ## 13. What to return to the owner
>
> Return a concise update with links:
>
> 1. What is now usable: the real route/preview and a newly generated PDF from the same result revision.
> 2. Desktop and phone screenshots, plus representative PDF pages and the location of the complete page-by-page evidence.
> 3. Acceptance results and independent review outcome, with failures and not-run checks explicit.
> 4. Remaining decision questions in the existing questionnaire, and the next visible action.
>
> Do not say “perfect,” “fully verified,” “complete” or “production ready” because the CSS looks good or a test runner is green. State what was implemented and what the evidence supports. A prompt cannot guarantee excellent design; a clear contract, rendered outputs, corrections and an architect walkthrough can establish whether this implementation meets the goal.
>
> ## 14. Research and optional skills
>
> Research checked 9 October 2026. The detailed measurements above are design recommendations for this project. The sources below inform the workflow; they do not certify this design.
>
> - **Anthropic frontend-design:** official skill for intentional frontend composition. Useful as a supporting design skill when available. The project contract, architectural workflow and current owner decisions take precedence over generic aesthetic advice. Do not install a new plugin solely to begin this work. [Official skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md).
> - **Anthropic webapp-testing:** supports using Playwright to inspect interactions, screenshots and browser logs. The repository already has Playwright and an acceptance process; use those first. [Official skill](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md).
> - **Claude Code memory/rules:** project instructions and path-scoped rules provide durable routing across sessions. Keep the always-loaded layer concise and the detailed contract in a referenced file. These instructions are context, not an automatic proof of compliance. [Memory and rules](https://code.claude.com/docs/en/memory), [skills](https://code.claude.com/docs/en/skills).
> - **W3C WCAG 2.2:** accessibility criteria for contrast, reflow, focus, names and targets. The 44 px project target is a design choice exceeding the general 24 px AA minimum target criterion; it is not a quotation of that criterion. [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).
> - **Office for National Statistics:** clear hierarchy, horizontal chart text and consistent numerical scales. The project uses those principles with its own visual tokens. [Chart typography](https://service-manual.ons.gov.uk/data-visualisation/build-specifications/typography), [axes and gridlines](https://service-manual.ons.gov.uk/data-visualisation/guidance/axes-and-gridlines), [chart text](https://service-manual.ons.gov.uk/data-visualisation/guidance/chart-text).
> - **Playwright:** screenshot comparisons detect changes relative to reviewed baselines; stable browser/font/environment matters. A baseline is not inherently a good design. [Visual comparisons](https://playwright.dev/docs/test-snapshots).
> - **AIA:** site plans, sections, overall dimensions and illustrative views are familiar architectural communication forms. This product remains a zoning feasibility tool; that does not authorize detailed apartment planning or construction documents. [Architect's basic services](https://www.aia.org/resource-center/defining-the-architects-basic-services).
>
> No authoritative skill found in this research can guarantee an architect-ready zoning UI. Use the official general-purpose design/testing skills if helpful, with the specific contract and actual validation above. Do not make unsupported claims about specialized skill quality or install third-party collections without the existing review process.

## Reading

| Words of the message | Requirement |
|---|---|
| "@"/root/.claude/uploads/f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7/86e0b80b-NYC_Buildability_Design_Handoff.zip" Open and read everything from a to z then implement it then remake the test pdf with the new approach" | R800 (obligation) |
| "@"/root/.claude/uploads/f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7/86e0b80b-NYC_Buildability_Design_Handoff.zip" Open and read everything from a to z then implement it then remake the test pdf with the new approach" | R801 (obligation) |
| "@"/root/.claude/uploads/f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7/86e0b80b-NYC_Buildability_Design_Handoff.zip" Open and read everything from a to z then implement it then remake the test pdf with the new approach" | R802 (obligation) |
| "Claude: read this entire brief, inspect the accompanying reference code and rendered examples, and implement the applicable work through the project's existing controlled workflow." "Begin the work; do not respond with another general design proposal." | R803 (obligation) |
| "Preserve the current product scope, calculation authority, security requirements and production activation holds." | R804 (prohibition) |
| "The objective is to save an architect time." "The full evidence must remain available." "A shorter-looking report is not a success if it hides an important condition, omits required scope, or presents an unsupported building as feasible." | R805 (obligation) |
| "This is a concrete presentation contract and implementation assignment, not a request to copy a competitor's numbers or turn a three-page example into the entire product." | R806 (prohibition) |
| "Recheck the active branch, current task, current owner directives and actual route wiring before editing." "Never infer current completion from a stale handoff or component comment." "Preserve fixes already made." | R807 (obligation) |
| "Record this directive once and map its requirements to implementation evidence in the existing mechanism." "Do not build a second governance system or a new collection of status documents." | R808 (obligation) |
| "| Pages 1–2 explain assembly, versions and internal state mapping before useful results | Lead with the property and the three answers." | R809 (obligation) |
| "| Pages 5–6 use long prose inside narrow table cells | Use concise metric rows." | R810 (obligation) |
| "| Labels and explanations repeat across sections | State shared context once; retain a local exception only where it changes that result. |" | R811 (obligation) |
| "| A floor schedule can look like proof of a fitted building | Distinguish allowance, envelope and achieved option." | R812 (obligation) |
| "| Eleven scenarios appear without eleven worked outcomes | Compare available results and mark unavailable outcomes honestly." | R813 (obligation) |
| "| Tiny drawing notes and crowded dimensions | Reserve label space, recompose the drawing, or use a larger/detail sheet." | R814 (obligation) |
| "| QA records and developer backlog enter the client report | Keep build evidence in the existing developer workflow." | R815 (prohibition) |
| "Organize the experience around these questions, in this order:" "1. **Which property and site selection am I reviewing?** Address, block/lot(s), district/overlay, selected lots and measurement basis." "2. **What is the floor-area allowance?** Program, allowance and the assumption that materially affects it." "3. **What is the permitted envelope?** Heights, setbacks, yards and coverage, with a drawing only where supported." "4. **What building option has actually been generated?** Achieved area, floor count, height, footprint and the binding constraint." "5. **What changes between options?** Same site, assumptions and units; gains and trade-offs together." "6. **What needs resolving, and what would it change?** A short prioritized list." "7. **How was this derived?** Inputs, formula, source and rule applicability, available on demand and in the report evidence." | R816 (obligation) |
| "The design target is that an unfamiliar architect can identify the property, main result and most important unresolved issue in about ten seconds." | R817 (evidence) |
| "Do not set an arbitrary maximum page count for the complete report." | R818 (prohibition) |
| "Do not introduce a new seven-page navigation system, move the user to another route just to inspect a map, or replace the app with this offline reference." | R819 (prohibition) |
| "Keep property search and confirmed identity together." "Keep the three answers together in the left results area." "The active property, lot selection and scenario must remain apparent when a tool opens." | R820 (obligation) |
| "Use one strip with at most three short context items." "Show at most three important notices at once; group additional notices behind a meaningful count." | R821 (obligation) |
| "Put detailed comparison, site facts, calculation evidence, report preview and map enlargement in the existing tool surfaces." | R822 (obligation) |
| "Keep A/B comparisons on the same site and measurement basis." "Changing an input must invalidate or refresh every dependent result and export." | R823 (obligation) |
| "Never couple a display toggle to a legal calculation input." | R824 (prohibition) |
| "Do not activate held functionality just to match a mockup." | R825 (hold) |
| "Below the width where both columns remain legible, stack results before the map/diagram." "At 320–700 px, use one column with 16 px internal padding." "Never hide a material limitation because the screen is narrow." | R826 (obligation) |
| "Comparisons may become stacked option summaries with a detailed table behind them." "Long addresses wrap." "Editing assumptions uses labeled numeric inputs with units, bounds and reset." | R827 (obligation) |
| "Focus moves into an opened tool, stays within a modal, closes on Escape, and returns to its opener." | R828 (obligation) |
| "Do not copy its continuous three-sheet screen layout as the application's navigation." | R829 (prohibition) |
| "For each result, use this order: **label → value and unit, or unavailable state → material exception → details action**." "Use these editorial budgets as defaults, not as truncation rules:" "Never cut off the qualification itself." | R830 (obligation) |
| "Avoid “the system has not yet implemented the functionality necessary to…” in user-facing copy." "Do not make the architect responsible for developer work: “complete the calculation” belongs to the team; “provide a survey” may be a property-information requirement." | R831 (obligation) |
| "Keep implementation identifiers, merge status, routes, contract versions, task numbers and test outcomes out of the architect's main view and client report." | R832 (prohibition) |
| "Find the latest owner decision and canonical mapping before modifying labels." "Use a compact label, a relevant symbol where useful and a short reason; color is secondary. “Verified” is never a synonym for “merged,” “arithmetic matches,” or “a source link exists.” Do not relabel a withheld value as conditional in order to show it." "Use a compact label, a relevant symbol where useful and a short reason; color is secondary. “Verified” is never a synonym for “merged,” “arithmetic matches,” or “a source link exists.” Do not relabel a withheld value as conditional in order to show it." | R833 (obligation) |
| "If C1 or a material mapping question is still unanswered, append it to the **existing active owner questionnaire**." | R834 (obligation) |
| "Use one legible sans-serif family for product UI and report body." "Use tabular numerals and right alignment for numerical columns." "Keep full precision internally; display rounding must not drive calculation." | R835 (obligation) |
| "Spacing scale: **4, 8, 12, 16, 24, 32, 48 px**." "Control height: **44 px** minimum as the project target." "Use natural height for variable text." | R836 (obligation) |
| "Check actual foreground/background combinations; a token list alone does not prove contrast." "Aim for WCAG 2.2 AA: 4.5:1 for ordinary text, 3:1 for qualifying large text, and the relevant 3:1 requirements for essential non-text boundaries." | R837 (obligation) |
| "Use a single shared token source and component styles; do not scatter magic numbers through TSX, SVG and PDF templates." "Consolidate shared type, spacing, color and status tokens." | R838 (obligation) |
| "Choose a visual because it answers a spatial or numerical question." "Bars start at zero and use the same scale for competing options." "Allowance and achieved area must have distinct labels and visual treatments." "A chart cannot be the only way to obtain essential values." | R839 (obligation) |
| "Never use 3D bar charts, gauges for legal certainty, unexplained radar scores, decorative pie charts or a “confidence percentage” invented by the UI." | R840 (prohibition) |
| "Use the existing server drawing kit and geometry contracts." "Do not trace a picture or create a pleasant rectangle that substitutes for the actual lot." | R841 (obligation) |
| "It must never be used as the site's footprint, permitted envelope or proof of site fit." | R842 (prohibition) |
| "For actual site plans, provide: selected lot outline, adjoining context needed for interpretation, street names/widths, north arrow, real scale bar, dimensions, yards/setbacks and a compact legend." "If context is missing, state that limitation instead of presenting an isolated polygon as a complete location map." | R843 (obligation) |
| "For actual sections, show ground/reference plane, floor elevations, base height, maximum height and relevant setbacks." "For massing, use a consistent axonometric camera, shared scale across option comparisons and restrained use colors." | R844 (obligation) |
| "Line-weight starting points at final print size: context 0.25–0.35 pt; secondary geometry 0.5 pt; primary lot/building outline 0.9–1.2 pt; important cut/ground line 1.2–1.5 pt." "Label placement is a layout algorithm, not wishful SVG text:" "Fail the visual check rather than shrinking labels below the minimum or suppressing dimensions silently." | R845 (obligation) |
| "Do not label local drawing feet as EPSG:2263 without the documented transform." "Never stretch the tax-map outline to match a recorded lot area." | R846 (prohibition) |
| "Use actual, licensed site/aerial/street imagery only when it helps the architect understand access, context or surroundings." "Do not use stock buildings, AI-generated streets or photorealistic proposed façades in a zoning feasibility report: they imply facts or design work that the program has not established." | R847 (prohibition) |
| "Use the same result revision, scenario identity, source basis, presentation vocabulary and diagram assets as the website." "PDF is a deliberately composed document, not a screenshot of the dashboard and not a dump of every component's expanded state." | R848 (obligation) |
| "Default to A4 portrait with **14 mm margins**." | R849 (obligation) |
| "| Decision brief | Understand the property and answer immediately | Identity, three answers, one useful visual, most important open items; no empty ceremonial cover |" "| Site and context | Understand the actual parcel and constraints | Location/zoning context and dimensioned site plan, with legible legends |" "| Option comparison | See differences quickly | Same metrics and basis across options; qualifying conditions and unavailable results explicit |" "| Scenario sheet(s) | Understand one supported option | Plan/section/massing, achieved vs allowed area, floor schedule and binding constraints |" "| Calculation/evidence | Reproduce and inspect the result | Inputs, formula, rule applicability, compact source references and provenance |" "| Assumptions/open items | Know what can change the conclusion | Group shared assumptions once; identify effect and required next input/check |" | R850 (obligation) |
| "Follow the full existing report section map." "Do not remove an entire promised section merely because it is currently unsupported: show its concise unavailable state or include it in the coverage inventory, with its material effect visible in the summary when necessary." | R851 (obligation) |
| "Use running property/scenario identity, actual page numbers, bookmarks and useful internal cross-references." "Repeat table headers after a page break." "Reserve header/footer space in the page template." | R852 (obligation) |
| "Keep text selectable, fonts embedded and diagrams vector where possible." "Production acceptance must catch this class of defect with long and partial-data reports too." | R853 (obligation) |
| "Trace the current production/preview entry points first." "Find the actual report assembly path and converter; this list is not a declaration that `ReportView.tsx` already produces the server PDF." "Do not create a competing exporter merely because it is easy to print the prototype." | R854 (obligation) |
| "Keep one canonical calculation result." "It may format numbers and group reasons, but it must not decide law, recalculate zoning in JSX or invent missing geometry." | R855 (obligation) |
| "Distinguish `0`, missing, not applicable, not assessed, failed check and unavailable." "Never use `value || 0`." "Screen and export must use the same revision; prevent stale export when property/scenario inputs change." | R856 (obligation) |
| "Read and adapt their layout patterns; do not import the sample constants into production." | R857 (prohibition) |
| "Do not introduce a framework, chart library, PDF converter or font service without a concrete need and the existing dependency/security approval process." | R858 (prohibition) |
| "1. **Reconcile and preserve:** identify active route/export paths, latest status mapping, current authorized work and the existing owner questionnaire." "2. **Establish shared presentation:** tokens, metric formatting, status/reason presentation, result identity and provenance hooks." "3. **Finish one complete website slice:** real property → three answers → details → one comparison → actual data states, including a partial-data case." "4. **Finish the corresponding PDF slice:** same data revision and SVGs, clean page one, comparison, scenario/detail and evidence treatment." "5. **Apply the same system to remaining supported report sections and website tools:** use the existing full-scope section map." "6. **Run bounded acceptance and independent review:** reuse existing tests and gates, fix concrete findings, and retain evidence for the reviewed revision." "7. **Record the exact next step and deliver the actual outputs:** website route or preview, exported PDF, screenshots, changed files and remaining issues. “Components implemented” is not “the architect can use it.”" | R859 (sequencing) |
| "Do not spend a session creating a large design-document bureaucracy." | R860 (prohibition) |
| "Save the adopted contract at `docs/design/ARCHITECT_PRESENTATION_CONTRACT.md`." "Incorporate later approved changes there rather than creating `v2`, `final-final` and competing policies." | R861 (obligation) |
| "Update the active routing in `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md` and `.claude/rules/frontend-web.md` to reference the contract." "Do not silently delete product requirements or change the single-dashboard plan." | R862 (obligation) |
| "Add a short pointer in `CLAUDE.md`, for example:" "Do not paste this entire brief into `CLAUDE.md` or import every historical design document into every session." | R863 (obligation) |
| "For backend report/drawing paths, extend the relevant existing rule or add one small path-scoped rule if no suitable rule exists." "Do not create a new skill, hook, watcher or enforcement daemon for this." | R864 (obligation) |
| "In the normal `docs/SESSION_HANDOFF.md` update, add a compact design entry containing:" "Ensure the receiving session/worktree has the commit containing these pointers; a handoff on an unmerged branch must name that branch explicitly." | R865 (obligation) |
| "Find the **active owner questionnaire already used by this program**, including the C1 reference from the sample." "Append material questions to the correct existing file and preserve numbering, answered decisions and links." "Ask only when the answer affects meaning, scope or a genuine product choice." | R866 (obligation) |
| "Use it for its established purpose; do not redirect owner implementation decisions there by assumption." | R867 (prohibition) |
| "Use these IDs in the existing directive/evidence process." "Report each as **PASS, FAIL, NOT RUN or NOT APPLICABLE with a reason**." | R868 (evidence) |
| "| UX-01 | Property, site selection, program and result scope are identifiable immediately | Desktop and phone captures; human walkthrough observations |" | R869 (evidence) |
| "| UX-02 | Allowance, envelope and achieved option are distinguishable; estimates remain separate | Populated and partial-data cases, screenshot plus semantic assertion |" | R870 (evidence) |
| "| UX-03 | No result is promoted from unknown/withheld to a number or from draft to verified by presentation | State tests using canonical contracts and current mapping |" | R871 (evidence) |
| "| UX-04 | Shared notices appear once; material local exceptions remain visible | Disclosure inventory and review of each affected surface |" | R872 (evidence) |
| "| UX-05 | Screen, comparison, drawings and PDF use matching property/scenario/revision/basis | Cross-output identity and value checks; stale-response scenario |" | R873 (evidence) |
| "| UX-06 | A/B comparisons use consistent units and site assumptions, with differences explicit | At least two genuinely different supported scenarios; unresolved case |" | R874 (evidence) |
| "| UX-07 | No clipped text, unintended horizontal page scrolling, overlapping labels or obscured controls | Captures and DOM checks at 320, 390, 768, 1,024, 1,440 and 1,920 px |" | R875 (evidence) |
| "| UX-08 | Long labels, long addresses, large/small values and text expansion remain readable | Stress fixtures, 200% zoom and text-spacing checks |" | R876 (evidence) |
| "| UX-09 | Keyboard, focus, modal return, accessible names, status announcements and contrast work | Actual keyboard walkthrough; targeted automated accessibility checks; manual findings |" | R877 (evidence) |
| "| UX-10 | Drawings match real geometry and metrics; labels remain legible at final output size | Canonical geometry/metric comparison, collision checks, visual inspection |" | R878 (evidence) |
| "| UX-11 | Every generated PDF page is readable and correctly paginated | Rendered page images; page-by-page review; font, boundary and content checks |" | R879 (evidence) |
| "| UX-12 | Full required report scope is retained with honest availability | Section inventory mapped to current report section map |" | R880 (evidence) |
| "| UX-13 | No development log, raw error, task ID or internal schema jargon appears in ordinary architect content | Content review of populated, loading, empty, partial and error states |" | R881 (evidence) |
| "| UX-14 | Conditional gains and unavailable alternatives are not represented as computed feasible outcomes | Comparison fixtures and independent review of meaning |" | R882 (evidence) |
| "| UX-15 | A fresh session finds the adopted design and resumes the right work | Committed routing/contract, handoff entry and receiving-session orientation check |" | R883 (evidence) |
| "| UX-16 | Final claims match actual completion and existing gates | Evidence on the reviewed revision; independent review; remaining failures explicit |" | R884 (evidence) |
| "Minimum meaningful state coverage:" "Normal supported result; currently incomplete benchmark result." "No geometry; conflicting site areas; unknown street width; unresolved eligibility." "Exact zero vs unavailable; very large numbers; long names and multiple lots." "Failed fetch, partial fetch, changed property during a request and stale result/export prevention." "A short report and a long report with repeated headers and multiple scenario sheets." | R885 (evidence) |
| "Use independently established expected values for correctness tests, including existing reviewed reference cases." "Screenshot baselines must be visually reviewed before approval; never update every baseline simply to make the test pass." | R886 (evidence) |
| "For PDFs, render **every page**, including appendices." "Check at normal reading size and in grayscale." | R887 (evidence) |
| "Respect existing producer/reviewer separation." | R888 (obligation) |
| "Return a concise update with links:" "What is now usable: the real route/preview and a newly generated PDF from the same result revision." "Desktop and phone screenshots, plus representative PDF pages and the location of the complete page-by-page evidence." "Acceptance results and independent review outcome, with failures and not-run checks explicit." "Remaining decision questions in the existing questionnaire, and the next visible action." | R889 (return) |
| "Do not say “perfect,” “fully verified,” “complete” or “production ready” because the CSS looks good or a test runner is green." | R890 (prohibition) |
| "Do not install a new plugin solely to begin this work. [Official skill](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)." "Do not make unsupported claims about specialized skill quality or install third-party collections without the existing review process." | R891 (prohibition) |

- **The attached brief** is bound as a whole by this source and adopted as the presentation contract (row R861); the rows above quote the sentences that carry its requirements; its tables of type sizes, palette, editorial budgets and line weights are bound through the rows that cite them.
- **Questions raised by this capture** are entered in the owner's questions file in the same step (rows R774, R775).
- **Sentences of the message quoted by no row:** none.
- **Lines of the attached brief quoted by no row:** 349 of 520; the rest of the brief (its explanations, tables and research notes) is bound as the adopted contract, not row by row.
- **Not claimed by this capture:** no row is verified; all 92 are pending. This capture changes no product file, no test and no instruction file.
