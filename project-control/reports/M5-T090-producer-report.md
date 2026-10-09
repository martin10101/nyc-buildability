# M5-T090 producer report — admit three@0.186.0 + @react-three/fiber@9.7.0 (D-087 3D-0)

- **Task:** M5-T090 (frontend; gates G0, G2, G4, G5). Producer: frontend-engineer (orchestrator-dispatched subagent).
- **Worktree / branch:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t090` on `task/M5-T090-3d-web-deps`, base `114e5e56e158d6f263e58a314c383ea62ee7eff4`.
- **Directive refs:** D-087-R001/R002/R003/R009/R011, D-066-R001.
- **Evidence status:** `[OBSERVED]` = ran it and saw the output. `[BLOCKED]` = not runnable here, with a harvest recipe. `[PREDICTED]` = worked out, not observed.
- **Requested status:** `awaiting_gate`. The lockfile step (AS-2) and the CI gates (AS-3) follow through the orchestrator.

## IMPLEMENTATION

One file changed: `apps/web/package.json`. Two exact pins were added to `dependencies`, kept in npm's alphabetical order:
line 18 `"@react-three/fiber": "9.7.0"`, line 23 `"three": "0.186.0"`. The only other line change is the
comma JSON needs after `"react-dom": "19.1.2"` (line 22), and that value did not change. No devDependency,
override, script, or other line changed. `drei` and `@types/three` were NOT added (see DISCOVERIES D1).
`apps/web/package-lock.json` was not touched. It must come only from the `generate-lockfile.yml` workflow.

```diff
   "dependencies": {
+    "@react-three/fiber": "9.7.0",
     "maplibre-gl": "6.7.0",
     "next": "15.5.24",
     "react": "19.1.2",
-    "react-dom": "19.1.2"
+    "react-dom": "19.1.2",
+    "three": "0.186.0"
   },
```

**Expected intermediate state:** `npm ci` fails on this commit until the workflow regenerates the lock,
because the committed lock does not list the new pins. That failure is expected for this interim commit.

## Commands run (cwd explicit; no npm/npx/node/pnpm/yarn run anywhere)

| # | cwd | Command | Result |
|---|---|---|---|
| C1 | `wt-m5t090` | `git rev-parse --show-toplevel` / `git rev-parse HEAD` / `git status --short` | `[OBSERVED]` `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t090` / `114e5e56e158d6f263e58a314c383ea62ee7eff4` / clean |
| C2 | scratchpad | `curl -s -D three.hdr -o three.json https://registry.npmjs.org/three` (same for `@react-three%2ffiber`) | `[OBSERVED]` HTTP 200 both; registry `Date: Thu, 24 Sep 2026 09:55:38 GMT` (the policy's clock) |
| C3 | scratchpad | `python inspect.py` / `python history.py` (parse the packuments: time map, dist, maintainers, scripts, deps, peers) | `[OBSERVED]` values in tables A-C |
| C4 | any | `curl -s -X POST https://api.osv.dev/v1/query -d '{"package":{"name":"three","ecosystem":"npm"},"version":"0.186.0"}'` (same for fiber 9.7.0) | `[OBSERVED]` HTTP 200, body `{}` for both |
| C5 | any | `curl -s "https://api.github.com/advisories?ecosystem=npm&affects=three@0.186.0"` (same for `%40react-three%2Ffiber@9.7.0`; plus the package-level queries without a version) | `[OBSERVED]` 0 / 0; package-level: three = 2 old GHSAs, fiber = 0 |
| C6 | `wt-m5t090` | `python tools/code_graph/query.py --no-regen impact apps/web/package.json` | `[OBSERVED]` `STALE (stale fingerprint): refusing to serve the cached graph`. Verified directly instead with Grep `from ['"](three\|@react-three/)` over `apps/web`: **0 matches** (no consumer exists yet) |
| C7 | `wt-m5t090` | JSON-validity + exact-pin + sort check (python one-liner, AS-1 recipe below) | `[OBSERVED]` `valid JSON; non-exact pins: []`, `deps sorted: True` |
| C8 | scratchpad | `python predict.py` (preview of the transitive tree, not authoritative) | `[PREDICTED]` table D |
| C9 | any | jsDelivr file listings `https://data.jsdelivr.com/v1/packages/npm/three@0.186.0?structure=flat` (and fiber 9.7.0) | `[OBSERVED]` three: 1263 files, **0 `.d.ts`**; fiber: ships its own `.d.ts`, and `dist/declarations/src/three-types.d.ts` line 1 = `import type * as THREE from 'three';` |
| C10 | any | `curl -s https://raw.githubusercontent.com/maplibre/maplibre-style-spec/main/src/reference/v8.json` → `paint_fill-extrusion` | `[OBSERVED]` see NECESSITY |

**AS-1 executable check** (cwd `wt-m5t090`):
`python -c "import json,re;p=json.load(open('apps/web/package.json'));d=p['dependencies'];assert d['three']=='0.186.0' and d['@react-three/fiber']=='9.7.0';assert all(re.fullmatch(r'\d+\.\d+\.\d+',v) for s in ('dependencies','devDependencies') for v in p[s].values());print('AS-1 pins OK')"`
Pair it with `git diff 114e5e56 -- apps/web/package.json`. It must show exactly the 3 `+` / 1 `-` lines above.

## A. Per-version registry evidence `[OBSERVED]` (registry `Date` 2026-09-24T09:55:38Z)

| Field | three 0.186.0 | @react-three/fiber 9.7.0 |
|---|---|---|
| Publish time (`time["<ver>"]`) | 2026-09-08T19:25:22.027Z | 2026-07-31T16:20:20.712Z |
| Elapsed s to registry Date | **1 348 215** (15.604 d), ≥ 604800 ✓ | **4 728 917** (54.733 d), ≥ 604800 ✓ |
| dist-tags.latest | 0.186.0 (this version) | 9.8.0 (NOT admitted, see B) |
| dist.integrity | `sha512-cr/fIM2ddMSVbYVgkfD4jLJv7Fh/8ZTjvo+7gQeSVGUZHxpx9FDwoL5iC7hUz/LiRA8wMbqfnb90xKfm1/HHkQ==` | `sha512-EWm9FwcaOZQu/ExFW5rggoCMM1NJet5YbxVxKaOE+KSncrjU0Wx7017qSyGFvupviK89nMYGCWU3BIK4dI1clw==` |
| dist.shasum | `08f70ce80dffa9247a567b421165bec630e86f8d` | `3cb620eafe7ed39540d3ebef4280c7827966c206` |
| dist.tarball | `https://registry.npmjs.org/three/-/three-0.186.0.tgz` | `https://registry.npmjs.org/@react-three/fiber/-/fiber-9.7.0.tgz` |
| Registry signature keyid | `SHA256:DhQ8wR5APBvFHLF/+Tc+AYvPOdTpcIDqOhxsBHRwC7U` | same keyid |
| Provenance attestation | none | none |
| Publisher (`_npmUser`) | `mrdoob` | `krispyaa` (also published 9.5.0, 9.6.0, 9.8.0) |
| Maintainers | package now: `mrdoob`, `mugen87`; the same 2 at this version and at every release since 0.182.0 | package now (8): `bela-bohlender`, `dennissmolek`, `drcmda`, `farazshaikh`, `gsimone`, `isaacmason`, `krispyaa`, `tdfka_rick`. At 9.7.0: 22 names. **Change flagged in C.** |
| Install scripts (pre/install/post, prepare) | **none**; `hasInstallScript` absent; no `gypfile` | **none** (the only script is `prebuild`, which does not run for a consumer) |
| Licence | MIT | MIT |
| dependencies | **none (0)** | 10: `buffer ^6.0.3`, `zustand ^5.0.3`, `its-fine ^2.0.0`, `base64-js ^1.5.1`, `scheduler ^0.27.0`, `@types/webxr *`, `suspend-react ^0.1.3`, `@babel/runtime ^7.17.8`, `react-use-measure ^2.1.7`, `use-sync-external-store ^1.4.0` |
| peerDependencies | none | `react >=19 <19.3`, `react-dom >=19 <19.3` (optional), `three >=0.156`, plus the optional `expo`, `expo-gl`, `expo-asset`, `expo-file-system`, `react-native` |
| Repository | `git+https://github.com/mrdoob/three.js.git` | `git+https://github.com/pmndrs/react-three-fiber.git` |
| Deprecated | no | no |
| Size | 1263 files, 20 443 175 B unpacked | 37 files, 2 188 429 B unpacked |

These values match the M5-T084 pre-screen's integrity strings and publish times.

## B. Newest-eligible check (re-verified at admission) `[OBSERVED]`

- **three:** no version was published after 0.186.0. 0.186.0 is the newest release, and it passes.
- **fiber stable line:** 9.6.1 (2026-04-28) → **9.7.0** (2026-07-31, PASS) → **9.8.0 published 2026-09-22T19:43:58.526Z, elapsed 137 499 s = FAIL** (it would pass at 2026-09-29T19:43:58.526Z).
  So 9.7.0 is the newest stable version that passes today. Many `10.0.0-canary.*` and `10.0.0-alpha.*` builds are older than 7 days, but pre-releases are not eligible.

## C. Maintainer / ownership change on @react-three/fiber — FLAG for the G5 reviewer `[OBSERVED]`

- At 9.6.1 (2026-04-28) the version-level maintainers were 23. At 9.7.0 (2026-07-31) there were 22: `codyjasonbennett`, who published 9.4.x and 9.6.1, was gone.
- At 9.8.0 (2026-09-22) there are **8**. Fifteen accounts were removed: `alaric.baraou`, `bjornstar`, `codynova`, `dropthebeatbro`, `giulioz`, `iinfin`, `joergjaeckel`, `marcofugaro`, `mlperego`, `nksaraf`, `sniok`, `stephencorwin`, `stockhuman`, `unframework`, `wiledal`. **One account was added: `dennissmolek`.**
- **Reading:** npm cannot republish an existing version, so the 9.7.0 tarball is fixed by its integrity hash. Seven of the 8 current maintainers were already maintainers at 9.7.0; `dennissmolek` was added later. The change matters for **future** fiber upgrades, which would come from the new 8-person set with the new `dennissmolek` account.
  I cannot tell from registry data whether this was a planned cleanup or an account compromise. That is the G5 reviewer's call.
- three: no maintainer change (the same 2 maintainers since at least 0.182.0; `mugen87` published 0.183.2, `mrdoob` the rest).

## D. Preview of the resolved tree `[PREDICTED]` — the generated lock is authoritative

`predict.py` resolves each range to the highest stable version that is at least 604800 s old, and reuses a version already in the current lock when it fits.
Predicted **13 new packages**: `three@0.186.0`, `@react-three/fiber@9.7.0`, `buffer@6.0.3`, `base64-js@1.5.1`, `ieee754@1.2.1` (**BSD-3-Clause**), `zustand@5.0.15`, `its-fine@2.0.0`, `@types/react-reconciler@0.28.9`, `scheduler@0.27.0` (installed nested: react-dom 19.1.2 needs `scheduler ^0.26.0`, and the lock has 0.26.0), `@types/webxr@0.5.24`, `suspend-react@0.1.3`, `react-use-measure@2.1.7`, `use-sync-external-store@1.7.0`.
`@babel/runtime` reuses the existing 7.29.7. All predicted packages are MIT except `ieee754` (BSD-3-Clause). None declares install scripts. Every required peer is `react`, `@types/react`, or `three`, and each is satisfied at the root.
The youngest predicted packages are `use-sync-external-store@1.7.0` (1 269 753 s ≈ 14.7 d) and `three`. None is near the 7-day floor.
**The G5 section-5 review (AS-4) must run on the generated lock, not on this preview.** `npm install --package-lock-only` may resolve differently, for example if a version ages past 7 days before the run.

## E. Advisory queries `[OBSERVED]` (2026-09-24 ~09:57Z)

| Query | three 0.186.0 | @react-three/fiber 9.7.0 |
|---|---|---|
| OSV `POST /v1/query` (version-specific) | HTTP 200, `{}`: **0** | HTTP 200, `{}`: **0** |
| GitHub advisory DB `affects=<pkg>@<ver>` | **0** | **0** |
| GitHub advisory DB, package-level (all versions) | 2: `GHSA-7vvq-7r29-5vg3` (high, `< 0.137.0`), `GHSA-fq6p-x6j3-cmmq` (high, `< 0.125.0`). Both fixed long before 0.186.0 | **0** |

**Positive control (to show an empty result is real, not an outage):** OSV for `three@0.124.0` returns `GHSA-fq6p-x6j3-cmmq`.
OSV does not return `GHSA-7vvq` for 0.124.0 or 0.136.0. The reason: OSV's record shows `withdrawn: 2022-01-28T18:32:01Z`, so OSV rightly drops it.
These are top-level checks only. The whole-tree advisory proof is AS-3: CI `npm audit --audit-level=low` plus a JSON total of 0 on the generated lock.

## F. Peer-range fit `[OBSERVED]` against `apps/web/package.json`

| fiber 9.7.0 peer | Range | apps/web | Fits? |
|---|---|---|---|
| react | `>=19 <19.3` | 19.1.2 | **yes** |
| react-dom (optional) | `>=19 <19.3` | 19.1.2 | **yes** |
| three | `>=0.156` | 0.186.0 (this commit) | **yes** |
| expo / expo-gl / expo-asset / expo-file-system / react-native | various | absent | all optional: npm will not install them |

Watch item: the `<19.3` cap means a later React 19.3 upgrade would break fiber 9.7.0's peer range. See D3.

## NECESSITY — why parcel-level 3D needs this stack rather than the zero-dependency MapLibre fill-extrusion (policy §5; D-087-R009 "zero-dependency preferred")

The required interactions come from `docs/3D_MASSING_ENGINE_ARCHITECTURE.md` §7 (lines ~309-345). Camera needs reset, fit property, fit selected object, isometric, top plan, front/side presets, and smooth transitions. Selection needs hover, click, Escape, and sync between the 3D view, the floor stack, and the evidence panel. Floor inspection needs a floor slider, **cutaway**, exploded stack, and **isolate floor**. Scenario comparison needs a **ghost overlay**. Delivery is **GLB** (`GET /api/v1/scenarios/{id}/model.glb`, lines 384-390).
MapLibre fill-extrusion falls short in these verified ways (style spec `v8.json`, `paint_fill-extrusion`, C10):

1. **Geometry: vertical prisms only.** The only geometry controls are `fill-extrusion-base` and `fill-extrusion-height`, one number each per feature. A 2D polygon becomes a flat-topped prism. The R6-R10 sky-exposure planes (ZR 23-73x, slopes 2.7/5.6) and sloped setback planes are non-prismatic. Fill-extrusion could only draw them as staircase approximations, which would misstate a legally derived envelope. Project rule 9 says "no shape is accepted without a calculation and provenance trace", so an approximated shape is not acceptable. Three.js renders the server's exact triangle geometry.
2. **Materials and ghosting.** `fill-extrusion-opacity` is **`data-constant`**, one opacity for the whole layer. Ghost overlays (max envelope vs proposal), translucent context, and "isolate floor with the rest ghosted" need per-object opacity, so they would take a stack of workaround layers. There are no clipping planes (so no cutaway or section), no per-face materials, and no edge outlines. Colour and height can vary by feature and `feature-state`.
3. **GLB viewing.** MapLibre has no glTF loader. MapLibre's own examples for 3D models (`/docs/examples/add-a-3d-model-using-threejs/`, `…-with-shadow-using-threejs/`, `…-on-terrain/`) all load the model with **three.js `GLTFLoader` inside a `CustomLayerInterface`**. The page imports `three@0.169.0`. So even the map-first route needs `three` to view the architecture's GLB. Staying zero-dependency would mean writing a glTF parser and WebGL renderer by hand, which rule 6 forbids ("do not build WebGL or a general rendering engine from scratch").
4. **Camera.** The map camera is centre/zoom/pitch/bearing over Web Mercator. The viewer needs object-framing presets ("fit selected object", top plan, front/side elevation) in a site-local frame, and measurement of height, distance, and area. Three.js cameras and raycasting cover these directly.

**What fill-extrusion CAN do, stated fairly:** simple prismatic block massing on the existing map, per-feature colour and height, and click-picking through `queryRenderedFeatures` with `feature-state` highlight. Per-floor stacking of prismatic floors is possible with base/height offsets. The zero-dependency route should stay the choice for **map-context massing**. This admission is for the parcel-level viewer only.

**Why fiber on top of three (fiber adds about 11 new transitive packages, table D):** plain `three` with a hand-written `useEffect` wrapper is the smaller-dependency option, and the G5 reviewer may weigh it.
The case for fiber: selection has to stay in sync between the 3D view, the floor stack, and the evidence panel, which is React state. Fiber gives a React-managed scene graph with per-object pointer events, so there is no hand-built raycast dispatcher. It frees GPU resources when components unmount. It loads GLB through Suspense. The project rule `.claude/rules/3d-ui-expansion.md` item 5 names "Three.js + React Three Fiber + Drei", and the owner's D-087-R011 names three.js + @react-three/fiber.
Drei is deferred, as the packet says: it has 21 direct dependencies, the largest fan-out.

## Directive mapping

- **D-087-R001/R002:** worked only in my isolated worktree, inside allowed_paths (`apps/web/package.json` and this report). No shared files.
- **D-087-R003:** this admits the 3D stack that the released 3D building-and-lot work needs. No component code, as scoped.
- **D-087-R009:** all dependency-security rules still apply: exact pins, 7-day age (A/B), zero advisories (E), G5 review pending, lock generated only by the workflow, zero-dependency argued (NECESSITY). No local npm.
- **D-087-R011:** the owner's "Go" admits exactly three.js + fiber at the ≥7-day versions the pre-screen names (0.186.0 / 9.7.0), re-verified here. It waives nothing.
- **D-066-R001:** ran the code-graph `impact` query (C6). It refused as STALE, so I checked in source: 0 consumers.

## Acceptance scenarios

- **AS-1 (pins):** `[OBSERVED]` the diff above, check C7, publish times ≥ 604800 s (table A).
- **AS-2 (lock):** `[BLOCKED]` (not mine by design). Recipe: the orchestrator dispatches `.github/workflows/generate-lockfile.yml` (`workflow_dispatch`, pinned `npm@11.18.0`, `npm install --package-lock-only --no-audit --no-fund`) on the pushed branch and cites the run id. Then check that `packages["node_modules/three"].version == "0.186.0"` and `packages["node_modules/@react-three/fiber"].version == "9.7.0"`, and that their `integrity` equals the strings in table A.
- **AS-3 (whole-tree gates):** `[BLOCKED]`. The CI `web-dependency-security` job on the head after the lockfile commit must pass: `dependency_age_gate.mjs` whole-tree, `npm audit` total 0, and the npm CLI advisory check.
- **AS-4 (provenance):** `[BLOCKED]`. Needs the G5 reviewer, who is not me. Inputs are A, B, C (the maintainer flag), D (preview only), E, and NECESSITY.
- **Human walkthrough / Playwright:** not applicable. This packet adds no UI (`apps/web/src/` and `apps/web/e2e/` are forbidden paths), so there is no user journey to walk. The first journey belongs to the later 3D viewer packet.

## Deviations

- None from the packet scope.
- The `react-dom` line gained the trailing comma that JSON requires. Its value did not change.

## DISCOVERIES (D-069 routing; nothing fixed in this packet)

- **D1: `@types/three` will be needed by the first consumer.** `three@0.186.0` ships **no** type declarations: 0 `.d.ts`, and its package.json has no `types` field or types exports condition. Fiber's own `.d.ts` files `import type * as THREE from 'three'`.
  With no consumer, `tsc --noEmit` is unaffected today. At the first `import … from 'three'`, strict mode raises TS7016. With `skipLibCheck: true`, fiber's `THREE` types silently become `any`.
  Candidate: `@types/three@0.186.0` (published 2026-09-11T18:07:29.669Z, ≈ 1 093 970 s at registry Date 10:00:20Z, passes; integrity `sha512-mxYSBpDC+D0pLfSP6sW4WZTcT+nrtmZcimMqnVmy36Hte3XpeYSrvgg4TRdaM1GemGog1AWzI5qL2VoIfMXbJQ==`).
  **Caution:** it brings 6 runtime dependencies (`@dimforge/rapier3d-compat ~0.12.0`, a WASM physics engine; `@tweenjs/tween.js ~23.1.3`; `meshoptimizer ~1.1.1`; `fflate ~0.8.3`; `@types/stats.js *`; `@types/webxr >=0.5.17`), so it needs its own G5 admission. It could go in `devDependencies`. Not added, per the dispatch.
- **D2: fiber maintainer-set change** (section C): pruned from 22 to 8 with one new account between 2026-07-31 and 2026-09-22. It does not change the fixed 9.7.0 tarball. Recheck before any fiber upgrade, including 9.8.0.
- **D3: React upgrade coupling.** fiber 9.7.0 peers `react`/`react-dom` `<19.3`. Any later React bump to 19.3 or higher must bump fiber together, or `npm` will refuse the peer conflict.
- **D4: `@types/webxr` has the range `*` in fiber's runtime dependencies.** Each lock regeneration picks up the newest `@types/webxr` that is at least 7 days old. The age and advisory gates cover this; noted for the reviewers.
- **D5: code-graph cache is STALE** in this worktree at `114e5e56` (C6). Advisory tool only. Noted in case the orchestrator wants to regenerate it.

END-OF-REPORT
