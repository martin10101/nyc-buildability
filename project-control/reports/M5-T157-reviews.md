# M5-T157 reviews (every return kept unchanged)

- G1 data-contract-verifier at 18e62ca4: PASS (NB-05 revision 2 agrees; the 'DB' token confirmed by a live PLUTO query; two advisories kept in the record's review entry). Carry to 0330d598 confirmed by the same reviewer.
- G3 code-reviewer at 18e62ca4: PASS (two advisories, no change needed). Carry to 0330d598 confirmed by the same reviewer.
- G4 qa-engineer at f48b3d97: PASS with one required correction (the sibling task M5-T159's law-link tests were red against this task's fixture change); delta at 0330d598: PASS.
- Identity: the only change inside this task's allowed paths after 18e62ca4 is the G1 review entry in NB-05 (dcd82851); the gates are recorded at a later head of the same branch where these files are byte-identical.

## G1 return

<!-- saved unchanged by save_return.py from agent-a001add3c557af12d.jsonl, entry 2026-10-11T05:44:46.707Z, sha256 6853ff3bb4f442a4d49e4fdb87c5092982ecf17a340e78bbea9bd326e823d9e9 -->
G1 REVIEW — M5-T157 (DB-231): special density area from the city's record. Reviewer: data-contract-verifier (read-only). Frozen head: 18e62ca45d71288532a3537aaa2e03fb0b14e1de, branch task/wave23-density-zoning-lot in /root/project/w-wave20. Affected record: docs/research/evidence-records/NB-05-special-density-area.json (revision 2).

VERDICT: PASS (record review entry: "agrees"). No REQUIRED findings; two ADVISORY items below.

Note on frozen-head integrity: HEAD moved to 10e5c55d mid-review (peer task M5-T158, ACRIS). `git diff --name-only 18e62ca4 10e5c55d` over every M5-T157 path (services/api/app/scenario/three_answers/**, r6b_dwelling_units.rule.json, the test dir, docs/research/zr-snapshots/v1/**, app/_zr_snapshots/v1/**, F08 fixture, NB-05) returns EMPTY — all task files are byte-identical between the two commits, so my file reads (pinned via `git show 18e62ca4:`) and my pytest run (against the working tree at 10e5c55d) are both valid for the frozen content.

=== G1 TASK 1 — FIELD MEANING (confirmed from the repo F08 PLUTO dictionary fixture + live DCP data) ===
From services/api/tests/fixtures/pluto/F08_api_views_columns_snapshot.json (dataset 64uk-42ks), I read the official column descriptions:
- cd ("community board", number): "three digits, the first of which is the borough code... second and third... the community district or joint interest area number." JIAs listed (164 Central Park, 226-228, 355-356, 480-484, 595) and "not considered part of any community district." Marble Hill = cd 207/208 (serviced by Bronx), Rikers = 401.
- borocode (number): Marble Hill BORO CODE 1 (legally Manhattan), Rikers 2.
- spdist1/2/3 (text): "Only special purpose districts that cover at least 10% of a tax lot's area are included"; blank if not in one; co-equal districts "separated by '/'"; "See Appendix A for valid values." Appendix A itself is NOT in the fixture.
special_density_geography.py reads them exactly this way: cd 101-108 = Manhattan Core; JOINT_INTEREST_AREA_CDS = {164,226,227,228,355,356,480-484,595}; _is_recognised_community_district requires borough 1-5 and number 1..18 and not a JIA. result_way_facts.gather_special_density_record reads cd/borocode as integers, reads spdist1/2/3, splits each on "/", upper-cases/strips tokens, and distinguishes served-empty (ABSENT) from not-read/untrusted (NOT_READ) via the fetch source. "Not read" is never "no": every null/JIA/unrecognised/contradiction path yields NOT KNOWN, and NOT_IN requires BOTH Manhattan-Core-no AND every spdist column read with none DB. Confirmed correct.

=== G1 TASK 2 — THE "DB" PROBE (required adverse finding only if token != DB) ===
Official source queried: Socrata SODA, dataset 64uk-42ks (official DCP PLUTO).
URL: https://data.cityofnewyork.us/resource/64uk-42ks.json?$select=bbl,borough,cd,spdist1,spdist2,spdist3,address&$where=spdist1%3D%27DB%27&$limit=5  (query run 2026-10-11)
Returned 5 Brooklyn CD 302 (Downtown Brooklyn) lots, all spdist1="DB": 423 STATE STREET, 65 WILLOUGHBY STREET, ASHLAND PLACE, 291 CADMAN PLAZA EAST, 365 JAY STREET.
RESULT: the token IS exactly "DB". The code's SPECIAL_DOWNTOWN_BROOKLYN_TOKEN="DB" (exact match after split/strip/upper) is correct. NOT a required adverse finding.

=== G1 TASK 3 — LAW (digests, benchmark, boundary) ===
I computed sha256(verbatim_excerpt) for each snapshot and compared to the code-pinned digests (all MATCH):
- zr-12-10-special-density-areas: e8029ab3...f401b6 (code SPECIAL_DENSITY_AREAS) MATCH
- zr-12-10-manhattan-core: 2c04132a...c59c56 (code MANHATTAN_CORE) MATCH
- zr-12-10-special-downtown-brooklyn-district: ae66c93e...d7dd2d (code SPECIAL_DOWNTOWN_BROOKLYN_DISTRICT) MATCH; verbatim: 'The "Special Downtown Brooklyn District" is a Special Purpose District designated by the letters "DB"...'
- zr-23-52: f48f1ddc...b908ac — pinned in app/_zr_snapshots/v1/zr-23-52.snapshot.json AND r6b_dwelling_units.rule.json (lines 24, 31) AND the review register; MATCH.
Test test_each_law_capture_digest_matches_the_committed_snapshot also pins both digest and verbatim_excerpt for the three ZR 12-10 captures. ZR 23-52 captured as: factor 680; "Fractions equal to or greater than three-quarters... one dwelling unit"; (a)(1) no factor in special density areas — the rule's condition line gates the estimate on `special_density_area != true` and treats qualifying senior housing as not-applicable. Correct.
Benchmark/boundary worked independently (three-quarters = fraction >= 0.75 counts as one): 20150/680=29.6324 -> 29; 20230/680=29.7500 -> 30; 20229/680=29.7485 -> 29; 20400/680=30.0 -> 30; 10710/680=15.75 -> 16. All match NB-05 worked_example.

=== G1 TASK 4 — NB-05 REVISION 2 ===
- Observed facts vs interpretation: cleanly separated (observed_facts = 4 record/law facts; interpretation = "Not in a special density area: the definition applied to recorded geography"). Supported.
- Two new conditions: (i) PLUTO 10%-of-tax-lot rule -> a DB sliver can read as none — directly supported by the F08 spdist1 description; (ii) record is per tax lot while ZR 23-52 sets the limit on the zoning lot — supported (BBL = tax block+lot per F08; E3 excerpt says "permitted on the zoning lot"). Both supported.
- Open item: searches[] records Appendix A "not_found" with next_step "G1 probe"; appropriately kept open.
- Regression cases map to existing tests: I confirmed every named test exists at the frozen head (test_queens_benchmark_cd_411_is_not_in, test_cd_108_manhattan_core_is_in, test_marble_hill_cd_207_is_not_in, test_special_district_db_token_is_in, test_split_special_district_value_xx_slash_db_is_in, test_special_district_columns_not_read_is_not_known, test_nothing_read_is_not_known, test_contradiction_cd_105_borocode_3_is_not_known, test_cd_164_joint_interest_area_is_not_known, test_user_statement_never_overrides_the_record_s5, test_m5t157_engine_not_in_one_iff_the_unit_limit_is_shown, test_each_law_capture_digest_matches_the_committed_snapshot).
- Code identities: I independently recomputed LF-normalized sha256 (`git show 18e62ca4:<p> | tr -d '\r' | sha256sum`) for all 8 files in implementation.code_identity — ALL 8 MATCH (engine_conditions 6768a49a, r6b_dwelling_units.rule 404179f2, special_density_geography ce2c6b15, result_way_facts 8e440578, result_way_bridge df70486d, result_ways 09d0009d, result_way_engine_bridge 31ee7f0a, three_way_scope_lines 8cece25b).
- `python3 tools/research_record_check.py --check` -> PASS (exit 0): NB-05 status=answered_from_primary_source, code_current=True, review_state=stale (expected — only a revision-1 review is recorded; revision 2 needs this fresh review).
- Behavioral run: `cd services/api && PYTHONPATH=... python -m pytest -q tests/scenario/three_answers/{test_special_density_geography,test_result_ways_input_states,test_result_way_bridge,test_result_way_facts}.py` -> 98 passed. These exercise the null/ambiguous/contradiction/schema-drift states (all resolve conservatively to NOT KNOWN; the invariant "engine given not-in-one iff the unit limit is shown" holds; a user statement never overrides the record).
- Live decisive-geography check: official PLUTO query for the named property. URL https://data.cityofnewyork.us/resource/64uk-42ks.json?$where=bbl=4073340070 (run 2026-10-11) returned borough QN, borocode 4, cd 411, spdist1/2/3 null, zonedist1 R6B, overlay1 C2-2, 215-16 NORTHERN BOULEVARD — EXACTLY matches NB-05 E4, and cd 411 (Queens(4) CD 11) + no DB -> NOT IN a special density area. The record's conclusion is confirmed against the live official source.

=== FINDINGS ===
F1 (ADVISORY, provenance completeness): NB-05's evidence array (E1-E4) and meaning_and_applicability.provisions_read do NOT cite the zr-12-10-special-downtown-brooklyn-district snapshot, which is the source of the load-bearing "DB" letters. The provenance DOES exist in the repo (snapshot content_digest ae66c93e..., pinned in special_density_geography.py and enforced by test_each_law_capture_digest_matches_the_committed_snapshot), and E1 names the district but not the "DB" designation. Because revision 2 broadens the record to the general record-driven geography (DB-231), recommend adding this snapshot as an evidence item (e.g. E5) / to provisions_read. Not decisive for the named Queens property (which is NOT IN via the Manhattan-Core-no + no-special-district path), so ADVISORY, not REQUIRED.
F2 (ADVISORY, strengthens the open item): The DB open item (OQ-5, "Appendix A not captured") can be corroborated: my official Socrata probe shows Downtown Brooklyn lots carry spdist1="DB" exactly. The record appropriately keeps OQ-5 open because the enumerated Appendix A list itself is still not captured in the repo; the empirical probe is strong corroboration of the token but not the authoritative enumeration. Recommend recording this G1 probe result (URL/query/date/result) against OQ-5.

=== WHAT I COULD NOT CHECK ===
- PLUTO Appendix A (the authoritative enumerated list of valid special-district values) — not in the repo; I confirmed the token empirically via the live dataset instead. OQ-5 remains appropriately open.
- Professional/legal verification (ADR-007) — not performed, not this gate's role; the record ships as an unreviewed draft with its law links; the 29/16 figures remain Conditional ceilings, never confirmed entitlements.
- I did not re-run the full api/web suites (CI's job); I ran the four targeted special-density suites (98 passed) + research_record_check.
- E4 was pulled via the ArcGIS MapPLUTO 26v2 FeatureServer; I verified the same lot via the Socrata channel (64uk-42ks); both official DCP channels agree. I did not re-fetch the exact ArcGIS query nor re-verify its saved_copy sha256.

=== RECORD REVIEW ENTRY (for the orchestrator to add) ===
{"reviewer": "data-contract-verifier", "date": "2026-10-11", "reviewed_revision": 2, "verdict": "agrees", "findings": ["DB probe: official Socrata dataset 64uk-42ks returns spdist1='DB' for Downtown Brooklyn CD 302 lots (423 State St, 365 Jay St, 291 Cadman Plaza E) - the code token 'DB' is correct.", "All 4 law-capture digests equal sha256 of their committed verbatim excerpts and match the code pins (ZR 12-10 x3) / the rule+snapshot pin (ZR 23-52 f48f1ddc). Benchmark 20,150/680=29 and boundaries 29.75->30, 29.7485->29, 30.0->30, interior 10,710/680=16 all reproduce.", "All 8 implementation.code_identity LF-normalized sha256 reproduce at the frozen head; research_record_check --check PASS (code_current=True); 98 targeted tests pass; null/ambiguous/contradiction states all resolve to NOT KNOWN; 'not read' is never 'no'.", "Live PLUTO for BBL 4073340070 (215-16 Northern) returns QN, borocode 4, cd 411, spdist1 null, R6B/C2-2 - matches E4 and the NOT-IN conclusion.", "ADVISORY: the record's evidence array omits the zr-12-10-special-downtown-brooklyn-district snapshot (source of the 'DB' letters); provenance exists in repo+code+test but should be cited as an evidence item in revision 2.", "ADVISORY: OQ-5 (Appendix A) correctly kept open; the empirical DB probe corroborates the token but is not the enumerated authoritative list."]}

END-OF-REPORT


## G1 carry

<!-- saved unchanged by save_return.py from agent-a001add3c557af12d.jsonl, entry 2026-10-11T06:08:12.571Z, sha256 b87ba6da22e75954f6da9f6f3a497d39aaf2bed525319f23c8d4aaa4b8c798da -->
Read-only confirmation at 0330d598eaa3197d4867048b88f85a2bd2be2aae (branch task/wave23-density-zoning-lot, /root/project/w-wave20):

1. Entry text = my return's entry: YES. `git show 0330d598:docs/research/evidence-records/NB-05-special-density-area.json` carries the new review.agent_reviews entry verbatim — reviewer data-contract-verifier, date 2026-10-11, reviewed_revision 2, verdict "agrees", all 6 findings (incl. both advisories) word-for-word as I returned. The only field I did not supply is `"report": "project-control/reports/M5-T157-reviews.md"` (an orchestrator-added pointer); acceptable.

2. reviewed_code_identity = current code identities: YES. I recomputed LF-normalized sha256 (`git show 0330d598:<p> | tr -d '\r' | sha256sum`) for all 8 files; every one matches the entry (engine_conditions 6768a49a, r6b_dwelling_units.rule 404179f2, special_density_geography ce2c6b15, result_way_facts 8e440578, result_way_bridge df70486d, result_ways 09d0009d, result_way_engine_bridge 31ee7f0a, three_way_scope_lines 8cece25b).

3. Nothing else in NB-05 changed since 18e62ca4: CONFIRMED. `git diff 18e62ca4 0330d598 -- <NB-05>` is a single hunk adding only the 25-line review entry; no other bytes changed.

4. No other allowed-path file changed in 18e62ca4..0330d598: CONFIRMED. `git diff --stat` over the packet's allowed_paths (read from 0330d598:project-control/tasks/M5-T157.json) reports exactly one file changed — NB-05, +25 insertions. All reviewed source, tests, snapshots, fixtures and register are byte-identical to the frozen head.

My PASS carries to 0330d598: YES. The sole delta is my own review entry; every substantive artifact I verified is unchanged. Advisories F1/F2 remain open findings (not applied), as you noted.

END-OF-REPORT


## G3 return

<!-- saved unchanged by save_return.py from agent-aa486b30261b0ba86.jsonl, entry 2026-10-11T05:49:52.028Z, sha256 62ec83f61bfc2049e9467bf2d8b6033b24019a96757936583d817a18d1b451b1 -->
# Gate report — M5-T157 G3 (code-reviewer): correctness and tests

**Task:** M5-T157 (DB-231: special density area read from the city's record; legal unit limit as a Conditional ceiling)
**Frozen reviewed SHA:** 18e62ca45d71288532a3537aaa2e03fb0b14e1de (branch task/wave23-density-zoning-lot, /root/project/w-wave20)
**Reviewer:** code-reviewer (independent, read-only). **Verdict: PASS.**

## Head/execution caveat (read first)
The read-only guard blocked `git worktree add` (treated as a file write), so I could not stand up a detached worktree at the frozen SHA. The checkout's HEAD had already advanced to f48b3d971 (two peer commits: M5-T159 and M5-T158 builder). I verified every M5-T157 scope file is **byte-identical** to the frozen head: the two intervening commits (`git diff --name-only 18e62ca4..f48b3d97`) touch only disjoint peer-task files (acris connector, law_links, zoning_lot_index, study_inputs, drawings/report sources, fixtures) and **no** file under `app/scenario/three_answers/` or the packet's test paths. So the suites I ran at HEAD reflect the frozen-head M5-T157 behavior. All commands below ran with the lanes venv (`/root/project/lanes-runtime/venv`, Python 3.12.3, ruff 0.13.0) and `PYTHONPATH=/root/project/w-wave20/services/api`.

## Research/verification done first (D-093)
I opened the primary sources and worked the result before reading code:
- ZR 12-10 snapshots (digests match the code constants): special density areas = (a) Manhattan Core, (b) Special Downtown Brooklyn District (e8029ab3…); Manhattan Core = Manhattan CDs 1-8 (2c04132a…); Special Downtown Brooklyn = Special Purpose District designated "DB" (ae66c93e…).
- ZR 23-52 (619a1ee8…): factor 680; fractions ≥ three-quarters count as one unit; no factor in special density areas (a)(1) / qualifying senior housing (a)(2).
- My arithmetic: 20,150/680=29.63→29; 20,230/680=29.75→30; 20,228/680=29.747→29; 10,710/680=15.75→16; 20,400/680=30. All confirmed against the actual round op (`_round_threshold(., 0.75)`) — exact matches.
- NB-05 revision 2 reviewed: evidence E1-E4, reading, conditions (10%-of-tax-lot sliver; per-tax-lot-vs-zoning-lot) and the open OQ-5 (exact PLUTO "DB" token not captured) are all faithfully recorded.

## Findings by the five G3 checks

**1. The fold `decide_special_density` (special_density_geography.py) — PASS.**
I re-derived every input state and exercised the fold inline. IN = DB token (checked first) OR Manhattan-Core cd 101-108 (borough 1 or None). NOT KNOWN = cd None / unrecognised / joint-interest-area (164 ∈ JOINT_INTEREST_AREA_CDS) / Manhattan-core code contradicted by non-Manhattan borough (105+boro3) / spdist columns not fully read. NOT IN = recognised non-core cd (411, 109, 112, 207 Marble Hill) AND all spdist columns read AND no DB. 16/16 cases matched my expectations (0 failures). **No path turns "not read" or an error into NOT IN** — the only NOT-IN branch requires `_Core.NO` (a recognised non-core cd) AND `all_special_district_columns_read`. Fact-gathering (`result_way_facts.gather_special_density_record`) sets `all_special_district_columns_read=False` on any not-fetched/untrusted spdist column (served-empty is a real absence), and tokens are split on "/" and upper-cased — correct.

**2. One decision drives engine + shown result; invariant; record wins — PASS.**
The 9 record×statement combinations in `result_way_bridge._density` matched my independent table exactly (record always wins; both disagreement directions → RECORD_AND_STATEMENT_DISAGREE withheld naming both sides). The engine value `engine_conditions.special_density(_density_decision(k)).engine_value` is False **iff** knowledge ∈ {EVIDENCE_NOT_IN_ONE, USER_STATEMENT_NOT_IN_ONE} — the same two states for which `result_ways._unit_standard_way` returns Conditional (shown). The invariant test `test_result_ways_input_states.py::test_m5t157_engine_not_in_one_iff_the_unit_limit_is_shown` is parametrized over all DensityKnowledge and asserts `(engine_value is False) == (not is_withheld(way))`; it genuinely fails on divergence. The strengthened `test_result_way_bridge.py::test_user_statement_never_overrides_the_record_s5` adds the disagreement-withheld and never-user_statement-kind assertions.

**3. Conditional ceiling, always-present zoning-lot condition, kept apart; D-094 R035 — PASS.**
`result_ways._zoning_lot_condition()` emits a KIND_UNCHECKED_CONDITION ("per tax lot … ZR 23-52 sets the limit on the zoning lot") placed first and never removed. The regenerated fixture shows `legal_unit_limit_standard` way=conditional, value 29.0, with the zoning-lot + contradicted-record conditions; `unit_estimate.status` and `building_option.status` = not_available (limit kept apart from the apartment estimate — R392/R569). The 29 never reads as a confirmed entitlement: scope line / SVG / DXF note all say "shown as a conditional ceiling on the zoning lot" (basis city_records, value "No"); no "confirmed"/"entitlement"/absolute wording anywhere. R035 satisfied in emitted text, scope line, SVG and DXF.

**4. Changed expectations explained; no weakening; law-derived values — PASS.**
`test_results_read_law_examples.py` asserts the unit limit against reference-case rows (`real-lot#L6`=29, `interior-lots#P5-units`=16) driven through the route, with a header stating values come from the reference cases, not a program run; the benchmark PLUTO fixture carries cd='411'/borocode='4'/spdist null, so the route genuinely reads NOT IN from the record. The truth-table change (US5 withheld→conditional, new US6 disagreement row, updated 20-key `_EXPECTED_WAY_SIGNATURE`, renamed `test_s1_…is_a_conditional_ceiling_on_the_zoning_lot`) and the bridge test (`_WITHHELD_ON_BENCHMARK` dropping `legal_unit_limit_standard` while adding positive Conditional assertions) are all correct behavior updates that match the builder's changed-expectations list — strengthened, not weakened.

**5. Modularity / ruff / focused suite / scope — PASS.**
- `python -m ruff check .` (services/api): All checks passed.
- `python3 tools/modularity_check.py --check`: selected 792 files; **failures 0**; 32 warnings (all pre-existing; `result_ways.py` is a pre-existing review_signal warn; new `special_density_geography.py` not flagged).
- Focused suite `pytest -q -p no:cacheprovider tests/scenario/three_answers tests/api/test_results_read_law_examples.py tests/journey tests/rules/test_zoning_rule_review_register_calculations.py`: **548 passed, 2 skipped** (49.9s).
- Also ran `tests/cad tests/drawings/report/test_report_pages.py test_location_sheet.py tests/drawings/kit/test_report_frame.py`: **728 passed** — the regenerated DXF/SVG snapshots are current, not stale.
- Register render `--check`: PASSED. `tools/research_record_check.py --check`: PASS (NB-05 code_current=True, review_state=stale — expected; awaiting the revision-2 G1 review).
- **Scope:** every one of the 46 files in the M5-T157 commits (9e19afacb, 754def4e2, ea3358446, b28dd1da1, a6aff3424, 18e62ca45) is within `allowed_paths` or is this task's own control record; **no out-of-allowed file changed**. The out-of-allowed files in the full f369b7e8..18e62ca4 range belong to peer tasks M5-T158/T159/T160/M0-T191.

## Minor observations (ADVISORY, not defects)
- A1 (special_density_geography.py `_read_integer_column`): a cd served as a float-form string (e.g. "411.0") would `int()`-fail → None → NOT KNOWN. This is the fail-safe direction (withheld, never a wrong NOT IN); the benchmark serves "411" and resolves correctly. No change needed.
- A2 (invariant scope): the engine-not-in-one↔limit-shown invariant holds when a recorded area is present. With EVIDENCE_NOT_IN_ONE but no recorded area, the way is Withheld (missing area) while the engine condition reads not-in-one — semantically correct (the lot genuinely isn't in a special density area; the limit is withheld for the independent missing-area reason, and the engine produces no dividend anyway). Not a defect; the invariant test correctly parametrizes with area present.

## What I could not check
- `apps/web` TS/vitest tests: not run here (producer reports full web suite green; CI's job). The five web test files are in allowed_paths and were updated to match the conditional-29 / inverted-S4 behavior.
- The exact PLUTO "DB" token spelling (OQ-5): an open research item, properly disclosed in NB-05 and the module docstring and carried as a condition — not promoted to Verified. Correctly left for the G1 probe; immaterial to the NOT-IN decision.
- Tests were executed at HEAD f48b3d971, not literally checked out at 18e62ca4 (worktree creation blocked by the read-only guard). Mitigated: all M5-T157 scope files are byte-identical to the frozen head and the intervening commits are disjoint peer tasks. If the orchestrator wants belt-and-suspenders, re-run the focused suite in a worktree at 18e62ca4.

**VERDICT: PASS.** All five G3 checks satisfied with reproducible evidence; no REQUIRED findings.

END-OF-REPORT


## G3 carry

<!-- saved unchanged by save_return.py from agent-aa486b30261b0ba86.jsonl, entry 2026-10-11T06:08:00.936Z, sha256 e6698927dd94200dc69407bf8ece3672c3f1ddb319f7ddcbc09d8252a34a8b51 -->
# Follow-up confirmation — M5-T157 G3 verdict carries to new head 0330d598

Confirmed read-only against the new head 0330d598eaa3197d4867048b88f85a2bd2be2aae.

**In-scope diff `18e62ca4..0330d598` across M5-T157 allowed_paths:** exactly one file changed — `docs/research/evidence-records/NB-05-special-density-area.json`, +25/-0. No production code, test, fixture, snapshot, register, or docs/calc file differs. Every code-bearing scope file is byte-identical to my reviewed head (18e62ca4).

**NB-05 change is purely additive:** one new entry appended to `review.agent_reviews` recording the data-contract-verifier's revision-2 pass (verdict "agrees") with its own reviewed_code_identity hashes, findings and two ADVISORY notes. Revision stays 2; no evidence, reading, conclusion, condition, measurement, or implementation field altered. (Commit dcd82851, as you stated.)

That appended review independently corroborates my G3 findings: DB token correct via live Socrata 64uk-42ks (Downtown Brooklyn CD 302 lots return spdist1='DB'); all four law-capture digests match their verbatim excerpts and code pins; benchmark 20,150/680=29 and boundaries 29.75→30, 29.7485→29, interior 10,710/680=16 reproduce; BBL 4073340070 reads QN/boro4/cd411/spdist null → NOT IN. Its two ADVISORY items (cite the Downtown-Brooklyn snapshot as an evidence entry; keep OQ-5 open) are record-provenance notes, not code/test defects, and are outside G3's scope (correctness and tests).

**My G3 verdict PASS carries to 0330d598 unchanged.** The only in-scope delta since my reviewed head is a non-executable, additive evidence-record review entry touching no code, test, or output I evaluated.

END-OF-REPORT


## G4 return (verdict A)

<!-- saved unchanged by save_return.py from agent-a458e08ba9c79cc79.jsonl, entry 2026-10-11T05:58:21.541Z, sha256 cee2b5983a978adbe87cab21cde011ec5b9c6711ed5fc036fcabdb55105fa075 -->
G4 (qa-engineer) INDEPENDENT GATE — M5-T157 and M5-T159. Frozen head f48b3d971f6964b119f905f2c5903ee7e587103f on task/wave23-density-zoning-lot. Reviewed read-only in a detached worktree (/tmp/rv-qa-w23, created at f48b3d97, removed at end; left clean, HEAD unchanged). Venv /root/project/lanes-runtime/venv. No ports touched.

================ VERDICT A (M5-T157): PASS WITH REQUIRED CORRECTIONS ================
VERDICT B (M5-T159): FAIL
Both failures share ONE root cause (finding 1 below) with ONE fix, owned by T159's test file.

===== WHAT I VERIFIED INDEPENDENTLY (law first, then tests) =====
LAW (opened the primary captures, not the brief/reports):
- zr-12-10-special-density-areas (digest e8029ab3…f401b6): special density areas = (a) Manhattan Core; (b) Special Downtown Brooklyn District.
- zr-12-10-manhattan-core (2c04132a…c59c56): Manhattan Community Districts 1–8.
- zr-12-10-special-downtown-brooklyn-district (ae66c93e…d7dd2d): designated by the letters "DB".
- zr-23-52 (f48f1ddc…b908ac): (b) factor 680; "Fractions equal to or greater than three-quarters … considered to be one dwelling unit"; (a)(1) no factor in special density areas.
All three digests hard-coded in special_density_geography.py EQUAL the committed snapshots. Engine copies exist under services/api/app/_zr_snapshots/v1/.

ARITHMETIC (worked myself from ZR 23-52 before reading tests):
- 20,150/680 = 29.63 → 29 (0.63 < 0.75). ✓ matches fixture row "20,150 ÷ 680 = 29.63", value 29.0.
- 10,710/680 = 15.75 → 16 (0.75 ≥ 0.75, boundary up). ✓
- 20,230/680 = 29.75 → 30 (exact .75, up). ✓   20,228/680 = 29.747 → 29 (< .75). ✓
- 20,400/680 = 30 exactly; 20,229/680 = 29.7485 → 29. ✓ (NB-05 worked_example consistent.)

FOLD LOGIC (special_density_geography.decide_special_density) — read line by line, correct:
either IN signal alone suffices (DB token OR Manhattan-Core cd 101–108); NOT IN requires BOTH the Manhattan-Core question answered no AND every special-district column read with none "DB"; everything else (cd None/unrecognised/joint-interest-area e.g. 164, Manhattan-Core cd contradicted by non-Manhattan borocode e.g. 105+borocode 3, or special-district columns not fully read) is NOT KNOWN; "not read" is never "no". Matches S1/S2/S3 exactly.

===== COMMANDS RUN (frozen head) =====
T157:
1. pytest tests/scenario/three_answers → 475 passed, 2 skipped.
2. pytest tests/scenario/three_answers tests/api tests/journey tests/rules tests/drawings tests/cad → **2 failed, 4473 passed, 8 skipped** (286s). The ONLY 2 failures: tests/drawings/report/test_report_law_links.py::test_s1 and ::test_s6 (T159's file). tests/journey (benchmark legal unit limit = 29 Conditional), tests/api law-examples, tests/rules, tests/cad all green.
3. render_review_register.py --check → "register check PASSED (no issues)".
4. research_record_check.py --check → PASS; NB-05 revision=2, status=answered_from_primary_source, code_current=True, review_state=stale (expected — awaits the fresh G1 review of rev 2; disclosed in-record).
5. apps/web: npm@11.18.0 ci (exit 0) then npx vitest run on the 5 changed web files (journey-215-16-northern, results-contract-checks, presented-notices, presented-results, three-answers) → **5 files / 71 tests passed**.
6. My own mutation (brief A#3): in the fold, forced the final "columns not fully read" branch to return NOT_IN (`if True`). → test_special_district_columns_not_read_is_not_known FAILED (got NOT_IN, expected NOT_KNOWN). Restored byte-for-byte (worktree clean).
7. ruff check . → All checks passed!  modularity_check --check → exit 0, failures 0 (new modules special_density_geography.py 238L and law_links.py 117L not flagged; result_ways.py is a pre-existing warn).

T159:
1. pytest tests/drawings/report/test_report_law_links.py → 2 failed, 19 passed.
2. pytest tests/drawings tests/rules (brief B#3) → **2 failed, 2141 passed, 6 skipped** (153s). Same 2 failures (test_s1, test_s6).
3. Independent benchmark href build through the REAL builder (build_report_html on packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json): evidence page has **12 hrefs** — 4× 23-22, 2× 23-52, 6× 23-432. EVERY href equals a capture's source.request_url (zr-23-22, zr-23-52, zr-23-432); NO homepage href. ZR 11-25 is cited but has no allowlist-valid capture, so it correctly prints as plain text (live proof of S3 at the benchmark).
4. allowlist port: compared law_links.official_zoning_text_url line-by-line against apps/web/src/lib/architect/source-links.ts — faithful (same prefix, length cap, forbidden-char class \u0000- /\u007f/\\, scheme/host/user/pass/port/query checks, path regex /^/article-[ivxlcdm]+/chapter-\d{1,2}(?:/\d{2}-\d{2,4})?$/, fragment \d{2}-\d{2,4}; '#' handled separately because urlsplit drops it). section_url drops the sub-paragraph for lookup, keeps it in the label; fail-closed to None/plain text; drops wrong-host (entityprint) and chapter-only captures.
5. My own mutation (brief B#3): removed the query rejection in official_zoning_text_url. → test_s4_allowlist_rejects_disallowed_urls[…?x=1] FAILED. Restored byte-for-byte.

===== FINDINGS =====
FINDING 1 — REQUIRED (the FAIL for B; the required correction for A). Cross-task interaction: T157's benchmark-fixture change breaks T159's law-links tests at the frozen head.
Files: services/api/tests/drawings/report/test_report_law_links.py:75 (test_s1) and :208 (test_s6).
Evidence: test_s1 `assert len(hrefs) == len(rendered)` → 12 == 13; test_s6 `assert len(hrefs) == 10` → 12 == 10. Cause: T157 added citations ZR 23-52, ZR 23-52(b), ZR 11-25 to the floor_area_allowance block (the conditional legal unit limit, 20,150÷680=29). So the evidence page now renders 13 cited sections across floor_area_allowance+permitted_envelope and 12 law hrefs (11-25 has no capture → plain text), vs the pre-T157 fixture's 10 hrefs / set {23-22,23-432} the tests were written against. T159 and T157 ran in parallel on different files, so T159's builder (base 439e22b2) could not see T157's fixture change.
IMPORTANT: the link BEHAVIOUR is CORRECT — I independently confirmed all 12 hrefs are exact section URLs equal to the captures' request_url, none is the homepage, and 11-25 (no capture) correctly prints as plain text. This is a STALE-TEST defect, not a code defect; no production change is needed.
Required fix (in T159's scope — test_report_law_links.py): (a) test_s6 → expect 12 hrefs and set {zr-23-22, zr-23-52, zr-23-432}; (b) test_s1 → its invariant `len(hrefs)==len(rendered)` is now false because a rendered section (11-25) has no capture and prints plain text; rework it to count only rendered sections that resolve to a URL, and add an explicit assertion that 11-25 is plain text (this is a genuine new S3 case on the benchmark). Because both T157 and T159 land in one wave ("never merged alone"), this fix must land before the wave merges; it clears both A's and B's red suite. If T159 cannot be reopened, route test_report_law_links.py via a scope correction as was done for test_result_way_engine_bridge.py.

FINDING 2 — ADVISORY (B). No automated test asserts that law_links.py's allowlist stays in parity with source-links.ts; I verified parity by hand this round. Consider a parity/golden test so a future edit to either side cannot drift silently. Not a blocker.

FINDING 3 — ADVISORY (A, context only). NB-05 revision 2 is code_current=True but review_state=stale: its agent_reviews still carry revision-1 code identities. The record discloses it awaits a fresh independent review of rev 2; T157's G1 (data-contract-verifier) covers that. Not a G4 blocker.

===== WHY THESE VERDICTS =====
A (M5-T157) — PASS WITH REQUIRED CORRECTIONS: every acceptance scenario S1–S7 is independently verified (fold against ZR 12-10, values against ZR 23-52, invariant/record-wins/nine-combination coverage present and proven real by my mutation, journey=29 Conditional, register+NB-05 checks pass, 5 web files pass, ruff+modularity clean, changed expectations explained and strengthened not weakened). The only frozen-head failures are in a sibling task's test file, caused by T157's CORRECT fixture change; the required correction is finding 1 (owned by T159) and must land before the wave merges.
B (M5-T159) — FAIL: the link-resolution code is correct and well-tested, but 2 tests in the task's own deliverable (test_report_law_links.py) are red at the frozen head; the packet's named suite (tests/drawings) does not pass. Fix = finding 1.

===== WHAT I COULD NOT CHECK =====
- Live reachability/currency of the recorded ZR URLs (no network to the ZR portal; by design the captures are the authority — I verified href == capture request_url).
- Exact PLUTO "DB" token spelling (PLUTO Appendix A not captured; OQ-5) — a known open item flagged for G1, matched here to the ZR 12-10 map-designation letters only; carried as a condition, never a zoning rule.
- Full web vitest suite (only the 5 changed files per brief; producer reported 128 files green at T157's base; no other web file changed in the wave).
- Professional/legal verification — out of scope per ADR-007; the 29/16 figures remain Conditional ceilings, never confirmed entitlements.

END-OF-REPORT


## G4 delta (verdict A)

<!-- saved unchanged by save_return.py from agent-a458e08ba9c79cc79.jsonl, entry 2026-10-11T06:14:06.776Z, sha256 a79274f31ac0d436d6064083f7189891f6bb0ff4d202562a3f914fd28a691cd5 -->
G4 DELTA RE-VERIFICATION — M5-T157 and M5-T159 at new head 0330d598eaa3197d4867048b88f85a2bd2be2aae (branch task/wave23-density-zoning-lot). Fresh detached worktree at 0330d598, read-only, mutations restored, worktree removed. D-093 observed.

===== DELTA VERDICT A (M5-T157): PASS =====
===== DELTA VERDICT B (M5-T159): PASS =====
My prior Finding 1 (the sole blocker; FAIL cause for B, required correction for A) is CLEARED at 0330d598. Findings 2 and 3 were ADVISORY and remain non-blocking.

WHAT CHANGED SINCE f48b3d97 (verified against T157/T159 allowed paths):
1. NB-05 (docs/research/evidence-records/NB-05-special-density-area.json): `git diff f48b3d97..0330d598` shows ONLY a new entry appended to review.agent_reviews (data-contract-verifier, reviewed_revision 2, verdict "agrees"). `revision` stays 2; evidence/meaning/measurement/implementation/conclusion all byte-unchanged. No T157 logic touched. The new G1 entry independently reproduces the law (4 digests, 20,150/680=29, boundaries 29.75→30 / 29.7485→29 / 10,710/680=16) and did a live Socrata probe confirming spdist1='DB' for Downtown Brooklyn CD 302 lots — corroborating the "DB" token empirically. It carries two of its own ADVISORIES (the SDB snapshot not yet cited as an evidence[] item; OQ-5 Appendix A kept open) — these are the verifier's, not G4 blockers.
2. test_report_law_links.py: production unchanged; the test file was rewritten to be fixture-derived. The new s1/s6 compute expectations from the rendered fixture citations plus an INDEPENDENT capture-file oracle (`_capture_section_url` scans the snapshot files directly, not through law_links/sources under test), with no hard-coded counts or URL strings; a new `test_s1_known_sections_link_or_print_plain_from_captures` explicitly pins 23-22/23-52/23-52(b)/23-432 as links and 11-25 (wrong-host capture only) as plain text. Other inter-head commits are M5-T160 (NB-06) + control records, outside both tasks' paths.

COMMANDS RUN (frozen head 0330d598, lanes venv):
- pytest tests/drawings tests/rules → 2144 passed, 6 skipped (was 2 failed / 2141 passed at f48b3d97 — the 2 red tests now pass, +1 new test).
- pytest tests/scenario/three_answers tests/journey tests/api → 1717 passed, 2 skipped. (Consistent with the orchestrator's 7062 passed, 8 skipped across all affected folders.)
- My own quick mutation (brief request): forced page_evidence._law_links to emit the homepage for every captured section (`url = "https://…nyc.gov/"`). → all three guards FAILED — test_s1_every_rendered_section_links_to_its_capture_or_prints_plain, test_s1_known_sections_link_or_print_plain_from_captures, and test_s6_only_link_targets_change_labels_and_text_stay (each asserts the exact `<a href="{capture_url}">` form and `_HOMEPAGE not in hrefs`). Restored byte-for-byte; worktree left clean then removed.

CONFIRMATIONS REQUESTED:
- New s1/s6 are fixture-derived: YES — expectations come from the fixture's rendered citations + the capture files via an oracle independent of the module under test; no typed URL/count. They would (and do) fail on a homepage or guessed URL, proven by my mutation.
- NB-05 change is only the review entry: YES — review.agent_reviews gained one data-contract-verifier entry; nothing else in T157's paths changed; revision stays 2.

CARRY-FORWARD (unchanged, non-blocking): my original A verification stands — fold correct vs ZR 12-10, values 29/16/30/29 vs ZR 23-52, invariant/record-wins/nine-combination coverage proven real, register + research_record checks PASS, 5 web files 71 passed, ruff + modularity clean. B's allowlist is a faithful port of source-links.ts (Finding 2 advisory: no automated parity test — still just advisory).

Both tasks now meet their acceptance at the integrated head; the wave's law-links regression is resolved with a test-only change and no production edit.

END-OF-REPORT
