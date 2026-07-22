# M4-T004 — Producer report

Task: **M4-T004 — pre-endpoint fail-closed safeguards FH-1/FH-2/FH-3.** Producer: rules-engineer
(dispatched); integrated + validated by the orchestrator. Frozen submit SHA **`3e45524`** (branch
`task/M4-T004-safeguards`, off main `58432cf`, pushed). Not accepted; no merge.

## What was built (additive; three allowed source files + synthetic tests)
- **FH-1** `evaluator.py::_valid_iso_date` — true `datetime.date(y,m,d)` calendar validation in
  try/except ValueError. Impossible dates (2024-02-30, 2024-04-31, 2025-02-29 non-leap) fail closed to
  `professional_review_required`; genuine leap 2024-02-29 stays valid; non-string/None unchanged. Added
  helper `applicability_satisfied(rule, inputs)` (fail-closed: a malformed predicate → not applicable).
- **FH-3** `integration.py::assert_not_verified` — `evaluations` iterated via `_as_list(...)` and
  `family_coverage` gated by `isinstance(dict)`, so a foreign non-list/non-dict payload fails safe
  instead of raising TypeError, while still raising DraftVerifiedError on any genuine `verified` status.
- **FH-2** `registry.py::detect_rule_conflicts` + `RuleRegistry.detect_conflicts` + integration
  `_conflict_result` / `PropertyRuleEvaluation.rule_conflict` / additive `as_of_date` threading —
  strictly fail-closed same-family conflict DETECTION per `M4-T004-FH2-SPEC.md`. A conflict requires all
  of: same family/output domain; simultaneously in effect (half-open `[effective_from, effective_to)`)
  for the same valid `as_of_date`; each independently applicable to the same inputs; competing for ≥1
  shared OUTPUT name. Returns a typed, deterministic (sorted → load-order-independent) object with
  competing rule IDs + effective windows; produces NO output/determination value; preserves district +
  provenance; coverage `professional_review_required`. NEVER selects/ranks/merges/supersedes/
  reinterprets. NOT a rule_series redesign; no endpoint.

## Placement / determinism / boundary (as required by the spec)
Detection lives in `registry.detect_rule_conflicts` (needs the family's rules + `is_in_effect` +
`output_names()`), called from `integration.evaluate_property` after concrete `inputs` +
`input_provenance` are built and before the per-rule eval loop (applicability + as_of are known there).
Determinism: `contested` output names sorted; competing rules keyed by `rule_id` then sorted; per-rule
`output_names` sorted — identical result under any load order. Boundary: half-open
`[effective_from, effective_to)` (from inclusive, to exclusive); at a seam exactly one rule governs → no
conflict.

## Negative controls (proven not to trigger)
Different families; non-overlapping windows; mutually-exclusive applicability; complementary
different-output rules; boundary dates. The real single-rule R5 `residential_far` family never triggers
FH-2; `as_of_date` defaults to None = prior behavior (regression: FAR 1.5 / 15000 unchanged).

## Scope / provenance
Only `evaluator.py`, `registry.py`, `integration.py` + `tests/rules/**` (new
`test_rules_fh_safeguards.py` + 16 SYNTHETIC fixtures under `fixtures/m4t004*` clearly labeled, no real
legal content). `models.py`/`coverage.py`/`lifecycle.py`/contracts/lock/manifest/scripts untouched.
Nothing Published/Verified.

## Evidence
- `ruff check app tests` clean; `pytest tests/rules/test_rules_fh_safeguards.py -v` = 48 passed;
  `pytest tests/rules/ -q` = 152 passed; `pytest -q` = 742 passed.
- Frozen `3e45524`: all 12 CI checks green (web-e2e flaky a11y focus-timing test re-run green;
  `M4-T004-ci-evidence.md`).

## Gate status
G0 PASS. Independent G3 (code) PASS, G4 (qa) PASS, G5 (security) PASS at `3e45524` (verbatim reports
`M4-T004-G{3,4,5}-*.md`). One consistent non-blocking INFO recorded as **FH-4** in
`M4-RULES-FUTURE-HARDENING.md` (route `as_of_date` through `_valid_iso_date` in conflict detection before
public endpoint exposure — already fail-closed today). Not accepted; no merge.
