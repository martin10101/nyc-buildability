# Rebase capsule — M4-T007 producer (PR #101)

**You are a producer, not the controller.** Your implementation is in good shape; your single red check was a
**suspected unrelated transient**, not a defect in your work. Your job: rebase onto current main and re-verify.

## Finding (controller, independent)
Your only failing check was one Playwright accessibility-focus test in `a11y-announcements.spec.ts` (web-e2e).
The controller **re-ran the exact same head** with no changes and it **PASSED** (both runs green) — so this is
recorded as a suspected unrelated transient in a frontend path **outside your allowed scope**. You correctly did
NOT modify `apps/web/**` (and must not). All your API/rules/math checks were already green.

## Your action
1. **Rebase** `task/M4-T007-decimal-legal-arithmetic` onto current `origin/main` (post-#99 merge).
2. **Do NOT touch `apps/web/**`** or any file outside your allowed paths (`services/api/app/rules/{operations,evaluator,units}.py`, `services/api/tests/rules/`, your report).
3. Rerun your complete local verification after the rebase (the existing rules-engine suite + your new
   `test_decimal_legal_arithmetic.py` / `test_units_exact.py`), push a new head, and obtain **green final-head CI**.
   If the a11y web-e2e flakes again on your rebased head, note it — it is a controller-owned frontend/CI matter,
   not yours to fix; do not dismiss a *repeatable* failure, but an isolated re-passing flake is not your defect.

## After you go green
Reply here with your new head SHA. The controller will independently verify at the rebased head: that the
`Fraction`/rational arithmetic satisfies the permitted "Decimal/rational" contract, that the differential
recomputation is genuinely independent, that no legal comparison has a binary-float decision path, and that the
unit/rounding limitation does not contradict AS-4 — then run G3/G4/G5 and accept. **B-014 is resolved only if the
accepted implementation actually satisfies exact legal arithmetic.**

## Boundaries
Do not merge, accept, replan, or operate another worktree. One PR (#101 stays; you push a new head). Stop only for
a real owner/legal/credential/security/destructive/impossible-acceptance condition.
