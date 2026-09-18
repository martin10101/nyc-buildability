"""Fully offline tests for the DCM Street Center Line connector (task
M4-T015), driven entirely by the recorded fixtures in
``services/api/tests/fixtures/dcm_street_centerline/`` via an injected
fetch seam. No network access occurs in this suite."""

from __future__ import annotations

import json
import os
import sys
import urllib.parse

import pytest

from app.connectors.dcm_street_centerline_arcgis import (
    CRS_STAMP,
    ENVELOPE_ABS_MAX_FT,
    ENVELOPE_SPATIAL_REL,
    EXPECTED_LATEST_WKID,
    EXPECTED_WKID,
    MAX_OBJECT_ID_LIST,
    SOURCE_ID,
    DcmTransport,
    DisallowedRequestError,
    LayerMetadata,
    MalformedResponseError,
    PagingPathologyError,
    SchemaDriftError,
    UpstreamError,
    WrongCRSError,
    build_metadata_url,
    build_segment_query_url,
    fetch_layer_metadata,
    fetch_street_segments,
    parse_segment_page,
    raw_body_digest,
)
from app.connectors.dcm_street_width_classifier import (
    DISPOSITION_NARROW_FAIL_CLOSED,
    DISPOSITION_WIDE,
)

FIXTURE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "dcm_street_centerline"
)


def _load_manifest() -> dict:
    with open(os.path.join(FIXTURE_DIR, "MANIFEST.json"), encoding="utf-8") as f:
        return json.load(f)


def _fixture_body(name: str) -> str:
    path = os.path.join(FIXTURE_DIR, name)
    with open(path, encoding="utf-8") as f:
        return f.read()


def _fetcher(fixture_name: str, *, status: int = 200):
    """Build a fetch(url, correlation_id) -> DcmTransport seam serving one
    fixture regardless of the URL requested (single-call tests)."""
    body = _fixture_body(fixture_name)

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        return DcmTransport(url=url, status=status, body=body, retrieved_at="2026-09-13T00:00:00Z")

    return _fetch


def _sequenced_fetcher(fixture_names: list[str]):
    """Build a fetch seam that serves fixtures in sequence, one per call
    (used for paged extractions: metadata first, then each page)."""
    return _bodies_fetcher([_fixture_body(name) for name in fixture_names])


def _bodies_fetcher(bodies: list[str]):
    """Build a fetch seam that serves raw body strings in sequence, one per
    call. Used when a test needs to mutate a loaded fixture in memory before
    serving it (e.g. forcing exceededTransferLimit or injecting a schema
    drift) rather than serving fixture files verbatim."""
    calls = {"i": 0}

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        i = calls["i"]
        calls["i"] += 1
        return DcmTransport(
            url=url, status=200, body=bodies[i], retrieved_at="2026-09-13T00:00:00Z"
        )

    return _fetch


def _first_segment(result):
    assert len(result.segments) >= 1
    return result.segments[0]


# ---------------------------------------------------------------------------
# Manifest self-consistency (every referenced fixture exists and hashes match)
# ---------------------------------------------------------------------------


def test_manifest_matches_fixture_bytes_on_disk() -> None:
    import hashlib

    manifest = _load_manifest()
    on_disk = {f for f in os.listdir(FIXTURE_DIR) if f != "MANIFEST.json"}
    in_manifest = {entry["file"] for entry in manifest["fixtures"]}
    assert on_disk == in_manifest
    for entry in manifest["fixtures"]:
        with open(os.path.join(FIXTURE_DIR, entry["file"]), "rb") as f:
            data = f.read()
        assert "sha256:" + hashlib.sha256(data).hexdigest() == entry["sha256"]
        assert len(data) == entry["bytes"]


# ---------------------------------------------------------------------------
# S1: authoritative source and provenance
# ---------------------------------------------------------------------------


def test_build_metadata_url_targets_the_researched_endpoint() -> None:
    url = build_metadata_url()
    assert url == (
        "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/"
        "DCM_Street_Center_Line/FeatureServer/0?f=json"
    )


def test_build_segment_query_url_uses_outsr_2263_and_bounded_fields() -> None:
    url = build_segment_query_url(borough="Manhattan", street_name="West 100 Street")
    assert "outSR=2263" in url
    assert "f=json" in url
    assert "outFields=" in url and "outFields=*" not in url
    assert "orderByFields=OBJECTID" in url
    assert url.startswith(
        "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/"
        "DCM_Street_Center_Line/FeatureServer/0/query"
    )
    where_encoded = urllib.parse.quote(
        "Borough='Manhattan' AND Street_NM='West 100 Street'", safe=""
    )
    assert f"where={where_encoded}" in url


def test_fetch_layer_metadata_validates_crs_and_pins_freshness() -> None:
    metadata = fetch_layer_metadata(fetch=_fetcher("metadata.json"))
    assert isinstance(metadata, LayerMetadata)
    assert metadata.wkid == EXPECTED_WKID == 102718
    assert metadata.latest_wkid == EXPECTED_LATEST_WKID == 2263
    assert metadata.max_record_count == 2000
    assert metadata.object_id_field == "OBJECTID"
    # dataLastEditDate 1764617995374 ms == 2025-12-01T19:39:55Z (research E5)
    assert metadata.source_data_last_edited_ms == 1764617995374
    assert metadata.source_data_last_edited == "2025-12-01T19:39:55Z"
    assert metadata.drift_signals == []
    assert CRS_STAMP["wkid"] == 102718


def test_west_100_st_two_segment_case_preserves_raw_text_verbatim() -> None:
    result = fetch_street_segments(
        borough="Manhattan",
        street_name="West 100 Street",
        fetch=_sequenced_fetcher(["metadata.json", "west_100_st_two_segments.json"]),
    )
    assert len(result.segments) == 2
    by_id = {seg.object_id: seg for seg in result.segments}
    assert by_id[7719].streetwidth_raw == "60"
    assert by_id[14471].streetwidth_raw == "100"
    assert by_id[7719].effective_disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert by_id[14471].effective_disposition == DISPOSITION_WIDE
    assert result.source_id == SOURCE_ID
    assert result.source_data_last_edited == "2025-12-01T19:39:55Z"


def test_clean_wide_segment_has_no_override_and_no_review() -> None:
    result = fetch_street_segments(
        object_id=7,
        fetch=_sequenced_fetcher(["metadata.json", "wide_clean_numeric_80.json"]),
    )
    segment = _first_segment(result)
    assert segment.streetwidth_raw == "80"
    assert segment.width_classification.disposition == DISPOSITION_WIDE
    assert segment.effective_disposition == DISPOSITION_WIDE
    assert segment.effective_review_required is False
    assert segment.override_reason is None
    assert segment.is_mapped_street is True


# ---------------------------------------------------------------------------
# S2: fail-closed width classification (spot-checks; exhaustive class
# coverage lives in test_dcm_street_width_classifier.py)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture,expected_class,expected_disposition",
    [
        ("width_irregular.json", "width_irregular", DISPOSITION_NARROW_FAIL_CLOSED),
        ("unknown_no_qualifier.json", "unknown_no_qualifier", DISPOSITION_NARROW_FAIL_CLOSED),
        ("varies_plain.json", "varies", DISPOSITION_NARROW_FAIL_CLOSED),
        ("gt_inequality_ge_75_wide.json", "gt_inequality_ge_75", DISPOSITION_WIDE),
        (
            "lt_inequality_le_75_narrow.json",
            "lt_inequality_at_or_below_75_confident_narrow",
            DISPOSITION_NARROW_FAIL_CLOSED,
        ),
        (
            "range_straddles_cutoff_60_75.json",
            "range_straddles_cutoff",
            DISPOSITION_NARROW_FAIL_CLOSED,
        ),
        ("range_both_ge_75_wide_75_90.json", "range_both_endpoints_ge_75", DISPOSITION_WIDE),
        (
            "range_both_lt_75_narrow_50_60.json",
            "range_both_endpoints_lt_75",
            DISPOSITION_NARROW_FAIL_CLOSED,
        ),
        (
            "range_straddles_cutoff_74_75_3.json",
            "range_straddles_cutoff",
            DISPOSITION_NARROW_FAIL_CLOSED,
        ),
        (
            "approximate_tilde_60.json",
            "approximate_or_hedged_value_ambiguous",
            DISPOSITION_NARROW_FAIL_CLOSED,
        ),
        ("unknown_hedged_below_75.json", "unknown_hedged_below_75", DISPOSITION_NARROW_FAIL_CLOSED),
        ("unknown_hedged_above_75.json", "unknown_hedged_above_75", DISPOSITION_NARROW_FAIL_CLOSED),
        (
            "approximate_prose_probably.json",
            "approximate_or_hedged_value_ambiguous",
            DISPOSITION_NARROW_FAIL_CLOSED,
        ),
        ("regular_but_unknown.json", "regular_but_unknown", DISPOSITION_NARROW_FAIL_CLOSED),
        ("not_applicable_n_a_unmapped.json", "not_applicable_n_a", DISPOSITION_NARROW_FAIL_CLOSED),
    ],
)
def test_live_ambiguity_class_fixtures_classify_as_researched(
    fixture: str, expected_class: str, expected_disposition: str
) -> None:
    result = fetch_street_segments(
        object_id=1,  # irrelevant: the fixture body determines the returned feature(s)
        fetch=_sequenced_fetcher(["metadata.json", fixture]),
    )
    segment = _first_segment(result)
    assert segment.width_classification.ambiguity_class == expected_class
    assert segment.width_classification.disposition == expected_disposition


# ---------------------------------------------------------------------------
# S3: mapped-street status honesty and the never-wide override
# ---------------------------------------------------------------------------


def test_unmapped_street_never_classifies_wide_via_n_a_fixture() -> None:
    result = fetch_street_segments(
        object_id=523,
        fetch=_sequenced_fetcher(["metadata.json", "not_applicable_n_a_unmapped.json"]),
    )
    segment = _first_segment(result)
    assert segment.feat_type == "Not_mapped"
    assert segment.is_mapped_street is False
    assert segment.effective_disposition == DISPOSITION_NARROW_FAIL_CLOSED


@pytest.mark.parametrize(
    "fixture,expected_reason_fragment",
    [
        ("paper_street_override_wide.json", "Paper_ST"),
        ("record_street_override_wide.json", "Record_ST"),
        ("former_street_override_wide.json", "Feat_Type="),
        ("unmapped_street_override_wide.json", "Feat_Type="),
    ],
)
def test_mapped_street_override_never_grants_wide_on_wide_looking_text(
    fixture: str, expected_reason_fragment: str
) -> None:
    result = fetch_street_segments(
        object_id=1,
        fetch=_sequenced_fetcher(["metadata.json", fixture]),
    )
    segment = _first_segment(result)
    # The RAW classifier read is preserved untouched and would be wide...
    assert segment.width_classification.disposition == DISPOSITION_WIDE
    # ...but the effective (connector-level) disposition is overridden narrow.
    assert segment.effective_disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert segment.effective_review_required is True
    assert segment.override_reason is not None
    assert expected_reason_fragment in segment.override_reason
    assert segment.is_mapped_street is False


def test_varies_with_paper_override_combines_both_ambiguities() -> None:
    result = fetch_street_segments(
        object_id=18356,
        fetch=_sequenced_fetcher(["metadata.json", "varies_paper_override.json"]),
    )
    segment = _first_segment(result)
    assert segment.width_classification.ambiguity_class == "varies"
    assert segment.paper_street == "Y"
    # Already-narrow text: the override changes nothing (no override_reason)
    # because there was nothing wide to suppress.
    assert segment.effective_disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert segment.override_reason is None


def test_feat_status_is_typed_passthrough_never_used_for_override() -> None:
    """OQ-2: Feat_status has no documented domain and must never drive the
    mapped-street override. The live 'Sharrott Avenue' segment shows
    Feat_status='Way_on_record' co-occurring with Record_ST='N' on the SAME
    feature - proof the two are independent."""
    result = fetch_street_segments(
        object_id=20420,
        fetch=_sequenced_fetcher(["metadata.json", "unmapped_street_override_wide.json"]),
    )
    segment = _first_segment(result)
    assert segment.feat_status == "Way_on_record"
    assert segment.record_street == "N"
    assert segment.paper_street == "N"
    # The override still fires because Feat_Type='Not_mapped', NOT because of
    # Feat_status or the Record_ST/Paper_ST flags.
    assert segment.feat_type == "Not_mapped"
    assert segment.effective_disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert "Feat_Type=" in segment.override_reason


def test_unrecognized_feat_type_is_schema_drift_never_wide() -> None:
    body = _fixture_body("wide_clean_numeric_80.json")
    doc = json.loads(body)
    doc["features"][0]["attributes"]["Feat_Type"] = "Some_New_Value"
    mutated = json.dumps(doc)

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        is_metadata_url = "?f=json" in url and "query" not in url
        source = _fixture_body("metadata.json") if is_metadata_url else mutated
        return DcmTransport(
            url=url, status=200, body=source, retrieved_at="2026-09-13T00:00:00Z"
        )

    result = fetch_street_segments(object_id=7, fetch=_fetch)
    segment = _first_segment(result)
    assert segment.feat_type_recognized is False
    assert segment.effective_disposition == DISPOSITION_NARROW_FAIL_CLOSED
    assert segment.effective_review_required is True
    assert "not in the documented domain" in segment.override_reason


# ---------------------------------------------------------------------------
# S5: upstream error / paging honesty
# ---------------------------------------------------------------------------


def test_http_200_arcgis_error_object_is_typed_upstream_error() -> None:
    with pytest.raises(UpstreamError) as excinfo:
        fetch_street_segments(
            object_id=1,
            fetch=_sequenced_fetcher(["metadata.json", "provider_error_http200_synthetic.json"]),
        )
    assert excinfo.value.error_type == "upstream_error"
    assert excinfo.value.detail["arcgis_error_code"] == 400


def test_paging_walks_two_pages_and_merges_disjoint_segments() -> None:
    # The two live-captured pages both truthfully report exceededTransferLimit
    # (the live predicate has more than 10 total matches beyond this thin-
    # client demo's 2-page window). To exercise a COMPLETE, terminating
    # paged extraction offline, page 2's flag is set False here - the same
    # mutate-a-real-fixture technique used elsewhere in this suite (e.g.
    # test_wrong_crs_is_typed_before_any_coordinate_use) - so this test
    # proves the offset/merge/termination logic without needing to capture
    # every remaining live page (thin client).
    page2 = json.loads(_fixture_body("paging_page2.json"))
    page2["exceededTransferLimit"] = False
    result = fetch_street_segments(
        borough="Manhattan",  # predicate value irrelevant; fixtures drive the response
        page_size=5,
        fetch=_bodies_fetcher(
            [_fixture_body("metadata.json"), _fixture_body("paging_page1.json"), json.dumps(page2)]
        ),
    )
    assert result.pages_fetched == 2
    object_ids = [seg.object_id for seg in result.segments]
    assert len(object_ids) == len(set(object_ids)) == 10
    assert object_ids == sorted(object_ids)
    assert result.exceeded_transfer_limit_on_last_page is False


def test_duplicate_page_is_a_typed_paging_pathology() -> None:
    with pytest.raises(PagingPathologyError) as excinfo:
        fetch_street_segments(
            borough="Manhattan",
            page_size=5,
            fetch=_sequenced_fetcher(
                ["metadata.json", "paging_page1.json", "paging_page1.json"]
            ),
        )
    assert excinfo.value.detail["reason"] == "duplicate_page"


def test_repeated_object_ids_across_pages_is_a_typed_paging_pathology() -> None:
    page1 = json.loads(_fixture_body("paging_page1.json"))
    page2 = json.loads(_fixture_body("paging_page2.json"))
    # A PARTIAL overlap (one feature from page 1 re-appears, mixed with new
    # page-2 features in a different order/set) is a distinct pathology from
    # an exact repeated page: the OBJECTID sequence differs from page 1's,
    # so the byte/sequence "duplicate_page" guard does NOT fire, but the
    # OVERLAP guard ("repeated_object_ids") does.
    partial_overlap = dict(page2)
    partial_overlap["features"] = [page1["features"][0], *page2["features"][1:]]
    partial_overlap["exceededTransferLimit"] = False
    bodies = [_fixture_body("metadata.json"), json.dumps(page1), json.dumps(partial_overlap)]

    with pytest.raises(PagingPathologyError) as excinfo:
        fetch_street_segments(borough="Manhattan", page_size=5, fetch=_bodies_fetcher(bodies))
    assert excinfo.value.detail["reason"] == "repeated_object_ids"
    assert excinfo.value.detail["object_ids"] == [page1["features"][0]["attributes"]["OBJECTID"]]


def test_zero_progress_empty_page_with_exceeded_flag_is_typed_pathology() -> None:
    empty_but_exceeded = {
        "objectIdFieldName": "OBJECTID",
        "features": [],
        "exceededTransferLimit": True,
    }
    bodies = [_fixture_body("metadata.json"), json.dumps(empty_but_exceeded)]
    calls = {"i": 0}

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        i = calls["i"]
        calls["i"] += 1
        return DcmTransport(url=url, status=200, body=bodies[i], retrieved_at="x")

    with pytest.raises(PagingPathologyError) as excinfo:
        fetch_street_segments(borough="Manhattan", page_size=5, fetch=_fetch)
    assert excinfo.value.detail["reason"] == "zero_progress"


def test_network_failure_is_a_typed_upstream_error_no_retry() -> None:
    def _raising_fetch(url: str, correlation_id: str) -> DcmTransport:
        raise UpstreamError(
            "official DCM ArcGIS service was unreachable",
            correlation_id=correlation_id,
            detail={"url": url, "reason_kind": "URLError"},
        )

    with pytest.raises(UpstreamError):
        fetch_layer_metadata(fetch=_raising_fetch)


def test_malformed_response_is_never_a_valid_empty_result() -> None:
    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        return DcmTransport(url=url, status=200, body="not json", retrieved_at="x")

    with pytest.raises(MalformedResponseError):
        fetch_layer_metadata(fetch=_fetch)


def test_wrong_geometry_type_is_schema_drift() -> None:
    doc = json.loads(_fixture_body("metadata.json"))
    doc["geometryType"] = "esriGeometryPoint"

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        return DcmTransport(url=url, status=200, body=json.dumps(doc), retrieved_at="x")

    with pytest.raises(SchemaDriftError):
        fetch_layer_metadata(fetch=_fetch)


def test_wrong_crs_is_typed_before_any_coordinate_use() -> None:
    doc = json.loads(_fixture_body("metadata.json"))
    doc["spatialReference"] = {"wkid": 4326}

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        return DcmTransport(url=url, status=200, body=json.dumps(doc), retrieved_at="x")

    with pytest.raises(WrongCRSError):
        fetch_layer_metadata(fetch=_fetch)


def test_missing_editing_info_degrades_visibly_not_silently() -> None:
    doc = json.loads(_fixture_body("metadata.json"))
    del doc["editingInfo"]

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        return DcmTransport(url=url, status=200, body=json.dumps(doc), retrieved_at="x")

    metadata = fetch_layer_metadata(fetch=_fetch)
    assert metadata.source_data_last_edited_ms is None
    assert any("dataLastEditDate" in signal for signal in metadata.drift_signals)


# ---------------------------------------------------------------------------
# Injection-proof query builder (bounded predicates only)
# ---------------------------------------------------------------------------


def test_unknown_borough_is_disallowed_before_any_network_io() -> None:
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(borough="New Jersey")


def test_unsafe_street_name_is_disallowed() -> None:
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(street_name="Main St'; DROP TABLE segments; --")


def test_street_name_with_apostrophe_is_escaped_not_rejected() -> None:
    url = build_segment_query_url(street_name="O'Brien Street")
    assert "O''Brien" in url or "O%27%27Brien" in url


def test_multiple_predicate_styles_are_disallowed() -> None:
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(borough="Manhattan", object_id=1)


def test_no_predicate_is_disallowed() -> None:
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url()


def test_object_id_in_over_the_bound_is_disallowed() -> None:
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(object_id_in=list(range(1, MAX_OBJECT_ID_LIST + 2)))


def test_object_id_in_within_bound_builds_an_in_clause() -> None:
    url = build_segment_query_url(object_id_in=[1, 2, 3])
    assert "OBJECTID+IN+" in url or "OBJECTID%20IN%20" in url


def test_page_budget_exhaustion_is_a_typed_pathology() -> None:
    # Every page reports exceededTransferLimit and returns segments, so the
    # loop would run forever without the hard page-count ceiling.
    page = json.loads(_fixture_body("paging_page1.json"))

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        if "query" not in url:
            return DcmTransport(
                url=url, status=200, body=_fixture_body("metadata.json"), retrieved_at="x"
            )
        return DcmTransport(url=url, status=200, body=json.dumps(page), retrieved_at="x")

    with pytest.raises(PagingPathologyError) as excinfo:
        fetch_street_segments(borough="Manhattan", page_size=5, max_pages=1, fetch=_fetch)
    assert excinfo.value.detail["reason"] == "page_budget_exhausted"


def test_raw_body_digest_is_stable_sha256() -> None:
    body = "hello"
    digest = raw_body_digest(body)
    assert digest == (
        "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )


def test_parse_segment_page_rejects_non_200_status() -> None:
    with pytest.raises(UpstreamError):
        parse_segment_page(
            DcmTransport(url="x", status=500, body="{}", retrieved_at="x"),
            correlation_id="c1",
        )


# ---------------------------------------------------------------------------
# Envelope-intersects predicate (M5-T035 / DB-015). The envelope changes only
# the SELECTION; it preserves the exactly-one-predicate rule, the injection-proof
# URL builder, and (through fetch_street_segments) the metadata-first freshness
# pin, the CRS / schema-drift gates, and the paging-pathology guards. A
# malformed / non-finite / absurd envelope is refused BEFORE any network I/O.
# ---------------------------------------------------------------------------

# A plausible EPSG:2263 (US survey feet) envelope well inside the NYC projected
# domain; the exact coordinates are irrelevant to the offline fixtures (the
# injected fetch drives the response), they only exercise the URL builder.
_VALID_ENVELOPE = (980000.0, 190000.0, 981000.0, 191000.0)


def test_envelope_predicate_builds_an_intersects_spatial_query() -> None:
    url = build_segment_query_url(envelope=_VALID_ENVELOPE)
    # esriGeometryEnvelope intersects in the authoritative EPSG:2263 CRS.
    assert "geometryType=esriGeometryEnvelope" in url
    assert "inSR=2263" in url
    assert f"spatialRel={ENVELOPE_SPATIAL_REL}" in url
    # A spatial predicate still carries a constant-true WHERE (1=1, url-encoded).
    assert "where=1%3D1" in url
    # The bounded out-field set, deterministic order, and outSR are unchanged.
    assert "outFields=" in url and "outFields=*" not in url
    assert "orderByFields=OBJECTID" in url
    assert "outSR=2263" in url
    # The four coordinates are present (4-decimal formatted, comma-joined).
    assert "980000.0000" in url and "191000.0000" in url


def test_envelope_is_mutually_exclusive_with_attribute_predicates() -> None:
    # Exactly one predicate style per call: envelope XOR (borough/street_name)
    # XOR object_id XOR object_id_in.
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=_VALID_ENVELOPE, borough="Manhattan")
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=_VALID_ENVELOPE, object_id=7)
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=_VALID_ENVELOPE, object_id_in=[1, 2])


@pytest.mark.parametrize(
    "bad",
    [
        (1.0, 2.0, 3.0),  # wrong length
        (1.0, 2.0, 3.0, 4.0, 5.0),  # wrong length
        "980000,190000,981000,191000",  # not a sequence of numbers
    ],
)
def test_envelope_must_be_a_four_item_numeric_sequence(bad: object) -> None:
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=bad)  # type: ignore[arg-type]


@pytest.mark.parametrize("nonfinite", [float("inf"), float("-inf"), float("nan")])
def test_envelope_rejects_nonfinite_coordinates(nonfinite: float) -> None:
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=(nonfinite, 190000.0, 981000.0, 191000.0))


def test_envelope_rejects_absurd_magnitude() -> None:
    over = ENVELOPE_ABS_MAX_FT * 2
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=(over, 190000.0, over + 1000.0, 191000.0))
    # A huge int not representable as a finite float must fail closed too (the
    # OverflowError is mapped to disallowed_request, never leaked uncaught).
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=(0.0, 0.0, 10**400, 191000.0))


def test_envelope_rejects_inverted_bounds() -> None:
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=(981000.0, 190000.0, 980000.0, 191000.0))
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=(980000.0, 191000.0, 981000.0, 190000.0))


def test_envelope_rejects_boolean_component() -> None:
    # bool is a subclass of int; a True/False coordinate is not a real number.
    with pytest.raises(DisallowedRequestError):
        build_segment_query_url(envelope=(True, 190000.0, 981000.0, 191000.0))


def test_fetch_street_segments_refuses_bad_envelope_before_any_network_io() -> None:
    calls = {"n": 0}

    def _must_not_fetch(url: str, correlation_id: str) -> DcmTransport:
        calls["n"] += 1
        raise AssertionError("no network I/O may occur for a refused envelope")

    with pytest.raises(DisallowedRequestError):
        fetch_street_segments(
            envelope=(float("nan"), 190000.0, 981000.0, 191000.0),
            fetch=_must_not_fetch,
        )
    # The refusal happens in the URL builder BEFORE the metadata round-trip.
    assert calls["n"] == 0


def test_envelope_fetch_runs_metadata_first_and_returns_segments() -> None:
    result = fetch_street_segments(
        envelope=_VALID_ENVELOPE,
        fetch=_sequenced_fetcher(["metadata.json", "west_100_st_two_segments.json"]),
    )
    # Metadata-first discipline is preserved (provenance pin populated) and the
    # first page URL carries the envelope spatial predicate, not an attribute one.
    assert result.metadata_request_url == build_metadata_url()
    assert "geometryType=esriGeometryEnvelope" in result.page_urls[0]
    assert "Borough=" not in result.page_urls[0]
    assert len(result.segments) >= 1


def test_envelope_fetch_preserves_the_wrong_crs_gate() -> None:
    # A non-authoritative layer CRS is refused during the metadata fetch, before
    # any envelope coordinate is trusted - the envelope path does NOT bypass it.
    doc = json.loads(_fixture_body("metadata.json"))
    doc["spatialReference"] = {"wkid": 4326}
    with pytest.raises(WrongCRSError):
        fetch_street_segments(envelope=_VALID_ENVELOPE, fetch=_bodies_fetcher([json.dumps(doc)]))


def test_envelope_fetch_preserves_the_paging_pathology_guard() -> None:
    with pytest.raises(PagingPathologyError) as excinfo:
        fetch_street_segments(
            envelope=_VALID_ENVELOPE,
            page_size=5,
            fetch=_sequenced_fetcher(
                ["metadata.json", "paging_page1.json", "paging_page1.json"]
            ),
        )
    assert excinfo.value.detail["reason"] == "duplicate_page"


# ---------------------------------------------------------------------------
# Rejection-diagnostic robustness (M5-T035): a malformed envelope SHAPE or a
# predicate CONFLICT that carries a huge integer must still refuse with the typed
# DisallowedRequestError and NEVER raise an uncaught ValueError while building the
# refusal's detail. Python 3.11+ caps int<->str conversion
# (sys.get_int_max_str_digits, default 4300 digits), so repr() of an oversized
# integer - or of a container that holds one - raises; the connector's diagnostics
# now use a bounded _safe_repr so the refusal itself can never fail during
# repr/string conversion. If the fix regressed, an uncaught ValueError would
# escape and pytest.raises(DisallowedRequestError) below would NOT catch it.
# ---------------------------------------------------------------------------

# An integer whose decimal repr exceeds the interpreter's int->str conversion cap,
# so repr()/str() of it (or of a tuple containing it) raises ValueError unless
# guarded. Built by arithmetic (int arithmetic is not capped; only str conversion
# is), sized above the live cap so this holds regardless of the configured limit.
_HUGE_INT = 10 ** (sys.get_int_max_str_digits() + 100)


def test_envelope_wrong_length_with_huge_int_is_disallowed_not_valueerror() -> None:
    # A malformed SHAPE (3-item) whose sole element is a huge int: the refusal
    # must be the typed DisallowedRequestError, and its detail must be bounded
    # (never the raw, unrepresentable value).
    with pytest.raises(DisallowedRequestError) as excinfo:
        build_segment_query_url(envelope=(_HUGE_INT, 0, 1))  # type: ignore[arg-type]
    assert len(str(excinfo.value.detail["envelope"])) <= 220


def test_envelope_non_numeric_component_with_huge_int_is_disallowed() -> None:
    # xmin is non-numeric (fails before any float() conversion), so the refusal
    # path reprs the whole envelope - which also holds a huge int at ymin. The
    # bounded _safe_repr keeps that from raising during the refusal.
    with pytest.raises(DisallowedRequestError) as excinfo:
        build_segment_query_url(envelope=("x", _HUGE_INT, 1.0, 1.0))  # type: ignore[arg-type]
    assert excinfo.value.detail["axis"] == "xmin"
    assert len(str(excinfo.value.detail["envelope"])) <= 220


def test_predicate_conflict_with_huge_int_envelope_is_disallowed() -> None:
    # A predicate CONFLICT (envelope AND object_id) whose envelope carries a huge
    # int: the conflict detail reprs every predicate arg, so a raw repr would fail
    # on the huge int; the typed refusal must survive.
    with pytest.raises(DisallowedRequestError) as excinfo:
        build_segment_query_url(envelope=(_HUGE_INT, 0, 1, 1), object_id=7)  # type: ignore[arg-type]
    assert len(str(excinfo.value.detail["envelope"])) <= 220


def test_predicate_conflict_with_huge_int_object_id_is_disallowed() -> None:
    with pytest.raises(DisallowedRequestError) as excinfo:
        build_segment_query_url(borough="Manhattan", object_id=_HUGE_INT)
    assert len(str(excinfo.value.detail["object_id"])) <= 220


def test_fetch_street_segments_refuses_huge_int_envelope_before_any_network_io() -> None:
    # Deterministic zero-fetch regression: a malformed huge-int envelope is refused
    # in the URL builder, BEFORE the metadata round-trip, with the typed
    # DisallowedRequestError - not an uncaught ValueError and not one network call.
    calls = {"n": 0}

    def _must_not_fetch(url: str, correlation_id: str) -> DcmTransport:
        calls["n"] += 1
        raise AssertionError("no network I/O may occur for a refused envelope")

    with pytest.raises(DisallowedRequestError):
        fetch_street_segments(
            envelope=(_HUGE_INT, 0, 1),  # type: ignore[arg-type]
            fetch=_must_not_fetch,
        )
    assert calls["n"] == 0

    with pytest.raises(DisallowedRequestError):
        fetch_street_segments(
            envelope=("x", _HUGE_INT, 1.0, 1.0),  # type: ignore[arg-type]
            fetch=_must_not_fetch,
        )
    assert calls["n"] == 0
