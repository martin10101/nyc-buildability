# M0-T012 — G2 producer self-check evidence (+ orchestrator-captured S5 CI proof)

- **Task:** M0-T012 CI SHA-pinning
- **Date:** 2026-07-17
- **Branch:** `task/M0-T012-sha-pinning` @ `e5f6ea4`

## Producer self-check (details + verbatim commands in project-control/reports/M0-T012-producer-report.md on the branch)

- S1 PASS: zero `@vN` tag refs remain in ci.yml / generate-lockfile.yml; all 12 refs are `<40-hex> # vX.Y.Z` in the secret-scan.yml style.
- S2 PASS: every SHA proven twice (gh api git/ref/tags + independent git ls-remote); method validated by re-resolving v4.2.2 → byte-identical to the pre-existing secret-scan.yml pin. All four tags were lightweight (object.type "commit"; no annotated dereference needed).
- S3 PASS: same major line — checkout v4→v4.3.1, setup-node v4→v4.4.0, setup-python v5→v5.6.0, upload-artifact v4→v4.6.2.
- S4 PASS: git diff = 12 single-line `uses:` substitutions only (2 files, +12/−12 excluding the report); PyYAML parses both files, job set unchanged.
- S6 PASS: exactly 4 distinct pin strings across all 12 refs.
- Disclosure: packet inventoried 11 refs; the actual count is 12 (5th checkout in the M2-T001 web-e2e job) — all 12 pinned per S1's zero-tag-refs rule.

## S5 — orchestrator-captured CI proof (the pinned SHAs actually resolve and run)

| Workflow | Run | Commit | Result |
| --- | --- | --- | --- |
| CI (all 6 jobs incl. web/web-e2e) | [29554930113](https://github.com/martin10101/nyc-buildability/actions/runs/29554930113) | `e5f6ea4` | completed / **success** |
| secret-scan | [29554930067](https://github.com/martin10101/nyc-buildability/actions/runs/29554930067) | `e5f6ea4` | completed / **success** |

## Result

**G2 PASS** — submission permitted; G3 (security-reviewer) next.
