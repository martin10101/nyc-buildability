---
name: massing-model-inprocess-mutation-harness
description: How to prove each new massing_model guard reddens via an in-process whole-module mutation (the technique reviewers accept for massing_model)
metadata:
  type: feedback
---

To prove a new fail-closed guard in `services/api/app/scenario/massing_model.py` is
mutation-sensitive, use a whole-module TEXT mutation injected into the CONSUMING
namespace — do not rely on line-editing the real file.

**Why:** Most massing_model guards are line-level (a boundary clause, a charge-before-scan
order, a decorator's `except` class) that a monkeypatch cannot express; and the module's
own tests import symbols FROM the module, so a mutation must be visible to those imports.
The G3/G4/G5 reviewers verify guards exactly this way, so matching the technique makes the
producer report's mutation table reproducible.

**How to apply:** Per mutant, in a FRESH interpreter (one subprocess each): read the module
source, apply a string replacement (assert `src.count(old) == 1` so no silent no-op),
build a `types.ModuleType("app.scenario.massing_model")` with `__package__="app.scenario"`,
put it in `sys.modules["app.scenario.massing_model"]` AND set `app.scenario.massing_model`
BEFORE the test imports, `exec(compile(src, path, "exec"), mod.__dict__)`, purge every
`sys.modules` key containing `"massing_model"` (this also drops the test module), then
`pytest.main([... "tests/scenario/test_massing_model.py::<target>"])`. Baseline (unmutated
source injected) MUST be GREEN (faithful harness); every mutant RED. A clean scratch script
`mutate_verify.py` with a `{name: [(old,new)], targets}` table runs baseline + all mutants
in a loop. Monkeypatch DOES work for one case: `_preview` (bounded echo) is resolved from
the module namespace at call time, so `monkeypatch.setattr(mm, "_preview", lambda v,limit=...: repr(v))`
is a clean unbounded-echo mutant. See [[massing-model-input-guard-ordering]].
