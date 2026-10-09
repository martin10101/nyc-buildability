# D-063 delivery and remaining work

The orchestrator accepted M4-T022 and M5-T031 at reviewed commit `daca3a0b949dc02100ed42499addfecc82c1ebe1` after every required gate and independent directive verification passed. PR 242 was integrated by non-forced fast-forward into `candidate/D-024-mrl-option-b`; GitHub records it merged at that exact commit. Main and PR 241 were not changed.

Only the existing frontend Render service `srv-dajnsctg1s2s73bg2do0` was deployed. Deploy `dep-dakvhsek1f9s73d60tv0` became live at 2026-09-16T02:05:04.929206Z on the reviewed commit. The backend remains on `f0e7d82f98481506f16f48614722059e807d73ca`, deploy `dep-dak18m2d0e5s738an8o0`. Both services retain manual deployment and all service settings are unchanged.

## Delivered behavior

- Overview, Zoning and Report lead with a shared development summary. City residential FAR, evaluated FAR and existing Built FAR have separate meanings and locations.
- Existing-building information is collapsed on Overview and remains available in facts, sources and reports. Lot-specific source links, original values, normalized values and full audit controls are retained.
- Unsupported, malformed or unassociated calculation results do not become numeric development limits. Raw evidence remains available. No frontend multiplication or substitution supplies a missing cap.
- The new internal source audit provides repeatable independent expectations across 45 residential district identifiers, including variants, with 21 real parcel records from all five boroughs. Its scope and unresolved conditions are explicit.

## Verification

Final CI 35045256846 passed all 18 jobs, including 918 unit/component tests and 113 browser journeys. Context-budget and secret-scan workflows also passed. Independent source, implementation, QA and security reviews passed, followed by independent verification of all 18 applicable directive/task requirement pairs. Failed earlier reviews and repaired negative-test evidence remain in history.

After deployment, six actual property examples were checked through the live UI: the reported Brooklyn M1-2/R6A lot plus R1-2, R2, R5, R5D and R6 examples spanning all five boroughs. Each displayed its expected city residential reference separately from existing Built FAR. At BBL 3052960043 the values were 3.00 and 2.61 respectively, with the source drawer linking the correct BBL. Zoning and Report retained the same distinction and the report retained full-audit selection. Exact observations and execution limitations are in `project-control/reports/D-063-live-v3.json`.

The source audit passes 26 tests; its engine run records 467 passing checks and 80 classified gap rows. These are mixed evidence layers, not a completion percentage or 80 distinct defects. It has not been wired into CI within this scope.

## Remaining calculation work

All six live examples still lack spatial evidence for a supported property-specific cap. This delivery does not resolve the existing `spatial_intersection_absent` problem. The next engineering work is a separately scoped diagnosis of the deployed spatial path and wiring of valid lot/district/street inputs into the normal calculation flow. Existing centerline and buffer modules alone do not prove that integration is complete.

Height, setbacks/yards, lot coverage, street-wall conditions, qualifying-site/bonus eligibility and special/mixed/split-district handling still need applicable calculations and independent case coverage before the product can claim a complete buildable envelope. General FAR-table agreement does not establish every property's eligibility. Original user frontend-only constraints remain in force; no backend or rule publication occurred.

Routine source comparisons and regression checks are the engineering team's responsibility. No new architect benchmark sheet was required for this delivery. Qualified legal approval remains distinct from engineering verification.

The cloud browser lacked WebGL; this run verified the honest map fallback and lot-specific ZoLa link, not the appearance of a rendered live interactive map. Live PDF printing was not repeated; its connected event and evidence-retention paths passed the recorded CI and independent review.

Final follow-up repository changes contain only review, acceptance, checkpoint and delivery records. They do not alter the deployed frontend content or require another deployment.
