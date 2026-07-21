# M4-T002 — G3 code-reviewer verbatim return (frozen SHA 609efe9)

VERDICT: PASS (4 non-blocking findings F1-F4)

---

# Gate Report

- **Gate ID:** G3 (independent code review)
- **Task ID:** M4-T002 (rules-engine ↔ property-analysis integration, service layer)
- **Reviewer:** code-reviewer (independent; read-only)
- **Producer:** lead orchestrator
- **Result:** PASS
- **Clean environment/worktree used:** Yes. Worktree `.claude/worktrees/M4-T002-integration` at frozen SHA `609efe917ebfcedc3e0512bab5c4ed2b82e445b0` (branch `task/M4-T002-integration`); `git status --short` empty (no local modifications); base main `f2939d6`. Python 3.11.9, pytest 8.4.2, shapely present.

## Acceptance criteria reviewed

All six task hard requirements plus the RI-S1…RI-S8 acceptance pack. Confirmed the frozen implementation commit (`883fee0..609efe9`) touches ONLY the three allowed files and that no consumed read-only module was modified anywhere on the branch.

## Steps independently executed (commands + observed results)

1. `git diff --name-only 883fee0..609efe9` → exactly three files: `services/api/app/rules/integration.py`, `services/api/tests/rules/test_rules_integration.py`, `project-control/reports/M4-T002-producer-report.md`. No profile / spatial / contract / endpoint / UI file.
2. `git diff --name-only f2939d6..609efe9` (whole branch vs main) → the three files above plus only control-plane artifacts from the claim commit (`project-control/{gates/M4-T002-G0.json, reports/M4-T002-G0-readiness.md, state.json, tasks/M4-T002.json}`). None of `app/rules/{evaluator,models,coverage,registry,lifecycle,snapshots}.py`, `app/spatial/**`, `app/profile/wave_integration.py`, or `packages/contracts/**` was modified. `883fee0^ == f2939d6` (lineage confirmed).
3. `python -m ruff check app/rules/integration.py tests/rules/test_rules_integration.py` → **All checks passed!**
4. `python -m pytest tests/rules/test_rules_integration.py -v` → **23 passed** (RI-S1…RI-S8, incl. the 3 parametrized RI-S2 cases).
5. `python -m pytest -q` (full `services/api`) → **649 passed** (626 M4-T001 baseline + 23 new; no regression).
6. Code inspection of `integration.py` against `spatial/engine.py` (the `single_district_confident` invariant), `evaluator.py`/`registry.py`/`lifecycle.py`/`snapshots.py` (evaluator API + fail-closed provenance), and `wave_integration.py` (serialization fidelity the fixtures mimic).

Could NOT execute a bespoke adversarial Python script: this sandbox exposes no Write tool and blocks shell file-writes (`cat >`/heredoc) and `python -c`. This is not a blocker — the required ruff/pytest evidence all ran, and the specific edge cases below were verified by direct code inspection.

## Expected versus actual

- Confident R5, 10,000 sq ft → `max_residential_far=1.5`, `max_residential_floor_area_sq_ft=15000.0`, coverage `conditional` (not verified), one trace, citations resolve to `content_digest_sha256`, trace validates against the canonical evaluation-trace schema. **Matches** (test RI-S1).
- R5D 5,000 → FAR 2.0 / 10,000; geometry-absent fallback 8,000 → 12,000 via `spatial_intersection.pairs[].lot_area_sq_ft`. **Matches** (RI-S1).
- Every uncertain class (boundary_uncertain / sliver_ambiguous / split_lot_confident / invalid_geometry_review) and `data_conflict` → `professional_review_required` (or `data_conflict`) with `zoning_district=None` and `evaluations==[]`; share ranges preserved verbatim. **Matches** (RI-S2/RI-S3).
- No `verified` anywhere across confident, non-R5, absent, and conflict outcomes; disclaimer text containing "Verified" is not treated as a status. **Matches** (RI-S7).
- Same profile → byte-identical output, including a fresh `RuleRegistry().load()`. **Matches** (RI-S5).

## Regression / security / provenance findings

- **No regression:** full suite 649 passed.
- **Provenance fail-closed:** evaluator traces are taken through `result.export()` (integration.py:491), and `RuleResult.export()` (models.py:170-179) raises `ProvenanceError` unless every citation carries a resolvable `content_digest_sha256`; the snapshot store (snapshots.py:82-89) is tamper-evident. Genuine, not cosmetic.
- **Never-Verified is structurally unreachable:** `evaluate_property` calls `registry.evaluate(...)` with NO `g6_approval`; the evaluator only reaches `verified` for a `published` rule *with* a matching `G6Approval`. `assert_not_verified` (construction + export()) is a correct additional backstop checking only `coverage_status` FIELDS.
- **No hard-coded legal values in the reviewed module.** FAR magnitudes live in the accepted R5 rule DSL (needs_review), consumed read-only.
- **No guessed schema:** fixtures built from REAL app.spatial dataclasses serialized like wave_integration; RI-S8 drift guard asserts equality with the real constants.
- **No new endpoint/UI/contract; no secret/network/dependency/RLS/migration surface.** Nothing published or Verified.

**Core safety property — verified sound.** The only path to a computed value requires ALL of: `spatial_intersection` is a dict; `lot_overall_class == "single_district_confident"`; `professional_review_required == False`; exactly one `interior_confident` base-zoning pair with a non-empty string label — a strict subset of the engine's own emission rule, tightened further. Every other branch routes through `_fail_safe(...)` with `evaluations=[]`, `zoning_district=None`, `lot_area_sq_ft=None`. Determinism holds (`sorted(statuses)`, sorted-glob rule_ids, order-independent `most_severe`, no wall-clock/random).

## Defects

None blocking. All hard requirements (1–6) are enforced and confirmed.

## Required rework

None required. Non-blocking recommendations (fast-follow):

- **F1 — LOW (test net), integration.py:440.** The `or professional_review_required` fail-safe trigger is not pinned in isolation: every `professional_review_required=True` test also uses a non-confident `lot_overall_class`. Behavior correct by inspection. Recommend adding: `single_district_confident` + `professional_review_required=True` + one `interior_confident` pair → assert `fail_safe`, `zoning_district is None`, `evaluations == []`.
- **F2 — LOW (maintainability), integration.py:126,151.** `verified_status_present` is a hard-coded `False` that is exported but never wired to `assert_not_verified`; could be mistaken for a computed safety signal. Recommend removing it or deriving it from an actual scan.
- **F3 — LOW (defense-in-depth), integration.py:166-187.** `assert_not_verified` scans three fixed locations vs the test helper's recursive scan. Not exploitable today; a recursive guard would match the test's rigor.
- **F4 — INFO, integration.py:399.** A missing `lot_overall_class` fails safe, but a missing `professional_review_required` key defaults to `False`. Both keys always present in real records; strict class gate is load-bearing. Informational.

## Reviewer conclusion

Faithful, pure, deterministic, read-only bridge; district derived only from a genuinely confident lot (strict subset of the engine invariant); fails safe with no district/value on every missing/uncertain/conflict condition; provenance fail-closed; Verified structurally unreachable with a correct backstop. Scope clean (3 files; imports only). Ruff clean; 23/23 + 649 full suite pass, no regression. Findings minor/non-blocking; F1 is the most worthwhile fast-follow. Nothing published or Verified; acceptance remains coupled to M4-T001's outstanding G6.

VERDICT: PASS
