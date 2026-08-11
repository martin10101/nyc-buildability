# M0-T047 — Producer report (security-hygiene; nanoid 3.3.17 remediation)

**Task:** Remediate GHSA-2v37-7h3g-55p8 (nanoid predictable-generation advisory, round-3) by admitting
nanoid **3.3.17** to the `apps/web` lock via an exact-pin override. Directive: **D-009:ALL**.

**Provenance of the change.** The fix was built and CI-validated on branch `task/M0-T047-nanoid-lock`
(PR #219, tip `7ac2f91`): commit `1e39021` adds the exact-pin override; commit `7ac2f91` regenerates
`apps/web/package-lock.json` via the CI lockfile-regeneration workflow. This report lands that exact,
byte-identical change onto the integration branch `control/session15-acceptance` for the M0-T047 gate
wave and acceptance. Blob parity verified: staged `apps/web/package.json` = `90e801a…` and
`apps/web/package-lock.json` = `6e75bff…`, both identical to `7ac2f91:<path>`.

## The change (2 files, exactly)

- `apps/web/package.json` — add `"nanoid": "3.3.17"` to the `overrides` block (exact version pin, no range).
- `apps/web/package-lock.json` — `node_modules/nanoid` `3.3.16 → 3.3.17`:
  - `resolved`: `https://registry.npmjs.org/nanoid/-/nanoid-3.3.17.tgz`
  - `integrity`: `sha512-xQLf0A3HOMlgHq0n247/LRuAOYmB7dXJ/DvAxGvsSBij45XtBSmQycu+F8ODbHwns/XyFZagyL1+J0Offw1E0g==`

No other package, dependency, or file changed. Diff is a strict subset of #219.

## D-009 dependency-security evidence (machine-enforced, fail-closed)

- **Advisory-free (D-009-R002).** 3.3.17 remediates GHSA-2v37-7h3g-55p8; the `web-dependency-security`
  (npm CLI advisory + audit) and `web tree re-audit` jobs are advisory-blocking and fail closed on any finding.
- **Exact pin (D-009-R003).** Override is the exact string `3.3.17` (no `^`/`~`/range).
- **Integrity match (D-009-R004).** The committed lock records the registry sha512 integrity above;
  the audit/lock verification jobs match it to the official npm registry.
- **Age ≥ 7 complete days (D-009-R003/R004, 604800 s).** Enforced by the committed-lockfile age gate inside
  `web-dependency-security`. **Authoritative evidence = the FRESH re-run of these jobs on this
  `control/session15-acceptance` commit** (they re-evaluate the registry release timestamp at today's date,
  2026-08-11). #219's identical lock already passed the same gate; the fresh #220 run reconfirms at HEAD.
- **Not a new package (D-009-R005).** nanoid was already in the tree (3.3.16 → 3.3.17 is a patch bump), so no
  new-package G5 provenance admission is required; this is an advisory remediation of an existing dependency.
- **No age waiver used.** This remediation does NOT invoke the owner-authorized age-only exception path; it
  relies on 3.3.17 genuinely satisfying the 7-day gate.

## Gate posture

required_gates G0/G2/G3/G5; reviewers code-reviewer (G3) + security-reviewer (G5) +
directive-compliance-verifier (D-009 DCV binding the REAL applicable requirement set, not empty).
Acceptance is contingent on the fresh #220 dependency-security CI being green (age gate at today's date).
After accept, PR #219 merges to main; #220 carries the identical fix (parity), so the #220→main merge
preserves nanoid 3.3.17 with no conflict.
