"""Versioned positional-accuracy provenance and tolerance-combination policy
for the M2-T013 spatial-intersection engine.

Everything here implements the owner-approved policy recorded in
``project-control/reports/M2-T013-geospatial-policy-advisory.md`` and the owner
decisions C1-C4 (2026-07-20):

* **C1** tolerance combination = **linear sum** (advisory 2.2): the compound
  band is ``lot_accuracy_ft + district_accuracy_ft``. Root-sum-square is
  deliberately NOT used - the two products share cadastral lineage (errors may
  be correlated) and "+/- 20 ft" is a stated bound, not a 1-sigma value; RSS
  would manufacture confidence from an undocumented statistical assumption.
* **C2** ZTLDB agreement may upgrade a geometrically uncertain *displayed*
  result to CONDITIONAL only, never confident/verified (handled in
  ``crosscheck``).
* **C3** no sliver suppression - the sliver floor is band-derived (firm area > 0
  after erosion); firm portions below ``MINOR_PORTION_SHARE`` are FLAGGED
  ``minor_portion`` and never dropped (handled in ``geometry``/``engine``).
* **C4** split percentages display as point + range (handled in ``geometry``).

Accuracy is modelled as a first-class provenance record per input geometry
(advisory 2.1), never a bare constant. The ``basis`` field records whether the
figure is ``documented`` (read from an official metadata document) or
``assumed`` (undocumented; propagated visibly and made to fail safe by the 2x
sensitivity trigger in ``geometry``). The honest current values below reflect
the repo state at task start; the V1/V2 in-task verification updates the
``documented``/``assumed`` split and citations where officials publish a figure.
"""

from __future__ import annotations

from dataclasses import dataclass

# Stable policy identifier stamped on every emitted record so a future,
# evidence-backed change (e.g. a switch to RSS if DCP ever publishes error
# statistics) is a versioned policy change, never a silent recalibration.
POLICY_VERSION = "M2-T013-spatial-policy-1"

# C1: tolerance combination rule.
COMBINATION_RULE = "linear_sum"

# Default per-input horizontal accuracy. The official nyzd metadata states
# "+/- 20 feet"; MapPLUTO and the five other zoning-features layers inherit the
# same value as an ASSUMED figure until their own metadata is verified (V1/V2).
DEFAULT_ACCURACY_FT = 20.0

# C3: a district's firm (eroded) share below this fraction of lot area is
# FLAGGED ``minor_portion`` - never suppressed. 2% per the advisory default.
MINOR_PORTION_SHARE = 0.02

# Advisory 2.6.7: reclassify once at this multiple of the band; if the class
# flips while an ``assumed`` accuracy participates, the result is escalated to
# professional review. This makes the undocumented-accuracy gap fail safe.
SENSITIVITY_BAND_MULTIPLIER = 2.0

# Area epsilon (sq ft) below which a coverage gap/overlap is treated as float
# noise rather than a topology signal. Far below the >=400 sq ft scale of any
# real NYC lot feature and the >=1600 sq ft (20 ft)^2 band-area scale.
AREA_EPSILON_SQ_FT = 1.0

# Zoning-features layer -> semantic family. Coverage/gap/overlap are computed
# WITHIN a family only (owner amendment invariant 1); cross-family stacking is
# legitimate and never a topology defect (invariant 2).
LAYER_FAMILY = {
    "nyzd": "base_zoning",
    "nyco": "commercial_overlay",
    "nysp": "special_purpose_district",
    "nysp_sd": "special_purpose_subdistrict",
    "nylh": "limited_height_district",
    "nyzma": "zoning_map_amendment",
}

# Only base zoning is expected to fully cover a lot; for every other family the
# ABSENCE of a feature is not "unassigned area" (invariants 3, 4). This drives
# whether a same-family gap is emitted as ``unassigned_area``.
FAMILY_COVERAGE_EXPECTATION = {
    "base_zoning": "expected_full_coverage",
    "commercial_overlay": "selective_no_gap_expectation",
    "special_purpose_district": "selective_no_gap_expectation",
    "special_purpose_subdistrict": "selective_no_gap_expectation",
    "limited_height_district": "selective_no_gap_expectation",
    "zoning_map_amendment": "selective_no_gap_expectation",
}


@dataclass(frozen=True)
class SourceAccuracy:
    """First-class positional-accuracy provenance record for one input
    geometry (advisory 2.1). ``basis`` is ``documented`` (an official metadata
    figure) or ``assumed`` (undocumented, propagated visibly)."""

    value_ft: float
    basis: str  # "documented" | "assumed"
    citation: str
    applies_to: str  # source_id + layer
    verified_at: str | None = None

    def __post_init__(self) -> None:
        if self.basis not in ("documented", "assumed"):
            raise ValueError(f"accuracy basis must be documented|assumed: {self.basis!r}")
        if not (self.value_ft > 0.0):
            raise ValueError(f"accuracy value_ft must be positive: {self.value_ft!r}")

    def as_dict(self) -> dict:
        return {
            "value_ft": self.value_ft,
            "basis": self.basis,
            "citation": self.citation,
            "applies_to": self.applies_to,
            "verified_at": self.verified_at,
        }


# ---------------------------------------------------------------------------
# Honest current accuracy registry (advisory 2.1 table). Updated by the V1/V2
# in-task verification: where an official figure is located the entry becomes
# ``basis="documented"`` with the citation + verified_at; where officials
# publish none, ``basis="assumed"`` is the permanent, visible finding.
# ---------------------------------------------------------------------------

# nyzd: the one DOCUMENTED figure (nyzd metadata PDF, verbatim "+/- 20 feet",
# research line 149, G1-confirmed OQ-10).
_NYZD_DOCUMENTED_CITATION = (
    "NYC DCP zoning-features nyzd metadata (Data Quality section), verbatim "
    '"The estimated horizontal accuracy is +/- 20 feet"; '
    "docs/research/zoning-features-ztldb-2026-07-16.md line 149 (G1-confirmed)."
)
_ASSUMED_LAYER_CITATION = (
    "ASSUMED equal to the documented nyzd +/- 20 ft: per-layer metadata not "
    "confirmed to publish a positional-accuracy figure (V2). Basis stays "
    "'assumed' and fails safe via the 2x-band sensitivity trigger until an "
    "official per-layer figure is verified."
)
_MAPPLUTO_ASSUMED_CITATION = (
    "ASSUMED +/- 20 ft: no positional-accuracy figure is published for "
    "MapPLUTO/DTM in the located official metadata (V1). MapPLUTO derives from "
    "the DCP-modified DOF Digital Tax Map; the 20 ft is an analogy to nyzd, not "
    "a documented MapPLUTO figure. Basis stays 'assumed' and fails safe."
)

_LAYER_ACCURACY: dict[str, SourceAccuracy] = {
    "nyzd": SourceAccuracy(
        value_ft=DEFAULT_ACCURACY_FT,
        basis="documented",
        citation=_NYZD_DOCUMENTED_CITATION,
        applies_to="nyc-dcp-zoning-features:nyzd",
        verified_at="2026-07-16",
    ),
}
for _assumed_layer in ("nyco", "nysp", "nysp_sd", "nylh", "nyzma"):
    _LAYER_ACCURACY[_assumed_layer] = SourceAccuracy(
        value_ft=DEFAULT_ACCURACY_FT,
        basis="assumed",
        citation=_ASSUMED_LAYER_CITATION,
        applies_to=f"nyc-dcp-zoning-features:{_assumed_layer}",
        verified_at=None,
    )

MAPPLUTO_LOT_ACCURACY = SourceAccuracy(
    value_ft=DEFAULT_ACCURACY_FT,
    basis="assumed",
    citation=_MAPPLUTO_ASSUMED_CITATION,
    applies_to="nyc-dcp-mappluto-arcgis:MAPPLUTO",
    verified_at=None,
)


def layer_accuracy(layer: str) -> SourceAccuracy:
    """Return the honest per-layer district accuracy record. Unknown layers
    fail safe as an ``assumed`` 20 ft rather than silently trusting them."""
    known = _LAYER_ACCURACY.get(layer)
    if known is not None:
        return known
    return SourceAccuracy(
        value_ft=DEFAULT_ACCURACY_FT,
        basis="assumed",
        citation=(
            f"ASSUMED +/- 20 ft: layer {layer!r} is not in the verified "
            "zoning-features accuracy registry."
        ),
        applies_to=f"nyc-dcp-zoning-features:{layer}",
        verified_at=None,
    )


def combined_band_ft(lot_accuracy: SourceAccuracy, district_accuracy: SourceAccuracy) -> float:
    """C1 linear-sum compound band. Both geometries are uncertain, so the band
    that guards a lot-vs-district test is the sum of the two stated bounds."""
    return float(lot_accuracy.value_ft) + float(district_accuracy.value_ft)


def family_for_layer(layer: str) -> str:
    """Semantic family for a zoning-features layer (unknown -> its own name so
    coverage never crosses families)."""
    return LAYER_FAMILY.get(layer, layer)


def policy_snapshot() -> dict:
    """Immutable record of the policy constants stamped onto every result so a
    stored record is fully reproducible and self-describing."""
    return {
        "policy_version": POLICY_VERSION,
        "combination_rule": COMBINATION_RULE,
        "default_accuracy_ft": DEFAULT_ACCURACY_FT,
        "minor_portion_share": MINOR_PORTION_SHARE,
        "sensitivity_band_multiplier": SENSITIVITY_BAND_MULTIPLIER,
        "area_epsilon_sq_ft": AREA_EPSILON_SQ_FT,
    }
