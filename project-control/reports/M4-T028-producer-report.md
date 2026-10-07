# M4-T028 producer report — the independent reading of the commercial-overlay text, written into the R6B reference cases

Producer: rules-engineer (isolated worktree `/root/project/nyc-buildability/.claude/worktrees/agent-a21702592cf616f5b`).
Contract head reset to `cc30ab1884cdb6541c41f0d759ebe198f91a6f46`. Directive D-090 R226/R241/R259/R291/R318; gap K9; DB-168.

Nothing in this work comes from a program run. No capture, rule file, engine, register, plan, helper-research file
or other test was changed. All values rest on the two sealed-folder step-P2 readings; a value is recorded only
where both readings agree on the same basis, otherwise the row is "not known" and names both.

## Files written

New:
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-5.md` — step-P2 reading 1, saved unchanged below a short header (the raw return is byte-for-byte below the `---`). sha256 of the whole file `3f7cd65e125ac4343a8a01660e549e49a38113dfc815cab053815df1beec3ff6`.
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-6.md` — step-P2 reading 2, same pattern. sha256 `2c3d3c3df850735d5a72d1e2bd1e0590dea690c48908838107173e7b5824a426`.
- `docs/reference-cases/R6B/cases/overlay-reading.json` — the new case (11 rows).
- `docs/reference-cases/R6B/overlay-reading.md` — rendered from the data file.

Edited:
- `docs/reference-cases/R6B/cases/interior-lots.json` — DB-168 wording correction + two ZR 23-362(b) citations + change-log entry.
- `docs/reference-cases/R6B/cases/real-lot.json` — case-level "does not establish" pointer to the new overlay case + change-log entry (no row value changed).
- `docs/reference-cases/R6B/README.md` — the cases list, the provenance line, and the "steps P1 and P2" law-text section (step P2 captured; what the overlay readings found still missing).
- `docs/reference-cases/R6B/interior-lots.md`, `docs/reference-cases/R6B/real-lot.md` — re-rendered from their data files.
- `services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py` — `overlay-reading` added to `CASE_IDS` and `REQUIRED_BASE_IDS`.
- `services/api/tests/rules/reference_cases/r6b_reference_cases_check.py` — `OVERLAY_READINGS` digest-pin + `overlay_reading_errors()` (shared `_reading_digest_errors` helper); `CASE_READINGS`/`READINGS_DIFFER` generalised to two-reading cases; `NOT_CAPTURED_SECTIONS` extended (23-435, 23-436, 23-41, 34-21, 34-22, 34-23, 35-64, 35-71, 36-64).
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases.py` — `CASE_IDS` tuple + `NOT_KNOWN` updated; 6 new overlay tests.

Support-file line counts (each < 600): check 520, lib 263, render 290, test 482.

## Rows added (case `overlay-reading`) — each a comparison of the lot WITH the C2-2 overlay against the same lot WITHOUT it (plain R6B)

Value rows (both readings agree on the same basis):
- `bulk-regulations` = same as plain R6B: R6B bulk governs via ZR 34-11 → 34-111; neither 34-111 exception (a)[R1-R5] nor (b)[R1-R2] reaches R6B.
- `floor-area-ratio` = same as plain R6B: captured overlay texts add no FAR; ZR 23-22 R6B = 2.00 standard.
- `lot-coverage` = same as plain R6B: captured overlay texts add no lot-coverage rule; ZR 23-362 governs. (Records the whole-lot-vs-per-portion difference in "does not establish"; asserts no whole-lot percentage; L5 unchanged.)
- `dwelling-units` = same as plain R6B: captured overlay texts add no DU rule; ZR 23-52 factor 680. (Count not asserted; ~29 at 10,075 sq ft, ~30 at 10,388 sq ft — conditional on the unresolved lot area.)
- `base-and-building-height` = same as plain R6B: 30/45/55 ft (standard) via ZR 34-24(b)(1) → 35-63 → 35-632(a) → the same ZR 23-432 R6B row plain R6B uses.
- `setback-above-base` = same as plain R6B: 10 ft (wide, Northern Blvd) / 15 ft (narrow, 215 Place) via ZR 35-632(a) → the same ZR 23-433.
- `street-wall-location` = **changed by the overlay**: from the R6B line-up of ZR 23-431(a) to the percentage rule of ZR 35-631(b) (≥70% within 8 ft of the street line), via ZR 35-63 and 35-633(a).
- `rear-yard` = same as plain R6B for an all-residential building: ZR 35-53 reaches only the residential portion of a mixed building; within 100 ft of the corner no rear yard (ZR 23-344(a)).
- `paragraphs-applicable` = which paragraphs apply/do not: 34-111 neither (a) nor (b); 34-24 (b) yes / (a) no; 35-632 (a) governs, (b) no [letter suffix], (c) no [R9-R12]; 35-631 (b) governs, (a) no [R8-R12 Manhattan Core], (c) no [needs 40,000 sq ft], (d) all districts.
- `not-captured` = the sections and defined terms the overlay texts point to that are not captured (34-21/22/23, 36-64, 35-71, 35-64, 23-434, 23-435, 23-436, 23-41; Manhattan Core, prevailing street wall frontage, mixed building) and what stays not known.

Not-known row (the two readings differ / one not known):
- `section-35-633` = **not known**. Both readings read the substance of what 35-633 adds as not known because Section 23-436 is not captured; and they differ on the ZR 35-633(b) corner-lot clause (see "where the readings differ").

Every citation quotes captured law only, with `snapshot_id` and `content_digest_sha256`; the checker confirms each quote is in the live capture and each digest matches.

## Rows / text changed in existing cases (no expected value changed)

- `interior-lots.json` row `interior-coverage` — expected value UNCHANGED (`80 percent`). DB-168 wording correction: the sentence "a different maximum also applies to lots of 30,000 sq ft or more" (too broad) replaced with what the captured ZR 23-362(b) says — the different maximum applies only to zoning lots "with buildings utilizing the eligible site provisions of Section 23-434" ("65 percent on zoning lots with a lot area of 30,000 square feet or more that are not large sites", 50 percent on large sites), not to every lot of that size. Two ZR 23-362(b) citations added (the eligible-site stem and the 65-percent/30,000-sq-ft clause). Change-log entry added, reason "a corrected reading".
- `real-lot.json` — no row value changed. The first "does not establish" item extended to point to `cases/overlay-reading.json` (overlay changes only street-wall location; other residential limits same as plain R6B). Change-log entry added. Row L5 deliberately left "not known" with its per-portion reason (per the packet's instruction that a whole-lot overlay-reading coverage figure does not change L5).

Scope note (disclosed, left unchanged): `interior-lots.json` case-level `what_it_does_not_establish[1]` carries a similar "does not apply to lots of 30,000 sq ft or more" phrase. DB-168 names only the row `interior-coverage` sentence and the packet says "ONE WORDING CORRECTION", so the case-level sentence was left unchanged; flag for a future packet.

## Where the two readings DIFFER

- Row `section-35-633` (what ZR 35-633 adds): reading 1 (return-independent-hand-calculation-5.md, Q3d) reads the ZR 35-633(b) corner-lot clause as NOT KNOWN because whether a Commercial District is mapped along the entire block frontage is not in the record; reading 2 (return-independent-hand-calculation-6.md, Q3d) reads that clause as not biting on the recorded facts because it is for a zoning lot "bounded by only one street line" and this lot has two frontages. Both agree the Section 23-436 substance itself is not known. The row is "not known" and names both; no winner picked, no reading of my own added.
- A residual-scope difference (not a value disagreement): reading 1 carries a bounded caveat that ZR 34-11's uncaptured Sections 34-21 through 34-23 could modify FAR, coverage or the rear yard; reading 2 treats the captured route as settled. Both give the SAME bottom-line value ("same as plain R6B"). The value rows record the agreed overlay effect (the captured overlay texts add no such rule) and disclose the 34-21..23 residual in "does not establish" and in the `not-captured` row.

## What stays "not known"

- `section-35-633`: what ZR 35-633 adds (Section 23-436 not captured; corner-lot clause read differently).
- Not asserted (recorded as conditional/withheld, not as the overlay answer): the whole-lot coverage percentage (L5 per-portion reading governs); the dwelling-unit count (unresolved lot area); the rear yard beyond 100 ft of the corner (plain-R6B reading, real-lot L12); absolute above-grade heights (base plane not captured); whether a prevailing street wall frontage exists; the 2.00-vs-2.40 FAR and 55-vs-65-ft height choice (needs a qualifying-housing fact).
- Named uncaptured sections/terms the overlay texts point to: ZR 34-21, 34-22, 34-23, 36-64, 35-71, 35-64, 23-434, 23-435, 23-436, 23-41; Manhattan Core, prevailing street wall frontage, mixed building.

## Checks — each run one at a time, direct exit code

All under `services/api` cwd with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`, except (d) from repo root.

- (a) `python -m ruff check .` — exit 0 ("All checks passed!"). (One E501 on a new test line was fixed, then re-run clean.)
- (b) `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases` — exit 0, **43 passed**. Targeted `-k "overlay or both_readings or readings_differ"`: 9 passed, 34 deselected.
- (c) renderer check mode `python tests/rules/reference_cases/r6b_reference_cases_render.py --check` — exit 0 ("reference-case check PASSED (no issues)"); pages byte-identical to the data (6 pages).
- (d) from repo root: `python3 tools/modularity_check.py --check` — exit 0 (716 files; failures 0; 29 pre-existing warnings, none on the four support files). `python3 scripts/lanes/check_lane_paths.py --coverage` — exit 0 ("LANE COVERAGE PASS: 8920 file(s)").
- (e) two mutation proofs on a temporary copy of `overlay-reading.json` OUTSIDE the repo (`scratchpad/tmp-overlay/`), exit 0:
  - Proof 1: one changed quoted law phrase in row `floor-area-ratio` → `citation_errors` returns "the quoted words for 23-22 are not found in the capture zr-23-22" and names `overlay-reading/floor-area-ratio`. PASS.
  - Proof 2: row `section-35-633` (readings differ) given a value → `readings_differ_errors` returns "the two readings differ here, so it must be 'not known', not 'value'" naming `overlay-reading/section-35-633`. PASS.
  - Control: the unmutated temporary copy validates clean (`validate_case` → `[]`). PASS.

The full `services/api` pytest was NOT run by me (the orchestrator runs it once on the wave's final candidate).

## Assumptions / limitations

- The two readings are from `/root/project/lanes-runtime/owner-docs/session-2026-10-07a/return-reading-P2-1.txt` and `-2.txt`, saved byte-for-byte below a header; digests pinned in the checker.
- Reading-5 marker "ONE HARD RULE" and reading-6 marker "ONE-HARD-RULE COMPLIANCE" are the distinctive strings each reading carries; both files carry "sealed folder" and END-OF-REPORT.
- Modularity: the new overlay logic (~45 lines) kept `r6b_reference_cases_check.py` at 520 lines, under the 600 warning threshold, so it stayed in the existing module per the packet's note; no new module was needed.
- No capture was re-read or re-fetched; all quotes are exact substrings of the already-committed snapshots (step-P2 captures from M4-T026 and the earlier residential captures).

## Doubt

- The case-level `interior-lots.json` `what_it_does_not_establish[1]` sibling phrase is the same DB-168 pattern but not named by the directive; left unchanged (flagged above) to honour "ONE WORDING CORRECTION". A reviewer may wish to decide whether it should be corrected in a later packet.
