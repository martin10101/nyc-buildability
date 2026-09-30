---
name: controller-update-repin-lockstep
description: Re-pinning tools/controller_update/source_binding.json must move THREE files in lockstep or test_runbook_parse.ps1 goes red; and the offline ps_tests suite can't run from an isolated agent
metadata:
  type: project
---

Re-pinning the controller install source is NOT a one-file edit. A consistent re-pin of
`tools/controller_update/source_binding.json` (`commit_sha`/`commit_tree_sha`/`subtree_tree_sha`)
must move THREE files to the SAME sha in the same reviewed commit:
1. `tools/controller_update/source_binding.json` (`commit_sha`);
2. `docs/CONTROLLER_UPDATE_RUNBOOK.md` Section 4 (hardcodes the sha in prose, ~line 84);
3. `tools/controller_update/ps_tests/test_runbook_parse.ps1` `$pinnedSha` (hardcoded, ~line 26).

`test_runbook_parse.ps1` asserts `binding.commit_sha == runbook text == $pinnedSha` (all equal).
Miss any of the three and that test ASSERT-FAILs, and the fail-fast `run_ps_tests.ps1` driver
(alphabetical; test_runbook_parse is 6th of 7, before test_source_binding) stops there.

**Why / how to apply:** M0-T160 (2026-09-24) re-pinned only the binding (a5886dab→a3f24ff3) with
the runbook + test as forbidden_paths — so AS-3 ("suite passes") was unsatisfiable and the suite
was ALREADY red (the runbook + test still named the Amendment-46 `3f4cee86` after two prior re-pins
`e0dd4a3a`/`a5886dab` never updated them). If you scope a source_binding re-pin, include all three
files or expect a scope gap. The other six ps_tests build fixture bindings in `$env:TEMP` and are
independent of the live pin.

**Running the ps_tests offline:** every fixture internally runs `git init`/`git commit` on temp
repos, so a worktree-isolated agent's sandbox refuses ALL `powershell -File .../run_ps_tests.ps1`
("what it reads ... cannot be shown not to run git"), even though the tests are temp-only and safe.
Route the run to the orchestrator / a non-isolated session as a harvest. See [[env-producer-sandbox-no-exec]].
