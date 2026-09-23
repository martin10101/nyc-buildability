# M5-T071 — G4 DELTA attestation (VERBATIM; the fuller of two consistent transmissions)

TRANSMISSION HISTORY (orchestrator note, not reviewer text): the reviewer sent two
consistent attestation transmissions (2026-09-23 ~04:5xZ; an earlier structured one and this
condensed restatement — a provider truncation notice appeared between them; both carry
identical blob SHAs, CI facts, and the ATTESTED-PASS verdict). The FIRST (fuller) transmission
is preserved below, followed by the second's one distinct closing note. Supplements the
wave-1 PASS report (M5-T071-G4.md). The reviewer's own text follows, unedited.

---

M5-T071 G4 delta attestation — ATTESTED-PASS (qa-engineer, read-only, delta only).

IDENTITY, VERIFIED MYSELF
- Correction set 0014ad8f touches exactly five files, all in allowed_paths (+96/-18). No forbidden file, no e2e, no ProposalEditor.
- Blob SHAs for the five files are identical at 0014ad8f, fb424f2d and head 86971988: ProposalOutlineDraw.tsx 84255fd4, proposal-outline-draw.test.tsx b7b79670, ProposalOutlineMap.tsx 0c06195d, proposal-outline-map.test.tsx 9a5d1690, lot-outline-map.test.tsx 0277209b. `git log fb424f2d..86971988 -- <the five>` lists no commits, so the later branch work is disjoint.
- CI run 35819674425 at fb424f2d: conclusion success, all 18 jobs green (verified via gh myself). secret-scan 35819674469 and context-budget 35819674527 also success at that sha.

(1) TEETH ON THE THREE NEW/CHANGED SPECS — all real
- Composed-section spec, proposal-outline-draw.test.tsx:153. This suite's leaf mock renders `<div data-testid="mock-lot-map">` with no interactive aria-label and no loading node, so the wrapper classifies the surface "absent" and the whole composed section is read in that state. Restoring the old header lead puts "Click the lot map to place points" back into `section.textContent`, which the `not.toContain("Click the lot map")` assertion catches; the two explicit paragraph assertions additionally red if either the header or the map-context note reverts. Three independent red paths.
- Loading-transition spec, proposal-outline-map.test.tsx:234. Reverting the tri-state to the boolean makes `present === false` in the loading variant, so the copy falls straight to the definite negative: `toHaveTextContent("Preparing the reference map")` fails AND `not.toHaveTextContent("no interactive drawing surface")` fails. Two assertions red on that single mutation. The spec's second and third phases also keep the observer teeth (loading → present → absent at a constant bbl, where only the MutationObserver can re-sync).
- The :568 swap is not merely equivalent, it is MORE precise. The mock's `getLayer(id)` is itself implemented as `addLayer.mock.calls.find(layer.id === id)` (lot-outline-map.test.tsx:95-97), and the production hit-test guard is `queryMap.getLayer(DRAWN_OVERLAY_POINTS)` at LotOutlineMap.tsx:509. The new barrier therefore asserts exactly the production precondition on exactly the layer that gates the click, where the old `toHaveBeenCalledTimes(4)` only counted four layers of unspecified identity. The drawn-vertex wait still gates correctly.

(2) FINDING 4 IS CLOSED. lot-outline-map.test.tsx:577 pins both wrapper-observed signals against the REAL unmocked leaf: `lot-outline-loading` present synchronously at first paint, then `getByLabelText("Interactive approximate lot outline map")` after the map resolves. I re-verified both against the leaf source — the loading node at LotOutlineMap.tsx:632 renders only while `outcome === null`, and the interactive container at :642-647 only under `view !== null && drawable && !mapRenderFailed`, so the two signals are mutually exclusive by construction and the tri-state mapping is faithful to the leaf, not to the mock. A rename on either side now reds this spec.

(3) NOTHING WEAKENED. Across the entire correction set exactly ONE assertion is removed — the :568 tally — and 11 are added. No `it(`/`describe(` block is deleted. Suite counts move by exactly the three new specs (lot-outline-map 26→27, proposal-outline-draw 9→10, proposal-outline-map 17→18) with every other spec unchanged and green. The user-visible copy edits left no stale assertion anywhere: grep for "shows the recorded lot for reference", "points over the lot" and "Click the lot map to place points" across all of apps/web returns nothing.

(4) REGRESSION AT THE CORRECTED HEAD — CLEAN. web-e2e: 55 files / 1359 tests passed (up exactly 3 from 1356) plus Playwright 119 passed. Every suite I enumerated in my PASS is green again: lot-outline-map, proposal-outline-draw, proposal-outline-map, proposal-editor (7, untouched), address-confirm (35), address-resolution (34), condo-resolution-display (49), development-limits (198), max-envelope-panel (12), entry (38), workspace, report-view, source-links, analysis-identity-substitution, proposal-check-report, zoning-context-panel, autocomplete. api, control-plane, modularity, contracts, dependency-security, supervisor-bridge and the rest all green; secret-scan green.

NON-BLOCKING NOTE (no action requested, not a finding): my finding 3 named five residual tallies; the correction swapped the one I ranked as carrying the flake class (:568, cross-effect with the overlay installed). Four `toHaveBeenCalledTimes(2)` remain at :248, :530, :741, :785 of the corrected file. All four sit in single-render, no-overlay specs where the documented rebuild trigger cannot occur, so the file-wide clause is substantively met even though it is not literally exhausted. Findings 2, 5 and 6 I confirm are NOT claimed closed by this delta.

VERDICT: ATTESTED-PASS

END-OF-REPORT

---

[Second transmission's distinct closing note, verbatim:] One honest non-blocking note: the correction swapped the residual tally I ranked as carrying the flake class, but four `toHaveBeenCalledTimes(2)` remain at lines 248, 530, 741, and 785 of the corrected file. They sit in single-render, no-overlay specs where the rebuild trigger cannot occur, so the file-wide clause is substantively but not literally exhausted. Findings 2, 5, and 6 are not claimed closed by this delta, as you specified.
