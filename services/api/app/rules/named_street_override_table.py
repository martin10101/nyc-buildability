"""ZR 12-10 named-street override — typed table-data model + normalization
vocabulary (M5-T049; DB-030f).

Two tightly-related halves of the override table's VALUE layer, both extracted
verbatim from ``named_street_override.py`` under the DB-030f cohesion ruling:

* the typed DATA model — the tri-state :class:`MatchStatus`, the query /
  provenance / result dataclasses, the internal :class:`_Row` record, the
  module-level identifiers (:data:`SNAPSHOT_ID`, :data:`BOUNDARY_OPEN_QUESTION`),
  and the snapshot-integrity :class:`NamedStreetOverrideError`; and
* the pure NORMALIZATION vocabulary — the text-normalization and source-anchoring
  helpers (:func:`_collapse`, :func:`_normalize_cd`, :func:`_normalize_district`,
  :func:`_word_bounded`, :func:`_anchored_in`, :func:`_bounded_repr`) that PRODUCE
  and COMPARE the normalized values the data model carries (a :class:`_Row`'s
  ``norm_*`` fields are literally the output of :func:`_collapse`).

Both halves are leaf-level value semantics with NO dependency on the snapshot or
the matcher, so this module is the base of a one-directional import chain
(matching -> table). The stateful engine that reads a snapshot and APPLIES these
values (:class:`NamedStreetOverrideMatcher` and :func:`load_default_matcher`)
lives in :mod:`app.rules.named_street_override_matching`.
:mod:`app.rules.named_street_override` stays the compatibility facade re-exporting
these names unchanged, so existing consumers import byte-identically. Pure
extraction — zero behavior change.

This is not legal advice. Everything here is DRAFT pending qualified-human (G6)
approval (D-045-R009).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

SNAPSHOT_ID = "zr-12-10"

# The boundary-cross-street inclusive/exclusive ambiguity is a third open reading
# question the packet's LEGAL BOUNDARY requires recording (distinct from the two
# snapshot-declared questions G6-Q1 / G6-Q2).
BOUNDARY_OPEN_QUESTION = "G6-Q3-boundary-cross-street-inclusive-exclusive"


class NamedStreetOverrideError(RuntimeError):
    """Raised when the snapshot cannot back a defensible matcher (missing table
    block, or a table quote not covered by the digested excerpt)."""


class MatchStatus(str, Enum):
    """Typed tri-state; fails closed to :attr:`INDETERMINATE`."""

    MATCHED_OVERRIDE = "matched_override"
    NOT_MATCHED = "not_matched"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class OverrideQuery:
    """A street segment described textually. ``community_district`` accepts an int
    or a string ("7", "CD 7", "Community District 7"). Bounds are the segment's
    two cross streets."""

    borough: str
    community_district: object
    street_name: str
    cross_street_from: str | None = None
    cross_street_to: str | None = None


@dataclass(frozen=True)
class OverrideProvenance:
    """Distinct override provenance carried by every non-``NOT_MATCHED`` result.
    ``snapshot_sha256`` and ``section_anchor`` are always populated; the
    provision/row fields are populated once a designated row is located."""

    snapshot_id: str
    snapshot_sha256: str
    section_number: str
    section_anchor: str
    node_anchor: str | None
    provision_id: str | None
    matched_row_id: str | None
    matched_row_verbatim: str | None


@dataclass(frozen=True)
class MatchResult:
    status: MatchStatus
    reason: str
    provision_id: str | None = None
    provenance: OverrideProvenance | None = None
    open_legal_questions: tuple[str, ...] = ()


@dataclass(frozen=True)
class AlternateWidthResult:
    """Result of the C5-3/C6-4/C6-6 alternate-width classification. No numeric
    width test is performed; the coverage class is ``professional_review_required``
    for an applicable district and ``not_applicable`` otherwise."""

    district: str
    coverage_class: str
    reason: str
    provision_id: str | None = None
    provenance: OverrideProvenance | None = None
    open_legal_questions: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Row:
    row_id: str
    borough: str
    community_district: int
    street_name: str
    frontage_from: str
    frontage_to: str
    norm_borough: str
    norm_street: str
    norm_from: str
    norm_to: str


# -- normalization vocabulary ----------------------------------------------
# The pure text-normalization and source-anchoring helpers that PRODUCE and
# COMPARE the normalized values above (a _Row's norm_* fields are the output of
# _collapse). No dependency on the snapshot or the matcher, so they are the leaf
# of the one-directional import chain (matching -> table).

_WS = re.compile(r"\s+")

# Generic NYC street-type words. A structured frontage endpoint such as
# "West 94th Street" is anchored to the source phrase "West 94th and West 97th
# Streets" by its distinctive locator ("west 94th") once a single trailing
# type word is removed - see :func:`_anchored_in`. Derived from the snapshot
# text, which spells street types in full; an endpoint whose type word is not
# in this set stays exact-matched and fails closed if it is not present verbatim.
_STREET_TYPE_WORDS = frozenset({"street", "streets", "avenue", "avenues"})

# Cap on the rendered length of a user-reachable query field embedded in a
# MatchResult.reason (DB-023c). Reasons are surfaced to callers, so an
# arbitrarily long typed input can never produce an unbounded reason string.
_MAX_QUERY_REPR = 80


def _bounded_repr(value: object, max_len: int = _MAX_QUERY_REPR) -> str:
    """Length-bounded ``repr()`` of a user-reachable query field for embedding in
    a :class:`MatchResult` reason (DB-023c). The full repr is used when short;
    otherwise it is truncated to ``max_len`` characters with an explicit marker,
    so the embedded fragment can never exceed ``max_len + len(marker)``."""
    text = repr(value)
    if len(text) <= max_len:
        return text
    return text[:max_len] + "...(truncated)"


def _collapse(value: object) -> str:
    """Documented text normalization (borough / street / cross-street): strip,
    collapse internal whitespace runs to one space, and casefold. Derived from
    the snapshot text, which uses ordinary spacing and full spellings; NO
    abbreviation expansion is defined, so matching stays exact and never fuzzy."""
    if value is None:
        return ""
    return _WS.sub(" ", str(value).strip()).casefold()


def _normalize_cd(value: object) -> int | None:
    """Normalize a community district to an int, or ``None`` if unparseable or
    ambiguous. Accepts an int or a string carrying exactly one integer run."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    runs = re.findall(r"\d+", str(value))
    if len(runs) != 1:
        return None
    return int(runs[0])


def _normalize_district(value: object) -> str:
    """Normalize a zoning district for the alternate-width vocabulary check:
    uppercase, drop all whitespace (so "C5 - 3" == "C5-3")."""
    if value is None:
        return ""
    return _WS.sub("", str(value).strip().upper())


def _word_bounded(needle: str, haystack: str) -> bool:
    """True when ``needle`` occurs in ``haystack`` bounded by non-word characters
    or the string edges (DB-023d word-boundary anchoring). A raw substring test
    would let a partial-word fragment anchor (``"est 94th"`` inside
    ``"west 94th"``, or a stray ``"on"`` inside ``"Rivington"``); requiring word
    boundaries keeps the source-tracing guard honest. ``needle`` is a normalized
    locator (casefold + single spaces) whose first/last characters are word
    characters, so the surrounding lookarounds are the correct boundary test."""
    if not needle:
        return False
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack) is not None


def _anchored_in(field: object, normalized_source: str) -> bool:
    """True when a structured locator field is grounded in the normalized source
    quote. This is STRICTER than "the block quote is a substring of the excerpt":
    it ties each individual structured row field back to the pinned source text.

    A field anchors if either its full normalized form appears in the source, or
    its distinctive core - the field with a single trailing generic street-type
    word (:data:`_STREET_TYPE_WORDS`) removed - appears. Both forms are matched
    with WORD-BOUNDARY anchoring (:func:`_word_bounded`), never a raw substring,
    so a partial-word fragment cannot anchor. The core form is what lets the
    normalized endpoint "West 94th Street" anchor to the source phrase
    "...Broadway between West 94th and West 97th Streets...", where the singular
    "Street" is never written. A field that anchors by neither form (a wrong
    borough, an invented cross street, a swapped street name) returns ``False``
    and the caller fails closed."""
    core = _collapse(field)
    if not core:
        return False
    if _word_bounded(core, normalized_source):
        return True
    head, _, tail = core.rpartition(" ")
    if head and tail in _STREET_TYPE_WORDS and _word_bounded(head, normalized_source):
        return True
    return False
