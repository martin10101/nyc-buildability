"""Focused tests for the extracted typed table-data model + normalization
vocabulary (M5-T049; DB-030f).

These import DIRECTLY from ``app.rules.named_street_override_table`` to prove the
value layer stands on its own after the pure extraction (no dependency on the
matcher; a one-directional matching -> table import chain). They cover BOTH halves
the DB-030f split placed here: the typed data model AND the pure normalization /
source-anchoring helpers that produce and compare its normalized values. The
unchanged M5-T039/T040 acceptance suite (``test_named_street_override.py``,
importing through the facade) remains the byte-identity behavior proof; these add
focused coverage of the moved boundary itself.
"""

from dataclasses import FrozenInstanceError

import pytest

from app.rules.named_street_override_table import (
    BOUNDARY_OPEN_QUESTION,
    SNAPSHOT_ID,
    AlternateWidthResult,
    MatchResult,
    MatchStatus,
    NamedStreetOverrideError,
    OverrideProvenance,
    OverrideQuery,
    _anchored_in,
    _bounded_repr,
    _collapse,
    _normalize_cd,
    _normalize_district,
    _Row,
    _word_bounded,
)

# -- typed data model ------------------------------------------------------

def test_module_identifiers():
    assert SNAPSHOT_ID == "zr-12-10"
    assert BOUNDARY_OPEN_QUESTION == "G6-Q3-boundary-cross-street-inclusive-exclusive"


def test_match_status_is_str_tristate():
    assert issubclass(MatchStatus, str)
    assert MatchStatus.MATCHED_OVERRIDE == "matched_override"
    assert MatchStatus.NOT_MATCHED == "not_matched"
    assert MatchStatus.INDETERMINATE == "indeterminate"
    assert {s.value for s in MatchStatus} == {
        "matched_override",
        "not_matched",
        "indeterminate",
    }


def test_error_is_runtime_error():
    assert issubclass(NamedStreetOverrideError, RuntimeError)


def test_override_query_defaults_and_frozen():
    q = OverrideQuery("Manhattan", 7, "Broadway")
    assert q.cross_street_from is None
    assert q.cross_street_to is None
    with pytest.raises(FrozenInstanceError):
        q.street_name = "changed"  # type: ignore[misc]


def test_result_dataclasses_defaults_and_provenance():
    prov = OverrideProvenance(
        snapshot_id="zr-12-10",
        snapshot_sha256="deadbeef",
        section_number="12-10",
        section_anchor="anchor",
        node_anchor=None,
        provision_id=None,
        matched_row_id=None,
        matched_row_verbatim=None,
    )
    mr = MatchResult(status=MatchStatus.INDETERMINATE, reason="r")
    assert mr.provision_id is None
    assert mr.provenance is None
    assert mr.open_legal_questions == ()

    aw = AlternateWidthResult(
        district="C5-3", coverage_class="professional_review_required", reason="r"
    )
    assert aw.provenance is None
    assert aw.open_legal_questions == ()

    carried = MatchResult(
        status=MatchStatus.MATCHED_OVERRIDE, reason="r", provenance=prov
    )
    assert carried.provenance is not None
    assert carried.provenance.snapshot_sha256 == "deadbeef"


def test_row_record_fields_and_frozen():
    row = _Row(
        row_id="broadway-cd7-w94-w97",
        borough="Manhattan",
        community_district=7,
        street_name="Broadway",
        frontage_from="West 94th Street",
        frontage_to="West 97th Street",
        norm_borough="manhattan",
        norm_street="broadway",
        norm_from="west 94th street",
        norm_to="west 97th street",
    )
    assert row.community_district == 7
    assert row.norm_street == "broadway"
    with pytest.raises(FrozenInstanceError):
        row.row_id = "changed"  # type: ignore[misc]


# -- normalization vocabulary ----------------------------------------------
# Moved here with the helpers they cover under the DB-030f split (they were the
# `matching`-side focused tests before the vocabulary was extracted to `table`).

def test_collapse_strips_collapses_and_casefolds():
    assert _collapse("  BROADWAY  ") == "broadway"
    assert _collapse("West   94th\tStreet") == "west 94th street"
    assert _collapse(None) == ""


def test_normalize_cd_accepts_int_and_single_run_strings():
    assert _normalize_cd(7) == 7
    assert _normalize_cd("CD 7") == 7
    assert _normalize_cd("Community District 3") == 3
    # fail-closed to None: ambiguous, non-numeric, boolean, or missing
    assert _normalize_cd("7 or 8") is None
    assert _normalize_cd("none") is None
    assert _normalize_cd(True) is None
    assert _normalize_cd(None) is None


def test_normalize_district_uppercases_and_drops_whitespace():
    assert _normalize_district("C5 - 3") == "C5-3"
    assert _normalize_district("c6-4") == "C6-4"
    assert _normalize_district(None) == ""


def test_word_bounded_requires_word_boundaries():
    source = "broadway between west 94th and west 97th streets"
    assert _word_bounded("west 94th", source) is True
    # a partial-word fragment must NOT anchor
    assert _word_bounded("est 94th", source) is False
    assert _word_bounded("", source) is False


def test_anchored_in_matches_full_and_street_type_core():
    source = "broadway between west 94th and west 97th streets"
    # full normalized form present
    assert _anchored_in("Broadway", source) is True
    # core form: "West 94th Street" -> "west 94th" anchors (singular "Street" gone)
    assert _anchored_in("West 94th Street", source) is True
    # a divergent locator does not anchor
    assert _anchored_in("Brooklyn", source) is False
    assert _anchored_in("", source) is False


def test_bounded_repr_bounds_long_input():
    short = _bounded_repr("Broadway")
    assert short == "'Broadway'"
    huge = "Z" * 5000
    bounded = _bounded_repr(huge)
    assert bounded.endswith("...(truncated)")
    assert len(bounded) < 100
    assert huge not in bounded
