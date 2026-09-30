---
name: npm-dependency-verification-thin-client
description: How to verify npm package advisories/age/integrity WITHOUT npm install (thin-client), and the npm age-gate implementation seams
metadata:
  type: project
---

Verifying npm dependency security on the owner's thin-client PC (no local npm /
node_modules) — learned building the M0-T019 web dependency-security gate.

**Why:** the ~7 GB owner PC prohibits `npm install`, so the usual `npm audit`
is unavailable locally. But the registry itself answers every question disk-free
over plain HTTPS (curl / node:https), which is how per-package evidence gets
produced without a CI round-trip.

**How to apply:**
- Advisories (the EXACT source `npm audit` uses): POST to
  `https://registry.npmjs.org/-/npm/v1/security/advisories/bulk` with body
  `{"<name>":["<version>", ...]}`. The response lists ONLY advisories affecting
  the queried versions; an empty object `{}` means advisory-free. This lets you
  re-verify a specific version offline-of-npm. `npm@11.18.0` was verified clean
  this way (FE-S11).
- Age + integrity in one GET: `https://registry.npmjs.org/<name>` (URL-encode
  the scope slash as `%2F` for `@scope/pkg`) returns `.time[version]` (publish
  timestamp) and `.versions[version].dist.integrity` (match against the lock's
  integrity). Authoritative "now" = the `Date` response header, never the local
  clock. 7-day rule is full-second: 604800 passes, 604799 fails.
- TRAP: a packet-directed override version can already be advisory-vulnerable —
  re-verify every pin/override at implementation time. The M0-T019 packet said
  `overrides.postcss==8.5.10`, but 8.5.10 is hit by GHSA-6g55-p6wh-862q (HIGH),
  GHSA-r28c-9q8g-f849 (HIGH), GHSA-fxqj-rqcc-2cmp (MODERATE, `<=8.5.22`). The
  minimum advisory-free AND >=7-day-old postcss was 8.5.23 (8.5.24/8.5.25 were
  too new for the age gate). Deviation from a packet version is REQUIRED, not a
  waiver, when the directed version is advisory-hit — record it for G5.
- The committed lockfile still needs a CI round-trip to REGENERATE (dispatch
  `.github/workflows/generate-lockfile.yml`, now pinned to npm@11.18.0 and
  self-validating before the bot commits) — the registry queries above verify
  versions but cannot compute a lock's integrity tree offline. See also
  [[property-profile-frontend-rules]] (lockfile-on-CI mechanism).
- Age-gate module seam: `apps/web/scripts/dependency_age_gate.mjs` keeps pure
  logic (parseLock / decide / evaluateLock / decideNpmCli) separate from
  `RegistryClient`, both taking an injectable request fn + `now`, so the 32
  node:test unit tests run fully offline. `node --test` in Node 22 needs an
  explicit file/glob (`scripts/tests/*.test.mjs`), not a bare directory.
