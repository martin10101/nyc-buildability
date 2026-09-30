---
name: mutation-nonvacuity-check
description: How to prove regression-lock tests are non-vacuous during a read-only G4 gate (in-process monkeypatch mutation, no repo edit)
metadata:
  type: feedback
---

When a G4 packet asks whether a regression test "would actually fail if the behavior regressed"
(e.g. "would test 3 fail if append silently repaired?"), do not settle for reading assertions.
Prove it empirically without violating reviewer read-only discipline: write a scratchpad script
that imports the REAL module, monkeypatches the fixed function back to its PRE-FIX form
in-process, then runs the target test module via `unittest.TextTestRunner`. If the tests turn
RED, they are non-vacuous.

**Why:** reviewer must never edit implementation source (ADR-005 read-only). `git checkout`-based
mutation is also blocked — a worktree-isolated reviewer's git can't target the code worktree
(`C:/Users/MLFLL/Downloads/nyc-zoning/orch`). Monkeypatching the imported class/function at runtime
touches no file and is pure read-only observation.

**How to apply:** reconstruct the pre-fix body from the `git diff` of the implementation (the diff
shows exactly what was added). Patch at the module attribute the tests import through
(e.g. `al.AuditLog._load_head_from_log = prefix_fn`, `lp.approve_pending_prompt = prefix_fn`).
Load tests with `loader.loadTestsFromName("tools.test_module.ClassName")`. Expect the REPORTING
tests (verify_chain / status surface) to stay GREEN and the FAIL-CLOSED / refusal tests to turn
RED — that partition itself confirms the tests target the right behavior. Applied on M0-T046
(audit-fork lock: 4/6 red; park-approve binding: 2/3 red, happy-path stays green because re-hash
== anchor on a match). Run the target files 3x to confirm determinism. See
[[in-regime-accept-mechanics]] for the surrounding gate flow.
