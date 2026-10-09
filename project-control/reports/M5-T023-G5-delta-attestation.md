# G5 DELTA RE-REVIEW ATTESTATION — M5-T023

> Preservation note: saved VERBATIM by the orchestrator from the same G5 reviewer's agent-return
> channel (transport entity-decoding only; the reviewer's opening confirmation line is folded
> into the body it summarizes). Companion to M5-T023-G5-security-review.md.

## VERDICT: G5 PASS STANDS at 3ff94619 — F-1 REMEDIATED (no residuals)

Same-reviewer attestation over `git diff b99ca6c0..3ff94619`. The delta touches exactly three in-scope files (`LotOutlineMap.tsx`, `lot-outline-map.test.tsx`, `lot-outline.spec.ts`); all other changed paths are control-plane (gates/reports/state/task). Reviewed read-only. The only grep hit in the added lines is the word "innerHTML" inside the explanatory code comment (not a sink); no new external URL, import, network call, or secret entered with the delta. At `3ff94619`, `customAttribution` receives the module constant `DCP_ATTRIBUTION` (`LotOutlineMap.tsx:259`), and the reflected `view.attribution` appears only as a React-escaped JSX text child (`:179`).

### (a) F-1 REMEDIATED exactly as specified (option a)
- Client-side constant added: `const DCP_ATTRIBUTION = "NYC Department of City Planning (DCP), MapPLUTO";` (`LotOutlineMap.tsx:119`).
- The HTML sink now receives the constant: `new gl.AttributionControl({ customAttribution: DCP_ATTRIBUTION })` (`:259`) — previously `customAttribution: attribution`.
- The reflected local `const attribution = view?.attribution ?? ""` is deleted; `view.attribution` no longer flows to the effect at all (effect deps reduced to `[geometry]`).
- The reflected value now appears ONLY at the React-escaped JSX text child `{view.attribution}` in `AttributionAndAccuracy` (`:179`) — verified as the sole remaining use via `git grep` at 3ff94619. No `view.attribution`/`view?.attribution` reaches any HTML/innerHTML sink.
- Net effect: the MapLibre HTML sink can only ever receive a compile-time constant containing no HTML metacharacters. This closes the finding regardless of MapLibre's internal rendering, which also moots my original "package internals unverifiable" caveat — no untrusted string reaches the sink under any code path.

### (a, cont.) Hostile-attribution test is load-bearing
New test `lot-outline-map.test.tsx:164-186`. It sets `fx.attribution = '<img src=x onerror="window.__pwned=1">NYC DCP'`, then **inspects the actual options handed to the mocked control**: `const opts = mocks.attributionCtor.mock.calls[0][0]` and asserts `opts.customAttribution === "NYC Department of City Planning (DCP), MapPLUTO"` and `not.toContain("onerror")`. It further asserts the reflected value renders as inert React-escaped text (`lot-outline-attribution` textContent contains "onerror"), that `container.querySelectorAll("img")` is empty, and `window.__pwned` is undefined. A regression to passing `view.attribution` would make `opts.customAttribution` carry the payload and the assertion would fail — the test genuinely guards the sink.

### (b) No new injection/network/dependency surface in the delta
Grep of added delta lines for external URLs / CDN / tile-sprite-glyph / `innerHTML` / `eval` / `new Function` / `fetch(` / new imports / `process.env` / `NEXT_PUBLIC` / secrets returns a single hit: the word "innerHTML" inside the explanatory comment at `LotOutlineMap.tsx:115` (documentation, not a sink). No new import, external URL, network call, flag read, or secret. `outcomeSummary` gained a `drawable` parameter and a truthful non-drawable single_lot string (G3 fold-in, copy-only, reads already-typed values — no reflected string, no injection). The `lot-outline.spec.ts` change scopes locators to the address form with `{ exact: true }` (Playwright disambiguation, test-only).

### (c) Other six PASS items unweakened
- 1 Dependency posture: package files still untouched; no import added; constant is inline. PASS.
- 2 Injection: strengthened (F-1 closed); BBL encoding, geometry-as-data, static paint literals, bounded reflection all unchanged. PASS.
- 3 Flag/exposure: no change to flag handling; no client flag read introduced. PASS.
- 4 Harness boundary: `fixture_api.py` not in the delta — unchanged. PASS.
- 5 Headers/PII: no header/console change; no full-response logging. PASS.
- 6 CSS/supply chain: `layout.tsx`/`globals.css` not in the delta — unchanged. PASS.
- 7 Generator: `generate_ts_types.py` not in the delta; `generated/lot_geometry.ts` still byte-identical (absent from delta). PASS.

### Reproduction
- `git diff b99ca6c0..3ff94619 -- <3 in-scope files>` — the reviewed delta.
- `git grep -nE "customAttribution|DCP_ATTRIBUTION|view\.attribution" 3ff94619 -- apps/web/src/components/address/LotOutlineMap.tsx` — sink uses constant (`:259`); reflected value only at React text (`:179`).
- Added-line grep for external URL/injection/network/import/secret — only the comment-word "innerHTML" (`:115`).
- CI: green at 3ff94619 per `project-control/reports/M5-T023-ci-evidence.md` (run 34736197598, 18/18). Captured separately; not independently re-run (thin client).

## Bottom line
F-1 (my sole prior ADVISORY) is fully remediated per remediation option (a), with a load-bearing test that inspects the control options. The delta introduces no new security surface and weakens none of the other six PASS items. **G5 PASS stands at 3ff94619; no residual findings.**
