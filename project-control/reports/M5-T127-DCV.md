# M5-T127 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `3c08c8dac8565c84966eebad2c42ef323efb3ab8` (branch `task/wave2-lot-reach-overlay-reading-further-captures`, pull request 460, review copy `/root/project/rv-w2-1007a`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R227, R229, R238 (3 rows).

## Verdict: PASS for all 3 rows. No required correction blocks acceptance.

- **Each row is met for this task's share only, and the verifier says what is left.** R227: every reach has a test whose expected number is read from the reference case, not typed and not taken from the module; the angle between the two street lines is carried from the existing site geometry and, on the real lot, is checked only against the program's own value, which the module and the records say plainly. R229: every measurement the module cannot make is unknown with a reason, never a zero; showing "not known" on a screen, a drawing or the PDF is not done by this task, because nothing uses the module yet. R238: the module holds no legal distance and states no coverage figure; using these measurements to withhold or split the engine's present whole-lot corner answer is later work of the work order's Part 0. All three rows stay open in the registry.
- **How the wave was run (four points, all met):** the concurrency record was committed before any builder's commit; no two builders' commits touch the same file; three builders and at most five helpers, one heavy run at a time, one pull request, nothing built on unmerged work; the one shared read (this task's test reads the corner-reach case through a loader another task changed) holds at the frozen head.
- The task's test, run by the verifier: exit 0 (14 passed).
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head: the task's three files, the corner-reach case and its loader, and the three rows, the manifest and the sources they trace to unchanged; later commits only under `project-control/` and lines of `docs/DISCOVERY_BACKLOG.md`.
- Read by the orchestrator on 2026-10-07 at 08:16 UTC: the pull request's check list on `3c08c8da` showed 46 checks, all a completed success.
- What it could not check itself: the builder's and the reviewer's mutation proofs (made on temporary copies outside the repository; it worked the three made-up lots' reference values again with its own arithmetic instead, and they match); the pull request's base and checks (it does not run `gh`; it confirmed from git that the branch starts at the merge of the earlier wave). It did not run the registry validator (the second verifier ran it once at the same head) or the full api suite (the orchestrator's run at `2e60a66e`: 8128 passed, 8 skipped).

How the return arrived (2026-10-07): in two messages (part 1 alone at 08:12 UTC; the orchestrator asked the same agent for the rest at once; part 2 with the closing line at 08:13 UTC). Both are reproduced below unchanged (copied by script from the session transcript `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl`, lines 2768 and 2787; only the two-space indent the transport adds to every line was removed).

---

```
PART 1 of 2

Role: INDEPENDENT directive-compliance verifier (DCV) for task M5-T127 (lot-reach measurements), directive D-090. Frozen head `3c08c8dac8565c84966eebad2c42ef323efb3ab8`, review copy `/root/project/rv-w2-1007a`, branch `task/wave2-lot-reach-overlay-reading-further-captures`, PR 460. I produced none of this work or its records. I am an AI agent; this is an automated agent review, NOT a human or professional/legal review. I confirmed `git -C /root/project/rv-w2-1007a rev-parse HEAD` = the frozen head and the worktree is clean. `directive_registry.load_registry(...).evaluate_task_refs(task)` returns ok=True, applicable == cited == [D-090-R227, D-090-R229, D-090-R238], no missing/invalid/unresolved.

ROW M5-T127 D-090-R227: PASS
 - Each reach measurement has a test whose expected number is PARSED (regex) from `docs/reference-cases/R6B/cases/corner-reach.json` via the loader `load_row` in `services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py` (lines 134-156, which reads the authored file and fetches no program output); in `services/api/tests/spatial/test_lot_reach.py` lines 120-126 and 163-165 the expected values are never typed and never read back from the module.
 - I read the authored expected values directly in corner-reach.json: real-lot-reach 99.97/103.93/144.60 ft (line 92), C1 100.00/40.00/107.70 (237), C2 80.00/60.00/100.00 (382), C3 100.00/150.00/180.28 (544); I independently recomputed the three made-up rectangles myself (hypot and opposite-dimension) and got exactly 100/40/107.70, 80/60/100.00, 100/150/180.28 — the reference numbers are arithmetically sound and program-independent.
 - Running the test at the frozen head (14 passed, exit 0) reproduces that the module's own geometry (`_farthest_perpendicular` cross-product, `_farthest_distance` math.dist, lot_reach.py lines 121-130) equals those independent values within 0.01 ft; `test_expected_values_are_read_from_the_reference_case_not_the_module` (test lines 329-337) is a direct independence guard.
 - The one quantity with no reference value, the corner angle, is a pass-through: lot_reach.py line 223 carries `relation.angle_deg` from site_geometry, not derived here. Its independent test is the 90.0-degree synthetic-rectangle check (test line 184); the real-lot angle is only checked against the program's own site_geometry value (test line 147). The module docstring (lines 71-77, 218-220) and the producer report/review disclose this honestly; it is not weakened, so PASS.

ROW M5-T127 D-090-R229: PASS
 - Every failure path in `services/api/app/spatial/lot_reach.py` returns a SourcedValue with value=None and a plain reason, never a zero/default: not-confirmed and not-straight frontages (lines 161-171), and `_no_corner` for 0/1/>2 measured, no relation, or non-crossing lines (lines 148-150, 193-216); the top guard returns empty street_lines tuple + all-unknown corner on no-outline/refused (lines 238-240). I grepped the module: no bare default distance returned on any branch.
 - All seven unknown branches have passing tests in test_lot_reach.py (lines 192-300): refused outline, outline-present-but-geometry-refused, uncertain frontage, bending frontage, interior lot, through lot, more-than-two-streets — each asserts `.value is None`, `.label == LABEL_UNKNOWN` and a non-empty reason, never zero.
 - The "shown as not-known on website/drawings/PDF" portion is correctly out of this measurement-only task's share: `test_nothing_imports_the_module_yet` (test 317-323) and my grep (`lot_reach` referenced by no other file under services/api/app) confirm nothing consumes it. The evidence map states this is "NOT done by this task, and not claimed" — an honest scope note, not a weakening.

ROW M5-T127 D-090-R238: PASS
 - The module holds no legal distance: my grep of lot_reach.py found no "100", no "135", no "coverage", no "yard" (case-insensitive), and no `app.rules`/`app.scenario` import; `test_measurements_only_no_law_in_the_module` (test 306-314) asserts the same. So no result or test in this task states whole-lot 100% coverage.
 - Nothing imports the module (grep + test 317-323), so it cannot cause any coverage figure; the engine's present whole-lot corner answer is untouched. The evidence map says connecting these measurements to withhold/split coverage is "the next part of the work order's Part 0" — i.e. the R238 "100% vs not-known coverage test" obligation lives in the reference case (M4-T027, merged) and later connection work, left explicitly to later. For THIS task (supply the geometry, assert no coverage), satisfied and not overclaimed.

END OF PART 1
```

```
PART 2 of 2

Wave-execution checks (read `project-control/reports/WAVE2-2026-10-07-concurrency-record.md` and `git log` 4fc0d85c..3c08c8da):

W1 (concurrency record committed before any builder's commit): MET. The record `project-control/reports/WAVE2-2026-10-07-concurrency-record.md` was added in the contract commit `3a08b2c6` at 2026-10-07 06:43:02 (git show --name-status confirms the file is added there). The first builder commit is `6a977805` (M5-T127) at 07:05:57. 06:43:02 precedes all builder commits.

W2 (no two builders' commits touch the same file): MET. From `git log --stat`/name-status, the three disjoint file sets are: M5-T127 (`6a977805`,`5ce12d90`) = lot_reach.py, test_lot_reach.py, M5-T127-producer-report.md; M4-T028 (`4b04689f`,`d23f6faf`,`db11e7af`) = docs/reference-cases/R6B/** and services/api/tests/rules/reference_cases/** and its report; M4-T029 (`eba169c5`,`2e60a66e`) = docs/research/zr-snapshots/v1/** (new only), services/api/app/_zr_snapshots/v1/** (new), its report. No file appears in two sets; this matches the three packets' allowed_paths. M5-T127's test READS corner-reach.json and the loader; the loader was written only by M4-T028 and corner-reach.json by neither (read vs write, not a write-write collision).

W3 (at most three builders / five helpers, heavy runs one at a time, one PR, nothing on unmerged work): MET. The record names three builders (geospatial-engineer, rules-engineer, legal-corpus-engineer) + two readers, peak four then up to five, heavy run once by the orchestrator after integration, one PR (460). The branch base `4fc0d85c` is the wave-1 merge (parents a5c6c2f0 + 38e45791, "Merge pull request #459") and `git branch -r --contains 4fc0d85c` lists `origin/candidate/D-024-mrl-option-b` — the branch PR 460 merges into — so nothing is built on unmerged work. (I could not run `gh` to read PR 460's base directly; verified via git refs only.)

W4 (the one shared read re-checked after integration): MET. The loader `r6b_reference_cases_lib.py` was changed in this wave by M4-T028 (`4b04689f`, adding the "overlay-reading" case id); corner-reach.json was NOT changed in the wave (no commit touches it in 4fc0d85c..HEAD). I ran M5-T127's test at the frozen head against the integrated loader: 14 passed.

Test direct exit code: `cd services/api && python -m pytest -q -p no:cacheprovider tests/spatial/test_lot_reach.py` → 14 passed, DIRECT EXIT CODE 0.

Carry-forward condition (blob-level predicate): my three PASS verdicts and the W1-W4 findings may be stamped at a later head WITHOUT re-asking me iff ALL of these blobs are byte-identical to the frozen head `3c08c8da`: (a) the three M5-T127 allowed-path files services/api/app/spatial/lot_reach.py, services/api/tests/spatial/test_lot_reach.py, project-control/reports/M5-T127-producer-report.md; (b) docs/reference-cases/R6B/cases/corner-reach.json and the loader services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py; (c) the three requirement rows R227/R229/R238 in requirements.json, the D-090 manifest/digests, and the source files they trace to (source-032-amendment.md, source-033-amendment.md). I TOLERATE later commits that touch none of (a)-(c): specifically commits confined to `project-control/**` (the other two tasks' gate/report/task/state records, acceptance records, verification rows) and added lines of `docs/DISCOVERY_BACKLOG.md`, and a merge of this integration branch into `candidate/D-024-mrl-option-b` that introduces no change to (a)-(c). I verified the already-present gate-recording step preserves this: the diff 66803c5a(reviewed)..3c08c8da(frozen) touches only project-control/** and docs/DISCOVERY_BACKLOG.md, and the three M5-T127 files are identical from material head 5ce12d90 to HEAD.

Required corrections that BLOCK acceptance: none.

Non-blocking observations:
 - The corner angle is a pass-through carried from site_geometry; its only program-independent test is the synthetic 90.0-degree rectangle (test line 184); the real-lot angle is checked against the program's own derived value. Honestly disclosed in the module docstring, producer report and review; not a defect for a measurements-only module.
 - Producer-report check (b) records "12 passed" at the first material head `6a977805`; round 2 (`5ce12d90`) added two guard tests, so the current count is 14 passed. Consistent, not a discrepancy.
 - modularity_check.py --check at the frozen head: exit 0, failures 0; lot_reach.py (245 lines) raises no warning. Nothing imports the module (grep confirmed).

What I could not check myself:
 - The mutation proof (producer report item (e)) was run against a temporary copy OUTSIDE the repository, so I could not reproduce that exact run from committed files; I substituted my own independent arithmetic recomputation of the C1/C2/C3 reference values (matched exactly) plus running the in-repo independence-guard test. The reviewer's claim that it independently re-derived the real-lot reaches and did its own two mutation proofs is a CLAIM in M5-T127-G3G4.md I did not reproduce.
 - PR 460's merge base and CI status: I did not run `gh` (read-only); W3 rests on git refs only.
 - I did not run tools/validate_directive_compliance.py, tools/test_directive_compliance.py, or the full api suite, per instructions (the second verifier/orchestrator own those).

Overall: all three bound rows PASS on reproduced primary evidence; W1-W4 MET; test exit 0; no blocking correction.

END-OF-REPORT
```
