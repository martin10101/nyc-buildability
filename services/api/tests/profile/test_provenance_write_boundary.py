"""Task M2-T018 acceptance scenarios AS-1, AS-2, AS-4: the FAIL-CLOSED
provenance write boundary in ``app.profile.builder``.

M2-T017 closed the canonical ``source_fact`` contract
(``additionalProperties:false``) and froze an un-wired allowlist serializer.
M2-T018 wires that serializer into ``_closed_provenance``, the single point
through which every ``source_fact`` record enters the profile ``provenance``
array. These tests pin the resulting behavior:

- AS-1 fail-closed: an UNDOCUMENTED key injected into ANY of the three feeds
  (PLUTO connector facts, ``additional_provenance``, the wave/spatial feed)
  raises ``ContractSerializationError`` and the build fails. The record is
  never silently dropped, no partial profile is returned, and the rejected
  VALUE never travels out through the exception.
- AS-2 real connector shapes: records produced by all four lineage-emitting
  connectors - PLUTO SODA, ZTLDB SODA, DCP zoning-features ArcGIS, MapPLUTO
  geometry ArcGIS - are driven from their RECORDED fixture captures and cross
  the boundary cleanly, with every documented lineage key
  (``dataset_id`` / ``request_url`` / ``input_vintages`` /
  ``source_rows_updated_at``) surviving. No bypass, nothing stripped.
- AS-4 completeness: the provenance count and every record's key set and
  values are preserved; the connector inputs are not mutated; the built
  profile still validates against the canonical schema.

Offline and deterministic: the same fixture-transport seam the accepted
M1-T005 / M2-T004 / M2-T008 / M2-T012 suites use. No test touches the network.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest

from app.connectors.mappluto_geometry_arcgis import fetch_lot_geometry
from app.connectors.pluto_soda import SOURCE_ID as PLUTO_SOURCE_ID
from app.connectors.pluto_soda import TransportResponse
from app.connectors.pluto_soda import fetch_by_bbl as pluto_fetch_by_bbl
from app.connectors.zoning_features_arcgis import extract_layer
from app.connectors.ztldb_soda import SOURCE_ID as ZTLDB_SOURCE_ID
from app.connectors.ztldb_soda import fetch_by_bbl as ztldb_fetch_by_bbl
from app.connectors.ztldb_soda import fetch_source_freshness
from app.contracts.serializers import (
    SOURCE_FACT_SERIALIZER,
    ContractSerializationError,
    MissingFieldError,
    UnknownFieldError,
)
from app.profile import builder as builder_module
from app.profile.builder import build_property_profile
from app.profile.contract import validate_profile
from app.profile.wave_integration import (
    MAPPLUTO_GEOMETRY_SOURCE_ID,
    ZONING_FEATURES_SOURCE_ID,
)

TESTS_DIR = Path(__file__).resolve().parents[1]
PLUTO_FIXTURES = TESTS_DIR / "fixtures" / "pluto"
ZTLDB_FIXTURES = TESTS_DIR / "fixtures" / "ztldb"
ZF_FIXTURES = TESTS_DIR / "fixtures" / "zoning_features"
MPG_FIXTURES = TESTS_DIR / "fixtures" / "mappluto_geometry"

FIXED_CLOCK = lambda: datetime(2026, 7, 20, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"


# --------------------------------------------------------------------------
# Fixture-transport seam (mirrors the accepted connector suites)
# --------------------------------------------------------------------------


def _body(directory: Path, name: str) -> str:
    return json.loads((directory / name).read_text(encoding="utf-8"))["response_body_raw"]


def _response(directory: Path, name: str) -> TransportResponse:
    fixture = json.loads((directory / name).read_text(encoding="utf-8"))
    return TransportResponse(
        status=fixture["http_status"], body=fixture["response_body_raw"], headers={}
    )


def _script_transport(*responses):
    items = list(responses)

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        if not items:
            raise AssertionError("fixture transport script exhausted")
        return items.pop(0)

    return transport


def _body_transport(*bodies):
    items = [
        b if isinstance(b, TransportResponse) else TransportResponse(200, b) for b in bodies
    ]

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return items.pop(0)

    return transport


def pluto_result(fixture: str = "F01_single_lot_normal.json", bbl: str = BBL):
    """Real PLUTO SODA connector output replayed from the accepted M1-T002
    capture (facts carry dataset_id / request_url / input_vintages)."""
    return pluto_fetch_by_bbl(
        bbl,
        transport=_body_transport(_body(PLUTO_FIXTURES, fixture)),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id="m2t018-pluto",
    )


def ztldb_result(fixture: str = "ZT01_record_single_lot.json", bbl: str = BBL):
    """Real ZTLDB SODA connector output replayed from the accepted M2-T008
    capture (facts carry dataset_id / request_url / source_rows_updated_at)."""
    freshness = fetch_source_freshness(
        transport=_body_transport(_body(ZTLDB_FIXTURES, "ZT08_api_views_metadata.json")),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        rng=Random(1),
        app_token=None,
    )
    return ztldb_fetch_by_bbl(
        bbl,
        freshness=freshness,
        transport=_body_transport(_body(ZTLDB_FIXTURES, fixture)),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        rng=Random(1),
        correlation_id="m2t018-ztldb",
        app_token=None,
    )


def zoning_features_result():
    """Real DCP zoning-features ArcGIS extraction (nylh, 3 recorded pages)."""
    return extract_layer(
        "nylh",
        page_size=6,
        transport=_script_transport(
            _response(ZF_FIXTURES, "ZF01e_meta_nylh.json"),
            _response(ZF_FIXTURES, "ZF02e_count_nylh.json"),
            _response(ZF_FIXTURES, "ZF04a_page_nylh_offset0.json"),
            _response(ZF_FIXTURES, "ZF04b_page_nylh_offset6.json"),
            _response(ZF_FIXTURES, "ZF04c_page_nylh_offset12.json"),
        ),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        rng=Random(42),
        correlation_id="m2t018-zf",
    )


def lot_geometry_result():
    """Real MapPLUTO geometry ArcGIS result replayed from the accepted M2-T009
    capture. NOTE: the recorded lot is 1008350041 while the PLUTO/ZTLDB facts
    are for 1000010100 - this composition is SYNTHETIC and exercises the
    boundary's record SHAPE only; it is never presented as a co-observation of
    one property (wave_integration stamps the profile's own bbl by design)."""
    return fetch_lot_geometry(
        "1008350041",
        transport=_script_transport(
            _response(MPG_FIXTURES, "MPG01_meta.json"),
            _response(MPG_FIXTURES, "MPG02_lot_single_1008350041.json"),
        ),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        rng=Random(42),
        correlation_id="m2t018-mpg",
    )


def full_profile(**overrides):
    """A profile fed by ALL provenance feeds at once: PLUTO facts, ZTLDB facts
    through additional_provenance, and the wave/spatial records."""
    kwargs = dict(
        clock=FIXED_CLOCK,
        additional_provenance=list(ztldb_result().facts),
        lot_geometry=lot_geometry_result(),
        zoning_features=[zoning_features_result()],
    )
    kwargs.update(overrides)
    return build_property_profile(pluto_result(), **kwargs)


def _canonical_order(record: dict) -> list[str]:
    return [f for f in SOURCE_FACT_SERIALIZER.allowed_fields if f in record]


# ==========================================================================
# AS-2 - all four lineage-emitting connector shapes cross the boundary
# ==========================================================================


def test_as2_all_four_connector_shapes_cross_the_boundary() -> None:
    profile = full_profile()
    by_source: dict[str, list[dict]] = {}
    for record in profile["provenance"]:
        by_source.setdefault(record["source_id"], []).append(record)

    # Every lineage-emitting connector is represented.
    for source_id in (
        PLUTO_SOURCE_ID,
        ZTLDB_SOURCE_ID,
        ZONING_FEATURES_SOURCE_ID,
        MAPPLUTO_GEOMETRY_SOURCE_ID,
    ):
        assert by_source.get(source_id), f"no provenance record from {source_id}"

    # Every emitted record is already serializer output: re-serializing is a
    # no-op, and the keys are in canonical schema order. A record spliced into
    # the array WITHOUT crossing _closed_provenance would fail this (the SODA
    # connectors emit their lineage keys in a different order), so this is also
    # the regression guard against a future un-routed splice.
    for record in profile["provenance"]:
        assert SOURCE_FACT_SERIALIZER.serialize(record) == record
        assert list(record) == _canonical_order(record)


def test_as2_documented_lineage_keys_survive_the_boundary() -> None:
    """The four M2-T017-documented connector lineage keys are NOT stripped:
    the boundary is a documented allowlist, never a silent filter."""
    profile = full_profile()
    pluto_records = [
        r for r in profile["provenance"] if r["source_id"] == PLUTO_SOURCE_ID
    ]
    ztldb_records = [
        r for r in profile["provenance"] if r["source_id"] == ZTLDB_SOURCE_ID
    ]
    assert pluto_records and ztldb_records

    for record in pluto_records:
        assert record["dataset_id"] == "64uk-42ks"
        assert record["request_url"].startswith("https://")
        assert isinstance(record["input_vintages"], dict)
    for record in ztldb_records:
        assert record["dataset_id"] == "fdkv-4t4z"
        assert record["request_url"].startswith("https://")
        assert record["source_rows_updated_at"]

    # And the union of keys actually emitted stays inside the closed contract.
    emitted = {key for record in profile["provenance"] for key in record}
    assert emitted <= set(SOURCE_FACT_SERIALIZER.allowed_fields)


def test_as2_built_profile_still_validates_against_the_canonical_schema() -> None:
    validate_profile(full_profile())  # must not raise: an invalid 200 is impossible


# ==========================================================================
# AS-4 - provenance completeness and fidelity preserved
# ==========================================================================


def test_as4_provenance_count_is_preserved_across_every_feed() -> None:
    pluto = pluto_result()
    ztldb = ztldb_result()
    profile = build_property_profile(
        pluto,
        clock=FIXED_CLOCK,
        additional_provenance=list(ztldb.facts),
        lot_geometry=lot_geometry_result(),
        zoning_features=[zoning_features_result()],
    )
    # PLUTO facts + ZTLDB facts + 1 lot-geometry record + 1 zoning-features
    # layer record. Nothing dropped, nothing deduplicated, nothing invented.
    assert len(profile["provenance"]) == len(pluto.facts) + len(ztldb.facts) + 2


def test_as4_every_record_keeps_its_keys_and_values() -> None:
    """Key-level enforcement only: the boundary may reorder keys, never change
    a key set or a value."""
    pluto = pluto_result()
    profile = build_property_profile(pluto, clock=FIXED_CLOCK)
    emitted = {record["provenance_id"]: record for record in profile["provenance"]}
    assert len(emitted) == len(pluto.facts)
    for source_fact in pluto.facts:
        out = emitted[source_fact["provenance_id"]]
        assert set(out) == set(source_fact)
        assert out == source_fact  # dict equality is order-insensitive


def test_as4_connector_inputs_are_never_mutated() -> None:
    pluto = pluto_result()
    snapshot = json.loads(json.dumps(pluto.facts))
    profile = build_property_profile(pluto, clock=FIXED_CLOCK)
    assert pluto.facts == snapshot
    # The emitted records are NEW dicts, not aliases of the connector's.
    by_id = {record["provenance_id"]: record for record in profile["provenance"]}
    for source_fact in pluto.facts:
        assert by_id[source_fact["provenance_id"]] is not source_fact


# ==========================================================================
# AS-1 - fail closed on an undocumented / missing key, in EVERY feed
# ==========================================================================


def test_as1_undocumented_key_in_connector_facts_fails_the_build_closed() -> None:
    pluto = pluto_result()
    pluto.facts[0]["_debug_internal_state"] = {"stage": "normalize"}
    with pytest.raises(UnknownFieldError) as exc:
        build_property_profile(pluto, clock=FIXED_CLOCK)
    assert isinstance(exc.value, ContractSerializationError)
    assert exc.value.unknown_keys == ["_debug_internal_state"]
    # The offending record was NOT silently cleaned out of the connector result
    # either: the platform rejects the build instead of quietly repairing data.
    assert "_debug_internal_state" in pluto.facts[0]


def test_as1_undocumented_key_in_additional_provenance_fails_the_build_closed() -> None:
    ztldb_facts = list(ztldb_result().facts)
    ztldb_facts[0] = {**ztldb_facts[0], "actor_ip": "203.0.113.7"}
    with pytest.raises(UnknownFieldError) as exc:
        build_property_profile(
            pluto_result(), clock=FIXED_CLOCK, additional_provenance=ztldb_facts
        )
    assert exc.value.unknown_keys == ["actor_ip"]


def test_as1_undocumented_key_in_the_wave_feed_fails_the_build_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The wave/spatial feed splices in AFTER the initial provenance assembly;
    it crosses the SAME boundary, so there is no second, laxer path."""
    real_build_wave_sections = builder_module.build_wave_sections

    def leaky_build_wave_sections(*args, **kwargs):
        sections, records = real_build_wave_sections(*args, **kwargs)
        assert records, "the wave feed must produce records for this test"
        records[0] = {**records[0], "_leaked_layer_debug": "internal"}
        return sections, records

    monkeypatch.setattr(
        builder_module, "build_wave_sections", leaky_build_wave_sections
    )
    with pytest.raises(UnknownFieldError) as exc:
        build_property_profile(
            pluto_result(), clock=FIXED_CLOCK, lot_geometry=lot_geometry_result()
        )
    assert exc.value.unknown_keys == ["_leaked_layer_debug"]


def test_as1_typo_of_an_optional_field_fails_closed_not_silently_dropped() -> None:
    """The exact defect the closed contract exists to catch: a mistyped
    OPTIONAL key would otherwise vanish, taking its units with it."""
    pluto = pluto_result()
    fact = pluto.facts[0]
    fact.pop("units", None)
    fact["unit"] = "square_feet"
    with pytest.raises(UnknownFieldError) as exc:
        build_property_profile(pluto, clock=FIXED_CLOCK)
    assert exc.value.unknown_keys == ["unit"]


def test_as1_missing_required_provenance_field_fails_closed() -> None:
    """PRD section 9 makes every listed provenance field mandatory; an
    incomplete record can never reach a profile."""
    pluto = pluto_result()
    del pluto.facts[0]["conflict_status"]
    with pytest.raises(MissingFieldError) as exc:
        build_property_profile(pluto, clock=FIXED_CLOCK)
    assert isinstance(exc.value, ContractSerializationError)
    assert exc.value.missing_keys == ["conflict_status"]


def test_as1_rejection_never_leaks_the_offending_value() -> None:
    """Diagnostic-leak safety at the WIRED boundary (not only in the unit
    tests of the serializer): the exception names the KEY, never the value -
    so a leaked token/stack trace cannot escape through logs."""
    secret = "Traceback: token=SUPER_SECRET_abc123 at line 42"  # noqa: S105
    pluto = pluto_result()
    pluto.facts[0]["_debug_stacktrace"] = secret
    with pytest.raises(ContractSerializationError) as exc:
        build_property_profile(pluto, clock=FIXED_CLOCK)
    message = str(exc.value)
    assert "_debug_stacktrace" in message
    assert "SUPER_SECRET" not in message
    assert secret not in message


def test_as1_failure_is_a_valueerror_so_the_api_maps_it_to_a_typed_500() -> None:
    """``ContractSerializationError`` subclasses ``ValueError`` and propagates
    out of the builder. Both API routes build INSIDE their outer handler, so
    this becomes a typed 500 carrying only the correlation id - never an
    invalid 200, and never a partially built profile."""
    assert issubclass(ContractSerializationError, ValueError)
    pluto = pluto_result()
    pluto.facts[0]["leaked"] = 1
    with pytest.raises(ValueError):
        build_property_profile(pluto, clock=FIXED_CLOCK)
