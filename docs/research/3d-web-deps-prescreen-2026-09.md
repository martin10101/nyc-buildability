# 3D web-dependency provenance pre-screen (M5-T084, D-087)

- **Task:** M5-T084 (research-only; D-087 wave 1). Producer: official-source-researcher.
- **Purpose:** provide the provenance inputs for a **later G5 admission packet** should the released
  3D building-and-lot massing work adopt a web 3D stack. **No package, `package.json`, or lockfile
  change is made here** (AS-4). This note does not admit anything; it records what an admission packet
  must satisfy under `docs/DEPENDENCY_SECURITY_POLICY.md`.
- **Sources (official/primary only):**
  - npm registry JSON `https://registry.npmjs.org/<pkg>` — for `time` (publish timestamps, UTC),
    `dist-tags.latest`, per-version `license`, `dependencies`, `peerDependencies`, `scripts`, and
    `dist.integrity`. Retrieved **2026-09-24T07:30:32Z**.
  - Advisory data: **OSV.dev** batch query `https://api.osv.dev/v1/querybatch` (aggregates the GitHub
    Advisory Database / GHSA), retrieved **2026-09-24T07:32:51Z**; cross-checked against the **GitHub
    Advisory Database REST API** `https://api.github.com/advisories?ecosystem=npm&affects=<pkg>[@ver]`,
    retrieved 2026-09-24 ~07:33Z. Positive control: OSV returned 7 GHSAs for `lodash@4.17.11`,
    confirming the endpoint returns real findings (so the empty results below are genuine, not an
    outage — matching the policy's fail-closed intent).
- **Age gate:** policy = "≥ 7 complete days old, **604800 s passes, 604799 s fails**." At the retrieval
  instant the cutoff is publish-time **≤ 2026-09-17T07:30:32Z**. "Newest ≥7-day-old version" = the
  highest stable (non-prerelease) version whose registry publish time is at/under that cutoff.

---

## 0. Headline (per package)

| Package | Registry latest (age) | **Newest ≥7-day-old stable** (use this) | Publish time (UTC) | Age at retrieval | License | Lifecycle install scripts | Direct deps | Advisories on that version |
|---|---|---|---|---|---|---|---|---|
| **three** | 0.186.0 (15.50 d) | **0.186.0** (latest already qualifies) | 2026-09-08T19:25:22Z | 15.50 d ✓ | MIT | **none** | **0** | **none** |
| **@react-three/fiber** | 9.8.0 (**1.49 d — FAILS gate**) | **9.7.0** | 2026-07-31T16:20:20Z | 54.63 d ✓ | MIT | none (only a `prebuild`) | 10 | none |
| **@react-three/drei** | 10.7.8 (49.69 d) | **10.7.8** (latest already qualifies) | 2026-08-05T14:57:28Z | 49.69 d ✓ | MIT | none | 21 | none |

Every "use this" version is MIT-licensed, runs **no** `preinstall`/`install`/`postinstall` script,
resolves from the official registry, and is advisory-free **at the top level**. The only current
age-gate failure is `@react-three/fiber@9.8.0` (published 2026-09-22, 1.49 days old) → an admission
packet built today must pin **9.7.0**, or wait until 9.8.0 crosses 604800 s (≈ 2026-09-29T19:43Z).

---

## 1. three — `https://registry.npmjs.org/three`

- **Version to admit:** **0.186.0** (also `dist-tags.latest`), published **2026-09-08T19:25:22.027Z**,
  age **15.50 d** ✓ (≥ 604800 s). `dist.integrity` =
  `sha512-cr/fIM2ddMSVbYVgkfD4jLJv7Fh/8ZTjvo+7gQeSVGUZHxpx9FDwoL5iC7hUz/LiRA8wMbqfnb90xKfm1/HHkQ==`.
- **License:** MIT. **Package maintainers:** 2 (`mrdoob`, `mugen87`).
- **Dependencies:** **0 runtime dependencies, 0 peerDependencies** — `three` is a self-contained leaf.
  This is the cleanest supply-chain profile of the three (no transitive tree at all).
- **Lifecycle scripts:** none of `preinstall`/`install`/`postinstall` (only dev `build`/`test`/`lint`
  scripts, which do not run on `npm ci` of a consumer).
- **Advisories:** OSV `three@0.186.0` → empty. GitHub advisory DB lists 2 GHSAs for the `three`
  *package* — `GHSA-7vvq-7r29-5vg3` (XSS, vulnerable range **< 0.137.0**) and `GHSA-fq6p-x6j3-cmmq`
  (DoS, vulnerable range **< 0.125.0**) — both patched far below 0.186.0; the version-filtered query
  `affects=three@0.186.0` returns **0**. → **advisory-free** for 0.186.0.

## 2. @react-three/fiber — `https://registry.npmjs.org/@react-three/fiber`

- **Version to admit:** **9.7.0** (NOT the latest — 9.8.0 is only 1.49 days old and FAILS the age
  gate). 9.7.0 published **2026-07-31T16:20:20.712Z**, age **54.63 d** ✓. `dist.integrity` =
  `sha512-EWm9FwcaOZQu/ExFW5rggoCMM1NJet5YbxVxKaOE+KSncrjU0Wx7017qSyGFvupviK89nMYGCWU3BIK4dI1clw==`.
- **License:** MIT. **Package maintainers:** 8 (`gsimone`, `drcmda`, `tdfka_rick`, `farazshaikh`,
  `isaacmason`, `bela-bohlender`, `dennissmolek`, `krispyaa`).
- **Lifecycle scripts:** none of preinstall/install/postinstall (only a `prebuild`).
- **Direct dependencies (10):** `@babel/runtime`, `@types/webxr`, `base64-js`, `buffer`, `its-fine`,
  `react-use-measure`, `scheduler`, `suspend-react`, `use-sync-external-store`, `zustand`.
- **peerDependencies (8):** `react`, `react-dom`, `three`, plus optional React-Native/Expo peers
  (`expo`, `expo-asset`, `expo-file-system`, `expo-gl`, `react-native`) — the RN/Expo peers are
  irrelevant to a web build. **Compatibility flag for the admission packet:** fiber 9.x targets the
  React 19 line and peers on `three` — the web app's pinned React and `three` (0.186.0) must satisfy
  these peers.
- **Advisories:** OSV `@react-three/fiber@9.7.0` → empty; GitHub advisory DB `affects=@react-three/fiber`
  → **0**. → advisory-free at top level.

## 3. @react-three/drei — `https://registry.npmjs.org/@react-three/drei`

- **Version to admit:** **10.7.8** (also `dist-tags.latest`), published **2026-08-05T14:57:28.145Z**,
  age **49.69 d** ✓. `dist.integrity` =
  `sha512-rJXyuzLm2Xq0kafHuR47ajDGbOe/pEhzIr4m8E8zwzQs0iNjloFDqBwRhrXmP/w+onLeYyN3EYPFW/cwWK/4yA==`.
- **License:** MIT. **Package maintainers:** 6 (`gsimone`, `drcmda`, `tdfka_rick`, `krispyaa`,
  `giulioz`, `stephencorwin`).
- **Lifecycle scripts:** none (no scripts block at all in the version manifest).
- **Direct dependencies (21):** `@babel/runtime`, `@mediapipe/tasks-vision` (pinned `0.10.17`),
  `@monogrid/gainmap-js`, `@use-gesture/react`, `camera-controls`, `cross-env`, `detect-gpu`,
  `glsl-noise`, `hls.js`, `maath`, `meshline`, `stats-gl`, `stats.js`, `suspend-react`, `three-mesh-bvh`,
  `three-stdlib`, `troika-three-text`, `tunnel-rat`, `use-sync-external-store`, `utility-types`,
  `zustand`. **peerDependencies (4):** `@react-three/fiber`, `react`, `react-dom`, `three`.
- **Supply-chain note:** drei has **by far the largest fan-out** (21 direct deps, several of which —
  `three-stdlib`, `three-mesh-bvh`, `hls.js`, `@mediapipe/tasks-vision`, `troika-three-text` — carry
  their own subtrees). It is the highest-risk of the three and the one most likely to trip the
  whole-tree age/advisory gate at admission.
- **Advisories:** OSV `@react-three/drei@10.7.8` → empty; GitHub advisory DB `affects=@react-three/drei`
  → **0**. → advisory-free at top level.

---

## 4. Transitive resolution — NOT done here (deferred to admission, by policy)

This pre-screen checked the **three top-level packages only**. Exact **transitive counts** were not
computed because that requires resolving semver ranges into a concrete tree (an `npm` lockfile), which
this thin-client/docs-only task does not produce. **The dependency-security policy applies to the
ENTIRE committed lockfile** — every direct, transitive, dev, and test package must independently be
advisory-free, ≥ 604800 s old, exact-pinned, integrity-matched to `registry.npmjs.org`, and from the
official registry (`dependency_age_gate.mjs` + `npm audit`). So the admission packet must:
1. generate the committed `package-lock.json` via the reviewed pinned npm CLI (no local install here),
2. run the committed-lock **age gate** over the whole tree (drei's fan-out is the likely long pole),
3. run `npm audit --audit-level=low` (JSON total == 0) over the whole tree,
4. record a **G5 provenance review** for each *new* package (name/typosquat, maintainers/ownership
   change, lifecycle scripts, registry origin, publication date, necessity) — a new dependency is a
   G5-reviewed change (policy §5),
5. re-confirm `@react-three/fiber` age at that time (pin 9.7.0 unless 9.8.0 has aged past 7 days).

## 5. Scope attestation (AS-4)
Docs-only. This task touches **only** its four allowed research/report files. No `package.json`,
no `apps/web/.npmrc`, no `package-lock.json`, no source, no rule, no gate config is modified. Nothing
here admits a package; it is provenance input for a future gated admission.

## 6. What I could not verify in this pass
- Exact transitive dependency counts / the full resolved tree (needs a lockfile — deferred to admission,
  §4). Only direct + peer dependencies were read from the registry manifests.
- Advisory coverage is top-level only; the whole-tree advisory audit is the admission packet's job.
- `npm audit` was not run (thin client / no local npm — per CODING_RULES). OSV + GitHub advisory DB are
  the primary-source substitutes used here for the top-level check.
