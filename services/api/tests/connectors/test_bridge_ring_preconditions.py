"""M5-T073 - DB-045(a) bridge-mount precondition validation on REAL parcel pairs.

Fully OFFLINE and deterministic. This harness reproduces the ACCEPTED outline
bridge's correspondence semantics (``services/api/app/api/v1/outline_bridge.py``)
and measures them, BEFORE any mount, against parcel ring PAIRS:

  * the DISPLAY ring - EPSG:4326, display-only, from
    ``app.connectors.mappluto_lot_outline`` (``build_lot_outline`` ->
    ``_exterior_ring_from_geojson`` -> ``_open_ring``); and
  * the AUTHORITATIVE ring - EPSG:2263 US survey feet, from
    ``app.connectors.mappluto_geometry_arcgis`` (``analyze_lot_geometry`` ->
    ``canonical_geometry[0][0]`` -> ``_open_ring``).

For each pair it records the two vertex counts, runs the bridge's OWN
``fit_correspondence`` (a 2D affine least-squares search over both windings and
all cyclic offsets), and classifies the pair by the bridge's OWN decision path:
a vertex-count mismatch (the differently-densified real-lot risk DB-045(a)
names), a fit residual above ``BRIDGE_MAX_RMS_RESIDUAL_FT`` (2.0 ft), an
ambiguous best alignment below ``BRIDGE_AMBIGUITY_SEPARATION_FT`` (2.0 ft), or a
PASS. The constants and the fit function are IMPORTED from the bridge, never
re-implemented, so the measurement is the bridge's real precondition.

Scope (validation only - NO mount, NO production edit; AS-4):
- AS-2 (measurement correctness): synthetic pairs with KNOWN outcomes prove the
  semantics - one passing (residual ~0, unique alignment) and two violating
  (a densification mismatch -> ``vertex_count_mismatch``; a non-corresponding
  same-count pair -> ``residual_too_high``), asserting the numeric residual AND
  the classification.
- AS-1/AS-3 (real pairs + honest verdict): real parcel pairs are measured
  OFFLINE from the accepted, provenance-stamped connector fixture packs
  (``tests/fixtures/mappluto_lot_outline`` display 4326 +
  ``tests/fixtures/mappluto_geometry`` authoritative 2263), bound by
  ``fixtures/bridge_ring_pairs/pairs_manifest.json``. Each pair's provenance
  (endpoint, BBL, retrieved_at, sha256) round-trips in the harness output and
  the authoritative body's sha256 is asserted against the recorded digest. A
  pair that violates a precondition is a FINDING with its refusal class, never a
  suppressed sample and never a test failure by itself.

HONEST BOUND (D-051 discipline): the accepted fixture packs overlap on 4 real
single-lot pairs across 2 boroughs. Reaching the packet's >=8 pairs / >=3
boroughs / regular-small-lot coverage requires capturing more real pairs through
the two live connectors, which needs network egress this offline worker does not
have. That remainder is ROUTED TO HARVEST (never fabricated) with an exact,
re-runnable spec in ``fixtures/bridge_ring_pairs/HARVEST_SPEC.md``; the harness
picks up harvested pairs with no code change. The bounded verdict on the current
real sample lives in ``project-control/reports/M5-T073-producer-report.md``.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import pytest

from app.api.v1.outline_bridge import (
    BRIDGE_AMBIGUITY_SEPARATION_FT,
    BRIDGE_MAX_RMS_RESIDUAL_FT,
    BRIDGE_MIN_CONTROL_POINTS,
    ParcelRing,
    _CorrespondenceError,
    _exterior_ring_from_geojson,
    _open_ring,
    fit_correspondence,
)
from app.connectors import mappluto_geometry_arcgis as geom
from app.connectors import mappluto_lot_outline as outline
from app.connectors.bbl import normalize_bbl

# ---------------------------------------------------------------------------
# Paths (offline fixture packs live in the repo; nothing here touches network).
# ---------------------------------------------------------------------------
API_TESTS = Path(__file__).resolve().parents[1]  # services/api/tests
FIXTURES = API_TESTS / "fixtures"
PAIRS_DIR = Path(__file__).resolve().parent / "fixtures" / "bridge_ring_pairs"
PAIRS_MANIFEST = PAIRS_DIR / "pairs_manifest.json"


# ---------------------------------------------------------------------------
# Verdict record (one row of the AS-3 verdict table).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PairVerdict:
    """One measured ring pair. ``verdict`` is ``pass`` or ``refuse``;
    ``refusal_class`` is the bridge's machine reason on a refusal (else None)."""

    pair_id: str
    bbl: str
    borough_code: int | None
    geometry_class: str
    display_vertex_count: int
    auth_vertex_count: int
    counts_equal: bool
    rms_residual_ft: float | None
    max_residual_ft: float | None
    runner_up_rms_residual_ft: float | None
    alignment_separation_ft: float | None
    residual_bound_ft: float
    verdict: str
    refusal_class: str | None
    notes: str = ""


def classify_ring_pair(
    display: ParcelRing,
    authoritative: ParcelRing,
    *,
    pair_id: str,
    bbl: str,
    borough_code: int | None,
    geometry_class: str,
    notes: str = "",
) -> PairVerdict:
    """Classify one pair by the bridge's OWN decision path. Vertex counts are
    recorded for BOTH rings even when the correspondence itself refuses (the
    densification mismatch DB-045(a) names surfaces as ``vertex_count_mismatch``
    from ``fit_correspondence``)."""
    dn = len(display.points)
    an = len(authoritative.points)
    base = {
        "pair_id": pair_id,
        "bbl": bbl,
        "borough_code": borough_code,
        "geometry_class": geometry_class,
        "display_vertex_count": dn,
        "auth_vertex_count": an,
        "counts_equal": dn == an,
        "residual_bound_ft": BRIDGE_MAX_RMS_RESIDUAL_FT,
        "notes": notes,
    }
    try:
        correspondence = fit_correspondence(display, authoritative)
    except _CorrespondenceError as exc:
        return PairVerdict(
            **base,
            rms_residual_ft=None,
            max_residual_ft=None,
            runner_up_rms_residual_ft=None,
            alignment_separation_ft=None,
            verdict="refuse",
            refusal_class=exc.reason,
        )
    fit = correspondence.fit
    separation = correspondence.separation
    runner_up = (
        None
        if math.isinf(correspondence.runner_up_rms_residual)
        else correspondence.runner_up_rms_residual
    )
    separation_ft = None if math.isinf(separation) else separation
    if fit.rms_residual > BRIDGE_MAX_RMS_RESIDUAL_FT:
        verdict, refusal_class = "refuse", "residual_too_high"
    elif separation_ft is not None and separation_ft < BRIDGE_AMBIGUITY_SEPARATION_FT:
        verdict, refusal_class = "refuse", "ambiguous_correspondence"
    else:
        verdict, refusal_class = "pass", None
    return PairVerdict(
        **base,
        rms_residual_ft=fit.rms_residual,
        max_residual_ft=fit.max_residual,
        runner_up_rms_residual_ft=runner_up,
        alignment_separation_ft=separation_ft,
        verdict=verdict,
        refusal_class=refusal_class,
    )


# ---------------------------------------------------------------------------
# Ring reconstruction - EXACTLY as the bridge's production adapters do, but from
# recorded fixture bytes (offline). See outline_bridge._default_display_ring and
# _default_authoritative_ring.
# ---------------------------------------------------------------------------
def display_ring_from_geojson_body(body: str, bbl: str, *, retrieved_at: str) -> ParcelRing:
    """Reconstruct the 4326 display ring from a verbatim
    ``f=geojson&outSR=4326`` response body (the lot-outline connector's raw
    output), through the connector's real parse + contract validation."""
    normalized = normalize_bbl(bbl)
    url = build_outline_query_url(normalized.canonical)
    doc = build_lot_outline(
        normalized.canonical,
        fetch=lambda *_: LotOutlineTransport(
            url=url, status=200, body=body, retrieved_at=retrieved_at
        ),
    )
    if doc["outcome"] != "single_lot":
        raise AssertionError(f"{bbl}: display outcome {doc['outcome']!r} is not single_lot")
    ring = _exterior_ring_from_geojson(doc["geometry"])
    if ring is None:
        raise AssertionError(f"{bbl}: no usable 4326 exterior ring")
    version = (doc.get("source") or {}).get("dataset_version")
    return ParcelRing(
        points=_open_ring(ring),
        crs="EPSG:4326",
        source_id=OUTLINE_SOURCE_ID,
        source_detail={"representation": "lot_outline_display", "dataset_version": version},
    )


def authoritative_ring_from_query_body(body: str, bbl: str) -> ParcelRing:
    """Reconstruct the 2263 authoritative ring from a verbatim esri ``f=json``
    query response body, through the connector's real ``analyze_lot_geometry``
    canonicalization - identical to what the bridge consumes
    (``canonical_geometry[0][0]``), without the metadata round-trip
    ``fetch_lot_geometry`` would add (the bridge uses only the canonical
    geometry, which is produced solely by ``analyze_lot_geometry``)."""
    doc = json.loads(body)
    sr = doc.get("spatialReference") or {}
    require_authoritative_crs({"wkid": sr.get("wkid"), "latest_wkid": sr.get("latestWkid")})
    features = doc.get("features") or []
    if len(features) != 1:
        raise AssertionError(f"{bbl}: expected exactly one feature, got {len(features)}")
    esri_geometry = features[0].get("geometry")
    assessment = analyze_lot_geometry(esri_geometry, crs=dict(CRS_STAMP))
    if not assessment.canonical_geometry:
        raise AssertionError(
            f"{bbl}: no canonical geometry (assessment status {assessment.status!r})"
        )
    shell = assessment.canonical_geometry[0][0]  # first polygon, exterior ring
    ring = [(float(x), float(y)) for x, y in shell]
    return ParcelRing(
        points=_open_ring(ring),
        crs="EPSG:2263",
        source_id=GEOM_SOURCE_ID,
        source_detail={
            "representation": "lot_geometry_authoritative",
            "normalized_digest": assessment.normalized_digest,
            "geometry_status": assessment.status,
        },
    )


# ---------------------------------------------------------------------------
# Provenance / fixture loading.
# ---------------------------------------------------------------------------
def _sha256(text: str) -> str:
    """sha256 over the exact UTF-8 bytes (matches the MapPLUTO-geometry pack's
    ``response_body_raw`` digest basis; those bodies are compact single-line
    JSON with no embedded newlines, so this is byte-stable across checkout)."""
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_pairs() -> list[dict]:
    if not PAIRS_MANIFEST.exists():
        return []
    return json.loads(PAIRS_MANIFEST.read_text(encoding="utf-8")).get("pairs", [])


def _read_body(rel_path: str) -> str:
    return (FIXTURES / rel_path).read_text(encoding="utf-8")


def _auth_response_body(rel_path: str) -> str:
    """The verbatim esri body lives under ``response_body_raw`` in the
    MapPLUTO-geometry provenance envelope."""
    envelope = json.loads(_read_body(rel_path))
    return envelope["response_body_raw"]


def measure_pair(pair: dict) -> tuple[PairVerdict, dict]:
    """Measure one manifest pair OFFLINE and return (verdict, provenance echo)."""
    disp_spec = pair["display"]
    auth_spec = pair["authoritative"]
    disp_body = _read_body(disp_spec["source_fixture"])
    auth_body = _auth_response_body(auth_spec["source_fixture"])
    display = display_ring_from_geojson_body(
        disp_body, pair["bbl"], retrieved_at=disp_spec["retrieved_at"]
    )
    authoritative = authoritative_ring_from_query_body(auth_body, pair["bbl"])
    verdict = classify_ring_pair(
        display,
        authoritative,
        pair_id=pair["pair_id"],
        bbl=pair["bbl"],
        borough_code=pair.get("borough_code"),
        geometry_class=pair["geometry_class"],
        notes=pair.get("notes", ""),
    )
    provenance = {
        "pair_id": pair["pair_id"],
        "bbl": pair["bbl"],
        "borough": pair.get("borough"),
        "geometry_class": pair["geometry_class"],
        "display": {
            "source_fixture": disp_spec["source_fixture"],
            "endpoint": disp_spec["endpoint"],
            "retrieved_at": disp_spec["retrieved_at"],
            "computed_sha256": _sha256(disp_body),
            "source_file_sha256": disp_spec.get("source_file_sha256"),
        },
        "authoritative": {
            "source_fixture": auth_spec["source_fixture"],
            "endpoint": auth_spec["endpoint"],
            "retrieved_at": auth_spec["retrieved_at"],
            "computed_response_body_sha256": _sha256(auth_body),
            "recorded_response_body_sha256": auth_spec.get("response_body_sha256"),
        },
    }
    return verdict, provenance


def build_verdict_table() -> list[dict]:
    """The full AS-3 verdict table over every manifest pair (verdict rows +
    provenance echoes). The orchestrator/CI can emit it with:
    ``python -c "import json;
    from tests.connectors.test_bridge_ring_preconditions import build_verdict_table as b;
    print(json.dumps(b(), indent=2))"`` (run from services/api)."""
    return [
        {"verdict": asdict(verdict), "provenance": provenance}
        for verdict, provenance in (measure_pair(pair) for pair in load_pairs())
    ]


# ---------------------------------------------------------------------------
# AS-2 - measurement correctness on synthetic pairs with KNOWN outcomes.
# ---------------------------------------------------------------------------
# Five asymmetric 4326 display vertices (an irregular pentagon, so exactly one
# index alignment fits - a symmetric parcel would be refused as ambiguous).
_SYNTH_DISPLAY = (
    (-73.98000, 40.75000),
    (-73.98000, 40.75080),
    (-73.97960, 40.75110),
    (-73.97910, 40.75070),
    (-73.97930, 40.75010),
)
# An exact local affine 4326 -> 2263 (feet). Over one NYC lot the true relation
# is locally affine to sub-inch, so a genuine pair fits with a tiny residual.
_SYNTH_AFFINE = (276000.0, 1500.0, 985000.0, -1200.0, 364000.0, 200000.0)


def _apply_affine(
    points: tuple[tuple[float, float], ...], coeffs: tuple[float, ...]
) -> tuple[tuple[float, float], ...]:
    a, b, c, d, e, f = coeffs
    return tuple((a * u + b * v + c, d * u + e * v + f) for (u, v) in points)


def _ring(points: tuple[tuple[float, float], ...], crs: str) -> ParcelRing:
    return ParcelRing(points=points, crs=crs, source_id="synthetic", source_detail={})


def test_bridge_constants_are_the_accepted_bounds():
    """Pin the measurement to the bridge's real precondition bounds; a drift in
    the bridge that this harness did not track fails here, not silently."""
    assert BRIDGE_MAX_RMS_RESIDUAL_FT == 2.0
    assert BRIDGE_AMBIGUITY_SEPARATION_FT == 2.0
    assert BRIDGE_MIN_CONTROL_POINTS == 4


def test_synthetic_corresponding_pair_passes_with_near_zero_residual():
    display = _ring(_SYNTH_DISPLAY, "EPSG:4326")
    authoritative = _ring(_apply_affine(_SYNTH_DISPLAY, _SYNTH_AFFINE), "EPSG:2263")
    verdict = classify_ring_pair(
        display,
        authoritative,
        pair_id="SYNTH_pass",
        bbl="synthetic",
        borough_code=None,
        geometry_class="synthetic_exact_affine",
    )
    assert verdict.verdict == "pass"
    assert verdict.refusal_class is None
    assert verdict.counts_equal and verdict.display_vertex_count == 5
    assert verdict.rms_residual_ft is not None and verdict.rms_residual_ft < 1e-3
    # Asymmetric parcel -> the correct alignment beats the runner-up by far.
    assert verdict.alignment_separation_ft is not None
    assert verdict.alignment_separation_ft >= BRIDGE_AMBIGUITY_SEPARATION_FT


def test_synthetic_densification_mismatch_is_a_vertex_count_finding():
    display = _ring(_SYNTH_DISPLAY, "EPSG:4326")
    matched = _apply_affine(_SYNTH_DISPLAY, _SYNTH_AFFINE)
    midpoint = (
        (matched[0][0] + matched[1][0]) / 2.0,
        (matched[0][1] + matched[1][1]) / 2.0,
    )
    densified = (matched[0], midpoint, *matched[1:])  # 6 vs 5 vertices
    authoritative = _ring(densified, "EPSG:2263")
    verdict = classify_ring_pair(
        display,
        authoritative,
        pair_id="SYNTH_densified",
        bbl="synthetic",
        borough_code=None,
        geometry_class="synthetic_densification_mismatch",
    )
    assert verdict.verdict == "refuse"
    assert verdict.refusal_class == "vertex_count_mismatch"
    assert verdict.display_vertex_count == 5
    assert verdict.auth_vertex_count == 6
    assert verdict.counts_equal is False


def test_synthetic_noncorresponding_same_count_pair_is_residual_too_high():
    display = _ring(_SYNTH_DISPLAY, "EPSG:4326")
    matched = list(_apply_affine(_SYNTH_DISPLAY, _SYNTH_AFFINE))
    matched[2] = (matched[2][0] + 40.0, matched[2][1] - 40.0)  # two large,
    matched[4] = (matched[4][0] - 40.0, matched[4][1] + 40.0)  # opposing outliers
    authoritative = _ring(tuple(matched), "EPSG:2263")
    verdict = classify_ring_pair(
        display,
        authoritative,
        pair_id="SYNTH_perturbed",
        bbl="synthetic",
        borough_code=None,
        geometry_class="synthetic_noncorresponding",
    )
    assert verdict.verdict == "refuse"
    assert verdict.refusal_class == "residual_too_high"
    assert verdict.counts_equal is True
    assert verdict.rms_residual_ft is not None
    assert verdict.rms_residual_ft > BRIDGE_MAX_RMS_RESIDUAL_FT


# ---------------------------------------------------------------------------
# AS-1 / AS-3 - real pairs measured OFFLINE from the accepted fixture packs.
# ---------------------------------------------------------------------------
_PAIRS = load_pairs()
_PAIR_IDS = [p["pair_id"] for p in _PAIRS]


def test_real_pairs_manifest_is_present_and_covers_multiple_classes():
    """The offline real sample assembled from the accepted connector fixture
    packs. It is a BOUNDED sample (see the producer report); the >=8-pair /
    >=3-borough completion is routed to harvest (HARVEST_SPEC.md)."""
    assert _PAIRS, "pairs_manifest.json must bind at least the accepted-fixture real pairs"
    boroughs = {p.get("borough_code") for p in _PAIRS}
    classes = {p["geometry_class"] for p in _PAIRS}
    assert len(_PAIRS) >= 4
    assert len(boroughs) >= 2
    assert len(classes) >= 3


@pytest.mark.skipif(not _PAIRS, reason="no real pairs bound yet (see HARVEST_SPEC.md)")
@pytest.mark.parametrize("pair", _PAIRS, ids=_PAIR_IDS)
def test_real_pair_measured_offline_with_roundtrip_provenance(pair):
    verdict, provenance = measure_pair(pair)
    # Provenance round-trips in the harness output; the authoritative body's
    # sha256 is asserted against the recorded digest (same byte basis).
    assert provenance["bbl"] == pair["bbl"]
    auth = provenance["authoritative"]
    if auth["recorded_response_body_sha256"]:
        assert auth["computed_response_body_sha256"] == auth["recorded_response_body_sha256"]
    assert provenance["display"]["computed_sha256"].startswith("sha256:")
    # A precondition violation is a FINDING, never a test failure by itself.
    assert verdict.verdict in ("pass", "refuse")
    if verdict.verdict == "refuse":
        assert verdict.refusal_class is not None
    assert verdict.display_vertex_count >= 3
    assert verdict.auth_vertex_count >= 3
    assert verdict.residual_bound_ft == BRIDGE_MAX_RMS_RESIDUAL_FT


def test_verdict_table_builds_over_every_real_pair():
    table = build_verdict_table()
    assert len(table) == len(_PAIRS)
    for row in table:
        assert row["verdict"]["verdict"] in ("pass", "refuse")
        assert row["provenance"]["authoritative"]["computed_response_body_sha256"].startswith(
            "sha256:"
        )
    # Emit the table so a harvest/CI run captures the concrete AS-3 numbers.
    print("M5-T073 bridge-ring verdict table:\n" + json.dumps(table, indent=2))
