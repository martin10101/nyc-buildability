# M5-T185 producer report - R6B reference case benchmark-options-5-8-9-10

Producer: rules-engineer (AI agent). Documents and reference-case checks only; no rule file, engine,
result, capture, register entry, law-library edit or human verdict. This is a draft reading of the law
by AI helpers (ADR-007), not professionally reviewed; nothing here is Verified and no row reads as
complies/buildable/optimal/feasible.

Worktree: /root/project/nyc-buildability/.claude/worktrees/agent-acd0b1b29bf3050b7
Contract/claim head reset to: fdfd2749261366dfb219710c69e0dc25235f69ab (task/wave27-comparison-appendix).

## What was built
One new R6B reference case, `benchmark-options-5-8-9-10` (49 rows), built from six sealed readings
(option 5 = provenance -26/-27; option 8 = -28/-29; options 9-10 = -30/-31) copied unchanged below a
truthful header, plus the shared comparer -25 (reused unchanged, frozen by M5-T184). Wired in through a
new step-P10 module behind one thin entry into check.py (3 lines); the three cross-case digests a new
case moves were recomputed; options 4 and 11 are named as owed; owner questions N1 (option 8) and N2
(option 10) are kept open.

## The rule of agreement, applied per row
A value is recorded only where BOTH readings of that option family give it on the same value and the same
basis and the comparer confirms it AND every cited section is captured in docs/research/zr-snapshots/v1.
Where they differ, where one says not known, or where the captured text does not settle a point, the row
is NOT SETTLED with both readings' words and the kind of its gap. The comparer adjudicates and is never a
value source. Capture-now-but-reader-hedged policy (Risk 5): where BOTH readings affirmed the same value
and the only divergence was that the section was not among the captures when they read (now captured by
M3-T010), RECORD (opt9-10 23-51; opt8-A 23-371; opt9-10 use permission 22-12/22-121/22-122). Where ONE
reading left the item not known (opt5 storey-limit 32-421; opt8-B whether 23-12 binds), it stays NOT
KNOWN even though the section is now captured. The JUDGE's REQUIRED correction is applied: opt8-B
"minimum lot area/width not binding" is NOT KNOWN (reader B left it not known; one reading only); the row
records only what both affirm (each half about 5,037.5 sq ft and about 50 ft wide) with the 23-12
thresholds (2,375/25; 1,700/18) in prose.

### Rows RECORDED as a value (settled on both readings; captured section)
Option 5: opt5-retail-use-grade (UG VI, 32-161, use-permission caveat), opt5-commercial-far (2.00,
33-121 plural tables -> quote-only, table_assertion null), opt5-residential-far (2.00/2.40, 23-22
table_assertion R6B), opt5-combined-cap (greatest single use 2.00, 35-31), opt5-max-total-floor-area
(20,150 = 2.00 x 10,075, 35-31/23-22), opt5-dwelling-units-baseline (29 = 20,150/680, 23-52),
opt5-heights (30/45/55; 65 qual, 23-432 table_assertion R6B std), opt5-setback-above-base (10 wide/15
narrow, 23-433), opt5-front-and-side-yard (none / none-or->=5 ft, 34-231 + 23-335, recorded as unchanged
vs option 1 per advisory A1), opt5-vs-option-1 (no extra FA; shops reduce residential FA/units).
Option 8: opt8-option1-baseline (20,150/29/30-45-55), opt8a-fa-shared (20,150, no gain), opt8a-units-
shared (29, no gain), opt8a-min-distance (40 ft < 125 ft, 23-371 plural tables -> quote-only, condition
from the text per A3), opt8-subdivision (a recorded legal act, 12-10 zoning-lot), opt8b-fa-per-half
(10,075 each / 20,150 total; 10,075/2=5,037.5, 2.00x5,037.5=10,075), opt8b-units-per-half (15 =
10,075/680), opt8b-heights (30/45/55).
Options 9-10: opt910-rooming-unit-residential (12-10 rooming-unit + 23-22), opt910-use-permission (UG II;
22-122 bar reaches only R1-R5; 22-12/22-121/22-122; use-permission caveat), opt910-residential-far
(20,150 = 2.00 x 10,075, 23-22), opt910-no-680-factor (680 does not apply to rooming units; no ZR unit
ceiling, 23-51, draft), opt910-room-size-minimum (set by MDL/HMC, outside ZR; 12-10 rooming-unit),
opt910-transit-zone (Outer, a recorded dataset value; 12-10 Transit Zone Outer; 25-241 does not reach
this lot's community district), opt10-parking-rooming-units (0, 25-221), opt910-standard-du-parking-
crosscheck (29 x 25% = 7.25 <= 15 Column C -> 0, 25-222 plural tables -> quote-only), opt910-bicycle-
parking (1 per 2 DU-equiv, 3 rooming = 1 DU, waived <=10; 25-80/25-811; count not computable),
opt910-loading (none for residences, 36-62 plural tables -> quote-only), opt910-heights (30/45/55),
opt910-conversion (rooming -> dwelling, 54-311), opt910-vs-option-1.
Shared: both-readers-did-not-have (prose list), options-out-of-scope (options 4 and 11 owed).

### Rows kept NOT SETTLED (kind not_known), with the kind of gap
- opt5-storey-limit: one reading only (reader A applied 32-421; reader B left it not known pending the
  capture). Kind: unresolved reading - the two-reading rule is unmet even though 32-421 is now captured.
- opt5-commercial-rear-yard: both readers left the depth beyond 100 ft not known (33-26 + 33-301 corner
  waiver cited). Kind: a missing fact about the property (lot geometry beyond the corner reach).
- opt5-lot-coverage-whole-lot: per-portion maximum, no single whole-lot figure (23-362). Kind: unresolved
  law + missing portion areas.
- opt5-overlay-mapped-line: mapped overlay line not read (76-131 named in prose only). Kind: a missing
  fact about the property.
- opt5-select-commercial-overlay-status: neither reading recorded a value; the now-captured 12-10
  definition names C2-2 but is noted in prose only. Kind: unresolved reading.
- opt5-street-wall-final-line: overlay routes to 35-631(b) but the final line turns on the prevailing
  street wall frontage (not had). Kind: a missing fact about the property.
- opt8a-windows-courts: 23-372 and 23-35x apply but values depend on footprints/heights (design inputs).
  Kind: a missing fact about the property.
- opt8b-aggregate-dwelling-units: both compute 15+15=30 vs 29 (draft +1) but both call the lawfulness
  "not sure" (shown only as a labelled draft in the reason, per advisory A4). Kind: unresolved law.
- opt8b-coverage-by-half: which half holds the corner turns on the division geometry (23-362). Kind: a
  missing fact about the property.
- opt8b-interior-half-rear-yard: a new required rear yard (23-342), depth not known pending lot-line
  kinds/street line. Kind: a missing fact about the property.
- opt8b-min-lot-area: JUDGE correction - one reading only on whether 23-12 binds; both affirm each half
  about 5,037.5 sq ft / about 50 ft wide; thresholds in prose. Kind: unresolved reading.
- opt8-which-meaning (N1): both meanings worked, neither chosen. Kind: open owner question.
- opt910-rooming-vs-dwelling-classification: an applicant/use determination gating density and parking.
  Kind: a missing fact / an agency determination.
- opt10-distinct-meaning (N2): options 9 and 10 reach the same parking answer; the difference is a
  product decision. Kind: open owner question.
- opt910-shared-housing-framework: the operating framework is pending 2027 legislation, not enacted.
  Kind: unresolved law / pending legislation.
- real-lot-missing-facts: the zoning lot (NB-01), the lot-area basis (NB-04), the division geometry, the
  overlay line, the use classification, the room standard, all eligibility.

## Point-by-point comparison per option (where the readings differ or hedge)
- Option 5: both agree on commercial FAR 2.00, residential 2.00/2.40, the 35-31 greatest-single-use cap
  (no stacking), 20,150 sq ft, 29-unit baseline, 30/45/55 ft, 10/15 setbacks, UG VI retail. Divergences:
  storey-limit (A applied 32-421, B left not known -> NOT SETTLED); front/side yard (B cited 34-231/23-335,
  A recorded the envelope as unchanged -> recorded as "unchanged vs option 1" per A1); commercial rear
  yard (both not known beyond 100 ft); select-commercial-overlay status (both not known).
- Option 8: both agree meaning A gives 20,150/29 shared with no gain and 40 ft spacing, and meaning B gives
  10,075/half (20,150 total) with 15 units/half and 30/45/55 ft, subdivision a recorded act. Divergences:
  the aggregate +1 (both call lawfulness "not sure" -> NOT SETTLED, draft in reason); whether 23-12 binds
  (A "not binding", B not known -> NOT SETTLED per the judge); which meaning (N1). The 23-371 40 ft is
  prose, not a table value (A3); plural-tables sections 23-371/23-12 carry table_assertion null.
- Options 9-10: both agree rooming units are residential at FAR 2.00/20,150, 23-51 removes the 680 factor
  (no ZR unit cap; a draft reading of the "this Section" referent), Outer Transit Zone, 0 parking for
  rooming units (25-221), the 25-222 standard cross-check (7.25 <= 15 -> 0), bicycle rule, no loading,
  30/45/55 ft, conversion (54-311). Both leave the rooming-vs-dwelling classification and the operating
  framework unresolved; option 10 vs 9 is a product decision (N2). The use-permission sections 22-12x and
  32-121 and 23-51/54-311 were read live when the readings were made and are now captured by M3-T010.

## Provenance (six new files, saved unchanged below a truthful header; -25 reused unchanged)
Each header supplies the literal phrase "sealed folder", carries its distinctive marker, states the method
truthfully (read-only detached checkout at bb5c02b9; some official ZR pages read live for sections not then
among the captures) and does NOT claim "no outside access"; each ends END-OF-REPORT. Pinned sha256 (raw
bytes of the saved file):
- -26 bb19e6f0398ff6640c471d65e2eac86afa2ab670c45955fb55bab8996b83c246
- -27 ed085e6e1921f86c0c65a49625f9f628a5bb8d6787a37bc438320d8105b37460
- -28 2e2f0f1d7f65bacaa7e8b0ac56934e57f45b2fc440b947d463b57714ff9cb9a5
- -29 285c427b78999009d6b2f74e551f21425d5c45d5b44d019b0f3996e31fbed6ee
- -30 6dbe12c7fbeb39ae58a2726af0aa8888c79ae60e865c83f2606eec6e2f2127f5
- -31 5066be9f12b3cdf7966fd6c3899dabbe499e5c202ef8febfb93bb7dc90f724c3

## Consumer pins moved and why
A new case changes every cross-case "all cases except mine" blob, so three digests were recomputed; the
literal CASE_IDS tuple and REQUIRED_BASE_IDS/CASE_IDS in lib were extended; the README gained a row:
- lib.CASE_IDS: appended "benchmark-options-5-8-9-10" (14th); test_r6b_reference_cases.py literal tuple
  appended to match.
- lib.REQUIRED_BASE_IDS: new entry listing all 49 row ids (S1 coverage).
- test_r6b_reference_cases_step_p7.py PRIOR_ROWS_DIGEST -> 74a7b99d7324521d7c8fea5bf3910292f1174a1eee7caea5c6ad5c4199ea23d2
- test_r6b_reference_cases_step_p8.py OTHER_CASES_DIGEST -> 964a5adccda38e0a39f0573cec340ebb65e1a1a7f3c501a4e5dfdf042ae4b314
- test_r6b_reference_cases_step_p9.py PRIOR_CASES_DIGEST -> 41e004d2fe0421e3034b2aa98bbf165cbeaa47d35b6b96a8cdfcf710faf356a7
- test_r6b_reference_cases_step_p10.py OTHER_CASES_DIGEST (own blob, excludes my case) = 0699424e0a7b8e48818845800185b5e1f0bb6908e28b763afb182146a1df79a9
- step_p6 REACH_ROWS_DIGEST: NOT moved (corner-reach rows only). No len(CASE_IDS)==N count pin exists.
- check.py thin wiring: +3 lines (import step_p10; step_p10.case_errors in validate_case;
  step_p10.reading_digest_errors in provenance_errors). check.py now 597 lines (< 600); step_p10 400 lines.

## Checks (lanes venv; PYTHONDONTWRITEBYTECODE=1; pytest -p no:cacheprovider; from services/api; heavy runs under flock heavy-run.lock)
- a. `python -m ruff check .` -> exit 0 (All checks passed).
- b. `flock ... python -m pytest -q -p no:cacheprovider tests/rules/reference_cases` -> exit 0 (212 passed in 2.87s).
- c. `python tests/rules/reference_cases/r6b_reference_cases_render.py --check` -> exit 0 (PASSED, no issues).
- d. `python3 tools/modularity_check.py --check` -> exit 0 (812 files; failures 0; warnings 33, none for the
  changed files; check.py 597 lines, step_p10 400 lines, both < 600).
- e. `python3 scripts/lanes/check_lane_paths.py --coverage` -> exit 0 (LANE COVERAGE PASS: 10676 files).
- f. `flock ... python -m pytest -q -p no:cacheprovider` (whole api suite) -> exit 0 (9984 passed, 8 skipped,
  1 warning in 462.13s).

## Mutation proofs (each applied to the committed case JSON, validator run, then restored; validator clean before and after)
1. changed value: opt5-max-total-floor-area arithmetic result 20150 -> 20151 => RED
   ("recomputes to 20150.00 but the case records 20151"). Restored.
2. one-reading row: opt5-commercial-far source_reference drops -27 => RED ("an option row must name BOTH its
   readings"). Restored.
3. uncaptured citation: opt910-residential-far citation snapshot -> zr-76-131 (not in captures) => RED
   ("capture file missing: ... zr-76-131.snapshot.json"). Restored.
4. NOT KNOWN turned into a value: opt8b-aggregate-dwelling-units kind value => RED ("the two readings do not
   jointly settle this, so it must be 'not known', not 'value'"). Restored.
5. dropped owed-options row: options-out-of-scope removed => RED (coverage: the work order's row is not
   present under its id). Restored.
Baseline before and after: `render.py --check` exit 0 (PASSED).

## Assumptions / limitations / doubt
- Agreement of two AI readings is not proof; nothing is Verified; every figure stays conditional on the
  zoning lot (Z1, NB-01), the lot-area basis (10,075 recorded, NB-04; GIS 10,387.99 never mixed), and
  eligibility. The comparer is an adjudicator, not a value source.
- The readers' "NOT CAPTURED" notes reflect the pre-M3-T010 state when they read at bb5c02b9. I verified
  against the actual captures at the claim head: every section recorded as a value (and every section cited
  on a not-known row) is physically present in docs/research/zr-snapshots/v1 with its content_digest_sha256,
  request_url and verbatim_excerpt matching the citation (the checker enforces all three). Genuinely-absent
  sections (76-131, 33-27/33-28/33-30, 23-154, 74-902/903, 22-131..135, 77-xx, MDL/HMC) and the image-map
  Appendix I appear in prose only and are never a value basis or a formal citation.
- opt910-standard-du-parking-crosscheck and opt910-bicycle-parking record the standard-DU/rule cross-checks
  the readings drew; they are not the rooming-unit answer (which is 0 parking by 25-221) and no rooming-unit
  count is computed (the ZR sets no unit ceiling for rooming units).
- render.py is in allowed_paths only as safety and was left byte-identical (no change); the page .md was
  produced by render.py so it is byte-identical to render_page.
- No push, no ledger CLI, no server, no ports touched. Report saved under project-control/reports/ for the
  orchestrator's submit --report; findings also returned to the orchestrator.
