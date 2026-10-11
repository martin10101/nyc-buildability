# M5-T164 reviews (every return kept unchanged)

Reviews pinned at 6dde1345 (the builder's material commit, cherry-pick of 3c3f5a10): G1 data-contract-verifier PASS, G3 code-reviewer PASS, G4 qa-engineer PASS (a fresh reviewer after the session handoff of 21:31 UTC; the first G4 reviewer was stopped before it returned). No REQUIRED findings; advisories recorded in the evidence map's known limits and in the backlog.

Every reviewer is an AI agent; none is a human or professional review.

## G1

G1 DATA-CONTRACT-VERIFIER REPORT — M5-T164 (results contract 1.5.0)
Reviewed at pinned head 6dde13459 (task/wave24-report-v3, /root/project/w-wave20). Read-only; all probes in scratch/venv.

VERDICT: PASS (no REQUIRED/blocking findings; three ADVISORY notes)

WHAT I CHECKED (independently re-derived from sources, not the producer's conclusion)

1. Shapes vs NB-03/NB-06 (lens 1) — PASS. rear_yard_check provision enum = exactly ["23-344(a)","23-344(b)","23-344(c)(3)"] (NB-03 scope a/b/c3). Each applies/not_applicable check carries inputs{name,value,unit,basis}; combined.way enum includes "conditional" (NB-03 applies=conditional); the not_known branch has no `inputs` property + additionalProperties:false, so a not_known check carries no number (proven: the withheld_check_with_number fixture is rejected and becomes valid only when inputs are dropped). constraint_line kind enum = [rear_yard_100ft_line, corner_area, street_wall_band, setback_line] — the four NB-03/NB-06 lines (the (b) 100-ft line, corner area per 12-10 corner-lot/ NB-06 E2, 35-631(b) 8-ft street-wall band, 23-433 setback line); geometry required only in the `established` branch, absent (additionalProperties:false) in not_established/not_known. envelope_row kind enum = [setback, street_wall, side_yard] (lens c). NB-03/NB-04/NB-06 bases used (printed_tax_map, gis, derived, administrative_record, law, filing_attribute) all fall inside the enum.

2. quantity_basis enum (lens 2) — PASS. enum == set(QUANTITY_BASES) from tools/research_record_check.py:51 and README.md:46, 9 members, no duplicates. input_fact.basis and rear_yard_input.basis both $ref the single def. A basis of "tax_map" is rejected (isolated).

3. Placement/area_allocation (lens 3) — PASS. illustrative_label const "Illustrative"; outline required in the placed branch, absent in the withheld branch (outline-only-when-placed proven by isolation). share minimum 0.60/maximum 0.75 closed (boundary probe: 0.50 REJECT, 0.60 ACCEPT, 0.75 ACCEPT, 0.80 REJECT). area_measure const "residential_floor_area"; plate_conversion_statement const byte-exact to G-14/design-contract R092 ("plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked"). area_allocation additionalProperties:false with no zone-geometry/unit-count/core keys (extra `zones` rejected, isolated). fitted-only-when-placed is a way rule: independent probe — schema ACCEPTS a fitted+withheld doc, results_way_violations flags allocation_fitted_without_placement, BOTH validators REJECT; same for apartment+other≠total (allocation_total_mismatch); a 1.2.0 copy yields no violation (version-gated).

4. Valid examples (lens 4) — PASS. Both fixtures = recorded_215_16_northern_journey.json (1.4.0) + only the new 1.5.0 blocks: strip-new-blocks + reset version/identity == journey exactly; identity fields distinct. New blocks use made-up values (rear-yard 182.5/95/168; shares 0.65/0.70; allocation totals 18,500/19,000). The benchmark 20,150 appears only in journey-inherited building_option content, never in a new 1.5.0 block. Journey fixture absent from the diff (S8).

5. Eight invalid fixtures (lens 5) — PASS. validate_contracts.py rejects all 8 at the intended location; isolation probe (apply the single documented fix → both validators accept) succeeds for all 8: withheld_check_with_number, withheld_placement_with_outline, allocation_zone_geometry, placement_label_wrong, input_fact_basis_unknown, allocation_share_out_of_range, allocation_without_measure, way_layer_broken. Each fails for exactly one reason.

6. Builder's three limitations (lens 6) — all ACCEPTABLE for this task (see ADVISORY).

7. Required commands (lens 7):
   - `python .github/scripts/validate_contracts.py` → EXIT 0 ("Checked 23 schema file(s); 0 failure(s)"; both valid 1.5.0 pass, all 8 invalid rejected).
   - `pytest -q tests/contracts/test_results_contract_1_5_0.py` (lanes venv, PYTHONPATH=services/api) → 71 passed, EXIT 0.
   Also verified: both schema copies byte-identical (sha256 4cf90a9c…395d7); reverse-binding fires for floor_plates.entries[].building (a 1.4.0 doc carrying a tagged plate is rejected at root).

ADVISORY FINDINGS (none block acceptance)
- A1 floor_plates.entries[].building has no valid fixture/test exercising an ACCEPTED tagged plate (the only drawable 1.4.0 fixture has floor_plates not_available). The reverse-binding clause IS present and fires (verified), and TS carries it; only positive coverage is missing. Acceptable for a contract-shape task; recommend a positive fixture/test when an engine emits tagged plates (waves 25-27).
- A2 synthetic_way_layer_broken is a SCHEMA-invalid value_state fixture (settled+conditions), not a cross-key way-rule break. Acceptable: invalid/ fixtures must fail validate_contracts, and the two cross-key rules are deliberately non-schema-expressible; their 1.5.0 behaviour is proven by the Python S12 tests and my independent probe.
- A3 Web client checks cover placement + area_allocation + the two way rules only, not rear_yard/envelope_rows/input_facts/constraint_lines. Acceptable disclosed scoping choice (panel consumes building_alternatives; the rest are server-validated and unread by the panel). If a future page renders those blocks, extend the client guard.

WHAT I COULD NOT CHECK
- Web vitest (TS) not independently run (not in the brief's required commands); logic verified by reading the diff (mirrors schema + way rules); producer reports 164 web tests pass — confirm in CI at the accepted head.
- SVG/DXF snapshots not re-generated (renderer/UPDATE flags); producer reports the two site-plan SVGs byte-identical because the renderer ignores the new blocks — not re-derived here.
- Full services/api pytest (2548) and the web suite are CI's job at the accepted head (D-090-R639).

END-OF-REPORT

## G3

G3 CODE-REVIEWER GATE REPORT — M5-T164 (results contract 1.5.0)
Reviewed read-only at pinned head 6dde13459 (task/wave24-report-v3, /root/project/w-wave20). All probes in the lanes venv; no repo/git/port writes.

VERDICT: PASS (no REQUIRED findings; three ADVISORY notes)

SCOPE: all 22 changed files are inside allowed_paths; forbidden paths untouched (journey fixture, services/api/app/scenario|drawings, docs/, test_study_contracts.py not in diff). S8 holds (journey fixture absent from the diff).

WHAT I CHECKED (independently re-derived, exit codes direct)
1. results_way_rules.py (lens 1) — PASS. CONTRACT_VERSIONS_WITH_WAY_LAYER gains "1.5.0" (line 40). New _building_alternative_violations (l.111+) is version-gated (reached only after the l.93 contract_version gate) and TOTAL. Inline probes (lanes venv) PROBE_EXIT=0:
   - rule fires normally → [('B','allocation_fitted_without_placement')];
   - MUTATION (remove "1.5.0" from the version set) → [] (rule goes silent → the S12/pure-rule tests are genuinely mutation-sensitive);
   - missing building_alternatives → []; placement without status → correctly flags (no crash); non-numeric total_sqft="NaNstr" → [] (no crash, total rule skipped); building_alternatives="string" → []; fitted True + absent placement → flags. No exception in any case.
   Existing 1.3.0/1.4.0 behaviour byte-for-byte unchanged: the only delta is the appended helper call; I swept ALL 12 valid + 28 invalid results fixtures and _building_alternative_violations returns [] for every pre-1.5.0 fixture (additive-delta proof), so outputs are identical to aac892fc.
2. Both Python validators (lens 2) — PASS. study_contracts.py:203 and three_answers/contract.py:100 both call the single shared results_way_violations; S12 tests parametrized over both validators raise (passed in fan-out). quantity_basis enum = exactly the 9 tool QUANTITY_BASES (schema vs tools/research_record_check.py).
3. results-contract-checks.ts (lens 3) — PASS. SUPPORTED_RESULTS_CONTRACT_VERSIONS gains "1.5.0" (l.52); unknown versions rejected via checkEnum at l.532 (S11). checkPlacement/checkAreaAllocation mirror the schema (label/measure/conversion const, share 0.60–0.75, outline-only-when-placed) and both way rules (fitted-only-when-placed; apartment+other=total). No `any` (params typed unknown/Record<string,unknown>). No truthiness on a numeric fact: isJsonNumber = typeof==="number"&&Number.isFinite (study-checks.ts:35), so a 0 area is a value.
4. results.ts generated, not hand-edited (lens 4): generate_ts_types.py --check → exit 0 ("results TypeScript types are up to date").
5. Fan-out (lens 5), exit codes:
   - validate_contracts.py → exit 0 (23 schemas, 0 failures; both valid 1.5.0 pass, all 8 invalid rejected at the intended location);
   - cd services/api && pytest -q tests/contracts tests/drawings/report/test_report_pages.py tests/drawings/kit tests/cad → 1837 passed, exit 0;
   - apps/web ./node_modules/.bin/vitest run results-contract-checks(.test / -1-4-0) + contract-versions → 3 files, 44 passed, exit 0.
6. Modularity (lens 6): modularity_check.py --check → 0 failures (warnings on untouched files only). results_way_rules.py 236 lines, results-contract-checks.ts 572 lines — focused, no dumping ground; new helper is a single-responsibility function.
7. Test file test_results_contract_1_5_0.py (lens 7) — PASS. Tests assert the displaced field exactly (pure-rule tests assert the precise [(answer,key,rule)] tuple / rule set; _fitted_without_placed_doc first asserts schema-validity then the way breach, isolating the rule from the schema; version-gating and non-mapping tests present). Independently confirmed mutation sensitivity above. No forbidden schema keywords (if/then/else/not/minProperties) introduced.

RESEARCH & VERIFICATION (D-093): I agree — this task adds contract SHAPES only. New blocks use made-up plausible values (shares 0.65/0.70, totals 18,500/19,000), the real benchmark journey fixture is untouched, and no evidence record changed. It changes no property fact, rule applicability, calculation input, result or certainty label.

ADVISORY FINDINGS (none block acceptance)
- A1 (concur with G1 A1): geometry.floor_plates.entries[].building is schema- and TS-supported and its reverse-version-binding fires, but no positive valid fixture/test exercises an ACCEPTED tagged plate (the only drawable 1.4.0 fixture has floor_plates not_available). Producer-disclosed structural gap; acceptable for a contract-shape task — add a positive fixture when an engine emits tagged plates (waves 25–27).
- A2 (provenance/process, not code): commit 6dde13459's co-author trailer reads "Claude Opus 5.5". Per D-085 the builder subagent should run on the pinned Opus 4.8. No code impact; flagged for the orchestrator to verify the builder's model via transcript.
- A3 (concur with G1 A3): the web guard covers placement + area_allocation + the two way rules only, not rear_yard/envelope_rows/input_facts/constraint_lines. Acceptable disclosed scoping (those are server-validated and not consumed by the panel); extend the client guard if a future page renders them.

WHAT I COULD NOT CHECK
- Full services/api pytest (2548) and the whole web suite + security checks are CI's job at the accepted head (D-090-R639) — confirm CI green there before accept.
- SVG/DXF snapshots not re-generated from the renderer; their consuming tests pass under the fan-out (tests/drawings/kit, tests/cad green), which exercises the two new snapshots.
- Scratch-file writes to /tmp were blocked by the read-only guard, so probes ran as inline python -c instead (does not affect any conclusion).

END-OF-REPORT

## G4

G4 QA-ENGINEER GATE REPORT — M5-T164 (results contract 1.5.0, additive/optional)
Independent reviewer; did NOT produce it. Read-only in every repo checkout; all probes in /tmp/claude-0/t164-g4b/ (fresh; old .../t164-g4/ ignored). Pinned material head 6dde13459 (task/wave24-report-v3, /root/project/w-wave20), isolated via `git archive 6dde13459 | tar -x`. lanes venv; w-wave20 node_modules (apps/web package.json+lockfile+configs byte-unchanged pinned->HEAD) symlinked onto pinned-head source. Built on G1(PASS)/G3(PASS); did not repeat their work.

VERDICT: PASS  (no REQUIRED findings; 3 ADVISORY)

SCOPE: the single M5-T164 commit (6dde13459 vs its parent) touches exactly 22 files, ALL inside allowed_paths; forbidden paths (services/api/app/scenario, drawings, journey fixture, apps/web/src/components, tests/drawings/report, test_study_contracts.py, docs/) untouched.

SCENARIO TABLE (scenario | how tested | result | exit)
S1 existing valid results fixtures | git diff aac892fc..6dde13459 -- valid/results (name-status) + validate_contracts over all | only 2 Added (synthetic_*_1_5_0); 10 existing incl. journey still pass, none modified | 0
S2 two new valid 1.5.0 examples validate | validate_contracts; both Python validators; web probe | ACCEPT by all | 0
S3 not_known check w/ number; withheld placement w/ outline; allocation w/ zones | own probes, both Python validators + validate_contracts + web | Python REJECT all 3 at intended path ($.rear_yard / $.building_alternatives); web REJECT withheld+outline; web ACCEPTS extra 'zones' (ADV-1) | 0
S4 placement/allocation label != "Illustrative" | own probe (label="Draft") both Python + web | REJECT (const) by all | 0
S5 input_fact basis outside nine ("tax_map") | own probe both Python + validate_contracts; enum==QUANTITY_BASES compared to tools/research_record_check.py:51 | REJECT at $.input_facts; enum == the 9 bases exactly | 0
S6 1.5.0 block requires contract_version 1.5.0; copies identical; results.ts regen | reverse-binding probe (both fixtures set to 1.4.0) both Python; sha256 of both schema copies; generate_ts_types.py --check | downgraded docs REJECT at <root>; copies byte-identical (4cf90a9c…395d7, diff exit 0); "types up to date" | 0
S7 validate_contracts + pytest .github/scripts/tests | ran both | "Checked 23 schema file(s); 0 failure(s)"; 24 passed | 0 / 0
S8 journey fixture unchanged | git diff aac892fc..6dde13459 -- journey | empty (unchanged) | 0
S9 each valid example = journey + only new blocks | strip rear_yard/envelope_rows/input_facts/constraint_lines/plate-tags/placement/area_allocation + reset version+identity, compare to journey | stripped==journey TRUE both; identity distinct | 0
S10 fan-out green & unedited | services/api pytest tests/contracts tests/drawings tests/cad tests/api/test_results_read_api.py; new file alone; apps/web vitest src/lib src/components/architect/answers | 2544 passed/6 skipped; new file 71 passed; web 76 files/1464 passed | 0/0/0
S11 web accepts 1.5.0, rejects unknown | own web probe (1.6.0) | 1.5.0 ok, 1.6.0 ok=false | 0
S12 1.5.0 way-break refused by both Python + web; 1.4.0 unchanged | fitted=true+withheld probe both Python + web; journey(1.4.0) accepts; results_way_violations([]) on 1.4.0 BA fixture | REJECT (allocation_fitted_without_placement) all three; 1.4.0 clean | 0
S13 share out of 0.60-0.75, or missing measure/conversion | own probes 0.5999/0.60/0.75/0.7501 + delete measure + delete conversion, both Python + validate_contracts + web | 0.5999/0.7501 REJECT, 0.60/0.75 ACCEPT; missing measure/conversion REJECT | 0

PROBES: 14 Python-validator probes (probes.py) ALL_OK, both validators agree on every case; 8 web probes ALL pass (incl. S11 1.6.0 reject, S12 fitted+withheld reject, S4 label, S13 share/total). Each invalid fixture rejects at exactly its intended location per validate_contracts.

MUTATION PROOF (mine, in scratch, both restored to byte-identical git objects):
M1 schema share maximum 0.75->1.0 (bundled copy) => my S13 share=0.7501 probe flips REJECT->ACCEPT (both validators). M2 remove "1.5.0" from CONTRACT_VERSIONS_WITH_WAY_LAYER => my S12 fitted+withheld probe flips REJECT->ACCEPT (way rule goes silent). After restore both probes REJECT again; restored files sha256 == pinned-head objects (schema 4cf90a9c…, way-rules 0e1a0f88…). Probes are genuinely sensitive.

RESEARCH & VERIFICATION (D-093): I AGREE it changes no property fact, rule applicability, calculation input, result or certainty label. Basis: schema additions are all optional (S1 byte-for-byte, S8 journey untouched); validators only gain version "1.5.0" + an additive helper that returns [] for every pre-1.5.0 doc (verified on the 1.4.0 building_alternatives fixture); no evidence record / docs/ / scenario (calculation) code is in the M5-T164 commit; new fixtures use made-up illustrative values — the benchmark 20150 appears in NO new 1.5.0 block of either fixture; not_known rows carry no number, withheld placements no outline, illustrative geometry is labelled. Could not check: byte-exactness of the conversion_statement/measure const to the docs/design R092 wording (docs/ is forbidden/unchanged — G1/DCV's domain; I confirmed the const is enforced and a doc missing it is rejected).

FINDINGS
ADV-1 (concurs G1-A3/G3-A3, now demonstrated): the web reader guard (checkPlacement/checkAreaAllocation) validates only the fields the panel reads and does NOT enforce additionalProperties:false, so an extra key such as `zones` on area_allocation passes the client guard. Caught server-side by the schema (both Python validators REJECT; proven) and never rendered by the panel. Acceptable disclosed web scope; extend the client guard if a page ever renders these blocks.
ADV-2 (concurs G1-A1/G3-A1): geometry.floor_plates.entries[].building tag is in schema + generated TS + reverse-binding (fires) but no positive valid fixture exercises an ACCEPTED tagged plate (the only drawable 1.4.0 fixture has floor_plates not_available). I could not independently build a positive fixture for the same reason. Add one when an engine emits tagged plates (waves 25-27).
ADV-3 (new, cosmetic, pre-existing, out of scope): both Python validators raise the hardcoded prose "results document declares contract 1.3.0 but breaks the value-state way rule" even for a 1.5.0 doc; the breach DETAIL is correct (names allocation_fitted_without_placement). The message strings live in study_contracts.py / three_answers/contract.py, which are NOT in the M5-T164 diff; the new 1.5.0 breaches now flow through that same message. No functional impact; worth a one-line message fix in a later task.

WHAT I COULD NOT CHECK
- modularity_check.py --check: fails in the git-archive scratch (no .git / `git ls-files`); G3 verified exit 0. I confirmed sizes instead: results_way_rules.py 236 SLOC, results-contract-checks.ts 572 SLOC (WARN_SLOC 600); new helper is single-responsibility and correctly placed in the way-rules module — no modularity concern.
- SVG/DXF snapshots not regenerated from the renderer; their consuming tests pass in the fan-out (tests/drawings/kit, tests/cad green), so the committed snapshots are self-consistent with the pinned-head renderer.
- Full services/api pytest (2548) + whole web suite + security checks are CI's job at the accepted head (D-090-R639) — confirm CI green there before accept.
- Per-requirement D-094 (R017/R026/R044/R058/R079/R082/R091/R092/R094/R096) verification is the directive-compliance-verifier's pass (producer != verifier); I verified the scenario-level evidence overlapping several (nine-bases enum = R-bases; Illustrative label; share 0.60-0.75; conversion-statement const enforced).
- Provenance note (process, flag for orchestrator; concurs G3-A2): commit 6dde13459 co-author trailer reads "Claude Opus 5.5"; per D-085 the builder subagent should run on Opus 4.8 — verify via transcript. No code impact.

END-OF-REPORT
