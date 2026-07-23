_Verbatim independent code-reviewer return, ROUND 2 (post legal-semantics correction; transport entity-decoding only). Orchestrator-recorded; reviewer performed no git/ledger writes._

# GATE REPORT — M4-T006 (G3 re-review, code)

**Task:** M4-T006 — R5/R5A height & setback rules; targeted legal-semantics correction
**Gate:** G3 (independent code review), re-review after correction
**Reviewed SHA (frozen):** `5d605d4` on `task/M4-T006-r5-height-setback` (PR #88/#89 lineage)
**Prior passing SHA:** `6509db3` (G3 PASS)
**Reviewer role:** independent, read-only (ADR-005)
**Verdict:** **PASS** (final acceptance remains gated on G6)

## Scope reconciliation (important non-blocking note)

The orchestrator brief states `git diff --name-only 6509db3 5d605d4` "must be exactly" the 2 correction files. **That raw command actually returns ~70 files, NOT 2** — because the branch merged `origin/main` at commit `8c53433` (already-accepted M0-T022 owner-dashboard, product-map, tooling, and M0-T022/M4-T006 gate/report ledger files) between the two SHAs. This is expected and benign, verified as follows:

- `6509db3` is a clean ancestor of the merge `8c53433` (`git merge-base --is-ancestor` → YES).
- The merge `8c53433` touched **no** r5 files: `git diff --name-only 6509db3 8c53433 -- <r5 rule/test/r5a files>` is empty.
- The correction commit `5d605d4` vs its parent `8c53433` is **exactly** the 2 files.
- Restricting the full range to code: `git diff --name-only 6509db3 5d605d4 -- services/api/app/ packages/` returns only `r5_setback.rule.json`; the whole-range `services/api/` delta is exactly the 2 target files.

So the substantive code delta is exactly the claimed 2-file correction; the extra files are previously-accepted `main` work merged in.

**Worktree HEAD note:** the worktree is checked out at `0830454`, one commit *past* `5d605d4`. That extra commit touches only `project-control/` (G2 self-check re-record, legal-semantics proof, state.json, task.json) — the r5 rule and test files are byte-identical between `5d605d4` and `0830454` (`git diff --stat` empty). Full-suite evidence captured at `0830454` therefore validly reflects the frozen code.

## The two-file delta (verified sound, honest, non-regressive)

**1. `services/api/app/rules/rulesets/r5_setback.rule.json`**
- Relabels `required_setback_depth` output + `setback_depth_by_street_class` param note as the **STANDARD UNMODIFIED minimum starting** depth under §23-423, explicitly "Never the final legally applicable setback."
- Adds always-on exception `section_23_423_modifications_unresolved` (`"condition": null`, `"effect": "documented_limitation"`, `"citation_ref": "zr-23-423"`) describing the section's unevaluated reductions/modifications (street-wall beyond min front yard with a **7 ft floor**, recesses/outer courts, >50 ft or qualifying-orientation optionality, dormers) → modified/final setback **UNRESOLVED**, professional review.
- Adds a matching `limitations[]` note.
- **No dimensional value changed:** `{"wide": 10, "narrow": 15}` intact. No change to `applicability`, `computation`, `outputs` mapping, or the other two conditional exceptions. Status unchanged: `"status": "needs_review"`, `"rule_version": "0.1.0-draft"` — `verified` remains unreachable.

**2. `services/api/tests/rules/test_r5_height_setback.py`** — one new parametrized test (wide/narrow = 2 cases) asserting the marker is present in `trace.exceptions_applied`, `effect == "documented_limitation"`, and the marker text contains `"standard unmodified"` and `"never be presented as the final"`. Assertions are non-vacuous (checked against actual description strings).

## Correctness of the mechanism

- Evaluator `_apply_exceptions` (evaluator.py:194-209): `condition is None` → `holds = True` (always fires); the exception is appended to `exceptions_applied`; `documented_limitation` hits the fall-through branch (line 208 comment: "recorded as a note only; no coverage change"). Confirmed the marker **annotates without downgrading coverage**.
- This is byte-for-byte the same shape as the pre-existing R5A precedent `pitched_plane_setback_professional_review` (r5a_height.rule.json:57 — `condition:null`, `documented_limitation`, `citation_ref:"zr-23-421"`).
- Coverage genuinely unchanged: on the confident path (street_width supplied) base coverage stays `conditional`; when `street_width_class` absent the rule still fails closed to `professional_review_required` before exceptions run. The marker appears exactly on the confident path where 10/15 is emitted — the correct place to prevent it being read as final.
- **R5A (§23-421) unchanged:** `git diff --stat 6509db3 5d605d4 -- r5a_height.rule.json r5_height.rule.json` is empty (byte-identical).
- No evaluator, snapshot, coverage, contract, or other ruleset changed (`app/` + `packages/` delta = the one rule file only).

## Commands and outputs

- `git diff --name-only 8c53433 5d605d4` → exactly `services/api/app/rules/rulesets/r5_setback.rule.json` + `services/api/tests/rules/test_r5_height_setback.py`
- `git diff --name-only 6509db3 5d605d4 -- services/api/` → the same 2 files
- `python -m ruff check .` (from `services/api`) → `All checks passed!`
- `python -m pytest tests/rules/test_r5_height_setback.py -q` → `47 passed in 1.66s`
- `python -m pytest -k standard_unmodified -v` → `2 passed, 45 deselected` (new tests collected & passing)
- `python -m pytest -q` (worktree, code == frozen `5d605d4`) → `928 passed in 13.40s`

## Findings

- **Blocking:** none.
- **Non-blocking:**
  1. The "exactly 2 files" diff expectation in the brief does not literally hold for `6509db3..5d605d4` because of the intervening `origin/main` merge; the code delta is nonetheless exactly the 2 files (documented above).
  2. Reviewed the frozen `5d605d4` code via a worktree at `0830454` (one ledger-only commit ahead); r5 rule/test byte-identical — no impact.
  3. Pre-existing (out of this delta's scope): the 10/15 values remain "candidate pending raw-HTML verbatim verification and G6 approval" — correctly deferred to G6, not this gate.

**Verdict: PASS** at frozen SHA `5d605d4`. The correction is sound, honestly labeled, follows the established R5A precedent, changes no value or coverage, and its new tests genuinely assert the marking that prevents 10/15 from being presented as the final legally applicable setback. Final acceptance remains gated on G6.
