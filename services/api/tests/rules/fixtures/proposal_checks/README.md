# proposal_checks fixtures (M5-T054)

Hand-computed fixture pack for the proposal-conditioned rule checks. Every numeric
expectation must show its arithmetic in the fixture or this README - never derived by
running the module itself (no self-proving fixtures).

## Rectangle case (`rectangle_case.json`)

100 ft x 50 ft rectangular building, 3 identical 10 ft floors, on an 8000 sq ft R5 lot
with one lot line 10 ft west of the west wall. Hand arithmetic:

- footprint = 100 x 50 = 5000 sq ft
- lot coverage = 5000 / 8000 = 0.625
- gross floor area = 5000 x 3 = 15000 sq ft (a geometric gross; no zoning deductions)
- cumulative height = 10 x 3 = 30 ft
- min wall-to-lot-line setback = 1000000 - 999990 = 10 ft

## Checks and commensurability

The four declared checks split by whether the PROVIDED derived fact establishes the
quantity the rule OUTPUT governs:

- `lot_coverage_ratio` - COMMENSURABLE (ratio vs ratio). PASS/FAIL. Here 0.625 > 0.5 -> FAIL, shortfall 0.125.
- `building_height` - COMMENSURABLE (feet vs feet), gated on an attested `street_width_class`. Attested wide -> 30 <= 60 -> PASS; unattested -> the allowance is professional_review_required -> COULD_NOT_CHECK (allowance_unresolved).
- `rear_yard_depth` - NOT COMMENSURABLE. The minimum wall-to-lot-line setback across all walls is not a rear-yard depth (no rear lot line is designated). Always COULD_NOT_CHECK (provided_fact_not_commensurate) - even though `pc-rear-yard-demo` computes 5 ft, the module refuses to compare against it.
- `residential_far_floor_area` - NOT COMMENSURABLE. A geometric gross floor area is not a residential zoning floor area (matching sq ft is not equivalence). Always COULD_NOT_CHECK (provided_fact_not_commensurate) - even though `pc-residential-far-demo` computes 8000 x 1.5 = 12000 sq ft, the module refuses to compare against it.

## Synthetic rulesets (`rulesets/*.rule.json`)

SYNTHETIC representability rules evaluated through the EXISTING evaluator; illustrative
values only, never a Verified determination or an official capture. `pc-height-setback-demo`
emits `max_building_height` (the same OUTPUT name as the real `r5-height` rule) so the one
declared `building_height` check runs against both the synthetic and the real registry;
the synthetic gate on `street_width_class` exercises only the module's attested/unattested
COULD_NOT_CHECK behavior, not R5 legal semantics (real `max_building_height` is
street-width independent). `pc-rear-yard-demo` and `pc-residential-far-demo` are retained
deliberately to prove the semantic gate holds even when a rule produces a number.

## Snapshot (`snapshots/pc-demo-synthetic.snapshot.json`)

The shared synthetic source snapshot the fixture rules cite (provenance for the evaluator's
export invariant). Synthetic; not an official capture.
