# Gate Report

> Saved VERBATIM by the orchestrator from the code-reviewer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.

- Gate ID: G3 (independent code review)
- Task ID: M4-T020 — B3 DCM centerline geometry parse-and-expose
- Reviewer: code-reviewer (independent; NOT the producer)
- Producer: D-053 loop worker (backend-engineer role), run persistent-local-34, worktree wt-m4t020
- Result: **PASS** (zero blocking findings; 5 advisories)
- Clean environment/worktree used: primary checkout `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` verified at pinned review head `16272c05bf0e1d8152673122a930aed3904596a4` (`git rev-parse HEAD` reproduced); review-surface working-tree files verified byte-identical (LF-normalized sha256) to the pinned blobs; `git status --porcelain` clean on `services/api` and the producer report. Sandbox Python 3.11.9 (CI py312 canonical, in flight — see "prior evidence").

## Identity verification (cherry-pick and scope)

- `ba301b67` is in `candidate/D-024-mrl-option-b` history (HEAD~1 of the pin) and touches EXACTLY the 3 allowed paths: `services/api/app/connectors/dcm_street_centerline_geometry.py` (+576/-placeholder), `services/api/tests/connectors/test_dcm_street_centerline_geometry.py` (+577), `project-control/reports/M4-T020-producer-report.md` (+1564).
- Byte-identity to the producer commit proven two ways: `git patch-id --stable` identical (`3ea576a6dca0b545…` for both d7766b8d and ba301b67), and per-file blob SHAs identical across `d7766b8d`, `ba301b67`, and `16272c05` (module `b066c742…`, test `3f848c2a…`, report `e7f31948…`).
- Producer report §7.1 digest claims independently reproduced: module LF-sha256 `864b24fc…d4223ef4` (22920 bytes, 572 lines) MATCH; test file `6f3f5892…fd220f03` (21663 bytes, 576 lines) MATCH.

## Rulings on contract items 1–6

**Item 1 — reuse-by-import, no second fetch: PASS.**
`parse_segment_geometry_page` (module:385-476) calls the accepted `parse_segment_page` FIRST (line 399 — reusing HTTP-status, ArcGIS-error-object, malformed-body, and attribute typing), then walks geometry over a deterministic re-parse of the SAME `transport.body` (line 403; zero I/O). Pairing is by document position with TWO typed guards: `len(features) != len(segments)` → `MalformedResponseError` (lines 422-431) and `zip(..., strict=True)` (line 434). The paged entry `fetch_street_segment_geometries` (484-572) drives the accepted `fetch_street_segments` through a pass-through recording seam (`_recording_fetch`, 506-509) — one transport per page, then a URL-list pairing guard (524-536) and an entry/segment count guard (545-554). No URL building, no socket: the module's only imports are `__future__`, `json`, `collections.abc`, `dataclasses`, `math`, and the accepted transport module (68-88). The AST test (test:233-268) genuinely enforces this: it walks every `Import`/`ImportFrom` node and asserts SET EQUALITY against exactly that 6-member allowlist (any added import fails), plus a non-prose token scan (`urllib`, `FeatureServer`, `outSR`, `http://`, `https://`, `pyproj`, `to_crs`, `0.3048`, `3.2808`) and identity proof `geometry_module.default_fetch is default_fetch`. `test_paged_fetch_transports_each_page_exactly_once` (520-534) proves N pages = exactly N+1 transports (metadata + N) via a counting fetcher.

**Item 2 — CRS fail-closed before coordinate interpretation: PASS.**
`_require_page_crs` (154-181) requires an exact dict pair `wkid == 102718 AND latestWkid == 2263`; bare `{"wkid": 2263}` refused (test id `wkid_2263_not_102718`), `{"wkid": 102718}` alone refused (`latestWkid_absent`), absent key / JSON null / empty dict / WGS84 / wrong latestWkid / non-object all refused (8-variant parametrize, test:288-317), raising the accepted taxonomy's `WrongCRSError` (`error_type == "wrong_crs"`) naming expected vs received. Ordering: the gate runs at line 404-406, before the geometryType check (407-420) and before any vertex is touched (`test_crs_gate_runs_before_the_geometry_type_check`, test:320-324 — a body missing BOTH raises WrongCRSError). `parse_segment_page` running first touches attributes only — no coordinate interpretation precedes the gate. Non-polyline or missing `geometryType` → typed `SchemaDriftError` (407-420; test:326-331). No reprojection/conversion path exists anywhere in the module (my full source read + the AST/token test). Bool-typed wkid cannot pass (True == 1 ≠ 102718).

**Item 3 — validity taxonomy: PASS.**
Eight distinct typed statuses (120-138): `ok`, `null_geometry` (key-missing AND json-null, distinguished in findings), `malformed_geometry_object`, `unexpected_geometry_kind` (rings/points/x/y payload — 209-221), `empty_paths`, `degenerate_path` (<2 points), `malformed_coordinate` (incl. the bool-is-not-numeric trap: `isinstance(component, bool) or not isinstance(component, int | float)`, 259-270), `nonfinite_coordinate` (NaN/Infinity via `isfinite`, 271-280). Refused geometry KEEPS its entry — `SegmentPolyline` is appended with status/findings, `paths=None`, and its full `StreetSegment` identity (433-450); the 13-condition parametrized test asserts `features_total == 1`, paired attributes intact, and refused/usable counters (test:339-435). No partial repair: one defective path refuses the whole geometry — `test_no_partial_polyline_repair…` (458-465) proves the intact sibling path is NOT salvaged. No coercion; extra z/m components recorded visibly as findings on an OK entry (281-288; test:468-473). A bad feature never drops neighbors (test:438-455).

**Item 4 — passthrough untouched: PASS.**
No rounding/simplification/averaging/conversion code exists; the only transformation is JSON-number → Python float (271). `test_paths_match_the_wire_json_exactly_no_rounding` (201-210) proves equality against an independent `json.loads` of the same bytes; high-precision/integer/negative-tiny values proven (481-495). Fixture first vertex `(992185.54514055, 229943.965358555)` matches the recorded wire body — I independently parsed the fixture and confirmed.

**Item 5 — provenance completeness: PASS.**
Per page (`SegmentGeometryPage`, 326-349): `request_url`, `retrieved_at`, `correlation_id`, `raw_digest` (accepted `raw_body_digest` over the exact body), CRS stamp (`crs=dict(CRS_STAMP)` + `wkid`/`latest_wkid`), declared `geometry_type`, `units` passthrough (`esriFeet` on the fixture), `source_id`/`service_root`/`layer`/`attribution`/`disclaimer`/`contract_version`. Per query (`SegmentGeometryQueryResult`, 352-377): `page_urls`, per-page `raw_digests`, `correlation_id`, `retrieved_at`, `source_data_last_edited(_ms)`, `metadata_request_url`, `drift_signals` — all copied unchanged from the accepted transport result (556-572). Tests: 498-512, 537-555.

**Item 6 (D-045-R009) — preservation: PASS.**
The material commit's file list is exactly the 3 allowed paths, so every accepted connector (and everything else) is byte-unchanged by construction; `dcm_street_centerline_arcgis.py` was last touched at the M4-T015 capture commit `8538c272` — untouched since acceptance. Zero dependency changes: `pyproject.toml`/`uv.lock`/`package-lock.json` untouched; module imports are stdlib + accepted transport only (AST-enforced).

**General quality: PASS.** Error taxonomy reuses the accepted typed classes (no forked hierarchy); every ambiguous input fails closed in the safe direction (unknown CRS → refuse; unknown geometry kind → typed visible refusal, never coerce; pairing break → typed error, never silent); module is a clean single-responsibility sibling (573 SLOC, below the 600 warn threshold; no HTTP/persistence/CLI mixing; modularity_check failures 0, exit 0). The producer's disclosed self-test correction (prose scan → AST allowlist) STRENGTHENED the test: import-set equality is strictly more enforcing than word matching and eliminates the docstring false positive; final form is sound (see A4).

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-045-R002 | 16272c05 / module blob b066c742 | PASS | B3 data-input mechanic ships with typed geometry; unavailable/malformed input stays an honest typed absence state (never a manufactured number): 8 CRS refusals, 8 geometry statuses, refused entries visible with counters; no guessed geometry, no default CRS, no coercion. My own runs: 39/39 focused, 752/752 suite. |
| D-045-R008 | 16272c05 | PASS | Bounded single-lane task under G0/G3/G4 (packet `required_gates`); diff confined to one family's sibling module — nothing monolithic, nothing displacing M5-T023/24 or D-043 (no such files in ba301b67's file list). |
| D-045-R009 | 16272c05 / ba301b67 | PASS | Commit touches exactly 3 allowed paths; accepted connectors byte-unchanged (`dcm_street_centerline_arcgis.py` last commit = M4-T015 capture 8538c272); no dependency-file change; no rule publication or compliance declaration in the diff; expansion-hold surfaces untouched. |
| D-046-R001 | 16272c05 | PASS (code surface) | Unit executed in isolated worktree wt-m4t020 on branch task/M4-T020-dcm-geometry (producer report header; packet progress_log). Dispatch mechanics are orchestrator-side; nothing in the diff conflicts. |
| D-046-R002 | 16272c05 / ba301b67 | PASS | allowed_paths are 3 exact files provably disjoint from the concurrent M5-T025/T026 surfaces (their diffs touch apps/web + project-control only; zero overlap with these 3 paths — verified in the branch diff between d7766b8d and ba301b67). |

## Acceptance scenarios S1–S5 (my own verification per row)

| Scenario | My verification | Result |
|---|---|---|
| S1 wire_format_parse_and_typing | Ran focused suite (39 passed, 0.08s); independently parsed the recorded fixture and confirmed 7719 → 3 paths/6 vertices `Streetwidth "60"`, 14471 → 3 paths/12 vertices `"100"`, first vertex exact; read the AST-allowlist test and confirmed it enforces the import contract by set equality; counting-fetcher test proves single transport per page. | PASS |
| S2 crs_fail_closed | Read `_require_page_crs` + all 8 parametrized refusal variants + gate-ordering test; confirmed no reprojection/conversion path in the full source; error names expected vs received with `error_type "wrong_crs"`. | PASS |
| S3 malformed_geometry_taxonomy | Read all 13 parametrized conditions + no-partial-repair + neighbor-visibility + extra-component tests against the implementation; bool trap handled at module:260; all executed green in my run. | PASS |
| S4 passthrough_integrity_and_provenance | Read the wire-equality test (independent `json.loads` comparison) and both provenance-schema tests; page `raw_digest` equals `raw_body_digest` over the same bytes; query provenance copied unchanged from the accepted result. | PASS |
| S5 scope_and_regression | My own runs at the pin: focused **39 passed**; `python -m pytest services/api/tests/connectors` **752 passed** (4.73s); `cd services/api && python -m ruff check .` **All checks passed! exit 0**; `python tools/modularity_check.py --check` **selected 404 files; failures 0; warnings 17** (none on M4-T020 files), exit 0. Commit file list = exactly the 3 allowed paths; zero dependency changes. | PASS |

## Steps independently executed

1. `git rev-parse HEAD` → 16272c05 (pin confirmed); `git status --porcelain` on review surface → clean.
2. Cherry-pick identity: `git patch-id --stable` on d7766b8d vs ba301b67 (identical) + per-file `git rev-parse <sha>:<path>` blob comparison across producer commit / cherry-pick / pin (identical).
3. Producer §7.1 digest reproduction (LF-normalized sha256 over pinned blobs AND working tree): both MATCH, byte/line counts match.
4. All four documented commands (results above, Python 3.11.9 sandbox).
5. Full source read: geometry module (573 lines), test file (577 lines), accepted transport `dcm_street_centerline_arcgis.py` (959 lines), packet JSON, D-045/D-046 requirement texts from `requirements.json`, producer report §1–§7.
6. Fixture sanity: parsed `west_100_st_two_segments.json` — `spatialReference {wkid:102718, latestWkid:2263}`, `geometryType esriGeometryPolyline`, `units esriFeet`, per-segment path/vertex counts match every S1 assertion.
7. `git log` on the accepted transport file → last touched at M4-T015 capture (byte-immutability corroborated).

## Taken from prior evidence (not independently executed)

- CI on the pinned head: IN FLIGHT per task statement — I did not run `gh` (read-only guard). My local runs plus the orchestrator pre-gate substitute meanwhile; acceptance correctly held until CI lands (py312 canonical context; the module uses `int | float` isinstance and `zip(strict=True)` — 3.10+, no py312-only syntax, and the whole suite collected under 3.11).
- Loop/dispatch process facts (worktree isolation, model pin, DL-2 checkpoint refusal) — from packet `progress_log` and producer report; orchestrator-recorded, not re-derivable by me.
- M4-T016 Part 2.3 research provenance for the CRS pair — corroborated independently by the recorded live fixture rather than re-reading the research report.

## Defects

**Blocking (F): none.**

**Advisory (A):**

- **A1** — `LAYER_NAME` is imported by the geometry module (module:74) but is NOT in the accepted transport's `__all__` (dcm_street_centerline_arcgis.py:78-111): reliance on an undeclared public name. Works and is read-only, but a future `__all__`-strict refactor could miss it. Fix belongs to a future accepted-module task (that file is byte-immutable here), or document the reliance.
- **A2** — `units` extraction (module:453-459): a non-string `geometryProperties.units` value silently becomes `None`, indistinguishable from an absent key and without a drift signal. Supplemental provenance only (the CRS gate already pins US-survey-feet semantics), so advisory — but a mistyped `units` is mild schema drift the module could surface.
- **A3** — the `_extract_paths` docstring claim "preserves the parsed value bit-for-bit" (module:196-198) is overstated for hypothetical integer wire coordinates above 2^53 (`float(int)` would lose precision). No practical exposure: EPSG:2263 coordinates are ~10^6 ft. Wording nit only.
- **A4** — the AST import-allowlist cannot catch a dynamic `__import__`/`importlib` escape and the token scan doesn't include those strings. My direct read of the full module confirms no dynamic import exists at the pin; adding `"importlib"`/`"__import__"` to the token list would close the gap cheaply in a future test touch.
- **A5** — in a refusal, extra-component (`z/m`) findings accumulated on EARLIER valid paths are discarded, leaving only the first-defect finding (module:233-291 early returns). Consistent with the documented "first defect in document order" semantics and the geometry is refused whole anyway; noted for completeness.

## Required rework

None. A1–A5 are non-blocking; A1/A4 are candidates for a future test/accepted-module touch, not this task.

## Reviewer conclusion

**PASS.** The material change is byte-identical from producer commit through cherry-pick to the pinned head, confined to exactly the three allowed paths, and satisfies all six contract items with genuinely enforcing tests: reuse is by read-only import with a structural single-fetch guarantee and typed pairing guards; the CRS gate is exact-pair fail-closed before any coordinate interpretation with no reprojection path; the validity taxonomy makes every named condition a distinct typed, visible state with no repair or coercion; values pass through untouched; provenance is complete per page and per query; the accepted transport and every other file are byte-unchanged with zero new dependencies. All four documented commands reproduced green by me at the pin (39/39, 752/752, ruff exit 0, modularity failures 0). Acceptance should still await the in-flight CI on 16272c05 (py312 canonical), as the orchestrator already plans.

Key file paths:
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\connectors\dcm_street_centerline_geometry.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\connectors\test_dcm_street_centerline_geometry.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M4-T020-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M4-T020.json`

**Verdict: PASS**
