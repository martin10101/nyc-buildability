# M4-T035 producer report

Producer: rules-engineer (an AI agent), in the isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a1debe94914432518`.
Claim-seam head: `b416cf0d154400ebf1dcaaabc199da4f4e25bc40`.

The independent reading of the 46 newly captured Zoning Resolution texts (tasks M4-T033 and
M4-T034), written into the R6B reference cases as a new step-P5 case. Documents, their data files and
their test support only — no rule file, no engine code, no result, no register entry, no human
verdict. Every value comes only from the two step-P5 readings
(`provenance/return-independent-hand-calculation-11.md` and `-12.md`), recorded where both give it on
the same basis; otherwise "not known"/"not sure" with both readings named. This is a draft reading of
the law by AI helpers, not professionally reviewed; nothing says anything complies.

## Files written
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-11.md` (new): reading 1
  (from `return-reading-P5-1.txt`), unchanged below a short header; digest
  `a23fcfbbe505f83c0d06c4b8de02e4e8792498b4b4eac8fdd0c8a02444388f20`.
- `docs/reference-cases/R6B/provenance/return-independent-hand-calculation-12.md` (new): reading 2
  (from `return-reading-P5-2.txt`), unchanged below a short header; digest
  `36b568520d201ef0ba70fa8568f8ad70a299c635c76fe80dbbef1e52b899c95a`.
- `docs/reference-cases/R6B/cases/step-p5-worked.json` (new): the step-P5 case, 28 rows.
- `docs/reference-cases/R6B/step-p5-worked.md` (new): the rendered page.
- `docs/reference-cases/R6B/cases/step-p4-worked.json` (changed): row `zr-34-23-sections` marked
  `superseded_by` `step-p5-worked#zr-34-23-page`, plus a dated change-log entry. No expected value or
  kind changed.
- `docs/reference-cases/R6B/step-p4-worked.md` (re-rendered from the data).
- `docs/reference-cases/R6B/README.md` (changed): the step-P5 case row, the step-P5 "had / did not
  have" section, the provenance line.
- `services/api/tests/rules/reference_cases/r6b_reference_cases_step_p5.py` (new, 71 lines): the
  step-P5 reading digests, reading stems and the must-stay-not-known guard.
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases_step_p5.py` (new, 153 lines):
  the step-P5 acceptance and mutation tests.
- `services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py` (changed): `step-p5-worked`
  added to `CASE_IDS` and a `REQUIRED_BASE_IDS` entry for its 28 rows.
- `services/api/tests/rules/reference_cases/r6b_reference_cases_check.py` (changed): the step-P5
  module wired into `CASE_READINGS`, `_READINGS_LABEL`, `READINGS_DIFFER`, `provenance_errors` and
  `validate_case`.
- `services/api/tests/rules/reference_cases/test_r6b_reference_cases.py` (changed, ONE line): the
  frozen `CASE_IDS` equality tuple gains `"step-p5-worked"`. See the scope note below.
- `project-control/reports/M4-T035-producer-report.md` (this file).

### Scope note on `test_r6b_reference_cases.py`
The packet path-notes list the files "expected to add or change" and do not name
`test_r6b_reference_cases.py`, but that file asserts `lib.CASE_IDS == (<the exact tuple>)`
(line 45). Adding `step-p5-worked` to `CASE_IDS` — which the packet path-notes explicitly require —
forces this one-line tuple update; otherwise the must-pass `tests/rules/reference_cases` suite goes
red. The same forced edit was made by task M4-T032 when it added `step-p4-worked` (commit
`48aa0de80` touches this file for exactly this line). The file is inside the packet's folder-level
`allowed_paths` (`services/api/tests/rules/reference_cases`) and S8's allowed-paths test, and the edit
is byte-minimal and behavior-preserving. Flagged for the reviewer to confirm as the intended
consequence.

## Rows added (28) in `cases/step-p5-worked.json`
mixed-use-sections; mixed-use-floor-area-combination; shared-floor-area-rule;
made-up-mixed-shared-attribution; made-up-mixed-residential-far; made-up-mixed-commercial-far [NK];
made-up-mixed-whole-building-max [NK]; floor-area-ratio-definition; floor-area-ratio-made-up-100x100;
zr-23-24-reach [NK]; zr-34-23-page; benchmark-rear-yard-23-342-23-344 [NK]; 
fully-electrified-building-definition; ultra-low-energy-building-definition;
energy-floor-area-exclusion; proposed-building-energy-eligibility; building-and-story-definitions;
parking-loading-bicycle-sections; transit-zone-value; option-standard-residences;
option-qualifying-affordable-housing; option-qualifying-senior-housing; option-shops-below-residences;
option-residences-with-community-facility; option-community-facility-alone; option-rooming-units;
parking-loading-bicycle-line-per-option; sections-and-facts-not-had. ([NK] = recorded "not known".)

## Rows changed (id, old value, new value, reason)
- `step-p4-worked#zr-34-23-sections`: expected kind/value **UNCHANGED** (still the value "ZR 34-23 is
  a header... none speaks of the rear yard"); the only change is `superseded_by` =
  `["step-p5-worked#zr-34-23-page"]` plus a dated change-log entry. Reason: the step-P5 readers both
  had the ZR 34-23 contents capture (`zr-34-23-contents`) — which step-P4 reading 9 did not — and
  read it as the complete three-subsection list, resolving reading 9's completeness caveat; the new
  `zr-34-23-page` row holds the current answer to the same question (one current answer per question).

## Point-4 supersession candidates — decisions
1. **step-p3-worked#real-lot-rear-yard-beyond-corner — NOT superseded.** Both step-P5 readings reach
   the identical "not known" for the part beyond the corner on the identical residual basis (the
   adjoining zoning lot's lot-line type, which neither the step-P3 nor the step-P5 readers had); the
   step-P5 reading does not change the answer. Also, that row is read as current through
   `lib.load_row` by `test_r6b_reference_cases.py:347` (a file not in this task's change set and which
   must pass unchanged), so superseding it would turn a frozen test red. The new step-P5 rear-yard
   row (`benchmark-rear-yard-23-342-23-344`) names this step-P3 row as the standing head for the
   beyond-corner part and does not re-answer it.
2. **step-p4-worked#made-up-100x100-units — NOT superseded, NOT changed.** The step-P5 readings
   settle only the floor-area-ratio definition and that floor area = ratio x lot area = 20,000 sq ft
   for the made-up lot (Q2); neither reading re-computes the dwelling-unit count (29), so no step-P5
   row gives the current answer to the unit-count question on the same basis. The row is also read as
   current through `lib.load_row` by `test_r6b_reference_cases_step_p4.py:75` (must pass unchanged).
   The new `floor-area-ratio-made-up-100x100` row records that the floor-area-ratio definition the
   step-P4 readers lacked is now had and confirms the floor-area basis, and names the step-P4
   units row as the standing head for the count.
3. **"any earlier row that says the readers did not have a text the step-P5 readers had"** — the one
   instance is **step-p4-worked#zr-34-23-sections** (reading 9's "the full ZR 34-23 sub-section list
   is not confirmed by the folder" caveat; the step-P5 readers had `zr-34-23-contents`). It is **not**
   read by any test through the loader, so superseding it is test-safe. **Superseded** by
   `step-p5-worked#zr-34-23-page` (see Rows changed).

## Before/after of every row's expected kind and value, per case file
- `cases/step-p5-worked.json`: all new (28 rows); no "before".
- `cases/step-p4-worked.json`: every row's expected kind and value is byte-identical before and
  after; only `zr-34-23-sections` gains `superseded_by` and the case gains one change-log entry.
- `cases/real-lot.json`, `interior-lots.json`, `corner-reach.json`, `suffix.json`,
  `step-p1-worked.json`, `overlay-reading.json`, `step-p3-worked.json`: unchanged (not written).
  The pinned corner-coverage rows and the `corner-reach` reach rows are untouched; the too-broad
  sentence in `interior-lots.json` (DB-168) is untouched.

## Acceptance test per input state (scenarios S1–S10)
| ID | Input state | Evidence | Result |
|---|---|---|---|
| S1 | mixed-building floor-area sections 35-30 to 35-33 + FAR-ratio definition | rows mixed-use-sections, mixed-use-floor-area-combination, shared-floor-area-rule, made-up-mixed-*; `test_step_p5_settled_rows`; commercial FAR = not known (Article III Ch 3 not had) | PASS |
| S2 | the two energy definitions + building + story | rows fully-electrified/ultra-low-energy-definition, energy-floor-area-exclusion, proposed-building-energy-eligibility, building-and-story-definitions; a user's statement never establishes eligibility (RDP verification does); `test_step_p5_settled_rows` | PASS |
| S3 | ZR 23-24 and the ZR 34-23 page | rows zr-23-24-reach (not known, children not had) and zr-34-23-page (value; none speaks of the rear yard); `test_step_p5_not_known_rows`, `test_step_p5_supersedes_the_zr_34_23_sections_overlay_row` | PASS |
| S4 | the 14 parking/loading/bicycle sections | row parking-loading-bicycle-sections (section by section); transit zone named as missing-fact-dependent; no conclusion the text does not state | PASS |
| S5 | one mixed building worked by hand | rows made-up-mixed-shared-attribution (83.58 / 316.42 of the 400) and made-up-mixed-residential-far (2.00 x 10,000 = 20,000, arithmetic step); worked from ZR 35-31, not a program run | PASS |
| S6 | each development option | rows option-* (seven) and parking-loading-bicycle-line-per-option: what a line MAY say and MAY NOT say (no count, not feasible, no preference) | PASS |
| S7 | benchmark rear yard from 23-342/23-344 (89.7°, 144.60 ft) | row benchmark-rear-yard-23-342-23-344: within 100 ft no rear yard (23-344(a)); beyond, not known (adjoining lot); report says which engine answer the readings support (below); no fixture/program change | PASS |
| S8 | the commit diff | only allowed-folder files changed; no app/research/register/measurement-basis/plans/scenario file; support code imports nothing from the engine (glob'd engine-free test passes); pages byte-identical to the data (render --check PASS) | PASS |
| S9 | each cited law quote | every captured citation carries its snapshot id and digest (pulled live from the capture) and the quoted words are in the capture; checker confirms; mutation 1 proves a changed quote is caught | PASS |
| S10 | both-readings-agree / one current answer | value only where both agree on the same basis, else not known with both named; "did not have" list holds only what both name; one condition stated in the value (energy proposed-building; residential loading); zr-34-23-sections superseded, its step-P5 target current; mutation 2/2b prove an unsettled/differing row given a value is refused; no human verdict | PASS |

## Where the two readings differ, or one holds an answer subject to something
- **Benchmark rear yard, far-edge reach** (row benchmark-rear-yard-23-342-23-344): reading 11 finds a
  small sliver of the west edge beyond 100 ft of the Northern Boulevard street line (the lot reaches
  ~101 ft there) and slivers on both non-street edges; reading 12 finds the west edge reaches only
  ~100 ft (no sliver) and only the far ~4 ft of the south edge beyond 100 ft of the 215 Place line.
  Both reach the same overall "not known" beyond the corner (adjoining-lot dependency). Recorded as a
  difference; the row stays not known (checker READINGS_DIFFER).
- **Residential loading** (option rows): both readings agree no captured section requires an
  off-street loading berth for a residence; reading 12 states this flatly as "not required"
  (residences are not a listed use in the ZR 36-62 table; ZR 25-02 scopes Chapter 5 to parking and
  bicycle only), while reading 11 reaches the same "no captured requirement" but holds that whether a
  residential loading section outside the folder exists is not known. Recorded as the shared answer
  with reading 11's beyond-folder condition stated in the value.
- **35-32 reach** (row mixed-use-sections): both agree 35-32 does not reach the lot (not a qualifying
  residential site); reading 11 adds that full confirmation would turn on the R1-to-R5 mapping, which
  the facts show is R6B. Stated as a condition in the value.
- **Ultra-low-energy / proposed building** (rows proposed-building-energy-eligibility and the
  definition): both agree a fully electrified building cannot be new; an ultra-low-energy building is
  provisional at plan approval, confirmed only by the post-construction report. A proposed status
  supports only a conditional result.

## Point-5 paragraph — which existing engine answer the rear-yard readings support
(Report-only, per the task; the case row states the reading from the text and the measurements, not
the program.) The program holds two existing rear-yard answers for the benchmark lot. The older
geometry engine outputs the rear yard as "not_required"
(`services/api/tests/scenario/three_answers/test_three_answers_benchmark.py` lines 174–178: the yards
entry's `status == "not_required"`, `zr_sections == ["ZR 23-344(a)", "ZR 11-25"]`). The decision
module instead WITHHOLDS the rear yard as owed
(`services/api/tests/scenario/three_answers/test_result_ways_benchmark.py` lines 91–93:
`is_withheld(ways.rear_yard)` with `"144.60 ft"` in the reason). The two independent readings support
NEITHER as a blanket whole-lot statement: they support the geometry engine's "not required" ONLY
within 100 ft of the ~89.7-degree corner (the same ZR 23-344(a) basis), but hold the part beyond 100
ft (the lot reaches 144.60 ft from the corner point) NOT KNOWN, because it turns on the adjoining
zoning lots' lot-line types under ZR 23-344(c), which the readers did not have. Taken as a single
whole-lot answer, the readings therefore align with the decision module's WITHHELD/owed result (a
reading is owed), not with a blanket "not required"; neither existing answer is fully right as one
label — the correct reading is split (no rear yard within 100 ft; not known beyond). No fixture and no
program code was changed.

## What stays "not known", and the further captures the readings name as missing (for the orchestrator)
| Section / fact (pointing words) | What waits on it |
|---|---|
| Article III, Chapter 3 — ZR 35-31 "as set forth in Article III, Chapter 3" | the made-up building's commercial FAR and whole-building maximum |
| ZR 23-24 subsections (23-241 and following) — ZR 23-20 "Special rules governing certain areas are set forth in Section 23-24" | whether ZR 23-24 reaches the lot |
| ZR 25-222 / ZR 25-232 — ZR 25-221/231 "in accordance with the provisions of Section 25-222 / 25-232" | the residential off-street parking COUNT for options 1–5 |
| the Use Group tables — ZR 36-21/36-62/36-711 "The specific designations for #uses# are set forth in the Use Group tables" | the commercial and community-facility parking/loading/bicycle RATES |
| ZR 36-23 / 36-24 / 36-25 (parking waivers) — ZR 36-21 waiver list | the small-lot commercial parking waivers |
| Section 66-11, APPENDIX I, ZoLa — ZR 12-10 Outer/Greater Transit Zone definitions | confirming the transit zone from the law (the served "Outer Transit Zone" is a recorded value, not a rule) |
| Local Law 154 of 2021, the NYC Energy Conservation Code and Building Code — the ZR 12-10 energy definitions | the substance of the energy requirements |
| the adjoining zoning lots' lot-line types (a fact) — ZR 23-344(c)(1) vs (c)(3) | the benchmark rear yard beyond 100 ft of the corner |
| the block's bounding dimensions (a fact) — ZR 23-344(b) / "short dimension of a block" | whether ZR 23-344(b) adds anything |

## Checks (each exit code captured directly with `echo $?`)
- a. `python -m ruff check .` (from services/api) — **EXIT 0** ("All checks passed!").
- b. `python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/spatial/test_lot_reach.py tests/scenario/three_answers/test_result_way_bridge_overlay.py` — **EXIT 0** (91 passed).
- c. `python tests/rules/reference_cases/r6b_reference_cases_render.py --check` — **EXIT 0** ("reference-case check PASSED (no issues)").
- d. `python3 tools/modularity_check.py --check` — **EXIT 0** (724 files; failures 0; 29 pre-existing warnings, none in the files this task touched). `python3 scripts/lanes/check_lane_paths.py --coverage` — **EXIT 0** ("LANE COVERAGE PASS: 9375 file(s)").
- e. Two mutation proofs on a temp copy outside the repo (`scratchpad/mutation_proofs.py`) — **EXIT 0**:
  (1) a changed law quote in `mixed-use-sections` is CAUGHT ("the quoted words for 35-31 are not
  found in the capture zr-35-31"); (2) a value on `benchmark-rear-yard-23-342-23-344` (readings
  differ) is REFUSED; (2b) a value on `made-up-mixed-commercial-far` (must stay not known) is REFUSED.
- The full services/api pytest was NOT run (the orchestrator runs it once at the wave's final
  candidate, per the packet).

## Doubt / disclosure
- The one-line edit to `test_r6b_reference_cases.py` is outside the packet's named path-notes list but
  forced by the required `CASE_IDS` addition and precedented by M4-T032 (see Scope note); the reviewer
  should confirm it.
- The seven option rows and the line-per-option row are recorded as "value" rows whose value states
  each topic's resolved applicability or "not yet checked / not known" with the missing fact named;
  they never give a count and never call an option feasible.
- This is an AI agent's draft reading of the law, not a professional review, and nothing here says
  anything complies.
