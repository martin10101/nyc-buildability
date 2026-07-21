# M4-T003 — G0 Definition-of-Ready reconciliation

- Gate ID: G0 (administrative readiness, orchestrator)
- Task ID: M4-T003 — Rules-engine correctness hardening (fail-closed input & predicate validation, temporal versioning, compliance determinations)
- Recorded by: orchestrator
- Result: PASS (ready to start; lead-only)

## Why this task now
Owner launch-readiness review (2026-07-21) returned a **no-go for public launch** and directed that the
M4-T001 rules engine be corrected and independently re-reviewed **before any G6** and **before the
M4-T002 integration is merged**. The findings were independently verified against the code on `main`
(`f2939d6`) before this task was opened:

- **Confirmed — negative / non-finite numeric inputs produce bad values.** `evaluator.py` gates required
  inputs only on `is None`; `operations.py` `_nums` accepts any `int|float` incl. negatives / `NaN` /
  `inf`, so `lot_area_sq_ft = -5000` → `floor_area = -7500`.
- **Confirmed — predicate references are not validated at load (fail-open).** `dsl.py._check_refs`
  validates computation refs but never walks the `applicability` / `exceptions[].condition` predicate
  trees, so a misspelled predicate input silently evaluates to `None` → `False` → the rule becomes
  `not_applicable` with no error.
- **Confirmed — a non-numeric required input crashes** with `EvaluationError` instead of a typed outcome.
- **Confirmed — enum inputs are not validated** against their declared `enum` at evaluation time.
- **Nuanced — "applies and fails"** requires a compliance-style rule (the R5 rule only computes a
  limit), and a genuine **effective-date transition** requires temporal rule-versioning the engine does
  not have. The owner chose the **broader corrective wave**, so both capabilities are in scope here.

## Scope (owner-selected: broader corrective wave)
1. **Fail-closed input validation** — validate type / declared enum / numeric finiteness / optional
   declared numeric domain (min/max) before computation; a required-or-supplied invalid value → typed
   `professional_review_required`, NO computed value, NO crash.
2. **Predicate-reference validation at DSL load** — every applicability / exception-condition predicate
   input must be a declared input, or the rule fails to load.
3. **Rule test/lifecycle release status in the trace** — deterministic-tests + independent-review + G6
   state; `verified_eligible=false` for a draft.
4. **Effective-date temporal rule-versioning** — `effective_from` / `effective_to`; evaluation accepts
   an `as_of` date and selects the version in effect (or a visible not-effective outcome); proven by a
   synthetic before/after amendment-transition fixture.
5. **Compliance determination capability** — a rule may test a proposal input against computed outputs
   and emit a genuine applies+passes / applies+fails determination; proven by a synthetic fixture.

## Readiness checks (2026-07-21, base main `f2939d6`)
- **Dependency M4-T001 (engine):** on main (`de88ba2`, PR #76), status `awaiting_gate`. Its code is the
  subject of this hardening. M4-T001 is NOT accepted; this task's corrections are exactly the work the
  owner requires before its G6/acceptance.
- **File scope:** `services/api/app/rules/**` (evaluator, dsl, operations, models, engine-owned schemas,
  rulesets + a synthetic temporal/compliance fixture) and `services/api/tests/rules/**`; the producer
  report. Engine-owned rule/trace schemas are extended **additively**; the canonical
  `packages/contracts/**` are untouched. No new endpoint/UI. Nothing published/Verified.
- **No blocker required.** G6 (human) remains the standing gate before any rule is Published/Verified;
  this task ships only `needs_review` / non-Verified draft behavior, all fail-closed.
- **Thin-client:** local checkout + CI; negligible disk (no bulk data).

## Scope binding
Producer: lead-only (rules-engineer label; no producer subagent dispatched). Reviewers (independent,
after a frozen SHA + CI): code-reviewer (G3), qa-engineer (G4), security-reviewer (G5). Required gates
G0/G2/G3/G4/G5.

## Verdict
**G0 PASS** — ready. Implement lead-only, freeze a SHA, run CI, dispatch G3/G4/G5 once at the frozen
SHA, and return the evidence packet before merge. Do not merge without owner authorization; M4-T002
integration is rebased onto this corrected engine afterward.
