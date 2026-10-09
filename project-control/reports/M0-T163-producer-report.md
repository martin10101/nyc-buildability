# M0-T163 producer report — brace-expansion 1.1.18 -> 1.1.21 (orchestrator producer)

## Change (exact, minimal)
- `apps/web/package.json` overrides: `"brace-expansion": "1.1.18"` -> `"1.1.21"` (the repo's exact-pin
  mechanism for this transitive, FE-S10; M0-T071 precedent).
- `apps/web/package-lock.json`: the two entries
  `node_modules/brace-expansion` and
  `node_modules/@typescript-eslint/typescript-estree/node_modules/minimatch/node_modules/brace-expansion`
  — version, resolved and integrity only. Dependencies of 1.1.21 are identical to 1.1.18
  (balanced-match ^1.0.0, concat-map 0.0.1), so no other lock entry changes.

## Evidence (retrieved 2026-09-30)
- Registry: 1.1.21 published 2026-09-14T21:59:28.332Z (>= 604800 s before today).
- Integrity: tarball downloaded from registry.npmjs.org and hashed locally:
  `sha512-9zeA+KLZNNzglF2TPKRQEDyx6Yby7daAkuy8MiPzpXPsYDWi/DRM8jmwUDxokQjYqBpv5DgPiwD4h4ZZSy1Ujw==`
  == registry `dist.integrity`.
- Advisories (GitHub advisory API): GHSA-q2hr-2g5m-vwhr `< 1.1.21`, GHSA-qhr7-859c-m2p7 `< 1.1.20`,
  GHSA-6j4f-fj2g-mc7p `< 1.1.19` (1.x line); `affects=brace-expansion@1.1.21` -> none.
- No npm/npx/node run locally; CI (`web-dependency-security`, `web`, `web-e2e`) is the proof.

## Not done
- No other dependency touched; no waiver requested or used.
