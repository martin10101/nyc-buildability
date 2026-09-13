# M4-T015 producer report - D-045 B2 street-width connector build

Producer: backend-engineer (claude-sonnet-5). Worktree: wt-m4t015, reset to base
`2c127706d373a4012813dc90e97723e9163d0f5d` on `candidate/D-024-mrl-option-b`. Date: 2026-09-13 (UTC).

STATUS: **submitting for independent review** (not a self-declared completion - producers submit
evidence only; gates judge it, per CLAUDE.md and the ORCHESTRATION_POLICY).

## 1. Sandbox capability check (disclosed up front)

The producer sandbox for this session had a working Python 3.11 launcher (`python`, not the bare
`python3` alias) AND live outbound network access to the DCM ArcGIS service. This was verified before
any fixture work began (`python -c "urllib.request.urlopen(...)"` against
`.../DCM_Street_Center_Line/FeatureServer/0?f=json"` returned HTTP 200). Because live capture
succeeded, **all fixtures below are genuinely live-captured this session** (2026-09-13), not
carried over from the M4-T013 research report's small inline samples - every fixture has its own
fresh URL, timestamp, and sha256 recorded in the MANIFEST.

The repo targets Python 3.12 (the packet's own risk note, M2-T015 pattern); the sandbox's Python is
3.11. No PEP 695 or other 3.12-only syntax was used in any new file, and the full local run below
succeeded under 3.11 without a single collection error. This is offered as an honest capability
statement, not a substitute for CI's `api` job (ruff 0.13.0 + pytest under the pinned 3.12), which
remains the executable authority per `documented_test_commands`.

## 2. Files created (all within `allowed_paths`; nothing outside scope touched)

- `services/api/app/connectors/dcm_street_centerline_arcgis.py` (NEW) - the ArcGIS query/paging/
  parsing connector and the per-segment typed envelope + mapped-street override.
- `services/api/app/connectors/dcm_street_width_classifier.py` (NEW) - the pure free-text width
  classifier (no I/O, no imports from the connector).
- `services/api/tests/connectors/test_dcm_street_centerline_arcgis.py` (NEW, 46 tests)
- `services/api/tests/connectors/test_dcm_street_width_classifier.py` (NEW, 85 tests)
- `services/api/tests/fixtures/dcm_street_centerline/` (NEW, 26 files: 25 live-captured + 1
  documented-synthetic + `MANIFEST.json`)
- `docs/research/source-registry-drafts/dcm-street-centerline.json` (MODIFIED - see section 6)

Files MODIFIED under `forbidden_paths`: **none**. Every existing connector
(`mappluto_geometry_arcgis.py`, `mappluto_lot_outline.py`, `geoclient_address.py`, `pluto_soda.py`,
`zoning_features_arcgis.py`, `ztldb_soda.py`, `bbl.py`) is untouched and was read-only (studied for
pattern reuse, never imported from - see section 8 disclosure on that deliberate deviation). No file
under `services/api/app/rules/**`, `services/api/app/api/**`, `services/api/app/scenario/**`,
`services/api/app/profile/**`, or `services/api/app/spatial/**` was touched. `git status --porcelain
-uall` in the worktree shows exactly the files above and nothing else (captured verbatim below).

```
 M docs/research/source-registry-drafts/dcm-street-centerline.json
?? services/api/app/connectors/dcm_street_centerline_arcgis.py
?? services/api/app/connectors/dcm_street_width_classifier.py
?? services/api/tests/connectors/test_dcm_street_centerline_arcgis.py
?? services/api/tests/connectors/test_dcm_street_width_classifier.py
?? services/api/tests/fixtures/dcm_street_centerline/  (26 files)
```

## 3. The classifier: complete class -> disposition table (S2)

The classifier (`classify_street_width`) never resolves OQ-3 - it only types the class and fails
closed. `AMBIGUITY_CLASS_DISPOSITIONS` in the module is the single source of truth this table
mirrors; a test (`test_every_documented_class_is_exercised_by_this_suite`) asserts the two never
drift apart.

| ambiguity_class | disposition | review_required | example raw text |
|---|---|---|---|
| `clean_numeric_ge_75` | **wide** | False | `"75"`, `"80"`, `"100"` |
| `range_both_endpoints_ge_75` | **wide** | False | `"75-90"`, `"75-100"` |
| `gt_inequality_ge_75` | **wide** | False | `">75"`, `">80"`, `">=75"` |
| `clean_numeric_lt_75` | narrow_fail_closed | False (confident) | `"60"`, `"30"`, `"49.5"` |
| `range_both_endpoints_lt_75` | narrow_fail_closed | False (confident) | `"50-60"` |
| `lt_inequality_at_or_below_75_confident_narrow` | narrow_fail_closed | False (confident) | `"<60"`, `"<75"` |
| `le_inequality_below_75_confident_narrow` | narrow_fail_closed | False (confident) | `"<=74"` |
| `range_straddles_cutoff` | narrow_fail_closed | **True** | `"60-75"`, `"74-75.3"` |
| `range_order_unexpected` | narrow_fail_closed | **True** | `"100-90"` (never observed live; defensive) |
| `gt_inequality_below_75_ambiguous` | narrow_fail_closed | **True** | `">60"` (defensive; not observed live) |
| `lt_inequality_above_75_ambiguous` | narrow_fail_closed | **True** | `"<80"` (defensive; not observed live) |
| `le_inequality_at_or_above_75_ambiguous` | narrow_fail_closed | **True** | `"<=75"` (defensive; not observed live) |
| `approximate_or_hedged_value_ambiguous` | narrow_fail_closed | **True** | `"~60"`, `"Probably between 80 - 90"` |
| `width_irregular` | narrow_fail_closed | **True** | `"Width Irregular"` |
| `varies` | narrow_fail_closed | **True** | `"Varies"` / `"varies"` |
| `not_applicable_n_a` | narrow_fail_closed | **True** | `"n/a"` |
| `unknown_no_qualifier` | narrow_fail_closed | **True** | `"Unknown"` |
| `unknown_hedged_below_75` | narrow_fail_closed | **True** | `"Unknown but <75"` |
| `unknown_hedged_above_75` | narrow_fail_closed | **True** | `"Unknown but >75"` |
| `regular_but_unknown` | narrow_fail_closed | **True** | `"Regular but unknown."` |
| `empty_or_missing` | narrow_fail_closed | **True** | `None`, `""` (never observed live on this field/layer) |
| `unexpected_type` | narrow_fail_closed | **True** | a non-string value (schema drift; defensive) |
| `negative_value_unexpected` | narrow_fail_closed | **True** | `"-10"` (never observed live; defensive) |
| `unrecognized_free_text_ambiguous` | narrow_fail_closed | **True** | any other free text (catch-all) |

**Design decision recorded (not in the packet verbatim, disclosed as a judgment call within the
mathematical-entailment spirit):** the strict/non-strict distinction on `<`/`<=`/`>`/`>=` matters
exactly at 75 because ZR 12-10 defines wide as "75 feet **or more**" - `"<=75"` includes exactly 75
(itself wide) and is therefore ambiguous, while `"<75"` strictly excludes 75 and is confidently
narrow. No occurrence of `<=`/`>=` was found live (the domain only showed bare `<`/`>`); the
generalization is implemented and unit-tested defensively but never fixture-proven against a live
`<=`/`>=` sample because none exists in the source at capture time.

## 4. Mapped-street override (S3) - proven against 4 live cases

`_mapped_street_override` in the connector applies exactly one additional rule on top of the pure
classifier: a segment that is not `Feat_Type='Mapped_St'`, or that is `Paper_ST='Y'`/`Record_ST='Y'`,
never classifies wide - the classifier's own read (`width_classification`) is preserved untouched;
only `effective_classification`/`effective_disposition` is overridden. Four live fixtures each
isolate one trigger:

- **paper_street_override_wide.json** (Jay Place, OBJECTID 599): `Paper_ST='Y'`, raw `"80"` (would be
  wide) -> effective `narrow_fail_closed`, `override_reason` cites `Paper_ST`.
- **record_street_override_wide.json** (Woodvale Avenue, OBJECTID 16549): `Record_ST='Y'`,
  `Feat_Type='Not_mapped'`, raw `"80"` -> overridden.
- **former_street_override_wide.json** (Stillwell Avenue, OBJECTID 10335): `Feat_Type='Former_St'`,
  raw `"100"` -> overridden.
- **unmapped_street_override_wide.json** (Sharrott Avenue, OBJECTID 20420): `Feat_Type='Not_mapped'`,
  `Paper_ST='N'`, `Record_ST='N'`, raw `"80"` -> overridden from `Feat_Type` alone, proving the rule
  does not depend on the paper/record flags being set.

## 5. Live-source findings that DIVERGE from the pinned research/registry draft (disclosed)

Live re-verification during this task's own fixture capture surfaced three facts the M4-T013
research/registry draft did not have (none contradict the research's conclusions; they refine
`Feat_Type`/`Feat_statu`/`Record_ST`/`Paper_ST`/`Build_Stat` characterizations):

1. **`Record_ST`/`Paper_ST` live value domain is `Y`/`N` (single letter), not the lowercase word
   `"yes"`** stated in the official metadata PDF (byte-quoted in the registry draft's E3 field
   definitions). Confirmed live: Jay Place `Paper_ST='Y'`, Woodvale Avenue `Record_ST='Y'`; a query
   for `Paper_ST='yes'` returns 0 rows while `Paper_ST='Y'` returns matches. **The connector and its
   override logic use the live `'Y'`/`'N'` domain, not the PDF's prose value** - this is disclosed as
   a metadata-vs-live discrepancy, not silently "corrected" in the registry text (the registry draft
   now records both the PDF wording and the live discrepancy verbatim).
2. **`Build_Status` DOES carry a published ArcGIS coded-value domain** (`DCMSCL_route_status_1` =
   `{Improved, Part_improved, Unimproved, Not_applicable(code 'n/a')}`), visible on the live layer/
   query field schema even though the static s-media metadata PDF (E3) gives no field-level
   description for it. This partially resolves research OQ-2 for `Build_Status` specifically;
   `Feat_statu` and `RoadwayTyp` remain genuinely undocumented (domain: null in the same live
   schema) - OQ-2 stays open for those two.
3. **`Feat_status='Way_on_record'` was observed co-occurring with `Record_ST='N'` on the SAME live
   feature** (Sharrott Avenue, OBJECTID 20420) - direct proof that `Feat_status` is independent of
   the `Record_ST`/`Paper_ST` flags and must never be used as a proxy for the mapped-street override
   (the connector deliberately does not use it that way; `test_feat_status_is_typed_passthrough_never_used_for_override`
   asserts this).
4. **`HonoraryNM`/`Old_ST_NM` carry the literal string `"None"`** (not JSON `null`) when absent on at
   least one live feature (Kappock Street, OBJECTID 7). The connector does NOT coerce this to `None`/
   null - it is preserved verbatim as the four-character string `"None"`, per the "never guess/coerce"
   principle; a human reviewing `honorary_name` output should be aware this string can mean "no
   honorary name" on the live service, not that a name literally reading "None" was assigned.

All three registry-draft edits (Record_ST/Paper_ST, Build_Status, Feat_status) are recorded in
`docs/research/source-registry-drafts/dcm-street-centerline.json` with the `M4-T015` tag so the
provenance of the refinement is traceable.

## 6. Registry draft update (S7/output requirement)

`docs/research/source-registry-drafts/dcm-street-centerline.json`, first record
(`nyc-dcp-dcm-street-centerline-arcgis`):
- `draft_status` updated: connector now IMPLEMENTED; still non-final (OQ-1/OQ-3 open; no consumer
  wiring yet).
- Added `self_declared_source_id` cross-check field confirming the connector's `SOURCE_ID` constant
  matches this record's `source_id` exactly.
- `connector_implementation` rewritten from "PLAN ONLY" to a full description of what was actually
  built (module names, query/paging/CRS/error discipline, classifier behavior, override rule,
  fixture count, what is explicitly NOT in scope).
- `field_definitions_byte_verified_from_metadata_E3` updated for `Feat_statu`, `Build_Stat`,
  `Record_ST`, `Paper_ST` per section 5 above.
- `health_status` / `latest_source_version` updated to record this task's re-verification.
- `draft_status` still says non-final (no source_registry mechanism was invented; the second SODA
  record is UNCHANGED - that channel's connector remains PLAN ONLY, out of this task's scope).

JSON validity confirmed (`json.load` succeeds; 2 records; `self_declared_source_id` present on record
0).

## 7. Fixture inventory (25 live + 1 documented-synthetic; MANIFEST.json verified self-consistent)

All 25 live fixtures were captured 2026-09-13 from the keyless public endpoint
`https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/DCM_Street_Center_Line/FeatureServer/0/query`
(plus one `.../0?f=json` metadata call), each a small bounded query (single `OBJECTID=` equality,
a two-row `Borough=/Street_NM=` equality, or a 5-row bounded predicate for the paging demo) - KB-scale,
no bulk download. Full URL, capture timestamp, sha256, and byte count are recorded per fixture in
`services/api/tests/fixtures/dcm_street_centerline/MANIFEST.json`; a self-consistency check
(`test_manifest_matches_fixture_bytes_on_disk`) asserts every manifest entry's sha256/byte-count
matches the file on disk exactly, and the file set on disk exactly equals the manifest's file set
(no orphans either direction).

Selected sha256 (full 26-entry table lives in the MANIFEST):
- `metadata.json` -> `sha256:5d59aa711054846cf5d0c2e56b772be66b0a7e459872a370eabcafcc2fde5db2`
- `west_100_st_two_segments.json` -> `sha256:ebf13f620bf374a132d37c2efe4ee48907c5d2660fafedc33d3a527ef2ed68bf`
- `wide_clean_numeric_80.json` -> `sha256:4184e761fec3538a46db3c81f69c106d8c6914725b06d7e444611ae9014decb1`
- `paper_street_override_wide.json` -> `sha256:e4e3216c4257355229ca7855dde0b184dbbfc911151d2eb2adaf44844f20d100`
- `paging_page1.json` -> `sha256:585607aac4592ff9b61fe7092a9bc2be3113f09259bdba0cf1f41ce64575191b`
- `paging_page2.json` -> `sha256:e691df415ec59a97a78d32c6e9d755eb6f7e0f84604b6f373c5e1104d367c5f9`
- `provider_error_http200_synthetic.json` (documented-synthetic, `"synthetic": true` in the
  manifest, handwritten to the documented ArcGIS error shape per the M2-T009 precedent - never
  derived from a live capture) -> `sha256:0d5e05a7f8b86ec9ec6f101d5a4651ec7498c73ed3be7c9d5e75aea3a09ce272`

Canonical-case coverage confirmed present: West 100 St Manhattan two-segment case (60/100, S4
requirement); a clean wide segment; a paper-street sample and a record-street/unmapped sample (S3);
a paging sample proving `resultOffset` advances with disjoint OBJECTIDs across pages; and a live
sample for every ambiguity class that could be located in the source at capture time (the research's
E7 grouped-count query pattern was reused this session, via `Streetwidth='<value>'` targeted queries
against the live ArcGIS channel, to locate one example per class). `empty_or_missing` has **no live
fixture** - repeated `Streetwidth IS NULL` / `Streetwidth=''` queries against the live layer both
returned 0 rows, so no live example of a missing value exists on this layer at capture time; this
class is proven only by direct unit tests of the pure classifier (`classify_street_width(None)` /
`classify_street_width("")`), never fabricated as a fixture. This is disclosed, not hidden.

## 8. Deliberate deviation from the packet's "reuse public patterns by import" note (disclosed)

The packet's `path_notes` say "reuse public patterns by import where applicable" and cite
`mappluto_lot_outline.py` as the precedent for importing from an accepted sibling connector. This
connector does **NOT** import any name from `mappluto_geometry_arcgis.py`, `pluto_soda.py`, or any
other existing connector. Reasoning: those connectors' public exports (`normalize_bbl`,
`canonical_json_digest`, geometry canonicalization, the BBL-keyed condo-classification helper) are
all BBL/lot-geometry concepts with no analog in a street-segment-by-OBJECTID/Borough/Street_NM
domain: there is no BBL to normalize, no polygon geometry to canonicalize (geometry/OQ-4 is
explicitly out of scope for this task), and no shared digest helper this module actually needs
(`raw_body_digest` is a two-line `hashlib.sha256` call, reimplemented locally rather than importing
it from a file this task cannot edit and whose only public surface for that helper - via
`pluto_soda.canonical_json_digest` - is for a *different* digest shape, canonical-JSON of a parsed
object, not raw bytes). Recall from the packet's own S5 language: "the bounded no-retry posture of
M5-T020" - that IS the pattern this module actually reuses, structurally (single-attempt bounded
fetch, no retry loop, typed transport/parse errors), just not via a Python import (there is nothing
importable in `mappluto_lot_outline.py` that this module's domain needs either - its exports are all
BBL/GeoJSON-4326/display-outline specific). This is disclosed as a considered scope judgment, not an
oversight, for the reviewer to weigh.

## 9. Self-checks (verbatim commands + exit codes, per `documented_test_commands`)

```
$ python -m pytest services/api/tests/connectors -q
........................................................................ [ 11%]
........................................................................ [ 23%]
........................................................................ [ 34%]
........................................................................ [ 46%]
........................................................................ [ 58%]
........................................................................ [ 69%]
........................................................................ [ 81%]
........................................................................ [ 93%]
...........................................                              [100%]
619 passed in 2.51s
EXIT CODE: 0
```

619 total tests collected in `services/api/tests/connectors` (the full pre-existing connector suite,
untouched, plus this task's additions): 131 new tests (46 in
`test_dcm_street_centerline_arcgis.py`, 85 in `test_dcm_street_width_classifier.py`), zero
regressions in any pre-existing connector test.

```
$ python tools/modularity_check.py --check
selected 399 files; failures 0; warnings 16
EXIT CODE: 0
```

The 16 warnings are all pre-existing files unrelated to this task (`scenario_analysis.py`,
`breakeven.py`, `mappluto_geometry_arcgis.py`, several `tools/agent_supervisor/*.py` files,
`tools/context_benchmark.py`, `apps/web/src/lib/surveyReview/types.ts`); neither new module
(`dcm_street_centerline_arcgis.py` at 959 lines, `dcm_street_width_classifier.py` at 390 lines)
appears in the warning list.

```
$ python -m ruff check services/api/app/connectors/dcm_street_centerline_arcgis.py \
    services/api/app/connectors/dcm_street_width_classifier.py \
    services/api/tests/connectors/test_dcm_street_centerline_arcgis.py \
    services/api/tests/connectors/test_dcm_street_width_classifier.py
All checks passed!
```

Ruff version confirmed `0.13.0` (matches the CI `api` job's pinned version per the M2-T015 memory
note) - run proactively even though it is not in `documented_test_commands`, because the sandbox
happened to have network+exec this session; this is offered as additional evidence, not a
replacement for CI's own run on the pushed head.

**Not run in this sandbox:** the full `services/api` test suite outside `tests/connectors` (out of
this task's scope - `allowed_paths`/`forbidden_paths` restrict this producer to the connectors
surface only, and the packet's own `documented_test_commands` scope the check to
`services/api/tests/connectors`). CI's `api` job on the pushed head remains the executable authority
for the complete Python-3.12 suite, per the packet's own risk note.

## 10. Scenario-by-scenario self-assessment (evidence only; not a completion claim)

- **S1** (authoritative source + provenance): `build_metadata_url()`/`build_segment_query_url()`
  target exactly `DCM_Street_Center_Line/FeatureServer/0` with `outSR=2263`; every segment envelope
  carries `source_id`, `service_root`, `layer`, `metadata_request_url`, and
  `source_data_last_edited`/`_ms` (freshness pin from `editingInfo.dataLastEditDate`, live-confirmed
  `1764617995374` ms = `2025-12-01T19:39:55Z`, matching the M4-T013 research exactly). Raw
  `Streetwidth` text is preserved verbatim on every segment (`streetwidth_raw`).
- **S2**: see section 3's table; `test_every_documented_class_is_exercised_by_this_suite` proves the
  table and the test suite never drift apart.
- **S3**: see section 4; `Feat_type`/`Feat_status`/`Record_ST`/`Paper_ST` all surface as typed fields
  on `StreetSegment`; unrecognized `Feat_Type` values are a typed schema-drift path
  (`feat_type_recognized=False`), never coerced (proven by
  `test_unrecognized_feat_type_is_schema_drift_never_wide`).
- **S4**: see section 7.
- **S5**: `test_http_200_arcgis_error_object_is_typed_upstream_error`,
  `test_paging_walks_two_pages_and_merges_disjoint_segments`,
  `test_duplicate_page_is_a_typed_paging_pathology`,
  `test_repeated_object_ids_across_pages_is_a_typed_paging_pathology`,
  `test_zero_progress_empty_page_with_exceeded_flag_is_typed_pathology`,
  `test_page_budget_exhaustion_is_a_typed_pathology`,
  `test_network_failure_is_a_typed_upstream_error_no_retry` all pass. `default_fetch` performs
  exactly one attempt per HTTP call (no retry loop), matching the cited M5-T020 posture.
- **S6**: `git status --porcelain -uall` (section 2) shows only `allowed_paths` files touched; the
  full connectors suite (619 tests, including every pre-existing connector's tests) passes unchanged;
  `modularity_check.py --check` exits 0; zero new dependencies were added (no `requirements*.txt` /
  `pyproject.toml` change appears in the git status).

## 11. Open questions explicitly NOT resolved (per the packet's instruction)

OQ-1 (exact geometric definition of DCM mapped width), OQ-2 (Feat_statu/RoadwayTyp domains - now
partially narrowed for Build_Status per section 5, but Feat_statu/RoadwayTyp remain open), OQ-3 (the
ZR-grounded fail-closed policy per ambiguity class - this connector only types classes and fails
closed; it never decides what the LEGAL treatment of e.g. a paper street or a straddling range should
be), OQ-4 (the within-100-ft-of-a-wide-street geometry computation), and OQ-5 (the BYTES shapefile
URL) are all UNCHANGED and unresolved by this task, as instructed.

## 12. Requested status

**awaiting_gate.** No blockers encountered; live capture and both self-checks succeeded fully.
Disclosures in sections 5 and 8 are offered for the independent reviewer's judgment, not resolved
unilaterally by the producer.
