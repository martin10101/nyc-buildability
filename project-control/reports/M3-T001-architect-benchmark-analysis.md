# M3-T001 — Architect benchmark analysis (derived; adversarial, NOT an answer key)

**Task:** M3-T001 (D-002 first-wave lane 1). **Tracked by:** B-010 (client R5 benchmark sheet absent from
repo). **Nature:** This is a *derived* analysis. It records the supplied sheet's **hash** and its **observed
statements**, and surfaces the required **discrepancy / missing-input findings**. It is **adversarial input,
not an answer key** — the sheet's own numbers are treated as claims to be checked, never as correct
results. It emits **no buildable/compliant conclusion** and **infers no project identity**.

## Provenance discipline (binding)

- The client architect PDF is **NOT committed** anywhere in this repository (B-010; NC-2). Only its
  content hash and human-readable observations are recorded here.
- Identity fields on the sheet (project / address / BBL / job number / checked-by) are **blank**, and this
  report **infers none** of them from PDF metadata, filename, or content (B-010; AS-7; NC-2).
- Provenance tier of this document class: **tier 6 (architect/client document)** per
  [SOURCE_AUTHORITY_POLICY.md](../../docs/SOURCE_AUTHORITY_POLICY.md) §2 — **never general legal
  authority**; it is project evidence to be checked.

## Captured identity of the artifact

| Field | Value |
|---|---|
| Artifact | One-page architect zoning-analysis sheet, labeled **"2 OF 2"** |
| SHA-256 | `9442b5002e10b8ac0d9f78500db7cd4e8b34240e9155d0c61bbb51e00407ea85` |
| Project / address / BBL / job / checked-by | **BLANK on the sheet — not inferred** |

## Observed sheet statements (recorded, NOT endorsed)

| Item | Sheet statement (as printed) |
|---|---|
| District | R5 |
| Lot | 40 × 125 ft = 5,000 sq ft |
| §23-361 (lot coverage) | 60% / 3,000 sq ft allowed; **2,850 proposed** |
| §23-21 (floor area ratio) | 1.50 / 7,500 sq ft allowed; **7,602 proposed** |
| §23-422 (perimeter wall / setback height) | "35 ft, 45 ft — with a setback of 15 ft"; **35 ft proposed** |
| Front yard | 10 ft |
| Rear yard | 20 ft |
| Side yards | 5 ft |

These are transcriptions of what the sheet visibly states (**extraction truth** only, per
[DOCUMENT_EVIDENCE_POLICY.md](../../docs/DOCUMENT_EVIDENCE_POLICY.md) §1). They are **not** confirmed as
legally correct (legal truth) and their arithmetic is **not** endorsed as applicable (mathematical truth
without applicability proves nothing).

## Required discrepancy / missing-input findings (the system's correct response)

1. **Proposed floor area exceeds the sheet's own stated cap by 102 sq ft.** The sheet states a §23-21 cap
   of 7,500 sq ft (1.50 × 5,000) yet lists **7,602 sq ft proposed** — **102 sq ft over** the cap it itself
   prints. This internal inconsistency must be surfaced, not silently accepted.
2. **No floor-area-exclusion schedule is supplied.** Whether 7,602 could be reconciled depends on
   applicable floor-area exclusions/deductions; **none is provided**, so the overage cannot be explained
   away and no exclusion may be invented.
3. **60% lot coverage is not selectable until the legal lot type and proposed residence type are known.**
   The 60% figure is conditional (lot type per §12-10; residence type); it must not be applied until those
   predicates are affirmatively resolved. Unknown predicates are `unsupported` /
   `professional_review_required`, never assumed.
4. **The 15-ft setback branch depends on narrow-street and vertical-envelope conditions.** §23-422's
   35 ft / 45 ft with 15-ft setback is branch-dependent (street width, envelope), and §23-422 carries the
   "except R5 Districts with a letter suffix" exclusion; the branch cannot be selected without those
   conditions resolved (see the §11-25 suffix-inheritance / §23-422 express-exclusion pair driving M3-T004).
5. **Side-yard requirements depend on the proposed building type and may require two yards.** A single
   "5 ft" side-yard entry is insufficient: building type (detached / semi-detached / zero-lot-line /
   attached) drives whether one or **two** side yards are required. The single value hides a building-type
   branch.
6. **Project identity and zoning-lot documentation are missing.** No zoning-lot boundary, no recorded
   instruments (variance / special permit / restrictive declaration / ZLDA), and no project identity are
   supplied; property-specific precedence (SOURCE_AUTHORITY_POLICY.md §3.1 factor 5) cannot be evaluated.

## Conclusion (the honest boundary)

This analysis **emits no buildable, compliant, or feasible conclusion** about any property. The sheet is an
adversarial benchmark whose correct system response is the discrepancy/missing-input findings above — a
forced "pass" would be wrong. Any modifier not found is treated as `unsupported` / `not_evaluated` /
`professional_review_required` until cross-reference closure (M3-T004); **nothing here is called "confirmed
absent"** (NC-1). This report seeds the downstream **architect-benchmark harness** (a real analysis must
reproduce these discrepancies, never a forced pass).
