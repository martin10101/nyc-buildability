# Wave 18 (2026-10-09; written 08:32 UTC) - concurrency record: M5-T145, one task of four parts built side by side

Written by the orchestrator before any builder of this task is started (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** D-090 row R773 (the owner's request of 2026-10-09 that long tasks be broken up or that several agents work in the same task on different parts) and the owner's recorded limits (at most three builders and four reviewers at once; never the same file; heavy runs and merges one at a time).

**Why one task with parts, not four tasks.** The owner named both ways. One task keeps one set of gates and one review over four small modules that are all checked against the same independent example (`docs/reference-cases/R6B/cases/step-p6-worked.json`). The parts share no file and none imports another.

**Who builds what (three builders, each a rules-engineer agent in its own worktree, each from the claim head, each making ONE commit):**

- Builder 1: PART A. `services/api/app/spatial/corner_reach_area.py`, `services/api/tests/spatial/test_corner_reach_area.py`, `project-control/reports/M5-T145-part-A.md`.
- Builder 2: PART C. `services/api/app/scenario/three_answers/first_building_options.py`, `services/api/tests/scenario/three_answers/test_first_building_options.py`, `project-control/reports/M5-T145-part-C.md`.
- Builder 3: PARTS B and D. `services/api/app/scenario/three_answers/lot_coverage_by_portion.py` and `preliminary_apartment_estimate.py`, their two test files under `services/api/tests/scenario/three_answers/`, `project-control/reports/M5-T145-part-B.md` and `-part-D.md`.

No path appears twice. No builder changes an existing file. The producer report is assembled by the orchestrator from the part reports.

**At the same time, and not a builder:** the wave-17 pull request (481) goes through its checks, its pre-merge check and its merge on its own branch; no builder touches that branch. **One at a time, by the orchestrator:** the three cherry-picks, the focused checks on the integrated head, the one push, and any merge. No full suite runs on the build machine: that is CI's.

**Recorded afterwards** in the task's review record: each builder's run time and whether any part had to wait for another.

**Added at 08:38 UTC (scope correction before any builder returned):** PART E, the review register follows the four new modules. ONE builder (a rules-engineer agent), started only AFTER parts A to D are integrated, from that integrated head: `services/api/app/rules/review_register/register.json`, the rendered files under `docs/zoning-rule-review/` (`REGISTER.md`, `HISTORY.md`, `calculations/`, `evidence/`), `services/api/tests/rules/test_zoning_rule_review_register_calculations.py` only where an assertion must move, `project-control/reports/M5-T145-part-E.md`. It shares no path with parts A to D and never runs beside them.
