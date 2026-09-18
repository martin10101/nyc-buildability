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
  decide the question. The ``MATCHED_OVERRIDE`` status is reached only by a row
  whose ``disposition_when_located == "matched_override"`` AND whose designation
  carries NO source-anchored unresolved qualifier (DB-023a). The disposition and
  qualifier metadata are not digest-covered, so that refusal is SOURCE-BOUND: a
  declared ``qualifier_clause`` must be a verbatim substring of the digest-covered
  source quote, and once source-anchored its presence refuses ``matched_override``
  regardless of the mutable ``open_legal_questions`` list - removing, nulling, or
  emptying that list cannot manufacture an unconditional override on a designation
  whose pinned source still carries the qualifier. Beyond that, the
  ``verbatim_source_quote`` is only constrained to be *a substring* of the
  digest-covered excerpt, so a tamperer can NARROW it to drop the trailing
  qualifier clause, and every qualifier signal is outside the digest cover, so a
  refusal keyed on that metadata is defeatable by stripping / nulling / falsely
  resolving all of it. The load-bearing accept gate therefore binds an
  unconditional disposition to the AUTHENTICATED, COMPLETE source span: the source
  quote must occupy a whole sentence unit of the digest-covered excerpt (begin at a
  span boundary and end at a sentence terminator - a narrowed sub-span cannot
  bind), and that complete span must carry no interposed or trailing qualifier
  clause. A word whitelist, capitalization, or bare substring membership is never
  that binding on its own. So neither narrowing the quote nor stripping every
  qualifier signal can manufacture MATCHED_OVERRIDE from the conditional
  Broadway/Allen designation.
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

# DB-023a metadata-bypass closure. The located-row disposition and the qualifier
# metadata are NOT covered by content_digest_sha256 (only verbatim_excerpt is), so
# the refusal of a matched_override on a conditioned designation is SOURCE-BOUND:
# the load-bearing signal is a declared qualifier_clause that traces verbatim to
# the digest-covered source quote. A qualifier_scope_status equal to this marker
# (casefolded) is the only value that clears that secondary signal.
_QUALIFIER_SCOPE_RESOLVED = "resolved"

# DB-023a defense-in-depth token grammar (M5-T040 rework). This is NOT the
# unconditional binding on its own (that is the complete-span check in
# _validate_unconditional_source_binding); it is the secondary no-qualifier signal
# applied AFTER the complete-span binding has forced the quote to be a whole
# sentence unit of the digest-covered excerpt. On that complete span, an
# unconditional designation decomposes ENTIRELY into the fixed grammar words of the
# designation template (matched casefold, below), its numeric/ordinal cross-street
# tokens, and its CAPITALIZED proper-noun locators; any residual lowercase
# common-word token is an interposed/trailing clause (e.g. "...which are separated
# by mapped public park...") the template cannot account for, so a full conditional
# quote kept intact while the mutable metadata is stripped still fails closed.
_UNCONDITIONAL_DESIGNATION_WORDS = frozenset(
    {
        "in",
        "community",
        "district",
        "the",
        "borough",
        "of",
        "roadways",
        "between",
        "and",
        "street",
        "streets",
        "avenue",
        "avenues",
        "shall",
        "each",
        "be",
        "considered",
        "a",
        "wide",
    }
)

# A source token that is a bare cardinal or ordinal number (a cross-street number
# such as "94th", or a community-district digit): part of a locator, never an
# interposed clause word.
_NUMERIC_LOCATOR_TOKEN = re.compile(r"^\d+(?:st|nd|rd|th)?$", re.IGNORECASE)

# Word tokens of a source quote (letters/digits/apostrophes), original case kept
# so a capitalized proper-noun locator is distinguishable from a lowercase
# common-word clause token.
_SOURCE_WORD_TOKEN = re.compile(r"[A-Za-z0-9']+")

# String provenance fields every structured block must carry. Validated at
# construction (DB-023b) so a malformed snapshot fails CLOSED there rather than
# raising a KeyError from match()/classify_alternate_width_district() after the
# module has been advertised as usable.
_REQUIRED_BLOCK_FIELDS = ("provision_id", "section_anchor")

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

        # DB-023b: every provenance string field match()/classify read at result
        # time must be present and well-typed at CONSTRUCTION, so a malformed
        # snapshot fails closed here instead of raising a KeyError from match().
        self._validate_block_provenance(named, "named_street_overrides")
        self._validate_block_provenance(alt, "alternate_width_provisions")

        # DB-023a (metadata-bypass closure): the located-row disposition and the
        # qualifier metadata are NOT covered by the digested excerpt, so a
        # matched_override on a row whose SOURCE still carries an unresolved
        # qualifier ("...which are separated by mapped public park...") is refused
        # SOURCE-BOUND, not merely on the mutable open_legal_questions list.
        # Refuse STRUCTURALLY at construction. The source quote is already proven
        # to be a digest-covered substring above, so anchoring the qualifier to it
        # carries the integrity guarantee.
        self._validate_disposition_against_qualifiers(
            named,
            _collapse(named.get("verbatim_source_quote", "")),
            self._snapshot.verbatim_excerpt,
        )

        self._rows: tuple[_Row, ...] = tuple(self._build_rows(named.get("rows", [])))

        # Beyond quote-substring presence: validate that every NORMALIZED
        # structured row field and the block dispositions actually trace to the
        # pinned source text, so a structured value that diverges from the source
        # fails closed here rather than producing a defensible-looking result.
        self._validate_against_source()

    @staticmethod
    def _validate_block_provenance(block: object, label: str) -> None:
        """DB-023b: fail closed unless the block carries every required
        provenance string field (:data:`_REQUIRED_BLOCK_FIELDS`) as a non-empty
        ``str``. These are the fields the provenance builders and match() read at
        result time; validating them here means match() can never KeyError (and
        never emit a provenance object with a non-string anchor/id)."""
        if not isinstance(block, dict):
            raise NamedStreetOverrideError(
                f"{label} block is not an object; cannot back a defensible matcher"
            )
        for field in _REQUIRED_BLOCK_FIELDS:
            value = block.get(field)
            if not isinstance(value, str) or not value.strip():
                raise NamedStreetOverrideError(
                    f"{label}.{field} is missing, empty, or not a string "
                    f"({value!r}); the snapshot cannot back a defensible matcher "
                    "(fail closed at construction)"
                )

    @staticmethod
    def _validate_disposition_against_qualifiers(
        named: dict, named_source: str, excerpt: str
    ) -> None:
        """DB-023a (metadata-bypass closure): refuse a ``matched_override``
        disposition whenever the named block still carries an UNRESOLVED
        qualifier, keyed on the digest-covered source rather than on free-floating
        metadata.

        ``disposition_when_located``, ``open_legal_questions``, and the qualifier
        fields are NOT covered by ``content_digest_sha256`` (only the
        ``verbatim_excerpt`` is). A tamperer could therefore flip the disposition
        to ``matched_override`` and remove / null / empty ``open_legal_questions``
        while leaving the source quote (which still reads "...which are separated
        by mapped public park...") untouched. A refusal keyed only on the mutable
        ``open_legal_questions`` list would let that edit read an unverifiable
        condition as an unconditional override - the metadata bypass this closes.

        So the load-bearing refusal is SOURCE-BOUND via integrity coverage: a
        declared ``qualifier_clause`` must be a verbatim substring of the
        digest-covered source quote (validated here ALWAYS - a declared clause
        that does not trace to the pinned source is a tamper and fails closed).
        Once source-anchored, its presence refuses ``matched_override`` no matter
        what the mutable metadata says. A non-empty ``open_legal_questions`` list,
        a ``qualifier_scope_status`` other than ``"resolved"``, and an explicit
        ``qualifier_predicate_resolvable_from_text is False`` are additional
        refusal signals. This decides NO legal question - it only refuses to treat
        a conditioned designation as unconditional (fail closed at construction)."""
        # Integrity + malformed-metadata coverage (runs regardless of disposition).
        clause = named.get("qualifier_clause")
        clause_source_anchored = False
        if clause is not None:
            if not isinstance(clause, str) or not clause.strip():
                raise NamedStreetOverrideError(
                    "named_street_overrides.qualifier_clause is present but is not a "
                    f"non-empty string ({clause!r}); malformed qualifier metadata "
                    "cannot back a defensible matcher (fail closed at construction, "
                    "DB-023a)"
                )
            if _collapse(clause) not in named_source:
                raise NamedStreetOverrideError(
                    f"named_street_overrides.qualifier_clause {clause!r} is not a "
                    "verbatim substring of the digest-covered source quote; a "
                    "qualifier declaration that does not trace to the pinned source "
                    "text is a tamper (fail closed at construction, DB-023a)"
                )
            clause_source_anchored = True

        open_questions_raw = named.get("open_legal_questions")
        if open_questions_raw is not None and not isinstance(
            open_questions_raw, (list, tuple)
        ):
            raise NamedStreetOverrideError(
                "named_street_overrides.open_legal_questions is present but is not a "
                f"list ({open_questions_raw!r}); malformed qualifier metadata cannot "
                "be silently coerced (fail closed at construction, DB-023a)"
            )
        open_questions = tuple(open_questions_raw or ())

        disposition = named.get("disposition_when_located", "indeterminate")
        if disposition != "matched_override":
            return

        # Unconditional binding (load-bearing): the accept of a matched_override is
        # bound to the AUTHENTICATED, COMPLETE source span (a whole sentence unit of
        # the digest-covered excerpt), not to the mutable qualifier signals below
        # and not to a narrowable substring - so neither narrowing the quote to drop
        # the qualifier clause nor stripping every qualifier signal can manufacture
        # MATCHED_OVERRIDE from a conditional designation. Runs FIRST, independently.
        NamedStreetOverrideMatcher._validate_unconditional_source_binding(named, excerpt)

        scope_status = named.get("qualifier_scope_status")
        resolvable = named.get("qualifier_predicate_resolvable_from_text")
        signals: list[str] = []
        if clause_source_anchored:
            signals.append(f"source-anchored qualifier_clause {clause!r}")
        if len(open_questions) > 0:
            signals.append(f"open_legal_questions {list(open_questions)!r}")
        if (
            isinstance(scope_status, str)
            and scope_status.strip()
            and scope_status.strip().casefold() != _QUALIFIER_SCOPE_RESOLVED
        ):
            signals.append(f"qualifier_scope_status {scope_status!r}")
        if resolvable is False:
            signals.append("qualifier_predicate_resolvable_from_text=False")
        if signals:
            raise NamedStreetOverrideError(
                "named_street_overrides.disposition_when_located is "
                "'matched_override' but the designation still carries unresolved "
                f"qualifier signal(s) {signals}; a conditioned override cannot be "
                "treated as unconditional and emptying the free-floating "
                "open_legal_questions list does not change that (fail closed at "
                "construction, DB-023a)"
            )

    @staticmethod
    def _validate_unconditional_source_binding(named: dict, excerpt: str) -> None:
        """DB-023a unconditional binding: establish a ``matched_override``
        (unconditional) disposition from the AUTHENTICATED, COMPLETE source span,
        or fail closed.

        Two source-bound conditions must BOTH hold; neither is the binding on its
        own (a word whitelist, capitalization, or bare substring membership never
        is):

        (1) COMPLETE-SPAN (primary). ``verbatim_source_quote`` is only constrained
            to be *a substring* of the digest-covered ``verbatim_excerpt`` - a
            substring a tamperer can NARROW to drop a trailing/interposed qualifier
            clause ("...which are separated by mapped public park...") while every
            structured row still anchors. An unconditional disposition must be
            established from the COMPLETE authenticated span, so the quote must
            occupy a whole sentence unit of the excerpt: it must begin at a span
            boundary (excerpt start, a newline, or a prior sentence terminator) and
            end at a sentence terminator followed by the span edge or whitespace. A
            quote cut before its terminator is a narrowed span and cannot bind.
        (2) NO-QUALIFIER on that complete span (defense in depth). Every token of
            the complete span must be accounted for by the fixed unconditional
            designation grammar (:data:`_UNCONDITIONAL_DESIGNATION_WORDS`), its
            numeric/ordinal cross-street tokens, or a CAPITALIZED proper-noun
            locator. A residual lowercase common word is an interposed/trailing
            clause, so a full conditional quote kept intact while the mutable
            qualifier metadata is stripped still fails closed.

        Both read ONLY digest-covered source (the excerpt and its substring quote)
        and NO mutable qualifier metadata, so the binding is tamper-evident. It
        decides NO legal question and is scoped to ``matched_override`` - an
        ``indeterminate`` disposition is unaffected."""
        quote = named.get("verbatim_source_quote", "")
        start = excerpt.find(quote)
        if not quote or start < 0:
            raise NamedStreetOverrideError(
                "named_street_overrides.verbatim_source_quote is empty or not "
                "located in the digest-covered excerpt; an unconditional binding "
                "cannot be established (fail closed at construction, DB-023a)"
            )
        preceding = excerpt[:start]
        following = excerpt[start + len(quote):]
        starts_at_boundary = (
            start == 0
            or preceding.endswith("\n")
            or preceding.rstrip(" ").endswith(".")
        )
        ends_at_boundary = quote.rstrip().endswith(".") and (
            following == "" or following[:1] in (" ", "\n")
        )
        if not (starts_at_boundary and ends_at_boundary):
            raise NamedStreetOverrideError(
                "named_street_overrides.disposition_when_located is "
                "'matched_override' but verbatim_source_quote is not a COMPLETE "
                "sentence span of the digest-covered excerpt (it begins mid-span or "
                "stops before its sentence terminator); a narrowed source span that "
                "drops an interposed or trailing qualifier clause cannot establish "
                "an unconditional designation - fail closed at construction "
                "(DB-023a complete-span binding)"
            )

        residual = sorted(
            {
                token
                for token in _SOURCE_WORD_TOKEN.findall(quote)
                if token.casefold() not in _UNCONDITIONAL_DESIGNATION_WORDS
                and not _NUMERIC_LOCATOR_TOKEN.match(token)
                and not token[:1].isupper()
            }
        )
        if residual:
            raise NamedStreetOverrideError(
                "named_street_overrides.disposition_when_located is "
                "'matched_override' but the complete digest-covered source span "
                "carries content the unconditional designation template cannot "
                f"account for {residual}; a trusted unconditional binding cannot be "
                "established from the pinned source, and mutable qualifier metadata "
                "(which may be stripped, emptied, or falsely resolved) cannot supply "
                "one - fail closed at construction (DB-023a source-bound)"
            )

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
                reason=(
                    f"street {_bounded_repr(query.street_name)} is not a "
                    "named-street override"
                ),
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
                    f"street {_bounded_repr(query.street_name)} is a named override "
                    "but not in the designated borough/community district "
                    f"({_bounded_repr(query.borough)}, CD {cd})"
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
                "segment bounds "
                f"{{{_bounded_repr(query.cross_street_from)}, "
                f"{_bounded_repr(query.cross_street_to)}}} "
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
                reason=block.get(
                    "disposition_reason",
                    "alternate-width district requires professional review",
                ),
                provision_id=block["provision_id"],
                provenance=self._alt_provenance(),
                open_legal_questions=tuple(block.get("open_legal_questions", ())),
            )
        return AlternateWidthResult(
            district=norm,
            coverage_class="not_applicable",
            reason=(
                f"district {_bounded_repr(district)} is not within the "
                "C5-3/C6-4/C6-6 alternate-width provision"
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
            reason=block.get(
                "disposition_reason",
                "located named-street row is INDETERMINATE (no disposition reason "
                "recorded)",
            ),
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
