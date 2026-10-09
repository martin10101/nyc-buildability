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


# --------------------------------------------------------------------------
# DB-023 hardening (M5-T040): (a) structural refusal of matched_override on a
# row carrying an unresolved qualifier; (b) construction-time provenance-field
# validation so match() never KeyErrors; (c) bounded raw-query reprs in reasons;
# (d) word-boundary source anchoring.
# --------------------------------------------------------------------------

_SOURCE_SHAPED_NAMED_QUOTE = (
    "In Community District 1 in the Borough of Testville, the roadways of "
    "Testonly Avenue between First and Second Streets shall each be "
    "considered a wide street."
)
_SOURCE_SHAPED_ALT_QUOTE = "In C5-3 Districts the alternate-width test may be considered."


def _named_block(**overrides) -> dict:
    """A source-tracing-clean named block (every row field anchors in the quote),
    with individual fields overridable for the DB-023 fail-closed probes."""
    block = {
        "provision_id": "test-named",
        "section_anchor": "test anchor",
        "node_anchor": "/node/0",
        "verbatim_source_quote": _SOURCE_SHAPED_NAMED_QUOTE,
        "disposition_when_located": "indeterminate",
        "disposition_reason": "r",
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
    block.update(overrides)
    return block


def _alt_block(**overrides) -> dict:
    block = {
        "provision_id": "test-alt",
        "section_anchor": "test anchor",
        "applicable_districts": ["C5-3"],
        "verbatim_source_quote": _SOURCE_SHAPED_ALT_QUOTE,
        "disposition_reason": "r",
    }
    block.update(overrides)
    return block


def _excerpt() -> str:
    return _SOURCE_SHAPED_NAMED_QUOTE + "\n\n" + _SOURCE_SHAPED_ALT_QUOTE


def test_db023a_matched_override_with_open_question_fails_closed(tmp_path):
    """AS-1 (DB-023a): flipping a qualifier-carrying row (a non-empty
    open_legal_questions - here the mapped-public-park predicate) to
    matched_override is refused STRUCTURALLY at construction; the disposition is
    outside the digest cover, so an unverifiable qualifier can never read as an
    unconditional override."""
    named = _named_block(
        disposition_when_located="matched_override",
        open_legal_questions=["G6-Q1-park-qualifier-scope"],
    )
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=named, alt=_alt_block(), snapshot_id="zr-db023a"
    )
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_db023a_matched_override_without_open_question_still_allowed(tmp_path):
    """The structural refusal is scoped: an unconditional row (NO open legal
    question) still reaches MATCHED_OVERRIDE (regression guard on DB-023a)."""
    named = _named_block(
        disposition_when_located="matched_override", open_legal_questions=[]
    )
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=named, alt=_alt_block(), snapshot_id="zr-db023a-ok"
    )
    matcher = NamedStreetOverrideMatcher(snap)
    result = matcher.match(
        OverrideQuery("Testville", 1, "Testonly Avenue", "First Street", "Second Street")
    )
    assert result.status is MatchStatus.MATCHED_OVERRIDE


@pytest.mark.parametrize(
    "block_kwargs,which",
    [
        ({"provision_id": None}, "named"),
        ({"section_anchor": None}, "named"),
        ({"provision_id": 7}, "named"),  # mistyped (not a str)
        ({"section_anchor": ""}, "named"),  # empty
    ],
)
def test_db023b_missing_or_mistyped_provenance_fails_closed(tmp_path, block_kwargs, which):
    """AS-2 (DB-023b): a block missing/mistyping provision_id or section_anchor
    fails CLOSED at construction so match() can never KeyError."""
    named = _named_block(**block_kwargs) if which == "named" else _named_block()
    alt = _alt_block() if which == "named" else _alt_block(**block_kwargs)
    # Remove a key entirely when the override value is None (missing, not null).
    for k, v in list(block_kwargs.items()):
        if v is None:
            (named if which == "named" else alt).pop(k, None)
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=named, alt=alt, snapshot_id="zr-db023b"
    )
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_db023b_alt_block_missing_provenance_fails_closed(tmp_path):
    alt = _alt_block()
    alt.pop("provision_id")
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=_named_block(), alt=alt, snapshot_id="zr-db023b-alt"
    )
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_db023c_reason_bounds_long_query_input(matcher):
    """AS-3 (DB-023c): a MatchResult.reason never embeds an unbounded raw-query
    repr. A 5000-char street name and cross streets produce a bounded reason."""
    huge = "Z" * 5000
    # unknown-street path embeds the street repr
    r1 = matcher.match(OverrideQuery("Manhattan", 7, huge, "A Street", "B Street"))
    assert r1.status is MatchStatus.NOT_MATCHED
    assert len(r1.reason) < 300
    assert huge not in r1.reason
    # outside-frontage path embeds both cross-street reprs
    r2 = matcher.match(OverrideQuery("Manhattan", 7, "Broadway", huge, "Z" * 4000))
    assert len(r2.reason) < 400
    assert huge not in r2.reason
    # wrong-CD path embeds the street + borough reprs
    r3 = matcher.match(OverrideQuery(huge, 7, huge, "West 94th Street", "West 97th Street"))
    assert len(r3.reason) < 400


def test_db023d_partial_word_field_does_not_anchor(tmp_path):
    """DB-023d: a structured field that would match the source only as a
    partial-word substring ('roadway' inside 'Broadway') no longer anchors, so
    it fails closed at construction (word-boundary anchoring)."""
    named_quote = (
        "In Community District 7 in the Borough of Manhattan, the roadways of "
        "Broadway between West 94th and West 97th Streets shall each be "
        "considered a wide street."
    )
    excerpt = named_quote + "\n\n" + _SOURCE_SHAPED_ALT_QUOTE
    named = {
        "provision_id": "p",
        "section_anchor": "a",
        "verbatim_source_quote": named_quote,
        "disposition_when_located": "indeterminate",
        "disposition_reason": "r",
        "open_legal_questions": [],
        "rows": [
            {
                # "roadway" is a partial-word fragment of "Broadway" in the source;
                # under raw-substring anchoring it would have passed.
                "row_id": "partial",
                "borough": "Manhattan",
                "community_district": 7,
                "street_name": "roadway",
                "frontage_from": "West 94th Street",
                "frontage_to": "West 97th Street",
            }
        ],
    }
    snap = _synthetic(
        tmp_path, excerpt=excerpt, named=named, alt=_alt_block(), snapshot_id="zr-db023d"
    )
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


# --------------------------------------------------------------------------
# DB-023a metadata-bypass closure (M5-T040 rework): disposition_when_located and
# the qualifier metadata are NOT digest-covered, so flipping the REAL qualified
# snapshot to matched_override and removing / nulling / emptying the mutable
# open_legal_questions list (source quote and digest unchanged) must STILL be
# refused. The refusal is SOURCE-BOUND to the qualifier_clause, which traces
# verbatim to the digest-covered source quote. Plus malformed-metadata coverage.
# --------------------------------------------------------------------------


def _load_mutated(tmp_path, raw: dict, name: str):
    """Write a mutated raw doc (verbatim_excerpt + content_digest untouched, so
    the loader's digest check still passes) and load it through the production
    loader."""
    path = tmp_path / f"{name}.snapshot.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    return load_snapshot_file(path)


def test_db023a_real_snapshot_qualifier_clause_is_source_anchored():
    """Precondition the DB-023a refusal relies on: in the REAL zr-12-10 snapshot
    the declared qualifier_clause is a verbatim substring of the digest-covered
    source quote (and of the excerpt), so the source-binding actually holds."""
    raw = _raw()
    named = raw["named_street_overrides"]
    assert named["qualifier_clause"] in named["verbatim_source_quote"]
    assert named["qualifier_clause"] in raw["verbatim_excerpt"]


@pytest.mark.parametrize("bypass", ["remove", "null", "empty"])
def test_db023a_real_qualified_snapshot_matched_override_metadata_bypass_refused(
    tmp_path, bypass
):
    """AS-1 (DB-023a metadata bypass): starting from the REAL qualified zr-12-10
    snapshot (source quote still reads '...which are separated by mapped public
    park...'), set disposition_when_located=matched_override and remove / null /
    empty open_legal_questions while leaving the source quote unchanged. Each
    variant must be REFUSED at construction: the refusal is source-bound to the
    qualifier_clause, so emptying the free-floating metadata list cannot
    manufacture an unconditional override on a conditioned designation."""
    raw = _raw()
    named = raw["named_street_overrides"]
    named["disposition_when_located"] = "matched_override"
    if bypass == "remove":
        named.pop("open_legal_questions", None)
    elif bypass == "null":
        named["open_legal_questions"] = None
    else:  # empty
        named["open_legal_questions"] = []
    snap = _load_mutated(tmp_path, raw, f"zr-12-10-bypass-{bypass}")
    # source quote and digest untouched, and the qualifier clause still traces to
    # the digest-covered source quote — the refusal below is genuinely source-bound.
    quote = snap.raw["named_street_overrides"]["verbatim_source_quote"]
    assert named["qualifier_clause"] in quote
    assert snap.content_digest_sha256 == snap.raw["content_digest_sha256"]
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_db023a_source_anchored_qualifier_refuses_override_despite_empty_list(tmp_path):
    """Isolates the source-bound signal: a SYNTHETIC block whose only unresolved
    signal is a qualifier_clause tracing to its own source quote is refused for
    matched_override even with an EMPTY open_legal_questions list and no
    qualifier_scope_status / resolvable flag — proving the refusal does not depend
    on the mutable metadata."""
    named_quote = (
        "In Community District 1 in the Borough of Testville, the roadways of "
        "Testonly Avenue between First and Second Streets, which are separated by "
        "mapped public park shall each be considered a wide street."
    )
    excerpt = named_quote + "\n\n" + _SOURCE_SHAPED_ALT_QUOTE
    named = {
        "provision_id": "test-named",
        "section_anchor": "test anchor",
        "node_anchor": "/node/0",
        "verbatim_source_quote": named_quote,
        "qualifier_clause": "which are separated by mapped public park",
        "disposition_when_located": "matched_override",
        "open_legal_questions": [],  # the bypass vector: emptied
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
    snap = _synthetic(
        tmp_path, excerpt=excerpt, named=named, alt=_alt_block(),
        snapshot_id="zr-db023a-sourcebound",
    )
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_db023a_qualifier_clause_absent_from_source_fails_closed(tmp_path):
    """Integrity coverage / malformed metadata: a declared qualifier_clause that
    is NOT a verbatim substring of the digest-covered source quote is a tamper and
    fails closed at construction (even for an indeterminate disposition)."""
    named = _named_block(qualifier_clause="which are separated by a private easement")
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=named, alt=_alt_block(),
        snapshot_id="zr-db023a-clausebad",
    )
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_db023a_qualifier_clause_wrong_type_fails_closed(tmp_path):
    """Malformed metadata: a non-string qualifier_clause fails closed rather than
    being read as a valid (or absent) qualifier declaration."""
    named = _named_block(qualifier_clause=7)
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=named, alt=_alt_block(),
        snapshot_id="zr-db023a-clausetype",
    )
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_db023a_open_legal_questions_malformed_fails_closed(tmp_path):
    """Malformed metadata: an open_legal_questions that is not a list is not
    silently coerced (a bare string would otherwise iterate into characters) — it
    fails closed at construction."""
    named = _named_block(
        disposition_when_located="matched_override",
        open_legal_questions="G6-Q1-park-qualifier-scope",  # a bare string, not a list
    )
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=named, alt=_alt_block(),
        snapshot_id="zr-db023a-olqbad",
    )
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


# --------------------------------------------------------------------------
# DB-023a ALL-SIGNALS-STRIPPED closure (M5-T040 rework, report §8 promotion):
# the disposition and ALL FOUR qualifier signals (qualifier_clause,
# qualifier_scope_status, qualifier_predicate_resolvable_from_text,
# open_legal_questions) are outside the digest cover, so stripping / nulling /
# falsely resolving every one of them together while keeping the REAL conditional
# source quote and digest must STILL be refused. The trusted binding for an
# unconditional disposition is taken from the digest-covered source itself.
# --------------------------------------------------------------------------

_FOUR_QUALIFIER_SIGNALS = (
    "qualifier_clause",
    "qualifier_scope_status",
    "qualifier_predicate_resolvable_from_text",
    "open_legal_questions",
)
_REAL_QUALIFIER_CLAUSE = "which are separated by mapped public park"


@pytest.mark.parametrize("mode", ["remove", "null", "falsely_resolved"])
def test_db023a_all_qualifier_signals_stripped_still_refused(tmp_path, mode):
    """AS-1 (DB-023a all-signals-stripped): from the REAL zr-12-10 snapshot set
    disposition_when_located=matched_override and strip EVERY qualifier signal at
    once — ``remove`` (pop all four), ``null`` (set all four to None), or
    ``falsely_resolved`` (qualifier_clause removed, qualifier_scope_status
    ='resolved', qualifier_predicate_resolvable_from_text=True,
    open_legal_questions=[]). The verbatim_excerpt and content_digest are left
    untouched, so the digest-covered source quote still reads '...which are
    separated by mapped public park...'. Each variant must be REFUSED at
    construction: no mutable qualifier metadata remains to drive the refusal, so it
    is bound to the digest-covered source (the metadata bypass this closes)."""
    raw = _raw()
    named = raw["named_street_overrides"]
    named["disposition_when_located"] = "matched_override"
    if mode == "remove":
        for key in _FOUR_QUALIFIER_SIGNALS:
            named.pop(key, None)
    elif mode == "null":
        for key in _FOUR_QUALIFIER_SIGNALS:
            named[key] = None
    else:  # falsely_resolved: metadata affirmatively (and falsely) claims resolution
        named.pop("qualifier_clause", None)
        named["qualifier_scope_status"] = "resolved"
        named["qualifier_predicate_resolvable_from_text"] = True
        named["open_legal_questions"] = []
    snap = _load_mutated(tmp_path, raw, f"zr-12-10-allstripped-{mode}")
    mutated_named = snap.raw["named_street_overrides"]
    # the real conditional clause is still in the DIGEST-COVERED source, the digest
    # is intact, and no truthy qualifier signal remains — the refusal is genuinely
    # source-bound, not driven by leftover metadata.
    assert _REAL_QUALIFIER_CLAUSE in mutated_named["verbatim_source_quote"]
    assert snap.content_digest_sha256 == snap.raw["content_digest_sha256"]
    assert not mutated_named.get("qualifier_clause")
    assert not mutated_named.get("open_legal_questions")
    assert mutated_named.get("qualifier_scope_status") in (None, "resolved")
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(snap)


def test_db023a_all_signals_stripped_refusal_is_source_bound(tmp_path):
    """Isolate that the all-signals-stripped refusal is driven by the
    DIGEST-COVERED source and not merely by the presence of matched_override: the
    SAME strip (all four qualifier signals ABSENT, disposition matched_override) is
    REFUSED on the real CONDITIONAL source but ALLOWED — reaching MATCHED_OVERRIDE
    — on a synthetic UNCONDITIONAL source."""
    # conditional source, every qualifier signal removed -> refused
    raw = _raw()
    named = raw["named_street_overrides"]
    named["disposition_when_located"] = "matched_override"
    for key in _FOUR_QUALIFIER_SIGNALS:
        named.pop(key, None)
    conditional = _load_mutated(tmp_path, raw, "zr-12-10-sourcebound-cond")
    with pytest.raises(NamedStreetOverrideError):
        NamedStreetOverrideMatcher(conditional)
    # unconditional source, no qualifier signals present at all -> allowed
    named_uncond = _named_block(disposition_when_located="matched_override")
    named_uncond.pop("open_legal_questions", None)  # match the "all absent" shape
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=named_uncond, alt=_alt_block(),
        snapshot_id="zr-sourcebound-uncond",
    )
    matcher = NamedStreetOverrideMatcher(snap)
    result = matcher.match(
        OverrideQuery("Testville", 1, "Testonly Avenue", "First Street", "Second Street")
    )
    assert result.status is MatchStatus.MATCHED_OVERRIDE


def test_db023a_unconditional_row_with_no_qualifier_signals_reaches_override(tmp_path):
    """Retain legitimate unconditional-row coverage: a genuinely unconditional
    designation (source quote decomposes entirely into the designation grammar +
    capitalized locators) with matched_override and NO qualifier signals is NOT
    over-refused by the source-bound gate — it still reaches MATCHED_OVERRIDE."""
    named = _named_block(disposition_when_located="matched_override")
    for key in _FOUR_QUALIFIER_SIGNALS:
        named.pop(key, None)
    snap = _synthetic(
        tmp_path, excerpt=_excerpt(), named=named, alt=_alt_block(),
        snapshot_id="zr-db023a-uncond-nosignals",
    )
    matcher = NamedStreetOverrideMatcher(snap)
    result = matcher.match(
        OverrideQuery("Testville", 1, "Testonly Avenue", "First Street", "Second Street")
    )
    assert result.status is MatchStatus.MATCHED_OVERRIDE
    assert result.provision_id == "test-named"


# --------------------------------------------------------------------------
# DB-023a COMPLETE-SPAN binding (M5-T040 rework): verbatim_source_quote is only
# constrained to be *a substring* of the digest-covered excerpt, so a tamperer can
# preserve the ORIGINAL excerpt + digest, remove all qualifier metadata, and NARROW
# the quote to a real sub-span that DROPS '...which are separated by mapped public
# park...' while every structured row still anchors. A whitelist/capitalization
# decomposition of that narrowed span has no residual, so the prior gate would have
# ALLOWED it. The unconditional binding must therefore come from the AUTHENTICATED,
# COMPLETE span (a whole sentence unit of the excerpt), which refuses the narrowing.
# --------------------------------------------------------------------------


def test_db023a_narrowed_source_quote_to_omit_condition_refused(tmp_path):
    """AS-1 (DB-023a complete-span binding): from the REAL zr-12-10 snapshot, keep
    the excerpt and digest, remove every qualifier signal, set
    disposition_when_located=matched_override, and NARROW verbatim_source_quote to
    a genuine sub-span of the excerpt that omits the conditional clause. The
    narrowed span still anchors both rows (borough/CD/frontages), so the
    source-tracing guard would NOT catch it and the token decomposition of the
    narrowed span is residual-free — yet construction is REFUSED because the quote
    is not a COMPLETE sentence span of the digest-covered excerpt."""
    raw = _raw()
    named = raw["named_street_overrides"]
    full_quote = named["verbatim_source_quote"]
    marker = ", " + _REAL_QUALIFIER_CLAUSE
    assert marker in full_quote
    narrowed = full_quote.split(marker)[0]
    named["verbatim_source_quote"] = narrowed
    named["disposition_when_located"] = "matched_override"
    for key in _FOUR_QUALIFIER_SIGNALS:
        named.pop(key, None)
    snap = _load_mutated(tmp_path, raw, "zr-12-10-narrowed-omit-condition")
    # original excerpt + digest preserved; the narrowed quote is a genuine sub-span
    # of the digest-covered excerpt that OMITS the condition ...
    assert snap.verbatim_excerpt == raw["verbatim_excerpt"]
    assert snap.content_digest_sha256 == snap.raw["content_digest_sha256"]
    assert narrowed in snap.verbatim_excerpt
    assert _REAL_QUALIFIER_CLAUSE not in narrowed
    # ... yet every row locator still anchors in the narrowed span, so the refusal
    # is not incidental to the source-tracing guard — it is the complete-span bind.
    assert "Community District 7" in narrowed and "Community District 3" in narrowed
    assert "Broadway" in narrowed and "Allen Street" in narrowed
    with pytest.raises(NamedStreetOverrideError, match="COMPLETE sentence span"):
        NamedStreetOverrideMatcher(snap)
