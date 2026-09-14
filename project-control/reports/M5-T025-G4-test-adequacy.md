<!-- Reviewer returns preserved VERBATIM by the orchestrator (report-preservation rule; transport entity-decoding only). Part 1: the pinned-head review at 10aaedcc. Part 2: the F1 delta / identity-carry attestation at 63495416. -->

# G4 TEST-ADEQUACY GATE REPORT — M5-T025 (D-056 web-fix packet)

**Reviewer:** qa-engineer (independent, read-only; producer ≠ reviewer)
**Reviewed SHA (pinned):** `10aaedccb80b3954f03d7bc1b504807ec8fb21c1` — my checkout HEAD is `d8b3899f`, so ALL content was reviewed via `git show 10aaedcc:<path>`; old baselines via `git show 3d99c92a:<path>` (contract head).
**Baseline integrity check:** `git log -1 10aaedcc` → parent `9a2607e8`; `git diff 3d99c92a..9a2607e8` over all 8 code files is **empty**, so the contract-head baselines are exactly the pre-change state and the material change is exactly this commit's diff (9 files, all inside `allowed_paths`; package.json/lockfiles untouched — S4 scope holds at the commit level).
**Execution constraint:** no `node_modules` on this machine — vitest was not run by me; this is a static adequacy review with paper mutation analysis. CI `web` + `web-e2e` at the pushed head is the executable authority (the packet's own `documented_test_commands`).

## 1. S1 — safe source links (D-056-R001)

**Exact-href pinning:** YES, in all three layers.
- Lib (`apps/web/src/lib/__tests__/provenance-link.test.ts`): `datasetLandingUrl("64uk-42ks")` pinned to the **literal** `"https://data.cityofnewyork.us/d/64uk-42ks"` (not only the self-referential `${DATASET_LANDING_PREFIX}...` form), and `DATASET_LANDING_PREFIX` itself pinned to the literal `"https://data.cityofnewyork.us/d/"` — so a prefix/host mutation cannot hide behind self-reference.
- `sections.test.tsx` ("valid dataset_id…"): anchor `href` pinned to the exact literal, plus `target="_blank"`, `rel="noopener noreferrer"`, and link text = id.
- `rule-evaluation.test.tsx` ("valid dataset_id…"): same exact-literal pinning on `rule-eval-source-link`.

**Hostile request_url negative, BOTH surfaces:** YES. Each surface's NEGATIVE test injects `https://evil.example.com/steal?x=<script>alert(1)</script>` as `request_url` and then scans **every `<a>` in the rendered container** asserting no href contains `evil.example.com`, then re-pins the valid link's exact href. The all-anchors scan means a mutation that turns *any* row (including "Retrieved from", currently `urlHost(...)` text-only — `RuleEvaluationResult.tsx:163-166`, `ProvenanceDisclosure.tsx` dd) into an href from `request_url` is caught, not just the dataset-id row.

**Mutation table (all caught):**
| Mutation | Killing test |
|---|---|
| Drop/loosen regex; href from raw dataset_id | lib "rejects uppercase/wrong length/…", both surfaces' "invalid dataset_id: honest text, no anchor" (`queryByTestId(...)` → null fails when an anchor renders) |
| Un-anchor regex | lib substring tests (`x64uk-42ks`, `prefix/64uk-42ks`, `"64uk-42ks\n"` — correct in JS `$` semantics, and guards a port to `$`-lenient semantics) |
| Swap `request_url` in as href | exact-literal href assertions + both all-anchors scans |
| Change prefix/host | literal prefix + literal URL assertions |
| Drop `target`/`rel` | valid-case attribute assertions, both surfaces |
| Link on invalid id | invalid-case null-anchor assertions, both surfaces |

Absent-id cases covered in both surfaces (`sections.test.tsx` "absent reproducibility: no row"; `rule-evaluation.test.tsx` "absent dataset_id … no row" — the fixture's natural, real-data shape; `draftApplicableDoc()` `structuredClone`s per call, so cross-test mutation pollution is excluded — `test-support/rule-evaluation-fixtures.ts:22`). The producer's disclosure that the RuleEvaluationResult row is currently unreachable with live ZR data is candid and correctly test-exercised via fixture mutation; the intent question is G3's, and the R001 required harness is satisfied as written.

## 2. S2 — regression guard (D-056-R002)

Verified against the OLD code at `3d99c92a`: `LotOutlineMap.tsx:262` `map.on("load", () => {…})` with **no** `isStyleLoaded()` check, **no** `error` handler, `:286` `maxZoom: 18`; old test mock `:28-29` `on("load", cb)` → unconditional `queueMicrotask(cb)` — the old mock structurally could never express "event already fired," confirming the producer's claim.

**Would the new tests really fail against the old component?** Yes, in three layers:
1. Trivially: old code doesn't export `runOnStyleReady`/`LOT_OUTLINE_MAX_ZOOM`/`lotOutlineFitBoundsOptions` → the new test file fails at import.
2. Mock-semantics: the new mock's `on()` records only `"error"`; the old `on("load", draw)` wiring never draws → S1/S2/hole tests time out on `waitFor(addSource)`.
3. **The discriminating behavioral case** (the load-bearing one): a hypothetical revert that keeps the exports but wires `once("load", draw)` *without* the readiness check would pass the default-path tests (the mock queues `"load"` when not-already-loaded) but **fails** "draws the outline even when the style is ALREADY loaded before wiring attaches" (`setStyleAlreadyLoaded(true)` → mock `once()` correctly no-ops → `addSource` never called). This is a genuine red-on-old guard, not theater.

**Mutation table (all caught):**
| Mutation | Killing test |
|---|---|
| Remove `isStyleLoaded()` fast path | unit test 1 (`draw` must be sync AND `once` must NOT be called) + the component already-loaded test |
| Remove idempotency guard | unit test 2 (both events fire → `toHaveBeenCalledTimes(1)`) |
| Arm `"load"` only | unit test 3 (`style.load`-only firing) |
| Remove `map.on("error", …)` | error test (`findByTestId("lot-outline-render-error")` times out; `fireMapError` iterates an empty listener list) |
| Route error to the webgl branch | error test (distinct testid) + untouched webgl test |
| Revert `LOT_OUTLINE_MAX_ZOOM` to 18 | `lotOutlineFitBoundsOptions` test — `toBeGreaterThan(18)` is the absolute pin backing the self-referential `toBe(LOT_OUTLINE_MAX_ZOOM)` |
| Inline `maxZoom: 18` bypassing the helper | S1 `fitBounds` `objectContaining({ maxZoom: LOT_OUTLINE_MAX_ZOOM })` with the constant at 19.5 |
| Recompute/simplify geometry | S1/S2/hole `toEqual(fx.geometry)` verbatim assertions |

Root-cause narrative vs code is coherent (missed one-time `"load"` → background paints, attribution is construction-time DOM, draw gated solely behind the listener = exactly gray-canvas+attribution+no-outline). The live owner-device trigger is honestly disclosed as non-reproducible here; final confirmation is the owner Manual Deploy re-test (D-056-R006, out of scope).

## 3. Fallback preservation

Deleted lines in the component diff are exactly 5 (old `outcomeSummary` signature, `on("load")`, old fitBounds options, old summary call, `drawable ? (` → `drawable && !mapRenderFailed ? (`). All pre-existing typed fallback branch copy/testids are byte-unchanged. All seven pre-existing fallback tests preserved verbatim and still meaningful: condo, no_feature, multiple_features, invalid_geometry, route_absent 404, network failure, webgl-unavailable (incl. the summary-matches-visible-fallback assertions). The NEW render-error fallback is tested: map renders → `fireMapError()` → `lot-outline-render-error` appears, map container gone, ±20 ft copy + attribution retained, summary contains "could not be rendered".

## 4. Gaps / theater scan

- **No theater found.** Every test asserts observable behavior; the two self-referential constant assertions are each backed by an absolute pin (literal prefix string; `>18`).
- **Advisory NB-1 (non-blocking):** the `single_lot` + `geometryUnusable` branch (`lot-outline-unavailable`, "not a usable shape") has no test in either the old or new file. Pre-existing gap on a byte-unchanged branch, and it is NOT in S3's enumerated must-stay-green list — suggest a follow-up test, not a correction to this packet.
- **Advisory NB-2 (non-blocking, G3-adjacent):** when `mapRenderFailed` flips, the map container unmounts but the effect (deps `[geometry]`) doesn't clean up, so the constructed map isn't `remove()`d until unmount — a transient detached-map instance. Minor; no test covers post-error re-render. Candidate follow-up, not a defect in what D-056 ordered.
- **Accepted, disclosed limits:** NavigationControl keyboard accessibility rests on MapLibre's native `<button>`s (S3's stated basis is "vitest + code review" — the ctor/`"top-right"`/`showCompass:false` wiring IS asserted, and a construct-but-never-add mutation is caught since attribution sits at `"bottom-right"`); jsdom cannot prove real-browser drawing.

## Verdict: **PASS**

No blocking findings (zero F-items). The test pack is adequate against every S1–S4 requirement expressible in this harness, the red-on-old claim is mechanically verified at the contract head, and the paper mutation analysis kills every named mutation. Standard fail-closed condition for the record (packet's own authority, not a producer correction): the orchestrator must confirm CI `web` + `web-e2e` green at `10aaedcc` before recording G4/acceptance — if CI fails, this verdict does not stand in for execution.

**Key files:** `C:\...\apps\web\src\lib\provenance-link.ts`, `apps\web\src\lib\__tests__\provenance-link.test.ts`, `apps\web\src\components\address\LotOutlineMap.tsx`, `apps\web\src\components\address\__tests__\lot-outline-map.test.tsx`, `apps\web\src\components\property\__tests__\sections.test.tsx`, `apps\web\src\components\rule-evaluation\__tests__\rule-evaluation.test.tsx`, `project-control\reports\M5-T025-producer-report.md` (all reviewed at the pinned sha via `git show`).

---

# G4 IDENTITY-CARRY ATTESTATION — M5-T025 (qa-engineer, read-only)

**CONFIRMED: my G4 PASS carries from `10aaedcc` to `634954162449c4c94b30ff3037ac7b743ef1df73`.** I did not take the comment-only claim on description — I proved it mechanically.

## Evidence (commands + outputs)

**1. Code-only identity of the two edited files in my surface.** Dumped both revisions of each file and compared with a string-literal-aware comment stripper (`scratchpad/strip_comments.py`; strips `//` and `/* */` while respecting `'`/`"`/`` ` `` literals, so a `//` inside a URL string can't skew it):

```
LotOutlineMap.tsx      OLD 8a285bec854da678ce245821fbeff0a37acf513da8c587987dba6af866f69896  lines=364
                       NEW 8a285bec854da678ce245821fbeff0a37acf513da8c587987dba6af866f69896  lines=364
                       RESULT: CODE-ONLY CONTENT IDENTICAL (difference is comments only)

lot-outline-map.test.tsx OLD 6611ff71b8e5d4eef58ba4f2c36a2479646730d3402ac695e116b4bba665a8aa  lines=394
                         NEW 6611ff71b8e5d4eef58ba4f2c36a2479646730d3402ac695e116b4bba665a8aa  lines=394
                         RESULT: CODE-ONLY CONTENT IDENTICAL (difference is comments only)
```

Byte-identical code-only digests. This also rules out the one pathological way a "comment-only" edit can bite — an unterminated block or accidentally commented-out code: zero executable lines moved, zero `expect()` added/removed/altered, mock semantics (`once`/`on`/`isStyleLoaded`/`styleAlreadyLoaded`) untouched.

**2. Rest of my reviewed surface untouched.** `git diff --stat 10aaedcc 63495416 -- provenance-link.ts provenance-link.test.ts ProvenanceDisclosure.tsx sections.test.tsx RuleEvaluationResult.tsx rule-evaluation.test.tsx` → **empty**. The only apps/web files in the whole range are the two above; everything else in the range is disjoint control-plane work (D-057, M5-T026, state/index) outside my gate surface.

**3. Every killing test in my mutation table is assertion-level and unmodified** — all 4 S1 rows (exact-literal hrefs, `target`/`rel`, null-anchor on invalid, all-anchors `evil.example.com` scans), all 8 S2 rows (`isStyleLoaded` fast path, idempotency guard, `style.load`-only, error handler, error-vs-webgl testid, `toBeGreaterThan(18)`, `objectContaining({maxZoom})`, verbatim `toEqual(fx.geometry)`), and the fallback-preservation rows. None sits in a changed line.

**4. CI-lint sanity on comment-only edits** (the real risk with prose changes): `apps/web/eslint.config.mjs` extends only `next/core-web-vitals` + `next/typescript` — **no `max-len`, no prettier/format step** in the `web` job (`ci.yml:48` lint → `:50` typecheck → build; `:94` vitest). Reflowed comments cannot fail lint or `tsc` here.

**5. My PASS condition is discharged.** The CI gate I attached to the verdict was green at the reviewed sha (18/18 incl. web + web-e2e, orchestrator-captured — I cannot run `gh`). Given proof 1, the in-flight run at `63495416` cannot change any test outcome; recording acceptance on it is a formality, not a new risk.

## On the G3 F1 correction itself (my domain)

The corrected mechanism **does not weaken** test adequacy, and on one point strengthens my original framing: under the corrected reading the *operative* fix is the `"style.load"` arm, and that has its own dedicated killing test — `runOnStyleReady` unit test 3 ("only 'style.load' fires: draw() still runs"), which kills an arm-`"load"`-only mutation independently of the `isStyleLoaded()` path. The `isStyleLoaded()` rows remain valid as defense-in-depth guards (they still kill their mutation), and the corrected comments now label them accurately rather than overclaiming. The producer report's original text is preserved verbatim beneath the tagged correction, as stated.

**Advisory NB-3 (new, non-blocking, no correction requested):** the operative fix's call-site wiring is proven as a *two-link chain* rather than one end-to-end row — the component-level regression test drives the `isStyleLoaded()` path, and the mock's `once()` only ever queues `"load"`, never `"style.load"`. No mutation survives the pair (bypassing `runOnStyleReady` at the call site → component already-loaded test red; dropping the `style.load` arm → unit test 3 red), so adequacy holds. A future one-line mock capability (`if (type === "style.load") queueMicrotask(cb)` under a flag) plus one component row would give the operative fix a direct end-to-end guard. Suggest as follow-up, not as a change to this packet.

**Verdict unchanged: G4 PASS at `634954162449c4c94b30ff3037ac7b743ef1df73`** (carried from `10aaedcc`; zero blocking findings; advisories NB-1 geometryUnusable-branch test gap, NB-2 map cleanup on render-error, NB-3 above all remain follow-up candidates).

Files: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\agent-a0f90fddd03a10c2a\.claude\agent-memory\qa-engineer\project_static-mutation-review-thin-client.md` (method note, incl. the identity-carry proof recipe); verification script at `C:\Users\MLFLL\AppData\Local\Temp\claude\C--Users-MLFLL-Downloads-nyc-zoning-ctl24\ecc0388e-9976-4c9f-b7f6-38068f48b69f\scratchpad\strip_comments.py`. Nothing written outside my memory dir and the scratchpad.
