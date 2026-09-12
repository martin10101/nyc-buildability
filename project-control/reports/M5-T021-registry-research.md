# M5-T021 — Registry research deliverable (verbatim)

Orchestrator preservation note: returned by the official-source-researcher agent
("Research advisory fix versions") on 2026-09-12 and preserved verbatim below (transport
entity-decoding only). This is the registry-fact basis for the M5-T021 package.json pins;
every timestamp is from the live npm registry .time object and every advisory range from
OSV, accessed 2026-09-12.

---

I have all the registry and advisory facts verified from the npm registry `.time` fields and the OSV advisory database. Here is the report.

---

# D-042 Dependency-Security Research — apps/web

**Access date:** 2026-09-12. **Age gate:** publish timestamp must be ≥ 604800 s (7 full days) before now, measured against npm registry `time[version]` (UTC). **Method:** `curl https://registry.npmjs.org/<pkg>` → `.time` for publish timestamps; `https://api.osv.dev/v1/vulns/<GHSA>` and `/v1/query[batch]` for affected ranges / fixed versions / clean-version confirmation. Current pins read from `apps/web/package.json` (deps: next 15.5.21, react 19.1.2, react-dom 19.1.2; vitest 3.2.7 devDep; overrides postcss 8.5.23, sharp 0.35.3, brace-expansion 1.1.18, js-yaml 4.3.1, nanoid 3.3.18).

## Findings table

| Package | Current (source) | Advisory (fixed in) | Newest **aged** fixed version — publish ts (age) | Required change |
|---|---|---|---|---|
| **next** | 15.5.21 (exact direct dep) | GHSA-p293-qw3h-jr36 (fix 15.5.24); GHSA-2xp9-vwfh-vxw4 (fix 15.5.24) — both affect `<15.5.24` in 15.x | **15.5.24** — 2026-08-25T16:14:06Z (17.3 d) ✓ | **Pin bump** → 15.5.24 (per D-042). 15.5.24 clears gate; OSV `query` on next@15.5.24 = **NONE** open |
| **js-yaml** | 4.3.1 (**override**) | GHSA-2883-xcg3-v3hh (CPU DoS) — 4.x fixed **4.3.2** (also 3.x fixed 3.15.2) | **4.3.2** — 2026-08-26T20:42:48Z (16.1 d) ✓ | **Override bump** → 4.3.2. Regen alone cannot fix: the override force-pins 4.3.1. 4.3.2 clean (OSV NONE) |
| **browserslist** | transitive (not pinned) | GHSA-c83g-rgw3-j3cx (fix 4.28.7); GHSA-73wf-gq98-2v4g (fix 4.28.7) | **4.28.9** — 2026-09-04T13:39:02Z (7.4 d) ✓ (safe fallback 4.28.8 — 2026-08-08, 35 d) | **None — lockfile regen** under existing `^4` parent ranges reaches ≥4.28.7. 4.28.9 clean |
| **baseline-browser-mapping** | transitive (dep of browserslist) | GHSA-w5vr-8v7q-w6rv (DoS on invalid input) — fix **2.11.0** | **2.11.21** — 2026-09-03T17:37:12Z (8.3 d) ✓ | **Override/constraint pin** → 2.11.21. Fix is in-range, BUT a plain regen pulls latest 2.11.23 (2026-09-12, 0 d) or 2.11.22 (2026-09-10, 2 d) → **fails the age gate**. Must pin to an aged fixed version |
| **@vitest/mocker** | transitive (dep of vitest) | GHSA-82fw-gwwq-j7x9 (path traversal) — fix **4.1.11** (affects `>=2.1.0 <4.1.11`; 5.0.0-beta line fixed 5.0.0-rc.2) | **5.0.0** — 2026-09-03T12:23:33Z (9.0 d) ✓ (or 4.1.11 — 2026-08-18, 25 d) | Follows vitest bump (see below) |
| **vitest** | 3.2.7 (exact devDep) | GHSA-82fw-gwwq-j7x9 — fix **4.1.11** (same range) | **5.0.0** — 2026-09-03T12:24:30Z (9.0 d) ✓ (or 4.1.11 — 2026-08-18, 25 d) | **Pin bump — major.** No 3.x fix exists (registry: 3.2.7 → 4.1.10 → 4.1.11 → 5.0.0). "fix via `--force`" = breaking major. Choose 4.1.11 (minimal jump, best-aged) or 5.0.0; both clear the gate. Compat check `@vitejs/plugin-react` |
| **sharp** ⚠ | 0.35.3 (**override**) | **GHSA-rgj7-g3m4-5g8c** (libheif RCE bundle, published 2026-09-08) — fix **0.35.4** | **0.35.4** — 2026-08-26T09:42:27Z (16.6 d) ✓ | **Override bump** → 0.35.4. See item 6/7 below. 0.35.4 clean (OSV NONE) |

## Answers to specific questions

**1. next 15.5.24** — VERIFIED. Published 2026-08-25T16:14:06.715Z (npm registry `time`); ~17.3 days old on 2026-09-12 → clears the 7-day gate comfortably. Both critical advisories affect `<15.5.24` in the 15.x line (fixed 15.5.24), so 15.5.24 is outside both ranges. OSV version query on next@15.5.24 returns **no open advisories**. (Note: both advisories also carry a separate 16.x range fixed at 16.3.3 — irrelevant to a 15.5.24 pin.)

**2. js-yaml** — GHSA-2883-xcg3-v3hh fixed in **4.3.2** (4.x line). Newest aged = 4.3.2 (2026-08-26, 16 d). New override value → **4.3.2**.

**3. browserslist** — Both GHSAs fixed in **4.28.7**. Transitive, not pinned. In-range lockfile regeneration under standard `^4` parent ranges resolves it (latest 4.28.9, 2026-09-04, clears the gate). No package.json edit required.

**4. baseline-browser-mapping** — GHSA-w5vr-8v7q-w6rv fixed in **2.11.0**. Transitive, but the two newest (2.11.22 @ 2026-09-10, 2.11.23 @ 2026-09-12) **fail the age gate**, so a bare regen risks a gate failure. Pin to an aged fixed version — newest aged is **2.11.21** (2026-09-03, 8.3 d). Requires an `overrides` entry (or a lockfile constraint) rather than a free regen.

**5. vitest / @vitest/mocker** — GHSA-82fw-gwwq-j7x9 fixed in **4.1.11** for both. Currently pinned vitest 3.2.7 (major 3); **no 3.x fix exists** — the fix is outside the current major, so a `package.json` devDependency bump is required (this is the "`--force`" breaking upgrade the audit flagged). Newest aged fixed = **5.0.0** (2026-09-03, 9 d); the minimal, best-aged option is **4.1.11** (2026-08-18, 25 d). @vitest/mocker resolves transitively from whichever vitest is chosen.

**6 & 7 (the "7th" advisory + override sanity).** These converge on one concrete finding. OSV version queries on all five override pins and both React packages returned **NONE open** *except* **sharp@0.35.3**, which is hit by **GHSA-rgj7-g3m4-5g8c** ("sharp: vulnerabilities in libheif," CVSS4 9.x, published 2026-09-08T21:25:11Z, fixed **0.35.4**). React 19.1.2 / react-dom 19.1.2 and overrides postcss 8.5.23, brace-expansion 1.1.18, js-yaml (at candidate 4.3.2), nanoid 3.3.18 are all clean.

The CONTEXT enumerates **7 GHSA IDs** but they map to only **6 vulnerable package nodes** (next carries 2 advisories; vitest+@vitest/mocker share 1). npm audit's "7 vulnerabilities" is most consistent with counting vulnerable **package nodes**, in which case the 7 nodes are next, browserslist, js-yaml, vitest, @vitest/mocker, baseline-browser-mapping **and sharp** — i.e. **sharp@0.35.3 / GHSA-rgj7-g3m4-5g8c is the most probable unlisted 7th vulnerability** (its 2026-09-08 publish predates the 2026-09-12 audit). I could **not** fully confirm this against the raw `npm audit --json` from CI job 103547594072 — that artifact is not in the repo and the job output was not accessible to me — so npm's exact node-vs-advisory counting for this run is unverified. Regardless of the counting question, **sharp 0.35.3 must be bumped to 0.35.4**: it is a pinned override at a version with a live critical advisory, and 0.35.4 is aged (16.6 d) and clean.

## Net package.json changes required (all clear the 7-day gate on 2026-09-12)

- `dependencies.next`: 15.5.21 → **15.5.24** (D-042).
- `overrides.js-yaml`: 4.3.1 → **4.3.2**.
- `overrides.sharp`: 0.35.3 → **0.35.4** (not in the original 7-list; required).
- `devDependencies.vitest`: 3.2.7 → **4.1.11** (or 5.0.0) — major bump; verify `@vitejs/plugin-react` / config compat.
- Add an `overrides` (or constraint) pinning **baseline-browser-mapping = 2.11.21** so regen does not pull the too-new 2.11.22/2.11.23 and trip the age gate.
- browserslist: **no edit** — lockfile regeneration reaches ≥4.28.7 (latest 4.28.9).
- Consider aligning `eslint-config-next` (currently 15.5.21) with next 15.5.24 for consistency; it is **not** named in either next advisory, so not required by the age/advisory gate.

## Limitations / uncertainty (disclosed)

- The npm registry and OSV responses in this environment return a **2026-dated ecosystem** (e.g. js-yaml latest 5.4.1, next latest 16.3.5, vitest 5.0.0). I treated these as the authoritative sources per the task; they differ from the public registry state at my training cutoff. Every timestamp above is copied verbatim from the live `time` object.
- Ages assume "now" = anytime on 2026-09-12. browserslist 4.28.9 (7.4 d) is the only fix that is *close* to the boundary — it clears (>604800 s from 2026-09-04T13:39Z as of 2026-09-11T13:39Z), but 4.28.8 (35 d) is the risk-free fallback if the exact evaluation instant matters.
- The identity of npm audit's literal "7th" entry is **inferred, not confirmed from the raw CI audit JSON** (unavailable to me). The evidence-backed fact is that sharp@0.35.3 carries an open critical advisory fixed in 0.35.4.
- Reachability calls for browserslist/baseline-browser-mapping assume standard caret parent ranges; the actual `package-lock.json` resolution should be regenerated and re-audited to confirm (fail-closed).

**Sources** (all accessed 2026-09-12):
- npm registry `.time`: https://registry.npmjs.org/next , /js-yaml , /browserslist , /baseline-browser-mapping , /vitest , /@vitest/mocker , /sharp
- OSV advisories: https://api.osv.dev/v1/vulns/GHSA-p293-qw3h-jr36 , /GHSA-2xp9-vwfh-vxw4 , /GHSA-2883-xcg3-v3hh , /GHSA-c83g-rgw3-j3cx , /GHSA-73wf-gq98-2v4g , /GHSA-82fw-gwwq-j7x9 , /GHSA-w5vr-8v7q-w6rv , /GHSA-rgj7-g3m4-5g8c
- OSV version queries: https://api.osv.dev/v1/query , /v1/querybatch (next@15.5.24, react@19.1.2, react-dom@19.1.2, js-yaml@4.3.2, postcss@8.5.23, sharp@0.35.3+0.35.4, brace-expansion@1.1.18, nanoid@3.3.18, browserslist@4.28.9, baseline-browser-mapping@2.11.21)
- Repo: `apps/web/package.json`
