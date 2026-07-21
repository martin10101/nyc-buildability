"""Deterministic (lot, district) geometric classification under the compound
positional-uncertainty band (advisory 2.3, 2.4, 2.6.7).

This is the production extension of the proven TEST-level
``classify_spatial_relation`` (``mappluto_geometry_arcgis.py:1037-1092``): same
erode/dilate erosion semantics, now with a COMPOUND band (both the lot and the
district geometry are uncertain), the five-class taxonomy, exact geometric
results preserved regardless of class, split-share RANGES, the degenerate
narrow-feature guard, and the 2x-band sensitivity trigger that makes an
``assumed`` accuracy fail safe.

No function here makes a legal zoning determination. Everything returned is a
geometric fact-with-uncertainty; ``Verified`` is out of scope by construction.
"""

from __future__ import annotations

from shapely.geometry.base import BaseGeometry

# Read-only reuse of the accepted MapPLUTO connector's proven, pinned geometry
# primitives (no connector edits; imports are the intended consumption path).
from app.connectors.mappluto_geometry_arcgis import (
    PINNED_GEOS_VERSION_STRING,
    PINNED_SHAPELY_VERSION,
)

from .models import (
    PAIR_EXTERIOR_CONFIDENT,
    PAIR_INTERIOR_CONFIDENT,
    PAIR_NEAR_BOUNDARY_UNCERTAIN,
    PAIR_SPLIT_CONFIDENT,
    PairIntersection,
)
from .policy import (
    AREA_EPSILON_SQ_FT,
    COMBINATION_RULE,
    MINOR_PORTION_SHARE,
    SENSITIVITY_BAND_MULTIPLIER,
    SourceAccuracy,
    combined_band_ft,
)

# Internal-only preliminary class for a raw-overlap-but-no-firm-area pair. The
# engine resolves it to ``sliver_ambiguous`` (firm area exists in a DIFFERENT
# district) or ``near_boundary_uncertain`` (no firm area anywhere). It is never
# emitted verbatim.
PAIR_SLIVER_LIKE = "_sliver_like"

# Emitted-record numeric precision (reproducibility SI-S10): classification uses
# raw floats; only the stored numbers are quantized so repeated/independent runs
# on the same pinned GEOS build produce byte-identical records.
_AREA_DECIMALS = 4
_SHARE_DECIMALS = 8
_DISTANCE_DECIMALS = 4


def assert_geometry_pins(shapely_version: str, geos_version: str) -> None:
    """Fail closed if the runtime geometry stack is not the exact pinned build
    the digests/areas are proven against (M2-T009 precedent: repaired-geometry
    digests are GEOS-build-dependent)."""
    if shapely_version != PINNED_SHAPELY_VERSION or geos_version != PINNED_GEOS_VERSION_STRING:
        raise RuntimeError(
            "spatial engine requires the pinned geometry build "
            f"shapely=={PINNED_SHAPELY_VERSION} / GEOS {PINNED_GEOS_VERSION_STRING}; "
            f"got shapely=={shapely_version} / GEOS {geos_version}"
        )


def _erode_dilate(shape: BaseGeometry, band_ft: float) -> tuple[BaseGeometry, BaseGeometry]:
    """Erode/dilate a district polygon by the compound band. Mirrors the proven
    M2-T009 ``buffer(-b)`` / ``buffer(+b)`` semantics exactly."""
    return shape.buffer(-band_ft), shape.buffer(band_ft)


def _preliminary_class(
    lot: BaseGeometry,
    district: BaseGeometry,
    erode: BaseGeometry,
    dilate: BaseGeometry,
    *,
    band_ft: float,
    eps: float,
) -> tuple[str, float, float, float, float, float]:
    """Return ``(class, raw, firm, dilated, firm_outside, distance)``.

    ``firm`` = area(lot ∩ erode); ``firm_outside`` = area(lot ∖ dilate). Order
    of tests is deterministic. ``PAIR_SLIVER_LIKE`` is resolved by the engine.
    """
    distance_ft = float(lot.distance(district))
    raw = float(lot.intersection(district).area)
    firm = 0.0 if erode.is_empty else float(lot.intersection(erode).area)
    dilated = float(lot.intersection(dilate).area)
    firm_outside = float(lot.difference(dilate).area)

    if distance_ft > band_ft:
        cls = PAIR_EXTERIOR_CONFIDENT
    elif (not erode.is_empty) and lot.within(erode):
        cls = PAIR_INTERIOR_CONFIDENT
    elif firm > eps and firm_outside > eps:
        cls = PAIR_SPLIT_CONFIDENT
    elif raw > eps and firm <= eps:
        # Apparent overlap entirely inside the band and no firm interior area:
        # a sliver-like pair (engine decides sliver_ambiguous vs near_boundary).
        cls = PAIR_SLIVER_LIKE
    else:
        cls = PAIR_NEAR_BOUNDARY_UNCERTAIN
    return cls, raw, firm, dilated, firm_outside, distance_ft


def classify_pair(
    lot_shape: BaseGeometry,
    lot_area_sq_ft: float,
    *,
    layer: str,
    family: str,
    district_label: str,
    district_shape: BaseGeometry,
    lot_accuracy: SourceAccuracy,
    district_accuracy: SourceAccuracy,
    feature_ref: dict | None = None,
) -> PairIntersection:
    """Classify one lot against one district polygon under the compound band.

    The returned ``pair_class`` may be the internal ``PAIR_SLIVER_LIKE``
    sentinel, resolved to a public class by the engine using cross-district
    context. Exact geometric results are always populated (advisory 2.3): the
    class is an interpretation; the numbers are the facts.
    """
    district = district_shape
    band_ft = combined_band_ft(lot_accuracy, district_accuracy)
    erode, dilate = _erode_dilate(district, band_ft)
    band_exceeds_feature_width = erode.is_empty

    cls, raw, firm, dilated, firm_outside, distance_ft = _preliminary_class(
        lot_shape, district, erode, dilate, band_ft=band_ft, eps=AREA_EPSILON_SQ_FT
    )

    # 2x-band sensitivity (advisory 2.6.7): reclassify once at double band; a
    # class change while an ASSUMED accuracy participates fails safe to review.
    accuracy_basis_assumed = lot_accuracy.basis == "assumed" or district_accuracy.basis == "assumed"
    sensitivity_flip = False
    if accuracy_basis_assumed:
        band2 = band_ft * SENSITIVITY_BAND_MULTIPLIER
        erode2, dilate2 = _erode_dilate(district, band2)
        cls2, *_ = _preliminary_class(
            lot_shape, district, erode2, dilate2, band_ft=band2, eps=AREA_EPSILON_SQ_FT
        )
        sensitivity_flip = cls2 != cls

    lot_area = float(lot_area_sq_ft)
    if lot_area > 0.0:
        share_min = firm / lot_area
        share_point = raw / lot_area
        share_max = min(dilated / lot_area, 1.0)
    else:
        share_min = share_point = share_max = 0.0

    firm_share = (firm / lot_area) if lot_area > 0.0 else 0.0
    minor_portion = 0.0 < firm_share < MINOR_PORTION_SHARE

    return PairIntersection(
        layer=layer,
        family=family,
        district_label=district_label,
        pair_class=cls,
        raw_intersection_sq_ft=round(raw, _AREA_DECIMALS),
        firm_intersection_sq_ft=round(firm, _AREA_DECIMALS),
        dilated_intersection_sq_ft=round(dilated, _AREA_DECIMALS),
        distance_ft=round(distance_ft, _DISTANCE_DECIMALS),
        lot_area_sq_ft=round(lot_area, _AREA_DECIMALS),
        share_min=round(share_min, _SHARE_DECIMALS),
        share_point=round(share_point, _SHARE_DECIMALS),
        share_max=round(share_max, _SHARE_DECIMALS),
        minor_portion=minor_portion,
        band_ft=round(band_ft, _DISTANCE_DECIMALS),
        combination_rule=COMBINATION_RULE,
        lot_accuracy=lot_accuracy.as_dict(),
        district_accuracy=district_accuracy.as_dict(),
        accuracy_basis_assumed=accuracy_basis_assumed,
        band_exceeds_feature_width=band_exceeds_feature_width,
        sensitivity_flip=sensitivity_flip,
        feature_ref=dict(feature_ref or {}),
        notes=(["band_exceeds_feature_width"] if band_exceeds_feature_width else []),
    )
