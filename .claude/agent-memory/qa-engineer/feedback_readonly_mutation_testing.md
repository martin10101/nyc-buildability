---
name: readonly-mutation-testing
description: How a read-only QA reviewer runs mutation testing without editing source — monkeypatch module globals at runtime
metadata:
  type: feedback
---

To judge whether a test is load-bearing vs smoke, run mutation testing. But a G3 reviewer here is **read-only** (must not edit implementation), so do NOT mutate the source file and `git checkout` it back.

**Why:** the run-quality-gate skill and ADR-005 forbid the reviewer editing implementation or running git/project_control; a mutated-then-reverted source file risks leaving the tree dirty and violates the read-only guard.

**How to apply:** write a standalone script in the scratchpad that imports the target module and monkeypatches its **module-global** helpers, then calls the public entrypoint and checks whether the test's core assertion would fail (mutant CAUGHT). This works because Python resolves internal helper calls (`cap = _positive_finite_float(x)`, `_json_safe_cap(...)`, `_copy_assumption(...)`) via module-global lookup at call time, so replacing `mod._helper` takes effect without touching the file. Restore the original in a `finally`. Confirmed on M5-T006 `services/api/app/scenario/derive.py` (2026-09-08): all 6 guards — LOW-1 null-cap, LOW-2 deepcopy no-alias, LOW-3 per-value + aggregate reason bounds, DERIVED-path golden, never-Verified — were provably caught. See [[probe-separator-deleting-normalizations]] for the other in-report evidence technique when a producer can't commit spans.
