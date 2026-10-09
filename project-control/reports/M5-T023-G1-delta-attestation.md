# G1 DELTA ATTESTATION — M5-T023 at 3ff94619

> Preservation note: saved VERBATIM by the orchestrator from the same G1 reviewer's agent-return
> channel (transport entity-decoding only). Companion to M5-T023-G1-code-review.md.

## VERDICT: G1 PASS STANDS at 3ff94619. No residuals.

The two rework rounds are confined to three M5-T023 source/test files (`LotOutlineMap.tsx`, `lot-outline-map.test.tsx`, `lot-outline.spec.ts`) plus orchestrator control-plane records; all interleaved commits are the other task's/control-plane records, and HEAD `56c49e26` adds control-plane only. I reviewed the actual `git diff b99ca6c0..3ff94619` on those three files.

## Verification against the four required points

**(a) No change contradicts any G1 PASS finding.**
- *Status-matrix mirror / bounded reflection / generator wiring*: `lot-geometry-api.ts` and `generate_ts_types.py` are untouched in the delta — every prior finding stands unchanged.
- *Bounded reflection (strengthened, not weakened)*: the reflected `view.attribution` is still produced by `boundedText` in `documentView` and still rendered as React-escaped text in `AttributionAndAccuracy` (unchanged). The delta only stops feeding that reflected string into MapLibre's `customAttribution` — an HTML/innerHTML sink that `boundedText` does not neutralize (it caps length + strips control chars but keeps `< > " onerror`). Replacing it with the module constant `DCP_ATTRIBUTION` (`LotOutlineMap.tsx:117`) closes the G5 F-1 sink. This reinforces, and does not contradict, my item-2 finding.
- *Display-only*: `outcomeSummary` gained a `drawable` param and one branch (`LotOutlineMap.tsx:136-149`); no coordinate/measurement math added; `geometryBounds` unchanged. Item-3 finding stands.
- *Keep-requirements*: ±20ft copy still present (server `accuracy_note` verbatim in `AttributionAndAccuracy`; drawable summary still says "plus or minus 20 feet"); ZoLa link unchanged. Item-4 finding stands (see (b) for attribution).
- *Modularity*: all edits are inside `LotOutlineMap.tsx`, the module that owns map behavior — the new constant, the `outcomeSummary` truthfulness branch, and the AttributionControl call all belong there. Nothing leaked to `AddressConfirmCard` or the transport client; `outcomeSummary` remains small and focused. Item-6 boundaries hold.

**(b) Constant attribution does NOT weaken the visible NYC DCP attribution.**
The map's `AttributionControl` now shows the constant `"NYC Department of City Planning (DCP), MapPLUTO"` (`LotOutlineMap.tsx:256-259`) — NYC DCP attribution is still on the map, now as a guaranteed, non-blankable string. The constant is byte-identical to the existing `boundedText` default in `lot-geometry-api.ts:277`, so it matches the canonical attribution. The reflected server attribution additionally still renders as React-escaped visible text (`lot-outline-attribution`). Both the on-map attribution and the visible reflected text are preserved; the requirement is satisfied, not weakened.

**(c) The new tests are load-bearing.**
- Hostile-attribution test (`lot-outline-map.test.tsx:164-186`): injects `<img src=x onerror=…>` as `fx.attribution` and asserts the mock control received the exact constant (`toBe("NYC Department of City Planning (DCP), MapPLUTO")`, `not.toContain("onerror")`), that the reflected value still appears as inert escaped text, and that no `<img>` element and no `window.__pwned` side effect exist. Reverting to the reflected string would fail this — genuinely load-bearing XSS-regression coverage.
- SR-summary test (`lot-outline-map.test.tsx:299-303`, in the WebGL-unavailable block): asserts the summary contains "could not open an interactive map" and NOT "An approximate lot outline is shown". If `outcomeSummary` regressed to ignore `drawable`, this fails — load-bearing for the G3 truthfulness fix. I confirmed the branch ordering is correct: `geometryUnusable` is checked before `!drawable`, so each single_lot sub-state gets its truthful copy.

**(d) generated/*.ts untouched — confirmed.** `git diff b99ca6c0..3ff94619 -- packages/contracts/generated/` is empty; `lot_geometry.ts` blob is `b17f5f3e…` at 3ff94619 (unchanged from b99ca6c0/c6aca328).

## Additional checks
- The `useEffect` dep array correctly dropped `attribution` (now unused; the constant needs no dep) → `[geometry]`. No stale-closure risk.
- The e2e `resolveTo` change (form-scoped locators + `{ exact: true }` on House number / Street / Borough, `lot-outline.spec.ts:25-32`) closes the Playwright strict-mode substring collision where "Borough" also matched the ZIP label "ZIP code (alternative to borough)". This is a determinism fix in the spec's own locators; `AddressForm.tsx` was not edited (not in the delta). It hardens the journey rather than weakening any assertion.
- Prior ADVISORY-1 (the `M5-T024.json` bundling) is recorded as confirmed-intended in the rework history; prior ADVISORY-2 (add a real interior-ring contract fixture) is unaffected by this delta and still stands as a non-blocking follow-up.

## CI (executable authority, orchestrator-captured)
`project-control/reports/M5-T023-ci-evidence.md` — run 34736197598, 18/18 jobs green, vitest 481/481, Playwright 83 including the 4 lot-outline journeys, at the final candidate. Consistent with the delta; I did not (and per thin-client cannot) re-run it and do not block on that.

**Result: G1 PASS STANDS at 3ff94619 — no blocking corrections, no new residuals.**
