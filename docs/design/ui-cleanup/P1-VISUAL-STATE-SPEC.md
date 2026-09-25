# D-086 P1 — Visual / state specification (UI cleanup)

Task **M5-T114** (D-086 phase P1, docs only, presentation-only). Companion static mockup:
`docs/design/ui-cleanup/P1-mockups.html`. This spec is a **design proposal over existing contracts** — it
adds no backend field, computes no number in the presentation layer, and never remaps a backend status.
It is assessment output, **not** implementation authorization (D-086-R001); the orchestrator contracts the
per-surface build slices (P2–P7) against one agreed picture.

## 0. Provenance, inputs and pins

| Input | Role here | Pin / note |
|---|---|---|
| `docs/UI_DEEP_DIVE_ASSESSMENT.md` | Spec source (input, never authorization). §14 P1 row = exit gate; §4/§10 no-loss + copy walls; §11 authority boundary; §12 visual direction. | Frozen `dc5a763e`, LF sha256 `c6d1b25779c2dd2…8504b84` per P0. Read, not edited. |
| `docs/design/ui-cleanup/P0-RECONCILIATION.md` | Route/state map, DB dispositions, D-040/D-076/D-082/D-087 boundary, print+a11y legend (§7). | Producer pin `b56f3d5b`; rework A `a57bb8de`. |
| `disclosure-ledger-a.json` / `disclosure-ledger-b.json` | The no-loss contract: every disclosure's progressive destination, accessibility path, print destination. **Authoritative per-row detail lives there; this spec cites row ids and places them.** | 381 rows (PART A 155, PART B 226). |
| `apps/web/src/**` (read-only, at head) | Grounds the status vocabulary in real backend statuses/returned fields. | See §2 citations. |
| `docs/design/address-entry-confirm-design-spec.md`, `docs/design/ui-prototype.html`, `docs/design/ui-inspiration/`, `docs/design/d087-export-and-3d-viewer-plan.md` | Reference only. | — |

**Scope of surfaces (binding).** Only surfaces that exist or were released may appear: the architect flag-on
workspace, the D-040 address/lot-outline confirm surface, the D-076 flat proposal editor, the D-082 drawing +
max-envelope panel, and the D-087 3D/CAD/PDF families **only as honest "planned/unavailable" states** (no
fabricated 3D viewer or export record). **The max-envelope route stays UNMOUNTED — the panel is shown only as
it exists today** (§8.5). The legacy flag-off `/property`, `/property/confirm`, `/property/compare` screens
are inventoried for no-loss but are not the redesign's primary surface (they retire on route consolidation).

**Overnight decision rule (D-089).** The owner is asleep. Every unresolved question is decided here within the
rules and recorded; anything that could change legal meaning is placed in the **meaning-change register (§10),
NOT adopted**, as a question for qualified review.

---

## 1. Design principles (from assessment §11–§12)

1. **One dominant decision per view.** The first viewport answers, in order: *Which property? What kind of
   result is this? Which limits are available? What prevents reliance? What can I do next?* Every view names
   exactly one primary action appropriate to the actual enabled state.
2. **Calm, premium, precise.** A single restrained shell, a stable property identity, fewer equally-weighted
   cards, generous spacing, readable type. Density is bought with grouping and whitespace — **never** by
   shrinking legal text, hiding content at mobile breakpoints, truncating identities without a full accessible
   counterpart, or turning text into unexplained icons (§12 acceptance targets).
3. **Legal status is never simplified away.** Complex legal state (conflict, withholding, review-required,
   split zoning, self-attested record, stale source) is always visible at the decision it affects. Collapsing a
   panel never clears its critical state; a closed summary still names the conflict/gap and the affected result.
4. **Provenance and uncertainty are first-class.** Every material value has one reliable route to its evidence.
   Ranges stay ranges; unknown stays unknown; a genuine zero stays distinct from absent.
5. **Status is never colour-only.** Every state pairs a hue with a **text label and a non-colour symbol**.
6. **Print carries its own complete meaning.** Screen disclosures do not become missing report evidence.
7. **AI drafts and explains; deterministic code calculates; qualified humans approve.** No presentation change
   creates legal certainty. Draft stays draft (PRD §§2,10,27; G6 unchanged).

These are mockup specifications, **not measured current dimensions or approved new requirements** (§12).

---

## 2. ONE shared status vocabulary (AS-1)

Every state below maps **FROM a named backend status or returned field**, shown **verbatim, never remapped, no
number computed in the UI**, and carries **non-colour accessible text**. The vocabulary is organised by the
five independent questions of assessment §12 ("several independent questions, not one confidence score") plus
the transport/channel families. The canonical enum value is always displayed; a plain-language gloss only
*explains* it (`apps/web/src/lib/coverage.ts:1-9`). The UI never invents or upgrades a status.

### 2.1 Question A — What kind of information is this? (claim class)

| State label | Meaning | Comes FROM (backend status / returned field) | Visual treatment | Accessible text (non-colour) |
|---|---|---|---|---|
| City record | An official recorded value (e.g. PLUTO residential FAR, existing built FAR). | `residentialReference().status === "City reference"`; `SourceFact` provenance (`development-limits.ts:8-27`). Value shown verbatim from `normalized_value`. | Neutral slate chip, label "City record". | Text "City record" + source name in the chip's accessible name. |
| Draft rule result | A deterministic draft evaluation, never a verified/final permission. | `rule_evaluation.coverage_source === "rule_evaluator"`; `coverage_status` (draft set **excludes** `verified`, `rule-evaluation-contract.ts:69-75`). | Indigo "Draft" eyebrow beside the value. | Text "Draft rule result". |
| Generated building option | A building-shaped candidate from the max-envelope engine. **Never** "permitted"/"approved"/"maximum allowed building". | `MaxEnvelopeOutcome.kind === "envelope"` → `EnvelopeCandidate` (`max-envelope-api.ts:151-155`). Copy-wall `max-envelope-panel.test.tsx:274-290`. | Line-drawing tint; caption "Generated building option". | Text "Generated building option". |
| Proposed input | Author-entered geometry/inputs, not a city record. | `ProposalEditor` draft / `proposal-draft.ts`; drawing `outline-bridge` typed states. | Amber "Proposed" badge. | Text "Proposed — not a city record". |
| Human confirmation record | A recorded human site-definition decision (not a system selection, not a calculation). | `condo-records.ts` `SiteDefinitionView` / `activeConfirmation`. | Slate "Human record" tag with actor/time. | Text "Human record" + confirmer + timestamp. |

### 2.2 Question B — Coverage status of a result (the six-value enum, verbatim)

Source of truth: `apps/web/src/lib/coverage.ts:22-47` (enum verbatim from `coverage_status.schema.json`, PRD
§12). Symbol is a non-colour glyph; gloss is accessibility content.

| Enum (verbatim) | Symbol | Gloss (accessible text) | Visual treatment |
|---|---|---|---|
| `verified` | ✓ | "Confirmed under a published, professionally reviewed rule." | Green chip — **only reachable via G6; a draft result never shows this** (`rule-evaluation-contract.ts:26,67`). |
| `conditional` | ◐ | "Official source fact, not yet professionally reviewed." | Indigo chip. |
| `professional_review_required` | ! | "A qualified professional must review this before reliance." | Amber chip. |
| `data_conflict` | ≠ | "Official sources disagree; both values are shown, nothing was resolved." | Rose chip. |
| `unsupported` | ∅ | "The platform detected a data problem and cannot support this value." | Slate chip. |
| `not_applicable` | — | "Does not apply to this property." | Muted chip. |

### 2.3 Question C — Was it assessed, and can this result be used?

Presentation-selection labels, each derived from a backend field by an **existing** selector — no arithmetic
(`development-limits.ts`).

| State label | Comes FROM | Visual / accessible text |
|---|---|---|
| Draft assessment · envelope incomplete | `calculationStatus()` default branch (`development-limits.ts:180`). | Neutral status line beside the cap. |
| Property identity mismatch | `evaluation.evaluated_input.bbl !== bbl` (`:168`). | Rose "Results withheld" state; `role=alert` retained (A15, LS-C04). |
| Zoning boundary check unavailable / incomplete · Lot boundary requires review · Conflicting boundary results · Conflicting rule results · Condo base lot needs site confirmation | `FAILURE_LABELS[evaluation.fail_safe_reason]` — the 7 `FAIL_SAFE_REASONS` (`development-limits.ts:155-165`, `rule-evaluation-contract.ts:88-100`). Each distinct label, **never a generic "Warning"** (A10). | Amber status line + "inspect evidence" link. |
| Rule details incomplete · inspect captured evidence | `!evaluationIsInspectable()` (`:171`). | "Blocked result" state; record preserved below (A05). |
| Analysis records differ / Scenario integrity check failed / Rule source support incomplete · inspect evidence | `analysisRecordsDiffer()`, `integrity_check.agreed === false`, citation-support mismatch (`:173-179`). | Amber status + evidence link. |
| Not calculated / Not supported / Review required / Conflicting results (Height, Setbacks, Lot coverage) | `bulkRow()` from `scenario.constraints[].state` (`unsupported`/`professional_review_required`/`conflicting`) or `coverage_status === "data_conflict"` (`:198-209`). **No magnitude invented** (A11). | Text state per row; never a blank green cell. |
| City reference / Unknown / Conflicting records / Source value unavailable | `residentialReference().status` (`:14-27`). | Text state beside the FAR cell (A09). |
| within_100ft_of_wide_street / not_within_100ft_of_wide_street / professional_review_required (+ far_row wide_street_row / standard_row / none) | `rule_evaluation.wide_street.determination_state` / `.far_row` (`rule-evaluation-contract.ts:123-134`). Conservative and conditional stay distinct; standard FAR never wears the conditional-FAR label (A07/A08, copy-wall `report-view.test.tsx:189-250`). | Distinct row label + withholding text next to value. |
| Base-district candidates: share_min / share_point / share_max | `spatial_uncertainty.base_district_candidates[]` (`rule-evaluation-contract.ts:280-299`). A range **never** collapses to one percentage (LS-C12). | Interval track whose accessible name is the exact min/point/max text. |

### 2.4 Question D — How complete / fresh is the evidence?

| State label | Comes FROM | Visual / accessible text |
|---|---|---|
| All expected official inputs were retrieved / Some non-critical official inputs are missing / Critical official inputs are missing | `DataCompleteness` enum headlines (`coverage.ts:60-77`, PRD §12). **Never** read as "Feasible" (F03). | Headline text + per-gap count; critical gaps never collapse behind only a number (LS-P09). |
| Stale source (dated) | `property_profile.reproducibility.staleness` (E03, LS-P12). | Dated cue "Retrieved {date} — review before reliance". |
| Source unavailable / Provenance not linkable | `ProvenanceDisclosure` gap branch (LS-P14). | Text "Source unavailable" in the Source column. |
| Drift signal / Unsupported | `reproducibility.drift_signals`, fact `coverage_status === "unsupported"` (LS-P12). | Affected-row state + count. |

### 2.5 Question E — Was it saved or professionally confirmed? (never inferred one from another)

| State label | Comes FROM | Visual / accessible text |
|---|---|---|
| Not saved / Session only | `ReportView` brief "not saved automatically"; editor "this browser session only" (`ProposalEditor.tsx:136`, R01, PE-08). | Text "Not saved" (not an icon). |
| Recalculation requested | `user_confirmations` action state. | Text state. |
| Self-attested — not usable for calculations | `site_definition` attestation `unauthenticated_self_attested` → `refusedForCalculation` forced TRUE (`condo-records.ts:437-448`, C05). A confirmation alone never unlocks a withheld figure. | Rose "Self-attested — not usable for calculations", always visible beside the record. |
| Professionally confirmed | Reserved for G6 verified-claim path; **not produced by this UI**. | Green — unreachable in draft. |

### 2.6 Transport / channel state families (the LS-F "distinct failure state" set)

Each is a **typed** returned outcome — never merged into one generic warning (LS-F01–LS-F17). Presented as a
distinct visual + accessible state with its own recovery action.

| Family | Backend outcome union | Distinct states surfaced |
|---|---|---|
| Address search | `AddressSearchOutcome` / `AddressSearchErrorReason` (`address-search.ts:30-44`) | suggestions · error(`source_unavailable`·`rejected`·`malformed`·`rate_limited`·`timeout`·`unavailable`) · aborted · geo `resolved`/`no_match`. |
| Condo records | `CondoChannelState` (`condo-records.ts:724-732`) | idle · loading · non_condo · single (allow) · multi_lot · unresolved · resolver_error · unavailable. **`channelWithholdsAllowances` = multi_lot \| unresolved \| resolver_error only** (`:788-794`); a transport outage never withholds on its own. |
| Drawing → coordinate bridge | `OutlineBridgeOutcome` (`outline-bridge-api.ts:110-199`) | bridged · feature_unavailable · out_of_neighborhood · correspondence_unavailable · residual_too_high · source_unavailable · payload_too_large · invalid_request · internal_error · validation_failure · network_error · client_timeout · aborted · unexpected_response. |
| Proposal check | `ProposalCheckOutcome` + per-check `outcome` (`proposal-checks-api.ts:86,113-163`) | report(per-check `pass`/`fail`/`could_not_check`) · feature_unavailable · payload_too_large · validation_error · internal_error · validation_failure · network_error · client_timeout · aborted · unexpected_response. |
| Max-envelope (generated option) | `MaxEnvelopeOutcome` + `DimensionRowKind` (`max-envelope-api.ts:151-200,589,608`) | envelope · feature_unavailable · payload_too_large · invalid_request · internal_error · validation_failure · network_error · client_timeout · aborted · unexpected_response; per-dimension `value`/`gap`/`contract_violation`. |
| Property/scenario failure | `ScenarioFailureStates` / `RuleEvaluationFailure` (SH-09, LS-F) | loading · typed failure (focus target, retry to h1) · identity notice (`role=alert`) · incomplete evaluation (`role=status`). |
| Route render error | `app/property/error.tsx` (SH-14) | one failure heading, "nothing was determined, nothing was saved", retry/back, digest in Support details. |

**Live-region rule (LS-P16, applies to every family).** Each screen keeps exactly ONE persistent
`OutcomeAnnouncer` (`role=status`, `aria-live=polite`, `aria-atomic`, `OutcomeAnnouncer.tsx:36-45`) per outcome
stream; a withheld calculation is announced **as withheld, never as loaded**; competing regions are merged only
through a reviewed assistive-technology test, never by downgrading an `alert`. Visually-hidden announcements are
**not** visual clutter to trim.

---

## 3. Design tokens (presentation-only proposal)

Mockup specification, not approved requirements or measured values (§12). Colour never carries status alone —
each status token is paired with the §2.2 symbol and text. Values are placeholders for the accepted premium
design system (`docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md`), to be confirmed against the real palette at build.

| Token group | Token | Value (proposal) | Use |
|---|---|---|---|
| Surface | `--surface-canvas` / `--surface-raised` / `--surface-sunken` | `#F7F8FA` / `#FFFFFF` / `#EEF1F5` | Page / cards / inset panels. |
| Ink | `--ink-strong` / `--ink` / `--ink-muted` | `#11151C` / `#2C3440` / `#5B6472` | Headings / body / captions. Body ≥ 16px; legal text never shrinks. |
| Line | `--line` / `--line-strong` | `#E2E6EC` / `#C7CDD6` | Dividers, card borders. |
| Accent (action) | `--accent` / `--accent-ink` | `#2F5BEA` / `#1C3AA8` | One primary action per view; links. |
| Status: draft/conditional | `--status-draft` + `◐` | `#4B57C4` | Draft rule result / `conditional`. |
| Status: review | `--status-review` + `!` | `#B5750B` | `professional_review_required`, withheld. |
| Status: conflict | `--status-conflict` + `≠` | `#C23B4B` | `data_conflict`, identity mismatch. |
| Status: unsupported | `--status-unsupported` + `∅` | `#5B6472` | `unsupported`, boundary-check unavailable. |
| Status: n/a / unknown | `--status-na` + `—` | `#8A93A2` | `not_applicable`, Unknown, "Not calculated". |
| Status: verified | `--status-verified` + `✓` | `#1E7A50` | `verified` only (G6-reachable, not in draft). |
| Provenance | `--claim-city` / `--claim-proposed` / `--claim-generated` / `--claim-human` | slate / `#9A6212` amber / dashed indigo / slate | Claim-class chips (§2.1). |
| Type scale | `display / h1 / h2 / h3 / body / caption / mono` | 28 / 22 / 18 / 16 / 16 / 13 / 13px | Caption never used for legal disclosures. |
| Space | `--s1…--s6` | 4 / 8 / 12 / 16 / 24 / 40px | 8px rhythm. |
| Radius / elevation | `--r` / `--shadow` | 10px / `0 1px 2px rgba(17,21,28,.06)` | Calm, low-elevation. |
| Focus | `--focus-ring` | `0 0 0 3px rgba(47,91,234,.45)` | Visible on every keyboard target. |
| Breakpoints | `--bp-tablet` / `--bp-phone` | 768px / 360px | See §11. |

**Reduced motion:** all transitions collapse to none under `prefers-reduced-motion`. **Contrast:** every
status hue meets ≥ 4.5:1 against its surface for text and pairs with a symbol so colour-blind users lose nothing.

---

## 4. Global shell, navigation and information architecture

One restrained shell wraps every flag-on surface (grounds A01–A03, LS-P01, SH-01/05/08).

**Desktop (≥768px).** Slim top bar: product mark · **"Internal build" environment badge** (opens the full
internal/no-access-control/do-not-share/"nothing here is a legal determination" restrictions in a native
disclosure — kept visible at every width, LS-P01/A01, B-001 open) · property identity header (address; borough +
BBL; explicit **Draft analysis** state; "Change property"). Left rail = task nav grouped by decision:
**Overview · Property records / Zoning · Proposal · Evidence · Report**, plus **Documents** when available and a
clearly-labelled **Planned** group (never advertised as working, A02/F07). One persistent workspace status line
"Preliminary analysis — professional review required" in the content region (A03; the nav footnote cannot be the
survivor — it is hidden ≤700px and in print). Skip-to-workspace link first in tab order.

**Mobile (≤360px).** Top bar collapses to mark + environment badge + identity + a nav toggle
(`aria-expanded`/`aria-controls`). The environment badge and the review line stay visible (never hidden by the
`architect.css:138` ≤700px rule — that hide is a P0-flagged gap, SH-02/A01/A03). Nav is a full-width menu keeping
every destination and its Planned/Unavailable state.

**Required legal disclaimer (SH-01, PRD §29) — preserved verbatim, one deliberate landmark, full prominence,
every route and every printed page:**

> This platform provides preliminary development and zoning feasibility information based on available public
> records, user-provided assumptions, and the platform's current rule coverage. It is not a legal opinion,
> architectural or engineering certification, DOB determination, permit approval, or guarantee that a proposed
> development will be approved. Results must be reviewed by qualified New York professionals before reliance,
> acquisition, design, filing, financing, or construction.

Rendered as `<footer role="contentinfo" aria-label="Required disclaimer">` (`app/layout.tsx:35-48`), outside every
print-hiding rule. **A tooltip or collapsed-only disclosure does not satisfy PRD §29.**

---

## 5. Per-surface specification

Each surface names one dominant decision, gives desktop + mobile wire-level annotations, and the four required
states (normal / boundary / missing / failure). The **disclosure placement table** lists every L-marked P0 row
for that surface with its progressive destination zone, accessibility path and print path; the ledger row holds
the authoritative per-cell detail (cited). Frame numbers reference `P1-mockups.html`.

### 5.1 Search  (mockup frames S-D / S-M)

**Dominant decision:** *Which property am I analysing?* One search field is the single dominant control.

- **Desktop:** centred entry card — one address field (with autocomplete), an explicitly-named "Search by tax
  lot (BBL)" native `<details>` alternative, the environment badge + review line, and the disclaimer footer.
- **Mobile:** full-width field; BBL alternative below; nothing else competes.
- **Normal:** typed query → address suggestions list (`kind:"suggestions"`), keyboard + touch, no auto-pick.
- **Boundary:** delayed-but-healthy source (6 s deadline, DB-008) shows a patient "still searching" status, not
  a failure; manual fallback preserves the typed text and clearly labels which structured fields are still
  needed (AD04, §13 Medium — copies query into Street today: flagged, not silently "fixed").
- **Missing:** zero results / `no_match` → honest "No matching address" with a BBL path; invalid BBL → the four
  distinct `lib/bbl.ts` errors (empty / digits-only / length / borough), never one generic red icon.
- **Failure:** `error` reasons `source_unavailable` (auto-retry once), `rejected`, `rate_limited`, `timeout`,
  `unavailable` each render a distinct recovery action, spoken once by the address announcer.

| L-marked row | Progressive destination (zone) | Accessibility path | Print path |
|---|---|---|---|
| SH-01 | Disclaimer footer landmark (global). | `role=contentinfo` "Required disclaimer", full §29 text. | Prints every page. |
| SH-02 | Compact landing header; environment badge + review line kept at every width. | Static header; keyboard link "Open workspace →". | Not a print surface (P5-D1 if landing prints). |
| SH-05 | Property/rule announcer (withheld never announced as loaded). | 2 `OutcomeAnnouncer` regions, one message per outcome. | Screen-reader only; visible parity prints via brief. |
| SH-10 | Search/failure state; mismatch retains returned record in evidence. | `role=alert` "No property selected"/mismatch; loading `role=status` `aria-busy`. | Not printed (replaces workspace). |
| SH-11/12/13 (legacy) | Legacy lookup identity + dated source chip + completeness state; BBL form unavailable-address "Why?". | Legacy announcer; `#bbl-error` polite; disabled address input `aria-describedby` reason. | Legacy has no print surface; shared primitives print via brief (LS-P). |
| SH-15 | Per-route browser title keeps the "(internal)" qualifier. | Document `<title>` per route. | Header only if user enables print headers. |
| AD01–AD28 | Single search/recovery area: suggestions, manual fallback, each typed error/retry category, the address announcer. Ledger holds each row's exact destination. | Address `OutcomeAnnouncer` (`AddressResolutionScreen.tsx:299`); autocomplete `role=status`; labelled fields; focus rules per row. | Not printed (pre-property state). |

*Placement note:* all 24 L-marked AD rows land in this one search/recovery area; their individual
progressive-destination/accessibility/print cells are authoritative in `disclosure-ledger-a.json` (AD01…AD28).

### 5.2 Confirmation  (mockup frames C-D / C-M) — D-040 released

**Dominant decision:** *Is this the right lot before I commit to analysis?*

- **Desktop:** confirm card = matched address + BBL + PLUTO-representative-address identity rows (material
  differences immediately visible), a **reference lot outline** on a MapLibre map (context only, never measured),
  the point-of-decision **city warnings above Continue**, and one primary **Continue** action.
- **Mobile:** identity rows stack above the map; warnings and Continue pinned in reading order.
- **Normal:** matched lot renders; outline present with "Approximate — reference only" accuracy line.
- **Boundary:** entered vs matched vs PLUTO addresses differ → all three identities kept distinct (never
  collapse the entered unit into billing); equal IDs legitimately collapse to one line.
- **Missing:** no lot geometry / no WebGL → map shows a truthful unavailable state; the outline's
  accuracy/source line and the BBL identity survive without the map.
- **Failure:** map render / basemap-only failure → a street-layer error never erases a working parcel; map
  failure and map accuracy stay separate meanings (no-loss §10.2).

**City-warning preservation (binding, §12 rule 2):** both exact city warning messages stay **above Continue** in
the first slice; an icon-only replacement is insufficient and would require a named reviewer-approved visibility
contract.

| L-marked row | Progressive destination (zone) | Accessibility path | Print path |
|---|---|---|---|
| AC01–AC11 | Confirm card: matched-address identity, record-address channel, equal-ID collapse, city warnings, Continue. | Confirm announcer; labelled rows; warnings visible above Continue. | Not printed (pre-analysis). Ledger AC01…AC11 authoritative. |
| M01–M13 | Lot-outline map block: "Approximate" accuracy + source line; truthful rendered/unavailable/no-WebGL/multi-parcel states; hidden summary region. | `LotOutlineMap` summary `role=status` + visible layer `role=status` (`:626-629`); keyboard path is the numeric identity, not the map. | Not printed (context map). Ledger M01…M13 authoritative. |
| LC01–LC22 (legacy off-flag) | Legacy confirm identity/source/completeness/warnings until route retirement. | Legacy confirm announcer; labelled controls. | Legacy has no print surface. Ledger LC01…LC22 authoritative. |

### 5.3 Overview  (mockup frames O-D / O-M)

**Dominant decision:** *What kind of result is this, which limits are available, and what prevents reliance?*

- **Desktop:** two-column canvas — ~55–60% real site map/context, ~40–45% limit matrix (an ordinary two-column
  layout, not a wall of cards). Above it: a single **exception strip** naming only active issues (identity
  mismatch · unresolved conflict · critical input · stale source · incomplete assessment) with critical field
  names and the blocked effect visible. Contextual **inspector** opens only when a fact/limit/warning/source is
  selected. Existing-building facts live in one collapsed, reversible group.
- **Mobile:** map and results stack; the inspector becomes a labelled full-width panel with close + focus return.
- **Normal:** city-record FAR and evaluated (draft) FAR shown as **distinct** rows; cap cell carries "FAR only —
  Buildable envelope not assessed" and the readable per-cap coverage status; bulk rows show honest states.
- **Boundary:** wide-street conditional vs conservative FAR kept distinct with the withholding sentence next to
  the value; split districts keep every district and preserved share ranges.
- **Missing:** `missing_critical`/`missing_noncritical` named with counts (critical never behind only a number);
  Unknown stays the word "Unknown", never a blank or dash; stale source dated.
- **Failure:** blocked result "Rule details incomplete" with the captured record preserved; each `fail_safe`
  branch keeps its distinct label (never a generic "Warning"); identity mismatch withholds and retains the record.

| L-marked row | Progressive destination (zone) | Accessibility path | Print path |
|---|---|---|---|
| SH-05/06/08/09/14 | Announcer parity; Analysis-issues rows; property header identity disclosure; single analysis-status area; route error boundary. | `OutcomeAnnouncer`s; `role=alert` for identity/mismatch/error boundary (kept); `role=status` for loading. | SH-08 header hidden in print (P5-D3); SH-09 prints when present; SH-14 replaces screen. |
| ZC-01–ZC-04 | Zoning-context panel: retrieved district/overlay/special-district with source; map is not canonical intersection proof. | Named region; chips with source disclosures; static (speaks via rule-eval announcer). | Prints via ZoningSection (ZC-04 map is display-only). |
| A01–A15 | Shell environment/nav/status; exception strip (A04); development-limits header, cap row, wide-street rows (A05–A11); assessment-coverage matrix (A12); site-context split (A13); condo substitution & withhold notices (A14/A15). | Per row: `role=status` for the issue strip and blocked result; `role=alert` kept for identity withhold (A15) and NOT for legitimate substitution (A14); named source controls with focus return. | A04–A12/A14/A15 print in the brief by default; A13 is screen-only (facts reach paper via PropertyFacts). Ledger A01…A15 authoritative. |
| LS-P01,03–15 (shared) | Environment strip; coverage badge + legend; facts table; zoning; missing-inputs; conflicts; unsupported; professional-review; provenance. | Coverage badge = symbol + enum + visually-hidden gloss (never colour alone); legend always-visible for present statuses; named source disclosures; `role=status` counts. | Print in the brief by default; badge glosses reach paper via CoverageLegend; JSON tier decision at P5 (LS-P15). Ledger LS-P01…LS-P15 authoritative. |
| LS-P16 (shared) | The one persistent property announcer. | Visually-hidden `role=status` polite/atomic, exactly-once. | Not printed (by design). |

### 5.4 Condo records  (mockup frames K-D / K-M)

**Dominant decision:** *What does the city record say about this condo's land — and does anything prevent using
a computed allowance?* **Records, never allowances** (D-073-R006): this surface transports recorded base lots
for display; it derives no value and unlocks nothing.

- **Desktop:** "City records for this condo — Reference only" group: entered-unit / billing-lot / land-lot
  identity rows (distinct, equal-ID collapse), per-base-lot recorded zoning ("not recorded (unknown)" when the
  resolver carries none), the site-definition confirmation block, and a dataset/version/retrieved provenance
  footer.
- **Mobile:** identity rows then records then provenance, single column.
- **Normal (single):** one base lot resolved → paired entered/base identity joined by "City record"; allowances
  are governed by the overview limits, not by this panel.
- **Boundary (multi_lot):** two-plus base lots → all base lots shown; the divergent-zoning notice appears **only**
  when zoning is actually recorded for a lot; a recorded human site confirmation may be present.
- **Missing:** unknown zoning per lot + a "Zoning missing for N lots" summary; the named ZTLDB source-gap note;
  no active confirmation distinguishes "never recorded" from "revoked/superseded".
- **Failure:** `unresolved` / `resolver_error` withhold allowances (monotonic ADD-only) and the surrounding
  limits carry the refusal; a self-attested confirmation shows "Self-attested — not usable for calculations"
  even when the payload claims otherwise; a transport `unavailable`/`route_absent` shows **no records** and
  never withholds on its own; a parcel discrepancy is surfaced for review and never silently revokes the record.

| L-marked row | Progressive destination (zone) | Accessibility path | Print path |
|---|---|---|---|
| C01 | Single-lot substitution: paired identity + "City record" + source stamp; expandable provenance. | `role=group` "Recorded base lot for this condo" + h2. | Prints in brief (report-view.test.tsx:417-430). |
| C02 | "City records — Reference only" + visible channel-disagreement state; no allowance wording. | `role=group` "City records for this condo" + h2. | Prints in brief. |
| C03 | Entered-unit / billing / base-lot identity table; equal-ID collapse; per-lot zoning. | Plain-text identity lines; unknowns as "not recorded (unknown)". | Prints in brief. |
| C04 | Recorded human site confirmation: actor / time / parcels + "Human record"; exact fractional timestamp. | `role=group` "Recorded site definition for this condo". | Prints in brief. |
| C05 | "Self-attested — not usable for calculations", always beside the record. | Text refusal (never colour/icon alone); no live region. | Prints in brief. |
| C06 | "Parcels differ" beside the confirmation; old/current comparison in disclosure. | Text state; comparison in native disclosure. | Prints in brief. |
| C07 | "Not confirmed" vs "No active confirmation" with reason/history. | Two distinct texts; history in disclosure. | Prints in brief. |
| C08 | Per-row "Unknown" + "Zoning missing for N lots" + named ZTLDB gap. | "Unknown" as a word, never blank/dash. | Prints in brief. |
| C09 | Source/dataset/version/retrieved footer with explicit unknowns (exact values). | Exact values as text. | Prints (exact retrieved/version pinned). |
| C10 | Non-multi-lot channel disagreement: "Records unavailable" + reference to the actual limits. | `role=status` (not alert); no second region. | Prints in brief. |
| C11 | Honest absence (loading/unavailable/unresolved/error/non-condo): no fabricated records; limits explain the refusal. | Renders nothing; limits speak via rule-eval announcer. | Nothing to print by design. |

### 5.5 Proposal / drawing  (mockup frames P-D / P-M) — D-076 + D-082 released

**Dominant decision:** *What am I proposing, and does a preliminary check flag anything?* Everything here is
**Proposed input**, not a city record; a check result **never** implies approval (D-076-R002).

- **Desktop:** three zones — (1) **Proposal editor** header with scoped "Proposed input" + "Preliminary check"
  badges and professional-review qualification; the numeric outline table (EPSG:2263 feet) as the authoritative
  model; levels and exterior-walls editors; (2) **Drawing surface** ("Proposed sketch / Approximate", Drawing →
  Converted-coordinates stages, an "Accuracy & method" detail, a reference map that measures nothing, and an
  always-available manual coordinate path); (3) the **Preliminary development limits** panel with the
  **Generated building option** — shown only as it exists today (route unmounted, §8.5).
- **Mobile:** editor table first (numeric authority), then drawing, then limits; the manual path is never
  replaced by a map-only surface.
- **Normal:** run check → per-check `pass`/`fail`/`could_not_check` with the visible could-not-check reason;
  conversion `bridged` shows exact fit residual (RMS), method, alignment and the verbatim server disclosure.
- **Boundary:** fewer than three finite points → Convert disabled with a **visible** readiness count and
  incomplete-row markers (never tooltip-only); a changed draft after a check shows a "Changed since check"
  state and the stale result is never saved as current (§13 High — freshness; reproduce before repair).
- **Missing:** example seed (`rectangleSampleDraft`) must not read as property-specific "your input" — it is a
  labelled example or actual provenance (§13 High — behaviour task first, §10 register); a generated option is
  **not** available merely because an adopt button exists.
- **Failure:** conversion `residual_too_high` / `correspondence_unavailable` / `out_of_neighborhood` /
  `feature_unavailable` / `source_unavailable` each show their typed refusal with exact residual/bound and
  "no coordinates were produced"; a client-blocked draft shows "Proposal not sent" with repairable errors.

*In-flight note:* the drawing rows (DR-01…DR-23) and max-envelope rows (ME-01…ME-17) are **pinned at
`b56f3d5b`** because M5-T078 / M5-T079 are in rework; the ledger re-pins them after those lanes accept. This
spec places their destinations; the exact copy is re-checked at re-pin (P0 §8).

| L-marked row | Progressive destination (zone) | Accessibility path | Print path |
|---|---|---|---|
| PE-01,03,04,07,08 (+02,10 cross-ref) | Editor header badges; numeric outline table as authority; not-sent + repairable errors; adopted/removed-wall announcements; example labelling. | Editor `OutcomeAnnouncer` (`ProposalEditor.tsx:180`), one message/event; `role=alert` problems card kept; table caption names the numeric authority; unique accessible names per repeated control. | Not printed today; P5-D4 export carries "Proposed — not a city record" + numeric outline + provenance if added. |
| DR-01…DR-23 | Drawing header ("Proposed sketch / Approximate"); reference-map "context only"; drawn-points table + keyboard path; readiness/incomplete markers; converted state (residual + disclosure + "approximate, not a survey"); typed refusals; hidden point-count status. | Named draw region; draw `OutcomeAnnouncer`; `role=alert` for refusal branch; disabled-Convert reason as visible adjacent `role=status`; map instructions match the rendered interactive surface. | Not printed today; P5-D4 export carries the sketch/approximate/not-a-survey framing + residual (D-083-R006). |
| PC-01,02,03,04,05,06 | Check report: per-check pass/fail/could-not-check with visible reason; conversion residual; "Changed since check" state. | `role=alert` check-problems card kept; announcer parity. | Not printed today; P5-D4. |
| PV-01,02 | Variations: session-only comparison; "Changed since check" freshness before save. | Editor announcer ("variation loaded"). | Not printed today; P5-D4. |
| ME-01…ME-17 | "Preliminary development limits" panel + "Generated building option": server disclosure, binding rule/version, typed reason instead of a missing value, "could not check" withhold, no adopt affordance for unsupported/non-contained geometry. | Max-envelope `OutcomeAnnouncer`; `role=alert` non-bridged branch kept; adopt hidden when not contained. | Not printed today; panel shown as-is (route unmounted). |
| SW-01,02 | Scenario workspace: single-preliminary-scenario scope, cap headline, "association not confirmed / not promoted as property limits". | No new live region; static scope text. | Cap headline prints (SW-01 scope note P5-D5); constraints vs "not promoted" label P5-D6. |
| ZC-04 | Reference map on the proposal/overview (display only, never measured). | `LotOutlineMap` layer `role=status`. | Not printed. |
| LS-C01–LS-C28 (shared scenario legend) | Compare/scenario result header, identity mismatch (prominent), cap card with both review flags beside the value, no-scenario/conflict/ranges blocks, citation chain, session-only state. | `role=status` completeness banner; mismatch text beside focused heading; flags as text adjacent to the value (never colour alone); single compare announcer. | Legacy compare not printed; architect scenario blocks reach the brief only via ScenarioConstraints/Assumptions (P5 decision LS-C09). Ledger LS-C01…LS-C28 authoritative. |

### 5.6 Evidence  (mockup frames E-D / E-M)

**Dominant decision:** *Where is the exact basis for this value?* One result/fact inspector with three tiers:
**summary → trace/source → raw**.

- **Desktop:** searchable grouped evidence index (master) + on-demand inspector drawer (detail). Facts view =
  Lot/Building/Identity tabs with one filter/count toolbar. Zoning/rule-evaluation evidence carries the
  calculation trace, citations (verbatim quotes), the wide-street D-052 provenance (reason + fallback note in the
  readable tier; internal IDs/machine values in the raw tier), and the scenario scope note + formula.
- **Mobile:** index collapses above; the inspector is a full-width panel with focus-in, Escape-close, focus
  return to the trigger.
- **Normal:** a value's "Source / Why" opens the inspector to that record with ZoLa-first links and the
  current-vs-captured distinction.
- **Boundary:** filter narrows facts → "No facts match this filter" with a Clear action restoring all rows.
- **Missing:** "Source record unavailable — was not supplied"; "No safe official dataset link" when links are
  absent; "No transformation steps recorded"; explicit unknown units.
- **Failure:** a hostile captured URL is **never** turned into a link; unsafe URLs stay non-links; the raw
  captured JSON is a deliberate final tier, lossless.

| L-marked row | Progressive destination (zone) | Accessibility path | Print path |
|---|---|---|---|
| F02,03,04,06,07,08 | Identity & coverage table (explicit unknowns); data-completeness state (never "Feasible"); spatial/boundary-assessment; read-only confirmations; planned-capability "not available in this version"; zoning-flags matrix (Unknown as a word). | Definition lists; `aria-pressed` fact tabs; `role=status` count; named disclosures. | F02/F03/F06/F08 print in brief; F04 spatial caveat + reasons P5 decision; F07 not printed. Ledger F01…F08 authoritative. |
| E01–E16 | Inspector drawer selection/absence; captured record with ZoLa link + current-vs-captured; dated stale + review count; raw lossless record; per-fact provenance/link safety; original vs normalized; review history; evidence index; complete-record availability; session-address identity; calculation summary + reasons; wide-street readable detail; determination trace; steps/outputs/uncertainty; citations; scenario scope note/formula. | Inspector `<aside tabIndex=-1>` focus-in / Escape / focus-return; `role=status` for unavailable; native disclosures expose expanded state; verbatim `<blockquote>` citations; named external links. | Inspector hidden in print; the same records reach paper via the brief appendix (ReportSources, R03/R04/R05); readable tier vs raw (audit appendix) decisions in ledger. Ledger E01…E16 authoritative. |
| LS-E01–LS-E11 (shared rule-eval legend) | Rule-evaluation result: draft coverage status, competing-rule conflict, spatial candidates/ranges, effective-window recorded dates. | `role=status`/announcer parity; ranges keep exact text as accessible name. | Reaches paper via Calculation evidence. Ledger LS-E01…LS-E11 authoritative. |

### 5.7 Report  (mockup frames R-D / R-M) — the one printing surface (★)

**Dominant decision:** *Can I take this off-screen with its scope, identity, conflicts and review status
intact?* The brief is the only designed print surface (`ReportView.tsx:67-132`).

- **Desktop:** a concise print toolbar (Print · "Include full audit appendix" checkbox · "Not saved" state ·
  BBL + generated identity), a contents nav, and disclosure sections that are closed on screen but **opened for
  print** (`beforeprint` opens every non-raw `<details>`; the raw tier prints only when the appendix is
  selected; screen state is restored afterward).
- **Mobile:** contents list then sections; the print action stays reachable.
- **Normal:** brief prints label, BBL, generated time, "This brief is not saved automatically.", the
  development-limits (with FAR-only + readable status + wide-street withholding), identity notices, condo records,
  facts, zoning flags, coverage legend glosses, calculation evidence (reasons, citations, steps), scenario
  constraints/assumptions, and the source & review appendix.
- **Boundary:** a printout taken while loading shows the loading/failure channel state (SH-09) — the print
  matches the screen, never a clean blank.
- **Missing:** absent inputs print as the named missing-input state; unknown prints as "Unknown — not supplied".
- **Failure:** identity mismatch prints its `role=alert` with both IDs and "Results are withheld"; incomplete
  evaluation prints "Numerical summaries are unavailable. The returned record is preserved below."

| L-marked row | Progressive destination (zone) | Accessibility path | Print path |
|---|---|---|---|
| R01 | Print toolbar: identity/time, "Not saved", audit-appendix control. | Named Print button; labelled appendix checkbox; "Not saved" as text. | Intro (label/BBL/time/"not saved") prints; controls hidden in print. |
| R03,04,05 | Source & review appendix: captured-vs-current notice; per-fact original/normalized/links/dates/conflict/review; confirmations history with explicit unknowns. | Column + row headers; named links; unknowns as words. | Prints by default (appendix opens; JSON is raw tier). |
| SH-01 | Disclaimer footer (global; also the report's canonical reliance statement on paper). | `role=contentinfo`. | Prints on the brief and every page. |

*Structure row R02 (`V/L->V/R`) governs the contents nav + controlled audit inclusion; placed here as the
report IA even though its L-portion is inclusion-behaviour.*

**Explicit P5 print decisions (real gaps, carried, not "fixed" here):** P5-D1 internal-environment identity on
paper (A01/LS-P01); P5-D2 nav footnote reliance framing; P5-D3 searched-vs-PLUTO identity alias in the printed
brief (SH-08); P5-D4 no proposal/limits/drawing print exists yet; P5-D5/P5-D6 scenario scope/label parity;
F04 spatial caveat; LS-P10 grouped missing fields; LS-P15 captured-JSON tier. These stay open questions for the
P5 slice; none is silently resolved.

---

## 6. Coverage matrix (AS-2) — 7 surfaces × 4 states

Every cell is filled; "n/a — why" where a state does not exist for a surface.

| Surface | Normal | Boundary | Missing | Failure |
|---|---|---|---|---|
| **Search** | Suggestions list (`kind:"suggestions"`), no auto-pick. | Delayed-but-healthy source (6 s, DB-008) → patient status; manual fallback keeps typed text. | Zero results / `no_match`; four distinct BBL errors. | `error` reasons (`source_unavailable`/`rejected`/`rate_limited`/`timeout`/`unavailable`), distinct recovery each. |
| **Confirmation** | Matched lot + reference outline + city warnings above Continue. | Entered/matched/PLUTO differ (kept distinct); equal-ID collapse. | No geometry / no WebGL → truthful map-unavailable; identity survives. | Map render / basemap-only failure; parcel not erased. |
| **Overview** | City-record vs draft FAR distinct; honest bulk states. | Wide-street conditional vs conservative; split districts + ranges. | `missing_critical`/`noncritical` named + counts; Unknown as a word; stale dated. | Blocked result "Rule details incomplete"; each `fail_safe` label distinct; identity mismatch withholds. |
| **Condo** | `single` base lot → paired identity + "City record". | `multi_lot` → all base lots; divergent-zoning notice only when recorded; human confirmation. | Unknown zoning + "Zoning missing for N lots"; never-vs-no-active confirmation. | `unresolved`/`resolver_error` withhold; self-attested refusal; transport `unavailable` shows no records, no withhold. |
| **Proposal / drawing** | Check `pass`/`fail`/`could_not_check`; `bridged` conversion with residual + disclosure. | < 3 finite points → visible readiness + incomplete markers; "Changed since check". | Example seed labelled (not "your input"); generated option not implied by an adopt button. | Typed conversion refusals (`residual_too_high` etc.) with exact residual/bound; "Proposal not sent". |
| **Evidence** | Inspector summary→trace→raw; ZoLa-first + current-vs-captured. | Filter → "No facts match this filter" + Clear restores. | "Source record unavailable"; "No safe official dataset link"; "No transformation steps recorded". | Hostile URL never a link; raw JSON stays lossless final tier. |
| **Report** | Brief prints scope/identity/conflicts/review + appendix. | Printout while loading shows the channel state (matches screen). | Absent inputs print as named missing states; "Unknown — not supplied". | Identity mismatch `role=alert` + both IDs prints; incomplete-evaluation notice prints. |

---

## 7. Preservation checklist (AS-3)

Nothing below may be dropped, weakened, shortened to an icon, or hidden behind hover for visual simplicity.

- [ ] **PRD §29 disclaimer** kept **verbatim** (§4 text), at full prominence, in one deliberate labelled landmark
      on every route and every printed page (SH-01). A tooltip/collapsed-only form does **not** satisfy §29.
- [ ] **Internal-build / no-access-control / do-not-share / "nothing here is a legal determination"**
      environment disclosure kept visible at every width (LS-P01/A01); the access/sharing qualification stays
      while **B-001** (no-auth) is open.
- [ ] **Point-of-decision city warnings** kept, both exact messages, **above Continue** in the first slice
      (§12 rule 2); any alternative needs a named reviewer-approved visibility contract.
- [ ] **Exact returned disclosures unchanged:** verbatim `report.disclosure` (drawing), `not_verified_disclaimer`
      (rule evaluation), server `wide_street.reason`/`fallback_direction_note`, "Preliminary development limits"
      title, condo provenance values, citation quotes. No untested synonym.
- [ ] **Claim classes stay distinct:** City record ≠ draft rule result ≠ generated option ≠ proposed input ≠
      human confirmation record. No reference-to-result promotion; no proposed shape shown as a permitted building.
- [ ] **Named states preserved:** Unknown, source unavailable, conflicting, not calculated, genuine zero, each
      distinct; no universal dash.
- [ ] **Withholding is authoritative and monotonic:** identity mismatch, integrity failure, condo `multi_lot`/
      `unresolved`/`resolver_error` withhold computed allowances; a record/confirmation never unlocks them.
- [ ] **Conflicts keep both values, sources, and "unresolved"** at the affected result; no silent winner.
- [ ] **Ranges stay ranges** (base-district share min/point/max); spatial uncertainty keeps the no-value
      professional-review fail-safe.
- [ ] **Provenance intact:** exact source records, direct-record vs dataset links, ZoLa-first, current-vs-captured,
      source-column fallback explicitly identified; unsafe URLs stay non-links.
- [ ] **Progressive disclosure accessible:** drawer focus-in / Escape / focus-return, mobile visibility, keyboard
      expansion, one polite announcement per state change; colour never sole carrier.
- [ ] **Print carries meaning:** critical scope/identity/conflicts/review print with the number; raw audit JSON
      remains a separately-selectable appendix; screen expansion restored after print.
- [ ] **Honest unavailable capability** on reachable routes (Documents, Planned tools, 3D/CAD/PDF export not
      fabricated as working).
- [ ] **Every L-marked P0 row for these seven surfaces is placed** at its progressive destination in §5, citing
      its ledger row id, with its accessibility and print path (SH·AD·AC·M·LC·ZC·PE·DR·PC·PV·ME·SW·A·C·F·E·R·
      LS-P·LS-C·LS-E, plus the LS-F transport family in §2.6 and LS-T test-invariants in §9). Rows outside these
      seven surfaces (SR survey, DB dashboard) belong to P6 and are not placed here.

---

## 8. Cross-cutting behaviour

### 8.1 Interaction hierarchy
One primary action per view (§1). Secondary actions grouped; no prose asking the user to hunt for a button.
"Source / Why" links attach to the exact result, not merely the top of Evidence (§12 rule 3).

### 8.2 Responsive behaviour
Desktop two-column → tablet (768px) single column with the map above results → phone (360px) stacked, inspector
full-width. Density from spacing/grouping only. **Never** hide content, shrink legal text, truncate identity
without a full accessible counterpart, or abbreviate units at a breakpoint (§12 acceptance targets). The current
`architect.css:138` ≤700px hides of the environment badge and nav footnote are **P0-flagged gaps to close**, not
patterns to keep (SH-02, A01, A03).

### 8.3 Empty / loading / error states
- **Empty:** always a scoped state that names what is absent and why (e.g. "No recorded facts", "No matching
  source facts", "No active confirmation") — never a bare blank or a green success card.
- **Loading:** genuine pipeline stages, no fake percentages; one polite region; Retry moves focus to the loading
  card / page h1, never to `<body>` (LS-P02).
- **Error:** typed, distinct, recoverable; one state-specific status + the actual available control (full-address
  / manual / BBL); never suggest retrying a path the outcome makes unavailable (§10.2 recovery row).

### 8.4 Status communication
Every status = hue + non-colour symbol (§2.2) + text label. A machine coverage status is **never** remapped
because a friendlier colour fits (§12). A generic "conditional" gloss that describes an official fact must not
imply a draft calculation is an official fact.

### 8.5 3D / CAD / PDF control organisation (D-087) and the unmounted max-envelope route
D-087 released the 3D massing, CAD/DXF export and phase-C PDF blueprint **families** as future orchestrator
packets. **No web surface for them exists yet.** This spec therefore:
- places their controls in the **Planned tools** group and the Report/Proposal **action area**, using the
  existing honest "not available in this version" pattern (A02/F07) — never a fabricated 3D viewer or a working
  export button;
- when built, a 3D/massing view must **consume canonical deterministic geometry** and label proposed massing
  "Proposed — not a city record" and any engine option "Generated building option" (never "maximum allowed
  building"); an export must carry the same scope/provenance/review meaning it had on screen
  (`docs/design/d087-export-and-3d-viewer-plan.md`, reference only);
- the **max-envelope route stays UNMOUNTED**: the "Preliminary development limits" panel and its "Generated
  building option" are shown **only as they exist today** (ME-01…ME-17), with the split-district disclosure and
  DB-050/DB-051 mount prerequisites still open. No mount is designed here.

### 8.6 Accessibility requirements (summary)
Native controls, keyboard + touch, visible focus ring, meaningful accessible names on every repeated control,
one persistent polite announcer per outcome stream (LS-P16), `role=alert` kept exactly where it exists today
(identity mismatch, error boundary, drawing/check refusal) and downgraded only via a reviewed AT test, colour
never sole carrier, and print/mobile parity of critical meaning. No tooltip-only legal content (§12 rule 5).

---

## 9. Approved copy samples (AS-4) — before → after, with the protected meaning

Honesty vocabulary (binding, D-073-R006 / D-076-R002 / D-083): proposal-derived geometry is
**"Proposed — not a city record"**; an engine option is a **"Generated building option"**; nothing is ever
labelled **permitted / approved / maximum allowed building**; no legal conclusion is drawn.

| # | Before (current / risk) | After (approved) | Protected meaning |
|---|---|---|---|
| 1 | Repeated full PRD-§29 paragraph in the editor, drawing, check, each variation and each compare column. | One canonical §29 footer landmark (verbatim) **+** a scoped **"Proposed input · Preliminary check · Professional review required"** badge on the proposal surface. | Proposed-vs-record framing and professional-review requirement survive; a detached report/column still identifies its own provenance (§5.1). |
| 2 | Any "maximum allowed building" / "demonstrated maximum" wording (banned by `max-envelope-panel.test.tsx:274-290`). | **"Generated building option"** (unchanged pinned term). | Claim-class prohibition: an engine candidate is not a permitted/approved building. |
| 3 | FAR cap cell risks reading as "Buildable area". | **"{value} — FAR only · Buildable envelope not assessed"** + readable coverage status (A06). | A FAR cap is not a buildable envelope; unrelated maxima are never combined into a volume. |
| 4 | Coverage conveyed by colour / friendly word. | **Symbol + exact enum + gloss** (e.g. "◐ conditional — Official source fact, not yet professionally reviewed"). | Status never colour-only and never upgraded by language (LS-P03). |
| 5 | Drawing surface leans on paragraphs. | **"Proposed sketch · Approximate — not a survey"** + Drawing → Converted-coordinates stage labels + "Accuracy & method" detail. | Sketch is approximate proposed input with disclosed fit accuracy; conversion precision never upgrades input precision (D-083-R006); manual path always available. |
| 6 | Condo records risk allowance vocabulary. | **"City records — Reference only"**; identity rows joined by **"City record"**. | Records are city references, not computed allowances; channel disagreement stays visible (C02, D-073-R006). |
| 7 | Self-attested confirmation could look usable. | **"Self-attested — not usable for calculations"**, always beside the record. | Unverified identity never unlocks calculation; refusal not buried (C05, B-001). |
| 8 | Identity mismatch could be softened. | **"Results are withheld from this property"** with Requested/Returned IDs (`role=alert`). | Wrong-property attribution blocked; nothing reconciled (A15, LS-C04). |
| 9 | Data-completeness could read as feasibility. | **"Data completeness: {complete / some non-critical missing / critical missing}"**, never "Feasible". | Completeness is not feasibility (F03). |
| 10 | Example seed shown as "User supplied". | **"Example — not your input"** (or actual provenance) until the PE-10 behaviour task lands. | No undisclosed example masquerades as property-specific input (PE-10, §13 High → register). |
| 11 | "No property selected" blank on Compare/Confirm. | Honest card: **"No property selected — {reason}"** + a lookup action; never blank. | Honest missing/invalid identity with a way out (LS-C03). |
| 12 | Generic "Warning" for a refusal. | The **distinct** typed label ("Zoning boundary check unavailable", "Condo base lot needs site confirmation", …). | Distinct fail-safe reasons never merge (A10). |

---

## 10. Meaning-change register (AS-4) — NOT adopted; questions for qualified review

Any copy whose change could alter legal meaning is **not adopted** in P1. Each item below stays as-is today and
is routed to qualified domain/legal review (G6-class) before any wording change. Recorded here per D-086-R003.

| # | Item (source) | Why it could change legal meaning | Recommended handling |
|---|---|---|---|
| MR-1 | Wide-street 100-ft condition + "Floor area = FAR × lot area" formula wording (A08; `development-limits.test.tsx:589-605`, test-locked). | Rewording the applicability condition could change which FAR governs. | Keep verbatim; reviewer equivalence required before migration. |
| MR-2 | Null-end framing "in effect … to present" / "simultaneously in effect" (LS-C10/LS-E10, `RuleEvaluationResult.tsx:279-280`, §13 Medium). | Frames null metadata as current legal effect. | **Not adopted.** Semantic correction needs rule/domain review; keep recorded dates/unknowns, do not merely hide. |
| MR-3 | Blanket "Professional review required" over confident wide-street states (DB-025/DB-030). | May be over-cautious or mislabel a confident determination. | **Not adopted.** Owner question; the whole-evaluation review banner text is an open owner decision. |
| MR-4 | Maximum-overage "short" wording in the proposal check (DB-043(e); `proposal-check-report.test.tsx:26-33`). | Pinned wording may mislead about overage direction/magnitude. | **Not adopted.** Change only via a coordinated direction-aware copy/contract/assertion decision. |
| MR-5 | Absolute "Every value … official-source fact" + shared coverage glosses across mixed-status fixtures (LS-P13, §13 Medium). | A single absolute claim can be wrong for a mixed-status property. | **Not adopted.** Test fact/rule/scenario/human-confirmation fixtures; preserve object-specific accuracy. |
| MR-6 | Inline condo billing/base definitions relocation (A14; `analysis-identity-substitution.test.tsx:76-93`, test-locked). | Moving/shortening the definition could change the substitution's meaning. | **Not adopted.** Relocate only through a reviewed test/gate; keep "a city record of the documented resolution", "not a computed allowance". |
| MR-7 | `rectangleSampleDraft` example labelled "your input" (PE-10, §13 High). | Presents an example as property-specific authored input. | **Not adopted as copy.** Requires a reviewed P4 **behaviour** task (label/gate) before/with the copy migration. |
| MR-8 | Report freshness — a changed draft can retain a prior check result on save (§13 High; `ProposalEditor.tsx:127-137`). | A polished result could describe a prior draft. | **Not a copy change.** Reproduce and bind displayed/saved result to the checked revision before any visual "current/stale" label is trusted. |

---

## 11. Handoff notes for the P2–P7 build slices

- P1 changes no source, test, copy, rule, ledger or assessment file. It is a picture the slices build against.
- Each slice must carry the **required migration record** (assessment §10.6): current source/condition, the risk
  it prevents, the new badge/row/disclosure location, what stays visible before interaction, the accessible
  name/announcement, what prints, and the regression assertion proving meaning was retained. **A passing text
  assertion alone is not proof of visibility; a prettier screenshot alone is not proof that meaning survived —
  both are required** (§14).
- The in-flight drawing/max-envelope rows (DR/ME) re-pin after M5-T078/T079 accept; verify their copy against
  the ledger at that point (P0 §8).
- LS-T01–LS-T15 (test invariants / copy-walls) are semantic requirements, not layout locks: a wording change
  needs an explicit reviewed test migration, never a weakened selector (assessment §8.6, §10.1).

*End of P1-VISUAL-STATE-SPEC. Companion mockup: `docs/design/ui-cleanup/P1-mockups.html`.*
