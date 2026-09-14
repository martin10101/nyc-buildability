<!-- Reviewer returns preserved VERBATIM by the orchestrator (report-preservation rule; transport entity-decoding only). Part 1: the pinned-head review at 10aaedcc. Part 2: the F1 delta / identity-carry attestation at 63495416. -->

All evidence is gathered. Here is my gate report and verdict.

---

# Gate Report

- Gate ID: G3 (independent code review)
- Task ID: M5-T025 (D-056 web-fix packet)
- Reviewer: code-reviewer (independent, read-only)
- Producer: frontend-engineer (claude-sonnet-5 dispatch override per packet path_notes)
- Result: **PASS with required corrections — F1 BLOCKING** (record as PASS per gate-verdict semantics; F1 blocks acceptance)
- Clean environment/worktree used: PRIMARY checkout verified at pinned HEAD `10aaedccb80b3954f03d7bc1b504807ec8fb21c1` (`git rev-parse HEAD` matched before review); all content read via `git show 10aaedcc:<path>` / `10aaedcc~1:<path>`. No writes performed; no `project_control.py`/git-write/gh commands run.

## Acceptance criteria reviewed

S1 (safe source links both surfaces), S2 (outline visible with root cause), S3 (zoom controls), S4 (scope and regression), plus the packet's four named risks and the five review dimensions in the dispatch.

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-056-R001 | 10aaedcc | PASS | Structural trace below; only two hrefs exist in all changed components, both built by `datasetLandingUrl` |
| D-056-R002 | 10aaedcc | PASS with F1 correction | Fix is sound and covers the reachable cause space; the *stated* root-cause mechanism is unreachable at the call site (F1) |
| D-056-R003 | 10aaedcc | PASS | `LotOutlineMap.tsx:355`; SSR/no-WebGL paths untouched |
| D-040-R001 (display-only, this packet's slice) | 10aaedcc | PASS | No new coordinate math; geometry verbatim; framing constants only |
| D-046-R001/R002 | 10aaedcc | Not re-derived here | Orchestration-level (writer count/disjointness); DCV scope. Noted: this commit's 9 files are all `apps/web/**` + own report, consistent with the claim |

## Steps independently executed (reproducible)

```
git rev-parse HEAD                                  -> 10aaedccb80b3954f03d7bc1b504807ec8fb21c1
git show --stat 10aaedcc                            -> 9 files, +932/-26
git diff-tree --no-commit-id --name-only -r 10aaedcc -> exactly the 9 allowed_paths entries
git grep -n "href\|dangerouslySetInnerHTML" 10aaedcc -- <3 changed components>
                                                    -> only ProvenanceDisclosure.tsx:82 and RuleEvaluationResult.tsx:149
python tools/modularity_check.py --check            -> exit 0; "selected 404 files; failures 0; warnings 17"
                                                       (no touched file among the warnings — all tools/*)
git show 10aaedcc~1:apps/web/src/components/address/LotOutlineMap.tsx (lines ~250-290)
                                                    -> pre-fix wiring order verified (basis of F1)
```
No local vitest/tsc possible (no `node_modules` anywhere on this machine — thin client); test DESIGN judged statically per the dispatch. CI `web` + `web-e2e` at the pushed head remains the executable authority (S4, packet `documented_test_commands`).

## Findings

### R001 — link safety (dimension 1): PASS

- **Structural no-reflected-href property verified.** `provenance-link.ts:27-46`: `DATASET_LANDING_PREFIX` is a module constant; `SOCRATA_DATASET_ID_PATTERN = /^[a-z0-9]{4}-[a-z0-9]{4}$/` is anchored both ends, no `i`/`m` flags (JS `$` without `/m` rejects trailing `\n` — explicitly tested). `datasetLandingUrl`'s only input is the dataset id; both call sites pass `reproducibility.dataset_id` (ProvenanceDisclosure.tsx:82) and `provenance.dataset_id` (RuleEvaluationResult.tsx:149) — never `request_url`. A grep of all three changed components finds **no other href and no `dangerouslySetInnerHTML`**; `request_url` renders only through `urlHost()` React-escaped text (ProvenanceDisclosure.tsx:94, RuleEvaluationResult.tsx:165); MapLibre `customAttribution` stays the `DCP_ATTRIBUTION` constant. `target="_blank" rel="noopener noreferrer"` present on both anchors (lines 83-84 / 150-151).
- **Honest absence:** ProvenanceDisclosure invalid-id fallback renders the identical text (one inert `data-testid` added to the `<dd>` — text-equivalent, not byte-equivalent; consistent with R001's "current text", see A5). Absent `reproducibility` → no row (pre-existing guard unchanged). RuleEvaluationResult absent `dataset_id` → no row (identical to prior behavior).
- **Tests:** 10 pure-module tests (anchored-substring, full-URL, case, `javascript:`, query/fragment/whitespace/script payloads → null; exact-output identity), +4/+4 component tests including the mandated negative: hostile `request_url` never appears in any rendered href in either surface even when a valid link is present. Fixture mutation is safe: `draftApplicableDoc()` `structuredClone`s per call (`test-support/rule-evaluation-fixtures.ts:22-28`).
- **Ruling on the producer's flag (dead-in-production RuleEvaluationResult row):** NOT a mis-scope. R001 itself constrains the link to constant-prefix + validated *dataset id* and mandates honest absence when the id is absent. ZR legal-text citations carry no dataset id (producer traced `snapshots.py` + the committed fixture; consistent with the repo's ZR-capture model), so honest absence is the R001-compliant behavior on that surface, and the guarded forward-compatible row is the maximal R001-compliant implementation. See A1 for the owner-facing residual.

### R002 — root-cause coherence (dimension 2): fix PASS; narrative requires correction (F1)

- **The fix is sound against MapLibre semantics.** `runOnStyleReady` (LotOutlineMap.tsx:103): synchronous `isStyleLoaded()` fast path, else arms both `once("load")` and `once("style.load")` with a `done` idempotency guard — no double-draw possible (double `addSource` would throw); `style.load` fires before/independent of the first visually-complete render, so drawing no longer depends on the full render pipeline completing. `map.on("error")` (line 360) routes to the new typed `lot-outline-render-error` branch (lines 424-447) — honest typed fallback with the ±20 ft copy, attribution, and matching SR summary; never a silent blank. All six pre-existing fallback branches are byte-identical in the diff (only the map-branch condition gained `&& !mapRenderFailed` and a new sibling branch was inserted).
- **Framing:** `maxZoom` 18 → 19.5 via exported `lotOutlineFitBoundsOptions()` (lines 132-139, used at 392). Math independently re-derived: at ~40.71°N, z18 ≈ 0.4527 m/px → a 7.62×30.48 m lot ≈ 17×67 px; z19.5 ≈ 0.160 m/px → ≈ 48×190 px. Correct, and correctly framed as a *secondary* defect ("too small even when drawn") — the producer does not claim it explains the owner's scroll-zoom-finds-nothing observation.
- **Only-maxZoom theater check:** confirmed not theater — the pre-fix constructor centers on the lot at zoom 15 (pre-existing), so a drawn-but-tiny outline would have been findable by the owner's scroll-zoom; "found nothing" ⇒ layers were never added ⇒ the draw callback never ran. The fix targets the draw-callback contingency, which is the right layer.
- **F1 (BLOCKING — record correction, no behavior change): the stated mechanism is unreachable at this call site.** The report, commit message, `runOnStyleReady`'s ROOT CAUSE comment block, and the regression-test comments all assert the "listener attached AFTER the one-time `load` already fired" race as the root cause ("This is exactly the race that produced the reported symptom"). Verified from `10aaedcc~1` (effect body ~lines 244-290): `map.on("load", ...)` was attached **synchronously in the same task** as `new gl.Map(...)` (only two `addControl` calls between; the sole `await` precedes construction). JavaScript is single-threaded and MapLibre dispatches `style.load` from a deferred style-JSON load and `load` from the render loop after the first visually-complete render — an event *defined* to require a completed render cannot fire inside the constructor (that would also break MapLibre's own primary documented `new Map(); map.on('load', ...)` idiom). Therefore (a) `load` cannot have fired before attachment, and (b) `isStyleLoaded()` can never be true at this call site's attachment moment — the fix's synchronous fast path is *inert here* (defense-in-depth for other call orders/tests only). The mechanistically reachable root cause, consistent with **all** the same evidence: *the entire draw step was contingent on the one-time `load` event, which requires a completed first visually-complete render and can therefore never fire on a degraded-rendering device — with no `style.load` arm, no readiness check, and no error surface — yielding exactly gray canvas + attribution + no outline, permanently.* This variant is corroborated by the owner's device also failing to boot ZoLa (itself a GL map SPA; the D-056-R004 diagnostic already names hardware acceleration), and it is exactly what the delivered `style.load` arm + error routing fix. The producer's own hedge ("cannot certify the exact internal trigger… there was simply nothing left to invoke the callback") already contains the correct framing; the headline "attached-too-late" claim is the part that is false-at-this-call-site. Because D-056-R002's harness makes the named root cause part of the verified record (and the packet names root-cause theater as the G3-gated risk), the record must not carry an impossible mechanism. **Required correction:** amend `project-control/reports/M5-T025-producer-report.md` (and the ROOT CAUSE comment at LotOutlineMap.tsx:~78-96 plus the two test comments claiming the attached-too-late race "produced the reported symptom") to state the reachable mechanism, and carry the same correction into the orchestrator-owned evidence-map R002 row at restamp. Comment/report edits only — zero behavior change; delta-attestation path applies.
- **Red-on-old proof verified statically:** old code + new mock ⇒ `on("load")` never dispatches (the new mock's `on()` handles only "error") ⇒ `addSource` never called ⇒ `waitFor` fails ⇒ red. New code passes via the `isStyleLoaded` fast path (regression test) and via `once("load")` microtask (baseline tests). The 3 pure `runOnStyleReady` unit tests (immediate-sync path with `once` never called; both-events idempotency; `style.load`-only) are genuine and jsdom-expressible, per the packet's guidance.

### R003 — zoom controls (dimension 3): PASS

`new gl.NavigationControl({ showCompass: false })` at `"top-right"` (LotOutlineMap.tsx:355), constructed only on the drawable path inside the dynamic-import IIFE; `MapLike`/`MapLibreModule` extended minimally (`once`, `isStyleLoaded`, `NavigationControl`); SSR/dynamic-import structure and the no-WebGL fallback are untouched by the diff. `showCompass: false` justification (flat top-down display-only outline, no rotation affordance) is sound. Keyboard accessibility via MapLibre's native `<button>`s — standard. Test asserts both the ctor options and the position.

### Display-only discipline (dimension 4): PASS

No measurement introduced. `lotOutlineFitBoundsOptions` returns constants; the m/px arithmetic lives in comments only; `geometryBounds` and the constructor midpoint are pre-existing camera-only code; geometry still passed to `addSource` verbatim (unchanged lines).

### Scope (dimension 5): PASS

`git diff-tree` lists exactly the 9 `allowed_paths` files, nothing else; `package.json`/lockfiles not in the commit (zero new dependencies; `maplibre-gl` pinned at 6.7.0 pre-existing); all forbidden paths untouched. The two placeholder files were replaced with real content (the empty-suite web-e2e breakage is closed by the 10 real tests in `provenance-link.test.ts`). Modularity: exit 0, 0 failures, no touched file in the warning set; `LotOutlineMap.tsx` at 522 lines remains a single-responsibility module (all lot-outline map behavior) with its exports consumed only by its own test.

## Advisory findings (non-blocking)

- **A1 — owner-experience residual on the rule-eval surface:** the new RuleEvaluationResult row is unreachable with live data (ZR citations carry no dataset id), so the owner will still see link-less provenance rows there after deploy; the visible improvement lands in ProvenanceDisclosure (PLUTO facts). If the owner expects clickable sources on ZR citation rows, that is a *different* link class (validated `zoningresolution.planning.nyc.gov` section links) requiring a new directive — surface at the seam (fits the D-056-R006 report).
- **A2 — sticky post-error state (new, narrow):** after a map `error` fires, `mapRenderFailed` can never reset on the same mounted instance: the map-init effect checks `containerRef.current` (null while the error fallback shows) at line 322 *before* `setMapRenderFailed(false)` at line 324, returns early on a later `geometry` change, and never rebuilds a map — the error fallback persists for subsequent BBLs (AddressConfirmCard mounts `<LotOutlineMap bbl=.../>` unkeyed, AddressConfirmCard.tsx:151). Also the errored round's map instance isn't removed until unmount/geometry change (the state flip doesn't run the effect cleanup) — bounded detached-canvas leak. Fails *honest* (typed text + attribution + ZoLa escape hatch), strictly better than the pre-fix silent gray map; recommend a follow-up (add `mapRenderFailed` to the effect deps or key by `bbl`), not rework here.
- **A3 — mock fidelity framing:** the new mock's `on()` drops "load" entirely, so the component-level regression test is a *wiring guard* (bare `on("load")` can never draw under this mock), not a faithful simulation of real `on("load")`-attached-in-time. Fit for its red-on-old purpose; the comments slightly overstate fidelity (can fold into F1's comment corrections).
- **A4 — flake hardening:** the error-event test fires `fireMapError()` right after `findByTestId("lot-outline-map")`; awaiting `waitFor(addSource)` first would make listener registration race-proof.
- **A5 — precision:** ProvenanceDisclosure's invalid-id fallback is text-identical, not byte-identical (inert `data-testid` added) — meets R001's "current text".
- **A6 — executable authority outstanding:** CI `web` + `web-e2e` green at `10aaedcc` is an S4 pre-condition for acceptance (orchestrator-verified; unverifiable read-only here). Static type-read of the new tests (casts, `Record<string, unknown>` provenance access matching the file's existing `source_id` precedent, `vi.fn()` assignability) found no expected tsc/eslint failures.

## Defects

F1 (above) — record/comment accuracy on the R002 root-cause mechanism. No functional defect found in the delivered code.

## Required rework

1. **F1:** amend the producer report's root-cause section, the `runOnStyleReady` ROOT CAUSE comment, and the two test comments to state the reachable mechanism (`load` never fires on a degraded device — the draw step's sole contingency — with the `isStyleLoaded` fast path described as defense-in-depth, not the operative fix at this call site); orchestrator carries the same correction into the evidence-map R002 row. Comment/markdown edits only in already-allowed files; zero behavior change; suitable for the tagged-correction + delta-attestation path.

## Reviewer conclusion

**PASS with required corrections (F1 BLOCKING).** The code is correct, safely structured, and fully in scope: the R001 link surface is structurally incapable of reflecting a server string into an href; the R002 fix (style.load arm + readiness helper + error routing + framing) genuinely closes the reachable cause space for the owner's symptom with a real red-on-old guard; R003 is minimal and correctly placed; display-only discipline and all six fallback branches are preserved; exactly the 9 allowed files changed with zero new dependencies. Acceptance must wait on (a) the F1 record correction and (b) green CI at the reviewed head per S4.

---

**Verdict returned to orchestrator: PASS with required corrections — F1 BLOCKING (record as PASS; F1 + CI-green gate acceptance).**

Key files reviewed (all at pinned sha `10aaedcc`): `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\lib\provenance-link.ts`, `...\apps\web\src\components\address\LotOutlineMap.tsx`, `...\apps\web\src\components\property\ProvenanceDisclosure.tsx`, `...\apps\web\src\components\rule-evaluation\RuleEvaluationResult.tsx`, the three test files, `...\project-control\reports\M5-T025-producer-report.md`, `...\project-control\reports\M5-T025-evidence-map.json`, `...\project-control\tasks\M5-T025.json`, `...\project-control\directives\D-056-provenance-links-lot-outline\requirements.json`.

---

Delta verified. Attestation below.

---

# G3 DELTA-ATTESTATION — M5-T025 (reviewer: code-reviewer, read-only)

**Attestation: F1 DISCHARGED. My G3 PASS verdict CARRIES to `634954162449c4c94b30ff3037ac7b743ef1df73` (and to seam `f5e7f4a1`, whose apps/web tree is byte-identical to `63495416`).**

## Identity-carry proof (reproducible)

```
git diff --stat 10aaedcc..63495416
  -> apps/web delta is EXACTLY 2 files: LotOutlineMap.tsx (36 lines), lot-outline-map.test.tsx (55 lines).
     The other 6 M5-T025 files (provenance-link.ts, its test, ProvenanceDisclosure.tsx,
     RuleEvaluationResult.tsx, sections.test.tsx, rule-evaluation.test.tsx) are ABSENT from the
     delta => byte-identical to my reviewed content.

git diff -U0 10aaedcc..63495416 -- apps/web | grep -E '^[+-]' | grep -v -E '^(\+\+\+|---)' \
  | grep -v -E '^[+-]\s*(\*|//|/\*\*?)'
  -> EMPTY. Every added and removed apps/web line is a comment line ( * / // ). Zero executable
     tokens changed; no test assertion, mock, export, or component code differs.

git log --oneline 10aaedcc..63495416 -- apps/web
  -> 63495416 only (the tagged correction commit). The interleaved peer commits
     (e4c785d3 D-057 capture, 7b2d90a7/554acac3 M5-T026 contract+G0) touch ZERO M5-T025
     reviewed-surface files — disjoint control-plane work, identity-neutral.

git diff --stat 63495416..f5e7f4a1 -- apps/web
  -> empty (seam is ledger/evidence-map bookkeeping only).
```
Therefore every finding in my G3 report — R001 structural link-safety trace (only 2 hrefs, both `datasetLandingUrl`-built; anchored constant-prefix regex; target/rel; honest absence), R002 fix soundness (style.load arm, idempotency, error routing, framing math), R003 NavigationControl wiring, display-only discipline, 9-file scope, `modularity_check --check` exit 0 — holds unchanged at the corrected head. My PASS conclusions were about executable behavior, none of which moved.

## F1 discharge — all four surfaces verified

1. **`LotOutlineMap.tsx:78-99` ROOT CAUSE block** — rewritten to the reachable mechanism I specified: one-time `"load"` requires a completed first visually-complete render and never fires on a degraded-GL device; ZoLa/GL-boot corroboration and the D-056-R004 hardware-acceleration record cited; the attached-too-late race explicitly marked NOT reachable at this call site with the reason (listener attached synchronously with construction); `isStyleLoaded()` labeled defense-in-depth; `"style.load"` arm + error surface named operative; D-056-R006 redeploy retest named as the confirming step. Accurate and complete.
2. **`lot-outline-map.test.tsx`** — header block (l.20-30), already-loaded unit-test comment (l.387-394), and component-regression banner (l.452-462) all corrected identically, with my A3 wiring-guard framing folded in ("a WIRING GUARD, not a faithful simulation of MapLibre's event timing (G3 A3)"). The red-on-old claim is retained and remains true (the new mock's `on()` handles only "error", so old bare-`on("load")` code never draws here).
3. **Producer report** — tagged correction block inserted above the original, which is preserved verbatim under an explicit "superseded as to mechanism" heading. Correct record practice: the false mechanism is no longer asserted, and the audit trail survives.
4. **Evidence-map R002 row** — first bullet replaced with the corrected mechanism, marked `[ORCH-CORRECTED per M5-T025-G3 F1]` and attributing the call-site finding to G3.

No behavior claim in my report is contradicted by the corrected prose, and no new claim was introduced that I have not verified.

## Residual advisories (non-blocking, carry forward from my G3 report)

- **A7 (new, cosmetic):** evidence-map `D-056-R002` bullets 2 and 4 still carry pre-correction phrasing — "categorically closing the race" and "a mock with REAL one-time-event semantics ... could never catch this class". Bullet 1 now governs and explicitly corrects the mechanism, and the test file itself carries the A3 framing, so this is a wording residue, not a false record. Optional tidy at restamp.
- **A2** (sticky `mapRenderFailed` across BBL changes) and **A1** (ZR-citation rows remain link-less in live data — surface at the D-056-R006 seam) stand as follow-ups, unchanged.
- **A6 unchanged and still gating acceptance:** CI was 18/18 green at `10aaedcc`; since the delta is provably comment-only, that run's result transfers logically — but the in-flight run at `63495416` must be green before accept (it is also the guard against a lint rule touching comment content, e.g. line length).

## Verdict carried

**PASS** at `634954162449c4c94b30ff3037ac7b743ef1df73` — F1 discharged, identity-carry established (comment-only delta on the reviewed surface, other six files byte-identical), acceptance gated only on the corrected head's CI run per A6.

Files re-verified this pass: `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\address\LotOutlineMap.tsx`, `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\apps\web\src\components\address\__tests__\lot-outline-map.test.tsx`, `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M5-T025-producer-report.md`, `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M5-T025-evidence-map.json`.
