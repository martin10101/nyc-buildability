---
name: npm-lockfile-age-gate
description: Verified npm registry / OSV / package-lock shapes and fail-closed semantics for the committed-lockfile release-age gate (M0-T019 FE-S9/S11)
metadata:
  type: project
---

Stable facts for the npm committed-lockfile release-age gate
(`apps/web/scripts/dependency_age_gate.mjs`, M0-T019 FE-S9/FE-S10/FE-S11). All
verified live against official sources 2026-07-20.

**Why:** `.npmrc min-release-age` filters only at npm RESOLUTION; `npm ci`
installs the committed lock WITHOUT resolving, so a hand-edited lock can smuggle
a <7-day or forged-integrity package past `npm ci` + `npm audit`. The committed
lock needs an independent fail-closed gate — the npm parallel of the accepted
Python `services/api/scripts/dependency_age_gate.py`.

**How to apply:**
- **package-lock.json (lockfileVersion 3):** `packages` object keyed by
  `node_modules/...` paths. Registry packages carry `resolved` (a
  `https://registry.npmjs.org/...tgz` URL), `integrity` (SRI), `version`. The
  root key is `""` (skip it). Link/workspace entries have NO `resolved` (skip
  them — no artifact to age-gate). Derive the package name from the segment
  after the LAST `node_modules/`, preserving a leading `@scope/`; nested
  transitives (`.../node_modules/lru-cache`) reduce to the bare name. Dedupe by
  `name@version`. The current apps/web lock has ZERO non-registry hosts and the
  `@next/swc-*` platform packages present.
- **npm packument (`GET https://registry.npmjs.org/<name>`, scoped `/`→`%2f`):**
  publication time is top-level `time[version]` (ISO-8601, e.g.
  `react` `time["19.1.2"]="2025-12-03T15:32:12.347Z"`). Per-version artifact
  integrity is `versions[version].dist.integrity` (SRI). Require it EQUALS the
  lock's committed integrity — anti-forgery so an old version number can't ship
  a swapped artifact.
- **OSV (`POST https://api.osv.dev/v1/query` `{package:{ecosystem:"npm",name},version}`):**
  returns `{}` (NO `vulns` key) when clean — treat absent `vulns` as "no
  advisories", only a non-empty `vulns` array is a finding. Every network/parse/
  non-OK path must throw → FAIL (fail-closed).
- **Authoritative UTC now:** HEAD `https://registry.npmjs.org/`, read the HTTP
  `Date` header (mirrors the Python `utc_now` PyPI Date-header approach). Never
  the local clock. Fail-closed if missing/unparseable.
- **Boundary:** `MIN_AGE_SECONDS=604800`; `ageSeconds=Math.floor((nowMs-publishedMs)/1000)`;
  `passed = ageSeconds >= 604800`. 604800 PASSES, 604799 FAILS. Integer seconds,
  no day rounding. NO allowlist/suppression/exception path anywhere.
- **Node built-ins only** (global `fetch`, `node:fs`, `node:process`,
  `node:test`/`node:assert`) so the gate is not itself install/age-gated and
  runs with zero install. Tests use `node --test`; the CLI self-invokes only
  when `process.argv[1]` ends with the script name (so `node --test` importing
  the module never triggers the CLI).
