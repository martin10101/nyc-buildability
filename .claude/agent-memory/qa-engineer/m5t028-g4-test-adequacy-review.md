---
name: m5t028-g4-test-adequacy-review
description: 2026-09-14 M5-T028 G4 test-adequacy gate PASS w/ NB-1 (generic-fallback text untested on 4/5 sibling modules) - worked example of the full independent-verification method
metadata:
  type: project
---

M5-T028 (derive the ZR section reference in five live-wired scenario-analysis modules instead of
hardcoding "ZR 23-21", D-059-R003 completion) got an independent G4 PASS from me on 2026-09-14, review
target `99f9b277` / material commit `7e7cd85e`.

**Why:** this was a real, non-trivial test-adequacy charge (12 new tests across 5 modules, a changed
optional-parameter signature, a grep-based regression guard) that needed genuine independent
reproduction, not a read-through. Full method used: [[isolated-worktree-pinned-sha-review]].

**What I found, for calibration on future similar tasks in this repo's scenario/ package:**
- RED-on-old reproduced exactly: 7 failed / 5 passed against pre-fix code, and the 5 that passed were
  exactly the 5 "names_the_low_density_section" tests (their expected value coincidentally equals the
  old hardcoded default) — a legitimate, disclosed pattern, not a weak test, AS LONG AS the paired
  R6-R12 test for the same site fails on old code (it did, in all 5 cases).
- Non-blocking finding (NB-1, not blocking): the task's own acceptance text ("follows the evaluated
  rule or is generic") implies a generic-fallback assertion is wanted per surface, but only `derive.py`
  had one; the 4 sibling modules' identical fallback ternary was correct by direct source read and
  exercised (no-crash) by pre-existing EMPTY-path tests, but never assertion-checked for TEXT content.
  Judged non-blocking because the grep-based no-hardcode test (proven non-vacuous by mutation) already
  guards the specific regression this task exists to prevent, even inside a broken fallback branch.

**How to apply:** if a future task in this `scenario/` package adds another per-surface derived label
with a "derived-or-generic" fallback contract, check specifically whether EVERY surface (not just the
first/reference one) has a content-level assertion for the generic branch, not just a no-crash exercise
via an existing EMPTY/INVALID-outcome test.
