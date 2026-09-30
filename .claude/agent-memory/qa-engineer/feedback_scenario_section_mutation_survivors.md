---
name: scenario-section-mutation-survivors
description: G4 adequacy heuristic for services/api scenario-document section tasks (M5-*) - the two mutants that routinely survive their acceptance packs
metadata:
  type: feedback
---

When gating a `services/api/app/scenario/*` section task (the C1 `unused_floor_area.py`
pattern; M5-T017 and successors), two adequacy gaps recur even when S1-S6 all pass:

1. **Exact-0 INPUT boundary untested.** Producers use paired guards
   `_positive_finite_float` (cap) vs `_nonnegative_finite_float` (existing area). The
   0-boundary is the ONLY thing that distinguishes them. Packs test the negative side
   (e.g. bldgarea -1 -> unusable) and the zero-RESULT side (bldgarea == cap -> 0), but
   NOT the zero-INPUT side (bldgarea == 0, a vacant lot -> computed, value == cap). So the
   `_nonnegative -> _positive` one-char mutant survives, silently breaking the vacant-lot
   case (the product-central "full unused floor area" headline). Always check for an
   exact-0 input test.
2. **Rounding mutant survives integer-only fixtures.** The canonical trace cap is
   15000.0 and helper bldgareas are round (cap-5000, cap-100, 10000), so every remainder
   is an integer. A `round(value)` mutant survives despite the "unrounded" invariant in
   S1/S6. Check that at least one computed assertion uses a fractional remainder.

**Why:** repo culture treats "an invariant with no test that exercises it" as a first-class
defect (see the recurring convergence lesson). These two are the concrete instances for
scenario sections.

**How to apply:** on any scenario-section G4, grep the test file for a bldgarea/input of
exactly `0` and for a non-integer expected remainder before concluding adequacy. Their
absence is a real (usually advisory, occasionally blocking-for-acceptance) coverage gap
even when the code is correct and all packet scenarios pass. Related: [[probe-separator-deleting-normalizations]].
