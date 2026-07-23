"""Shared, deterministic input builders for the scenario acceptance pack
(task M5-T001).

Every helper returns FRESH deep copies so a test can mutate its input without
leaking into another test. The canonical starting point is the committed
rule_evaluation valid fixture (the exported evaluate_property shape), so the
acceptance pack proves the builder against the same payload shape the rule
engine actually emits.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
CANONICAL_RULE_EVALUATION = (
    FIXTURE_ROOT / "valid" / "rule_evaluation" / "supported_family_draft.json"
)

# A minimal property_profile whose provenance array resolves the lot-area
# provenance_ref carried by the canonical rule_evaluation input_provenance.
PROFILE: dict[str, Any] = {
    "identity": {"bbl": "1000477501"},
    "provenance": [
        {
            "provenance_id": "prov-lotgeom",
            "source_id": "nyc-dcp-lot-geometry",
            "dataset_version": "26v1",
            "original_field_name": "area_sq_ft",
            "effective_date": None,
        },
        {
            "provenance_id": "prov-spatial-nyzd",
            "source_id": "nyc-dcp-nyzd",
            "dataset_version": "26v1",
            "original_field_name": "zoning_district",
            "effective_date": None,
        },
    ],
}


def profile() -> dict:
    return copy.deepcopy(PROFILE)


def canonical_rule_evaluation() -> dict:
    return json.loads(CANONICAL_RULE_EVALUATION.read_text(encoding="utf-8"))


def trace_cap(rule_evaluation: dict) -> float:
    """The canonical trace output the builder must surface verbatim."""
    return rule_evaluation["evaluations"][0]["outputs"][
        "max_residential_floor_area_sq_ft"
    ]


# ---------------------------------------------------------------------------
# Variant builders
# ---------------------------------------------------------------------------


def unsupported_rule_evaluation() -> dict:
    re = canonical_rule_evaluation()
    re["coverage_status"] = "unsupported"
    re["zoning_district"] = "M1-1"
    re["evaluations"] = []
    re["family_coverage"] = {
        "family": "residential_far",
        "coverage_status": "unsupported",
        "note": "no implemented rule family for this district",
    }
    return re


def not_applicable_rule_evaluation() -> dict:
    re = canonical_rule_evaluation()
    re["coverage_status"] = "not_applicable"
    re["zoning_district"] = "C8-1"
    re["evaluations"] = []
    re["family_coverage"] = {
        "family": "residential_far",
        "coverage_status": "not_applicable",
        "note": "family not applicable for this district",
    }
    return re


def conflict_rule_evaluation() -> dict:
    re = canonical_rule_evaluation()
    re["coverage_status"] = "data_conflict"
    re["fail_safe"] = True
    re["fail_safe_reason"] = "rule_conflict"
    re["evaluations"] = []
    re["rule_conflict"] = {
        "conflict": True,
        "family": "residential_far",
        "as_of_date": None,
        "competing_output_names": ["max_residential_floor_area_sq_ft"],
        "competing_rules": [
            {
                "rule_id": "r5-residential-far",
                "rule_version": "0.1.0-draft",
                "effective_from": "2024-12-05",
                "effective_to": None,
                "output_names": ["max_residential_floor_area_sq_ft"],
            },
            {
                "rule_id": "r5-residential-far-alt",
                "rule_version": "0.2.0-draft",
                "effective_from": "2024-12-05",
                "effective_to": None,
                "output_names": ["max_residential_floor_area_sq_ft"],
            },
        ],
        "note": "two same-family rules simultaneously in effect for the same output",
    }
    return re


def professional_review_rule_evaluation() -> dict:
    re = canonical_rule_evaluation()
    re["coverage_status"] = "professional_review_required"
    re["professional_review_required"] = True
    re["fail_safe"] = True
    re["fail_safe_reason"] = "geometry_uncertain"
    re["evaluations"] = []
    re["spatial_uncertainty"] = {
        "lot_overall_class": "split_lot",
        "professional_review_required": True,
        "coverage_note": "lot spans two base districts; shares uncertain",
        "review_reasons": ["split_lot", "boundary_uncertain"],
        "notes": [],
        "base_district_candidates": [
            {
                "district_label": "R5",
                "pair_class": "boundary_uncertain",
                "share_min": 0.4,
                "share_point": 0.55,
                "share_max": 0.7,
                "minor_portion": False,
            },
            {
                "district_label": "R6",
                "pair_class": "boundary_uncertain",
                "share_min": 0.3,
                "share_point": 0.45,
                "share_max": 0.6,
                "minor_portion": True,
            },
        ],
        "crosscheck": None,
    }
    return re


def missing_lot_area_rule_evaluation() -> dict:
    """R5 family conditional, but no lot area and no computed cap - a required
    controlling input is absent."""
    re = canonical_rule_evaluation()
    re["lot_area_sq_ft"] = None
    re["lot_area_source"] = None
    re["evaluations"][0]["outputs"] = {"max_residential_far": 1.5}
    return re


def integrity_disagreement_rule_evaluation() -> dict:
    """Canonical trace cap kept at 15000, but the top-level lot area used for the
    scenario is changed so that far * lot_area no longer equals the trace cap -
    forcing the verification-only integrity check to fail closed."""
    re = canonical_rule_evaluation()
    re["lot_area_sq_ft"] = 20000.0  # far(1.5) * 20000 = 30000 != trace cap 15000
    return re


def malformed_rule_evaluation(field: str, value: Any) -> dict:
    """Inject a malformed numeric into either the top-level lot area or the trace
    cap/far output. ``field`` is 'lot_area_sq_ft', 'max_residential_floor_area_sq_ft',
    or 'max_residential_far'."""
    re = canonical_rule_evaluation()
    if field == "lot_area_sq_ft":
        re["lot_area_sq_ft"] = value
    else:
        re["evaluations"][0]["outputs"][field] = value
    return re
