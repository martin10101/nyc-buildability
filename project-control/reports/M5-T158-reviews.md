# M5-T158 reviews (every return kept unchanged)

- G1 data-contract-verifier at 1e43857e: PASS (NB-01 revision 3 agrees; live index still lists the ZONE against lots 1 and 70; two advisories). Carry to a68901be confirmed (NB-01 entry, NB-05 revision 3 accurate).
- NB-05 revision 3 (part B moved three of its linked code files): delta-reviewed by a data-contract-verifier at fb52a874 (agrees); entry recorded 2a7cc7f0.
- G3 code-reviewer at 1e43857e: PASS with one REQUIRED correction (F1: the journey test hit the study-route rate limiter; documented command not reproducible) and one advisory (module size, backlog DB-238). Correction round C (test-only) integrated a68901be; delta PASS. The orchestrator re-ran the failing order at a68901be: tests/scenario/three_answers tests/journey 482 passed, 2 skipped; the documented command 3439 passed, 8 skipped (session-2026-10-11b/repro-T158-F1.txt).
- G4 qa-engineer at 1e43857e: PASS with three advisories (per-state emit tests, a structural guard, a NOT_READ route test), all applied in round C; delta PASS with the reviewer's own mutations.
- G5 security-reviewer at 1e43857e: PASS with two advisories (malformed server id; request fan-out) kept for the flag's production-enablement review (backlog DB-237); carry to a68901be confirmed.

## G1

<!-- saved unchanged by save_return.py from agent-a51ca56bf0fd96b93.jsonl, entry 2026-10-11T07:26:20.787Z, sha256 79e26272042440328c93cbbd8466622a2dad046408c8f3f70ec23e535e69c047 -->
# G1 (data-contract-verifier) review — M5-T158 / DB-232, NB-01 revision 3

Frozen head `1e43857ee0ca46da1da91ad1ed0d813cf41d0bdc` on `task/wave23-density-zoning-lot` in `/root/project/w-wave20` (worktree clean at that head; acris/classifier files unmodified). Read-only. Research & verification (D-093): I opened the primary sources NB-01 cites, worked the expected result myself before reading the code, and did a read-only live confirmation against the official Socrata datasets.

## VERDICT: PASS (verdict "agrees"). No REQUIRED corrections. Two ADVISORY notes below.

---

## What I checked myself (reproducible)

### Part 1 — Connector `services/api/app/connectors/acris_index_soda.py`
- Datasets correct: Legals `8h5j-fqxa`, Master `bnx9-e6tj`, codes `7isb-wh4c` (module constants). Confirmed against **live** Socrata metadata.
- URL builders ran and match NB-01 byte-for-byte: `build_legals_by_lot_url(4,7334,70,...)` == E8 URL; `build_legals_by_documents_url([...3 ids],...)` == E9 URL. Q2 `build_master_url` emits `$select=document_id,doc_type,document_date,recorded_datetime,crfn,good_through_date` — **document_amt absent**; Q4 `$select=max(good_through_date)`.
- `MASTER_SELECT` has no `document_amt` and no `recorded_borough`. The Parties dataset is never referenced anywhere in the module.
- BBL normalized first: `fetch_zoning_lot_index` calls `normalize_bbl(bbl)` before any request; a bad BBL raises `BBLValidationError` with no request made (and the seam maps it to NOT_READ).
- Paging bounded/stable: Q1 uses `$order=document_id`; `_fetch_all_pages` pages by `$limit/$offset` to a short page, else raises `PageBudgetExceededError` (max_pages=20) — refuses silent truncation.
- Fail-closed to NOT_READ: whole typed taxonomy subclasses `AcrisIndexConnectorError` (rate_limited, schema_drift, timeout, source_unavailable, page_budget_exhausted, incomplete_index). The study-inputs seam (`study_inputs.py:517`) maps **every** `AcrisIndexConnectorError` → `not_read(...)`, never NONE_FOUND; `IncompleteIndexError` fires when a subject doc has no Master row. Confirmed by the green error-path tests.
- `recorded_borough` never used (not selected; module docstring notes it reads "1" on these Queens docs).

### Part 2 — Fixtures + MANIFEST (`services/api/tests/fixtures/benchmark_215_16_northern/acris_index_*`)
- Raw SHA-256 of all five connector fixtures MATCH the values recorded in NB-01 (E8/E9) and the MANIFEST (Q1 4340109f, Q2 81cd75bf, Q3 d8b5c868, Q4 9b2e2a01, codes 518363…).
- Parsed-row equality to the evidence pack (`docs/research/owner-research/2026-10-10-215-16-northern-evidence/data/`): Q1 == evidence `acris_legals_lot70_primary.json` AND the B-01 fixture copy (order-only byte difference, as claimed — connector adds `$order=document_id`); Q2 == evidence `acris_master_all.json` (7 ids) AND B-01 master; Q3 == evidence `acris_legals_keydocs.json` restricted to the 3 ZONE/DECL/CERT ids; Q4 and codes are **byte-identical** to the evidence pack.
- Pinned `DOCUMENT_TYPE_DESCRIPTIONS` match the recorded 126-row codes copy (`doc__type`/`doc__type_description`): ZONE="ZONING LOT DESCRIPTION", DECL="DECLARATION", CERT="CERTIFICATE".
- Synthetic variants: MANIFEST states none are stored; synthetic classifier inputs are built inline in the tests and labelled there (S2/S5/S6).

### Part 3 — Reading DB232-R1 (`services/api/app/profile/zoning_lot_index.py`), worked independently
From ZR 12-10(b)-(d) (E6: zoning lot within a single block) + the codes table (E3), I derived the benchmark expectation before reading the classifier, then ran my own end-to-end connector→classifier replay through a URL-routed fake transport: state **OTHER_LOTS_NAMED**, same-block lot **4073340001**, ZONE **2022020201551002** CRFN **2022000059134** recorded 2022-02-08, CERT+DECL reminders, as_of 2026-09-30, `figures_conditional`=True, 4 request URLs. Matches NB-01 and scenario S1 exactly.
Counterexamples and how the output words each (verified in `three_way_document.py:_zoning_lot_scope_statement`):
- DECL/CERT with no ZONE → NONE_FOUND, no condition (rule b); worded "lists no zoning lot description filed on this lot together with other lots. This is not a title search" — literally true (no ZONE), never "no zoning-lot issue". The DECL-only ZR 12-10(d) gap is disclosed (classifier docstring (b), NB-01 risks, registry `known_limitations`).
- Former-lot ZONE after a tax-lot split → NONE_FOUND can under-warn for OTHER lots; disclosed in the registry (the 2016 ZONE is indexed only against lot 1; the benchmark is saved by the 2022 re-recording against both lots). Worded "not a title search", not proof of absence.
- Cross-block development → SINGLE_LOT_ONLY with the other-block note "check what it covers"; no same-block warning (rule c).
- NOT_READ → condition added ("could not be read, so whether a recorded zoning lot description names other lots is not known"), never "none found" (S4). Scope-row value is always "Not confirmed", basis `city_records`.

### Part 4 — NB-01 revision 3
- E1 URL is now the document-id query matching its saved copy `acris_legals_keydocs.json` (4 ids: the three 2022 instruments + the 2018 doc). Confirmed.
- E8/E9/E10 added; saved copies present; SHA-256 match both raw and LF-normalized (E8=Q1 lot query, E9=Q3 doc-id query, E10=Legals `partial_lot` metadata whose column description reads exactly "P=partial E=entire").
- observed_facts vs interpretation are cleanly separated; interpretation labelled draft DB232-R1 (ADR-007); `research_status` stays `access_blocked`.
- All 10 `code_identity` hashes equal the frozen-head file bytes.
- All 14 named regression tests exist; I ran `tests/connectors/test_acris_index_soda.py tests/profile/test_zoning_lot_index.py tests/connectors/test_benchmark_215_16_northern_fixtures.py` → **70 passed**.
- `python3 tools/research_record_check.py --check` → **PASS** (exit 0); NB-01 `code_current=True`, `review_state=stale` (expected — the revision-3 review is this G1; revisions 1–2 are recorded).

### Part 5 — Read-only live confirmation (today, 2026-10-11)
- Live Legals Q3 (`8h5j-fqxa`, the three doc ids): ZONE **2022020201551002** indexed against lot 1 (215-10) AND lot 70 (215-16) on borough 4 block 7334, all partial_lot E — matches the fixture/record.
- Live Legals Q1 (borough 4 block 7334 lot 70): same 7 document ids, all partial_lot E, ZONE present — index still reads as recorded.
- Live Master metadata (`bnx9-e6tj`): doc_type ("Specific type of instrument"), document_date ("Date of Document"), recorded_datetime ("Legal date instrument was recorded"), crfn ("City Register File Number"), good_through_date ("Date of latest recording or correction included with this extract") — all present with meanings/units matching the connector's use. `document_amt`="Principal debt or obligation" **exists and is deliberately omitted**; `recorded_borough`="Borough where document was recorded" **exists and is deliberately unused**.

## What I could not check (and why)
- The actual ACRIS document images (contents of the CERT/ZONE/DECL) — viewer-gated, automated capture prohibited (registry §11.5). This is by design: NB-01 correctly stays `access_blocked` and nothing concludes the zoning lot.
- I did not re-run the full part-B journey/web/snapshot suites (G3/G4 scope); I verified the part-B scope-row/condition wording by reading the source and ran the G1-scope suites. The producer reports them green at head e97080823.
- Live `max(good_through_date)` today may post-date the fixture's 2026-09-30 — not a defect; tests are offline exact-URL replays of a point-in-time capture.

## Findings
- **ADVISORY-1** (`zoning_lot_index.py` rule (b); registry `known_limitations`): NONE_FOUND can under-warn for a DECL-only ZR 12-10(d) zoning lot or a former-lot ZONE not re-indexed to the subject lot. Honestly disclosed in the classifier docstring, NB-01 risks, and the registry; wording is a bounded negative ("not a title search", never "no zoning-lot issue"), consistent with D-051/D-093. No change required.
- **ADVISORY-2** (`zoning_lot_index.py:_other_lots`): a lot whose BBL cannot be formed from its components is bucketed as other_block (listed for checking), never same_block. Fail-safe (no false same-block warning); for well-formed NYC borough/block/lot it never arises. Informational.

## Review entry (exact shape for the orchestrator to append to NB-01)
{"reviewer": "data-contract-verifier", "date": "2026-10-11", "reviewed_revision": 3, "verdict": "agrees", "findings": ["G1 at 1e43857e: the five acris_index_* fixtures match their recorded SHA-256 (raw and LF); parsed rows equal the evidence-pack copies (Q1 order-only diff, confirmed), Q4 and the codes copy byte-identical; URL builders equal NB-01 E8/E9; MASTER_SELECT omits document_amt and recorded_borough; the Parties dataset is never queried; BBL normalized before any request; paging stable/bounded; every typed failure fails closed to NOT_READ (never NONE_FOUND).", "Independent connector+classifier replay reproduces NB-01/S1 exactly: OTHER_LOTS_NAMED naming 4073340001, ZONE 2022020201551002 CRFN 2022000059134, CERT+DECL reminders, as_of 2026-09-30; the five scope-row statements word each state correctly (NONE_FOUND/NOT_READ never 'no zoning-lot issue'; value 'Not confirmed').", "NB-01 revision 3 verified: E1 URL now the document-id query of its saved copy; E8-E10 saved copies present with matching SHA-256 (raw+LF); observed_facts vs interpretation separated; research_status stays access_blocked; all 10 code_identity hashes equal the frozen head; 14 regression-case tests exist; research_record_check --check PASS (exit 0).", "Live confirmation 2026-10-11: official Legals still indexes ZONE 2022020201551002 against lots 1 and 70 (all E) and returns the 7 lot-70 docs; Master metadata confirms document_amt='Principal debt or obligation' (omitted) and recorded_borough (unused), and good_through_date means 'index up to date through'. Disclosed DECL-only / former-lot-ZONE gaps are honest bounded negatives (ADVISORY-1)."]}

END-OF-REPORT


## G1 carry

<!-- saved unchanged by save_return.py from agent-a51ca56bf0fd96b93.jsonl, entry 2026-10-11T08:24:40.659Z, sha256 403995fcf84e819ff1cf4284232bcfad3abfdee5b3284d5904893b41b15f7c7a -->
# G1 follow-up confirmation — M5-T158, integrated head a68901be (read-only)

All four items confirmed. Verifications done via `git show`/`git diff` (worktree-independent); the record check ran at the live worktree HEAD `5fd14ac6`, but NONE of the NB-01/NB-05 record files or their listed code files changed between a68901be and 5fd14ac6 (only 4 unrelated files differ), so the result holds at a68901be.

1. NB-01 entry text == my return: CONFIRMED. The `git diff 1e43857e..a68901be` on NB-01 is a single appended `agent_reviews` entry; its four `findings` strings are byte-for-byte my returned findings. Only the date carries its time (`2026-10-11T07:26Z`) and the `report` pointer (`project-control/reports/M5-T158-reviews.md`) was added, as you described. `reviewed_revision` 3, `verdict` "agrees", `reviewed_code_identity` the 10 paths — all as expected.

2. NB-01 otherwise unchanged: CONFIRMED. The appended entry is the only change in the diff.

3. NB-01 code identities at a68901be: CONFIRMED. All 10 `code_identity` hashes equal the a68901be file bytes (raw == LF).

4. NB-05 revision 3 accurate: CONFIRMED (diff 7f47fa05..a68901be).
   - revision 2 -> 3.
   - Three code identities updated: result_way_bridge df70486d->485dff13, result_ways 09d0009d->ac0747a3 (both equal the values I verified on NB-01 — same files, same head), result_way_engine_bridge 31ee7f0a->3faa78e6; the other five unchanged. All 8 NB-05 identities verified against a68901be bytes.
   - One dependency_assessment sentence added (the M5-T158 paragraph: property-specific vs generic condition, exactly one either way, special-density decision and 680 arithmetic unchanged).
   - The `conditions` tax-lot sentence extended to name lot 1 ("Where the ACRIS index names another lot on the same block (the benchmark: lot 1), the condition names it").
   - This matches my G1 finding that part B changed the zoning-lot CONDITION only (the special-density/680 path is untouched). The other verifier's delta entry (agrees, 2026-10-11T07:55Z) is consistent.

5. `python3 tools/research_record_check.py --check`: PASS (exit 0). NB-01 code_current=True, review_state=current (my rev-3 entry cleared the earlier "stale"); NB-05 code_current=True, review_state=current.

No new findings; my PASS stands at the integrated head.

END-OF-REPORT


## NB-05 revision-3 delta

<!-- saved unchanged by save_return.py from agent-a001add3c557af12d.jsonl, entry 2026-10-11T07:57:00.940Z, sha256 4497fcf32a9c61b1ec41d40ba15824915f26ae4cffb12d084806c6eb9c57777f -->
NB-05 REVISION 3 DELTA REVIEW — data-contract-verifier, read-only, at fb52a8749abb94153ba6f52d890091d77c8d12e3 (HEAD == this commit; working tree clean for NB-05 + all 8 code files, so the record check below is valid for this head).

DELTA VERDICT: AGREES — revision 3 is accurate; my earlier PASS carries to fb52a874. The two advisories (F1 DB-snapshot not cited in the evidence array; F2 OQ-5/Appendix A kept open) still stand, unchanged by revision 3.

(1) Code identities — CONFIRMED. I recomputed LF-normalized sha256 (`git show fb52a874:<p> | tr -d '\r' | sha256sum`) for all 8:
- Changed three match revision 3's new values: result_way_bridge.py 485dff13…0fb06f, result_ways.py ac0747a3…b2af3, result_way_engine_bridge.py 3faa78e6…cca5a2.
- Other five unchanged from revision 2: engine_conditions 6768a49a, r6b_dwelling_units.rule 404179f2, special_density_geography ce2c6b15, result_way_facts 8e440578, three_way_scope_lines 8cece25b.

(2) Special-density decision + 680 arithmetic unaffected — CONFIRMED by reading the three diffs 18e62ca4..fb52a874:
- result_way_bridge.py (+87): adds `zoning_lot_citation()` projection and threads a `zoning_lot_index` param, setting `zoning_lot=zoning_lot_citation(...)` on the inputs (None -> not_checked, byte-identical). The `_density` record×statement combination table (the special-density decision) is NOT touched; special_density_geography is unchanged.
- result_way_engine_bridge.py (+7): threads `zoning_lot_index` through and passes `zoning_lot` to the emitter. No decision/arithmetic change.
- result_ways.py (+31/-7): `_unit_standard_way` EVIDENCE_NOT_IN_ONE branch changes only which zoning-lot CONDITION attaches — `zoning_lot = zoning_lot_condition(inp) or _zoning_lot_condition()` (property-specific in OTHER_LOTS_NAMED/NOT_READ, else the generic M5-T157 one; exactly one, never two). The USER_STATEMENT_NOT_IN_ONE branch adds the property-specific condition only when present. Coverage and corner-rear-yard ways also pick up the property-specific zoning-lot condition (DB-232 scope). No value is re-derived; the 680 factor/rounding lives in the rule (404179f2, unchanged). The branches still key on `DensityKnowledge`, so the decision is unchanged.

(3) Added dependency_assessment sentence + extended tax-lot condition — ACCURATE. The sentence ("Since M5-T158 (DB-232)… property-specific when the ACRIS index names another lot on the same block or cannot be read; otherwise the generic always-present condition stays; exactly one either way; special-density and 680 unchanged") matches the code I read. The extended condition's factual claim ("the benchmark: lot 1") is corroborated end-to-end by the benchmark journey fixture at fb52a874, whose unit-limit condition reads: "If lot 70 alone is the zoning lot. The city's register of recorded documents lists a zoning lot description recorded on February 8, 2022 that is filed on this lot together with lot 1 on the same block, so the zoning lot may include lot 1. The documents themselves were not read." The special-density scope note is unchanged ("outside both special density areas… conditional ceiling on the zoning lot"), and exactly one zoning-lot condition is shown.

(4) `python3 tools/research_record_check.py --check` at fb52a874 — PASS, DIRECT_EXIT=0. NB-05 status=answered_from_primary_source, code_current=True (revision-3 identities match the working tree), review_state=stale (expected — this revision-3 review is not yet recorded). 6 records all structurally valid; none claims Verified improperly.

REVIEW ENTRY (orchestrator to add):
{"reviewer": "data-contract-verifier", "date": "2026-10-11T07:55Z", "reviewed_revision": 3, "reviewed_code_identity": {"services/api/app/scenario/three_answers/engine_conditions.py": "6768a49a023ee92b2919fad14bf27c0a067171073a31ec0c6232dfe6a2f0811f", "services/api/app/rules/rulesets/r6b_dwelling_units.rule.json": "404179f2c2aab9c25826c59c92c4715fe0647a8f552cb1e385c72ccc7cb7ef02", "services/api/app/scenario/three_answers/special_density_geography.py": "ce2c6b15416ec232f04f46f0f319fc68dd807a677ab7a806c6fc3f9744de11b6", "services/api/app/scenario/three_answers/result_way_facts.py": "8e440578e5c38ed11488f64bf1d172716301b264e814926887feee9c3bff560c", "services/api/app/scenario/three_answers/result_way_bridge.py": "485dff13c10228665df4febe12a09a9412b3bd6820ae4926a46d66b06f0fb06f", "services/api/app/scenario/three_answers/result_ways.py": "ac0747a37bb4c462483041cd8f4b0fffce6ff450af492ff61aee5ca76e7b2af3", "services/api/app/scenario/three_answers/result_way_engine_bridge.py": "3faa78e607b5ac366122f94486dc9381e66f0e187f3f9b91977c8692abcca5a2", "services/api/app/scenario/three_answers/three_way_scope_lines.py": "8cece25b78227d8c63840826173220d8b06c2d805cc1a2b59ea0f5fd19abd0ee"}, "verdict": "agrees", "findings": ["Revision 3 delta verified at fb52a874: the three updated code identities (result_way_bridge 485dff13, result_ways ac0747a3, result_way_engine_bridge 3faa78e6) reproduce LF-normalized; the other five are unchanged.", "DB-232 changed the zoning-lot CONDITION only: the special-density decision (_density, special_density_geography) and the 680 factor/rounding (r6b rule unchanged) are untouched; _unit_standard_way attaches exactly one zoning-lot condition - property-specific in other_lots_named/not_read, else the generic M5-T157 one.", "The added dependency_assessment sentence and the extended tax-lot condition are accurate; the benchmark journey fixture confirms the unit-limit condition names lot 1 (recorded February 8, 2022, CRFN 2022000059134), special-density note unchanged.", "research_record_check --check PASS (exit 0); NB-05 code_current=True.", "Advisories from revision 2 still stand: the evidence array still omits the zr-12-10-special-downtown-brooklyn-district snapshot (DB source), and OQ-5/Appendix A is correctly kept open."]}

END-OF-REPORT


## G3

<!-- saved unchanged by save_return.py from agent-a35c9484078bb96f1.jsonl, entry 2026-10-11T07:39:08.586Z, sha256 f7d58575371adb2f89a113c6dba7a8f7ff91c476cf8e2ac220b10e3d40934649 -->
# M5-T158 (DB-232) — G3 code-reviewer gate report

**Frozen head:** 1e43857ee0ca46da1da91ad1ed0d813cf41d0bdc (task/wave23-density-zoning-lot, /root/project/w-wave20). Worktree clean at that head.
**Verdict: PASS WITH REQUIRED CORRECTIONS** (production behaviour correct and the full services/api CI suite is green; one REQUIRED test-isolation/reproducibility defect, one advisory).

## What I verified independently (D-093)
I opened the primary ACRIS sources in the evidence pack, not the brief/report, and worked the expected result first:
- E1 `data/acris_legals_keydocs.json` + E2 `data/acris_master_all.json`: the ZONE document **2022020201551002** ("ZONING LOT DESCRIPTION", CRFN **2022000059134**, recorded **2022-02-08**) is indexed against **both lot 1 and lot 70** on block 7334; the CERT (…133) and DECL (…661) likewise. ZR 12-10 (E6) confirms a zoning lot may span several tax lots within one block, and an index entry does not establish an instrument's contents. My independent expectation = **OTHER_LOTS_NAMED naming 4073340001**, with CERT/DECL as reminders, as-of 2026-09-30. The classifier, the seam, and the regenerated benchmark fixture reproduce exactly this. NB-01 correctly stays `access_blocked`.

Confirmed against the diff limited to M5-T158 allowed paths (`git diff 41c6778f..1e43857e`):
1. **Five states** (`zoning_lot_index.py`): `figures_conditional` True only in OTHER_LOTS_NAMED and NOT_READ — matches brief item 1.
2. **Condition** (`result_way_conditions.zoning_lot_condition`): uses `unchecked_condition`, never `contradicted_record`; carries the unique marker "register of recorded documents". `result_ways.py` threads it onto the four floor-area values, coverage and rear-yard where shown, building B, and the unit limit where the property-specific condition REPLACES M5-T157's generic one (`zoning_lot_condition(inp) or _zoning_lot_condition()`) → exactly one zoning-lot condition. Fixture: 7 marker occurrences (4 floor-area + unit limit, scope row, building B); the generic M5-T157 phrase is absent (0) on the benchmark.
3. **No combined area / no DOB remainder**: "20,000" = 0 and "39,934" = 0 in the fixture; 20,150 / 24,180 / FAR present; unit limit 29 via EVIDENCE_NOT_IN_ONE. Matches R032.
4. **Scope row** `zoning_lot`="Not confirmed", basis city_records, in every state except NOT_CHECKED; web label (`three-answers.ts`) and kit key (`drawings/kit/scope.py`) added; report open item "Zoning lot" ordered FIRST (`readers._ORDER`, `decision_open_items` preference). SVG snapshot change is additive (new row at assumptions/12 + repositioning); nothing weakened.
5. **Seam + flag** (`study_inputs.py`, `config.py`): `INTERNAL_ZONING_LOT_INDEX_ENABLED` default OFF, fail-safe posture; `acris_zoning_lot_index_provider` maps BBLValidationError and every `AcrisIndexConnectorError` to NOT_READ (never raises/503/none-found); `zoning_lot_index` defaults to `not_checked()`.
6. **Connector S9** (`acris_index_soda.py`): `normalize_bbl` runs before any request; `MASTER_SELECT` excludes document_amt and Parties is never queried; ZONE/DECL/CERT descriptions pinned from the recorded 7isb-wh4c copy with a contract test; document-id regex guard before IN-lists; all failure modes fail-closed to typed errors.
7. **NOT_CHECKED byte-identity**: `test_route_body_identical_whether_or_not_index_bound` (study route) and `test_db232_not_checked_adds_no_scope_row_or_condition` (results doc) genuinely prove it; producer's mutation proofs (shows_scope_row→True; not_checked→SINGLE_LOT_ONLY) are consistent with the code.
8. **Provenance**: all six NB-01 revision-3 `code_identity` sha256 values match the frozen-head file bytes exactly.

## Checks run (frozen head, lanes venv, PYTHONPATH=services/api)
- `ruff check .` → All checks passed.
- `tools/modularity_check.py --check` → failures 0, warnings 32 (PASS). result_ways.py (711) and three_way_document.py (904) at WARN only.
- `research_record_check.py --check` → PASS; `render_review_register.py --check` → PASSED.
- `tests/connectors tests/profile` → 1619 passed. `tests/journey` alone → 2 passed.
- **FULL `pytest tests`** (CI-style, one process) → **9380 passed, 8 skipped, exit 0** → R639 met.

## REQUIRED finding F1 — documented test command is non-reproducible (test-isolation fragility)
The packet's `documented_test_commands` pytest line and the brief's focused-suite list do NOT reproduce green at the frozen head:
- `pytest … tests/scenario/three_answers tests/journey tests/drawings tests/cad tests/api` (documented) → **1 failed, 3433 passed** — FAILED `tests/journey/test_215_16_northern_journey.py::test_recorded_journey_entry_bbl_to_results_to_exports_to_fixture` with **HTTP 429** at `tests/contracts/test_study_setup_bridge.py:98` (via `_northern_setup`).
- Brief's list `tests/connectors tests/profile tests/scenario/three_answers tests/journey tests/drawings/report tests/api` → **1 failed, 3427 passed** (same test, same 429).
- `pytest tests/scenario/three_answers tests/journey` → **1 failed, 477 passed** (minimal repro).

Root cause: the study-read route's process-wide sliding-window limiter (30 req / 60 s, `app/api/v1/study_read_api.py`) is not reset by the journey test module nor by the route-hitting `tests/scenario/three_answers` tests. `test_three_answers_three_way_emit.py::_benchmark_adapter` and `test_result_way_engine_bridge.py` each make one `/study` call via `_northern_setup` and never reset; none of the three_answers files reset the limiter. When scenario/three_answers runs immediately before the journey test, the trailing-60s `/study` count exceeds 30 and the journey test's single `/study` call 429s. The journey test passes alone and in the full suite only because the full-suite alphabetical order puts `tests/journey` before `tests/scenario` and the interleaved `tests/api` tests reset the limiter per-test. The producer's self-check "7064 passed" used `tests/scenario tests/api tests/journey` — `tests/api`'s per-test resets clear the window before journey, masking the defect.

Impact: CI's full-suite ordering currently passes (R639 satisfied), but (a) the task's own documented evidence command does not reproduce, and (b) the suite is order-fragile — sharding, randomized ordering, or any added route-hitting test can turn CI red. The journey test and its route call pre-date this task, but the journey test, the emit test, and the documented_test_commands are all in M5-T158's scope and the wave's added `/study`-hitting tests tip the count over 30.

Required fix (test-only; same shape as the existing `_reset_rate_limiter` autouse fixtures in `tests/contracts/test_study_setup_bridge.py` and `tests/profile/test_zoning_lot_index.py`): add an autouse `get_rate_limiter().reset()` fixture to `tests/journey/test_215_16_northern_journey.py` (and ideally the route-hitting `tests/scenario/three_answers` tests), and/or correct the documented_test_commands ordering so the documented evidence reproduces green. No production or benchmark-number change.

## ADVISORY A1 — module size
`three_way_document.py` is 904 lines (WARN threshold); the DB-232 scope-row statement builder is cohesive but the module is sizeable — consider extracting `_zoning_lot_scope_statement`/`_apply_zoning_lot_scope_row` in a future task. `result_ways.py` (711, WARN) grew minimally and cohesively for this task. modularity_check passes; not blocking.

## Not checked / limits
- apps/web vitest not run (backend G3 scope); I inspected the additive `three-answers.ts` label (one-line map entry matching the kit key). Flag for the web/walkthrough reviewer — producer reported web green.
- Live ACRIS egress correctly never exercised (flag off; offline exact-URL replay). Professional/legal verification of draft rule DB232-R1 is out of scope (ADR-007, labelled draft).
- Directive-requirement-to-evidence completeness is the directive-compliance-verifier's pass; I verified the behaviours above, not each D-090/D-093/D-094 requirement id individually.

END-OF-REPORT


## G3 delta

<!-- saved unchanged by save_return.py from agent-a35c9484078bb96f1.jsonl, entry 2026-10-11T08:25:42.883Z, sha256 a13bbb5016d9c04086e4a912e539e555b401be55e68cf8f6cefc796284e4c139 -->
# M5-T158 — G3 delta verdict on correction round C (head a68901be)

**Delta verdict: PASS — F1 resolved.**

## (1) Repro / documented command — fix verified (by inspection; could not execute, see note)
F1 was: the journey test's single `/study` call 429s when `tests/scenario/three_answers` runs immediately before `tests/journey`, because the process-wide study-route limiter (30/60 s) was not reset. The fix is correct and complete:
- `tests/journey/test_215_16_northern_journey.py` now imports `get_rate_limiter` from `app.api.v1.study_read` (line 47) and adds an autouse fixture (line 137) that resets it before AND after every test (144/146).
- I confirmed this is the SAME singleton the study route enforces (`study_read.py` `_RATE_LIMITER`/`get_rate_limiter`, the 429 source) and the same one `_northern_setup` saturates via `GET /api/v1/properties/{bbl}/study`. So every journey test now starts with an empty limiter → its one `/study` call cannot 429, regardless of any prior route-hitting module. This deterministically fixes the minimal repro and the documented command. It is the exact pattern already working in `tests/contracts/test_study_setup_bridge.py` and `tests/profile/test_zoning_lot_index.py` (both of which I ran green in round 1). `test_three_answers_three_way_emit.py` got the same autouse reset (it was the main saturator — defense in depth).

Execution note: I could not run the repro at a68901be myself — the read-only guard blocks shell file-writes, so a `git archive | tar -x` export fails. I rely on the above inspection, the empty production diff, and your captured one-process full run (9385 passed, 8 skipped). The full run is alphabetical (journey before scenario), so it corroborates but does not itself exercise the scenario-before-journey order; the inspection above is what proves that order is fixed. If you want belt-and-suspenders, an orchestrator-captured `pytest tests/scenario/three_answers tests/journey` at a68901be would show it green.

## (2) Production unchanged — confirmed
`git diff 1e43857e..a68901be -- services/api/app apps/web/src` is EMPTY. No production file changed since my frozen head. (Out-of-scope changes — `tools/research_record_check.py`, NB-05, M0-T192 records — belong to another task and are not part of this M5-T158 delta.)

## (3) New tests assert real behaviour — confirmed
- Journey structural guard (C3): enumerates every shown value whose sources cite `{bbl}:lot_area` and every building alternative, asserts each is `conditional` with EXACTLY ONE marker ("register of recorded documents") condition, with a non-vacuous `>= 1` check. Catches a future lot-area figure missing or doubling the condition.
- `test_db232_connector_failure_route_answers_200_with_could_not_be_read` (C4/S4): drives the PRODUCTION `acris_zoning_lot_index_provider` with a 503 transport → asserts NOT_READ, route 200, exactly one "could not be read" condition, scope row "Not confirmed"/"could not be read", and "none found" absent from the whole document. Real end-to-end NOT_READ.
- Four emit per-state tests (C2): NOT_READ/NONE_FOUND/SINGLE_LOT_ONLY/another-block, asserting the correct scope-row wording ("not a title search", "filed on this lot alone", "another block"/"check what it covers") and condition presence/absence. Closes the document-level S2/S3/S4/S5 gap.

My round-1 ADVISORY A1 (three_way_document.py at 904 lines) stands — unchanged, non-blocking.

END-OF-REPORT


## G4

<!-- saved unchanged by save_return.py from agent-a9c7f1dd92e785b83.jsonl, entry 2026-10-11T07:33:54.670Z, sha256 fd5e2beb370a604be7b2bf4cd3317b147f3f34a01af1e52ab65b5950fd4d8b2a -->

# G4 GATE REPORT — M5-T158 (DB-232 zoning-lot warning from the ACRIS index)

Reviewer: qa-engineer (independent, read-only). Gate: G4 (tests).
Frozen head: 1e43857ee0ca46da1da91ad1ed0d813cf41d0bdc (task/wave23-density-zoning-lot).
Method: `git archive` export of the frozen head under /tmp; lanes venv
(/root/project/lanes-runtime/venv, Python 3.12.3). Primary sources opened directly
(NB-01 revision 3 + evidence E1–E10, work order, benchmark fixtures); expected values
re-derived before reading the tests. No project-control/git/gh run; ports untouched.

## VERDICT: PASS (3 ADVISORY findings, no REQUIRED defects)

## Required runs (reproduced in my export)

1. Full api suite (binding item 4):
   `PYTHONPATH=. python -m pytest -q -p no:cacheprovider tests/scenario tests/api
   tests/journey tests/drawings tests/cad tests/rules tests/connectors tests/profile
   tests/test_lane_flags.py`
   → **7064 passed, 8 skipped, 1 warning in 349.59s** (the 1 warning is the pre-existing
   Starlette/httpx TestClient deprecation). Matches the producer's reported count.
2. Web (apps/web): `npx --yes npm@11.18.0 ci --no-audit --no-fund` → 314 packages; then
   `npx vitest run` on the four changed files (three-answers, presented-notices,
   journey-215-16-northern, three-answers-panel) → **4 files passed, 136 tests passed**.

## My own mutations (break → fail → restore; both restored, files byte-clean)

M1 (classifier bucketing, app/profile/zoning_lot_index.py:216): changed
`bucket = same_block if other.same_block else other_block` → `bucket = same_block`
(treat an other-block lot as same-block). → `test_another_block_zone_is_not_a_same_block_warning`
AND `test_mixed_document_triggers_only_on_same_block_lots` FAILED (other-block 4073350005
wrongly listed as same-block). Restored → 2 passed.

M2 (fail-closed mapping, app/api/v1/study_inputs.py:518): changed the connector-failure
handler `return not_read(canonical_bbl, reason=exc.error_type)` →
`return not_checked()` (a connector failure silently returns the benign NOT_CHECKED).
→ `test_live_provider_maps_schema_drift_to_not_read` FAILED (got NOT_CHECKED /
figures_conditional False, expected NOT_READ / True); the malformed-BBL test still passed
because it uses the untouched validation branch — a correctly targeted bite. Restored → green.

## Independent source cross-check (D-093)

From NB-01 E2/E9/E3 I derived, before reading the tests: ZONE 2022020201551002, CRFN
2022000059134, recorded 2022-02-08, doc_date 2016-08-09, indexed against lots 1 and 70 (both
partial_lot E); other same-block lot = BBL 4073340001; CERT 2022000059133 + DECL 2022000121661
are reminders; as-of (max good_through) 2026-09-30. Floor area 20,150 = 10,075×2.0; unit limit
29 = floor(20,150/680)=floor(29.63). The committed fixtures
(acris_index_master_*, acris_index_legals_*_zone_decl_cert, *_good_through) carry exactly these
bytes, and the codes fixture sha256 (518363…c625) equals the value the connector test pins and
NB-01 E3. Every test expectation I checked (classifier, connector, journey, report) matches my
own derivation, not a program run.

## Scenario-by-scenario (binding item 1)

- **S1 OTHER_LOTS_NAMED** — STRONG. classifier `test_benchmark_replay_names_lot_1_with_crfn`;
  connector `test_benchmark_replay_classifies_other_lots_named`; journey end-to-end (20,150
  carries the condition naming lot 1 + file 2022000059134 + "February 8, 2022",
  kind unchecked_condition; scope row value "Not confirmed"/basis city_records/"lot 1"/"not a
  title search"; 13 assumptions); live route (`test_m5t146_live_route…`, 200 + building B
  condition); report first open item.
- **S2 SINGLE_LOT_ONLY** — classifier `test_single_lot_only_when_zone_names_this_lot_alone` ✓
  (state, no condition, no other lots, crfn). Scope SENTENCE not tested at emit (see F1).
- **S3 NONE_FOUND** — classifier `test_none_found_when_no_zone_document` ✓ (state,
  figures_conditional False, as_of). Scope SENTENCE ("not a title search", never "no
  zoning-lot issue") not tested at emit (see F1).
- **S4 NOT_READ** — connector failure paths all raise typed errors (timeout→SourceTimeout,
  503→SourceUnavailable, 429→RateLimited, 400 no-such-column→SchemaDrift, other-400→Unavailable,
  non-JSON/obj→SchemaDrift, missing field→SchemaDrift, page-budget→PageBudgetExceeded, missing
  Master row→IncompleteIndex); provider `test_live_provider_maps_schema_drift_to_not_read`
  (figures_conditional True); `test_not_read_state`. No single end-to-end test drives a NOT_READ
  index through route/emit to assert the "could not be read" condition + 200 together (see F1/F3).
- **S5 another block** — classifier `test_another_block_zone_is_not_a_same_block_warning` +
  `test_mixed_document_triggers_only_on_same_block_lots` ✓. "check what it covers" scope wording
  not tested at emit (F1).
- **S6 DECL/CERT only; partial_lot P** — STRONG:
  `test_decl_or_cert_only_is_reminder_only_no_condition`,
  `test_partial_lot_p_on_a_zone_is_conditional`.
- **S7 NOT_CHECKED byte-identity** — STRONG:
  `test_db232_not_checked_adds_no_scope_row_or_condition`,
  `test_route_body_identical_whether_or_not_index_bound`,
  `test_assemble_defaults_to_not_checked_and_is_inert`.
- **S8 guard + no 39,934** — STRONG: journey asserts the condition on max_residential_floor_area,
  the unit limit (exactly ONE zoning-lot condition, the property-specific one replacing the
  generic, "whole zoning lot" absent) and building B, plus `assert "39,934" not in blob and
  "39934" not in blob`, plus a byte-exact fixture comparison. I confirmed the fixture carries the
  condition on exactly the 6 figures the work order names (4 floor-area values + unit limit +
  building B). See F2 re: the guard being fixture-anchored.
- **S9 connector requests** — STRONG: `test_bbl_is_validated_before_any_request`,
  `test_no_request_asks_for_document_amt_or_the_parties_dataset`,
  `test_pinned_codes_match_the_recorded_control_codes_copy` (+sha256),
  `test_url_builders_are_stable_and_scoped`, `test_malformed_document_id_cannot_enter_a_query`.

Classifier states each have one test with an input/expected table (header comment at
tests/profile/test_zoning_lot_index.py:104–115). Lane-flag fail-safe posture is covered
(name, absent→off, non-true tokens incl. ""/" "/"maybe"→off, true tokens→on, process default off).
Fixture-pack integrity test checks each file's sha256/http_status/https/capture-date and rebuilds
every ACRIS URL from the connector's own builders.

## Item 2 (expected values from recorded data/rule text; synthetic labelled) — MET

Expected values trace to NB-01 E2/E3/E9 and the fixtures, not a program run; the journey reads
the benchmark pack value (`_benchmark_value(...)==20150`). README states "No synthetic files are
stored in this pack — synthetic classifier inputs … are built inline in test_zoning_lot_index.py
and labelled there"; the classifier file labels them inline (SUBJECT_ENTIRE / SAME_BLOCK_LOT_1 /
OTHER_BLOCK_LOT; correlation_id="synthetic").

## Item 5 (changed expectations explained; none weakened) — MET

Web counts moved 2→3 and `has(2)`→`has(3)` (three-answers.test.ts, presented-notices.test.ts,
three-answers-panel.test.tsx) — each is a STRENGTHENING (also adds a "zoning lot" content
assertion / `index.size===3` / `local.length===0`), explained in-code and matching the producer's
list. Note: the diff range 41c6778f..1e43857e bundles M5-T157/T159/T160 (already accepted); the
emit-test changes `29.0 not in`→`29.0 in` and the S5/S8 rewrites are M5-T157-driven (unit limit
shown as a conditional ceiling) and explained — not an M5-T158 weakening.

## Findings

**F1 (ADVISORY)** — The per-state scope SENTENCE wording for NOT_READ, NONE_FOUND,
SINGLE_LOT_ONLY and the another-block clause ("check what it covers"), generated in
three_way_document._zoning_lot_scope_statement (app/scenario/three_answers/three_way_document.py
:744–768) and result_way_conditions._not_read_condition (:277+), is exercised by NO test at the
document/emit level — only OTHER_LOTS_NAMED (benchmark) and NOT_CHECKED (no row) run end-to-end
(grep for `zoning_lot_citation`/`ZoningLotCitation`/these wordings returns nothing in tests
beyond the benchmark). The classifier STATE for each is tested, so a reword/regression in those
templates (e.g. NONE_FOUND emitting "no zoning-lot issue", or the NOT_READ condition dropping at
emit) would pass CI. Recommend a small emit/document test per non-benchmark state. (Not in the
G4 explicit checklist, which requires "one test per classifier state" — met.)

**F2 (ADVISORY)** — The S8 "guard over every lot-area figure" is enforced by explicit assertions
on 3 of the 6 condition-bearing figures (max_residential_floor_area, unit limit, building B) plus
the byte-exact journey fixture (covers all 6) and the no-39,934 structural check. There is no
structural loop that enumerates every value citing 4073340070:lot_area and asserts the condition;
the guard is anchored to the frozen benchmark fixture (a blind fixture regen could mask a future
lot-area figure added without the condition). My mutation and the producer's mutation #1 both show
the current guard bites, so this is robustness only.

**F3 (ADVISORY, minor)** — S4's "the route still answers 200" with a NOT_READ index is only
covered compositionally (provider→NOT_READ test; route-with-OTHER_LOTS_NAMED-index test;
NOT_CHECKED byte-identity test); no single test threads a NOT_READ index through the route/emit.

Observation (not a G4 finding; for G1/code-review): the pack README cites SOURCE_ACCESS_REGISTRY
§11.5 while the producer report part A cites §11.4.

## What I could not check
- Live ACRIS network behavior (all tests are offline replay by exact URL, by design — correct).
- Real DWG/DOB-image contents (out of scope; connector reads index metadata only, confirmed).
- I did not run the heavy full `tools/test_directive_compliance.py` (CI's job / separate DCV gate).

## Reproducible commands
- `cd <export>/services/api && PYTHONPATH=. python -m pytest -q -p no:cacheprovider tests/scenario
  tests/api tests/journey tests/drawings tests/cad tests/rules tests/connectors tests/profile
  tests/test_lane_flags.py` → 7064 passed, 8 skipped.
- `cd <export>/apps/web && npx --yes npm@11.18.0 ci --no-audit --no-fund && npx vitest run
  src/lib/architect/__tests__/three-answers.test.ts
  src/lib/architect/__tests__/presented-notices.test.ts
  src/components/architect/answers/__tests__/journey-215-16-northern.test.tsx
  src/components/architect/answers/__tests__/three-answers-panel.test.tsx` → 4 files, 136 passed.
- Mutations: sed edits at app/profile/zoning_lot_index.py:216 and app/api/v1/study_inputs.py:518,
  each followed by the targeted pytest selector above, then restore.

The G4 test gate is satisfied: every required test element is present and verified, the full api
suite and the web tests pass in a clean export at the frozen head, the mutations bite, and no
required expectation is weakened. The three findings are ADVISORY (regression robustness) and do
not block acceptance.

END-OF-REPORT


## G4 delta

<!-- saved unchanged by save_return.py from agent-a9c7f1dd92e785b83.jsonl, entry 2026-10-11T08:27:09.911Z, sha256 93f5104c6960634b66f2375b298ec7ab497dcd65764c6e13ab177c9a77a2b9d8 -->

# G4 DELTA — M5-T158 correction round C (head a68901bee5758901e997da892d718601b4a5b3ac)

Independent, read-only. Fresh `git archive` export at a68901be; lanes venv (Python 3.12.3).
My F1–F3 advisories were applied test-only (orchestrator confirms no production file changed);
I verified that against the diff surface by mutating production in a throwaway copy — the new
tests, not the implementation, carry the added coverage.

## Runs (reproduced)
- The six new/updated tests (the four `test_db232_emit_*`, the journey structural guard,
  `test_results_read_api.py::test_db232_connector_failure_route_answers_200_with_could_not_be_read`)
  → **6 passed**.
- `PYTHONPATH=. python -m pytest -q -p no:cacheprovider tests/scenario/three_answers tests/journey`
  → **482 passed, 2 skipped**.

## My own mutations (throwaway copy; one per advisory; each restored to green)

**F1** (per-state emit scope sentence). In `three_way_document.py:761` I reworded the
SINGLE_LOT_ONLY branch (dropped "filed on this lot alone", changed "was not read"→"was reviewed").
→ `test_db232_emit_single_lot_only_says_filed_on_this_lot_alone_and_not_read_no_condition` FAILED
(`assert 'filed on this lot alone' in ...`). Restored. The new emit tests now drive NOT_READ,
NONE_FOUND, SINGLE_LOT_ONLY and the another-block clause through `emit_three_way_document` on a
made-up R6B lot (no benchmark-fixture dependency) and assert the scope wording, the "could not be
read" condition for NOT_READ, "not a title search"/as-of for NONE_FOUND, and that none is worded
"none found"/"no zoning-lot issue" — exactly the emit-level gap F1 named.

**F2** (structural guard). In `result_ways.py:187` I attached `zoning_lot_condition` only when
`key == "max_residential_floor_area"`, so the FAR / qualifying floor-area figures silently lost it.
The named-key assertions (which check only max_residential_floor_area, the unit limit and building
B) still passed, but the new structural guard FAILED at journey:424 —
`AssertionError: max_residential_floor_area_qualifying_affordable_or_senior / assert 0 == 1`.
Restored. The guard enumerates every shown value whose `sources[].ref == "<bbl>:lot_area"` plus
every building alternative, asserts exactly one index condition each, and is non-vacuous
(`lot_area_values_checked >= 1`). This is precisely the figure-coverage robustness F2 asked for:
it catches a lot-area figure added/left without the condition that the named assertions miss.

**F3** (NOT_READ route). In `study_inputs.py:518` I made the connector-failure handler fail open
(`return not_checked()` instead of `not_read(...)`). →
`test_db232_connector_failure_route_answers_200_with_could_not_be_read` FAILED (classified
NOT_CHECKED, not NOT_READ). Restored. The new test binds a 503-through-retries transport so the
route genuinely exercises the connector-failure path end to end, answers 200, and carries exactly
one "could not be read" condition with the scope row "Not confirmed" — closing the end-to-end seam
F3 named.

## Research/verification (D-093)
The NONE_FOUND emit test's "September 30, 2026" as-of is the synthetic `_result` default, matching
NB-01 E2's dataset good-through date; expected wordings trace to the work-order sentences and
rule DB232-R1, not a program run. NB-01's review entry and NB-05 revision 3 (part B moved its
linked code) are record-side only and do not bear on the test gate. No production behavior was
changed by round C.

## Delta verdict: PASS
All three G4 advisories (F1, F2, F3) are properly closed with non-vacuous tests that bite under a
targeted regression and pass when restored; the two affected suites are green at a68901be. No new
findings.

END-OF-REPORT


## G5

<!-- saved unchanged by save_return.py from agent-ab00468fe22aaeb30.jsonl, entry 2026-10-11T07:24:00.477Z, sha256 e9ec877c6294ee0c1eda17f6e215347322cf22bf944c7aa294bbb218241cb2de -->
# G5 SECURITY GATE REPORT — M5-T158 (DB-232: ACRIS zoning-lot index warning)

- Task: M5-T158 (part A connector/classifier/seam/flag + part B wiring). Gate: G5 (security-reviewer). Reviewer role: independent, read-only.
- Frozen head reviewed: `1e43857ee0ca46da1da91ad1ed0d813cf41d0bdc` on `task/wave23-density-zoning-lot` in `/root/project/w-wave20` (confirmed HEAD == frozen).
- Range for the task change: `41c6778f..1e43857e` (M5-T157/T159/T160/M0-T191 already accepted on this branch; I scoped my security pass to T158's allowed_paths, security-relevant files first).
- **VERDICT: PASS.** No REQUIRED findings. Two ADVISORY notes for the future production-enablement review (neither blocks acceptance; neither is an exploitable defect at the frozen head).

## What I verified independently (from source + primary sources + live tests)

I read the actual source at the frozen head rather than trusting the producer report: the connector (`services/api/app/connectors/acris_index_soda.py`), the shared transport (`services/api/app/resilience/transport.py`), the BBL normalizer (`services/api/app/connectors/bbl.py`), the pure classifier (`services/api/app/profile/zoning_lot_index.py`), the study-inputs seam (`services/api/app/api/v1/study_inputs.py`), the flag module (`services/api/app/config.py`), the `results_read.py` one-line change, the five new fixtures, and the connector/classifier tests. I opened the primary-source evidence record `docs/research/evidence-records/NB-01-zoning-lot-instruments.json` (revision 3) and `docs/SOURCE_ACCESS_REGISTRY.md` §11 to verify the access posture. I ran the offline tests with the lanes venv.

Live test evidence (read-only, offline, no ports touched), cwd `services/api`, `PYTHONPATH=.../services/api`, interpreter `/root/project/lanes-runtime/venv/bin/python`:
- `tests/connectors/test_acris_index_soda.py tests/profile/test_zoning_lot_index.py tests/connectors/test_benchmark_215_16_northern_fixtures.py` → **70 passed**.
- `tests/test_lane_flags.py tests/api/test_study_inputs_live.py` → **45 passed**.
(I did not run the full services/api suite; per R639 that is CI's job at the accepted head.)

## Checklist item 1 — external calls (host/dataset pinning, input escaping, bounds, fail-closed parsing): PASS

- Host pinned and not user-controllable. `LEGALS_BASE_URL`/`MASTER_BASE_URL` are hardcoded to `https://data.cityofnewyork.us/resource/{8h5j-fqxa|bnx9-e6tj}.json` (connector:101-102). No input reaches the host or path. Test `test_no_request_asks_for_document_amt_or_the_parties_dataset` asserts every requested URL `startswith` those two bases.
- SSRF defended end-to-end. The shared transport refuses ALL redirects (`NoRedirectHandler`, transport:108-123) via a module opener, so an open redirect on the official host cannot exfiltrate the token or pivot to another host; a refused 3xx is classified as a typed error, never re-issued. HTTPS only.
- BBL normalized before any network call. `fetch_zoning_lot_index` calls `normalize_bbl` first (connector:513); `bbl.py` yields validated ints (borough 1-5, block 1-99999, lot 1-9999). `build_legals_by_lot_url` interpolates those ints (connector:273) — no user string reaches the URL. Proven by `test_bbl_is_validated_before_any_request` (a `_never_called` transport; a bad BBL raises before any request).
- No $where injection. Document ids used in `$where ... in('…')` are validated against `^[A-Za-z0-9_]{1,64}$` by `_validate_document_ids` (connector:127,262-266) before building the URL (`build_master_url`:281, `build_legals_by_documents_url`:291); `$where`/`$select` are percent-encoded via `_q`. `test_malformed_document_id_cannot_enter_a_query` proves `x'); DROP` is rejected (cannot enter the query).
- IN-lists bounded: `MAX_IN_LIST = 50` (connector:123), chunked in `_fetch_by_document_ids` (:475).
- Retries/timeouts bounded through the existing transport: `request_with_retry` with `max_attempts=3`, `timeout=10.0`, retries only on 429/5xx/timeout/network (transport:430-513).
- Response size + page budget bounded: per-response body capped at `MAX_RESPONSE_BYTES = 10 MiB` (transport:62,140-148); paging capped at `max_pages=20 × page_size=1000`, raising `PageBudgetExceededError` instead of silent truncation (connector:441-459). `test_page_budget_reached_is_fail_closed` proves it.
- Parsing fails closed: non-JSON, non-array, non-object, or a missing required field → `SchemaDriftError`; a subject document with no Master row → `IncompleteIndexError`; the `query.soql.no-such-column` 400 is typed schema drift and never retried. Every connector error maps at the caller to the classifier's `NOT_READ` (never `NONE_FOUND`). Tests `test_timeout/503/429/no_such_column_400/other_400/non_json/object_instead_of_array/missing_required_field/subject_document_without_a_master_row` all pass, and `test_live_provider_maps_schema_drift_to_not_read` / `test_live_provider_maps_malformed_bbl_to_not_read` confirm the NOT_READ mapping.

## Checklist item 2 — secrets (optional app token): PASS

- `APP_TOKEN_ENV_VAR = "SOCRATA_APP_TOKEN"`, read from `os.environ` (connector:103,339-340), sent only as the `X-App-Token` request header over HTTPS (`_build_headers`:332-336). It is never placed in a URL, never in an error `detail` (details carry only `url`/`http_status`/`field`), and never logged — the transport's warning lines emit only `url`, `attempt`, `correlation_id` (transport:459-496), and request headers are never logged. Provenance stores only the plain request URLs (no token).
- gitleaks-safe: a full-diff grep found NO token-looking value literal anywhere. The only matches are the env-var NAME `SOCRATA_APP_TOKEN`, the header NAME `X-App-Token`, variable names, and the 429 message text "configure SOCRATA_APP_TOKEN…" (a name, not a value). The test `_hermetic_app_token` deletes the env var; no fixture/test/report carries a token.

## Checklist item 3 — privacy (never Parties, never amounts, no PII in fixtures): PASS

- `MASTER_SELECT` deliberately omits `document_amt` (connector:120); the Parties (grantor/grantee names) dataset is never queried by any URL builder. `test_no_request_asks_for_document_amt_or_the_parties_dataset` asserts `document_amt` absent from `MASTER_SELECT` and from every URL, and `parties` absent from every URL.
- The classifier is pure and carries only index metadata (document ids, CRFN, dates, block/lot, partial_lot flags) — no names, no amounts.
- The five new fixtures (`services/api/tests/fixtures/benchmark_215_16_northern/acris_index_*.json`) contain only public index metadata. The Document Control Codes copy (`7isb-wh4c`) carries generic party-ROLE labels (e.g. "GRANTOR/SELLER") that are the dataset's own schema metadata, not any real party. No `document_amt`, no personal names.

## Checklist item 4 — activation (default-off flag; production unchanged): PASS

- `INTERNAL_ZONING_LOT_INDEX_ENABLED` is a new flag with the same fail-safe posture as the other `INTERNAL_*` flags: absent/empty/unknown → disabled; only an explicit true token enables (`config.py`:131,218-224 via `_flag_enabled`). `config.py` is additive-only (no deletions).
- The live binding is bound only behind that flag: `_live_study_inputs_provider` sets `zoning_lot_index_provider = acris_zoning_lot_index_provider() if internal_zoning_lot_index_enabled() else None` (`study_inputs.py`:583-585). Off → `None` → `not_checked()` → `NOT_CHECKED` state → output byte-identical to the pre-wiring slice (S7). Proven by `test_route_body_identical_whether_or_not_index_bound`. The flag's docstring records the production-enablement preconditions (route auth / blocker B-001, route-local rate limit, directive scope) and states it stays OFF in production until they exist.
- No other setting/workflow/deployment file changed: a name-only scan found no `render.yaml`, `.github/`, `.env`, docker/compose, or settings file in the change set. Connector module imports do no I/O at import time (the provider's connector/classifier imports are function-local).

## Checklist item 5 — no new package (dependency policy): PASS

- No Python or npm dependency manifest or lockfile is in the change set (precise basename scan: no `requirements*.txt`, `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`, `pdm.lock`, `pyproject.toml`, `setup.*`). The packet's `forbidden_paths` also fence `apps/web/package.json`, `apps/web/package-lock.json`, and `services/api/requirements.txt`. The connector uses only the stdlib (`json`, `os`, `re`, `time`, `urllib`, `uuid`, `datetime`) plus existing in-repo modules.

## Access-control / least-privilege (D-093 primary-source check): PASS

NB-01 revision 3 and `SOURCE_ACCESS_REGISTRY.md` §11 show the connector reads ONLY the authorized NYC Open Data SODA index datasets (Legals `8h5j-fqxa`, Master `bnx9-e6tj`; codes `7isb-wh4c` pinned in code, not fetched live). §11.5 marks the ACRIS document IMAGES as having NO authorized programmatic access (viewer-gated, SR-S5); the code honors that — there is no viewer URL and no document-image fetch anywhere. The connector's recorded capture URLs in NB-01 (E8/E9) match its own URL builders exactly (`build_legals_by_lot_url(4,7334,70,…)`, `build_legals_by_documents_url([…])`), confirming provenance. The draft reading (rule DB232-R1) and NB-01 are explicitly labelled unreviewed / `access_blocked` and never conclude the zoning lot — consistent with plan P-2 "flag only" and ADR-007.

## Findings

1. **ADVISORY (robustness, not a security vulnerability)** — `services/api/app/connectors/acris_index_soda.py:262-266`: `_validate_document_ids` raises a plain `ValueError` on a malformed server-supplied `document_id`. The live provider `acris_zoning_lot_index_provider.provide` (`study_inputs.py`:510-519) catches only `BBLValidationError` and `AcrisIndexConnectorError`, so this `ValueError` would propagate (a 500) rather than mapping to the connector's fail-closed `NOT_READ`. Injection is still fully prevented and no request is issued with a bad id, and the path is unreachable with real ACRIS ids (all match the regex), so this is not exploitable. Suggested (future): raise `SchemaDriftError` (which maps to `NOT_READ`) for a malformed server id so the study still answers. No test exercises this path.

2. **ADVISORY (enablement review)** — The per-study upstream request count scales with the subject document count: Q2/Q3 fan out in IN-list chunks of 50, each chunk paging up to `max_pages`, with no hard cap on the number of chunks (bounded only by the Q1 page budget, 20×1000). Realistic single-lot data is tiny, and the `config.py` enablement checklist already requires a route-local rate limit before this binding serves production traffic. Flagged only so that rate limit is confirmed when the flag is turned on.

## What I could not check (and why)

- I did not reach the live ACRIS/SODA endpoint (no network; the brief forbids live calls). I verified behavior via the recorded fixtures, whose capture URLs I cross-checked against NB-01's primary-source evidence and the connector's own URL builders.
- I did not run the full `services/api` pytest suite or web/CI suites (read-only review; per R639 the full suites + security checks must pass in CI at the exact accepted head — that remains the orchestrator/CI responsibility). I ran the security-relevant connector, classifier, flag, and study-inputs-live tests offline (115 passed total).
- I reviewed only T158's security-relevant scope; the already-accepted M5-T157/T159/T160/M0-T191 changes in the same range (e.g. `law_links.py`'s `parts.password` URL-credential check) were out of this gate's scope and only spot-confirmed as unrelated to the new external source.

END-OF-REPORT


## G5 carry

<!-- saved unchanged by save_return.py from agent-ab00468fe22aaeb30.jsonl, entry 2026-10-11T08:23:50.839Z, sha256 cd90a8605942b81cac97a03d6772a3ec99850552452dcc0ed63cfbca57902422 -->
# G5 M5-T158 — confirmation of 1e43857e..a68901be (read-only)

Confirmed. Diffed the range read-only.

Within this task's allowed paths, the only changes are test files and records — NO production, config, CI, settings, or dependency file:
- Tests: `services/api/tests/api/test_results_read_api.py`, `tests/journey/test_215_16_northern_journey.py`, `tests/scenario/three_answers/test_three_answers_three_way_emit.py`.
- Records: `project-control/reports/M5-T158-producer-report.md`, `M5-T158-G0.md`, NB-01 (review entry), NB-05 (revision 3 code identities), `docs/DISCOVERY_BACKLOG.md`, `docs/RESEARCH_REQUESTS.md`, plus T158 task/gate ledger JSON.
- NO change to `services/api/app/**` production source; NO `config.py`, `render.yaml`, `.github/`, `.env`, docker/compose, settings, `requirements*.txt`, `package*.json`, or any lockfile. (The range also carries a separate M0-T192 task — its directive/gates/reports and `tools/research_record_check.py` + its test — all outside T158's paths and none production/CI/settings/deps.)

New NOT_READ route test (`test_db232_connector_failure_route_answers_200_with_could_not_be_read`): it drives the production `acris_zoning_lot_index_provider` over an injected `_failing_503_transport` under a `_no_network` guard and asserts the 5xx failure maps to `NOT_READ` (route still answers 200, never NONE_FOUND). A targeted grep of all added test lines found no `urlopen`/`requests`/`http(s)://`/socket/real-transport call and no token/secret/`X-App-Token`/`SOCRATA` literal. Offline, fail-closed, secret-free.

My verdict carries: **PASS**. The two advisories are correctly logged as DB-237 (WATCH) for the flag's production-enablement review.

END-OF-REPORT
