# M5-T158 producer report — PART A (backend-engineer)

Backlog DB-232: the zoning-lot warning from the city's recorded-document index (ACRIS).
Part A builds the data side (connector, classifier, fixtures, registry, study-inputs seam, flag)
that makes R029/R030 possible; part B (another builder, after M5-T157) wires it into the results.

- Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-ace22aa31f8767a1d`
- Base reset to `41c6778f8491d4a2af15d01a8291bdf1440a8c71` (branch `task/wave23-density-zoning-lot`);
  confirmed `git log --oneline -1` = `41c6778f Wave 23: G0 PASS for M5-T158 at its contract head`.
- Research & verification (D-093): read `.claude/rules/research-and-verification.md`,
  `docs/RESEARCH_AND_VERIFICATION.md`, record NB-01, and the evidence pack's primary data files
  and `source-manifest.json`. An index entry is not the instrument (NB-01 stays `access_blocked`);
  nothing here concludes the zoning lot. NB-01 itself NOT edited (orchestrator writes revision 3).

## Files changed (all within part-A scope; no part-B / NB-01 / result-way / web / snapshot file touched)

New production code:
- `services/api/app/connectors/acris_index_soda.py` (643 lines) — fail-closed ACRIS index connector.
- `services/api/app/profile/zoning_lot_index.py` (248) — pure 5-state classifier, draft rule DB232-R1.

Edited production code:
- `services/api/app/api/v1/study_inputs.py` (+84 lines; now 617) — `zoning_lot_index` carrier +
  `ZoningLotIndexProvider` seam + `acris_zoning_lot_index_provider` (live binding, maps failure
  to NOT_READ) bound only behind the new flag.
- `services/api/app/config.py` (+28) — `INTERNAL_ZONING_LOT_INDEX_ENABLED` (default OFF).

Tests:
- `services/api/tests/connectors/test_acris_index_soda.py` (284) — replay + every failure path +
  pinned-codes contract + "never document_amt/Parties" + URL builders.
- `services/api/tests/profile/test_zoning_lot_index.py` (359) — one test per state, the boundary
  cases, the benchmark replay, and the study-inputs seam (no allowed api test file in part A, so
  the NOT_CHECKED byte-identity + route-inert + live-provider tests live here; documented at top).
- `services/api/tests/connectors/test_benchmark_215_16_northern_fixtures.py` (+26) — allow the new
  capture dates; rebuild the four new connector URLs from the connector's own builders.
- `services/api/tests/test_lane_flags.py` (+43) — the new flag (name, fail-safe posture, default off).

Fixtures (benchmark pack, `services/api/tests/fixtures/benchmark_215_16_northern/`):
- 5 new `acris_index_*` data files + MANIFEST.json (+83) + README.md (+23) entries naming the connector.

Records:
- `docs/research/source-registry-drafts/acris-index.json` — placeholder replaced (mirrors ztldb.json shape).
- `docs/SOURCE_ACCESS_REGISTRY.md` §11.4 — connector, what is read, what is NEVER read, fail-closed.

## Captured fixtures (Q1–Q4 live once; cross-check)

Captured 2026-10-11 from `data.cityofnewyork.us` through the connector's OWN URL builders
(recording transport, byte-exact), then a confirmatory second GET re-hashed each to the same
sha256 and read the Date/Last-Modified headers. Codes file is a byte copy of the evidence pack
(no live codes call).

| File | URL (connector builder) | retrieved_at | bytes | sha256 |
|---|---|---|---|---|
| acris_index_legals_8h5j-fqxa_lot_4-7334-70.json (Q1) | `…/8h5j-fqxa.json?borough=4&block=7334&lot=70&$order=document_id&$limit=1000&$offset=0` | 2026-10-11T05:19:57Z | 2080 | 4340109ffeb1d593ad15c0a086742e730301dbbc4c8a5b6d31a51b308ffe637a |
| acris_index_master_bnx9-e6tj_subject_docs.json (Q2) | `…/bnx9-e6tj.json?$where=document_id in(7 ids)&$select=document_id,doc_type,document_date,recorded_datetime,crfn,good_through_date&$order=document_id&$limit=1000&$offset=0` | 2026-10-11T05:19:57Z | 1478 | 81cd75bf2db3150256629f02a33f5275bcbac660e191a3fea213dbf556153ec8 |
| acris_index_legals_8h5j-fqxa_zone_decl_cert.json (Q3) | `…/8h5j-fqxa.json?$where=document_id in(3 ids)&$order=document_id,lot&$limit=1000&$offset=0` | 2026-10-11T05:19:57Z | 1780 | d8b5c868a1e16aafdc5905815cc2a86c120c6843af6327abdcc61f8cd100f158 |
| acris_index_legals_8h5j-fqxa_good_through.json (Q4) | `…/8h5j-fqxa.json?$select=max(good_through_date)` | 2026-10-11T05:19:58Z | 54 | 9b2e2a01fe269e9f77bab6aa4092ee2601907a6908d963ba6eebfd5052e47ca3 |
| acris_index_doc_control_codes_7isb-wh4c.json (codes copy) | `…/7isb-wh4c.json` | 2026-10-10T18:46:00Z | 24004 | 518363532df753ac364ce47c5d62dfbdbaf609b598845bfcfe2ec83b9739c625 |

Cross-check vs the evidence pack:
- Q1 raw sha256 (4340109f…) does NOT equal the pack/evidence lot-70 Legals copy 712dbf8f… —
  EXPECTED: this connector adds `$order=document_id` for stable paging, so the 7 rows come back in
  a different order (same byte count, 2080). The PARSED content is IDENTICAL: same 7 document_ids,
  same lots, same partial_lot (verified programmatically — `key(live_q1) == key(evidence_q1)`).
- Q4 (9b2e2a01…) is byte-identical to the evidence pack's `acris_global_goodthrough.json`.
- Codes (518363…) is byte-identical to the evidence pack's `acris_codes.json` (NB-01 E3).
- End-to-end replay through the connector → classifier reproduces NB-01 exactly: state
  OTHER_LOTS_NAMED, other same-block lot 4073340001 (lot 1), ZONE 2022020201551002, CRFN
  2022000059134, recorded 2022-02-08, CERT+DECL as reminders, as-of 2026-09-30.

## Self-check outputs

1. `cd services/api && python -m ruff check .` → `All checks passed!` (exit 0).
2. `cd services/api && python -m pytest -q -p no:cacheprovider tests/connectors tests/profile tests/test_lane_flags.py tests/api`
   → `2895 passed, 1 warning in 100.41s`. (The 1 warning is the pre-existing Starlette/httpx
   TestClient deprecation, unrelated. The full tests/api suite staying green is the byte-identity
   proof for the study-read route.)
3. `python tools/modularity_check.py --check` → exit 0 (no warning names any file I added/edited;
   study_inputs.py not flagged).
4. `python scripts/lanes/check_lane_paths.py --coverage` → `LANE COVERAGE PASS: 10062 file(s)` (exit 0).
5. `python tools/research_record_check.py --check` → `PASS` (exit 0); NB-01 `code_current=True`
   (its listed code paths are unchanged; the connector/classifier are added to NB-01 in revision 3
   by the orchestrator).

Ran with the lanes venv (`/root/project/lanes-runtime/venv`), `PYTHONPATH=services/api` for pytest.

## Mutation proofs (break → show failing test → restore)

1. Rule (a) same-block: in `zoning_lot_index.py` changed the bucket to always `other_block`
   (ignore same-block). `test_other_lots_named_when_zone_names_a_same_block_lot` FAILED
   (`SINGLE_LOT_ONLY is not OTHER_LOTS_NAMED`). Restored → green.
2. Fail-closed NOT_READ: in `study_inputs.py` changed `except AcrisIndexConnectorError: return
   not_read(...)` to `raise`. `test_live_provider_maps_schema_drift_to_not_read` FAILED
   (`SchemaDriftError` propagated instead of NOT_READ). Restored → green.
3. NOT_CHECKED identity: in `zoning_lot_index.py` made `not_checked()` return SINGLE_LOT_ONLY.
   `test_not_checked_state` and `test_assemble_defaults_to_not_checked_and_is_inert` both FAILED.
   Restored → green.

## NB-01 revision-3 notes (for the orchestrator; I did NOT edit NB-01)

- E1 URL correction: E1's URL is the lot query `…8h5j-fqxa.json?borough=4&block=7334&lot=70`, but
  its saved copy `acris_legals_keydocs.json` was fetched with a document-id query (lots 1 and 70
  rows come only from that second query). The type/dates/CRFN live in the Master dataset (E2), not
  Legals. This connector's Q1 (lot-70 Legals) returns only lot-70 rows; the other-block/same-block
  lots come from Q3 (Legals by the ZONE/DECL/CERT ids).
- `partial_lot` meaning: from the Legals `api/views` column description — `P=partial, E=entire`
  (all benchmark rows are E). Draft rule DB232-R1(d): partial_lot `P` on a ZONE makes the figures
  conditional even with no other lot named.
- New code paths + identities to add to NB-01 `code_paths`/`code_identity` (sha256 over the file
  bytes at the accepted head):
  - `services/api/app/connectors/acris_index_soda.py`
  - `services/api/app/profile/zoning_lot_index.py`
  - `services/api/app/api/v1/study_inputs.py` (the seam) — part B also touches result_way_conditions.py.
  (I did not pin the sha256 here because the files may change under review; recompute at the
  reviewed head.)
- DB232-R1 is a DRAFT reading (not reviewed, ADR-007), grounded in the codes table (E3) and ZR
  12-10 "zoning lot" (capture `zr-12-10-zoning-lot`, `docs/research/zr-snapshots/v1/`). Research
  status stays `access_blocked`.
- Regression cases → tests (part A side):
  - Multi-lot ZONE (recorded replay) → OTHER_LOTS_NAMED: `test_benchmark_replay_names_lot_1_with_crfn`
    (profile) and `test_benchmark_replay_classifies_other_lots_named` (connector).
  - Single lot only (synthetic) → `test_single_lot_only_when_zone_names_this_lot_alone`.
  - No ZONE / deeds-and-mortgages-only → NONE_FOUND: `test_none_found_when_no_zone_document`.
  - Index not reachable → NOT_READ: the connector failure-path tests
    (`test_timeout_is_source_timeout`, `test_persistent_503_is_source_unavailable`,
    `test_persistent_429_is_rate_limited`, `test_no_such_column_400_is_schema_drift`,
    `test_page_budget_reached_is_fail_closed`,
    `test_subject_document_without_a_master_row_is_incomplete_index`) + the seam mapping
    (`test_live_provider_maps_schema_drift_to_not_read`).
  - Another block (synthetic) → `test_another_block_zone_is_not_a_same_block_warning`; mixed doc →
    `test_mixed_document_triggers_only_on_same_block_lots`.
  - DECL/CERT only → reminder only: `test_decl_or_cert_only_is_reminder_only_no_condition`;
    partial_lot P → `test_partial_lot_p_on_a_zone_is_conditional`; NOT_CHECKED byte-identity →
    `test_assemble_defaults_to_not_checked_and_is_inert` + `test_route_body_identical_whether_or_not_index_bound`.

## What I could not verify / limitations (kept unresolved)

- Whether ACRIS re-indexes older documents to a new lot after a tax-lot split (so a query on the
  subject lot can miss a former-lot ZONE) — not established from the repository. NONE_FOUND is
  therefore "not a title search", not proof of absence.
- Whether every zoning-lot description is typed ZONE (incl. pre-ACRIS Queens, ~before 2003).
- Whether the recorded CERT is the ZR 12-10(f) title certificate; whether the codes table 7isb-wh4c
  is complete (no api/views metadata saved for it).
- A zoning lot declared only by a DECL (no ZONE) is not caught by rule (b); cross-block
  developments and condo/air-rights lots are out of scope. These are disclosed in the registry
  draft `known_limitations`/`open_questions` and in NB-01's risks.
- Part B (result ways, scope row, open item, web label, regenerated journey fixture/snapshots,
  review register, NB-01 revision 3, RESEARCH_REQUESTS/DISCOVERY_BACKLOG at merge) is out of this
  part's scope and NOT done here.

## Files needed outside scope

None. Everything required for part A was inside the allowed paths.
