# M5-T029 producer report

Producer: frontend-engineer. This is a submission for independent review, not task acceptance or deployment approval. Worktree: `/workspace/scratch/cfa2464c5c7f/nycdf-ui-work`. Implementation began from base `3d511b47`; the orchestrator subsequently integrated metadata-only intake correction `f7a5eee2`. The orchestrator records the frozen implementation SHA and independent gate results.

## Implemented surface

The existing server rule-evaluation decision selects the connected architect workspace on Property, Confirm and Compare. A request kill switch still disables it. The existing legacy routes/components remain available when that surface is off; the survey runtime gate and digest validation remain unchanged. Home has an honest Open workspace entry that does not implicitly opt in.

The workspace provides Search, Overview, Property facts, Zoning, Scenarios, Evidence, Documents, Survey review, Open issues and a printable property brief. Envelope, Units and Financials are explicitly planned and unavailable. Navigation carries a validated BBL. Confirmed searched addresses are held as browser-session presentation context, distinctly labeled when PLUTO supplies another representative address for that BBL. Profile/analysis identity disagreements are visible and their results are withheld from the selected property; the full returned record remains inspectable.

Presentation is scoped under `.architect-shell`: warm canvas, ink text/navigation, narrow rail, restrained amber parcel selection, map/result composition, contextual source inspector, mobile navigation and immediate mobile source drawer. Escape closes source inspection and returns focus. Background evaluation arrival does not steal focus. The existing required global disclaimer remains unchanged. Internal-build restrictions remain available from the shared top bar; dashboard source and styles are untouched.

Every supplied lot/building fact remains in the fact tables, with Lot/Building/Identity category controls and a name/value/units filter. Zoning districts, overlays, mapped flags and spatial evidence remain accessible; a shared block keeps missing landmark/historic/flood flags and the unconnected pending-action check explicitly unknown in both Zoning and the printable brief. Conflicts, critical missing inputs, stale-record status and unsupported analysis remain visible with affected results. Additional source and review records are available on demand.

Evidence exposes original and normalized values, units, source/version/retrieval/effective dates, linked fact review state, all confirmation/override records, rule inputs, applicability, computation operations/resolved arguments/results, outputs, source quotations/snapshot IDs, effective windows and release/review status. Absent transformation steps, dates, links and event history are explicitly absent. Complete captured property/scenario/evaluation records remain accessible as escaped text. Dataset links use the existing validated dataset-token helper. Legal-text links use only observed official HTTPS article/chapter/section forms, with a fixed origin and no credentials/query/custom port; the label distinguishes current official text from the captured quotation.

The brief starts with a concise summary, contents links and collapsed screen sections. Printing expands every readable fact, calculation, limitation and source/review section, including via the browser's beforeprint event, then restores the screen state after printing. Complete captured records are included in print only when the architect selects the audit appendix. The frontend does not claim a saved report or server PDF service.

## Source-backed address and map behavior

Source verification was performed independently by the G1 researcher and relayed through the orchestrator; independent source/security gates must confirm this implementation against their final recorded evidence.

- NYC DCP GeoSearch v2 `/v2/autocomplete?text=...`: 300 ms debounce, 6 second deadline, AbortController and sequence guard, 128 KB response cap, at most eight selectable suggestions. Only verified `nycpad` address parts and one of the five explicit borough names are selectable. Queens hyphenated house numbers are passed verbatim. The PAD candidate BBL is never used; selection invokes the existing Geoclient resolver. Manual address and BBL entry remain available after no match, rate-limit, malformed, timeout or network outcomes. Editing cancels stale suggestion and resolution work.
- Official City of New York cartographic basemap/labels: fixed 256 px XYZ templates, documented bounds and zooms 8–21, static City/CC BY attribution, selected parcel supplied unchanged by the accepted geometry client. Recenter and MapLibre keyboard zoom remain available. Street/label errors are independently visible and preserve the parcel; WebGL, geometry, map startup and transport failures retain honest fallback/source links.
- Optional NYC DCP NYZD boundaries: fixed FeatureServer query, bounded parcel-envelope request in EPSG:4326, 100-feature/30,000-point/1.5 MB limits and 8 second deadline. GeoJSON transfer-limit signals, HTTP-200 error documents, invalid/open rings, unsupported geometry and malformed coordinates fail closed. Returned polygons are passed through, never clipped or used for legal calculations. Nullable district labels remain unknown rather than becoming an absent boundary. The layer is explicitly boundary context, not a lot zoning determination.

## Module boundaries and paths

New production modules are in `apps/web/src/components/architect`, `apps/web/src/lib/architect`, plus `src/lib/address-search.ts` and `src/lib/map-context.ts`. Canonical API clients and generated contracts were consumed unchanged. Separate hooks own property, analysis, address-suggestion and zoning-context requests; presentation components own selection/display and map-layer lifecycle. The existing map remains cohesive at 564 physical lines (under the target); new modules remain below the 600 SLOC target. Rule calculations, API services, database, credentials, dependency files, locks, build/deployment configuration and dashboard files were not changed by this producer.

Other edits are confined to app route wiring/scoped styles, optional presentation props in existing address/facts/survey components, focused tests and browser journeys. No producer git mutation, project-control CLI mutation, push, merge, dependency installation or deployment was performed.

## Executable evidence

Cloud Linux runtime; dependencies were installed by the orchestrator from the unchanged lock. No owner-PC installation. Commands below ran from `apps/web` unless specified. Raw logs are in cloud scratch for the orchestrator to attach to frozen-SHA evidence.

| Command | Observed result |
| --- | --- |
| `./node_modules/.bin/vitest run src/components/architect/__tests__/workspace.test.tsx` before implementation | FAIL: new EvidenceRecord/navigation modules absent; recorded red run before implementation |
| `./node_modules/.bin/tsc --noEmit` | PASS |
| `./node_modules/.bin/eslint .` | PASS; `ui-producer-lint.log` |
| `./node_modules/.bin/vitest run` | PASS: 37 files / 601 tests; `ui-producer-vitest.log` |
| Focused source/map/workspace suite | PASS: 6 files / 41 tests; `ui-new-tests.log` |
| Print brief/audit-appendix regression | PASS: 1 file / 3 tests; `ui-print-test.log` |
| `./node_modules/.bin/next build` | PASS: compiled, typechecked, generated all seven static pages and collected build traces; `ui-producer-build-final.log` (direct tool transcript) |
| `python tools/modularity_check.py --check` from repository root | PASS: failures 0; 18 pre-existing advisory warnings; `ui-producer-modularity.log` |
| `npm run test:e2e` | Browser execution delegated to existing CI by orchestrator; not claimed locally. Local browser acquisition/preview was unavailable. |

New focused tests cover all five boroughs, Queens house-number preservation, authoritative resolver boundary, empty/malformed/rate-limited/network/oversized/deadline/abort outcomes, explicit keyboard pick, delayed stale suggestions, safe source links, bounded map parsing, per-layer failure preserving the lot, full source metadata, complete fact headings, searched/representative address separation, wrong-property withholding, missing flags, planned tools, and source focus/close behavior. Print tests distinguish default brief from requested audit appendix.

An initial test-authoring cluster failed because these new Vitest files lacked explicit Testing Library cleanup; all affected files were corrected together without weakening assertions. Type-only test errors (mock signature and unsupported RTL `exact` option) were corrected before green. Existing application assertions remained passing. Critical-regression mutation proof also ran: allowing arbitrary source URLs made the safe-link test fail (exit 1, `ui-source-link-mutation.log`); removing the evaluation BBL binding made the wrong-property test fail (exit 1, `ui-identity-mutation.log`). Both exact original files were restored and the targeted suites rerun green (`ui-mutation-restored.log`). No safety test was skipped or removed.

`e2e/architect-workspace.spec.ts` records named screenshots through `testInfo.outputPath` and attachments: search, confirmed-address overview, overview/facts/zoning/scenarios/evidence/documents/issues/brief, survey review, all three planned capability views, mobile overview and mobile source drawer. It exercises the actual recorded-profile API, with the explicitly labeled synthetic address/review harness seams already used by the repository. Existing flag-on rule-evaluation and lot-outline journeys were adapted to new entry/disclosure navigation; draft, provenance, spatial-range, fail-safe, retry isolation, keyboard, no-WebGL and attribution checks remain. The legacy flag-off and unrelated suites remain intact. Independent browser/visual review must evaluate the emitted screenshots and traces.

## Requirement map

| Requirement | Implementation / proof |
| --- | --- |
| D-061-R001 | ArchitectShell, ArchitectEntry, scoped architect styles and route wiring; named browser screenshots |
| D-061-R002 | PropertyFacts, ZoningView, OpenIssues, readable scenario constraints, identity notices; complete-facts/absent-flags/identity tests |
| D-061-R003 | EvidenceRecord, CalculationEvidence, EvidenceWorkspace, ReportSources; original/normalized/review/source-link tests |
| D-061-R004 | AddressAutocomplete + existing AddressResolutionScreen/AddressConfirmCard; manual/BBL recovery browser journey |
| D-061-R005 | Existing LotOutlineMap with source-backed streets/labels, optional bounded NYZD context; map parsing/per-layer tests and outline browser journeys |
| D-061-R006 | Available workflow pages plus truthful planned Envelope/Units/Financials, live survey context and printable brief; planned-view and print tests |
| D-061-R007 | Typecheck/lint/unit/build/modularity producer evidence; independent source/code/security/visual/CI review pending orchestrator recording |
| D-061-R009 | Frontend-only changed scope; canonical clients/contracts, legal math, backend, database, credentials and dependency files untouched |
| D-061-R010 | Bounded typing suggestions, five-borough validation, explicit keyboard selection, cancellation and resolver authority tests |
| D-061-R013 | No producer git/control/push/merge authority used; protected main and PR 241 remain orchestrator-controlled |

Delivery-only R008/R011/R012 are outside this producer's authority and belong to the orchestrator's delivery report.

## Independent G1 correction

G1 identified official mixed-district labels containing `/` that the initial NYZD parser rejected. The parser now accepts that observed character while retaining the existing string/null type, 15-character maximum, OBJECTID, geometry, byte and request bounds. Regression cases use the source-verified pairs OBJECTID 10 `M1-2/R6`, 114 `M1-4/R6A` and 132 `M1-2/R6B`, with local test polygon coordinates. Each failed against the original parser before the one-line fix. Additional checks continue rejecting non-string, empty, overlong, backslash and markup labels.

Rework checks: `./node_modules/.bin/vitest run src/lib/__tests__/map-context.test.ts src/components/address/__tests__/lot-outline-map.test.tsx` passed (2 files / 27 tests); focused ESLint and full `tsc --noEmit` passed. Logs: `ui-g1-mixed-district-red.log`, `ui-g1-mixed-district-green.log`, `ui-g1-mixed-district-lint.log` and `ui-g1-mixed-district-types.log`. This correction is submitted for independent re-review; the previous full-suite/build results above describe the first freeze.

## Independent accessibility and visual corrections

The first frozen browser run produced 95 passes and three failures; the independent G3 review also measured excessive page lengths and an incomplete map capture. The following corrections address that review together:

- Identity announcements now use the same BBL boundary as visible results. Mismatched or unstated rule-evaluation identities announce withholding instead of an applicability/spatial classification. A mismatched property profile also announces its identity error. Unsupported and spatial-uncertainty fixtures reproduced both rule-announcement defects before the fix; correctly bound results still announce normally.
- A dangling source reference now displays an explicit unavailable-source message and always retains Close while selected. A behavioral regression reproduces the previous failure and verifies focus restoration after closing.
- Facts starts with one category and provides a reversible filter. Tests traverse all categories, enumerate all supplied lot/building rows and retain source inspection after filtering.
- Evidence puts applicable determinations first and opens those traces initially; all other determinations remain individually expandable with their complete records. The supplied evaluation array is not modified.
- Overview uses a concise zoning-floor-area label. The original supplied label and reasons remain in Result scope and source wording; the complete coverage matrix retains original keys under readable labels. Envelope-blocking checks remain visible in a compact summary. Mobile metrics keep formatted numbers on one line. Architect maps show the ±20 ft accuracy and NYC DCP attribution succinctly; full technical source wording is available in Map sources and limitations. Legacy map wording remains unchanged.
- Compact survey composition places the fact queue beside the selected item and its existing checks/actions. The original document/overlays, detailed downstream impacts and state history have explicit disclosures. Current blockers and impact counts stay visible; accept/correct/reject, confirmation gating, stale drafts and the server review semantics are unchanged. The compact-mode test exercises selection, source opening, affirmation and impact access.
- Screen report folding preserves all sections for print. The shared missing-flags block is included in the standalone brief. Unit tests cover beforeprint/afterprint expansion/restoration and audit selection. A new Chromium journey checks actual print CSS: an initially hidden fact and captured-source row become visible, default raw audit records stay hidden, and explicit audit selection includes them.

The browser corrections scope GeoSearch options to the named suggestions list and assert the complete determination collection plus the applicable trace. The keyboard trace showed the old substring helper returning true after tabbing past the last overview control while the URL remained Overview; the replacement checks the exact navigation/disclosure element's focus using Tab, then asserts the Evidence URL. Screenshots now wait for scenario/evaluation outcomes and bounded map-layer loaded/unavailable settlement. Survey overlay assertions explicitly open the source disclosure. No safety assertion or journey was removed.

Final correction checks are recorded in `ui-review-corrections-full.log` (37 files / 612 tests), `ui-review-corrections-types.log`, `ui-review-corrections-lint.log` and `ui-review-corrections-build.log`. Targeted red/green logs for the identity and missing-source defects are `ui-g3-identity-announcement-red.log`, `ui-g3-missing-source-red.log` and `ui-g3-identity-source-green.log`. Browser/print-media execution and new density measurements remain pending the orchestrator's next frozen-SHA CI and independent review; this producer does not claim the first failing browser run as a pass.

## Remaining limits / independent verification

No legal-rule publication, 3D envelope engine, unit optimizer, financial model, property-confirmation persistence, document upload or saved report service was introduced. Documents shows only the actual review queue records for the selected BBL; it is not a claim to enumerate every stored document. Survey decisions retain their existing server authorization and review semantics. Source services may be unavailable or stale, and map raster capture dates are not supplied for the viewport. Browser-session searched-address context can be unavailable if the browser denies session storage; the authoritative BBL and fetched property record remain usable.

Producer checks establish implementation evidence only. Frozen-SHA CI, actual browser/visual walkthrough, source-contract/security gates and directive-completeness review remain required before orchestrator acceptance. This report does not assert that a push or local build is live deployment.
