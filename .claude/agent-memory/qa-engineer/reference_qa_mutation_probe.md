---
name: qa-mutation-probe-technique
description: Read-only way to prove committed tests are load-bearing (not smoke tests) by mutating a scratchpad copy of the source under test
metadata:
  type: reference
---

To judge whether a committed acceptance pack actually asserts boundaries (vs. smoke-passing)
without editing the frozen reviewed worktree:

1. Copy the source-under-test file into the scratchpad; add a minimal shim module for its
   package-relative imports (e.g. rewrite `from .constants import X` to `from constants import X`
   and provide a stub `constants.py`).
2. In a scratchpad script, load the source text and build mutants via targeted string-replace
   (remove a guard, inject a hidden default, drop a fail-closed branch, silently skip instead of
   fail). `exec(compile(mutant, ...))` each into a fresh module.
3. Call the function on the same inputs the committed test uses and confirm the mutant flips the
   exact value the committed assertion checks (e.g. mutant makes derivable=False where the test
   asserts True). A caught mutant proves that assertion is load-bearing.

Applied on M5-T005 `services/api/app/scenario/derive.py`: mutants for no-underflow-fold,
hidden 0.85 default, never-Verified cap removed, and silently-skip-non-dict were all caught by
RT-6 / AS-1 / RT-5 / RT-4 respectively. Pairs with [[readonly-reviewer-bash-guard]].
