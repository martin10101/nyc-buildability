"""Adapters mapping accepted connector domain models onto the spatial engine's
inputs. Consumes connector objects READ-ONLY (no connector edits): the lot
polygon from a MapPLUTO ``LotGeometryResult``, district polygons from
zoning-features ``LayerQueryResult`` / ``LayerExtractResult`` features, and the
official assignment from a ZTLDB ``ZtldbFetchResult``.

District esri geometries are canonicalized with the accepted MapPLUTO
``analyze_lot_geometry`` validator - the exact path the M2-T009 spatial tests
already use to feed real zoning-features fixtures to ``classify_spatial_relation``.
"""

from __future__ import annotations

from app.connectors.mappluto_geometry_arcgis import CRS_STAMP, analyze_lot_geometry

from .engine import compose_lot_intersection
from .models import DistrictFeature, LotInput
from .policy import MAPPLUTO_LOT_ACCURACY, family_for_layer, layer_accuracy

# Meaningful district-identity field per layer (primary, then fallbacks).
_LAYER_LABEL_FIELDS = {
    "nyzd": ("ZONEDIST",),
    "nyco": ("OVERLAY",),
    "nysp": ("SDLBL", "SDNAME"),
    "nysp_sd": ("SUBDIST_LBL", "SUBDIST", "SPLBL", "SPNAME"),
    "nylh": ("LHLBL", "LHNAME"),
    "nyzma": ("ULURPNO", "STATUS", "PROJECT_NAME"),
}

_LOT_SOURCE_ID = "nyc-dcp-mappluto-arcgis"
_NON_INTERSECTABLE = frozenset(
    {"invalid_geometry", "review_required", "no_feature", "multiple_features"}
)


def _date_prefix(value: object) -> str | None:
    if isinstance(value, str) and len(value) >= 10:
        return value[:10]
    return value if isinstance(value, str) else None


def _label_for(layer: str, attributes: dict, object_id: object) -> str:
    for field_name in _LAYER_LABEL_FIELDS.get(layer, ()):
        raw = attributes.get(field_name)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return f"{layer}:oid{object_id}"


def lot_input_from_result(lot_result: object) -> LotInput:
    """Map a MapPLUTO ``LotGeometryResult`` onto a :class:`LotInput`."""
    outcome = getattr(lot_result, "outcome", None)
    geometry = getattr(lot_result, "geometry", None)

    if outcome == "no_feature":
        status, canonical = "no_feature", None
    elif outcome == "multiple_features":
        status, canonical = "multiple_features", None
    elif geometry is None:
        status, canonical = "invalid_geometry", None
    else:
        status = geometry.status
        canonical = geometry.canonical_geometry

    review_required = (
        bool(getattr(lot_result, "review_required", False))
        or status in _NON_INTERSECTABLE
        or canonical is None
    )

    provenance = {
        "source_id": _LOT_SOURCE_ID,
        "requested_bbl": getattr(lot_result, "requested_bbl", None),
        "retrieved_at": getattr(lot_result, "retrieved_at", None),
        "normalized_digest": getattr(lot_result, "normalized_digest", None),
        "source_data_last_edited": getattr(lot_result, "source_data_last_edited", None),
        "crs": getattr(lot_result, "crs", None),
    }
    return LotInput(
        bbl=str(getattr(lot_result, "requested_bbl", "")),
        canonical_geometry=canonical,
        area_sq_ft=getattr(lot_result, "area_sq_ft", None),
        accuracy=MAPPLUTO_LOT_ACCURACY,
        geometry_status=status,
        review_required=review_required,
        provenance=provenance,
    )


def district_features_from_layer_result(layer_result: object) -> list[DistrictFeature]:
    """Map a zoning-features ``LayerQueryResult`` / ``LayerExtractResult`` onto
    a list of :class:`DistrictFeature`. Invalid district geometries are kept
    (canonical None + status) so the engine can route them to review, never
    silently drop them."""
    layer = layer_result.layer
    family = family_for_layer(layer)
    accuracy = layer_accuracy(layer)
    oid_field = getattr(layer_result, "object_id_field", "OBJECTID")
    digest = getattr(layer_result, "normalized_digest", None)
    retrieved_at = getattr(layer_result, "retrieved_at", None)

    features: list[DistrictFeature] = []
    for feature in getattr(layer_result, "features", []):
        attributes = feature.get("attributes", {}) or {}
        object_id = attributes.get(oid_field)
        assessment = analyze_lot_geometry(feature.get("geometry"), crs=dict(CRS_STAMP))
        features.append(
            DistrictFeature(
                layer=layer,
                family=family,
                label=_label_for(layer, attributes, object_id),
                canonical_geometry=assessment.canonical_geometry,
                accuracy=accuracy,
                geometry_status=assessment.status,
                feature_ref={
                    "layer": layer,
                    "object_id": object_id,
                    "source_normalized_digest": digest,
                    "retrieved_at": retrieved_at,
                    "geometry_status": assessment.status,
                },
            )
        )
    return features


def ztldb_inputs_from_result(ztldb_result: object) -> dict:
    """Extract the ZTLDB cross-check inputs from a ``ZtldbFetchResult``."""
    freshness = getattr(ztldb_result, "source_freshness", None) or {}
    return {
        "ztldb_assignment": getattr(ztldb_result, "zoning_assignment", None),
        "ztldb_status": getattr(ztldb_result, "status", None),
        "ztldb_dataset_version": getattr(ztldb_result, "dataset_version", None),
        "ztldb_source_vintage": _date_prefix(freshness.get("rows_updated_at")),
    }


def district_vintage_from_layer_result(layer_result: object) -> str | None:
    """Source vintage (date) of a zoning-features layer, for ZTLDB skew tagging."""
    return _date_prefix(getattr(layer_result, "source_data_last_edited", None))


def compose_from_connectors(
    lot_result: object,
    layer_results: list,
    ztldb_result: object | None = None,
    *,
    district_source_vintage: str | None = None,
):
    """Convenience: run the full engine directly on accepted connector domain
    models. ``layer_results`` is any mix of zoning-features layer results; the
    nyzd layer's source vintage is used for ZTLDB skew tagging unless overridden.
    """
    lot = lot_input_from_result(lot_result)
    districts: list[DistrictFeature] = []
    nyzd_vintage = district_source_vintage
    for layer_result in layer_results:
        districts.extend(district_features_from_layer_result(layer_result))
        if nyzd_vintage is None and getattr(layer_result, "layer", None) == "nyzd":
            nyzd_vintage = district_vintage_from_layer_result(layer_result)

    ztldb_inputs = (
        ztldb_inputs_from_result(ztldb_result)
        if ztldb_result is not None
        else {
            "ztldb_assignment": None,
            "ztldb_status": None,
            "ztldb_dataset_version": None,
            "ztldb_source_vintage": None,
        }
    )
    return compose_lot_intersection(
        lot,
        districts,
        ztldb_assignment=ztldb_inputs["ztldb_assignment"],
        ztldb_status=ztldb_inputs["ztldb_status"],
        ztldb_dataset_version=ztldb_inputs["ztldb_dataset_version"],
        ztldb_source_vintage=ztldb_inputs["ztldb_source_vintage"],
        district_source_vintage=nyzd_vintage,
    )
