---
name: gate-reproduce-producer-numbers
description: G4 lesson - always re-run the producer's self-check commands at the frozen reviewed SHA; producer report counts (modularity warnings, per-file test split, class count) drift from reality and must not be trusted as verbatim
metadata:
  type: feedback
---

At a G4/quality gate, re-run EVERY documented self-check command yourself at the frozen reviewed SHA
and compare the raw output to the producer report's "verbatim" numbers. Producer-reported counts
drift and are often slightly optimistic.

**Why:** M4-T015 (DCM street-width connector, gate 2026-09-13) taught this three ways in one report:
- Producer section 9 claimed `modularity_check.py --check` = "selected 399 files; failures 0;
  warnings 16" and that "neither new module appears in the warning list." At the reviewed SHA the
  real output was "selected 401 files; failures 0; warnings 17" and the new 959-line connector
  `dcm_street_centerline_arcgis.py` WAS listed: `review_signal: above the justification threshold;
  record a cohesion justification in review`. The modularity tool had not changed
  (`git log -- tools/modularity_check.py` newest = 5487b84a, pre-task), so the claim was simply
  inaccurate at the reviewed candidate, not stale-by-tool-change.
- Producer claimed the 131 new tests split 46 (connector) / 85 (classifier); `pytest --collect-only`
  showed 49 / 82. The total 131 was right; the split was wrong.
- Evidence map + commit message said "23 typed ambiguity classes"; the code's
  `AMBIGUITY_CLASS_DISPOSITIONS` tuple and the producer report table both have 24. Off-by-one.

None of these changed the PASS (all acceptance criteria reproduced green: 619 passed, 131 new,
modularity EXIT 0, ruff 0.13.0 EXIT 0), but a reviewer relying on the producer's narrative would
have missed a real modularity signal.

**How to apply:** Reproduce, don't read. When a "review_signal: record a cohesion justification in
review" fires on a large but genuinely cohesive module (single connector responsibility, separable
pure logic already extracted to its own module), the reviewer discharges the policy obligation by
recording the cohesion justification in the gate report - it is not a FAIL when the check exits 0
and the module is not a dumping ground. Flag the producer report's inaccurate counts as an ADVISORY
correction. See [[connector-override-fixture-isolation]].
