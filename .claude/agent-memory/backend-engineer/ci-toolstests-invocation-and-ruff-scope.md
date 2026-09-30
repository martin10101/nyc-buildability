---
name: ci-toolstests-invocation-and-ruff-scope
description: How CI actually runs tools/ tests (direct __main__/unittest, NOT pytest) and that CI ruff only lints services/api, not tools/
metadata:
  type: reference
---

Verified at commit 7cc1fed reading `.github/workflows/ci.yml` (M0-T057).

**CI ruff scope is narrow.** The `api` job sets `defaults.run.working-directory: services/api`
and runs `ruff check .` — so **CI ruff lints only `services/api`, never `tools/`**. `tools/`
carries many pre-existing ruff findings (E702 semicolons, E401/E402 import placement, E741,
F841) that do NOT gate CI. When you touch `tools/`, ruff cleanliness of your *added* lines is
good hygiene but is not a CI gate; don't try to "fix" the pre-existing tools/ findings.

**The control-plane job runs tools tests DIRECTLY, not via pytest.** In `ci.yml` the job runs:
- `python3 tools/test_project_control.py` → executes its `if __name__=="__main__"` block, which
  loops a hand-maintained `ALL_TESTS` list. **A new `def test_*()` you add is invisible to CI
  unless you append it to `ALL_TESTS`** (pytest would collect it; the direct runner will not).
- `python3 tools/test_directive_compliance.py` → `unittest.main()`, which **auto-discovers**
  every `unittest.TestCase` subclass — so new test *classes* there need no registration.
- `python3 tools/validate_directive_compliance.py --check` → must be **EXIT 0**.

So: put function-style control-plane tests in `test_project_control.py` AND register them in
`ALL_TESTS`; put class-style tests in `test_directive_compliance.py` (auto-discovered).

**These tool suites are slow** (each test spawns real `git` subprocesses in temp repos):
`test_project_control.py` + `test_directive_compliance.py` together ~9–18 min. Run targeted
node-ids/`-k` while iterating; run the full pair once for evidence. Note: the Bash auto-mode
classifier sometimes blocks `-k` expressions (esp. containing "or" or words like "governance");
fall back to the explicit `file::test_name` node-id form. See [[env-producer-sandbox-no-exec]].
