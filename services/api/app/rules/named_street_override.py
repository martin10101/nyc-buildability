"""ZR 12-10 named-street override matcher (M5-T039; DB-010).

Deterministic, textual matcher for the NYC Zoning Resolution section 12-10
"street, wide" **named-street override** designations (Broadway between West 94th
and West 97th Streets, Manhattan CD7; Allen Street between Rivington and Delancey
Streets, Manhattan CD3) and the C5-3/C6-4/C6-6 **alternate-width** provisions.

Boundaries this module deliberately keeps (packet contract, M4-T018 legal flags):

* It matches ONLY from the sha256-pinned ``zr-12-10`` snapshot capture. It never
  fetches the network, never reads any other source, and hard-codes no street.
  Every row it uses is read from the snapshot's ``named_street_overrides`` block,
  whose ``verbatim_source_quote`` is checked at construction to be a substring of
  the digest-covered ``verbatim_excerpt`` (tamper-evidence).
* Street/cross-street matching is EXACT after a documented normalization
  (casefold + whitespace-collapse). There is NO fuzzy matching and NO geometry
  inference; the snapshot spells street types in full, so no abbreviation
  expansion is defined and an abbreviated input (e.g. "Allen St") is NOT a match.
* Output is a typed tri-state (:class:`MatchStatus`) that FAILS CLOSED to
  ``INDETERMINATE`` on any unparseable locator, missing segment bound, degenerate
  segment, or boundary-cross-street inclusive/exclusive ambiguity.
* The two named designations are conditioned on the roadways being "separated by
  mapped public park" - a physical predicate this textual matcher cannot verify -
  and the grammatical scope of that qualifier is an unresolved qualified-legal
  question (G6-Q1). So a located named row returns ``INDETERMINATE`` (conservative
  refusal) with full provenance and the open question recorded; it does not
  decide the question. The ``MATCHED_OVERRIDE`` status is reached only by an
  unconditional row (``disposition_when_located == "matched_override"``).
* The C5-3/C6-4/C6-6 alternate-width clause reads "may be considered" (permissive
  vs declarative is unresolved, G6-Q2) and needs portion-level widths no connector
  supplies, so this module performs NO numeric width computation and returns a
  ``professional_review_required`` coverage class for those districts only.

This module implements the capture; it is not legal advice. Everything here is
DRAFT pending qualified-human (G6) approval (D-045-R009).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from app.rules.snapshots import SectionSnapshot, SnapshotStore

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


_WS = re.compile(r"\s+")

# Generic NYC street-type words. A structured frontage endpoint such as
# "West 94th Street" is anchored to the source phrase "West 94th and West 97th
# Streets" by its distinctive locator ("west 94th") once a single trailing
# type word is removed - see :func:`_anchored_in`. Derived from the snapshot
# text, which spells street types in full; an endpoint whose type word is not
# in this set stays exact-matched and fails closed if it is not present verbatim.
_STREET_TYPE_WORDS = frozenset({"street", "streets", "avenue", "avenues"})

# The only dispositions the matcher understands for a located named row. Any
# other value in the snapshot fails closed at construction rather than being
# silently coerced to INDETERMINATE.
_ALLOWED_DISPOSITIONS = frozenset({"indeterminate", "matched_override"})


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


def _anchored_in(field: object, normalized_source: str) -> bool:
    """True when a structured locator field is grounded in the normalized source
    quote. This is STRICTER than "the block quote is a substring of the excerpt":
    it ties each individual structured row field back to the pinned source text.

    A field anchors if either its full normalized form appears in the source, or
    its distinctive core - the field with a single trailing generic street-type
    word (:data:`_STREET_TYPE_WORDS`) removed - appears. The second form is what
    lets the normalized endpoint "West 94th Street" anchor to the source phrase
    "...Broadway between West 94th and West 97th Streets...", where the singular
    "Street" is never written. A field that anchors by neither form (a wrong
    borough, an invented cross street, a swapped street name) returns ``False``
    and the caller fails closed."""
    core = _collapse(field)
    if not core:
        return False
    if core in normalized_source:
        return True
    head, _, tail = core.rpartition(" ")
    if head and tail in _STREET_TYPE_WORDS and head in normalized_source:
        return True
    return False


class NamedStreetOverrideMatcher:
    """Deterministic matcher built from a single :class:`SectionSnapshot`."""

    def __init__(self, snapshot: SectionSnapshot):
        self._snapshot = snapshot
        raw = snapshot.raw
        try:
            named = raw["named_street_overrides"]
            alt = raw["alternate_width_provisions"]
        except (KeyError, TypeError) as exc:
            raise NamedStreetOverrideError(
                f"snapshot {snapshot.snapshot_id!r} does not carry the named-street "
                f"override table ({exc}); the source has not been repaired"
            ) from exc

        # Tamper-evidence: each structured block's verbatim quote must be covered
        # by the digested excerpt, so the content_digest_sha256 provenance is honest.
        for block, label in (
            (named, "named_street_overrides"),
            (alt, "alternate_width_provisions"),
        ):
            quote = block.get("verbatim_source_quote", "")
            if not quote or quote not in snapshot.verbatim_excerpt:
                raise NamedStreetOverrideError(
                    f"{label}.verbatim_source_quote is not a substring of the "
                    f"digest-covered verbatim_excerpt in snapshot "
                    f"{snapshot.snapshot_id!r} (integrity failure)"
                )

        self._named_block = named
        self._alt_block = alt
        self._rows: tuple[_Row, ...] = tuple(self._build_rows(named.get("rows", [])))

        # Beyond quote-substring presence: validate that every NORMALIZED
        # structured row field and the block dispositions actually trace to the
        # pinned source text, so a structured value that diverges from the source
        # fails closed here rather than producing a defensible-looking result.
        self._validate_against_source()

    @staticmethod
    def _build_rows(rows: list) -> list[_Row]:
        built: list[_Row] = []
        for row in rows:
            cd = _normalize_cd(row.get("community_district"))
            if cd is None:
                raise NamedStreetOverrideError(
                    f"override row {row.get('row_id')!r} has an unparseable "
                    "community_district"
                )
            built.append(
                _Row(
                    row_id=row["row_id"],
                    borough=row["borough"],
                    community_district=cd,
                    street_name=row["street_name"],
                    frontage_from=row["frontage_from"],
                    frontage_to=row["frontage_to"],
                    norm_borough=_collapse(row["borough"]),
                    norm_street=_collapse(row["street_name"]),
                    norm_from=_collapse(row["frontage_from"]),
                    norm_to=_collapse(row["frontage_to"]),
                )
            )
        return built

    def _validate_against_source(self) -> None:
        """Fail closed unless every normalized structured field and disposition
        traces to the pinned source text (not merely that the block quote is a
        digest-covered substring).

        For each named row, the borough, community district, street name, and
        both frontage endpoints must be anchored (:func:`_anchored_in`) in the
        named block's own ``verbatim_source_quote``. The community-district value
        is checked against the source's own phrasing ("Community District N").
        The located-row disposition must be a recognized value. Each applicable
        alternate-width district must appear in the alternate-width quote. Any
        miss raises :class:`NamedStreetOverrideError` so a snapshot whose
        structured rows do not decompose the source faithfully cannot back a
        result."""
        named_source = _collapse(self._named_block.get("verbatim_source_quote", ""))
        disposition = self._named_block.get("disposition_when_located", "indeterminate")
        if disposition not in _ALLOWED_DISPOSITIONS:
            raise NamedStreetOverrideError(
                f"named_street_overrides.disposition_when_located {disposition!r} is "
                f"not one of {sorted(_ALLOWED_DISPOSITIONS)}; an unrecognized "
                "disposition fails closed rather than defaulting silently"
            )
        for row in self._rows:
            field_checks = {
                "borough": _anchored_in(row.borough, named_source),
                "community_district": (
                    f"community district {row.community_district}" in named_source
                ),
                "street_name": _anchored_in(row.street_name, named_source),
                "frontage_from": _anchored_in(row.frontage_from, named_source),
                "frontage_to": _anchored_in(row.frontage_to, named_source),
            }
            unanchored = sorted(name for name, ok in field_checks.items() if not ok)
            if unanchored:
                raise NamedStreetOverrideError(
                    f"override row {row.row_id!r} has structured field(s) {unanchored} "
                    "not anchored in the digest-covered verbatim_source_quote; the "
                    "normalized row does not trace to the pinned source text (fail "
                    "closed)"
                )

        alt_source = _collapse(self._alt_block.get("verbatim_source_quote", ""))
        for district in self._alt_block.get("applicable_districts", []):
            if _collapse(district) not in alt_source:
                raise NamedStreetOverrideError(
                    f"alternate_width_provisions applicable district {district!r} is "
                    "not present in its digest-covered verbatim_source_quote (fail "
                    "closed)"
                )

    # -- provenance helpers ------------------------------------------------

    def _section_provenance(self) -> OverrideProvenance:
        """Snapshot-level provenance for a non-located non-NOT_MATCHED result."""
        return OverrideProvenance(
            snapshot_id=self._snapshot.snapshot_id,
            snapshot_sha256=self._snapshot.content_digest_sha256,
            section_number=self._snapshot.section_number,
            section_anchor="ZR 12-10, definition 'street, wide'",
            node_anchor=self._named_block.get("node_anchor"),
            provision_id=None,
            matched_row_id=None,
            matched_row_verbatim=None,
        )

    def _row_provenance(self, row: _Row) -> OverrideProvenance:
        block = self._named_block
        return OverrideProvenance(
            snapshot_id=self._snapshot.snapshot_id,
            snapshot_sha256=self._snapshot.content_digest_sha256,
            section_number=self._snapshot.section_number,
            section_anchor=block["section_anchor"],
            node_anchor=block.get("node_anchor"),
            provision_id=block["provision_id"],
            matched_row_id=row.row_id,
            matched_row_verbatim=block["verbatim_source_quote"],
        )

    def _alt_provenance(self) -> OverrideProvenance:
        block = self._alt_block
        return OverrideProvenance(
            snapshot_id=self._snapshot.snapshot_id,
            snapshot_sha256=self._snapshot.content_digest_sha256,
            section_number=self._snapshot.section_number,
            section_anchor=block["section_anchor"],
            node_anchor=block.get("node_anchor"),
            provision_id=block["provision_id"],
            matched_row_id=None,
            matched_row_verbatim=block["verbatim_source_quote"],
        )

    # -- public API --------------------------------------------------------

    def match(self, query: OverrideQuery) -> MatchResult:
        """Classify a street segment against the named-street override table."""
        borough = _collapse(query.borough)
        street = _collapse(query.street_name)
        cd = _normalize_cd(query.community_district)

        if not borough:
            return self._indeterminate("borough missing or unparseable")
        if not street:
            return self._indeterminate("street name missing or unparseable")
        if cd is None:
            return self._indeterminate("community district missing or unparseable")

        street_rows = [r for r in self._rows if r.norm_street == street]
        if not street_rows:
            return MatchResult(
                status=MatchStatus.NOT_MATCHED,
                reason=f"street {query.street_name!r} is not a named-street override",
            )

        located = [
            r
            for r in street_rows
            if r.norm_borough == borough and r.community_district == cd
        ]
        if not located:
            return MatchResult(
                status=MatchStatus.NOT_MATCHED,
                reason=(
                    f"street {query.street_name!r} is a named override but not in the "
                    f"designated borough/community district ({query.borough!r}, CD {cd})"
                ),
            )
        row = located[0]

        qf = _collapse(query.cross_street_from)
        qt = _collapse(query.cross_street_to)
        if not qf or not qt:
            return self._indeterminate(
                "segment cross-street bounds are required to confirm the designated "
                "frontage",
                provenance=self._row_provenance(row),
                provision_id=self._named_block["provision_id"],
            )
        if qf == qt:
            return self._indeterminate(
                "degenerate segment: identical cross-street bounds",
                provenance=self._row_provenance(row),
                provision_id=self._named_block["provision_id"],
            )

        designated = {row.norm_from, row.norm_to}
        query_pair = {qf, qt}
        if query_pair == designated:
            return self._located(row)
        if query_pair & designated:
            return self._boundary_indeterminate(row)
        return MatchResult(
            status=MatchStatus.NOT_MATCHED,
            reason=(
                f"segment bounds {{{query.cross_street_from!r}, {query.cross_street_to!r}}} "
                f"lie outside the designated frontage for {row.street_name} "
                f"({row.frontage_from} - {row.frontage_to})"
            ),
        )

    def classify_alternate_width_district(self, district: object) -> AlternateWidthResult:
        """Classify a zoning district against the C5-3/C6-4/C6-6 alternate-width
        provision. Performs NO numeric width test."""
        block = self._alt_block
        norm = _normalize_district(district)
        applicable = {_normalize_district(d) for d in block.get("applicable_districts", [])}
        if norm and norm in applicable:
            return AlternateWidthResult(
                district=norm,
                coverage_class="professional_review_required",
                reason=block["disposition_reason"],
                provision_id=block["provision_id"],
                provenance=self._alt_provenance(),
                open_legal_questions=tuple(block.get("open_legal_questions", ())),
            )
        return AlternateWidthResult(
            district=norm,
            coverage_class="not_applicable",
            reason=(
                f"district {district!r} is not within the C5-3/C6-4/C6-6 "
                "alternate-width provision"
            ),
        )

    # -- result builders ---------------------------------------------------

    def _indeterminate(
        self,
        reason: str,
        provenance: OverrideProvenance | None = None,
        provision_id: str | None = None,
        open_legal_questions: tuple[str, ...] = (),
    ) -> MatchResult:
        return MatchResult(
            status=MatchStatus.INDETERMINATE,
            reason=reason,
            provision_id=provision_id,
            provenance=provenance or self._section_provenance(),
            open_legal_questions=open_legal_questions,
        )

    def _located(self, row: _Row) -> MatchResult:
        block = self._named_block
        disposition = block.get("disposition_when_located", "indeterminate")
        open_qs = tuple(block.get("open_legal_questions", ()))
        if disposition == "matched_override":
            return MatchResult(
                status=MatchStatus.MATCHED_OVERRIDE,
                reason=(
                    f"exact designated-frontage match for {row.street_name} "
                    f"({row.frontage_from} - {row.frontage_to}); unconditional override"
                ),
                provision_id=block["provision_id"],
                provenance=self._row_provenance(row),
                open_legal_questions=open_qs,
            )
        return MatchResult(
            status=MatchStatus.INDETERMINATE,
            reason=block["disposition_reason"],
            provision_id=block["provision_id"],
            provenance=self._row_provenance(row),
            open_legal_questions=open_qs,
        )

    def _boundary_indeterminate(self, row: _Row) -> MatchResult:
        block = self._named_block
        open_qs = (BOUNDARY_OPEN_QUESTION,) + tuple(block.get("open_legal_questions", ()))
        return MatchResult(
            status=MatchStatus.INDETERMINATE,
            reason=(
                "boundary cross-street inclusive/exclusive treatment is textually "
                f"ambiguous ('between {row.frontage_from} and {row.frontage_to}'); a "
                "segment sharing one boundary with the designated frontage is "
                "INDETERMINATE"
            ),
            provision_id=block["provision_id"],
            provenance=self._row_provenance(row),
            open_legal_questions=open_qs,
        )


def load_default_matcher(store: SnapshotStore | None = None) -> NamedStreetOverrideMatcher:
    """Build a matcher from the default (packaged) snapshot store."""
    store = store or SnapshotStore()
    return NamedStreetOverrideMatcher(store.get(SNAPSHOT_ID))
