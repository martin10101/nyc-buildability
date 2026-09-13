# GATE REPORT — M5-T023 (G4 integration / regression)

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only). Reviewer: independent qa-engineer agent.

**Task:** M5-T023 — MapLibre lot-outline rendering on the address confirm card + `lot_geometry` generator wiring (D-040:D-040-R001 web half)
**Reviewer:** independent G4 (integration/regression), read-only. Thin client — I did not run the JS toolchain; CI on the frozen candidate is the executable authority and I verified the stored artifact against the committed code/tests.
**Frozen candidate reviewed:** `3ff94619` (round-2 final). Confirmed `git diff 3ff94619..56c49e26` adds only control-plane records (D-043 directive files, `M5-T023-ci-evidence.md`, `state.json`, `M5-T024.json`) — no M5-T023 source/test changed since the CI run, so run 34736197598 on `3ff94619` covers the exact frozen source state.

## VERDICT: PASS
No blocking corrections. Four carried-forward advisories (all non-blocking) listed at the end. The orchestrator records the gate.

---

## Per-item findings

**1. REGRESSION SURFACE — PASS.** Read both modified regression test diffs line by line (`git diff c6aca328..3ff94619`).
- `address-confirm.test.tsx`: `stubFetchOnce` now wraps fetch in a URL-aware dispatcher (`lotGeometryStub`) that returns a 404 for `/lot-geometry` **without** calling the address spy, so `spy.mockResolvedValueOnce` queue and call-count are untouched. The only assertion change is the packet-sanctioned swap `lot-outline-placeholder` → `lot-outline` present + placeholder null (address-confirm.test.tsx:196-206); the sibling `correlation-id` assertion is retained. No existing assertion weakened.
- `address-resolution.test.tsx`: identical dispatcher pattern via `installFetch()`; every prior `vi.stubGlobal("fetch", spy)` became `installFetch(spy)` (lines 252, 266, 786, 830, 858, 879). This is **required** to keep the S7 `mockReturnValueOnce(slow.promise)` sequencing intact — the lot-geometry fetch is diverted before it can consume a queued response. No assertion line removed. Flag-off (line 261) and flag-on/no-submit (line 285) "no fetch" assertions preserved; the primary flag guard — `address-resolution-screen`/`address-form` null (lines 255-256) — is unchanged and independently guarantees `LotOutlineMap` cannot mount when the flag is off.

**2. SUITE INTEGRITY — PASS.** `git ls-tree 3ff94619 -- apps/web/src | grep .test.(ts|tsx)` = **31 files**, matching CI's "31 passed (31)". `git grep -E "skip|only|todo|fixme|xit|xdescribe"` over the five new/changed test files returns only prose in comments (e.g. "only two URL contexts", "documented only with") — **no** `test.skip`/`it.only`/`describe.skip`/`.todo`/`xit`/`xdescribe` introduced. I cannot hand-count 481 vitest / 83 Playwright, but the file count reconciles and the CI log names the 4 lot-outline journeys passing at indices 44-47.

**3. ACCEPTANCE SCENARIOS S1–S6 — all satisfied at `3ff94619`.**
- **S1** single_lot: `lot-outline-map.test.tsx` deep-equals geometry to fixture (:126/:157) + layers/fitBounds/attribution; e2e `lot-outline.spec.ts:38` (map-or-fallback, `20 ft`, `City Planning`, zola, no `square feet`/`acres`) — CI test 44 PASS.
- **S2** multipolygon/holes: real committed MultiPolygon fixture deep-equal + labelled synthetic interior-ring polygon (`lot-outline-map.test.tsx`, `lot-geometry-api.test.ts:239-258`). Gap disclosed: no committed contract fixture carries an interior ring (G1-ADVISORY-2, backlog); structural pass-through proof is adequate.
- **S3** honest empties/review: `lot-outline-map.test.tsx:191-225` (mapCtor not called); e2e `:72` condo ("condominium unit lot", no map) test 45 and `:87` multiple_features ("more than one parcel", no map) test 46; first-pick discard `lot-geometry-api.test.ts:114-121`.
- **S4** failure posture: `lot-geometry-api.test.ts` (network/parse/abort/timeout :218-229, undocumented pair→`unexpected_response` :184, `route_absent`); WebGL-unavailable (maplibre never imported); e2e `:100` ("could not be loaded", zola, no map) test 47; flag-off no-fetch inherited via address-resolution S1.
- **S5** generator drift: **structurally certain** — `check_lot_geometry()` (generate_ts_types.py:700-704) → `_check_generated` returns 1 on any byte diff of the committed file (:494-500) naming `lot_geometry`; `main() --check` calls it unconditionally (line 868) and propagates via `... or rc_lot` (line 869) to a non-zero exit. CI `contracts-typegen` green on 3ff94619 proves the exit-0/byte-identical half; the producer mutation (exit-1) half is now guaranteed by the committed code.
- **S6** regression/a11y/modularity: CI `web` + `web-e2e` + `modularity` all green on 3ff94619 (vitest 481/481, Playwright 83); a11y `role="region"`/`role="status"` summary verified in LotOutlineMap (G3-confirmed); generator deduped to 651 SLOC keeps `modularity_check` exit 0.

**4. CONVERGENCE QUALITY — PASS (complete).** I audited every locator in `lot-outline.spec.ts`. The only substring-hazard-prone locators are the three `getByLabel` calls in `resolveTo()` (lines 29-31); round-2 (`8b3428b7..3ff94619`, spec-only, 15 lines) added `{ exact: true }` **and** kept round-1's form-scoping. I verified against `AddressForm.tsx` that the in-form labels are "House number" (69), "Street" (89), "Borough" (108), "ZIP code (alternative to borough)" (131) — with `exact:true`, "Borough" no longer substring-matches the ZIP label, and each of the three lookups matches exactly one label. Every other spec locator is a unique `data-testid`. The fix is complete for this spec. **No same-cause hazard in the other changed test files:** they are vitest (Testing Library `getByLabelText` is exact-by-default) and use `getByTestId` + the URL dispatcher, not Playwright substring matching.

**5. FLAKE RISK — LOW.** `LotOutlineMap.tsx`: exactly one bounded fetch per BBL view via `useEffect` deps `[bbl, fetchImpl]` (line 218) with `AbortController` cleanup + `active` guard (205-217) — no retry storm; `fetchImpl` is undefined/stable in production. Client 12s timeout settles the loading state. E2e uses 15s visibility timeouts and dual acceptance `getByTestId("lot-outline-map").or(getByTestId("lot-outline-webgl-unavailable"))` (lines 48-51), so headless-Chromium WebGL variance cannot flake the single_lot journey. The one historical `supervisor-bridge` flake noted in the handoff is green in this run.

**6. GENERATED-ARTIFACT INTEGRITY — PASS.** `git diff c6aca328..3ff94619 -- packages/contracts/generated/` is empty; blob at 3ff94619 is `b17f5f3e98c5937cc1be903376277c57e0847faf`, matching the producer/G1 claim. Byte-identity duty held.

## CI evidence cross-check (internal consistency) — reconciles
The stored `M5-T023-ci-evidence.md` names run 34736197598 on `3ff94619`, 18 jobs — I counted exactly 18 job names listed. The run lineage (b99ca6c0 cancelled → 58839789 unscoped-`getByLabel` failure → 8b3428b7 form-scoped-but-ZIP-substring failure → f13fe0df superseded → 3ff94619 exact:true success) reconciles with the packet progress log, the producer report's two rework rounds, and my own `8b3428b7..3ff94619` diff (round-2 = spec-only exact-match). vitest "31 files" matches my ls-tree count; the 4 named lot-outline journeys map to `lot-outline.spec.ts:38/72/87/100`. Nothing in the artifact contradicts the repo.

## Carried-forward advisories (non-blocking; do not block G4)
- **ADV-A (G3-A2):** the real maplibre render path is likely never exercised in headless CI (fallback branch taken); proven only by mocked vitest + `next build`. Consider a swiftshader/ANGLE Playwright run so the first real render of the newly admitted `maplibre-gl@6.7.0` is exercised once end-to-end.
- **ADV-B (G1-A2):** interior-ring (hole) pass-through proven via labelled synthetic polygon only; recommend a real interior-ring MapPLUTO contract fixture (fixtures forbidden to this producer — a follow-up task).
- **ADV-C (G3-A4):** map created `interactive: true` (LotOutlineMap.tsx:251) for a display-only outline; consider `interactive: false` or documented keyboard affordances.
- **ADV-D (my observation, consistent with G1's observation):** the flag-off "no fetch" assertion is now indirect (a hypothetical intercepted lot-geometry call would bypass the inner spy); it remains sound only via the `address-resolution-screen`-null mount assertion. Keep that structural assertion as the flag guard.

**Bottom line:** The integration is clean and regression-safe: no existing assertion weakened, no quarantined tests, generator drift coverage structurally guaranteed, generated contract byte-identical, and the e2e convergence fix is complete and correctly scoped. CI evidence is internally consistent and reconciles with the committed code at the frozen candidate. **G4: PASS.**
