# NYC Buildability — UI Deep Dive Assessment

**Assessment only · 23 September 2026 · Uncommitted handoff for the orchestrator**

**Reading path:** [Main finding](#2-main-finding) · [Route map](#3-route-and-capability-map) · [Visual direction](#12-one-coherent-visual-direction) · [Gated plan](#14-phased-handoff-for-orchestrator-owned-tasks). Sections 4–10 contain the detailed text inventory and disclosure trace.

## 1. Scope, evidence, and limits

- Repository: [martin10101/nyc-buildability](https://github.com/martin10101/nyc-buildability).
- Audited branch: `candidate/D-024-mrl-option-b`.
- Frozen source: [`dc5a763e7494de62a0dbfd8e60e8cbbade73bc8c`](https://github.com/martin10101/nyc-buildability/tree/dc5a763e7494de62a0dbfd8e60e8cbbade73bc8c), committed **2026-09-23 21:11:56 UTC**. The default `main` branch remained at `d8b3899` dated August 20; it is not the audit baseline.
- The owner authorized GitHub inspection after the Windows shared checkout was found inaccessible from this session. This report evaluates the committed GitHub snapshot, **not unpushed changes in `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`**. The orchestrator must compare this baseline with its checkout before task creation.
- Study sequence: user-facing source and its state branches; reviewer memories, discovery entries and copy assertions; product intent; parked expansion material and hold. Independent screen reviews supplied the inventories below.
- No repository source was edited or committed. No `project-control/` contents were accessed; `tools/project_control.py`, npm, npx and node were not run. No application, test suite, build, CI workflow, deployment, record mutation, or browser journey was executed.
- **This is a source-grounded product assessment, not a formal acceptance gate or deployment verification.** Assertions about crowded compositions follow rendered component structure; pixel layout, latency, screen-reader speech and live endpoint availability require the remote/browser validation described later.
- The only deliverable is this Markdown file. It is prepared at the requested relative path `docs/UI_DEEP_DIVE_ASSESSMENT.md`; it has not been placed into the inaccessible Windows checkout. The orchestrator owns recording, committing, task IDs and release decisions.

### How to read the inventory

Paths and line numbers refer to the frozen commit above. Under inventory tables, relative paths are anchored to `apps/web/src/` unless a different prefix is stated. A row inventories a logical text element or an explicitly named dynamic family; repeated table rows, source excerpts, server warnings and record values are data-dependent and must be preserved for every instance, not just the examples in tests. Visible strings, conditional errors, control labels and screen-reader-only announcements are distinguished. The latter do not create visual crowding.

| Mark | Meaning | Allowed treatment |
|---|---|---|
| **L** | Must-survive legal-sensitive/product-honesty meaning: identity, source, scope, uncertainty, draft status, review requirement, gap, failure or authority boundary. | Keep meaning and point-of-decision salience. This is **not a finding that a statute mandates the sentence**. |
| **V** | Convert to a visual/progressive presentation: concise labelled state, comparison, diagram with real data, or accessible detail. | Keep text alternatives, discoverability and complete detail. L+V is common. |
| **R** | Removable presentation overhead: duplicated narration, obsolete routing instructions, developer implementation detail or redundant empty cards. | Remove only that occurrence after the report's specified replacement retains any underlying disclosure. Never silently delete an honest-gap statement or provenance. |

Exact wording may be separately required by the PRD, a current test, or a returned contract. A test pin is an implementation obligation, not proof of a legal wording obligation. This assessment does not authorize weakening tests or changing legal interpretations.

## 2. Main finding

**The owner's complaint is supported by the code. The UI repeatedly explains its architecture and limitations instead of giving each result one clear visual home.** The largest problem is the accumulated information hierarchy, not the mere existence of warnings.

1. The same draft/review/scope meaning appears in the workspace header, result cards, coverage panels, evidence inspector, report sections and global disclaimer. Several are individually justified; their cumulative presentation has not been designed as one system.
2. Independent components each add an explanation, empty-state paragraph and source area. Composing them produces a long stack of equally weighted cards. Clean success states and exceptional failures compete for attention.
3. Internal terms appear in normal workflows: canonical contracts, route constants, schema/endpoint names, raw machine status tokens and future milestone narration. The user needs their effect, not their implementation.
4. The primary and legacy route variants have different information architectures. A paragraph protected for an old flag-off screen must not be treated as a global obligation on every current screen.
5. Existing compact patterns already work as design precedents: contextual source inspection, counted missing-field disclosures, the compact map source/accuracy line, and a calm wide-street result with deeper evidence available.
6. Some changes require behavior work before visual polish: proposal result freshness, clearly identified sample defaults, incomplete drawing rows, capability readiness and replacement feedback. Hiding paragraphs would not repair those problems.

**Direction:** a stable property identity, a compact matrix of development limits, a real map when available, one priority action, and one consistent evidence inspector. Put the result and its short status together. Put the reason and full record one deliberate interaction away. Keep material blockers visible without opening anything.

## 3. Route and capability map

| Route / surface | Source composition | Audit implication |
|---|---|---|
| `/` | `app/page.tsx` | Welcome/entry screen; not a calculation result. |
| `/property` | `app/property/page.tsx:39–46` selects `ArchitectEntry` when `ruleEvaluationSurfaceEnabled(...)`; otherwise `PropertyLookup` with the flag false. | Audit both. Do not mistake an old BBL-only warning for the current architect entry experience. |
| `/property/confirm` | `app/property/confirm/page.tsx:22–28`: architect overview with required BBL, or legacy `ConfirmEntry`. | The two confirmation compositions are materially different. |
| `/property/compare` | `app/property/compare/page.tsx`: architect scenarios, or legacy `CompareEntry`. | Legacy future-Evidence copy is not evidence that the architect workspace lacks Evidence. |
| Architect query views | `ArchitectEntry.tsx:114–165`; `lib/architect/navigation.ts:2–9`. | Overview, Property facts, Zoning, Scenarios, Proposal editor, Evidence, Documents, Open issues and Report; Envelope, Units, Financials route to planned-state handling. |
| Proposal | `ArchitectEntry.tsx:44–50,162–164` renders `MaxEnvelopePanel` before `ProposalEditor`. | Frontend composition is proven by source. It does not prove the max-envelope endpoint is mounted, authoritative geometry is supplied, or live adoption works. |
| Survey review | `app/survey/review/page.tsx`, `[documentId]/page.tsx`; architect Documents is separately enabled. | Dedicated review workflow; not a reason to expose all review detail on property results. |
| `/dashboard` | `app/dashboard/page.tsx` and dashboard components. | Internal project/operations surface, not the main architect product. Its runtime data was not accessed. |
| Failure boundary | `app/property/error.tsx`, dashboard error route and typed outcome components. | Include recovery, partial-result trust and support-detail states in redesign, not only happy paths. |

## 4. Shared shell, entry adapters and legacy lookup inventory

| ID / source | Text elements and conditions | Why / triage | Concrete destination |
|---|---|---|---|
| SH-01 `app/layout.tsx:13–17,36–50`; `lib/disclaimer.ts:1–11` | Page title “NYC Buildability”; description “Preliminary NYC development feasibility and zoning intelligence platform”; global “Required disclaimer” footer with the full PRD §29 text. | L: explicitly mandated prominently in app and reports. No statutory wording determination. | Preserve full wording and prominence until a qualified/product policy decision permits an alternative. Use one deliberate legal area; do not assume a hidden tooltip satisfies §29. |
| SH-02 `app/page.tsx:6` | “NYC BUILDABILITY”; “Internal development build”; “Property intelligence · New York City”; “From property facts to an informed next step.”; “Official records, preliminary development analysis and the evidence behind every result, in one workspace.”; “Open workspace →”; “Available tools follow the capabilities enabled in this environment. Preliminary results require professional review.” | Brand/navigation V; environment/review L+V; marketing explanation R/V. | Compact entry header + address action. Environment badge and review line remain legible; remove redundant welcome narration once the search has a clear home. |
| SH-03 `ArchitectEntry.tsx:65–80` | Eyebrow; “Search by tax lot (BBL)”; “BBL”; “10-digit borough–block–lot”; “Open property”; validation error. | V; format errors remain actionable. | One address field with an explicitly named BBL alternative; format hint inside that alternative. |
| SH-04 `lib/bbl.ts:35–80` | Empty: “Enter a 10-digit BBL (borough, block, and lot).”; digits-only instruction with `1000010010` example; exact-length count; borough digit 1–5 and borough mapping. | V: correct input without a request. | Inline field error; one example/help disclosure. Do not replace all four distinct errors with a generic red icon. |
| SH-05 `ArchitectEntry.tsx:95–98,216–218` | Screen-reader messages for rule/property identity mismatch or missing identity, requested/returned BBL, withheld results, incomplete rule detail. | L; parity with visible withholding, not visual clutter. | One relevant outcome announcement; never announce a loaded calculation that has been withheld. |
| SH-06 `ArchitectEntry.tsx:136–146` | “Analysis issues”; each constraint key, state and note. | L+V: unresolved analysis conditions. | Named issue rows grouped by affected limit, not raw key-led paragraphs; original key in details. |
| SH-07 `ArchitectEntry.tsx:154–157` | “Document review is unavailable in this environment”; enabling/no-inventory/no-upload paragraph. | L+V capability honesty; implementation phrasing R. | Disabled Documents action with “Unavailable here” and reason on activation; retain that inventory/upload are not available. |
| SH-08 `ArchitectEntry.tsx:169–185` | Address or `BBL {bbl}` heading; “Draft analysis”; borough fallback; BBL + active view; conditional “Searched address retained · PLUTO representative address: …”; “Change property”. | L identity, draft and address-role distinction; V layout. | Stable property header with a compact typed/matched/recorded identity disclosure. Keep material identity differences visible. |
| SH-09 `ArchitectEntry.tsx:189–196` | “Loading draft scenario…”; scenario/evaluation failures; scenario and rule identity notices; incomplete-evaluation notice. | L+V: independently loading/failed analyses cannot become successful blanks. | One analysis-status area with separate named channel states; affected values explicitly unavailable. |
| SH-10 `ArchitectEntry.tsx:221–241` | “No property selected”; invalid-BBL/choose-property instructions; “Retrieving property facts…”; “Loading the official property profile.”; “Property identity mismatch”; requested/returned BBL; unusable-record sentence; “Returned property record”; “Change property”. | L identity refusal; V transient messages; repeated loading prose R. | Search/failure state with one next action; mismatch stops analysis and retains returned record in evidence. |
| SH-11 `PropertyLookup.tsx:61–112` | BBL/address identity; absent-address/conflict explanation; official source/dataset/release or release-not-published/retrieved/host/profile reference; completeness headline, token and gloss. | L source scope/completeness; V presentation. | Identity header + dated source chip, details retain all metadata; completeness as a named state near results. |
| SH-12 `PropertyLookup.tsx:125–159` | Shared coverage, conflicts, zoning and gap components; “Lot facts”/official-lot note; “Existing building facts”/what-stands note; “Next step”; compact-card explanation; “Review and confirm this property”. | L inherited semantics; V fact groups; R duplicated navigation explanation. | One confirm action after identity and blocking issues. Building facts stay in a secondary tab/toggle with explicit availability. |
| SH-13 `PropertyLookup.tsx:266–340` | “Property lookup”; 10-digit BBL explanation; “BBL”; `e.g. 1000010010`; borough/block/lot format hint; “Look up property”; inline validation. Flag-off: “Address (not yet available)”, disabled placeholder and Geoclient-credentials/BBL-only/no-pretend paragraph. | V form labels; L true unavailable capability; R credentials/metacommentary on analyst surface. | BBL form with concise unavailable-address state and a “Why?” detail. Preserve legacy flag-off behavior until its route retirement is separately authorized. |
| SH-14 `app/property/error.tsx:37–64` | “This screen could not be displayed”; containment/“Nothing was determined, nothing was saved”/do-not-rely paragraph; official-data/engine-unaffected claim; optional support reference; “Try this screen again”; “Back to property lookup”. | L failure and no reliable partial analysis; V recovery. Absolute saved/backend claims require checking against future side-effecting flows. | One failure heading, one trust sentence, retry/back actions; digest in Support details. Do not shorten into an implied successful or saved analysis. |
| SH-15 `app/property/page.tsx:9–11`, `confirm/page.tsx:8–10`, `compare/page.tsx:8–10`; `app/survey/review/page.tsx:8–10`, `[documentId]/page.tsx:8–10` | Browser titles: “Property lookup — NYC Buildability (internal)”; “Confirm property — NYC Buildability (internal)”; “Compare scenario — NYC Buildability (internal)”; “Survey review inbox — NYC Buildability (internal)”; “Survey review — NYC Buildability (internal)”. | V route orientation; L+V internal-environment identity. | Retain meaningful browser-tab names and the internal qualifier while reorganizing the corresponding screen. Dashboard's separate title is inventoried in DB22. |

### Required disclaimer — preserved verbatim

> This platform provides preliminary development and zoning feasibility information based on available public records, user-provided assumptions, and the platform’s current rule coverage. It is not a legal opinion, architectural or engineering certification, DOB determination, permit approval, or guarantee that a proposed development will be approved. Results must be reviewed by qualified New York professionals before reliance, acquisition, design, filing, financing, or construction.


## 5. Proposal, drawing, generated limits, and zoning context

### 5.1 Findings that should guide this work

The proposal surface repeats the same honesty statement in the editor, drawing, check results, variations, and each comparison column. Its meaning is necessary; repeating the full paragraph is a presentation choice. Persistent scoped claim badges and accessible details can carry this meaning, provided a detached report or comparison column still identifies its own provenance.

Point-selection instructions, coordinate-conversion stages, disabled-button explanations, and failure recovery currently rely on paragraphs. Toolbar modes, a stage indicator, row validation, and direct recovery actions can explain these visually. Live-region announcements must not be counted as visible copy clutter: accessible outcomes remain necessary even when the visible explanation becomes compact.

Two source-supported correctness risks need reproduction before cosmetic cleanup:

- **Example attribution:** ProposalEditor.tsx:73 initializes rectangleSampleDraft() for every BBL. lib/architect/proposal-draft.ts:421–449 supplies example R5 zoning, 8,000 sq ft lot area, wide street, example coordinates and a lot line. The form calls them “your input” without a visible example label. This is a code finding, not a claimed live observation.
- **Report freshness:** ordinary input handlers call setDraft without clearing outcome, while saveVariation combines the current draft with the existing report (ProposalEditor.tsx:127–137,195–403). Drawing adoption correctly clears the result (144–158). A changed draft may therefore retain a prior report and save that pairing. Reproduce the transition; the inspected editor tests do not cover it.

Do not assume generated options are available merely because the UI has an adoption button. Max-envelope tests preserve the real geometry-free request state: no candidate because no lot-line geometry was supplied. The successful adoption browser journey intercepts responses. It proves a rendering/interaction contract, not deployed capability.

### 5.2 Proposal editor text inventory

Paths below are relative to apps/web/src/components/architect/ unless otherwise stated. Dynamic strings are inventoried by their exact rendering template/data source rather than invented values.

| ID / source | Text elements and states | Why it exists | Triage and proposed destination |
|---|---|---|---|
| PE-01 ProposalEditor.tsx:181–186 | “Proposal editor”; “Proposed — your input, not a city record. You enter the numbers; the check compares them against the rules and returns a preliminary result that requires professional review.” | Separates authored input from official records and prevents a check result implying approval; D-076-R002 in source comments. | L→V: scoped Proposed input and Preliminary check badges; professional-review qualification beside results; full explanation in accessible detail. Correct example attribution first. |
| PE-02 :192–254 | “Proposal label”; “Proposal id (optional)”; “Zoning district (caller-attested)”; “Street width class (caller-attested)”; “Not attested”; “Wide”; “Narrow”; “Lot area (sq ft, caller-attested)”. | Identifies draft and user-attested inputs. Missing attestation differs from either width class. | V labels; L attestation meaning. Compact property-input inspector with User supplied provenance; optional ID in advanced metadata. |
| PE-03 :256–297 | “Outline vertices (EPSG:2263 feet) — the numeric authority for this proposal”; “#”; “X (ft)”; “Y (ft)”; “Actions”; “Delete”; “Add vertex”. | Numeric model is authoritative for this proposal; manual entry survives drawing failure. | L→V: concise caption with explicitly visible/editable coordinate table. Technical explanation in detail; no map-only replacement. |
| PE-04 :273–287 | Accessible names “Vertex {i} X coordinate”, “Vertex {i} Y coordinate”, “Delete vertex {i}”. | Distinguishes repeated controls to assistive technology. | L retain; not visible clutter. |
| PE-05 :299–351 | “Levels”; “Level”; “Floor count”; “Floor-to-floor (ft)”; “Actions”; “Delete”; “Add level”; accessible “Level {i} index”, “Level {i} floor count”, “Level {i} floor to floor height”, “Delete level {i}”. | Explicit dimensional inputs and accessible row actions. | V: compact level editor with units and keyboard controls preserved. |
| PE-06 :353–404 | “Exterior walls”; “Id”; “Start vertex”; “End vertex”; “Actions”; “Delete”; “Add wall”; accessible “Wall {i} id”, “Wall {i} start vertex index”, “Wall {i} end vertex index”, “Delete wall {i}”. | Associates exterior walls with numeric vertices. | V: inspector tied to selected edge, with full numeric table available. |
| PE-07 :406–423 | “Checking…” / “Run check”; “Proposal not sent”; “The draft was blocked before sending. Fix these to match what the checking service will accept:”; {p.message}; “(route: {p.routeConstant})”. | Running state, client-side refusal and boundary diagnostics. | L not-sent status and repairable errors; V inline field errors; R visible route constants/generic preamble only after moving diagnostics to details. Test currently pins _LABEL_CHARSET. |
| PE-08 :99–101,113,136,153–157,173 | Announcements: adopted generated option as proposed starting draft; “Proposal not sent: the draft has input problems, listed below.”; saved current proposal “this browser session only”; adopted {n} drawn points into numeric outline; removed {n} walls with IDs and re-add instruction; “Loaded variation {label}.” | Accessible outcomes; geometry/wall changes cannot be silent. | L preserve announcements and exact wall-change information; concise visible change summary can replace prose repetition. |
| PE-09 lib/architect/proposal-draft.ts:105–188 | “{field} must be a non-empty label”; “{field} exceeds MAX_LABEL_LEN ({limit}); got {length} characters”; “{field} contains characters outside the allowed set [A-Za-z0-9 ._:-]”; wall/lot-line/street-line/outline-position counts exceeding named route caps; “vertex {i} must be finite EPSG:2263 coordinates”. | Mirrors transport limits and prevents doomed submissions. | V friendly field names, actual numeric limits and repair actions; R implementation identifiers from default UI, retained in technical details. |
| PE-10 proposal-draft.ts:342–355,425–449 | Default “New proposal”; seed “scenario-A-baseline”, “prop-0001”, “R5”, “wide”, 8000, numeric coordinates/levels and wall IDs. | Demo seed populates first render. | R as undisclosed default; retain only as explicitly chosen/labeled example or correctly seeded actual proposal through separately reviewed behavior change. |

### 5.3 Drawing and coordinate-conversion inventory

| ID / source | Text elements and states | Why it exists | Triage and proposed destination |
|---|---|---|---|
| DR-01 ProposalOutlineDraw.tsx:177–189 | Accessible “Draw the building outline”; “Draw the outline”; “Proposed — your sketch, not a city record. Add points and type them by keyboard in the table below, then convert them to numeric coordinates. The conversion is approximate proposed input with its fit accuracy disclosed — not a survey. The numbers table stays editable; typing coordinates is always an option.” | Proposed/record distinction, accuracy boundary and manual path; D-076-R002 and D-082-R003. | L→V: Proposed sketch / Approximate labels, Drawing → Converted coordinates stages, Accuracy & method detail; manual path persists. |
| DR-02 :194–197 | “Any reference map shown displays the recorded lot for context only. Nothing is measured from it; your drawing is converted to official-grid feet on the server.” | Avoids claiming a map exists in typed fallback states; display coordinates are not authoritative measurements. | L→V: Reference lot — context only map legend; conversion method detail. No measured dimensions derived from display map. |
| DR-03 :209–267 | “Drawn points (display longitude / latitude) — a proposed sketch, converted server-side”; “#”; “Longitude”; “Latitude”; “Actions”; “Select” / “Deselect”; “Delete”; “No points drawn yet. Add at least 3 points, then convert.” | Keyboard equivalent; distinguishes display from authoritative coordinates. | V controls; L coordinate/proposed distinction. Compact point inspector/table and actionable empty state. |
| DR-04 :226–252 | Accessible “Drawn point {i} longitude”, “Drawn point {i} latitude”, “Select/Deselect drawn point {i}”, “Delete drawn point {i}”. | Accessible repeated controls and selection. | L retain. |
| DR-05 :270–298 | “Add drawn point”; “Converting…” / “Convert to numeric outline”; “Convert needs at least 3 points with both coordinates filled in. {n} row(s) still need(s) a longitude and latitude — fill it/them in or delete it/them ({ready} of 3 ready).”; alternatively “Add {n} more point(s) to convert — an outline needs at least 3 points (you have {n}).” | Explains disabled action from finite points rather than row count; DB-045(g), DB-047(e). | L→V: visible readiness count, incomplete-cell markers, short adjacent reason. No tooltip-only explanation. |
| DR-06 :310–329 | “Outline converted to numeric coordinates”; verbatim report.disclosure; “Fit residual (RMS)” with exact number or “disclosed by the server”; “Correspondence method”; “Alignment”; “Source rings”; source IDs/CRS with display/4326 and authoritative/2263 fallbacks. | Conversion lineage and fit accuracy, never survey-grade claim. | L→V: exact accuracy beside success status; full disclosure, method, alignment and source rings in Accuracy & conversion details. |
| DR-07 :334–347 | “Outline not converted”; outcome announcement; “Fit residual {value} ft exceeds the bound of {bound} ft. No coordinates were produced.” (or “was over the bound” if values absent); “Reason: {reason}”. | Typed refusal and no coordinates after failed conversion. | L→V: persistent failure/recovery; exact residual/bound retained and visible when blocking. |
| DR-08 ProposalOutlineMap.tsx:151–158 | Interactive: “Click the lot map to place a proposed outline point, or add points by keyboard in the table below. Click a placed point to select it.” Selected: “Point {i} is selected — click the map to move it, or edit it in the table below. Click the point again to deselect.” Loading: “Preparing the reference map — you can start adding points by keyboard in the table below; enter each point's longitude and latitude.” Fallback: “Add proposed outline points by keyboard in the table below — enter each point's longitude and latitude. The reference map on this lot has no interactive drawing surface.” | DB-047(d), HJ B1/B2: only invite real gestures; loading cannot assert definite absence. | L→V: Place point / Move point toolbar modes; neutral loading; keyboard entry always available; explicit fallback. Preserve all four states. |
| DR-09 :168–173 | Hidden status “No points drawn yet.” / “{n} point(s) drawn. Point {i} selected.” | Announces finite/rendered points only, DB-047(e). | L retain as accessibility output. |

lib/outline-bridge-api.ts:520–556 supplies these distinct conversion outcomes, all L→V as typed states rather than one generic warning:

| ID | Outcome text / meaning | Required visual state |
|---|---|---|
| DR-10 | Success: {n} points placed in numeric table; fit residual; approximate proposed values, not a survey/not a city record; edit then run check. | Converted, exact accuracy, proposed provenance, next action. |
| DR-11 | “Map-drawing conversion is not available in this environment. Enter coordinates in the table instead.” | Unsupported capability with working manual path. |
| DR-12 | “Outline not converted: the drawing was too large to send.” | Size refusal; no conversion. |
| DR-13 | “Outline not converted: the drawn shape was refused. Adjust the drawn points and try again.” | Geometry/input refusal and repair. |
| DR-14 | “Outline not converted: a drawn point fell outside the shown lot. Draw over the parcel and try again.” | Out-of-neighborhood refusal, distinct from residual failure. |
| DR-15 | “Outline not converted: the drawing could not be matched to the official parcel geometry, so no coordinates were produced.” | Correspondence unavailable, no authoritative output. |
| DR-16 | “Outline not converted: the drawing did not align closely enough with the official parcel, so no coordinates were produced.” | Residual failure, no output. |
| DR-17 | “Outline not converted: an official parcel source could not be reached. This is safe to retry.” | Source outage with retry. |
| DR-18 | “Outline not converted: something went wrong on our side. This is safe to retry.” | Internal failure with retry. |
| DR-19 | “Outline not converted: the response did not match the published data contract.” | Invalid response; no invented coordinates. |
| DR-20 | “Outline not converted: the bridge service could not be reached.” | Network failure. |
| DR-21 | “Outline not converted: the request took too long and was cancelled.” | Timeout/cancelled operation. |
| DR-22 | “Outline not converted: unexpected response from the platform API.” | Unexpected response. |
| DR-23 | Aborted outcome emits an empty announcement. | No false success or redundant abort announcement. |

### 5.4 Proposal-check report inventory

| ID / source | Text elements and states | Why it exists | Triage and proposed destination |
|---|---|---|---|
| PC-01 ProposalCheckReport.tsx:50–65 | Icon+text “Fail”, “Pass”, “Could not check”; unknown outcome shown literally with “?”. | Failure/gaps are first-class; status cannot rely on color; unsupported is not pass. | L→V: compact symbol+text, retaining unknown state rather than inventing confidence. |
| PC-02 :56–65 | “The proposal provides no such value.”; “The proposed value does not establish the quantity this rule governs — matching units are not equivalence.”; “No rule in this family applies to the supplied lot facts.”; “An applicable rule produced no usable allowance (a required input is missing, or it needs professional review).”; “No rule for this family is implemented yet.”; “More than one rule produced an allowance; which one governs is a professional determination, not made here.” | Distinct missing input, noncommensurability, nonapplicability, unresolved allowance, unsupported family and ambiguous governing rule. | L→V: short reason stays visible; full explanation in Why? detail. Never collapse into a missing numeric cell. |
| PC-03 :77–120 | Rule label; fail “{provided} {unit} provided; {required} {unit} required; {shortfall} {unit} short”; pass “{provided} {unit} provided; {required} {unit} allowed”; “This check could not be run.”; “Proposed value recorded: {value} {unit} (your input, not compared).”; “Why this cannot be compared” and semanticGap; “Rule {id} · coverage {status}”. | Exact server quantities; raw proposed quantity differs from legally comparable quantity; provenance. | L→V: Provided / Allowance / Difference / Status / Evidence table; explicit not-compared designation for CNC. Preserve exact phrase until approved test migration. |
| PC-04 :170–185 | “Checking the proposal against the rules…”; “Enter a proposal and run a check to see how it measures against the rules. Every value is a proposed value you entered — not a city record.” | Loading versus unrun state and input provenance. | V compact Not checked state with action; L provenance badge. |
| PC-05 :193–209 | “Proposal check report”; “Proposed — your input, not a city record. Preliminary result; professional review required.”; “{fail} did not meet an allowance · {cnc} could not be checked · {pass} met an allowance”; groups “Did not meet a rule allowance”, “Could not be checked”, “Met the rule allowance”; “Inputs not used by any rule: {facts}”; “Reference: {correlationId}”. | A passing subset is not whole-building approval; unused inputs and trace remain available. | L→V: Fail / Unchecked / Pass count tabs; report scope badge; named unused-input disclosure; reference in technical details. |
| PC-06 :140–159,213–225 | “The proposal could not be checked”; “Proposal checking is not available in this environment.”; server payload/validation/internal/network messages; “The response did not match the published data contract, so nothing was rendered.”; “The request took too long and was cancelled.”; “The platform API returned an unexpected response.”; generic “The proposal could not be checked.”; “Field: {field}”; recoverable-only “Nothing was checked, and this is safe to retry.” | Typed failure/recovery and no fabricated results. | L→V: one status card, actual field repair or retry; technical cause in details. |

lib/proposal-checks-api.ts:446–473 also announces report counts plus proposed/professional-review qualification. Feature-unavailable, oversized, refused draft, internal error, invalid contract, unreachable service, timeout and unexpected response each retain outcome-specific announcements; aborted emits none.

The exact “short” phrasing is currently pinned even for a maximum-rule exceedance: “0.625 ratio provided; 0.5 ratio required; 0.125 ratio short.” A future gate should consider “over limit” versus “short” using rule direction. This is an accepted copy-contract change, not an incidental cleanup.

### 5.5 Proposed variations inventory

| ID / source | Text elements and states | Why it exists | Triage and proposed destination |
|---|---|---|---|
| PV-01 ProposalVariations.tsx:14–35 | “not checked yet”; “{fail} fail · {cnc} could not check · {pass} pass”; comparison label; “Proposed — not a city record.”; “{rule label}: {outcome}”; “Run a check on this variation to compare its results.” | Scoped outcomes and honest unrun state. | L→V: aligned comparison rows, status symbols+text and proposed provenance in each column. |
| PV-02 :60–95 | “Proposed variations”; “Proposed — your input, not a city record.”; “Kept in this browser session only — not saved.”; “Save current proposal as a variation”; “No variations saved yet.”; label and summary for each variation. | In-memory variations are not persisted scenario documents or official records. | L→V: Session only pill adjacent to title/action with explicit loss-on-leaving detail. Review contradictory Save/not-saved action wording. |
| PV-03 :96–130 | “Compare two variations”; “First variation”; “Second variation”; “Choose…”; “Choose two saved variations to compare their results side by side.” | Selection setup. | V labels; R repeated guidance once controls and disabled-state reason explain the task. |

### 5.6 Preliminary development limits and generated-option inventory

| ID / source | Text elements and states | Why it exists | Triage and proposed destination |
|---|---|---|---|
| ME-01 MaxEnvelopePanel.tsx:50–63,87–100 | Dimension label and exact value+unit, or “Could not check — {reason}”. Reasons: “no applicable rule was found for this dimension”; “the governing allowance could not be resolved”; “this rule family is not supported by the engine yet”; “the rule does not translate to this massing dimension”; null fallback “the reason was not stated”; unknown token literally. Server gap detail remains. | No invented limit; distinct gap families; fail-honest unknowns. | L→V: dimension tile contains number OR explicit gap, reason chip and Why? detail. |
| ME-02 :103–128 | “Binding rule {id/unknown} v{version} · {n} rule(s) out-competed · {n} citation(s)”; “Cited sections: {sections}”; “Rule conflict surfaced for professional review, not resolved here: competing rules {ids} — {note}.” | Binding provenance and unresolved legal conflicts, D-083. | L→V: anchored citation link per tile; visible conflict badge with IDs/note in detail; out-competed count/list in evidence. |
| ME-03 :168–183 | Verbatim envelope.disclosure; complete “All {n} preliminary development limits were checked — a rules-derived estimate requiring professional review.”; incomplete “Could not check {gap} of {total} development limits[, and a rule conflict needs professional review]. This preliminary picture is incomplete.” | Exact server disclosure; no unrestricted green while gap/conflict remains. | L→V only through gate: persistent Incomplete / unchecked count and conflict state; verbatim disclosure in accessible detail if approved; no approval/maximum-building headline. |
| ME-04 :192–211 | “Generated building option”; “A single checked building OPTION shaped from the limits above — a rules-derived estimate, not a permitted building and not a city record. The per-limit ceilings above are never combined into one building; only this checked option is building-shaped.”; “Adopt as a proposed starting draft”; “No building option can be adopted for this lot: {placement.detail}”. | D-083 claim class; independent ceilings differ from checked candidate; adoption only if fitted and contained. | L→V: separate option card, class badge and estimate qualifier; What this represents detail. No fabricated 3D building made from independent maxima. |
| ME-05 :260–275 | “Preliminary development limits”; “The computed limits for this lot, shown first — a rules-derived estimate that requires professional review, not a maximum permitted building. Test a design below whenever you are ready.”; missing context “Preliminary development limits cannot be computed for this property: no usable lot area is recorded. Enter a proposal below to check a design directly.”; “Computing the preliminary development limits…”. | Answer-first hierarchy, honest context absence, independent editor fallback. | L claim/scope/absence; V compact states/actions; R orientation phrases “shown first”/“below whenever ready” after action replaces directions. |
| ME-06 :285–299 | “Preliminary development limits are unavailable right now”; typed outcome message; “Nothing was fabricated. The proposal editor below is unaffected — enter a design and check it directly.”; “Try again”. | Failure does not fabricate a limit or block manual proposal checking. | L honest failure/recovery; V direct editor/retry action; R self-congratulatory “Nothing was fabricated” phrasing after deliberately updating its test. |
| ME-07 :160–163 | Adoption announcement: generated option becomes proposed starting draft; every value remains proposed/editable. | No silent replacement or reclassification. | L retain announcement; short visible toast. |

The exact full server disclosure is reproduced and pinned in apps/web/e2e/proposal-editor.spec.ts:430–444:

> This maximum-buildable envelope is a DETERMINISTIC, rules-derived ESTIMATE for the rectangle-prism massing class - NOT a city record, a permit, an approval, or a legal determination. Each dimension is the tightest applicable draft rule's allowance for this lot (the looser rules are automatically satisfied and recorded as out-competed); where more than one rule bounds a dimension, which rule governs is a legal determination requiring professional review, surfaced here as an advisory rather than resolved. Non-commensurable dimensions (residential FAR, rear yard) are disclosed as honest gaps. Qualified professional review is required before any reliance.

All these meanings need explicit destinations. A badge alone is insufficient; retain the complete verbatim contract in an accessible disclosure unless a separate approval changes that requirement.

lib/architect/max-envelope-api.ts:579–606 supplies and announces these additional typed states:

| ID | Text / state | Triage |
|---|---|---|
| ME-08 | Success: “Preliminary development limits loaded, but {gap} of {total} could not be checked” or “Preliminary development limits loaded for {total} dimensions”; then “A rules-derived estimate requiring professional review, not a maximum permitted building.” | L: count, incomplete/complete scope and qualification; keep accessible output. |
| ME-09 | “Preliminary development limits are not available in this environment.” | L→V feature unavailable, distinct from outage. |
| ME-10 | “Preliminary development limits not loaded: the request was too large to send.” | L→V size refusal. |
| ME-11 | “Preliminary development limits not loaded: the lot context was refused.” | L→V input refusal. |
| ME-12 | “Preliminary development limits not loaded: something went wrong on our side. This is safe to retry.” | L→V recoverable internal failure. |
| ME-13 | “Preliminary development limits not loaded: the response did not match the published data contract.” | L→V invalid response, no invented result. |
| ME-14 | “Preliminary development limits not loaded: the service could not be reached.” | L→V network failure. |
| ME-15 | “Preliminary development limits not loaded: the request took too long and was cancelled.” | L→V timeout/cancellation. |
| ME-16 | “Preliminary development limits not loaded: unexpected response from the platform API.” | L→V unexpected response. |
| ME-17 | Aborted outcome emits no announcement. | Preserve no false completion. |

### 5.7 Scenario-workspace inventory

| ID / source | Text elements and states | Why it exists | Triage and proposed destination |
|---|---|---|---|
| SW-01 ScenarioWorkspace.tsx:18–26 | DraftHeadline; conditional calculationStatus; “One preliminary scenario is supplied. Alternative optimization, practical usable range and design selection are not available.”; “Objective: {output_name/No supported objective returned}”; server cap_provenance.note. | One preliminary artifact cannot imply alternatives/optimization; supported association and actual objective must remain honest. | L→V: 1 preliminary scenario scope state, objective row and scope detail; unsupported association stays visible. |
| SW-02 :32–47 | “Returned scenario figures · association not confirmed”; “These are the supplied records. They are not promoted as property limits.”; “Assumptions, integrity and coverage”; “Source and evaluation record”; “Rule, citation snapshots and source metadata”; “Complete scenario record”. | Quarantines unassociated figures and preserves reproducibility/provenance. | L→V: keep unsupported figures behind explicitly labeled disclosure; evidence drawer with assumptions/integrity/coverage and raw record. |
| SW-03 :28–42 | Composes NoScenarioBlock, UnusedFloorAreaSection, ScenarioConstraints, ScenarioAssumptions, IntegrityCheckBlock, CoverageMatrixSection. | Composed compare/evidence content. | Child obligations remain covered in their inventory; do not duplicate or drop them during consolidation. |

### 5.8 Zoning-context inventory

| ID / source | Text elements and states | Why it exists | Triage and proposed destination |
|---|---|---|---|
| ZC-01 ZoningContextPanel.tsx:48–72 | “Zoning context”; shared ZOLA_LOT_LINK_LABEL or ABSENT_BBL_MAP_LINK_NOTE; “Official designations as recorded by the source, shown next to the computed answers. Multiple districts on one lot (a split zoning lot) are all shown. Nothing here is computed — the calculated result stays in Development limits.” | DB-016 label-display-only ruling; recorded designations differ from calculated limits; validated lot link only. | L→V: Recorded zoning title, all district chips, official-map action and explicit unavailable state; paragraph migrates to context detail. Shared label literals are inventoried with AddressAutocomplete. |
| ZC-02 :73–96 | “Zoning districts”; “Commercial overlays”; “Special districts”; respectively “No zoning district is present in the official record for this lot.”, “No commercial overlay is present in the official record for this lot.”, “No special district is present in the official record for this lot.”; “Landmark and historic status”. | Every designation class plus explicit absence, never invented defaults. | L→V: structured rows; proposed “None recorded” requires test migration, never substitute “None applies”. |
| ZC-03 :111–129 | “Landmark”; “Historic district”; source value or “Unknown — not supplied”; per-value CoverageBadge; “Source for {label}”. | Missing data differs from a negative finding; per-row provenance/coverage. | L→V: unknown/coverage inline, evidence action per row. |
| ZC-04 ZoningContextControl.tsx:30–53 | “Zoning boundaries”; statuses “loading”, “unavailable”, “no nearby boundaries returned”, “loaded: {districts}”, “loaded; district labels not supplied”; “Boundary context {status}. Not a lot zoning determination.”; “NYC DCP source / ±20 ft accuracy ↗”. | Display-only layer and source accuracy do not establish parcel zoning. | L→V: layer-menu status plus Context only legend and source/accuracy detail; loading/source failure/empty result remain distinct. |

lib/architect/zoning-context.ts adds no human-facing prose; it supplies official features/status. SurveyWorkspace.tsx adds no authored visible text; it composes ArchitectShell, ReviewInbox and SurveyReviewScreen, inventoried in the survey section.

### 5.9 Concrete mockup direction

**Proposal screen.** Keep property identity in the existing shell. Beneath it: Proposal [label] · Proposed input · Not checked / Changed since check, with Run check at the right. The drawing/reference map and compact numeric model form the main work area. A side inspector groups Lot inputs, Levels and Exterior walls; each fact carries User supplied or actual provenance instead of repeated paragraphs. Numeric authority and keyboard entry remain explicitly visible/editable.

Results use Check / Proposed / Allowance / Difference / Status / Evidence columns. Failed and unchecked rows lead. Unchecked means a visible Could not check status and short reason, never an empty green cell. Why? opens the exact semantic gap. Professional review required remains visible at report scope. Mobile stacks the inspector and result sections without full-page horizontal overflow. Example proposal must be explicit if sample seeding remains. After changes, previous results must visibly become stale and cannot be reused as current evidence pending the correctness gate.

**Drawing.** Toolbar modes are Place point, Move point 2, Delete and Enter coordinates. A readiness strip says 2 of 3 points ready; incomplete coordinate cells are marked at source. Sketch → Converted coordinates shows the transition. A successful conversion shows Approximate · RMS {exact value} ft and Accuracy & source details. Loading is neutral; fallback offers coordinates and never invites clicks on an absent map. Failed conversion produces no displayed authoritative coordinates. Out-of-neighborhood, correspondence and residual refusals stay distinct. Residual is never turned into a survey accuracy guarantee.

**Variations.** Compact named draft cards carry check state, with Session only beside the title/action and explicit persistence detail. “Keep variation for this session” is proposed copy to resolve the current Save/not-saved contradiction. Comparison uses aligned check rows, provenance in both columns and preserved unchecked reasons. Selection controls replace duplicate instructions.

**Preliminary limits.** Independent dimension tiles show exact values/units or explicit gaps. The heading remains Preliminary development limits, with estimate qualification, incomplete count and conflicts. Each tile has an anchored citation/detail affordance. A separate Generated building option card represents only the actual candidate or its unavailability; it never unites independent ceilings into a permitted building. No candidate means Option unavailable plus the placement reason and manual-design action. Adoption must not be advertised based on successful fixtures.

**Scenario.** One headline objective and one preliminary-scenario scope state precede supported figures. Unsupported association remains separate and cannot become top-line limits. Assumptions/integrity/coverage remain in the evidence detail.

**Zoning.** A compact Recorded zoning list sits beside the map. All districts remain individually visible. None recorded differs visibly from Unknown — not supplied. Layer controls show context-only status and accuracy/source detail; they never assign zoning to a lot.

### 5.10 Copy-wall and interaction gates for these screens

Test paths below are under apps/web/src/components/architect/__tests__/ unless otherwise stated. Tests were inspected, not executed.

| Source anchor | Existing requirement | Required redesign gate |
|---|---|---|
| proposal-editor.test.tsx:24–42,83–88,176–205 | Non-city-record framing; session-only variation; visible route constant; numeric edit/add/delete and adoption. | Preserve provenance/freshness/manual editing; deliberately migrate developer-token assertions, rather than delete tests. |
| proposal-check-report.test.tsx:26–63,74–88,148–164 | Exact shortfall phrase; first-class CNC “matching units are not equivalence”; semantic-gap prose already in closed details; typed validation versus retry. | Exact values/units, explicit uncheckable reason and recovery. Existing suite already supports progressive disclosure. |
| proposal-outline-draw.test.tsx:127–169,171–239,320–333 | Three finite points; disabled-action explanation; no absent-map gesture invitation; exact residual; refusal types and focus restoration. | Preserve every state, accuracy and keyboard behavior. |
| proposal-outline-map.test.tsx:183–309,313–342 | Click instructions only with real map; loading is not definite absence; selected fallback is not clickable; finite counts. | State-aware modes and matching accessible announcements. |
| max-envelope-panel.test.tsx:119–205 | Claim headings, verbatim disclosure, rule version/counts/IDs, conflict and incomplete aggregate, professional review. | Claim taxonomy, per-dimension truth and headline gap/conflict state. |
| max-envelope-panel.test.tsx:221–248 | No adoption unless fitted/contained; real geometry-free/no-candidate state. | Honest availability; no inferred candidate/fake adoption. |
| max-envelope-panel.test.tsx:274–291 | Source copy wall forbids “maximum allowed building” and “demonstrated maximum” in MaxEnvelopePanel, API lib, proposal-draft, ArchitectEntry and ProposalEditor. | Do not weaken the claim-class rule to fit a mockup. |
| zoning-context-panel.test.tsx:46–185,299–321 | Every split district, each provenance, explicit empty/unknown, validated link and row coverage. | Compact rows cannot suppress a second district, unknown, provenance or coverage. |
| apps/web/e2e/proposal-editor.spec.ts:130–214,282–427,544–624 | Keyboard/pointer journeys, honest framing, conversion, answer-first order/adoption; backend proposal/envelope responses intercepted. | Preserve browser interaction gates; do not describe stubs as deployed capability proof. |

### 5.11 Coverage manifest for this section

Fully read before reviewing tests: ProposalEditor.tsx; ProposalOutlineDraw.tsx; ProposalOutlineMap.tsx; ProposalCheckReport.tsx; ProposalVariations.tsx; MaxEnvelopePanel.tsx; ScenarioWorkspace.tsx; ZoningContextControl.tsx; ZoningContextPanel.tsx; SurveyWorkspace.tsx; lib/architect/proposal-draft.ts; lib/architect/zoning-context.ts; lib/outline-bridge-api.ts; lib/proposal-checks-api.ts; lib/architect/max-envelope-api.ts. All component paths are under apps/web/src/components/architect/ and lib paths under apps/web/src/.

Then read the six component test suites and proposal-editor browser suite listed above. No deployed behavior is inferred from source comments claiming a route is mounted/unmounted; deployment reachability must be established separately.


## 6. Address entry, lot confirmation, and map states

All paths in this section are relative to `apps/web/src/` and refer to the pinned assessment commit. Shared components inherited by the legacy confirmation screen are cross-referenced in the results/evidence inventory rather than counted as independent implementations.

### 6.1 Address entry and resolution inventory

| ID | Source and lines | Visible text element or conditional family | Why it exists | Triage and proposed destination |
|---|---|---|---|---|
| AD01 | `components/address/AddressResolutionScreen.tsx:304-312` | `Find a property` / `Address lookup`; `Search an address, then confirm the official lot match.` / `Enter a street address for the city’s official Geoclient lot match.`; `Enter address manually` | Architect versus legacy route; source and confirmation sequence; fallback | Heading/control **V**, keep. Intro **L→V/R**: `Find → Review lot` step indicator and compact source caption account for the source/sequence; omit the repeated instruction paragraph. |
| AD02 | Same `:79-86` | `Resolving address…`; `Asking the city's Geoclient service for the official record. Nothing is guessed on this side.` | Actual resolve in progress; focus target on retry or candidate pick | State **L→V** spinner and `Matching address`; city source in details. Repeated no-guess assurance **R** after preserving the behavior. |
| AD03 | `components/address/AddressForm.tsx:69-88` | `House number`; placeholder `e.g. 120`; `As it appears in the postal address.` | Manual structured query | Label/example **V**, retain. Hint **R** from the main surface or field help. |
| AD04 | Same `:90-109` | `Street`; `e.g. Broadway`; `Street name only — the city's service normalizes spelling.` | Distinguishes street-name field from a full-address query | **L→V** compact `Street name only` hint; normalization explanation in help. The manual-fallback mismatch below must be resolved deliberately. |
| AD05 | Same `:111-133` | `Borough`; `Choose a borough…`; Manhattan, Bronx, Brooklyn, Queens, Staten Island; `The city's service needs a borough or a ZIP code.` | Connector requires borough or ZIP; no borough guessed | Labels/options **V**, retain; requirement **L→V** as one `Borough or ZIP` grouping. |
| AD06 | Same `:135-157` | `ZIP code (alternative to borough)`; `e.g. 10007`; `Optional when a borough is chosen.` | Alternative area identifier | **L→V**, compact optional ZIP field; shared grouping replaces repetitive explanations. |
| AD07 | Same `:159-167` | `Resolve address` | Explicit submission; only both-blank input makes it inert; server validates | **V**, retain explicit action, without new local validation or automatic lot selection. |
| AD08 | `components/architect/AddressAutocomplete.tsx:169-170,196-207` | `Street address`; `Enter a New York City address`; listbox accessible name `Official NYC address suggestions`; dynamic house number/street, borough and ZIP; `All five boroughs`; `NYC Planning address suggestions`; decorative `↗` | Candidate source and accessible combobox; suggestion is not the authoritative BBL | **L→V**, preserve identity and accessible names. Compact clickable NYC Planning source caption can replace the separate long hint. |
| AD09 | Same `:16,209-215` | `Search this full address`; `Use manual entry with this address` | Full-address recovery differs from autocomplete; manual fallback preserves typed text | **V**, retain genuine actions beside the error, instead of instructions telling users to find buttons elsewhere. |
| AD10 | Same `:152-166` | `Searching the city’s full address service…`; `Searching official NYC addresses…`; `Keep typing the full address (at least 3 characters).`; `{N} address suggestions. Use arrow keys to choose, then Enter.`; `No matching address found in the city’s records. Search the full address, or use manual entry or BBL below.` | Separate loading, incomplete input, populated suggestion list and zero results; live keyboard help | **L→V**, distinct statuses. Count can be visible, keyboard instruction accessible help, zero result paired with actual recovery controls. Never label an outage as no match. |
| AD11 | Same `:39-46` | Six autocomplete errors: `rate-limited right now`; `taking too long to suggest`; `temporarily unavailable`; `didn’t accept that search`; `Couldn’t reach … Check your connection`; `returned a response we can’t read safely`. Each then names `Search this full address`, manual entry and BBL. | Typed causes; retained input; real recovery. DB-006 distinguishes rejected query from source outage; DB-009 prevents copy/action label drift. | **L→V**, six distinct state reasons and appropriate actions survive. Short state heading with buttons replaces multi-option prose; technical reason remains in details. |
| AD12 | Same `:53-60` | Six full-search failures: rate-limited, taking too long, source unavailable, rejected, connection failure, unreadable response. Each points to manual entry or BBL, not the just-failed full search. | DB-024(a) prevents circular recovery | **L→V**, state plus manual-entry/BBL controls. Never instruct the user to perform the very operation just reported failed. |
| AD13 | `components/address/AddressOutcomeCards.tsx:36-50,56-81` | `Reference id for support and server logs: {id}`; `Retry address lookup`; `You entered: {address} ({area})`; `Geosupport return code: {code} — {message}`; `Second return code: {code} — {message}`; `none` for absent codes | Trace, recovery, faithful input echo, both official reasons | Identity/raw reasons **L**. IDs/codes **L→V** technical drawer. Actions **V**. Existing not-found/rejected contract says both reasons never hidden; review required before relocation. |
| AD14 | Same `:89-102` | `Edit the address`; `Look up by BBL instead` | Recovery from official rejection/no match | **V**, retain prominent recovery pair. |
| AD15 | Same `:115-124`; `SuggestionChooser.tsx:31-70` | `Which of these did you mean?`; city returned more than one match, choose, platform will not guess; `Possible street matches, in the city’s own order`; dynamic street names; `(street code {code})`; `Use this address` | Caller selects: source order, no default selection, ranking, or recommendation | **L→V**, labelled selection list and `Multiple matches` state. Raw names/order survive; street code secondary. Selection semantics replace repeated no-guess narrative. |
| AD16 | `AddressOutcomeCards.tsx:137-147` | `No matching address in the city’s records`; source has no matching record, not a system failure; input echo, both GRC lines, recovery, support id | Official negative result is distinct from outage | **L→V**, `No match` state, source reason, input and actions. Never fold into unavailable. |
| AD17 | Same `:160-171` | `The city’s address service rejected this address`; source judged address unresolvable, exact source reasons; shared echo/GRC/recovery/id | Official rejection distinct from no-match or infrastructure failure | **L→V**, rejected state and exact escaped reason; `City response` label can replace framing paragraph. |
| AD18 | Same `:184-202` | City answered in unrecognized form; not trusted/interpreted and NOT not-found; worth reporting; `Reported status: {token}`; retry/id | Unknown future status must not become false negative/trusted result | **L→V**, visible interpretation failure; token/support metadata in details, no fabricated result. |
| AD19 | Same `:215-221,302-332` | `That address can't be read yet`; connector `outcome.message`; `Failure type: invalid_input (HTTP …)`; `Edit the address` | Connector is validation authority; preserves actual reason | Reason/action **L/V**, visible by form. HTTP/type **L→V** technical detail. |
| AD20 | Same `:222-228` | `Address lookup isn't configured on our side`; missing platform credential; input fine; retry cannot help until fixed | No false user blame or useless retry | **L→V**, configuration-specific reason and valid alternate journey; no retry action falsely presented as helpful. |
| AD21 | Same `:230-237` | `Our access to the city's address service was refused`; credential refused, server-side issue, possibly transient, retry safe | Auth failure distinct from user input | **L→V**, distinct reason and real retry action. |
| AD22 | Same `:238-244,310-314` | `The city's address service is throttling us`; temporarily limited requests, input fine, retry shortly; optional `The service asked us to wait before retrying: {retryAfter}` | Rate limiting and server wait guidance | **L→V**, short busy state with actual wait value retained; do not invent countdown semantics/units absent from the source. |
| AD23 | Same `:245-258` | `The city's address service is unavailable`, several attempts, input fine, retry safe; `The city's address service timed out`, no timely response, input fine, retry safe | Outage versus timeout | **L→V**, distinct state labels and retry, full cause in detail. |
| AD24 | Same `:259-276` | Unreadable city response, nothing trusted, platform attention, retry likely same; platform request budget exhausted, unfinished lookup, input fine, safe retry | Unsafe data withheld; typed budget state handled even if endpoint currently documents it unreachable | **L→V**, reasons and incomplete-result posture survive; never a generic no-match. |
| AD25 | Same `:277-284,316-333` | `Something went wrong on our side`; internal failure, input fine, id identifies failure; every typed card has `Failure type: {state} (HTTP {status})`, conditional retry and support id | Traceable platform error and state-specific retry matrix | **L→V**, visible error/action; HTTP, state and ID in diagnostics. |
| AD26 | Same `:350-354`; `lib/address-api.ts:363-368` | `Could not reach the platform API`; API unreachable, nothing resolved, safe retry; retry | Client transport failure without HTTP document | **L→V**, preserve no-result truth and recovery. |
| AD27 | `AddressOutcomeCards.tsx:366-373` | `The address lookup took too long`; API did not answer within `{seconds}`, cancelled, input fine, no partial result, retry safe; retry | Client timeout differs from upstream timeout; no stale partial result | **L→V**, short timeout status; duration/cancellation detail survives. |
| AD28 | Same `:394-411` | `Unexpected response from the platform API`; HTTP/state pairing or missing recognized machine state; not not-found; untrusted body; retry/id | Contract pairing validation | **L→V**, visible unexpected-response state with full diagnostic pairing available. |

**Manual fallback issue:** `AddressResolutionScreen.tsx:220-229` preserves the entire original one-box text by copying it into `Street`, clears house number/borough/ZIP, and focuses that field. This is honest input preservation, but the resulting form says “Street name only.” A visual redesign should show the preserved original query distinctly and clearly identify the structured fields still needed. Silently parsing/reassigning it would be a functional change requiring a separate contract review; it is not a copy fix.

### 6.2 Address-match confirmation inventory

| ID | Source | Text element / branch | Why it exists | Triage / destination |
|---|---|---|---|---|
| AC01 | `AddressConfirmCard.tsx:185-201` | `Is this the right lot?`; matched address and optional ZIP; fallback explains no printable normalized street and BBL is the result | Human lot confirmation, no invented address | **L→V**, prominent matched address/BBL; compact absent-address state with identity detail. |
| AC02 | Same `:204-234` | `You searched for {raw input}`; alongside city-matched address so user can compare; identity carried forward is tax lot BBL; no-matched-line branch omits reference to city match | DB-026 typed input differs from picked suggestion and city match; DB-033/035 a11y and absent-line honesty | **L→V**, labelled `Entered` and `City match` rows, BBL `Lot identity`; explanation in `Why different?`. Full visible/raw identity remains correctly accessible. |
| AC03 | Same `:236-257` | City resolved address with warnings, exact received warnings do not block; raw GRC/GRC2 messages; return-code pair | Usable result may carry warnings; both reasons must survive | **L**, currently required visible above Continue. First-phase compact strip keeps raw messages visible; collapsing them requires explicit review and test-contract migration. |
| AC04 | Same `:259-275` | `Tax lot (BBL): {canonical}`; optional `· building (BIN) {bin}`; invalid identifier branch says no valid canonical BBL and cannot link onward | BBL owns lot identity; BIN is distinct; invalid text never forms links | **L→V**, compact metadata and one blocked-identity state. |
| AC05 | Same `:278-293`; `AddressAutocomplete.tsx:23-31` | `Open ZoLa`; `The city map link needs a valid BBL, which this lot did not provide.` | Validated official map escape hatch; exact shared copy | **L→V**, map action; one blocked-identity state can explain unavailable map and Continue, subject to coordinated shared-copy review. |
| AC06 | Same `:307-322` | `Where this came from`; source or `not stated`, endpoint host, retrieved time; both return codes | Provenance and safe source identity | **L→V**, current collapsed disclosure is appropriate; reusable source label only through coordinated change. |
| AC07 | Same `:323-347` | Connector reference ID explicitly distinct from HTTP ID; response digest; `Request parameters, as sent:`; dynamic key/value list | Trace/reproducibility and distinct IDs | **L→V**, technical disclosure; replace layout-dependent “below” with neutral labels. |
| AC08 | Same `:349-372` | `Source facts (original value → normalized value):`; dynamic field/original/normalized values with `(absent)`; withheld-facts reason; official match transported as received, not platform rule-reviewed | Source fidelity and retrieval confidence not legal verification | **L→V**, source table and compact `Official match · Rules not reviewed`; never promote retrieval confidence to Verified. |
| AC09 | Same `:377-398` | `Continue with this lot`; no-valid-BBL branch says cannot continue and use BBL lookup; `Not my property` | Explicit validated-BBL handoff and recovery retaining input | **L/V**, one dominant Continue and secondary edit/recovery; shared blocked-state detail accounts for absence. |
| AC10 | Same `:23-26,420-431` | `City record address: {record}`; PLUTO record can differ from matched frontage; one tax lot may front multiple streets; support footer | DB-032/033 corner/frontage identity explanation; optional late fetch cannot shift CTAs | **L→V**, conditional third identity row `PLUTO record` with `Why different?`. Initially preserve placement after both actions/before footer; moving it requires proof of stable layout. |
| AC11 | Same `:138-176,420` | Equal/absent/error/route-absent/loading optional record outcome intentionally has no line or placeholder | Accepted nonblocking optional channel and no fabricated record | **L**, no invented “same” or “none” for absent/error, no generic warning added merely to fill space. |

### 6.3 Lot map text and state inventory

| ID | Source | Text element / branch | Why it exists | Triage / destination |
|---|---|---|---|---|
| M01 | `LotOutlineMap.tsx:324-334` | Architect `Approximate outline · ±20 ft · NYC Department of City Planning / MapPLUTO`; legacy dynamic accuracy and attribution | Display geometry must not imply survey accuracy | **L**, keep concise accuracy/source physically attached to map. This is an existing successful compact pattern. |
| M02 | Same `:617,621-626,646` | Region `Approximate tax lot outline`; `Selected lot`; `Recenter lot`; `Preparing map…`; each basemap/label layer loaded/unavailable/loading; accessible interactive-map label | Selection legend, navigation, independent layer status, accessible identity | **L→V**, retain key/action; compact incomplete/error layer state with full statuses in layer panel. Never announce drawn parcel from layer creation alone. |
| M03 | Same `:631-634` | `Loading the approximate lot outline…` | Loading is not a blank map | **V**, skeleton/spinner with truthful accessible status. |
| M04 | Same `:655-663` | Outline exists but map could not render; open ZoLa; accuracy/source retained | Geometry exists independently of successful rendering | **L→V**, contained `Map couldn’t render` state with actual ZoLa action and detail. |
| M05 | Same `:670-678` | Browser cannot open interactive map `(no WebGL)` although outline exists; ZoLa; accuracy/source | Browser capability is distinct from missing geometry | **L→V**, specific unavailable state; WebGL explanation progressive. |
| M06 | Same `:683-690` | Official geometry not usable, no drawn shape; ZoLa; accuracy/source | Guards unusable coordinates despite single-lot outcome | **L→V**, unusable-source-geometry state; never substitute a shape. |
| M07 | Same `:694-702` | Condo unit has no own MapPLUTO polygon; billing lot holds merged complex outline; ZoLa | Unit identity differs from land/billing polygon | **L→V**, `Condo unit · No individual parcel outline`, relationship visual and expanded billing-lot explanation; no silent automatic substitution. |
| M08 | Same | Other no-outline branch: official source returned no lot for this BBL; ZoLa | Official no-feature result | **L→V**, distinct `No parcel returned`, not render failure. |
| M09 | Same `:705-714` | Multiple parcels returned, review before trusted outline, platform never silently picks one; ZoLa; source/accuracy | No arbitrary first-pick geometry | **L→V**, `Multiple parcels · Review needed`; source reason retained. |
| M10 | Same `:717-724` | Official geometry not usable; no outline; ZoLa; source/accuracy | Typed invalid-geometry outcome | **L→V**, same visual family as unusable geometry with cause retained. |
| M11 | Same `:729` | `Map sources and limitations`; accuracy/attribution; basemap and labels link `City of New York, CC BY 4.0`; tile capture dates not supplied, reference context not current survey; selected MapPLUTO lot; no map-derived dimensions or zoning calculations | Source license, unknown vintage and display-only boundary | **L→V**, retain current disclosure and attribution link; visible compact approximation persists. |
| M12 | Same `:730-735` | Route absent in this environment versus outline could not be loaded/address unaffected; ZoLa | Disabled feature differs from error; optional map failure does not invalidate address | **L→V**, contained map state, not a full-page warning. |
| M13 | Same `:283-320,627-628` | Live summaries for initial loading, unusable geometry, render failure, browser failure, parcel pending, actually rendered approximate outline ±20ft, condo/no-feature, multiple, invalid, route absent, fetch failure/address unaffected; aborted silence | Announced result must match actual visible rendering | **L**, preserve synchronized live region; do not replace meaning with color/icon alone. |

`lib/lot-geometry-api.ts:279-283` also populates a `disclaimer` (fallback: “Provided by NYC DCP for informational purposes only; not a legal boundary survey.”), notes and source fields. `LotOutlineMap` does not render those particular fields. These are not visible disclosures to mark as deleted; separately verify whether actual rendered accuracy/source text covers the required disclaimer. Adapter transport messages at `:342-344,420-422` are similarly not rendered verbatim; the component uses its typed fallback.

### 6.4 Legacy property-confirmation inventory

`components/confirm/ConfirmScreen.tsx` composes shared `InternalBanner`, `ZoningSection`, `ConflictsSection`, `CoverageLegend`, `CoverageBadge`, `ProvenanceDisclosure`, `LoadingStages`, `OutcomeFailureStates` and `OutcomeAnnouncer`. Their common text is covered by the corresponding shared inventory; the following rows inventory this screen’s own text and overrides.

| ID | Source | Text element / branch | Why it exists | Triage / destination |
|---|---|---|---|---|
| LC01 | `ConfirmScreen.tsx:449-457` | `Step 2 — Confirm the property`; review official facts for BBL before analysis; same canonical profile and validated contract as Property screen | Workflow and source consistency | Step **V**; implementation-contract narrative **R** from product surface, with provenance still accessible. |
| LC02 | Same `:188-201` | `BBL {bbl}`; normalized address/borough/ZIP; missing address with conflict-section pointer | Identity and honest absence | **L→V**, address primary, BBL secondary, compact absence plus actual conflict link. |
| LC03 | Same `:205-217` | `BIN`; IDs or not-yet-retrieved/connector-future/unknown-never-guessed paragraph; `Geometry`; recorded type/no assumed outline OR not-in-profile/future MapPLUTO/unknown paragraph | Known versus missing records; no imaginary geometry | **L→V**, `BIN: Not retrieved`, `Geometry: {type}/Not included` with reasons on demand. Future connector narration **R** after current gap preserved. |
| LC04 | Same `:220-225` | `Data completeness`; dynamic headline and raw enum in parentheses | Reported profile completeness | **L→V**, labelled chip with definition, raw enum in diagnostics. |
| LC05 | Same `:231-249` | `Lot summary`; all columns still on Property screen/nothing hidden/display summary paragraph; Lot area, Lot frontage, Lot depth, Lot type code, Irregular lot with values/units | Compact official summary, not exhaustive data claim | Values **L/V**; self-explanation **R**, replaced by working `All property records` disclosure/link. |
| LC06 | Same `:90-114` | Per missing field: not in official record/listed in missing inputs OR not in profile; both unknown-never-guessed. Present values have coverage badge and `Source for {field}`. | Distinct absence causes and field source | **L→V**, `Unknown` cells and field-specific reason/source detail; no repeated sentence per cell. |
| LC07 | Same `:252-265` | `Existing building`; Building floor area, Number of floors, Residential units, Total units, Year built, Building class; values/units/status/source/missing branches | Existing records are distinct from development limits | **L→V**, collapsed record group/toggle per owner preference, all actual records retained. |
| LC08 | Same `:268-277` | Shared zoning; `Mapped features`; landmark/historic/flood flags appear below, each shown once | Avoids duplicated flags | Heading **V**; self-narrating layout note **R**, grouping/navigation supplies location. |
| LC09 | Same `:279-300` | `Landmark, flood, and pending flags`; Landmark, Historic district, 2007 FIRM flood flag, 2015 preliminary FIRM flood flag; values/status/source | Official flags with specific vintage, not blanket current determination | **L→V**, concise rows/chips retaining full vintage in source details; never relabel historical flags “Flood safe.” |
| LC10 | Same `:133-156` | Missing flag not in official record OR not in profile; unknown-never-assumed-absent; `Source for {label}` | Omission/null is not No | **L→V**, labelled Unknown and exact reason; no green all-clear. |
| LC11 | Same `:293-297` | `Pending land-use actions`; not yet retrievable/no connector for pending land-use and zoning-map changes/unknown not none | Unsupported category remains unknown | **L→V**, `Pending actions: Not checked` and why detail; connector internals move, unknown stays visible. |
| LC12 | Same `:308-315` | `Questions the official data cannot answer`; everything above official, only items below need user, government answers never asked twice | Intent and unresolved inputs only | Heading **V**, intro **R**; actual inputs or explicitly read-only gap list clarify purpose. |
| LC13 | Same `:317-323` | `What do you intend to build or change?`; objectives user choice, not government record; selection awaits future workflow | Intent is user input but control absent | **L→V**, compact unavailable capability state rather than apparently answerable question; future-work paragraph **R**. |
| LC14 | Same `:325-335` | `Can you provide {field}?`; critical official input missing, optional source reason, never guessed | Critical gaps cannot be defaulted | **L→V**, Required inputs list, reasons in row detail and honest save availability. |
| LC15 | Same `:337-347` | `Which value of {field} is correct?`; sources disagree; conflict pointer; future recording; not auto-resolved | Conflict unresolved; no pretend persistence | **L→V**, source comparison table and Unresolved state; no fake saving interaction. |
| LC16 | Same `:350-355` | No critical gap/no unresolved conflict in this property record; intent remains open | Empty state for specifically tested categories | **L→V**, specific no-critical-gaps-in-profile/no-unresolved-conflicts statuses, never general Verified or complete-zoning conclusion. |
| LC17 | Same `:357-372` | Disabled `Confirm facts (not yet available)`; cannot save confirmations/overrides; `user_confirmations` contract/API/later milestone; nothing persisted or auto-confirmed | Current read-only capability truth | Persistence/auto-confirm **L→V**, `Read-only review · Changes are not saved`; schema/API/milestone narration **R**. Disabled control can leave only after its unavailable capability remains explicitly accounted for. |
| LC18 | Same `:377-393` | `Next step`; continue to Step 3 draft engineering, never Verified, does not pretend otherwise; `Compare preliminary scenario`; `Back to property lookup` | Navigation and draft-only posture | **L→V**, action adjacent to Draft state and review limitation; repeated defensive sentence **R**. |
| LC19 | Same `:467-468` | Failure branch `Back to property lookup`, shared failures | Recovery | **V**, keep actual control. |
| LC20 | Same `:493-506`; `lib/bbl.ts:36-68` | `No property selected`; valid 10-digit BBL required in URL, example route; no BBL or invalid BBL with validation message; `Go to property lookup` | No silent default lot/deep-link validation | **L→V**, concise missing/invalid state and lookup action; route syntax in technical detail. |
| LC21 | `lib/bbl.ts:42,49-51,58,67-68` | Enter 10-digit BBL; digits only/no dashes/spaces/letters/example; exactly 10 digits with entered count; first digit 1–5 with borough mapping | Actionable format errors; server remains authority | **L/V**, short error with specific reason; borough mapping in help when needed. |
| LC22 | `lib/format.ts:9-23,233-234` | Values: `—`, exact-precision localized numbers, Yes/No, strings/JSON; unknown label `{field} (source column — label pending review)` | No invented interpretation/precision loss, reviewed labels | **L**, compact presentation must not turn missing into zero/No or silently invent field meaning. |

### 6.5 Accessible announcements are retained content

`lib/announce.ts:20-53` supplies the shared property/confirm outcomes: successful profile with BBL; official no-record; API rejected BBL; source throttling/unavailable/timeout/schema change; internal error; invalid profile refused; contract mismatch; API unreachable; cancelled client timeout; unexpected response; aborted silence.

`lib/announce.ts:65-111` supplies address outcomes: single-lot resolved; resolved with warnings; multiple candidates; official no matching record; rejected as unresolvable; unrecognized status; each invalid-input/configuration/auth/rate-limit/source/timeout/unreadable/budget/internal error; API unreachable; client timeout; unexpected response; aborted silence.

These are **L** equivalents for assistive technology, not removable excess prose. Keep one synchronized arrival announcement, correct outcome focus, retry focus, and repeated-identical-outcome announcement. Compact visible states must not leave accessible status describing an earlier or nonexistent result.

### 6.6 Specific copy and interaction gates

| Test anchor | Protected contract | Redesign implication |
|---|---|---|
| `address/__tests__/address-confirm.test.tsx:188-241` | Thin card; question/address/BBL/one dominant action; raw warnings above Continue, role status, never blocking | Compact warnings can be restyled; hiding them needs explicit reviewer agreement and test migration. |
| `address/__tests__/address-resolution.test.tsx:340-360,438-510` | Both raw warning messages; both GRC codes/messages on not-found/rejected; echoed input; actual recovery; unknown status never no-match | No generic error catch-all; relocation of required source reasons is gated. |
| Same `:511-628` | Distinct phrase per error, HTTP/state pairing, retry matrix, connector invalid-input message, no server-side blame, retry-after | Some phrases are presentation locks protecting semantics. Replace only with approved invariant assertions, not weaker coverage. |
| `address/__tests__/address-confirm.test.tsx:352-416` | Provenance collapsed by default; source/host/both GRCs/two IDs/digest/params/facts/withheld reason; not Verified | Existing progressive disclosure is accepted; every field still needs a destination. |
| Same `:465-487` | Exact shared Open ZoLa label and absent-BBL note | Coordinate shared-copy migration across all consumers. |
| Same `:495-660` | Typed text retained apart from picked and matched addresses; BBL carried forward | Two/three-row identity design must preserve all distinct identities and full accessible correspondence. |
| Same `:667-799` | PLUTO record only when different; equal/absent/error no line; never blocking | No invented same/none values or new blocking state. |
| Same `:809-1208` | Record note after both actions/before Meta; delayed insertion preserves CTA position; no reserved box; full accessible input; no nonexistent match reference; exact normal-case sentence; why-different note | Cleaner grouping can require structural-test migration. Prove stable actions and full identity truth at 360/768/1280 first. No-reserved-box is an accepted implementation contract, not a timeless statutory requirement. |
| `architect/__tests__/autocomplete.test.tsx:50-153` | Six failures; retained query; full-search recovery on timeout; shared exact button label; incomplete/no-match distinction; manual prefill; no first-pick acceptance | Maintain real recovery and typed distinctions while shortening narration. |
| Same `:277-307` | Full-search failure never points back to itself; suggestion failure may point to full search | Recovery design must know which operation failed. |
| `address/__tests__/lot-outline-map.test.tsx:229-443` | Exact polygon/multipolygon/rings; attribution and ±20ft visible without WebGL; distinct condo/no-feature/multiple/invalid/route/fetch outcomes | No fabricated boundary or selected first feature; accuracy remains attached to map/fallback. |
| Same `:581-592` | Proposal wrapper observes map aria-label and loading test ID | Renames must coordinate with drawing wrapper. |
| Same `:751-844` | Parcel-render proof before announcing drawn; bounded fallback; street-layer failure leaves usable parcel; compact accuracy/source | State chips follow actual parcel rendering, not fetch/layer installation. |
| `confirm/__tests__/confirm-screen.test.tsx:23-117` | Record groups, units/human labels, unknown BIN, unknown pending connector, conflict empty state, legend, only intent/gaps/conflicts asked, save unavailable/no auto-confirm, no Verified/best | Preserve coverage and truth while regrouping. API-details paragraphs are not intrinsically required even where substrings are pinned. |
| Same `:175-295` | Single arrival announcement/focus/retry, flags shown once | Preserve accessible journey and deduplication. |

No local tests were run. These are read-only findings from test code.

### 6.7 Mockup-level direction and task-specific acceptance

**Search landing.** One restrained search panel with `Find a property`, a full-address input, explicit search and compact NYC Planning source. Two quiet alternatives: Enter manually and Use BBL. Suggestions show street address then borough/ZIP, with controlled dropdown height. Empty/error state occupies that same region and supplies actual recovery buttons. A failed full-search promotes manual entry/BBL; it does not instruct the same failed search. Preserve keyboard combobox behavior, no default candidate, explicit selection and raw typed text.

**Manual entry.** Four labelled inputs with a shared Borough-or-ZIP grouping. Show the retained original full query separately during fallback so the Street field is not mistaken for a successfully split address. Required fields and connector-specific errors are visible. Parsing or normalization would be a separately scoped functional change.

**Lot review.** Desktop map roughly 60% / identity-action panel 40%; mobile identity headline, compact map, comparison rows, actions. Large city-matched address, secondary BBL, rows for Entered/City match and conditional PLUTO record. A Why different disclosure holds frontage explanation. Continue and Edit occupy a stable action area. First phase leaves late-arriving PLUTO content in its accepted after-actions position; a later relocation proves unchanged CTA positions, long-address wrapping and accessible order at all tested widths.

Warnings remain above Continue with raw source content visible in the first phase. Replace broad warning boxes with a restrained icon/text strip whose severity is accurate. Codes/IDs join one Source details drawer. Missing canonical BBL becomes one coherent blocked identity state explaining why both map link and Continue are unavailable, after shared-copy/test review. `Official match` never implies rules verified.

**Map.** Persistent compact `Approximate · ±20 ft · MapPLUTO` footer; selected-lot swatch and accessible recenter action; a sources/layers control holds detailed layer states, license, unavailable vintage, survey limitation and no-calculation boundary. Failure is contained within map region with a specific reason and actual ZoLa action. Condo, no parcel, multiple parcels, browser failure and fetch failure remain different states. Do not claim displayed geometry until rendered-feature proof exists.

**Legacy review.** Compact identity and five lot facts; zoning identifiers and a concise exception strip. Group Property, Existing building, Source conflicts, Missing inputs, Sources. Existing-building facts collapse by default. Unknown cells use labelled Unknown plus field-specific reasons. Landmark/flood/pending statuses retain source/vintage and never imply general all-clear. A narrow read-only/not-saved state replaces schema/API exposition; Draft remains adjacent to the preliminary comparison action. Critical gaps and unresolved conflicts remain visible enough to prevent an apparent ready/verified conclusion, with detailed source comparisons expandable.

These changes need focused acceptance cases for: all six suggestion errors and nine resolution-error states; absent/invalid BBL; typed/picked/matched/PLUTO address differences; official warnings; delayed record insertion; ambiguous choices; condo/no parcel/multiple parcel; unusable geometry; no WebGL; partial basemap failure; accessible announcements; retained input; and real recovery actions. Do not weaken existing tests to make a screenshot cleaner.

### 6.8 Read manifest for this section

Source read: `components/address/AddressConfirmCard.tsx`, `AddressForm.tsx`, `AddressOutcomeCards.tsx`, `AddressResolutionScreen.tsx`, `LotOutlineMap.tsx`, `SuggestionChooser.tsx`; `components/architect/AddressAutocomplete.tsx`; `components/confirm/ConfirmScreen.tsx`; `lib/address-search.ts`, `address-api.ts`, `lot-geometry-api.ts`, `record-address.ts`, `announce.ts`, `format.ts`, `bbl.ts`.

Tests read: `components/address/__tests__/address-confirm.test.tsx`, `address-resolution.test.tsx`, `lot-outline-map.test.tsx`; `components/architect/__tests__/autocomplete.test.tsx`; `components/confirm/__tests__/confirm-screen.test.tsx`.

## 7. Results, condo records, evidence and printed brief

### 7.1 Findings and classification

The source supports the owner's complaint. Development limits combines a Draft badge, calculation-status sentence, reference/evaluated FAR distinction, draft-cap heading, FAR-only/envelope limitation, scenario status, wide-street conditions, another legal-review sentence, three bulk-status rows, assessment-coverage sentence and repeated source links. The default source inspector adds another draft/professional-review statement. The accumulated presentation creates the burden, even where individual meanings are necessary.

Existing code already permits progressive disclosure: exact scenario status lives inside Result scope and source wording; existing buildings and raw records collapse; reviewer-directed tests explicitly move server jargon out of the wide-street answer panel. The redesign can extend an accepted pattern.

In these tables, L means legally sensitive or product-required honesty that must survive; it does not assert that a statute mandates the exact sentence. L→V means preserve that meaning as an immediately legible state plus accessible progressive detail. V denotes structural text/control that can be reorganized. R is restricted to duplicate narration/navigation after a named replacement exists. Dynamic text families include every instance returned by the cited renderer, including all reasons, facts, citations and raw records; source-derived words are not inferred here. Paths in tables are relative to apps/web/src/components/architect unless explicitly prefixed otherwise.

### 7.2 Shell, development limits and identity inventory

| ID / source | Visible text or dynamic family | Why it exists | Triage and proposed destination |
|---|---|---|---|
| A01 ArchitectShell.tsx:16–28 | Skip to workspace; NYC BUILDABILITY; Internal development build; Navigation | Accessibility, identity, environment disclosure, mobile navigation | V for controls; L→V for environment. Keep skip link and accessible menu. Compact environment badge/disclosure must remain available on mobile. |
| A02 ArchitectShell.tsx:32–46; lib/architect/navigation.ts:4–9 | Search property; Property workspace; Overview; Property facts; Zoning; Scenarios; Proposal editor; Evidence; Documents; Open issues; Report; Survey review / Unavailable; Planning tools; Envelope / Units / Financials, each Planned | Route discovery and honest unavailable states | V. Task-oriented navigation; planned tools can move into an explicit Planned tools disclosure, never imply availability. |
| A03 ArchitectShell.tsx:47 | Preliminary analysis; Professional review required | Non-final reliance framing | L→V. Coordinate one persistent workspace status with result status and disclaimer. R only for a duplicate occurrence after replacement is recorded. |
| A04 PropertyOverview.tsx:31–47 | Unresolved data conflicts; every affected field label; Review conflicting source values →; Critical inputs missing; every critical-field label; Review missing inputs →; The property source is stale. Captured dates and retrieval status are available in Evidence. | Immediately surfaces unresolved conflicts, critical gaps and stale source | L→V. One active-issue strip with distinct categories/counts. Critical field names stay visible; source comparisons/reasons expand. Staleness becomes a dated state with retrieval detail. |
| A05 DevelopmentLimits.tsx:23–29 | Rule details incomplete; Numerical summaries are unavailable. The returned record is preserved below.; Captured unusable rule-evaluation record | Inspectability fail-safe with lossless record | L→V. Blocked-result state, Why unavailable?, captured record. Never silently disappear or show an untrustworthy number. |
| A06 DevelopmentLimits.tsx:32–47 | Draft zoning floor-area cap; value + sq ft / Not calculated; FAR only · Buildable envelope not assessed; Conditional / Professional review required / Data conflict / Unsupported / Not applicable; Result scope and source wording; Recorded coverage: exact enum; verbatim scenario.cap_label and every scenario.reason | FAR cap is not buildable envelope; canonical coverage/scope/reasons survive | L→V. One large cap cell with attached FAR only and Envelope incomplete text labels; adjacent scope disclosure. Never rename this Buildable area. |
| A07 DevelopmentLimits.tsx:73–94 | Wide-street conditional FAR versus Governing floor-area ratio; Draft; value / Not calculated; Professional review required — the higher wide-street floor-area ratio is withheld until a qualified reviewer confirms the determination. | Higher conditional, conservative governing and withheld values are different states | L→V. State-specific row, explicit label and withholding next to value; standard FAR must not receive conditional-FAR label. |
| A08 same | {valueLabel} — a dimensionless ratio. Floor area = FAR × zoning-lot area (sq ft).; Applies within 100 ft of a wide street. / Outside 100 ft of a wide street; the conservative floor-area ratio governs.; Draft — pending qualified legal review (not verified).; Wide-street sources and provenance → | Units, applicability, legal-review scope, traceability | L→V. Visible condition and ratio labels; formula definition and exact source wording in Why this FAR?; one row source control. Copy-wall migration required before wording changes. |
| A09 DevelopmentLimits.tsx:111–125 | Development limits; Draft; dynamic calculation status; Residential FAR · city record; value / source status; PLUTO reference · version; Source for residential FAR / View source records →; Evaluated residential FAR; value / Not calculated; Draft rule result / No supported rule result supplied; Rules and calculation → | Prevents recorded FAR masquerading as evaluated result | L→V. Explicit City record / Rule evaluation comparison with one source action per row. Both values remain when different; no reference-to-result promotion. |
| A10 apps/web/src/lib/architect/development-limits.ts:155–180 | Zoning boundary check unavailable; Zoning boundary check incomplete; Conflicting property data; Lot boundary requires review; Conflicting boundary results; Conflicting rule results; Condo base lot needs site confirmation; Property identity mismatch; Conflicting results; Rule details incomplete · inspect captured evidence; Rule result unavailable · inspect evidence; Analysis records differ · inspect evidence; Scenario integrity check failed · inspect evidence; Rule source support incomplete · inspect evidence; Draft assessment · envelope incomplete | Branch-specific reasons for refusal/unavailability | L→V. Preserve distinct labeled states. Inspect evidence becomes adjacent control; exact reason remains reachable. Do not merge into generic Warning. |
| A11 DevelopmentLimits.tsx:130–137; helper:188–208 | Height; Setbacks and yards; Lot coverage and open space; Conflicting results / Conflicting records / Not supported / Review required / Not calculated; repeated Evidence; Lot area; value + units / Unknown; Source | Displays unavailable dimensions without inventing limits | L→V. Compact limit matrix with row Why/Source. No numeric height/yard/coverage from untyped outputs and no ungrounded envelope drawing. |
| A12 AssessmentCoverage.tsx:3–30 | Assessment coverage not supplied.; Envelope assessment incomplete. {N} checks remain open.; Assessment coverage · {N} checks; Check; Status; Residential FAR cap; Height; Setbacks and yards; Lot coverage and open space; Street wall and base height; Parking and loading; Use and overlays; Special districts and overlays; Density bonuses; Higher-density bulk and towers; Gross-to-net efficiency; raw family key; rule_status_today; · Blocks envelope | Complete assessment/check coverage and blockers | L→V. Visible envelope state and blocker count; expandable matrix. Raw keys in technical view. Unknown/unassessed never appears as Pass. |
| A13 PropertyOverview.tsx:365–390 | View zoning details →; Site context; shared ZoLa label or missing-BBL note; Existing building information; Existing building facts; All property facts → | Navigation, map and existing-building separation | V. Keep map/results split and collapsed existing buildings. R candidate for repeated zoning CTA only if persistent navigation supplies same direct action. Map absence meaning survives. |
| A14 AnalysisIdentityNotice.tsx:64–67 | {Scenario/Rule evaluation} analyzed on the base lot; paragraph identifies entered BBL, defines condo billing lot as the single tax lot a condo is billed under, identifies recorded base tax lot BBL and defines it as city-recorded land parcel; recorded as entered versus analyzed; a city record of the documented resolution, not a computed allowance; Returned {analysis} record | Legitimate stamped billing-to-base substitution must not raise false mismatch | L→V. Entered/billing and analyzed/base identity table with City-recorded mapping relationship. Inline definitions currently locked by tests; relocation requires reviewed gate. |
| A15 AnalysisIdentityNotice.tsx:72–78 | {analysis} identity mismatch / missing; Requested BBL {X}; returned BBL {Y/not stated}. Results are withheld from this property.; second paragraph naming opened/analyzed identifiers; no relationship between them is inferred; no calculated allowance is shown while they differ; returned-record disclosure | Blocks foreign/missing identity without inventing condo resolution | L→V. One alert with two labeled IDs, Results withheld and Why/record. R for duplicate narration only after neutral non-inference meaning survives. |

### 7.3 Condo records inventory

These cases must remain separate: entered unit, billing lot and land lot; single and multi-lot; unknown and recorded zoning; active and revoked/superseded human confirmation; self-attested calculation refusal; current-parcel discrepancy. A single generic condo badge would lose material distinctions.

| ID / source | Visible text or dynamic family | Why it exists | Triage and proposed destination |
|---|---|---|---|
| C01 PropertyOverview.tsx:264–267 | Recorded base lot for this condo; paragraph states the analysis runs on city-recorded land, names entered and base BBL, repeats that analysis runs on that base lot, and says this is a city mapping stated as entered versus analyzed; Source / dataset(s) / dataset version / retrieved, each with not recorded (unknown) fallback | Single-lot substitution and provenance | L→V. Paired identity rows joined by City record; source stamp and expandable provenance. R for repeated analysis-runs narration after relationship is explicit. |
| C02 PropertyOverview.tsx:306–308 | City records for this condo; These are the tax lots the city records for the condo lot you entered. They are city records of the condo's land, shown for reference under the development limits above.; conditional: The property record and the city records channel differ on this condo; the lots below are what the city records channel returned. | Records are distinct from allowances; truthful disagreement | L→V. Records heading and Reference only label; visible disagreement state. No calculated-result or allowance wording inside records panel. |
| C03 PropertyOverview.tsx:309–317 | Condo lot you entered: {BBL} (also the condo billing lot the city records for it) when equal; otherwise separate Condo lot you entered and Condo billing lot rows; Recorded base lot {BBL} — recorded zoning: {district/not recorded (unknown)} for every base lot | Distinguishes entered unit/billing/land IDs; avoids redundant equal-ID line | L→V. Identity table and base-lot/zoning rows. Preserve equality collapse and unknown billing ID; no guessed relationships. |
| C04 PropertyOverview.tsx:235–239 | Site definition: a person has recorded a confirmation to treat these base lots as one site. This is a recorded human decision, shown for reference under the development limits above; the system never selects a site on its own.; Confirmed by {name/an unnamed person} ({role}) on {timestamp}. Recorded base lots: {parcels/the recorded base lots}. | Human record is not automated site choice or calculation | L→V. Recorded confirmation state with actor/time/parcels and Human record label; detailed policy accessible. Exact fractional timestamps survive. |
| C05 PropertyOverview.tsx:238 | This confirmation is self-attested — the person's identity is not yet verified — so it is recorded for reference only and is refused for any calculation use. | Unverified identity cannot unlock calculation | L→V. Immediately visible Self-attested · Not usable for calculations state. Detailed explanation may expand; refusal may not be buried. |
| C06 PropertyOverview.tsx:239 | The base lots the city records now differ from the lots in this confirmation. This is surfaced for professional review and does not change the confirmation, which changes only by a human act. | New parcel discrepancy does not silently revoke human record | L→V. Parcels differ state next to confirmation; old/current parcel comparison and human-only-change detail. |
| C07 PropertyOverview.tsx:247 | No history: Site definition: not confirmed. No one has recorded a confirmation to treat these base lots as one site...; history: Site definition: not confirmed. A previously recorded confirmation...is no longer active — it was revoked or superseded and none has replaced it...; both end by describing development limits as standing on their honest unconfirmed footing | Distinguishes never recorded from no longer active | L→V. Not confirmed versus No active confirmation, with reason/history. R for self-descriptive honest-footing prose after state and effect survive. |
| C08 PropertyOverview.tsx:285–287,319–320 | Every returned divergent-zoning notice; mixed-gap paragraph begins Recorded zoning is not yet shown for every base lot above and names Zoning Tax Lot Database (ZTLDB), explains source not connected, unknown lots not guessed, recorded districts unaffected; all-unknown variant says these base lots and city identity records only | Unknown zoning is not no zoning; partial gap must not erase recorded districts | L→V. Unknown per row, Zoning missing for N lots summary, named ZTLDB source-gap detail. Divergence only when some zoning actually recorded. |
| C09 PropertyOverview.tsx:321 | Source: ... · dataset(s): ... · dataset version: ... · retrieved: ... with explicit unknowns | Dataset/version/capture provenance | L→V. Source footer + exact details; preserve exact values on screen and print. |
| C10 PropertyOverview.tsx:327–330 | The city records channel and the property record differ on this condo, so no city records are shown here. The development limits above govern. | Non-multi-lot disagreement; withholding remains authoritative | L→V. Conflict row, Records unavailable, direct actual-limits reference; no dangling professional-review determination above. |
| C11 PropertyOverview.tsx:332–334 | No records section for loading/unavailable/unresolved/resolver-error/non-condo | Code-level honest absence; accepted backend/profile guards remain authoritative | Do not invent records, or make a transport outage alone withhold allowances. Verify surrounding limits explain whichever refusal actually applies. |

### 7.4 Facts, zoning, issues and planned capability inventory

| ID / source | Visible text or dynamic family | Why it exists | Triage and proposed destination |
|---|---|---|---|
| F01 PropertyFacts.tsx:19–38 | Lot / Building / Identity; Lot facts / Existing building facts; Filter facts; Name, value or units...; {visible} of {total} {lot/building} fields; No facts match this filter.; Clear filter | Grouping/filtering and accurate result counts | V. Compact tab/filter toolbar with count; all underlying facts remain reachable. |
| F02 PropertyFacts.tsx:41–52 | Identity & source coverage; BBL; BIN; Profile address; Data completeness; Development intent; Profile geometry; Unknown — not supplied; Not supplied; Not recorded; Not included in this profile; Full identity record; All source and analysis status dimensions | Identity and explicit absence | L→V for values/unknowns. Definition table, short state cells, captured-record disclosure. |
| F03 apps/web/src/lib/coverage.ts:60–76 | All expected official inputs were retrieved; Some non-critical official inputs are missing; Critical official inputs are missing; corresponding full glosses | Completeness is not feasibility | L→V. Data completeness state with detail/count. Complete input data must never mean Feasible. |
| F04 ProfileViews.tsx:31–46 | Spatial evidence; Map boundaries provide context. Canonical intersection results and uncertainty are preserved below.; supplied coverage_note and every review_reason; Spatial-intersection evidence is not included in this profile.; Full spatial-intersection result; Zoning feature layers and provenance; Lot geometry status and provenance | Displayed map is not canonical intersection/uncertainty proof | L→V. Boundary assessment state with uncertainty detail; every reason and raw payload retained. |
| F05 ProfileViews.tsx:49–53 | Draft rule result, conflicts and applicability; Inspect calculation evidence → | Full rule result/trace reachable | V. One evidence control on relevant result instead of another large navigation CTA below repetitive content. |
| F06 ProfileViews.tsx:64–72 | Confirmations and overrides; Property confirmations cannot be saved in this version. Survey decisions use their separate, authorized review workflow.; Recorded review history / No recorded confirmations or overrides were supplied.; Coverage definitions and source policy | Honest unsaveable workflow and separate authorized survey review | L→V. Read only state and history; survey action only where actually available. No fake Save. |
| F07 ProfileViews.tsx:78–83 | Planned capability; {Envelope/Units/Financials} is not available in this version; No {label} model or calculation is connected. The property facts, current draft evaluation and complete evidence remain available in the workspace. | Planned route is not implemented capability | L→V. Explicit unavailable state in planned-tools area. R for repetitive directions to existing workspace tabs. |
| F08 AdditionalZoningFlags.tsx:6–15 | Additional flags; absent Landmark / Historic district / 2007 FIRM flood flag / 2015 preliminary FIRM flood flag with Unknown — not supplied; Pending land-use actions with Unknown — source not connected | Missing source is not a negative flag | L→V. Compact flag matrix with readable Unknown and explanation; never green checks for absent data. |

### 7.5 Evidence and report inventory

| ID / source | Visible text or dynamic family | Why it exists | Triage and proposed destination |
|---|---|---|---|
| E01 EvidenceInspector.tsx:29–36 | Fact evidence / Source record unavailable / Sources & review; Close; The source record for reference {id} was not supplied with this property. | Selection context and unavailable provenance | L→V. On-demand drawer with explicit selected state/error. |
| E02 EvidenceInspector.tsx:37–61 | Captured property record; source ID / Source not supplied; View this lot on ZoLa; Current PLUTO record (JSON); About this dataset / Official dataset link not supplied.; Current records may differ from the captured evidence shown here.; Release / Not published; Captured / Not supplied; Profile version; Full captured source metadata | Human-first official link, current-versus-captured distinction and metadata | L→V. Source/date summary then exact metadata. Current-versus-captured notice stays by current-record link. Default inspector need not occupy permanent space. |
| E03 EvidenceInspector.tsx:62–68 | Cached source is stale. Review retrieval details before using these facts.; Review; Draft analysis · Professional review required; Recorded confirmations: {N}; Open evidence and review history → | Staleness and review status | L→V. Dated state and history count. R for duplicate review prose only after its scoped meaning remains in shared state. |
| E04 EvidenceRecord.tsx:5–16 | Any CapturedRecord label / Full captured record; complete escaped JSON; Unknown — no record supplied | Lossless audit and safe escaped data | L→V. Final raw-record tier; retain every supplied field and do not turn unsafe captured URL into link. |
| E05 EvidenceRecord.tsx:24–34 | Captured source fact; human field label; ZoLa/current PLUTO/dataset links; No safe official dataset link is available in this record.; current-versus-captured sentence | Fact-level provenance and link safety | L→V. Fact drawer header and source-link group; absence state remains. |
| E06 EvidenceRecord.tsx:35–76 | Original field; Original value; Normalized value; Units / Not supplied; Transformation with No transformation steps recorded. Original and normalized values are shown above.; Source; Version; Captured; Effective date / Not published by the source; Source conflict; Fact review | Exact original/normalized distinction, no invented transformation/review | L→V. Side-by-side values and fact metadata, explicit missing transformation record. |
| E07 EvidenceRecord.tsx:77–81 | Review history; Recorded confirmations and overrides / No confirmation or override history is supplied for this fact.; Full captured source record | Fact-specific human audit | L→V. History and raw-record disclosures. |
| E08 EvidenceWorkspace.tsx:22–34 | Evidence; Search evidence accessible label; Search evidence... placeholder; Calculation and rule trace; Full property and review record; Confirmed address match; Source facts · {N}; every human field label; No matching source facts. | Findable evidence index | V. Master-detail layout, searchable grouped index. |
| E09 EvidenceWorkspace.tsx:38–44 | Complete property record; Every supplied field, source, conflict and review record is included below.; Profile version and generated date; Retrieval, source version and staleness; All recorded confirmations and overrides; Recorded development intent; Complete property source record | Complete record availability | L→V for records. R for announcing availability once structured index already proves what is accessible. |
| E10 EvidenceWorkspace.tsx:46–51 | Confirmed address match; address label; Selected in this browser session at {time}. BBL {bbl} remains the property identity.; Original address match and source facts | Session selection does not replace property identity | L→V. Address/BBL/time rows and This session state, original record disclosure. |
| E11 CalculationEvidence.tsx:27–38 | Deterministic evaluation; How this was calculated; Draft · Professional review required; coverage badge; every evaluation.reason; No applicable computation trace was returned. No result is inferred. | Deterministic/draft origin and no-inference gap | L→V. Summary state/reasons, not repeated broad warnings. Technical eyebrow R only if same role remains clear. State-specific review semantics need the separate DB-025/DB-030 review noted elsewhere. |
| E12 CalculationEvidence.tsx:39–55 | Wide-street determination; {Wide-street conditional FAR/Governing floor-area ratio} · D-052 provenance; Draft · verbatim draft_label and conditionally Professional review required; verbatim reason; ratio/withheld/Not calculated plus formula; verbatim fallback_direction_note; Determination; Conditional-FAR row; Exceptions checked; Named-street override pending; yes/no; Width-policy decisions and D-052 source provenance; Wide-street determination and D-052 provenance summary | Exact source wording and determination-state gating | L→V. Summary/detail/raw tiers; internal D-052 ID belongs technical tier. Conservative and conditional labels stay distinct. |
| E13 CalculationEvidence.tsx:57–73 | Applicable determination / Other determination plus rule ID / Rule identifier not supplied; repeated rule heading; Version {version/unknown} · {status} · Applicability: applies/does not apply; Inputs used; every input key/value | Applicable trace first, rule/version/input identity | L→V. Determination row with expandable inputs. R for duplicated rule heading only after same identifier is retained. |
| E14 CalculationEvidence.tsx:73–115 | Calculation steps; Step / operation; Resolved inputs; Result; every step ID/op/note/argument/result; No calculation steps recorded.; Outputs plus all output keys/values; Units are shown where supplied in the source output.; Applicability, validation and uncertainty with complete applicability_trace/input_validation/uncertainty/exceptions_applied/notes | Transparent calculation, units and validation uncertainty | L→V. Expandable trace table and output summary; absent units attached to affected output. No output meaning inferred. |
| E15 CalculationEvidence.tsx:117–140 | Rule sources; section / Section not supplied; verbatim citation quote; Snapshot {id} · Last amended {date/not supplied}; Open current official text ↗ / Official text link not supplied in a supported form.; Captured source metadata; No source citation supplied.; Rule version, effective dates and review history; These are the supplied review statuses. Individual reviewer events are not included in this record.; Full evaluation trace; Full rule-evaluation document; Rule evaluation has not returned a usable document. No calculation trace is available. | Citation/temporal/review gaps and original evidence | L→V. Citation cards, source-time distinction and explicit review-events gap; full records reachable. No invented authoritative paraphrase replaces source quote. |
| E16 CalculationEvidence.tsx:141–151 | Scenario assumptions and area remainder; verbatim scope_note; formula / No supported remainder formula; All scenario assumptions; Remainder inputs, result and provenance; Complete scenario record | Assumptions/remainder are not automatically unused rights | L→V. Separate scenario detail group; scope and formula remain exact. |
| R01 ReportView.tsx:68–81 | Property brief; selected label; BBL {id} · Profile generated {time}; Print the current facts, draft results, limitations and source appendix. This brief is not saved automatically.; Print property brief; Include full audit appendix | Artifact identity/time, print and unsaved state | L→V for identity/unsaved/appendix semantics; concise print toolbar and Not saved state. |
| R02 ReportView.tsx:99–130 | Contents: Facts, Zoning, Issues & assumptions, Calculations, Sources; disclosures: Property facts and identity; Zoning and mapped flags; Open issues, constraints and assumptions; Calculation and rule evidence; Source and review appendix; Complete audit appendix; Available here on demand. Included in print only when the audit appendix is selected.; Full property source and review records | Report navigation and controlled audit inclusion | V for structure; L→V for inclusion behavior. R for duplicated on-demand instructions after clear checkbox semantics. |
| R03 ReportSources.tsx:8–17 | Source and review appendix; Profile revision {revision} · Generated {time}. Current records may differ from the captured evidence shown here.; Fact / captured values; Official links / captured source; Dates / review | Stable report identity and captured/current comparison | L→V. Readable appendix table, not default full JSON. |
| R04 ReportSources.tsx:23–46 | Human field plus source key; Original: and Normalized: values/units; ZoLa/current PLUTO/dataset links; source/version/provenance ID; Captured; Effective / not published; Review:; Conflict: | Exact per-fact trace in export | L→V. Compact columns, exact captured data retained. No implied safe provenance when links absent. |
| R05 ReportSources.tsx:52–58 | Recorded confirmations and overrides; field/action/optional override/reviewer/date; Reviewer not supplied; Date not supplied; No recorded confirmations or overrides were supplied. | Human decision history and explicit missing metadata | L→V. History table with explicit unknowns. |

### 7.6 Typed state and source families

The reviewed field-label dictionary in apps/web/src/lib/format.ts supplies the dynamic labels to facts and evidence tables. It is a label mapping, not rule interpretation. Unrecognized fields render the explicit fallback {field} (source column — label pending review). Existing-building/facts/source renderers retain the complete returned family; technical source keys can be secondary to reviewed names.

apps/web/src/lib/coverage.ts:22–46 supplies verified, conditional, professional_review_required, data_conflict, unsupported and not_applicable, each with symbol and gloss. Never replace these with color alone, upgrade a status, or decorate an unreviewed property with a Verified badge. Exact enum can remain reachable in the accepted readable-summary/canonical-detail pattern where policy permits.

apps/web/src/lib/missing-inputs.ts:9–23 currently keeps critical gaps immediately visible, surfaces feasibility-relevant gaps, and groups other missing fields behind an explicit count. A blanket collapse of all warnings would violate that policy. Required disclaimer wording/prominence is separately established by apps/web/src/lib/disclaimer.ts:1–12 and the product-authority analysis; this section does not authorize weakening it.

The numeric safeguards are presentation guards, not calculations: reference values require source/BBL/unique provenance; evaluated FAR requires supported rule/citation/identity/validation/effective state; cap requires associated fingerprint/contract/trace/source agreement; bulk outputs remain Not calculated because their current open-typed contract does not establish usable family/output/unit meaning. Redesign must reuse these checks unchanged rather than infer a visually attractive answer.

### 7.7 Unit-test copy walls and invariant evidence

Paths in this table are relative to apps/web/src/components/architect/__tests__. Tests were read, not executed.

| Test anchors | Exact requirement or invariant | Design consequence |
|---|---|---|
| analysis-identity-substitution.test.tsx:59–88 | Entered/analyzed IDs; recorded as entered versus analyzed; not a computed allowance; inline condo billing lot (the single tax lot a condo is billed under) and base-land definition | Definitions currently freeze first-use prose. Moving them requires explicit test/reviewer migration, not simple deletion. |
| same:94–153 | Unstamped/missing/mismatched identities withhold; no relationship inferred; bad stamp ignored | Blocking behavior unchanged; legitimate substitution cannot merge with mismatch. |
| condo-resolution-display.test.tsx:306–324 | Full Requested BBL...Results are withheld... sentence AND You opened BBL...was analyzed for... sentence pinned; neutral no-condo-inference; no calculated allowance | Direct duplicate-copy lock. Replace with tested visible ID comparison, withholding state and non-inference detail only through review. |
| same:389–407 | City-record heading, every base lot/zoning state, divergent legal question; no analysis/result/allowance vocabulary in records; no decimal result figures in fixture | Keep records separate. Do not blanket-strip numbers: later cases preserve fractional timestamps. |
| same:734–778 | Equal entered/billing collapse; no dangling professional-review determination above; named ZTLDB; all-unknown versus partial-gap wording; recorded districts unaffected | Identity table preserves equality and partial knowledge. Exact phrases need deliberate migration. |
| same:781–815 | Real h2 headings, exact retrieved/version timestamps, slash district M1-5/R7-2 intact | Semantic outline and exact source identity survive visual change. |
| same:881–960 | Confirmer, role, fractional timestamp, parcels; self-attested refusal; never-confirmed versus revoked/superseded; discrepancy does not change confirmation | Timeline/record state cannot be a generic Reviewed badge. |
| same:963–976 | Active recorded confirmation never unlocks withheld values | Preserve calculation boundary. |
| development-limits.test.tsx:141–172 | City FAR 3.00 distinct from built FAR 2.61; existing-building disclosure reversible and complete | Keep building collapsed and references distinct from evaluated output. |
| same:43–138,202–250,332–414,427–509 | Empty/unbound citation, wrong identity/fingerprint, conflict, malformed output, duplicate trace and inferred bulk outputs withhold; original records retained | Reuse guards. No frontend arithmetic or inferred limits. |
| same:417–426 | Readable Professional review required; exact enum inside Result scope and source wording | Existing proof that canonical meaning can be retained behind readable progressive summary. |
| same:527–547 | Condo base lot needs site confirmation is not generic boundary failure | Preserve specific refusal; verify routed condo-withholding branch still explains cause. |
| same:589–614,655–682 | Ratio units, within-100-ft condition, draft/review/source link; standard versus conditional value label and accessible label | Visual condition badges require semantic parity. |
| report-view.test.tsx:50–107,146–274 | Screen/report wide-street parity; non-review null value does not become professional-review determination; conservative/conditional labels agree | Same state model across app/export. |
| same:109–142 | Main panel explicitly bans D-045-R009, D-051, needs_review, within_100ft_of_wide_street, ZR 23-22 from real backend strings; pins Draft — pending qualified legal review (not verified). | Strong existing precedent for moving honest technical detail into evidence. |
| same:278–320,417–500 | Identity withholding and condo records parity in report; exact provenance and h2 | Printed report cannot be more affirmative than screen. |
| source-links.test.tsx:22–68,76–148 | ZoLa first; current raw PLUTO secondary; dataset link; captured/current notice; exact values/version/time; wrong-lot/source/conflicting dataset links suppressed; raw metadata retained | Drawer retains safe link builders and exact evidence. |
| workspace.test.tsx:36–50 | Applicable determination expanded first; other determinations closed but reachable | Changing to collapsed-all is a deliberate behavior change requiring review. |
| workspace.test.tsx:56–85 | Report facts/sources closed onscreen, expanded for print; flags/unknowns retained; raw records excluded until selected; state restored after print | Print acceptance is separate and mandatory. |

### 7.8 CSS and print implications

- apps/web/src/app/property/architect.css:16–25 gives navigation 188 px plus workspace padding. At wide widths, :47–50 adds a persistent 270 px inspector. The overview then divides the remaining space into results and a minimum 320 px map at :65. Text wraps inside an already constrained answer area; reducing repeated surface copy and making the inspector contextual addresses this directly.
- The evidence index is sticky, 245 px wide at :100–105; the detail panel pads 28 px. Preserve master/detail usability while using summary/detail/raw tiers.
- The sheet uses small text: source keys/statuses 10–12 px, map status 10 px and map accuracy/attribution 10 px at :74–77. Do not make required meaning smaller to meet a density target.
- At ≤700 px, :138 hides .architect-environment and .architect-nav-footnote. Verify root-level disclaimer/environment alternatives before asserting mobile notice parity. Facts tables force 490 px minimum width, so exact phone overflow/readability needs browser evidence.
- ReportView.tsx:53–65 opens all non-raw details before print and restores their previous state after printing. CSS :187–188 hides raw records/audit appendix unless includes-audit is selected. Collapsing screen paragraphs alone therefore does not solve printed length. Default print must retain readable assumptions, constraints, unknown flags, sources and limitations; raw payload is separately opt-in.

### 7.9 Mockup-level direction by screen

**Overview / development limits.** A single property identity/header row, then one compact active-issue strip for real current problems. Main area splits map and development-limit matrix. The matrix explicitly separates city-record FAR, evaluated FAR and draft FAR-only area cap. Place envelope incompleteness beside the cap, with height/yards/coverage as compact labeled unavailable rows. A value or Source control opens the contextual evidence drawer. Existing buildings remain one collapsed section. Replace repeated directions with actual controls. Critical missing inputs and withholding remain visible before a user can mistake the page for a complete answer.

**Zoning.** Map/context left; district/overlay/flag matrix right. Districts remain recorded designations, not legal determinations. A separate Boundary assessment state distinguishes map illustration from canonical uncertainty. Multiple districts and share ranges remain separate. Spatial evidence and full rule result expand below their relevant states.

**Facts.** Lot/Building/Identity tabs with one filter/count toolbar. A compact fact/value/status/source matrix keeps every fact. Repeated full Source for {name} copy can become a shorter Source control retaining the full accessible name. Unknown/review states remain specific.

**Condo records.** Below governing limits, an entered/billing/base relationship table, then base-lot rows with individual zoning. Site definition has distinct Never confirmed / No active confirmation / Recorded confirmation states. Self-attested calculation refusal and parcel mismatch remain visible next to the record. Source footer and Why/history contain definitions, source-gap detail, exact timestamps and actor record. No combined-site calculation or fabricated relationship is implied.

**Evidence.** Three tiers: selected result/fact summary; readable source/trace/review detail; raw captured record. Preserve applicable-first expansion until deliberately re-approved. Source cards and trace tables replace announcements about where information can be found. The evidence workspace can contain depth without requiring the user to traverse repeated policy paragraphs to find the fact.

**Report.** First page prioritizes property/BBL/capture identity, draft scope, development matrix, critical limitations, necessary condo mapping, key sources and required disclaimer. Readable assumptions/constraints/source appendix remains included; optional full audit appendix contains raw records. Do not promise single-page completeness or omit critical caveats to fit a page. Screen and print share the same result/withholding decisions.

### 7.10 Read manifest and limitations

Full assigned source read: PropertyOverview.tsx; DevelopmentLimits.tsx; PropertyFacts.tsx; ProfileViews.tsx; AssessmentCoverage.tsx; AdditionalZoningFlags.tsx; CalculationEvidence.tsx; EvidenceInspector.tsx; EvidenceRecord.tsx; EvidenceWorkspace.tsx; ReportSources.tsx; ReportView.tsx; ArchitectShell.tsx; AnalysisIdentityNotice.tsx.

Helpers read: apps/web/src/lib/architect/development-limits.ts and navigation.ts; apps/web/src/lib/disclaimer.ts, format.ts, coverage.ts, missing-inputs.ts. Styles: apps/web/src/app/property/architect.css and relevant globals.css. Imported property/compare/rule components were inspected; their detailed inventories reside in their corresponding report sections to avoid duplication.

Tests read: architect/__tests__/analysis-identity-substitution.test.tsx; condo-resolution-display.test.tsx; development-limits.test.tsx; report-view.test.tsx; source-links.test.tsx; workspace.test.tsx.

Static source evidence does not establish deployment SHA, rendered paragraph count for a live property, pixel layout, Chrome keyboard behavior or printed pagination. Browser checks must verify those separately. This section does not authorize implementation or activation of held capabilities.


## 8. Legacy property, compare, draft-rule and shared-state audit

This section inventories the 28 assigned components under apps/web/src/components/property, compare and rule-evaluation, plus their display helpers and relevant test assertions at the pinned commit. These are not merely abandoned files: app/property/page.tsx:40–46 selects ArchitectEntry when the rule-evaluation surface is enabled and PropertyLookup otherwise; app/property/confirm/page.tsx:24 and app/property/compare/page.tsx:24 similarly retain older flag-off entries. Shared primitives also occur in the architect workspace. This source inventory does not establish which flags are enabled on the deployed site.

**Notation:** L means legally sensitive or product-required honesty that must survive; it does not assert that a statute mandates the exact sentence. V means compact visual or progressive presentation is appropriate. R is limited to repeated wording or interface narration after its surviving meaning and destination have been explicitly recorded. Most disclosures below are **L→V**, not deletion candidates. Server-supplied reasons, disclaimers, notes and provenance remain available verbatim. Source anchors below use path:line spans within the pinned source; dynamic families cover all supplied entries, not just example fixtures.

### 8.1 Property primitives and their text inventory

Paths in this table are relative to apps/web/src/components/property/.

| ID / source | Visible text elements and conditional families | Why they exist | Triage and concrete destination |
|---|---|---|---|
| LS-P01 InternalBanner.tsx:8–12 | “INTERNAL DEVELOPMENT BUILD — not a public product.”; “This screen has no user accounts or access control yet, shows unreviewed official-source data, and must not be shared outside the engineering team. Nothing here is a legal determination.” | B-001/no-auth and M2-T001 S7 environment and reliance limits. | L→V: persistent compact environment strip with an accessible disclosure carrying full restrictions. Do not remove the access/sharing qualification while unresolved. |
| LS-P02 LoadingStages.tsx:42–51 | “Looking up BBL {bbl}”; “BBL format checked”; “Retrieving the official property record and building the canonical profile”; “Rendering official facts”. | Actual pipeline, no fake percentages; retry focus and live status. | V: a compact three-stage indicator using genuine stages. R for “canonical profile” in primary copy after the actual retrieval state remains clear. |
| LS-P03 CoverageBadge.tsx:12–15 | Exact coverage enum and symbol; hover title and visually hidden gloss from lib/coverage.ts. | Status must not be conveyed by color alone or upgraded by friendly language. | L→V: a labelled chip. The hidden gloss is accessibility content, not visual clutter to delete. |
| LS-P04 CoverageLegend.tsx:44–89 | “What the coverage labels mean”; each status actually present, its symbol, exact enum and gloss; “No fact on this profile carries a coverage label.”; “Full coverage vocabulary (statuses not used on this profile)” and remaining enum/gloss pairs. | Corrects a previous hover-only explanation that touch and sighted keyboard users could not access. Unused status words are documented without falsely applying a badge. | L→V: a short visible explanation for present states, with other vocabulary in a labelled disclosure. Do not recreate the hover-only defect. |
| LS-P05 FactsTable.tsx:34–39,45–83 | Dynamic group title/note; “The official record contains no facts in this group for this property.”; “Fact / Value / Coverage status / Source”; every human field label, exact formatted value, unit, coverage badge or “not labeled”; “Source for {fieldLabel}”. | Canonical official facts with units and per-value lineage; no client arithmetic/defaults. | L→V: compact fact rows and a shared source inspector. Empty group becomes a scoped “No recorded facts” row with detail, not a full card. |
| LS-P06 ZoningSection.tsx:15–19,39–59 | Dynamic group heading/empty text; every district or overlay code; “Source for {value}”; fallback join note: “Linked by source column name (this profile carries no direct district-provenance map — the documented contract-1.0.0 situation).” | Honest provenance join rather than inferred map coverage. | L→V: zoning chips linked to the evidence inspector; retain fallback join method inside that inspector. Contract-version narration need not occupy the main zoning view. |
| LS-P07 ZoningSection.tsx:102–140 | “Zoning”; “District designations as recorded by the official source. Multiple districts on one lot (a split zoning lot) are all shown.”; “Zoning districts”, “Commercial overlays”, “Special districts”; the respective “No … is present in the official record for this lot.” empty sentences; dynamic/default “Mapped features and flags”; featureNote; “Every mapped feature recorded for this lot is a flag shown in its dedicated section.” or “No mapped features are present in the official record for this lot.” | All split districts survive; source absence is not legal nonexistence; dedicated flags may appear elsewhere without duplication. | L→V: compact designation/overlay/special-district rows with “Not recorded” states. R for location narration only when actual linked placement replaces it. |
| LS-P08 ZoningSection.tsx:143–179 | “Feature / Value / Coverage status / Source”; human feature names or “feature {n}”; exact value; badge or “not labeled”; “Source for {name}”. | Full feature inventory with no guessed label or status. | L→V: compact flags grid with labelled states and one source action per item. |
| LS-P09 MissingInputsSection.tsx:28–38,43–56 | “Missing official inputs ({total})”; every field label and criticality; optional “· completeness basis”; differing per-field reason; empty “No expected official input is missing for this property.”; intro: missing values are never guessed, feasibility-relevant gaps first, remaining entries accessible. | Completeness and absent-value honesty; all gaps preserved. lib/missing-inputs.ts:10–23 explicitly requires total always visible and critical gaps never collapsed. | L→V: a gap summary with critical/relevant named rows visible and counted administrative disclosure. Never reduce critical gaps to a hidden list behind only a number. |
| LS-P10 MissingInputsSection.tsx:58–84 | “Shared reason (stated once — applies to every field below unless a different reason is shown next to it): {sharedReason}”; “None of the missing fields is classified critical or feasibility-relevant under the documented display policy.”; “Hide {n} additional missing fields” / “Show {n} more missing fields (administrative or non-feasibility columns)”. | Existing density reduction: exact shared reason appears once, exceptions remain explicit; counted grouping is not data filtering. | L→V: retain exact reason applicability and all exceptions. Shorten interface narration only after the count/group labels and disclosure make the same relationship evident. |
| LS-P11 ConflictsSection.tsx:12–44 | “Data conflicts”; “No cross-source conflicts were detected for this property in the current official data.”; “Official records disagree on the values below. All values are shown with their source. Nothing has been resolved automatically.”; each human field label and “resolution: {resolution}”; every value, “— source: {source_id}” and optional derivation. | PRD principles 2/4: no hidden disagreement and no selected winner. | L→V: comparison rows showing both values, source and unresolved state. Empty state becomes a scoped status row; not a whole equally weighted card. |
| LS-P12 UnsupportedSection.tsx:38–67 | “Unsupported values and dataset drift”; “No unsupported values or dataset drift signals were detected in this retrieval.”; each “{field} = {value} — coverage status: unsupported”; “The official dataset returned values that no longer match its recorded contract (schema drift):”; every drift signal. | Broken/stale source conditions must remain visible rather than silently trusted. | L→V: affected-row state and issue count, all signals in detail. Keep “this retrieval” scope for absence. |
| LS-P13 ProfessionalReviewPanel.tsx:17–39 | “Professional review”; paragraph beginning “Every value on this screen is an unreviewed official-source fact…” and ending with unavailable professional-review workflow/rule-review milestone; “{n} fact(s) … explicitly marked professional_review_required”; “Coverage labeling policy for this profile” and exact server coverage_policy. | No legal determination; qualified New York review before reliance; no pretend submission workflow. | L→V: persistent review state/count and exact policy disclosure. R for roadmap narration after an accurate unavailable capability state exists. Check absolute “Every value…” against mixed-status fixtures before carrying it forward. |
| LS-P14 ProvenanceDisclosure.tsx:26–39 | “Provenance not linkable for this value — the profile carries no resolvable provenance record. This gap is shown, never hidden.”; dynamic summary label; joinNote; “Current records may differ from the captured evidence shown here.” | Missing lineage and captured-versus-current distinction. | L→V: visible “Source unavailable” with why; retain current/captured qualification adjacent outgoing links. “shown, never hidden” is removable interface narration after the gap stays explicit. |
| LS-P15 ProvenanceDisclosure.tsx:47–109 | “View this lot on ZoLa”; “Current PLUTO record (JSON)”; “Source / Original field / Original value / Normalized value / Units / Dataset version / Retrieved at / Effective date / Conflict status / Fact review / Dataset id / Retrieved from”; absent date “not published by the source (shown explicitly, not omitted)”; “About this dataset · {id}”; “Full captured source record” plus entire JSON; “Full captured profile metadata” plus entire JSON. | Complete field-level lineage; human lot link primary, raw current JSON secondary; no wrong-lot or wrong-source links. | L→V: shared inspector with source/date summary, exact field details, then raw-record disclosures. R only for self-narrating parenthetical after date absence is explicit. |
| LS-P16 OutcomeAnnouncer.tsx:37–44 | Dynamic outcome message in persistent visually hidden polite/atomic live region. | Previous outcomes were silent for screen readers when loading unmounted; this supplies exactly-once arrival announcement. | L: preserve announcement and focus behavior. This is not a visible paragraph and must not be removed for a visual word budget. |

**Property mockup direction:** the main workspace should lead with identity and development limits. Put official records in a compact secondary facts/zoning view; a source button on any row opens the same inspector. A single issue strip names critical missing inputs and unresolved conflicts; noncritical administrative gaps have a count and a keyboard/touch disclosure. Clean conflict/drift states become small scoped status rows. Keep source absence distinct from a factual negative. Existing-building information stays secondary; its data still remains available. The current missing-input shared-reason policy is a useful precedent for deduplication without loss.

### 8.2 Compare: screen-by-screen text and disclosure inventory

Paths are relative to apps/web/src/components/compare/. ScenarioResult.tsx:254–278 mounts twelve card-level blocks on a successful document: summary; cap or no-scenario; floor-area comparison; reasons; practical range; assumptions; constraints; integrity; coverage; provenance; opportunity/risk; next action. This directly explains the source-level reading burden. Not every conditional failure below appears at the same time.

| ID / source | Visible text elements and conditional families | Why they exist | Triage and destination |
|---|---|---|---|
| LS-C01 CompareScreen.tsx:100–107 | “Step 3 — Compare”; “Preliminary, unreviewed scenario for BBL {bbl}, built by deterministic code from the official record. Draft engineering only — never a Verified determination.” | Identity, preliminary status and non-final reliance. | L→V: title plus compact Draft state; implementation description in detail. |
| LS-C02 CompareScreen.tsx:128–133 | “Building the preliminary scenario for BBL {bbl}…”; “Retrieving and validating the scenario document. Nothing is shown until it passes the published data contract.” | Actual load stage and fail-closed behavior. | V: short progress state; validation mechanics need not be a default paragraph. |
| LS-C03 CompareScreen.tsx:144–147,173–183 | “Back to the confirmed property”; “Back to property lookup”; “No property selected”; valid 10-digit BBL requirement with example route; “None was provided.” or provided-invalid explanation plus validation.message; “Go to property lookup”. | Honest missing/invalid identity and recovery; no default lot lookup. | L→V: friendly no-selection/invalid selection card and lookup action; route-syntax example in technical detail. |
| LS-C04 ScenarioResult.tsx:118–132 | Missing-BBL notice distinguishing requested ID from document claim; “IDENTITY MISMATCH — this scenario states it was evaluated for BBL {evaluated}, but it was requested for BBL {requested}. Do not treat anything below as describing BBL {requested}. Both values are shown; nothing has been reconciled.” | Prevents wrong-property attribution and fabricated reconciliation. | L: cannot bury. V: prominent Requested/Returned identity row and explicit withholding/nonreliance state. |
| LS-C05 ScenarioResult.tsx:152–189 | “Step 3 — Preliminary comparison for BBL {documentBbl or not stated}”; completeness headline, exact enum and gloss; “Coverage label: {symbol enum} — {gloss}”; “Scenario kind: {enum} — {label}”; exact document.not_verified_disclaimer. | Document identity/completeness even on the branch showing a number; no critical-gap dilution. | L→V: one truthful result header, exact status vocabulary retained. Exact disclaimer in one explicit reachable location with concise visible scope; migrate duplicate uses deliberately. |
| LS-C06 ScenarioCard.tsx:47–75 | “Scenario {rank}: {kind label} ({enum})”; “This is the single preliminary scenario the deterministic engine produced. No additional or ranked alternatives are invented.”; “Draft maximum residential zoning floor-area cap:” plus exact value and “square feet”; conditional “(DRAFT — needs professional review, not Verified)”; document.cap_label. | Exactly one real scenario; not invented alternatives; exact cap scope and draft status. | L→V: “1 preliminary scenario” state and primary cap card with value, unit and scope. R for narration once count/state makes no-ranking reality clear. |
| LS-C07 ScenarioCard.tsx:81–121 | “Optimized objective and the rule behind it”; “Optimized objective / Rule / Note”; output_name, rule ID/version/status and note; “id not stated” / “not stated”; no-provenance paragraph says no objective and no cap can be shown without provenance. | A maximum must name the objective; material value requires provenance; blank IDs must not disappear. | L→V: objective next to value, source action, complete details in inspector; absence remains explicit. |
| LS-C08 ScenarioCard.tsx:123–126 | “The full citation chain for this number — snapshot, section, quoted text, source, retrieval and verification status — is in the evaluated input and provenance disclosure below.” | Makes evidence discoverable. | V/R: direct “Source and calculation” control replaces location narration; not evidence deletion. |
| LS-C09 NoScenarioBlock.tsx:183–197 | “{kind label} ({enum}) — no maximum can be stated”; paragraph beginning “No draft maximum development potential could be stated…” explaining informative engine result, reasons and preserved ranges; optional “Professional review required before any reliance.” | No supported answer is not zero and not necessarily a software error. | L→V: concise no-supported-maximum state with concrete reason and appropriate next action. |
| LS-C10 NoScenarioBlock.tsx:59–105 | “Competing rules and conflicting values (nothing was resolved)”; paragraph beginning “More than one draft rule is simultaneously in effect over the same output, or sources disagree…”; legal-governance/no-winner/no-value/both-sides explanation; every conflicting key/value/unit/state; “Recorded on constraint {key} — the conflict is over output(s): {names}” or “— the document names no competing output”; no-competing-rules sentence. | Both sides and reason for no result must survive; never select a governing rule in presentation. | L→V: unresolved A/B conflict table. **Review wording defect:** intro still says “simultaneously in effect”; do not preserve an unsupported legal-effect assertion just because it is old copy. Correct it transparently under a reviewed task. |
| LS-C11 NoScenarioBlock.tsx:110–135 | Rule ID/version or “rule id not stated” / “version not stated”; “no effective dates are recorded for this rule” or “recorded effective dates: from {date/not stated}, to {date/not stated}”; “· emits {outputs}”. | Dates are recorded fields, not a claim of present legal effect. | L→V: rule comparison rows; unknown end is never “present”. |
| LS-C12 NoScenarioBlock.tsx:151–171 | “Preserved base-district share ranges (never collapsed)”; district or “district not stated”; “share range min {x} / point {y} / max {z}”; “(minor portion)” / “(not a minor portion)” / “(minor portion not stated)”; optional “(classification: {pairClass})”. | Uncertainty and tri-state absence must not become one precise percentage. | L→V: labelled interval tracks or table with exact min/point/max text. No inferred parcel boundary or single share. |
| LS-C13 UnusedFloorAreaSection.tsx:92–113,129–141 | “Floor-area record comparison”; exact section.label; “Draft cap minus recorded building area:” plus exact signed value, square feet and Draft/review label; exact scope_note directly underneath on every state. | FAR-derived difference is not unused rights, buildable area or remaining capacity; scope must stay adjacent. | L→V: secondary metric aligned with cap; material scope remains directly beneath, not buried in a remote help panel. |
| LS-C14 UnusedFloorAreaSection.tsx:160–200,57–67 | Exact over_built_statement; “This result exceeds the draft cap and is flagged for professional review before any reliance.”; “No supported estimate”; reason-specific sentences for absent building floor-area record, unusable record or absent draft cap, explicitly distinguishing absent/unusable from zero; fallback “No supported estimate is available for this calculation.” | Negative remainder retained, no clamping/positive restyling; no-compute is not zero. | L→V: signed number plus review state, or unavailable state with its actual reason. Exact zero must still render 0. |
| LS-C15 ScenarioReasons.tsx:22–35 | “What the engine recorded about this result”; “These sentences come from the deterministic engine itself and are shown verbatim — they are not this screen’s summary of them.”; empty sentence beginning “The scenario document records no reasons…”; all document.reasons entries. | Previously reasons vanished on the only branch showing a number; future applicability/inputs notes must not be dropped. | L→V: labelled exact “Result basis” detail, material limitations surfaced near dependent value. R for engine/self-narration after exact basis remains accessible. |
| LS-C16 ScenarioResult.tsx:68–90 | “Practical usable range”; “A draft zoning-floor-area cap is not gross, net, sellable, or feasible area, and it is not a buildable envelope — where this screen shows one, that is all it is.”; no-blockers branch says no recorded blocking missing family does not mean a range exists; blockers branch lists document-derived number and family names and “They are listed with the other gaps below.” | Cap is not envelope or usable area; no blockers is not positive feasibility; current families must come from server matrix. | L→V: visible “Buildable envelope: Not established” state, named blocker chips, direct matrix link. R for location sentence only after relationship/count is preserved; current test locks it. |
| LS-C17 ScenarioAssumptions.tsx:25–60 | “Declared assumptions”; paragraph says variations only through declared assumptions, no hidden utilization/efficiency/optimization; “No assumptions are declared on this scenario. Nothing has been assumed, factored, or discounted — what is shown is the draft rule output as the engine recorded it.”; every assumption key/value/unit/type/rationale; “no unit recorded”; “No rationale was recorded for this assumption.” | Typed assumptions distinguish scenarios and prevent hidden discounts. | L→V: compact None declared or counted assumptions row; each material assumption stays adjacent to its dependent metric, full exact records accessible. |
| LS-C18 ScenarioConstraints.tsx:80–117 | “Constraints considered ({n})”; introduction says every constraint/state/note and missing cannot be inferred/defaulted/estimated or accounted for by a shown number; unexpected-empty sentence; every key/value/unit; “state: {enum} — {gloss}; completeness: {enum}”; exact constraint.note or “The document records an empty note for this constraint.” | Prior capless branches dropped all constraints; notes carry anti-inference warnings stronger than a missing badge. | L→V: canonical limits/constraints table with visible critical states and row-level note/source detail. Merging duplicate tables cannot drop note, completeness or provenance. |
| LS-C19 ScenarioConstraints.tsx:38–69 | “No provenance is attached to this constraint by the document.”; “A provenance object is attached but records no fields.”; “Provenance for this constraint ({n})”; all generic path/value leaves; explicit record-larger-than-view omission note. | Absent, empty and truncated records differ; generic traversal prevents dropped open-schema fields. | L→V: row-linked evidence panel, explicit truncation state. No silent curation. |
| LS-C20 ScenarioConstraints.tsx:130–152 | “Platform integrity check”; verification-only recompute paragraph saying canonical value unchanged and disagreement fails closed; Performed “agreed with” / “did NOT agree with” / “result unrecorded against” canonical trace, or “Not performed for this scenario”; exact note or “No note was recorded.”; “Method: {method} · tolerance used: {value}”. | Engineering consistency check, not legal verification; tolerance makes method interpretable. | L→V: technical integrity detail in evidence, consequential failure visible at result. Never present as a Verified legal checkmark. |
| LS-C21 CoverageMatrixSection.tsx:63–86 | “Coverage labels and rule gaps”; paragraph says never above conditional/never Verified, labels not color alone, missing families prevent complete-answer implication; “What the coverage labels mean”; all six enum/symbol/gloss pairs; unsupported correction: “On a scenario this specifically means the district or rule family is not implemented yet — not that a data problem was detected.” | Contextual status semantics; scenario unsupported differs from corrupted source data. | L→V: current-status explanation at result, complete glossary one action away. Resolve contradictory generic gloss through reviewed context-aware vocabulary, not a frontend status upgrade. |
| LS-C22 CoverageMatrixSection.tsx:93–119 | “Full rule-coverage matrix ({n} family/families)”; unexpected no-matrix sentence; every constraint_family/governs; “status: {enum} — {gloss}”; “blocks a buildable envelope” or “does not block a buildable envelope”. | Before rework, draft and out-of-scope rows disappeared; full matrix is authoritative. | L→V: one coverage matrix containing all rows, explicit unavailable/out-of-scope distinction. |
| LS-C23 CoverageMatrixSection.tsx:124–148 | “Rule families still missing ({n})”; “No coverage-matrix family is recorded as missing for this scenario.”; missing rows repeated with same family/governs/status/envelope-blocker text. | Separately highlights gaps, but duplicates most matrix content. | L→V/R: replace repeated list with missing/blocker views of the same complete matrix, count reconciliation and visible critical items. Current tests expect two lists, so migration requires explicit equivalence review. |
| LS-C24 ScenarioProvenance.tsx:112–119 | “Evidence for what is shown above”; paragraph identifying inputs/versions/legal source and narrating “Progressive disclosure: the detail is one keystroke away rather than absent.”; “Evaluated input, contract version, and legal-source provenance”. | Evidence discoverability. | L→V: direct Source control. R for explaining the disclosure mechanism once accessible controls exist. |
| LS-C25 ScenarioProvenance.tsx:122–175 | “Scenario contract version / BBL this document was evaluated for / BBL requested by this screen / Property-profile contract version / Rule-evaluation contract version / Input fingerprint”; “not stated”; “Legal-source citations for the draft cap”; no-cap-provenance/no-cap explanation; cap-provenance-NO-citations explanation; “Unverified draft extraction from the official source — not a Verified reading of it:”. | Identity, reproducibility and citation gaps; source extraction is not reviewed interpretation. | L→V: common inspector. A material uncited result's gap must remain apparent, not visually cleaned away. |
| LS-C26 ScenarioProvenance.tsx:59–93 | “Snapshot / Section / Quote / Last amended”; exact data or “snapshot id not stated”, “not stated”, “no quoted text was carried”; every open provenance leaf; “Source provenance — not stated by the document”; explicit citation-provenance-larger-than-view note. | No invisible blanks or silently dropped provenance leaves. | L→V: summary citation then complete technical fields, with absence/truncation labels. |
| LS-C27 ScenarioResult.tsx:199–217 | “Main opportunity and main risk”; “Main opportunity”; repeats exact cap as preliminary-study starting point or says no quantified opportunity/reasons/ranges above; “Main risk”; repeats document.not_verified_disclaimer; review-before-reliance sentence when flagged. | Opportunity/risk product framing; currently duplicates cap and disclaimer. | L→V/R: primary metric and visible risk state carry the same meaning; remove duplicate card only after one canonical disclaimer and each specific risk have explicit destinations. |
| LS-C28 ScenarioResult.tsx:227–239 | “Next step”; “Evidence and provenance for every value shown here (Step 4) arrive with a later milestone; this build does not pretend to run it.”; back-confirmed/back-lookup links. | No fake feature progression. | L→V/R: actual gate-aware next action. Newer evidence screens exist, so verify route capability before carrying old roadmap claim forward. This is source drift to assess, not proof of a live defect. |

**Compare mockup:** top row has document identity, one Draft status and critical gap state. The primary metric is the draft zoning-floor-area cap with its exact scope; the record-difference metric is secondary and keeps its scope under the number. A compact assumption row states None declared or a count. One limits/coverage matrix provides value, status, reason and Source controls; show named critical blockers without expansion, keep all remaining rows reachable and count relationships explicit. The evidence drawer contains exact server reasons, citation chain, provenance, integrity detail and glossary.

For a no-scenario document, replace the metric with “No supported maximum” and the actual reason, followed by an unresolved-rule comparison or district-share interval table. There is no invented cap, completed envelope graphic or ranking. Provide one genuine enabled next action. A blocked/unknown/unsupported result is an informative state, not automatically an alarming technical failure.

### 8.3 Draft rule-evaluation surface

Paths are relative to apps/web/src/components/rule-evaluation/.

| ID / source | Text inventory | Why | Triage and destination |
|---|---|---|---|
| LS-E01 RuleEvaluationPanel.tsx:50–59 | “Evaluating draft rules for this property…”; “Official property facts retrieved”; “Running the deterministic draft rule evaluator over the official facts”; “Rendering the draft result”. | Actual optional-enrichment progress. | V: concise stage indicator. Preserve separate loading and retry state without moving focus on background arrival. |
| LS-E02 RuleEvaluationPanel.tsx:139–145 | “Draft rule evaluation (internal)”; paragraph beginning “An experimental, unreviewed draft rule result for this property…” and stating non-final output, unchanged official facts, independent load and usable profile if it fails. | Official facts and draft outputs are different; optional enrichment cannot block the profile. | L→V: short Draft limits label and review/scope state. R for loading architecture narration after the actual failure isolation remains. |
| LS-E03 RuleEvaluationResult.tsx:34–58 | Five headings: “Draft determination — requires professional review”; “No applicable draft rule for this property”; “Professional review required — evidence missing”; “Conflicting draft rules — professional review required”; “Spatial uncertainty — the lot spans districts”. Corresponding intros: unreviewed/qualified NY professional before reliance; no applicable rule/no value; inputs not established/no guess; competing rules/legal determination/no winner; preserved district-share ranges/no single asserted district. | Five distinct server-derived states must not collapse into one generic warning. | L→V: concise state and concrete reason in the limits table. Retain unsupported versus unavailable-service distinction. |
| LS-E04 RuleEvaluationResult.tsx:381–388 | “DRAFT — not a final legal determination. Produced by an unreviewed draft rule pending qualified-human legal approval. Do not rely on it for acquisition, design, filing, financing, or construction.”; exact coverage badge; state-specific intro. | Draft and non-reliance framing, not a Verified determination. | L→V: prominent concise status with review/scope; exact policy stays reachable. Existing explicit banner wording needs reviewer equivalence approval before shortening. |
| LS-E05 RuleEvaluationResult.tsx:68–71 | “Draft-result disclaimer (exact wording)” and exact document.not_verified_disclaimer. | Explicit accepted precedent: canonical disclaimer may be collapsed when prominent plain-language scope survives. | L→V: retain labelled keyboard/touch disclosure; coordinate duplicates around it. |
| LS-E06 RuleEvaluationResult.tsx:83–105 | “Evaluated input and source provenance”; “Evaluated BBL / Property-profile contract version / Input fingerprint / Zoning-district input provenance / Lot-area input provenance”; “not stated”; “none linked (shown explicitly, not omitted)”. | Identity/input lineage and explicit missing linkage. | L→V: common evidence inspector. R for self-narrating parenthetical once None linked is explicit. |
| LS-E07 RuleEvaluationResult.tsx:110–182 | “Legal-source citations backing the draft rule (unverified draft extraction; not a Verified reading of the source):”; “Rule / Section / Quote / Source / Dataset id / Retrieved from / Retrieved at”; exact rule/version/status/quote/source values, safe dataset links and host; “No legal-source citations accompany this result (there is no computed value to cite).” | Citation chain and official-source-versus-reviewed-reading distinction. | L→V: source inspector. Verify invariant behind “there is no computed value” before reusing that hard-coded absence explanation. |
| LS-E08 RuleEvaluationResult.tsx:192–218 | All document.reasons entries; “Draft outputs from rule {id} ({status}) — draft values, not a final determination:”; all output keys and exact values. | No client calculation and no omitted engine reason. | L→V: output rows and direct sources; any friendly label must be reviewed, not a new legal interpretation. |
| LS-E09 RuleEvaluationResult.tsx:239–257 | District or “district not stated”; “share {min}–{max}” or “range not stated”; optional “(point estimate {x})” and “— minor portion”; “Base-zoning districts the lot intersects (shares preserved as ranges):”. | Range/uncertainty retention. | L→V: exact range table/interval depiction, never point-only share. |
| LS-E10 RuleEvaluationResult.tsx:270–280 | “The conflict is over output(s): {names}”; “Competing draft rules (none was selected):”; every rule ID/version; “— in effect {effective_from or unknown start} to {effective_to or present}”. | Show both competing rules without legal choice. | L→V plus corrective finding: null end becomes “present” and draft rules are asserted “in effect”. The compare sibling explicitly rejects this wording. A reviewed repair should use recorded dates and not-stated ends, not conceal the problem. |
| LS-E11 RuleEvaluationResult.tsx:299–345 | “Draft base-zoning district: {district} · lot area used: {value} sq ft ({source})”; “Fail-safe reason: {code}”; spatial review_reasons; general reasons on every branch. | Inputs, failure basis and spatial uncertainty. | L→V: compact input row and reason-specific state; exact reasons in reachable detail, consequential gap visible at the result. |

**Draft-evaluation mockup:** integrate this surface with the development-limit rows instead of stacking introduction, banner, badge, another introduction and outputs. Each row has state, value or an honest unavailable mark, and Why/Source controls. Conflict opens a rule A/B table using recorded dates. Spatial uncertainty opens ranges. A service failure stays local and leaves confirmed facts usable; retry acts only on the failed enrichment. The current status has a visible explanation accessible to touch users, not a hover-only tooltip.

**Additional source-level risk:** lib/coverage.ts uses “Official source fact” for conditional and “data problem” for unsupported. Those shared glosses are reused for draft outputs/scenarios whose meanings differ; Compare appends a correction for unsupported. A reviewed, context-aware vocabulary should preserve exact backend enums while explaining fact/rule/scenario meaning accurately. Do not achieve a cleaner UI by changing the underlying coverage status.

### 8.4 Complete failure-state family inventory

P denotes apps/web/src/components/property/FailureState.tsx; C denotes apps/web/src/components/compare/ScenarioFailureStates.tsx; E denotes apps/web/src/components/rule-evaluation/RuleEvaluationFailure.tsx. Each row is a conditional outcome, not cumulative screen prose. All preserve a distinct honest state (L); compact error presentation and technical disclosure are V. No partial property/scenario/result is rendered from an invalid response.

| ID / state | Headlines and source anchors | Other text families / meaning that must survive |
|---|---|---|
| LS-F01 No match | P:58–68 and C:80–90 “No property record found”; E:77–85 “No record to evaluate”. | P/C valid-format BBL but no current official dataset record, not system error; C no scenario built. Bounded outcome.message, including specific condo guidance, and optional support reference. |
| LS-F02 Validation rejected | P:73–85 / C:95–108 “The API rejected this BBL”; E:89–99 “The evaluation service rejected this BBL”. | Bounded message; “Rejection code: {code}”; reference. Distinguish server rejection from local formatting or absent record. |
| LS-F03 Rate limited | P:94–99 / C:117–122 / E:105–110 “The official data source is throttling requests”. | Source temporarily limited requests; retry shortly safe; input is not faulty. E says draft unavailable while existing profile is unaffected. |
| LS-F04 Source unavailable | P:100–105 / C:123–128 / E:111–116 “The official data source is unavailable”. | Could not reach source (P/C after attempts); safe retry; E profile remains usable. |
| LS-F05 Upstream timeout | P:106–111 / C:129–134 / E:117–122 “The official data source timed out”. | Source did not respond in time; safe retry; P/C input fine, E profile unaffected. |
| LS-F06 Schema drift | P:112–119 / C:135–141 / E:123–128 “The official dataset changed shape”. | Source no longer matches recorded contract; platform attention. P/C explicitly not transient and retry likely unchanged until connector fix; E profile unaffected. |
| LS-F07 Shared upstream metadata | P:132–138 / C:154–160 / E:141–147. | “Failure type: {state} (HTTP {status})”, scope-specific retry and optional reference. Put machine details behind labelled technical disclosure without merging failure states. |
| LS-F08 Internal fault | P:143–159 / C:165–181 “Something went wrong on our side”; E:152–170 “The draft evaluation hit an internal error”. | Platform fault, input fine; support ID identifies exact fault. C during scenario build; E existing profile unaffected. |
| LS-F09 Server contract refusal | P:170–195 “The server refused to deliver an invalid profile”; C:186–206 “… invalid scenario”; E:175–197 “… invalid draft evaluation”. | Server withheld a result failing contract checks; unreliable data not displayed; platform attention; retry likely unchanged until repair. P also names failure type; E retains profile. |
| LS-F10 Client validation refusal | P:205–238 / C:216–246 “The response did not match the published data contract”; E:202–233 “The draft evaluation did not match the published data contract”. | Nothing from invalid response shown; E unaffected profile. Conditional “Validation problems ({n}, bounded)” disclosure with every bounded problem. |
| LS-F11 Network failure | P:243–254 “Could not reach the platform API”; C:251–262 “Could not reach the scenario service”; E:237–250 “Could not reach the draft-evaluation service”. | Bounded message and retry. lib/api.ts:201–205 fallback: “The platform API could not be reached. Nothing was retrieved. This lookup is safe to retry.” |
| LS-F12 Client timeout | P:260–276 “The lookup took too long”; C:267–283 “The scenario took too long”; E:255–272 “The draft evaluation took too long”. | Actual timeout seconds, request cancelled, no partial data, safe retry. P/C input fine; E profile remains unaffected. |
| LS-F13 Unexpected response | P:281–307 / C:288–316 “Unexpected response from the platform API”; E:277–303 “… draft-evaluation service”. | HTTP and optional body state, “not a documented pairing” or “without a recognized machine-readable state”; response untrusted/not rendered. P is explicitly not property-not-found; C not no-scenario; E unaffected profile. |
| LS-F14 Feature unavailable | C:66–75 “Scenario comparison is not available here”; E:62–72 “Draft rule evaluation is not available here”. | Disabled environment feature, not bad input. No scenario requested/nothing compared C; no enrichment but usable profile E. No Retry because retry cannot enable a feature. |
| LS-F15 Shared actions/diagnostics | P:40–54 / C:42–56 / E:44–58. | “Reference id for support and server logs: {correlationId}”; “Retry lookup” / “Retry compare” / “Retry draft evaluation”. IDs are bounded; no raw stack is exposed. |
| LS-F16 Navigation after comparison failure | CompareScreen.tsx:143–147. | Back to confirmed property and back to lookup preserve a way out when the scenario cannot load. |
| LS-F17 Superseded request | P:341–342, C switch intentionally excludes aborted, E:341–342. | Aborted/superseded request renders no stale failure because newer request owns the screen. This silence is intentional, not an omitted gap. |

**Failure mockup:** one state heading, one plain-language cause, one relevant recovery action, then Technical details with HTTP/state, validation problems and support reference. Keep a distinct source outage versus unsupported property versus invalid result. For schema/contract defects, do not make Retry visually promise a repair it cannot provide. Keep a professional-review state visually separate from a technical outage.

The failure cards intentionally do not each have a live alert. The persistent OutcomeAnnouncer owns one arrival announcement; focus moves to the outcome heading. Background rule evaluation must not steal profile focus; retry moves focus only after the user's action. A redesign must preserve these behavior contracts, not just visible text.

### 8.5 Shared vocabulary, dynamic content and exact labels

All source notes, reasons, diagnoses, rule-output names, coverage rows, candidate districts, assumptions, provenance fields and their values are dynamic families: every supplied entry is in the inventory. It is not possible to enumerate every future server sentence from frontend source. No claim is made that every future response has been observed.

| Source | Exact vocabulary / dynamic behavior | Preservation |
|---|---|---|
| lib/coverage.ts:22–47 | verified: “Confirmed under a published, professionally reviewed rule.”; conditional: “Official source fact, not yet professionally reviewed.”; professional_review_required: “A qualified professional must review this before reliance.”; data_conflict: “Official sources disagree; both values are shown, nothing was resolved.”; unsupported: “The platform detected a data problem and cannot support this value.”; not_applicable: “Does not apply to this property.” Symbols respectively ✓, ◐, !, ≠, ∅, —. | L→V: exact states, non-color semantics and appropriate context. “Both values are shown” requires both values actually reachable. |
| lib/coverage.ts:60–76 | complete: “All expected official inputs were retrieved” / “No expected source field is missing for this property.”; missing_noncritical: “Some non-critical official inputs are missing” / official record omits fields, none critical, every gap listed; missing_critical: “Critical official inputs are missing” / critical field absent and feasibility conclusions cannot be complete without it. | L→V: data completeness is not rule coverage or feasibility. |
| lib/scenario-display.ts:35–59 | Kinds: “Preliminary draft scenario”, “No preliminary scenario”, “Not supported yet”. Constraint glosses: “known (from the official record)”, “draft (unreviewed rule output)”, “missing (no rule family provides it)”, “conflicting (rules or sources disagree)”, “unsupported (no implemented rule family)”, “professional review required”. Matrix: “draft rule available (unreviewed)”, “missing — no rule family provides it”, “out of scope for this property”. | L→V: three distinct status dimensions; not one universal red/yellow/green verdict. |
| lib/scenario-display.ts:243–308 | Generic provenance leaves limited to 200 and depth 12; paths/values retained; “(unnamed field)”, “(nested deeper than this view shows)”, “(empty list)”, “(empty object)”. | L: bounds and missing/empty states disclosed; generic open fields must not vanish during visual curation. |
| lib/format.ts:9–31 | Null/undefined “—”; Boolean “Yes”/“No”; exact numeric grouping with up to 20 fractional digits; source strings verbatim; objects JSON; invalid host “unavailable”. | L→V: no display rounding that changes magnitude or missing→zero. Pair dash with a meaningful unavailable/unknown state when needed. |
| lib/format.ts:233–234 | Unknown-field fallback “{field} (source column — label pending review)”. | L→V: no guessed expansion. Reviewed FIELD_LABELS are inventoried below. |
| lib/missing-inputs.ts:10–23,34–101,113–136 | Total always visible; critical or enumerated feasibility-relevant fields surfaced; other entries behind count toggle; grouping does not alter data completeness. Exact repeated reason deduplicated only if at least two identical strings; different reasons remain inline. | L: existing progressive-disclosure precedent and guardrail. |
| lib/scenario-api.ts:431–474 | Outcome announcements for preliminary/no-scenario/unsupported, feature disabled, no-match, rejection, four upstream states, internal/refusal/validation/network/timeout/unexpected; aborted empty. | L: announcements remain accurate to the rendered outcome, not generic success. |
| lib/rule-evaluation.ts:492–577 | Five result-state announcements, all failure families, explicit analyzed-base-lot/entered-billing-lot notice when legitimate, and unresolved condo/site-confirmation notice; aborted empty. | L: accessible identity/condo specificity must match visible state. Base-lot notice says city record, not computed allowance. |

The coverage exact-enum requirement currently appears in implementation comments and tests. A friendlier primary label with the enum moved into a technical disclosure is a proposal requiring explicit equivalence review, not a permission already granted by this audit.

### 8.6 Tests: what is a semantic requirement versus a copy/layout lock

These assertions were inspected; **no tests were executed**. Anchors below are within apps/web/src/components/. Adapt tests only after a documented equivalence decision. Passing a string assertion while hiding a critical warning behind an undiscoverable control is not a valid redesign.

| ID / test source | Current requirement or exact lock | Redesign implication |
|---|---|---|
| LS-T01 compare/__tests__/compare-screen.test.tsx:52–87 | Literal “15,000” and fractional “12,345.678”; objective max_residential_floor_area_sq_ft; cap_label includes “DRAFT maximum residential ZONING-FLOOR-AREA CAP”; Draft node. | Preserve exact magnitude, objective, label and review/scope, irrespective of layout. |
| LS-T02 same:90–120,125–180 | Document BBL, mismatch both IDs plus “IDENTITY MISMATCH”; “not stated” absence; missing_critical and “Critical official inputs are missing”; reasons include “NOT a buildable envelope” and verbatim; anti-inference constraint note; provenance source/version; no assumptions; integrity tolerance; contract/fingerprint/citation section/quote/extraction status. | These guard prior losses. Every semantic item needs a destination; no removing reasons because a cap rendered successfully. |
| LS-T03 same:185–262 | Matrix-derived blocking families; changes when server removes blockers; “Nothing on this screen infers one”; zoning-floor-area-cap/not-envelope definition on capless branches; no “The value above”; exact “listed with the other gaps below”. | First assertions are semantic. Last phrase encodes the old spatial arrangement: replace only with a reviewed linked matrix/count relationship and new semantic assertion. |
| LS-T04 same:267–278,284–364,368–466 | Blank rule identifiers, capless constraints/integrity, all district ranges/classification and competing rules; blank citation fields explicit; “recorded effective dates”, “to not stated”; rejects “present” and “in effect”; empty-date and district-label states. | Range/identity/provenance and date truth survive. Apply the same date discipline to rule-evaluation's inconsistent copy. |
| LS-T05 same:471–515 | All six vocabulary enums; “Rule families still missing (8)”; eight missing rows; blocker label; separate full eleven-row matrix including draft and out_of_scope. | Count and no-row-loss requirements are semantic. Two separate rendered lists are a layout lock requiring explicit approved migration if merged. |
| LS-T06 same:520–579,583–657,688–706 | Invalid document/provenance refused, no partial cap; unexpected HTTP/state not no-match; flag-off no retry; recoverable retry; navigation preserves BBL; persistent live region/focus; actual loading announcement. | Preserve behavior alongside visual cleanup. Do not “simplify” all failures to property unsupported. |
| LS-T07 same:748–790 | Bounded unit/free-text behavior; oversized arrays rejected; overlong text explicitly truncated rather than silently dropped. | Condensation cannot become undisclosed truncation. |
| LS-T08 compare/__tests__/unused-floor-area.test.tsx:139–174 | Heading “Floor-area record comparison”; exact “Draft cap minus recorded building area:”; exact value/unit/document label/scope_note; Draft discipline; scope under number described in test. | Label precision and adjacent scope are load-bearing; reducing prose must not turn difference into rights/capacity. |
| LS-T09 same:179–241 | Negative “-5,000” never positive/zero; exact over_built_statement; accessible professional-review role=status; not-computable has no number, “No supported estimate” and reason-specific text. | Preserve signed values, exact zeros, absent/unusable/no-cap distinctions and review accessibility. |
| LS-T10 property/__tests__/sections.test.tsx:47–145 | Both conflict values/source/derivation, “resolution: unresolved”, “Nothing has been resolved automatically”; explicit conflict-empty state; missing-input total; human labels; counted expanded toggle; shared null-omission reason exactly once; per-field exception visible. | Existing tests already support deduplication and grouping. Critical and relevant gaps cannot disappear; technical source keys do not replace human labels. |
| LS-T11 same:151–315 and property/__tests__/provenance-disclosure.test.tsx:8–69 | Valid safe dataset/current lot links; hostile URL never href; no borrowed source identity/dataset; ZoLa primary before raw PLUTO; current may differ from captured; exact metadata and full raw record retained. | A shared source inspector must preserve link gating, ordering and snapshot distinction, not only look cleaner. |
| LS-T12 property/__tests__/property-lookup.test.tsx:283–309,314–532 | Current-status gloss visible without hover; no absent-status Verified badge; disabled address honest “credentials are still pending” copy on this older route; every outcome announced once; no duplicate alerts; retry clears/reannounces/focuses correctly; invalid retype does not hijack focus. | Do not treat legacy disabled-address copy as current architect-entry availability. Verify each flag route. Non-hover status comprehension and focus remain required. |
| LS-T13 rule-evaluation/__tests__/rule-evaluation.test.tsx:32–97 | Five distinct headings; “DRAFT — not a final legal determination”; no Verified badge, exact conditional enum; exact server disclaimer inside native details; both district ranges; competing rules and no outputs in conflict; evaluated-input/citation disclosure and exact draft outputs. | Explicit precedent for exact legal text in progressive disclosure when prominent scope survives. Preserve state distinctions and full ranges. |
| LS-T14 same:123–195,201–231,256–276 | Safe links, no invented dataset row; network retry; feature-disabled no retry; separate arrival announcement; profile preserved; flag-off does not mount/call endpoint. | Visual integration must not weaken isolation/gating or invent retryable capability. |
| LS-T15 compare/__tests__/property-error-boundary.test.tsx:80–163 | Route error heading “This screen could not be displayed”, alert, “Try this screen again”; opaque digest only, never raw message/host/path; “Nothing was determined” and no reliance; internal banner and lookup exit; reset exactly once. | Clean error presentation cannot imply a partially rendered analysis is usable. Keep containment, recovery and nonreliance. |

### 8.7 Source/test manifest for this section

Read source: components/compare/{CompareScreen,CoverageMatrixSection,NoScenarioBlock,ScenarioAssumptions,ScenarioCard,ScenarioConstraints,ScenarioFailureStates,ScenarioProvenance,ScenarioReasons,ScenarioResult,UnusedFloorAreaSection}.tsx; components/rule-evaluation/{RuleEvaluationFailure,RuleEvaluationPanel,RuleEvaluationResult}.tsx; components/property/{ConflictsSection,CoverageBadge,CoverageLegend,FactsTable,FailureState,InternalBanner,LoadingStages,MissingInputsSection,OutcomeAnnouncer,ProfessionalReviewPanel,ProvenanceDisclosure,UnsupportedSection,ZoningSection}.tsx. PropertyLookup itself belongs to the address/root audit.

Read relevant display/client source: lib/{scenario-display,missing-inputs,coverage,format,api,scenario-api,rule-evaluation}.ts. Reviewed the seven test files cited in §8.6. No local runtime, build, package manager, test execution, project-control access or repository mutation was used for this audit.

### 8.8 Canonical fact-name mapping inventory

The complete, exact 108-field mapping from lib/format.ts:71–224 appears once in the [shared field-label register](#exact-shared-field-label-register) in §16. It covers every current dynamic field label used by these views. Each field/source relationship must survive; layout may become compact. These are display-name expansions, not legal interpretations, and code-list values remain source codes. In particular, PLUTO “Maximum residential FAR” requires explicit city-record context and is not proof of an evaluated governing allowance. Future unknown keys retain the label-pending-review fallback; no unknown key is silently interpreted.

## 9. Survey review and internal owner dashboard inventory

This section covers the survey inbox, document review, fact correction, downstream consequences, professional decisions and the internal owner dashboard. References are relative to `apps/web/src/` at the assessed commit. `L` identifies reliance, authority, provenance or truthful-state meaning that must survive; it does not assert that a statute mandates a particular sentence. `V` identifies a visual/progressive presentation opportunity. `R` identifies a duplicate or scaffolding instance removable only after its meaning has a named surviving destination. Braces identify dynamic text supplied by the model.

### 9.1 Findings specific to these screens

The survey review already has useful visual primitives: status label + symbol + tone, page annotation, ordered fact rows, linked blockers, and a progressive audit trail. The compact route moves some source details into disclosure, but the focused fact still eagerly stacks original/current values, provenance paragraphs, correction history, check explanations, permission explanations, and action-semantics paragraphs. That composition directly supports the complaint about excessive reading.

Disclosure duplication occurs at concrete source locations: extraction-unavailable explanations in both `SurveyReviewScreen` and `DocumentOverlay`; extraction method/advisory explanations in both `FocusedItem` and `CorrectionHistory`; and confirmation restrictions across the dominant action, action help, downstream impact, and confirmation panel. Preserve each decision-relevant meaning with one compact state at the relevant action, and keep the full reasons accessible.

The owner dashboard already uses metrics, tiles, a dependency map, bars, and a detail drawer. Its opportunity is reducing instructions and emphasizing owner-readable titles over IDs. Its vocabulary must remain separate from architect property verdicts: “Accepted,” “Built,” “Launch-ready,” and “Healthy” describe engineering/launch state here.

Two source-only follow-ups need reproduction before any corrective task is accepted:

- `lib/surveyReview/model.ts:130–145` can fall through to “All material facts are resolved.” for an uploaded/processing document with no facts and no blockers. Verify that this cannot imply completion for an unprocessed document.
- `DocumentOverlay.tsx:126–138` draws a blank page rectangle when `imageRef` is null, while annotation boxes can still render. An explicit preview-unavailable cue belongs beside that canvas so it cannot be mistaken for the original survey. The separate B-001 note in correction history is less local. This is a source-observed risk, not a demonstrated runtime failure.

### 9.2 Survey inbox inventory

| ID | Current text / dynamic family | Source | Why it exists; triage and destination |
|---|---|---|---|
| SR01 | “Survey documents for this property” / “Survey review inbox” | `components/survey-review/ReviewInbox.tsx:45–50` | Orientation. **V:** retain short heading. |
| SR02 | “Documents awaiting review, ordered by state. Every extracted fact is unconfirmed evidence until a designated professional confirms it.” | Same `47–50` | Ordering and extraction≠professional confirmation. **L+V:** unconfirmed badge and “Review rules” disclosure; represent order with group/filter labels. |
| SR03 | “Loading the review queue…” | Same `53–56` | Loading. **V:** concise loading label, skeleton and accessible busy state. |
| SR04 | “No documents to review”; “No survey documents for this BBL were returned in the review queue.” / “There are no survey documents in review right now.”; “Upload is not available in this version; existing routed documents appear here.” | Same `59–65` | Empty state, BBL scope, absent upload. **L+V:** “No surveys” and “Upload unavailable” states; full scope/gap under “Why?”. Do not imply working upload. |
| SR05 | Document `{entry.title}`; “BBL {target_bbl} · {open_item_count} open item(s)”; document state badge/gloss | Same `68–80` | Identity, workload, lifecycle. **L+V:** compact Survey / Property / Open items / Status columns. |
| SR06 | “The review inbox could not be loaded”; unauthorized `{outcome.message}` or “The review service could not be reached or returned an unexpected response. Nothing was changed.”; “Retry” | Same `87–99` | Failure/recovery, authority, no mutation. **L+V:** state card with concise cause; detailed diagnostics progressive. |
| SR07 | Accessible announcements “Review inbox loaded with {n} document(s).” / “The review inbox could not be loaded.” | Same `32–36,44` | Screen-reader outcome. **L:** preserve accurate result; this is not visible clutter. |

### 9.3 Survey document and fact inventory

| ID | Current text / dynamic family | Source | Why it exists; triage and destination |
|---|---|---|---|
| SR08 | “Loading survey document…”; “Retrieving the document, its extracted facts, and any dependent buildability conclusions.” | `components/survey-review/SurveyReviewScreen.tsx:173–180` | Loading orientation. **V:** heading and skeleton; second sentence **R** only after accessible loading description carries scope. |
| SR09 | `{document.title}`; “Target BBL {…} · digest {prefix}…”; document state badge | Same `274–285` | Identity, immutable reference. **L+V:** title + BBL; full digest/provenance in Document details. |
| SR10 | “Recalculating dependent conclusions…” | Same `285–289` | In-progress action. **L+V:** busy indicator with text; does not prove recalculation succeeded. |
| SR11 | “Next: confirm or reject the document below.”; “Next: resolve {n} open item(s) (highest priority first).”; “Rejected facts block confirmation — reopen the document or upload a corrected survey.”; “All facts are resolved. A designated professional must confirm the document.”; “All material facts are resolved.” | `lib/surveyReview/model.ts:130–145`; rendered `SurveyReviewScreen.tsx:291–293` | Dominant next action, truthful completion. **L+V:** action-adjacent “Review {n} open items” / professional-decision state. Verify uploaded/empty fallback and actual upload availability. |
| SR12 | “Extraction is temporarily unavailable; the document is stored safely and unprocessed. It rests in its uploaded state and no extracted facts or overlay are shown — nothing is fabricated.” | `SurveyReviewScreen.tsx:296–303` | Processing gap/no invented evidence. **L+V:** one “Uploaded · Extraction unavailable” state; full reason expandable. |
| SR13 | “Original document and overlays”; “Page {n}”; “Document state history”; “Back to the review inbox” | Same `309–336,373–376` | Source access, pagination, audit, navigation. **V:** retain controls; avoid nested audit disclosures, currently added around StateHistory in compact mode. |
| SR14 | Announcements: “Loaded survey document for BBL {…}. Document state: {…}.”; “The survey document could not be loaded.”; “Decision recorded. A recalculation of dependent conclusions was requested.” | Same `75–79,93–97,172` | Accessible outcome and requested≠completed recalculation. **L:** preserve truthfulness. |
| SR15 | “This item changed while you were editing. The current state is shown; your draft below is preserved — re-apply it.” | Same `151–155` | Concurrency/draft recovery. **L+V:** persistent “Updated by another reviewer · Draft preserved” beside original/current/draft comparison. |
| SR16 | “Extracted facts”; “Needs attention first · Unconfirmed until professional review.” / “Ordered by decision urgency. Each fact is unconfirmed evidence until a designated professional confirms it — nothing here is verified by extraction alone.”; “This document has no extracted facts yet.” | `components/survey-review/FactList.tsx:24–34` | Order, no automatic confirmation, empty state. **L+V:** issue-first list with per-fact unconfirmed state and Review rules detail. |
| SR17 | `{fact.display_label}`, normalized value and units; “AI-drafted label”; title “This label was drafted by AI and is not authoritative.” | `components/survey-review/FactRow.tsx:39–51` | Fact content/units/AI provenance. **L+V:** one row; AI marker stays adjacent and accessible on click/focus. |
| SR18 | Confirmation state; “{n} conflict(s)”; “{n} unresolved”; “{n} check(s) passed” | Same `54–68` | Independent confirmation/check dimensions. **L+V:** separate compact statuses; never turn checks passed into Verified. |
| SR19 | Focused fact label, confirmation badge, extraction method + “· advisory extraction, never authoritative” | `components/survey-review/FocusedItem.tsx:89–98` | Selection, professional state, origin. **L+V:** inspector header badges; duplicate method detail moves to Source. |
| SR20 | “Deterministic checks” | Same `103–104` | Distinguishes checks from professional review. **V:** compact check summary. |
| SR21 | “Accept value” / “Affirming…”; “Correct…”; “Reject…” | Same `106–135` | Distinct actions. **L+V:** action bar; assess “Affirm value” wording through reviewer gate without altering behavior. |
| SR22 | “Some actions are disabled for your role. Rejecting a detection is reserved for a designated professional. The server enforces this regardless of what is shown here.” | Same `137–145` | Authority and disabled-action reason. **L+V:** locked “Professional role required” state and Why?; server-enforcement detail in role explanation. |
| SR23 | “You affirmed this value this session at {time}. A recalculation of dependent conclusions was requested. (Affirmation is recorded in the server audit trail; this marker is a session reminder.)” | Same `146–151` | Session marker≠professional confirmation; requested≠completed. **L+V:** “Affirmed this session · {time}” and “Recalculation requested” plus precise action details. |
| SR24 | “Accept affirms the current value and requests a dependent recalculation. It is not professional confirmation — a fact becomes confirmed only when a designated professional confirms the whole document.” | Same `152–157` | Prevents action misconception. **L+V:** short local distinction and expandable full meaning. |
| SR25 | “This detection was rejected. A corrected upload or re-extraction is needed to supply a usable value; it blocks document confirmation until then.” | Same `159–163` | Unusable fact/block/recovery. **L+V:** persistent Rejected and Blocks confirmation; full recovery detail; no false upload affordance. |
| SR26 | Accept error from actionFailureCopy; fallback “The action could not be completed.”; “Reject this detection” / “Reject detection” | Same `78–85,165–168,184–190` | Failure and reasoned rejection. **L+V:** contextual error; rejection form opens on demand. |

### 9.4 Original document, correction and checks

| ID | Current text / dynamic family | Source | Why it exists; triage and destination |
|---|---|---|---|
| SR27 | “Extraction is temporarily unavailable, so this document is stored safely and unprocessed. No overlay or extracted facts are shown — nothing is fabricated. The document rests in its uploaded state.” | `components/survey-review/DocumentOverlay.tsx:95–103` | Same gap as SR12. **L; duplicate R:** compact canvas empty state and document badge, with one shared complete reason; remove repeated full paragraph only after mapping. |
| SR28 | “Page {n} — extracted-geometry annotation (not a georeferenced map)”; “Show only open items” | Same `110–123` | Document coordinates≠site geometry. **L+V:** “Survey annotation · Not a site map” badge, page selector and filter. |
| SR29 | “Text summary of the overlay findings”; per-fact label/value/unit/state + “— has a data conflict”, “— has an unresolved check”, “(located by vector object reference)”; “No extracted facts on this page.” | Same `181–198` | Equivalent accessible evidence, including non-boxed facts. **L+V:** retain disclosure or equivalent synchronized text list. |
| SR30 | Accessible labels “Original document, page {n}, with extracted-geometry overlay”; “Extracted-geometry overlay for page {n}”; “{label}: {value} {units}. {confirmation}. Select to focus.” | Same `110,131,156` | Keyboard/screen-reader operability. **L:** preserve. |
| SR31 | “Original extraction (immutable)”; “Original detected value”; “Original normalized value”; baseline values/units; “Extraction method”; method + “— advisory, never authoritative” | `components/survey-review/CorrectionHistory.tsx:29–54` | Original/current and normalization provenance. **L+V:** paired Original → Current values; method in Source details. |
| SR32 | “Original document”; “Page {n} of the immutable original (digest {prefix}…).”; “The original bytes and this value are unchanged after any correction.” / “The original bytes are not retrievable in this environment (B-001), but the digest and this value are unchanged.” | Same `55–63` | Preservation≠retrievability. **L+V:** separate “Original preserved” and “Original unavailable” states; digest/environment detail in Source. |
| SR33 | “Current value”; value/units; “Never corrected.” / “{n} correction(s) applied (see the chain below). The original above is preserved.” | Same `68–80` | Current reading/correction count/immutability. **L+V:** value + corrections disclosure. Location instruction **R** after count directly opens history. |
| SR34 | “Append-only correction history (oldest first)”; “When”, “By (role)”, “From”, “To”, “Reason”; timestamps, role/identity, previous/current values/units, reasons | Same `85–115` | Attributed chronological audit and explicit unit changes. **L+V:** progressive history; original/current comparison visible during editing. |
| SR35 | “No deterministic check has run against this fact yet.”; “{n} deterministic check(s) in conflict”; “{n} check(s) unresolved”; “{n} check(s) passed”; status glosses and downstream reason | `components/survey-review/ChecksPanel.tsx:26–65` | Untested/failed/unresolved/passed distinction. **L+V:** compact counts and focused reason; untested never looks passed. |
| SR36 | “This conflict cannot be dismissed. Resolve it by correcting the fact or rejecting the detection — both require a reason and are audited.” | Same `69–73` | No click-away contradiction, audited resolution. **L+V:** visible conflict and Correct/Reject; Why no dismiss? detail. |
| SR37 | “Correct this fact”; “Original detected value (immutable)”; “Corrected normalized value”; “(numeric)”; “Current: {value}”; “Units (leave blank if unitless)”; “Reason (required)”; “Apply correction” / “Applying…”; “Cancel” | `components/survey-review/CorrectionForm.tsx:86–160` | Safe comparison, units/type/reason/submission. **L+V:** focused form; original/current/proposed value and unit labels directly visible while editing. |
| SR38 | “A reason is required for every correction.”; “Nothing changed. A correction must change the value or units — use Accept to affirm an unchanged value.”; action failure/fallback “The correction could not be applied.”; stale notice | Same `52–82,89–92,145–153` | Validation, no-op prevention, concurrency/recovery. **L+V:** field errors and short form state; integrity details progressive. |
| SR39 | Reason form heading/submit label; “Reason (required)”; “Working…”; “Cancel”; “A reason is required.”; failure/fallback “The action could not be completed.” | `components/survey-review/ReasonForm.tsx:33–86` | Rejection/reopen requires reason. **L+V:** retain task-specific confirmation form, not generic OK. |

### 9.5 Downstream consequence and document decision

| ID | Current text / dynamic family | Source | Why it exists; triage and destination |
|---|---|---|---|
| SR40 | “Downstream buildability impact”; “No survey fact currently blocks or provisionally affects a dependent buildability conclusion.” | `components/survey-review/DownstreamImpact.tsx:37–43` | Scope-limited absence of survey impact≠whole-property approval. **L+V:** “Survey impact: none” with scoped explanation. |
| SR41 | “{n} fact(s) block dependent conclusions” / “No fact blocks a dependent conclusion”; “{n} render(s a) dependent conclusion(s) provisional until confirmation.” | Same `46–52` | Blocked≠provisional. **L+V:** two counts/chips opening filtered facts. |
| SR42 | “Affected facts and reasons”; fact label; Blocked/Provisional; impact reason; “Coverage: {coverage_status} — {gloss}” | Same `54–80` | Evidence-to-consequence path and backend reasons. **L+V:** expandable list. Backend does not name affected conclusions here; do not invent them. |
| SR43 | “Document confirmed”; “A designated professional confirmed this document after per-fact review. Each fact still carries its own confirmation state above.” | `components/survey-review/ConfirmDocumentPanel.tsx:57–64` | Document confirmation retains per-fact state. **L+V:** confirmed document header and independent fact states. |
| SR44 | “Reopen document…”; “Reopen this document (post-confirmation contradiction)”; “Reopen document”; “Only a designated professional can reopen a confirmed document.” | Same `65–89` | Audited reversal/authority. **L+V:** secondary action/locked capability and reason form. |
| SR45 | “Document rejected”; “This document was professionally rejected and is terminal. A corrected upload is a new document with its own digest.” | Same `95–102` | Terminal state/new source identity. **L+V:** Rejected and explicit recovery detail. |
| SR46 | “Document decision”; “Only a designated qualified professional can confirm or reject this document. Your role can review and correct facts, but the document decision is reserved for that role. The specific qualifying designation is pending an owner decision.” | Same `108–117` | Authority and unresolved role policy. **L+V:** role/capability strip; precise pending designation in role details. Do not imply resolved policy. |
| SR47 | “Confirm document” / “Confirming…”; “Reject document…”; “Reject this document”; “Reject document” | Same `120–139,202–208` | Explicit document decision. **L+V:** sticky decision bar; keep distinct from fact actions. |
| SR48 | “Confirmation is unavailable until every material fact passes its deterministic checks and no material fact is rejected. These facts still block confirmation:” | Same `144–150` | Backend confirmation gate. **L+V:** “Confirmation blocked · {n} facts” beside disabled control and named blockers. |
| SR49 | Blocking label + “— professionally rejected (blocks confirmation until replaced)” / “— has a data conflict” / “— has an unresolved check”; “This document has no material facts to confirm yet.” | Same `151–175` | Exact target/reason; empty≠complete. **L+V:** linked blocker list with reason chips. |
| SR50 | Confirmation failure/fallback “The document could not be confirmed.”; rejected fact list + “— reject this document or upload a corrected survey to proceed.” | Same `43–53,179–199` | Server refusal, exact rejected facts/recovery. **L+V:** action-local error and directly reachable blockers. |
| SR51 | “Document audit trail ({n} transition(s))”; “State transitions (oldest first)”; “When”, “From → To”, “Actor”, “Reason”; attributed transitions/timestamps/reasons | `components/survey-review/StateHistory.tsx:14–39` | Lifecycle provenance. **L+V:** one progressive audit surface. |

### 9.6 Shared survey vocabulary and errors

| ID | Full family | Source | Preservation / treatment |
|---|---|---|---|
| SR52 | Document states Uploaded, Processing, Auto-extracted, Needs review, Rejected, Professionally confirmed; glosses preserve immutable/unprocessed, read-only processing, extraction never confirmation, professional resolution, terminal/new digest, professional review/per-fact states | `lib/surveyReview/labels.ts:25–63` | **L+V:** exact state meaning with label, symbol and accessible explanation. |
| SR53 | Fact states Unconfirmed evidence, Confirmed, Rejected; check states Conflict, Unresolved, Checks passed; consequences Blocked, Provisional | Same `70–137` | **L:** three different dimensions; never collapse into one green/red verdict. |
| SR54 | “Official/derived sources disagree; nothing was resolved.” / “A qualified professional must review this before reliance.” | Same `143–146` | **L+V:** coverage badge and full meaning in detail. |
| SR55 | “Vector object extraction”, “Embedded text extraction”, “OCR text (advisory)”, “Line / symbol detection (advisory)”, “AI-assisted classification (advisory)”, “Deterministic geometry reconstruction”, “Unknown extraction method” | Same `149–165` | **L+V:** method provenance; unknown stays unknown/advisory. |
| SR56 | “Boundary segment distance”, “Boundary bearing”, “Stated lot area”, “Scale statement”, “North arrow orientation”, “Elevation value”, “Address text”; humanized wire-value fallback | Same `173–189` | **V:** meaningful fact labels; do not fabricate classifications. |
| SR57 | StatusBadge label, symbol, title gloss, visually hidden “— {gloss}” | `components/survey-review/StatusBadge.tsx:18–27` | **L:** accessible/non-color meaning. Add keyboard/touch detail rather than relying on native title. Audit repeated hidden glosses for excessive screen-reader verbosity. |
| SR58 | “You are not authorized for this action”; “The document was not found”; “The fact was not found”; “This item was updated by someone else”; “The correction was rejected by a deterministic check”; accompanying bodies describe role, return/reopen, unchanged state, preserved draft, immutable original and safe next step | `lib/surveyReview/errorCopy.ts:25–57` | **L+V:** short cause/next action, complete integrity explanations progressive. |
| SR59 | “Rejected facts block confirmation”; “That transition is not allowed from the current state”; “Only a designated professional can do this”; “A reason is required”; “Reopen the document before editing a confirmed fact”; bodies explain rejected facts, current state/H5, authority, reason and audited reopening | Same `58–91` | **L+V:** blocker/authority/reason/reopen requirement apparent at the failed action. |
| SR60 | Action: “Could not reach the review service” + message; “The action took too long” + cancelled/no partial write/retry safe; “Unexpected response from the review service” + HTTP/untrusted/not applied; “The response did not match the review contract” + not applied/platform attention | Same `98–129` | **L+V:** preserve transport/timeout/contract/validation distinction. Diagnostic HTTP/contract details progressive. Do not broaden backend guarantees. |
| SR61 | Read: “No survey document found”; “You are not authorized to view this document”; “Could not reach the review service”; “The document took too long to load”; “Unexpected response from the review service”; “The response did not match the review contract”; associated reason/cancelled/retry/untrusted/not-shown bodies | Same `133–170` | **L+V:** compact error card preserving safe-retry distinction. |
| SR62 | Failure title/body; conditional “Retry”; “Back to the review inbox” | `components/survey-review/ReadFailureState.tsx:23–35` | **L+V:** actionable failure state instead of blank screen. |

### 9.7 Survey mockup direction

**Inbox.** One title row, property context, compact status filters/counts, then document rows with name, BBL, open-item count and status. One empty/failed card replaces the list when needed. Review rules carries the full extraction/authority explanation; upload availability remains a visible capability state.

**Review.** Topbar: document title, BBL, lifecycle badge, Document details. A narrow persistent strip shows conflicts, unresolved items, unconfirmed facts and the current next action. The source document/annotations occupy the main pane; urgency-ordered facts sit beside it. Selecting a fact opens its focused inspector. On narrow screens, switch explicitly between Document and Facts while preserving selection.

**Focused inspector.** Label, value/unit and separate confirmation/check statuses lead. Compact Original → Current values remain visible; editing expands proposed value/unit/reason. Source, Checks and History expand exact evidence. Current blocking contradiction reason remains visible without opening general help. Affirm / Correct / Reject actions retain accurate semantics and accessible role restrictions.

**Decision bar.** A sticky footer shows Confirmation blocked and an exact linked blocker count. When backend eligibility permits, show Confirm document and secondary Reject. Do not compute eligibility anew in presentation code. Downstream blocked/provisional counts remain visible; per-fact coverage and reasons occupy one expansion. Confirmed/rejected states preserve consequences and permitted recovery actions.

### 9.8 Owner dashboard inventory

| ID | Current text / dynamic family | Source | Why / treatment |
|---|---|---|---|
| DB01 | “INTERNAL DEVELOPMENT BUILD — read-only owner observability over the project-control system. Not a public product, no access control yet, and not a legal determination. Do not share outside the engineering team.” | `components/dashboard/InternalBanner.tsx:10–13` | Internal/access/legal boundary. **L+V:** persistent Internal / Read-only state, full restrictions in banner detail; no public-exposure authorization. |
| DB02 | Project name; “Owner Mission Control · read-only”; “Owner”, “Technical”; “Mission Control”, “Product Map”, “Current Work”, “Roadmap”, “What Changed” | `components/dashboard/DashboardApp.tsx:15–20,44–62` | Identity/navigation/detail level. **V:** retain clean shell and engineering scope. |
| DB03 | “Progress unavailable — project state could not be verified. The dashboard could not read the control-plane files. Showing no fabricated numbers.” | `components/dashboard/MissionControl.tsx:27–31` | Unknown≠0%. **L+V:** Unavailable state and cause details. |
| DB04 | “Engineering completion”; “Launch readiness (architect beta)” | Same `34–36` | Distinct metrics/gates. **L+V:** retain both explicit labels. |
| DB05 | “System health”, health reason; “Current work”, task ID/title or “No active task”; “Blocked tasks”, count, “Needs attention” / “None”; “CI on main”, Passing/Failing/Running/Unknown, “stale” / “live data unavailable” / check count; “Open PRs”, count, “main @ {sha}” / “main head unknown”; “Milestone”, milestone/checkpoint | Same `39–82`; CI labels `6–10` | Snapshot/freshness. **L+V:** retain tiles; Owner mode leads with owner title, technical IDs secondary. Unknown never becomes 0. |
| DB06 | “Biggest things preventing an architect beta”; “Nothing outstanding on the launch-critical path.”; blocker rank/label/detail/type | Same `85–108` | Derived launch gaps. **L+V:** concise ranked list with precisely scoped empty state. |
| DB07 | “This is a read-only observatory over the project-control ledger. Progress is derived deterministically from recorded state, not from commit volume. Rules shown in later systems are engineering drafts and are not legally verified until a qualified human approves them (gate G6).” | Same `112–117` | Calculation and legal-verification boundary. **L+V:** calculation/status details; unverified-rules state stays attached where relevant. |
| DB08 | “Ledger read {timestamp}”; “Synced {time}” / “Live data STALE — last synced {time}” / “Live data unavailable”; “never” fallback | Same `119–121`; `components/dashboard/ui.tsx:120–127` | Different project-read and live-GitHub timestamps. **L+V:** compact data-status bar and expandable source timestamps. |
| DB09 | Health Healthy/Attention/Problem/Unknown; status Planned/Ready/Active/Testing/In review/Accepted/Blocked/Canceled/Unknown | `ui.tsx:11–16,30–39` | Operational state without color dependence. **L+V:** retain label and symbol. |
| DB10 | “unavailable”; “Unavailable” / “Partial”; “Progress unavailable — project state could not be verified.” / “Partial — {weight}% of the model could not be verified.”; “How is this calculated?”; method; “Exact: {n}%”; “System”, “Weight”, “Done”, “Contribution”; “(capped until {gate})”; unknown/— | Same `51–115` | Null≠zero and reproducibility. **L+V:** keep progressive calculation; consolidate repeated cause only with explicit mapping. |
| DB11 | “How the systems connect (left → right = the architect journey). Colour shows health; every node is also labelled. Select a system for detail. Scroll sideways to see all.” | `components/dashboard/ProductMap.tsx:69–72` | Orientation/instruction. **V; partial R:** axis labels, affordances and accessible help replace narration after equivalence is verified. |
| DB12 | System name, health, “{n}% built” / “unknown”; legend Healthy/Attention/Problem/Unknown/“Critical for beta”; accessible completion/criticality label | Same `109–145` | Dependencies/health/progress/criticality. **L+V:** preserve; responsive vertical layout or zoom-to-fit reduces sideways-navigation instruction. |
| DB13 | “What’s being worked on now”; “No task is currently in an active lifecycle state.”; “Also active ({n})”; “Next up”; “No unblocked task is ready to start next.” | `components/dashboard/CurrentWork.tsx:65–95` | Lifecycle-based work/readiness. **L+V:** primary task and compact next list. |
| DB14 | Task ID/status/title/owner description; gates/pass/pending; “Before acceptance: {blockers}.”; “Status note: {reconciliation}”; “Branch”, “PR”, “Milestone”, “System”, “Depends on” | Same `6–48` | Conditions/reconciliation/provenance. **L+V:** owner title/status and blocker-count expansion; technical identifiers in detail mode. |
| DB15 | “Roadmap — by product system”; “Two bars per system: built (engineering) and launch-ready (accepted & verified). They differ on purpose.”; system name/“critical”/health/status; “Built”, “Launch-ready”; “{n} task(s) · {n} accepted”; “Not started — no tasks contracted yet.”; task ID/title/status/PR | `components/dashboard/Roadmap.tsx:18–65` | Built≠accepted readiness. **L+V:** dual labeled bars; explanatory sentence becomes label help. |
| DB16 | “What changed”; “Meaningful control-plane events (acceptances, gate reviews, merges, blockers, checkpoints) — not a raw commit log.”; “Today ({n})”; “No control-plane changes recorded today.”; “Earlier”; event title/kind/time | `components/dashboard/ActivityFeed.tsx:5–13,20–58` | Event scope/chronology. **L+V:** timeline and event filters; source-scope explanation progressive. |
| DB17 | System name; “Close detail”; critical/health/status; “What it does”, purpose; “Why it matters”, why; “Can an architect rely on this today?” | `components/dashboard/SystemDrawer.tsx:54–74` | System meaning/readiness. **V:** readiness and purpose lead; Why detail expandable. Explicitly scope reliance to capability readiness. |
| DB18 | “Unknown — readiness could not be verified.”; “Yes — this system is accepted and healthy.”; “No — this system has not been started yet.”; “No — this system currently needs attention (see health below).”; “Not yet — it is built or partially accepted but not fully launch-ready.” | Same `7–12` | Code completion≠reliance. **L+V:** launch-readiness status and reason; never property approval. |
| DB19 | “Built”, “Launch-ready”; “What is still missing?”; “No tasks contracted yet.”; “Pending gate(s): {…}.”; “{n} task(s) not yet accepted.”; “{n} more planned task(s) not yet contracted.”; “Nothing outstanding.”; “Health”, reasons | Same `15–25,77–95` | Task/gate/completion/health gaps. **L+V:** compact grouped issues, avoid duplicate prose/counts. |
| DB20 | “Technical detail”; “Engineering weight”, “Launch weight”, “Tasks”; “{n} accepted / {n} contracted / {n} expected”; “Depends on”; “Task”, “Status”, “Gates”; task/PR/gates/pending | Same `100–125` | Reproducible technical detail. **V:** collapsed in Owner view. |
| DB21 | “INTERNAL DEVELOPMENT BUILD — owner dashboard.”; “Dashboard temporarily unavailable”; “The owner dashboard hit an unexpected error and was contained here. This is internal, read-only observability tooling — the property-analysis product is unaffected. No project state was changed.”; “Reference: {digest}”; “Try again” | `app/dashboard/error.tsx:19–34` | Isolated error/unchanged project/opaque reference. **L+V:** concise error/recovery, reference in details. |
| DB22 | Browser title “Owner Mission Control — NYC Buildability (internal)” | `app/dashboard/page.tsx:12–14` | Route identity/internal scope. **V:** retain; fail-off source at `25–26` is not proof of deployed flag state. |

Dashboard dynamic-copy producers read: `lib/dashboard/activity.ts:39–108` (Accepted, Started, Merged PR, gate result, Blocker opened/resolved, Checkpoint); `health.ts:36–79,95–115` (unknown data, inconsistency, blocked tasks, open blockers, failing CI, independent review, stale/unavailable GitHub, health summary); `launch.ts:24–56` (unknown readiness, not started, unmet gates, accepted pieces, owner action); `model.ts:148–161,185–204` (acceptance blockers, reconciliation, owner titles/descriptions); `progress.ts:138–140` (exact engineering/launch methods). These are **L+V** when rendered: short state/count first, exact cause/calculation in detail. Actual project-control-supplied titles, descriptions and live values were deliberately not retrieved.

**Dashboard mockup direction.** Retain the shell/five tabs. Mission view: two metrics, compact operational row, three leading blockers and View all, one data-status footer. System drawer: name, health/readiness, purpose, dual bars, outstanding items; explanatory and technical details collapsed. Keep owner observability independent of architect property verdicts.

### 9.9 Existing test requirements read, not executed

| Test source | Meaning protected |
|---|---|
| `components/survey-review/__tests__/survey-review.test.tsx:43–60` | Compact review keeps facts, conflicts, actions, disabled confirmation and downstream summary visible; source/affected-fact details remain reachable. |
| Same `61–69` | Unconfirmed evidence appears; Verified does not. |
| Same `71–84` | Next action counts open checks then changes to document confirmation. |
| Same `88–108` | Immutable original remains; no dismiss/acknowledge/ignore conflict escape; resolution can change blocked to provisional, not auto-final. |
| Same `111–120` | Session affirmation and recalculation-requested wording. |
| Same `123–174` | Draft survives concurrent update/remount. |
| Same `176–215` | Role restriction, disabled confirmation and named blockers. |
| Same `218–227` | Recoverable initial-read failure with retry. |
| `lib/dashboard/__tests__/engine.test.ts:13–41` | Different engineering/launch metrics, G6 cap, reproducible calculation. |
| Same `76–95` | Accepted historical task never falsely shows pending gates. |
| Same `99–116` | Health independent of completion. |
| Same `119–149` | Unknown/degraded never coerced; contradictions surfaced. |
| Same `152–183` | Lifecycle-based current work and deterministic activity/blockers. |
| Same `197–213` | Last-known data explicitly stale. |
| Same `216–223` | Owner route fail-safe off. |

The dashboard test source at `226–238` contains a real-ledger smoke test. It was **not executed**; its loader and project-control inputs were not accessed.

### 9.10 Coverage manifest

Read in full before test review:

- `components/survey-review/{ChecksPanel,ConfirmDocumentPanel,CorrectionForm,CorrectionHistory,DocumentOverlay,DownstreamImpact,FactList,FactRow,FocusedItem,ReadFailureState,ReasonForm,ReviewInbox,StateHistory,StatusBadge,SurveyReviewScreen}.tsx`.
- `lib/surveyReview/{errorCopy,labels,model}.ts`.
- `app/survey/review/page.tsx` and `app/survey/review/[documentId]/page.tsx`.
- `components/dashboard/{ActivityFeed,CurrentWork,DashboardApp,InternalBanner,MissionControl,ProductMap,Roadmap,SystemDrawer,ui}.tsx`.
- `app/dashboard/{page,error}.tsx`.
- `lib/dashboard/{activity,assemble,currentWork,health,launch,model,progress}.ts`.
- The two test files cited above, after the source review.

Survey routes render `components/architect/SurveyWorkspace`, whose surrounding shell belongs to the architect workspace inventory. Both survey routes are internally gated in source; this is not a claim about public/live availability. No dashboard loader or project-control data was accessed.

## 10. Disclosure origins, no-loss requirements, and test migration

This section traces why the copy exists. All anchors refer to the assessed GitHub commit `dc5a763e7494de62a0dbfd8e60e8cbbade73bc8c`. The tests were inspected as source; they were not executed in this assessment.

### 10.1 What “must survive” means

The repository generally requires preservation of a claim's meaning, state, evidence, and consequence. It does not establish that every explanatory paragraph is a statutory requirement. In this report, **must-survive legal/product honesty** means that the user must still understand the applicable limitation and be able to inspect its basis. **Exact-copy pin** means that a current test or recorded product direction expects particular wording. These are distinct requirements.

Redesign can move a technical explanation into an accessible disclosure while keeping the material status next to the affected result. It cannot hide a conflict while leaving its result apparently usable, replace a missing value with an invented value, turn a recorded fact into a legal allowance, or make a proposed shape look like a permitted building. Exact-copy pins require an explicit, reviewed test migration where wording changes; weakening selectors or replacing the wording with an untested synonym is not evidence that the obligation survived.

### 10.2 No-loss requirements

Paths in the following table are relative to `apps/web/`. These rows supplement the element-by-element screen inventories; they identify the minimum meaning and behavior that a redesign must preserve.

| Obligation | Source evidence | Required outcome in the redesign |
|---|---|---|
| Preliminary product scope and internal-build identity | `e2e/honesty.spec.ts:11–23` pins the internal banner and visible PRD §29 disclaimer | Retain the preliminary/non-legal-opinion disclosure and the applicable internal-build state. Do not replace either with an unlabeled icon. The product-policy basis is PRD §29, not a claim that each sentence is mandated by statute. |
| Draft calculation is not a verified or final permission | `e2e/honesty.spec.ts:35–47`; `e2e/rule-evaluation.spec.ts:26–38` | Keep an adjacent textual draft/scope state and accessible supporting detail. Do not imply unrestricted permission through green styling or an approval icon. |
| City reference, evaluated draft, and existing building are different claim classes | `e2e/development-limits.spec.ts:19–32,64–69`; `src/components/architect/__tests__/development-limits.test.tsx:150–171,274–299` | Clearly label the PLUTO reference, evaluated FAR, square-foot cap, and existing built FAR. Existing-building information can remain collapsed; the source values cannot disappear. |
| Unknown, source unavailable, conflicting, not calculated, and genuine zero are different | `src/components/architect/__tests__/development-limits.test.tsx:283–318` | Preserve named states and genuine zero. A universal dash would erase distinctions the system already makes. |
| Numerical summaries need trustworthy association and usable evidence | `e2e/development-limits.spec.ts:72–118`; `src/components/architect/__tests__/development-limits.test.tsx:417–520` | Withhold promoted figures for malformed traces, missing/unequal fingerprints, conflicts, or unsupported records. Keep the captured returned record inspectable. |
| Important missing official inputs are discoverable without erasing the remaining omissions | `e2e/partial-and-conflict.spec.ts:18–34` | Preserve the important missing-input state and an explicit count/disclosure for the remainder. Severity and consequence can determine prominence. |
| Conflicts retain both values, sources, and unresolved status | `e2e/partial-and-conflict.spec.ts:43–62` | An expandable side-by-side comparison can replace prose, but no value is silently selected and the conflict remains visible at the affected result. |
| Spatial uncertainty remains uncertain | `e2e/rule-evaluation.spec.ts:41–58` | Preserve district candidates/share ranges and the no-value professional-review fail-safe. Do not turn a range into a point estimate. |
| Provenance preserves original field/value, source, and link meaning | `e2e/development-limits.spec.ts:36–47`; `e2e/architect-workspace.spec.ts:115–139`; `e2e/partial-and-conflict.spec.ts:71–77` | A shared evidence drawer must retain exact source records and direct-record versus dataset links. The source-column fallback remains explicitly identified when used. |
| Progressive disclosure remains accessible | `e2e/architect-workspace.spec.ts:149–170`; `e2e/rule-evaluation.spec.ts:79–99` | Source drawer focus, Escape return, mobile visibility, keyboard expansion, and polite background announcements survive. Color alone does not carry state. |
| Unavailable capability is not a populated product result | `e2e/architect-workspace.spec.ts:141–143` | Keep an honest unavailable state on reachable routes. Navigation can be reorganized, but the product must not imply that planned features work. |
| Map failure and map accuracy have separate meanings | `e2e/architect-workspace.spec.ts:82–92`; `src/components/address/__tests__/lot-outline-map.test.tsx:827–841` | Keep the approximate-outline accuracy/source line and truthful rendered/unavailable state. A street-layer error does not erase a working parcel. EPSG mechanics already belong behind a disclosure. |
| Printing does not silently drop screen-collapsed facts and sources | `e2e/architect-workspace.spec.ts:185–213`; `e2e/development-limits.spec.ts:91–102` | Print expands readable facts/provenance, raw appendix remains optional, and the screen's open/closed state is restored afterward. |
| Recovery messages describe available actions | `e2e/architect-workspace.spec.ts:216–235` | Short, state-specific status plus actual full-address/manual/BBL controls. Do not suggest retrying a path that the current outcome makes unavailable. |

### 10.3 Copy walls and wording that need deliberate migration

These are concrete regression boundaries. Some protect semantics; some additionally pin current presentation. A future task should record the old element, new location/form, preserved meaning, and revised assertion before removing the old string.

| Current wall or exact pin | Source anchor, relative to `apps/web/` | Migration constraint |
|---|---|---|
| Unqualified maximum-building claims are prohibited | `src/components/architect/__tests__/max-envelope-panel.test.tsx:274–290` scans `MaxEnvelopePanel.tsx`, `max-envelope-api.ts`, `proposal-draft.ts`, `ArchitectEntry.tsx`, and `ProposalEditor.tsx` after lowercasing; bans `maximum allowed building` and `demonstrated maximum` | Preserve the claim-class prohibition semantically. DB-050(l) notes that punctuation/hyphenation can evade the literal test; such evasion would not make a claim valid. |
| Preliminary limits title and verbatim server disclosure | `src/components/architect/__tests__/max-envelope-panel.test.tsx:119–140` | The title is “Preliminary development limits”; server disclosure, binding rule/version, and a typed reason instead of a missing numerical value are pinned. Any movement/shortening needs an explicit approved replacement and no-loss assertion. |
| Generated option, unresolved competition, and incomplete aggregate | `src/components/architect/__tests__/max-envelope-panel.test.tsx:168–204` | The building-shaped result is a “Generated building option.” Competing rule IDs remain unresolved; any gap prevents complete appearance; all checked still carries preliminary/professional-review scope. |
| Candidate adoption requires a contained fit | `src/components/architect/__tests__/max-envelope-panel.test.tsx:221–248` | No adopt affordance for unsupported geometry or a non-contained candidate. Do not ship a permanently dead adoption button with optimistic explanatory text. |
| Internal street-FAR jargon is already prohibited on the calm result panel | `src/components/architect/__tests__/report-view.test.tsx:109–143` | Directive IDs, `needs_review`, raw determination tokens, and similar server mechanics belong in Evidence. This existing test is evidence for progressive disclosure, not a reason to keep a text wall. |
| Wide-street review labels are determination-specific | `src/components/architect/__tests__/report-view.test.tsx:146–185` | A confident street determination must not be mislabeled “Professional review required.” A non-review null-FAR fallback reads “Not calculated.” This does not remove the distinct product-wide preliminary scope. |
| Conservative FAR cannot wear the conditional-FAR caption | `src/components/architect/__tests__/report-view.test.tsx:189–250`; `src/components/architect/__tests__/development-limits.test.tsx:655–682` | Preserve the actual within/not-within/review state and screen/report parity. |
| Condo records are not computed allowances | `src/components/architect/__tests__/condo-resolution-display.test.tsx:389–407` | Preserve record-only class and all base lots. The current section-level vocabulary/decimal grep is a test implementation; assess legitimate source-label/timestamp changes deliberately instead of defeating the guard. |
| Unproven identity differences cannot be redescribed as benign condo substitution | `src/components/architect/__tests__/condo-resolution-display.test.tsx:306–348` | Preserve requested/returned identifiers, withholding, and neutral “no relationship inferred” meaning. A valid substitution needs its independently supported path. |
| Entered unit BBL and billing BBL are distinct | `src/components/architect/__tests__/condo-resolution-display.test.tsx:722–744` | Never relabel the entered unit as billing. Identical entered/billing identity already collapses into one line, demonstrating permitted deduplication. |
| Condo zoning gap scope is specific | `src/components/architect/__tests__/condo-resolution-display.test.tsx:754–778` | All-unknown and partial gaps differ. Keep already-recorded districts intact and name ZTLDB accessibly. “Out of scope” is not acceptable user-facing substitution. |
| Recorded identity/provenance values remain faithful | `src/components/architect/__tests__/condo-resolution-display.test.tsx:781–815` | Preserve meaningful headings, retrieval/version values, and district slashes such as `M1-5/R7-2`. A shorter label must not change the official designation. |
| Human site confirmation remains a record, with self-attestation/refusal/history | `src/components/architect/__tests__/condo-resolution-display.test.tsx:881–977` | Preserve confirmer, parcels, time, active/history status, discrepancy, and refusal for calculation use. A confirmation alone never unlocks withheld figures. |
| Drawing and checking concern proposed input | `src/components/architect/__tests__/proposal-check-report.test.tsx:26–63`; `src/components/architect/__tests__/proposal-outline-draw.test.tsx:127–199` | Keep proposed/not-city-record framing, visible could-not-check reason, conversion residual, and semantic-gap details. |
| Maximum overage is presently described with pinned “short” wording | `src/components/architect/__tests__/proposal-check-report.test.tsx:26–33,92–103`; DB-043(e) | Do not preserve misleading wording solely because a test pins it, but change it through a coordinated direction-aware copy/contract/assertion decision. |
| Gesture instructions correspond to the rendered interaction | `src/components/architect/__tests__/proposal-outline-draw.test.tsx:153–169`; `src/components/architect/__tests__/proposal-outline-map.test.tsx:183–309` | Do not invite click-to-place/move when the actual surface is absent/loading/noninteractive. Retain keyboard alternatives and truthful state changes. |

### 10.4 Backlog trace: why the disclosures accumulated

Every anchor in this table refers to `docs/DISCOVERY_BACKLOG.md`. Backend hardening is included only where it changes a visible claim, source, identity, or available action. The append-only ledger is historical: later closure sweeps override an earlier row's unchanged OPEN cell.

| Discovery and anchor | Disclosure meaning / relevant design consequence |
|---|---|
| DB-001 `:12` | Split-zoning apportionment is unsupported for the identified class. Preserve unresolved scope and all relevant districts rather than allowing the UI to imply a single-district answer. |
| DB-002 `:13`, DB-029 `:38`, DB-031 `:122` | Billing condo identifiers are not ordinary base-lot records. Resolution and records-view distinctions prevent false no-data or false allowance conclusions. DB-031's later closure is recorded below. |
| DB-003 `:14` | An official dataset can be stale at source. Preserve dataset version/freshness and scope; do not confuse retrieval time with source update time. |
| DB-005 `:16`, DB-018 `:32`, DB-019 `:34`, DB-027 `:91` | Validated ZoLa destination, absent-BBL honesty, coverage badges, and accessible names matter. Duplicate ZoLa affordances are expressly a design decision, not a legal obligation. |
| DB-006–009 `:17–20`, DB-024 `:62` | Distinct suggestion failures need accurate recovery. Circular instructions and copy that fails to name the rendered control were defects, not immutable disclosure requirements. |
| DB-008 `:19` | A six-second deadline can fail a healthy but slow address service. This is a latency/recovery issue; an additional explanatory paragraph cannot solve it. |
| DB-010 `:21`, DB-011 `:22`, DB-021 `:57`, DB-023 `:60` | Named-street exceptions, tangency interpretation, attestation, and unresolved legal conditions constrain the result. Surface the applicable uncertainty without mislabeling confident outcomes. |
| DB-014–016 `:26–29`, DB-020 `:56` | Wide-street outputs and accurate provenance needed to reach the UI; retrieved zoning context needed visibility. Source digests and actual provenance must survive any simplified presentation. |
| DB-017 `:31` | Flood/transit/split-zone/map flags need a coherent home. Consolidation is possible; silent omission is not. |
| DB-025 `:64`, DB-028 `:36`, DB-030 `:40` | Blanket professional-review wording was identified as over-cautious for confident street states. The whole-evaluation evidence banner remains a separate OPEN owner question; this assessment cannot label its exact text legally mandatory. |
| DB-026 `:89`, DB-032 `:124`, DB-033 `:127`, DB-035 `:139` | Entered, matched, and city record addresses can legitimately differ. Preserve those identities and stable confirm actions; expand a concise explanation only when needed. |
| DB-036 `:143`, DB-038 `:150`, DB-044 `:164` | Unit/billing labels, slash districts, ZTLDB gap scope, heading semantics, and spoken/visible identity must agree. Residual duplicate base-lot messages are acknowledged design debt. |
| DB-037 `:148` | Rear-yard evaluation lacks a professionally designated rear line; matching units do not establish legally comparable measurements. Multi-lot site assembly is also a professional interpretation, not a silent automatic merge. |
| DB-040 `:155`, DB-042 `:159` | A human site record cannot imply calculation authority. Recorded/current parcels, supersession, self-attestation, mixed billing/base substrate, and the absence of live confirmation controls affect honest presentation. |
| DB-043 `:161` | Proposal concerns include deletion focus, EPSG jargon, recovery action, incorrect direction wording, overloaded “coverage,” support references, report headings, and absent numerical variation deltas. These are interaction/structure issues as much as copy. |
| DB-045 `:167` | Drawing availability must correspond to usable conversion; described gestures must exist; adopted outlines must reconcile affected walls. Mount dependencies cannot be solved cosmetically. |
| DB-046 `:169`, DB-050 `:179–182` | Preliminary-limit/candidate generation needs authoritative geometry and cannot claim a maximum permitted building. Split-district omission, silent replacement, and adoption feedback remain material mount concerns. |
| DB-047 `:172`, DB-049 `:177` | Finite points, actual map availability, removed-wall feedback, incomplete rows, keyboard access, and competing live regions all require explicit state. A row marker and one announcement may replace several paragraphs without losing honesty. |
| DB-048 `:174` | Exact cross-render mock call counts were flaky. This is a test-quality issue, not new product disclosure copy. |

Latest explicit dispositions within the assessed ledger:

| Earlier row | Later disposition | What remains relevant |
|---|---|---|
| DB-031 records-view row `:122` | Closed by sweep `:144` | Do not report the entire records-view channel as still missing. Its successor identity/zoning riders are assessed separately. |
| DB-033 confirm-arc row `:127` | Closed `:140` | Do not re-open the original nine riders without current-source evidence. |
| DB-035 row `:139` | All four riders closed `:151` | The pixel CLS test caught a real map-status settle issue; current review must distinguish accepted repair from later concerns. |
| DB-036 row `:143` | Fully resolved `:165` | Slash-preserving display, labels, headings, and correspondence checks are protected behavior to preserve. |
| DB-042 row `:159` | (c)/(d)/(e) closed `:165`; (a)/(b) remain bound to site-definition mounting | Mixed-substrate caveat and useful path from site-confirmation refusal remain relevant. Later DB-044 still records residual redundancy/announcement concerns. |
| DB-043(a) deletion-focus finding `:161` | Applied-from-start closure recorded `:168` for the drawing increment | Do not assume every earlier editor surface has thereby received every separate advisory; verify the specific control/surface. |
| DB-045(a) real-parcel bridge validation `:167` | Queued as M5-T073 at `:178` | Queueing is not closure. Mount/readiness still needs concrete evidence. |
| DB-046(a)–(f) max-engine test cluster `:169` | Closed `:175` | Remaining watch/public-exposure/mount concerns are separate from those accepted tests. |
| DB-047(d)/(e) and DB-048 `:172,174` | Closed by M5-T071 sweep `:181` | The newer DB-049 describes remaining finite-row disclosure/readiness/a11y issues. Do not confuse those with the already-fixed count-only gate and absent-map instruction bug. |
| DB-050 `:179` | Extended `:180`, accepted-panel dispositions `:182` | Geometry threading is submitted/live work in this snapshot, not proven closed there. Split-district disclosure is explicitly required before mounting; other HJ/SEC adoption/mount riders remain. |

### 10.5 Reviewer memory: useful methods, not a complete mandate for paragraphs

All paths in this table are under `.claude/agent-memory/human-journey-reviewer/`.

| Memory and anchor | Valid lesson | Historical limitation |
|---|---|---|
| `project_a11y-announcement-review-technique.md:8–16` | Check the composed screen for competing live regions; clear repeat outcomes appropriately; distinguish retry focus from initial-load focus. | DOM assertions can miss duplicate spoken messages. This does not require extra visible paragraphs, and the memo itself says to carry real screen-reader verification separately. |
| `project_field-label-review-technique.md:8–12` | Inventory completeness alone misses invented semantics. The historical “Zoning map change code” label added a misleading meaning. Shorter/plain labels still need a traceable basis. | Its 108-field count is a historical review result, not current visual verification. |
| `project_rule-eval-two-factor-flag.md:8–12` | Flag-off should mean no network call, not merely absent DOM. Server and per-request gating protect other journeys. | The claim that production's gate stays closed is historical; it is not evidence of current deployment configuration. |
| `playwright-artifact-evidence.md:8–12` | Trace frames show only the viewport at action time; text assertions do not prove every below-fold element was visually inspected. | “Green runs have no standalone PNGs” is not universally current: `apps/web/e2e/architect-workspace.spec.ts:8–11` explicitly captures/attaches PNGs; development-limits tests also capture screenshots. |
| `MEMORY.md:1–3` | Indexes the Playwright artifact technique. | It is not a full list of disclosure obligations or reviewer findings. The backlog and tests carry much of the relevant history. |

Two apparent contradictions must not become redesign requirements: `apps/web/e2e/honesty.spec.ts:25–33` still asserts an unavailable-address/credentials state in its legacy journey, while `apps/web/e2e/architect-workspace.spec.ts:60–80,216–235` covers an active address journey. Treat these as route/mode/test-scope distinctions to reconcile, not a reason to re-disable current address search. Likewise, a blanket ban on positive “verified” claims does not prohibit an honest statement saying a draft is **not** verified; inspect the actual claim and scope rather than matching one word out of context.

### 10.6 Required migration record for every disclosure change

For each affected inventory item, the implementation task should carry: its current source/condition; the claim or risk it prevents; the new badge, row, diagram, or disclosure location; what remains visible before interaction; the accessible name/announcement; what prints; and the regression assertion that proves meaning was retained. Any item judged removable should identify the surviving equivalent or establish that it is redundant navigation/implementation chatter with no unique honest-gap or provenance meaning.

No tests, CI artifacts, or deployed browser journey were executed/reviewed by this disclosure-trace phase. The evidence above is repository source and existing test-contract inspection; it does not assert that the assessed commit passed tests or that every layout rendered correctly.

## 11. Product intent and authority boundary

The proposed direction restores the stated product intent:

| Requirement | Source | Consequence for this redesign |
|---|---|---|
| Simple controlled Property → Confirm → Compare → Evidence experience; normal analysts do not see ingestion internals | PRD §32.2; docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md:3–61 | Each view answers one decision. Endpoint names, schema mechanics and future-work narration leave the primary canvas, with honest capability states retained. |
| Exact facts, rules, formulas, versions, assumptions, review and source links remain inspectable | PRD §§9,19,20; PRODUCT_FLOW:41–51 | Every material value gets one reliable route to its evidence. A compact interface cannot discard the record it summarizes. |
| Conflicts and unsupported checks remain visible in results and reports; no material silent defaults; status never color-only | PRODUCT_FLOW:55–61; PRD §§12,23 | Collapsed detail is acceptable only behind an explicit visible state. Critical blockers cannot disappear into a generic “Details” drawer. |
| Qualified approval controls verified/published claims | PRD §§2,10,27; docs/GATES_AND_CHECKPOINTS.md G6 | Draft calculations stay draft. UX changes cannot create legal certainty. |
| Required disclaimer displayed prominently in application and reports | PRD §29; lib/disclaimer.ts | Preserve the full disclaimer and evaluate actual prominence. Reducing duplicate notices does not authorize removing this requirement. |
| Premium, calm, precise design; slim shell, optional rail, contextual inspector, one dominant action; no tiny text to fit more | docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md §§1,3,7,10,15–16 | Use the existing design principles. Do not solve density by shrinking type or turning text into unexplained icons. |

The premium design document was read for consistency after the requested parked-work review. Its suggested libraries, 3D views and future navigation are **not implementation authorization**. No new dependency is needed merely to assess or organize the current interface.

### Parked expansion work: narrow scope only

The July integration report is a historical proposal, not a current dispatch list. Its “can start now” statements are overridden by the hold. It proposes 19 tasks, nine contract families and GDS changes P1–P8; this assessment starts none of them. Its useful design principles are additive integration, preserve accepted work, geometry from deterministic contracts, and independent visual acceptance.

| Authority / source | What the inspected source says | Boundary for this handoff |
|---|---|---|
| .claude/rules/expansion-agent-dispatch-hold.md §2, lines 16–24 | Do not contract/start the 19 proposed tasks, author nine proposed contracts, apply P1–P8 or change the master plan on the pack's instruction. | Remains the boundary. This report recommends cleanup of existing surfaces; it is not a release of the pack. |
| Same §2.1, lines 37–46 — D-040 | Exactly the address-flow lot-outline connector/rendering increment is released. | Assess/reorganize the existing reference map. Do not infer permission for 3D massing or a new geometry authority. |
| Same §2.2, lines 26–35 — D-076 | Proposal-editor phased planning and phase-B flat outline/walls/floors/heights increments under normal gates; work beyond phase B waits for its checkpoint. | Proposed editor presentation improvements stay within the existing flat workflow. |
| D-082 references in ArchitectEntry, ProposalOutlineDraw, proposal-draft and discovery entries DB-045–050 | Source implements/releases specific drawing and maximum-first work, with honest limits and mount prerequisites. | The inspected hold file itself names D-040/D-076 but contains **no D-082 subsection**. Treat this as an authority-document reconciliation item for the orchestrator; no broader release is inferred. The owner named these three releases as the boundary of this assessment. |
| docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md §§2,5,6 | Rendering must consume canonical geometry; remote builds; source-linked primitives; independent acceptance. | No invented building visualization to make the current UI attractive. No local runtime or new 3D dependencies. |

No project-control source was read to resolve the D-082 documentary mismatch; the live orchestrator owns that reconciliation. G6 is a publication/reliance gate, not a blanket ban on improving an honestly draft interface.

## 12. One coherent visual direction

### Composition and priority

Use a single restrained shell with a stable property identity and fewer equally weighted cards. The first viewport should answer: **Which property? What kind of result is this? Which limits are available? What prevents reliance? What can I do next?**

The following are mockup specifications, not measured current dimensions or approved new requirements:

| Area | Default composition | Progressive layer |
|---|---|---|
| Header | Address; borough and BBL; explicit Draft state; Change property. Internal build remains identifiable at narrow widths. | Entered/matched/PLUTO identity differences and capture metadata. Material mismatch remains immediately visible. |
| Navigation | Existing useful destinations grouped by task: Overview, Property records/Zoning, Proposal, Evidence, Report. Documents when available. | Planned destinations in a clearly labelled group; do not silently remove unavailable capability truth or advertise nonexistent tools. Any renaming maps to existing routes. |
| Overview canvas | Approximately 55–60% real site map/context and 40–45% limit matrix on wide screens; an ordinary two-column layout, not a wall of cards. | Inspector opens only when a fact, limit, warning or source is selected. On mobile, map and results stack; evidence becomes a labelled full-width panel with close/focus return. |
| Result rows | Limit name; supplied value and unit or explicit state; short scope/status; Source / Why action. City-record FAR and evaluated FAR remain distinct. | Exact formula, inputs, assumptions, reason, citation, version and raw record. |
| Exception strip | Only active issues, separately named: identity mismatch, unresolved conflict, critical input, stale source, incomplete assessment. Critical names and blocked effect visible. | Full values/sources, exact reasons and remediation. No catch-all warning count that hides the nature of a blocker. |
| Existing building | Clearly named optional/collapsed group, preserving all records and source controls. | Lot/Building/Identity fact tabs and complete source appendix. |
| Action area | One primary task appropriate to actual enabled state. | Secondary actions grouped; no prose requiring the user to hunt for a button elsewhere. |

Example matrix labels below are **placeholders for existing backend values**, not calculations or proposed outputs:

| Metric | Main display | Scope attached to display | Detail action |
|---|---|---|---|
| Residential FAR — city record | {recorded value or Unknown} | PLUTO reference + version | Source |
| Residential FAR — rule evaluation | {supported result or Not calculated} | Draft; applicable condition where relevant | Why this FAR? |
| Zoning floor-area cap | {supported square feet or Not calculated} | FAR only; buildable envelope not assessed where true | Calculation |
| Height | {typed supported value or honest state} | Assessed / Not assessed / conflict as supplied | Why? |
| Setbacks and yards | {typed supported value or honest state} | Scope and missing prerequisite | Why? |
| Lot coverage and open space | {typed supported value or honest state} | Scope and missing prerequisite | Why? |

Never compute a missing number in this presentation layer. Never combine unrelated maxima into a buildable-volume illustration. The current overview and the separate preliminary-limit panel have different supported outputs; the layout must respect their actual contracts.

### State design: several independent questions, not one confidence score

| Question | Examples | Visual treatment |
|---|---|---|
| What is this information? | City record; proposed input; draft rule result; generated option; human confirmation record | Small explicit type label near value/title. |
| Was it assessed? | Not checked; checked; cannot check; not applicable | Short text state with icon; no blank green cell. |
| Can this specific result be used? | Withheld for identity; conflict; review required; draft only | Adjacent status and effect, not hidden behind hover. |
| How fresh or complete is its evidence? | Captured date; stale; source missing; partial coverage | Dated source/coverage cue with full detail. |
| Was it saved or professionally confirmed? | Session only; recalculation requested; self-attested; professionally confirmed | Separate persistence/authority label. Never infer one from another. |

Keep the backend enum and object type available. Do not silently remap a machine coverage status because a friendlier color fits the layout. A generic “conditional” gloss that describes an official fact must not imply a draft calculation is an official fact; contract-aware wording requires its own review.

### Rules for progressive disclosure

1. **Always visible at the relevant decision:** selected identity; mismatch/withheld effect; result type; draft/review scope; material conflict; critical missing input; incomplete assessment; current action failure; self-attested calculation refusal; session-only persistence where “save” is offered.
2. **Point-of-decision city warnings:** retain both exact city warning messages above Continue in the first implementation slice. The current tests explicitly require this. A later alternative must pass a named reviewer-approved visibility contract; an icon-only replacement is insufficient.
3. **One interaction away:** field-specific reasons, full scope wording, assumptions, applicability detail, source metadata, conversion accuracy method, recorded versus current relationships. Link the action to the exact result, rather than merely navigating to the top of Evidence.
4. **Technical tier:** route constants, HTTP/status pairs, correlation IDs, source digests, machine keys, full captured JSON. These stay inspectable without becoming the primary explanation.
5. **No tooltip-only legal content:** controls must work by keyboard and touch and have meaningful accessible names. Color, icons and hover titles complement visible labels.
6. **No automatic dismissal of material truth:** collapsing a panel does not clear its critical state. If a detail is closed, its summary still names the conflict/gap and affected result.
7. **Print carries its own complete meaning:** screen disclosures do not become missing report evidence. Critical scope, identity, conflicts and review status appear with the number; readable sources/assumptions/constraints remain in appendices. Raw audit JSON remains separately selectable.
8. **One state change, coherent announcement:** visually hidden announcements are not visual clutter. Consolidate competing live regions based on real assistive-technology testing while retaining accurate outcome and focus semantics.

### Measurable acceptance targets to propose at G0

- In a five-second uncoached view, the reviewer can identify the property, result class, main available value/state and the important open condition.
- Every main-screen number has an immediate Source/Why route; every collapsed detail is reachable by keyboard and touch; closing restores focus.
- No instruction says “below/above” where a direct, meaningful control can lead to the target.
- Do not impose a warning-count cap that hides real problems. Instead, count repeated boilerplate separately from distinct active conditions.
- Compare default viewport text blocks, repeated disclaimer occurrences, required navigation clicks and mobile overflow **on the same fixed fixture before and after**. Set the reduction target after capturing the baseline; this audit did not invent a current word count.
- Use spacing/grouping and readable type. Do not obtain density gains by hiding content at mobile breakpoints, shrinking legal text, truncating identities without a full accessible counterpart, or abbreviating units away.

## 13. Findings that need verification before or alongside layout work

These are source-grounded risks and existing backlog constraints, not claimed live reproductions.

| Priority | Finding / evidence | Why it matters | Gated verification |
|---|---|---|---|
| High | Ordinary proposal edits leave outcome state intact; saving uses current draft with existing report. ProposalEditor.tsx:73–79,105–137,195–403. | A polished result may describe a prior draft. | Run a check, edit geometry/levels/attestations, inspect current result, save/select a variation, and edit during an in-flight check. Bind displayed/saved results to the checked input revision; current vs stale must be visible. Verify before repair. |
| High | rectangleSampleDraft() initializes each editor: sample R5/wide/8,000 sq ft/example coordinates; only the model provenance note says example. ProposalEditor.tsx:73,183–185; proposal-draft.ts:421–449. | “Your input” can appear to be property-specific although defaults are an example. | Open two different BBLs and inspect the seed. Clearly choose/label examples or seed only actual provenance-supported inputs. Do not silently replace missing facts with inferred inputs. |
| High before capability mount | DB-050 retains authoritative-geometry, split-district disclosure, adoption feedback/replacement and other pre-mount requirements. | UI/tests with intercepted candidates do not establish live generated-option availability or a legal maximum. | Orchestrator reconciles actual accepted backend/mount state and each precondition. Show all split districts and truthful candidate availability; preserve edits on re-adoption through an explicit reviewed interaction. |
| Medium | RuleEvaluationResult.tsx:279–280 says draft competing rules are “in effect … to present” when end date is null; NoScenarioBlock uses safer recorded-date wording in its rows but retains “simultaneously in effect” in its introduction. | Null metadata is being framed as current legal effect. | Scope a semantic correction with rule/domain review; retain recorded dates/unknowns, not merely hide the claim. |
| Medium | AddressResolutionScreen.tsx:220–229 copies the full query into Street, whose hint says “Street name only.” | Recovery preserves text but can confuse the user about which structured fields are complete. | Exercise manual fallback; visibly preserve the original query and clearly label needed fields. Parsing would be separate behavior work. |
| Medium | DB-049 drawing issues: incomplete rows can be omitted from conversion; missing row markers; disabled Convert/focus and competing live announcements; real canvas readiness. | A short message alone cannot explain mismatched visible rows and submitted points. | Validate mixed complete/incomplete rows, map loading/fallback/selection and keyboard-only conversion. Keep explicit omitted-row state until every row is resolved. |
| Medium | Survey model “All material facts are resolved” fallback may apply to a document with no facts; DocumentOverlay permits null imageRef with annotation boxes. | Unprocessed/preview-unavailable can look complete or look like an actual original. | Reproduce uploaded/processing/zero-fact/null-preview states; display true lifecycle/preview availability locally. |
| Medium | Static “Every value … official-source fact” and shared coverage glosses span different record/result contexts. | Shortening without context can preserve or worsen a misleading interpretation. | Test fact, rule, scenario and human-confirmation fixtures; preserve backend statuses with accurate object-specific explanation. |
| Medium | Report print opens non-raw disclosures; mobile CSS hides environment/nav-footnote; map attribution uses very small type. | Screen-only cleanup may leave long or misleading print/mobile views. | Separate print, narrow-width and assistive-technology gates; verify actual disclaimer/environment visibility and readable source/accuracy text. |
| Low / consolidation | Duplicated ZoLa links, source-location narration, empty success cards, internal route/schema strings and legacy future-Evidence statement. | These add reading without improving a decision. | Map each removal to one surviving affordance/state and verify the relevant route variant. No disclosure deleted without a destination. |

## 14. Phased handoff for orchestrator-owned tasks

**These are assessment recommendations, not contracted tasks or release authorization.** Phase names are local report labels; the orchestrator assigns canonical task IDs, exclusive file scopes, dependencies, owners and required gates after reconciling its current checkout and holds. Do not launch the old 19-task pack from this plan.

Gate meanings follow docs/GATES_AND_CHECKPOINTS.md: G0 ready/scope; G1 official source/contracts; G2 producer evidence; G3 independent real-user/browser walkthrough; G4 integrated regression; G5 relevant security/privacy; G6 qualified publication/verified claims; G7 production release. Independent reviewers do not self-accept.

| Phase | Concrete reviewable output | Proposed scope / dependency | Exit gate and evidence |
|---|---|---|---|
| P0 — Reconcile and preserve meaning | Current-SHA comparison; reachable route/state map; one disclosure migration ledger using every inventory row/source span; latest DB dispositions; verified D-040/D-076/D-082 boundaries. | Orchestrator records this assessment; no redesign yet. Reconcile unpushed/current changes and documentary drift. | G0 + independent source/meaning review. Every L item has an always-visible cue, expanded destination, accessible equivalent, print destination and test owner. No orphaned disclosure. |
| P1 — Visual/state specification | Annotated desktop and mobile mockups for search, confirmation, overview, condo, proposal/drawing, evidence and report; shared status vocabulary; approved copy samples. | Presentation-only design over existing contracts. Resolve P0 questions before source/test wording changes. | G3 design walkthrough with normal/boundary/missing/failure states; qualified domain input for changed legal meaning. Keep §29 wording/prominence, exact returned disclosures and current city-warning visibility until explicitly resolved. |
| P2 — Address and confirmation slice | Single search/recovery area; identity comparison; stable action area; concise map states; single source disclosure. | Address/confirm/autocomplete and their route-specific styles/tests. Existing no-guess matching, raw warning placement and optional record-address behavior unchanged unless separately approved. | G0/G2/G3/G4. Keyboard and touch, no auto-pick, manual fallback, all error/retry categories, delayed PLUTO result without CTA shift, invalid/missing BBL, no WebGL, multiple/invalid parcel, absent source. |
| P3 — Overview, limits, records and condo slice | Compact limit matrix, true exception strip, optional existing building, paired identity/base-lot records, contextual evidence. | Architect display components/shared facts; retain current numeric-promotion, identity, fingerprint, condo and source-link guards. | G0/G2/G3/G4; G1 if field meanings/mappings change. Compare city/reference/evaluated/existing FAR, unsupported district, critical gaps, mismatched identity, missing citation, stale source, split zones, mixed-known condo zoning, self-attested/revoked/discrepant record. |
| P4 — Proposal and drawing slice | First reproduce/fix freshness and sample-attribution risks in bounded behavior tasks; then concise editor/tool states, numeric authority, result table and session-only comparison. | Existing D-076/D-082 slice only. Do not couple visual cleanup to new 3D capability or endpoint release. | G0/G2/G3/G4; G1 for any changed measurement/data contract. Checked draft → edit → recheck; in-flight edit; variation save/load; sample vs real context; finite/incomplete drawing points; correspondence/refusal/accuracy; stale result withheld; manual path remains usable. |
| P5 — Evidence and printable report | One result/fact inspector with summary → trace/source → raw tiers; compact brief plus readable provenance/assumption/constraint appendix; explicit optional raw appendix. | Evidence/report components and shared disclosures, using the same state/model as results. After P3 vocabulary; may design alongside P4. | G0/G2/G3/G4. Open/close/focus return, exact original/normalized/units/version/time, safe official URLs, source absence, all critical report states, print pagination and no clipping, restore screen expansion after print. |
| P6 — Survey review; optional internal dashboard polish | Urgency-first review list, scoped inspector, original/current/proposed comparison, decision blockers, clear capability states. Dashboard refinements stay a separate optional task. | Survey UI only, keeping backend authority and audit semantics. No dashboard loader/control-plane change is part of visual polish. | G0/G2/G3/G4; G5 if actions/auth/upload/data exposure change. Conflicts cannot dismiss; preparer vs professional; stale edit preserves draft; affirmation vs confirmation; recalculation requested vs completed; no-facts/unavailable-preview states. |
| P7 — Integrated validation and release recommendation | Before/after evidence on the frozen candidate; semantic disclosure coverage reconciliation; desktop/mobile/print and uncoached walkthrough; deployment/rollback packet if later authorized. | All accepted slices; remote build/test environment only. | G4 integrated build/lint/types/tests and affected golden regressions, independent G3. G5/G7 as release scope requires. G6 only for publication/reliance transitions, never substituted by UI reviewers. Orchestrator records the result. |

### Required migration row for every disclosure

| Field | Required content |
|---|---|
| Stable reference | Report inventory ID + frozen source file/span; split a grouped family into state-specific rows when contracting. |
| Trigger and protected meaning | Exactly when it appears; what mistaken belief it prevents. |
| Authority | PRD/product rule, reviewer finding/DB item, returned contract, exact-copy test or implementation-only prose. Distinguish them. |
| Proposed primary state | Exact visible label/value/scope and location before the user acts. |
| Progressive destination | Named control and complete retained wording/data; no unspecified “move to tooltip.” |
| Accessibility | Role/name, keyboard/touch path, announcement and focus behavior. |
| Print/export | Where the same scope, source and critical gap survives when detached from the app. |
| Disposition | Keep / convert / consolidate duplicate / retire obsolete instruction; replacement reference required for any removed occurrence. |
| Proof | Before/after state fixture, affected tests, independent reviewer acceptance; exact source words retained when contract requires. |

A passing text assertion alone is insufficient proof of visibility, clarity or screen-reader behavior. Conversely, a prettier screenshot is insufficient proof that source data, withholding and professional-review meaning survived. Require both.

### Specific regression matrix

Use existing fixtures; do not label them real live findings. Include:

- Architect gate on and legacy gate off; present false/unknown opt-in tokens remain fail-safe.
- Ordinary supported property; unsupported rule family; incomplete/malformed evaluation; wrong property identity; mismatch between rule and scenario fingerprints.
- Recorded residential FAR, evaluated FAR, wide-street conditional versus conservative FAR, existing built FAR, and exact zero versus absent value.
- Missing critical and noncritical inputs; stale dataset; competing source values; split districts with preserved share ranges.
- Condo entered-unit/billing/base identity; equal-ID collapse; unknown billing; single/multiple base lots; recorded/unknown/slash zoning; channel disagreement.
- Never confirmed, active self-attested, revoked/superseded, and parcel-discrepancy site records. None unlocks an allowance by styling.
- Address zero results, multiple choices, city warnings, rejection, timeout, source outage, network failure, unknown response and manual recovery.
- Map ready, preparing, no geometry, unusable geometry, multiple parcels, condo unit, no WebGL, render failure and basemap-only failure.
- Proposal initial example, unrun, running, failed/unchecked/passed subsets, edit after result, edit during request, adoption/re-adoption, discarded walls, variation freshness and session-only state.
- Survey original/current/correction, conflict/unresolved/passed checks, roles, stale draft, no facts, extraction unavailable, preview unavailable, rejected and professionally confirmed states.
- Desktop, 768-pixel tablet, 360-pixel phone, keyboard-only and reduced-motion usage; print without/with raw appendix. These are proposed acceptance widths, not a claim of measurements taken here.

## 15. Conditional deployed-Chrome walkthrough

The owner offered to open the deployed site in Chrome. That step has **not occurred in this assessment**. No deployed screenshot, browser automation result, current feature flag, endpoint mount, runtime performance measurement or current deployment SHA is claimed.

When the owner opens a browser that this session can actually access, use this bounded walkthrough. If no browser connection is exposed, identify that limitation; do not run a local Node/browser harness to bypass the thin-client rule.

| Step | What to inspect with the owner | Evidence / decision |
|---|---|---|
| 1 | Establish actual URL, deployed version where available and route/flag variant. | Distinguish deployed product from the audited GitHub source and fixture-only paths. |
| 2 | Start at entry; ask owner to search a property without coaching. | Can the owner locate the action in five seconds? Record actual source failure/recovery if it occurs. |
| 3 | Pick a suggestion, compare typed/matched/PLUTO identity, inspect warnings and Continue. | Correct BBL role, no auto-selection, no disappearing warnings, no late CTA movement. |
| 4 | Open overview; ask what the main number means and which development limits are unknown. | FAR/cap/building/usable-area distinctions are understood without a paragraph recital. |
| 5 | Open one Source/Why control, then close by keyboard and touch. | Exact record and scope reachable; focus returns; current-source versus captured-source distinction understood. |
| 6 | Review an existing condo fixture/property where applicable. | Entered/billing/base relationship and calculation refusal clear; no synthetic relationship asserted. |
| 7 | Open proposal if enabled. Read the initial input provenance and check-state labels; test harmless local draft editing only. | Sample and stale-result concerns verified without saving or changing shared records. Server actions require scope-aware assessment of what they do. |
| 8 | Try drawing/keyboard fallback if enabled; observe map readiness and incomplete points. | Gesture instructions match actual map; conversion accuracy is not read as survey accuracy. |
| 9 | Review print preview and a phone-width presentation through a supported remote preview. | Critical limitations and provenance survive; no clipped tables or hidden environment truth. |
| 10 | Owner explains the result and next action unaided. | Record misunderstandings as design findings. This is not professional zoning approval or formal acceptance. |

For mutation-capable survey/site-record interfaces, inspect existing states or controlled fixtures; do not confirm, reject, revoke or overwrite shared records during this assessment.

## 16. Coverage and handoff notes

The scoped source tree contains **97 non-test TSX files** (routes, components and one survey context provider). The screen reviews cover every user-facing route/component in that set, including flag-off compositions, shared primitives, failure states, the internal dashboard and survey review. The context provider has no authored visible UI; its thrown developer error is handled as runtime failure, not an extra product screen. Four CSS files form the presentation tree; architect/global styling was inspected where relevant, but there was no comprehensive rendered CSS or visual verification.

The inventory enumerates text by rendering branch and data family, not by a single sample property. All source-driven values, source excerpts, reasons, warnings, provenance leaves, task titles and histories remain parameterized. Protected project-control data was deliberately not read to enumerate live dashboard values. This is a transparent scope limit, not authority to drop dynamic content.

Component/source names abbreviated without an extension in an inventory table refer to the corresponding .tsx file in that table's declared directory. Source anchors are specific to the frozen SHA and must be refreshed if the orchestrator rebases. Tables preserve current wording or identify a block by its exact opening plus its complete rendered data family; they are a migration inventory, not a substitute for the source of long returned legal text.

No automated suite was run. Test assertions were inspected to identify current contracts; “test pins” throughout means code assertions exist, **not that those tests passed in this session**. Reviewer memories are historical evidence, not current deployment truth. No current legal interpretation was approved.

### Exact shared field-label register

The following 108 mappings come from apps/web/src/lib/format.ts at the audited commit. They complete the dynamic fact-label family used across property, confirmation, source and report views. Every row is **L+V**: preserve the source field and reviewed meaning; compact placement is allowed; do not invent an expanded legal meaning. These are current application labels, not this audit's certification of their legal correctness. In particular, “Maximum residential FAR” in a city record must remain clearly labelled as a PLUTO reference, distinct from evaluated allowances. The unknown-field fallback remains “{field} (source column — label pending review)”.

| Source field | Current visible label | Source line |
|---|---|---|
| `bbl` | BBL | 73 |
| `borocode` | Borough code | 74 |
| `borough` | Borough (source code) | 75 |
| `block` | Tax block | 76 |
| `lot` | Tax lot | 77 |
| `address` | Address | 78 |
| `zipcode` | ZIP code | 79 |
| `lotarea` | Lot area | 82 |
| `lotfront` | Lot frontage | 83 |
| `lotdepth` | Lot depth | 84 |
| `lottype` | Lot type code | 85 |
| `irrlotcode` | Irregular lot | 86 |
| `easements` | Easements | 87 |
| `splitzone` | Split zoning lot | 88 |
| `zonedist1` | Zoning district 1 (primary) | 93 |
| `zonedist2` | Zoning district 2 | 94 |
| `zonedist3` | Zoning district 3 | 95 |
| `zonedist4` | Zoning district 4 | 96 |
| `overlay1` | Commercial overlay 1 | 97 |
| `overlay2` | Commercial overlay 2 | 98 |
| `spdist1` | Special purpose district 1 | 99 |
| `spdist2` | Special purpose district 2 | 100 |
| `spdist3` | Special purpose district 3 | 101 |
| `ltdheight` | Limited height district | 102 |
| `zonemap` | Zoning map | 103 |
| `zmcode` | Zoning map code | 107 |
| `builtfar` | Built FAR | 114 |
| `residfar` | Maximum residential FAR | 115 |
| `commfar` | Maximum commercial FAR | 116 |
| `facilfar` | Maximum community facility FAR | 117 |
| `affresfar` | Maximum affordable residential FAR | 118 |
| `mnffar` | Maximum manufacturing FAR | 119 |
| `mih_opt1` | Mandatory Inclusionary Housing option 1 | 125 |
| `mih_opt2` | Mandatory Inclusionary Housing option 2 | 126 |
| `mih_opt3` | Mandatory Inclusionary Housing option 3 | 127 |
| `mih_opt4` | Mandatory Inclusionary Housing option 4 | 128 |
| `edesignum` | E-designation number | 129 |
| `transitzone` | Transit zone | 130 |
| `landmark` | Landmark | 133 |
| `histdist` | Historic district | 134 |
| `firm07_flag` | 2007 FIRM flood flag | 135 |
| `pfirm15_flag` | 2015 preliminary FIRM flood flag | 136 |
| `landuse` | Land use code | 139 |
| `bldgclass` | Building class | 140 |
| `bldgarea` | Building floor area | 141 |
| `comarea` | Commercial floor area | 142 |
| `resarea` | Residential floor area | 143 |
| `officearea` | Office floor area | 144 |
| `retailarea` | Retail floor area | 145 |
| `garagearea` | Garage floor area | 146 |
| `strgearea` | Storage floor area | 147 |
| `factryarea` | Factory floor area | 148 |
| `otherarea` | Other floor area | 149 |
| `areasource` | Area source code | 150 |
| `numbldgs` | Number of buildings | 151 |
| `numfloors` | Number of floors | 152 |
| `unitsres` | Residential units | 153 |
| `unitstotal` | Total units | 154 |
| `bldgfront` | Building frontage | 155 |
| `bldgdepth` | Building depth | 156 |
| `ext` | Extension code | 157 |
| `proxcode` | Proximity code | 158 |
| `bsmtcode` | Basement code | 159 |
| `yearbuilt` | Year built | 160 |
| `yearalter1` | Year altered (1) | 161 |
| `yearalter2` | Year altered (2) | 162 |
| `ownertype` | Owner type code | 165 |
| `ownername` | Owner name | 166 |
| `assessland` | Assessed land value | 167 |
| `assesstot` | Assessed total value | 168 |
| `exempttot` | Exempt total value | 169 |
| `appbbl` | Apportionment BBL (originating tax lot) | 173 |
| `appdate` | Apportionment date | 174 |
| `condono` | Condominium number | 175 |
| `cd` | Community district | 179 |
| `schooldist` | School district | 180 |
| `council` | City Council district | 181 |
| `firecomp` | Fire company | 182 |
| `policeprct` | Police precinct | 183 |
| `healtharea` | Health area | 184 |
| `healthcenterdistrict` | Health center district | 185 |
| `sanitboro` | Sanitation district borough | 186 |
| `sanitdistrict` | Sanitation district | 187 |
| `sanitsub` | Sanitation subsection | 188 |
| `ct2010` | 2010 census tract | 191 |
| `cb2010` | 2010 census block | 192 |
| `tract2010` | 2010 census tract (alternate format) | 193 |
| `bct2020` | 2020 census tract (borough-prefixed) | 194 |
| `bctcb2020` | 2020 census block (borough-prefixed) | 195 |
| `xcoord` | X coordinate (NY state plane) | 199 |
| `ycoord` | Y coordinate (NY state plane) | 200 |
| `latitude` | Latitude | 201 |
| `longitude` | Longitude | 202 |
| `geom` | Geometry | 203 |
| `sanborn` | Sanborn map number | 206 |
| `taxmap` | Tax map number | 207 |
| `plutomapid` | PLUTO map id | 208 |
| `version` | PLUTO release version | 209 |
| `dcpedited` | DCP-edited flag | 210 |
| `notes` | Notes | 211 |
| `basempdate` | Input data vintage (base map) | 216 |
| `dcasdate` | Input data vintage (DCAS) | 217 |
| `edesigdate` | Input data vintage (E-designations) | 218 |
| `landmkdate` | Input data vintage (landmarks) | 219 |
| `masdate` | Input data vintage (MAS) | 220 |
| `polidate` | Input data vintage (political districts) | 221 |
| `rpaddate` | Input data vintage (RPAD) | 222 |
| `zoningdate` | Input data vintage (zoning features) | 223 |


### Complete non-test TSX coverage register

Paths below are relative to apps/web/src/. They identify inspected source coverage, not executed routes or passing tests.

| Source file | Inventory location |
|---|---|
| app/dashboard/error.tsx | §9 — internal dashboard |
| app/dashboard/page.tsx | §9 — internal dashboard |
| app/layout.tsx | §4 — root shell and route adapters |
| app/page.tsx | §4 — root shell and route adapters |
| app/property/compare/page.tsx | §4 — root shell and route adapters |
| app/property/confirm/page.tsx | §4 — root shell and route adapters |
| app/property/error.tsx | §4 — root shell and route adapters |
| app/property/layout.tsx | §4 — root shell and route adapters |
| app/property/page.tsx | §4 — root shell and route adapters |
| app/survey/review/[documentId]/page.tsx | §9 — survey review |
| app/survey/review/page.tsx | §9 — survey review |
| components/address/AddressConfirmCard.tsx | §6 — address, confirmation, map |
| components/address/AddressForm.tsx | §6 — address, confirmation, map |
| components/address/AddressOutcomeCards.tsx | §6 — address, confirmation, map |
| components/address/AddressResolutionScreen.tsx | §6 — address, confirmation, map |
| components/address/LotOutlineMap.tsx | §6 — address, confirmation, map |
| components/address/SuggestionChooser.tsx | §6 — address, confirmation, map |
| components/architect/AdditionalZoningFlags.tsx | §7 — results, facts, records, evidence, report |
| components/architect/AddressAutocomplete.tsx | §6 — address, confirmation, map |
| components/architect/AnalysisIdentityNotice.tsx | §7 — results, facts, records, evidence, report |
| components/architect/ArchitectEntry.tsx | §4 — route composition; §§5–7 child views |
| components/architect/ArchitectShell.tsx | §7 — results, facts, records, evidence, report |
| components/architect/AssessmentCoverage.tsx | §7 — results, facts, records, evidence, report |
| components/architect/CalculationEvidence.tsx | §7 — results, facts, records, evidence, report |
| components/architect/DevelopmentLimits.tsx | §7 — results, facts, records, evidence, report |
| components/architect/EvidenceInspector.tsx | §7 — results, facts, records, evidence, report |
| components/architect/EvidenceRecord.tsx | §7 — results, facts, records, evidence, report |
| components/architect/EvidenceWorkspace.tsx | §7 — results, facts, records, evidence, report |
| components/architect/MaxEnvelopePanel.tsx | §5 — proposal, drawing, zoning context |
| components/architect/ProfileViews.tsx | §7 — results, facts, records, evidence, report |
| components/architect/PropertyFacts.tsx | §7 — results, facts, records, evidence, report |
| components/architect/PropertyOverview.tsx | §7 — results, facts, records, evidence, report |
| components/architect/ProposalCheckReport.tsx | §5 — proposal, drawing, zoning context |
| components/architect/ProposalEditor.tsx | §5 — proposal, drawing, zoning context |
| components/architect/ProposalOutlineDraw.tsx | §5 — proposal, drawing, zoning context |
| components/architect/ProposalOutlineMap.tsx | §5 — proposal, drawing, zoning context |
| components/architect/ProposalVariations.tsx | §5 — proposal, drawing, zoning context |
| components/architect/ReportSources.tsx | §7 — results, facts, records, evidence, report |
| components/architect/ReportView.tsx | §7 — results, facts, records, evidence, report |
| components/architect/ScenarioWorkspace.tsx | §5 — proposal, drawing, zoning context |
| components/architect/SurveyWorkspace.tsx | §5 — proposal, drawing, zoning context |
| components/architect/ZoningContextControl.tsx | §5 — proposal, drawing, zoning context |
| components/architect/ZoningContextPanel.tsx | §5 — proposal, drawing, zoning context |
| components/compare/CompareScreen.tsx | §8 — legacy property/compare and shared states |
| components/compare/CoverageMatrixSection.tsx | §8 — legacy property/compare and shared states |
| components/compare/NoScenarioBlock.tsx | §8 — legacy property/compare and shared states |
| components/compare/ScenarioAssumptions.tsx | §8 — legacy property/compare and shared states |
| components/compare/ScenarioCard.tsx | §8 — legacy property/compare and shared states |
| components/compare/ScenarioConstraints.tsx | §8 — legacy property/compare and shared states |
| components/compare/ScenarioFailureStates.tsx | §8 — legacy property/compare and shared states |
| components/compare/ScenarioProvenance.tsx | §8 — legacy property/compare and shared states |
| components/compare/ScenarioReasons.tsx | §8 — legacy property/compare and shared states |
| components/compare/ScenarioResult.tsx | §8 — legacy property/compare and shared states |
| components/compare/UnusedFloorAreaSection.tsx | §8 — legacy property/compare and shared states |
| components/confirm/ConfirmScreen.tsx | §6 — address, confirmation, map |
| components/dashboard/ActivityFeed.tsx | §9 — internal dashboard |
| components/dashboard/CurrentWork.tsx | §9 — internal dashboard |
| components/dashboard/DashboardApp.tsx | §9 — internal dashboard |
| components/dashboard/InternalBanner.tsx | §9 — internal dashboard |
| components/dashboard/MissionControl.tsx | §9 — internal dashboard |
| components/dashboard/ProductMap.tsx | §9 — internal dashboard |
| components/dashboard/Roadmap.tsx | §9 — internal dashboard |
| components/dashboard/SystemDrawer.tsx | §9 — internal dashboard |
| components/dashboard/ui.tsx | §9 — internal dashboard |
| components/property/ConflictsSection.tsx | §8 — legacy property/compare and shared states |
| components/property/CoverageBadge.tsx | §8 — legacy property/compare and shared states |
| components/property/CoverageLegend.tsx | §8 — legacy property/compare and shared states |
| components/property/FactsTable.tsx | §8 — legacy property/compare and shared states |
| components/property/FailureState.tsx | §8 — legacy property/compare and shared states |
| components/property/InternalBanner.tsx | §8 — legacy property/compare and shared states |
| components/property/LoadingStages.tsx | §8 — legacy property/compare and shared states |
| components/property/MissingInputsSection.tsx | §8 — legacy property/compare and shared states |
| components/property/OutcomeAnnouncer.tsx | §8 — legacy property/compare and shared states |
| components/property/ProfessionalReviewPanel.tsx | §8 — legacy property/compare and shared states |
| components/property/PropertyLookup.tsx | §4 — legacy lookup; §8 child result states |
| components/property/ProvenanceDisclosure.tsx | §8 — legacy property/compare and shared states |
| components/property/UnsupportedSection.tsx | §8 — legacy property/compare and shared states |
| components/property/ZoningSection.tsx | §8 — legacy property/compare and shared states |
| components/rule-evaluation/RuleEvaluationFailure.tsx | §8 — legacy property/compare and shared states |
| components/rule-evaluation/RuleEvaluationPanel.tsx | §8 — legacy property/compare and shared states |
| components/rule-evaluation/RuleEvaluationResult.tsx | §8 — legacy property/compare and shared states |
| components/survey-review/ChecksPanel.tsx | §9 — survey review |
| components/survey-review/ConfirmDocumentPanel.tsx | §9 — survey review |
| components/survey-review/CorrectionForm.tsx | §9 — survey review |
| components/survey-review/CorrectionHistory.tsx | §9 — survey review |
| components/survey-review/DocumentOverlay.tsx | §9 — survey review |
| components/survey-review/DownstreamImpact.tsx | §9 — survey review |
| components/survey-review/FactList.tsx | §9 — survey review |
| components/survey-review/FactRow.tsx | §9 — survey review |
| components/survey-review/FocusedItem.tsx | §9 — survey review |
| components/survey-review/ReadFailureState.tsx | §9 — survey review |
| components/survey-review/ReasonForm.tsx | §9 — survey review |
| components/survey-review/ReviewInbox.tsx | §9 — survey review |
| components/survey-review/StateHistory.tsx | §9 — survey review |
| components/survey-review/StatusBadge.tsx | §9 — survey review |
| components/survey-review/SurveyReviewScreen.tsx | §9 — survey review |
| lib/surveyReview/context.tsx | §16 — provider only; no authored visible UI |

### Handoff

This assessment is ready for the orchestrator to record, reconcile against the shared checkout, and use to scope gated work. The candidate branch still pointed to the audited SHA when checked at completion. The report is a single uncommitted handoff artifact; it has not been placed in the inaccessible Windows checkout or committed through GitHub. No source change, project-control operation, test execution, deployment, or parked-work release is implied. The deployed-Chrome walkthrough remains outstanding.
