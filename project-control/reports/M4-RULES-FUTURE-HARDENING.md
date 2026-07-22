# M4 rules-engine — explicit future-hardening items (before public endpoint exposure)

Owner directive (2026-07-21 corrective wave): the following two known, non-blocking
limitations from the M4-T003 / M4-T002 gate reviews are recorded here as explicit
future-hardening items. Both are safe today (fail-closed, no fabricated value, no crash),
but **must be resolved before any public rules-evaluation endpoint / UI exposes these
results to untrusted callers.**

## FH-1 — Impossible-calendar-date acceptance in `as_of_date` validation
- **Where:** `services/api/app/rules/evaluator.py` → `_valid_iso_date`.
- **Current behavior:** validates `YYYY-MM-DD` shape + month 1–12 + day 1–31. It therefore
  *accepts* calendar-impossible days (e.g. `2024-02-30`, `2024-04-31`, `2024-11-31`).
- **Why safe now:** temporal effectiveness is a lexical string comparison in `is_in_effect`,
  so a syntactically-valid non-existent date still orders deterministically, produces a real
  coverage status, fabricates no value, and never raises. The fail-closed goal (reject
  non-ISO / non-string `as_of_date`) is met. Flagged LOW / INFO by G5, G3, and G4 round-2.
- **Future fix:** tighten to true calendar validation (`datetime.date(y, m, d)` in a
  `try/except ValueError`) so an impossible date fails closed like any other malformed input.

## FH-2 — No same-applicability overlapping-effective-window guard (`rule_series`)
- **Where:** `services/api/app/rules/registry.py` → `RuleRegistry.effective_rules` (and rule load).
- **Current behavior:** `effective_rules` returns **all** in-effect rules for a family and
  documents that the caller must disambiguate; there is deliberately **no** naive family-wide
  overlap guard (a naive guard would wrongly reject legitimate multi-district families that
  coexist across an overlapping window when distinguished by applicability — G4-L1 "Do NOT do").
- **Why safe now:** `evaluate()` gates per-rule on applicability; there is no consumer today that
  silently picks one of several in-effect rules, so no mis-evaluation can occur. Flagged as a
  documented limitation by G4 round-1/round-2 (INFO-2).
- **Future fix:** introduce a `rule_series` grouping (same-applicability temporal versions) and a
  precise guard that rejects only a true overlap **within a series** — i.e. two rules that would
  both apply to the same inputs over an overlapping effective window — while still permitting
  distinct-applicability rules to share a window.

## FH-3 — `assert_not_verified` iterates `evaluations` without a list-guard
- **Where:** `services/api/app/rules/integration.py` → `assert_not_verified`
  (`for trace in data.get("evaluations") or []`).
- **Current behavior:** if a caller passes a *foreign* payload whose `evaluations` is a truthy
  non-iterable (e.g. a scalar), the guard raises `TypeError` there rather than iterating.
- **Why safe now:** the internal producer always emits `evaluations` as a list; the guard is only
  ever called on payloads this module built (at construction and in `export()`). Flagged as a
  non-blocking carry-forward INFO by G3 and G5 round-2 — the same robustness class as FH/LOW-1 but
  in the downstream-safety guard rather than the spatial-container helpers.
- **Future fix:** apply the same `_as_list`-style coercion (or an `isinstance` list-guard) inside
  `assert_not_verified` so a hostile foreign payload fails safe instead of raising, once the guard is
  exposed to untrusted callers at the public endpoint.

Neither item blocks the current service-layer slice (no endpoint/UI; results are draft
`needs_review`, never Published/Verified). All three are prerequisites for the future
property-analysis endpoint + UI task.

## FH-4 — `detect_rule_conflicts` gates temporal effectiveness lexically (consistency)
- **Where:** `services/api/app/rules/registry.py` → `detect_rule_conflicts` uses `rule.is_in_effect`
  (lexical string comparison) directly rather than routing `as_of_date` through FH-1's
  `_valid_iso_date` calendar validation.
- **Why safe now:** independently confirmed by G5/G3/G4 (M4-T004): every reachable path with an invalid
  `as_of_date` resolves fail-closed — a conflict at most surfaces `professional_review_required` with no
  value, and the `evaluate_property` eval loop separately routes an invalid `as_of_date` through the
  evaluator's `as_of_invalid` guard (PRR, no computation) before any value is emitted. The real corpus is
  single-rule so FH-2 never triggers. Raised as a non-blocking INFO by all three M4-T004 gates.
- **Future fix (before public endpoint):** validate `as_of_date` via `_valid_iso_date` at the
  `evaluate_property`/`detect_conflicts` boundary so an impossible date fails closed identically on both
  the conflict-detection and single-rule paths (belt-and-suspenders; today they already both fail closed).
