# M4-T004 — G4 (QA / regression) verbatim return

_Verbatim independent qa-engineer return (transport decoding only). Orchestrator-recorded._

**Task:** M4-T004. **Frozen SHA:** `3e45524` (base `58432cf`). **Reviewer:** qa-engineer (read-only). **Verdict: PASS.**

## Scope
Delta: 3 source files, 16 synthetic fixtures, 1 new test file (453 lines). Real corpus `app/rules/rulesets/` UNCHANGED — no real rule JSON touched.

## Commands (from services/api) — exact counts
| Command | Expected | Actual |
|---|---|---|
| `pytest tests/rules/test_rules_fh_safeguards.py -v` | 48 | **48 passed** |
| `pytest tests/rules/ -q` | 152 | **152 passed** |
| `pytest -q` (full api) | 742 | **742 passed** |
| `ruff check app tests` | clean | **All checks passed!** |

## Adversarial coverage — regression-meaningful
- **FH-1:** pre-fix `1<=month<=12 and 1<=day<=31` returned True for 2024-02-30/04-31/11-31/2025-02-29/2023-02-29; post-fix datetime.date fails them. The impossible-date test + evaluator fail-closed path test would BOTH fail pre-fix. Leap 2024-02-29/2000-02-29 stay valid (no over-tightening).
- **FH-3:** scalar non-iterables (5, 3.14) genuinely raised TypeError pre-fix and are covered; dict/str/tuple/0 are defensive/consistency coverage. Fail-closed intact: genuine verified still raises even with junk siblings.
- **FH-2 (core):** entirely new surface, so every FH-2 test fails against pre-fix by construction. Verified: typed+complete conflict (no outputs/determination); load-order independence (byte-identical forward vs reversed); overlapping-only-inside-overlap; non-overlapping never; half-open [from,to) boundary determinism (seam → exactly one governs); disjoint/mutually-exclusive → none; complementary different-output → none; cross-family → none; unknown family → None; integration conflict PRR + typed + NO value (evaluations==[]); deterministic across fresh registries; as_of inside → conflict / outside → normal single value (FAR 1.0/2.0, proving genuine as_of_date threading); never-Verified (recursive scan); strict-JSON; provenance preserved. applicability_satisfied fails closed on predicate errors.
- **Regression:** real R5 UNCHANGED — no conflict with/without as_of_date; rule_conflict is None; conditional; max_residential_floor_area_sq_ft==15000.0; additive rule_conflict:None key. Full suite (RI-S1..S8, C1-C3, M4-T003 hardening) green.

## Synthetic-fixture discipline
All 16 fixtures + snapshot labeled SYNTHETIC ("not verbatim from any source", "illustrative value", limitations require official capture + G6; snapshot source_id synthetic-test-fixture, urn:synthetic). No real legal content.

## Findings
BLOCKING: none. INFO-1: FH-3 parametrization mixes crash-regression scalars with defensive cases (not a defect). INFO-2: applicability_satisfied catches a fixed exception tuple; an unexpected type would propagate (low risk; consistent with fail-closed-to-no-conflict). INFO-3: no explicit shape-malformed-string FH-1 case (shape validation via _ISO_DATE_RE is pre-existing/unchanged; no gap for the claimed calendar-validation safeguard). No required negative control or invariant missing.

## VERDICT: PASS
