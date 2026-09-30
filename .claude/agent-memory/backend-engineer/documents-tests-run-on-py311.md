---
name: documents-tests-run-on-py311
description: services/api documents/** app+tests run locally on the 3.11 sandbox EXCEPT PEP-695 modules; keep new modules 3.11-clean to self-test
metadata:
  type: feedback
---

The sandbox Python is 3.11 but repo targets 3.12. Most `services/api/app/documents/**`
modules and their tests are 3.11-collectable and RUN locally; only the PEP-695 modules
fail collection (e.g. `units.py` line 276 uses the `type`/generic syntax → `SyntaxError:
expected '('` on 3.11, cascading to test_units/test_promotion/test_survey_pipeline/etc).

**Why:** the blanket memory "pytest cannot collect PEP-695 on 3.11" is true only for the
PEP-695 files; state.py/promotion.py/models.py/correction_history.py/taxonomy.py and their
tests are plain 3.10+ union syntax and execute fine.

**How to apply:** when writing NEW documents modules, avoid PEP-695 `type X = ...` and
`class C[T]` / `def f[T]` so the module AND its tests stay 3.11-importable — then you can
run real local evidence: `python -m pytest tests/documents/<yours>.py -q` and, for the
whole subset, `python -m pytest tests/documents/ -q --continue-on-collection-errors`
(548 passed + 15 pre-existing PEP-695 collection errors as of M2-T016). `ruff 0.13.0` is
already installed in the sandbox (`ruff check app/documents tests/documents`). This let
M2-T016's backend slice ship with 181 locally-passing tests instead of CI-only evidence.
Run pytest/ruff from the WORKTREE's `services/api`, never the shared checkout (git redirect
is refused).
