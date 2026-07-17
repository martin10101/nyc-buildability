---
name: m1-t007-g3-carryforward
description: M1-T007 DOB NOW research G3 PASS @294dad5; bf97-mjsy -> M1-T008 binding; conservative-join-language precedent; residual low observations
metadata:
  type: project
---

M1-T007 (DOB NOW Open Data family research) G3 PASS 2026-07-17 at 294dad5 (4 commits: 65cef7a producer, 385de84 C1, d2949c0 C1v2, 294dad5 owner corrections 1-3). All owner-directed items verified, incl. live bf97-mjsy re-checks (count 1326, min/max 2024-01-03..2026-07-14, 20 cols) and SHA256 recomputation of all 4 bf97-mjsy fixtures (all match README).

**Why:** owner re-opened C1 as C1v2 demanding evidence-backed dispositions (not catalog-completion exclusions) and personally corrected padding/join overclaims — this project treats "joins cleanly"/"trivial" as overclaims; required wording is "appear compatible ... subject to connector validation, normalization, and mismatch handling". Padding claims may only cover what samples actually prove (bf97-mjsy: block unpadded proven, shorter-lot padding NOT established).

**How to apply:**
- M1-T008 contracting: MUST be DOB-wide (bf97-mjsy as DOB Incident Database source — never call it BIS — plus g76y-dcqj, 855j-jady) per binding §6 of project-control/reports/M1-T007-owner-connector-directives.md; if narrowed to BIS-only, a sibling task must carry the three in the same replan.
- M2 DOB connector reviews: enforce directives §2-§5 (BIN fan-out model, key-format validation `^[A-Z]\d{8}-` vs "Permit is no" pollution, borough casing, non-ISO dates in 52dp/pkdm text columns, "DOB NOW channel coverage" labeling until BIS reconciled).
- Residual LOW observations (non-blocking, recheck at M1-T008/M2): the 2 HPD noise catalog hits (rrtd-iyd7, pq4c-wbq4) are dispositioned only as a category, not by ID, in findings §2.1; OQ-2 XLSX dictionaries and OQ-4/OQ-5 remain open for connector build.
- Reproduction gotcha: percent-encoding the `$` in Socrata param names (%24limit) → HTTP 400 "Unrecognized arguments []"; use literal `$`.

Related: [[m1-t002-g3-carryforward]] (connector precedents), [[m1-t001-g3-carryforward]] (BBL serialization/PLUTO C6 contrast — rbx6 number-BBL observed clean but OQ-3 keeps defensive normalization).
