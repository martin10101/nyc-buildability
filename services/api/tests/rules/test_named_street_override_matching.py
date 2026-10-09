"""Focused tests for the extracted snapshot-bound matching engine
(M5-T049; DB-030f).

These import DIRECTLY from ``app.rules.named_street_override_matching`` to prove
the engine module stands on its own after the pure extraction, and add a
re-export IDENTITY check confirming the facade
(``app.rules.named_street_override``) exposes the very SAME objects (not copies)
as the two implementation modules — the structural half of the pure-extraction
proof. The unchanged M5-T039/T040 acceptance suite remains the byte-identity
behavior proof; the normalization-helper focused tests live with the helpers in
``test_named_street_override_table.py`` (their extracted home).
"""

from app.rules import named_street_override as facade
from app.rules import named_street_override_matching as matching
from app.rules import named_street_override_table as table
from app.rules.named_street_override_matching import (
    NamedStreetOverrideMatcher,
    load_default_matcher,
)
from app.rules.named_street_override_table import MatchStatus, OverrideQuery


def test_load_default_matcher_builds_engine_and_matches():
    matcher = load_default_matcher()
    assert isinstance(matcher, NamedStreetOverrideMatcher)
    # an unknown street is a deterministic NOT_MATCHED regardless of the packaged
    # snapshot's designated rows.
    result = matcher.match(
        OverrideQuery("Manhattan", 7, "Nowhere Road", "A Street", "B Street")
    )
    assert result.status is MatchStatus.NOT_MATCHED
    assert result.provenance is None


def test_facade_reexports_are_the_same_objects():
    """Pure-extraction structural proof: the facade exposes the SAME objects the
    implementation modules define (identity, not equality), so no behavior can
    diverge between an import through the facade and a direct import. After the
    DB-030f split the engine + loader come from the matching module while the data
    model AND the normalization helpers come from the table module."""
    # engine + loader come from the matching module
    assert facade.NamedStreetOverrideMatcher is matching.NamedStreetOverrideMatcher
    assert facade.load_default_matcher is matching.load_default_matcher
    # the typed data model comes from the table module
    assert facade.MatchStatus is table.MatchStatus
    assert facade.MatchResult is table.MatchResult
    assert facade.AlternateWidthResult is table.AlternateWidthResult
    assert facade.OverrideQuery is table.OverrideQuery
    assert facade.OverrideProvenance is table.OverrideProvenance
    assert facade.NamedStreetOverrideError is table.NamedStreetOverrideError
    assert facade.SNAPSHOT_ID == table.SNAPSHOT_ID
    assert facade.BOUNDARY_OPEN_QUESTION == table.BOUNDARY_OPEN_QUESTION
    assert facade._Row is table._Row
    # the normalization helpers now come from the table module (their extracted
    # home) and are re-exported byte-identically through the facade
    assert facade._normalize_cd is table._normalize_cd
    assert facade._collapse is table._collapse
    assert facade._anchored_in is table._anchored_in
    assert facade._bounded_repr is table._bounded_repr
    assert facade._normalize_district is table._normalize_district
    assert facade._word_bounded is table._word_bounded
    # and the engine applies the very same helper objects it imports from table
    assert matching._collapse is table._collapse
    assert matching._normalize_cd is table._normalize_cd
    assert matching._anchored_in is table._anchored_in
    assert matching._bounded_repr is table._bounded_repr
    assert matching._normalize_district is table._normalize_district
