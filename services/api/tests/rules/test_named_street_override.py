"""M5-T039 (DB-010) acceptance pack for the ZR 12-10 named-street override matcher.

Covers: Phase-0 source repair integrity (digest self-consistency, verbatim text
present, table quotes covered by the digest); STRUCTURED-FIELD source tracing
(every normalized row field and disposition validated against the pinned source
text, beyond quote-substring presence, plus the fail-closed guards that reject a
row whose fields diverge from the source); every named row; boundary cross-street
inclusive/exclusive ambiguity; wrong borough/CD; unknown street; documented
normalization (incl. the abbreviation limitation); the C5-3/C6-4/C6-6
alternate-width classification; exact provenance fields; determinism; the
MATCHED_OVERRIDE path (via an unconditional synthetic row); and fail-closed
snapshot-integrity errors.

Anti-tautology: expected digests are recomputed with hashlib, never restated as
literals; the real snapshot is loaded through the production loader; the
structured-field tracing test normalizes independently (a local ``_norm``), not
by reusing the module's own helpers.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from app.rules.named_street_override import (
    BOUNDARY_OPEN_QUESTION,
    AlternateWidthResult,
    MatchStatus,
    NamedStreetOverrideError,
    NamedStreetOverrideMatcher,
    OverrideQuery,
    load_default_matcher,
)
from app.rules.snapshots import SnapshotStore, load_snapshot_file

# test file: <root>/services/api/tests/rules/test_named_street_override.py
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DOCS_SNAPSHOT = (
    _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1" / "zr-12-10.snapshot.json"
)

_NAMED_PROVISION = "zr-12-10-named-street-wide"
_ALT_PROVISION = "zr-12-10-c-district-alternate-width"
_Q1 = "G6-Q1-park-qualifier-scope"
_Q2 = "G6-Q2-may-be-considered-permissive"


def _raw() -> dict:
    return json.loads(_DOCS_SNAPSHOT.read_text(encoding="utf-8"))


def _norm(text: str) -> str:
    """Independent normalization for the source-tracing test (strip, collapse
    internal whitespace, casefold) - deliberately NOT the module's own helper, so
    the test proves the structured fields trace to the source on its own terms."""
    return re.sub(r"\s+", " ", text.strip()).casefold()


@pytest.fixture(scope="module")
def snapshot():
    return load_snapshot_file(_DOCS_SNAPSHOT)


@pytest.fixture(scope="module")
def matcher(snapshot):
    return NamedStreetOverrideMatcher(snapshot)


# --------------------------------------------------------------------------
# Phase 0 — source repair integrity
# --------------------------------------------------------------------------

def test_phase0_digest_self_consistent():
    """content_digest_sha256 == sha256(verbatim_excerpt) (loader contract). If
    this fails it prints the correct digest to paste into the snapshot."""
    raw = _raw()
    excerpt = raw["verbatim_excerpt"]
    recomputed = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
    assert raw["content_digest_sha256"] == recomputed, (
        f"stored={raw['content_digest_sha256']} recomputed={recomputed}"
    )


def test_phase0_verbatim_text_carries_amendment(snapshot):
    excerpt = snapshot.verbatim_excerpt
    assert "Broadway between West 94th and West 97th Streets" in excerpt
    assert "Allen Street between Rivington and Delancey Streets" in excerpt
    assert "which are separated by mapped public park" in excerpt
    assert "In C5-3, C6-4 or C6-6 Districts" in excerpt
    assert "70 feet or more in width" in excerpt
    assert "A 'narrow street' is any street less than 75 feet wide." in excerpt


def test_phase0_table_quotes_are_digest_covered(snapshot):
    raw = snapshot.raw
    named_quote = raw["named_street_overrides"]["verbatim_source_quote"]
    alt_quote = raw["alternate_width_provisions"]["verbatim_source_quote"]
    assert named_quote in snapshot.verbatim_excerpt
    assert alt_quote in snapshot.verbatim_excerpt


def test_phase0_section_metadata_corrected(snapshot):
    assert snapshot.section_last_amended == "2026-03-26"


def test_bundled_copy_matches_canonical_or_absent():
    """After sync the packaged copy must be byte-identical to the canonical one;
    load_default_matcher then builds from the deployable bundle."""
    bundled = (
        _REPO_ROOT
        / "services"
        / "api"
        / "app"
        / "_zr_snapshots"
        / "v1"
        / "zr-12-10.snapshot.json"
    )
    if bundled.exists():
        assert bundled.read_bytes() == _DOCS_SNAPSHOT.read_bytes()
    matcher = load_default_matcher()
    result = matcher.match(
        OverrideQuery("Manhattan", 7, "Broadway", "West 94th Street", "West 97th Street")
    )
    assert result.status is MatchStatus.INDETERMINATE


# --------------------------------------------------------------------------
# Structured-field source tracing — every normalized row field and disposition
# is validated against the pinned source text, BEYOND quote-substring presence.
# --------------------------------------------------------------------------

def test_structured_row_fields_trace_to_source_quote(snapshot):
    """Beyond quote-substring presence: each structured row field traces to the
    named block's own verbatim_source_quote by an INDEPENDENT normalization, and
    the two real rows reconstruct - order-faithfully - into a phrase that is a
    literal substring of that quote. This is what proves the from/to
    decomposition (source 'Broadway between West 94th and West 97th Streets' ->
    frontage_from 'West 94th Street', frontage_to 'West 97th Street') was derived
    from the pinned text, not invented."""
    block = snapshot.raw["named_street_overrides"]
    source = _norm(block["verbatim_source_quote"])
    # The two rows must equal the accepted M4-T018 3.1 build-input spec exactly.
    expected = {
        "broadway-cd7-w94-w97": {
            "borough": "Manhattan",
            "community_district": 7,
            "street_name": "Broadway",
            "frontage_from": "West 94th Street",
            "frontage_to": "West 97th Street",
        },
        "allen-st-cd3-rivington-delancey": {
            "borough": "Manhattan",
            "community_district": 3,
            "street_name": "Allen Street",
            "frontage_from": "Rivington Street",
            "frontage_to": "Delancey Street",
        },
    }
    assert {r["row_id"] for r in block["rows"]} == set(expected)
    for row in block["rows"]:
        want = expected[row["row_id"]]
        assert {k: row[k] for k in want} == want
        # borough + community district appear in the source's own phrasing
        assert _norm(row["borough"]) in source
        assert f"community district {row['community_district']}" in source
        # street name appears; each frontage endpoint's core (minus " Street")
        # appears; and an order-faithful reconstruction is a literal substring.
        assert _norm(row["street_name"]) in source
        frm_core = _norm(row["frontage_from"]).removesuffix(" street")
        to_core = _norm(row["frontage_to"]).removesuffix(" street")
        assert frm_core in source
        assert to_core in source
        phrase = f"{_norm(row['street_name'])} between {frm_core} and {to_core} streets"
        assert phrase in source


def test_structured_field_divergent_from_source_fails_closed(tmp_path):
    """A row whose normalized field does NOT trace to the source quote fails
    closed at construction, even though the block quote IS present and
    digest-covered (the old quote-substring check alone would have passed)."""
    named_quote = (
        "In Community District 7 in the Borough of Manhattan, the roadways of "
        "Broadway between West 94th and West 97th Streets shall each be "
        "considered a wide street."
    )
    alt_quote = "In C5-3 Districts the alternate-width test may be considered."
    excerpt = named_quote + "\n\n" + alt_quote
    named = {
        "provision_id": "p",
        "section_anchor": "a",
        "node_anchor": "/node/0",
        "verbatim_source_quote": named_quote,
        "disposition_when_located": "indeterminate",
        "disposition_reason": "r",
        "open_legal_questions": [],
        "rows": [
            {
                # borough diverges from the source ("Manhattan") -> fail closed
                "row_id": "tampered",
                "borough": "Brooklyn",
                "community_district": 7,
                "street_name": "Broadway",
                "frontage_from": "West 94th Street",
                "frontage_to": "West 97th Street",
            }
        ],
    }
    alt = {
        "provision_id": "p2",
        "section_anchor": "a",
        "applicable_districts": ["C5-3"],
        "verbatim_source_quote": alt_quote,
        "disposition_reason": "r",
    }
    snap = _synthetic(tmp_path, excerpt=excerpt, named=named, alt=alt, snapshot_id="zr-tamper")
    # the block quote IS a digest-covered substring (old check passes)...
    assert named_quote in snap.verbatim_excerpt
    # ...but the divergent borough fails the new source-anchoring check.
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_alternate_width_district_absent_from_source_fails_closed(tmp_path):
    """An applicable alternate-width district not present in that block's own
    verbatim_source_quote fails closed at construction."""
    named_quote = (
        "In Community District 7 in the Borough of Manhattan, the roadways of "
        "Broadway between West 94th and West 97th Streets shall each be "
        "considered a wide street."
    )
    alt_quote = "In C5-3 Districts the alternate-width test may be considered."
    excerpt = named_quote + "\n\n" + alt_quote
    named = {
        "provision_id": "p",
        "section_anchor": "a",
        "verbatim_source_quote": named_quote,
        "disposition_when_located": "indeterminate",
        "disposition_reason": "r",
        "rows": [],
    }
    alt = {
        "provision_id": "p2",
        "section_anchor": "a",
        "applicable_districts": ["C5-3", "C9-9"],  # C9-9 is absent from the quote
        "verbatim_source_quote": alt_quote,
        "disposition_reason": "r",
    }
    snap = _synthetic(tmp_path, excerpt=excerpt, named=named, alt=alt, snapshot_id="zr-altbad")
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_unrecognized_disposition_fails_closed(tmp_path):
    """A located-row disposition outside the recognized vocabulary fails closed
    rather than being silently coerced to INDETERMINATE."""
    named_quote = (
        "In Community District 7 in the Borough of Manhattan, the roadways of "
        "Broadway between West 94th and West 97th Streets shall each be "
        "considered a wide street."
    )
    alt_quote = "In C5-3 Districts the alternate-width test may be considered."
    excerpt = named_quote + "\n\n" + alt_quote
    named = {
        "provision_id": "p",
        "section_anchor": "a",
        "verbatim_source_quote": named_quote,
        "disposition_when_located": "auto_match",  # not a recognized disposition
        "disposition_reason": "r",
        "rows": [],
    }
    alt = {
        "provision_id": "p2",
        "section_anchor": "a",
        "applicable_districts": ["C5-3"],
        "verbatim_source_quote": alt_quote,
        "disposition_reason": "r",
    }
    snap = _synthetic(tmp_path, excerpt=excerpt, named=named, alt=alt, snapshot_id="zr-dispbad")
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


# --------------------------------------------------------------------------
# AS-1 — every named row is located and carries provision id + verbatim row
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "borough,cd,street,frm,to,row_id",
    [
        (
            "Manhattan", 7, "Broadway", "West 94th Street", "West 97th Street",
            "broadway-cd7-w94-w97",
        ),
        (
            "Manhattan", 3, "Allen Street", "Rivington Street", "Delancey Street",
            "allen-st-cd3-rivington-delancey",
        ),
    ],
)
def test_as1_named_rows_located_indeterminate_with_provenance(
    matcher, snapshot, borough, cd, street, frm, to, row_id
):
    result = matcher.match(OverrideQuery(borough, cd, street, frm, to))
    # Conservative refusal: located, but the mapped-public-park predicate is
    # unverifiable and its scope is an open legal question (G6-Q1).
    assert result.status is MatchStatus.INDETERMINATE
    assert result.provision_id == _NAMED_PROVISION
    assert result.provenance is not None
    assert result.provenance.matched_row_id == row_id
    expected_quote = snapshot.raw["named_street_overrides"]["verbatim_source_quote"]
    assert result.provenance.matched_row_verbatim == expected_quote
    assert _Q1 in result.open_legal_questions


# --------------------------------------------------------------------------
# AS-2 — boundary cross-street resolution
# --------------------------------------------------------------------------

def test_as2_exact_designated_pair_is_located_order_independent(matcher):
    forward = matcher.match(
        OverrideQuery("Manhattan", 7, "Broadway", "West 94th Street", "West 97th Street")
    )
    reversed_ = matcher.match(
        OverrideQuery("Manhattan", 7, "Broadway", "West 97th Street", "West 94th Street")
    )
    assert forward.status is MatchStatus.INDETERMINATE
    assert reversed_.status is MatchStatus.INDETERMINATE
    assert forward.provenance.matched_row_id == reversed_.provenance.matched_row_id


def test_as2_shared_boundary_is_indeterminate_with_boundary_question(matcher):
    result = matcher.match(
        OverrideQuery("Manhattan", 7, "Broadway", "West 97th Street", "West 100th Street")
    )
    assert result.status is MatchStatus.INDETERMINATE
    assert BOUNDARY_OPEN_QUESTION in result.open_legal_questions
    assert result.provision_id == _NAMED_PROVISION
    assert result.provenance is not None


def test_as2_disjoint_segment_is_not_matched(matcher):
    result = matcher.match(
        OverrideQuery("Manhattan", 7, "Broadway", "West 100th Street", "West 103rd Street")
    )
    assert result.status is MatchStatus.NOT_MATCHED
    assert result.provenance is None


# --------------------------------------------------------------------------
# AS-3 — unknown / wrong / malformed inputs: NOT_MATCHED or INDETERMINATE,
# never an exception, never a match
# --------------------------------------------------------------------------

def test_as3_unknown_street_not_matched(matcher):
    result = matcher.match(
        OverrideQuery("Manhattan", 7, "Elm Street", "A Street", "B Street")
    )
    assert result.status is MatchStatus.NOT_MATCHED


def test_as3_wrong_cd_not_matched(matcher):
    result = matcher.match(
        OverrideQuery("Manhattan", 1, "Broadway", "West 94th Street", "West 97th Street")
    )
    assert result.status is MatchStatus.NOT_MATCHED


def test_as3_wrong_borough_not_matched(matcher):
    result = matcher.match(
        OverrideQuery("Brooklyn", 7, "Broadway", "West 94th Street", "West 97th Street")
    )
    assert result.status is MatchStatus.NOT_MATCHED


@pytest.mark.parametrize(
    "query",
    [
        OverrideQuery("", 7, "Broadway", "West 94th Street", "West 97th Street"),
        OverrideQuery("Manhattan", 7, "", "West 94th Street", "West 97th Street"),
        OverrideQuery(
            "Manhattan", "not-a-number", "Broadway", "West 94th Street", "West 97th Street"
        ),
        OverrideQuery("Manhattan", 7, "Broadway", None, "West 97th Street"),
        OverrideQuery("Manhattan", 7, "Broadway", "West 94th Street", "West 94th Street"),
    ],
    ids=["blank-borough", "blank-street", "bad-cd", "missing-bound", "degenerate"],
)
def test_as3_malformed_inputs_are_indeterminate(matcher, query):
    result = matcher.match(query)
    assert result.status is MatchStatus.INDETERMINATE


def test_as3_never_raises_and_never_false_matches(matcher):
    for query in [
        OverrideQuery("Queens", 7, "Broadway", "West 94th Street", "West 97th Street"),
        OverrideQuery("Manhattan", 7, "Allen Street", "Rivington Street", "Delancey Street"),
        OverrideQuery("Manhattan", 99, "Allen Street", "Rivington Street", "Delancey Street"),
    ]:
        result = matcher.match(query)
        assert result.status is not MatchStatus.MATCHED_OVERRIDE


# --------------------------------------------------------------------------
# Documented normalization
# --------------------------------------------------------------------------

def test_normalization_case_and_whitespace(matcher):
    result = matcher.match(
        OverrideQuery(
            "  manHATTAN ", "CD 7", "  BROADWAY  ", "west 94th street", "WEST 97TH STREET"
        )
    )
    assert result.status is MatchStatus.INDETERMINATE
    assert result.provenance.matched_row_id == "broadway-cd7-w94-w97"


def test_normalization_no_abbreviation_expansion_is_not_matched(matcher):
    # "Allen St" is not exactly "Allen Street"; no fuzzy/abbrev matching.
    result = matcher.match(
        OverrideQuery("Manhattan", 3, "Allen St", "Rivington Street", "Delancey Street")
    )
    assert result.status is MatchStatus.NOT_MATCHED


def test_community_district_string_forms(matcher):
    for cd in [7, "7", "CD7", "CD 7", "Community District 7"]:
        result = matcher.match(
            OverrideQuery("Manhattan", cd, "Broadway", "West 94th Street", "West 97th Street")
        )
        assert result.provenance is not None
        assert result.provenance.matched_row_id == "broadway-cd7-w94-w97"


# --------------------------------------------------------------------------
# Alternate-width (C5-3/C6-4/C6-6)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("district", ["C5-3", "c6-4", "C6 - 6"])
def test_alternate_width_applicable_districts(matcher, snapshot, district):
    result = matcher.classify_alternate_width_district(district)
    assert isinstance(result, AlternateWidthResult)
    assert result.coverage_class == "professional_review_required"
    assert result.provision_id == _ALT_PROVISION
    assert result.provenance is not None
    assert result.provenance.snapshot_sha256 == snapshot.content_digest_sha256
    assert _Q2 in result.open_legal_questions


@pytest.mark.parametrize("district", ["R6", "C1-1", "", None])
def test_alternate_width_non_applicable_districts(matcher, district):
    result = matcher.classify_alternate_width_district(district)
    assert result.coverage_class == "not_applicable"
    assert result.provenance is None


# --------------------------------------------------------------------------
# AS-4 — provenance fields exact on every non-NOT_MATCHED result
# --------------------------------------------------------------------------

def test_as4_provenance_carries_sha_and_anchor(matcher, snapshot):
    non_not_matched = [
        matcher.match(
            OverrideQuery("Manhattan", 7, "Broadway", "West 94th Street", "West 97th Street")
        ),
        matcher.match(
            OverrideQuery("Manhattan", 7, "Broadway", "West 97th Street", "West 100th Street")
        ),
        matcher.match(
            OverrideQuery("", 7, "Broadway", "West 94th Street", "West 97th Street")
        ),
    ]
    for result in non_not_matched:
        assert result.status is not MatchStatus.NOT_MATCHED
        assert result.provenance is not None
        assert result.provenance.snapshot_sha256 == snapshot.content_digest_sha256
        assert result.provenance.section_anchor
        assert result.provenance.section_number == "12-10"


def test_not_matched_has_no_provenance(matcher):
    result = matcher.match(OverrideQuery("Manhattan", 7, "Nowhere Road", "A", "B"))
    assert result.status is MatchStatus.NOT_MATCHED
    assert result.provenance is None


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------

def test_determinism_same_input_same_output(matcher):
    query = OverrideQuery("Manhattan", 3, "Allen Street", "Rivington Street", "Delancey Street")
    assert matcher.match(query) == matcher.match(query)
    alt_a = matcher.classify_alternate_width_district("C5-3")
    alt_b = matcher.classify_alternate_width_district("C5-3")
    assert alt_a == alt_b


# --------------------------------------------------------------------------
# MATCHED_OVERRIDE path + snapshot-integrity fail-closed (synthetic snapshots)
# --------------------------------------------------------------------------

def _synthetic(tmp_path, *, excerpt, named, alt, snapshot_id="zr-test"):
    doc = {
        "snapshot_id": snapshot_id,
        "section_number": "12-10",
        "section_title": "synthetic",
        "source": {"request_url": "u", "retrieved_at": "t", "raw_html_verified": False},
        "verbatim_excerpt": excerpt,
        "content_digest_sha256": hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
        "extraction_status": "extracted_draft",
        "named_street_overrides": named,
        "alternate_width_provisions": alt,
    }
    path = tmp_path / f"{snapshot_id}.snapshot.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return load_snapshot_file(path)


def test_matched_override_for_unconditional_row(tmp_path):
    # Source-shaped synthetic quote so every structured row field anchors in it
    # (the new source-tracing guard) while the row stays an unconditional match.
    named_quote = (
        "In Community District 1 in the Borough of Testville, the roadways of "
        "Testonly Avenue between First and Second Streets shall each be "
        "considered a wide street."
    )
    alt_quote = "In C5-3 Districts the alternate-width test may be considered."
    excerpt = named_quote + "\n\n" + alt_quote
    named = {
        "provision_id": "test-named",
        "section_anchor": "test anchor",
        "node_anchor": "/node/0",
        "verbatim_source_quote": named_quote,
        "disposition_when_located": "matched_override",
        "open_legal_questions": [],
        "rows": [
            {
                "row_id": "testonly",
                "borough": "Testville",
                "community_district": 1,
                "street_name": "Testonly Avenue",
                "frontage_from": "First Street",
                "frontage_to": "Second Street",
            }
        ],
    }
    alt = {
        "provision_id": "test-alt",
        "section_anchor": "test anchor",
        "applicable_districts": ["C5-3"],
        "verbatim_source_quote": alt_quote,
        "disposition_reason": "test",
        "open_legal_questions": [],
    }
    snap = _synthetic(tmp_path, excerpt=excerpt, named=named, alt=alt)
    matcher = NamedStreetOverrideMatcher(snap)
    result = matcher.match(
        OverrideQuery("Testville", 1, "Testonly Avenue", "First Street", "Second Street")
    )
    assert result.status is MatchStatus.MATCHED_OVERRIDE
    assert result.provision_id == "test-named"
    assert result.provenance is not None
    assert result.provenance.matched_row_verbatim == named_quote


def test_integrity_missing_table_block_raises(tmp_path):
    excerpt = "some text"
    doc = {
        "snapshot_id": "zr-missing",
        "section_number": "12-10",
        "verbatim_excerpt": excerpt,
        "content_digest_sha256": hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
        "source": {"raw_html_verified": False},
    }
    path = tmp_path / "zr-missing.snapshot.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    snap = load_snapshot_file(path)
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_integrity_quote_not_in_excerpt_raises(tmp_path):
    excerpt = "this excerpt does not contain the table quote"
    named = {
        "provision_id": "p",
        "section_anchor": "a",
        "verbatim_source_quote": "a quote absent from the excerpt",
        "disposition_when_located": "indeterminate",
        "disposition_reason": "r",
        "rows": [],
    }
    alt = {
        "provision_id": "p2",
        "section_anchor": "a",
        "applicable_districts": [],
        "verbatim_source_quote": "this excerpt does not contain the table quote",
        "disposition_reason": "r",
    }
    snap = _synthetic(tmp_path, excerpt=excerpt, named=named, alt=alt, snapshot_id="zr-bad")
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


# --------------------------------------------------------------------------
# Default store is loadable (the M4-T005 deployability contract still holds).
# --------------------------------------------------------------------------

def test_default_store_has_repaired_snapshot():
    snap = SnapshotStore().get("zr-12-10")
    assert "named_street_overrides" in snap.raw
