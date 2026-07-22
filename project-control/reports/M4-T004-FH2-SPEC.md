# M4-T004 — FH-2 authoritative spec (owner directive 2026-07-22)

FH-2 is **strictly fail-closed**. It MAY detect ambiguity and return `professional_review_required`,
but it MUST NEVER select, rank, merge, supersede, or reinterpret competing legal rules. It is not a
`rule_series` redesign and does no endpoint work.

## Trigger — a genuine conflict requires ALL of:
1. The rules belong to the **same rule family / output domain**.
2. They are **simultaneously in effect** for the **same valid `as_of_date`**.
3. They **independently match the same normalized property inputs** (each rule's applicability is
   independently satisfied by the inputs).
4. They **would otherwise compete for the same evaluation decision** (same output(s) — not
   complementary rules producing different outputs).

## Negative controls — these MUST NOT conflict:
- **Different rule families** → no conflict.
- **Non-overlapping effective windows** → no conflict.
- **Mutually exclusive applicability** (only one matches the inputs) → no conflict.
- **Complementary rules producing DIFFERENT outputs** → not competitors, no conflict.
- **Boundary dates** must behave deterministically (a rule effective_to boundary and the next rule's
  effective_from must resolve deterministically — define and test the exact inclusivity used by
  `is_in_effect`).

## On a genuine conflict:
- Return a **typed, deterministic conflict** object containing the **competing rule IDs and their
  effective windows** (effective_from/effective_to).
- Produce **no legal value** from those competing rules (no outputs, no determination).
- **Preserve provenance** (the usual provenance/citation discipline is not bypassed).
- Coverage = `professional_review_required` (fail closed); **require professional review**.
- **Never** silently choose the first-loaded or highest-version rule. Ordering of rules must not change
  the outcome (deterministic regardless of load order).

## Placement / scope
Producer chooses the minimal correct placement within `allowed_paths` (evaluator.py / registry.py /
integration.py). The conflict test depends on inputs (applicability) + `as_of_date` (temporal) +
output-domain overlap, so detection generally belongs where the family is evaluated against concrete
inputs. Do NOT modify coverage.py/models.py/lifecycle.py, contracts, rule JSON, or lock/manifest.

## Required adversarial tests (deterministic, synthetic fixtures)
Malformed dates; impossible dates (FH-1); malformed evaluation containers (FH-3); **rule ordering**
(same conflict regardless of load order); **overlapping vs non-overlapping windows**; **disjoint
applicability**; **cross-family** rules; **complementary different-output** rules; **boundary dates**;
strict-JSON (`allow_nan=False`) on the conflict trace; provenance preserved; never-Verified holds
(a conflict is PRR, never verified). Full services/api suite stays green.
