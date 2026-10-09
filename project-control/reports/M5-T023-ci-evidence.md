# M5-T023 CI evidence capture (orchestrator; reviewers verify this stored artifact)

**Executable authority run:** CI run **34736197598** on head **`3ff94619`** (the deficit-convergence
closure verification run), branch `candidate/D-024-mrl-option-b`. Conclusion: **success** —
**all 18 jobs green**, captured 2026-09-13 ~04:55 UTC via `gh run view 34736197598`:

api-lock-verify, api-tooling-lock-verify, **web (lint + typecheck + build)**, contracts-typegen,
contracts-schema-bundle, control-plane, exact-production-install,
**web-e2e (vitest + Playwright vs recorded-official-fixture API)**, product-map, api, code-graph,
model-routing, context-index-a1, **modularity**, web-dependency-security, contracts,
supervisor-bridge, context-pipeline — every conclusion `success`.

**web-e2e job 103667983151 log excerpts (verbatim, trimmed to the material lines):**

```
2026-09-13T03:44:55.2035851Z  Test Files  31 passed (31)
2026-09-13T03:44:55.2038259Z       Tests  481 passed (481)
2026-09-13T03:46:35.6039510Z   ✓  44 [chromium] › e2e/lot-outline.spec.ts:38:5 › single_lot: the confirm card shows the lot-outline surface (map or honest WebGL fallback), keeping the +/-20 …
2026-09-13T03:46:36.0012902Z   ✓  45 [chromium] › e2e/lot-outline.spec.ts:72:5 › condo unit lot: an honest-empty state names the reason (no polygon of its own); no map is fabricated and the …
2026-09-13T03:46:36.4022597Z   ✓  46 [chromium] › e2e/lot-outline.spec.ts:87:5 › multiple_features: a review posture is shown (never a silent first-pick outline), with the ZoLa link kept (37…
2026-09-13T03:46:36.7987956Z   ✓  47 [chromium] › e2e/lot-outline.spec.ts:100:5 › upstream failure: a typed fallback states the outline is unavailable and keeps the ZoLa link — no crash, no …
2026-09-13T03:46:58.8205037Z   83 passed (1.2m)
```

- vitest: **31 files / 481 tests passed** (includes the new lot-geometry-api + lot-outline-map
  suites and both updated address suites).
- Playwright: **83 passed**, including all 4 `lot-outline.spec.ts` journeys.
- `web` job green = TypeScript typecheck + ESLint + `next build` succeed with the FIRST
  maplibre-gl import; `contracts-typegen` green = generated TS byte-identical incl. lot_geometry
  (the wired `--check` at ci.yml:392); `modularity` green.

**Run lineage (the convergence record):**
1. Run 34735198187 on `b99ca6c0` — CANCELLED (superseded by the orchestrator's own control-plane
   push; its `web` job had already succeeded).
2. Run 34735243173 on `58839789` — FAILURE: web-e2e only; all 4 lot-outline tests,
   `getByLabel('Borough')` strict-mode violation (unscoped).
3. Run 34735830129 on `8b3428b7` — FAILURE: same 4 tests, form-scoped locator still ambiguous
   (in-form collision: the ZIP label "ZIP code (alternative to borough)" contains "borough";
   Playwright getByLabel is substring by default).
4. Run on `f13fe0df` — superseded (a PS5.1 quoting failure aborted the round-2 commit while the
   push went out; disclosed in the ledger progress log).
5. **Run 34736197598 on `3ff94619` — SUCCESS (this capture): `{ exact: true }` label lookups;
   closure matrix completed BEFORE this single verification rerun. VERIFIED_CLOSED.**

G3's requested branch-visibility item (map vs WebGL-fallback in the single_lot e2e) is not
distinguishable from the captured summary lines alone; the test passes under either branch by
design and the fallback path is separately proven in vitest. Recorded as part of G3 ADVISORY-2
(already on the advisory backlog).
