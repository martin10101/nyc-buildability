# M5-T126 producer report - measurement basis for the realistic apartment estimate

Producer: scenario-optimization-engineer (builder), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-aae3eff37b653ce7e`.
Contract/claim-seam head reset to `8dd39c9f0d2c09bc596063eaf259dc658f29b1c5`.
No estimator built; no program code changed. Only allowed paths touched.

## What was delivered

- `docs/measurement-basis/MEASUREMENT_BASIS.md` - the record: the two area definitions, each
  quoted from its source before any formula (ZR 12-10 floor area, ZR 23-23 + 23-231..234,
  qualifying exterior wall thickness, from the captures; HPD 2026 UNIT AREA CALCULATION read
  at the official source); the area-schedule form (one row per component, treatment under
  each system with provision and condition); the method (two separate sums from one
  schedule, reconciled, nothing deducted twice, no generic gross-to-net percentage); the
  ratio rule (total HPD-measured dwelling-unit area / residential zoning floor area, and
  nothing else); the legal cap kept separate; what the examples show and do not show; eight
  open points for the owner, each with a recommendation and its basis.
- `docs/measurement-basis/examples/<id>.json` + `<id>.md` (x3) - the worked examples
  (data + rendered page).
- `services/api/tests/scenario/measurement_basis/` - stdlib checker, renderer and
  `test_measurement_basis_examples.py` (engine-free; recompute every area and reconciliation
  line with exact decimal arithmetic).

## The three worked examples

| Example id | Mixed use | Residential zoning floor area | Total HPD dwelling-unit area | Ratio (denominator = residential zoning floor area) | Legal cap (ZR 23-52, separate) |
|---|---|---|---|---|---|
| example-a-standard-residential | no | 8,000 sq ft | 6,032 sq ft | 0.7540 | 13 units (9,000 / 680) |
| example-b-allowances-conditions-shown | no | 11,291 sq ft | 6,800 sq ft | 0.6022 | 17 units (12,000 / 680) |
| example-c-mixed-use | yes | 6,920 sq ft | 4,620 sq ft | 0.6676 | 11 units (7,500 / 680) |

The three ratios differ by design: each depends only on its own made-up layout. No
percentage is presented as typical; 700 sq ft, 25 percent, 10 ft and 15 ft remain
unapproved assumptions and are validated by none of this.

## Open points put to the owner (one line each; full basis in the record section 8)

1. The apartment-area ratio is unvalidated -> carry it as an editable assumption, not a
   fixed 75 percent (neither HPD nor HCR establishes a ratio).
2. The average apartment size is unvalidated -> carry 700 sq ft as an editable historical
   reference, labelled "not an HPD-measured R6B average".
3. What a user must see and change -> expose ratio, average size, unit mix and floor heights
   as visible editable assumptions with their basis and uncertainty.
4. What stays "not known" without a layout -> without a layout report the physical count as
   not known; show only the legal cap, labelled a ceiling.
5. The exact legal base for the amenity 5 percent -> define it before relying on it (not
   sure; a legal-interpretation point; the examples' caps did not bind).
6. Shared-space allocation in mixed-use -> decide how shared stairs/lifts/lobby split between
   the portions before relying on a mixed-use estimate.
7. Which ZR 12-10 exclusions to model -> decide whether the energy (5 percent) and
   qualifying-exterior-wall exclusions are modelled or left as user-confirmed conditions.
8. What the estimator needs before it is built -> build only after points 1-7 settle; it
   needs a layout (or explicit layout assumption), the editable ratio and average size, and
   must keep the physical estimate separate from the legal cap.

## Sources read at an official address

- HPD Design Guidelines for New Construction, 2026 edition, subsection UNIT AREA CALCULATION
  (and APPLICABILITY), read 2026-10-07 at
  `https://www.nyc.gov/assets/hpd/downloads/pdfs/services/hpd-design-guidelines-for-new-construction-2026.pdf`
  (HTTP 200; PDF last-modified 2026-09-23; sha256
  `309d1863649bb7ff75d38931ed610de66c8b2ff3986b0de86299212e2cddb890`; the subsection is on
  PDF page 28; quote confirmed visually). The exact quote is embedded in the test-support
  library as the oracle for the HPD citations; it is a guideline, not law, and applies to
  HPD-loan-program projects whose design-consultation submission is on or after
  2026-10-01 (MIH/UAP incentive-only projects are not subject to it).
- The ZR law text was quoted only from the existing pinned captures under
  `docs/research/zr-snapshots/v1/` (digests verified live by the checker against each
  snapshot). Nothing I could not read: the HPD guideline was read successfully at the
  official source.

## Checks (run one at a time; direct exit codes)

a. `python -m ruff check .` (from services/api) -> exit 0 ("All checks passed!").
b. `python -m pytest -q -p no:cacheprovider tests/scenario/measurement_basis` (from
   services/api, lanes venv, PYTHONPATH=services/api) -> exit 0, 27 passed.
c. renderer check mode `measurement_basis_render.py --check` -> exit 0
   ("measurement-basis check PASSED (no issues)"); the three rendered pages are
   byte-identical to the data.
d. `python3 tools/modularity_check.py --check` -> exit 0 (selected 715 files; failures 0;
   none of the new files flagged). `python3 scripts/lanes/check_lane_paths.py --coverage`
   -> exit 0 ("LANE COVERAGE PASS"); the new files match existing globs
   (`docs/**`, `services/api/tests/scenario/**`, `project-control/**`).
e. Two mutation proofs (also encoded as passing tests):
   - changed dimension: in a copy of example A, apartment-interior width 46 -> 47 ->
     "example-a-standard-residential/apartment-interior: measured_area recomputes to 6016 but
     the example records 5888" (names the example and the component).
   - a component deducted under both systems: in a copy of example B, adding a bridge step
     that subtracts the cellar (already excluded from zoning) -> "bridge step for 'cellar'
     deducts area that is not in the residential zoning floor area (nothing already excluded
     may be deducted again)" - the reconciliation check fails.

The full `services/api` pytest suite was NOT run by the producer (per the packet, the
orchestrator runs it once on the frozen candidate).

## Acceptance scenarios

S1 definitions-before-formula, S2 one-schedule-two-treatments (HPD rows use "mechanical and
plumbing chases" and keep internal partitions in the unit), S3 conditional allowances
(amenity/refuse taken when shown; corridor length not met -> only 50%; parking condition not
met -> counts; cellar/mechanical excluded under both and never re-deducted), S4 space from the
layout not the FAR, S5 two separate sums reconciled by component, S6 exact arithmetic +
byte-identical pages + the dimension mutation, S7 ratios are example-only and 700/25/10/15
stay unapproved, S8 mixed-use uses the residential portion only, S9 legal cap kept separate
with the ratio's denominator named, S10 open points with recommendations, S11 no program
change and engine-free support files - all covered by the committed tests.

## Assumptions and limitations

- The layouts, dimensions, unit mixes and the three legal-cap maximum-floor-area figures are
  made up and editable; nothing here is validated or a legal determination.
- The amenity 5-percent cap is modelled against a stated base that does not bind in the
  examples; the exact statutory base is left as open point 5 ("not sure").
- Mixed-use shared-space allocation is not settled (open point 6).
- No internal ledger task ids appear in the reader-facing record or example pages; directive
  D-090 requirement ids are retained as the owner's own provenance vocabulary.

## Requested status

awaiting_gate (G0 already recorded at the claim seam; requesting G2 producer self-check and
the independent G3/G4 review by code-reviewer and directive-compliance-verifier).

END-OF-REPORT
