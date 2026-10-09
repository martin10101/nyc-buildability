# M4-T020 producer report — B3 DCM centerline geometry parse-and-expose

- **Task:** M4-T020 (D-045 A2 geometry lane, research item B3; first wave-5 packet under the
  D-053 loop relaunch, run-id `persistent-local-34`)
- **Producer:** loop worker (backend-engineer role), worktree `wt-m4t020`,
  branch `task/M4-T020-dcm-geometry`
- **Base (packet claim head at unit start):** `7f297f0973ae54da94164418acd318caf13ce907`
- **Directive refs (from the packet):** D-045:D-045-R002,D-045-R008,D-045-R009;
  D-046:D-046-R001,D-046-R002
- **Date:** 2026-09-14 (resubmitted same day with the supervisor-requested digest-bound
  full-source packet — §7–§11; implementation unchanged)

## 1. What was produced (exactly the three allowed paths)

1. `services/api/app/connectors/dcm_street_centerline_geometry.py` — NEW sibling measurement
   module (placeholder replaced): typed esriGeometryPolyline parsing over the accepted M4-T015
   transport's own page bodies, CRS fail-closed to EPSG:2263, per-feature geometry-validity
   taxonomy, passthrough integrity, per-page and per-query provenance.
2. `services/api/tests/connectors/test_dcm_street_centerline_geometry.py` — NEW fully offline
   test file (39 tests): wire-format parse from the recorded M4-T015 fixture (read-only) and
   from documented in-memory page bodies, multi-path preservation, CRS refusal matrix,
   malformed-geometry taxonomy, passthrough integrity, provenance schema, single-fetch paged
   flow, reuse-fidelity proofs.
3. This report.

No other file was created or modified. The accepted connector modules (including the
byte-immutable `dcm_street_centerline_arcgis.py`) were touched only by READ-ONLY import.

## 2. Contract mapping (packet objective items 1–6 → implementation)

| # | Contract item | Implementation |
|---|---|---|
| 1 | Parse `features[].geometry.paths` from the same page body; typed polylines; multi-path preserved; paired with segment identity/attributes; transport reused by import, never a second fetch | `parse_segment_geometry_page` consumes the accepted module's `DcmTransport` verbatim: the accepted `parse_segment_page` runs first (reused HTTP-status / ArcGIS-error / malformed-body / attribute typing), then this module's geometry walk over the SAME parsed body, zipped by document position (typed guard on any pairing break). `fetch_street_segment_geometries` drives the accepted `fetch_street_segments` (metadata gate, URL building, paging, loop safety all reused) through a pass-through recording seam: each page is transported exactly once and parsed on both sides. The module builds no URL and opens no socket (AST-verified in tests: its only imports are `json`, `collections.abc`, `dataclasses`, `math`, and the accepted transport module). |
| 2 | CRS fail-closed: page `spatialReference` must be wkid 102718 / latestWkid 2263; anything else or absent → typed error, no assumed CRS, no reprojection, no unit conversion | `_require_page_crs` gates every page BEFORE any coordinate is interpreted; raises the accepted taxonomy's `WrongCRSError` (`error_type="wrong_crs"`) naming expected vs received. Basis: the recorded live fixture `west_100_st_two_segments.json` carries top-level `"spatialReference":{"wkid":102718,"latestWkid":2263}` on the query page (research Part 2.3). Note the gate refuses `{"wkid":2263}` too — only the exact live-verified pair passes. Additionally the page's declared `geometryType` must be `esriGeometryPolyline` (else typed `SchemaDriftError`), so an attribute-only or non-polyline page can never be misread as geometry. No conversion/reprojection code path exists (test-enforced import allowlist + token scan). |
| 3 | Validity taxonomy: null/missing geometry, empty paths, path <2 points, non-numeric / non-finite coordinates each a TYPED state; absence visible, never a silent drop | Per-feature statuses: `ok`, `null_geometry`, `malformed_geometry_object`, `unexpected_geometry_kind` (e.g. a rings/polygon payload), `empty_paths`, `degenerate_path`, `malformed_coordinate` (incl. the bool-is-not-numeric trap), `nonfinite_coordinate` (NaN/Infinity). A refused geometry keeps its entry — identity + attributes stay paired and visible (`features_total` / `usable_geometry_count` / `refused_geometry_count` aggregates). No partial-polyline repair: one defective path/vertex refuses the whole feature's geometry with the first defect typed in `findings` (proven: the intact sibling path is NOT salvaged). No coordinate coercion; extra z/m vertex components are recorded visibly as findings, never silently discarded. |
| 4 | Values pass through untouched | Coordinates are exposed exactly as parsed from the wire JSON (typed `(float, float)` tuples); no rounding/simplification/averaging/conversion. Test proves entry paths equal an independent `json.loads` of the same body, plus a high-precision/integer/negative passthrough case. |
| 5 | Provenance per output | Page level: `request_url`, `retrieved_at`, `correlation_id`, `raw_digest` (via the accepted `raw_body_digest`), `source_id`, `service_root`, `layer`, `attribution`, `disclaimer`, CRS stamp, declared `geometry_type`, `units` passthrough (`esriFeet` on the fixture), `contract_version`. Query level additionally: `pages_fetched`, `page_urls`, per-page `raw_digests`, `source_data_last_edited(_ms)`, `metadata_request_url`, `drift_signals` — all carried unchanged from the accepted transport result. |
| 6 | Zero new dependencies; accepted modules read-only | Imports are stdlib + the accepted transport module only (AST-asserted in the test suite). No dependency file was touched. |

## 3. Acceptance scenarios → evidence

| Scenario | Evidence (all in the new test file; all PASS) |
|---|---|
| S1 wire_format_parse_and_typing | `test_recorded_fixture_page_parses_typed_multipath_polylines` (real fixture: OBJECTID 7719 → 3 paths / 6 vertices, 14471 → 3 paths / 12 vertices; typed float tuples; first vertex `(992185.54514055, 229943.965358555)`), `test_entries_pair_geometry_with_attributes_from_the_same_page_body`, `test_module_reuses_the_accepted_transport_surfaces_by_import` (AST import allowlist + no-URL-building token scan), `test_paged_fetch_transports_each_page_exactly_once` / `test_paged_fetch_walks_multiple_pages_one_transport_each` (counting fetch seam: metadata + N pages = exactly N+1 transports, no second fetch per page) |
| S2 crs_fail_closed | `test_crs_fail_closed_rejects_everything_but_the_authoritative_pair` (8 variants: key absent, JSON null, wkid absent, WGS84, bare-2263, latestWkid absent, wrong latestWkid, non-object) — typed `wrong_crs` naming expected vs received; `test_crs_gate_runs_before_the_geometry_type_check`; `test_non_polyline_page_geometry_type_is_typed_schema_drift`; `test_paged_fetch_fails_closed_when_a_page_carries_the_wrong_crs`; no-reprojection/no-conversion proof inside the reuse test |
| S3 malformed_geometry_taxonomy | `test_each_malformed_geometry_condition_is_a_distinct_typed_state` (13 parametrized conditions incl. NaN/Infinity and boolean coordinates), `test_a_bad_feature_never_hides_or_drops_its_page_neighbors`, `test_no_partial_polyline_repair_one_bad_path_refuses_the_whole_geometry`, `test_extra_vertex_components_are_visible_not_silently_discarded` |
| S4 passthrough_integrity_and_provenance | `test_paths_match_the_wire_json_exactly_no_rounding`, `test_high_precision_and_integer_wire_values_pass_through_untouched`, `test_page_provenance_carries_retrieval_identity_and_digest`, `test_paged_fetch_carries_transport_provenance_through` |
| S5 scope_and_regression | Exactly the three allowed files changed (working tree; orchestrator verifies via `git status` at integration). Documented commands, this worktree, 2026-09-14: `python -m pytest services/api/tests/connectors/test_dcm_street_centerline_geometry.py` → **39 passed**; `python -m pytest services/api/tests/connectors` → **752 passed** (accepted suites all green — accepted connectors byte-unchanged); `python -m ruff check services/api` → **All checks passed** (exit 0); `python tools/modularity_check.py --check` → **failures 0** (17 pre-existing warnings, none on this task's files). Zero new dependencies. |

## 4. Command log (documented commands only, exact invocations — original unit)

| Command | Result |
|---|---|
| `python -m pytest services/api/tests/connectors/test_dcm_street_centerline_geometry.py` | first run 38 passed / 1 failed (the producer's own source-scan test matched the prose word "reprojection" in the module docstring — test tightened to an AST import allowlist + non-prose tokens; no module behavior change); final run **39 passed** |
| `python -m pytest services/api/tests/connectors` | **752 passed** |
| `python -m ruff check services/api` | **All checks passed!** (exit 0) |
| `python tools/modularity_check.py --check` | **selected 403 files; failures 0; warnings 17** (all pre-existing, none on M4-T020 files) |

## 5. Honest notes / limits

- Local interpreter for this unit's runs is Python 3.11.9 (thin-client sandbox); the whole
  connectors suite collected and passed under it. CI remains the canonical py312 context.
- The CRS gate requires the exact live-verified pair `{wkid:102718, latestWkid:2263}`; a page
  reporting the modern id alone (`wkid:2263`) is refused. This is deliberate fail-closed
  behavior pinned to the recorded wire evidence; if DCP ever migrates the service's reported
  pair, the typed `wrong_crs` error surfaces it for a sourced decision instead of silent
  acceptance.
- `fetch_street_segment_geometries` re-parses each page body once on the geometry side
  (deterministic, zero I/O); the single-transport-per-page guarantee is structural (recording
  seam) and test-enforced.
- The first-run test failure and fix in §4 is disclosed deviation-free rework inside the
  producer's own new test file; no accepted file was involved.
- The D-047 producer-model note: this unit executed under the loop's owner-pinned worker model
  (packet `path_notes`; deviation already recorded at G0 / owner seam — nothing new from this
  unit).
- **Resubmission note (2026-09-14):** §7–§11 below were added on supervisor request purely as
  evidence packaging. The implementation and test files were NOT modified for the resubmission:
  the only working-tree motion was a disclosed temporary digest probe appended to, then removed
  from, the producer's own test file (§7.2); the final working tree is digest-verified identical
  to the form all §8 commands ran against.

## 6. Self-check summary

All four documented commands green at the end of the unit; scope exactly the three allowed
paths; accepted modules imported read-only and byte-unchanged; taxonomy/CRS/passthrough/
provenance behaviors each carried by named executable tests listed above.

## 7. Resubmission: digest binding for the embedded full sources (§10–§11)

The supervisor returned the prior checkpoint requesting digest-bound sections exposing the
COMPLETE geometry module and test file, chunked so neither implementation nor assertions are
omitted. §10 and §11 embed both files verbatim and in full; this section binds those embedded
sections to the working tree with sha256 digests the supervisor can independently re-collect.

### 7.1 Binding digests (working tree, worktree `wt-m4t020`, 2026-09-14)

| Artifact | sha256 (LF-normalized) | Bytes (LF) | Lines |
|---|---|---|---|
| `services/api/app/connectors/dcm_street_centerline_geometry.py` | `864b24fc6d911571c40828632d8942e3af1c76c0593acdd9d118e350d4223ef4` | 22920 | 572 (572 `\n`; ends with one terminating newline) |
| `services/api/tests/connectors/test_dcm_street_centerline_geometry.py` | `6f3f5892428caf990d518d8bd7afe9779a0c70fa1b04605fb9bd299fdf220f03` | 21663 | 576 (576 `\n`; ends with one terminating newline) |

Both files are LF on disk in this worktree (for the module the raw-byte digest was measured and
EQUALS the LF-normalized digest above; the test-file digest is defined in LF space by
construction, §7.2). Each file ends with exactly one terminating newline (the byte counts above
include it); the stated digests are over the exact byte content described.

### 7.2 Collection method — disclosed temporary in-suite digest probe

Producers in this regime cannot run ad-hoc shell commands (`git hash-object` is not
broker-approved), so the digests were collected with the proven stale-span inspectability
pattern: a disclosed TEMPORARY probe test appended to the producer's own test file (an allowed
path), run through the documented pytest command, then removed. The probe deliberately fails
with an `AssertionError` whose message carries the digest payload.

Because a probe cannot naively self-bind its host file (its own bytes are part of what it
hashes), the probe bound the test file via a PREFIX construction: it hashed the LF-normalized
bytes strictly BEFORE the probe block's unique marker (`\n\n# === TEMPORARY M4-T020 DIGEST
PROBE`). Since the probe block was appended immediately after the file's last byte and then
removed by exact reverse edit, that prefix IS the final test file byte-for-byte. Consistency
cross-checks: the probe run collected exactly 40 items (39 real tests + probe), pytest located
the probe's `raise` at line 607 (= 577 final lines + the appended block's offset), and the
payload's newline counts (572 / 576) equal the line totals in §9.

The probe block, verbatim as appended (and then removed by the exact reverse edit):

```python
# === TEMPORARY M4-T020 DIGEST PROBE (disclosed; removed before checkpoint) ===
def test_m4t020_temporary_digest_probe() -> None:
    """Deliberately failing digest probe (stale-span inspectability pattern):
    raises AssertionError carrying sha256 digests that bind the producer
    report's embedded full-source sections to this working tree. The test
    file binds via the LF-normalized prefix BEFORE this probe block (a probe
    cannot self-bind its host file's final form directly); the probe is
    removed, and the removal disclosed, before the checkpoint."""
    import hashlib

    with open(geometry_module.__file__, "rb") as f:
        module_raw = f.read()
    with open(__file__, "rb") as f:
        self_raw = f.read()
    module_lf = module_raw.replace(b"\r\n", b"\n")
    self_lf = self_raw.replace(b"\r\n", b"\n")
    marker = b"\n\n# === TEMPORARY M4-T020 DIGEST PROBE"
    final_test_lf = self_lf[: self_lf.index(marker)]
    payload = {
        "module_raw_sha256": hashlib.sha256(module_raw).hexdigest(),
        "module_raw_bytes": len(module_raw),
        "module_lf_sha256": hashlib.sha256(module_lf).hexdigest(),
        "module_lf_bytes": len(module_lf),
        "module_lf_lines": module_lf.count(b"\n"),
        "testfile_final_lf_sha256": hashlib.sha256(final_test_lf).hexdigest(),
        "testfile_final_lf_bytes": len(final_test_lf),
        "testfile_final_lf_lines": final_test_lf.count(b"\n"),
    }
    raise AssertionError(f"M4T020-DIGEST-PROBE {payload!r}")
```

Probe-run payload, verbatim from the documented command's failure output:

```
M4T020-DIGEST-PROBE {'module_raw_sha256': '864b24fc6d911571c40828632d8942e3af1c76c0593acdd9d118e350d4223ef4',
'module_raw_bytes': 22920,
'module_lf_sha256': '864b24fc6d911571c40828632d8942e3af1c76c0593acdd9d118e350d4223ef4',
'module_lf_bytes': 22920, 'module_lf_lines': 572,
'testfile_final_lf_sha256': '6f3f5892428caf990d518d8bd7afe9779a0c70fa1b04605fb9bd299fdf220f03',
'testfile_final_lf_bytes': 21663, 'testfile_final_lf_lines': 576}
```

(Line breaks added here for readability only; the run emitted it as one line.)

### 7.3 Supervisor/orchestrator re-collection instructions

To verify independently at collection time: read each file's working-tree bytes, replace every
`\r\n` with `\n`, sha256 the result, and compare with §7.1. To verify the embedded sections:
concatenate the §10 chunks G1–G7 in order (they are contiguous, non-overlapping line ranges
1–572) and the §11 chunks T1–T9 in order (contiguous ranges 1–576); each concatenation, joined
with `\n` line terminators plus ONE trailing `\n` (each file ends with a single terminating
newline), reproduces the corresponding file's LF-normalized bytes exactly and must hash to the
§7.1 digest. This reassembly was itself machine-verified in this worktree (§7.4).

### 7.4 Reassembly verification — the embedded sections are machine-proven, not trusted

Because §10–§11 were transcribed into this report by the producer, transcription itself was a
risk surface. It was eliminated mechanically: a SECOND disclosed temporary probe (same pattern,
same allowed path, same documented command) read this report from disk, extracted every
` ```python ` fence in §10 and §11, reassembled the chunks per the §7.3 rule, and compared the
result byte-for-byte against the working-tree module and the test file's final form (prefix
construction, as in §7.2).

The first reassembly run deliberately exposed its own packaging defects: it reported both
reassemblies as strict line-prefixes of the actual files (zero content mismatches over all
572 / 576 compared lines) and thereby surfaced that both files END with a terminating newline
and that three declared chunk ranges (G6/G7/T9) were off by one. The §7.1/§9/§10/§11 metadata
was corrected accordingly; NO source chunk content needed any change. The corrected probe run
then returned full equality. Final payload, verbatim:

```
M4T020-REASSEMBLY-PROBE {'module_chunks': 7, 'test_chunks': 9,
'module_reassembly_matches_file': True,
'module_reassembled_sha256': '864b24fc6d911571c40828632d8942e3af1c76c0593acdd9d118e350d4223ef4',
'testfile_reassembly_matches_final_form': True,
'testfile_reassembled_sha256': '6f3f5892428caf990d518d8bd7afe9779a0c70fa1b04605fb9bd299fdf220f03',
'module_first_diff': None, 'testfile_first_diff': None}
```

(Line breaks added for readability; emitted as one line.) The reassembled sha256 digests equal
the §7.1 binding digests exactly: the embedded sections reproduce both files byte-for-byte.

The verification probe, verbatim as appended (and then removed by the exact reverse edit):

```python
# === TEMPORARY M4-T020 DIGEST PROBE (disclosed; removed before checkpoint) ===
def test_m4t020_temporary_reassembly_probe() -> None:
    """Deliberately failing verification probe (disclosed; removed before the
    checkpoint): reassembles the producer report's embedded source chunks
    (report sections 10 and 11) and proves they reproduce this working
    tree's module and final-form test file byte-for-byte (LF-normalized)."""
    import hashlib
    import re

    root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    report_path = os.path.join(
        root, "project-control", "reports", "M4-T020-producer-report.md"
    )
    with open(report_path, "rb") as f:
        report = f.read().replace(b"\r\n", b"\n").decode("utf-8")
    with open(geometry_module.__file__, "rb") as f:
        module_lf = f.read().replace(b"\r\n", b"\n").decode("utf-8")
    with open(__file__, "rb") as f:
        self_lf = f.read().replace(b"\r\n", b"\n")
    marker = b"\n\n# === TEMPORARY M4-T020 DIGEST PROBE"
    final_test_lf = self_lf[: self_lf.index(marker)].decode("utf-8")

    idx10 = report.index("\n## 10.")
    idx11 = report.index("\n## 11.")
    fences = re.compile(r"```python\n(.*?)\n```", re.DOTALL)
    module_chunks = fences.findall(report[idx10:idx11])
    test_chunks = fences.findall(report[idx11:])
    module_reassembled = "\n".join(module_chunks) + "\n"
    test_reassembled = "\n".join(test_chunks) + "\n"

    def first_diff(reassembled: str, actual: str) -> object:
        a_lines = reassembled.split("\n")
        b_lines = actual.split("\n")
        for i, (x, y) in enumerate(zip(a_lines, b_lines)):
            if x != y:
                return {"line": i + 1, "reassembled": x[:70], "actual": y[:70]}
        if len(a_lines) != len(b_lines):
            return {"reassembled_lines": len(a_lines), "actual_lines": len(b_lines)}
        return None

    payload = {
        "module_chunks": len(module_chunks),
        "test_chunks": len(test_chunks),
        "module_reassembly_matches_file": module_reassembled == module_lf,
        "module_reassembled_sha256": hashlib.sha256(
            module_reassembled.encode("utf-8")
        ).hexdigest(),
        "testfile_reassembly_matches_final_form": test_reassembled == final_test_lf,
        "testfile_reassembled_sha256": hashlib.sha256(
            test_reassembled.encode("utf-8")
        ).hexdigest(),
        "module_first_diff": first_diff(module_reassembled, module_lf),
        "testfile_first_diff": first_diff(test_reassembled, final_test_lf),
    }
    raise AssertionError(f"M4T020-REASSEMBLY-PROBE {payload!r}")
```

(The v1 run of this probe differed only in joining the chunks WITHOUT the trailing terminating
`\n`; that omission was itself the finding it surfaced.)

## 8. Resubmission command log (documented commands only, exact invocations)

| # | Command | Result |
|---|---|---|
| 1 | `python -m pytest services/api/tests/connectors/test_dcm_street_centerline_geometry.py` | digest-collection run (§7.2 probe present, disclosed): **39 passed, 1 failed** — the single failure is the deliberate digest probe; payload quoted verbatim in §7.2; exit 1 |
| 2 | `python -m pytest services/api/tests/connectors/test_dcm_street_centerline_geometry.py` | digest probe removed (exact reverse edit): **39 passed**, exit 0 |
| 3 | `python -m pytest services/api/tests/connectors` | **752 passed**, exit 0 |
| 4 | `python -m ruff check services/api` | **All checks passed!**, exit 0 |
| 5 | `python tools/modularity_check.py --check` | **selected 403 files; failures 0; warnings 17** (all pre-existing, none on M4-T020 files), exit 0 |
| 6 | `python -m pytest services/api/tests/connectors/test_dcm_street_centerline_geometry.py` | reassembly-verification run v1 (§7.4 probe present, disclosed): **39 passed, 1 failed** — probe payload surfaced the terminating-newline representation and the G6/G7/T9 declared-range off-by-ones; report metadata corrected, source chunks unchanged; exit 1 |
| 7 | `python -m pytest services/api/tests/connectors/test_dcm_street_centerline_geometry.py` | reassembly-verification run v2 (corrected probe): **39 passed, 1 failed** — payload (verbatim in §7.4) proves both reassemblies equal the working-tree files with sha256 equal to §7.1; exit 1 |
| 8 | `python -m pytest services/api/tests/connectors/test_dcm_street_centerline_geometry.py` | reassembly probe removed (exact reverse edit), FINAL state: **39 passed**, exit 0 |
| 9 | `python -m pytest services/api/tests/connectors` | FINAL state: **752 passed**, exit 0 |
| 10 | `python -m ruff check services/api` | FINAL state: **All checks passed!**, exit 0 |
| 11 | `python tools/modularity_check.py --check` | FINAL state: **selected 403 files; failures 0; warnings 17** (all pre-existing, none on M4-T020 files), exit 0 |

Runs 2–5 and 8–11 all executed against exactly the §7.1 digest-bound module/test bytes, so the
original §4 evidence and this resubmission's evidence describe one and the same content
identity. The only file that changed between runs 5 and 6 is this report itself.

## 9. Chunk index and review-dimension routing

Chunks are contiguous, non-overlapping, and complete: G1–G7 concatenated = the whole module
(lines 1–572); T1–T9 concatenated = the whole test file (lines 1–576). Nothing is elided.

| Chunk | Lines | Content |
|---|---|---|
| G1 | 1–59 | Module docstring: reuse discipline, CRS fail-closed contract, taxonomy, passthrough |
| G2 | 60–140 | Imports (accepted-transport surface), `__all__`, contract version, expected geometry type, status taxonomy constants, `TypedPaths` |
| G3 | 141–183 | CRS gate `_require_page_crs` (fail closed, before any coordinate) |
| G4 | 184–293 | `_extract_paths`: per-feature typed taxonomy, no repair, no coercion, extra-component findings |
| G5 | 294–379 | Typed results: `SegmentPolyline`, `SegmentGeometryPage`, `SegmentGeometryQueryResult` (provenance fields) |
| G6 | 380–477 | `parse_segment_geometry_page`: reuse order, CRS gate, geometryType check, pairing guard, page provenance |
| G7 | 478–572 | `fetch_street_segment_geometries`: recording seam, single-fetch pairing guards, query provenance passthrough |
| T1 | 1–54 | Test docstring, imports, fixture dir, correlation id, authoritative SR constant |
| T2 | 55–161 | Builders/helpers: `_fixture_body`, `_attributes`, `_feature`, `_page_body`, `_transport`, `_parse`, `_counting_fetcher` |
| T3 | 162–226 | S1: recorded-fixture parse/typing, attribute pairing, no-rounding equality, exceeded flag, empty page |
| T4 | 227–282 | S1 reuse fidelity: AST import allowlist + forbidden-token scan; reused transport-failure typing |
| T5 | 283–333 | S2: CRS refusal matrix (8 variants), gate ordering, geometryType schema drift |
| T6 | 334–437 | S3: 13 parametrized malformed-geometry conditions → distinct typed states, visibility invariants |
| T7 | 438–475 | S3: neighbor visibility, no partial-polyline repair, extra-component visibility |
| T8 | 476–514 | S4: high-precision passthrough; page provenance schema assertions |
| T9 | 515–576 | Paged flow: single transport per page, provenance carry-through, multi-page walk, paged CRS fail-closed |

Review-dimension routing (each dimension's complete surface):

| Dimension | Module chunks | Test chunks |
|---|---|---|
| Transport reuse / single fetch | G1, G2, G6, G7 | T4, T9 |
| CRS validation | G1, G3, G6 | T5, T9 |
| Geometry taxonomy | G2, G4 | T6, T7 |
| Coordinate integrity / passthrough | G4 | T3, T7, T8 |
| Provenance | G5, G6, G7 | T8, T9 |
| Test assertions (complete) | — | T1–T9 |

## 10. Complete module source (digest-bound): `services/api/app/connectors/dcm_street_centerline_geometry.py`

sha256(LF) `864b24fc6d911571c40828632d8942e3af1c76c0593acdd9d118e350d4223ef4` — 572 lines, single terminating newline.

### G1 — lines 1–59

```python
"""DCM Street Center Line polyline-geometry sibling module (task M4-T020,
D-045 A2 geometry lane item B3; pinned research
``project-control/reports/M4-T016-a2-geometry-mechanics-research.md`` Parts
2.3, 3.1, and 4.3 item 1).

MEASUREMENT-GRADE GEOMETRY VIEW over the SAME wire bytes the accepted
M4-T015 transport (:mod:`app.connectors.dcm_street_centerline_arcgis`)
already fetches: ``returnGeometry`` defaults TRUE on this endpoint, so every
segment-query page body already carries ``features[].geometry.paths``; the
accepted ``parse_segment_page`` deliberately reads attributes only and stays
byte-immutable. This sibling module (the ``mappluto_lot_outline.py``-beside-
``mappluto_geometry_arcgis.py`` precedent, here on the measurement side)
parses, CRS-validates, and TYPES that polyline geometry WITHOUT modifying
the accepted module and WITHOUT ever issuing a second fetch for the same
page.

REUSE DISCIPLINE (packet contract item 1): every transport surface -
fetching, URL building, paging with its loop-safety guarantees, HTTP-status
and ArcGIS-error handling, attribute typing, and the raw-body digest - is
reused by READ-ONLY import from the accepted module. This module builds no
URL, opens no socket of its own, and re-implements no validation the
accepted module already owns. ``parse_segment_geometry_page`` consumes the
exact :class:`DcmTransport` the accepted fetch produced;
``fetch_street_segment_geometries`` drives the accepted
``fetch_street_segments`` through a pass-through recording seam so each page
body is transported ONCE and then parsed on both the attribute side
(accepted module) and the geometry side (this module).

CRS FAIL-CLOSED (packet contract item 2; research Part 2.3): the query-page
``spatialReference`` must be exactly wkid 102718 / latestWkid 2263
(EPSG:2263, NAD83 New York Long Island, US survey feet - the live-verified
value on the recorded fixtures). Anything else, or an absent/mistyped
spatial reference, raises the typed ``wrong_crs`` error naming expected vs
received. There is NO assumed-CRS path, NO reprojection path, and NO unit
conversion anywhere in this module. This is the measurement-grade sibling;
display-only EPSG:4326 remains ``mappluto_lot_outline``'s job and this
module never serves display.

GEOMETRY-VALIDITY TAXONOMY (packet contract item 3, the
``mappluto_geometry_arcgis`` precedent): a feature whose geometry is
null/missing, malformed, empty, degenerate (a path with fewer than two
points), or carries non-numeric or non-finite coordinates is a DISTINCT
typed state on a visible entry - never a silent drop and never an exception
that hides the rest of the page. Downstream buffer correctness (B4) depends
on absence being visible. There is no partial-polyline repair and no
coordinate coercion: one defective path or vertex refuses the WHOLE
feature's geometry with the specific typed reason (first defect in document
order), while the feature itself - identity and attributes - stays in the
result.

PASSTHROUGH INTEGRITY (packet contract item 4): coordinate values are
exposed exactly as parsed from the wire JSON - no rounding, simplification,
averaging, or unit conversion. Multi-path segments (real on this layer: the
accepted West 100 Street fixture carries three paths per segment) are
preserved as distinct paths in wire order.

Deterministic code only: no AI, no legal interpretation. The official DCP
disclaimer applies (informational purposes only).
"""
```

### G2 — lines 60–140

```python

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite

from app.connectors.dcm_street_centerline_arcgis import (
    ATTRIBUTION,
    CRS_STAMP,
    DCP_DISCLAIMER,
    EXPECTED_LATEST_WKID,
    EXPECTED_WKID,
    LAYER_NAME,
    MAX_RESULT_RECORD_COUNT,
    SERVICE_ROOT,
    SOURCE_ID,
    DcmTransport,
    MalformedResponseError,
    SchemaDriftError,
    StreetSegment,
    WrongCRSError,
    build_metadata_url,
    default_fetch,
    fetch_street_segments,
    parse_segment_page,
    raw_body_digest,
)

__all__ = [
    "EXPECTED_PAGE_GEOMETRY_TYPE",
    "GEOMETRY_CONTRACT_VERSION",
    "GEOMETRY_DEGENERATE_PATH",
    "GEOMETRY_EMPTY_PATHS",
    "GEOMETRY_MALFORMED_COORDINATE",
    "GEOMETRY_MALFORMED_OBJECT",
    "GEOMETRY_NONFINITE_COORDINATE",
    "GEOMETRY_NULL",
    "GEOMETRY_OK",
    "GEOMETRY_STATUSES",
    "GEOMETRY_UNEXPECTED_KIND",
    "SegmentGeometryPage",
    "SegmentGeometryQueryResult",
    "SegmentPolyline",
    "fetch_street_segment_geometries",
    "parse_segment_geometry_page",
]

GEOMETRY_CONTRACT_VERSION = "1.0.0"

# The layer's documented geometry type; a query page declaring anything else
# (or declaring nothing - e.g. an attribute-only page this module must never
# be fed) is typed schema drift, never guessed around.
EXPECTED_PAGE_GEOMETRY_TYPE = "esriGeometryPolyline"

# Per-feature geometry-validity taxonomy (packet contract item 3; the
# mappluto_geometry_arcgis findings-code precedent). Each condition the
# packet names is a DISTINCT status; ``findings`` carries the path/vertex
# coordinates of the first defect in document order.
GEOMETRY_OK = "ok"
GEOMETRY_NULL = "null_geometry"
GEOMETRY_MALFORMED_OBJECT = "malformed_geometry_object"
GEOMETRY_UNEXPECTED_KIND = "unexpected_geometry_kind"
GEOMETRY_EMPTY_PATHS = "empty_paths"
GEOMETRY_DEGENERATE_PATH = "degenerate_path"
GEOMETRY_MALFORMED_COORDINATE = "malformed_coordinate"
GEOMETRY_NONFINITE_COORDINATE = "nonfinite_coordinate"

GEOMETRY_STATUSES = (
    GEOMETRY_OK,
    GEOMETRY_NULL,
    GEOMETRY_MALFORMED_OBJECT,
    GEOMETRY_UNEXPECTED_KIND,
    GEOMETRY_EMPTY_PATHS,
    GEOMETRY_DEGENERATE_PATH,
    GEOMETRY_MALFORMED_COORDINATE,
    GEOMETRY_NONFINITE_COORDINATE,
)

TypedPaths = tuple[tuple[tuple[float, float], ...], ...]
```

### G3 — lines 141–183

```python


# ---------------------------------------------------------------------------
# CRS gate (fail closed, BEFORE any coordinate is interpreted)
# ---------------------------------------------------------------------------


def _describe_spatial_reference(spatial_reference: object) -> str:
    if spatial_reference is None:
        return "absent"
    return repr(spatial_reference)[:200]


def _require_page_crs(
    spatial_reference: object, *, url: str, correlation_id: str
) -> None:
    """The page-level CRS gate: geometry is interpreted ONLY under the
    authoritative EPSG:2263 spatial reference (wkid 102718 / latestWkid
    2263, US survey feet - research Part 2.3). Anything else or absent is
    the typed ``wrong_crs`` refusal naming expected vs received; there is
    no assumed-CRS path and no reprojection path."""
    if (
        isinstance(spatial_reference, dict)
        and spatial_reference.get("wkid") == EXPECTED_WKID
        and spatial_reference.get("latestWkid") == EXPECTED_LATEST_WKID
    ):
        return
    raise WrongCRSError(
        "segment-query page spatialReference is not the authoritative "
        f"EPSG:2263 (expected wkid {EXPECTED_WKID} / latestWkid "
        f"{EXPECTED_LATEST_WKID}; received "
        f"{_describe_spatial_reference(spatial_reference)}); geometry in an "
        "unknown or unexpected CRS is never interpreted, assumed, or "
        "reprojected",
        correlation_id=correlation_id,
        detail={
            "url": url,
            "expected": {"wkid": EXPECTED_WKID, "latestWkid": EXPECTED_LATEST_WKID},
            "received": _describe_spatial_reference(spatial_reference),
        },
    )


```

### G4 — lines 184–293

```python
# ---------------------------------------------------------------------------
# Per-feature geometry extraction (typed taxonomy, no repair, no coercion)
# ---------------------------------------------------------------------------


def _extract_paths(
    geometry_present: bool, geometry: object
) -> tuple[str, list[str], TypedPaths | None]:
    """Extract and type one feature's ``geometry.paths``. Returns
    ``(status, findings, paths)``: ``paths`` is populated ONLY on
    ``GEOMETRY_OK``; every refusal is the whole geometry (no partial
    salvage) with the first defect in document order typed in ``findings``.
    Values pass through untouched - the only transformation is the numeric
    JSON value becoming a Python float, which preserves the parsed value
    bit-for-bit."""
    if not geometry_present:
        return GEOMETRY_NULL, ["geometry_key_missing"], None
    if geometry is None:
        return GEOMETRY_NULL, ["geometry_json_null"], None
    if not isinstance(geometry, dict):
        return (
            GEOMETRY_MALFORMED_OBJECT,
            [f"geometry_not_an_object:{type(geometry).__name__}"],
            None,
        )
    if "paths" not in geometry:
        other_kind_keys = [
            key for key in ("rings", "points", "x", "y") if key in geometry
        ]
        if other_kind_keys:
            # A polygon/multipoint/point payload where the layer contracts
            # polylines: typed visibly, never coerced (the
            # mappluto_geometry_arcgis geometry-collection precedent).
            return (
                GEOMETRY_UNEXPECTED_KIND,
                ["non_polyline_geometry_keys:" + ",".join(other_kind_keys)],
                None,
            )
        return GEOMETRY_MALFORMED_OBJECT, ["paths_key_missing"], None
    raw_paths = geometry["paths"]
    if not isinstance(raw_paths, list):
        return (
            GEOMETRY_MALFORMED_OBJECT,
            [f"paths_not_a_list:{type(raw_paths).__name__}"],
            None,
        )
    if not raw_paths:
        return GEOMETRY_EMPTY_PATHS, ["paths_empty"], None

    findings: list[str] = []
    typed_paths: list[tuple[tuple[float, float], ...]] = []
    for path_index, raw_path in enumerate(raw_paths):
        if not isinstance(raw_path, list):
            return (
                GEOMETRY_MALFORMED_OBJECT,
                [f"path_{path_index}_not_a_list:{type(raw_path).__name__}"],
                None,
            )
        if len(raw_path) < 2:
            return (
                GEOMETRY_DEGENERATE_PATH,
                [
                    f"path_{path_index}_has_{len(raw_path)}_point(s);"
                    "_a_polyline_path_needs_at_least_2"
                ],
                None,
            )
        typed_vertices: list[tuple[float, float]] = []
        for vertex_index, vertex in enumerate(raw_path):
            if not isinstance(vertex, list | tuple) or len(vertex) < 2:
                return (
                    GEOMETRY_MALFORMED_COORDINATE,
                    [f"path_{path_index}_vertex_{vertex_index}_is_not_an_xy_pair"],
                    None,
                )
            for axis, component in (("x", vertex[0]), ("y", vertex[1])):
                if isinstance(component, bool) or not isinstance(
                    component, int | float
                ):
                    return (
                        GEOMETRY_MALFORMED_COORDINATE,
                        [
                            f"path_{path_index}_vertex_{vertex_index}_{axis}"
                            f"_non_numeric:{type(component).__name__}"
                        ],
                        None,
                    )
            x, y = float(vertex[0]), float(vertex[1])
            if not (isfinite(x) and isfinite(y)):
                return (
                    GEOMETRY_NONFINITE_COORDINATE,
                    [
                        f"path_{path_index}_vertex_{vertex_index}"
                        f"_nonfinite:({vertex[0]!r},{vertex[1]!r})"
                    ],
                    None,
                )
            if len(vertex) > 2:
                # Extra components (z/m) are outside the typed (x, y)
                # contract: recorded VISIBLY, never silently discarded
                # without a trace, never coerced into the pair.
                findings.append(
                    f"path_{path_index}_vertex_{vertex_index}"
                    f"_extra_components:{len(vertex) - 2}"
                )
            typed_vertices.append((x, y))
        typed_paths.append(tuple(typed_vertices))
    return GEOMETRY_OK, findings, tuple(typed_paths)


```

### G5 — lines 294–379

```python
# ---------------------------------------------------------------------------
# Typed results
# ---------------------------------------------------------------------------


@dataclass
class SegmentPolyline:
    """One feature from a segment-query page: the accepted transport's
    typed :class:`StreetSegment` (identity + attributes, parsed from the
    SAME page body) paired with this module's typed geometry view.
    ``paths`` is populated only when ``status`` is ``GEOMETRY_OK``; a
    feature with attributes but no usable geometry stays VISIBLE here with
    its distinct typed status - never silently dropped."""

    feature_index: int
    segment: StreetSegment
    status: str
    findings: list[str]
    paths: TypedPaths | None
    path_count: int
    vertex_count: int

    @property
    def object_id(self) -> int | None:
        return self.segment.object_id

    @property
    def has_usable_geometry(self) -> bool:
        return self.status == GEOMETRY_OK


@dataclass
class SegmentGeometryPage:
    """One parsed segment-query page on the geometry side, with per-page
    provenance (retrieval identity + raw-body digest passthrough)."""

    entries: list[SegmentPolyline]
    exceeded_transfer_limit: bool
    features_total: int
    usable_geometry_count: int
    refused_geometry_count: int
    geometry_type: str
    units: str | None
    wkid: int
    latest_wkid: int
    crs: dict
    correlation_id: str
    request_url: str
    retrieved_at: str
    raw_digest: str
    source_id: str = SOURCE_ID
    service_root: str = SERVICE_ROOT
    layer: str = LAYER_NAME
    attribution: str = ATTRIBUTION
    disclaimer: str = DCP_DISCLAIMER
    contract_version: str = GEOMETRY_CONTRACT_VERSION


@dataclass
class SegmentGeometryQueryResult:
    """Complete result of one bounded, possibly-paged geometry query:
    flattened typed entries, the per-page parses, and the provenance the
    accepted transport exposes (source freshness fields, retrieval
    identity, per-page raw-body digests, drift signals)."""

    entries: list[SegmentPolyline]
    pages: list[SegmentGeometryPage]
    exceeded_transfer_limit_on_last_page: bool
    pages_fetched: int
    page_urls: list[str]
    raw_digests: list[str]
    correlation_id: str
    retrieved_at: str
    source_data_last_edited_ms: int | None
    source_data_last_edited: str | None
    metadata_request_url: str
    drift_signals: list[str]
    crs: dict
    source_id: str = SOURCE_ID
    service_root: str = SERVICE_ROOT
    layer: str = LAYER_NAME
    attribution: str = ATTRIBUTION
    disclaimer: str = DCP_DISCLAIMER
    contract_version: str = GEOMETRY_CONTRACT_VERSION


```

### G6 — lines 380–477

```python
# ---------------------------------------------------------------------------
# Page-level parse (the core parse-and-expose surface)
# ---------------------------------------------------------------------------


def parse_segment_geometry_page(
    transport: DcmTransport, *, correlation_id: str
) -> SegmentGeometryPage:
    """Parse ONE already-transported query page on the geometry side.

    Order of operations: (1) the accepted ``parse_segment_page`` runs first
    - reusing, not re-implementing, the HTTP-status check, the
    ArcGIS-error-object classification, the malformed-body refusals, and
    the attribute typing; (2) the CRS gate runs BEFORE any coordinate is
    interpreted; (3) the page's declared ``geometryType`` must be the
    documented polyline type (else typed schema drift); (4) each feature's
    geometry is extracted under the typed validity taxonomy and paired by
    document position with its :class:`StreetSegment` from the SAME body.
    """
    segments, exceeded = parse_segment_page(transport, correlation_id=correlation_id)
    # parse_segment_page just proved the body is a well-formed JSON object
    # with a well-formed features list; this second parse of the same bytes
    # is deterministic and involves no I/O (single-fetch guarantee).
    doc = json.loads(transport.body)
    _require_page_crs(
        doc.get("spatialReference"), url=transport.url, correlation_id=correlation_id
    )
    geometry_type = doc.get("geometryType")
    if geometry_type != EXPECTED_PAGE_GEOMETRY_TYPE:
        raise SchemaDriftError(
            "segment-query page does not declare the documented polyline "
            f"geometry type (expected {EXPECTED_PAGE_GEOMETRY_TYPE!r}, "
            f"received {repr(geometry_type)[:200]}); an attribute-only or "
            "non-polyline page is never interpreted as geometry",
            correlation_id=correlation_id,
            detail={
                "url": transport.url,
                "expected": EXPECTED_PAGE_GEOMETRY_TYPE,
                "received": repr(geometry_type)[:200],
            },
        )
    features = doc.get("features")
    if not isinstance(features, list) or len(features) != len(segments):
        # Unreachable in practice (parse_segment_page builds exactly one
        # segment per feature of this same body); kept as a typed guard so
        # a pairing break can never pass silently.
        raise MalformedResponseError(
            "geometry-side feature walk does not line up with the accepted "
            "attribute-side parse of the same page body (pairing guard)",
            correlation_id=correlation_id,
            detail={"url": transport.url},
        )

    entries: list[SegmentPolyline] = []
    for index, (feature, segment) in enumerate(zip(features, segments, strict=True)):
        status, findings, paths = _extract_paths(
            "geometry" in feature, feature.get("geometry")
        )
        entries.append(
            SegmentPolyline(
                feature_index=index,
                segment=segment,
                status=status,
                findings=findings,
                paths=paths,
                path_count=len(paths) if paths is not None else 0,
                vertex_count=(
                    sum(len(path) for path in paths) if paths is not None else 0
                ),
            )
        )
    usable = sum(1 for entry in entries if entry.status == GEOMETRY_OK)

    geometry_properties = doc.get("geometryProperties")
    raw_units = (
        geometry_properties.get("units")
        if isinstance(geometry_properties, dict)
        else None
    )
    units = raw_units if isinstance(raw_units, str) else None

    return SegmentGeometryPage(
        entries=entries,
        exceeded_transfer_limit=exceeded,
        features_total=len(entries),
        usable_geometry_count=usable,
        refused_geometry_count=len(entries) - usable,
        geometry_type=geometry_type,
        units=units,
        wkid=EXPECTED_WKID,
        latest_wkid=EXPECTED_LATEST_WKID,
        crs=dict(CRS_STAMP),
        correlation_id=correlation_id,
        request_url=transport.url,
        retrieved_at=transport.retrieved_at,
        raw_digest=raw_body_digest(transport.body),
    )

```

### G7 — lines 478–572

```python

# ---------------------------------------------------------------------------
# Paged public entry point (accepted transport drives; this module parses)
# ---------------------------------------------------------------------------


def fetch_street_segment_geometries(
    *,
    borough: str | None = None,
    street_name: str | None = None,
    object_id: int | None = None,
    object_id_in: list[int] | None = None,
    page_size: int = MAX_RESULT_RECORD_COUNT,
    max_pages: int | None = None,
    fetch: Callable[[str, str], DcmTransport] = default_fetch,
    correlation_id: str | None = None,
) -> SegmentGeometryQueryResult:
    """Fetch typed segment geometries for exactly one predicate style.

    The accepted ``fetch_street_segments`` performs ALL transport work -
    metadata gate, URL building, paging, loop safety - through a
    pass-through recording seam, so every page body is transported exactly
    ONCE and then parsed here on the geometry side. Provenance from the
    accepted result (source freshness fields, retrieval identity, per-page
    raw digests, drift signals) is carried through unchanged.
    """
    recorded: list[DcmTransport] = []

    def _recording_fetch(url: str, cid: str) -> DcmTransport:
        transport = fetch(url, cid)
        recorded.append(transport)
        return transport

    attribute_result = fetch_street_segments(
        borough=borough,
        street_name=street_name,
        object_id=object_id,
        object_id_in=object_id_in,
        page_size=page_size,
        max_pages=max_pages,
        fetch=_recording_fetch,
        correlation_id=correlation_id,
    )

    metadata_url = build_metadata_url()
    page_transports = [t for t in recorded if t.url != metadata_url]
    if [t.url for t in page_transports] != attribute_result.page_urls:
        # Unreachable in practice (the recording seam sees exactly the
        # calls the accepted loop makes); typed so a transport-pairing
        # break can never pass silently.
        raise MalformedResponseError(
            "recorded page transports do not line up with the accepted "
            "transport's page_urls (single-fetch pairing guard)",
            correlation_id=attribute_result.correlation_id,
            detail={
                "recorded_urls": [t.url for t in page_transports],
                "page_urls": attribute_result.page_urls,
            },
        )

    pages = [
        parse_segment_geometry_page(
            transport, correlation_id=attribute_result.correlation_id
        )
        for transport in page_transports
    ]
    entries = [entry for page in pages for entry in page.entries]
    if len(entries) != len(attribute_result.segments):
        raise MalformedResponseError(
            "geometry-side entry count does not match the accepted "
            "transport's segment count for the same pages (pairing guard)",
            correlation_id=attribute_result.correlation_id,
            detail={
                "geometry_entries": len(entries),
                "attribute_segments": len(attribute_result.segments),
            },
        )

    return SegmentGeometryQueryResult(
        entries=entries,
        pages=pages,
        exceeded_transfer_limit_on_last_page=(
            attribute_result.exceeded_transfer_limit_on_last_page
        ),
        pages_fetched=attribute_result.pages_fetched,
        page_urls=list(attribute_result.page_urls),
        raw_digests=list(attribute_result.raw_digests),
        correlation_id=attribute_result.correlation_id,
        retrieved_at=attribute_result.retrieved_at,
        source_data_last_edited_ms=attribute_result.source_data_last_edited_ms,
        source_data_last_edited=attribute_result.source_data_last_edited,
        metadata_request_url=attribute_result.metadata_request_url,
        drift_signals=list(attribute_result.drift_signals),
        crs=dict(CRS_STAMP),
    )
```

## 11. Complete test source (digest-bound): `services/api/tests/connectors/test_dcm_street_centerline_geometry.py`

sha256(LF) `6f3f5892428caf990d518d8bd7afe9779a0c70fa1b04605fb9bd299fdf220f03` — 576 lines, single terminating newline.

### T1 — lines 1–54

```python
"""Fully offline tests for the DCM centerline geometry sibling module
(task M4-T020, packet scenarios S1-S4; S5 is the scope/regression scenario
run via the documented commands). Wire bodies are either the recorded
M4-T015 fixtures in ``services/api/tests/fixtures/dcm_street_centerline/``
(READ-ONLY) or documented in-memory page bodies built here; no network
access occurs in this suite and no fixture file is modified."""

from __future__ import annotations

import ast
import json
import os

import pytest

import app.connectors.dcm_street_centerline_geometry as geometry_module
from app.connectors.dcm_street_centerline_arcgis import (
    ATTRIBUTION,
    CRS_STAMP,
    SOURCE_ID,
    DcmTransport,
    MalformedResponseError,
    SchemaDriftError,
    UpstreamError,
    WrongCRSError,
    build_metadata_url,
    default_fetch,
    raw_body_digest,
)
from app.connectors.dcm_street_centerline_geometry import (
    EXPECTED_PAGE_GEOMETRY_TYPE,
    GEOMETRY_DEGENERATE_PATH,
    GEOMETRY_EMPTY_PATHS,
    GEOMETRY_MALFORMED_COORDINATE,
    GEOMETRY_MALFORMED_OBJECT,
    GEOMETRY_NONFINITE_COORDINATE,
    GEOMETRY_NULL,
    GEOMETRY_OK,
    GEOMETRY_STATUSES,
    GEOMETRY_UNEXPECTED_KIND,
    SegmentGeometryPage,
    SegmentGeometryQueryResult,
    fetch_street_segment_geometries,
    parse_segment_geometry_page,
)

FIXTURE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "dcm_street_centerline"
)

CORRELATION_ID = "m4t020-test"

AUTHORITATIVE_SR = {"wkid": 102718, "latestWkid": 2263}

```

### T2 — lines 55–161

```python

def _fixture_body(name: str) -> str:
    with open(os.path.join(FIXTURE_DIR, name), encoding="utf-8") as f:
        return f.read()


def _attributes(object_id: int = 1, streetwidth: str = "60") -> dict:
    return {
        "OBJECTID": object_id,
        "Borough": "Manhattan",
        "Feat_Type": "Mapped_St",
        "Feat_status": "City_St",
        "Street_NM": "West 100 Street",
        "HonoraryNM": "None",
        "Old_ST_NM": "None",
        "Streetwidth": streetwidth,
        "Route_Type": "Gen_use",
        "RoadwayType": "Surface_ST",
        "Build_Status": "Improved",
        "Record_ST": "N",
        "Paper_ST": "N",
        "Stair_ST": "N",
        "CCO_ST": "N",
        "Marg_Wharf": "N",
        "Edit_Date": None,
    }


def _feature(
    object_id: int = 1,
    *,
    paths: list | None = None,
    geometry: object = "default",
    include_geometry: bool = True,
) -> dict:
    """One documented query-page feature. ``geometry='default'`` builds a
    paths geometry from ``paths``; pass ``geometry=...`` explicitly (or
    ``include_geometry=False``) to exercise the taxonomy."""
    feature: dict = {"attributes": _attributes(object_id)}
    if not include_geometry:
        return feature
    if geometry == "default":
        feature["geometry"] = {
            "paths": paths if paths is not None else [[[1.0, 2.0], [3.0, 4.0]]]
        }
    else:
        feature["geometry"] = geometry
    return feature


def _page_body(
    features: list[dict],
    *,
    spatial_reference: object = "authoritative",
    include_spatial_reference: bool = True,
    geometry_type: object = EXPECTED_PAGE_GEOMETRY_TYPE,
    include_geometry_type: bool = True,
    exceeded: bool | None = None,
) -> str:
    doc: dict = {
        "objectIdFieldName": "OBJECTID",
        "geometryProperties": {"shapeLengthFieldName": "Shape__Length", "units": "esriFeet"},
        "features": features,
    }
    if include_geometry_type:
        doc["geometryType"] = geometry_type
    if include_spatial_reference:
        doc["spatialReference"] = (
            dict(AUTHORITATIVE_SR)
            if spatial_reference == "authoritative"
            else spatial_reference
        )
    if exceeded is not None:
        doc["exceededTransferLimit"] = exceeded
    return json.dumps(doc)


def _transport(body: str, *, status: int = 200) -> DcmTransport:
    return DcmTransport(
        url="https://example.invalid/recorded-page",
        status=status,
        body=body,
        retrieved_at="2026-09-14T00:00:00Z",
    )


def _parse(body: str, *, status: int = 200) -> SegmentGeometryPage:
    return parse_segment_geometry_page(
        _transport(body, status=status), correlation_id=CORRELATION_ID
    )


def _counting_fetcher(bodies: list[str]):
    """Serve raw bodies in sequence and count calls (proves the paged flow
    performs exactly one transport per page and never a second fetch)."""
    calls: list[str] = []

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        index = len(calls)
        calls.append(url)
        return DcmTransport(
            url=url, status=200, body=bodies[index], retrieved_at="2026-09-14T00:00:00Z"
        )

    return _fetch, calls


```

### T3 — lines 162–226

```python
# ---------------------------------------------------------------------------
# S1: wire-format parse and typing (real recorded fixture + multi-path)
# ---------------------------------------------------------------------------


def test_recorded_fixture_page_parses_typed_multipath_polylines() -> None:
    body = _fixture_body("west_100_st_two_segments.json")
    page = _parse(body)
    assert isinstance(page, SegmentGeometryPage)
    assert page.features_total == 2
    assert [entry.status for entry in page.entries] == [GEOMETRY_OK, GEOMETRY_OK]
    by_id = {entry.object_id: entry for entry in page.entries}

    # Multi-path segments preserved as distinct paths in wire order.
    assert by_id[7719].path_count == 3
    assert by_id[14471].path_count == 3
    assert by_id[7719].vertex_count == 6
    assert by_id[14471].vertex_count == 12

    # Typed polylines: tuples of finite (x, y) float pairs.
    assert by_id[7719].paths is not None
    first_vertex = by_id[7719].paths[0][0]
    assert isinstance(by_id[7719].paths, tuple)
    assert isinstance(by_id[7719].paths[0], tuple)
    assert isinstance(first_vertex, tuple)
    assert all(isinstance(component, float) for component in first_vertex)
    assert first_vertex == (992185.54514055, 229943.965358555)


def test_entries_pair_geometry_with_attributes_from_the_same_page_body() -> None:
    page = _parse(_fixture_body("west_100_st_two_segments.json"))
    by_id = {entry.object_id: entry for entry in page.entries}
    assert by_id[7719].segment.streetwidth_raw == "60"
    assert by_id[14471].segment.streetwidth_raw == "100"
    assert by_id[7719].segment.street_name == "West 100 Street"
    assert by_id[7719].feature_index == 0
    assert by_id[14471].feature_index == 1


def test_paths_match_the_wire_json_exactly_no_rounding() -> None:
    body = _fixture_body("west_100_st_two_segments.json")
    page = _parse(body)
    raw_features = json.loads(body)["features"]
    for entry, raw_feature in zip(page.entries, raw_features, strict=True):
        raw_paths = tuple(
            tuple((float(x), float(y)) for x, y, *_ in path)
            for path in raw_feature["geometry"]["paths"]
        )
        assert entry.paths == raw_paths


def test_exceeded_transfer_limit_flag_passes_through() -> None:
    page = _parse(_page_body([_feature(1)], exceeded=True))
    assert page.exceeded_transfer_limit is True
    page = _parse(_page_body([_feature(1)]))
    assert page.exceeded_transfer_limit is False


def test_empty_features_page_is_a_normal_empty_result() -> None:
    page = _parse(_page_body([]))
    assert page.entries == []
    assert page.features_total == 0
    assert page.usable_geometry_count == 0


```

### T4 — lines 227–282

```python
# ---------------------------------------------------------------------------
# S1 (reuse fidelity): the accepted transport is reused by import; no
# duplicated HTTP/query building exists in the geometry module
# ---------------------------------------------------------------------------


def test_module_reuses_the_accepted_transport_surfaces_by_import() -> None:
    assert geometry_module.default_fetch is default_fetch
    assert geometry_module.SOURCE_ID == SOURCE_ID
    with open(geometry_module.__file__, encoding="utf-8") as f:
        source = f.read()
    # No transport re-implementation and no reprojection/conversion library:
    # the module's ONLY imports are the stdlib parse/typing helpers and the
    # accepted transport module (read-only reuse).
    imported_modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
    assert imported_modules == {
        "__future__",
        "json",
        "collections.abc",
        "dataclasses",
        "math",
        "app.connectors.dcm_street_centerline_arcgis",
    }
    # No URL building against the service and no unit-conversion constant
    # (tokens that cannot occur as prose in the module's documentation).
    for forbidden in (
        "urllib",
        "FeatureServer",
        "outSR",
        "http://",
        "https://",
        "pyproj",
        "to_crs",
        "0.3048",
        "3.2808",
    ):
        assert forbidden not in source, forbidden


def test_reused_validation_surfaces_type_transport_failures() -> None:
    # Non-200 status: typed by the accepted parse_segment_page (reused).
    with pytest.raises(UpstreamError):
        _parse(_page_body([_feature(1)]), status=502)
    # ArcGIS error object with HTTP 200: upstream error, never data.
    with pytest.raises(UpstreamError):
        _parse(json.dumps({"error": {"code": 400, "message": "bad"}}))
    # Missing features array: malformed, never a valid empty result.
    with pytest.raises(MalformedResponseError):
        _parse(json.dumps({"spatialReference": AUTHORITATIVE_SR}))


```

### T5 — lines 283–333

```python
# ---------------------------------------------------------------------------
# S2: CRS fail-closed (only wkid 102718 / latestWkid 2263 is accepted)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "spatial_reference,include",
    [
        pytest.param(None, False, id="spatialReference_key_absent"),
        pytest.param(None, True, id="spatialReference_json_null"),
        pytest.param({}, True, id="wkid_absent"),
        pytest.param({"wkid": 4326, "latestWkid": 4326}, True, id="wrong_wkid_wgs84"),
        pytest.param({"wkid": 2263, "latestWkid": 2263}, True, id="wkid_2263_not_102718"),
        pytest.param({"wkid": 102718}, True, id="latestWkid_absent"),
        pytest.param({"wkid": 102718, "latestWkid": 9999}, True, id="wrong_latestWkid"),
        pytest.param("EPSG:2263", True, id="spatialReference_not_an_object"),
    ],
)
def test_crs_fail_closed_rejects_everything_but_the_authoritative_pair(
    spatial_reference: object, include: bool
) -> None:
    body = _page_body(
        [_feature(1)],
        spatial_reference=spatial_reference,
        include_spatial_reference=include,
    )
    with pytest.raises(WrongCRSError) as excinfo:
        _parse(body)
    message = str(excinfo.value)
    # The typed error names expected vs received.
    assert "102718" in message
    assert "2263" in message
    assert excinfo.value.error_type == "wrong_crs"
    assert excinfo.value.detail["expected"] == {"wkid": 102718, "latestWkid": 2263}
    assert "received" in excinfo.value.detail


def test_crs_gate_runs_before_the_geometry_type_check() -> None:
    body = _page_body([_feature(1)], include_spatial_reference=False, include_geometry_type=False)
    with pytest.raises(WrongCRSError):
        _parse(body)


def test_non_polyline_page_geometry_type_is_typed_schema_drift() -> None:
    with pytest.raises(SchemaDriftError) as excinfo:
        _parse(_page_body([_feature(1)], geometry_type="esriGeometryPolygon"))
    assert "esriGeometryPolyline" in str(excinfo.value)
    with pytest.raises(SchemaDriftError):
        _parse(_page_body([_feature(1)], include_geometry_type=False))


```

### T6 — lines 334–437

```python
# ---------------------------------------------------------------------------
# S3: malformed-geometry taxonomy (typed, visible, never a silent drop)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "feature,expected_status,expected_finding_fragment",
    [
        pytest.param(
            _feature(1, include_geometry=False),
            GEOMETRY_NULL,
            "geometry_key_missing",
            id="geometry_key_missing",
        ),
        pytest.param(
            _feature(1, geometry=None), GEOMETRY_NULL, "geometry_json_null", id="geometry_null"
        ),
        pytest.param(
            _feature(1, geometry=[[1.0, 2.0]]),
            GEOMETRY_MALFORMED_OBJECT,
            "geometry_not_an_object",
            id="geometry_not_a_dict",
        ),
        pytest.param(
            _feature(1, geometry={}),
            GEOMETRY_MALFORMED_OBJECT,
            "paths_key_missing",
            id="paths_key_missing",
        ),
        pytest.param(
            _feature(1, geometry={"rings": [[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]]}),
            GEOMETRY_UNEXPECTED_KIND,
            "non_polyline_geometry_keys:rings",
            id="polygon_payload_on_polyline_layer",
        ),
        pytest.param(
            _feature(1, geometry={"paths": "not-a-list"}),
            GEOMETRY_MALFORMED_OBJECT,
            "paths_not_a_list",
            id="paths_not_a_list",
        ),
        pytest.param(
            _feature(1, geometry={"paths": []}),
            GEOMETRY_EMPTY_PATHS,
            "paths_empty",
            id="empty_paths",
        ),
        pytest.param(
            _feature(1, paths=[[[1.0, 2.0]]]),
            GEOMETRY_DEGENERATE_PATH,
            "path_0_has_1_point",
            id="single_point_path",
        ),
        pytest.param(
            _feature(1, paths=[[["abc", 2.0], [3.0, 4.0]]]),
            GEOMETRY_MALFORMED_COORDINATE,
            "path_0_vertex_0_x_non_numeric:str",
            id="non_numeric_x",
        ),
        pytest.param(
            _feature(1, paths=[[[1.0, True], [3.0, 4.0]]]),
            GEOMETRY_MALFORMED_COORDINATE,
            "path_0_vertex_0_y_non_numeric:bool",
            id="boolean_y_is_not_numeric",
        ),
        pytest.param(
            _feature(1, paths=[[[1.0], [3.0, 4.0]]]),
            GEOMETRY_MALFORMED_COORDINATE,
            "path_0_vertex_0_is_not_an_xy_pair",
            id="vertex_missing_y",
        ),
        pytest.param(
            _feature(1, paths=[[[float("nan"), 2.0], [3.0, 4.0]]]),
            GEOMETRY_NONFINITE_COORDINATE,
            "path_0_vertex_0_nonfinite",
            id="nan_coordinate",
        ),
        pytest.param(
            _feature(1, paths=[[[1.0, 2.0], [float("inf"), 4.0]]]),
            GEOMETRY_NONFINITE_COORDINATE,
            "path_0_vertex_1_nonfinite",
            id="infinity_coordinate",
        ),
    ],
)
def test_each_malformed_geometry_condition_is_a_distinct_typed_state(
    feature: dict, expected_status: str, expected_finding_fragment: str
) -> None:
    page = _parse(_page_body([feature]))
    assert page.features_total == 1  # visible, never dropped
    entry = page.entries[0]
    assert entry.status == expected_status
    assert entry.status in GEOMETRY_STATUSES
    assert any(expected_finding_fragment in finding for finding in entry.findings)
    assert entry.paths is None
    assert entry.path_count == 0 and entry.vertex_count == 0
    assert entry.has_usable_geometry is False
    # Identity/attributes stay paired even when the geometry is refused.
    assert entry.object_id == 1
    assert entry.segment.streetwidth_raw == "60"
    assert page.usable_geometry_count == 0
    assert page.refused_geometry_count == 1


```

### T7 — lines 438–475

```python
def test_a_bad_feature_never_hides_or_drops_its_page_neighbors() -> None:
    page = _parse(
        _page_body(
            [
                _feature(1, paths=[[[1.0, 2.0], [3.0, 4.0]]]),
                _feature(2, geometry=None),
                _feature(3, paths=[[[5.0, 6.0], [7.0, 8.0]]]),
            ]
        )
    )
    assert [entry.object_id for entry in page.entries] == [1, 2, 3]
    assert [entry.status for entry in page.entries] == [
        GEOMETRY_OK,
        GEOMETRY_NULL,
        GEOMETRY_OK,
    ]
    assert page.usable_geometry_count == 2
    assert page.refused_geometry_count == 1


def test_no_partial_polyline_repair_one_bad_path_refuses_the_whole_geometry() -> None:
    page = _parse(
        _page_body([_feature(1, paths=[[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0]]])])
    )
    entry = page.entries[0]
    assert entry.status == GEOMETRY_DEGENERATE_PATH
    assert entry.paths is None  # the intact first path is NOT salvaged
    assert any("path_1_has_1_point" in finding for finding in entry.findings)


def test_extra_vertex_components_are_visible_not_silently_discarded() -> None:
    page = _parse(_page_body([_feature(1, paths=[[[1.0, 2.0, 99.5], [3.0, 4.0]]])]))
    entry = page.entries[0]
    assert entry.status == GEOMETRY_OK
    assert entry.paths == (((1.0, 2.0), (3.0, 4.0)),)
    assert any("path_0_vertex_0_extra_components:1" in f for f in entry.findings)


```

### T8 — lines 476–514

```python
# ---------------------------------------------------------------------------
# S4: passthrough integrity and provenance schema
# ---------------------------------------------------------------------------


def test_high_precision_and_integer_wire_values_pass_through_untouched() -> None:
    page = _parse(
        _page_body(
            [
                _feature(
                    1,
                    paths=[[[992185.54514055, 229943.965358555], [1000, -0.000001]]],
                )
            ]
        )
    )
    paths = page.entries[0].paths
    assert paths is not None
    assert paths[0][0] == (992185.54514055, 229943.965358555)
    assert paths[0][1] == (1000.0, -0.000001)


def test_page_provenance_carries_retrieval_identity_and_digest() -> None:
    body = _fixture_body("west_100_st_two_segments.json")
    page = _parse(body)
    assert page.raw_digest == raw_body_digest(body)
    assert page.request_url == "https://example.invalid/recorded-page"
    assert page.retrieved_at == "2026-09-14T00:00:00Z"
    assert page.correlation_id == CORRELATION_ID
    assert page.source_id == SOURCE_ID
    assert page.layer == "DCM_Street_Center_Line"
    assert page.attribution == ATTRIBUTION
    assert page.crs == CRS_STAMP
    assert page.wkid == 102718 and page.latest_wkid == 2263
    assert page.geometry_type == EXPECTED_PAGE_GEOMETRY_TYPE
    assert page.units == "esriFeet"
    assert page.contract_version == "1.0.0"


```

### T9 — lines 515–576

```python
# ---------------------------------------------------------------------------
# Paged entry point: single fetch per page, provenance passthrough
# ---------------------------------------------------------------------------


def test_paged_fetch_transports_each_page_exactly_once() -> None:
    metadata_body = _fixture_body("metadata.json")
    page_body = _fixture_body("west_100_st_two_segments.json")
    fetch, calls = _counting_fetcher([metadata_body, page_body])
    result = fetch_street_segment_geometries(
        borough="Manhattan", street_name="West 100 Street", fetch=fetch
    )
    assert isinstance(result, SegmentGeometryQueryResult)
    # Exactly one metadata call + one page call: no second fetch per page.
    assert len(calls) == 2
    assert calls[0] == build_metadata_url()
    assert result.pages_fetched == 1
    assert len(result.entries) == 2
    assert {entry.object_id for entry in result.entries} == {7719, 14471}
    assert all(entry.status == GEOMETRY_OK for entry in result.entries)


def test_paged_fetch_carries_transport_provenance_through() -> None:
    metadata_body = _fixture_body("metadata.json")
    page_body = _fixture_body("west_100_st_two_segments.json")
    fetch, calls = _counting_fetcher([metadata_body, page_body])
    result = fetch_street_segment_geometries(
        borough="Manhattan", street_name="West 100 Street", fetch=fetch
    )
    assert result.source_data_last_edited_ms == 1764617995374
    assert result.source_data_last_edited == "2025-12-01T19:39:55Z"
    assert result.metadata_request_url == build_metadata_url()
    assert result.raw_digests == [raw_body_digest(page_body)]
    assert result.page_urls == [calls[1]]
    assert result.drift_signals == []
    assert result.crs == CRS_STAMP
    assert result.source_id == SOURCE_ID
    assert len(result.pages) == 1
    assert result.pages[0].raw_digest == raw_body_digest(page_body)
    assert result.pages[0].correlation_id == result.correlation_id
    assert result.exceeded_transfer_limit_on_last_page is False


def test_paged_fetch_walks_multiple_pages_one_transport_each() -> None:
    metadata_body = _fixture_body("metadata.json")
    page_one = _page_body([_feature(1)], exceeded=True)
    page_two = _page_body([_feature(2)])
    fetch, calls = _counting_fetcher([metadata_body, page_one, page_two])
    result = fetch_street_segment_geometries(object_id_in=[1, 2], fetch=fetch)
    assert len(calls) == 3  # metadata + two pages, each transported once
    assert result.pages_fetched == 2
    assert [entry.object_id for entry in result.entries] == [1, 2]
    assert [page.exceeded_transfer_limit for page in result.pages] == [True, False]
    assert result.raw_digests == [raw_body_digest(page_one), raw_body_digest(page_two)]


def test_paged_fetch_fails_closed_when_a_page_carries_the_wrong_crs() -> None:
    metadata_body = _fixture_body("metadata.json")
    bad_page = _page_body([_feature(1)], spatial_reference={"wkid": 3857, "latestWkid": 3857})
    fetch, _ = _counting_fetcher([metadata_body, bad_page])
    with pytest.raises(WrongCRSError):
        fetch_street_segment_geometries(object_id=1, fetch=fetch)
```
