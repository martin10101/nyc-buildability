---
name: in-process-mutation-probe
description: Read-only mutation-sensitivity technique — exec a mutated copy of frozen source under its real package context without touching any tracked file
metadata:
  type: reference
---

To prove test mutation-sensitivity as a READ-ONLY reviewer (cannot edit the producer's
worktree source), execute mutated copies of the frozen module IN-PROCESS instead of
editing files:

```python
import types, sys
sys.path.insert(0, str(API))          # services/api so `app` imports
import app.scenario                    # ensure real package is importable
src = FROZEN.read_text()
mutated = src.replace(OLD_LINE, NEW_LINE)
mod = types.ModuleType("app.scenario._bk_mut")
mod.__package__ = "app.scenario"       # <-- makes `from ._json_safety import ...` resolve
exec(compile(mutated, "mut.py", "exec"), mod.__dict__)
mod.find_scenario_threshold(...)        # run the mutant; optionally mod.dep = fake_double
```

**Why:** the frozen module uses relative imports (`from .derive import ...`). Setting
`mod.__package__` to the real package lets those resolve while the mutant lives only in
`sys.modules` under a throwaway name — nothing on disk changes, so read-only discipline
holds and the producer worktree is never mutated.

**How to apply:** for each candidate mutation, `.replace()` one exact source line, run the
mutant against the same inputs the frozen tests use, and check whether the specific test
assertion flips (CAUGHT) or survives (MISSED). Load `tests/scenario/_support.py` via
`importlib.util.spec_from_file_location` so its `REPO_ROOT = parents[4]` resolves under the
frozen worktree and fixtures load. To exercise a doubled dependency, assign
`mod.derive_practical_usable_range = fake` on the mutant module object directly.

Build the AS-1 scenario doc with `build_scenario(S.profile(), S.canonical_rule_evaluation())`
(canonical R5 draft cap = 15000.0; utilization/efficiency factor in (0,1] → point = cap*factor).
