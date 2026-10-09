"""Named-street override status construction (M5-T043 extraction; DB-028 a).

The ZR 12-10 named-street override *status* — the attestation about whether the
named-street override / alternate-width exceptions were consulted and resolved
for a wide-street determination — is constructed here, extracted out of
:mod:`app.rules.wide_street_wiring` at the G3 cohesion seam
(``project-control/reports/M5-T040-G3.md`` finding 6). It owns:

* :class:`MatchedNamedStreetOverride` — the distinct override provenance carried
  when a candidate segment DEFINITIVELY matched a designation;
* :class:`NamedStreetOverrideStatus` — the attestation the FAR determination
  consumes;
* :func:`build_named_street_override_status` — the M5-T040 wiring that runs the
  accepted ZR 12-10 matcher over the candidate segments (the FIRST production
  consumer of :mod:`app.rules.named_street_override`);
* :func:`_fully_resolved_typed_inputs` — the independent typed-input re-check the
  builder uses before an all-``NOT_MATCHED`` result may attest.

:mod:`app.rules.wide_street_wiring` re-exports :class:`MatchedNamedStreetOverride`,
:class:`NamedStreetOverrideStatus`, and :func:`build_named_street_override_status`
as a compatibility facade, so every existing public import path keeps resolving
and no consumer is edited.

Deterministic and side-effect-free; the matcher itself never fetches the network.
This decides NO legal question — a match escalates to a qualified human (G6).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.rules.named_street_override import (
    MatchStatus,
    NamedStreetOverrideMatcher,
    OverrideQuery,
    _normalize_cd,
)

__all__ = [
    "MatchedNamedStreetOverride",
    "NamedStreetOverrideStatus",
    "build_named_street_override_status",
]


@dataclass(frozen=True)
class MatchedNamedStreetOverride:
    """The distinct override provenance carried when a candidate segment
    DEFINITIVELY matched a ZR 12-10 named-street override designation (M5-T040
    wiring; AS-4). A match is a qualified-legal determination that the designated
    street is WIDE regardless of its numeric width - so it is never applied
    numerically here (M5-T039 ruling; the C5-3/C6-4/C6-6 alternate-width value
    stays in the G6 legal queue) and forces a professional-review determination.

    ``snapshot_sha256`` / ``section_anchor`` / ``provision_id`` /
    ``matched_row_verbatim`` are the four provenance elements the refusal must
    carry (from the matcher's :class:`OverrideProvenance`). ``reason`` is the
    composed, user-reachable explanation folded into the determination's reason."""

    provision_id: str | None
    snapshot_sha256: str | None
    section_anchor: str | None
    matched_row_verbatim: str | None
    reason: str


@dataclass(frozen=True)
class NamedStreetOverrideStatus:
    """Attestation about the named-street override / alternate-width table
    (M4-T021 G3 A1 elevated criterion; AS-4). Built either directly or, from
    M5-T040, by :func:`build_named_street_override_status`, which runs the
    accepted ZR 12-10 matcher over the candidate segments.

    ``override_table_implemented`` - whether the ZR 12-10 named-street override
    matcher (Broadway W94-97 CD7; Allen St Rivington-Delancey CD3) and the
    C5-3/C6-4/C6-6 alternate-width clause were APPLIED and fully resolved for this
    determination. ``build_named_street_override_status`` sets it True once the
    matcher actually ran and resolved every candidate segment; a hand-built status
    may leave it False.
    ``segment_may_touch_named_override`` - whether any candidate segment may fall
    under one of those provisions but could NOT be cleared. When the matcher could
    not resolve/apply the table for this determination
    (``override_table_implemented`` False), ``exceptions_checked`` can never be
    True and a ``wide``-tending lot fails safe to professional review.
    ``note`` - free-form provenance (required, may be explicitly None).
    ``matched_override`` - set (non-None) ONLY when a candidate segment
    DEFINITIVELY matched a named-street override designation with fully-resolved
    inputs. It carries the distinct override provenance and forces a
    professional-review determination; ``exceptions_checked`` is never True.
    """

    override_table_implemented: bool
    segment_may_touch_named_override: bool
    note: str | None
    matched_override: MatchedNamedStreetOverride | None = None


def _fully_resolved_typed_inputs(query: OverrideQuery) -> bool:
    """True only when a candidate segment's locator is TYPED and NORMALIZED on
    every dimension the ZR 12-10 matcher keys on: borough, street name, and BOTH
    cross-street bounds are non-blank ``str`` values, and the community district
    normalizes to a single integer (:func:`_normalize_cd`).

    The matcher SHORT-CIRCUITS to ``NOT_MATCHED`` for an ordinary (non-override)
    street WITHOUT ever inspecting the cross-street bounds, and it COERCES a
    non-string locator (``str()`` / digit-scan) before it can reach that
    short-circuit. So a ``NOT_MATCHED`` alone does NOT establish typed, normalized
    inputs. The wiring re-establishes them here, INDEPENDENTLY of that coercing
    short-circuit, before an all-``NOT_MATCHED`` result may attest
    ``exceptions_checked``: a malformed-but-nonblank field (a non-string bound, a
    list community district) can never clear the exception (D-051 fail-closed)."""
    for field in (
        query.borough,
        query.street_name,
        query.cross_street_from,
        query.cross_street_to,
    ):
        if not isinstance(field, str) or not field.strip():
            return False
    cd = query.community_district
    if isinstance(cd, bool) or not isinstance(cd, (int, str)):
        return False
    return _normalize_cd(cd) is not None


def build_named_street_override_status(
    matcher: NamedStreetOverrideMatcher,
    segment_queries: Sequence[OverrideQuery],
    *,
    note: str | None = None,
) -> NamedStreetOverrideStatus:
    """Run the accepted ZR 12-10 named-street override matcher over the candidate
    street segments and produce the wiring's :class:`NamedStreetOverrideStatus`,
    fail-closed (D-051; M5-T040 wiring - the FIRST production consumer of
    :mod:`app.rules.named_street_override`).

    The matcher's typed tri-state drives the outcome:

    * Any candidate segment returns ``MATCHED_OVERRIDE`` -> a DEFINITIVE
      named-street override designation applies. The status carries the distinct
      override provenance (:class:`MatchedNamedStreetOverride`: snapshot sha256,
      section anchor, provision id, verbatim matched row) and forces a
      professional-review determination; the designated-wide value is NEVER
      applied numerically (M5-T039 ruling). Decisive - the first match wins.
    * Every candidate segment returns ``NOT_MATCHED`` **with fully-resolved,
      typed inputs** -> the override table was applied and no designation applies,
      so the exception is genuinely CHECKED AND RESOLVED
      (``override_table_implemented`` True, ``segment_may_touch`` False).
      Fully-resolved is established INDEPENDENTLY of the matcher's coercing
      NOT_MATCHED short-circuit (:func:`_fully_resolved_typed_inputs`): the
      candidate's borough, street, and BOTH cross-street bounds must be non-blank
      strings and the community district must normalize to a single int. The
      matcher can reach NOT_MATCHED for an ordinary street WITHOUT inspecting the
      bounds and coerces non-string locators, so a malformed-but-nonblank field
      (a non-string bound, a list community district) can never attest here.
    * Any ``INDETERMINATE``, any ``NOT_MATCHED`` on a segment whose locator is not
      fully typed/normalized, or an empty candidate list -> the segment could not
      be cleared, so the existing refusal stands unchanged (``segment_may_touch``
      True, ``override_table_implemented`` False): ``exceptions_checked`` can never
      be True. Missing/unresolvable/malformed input is a refusal, never a guessed
      NOT_MATCHED.

    Deterministic and side-effect-free; the matcher itself never fetches the
    network. This decides NO legal question - a match escalates to a qualified
    human (G6)."""
    if not segment_queries:
        return NamedStreetOverrideStatus(
            override_table_implemented=False,
            segment_may_touch_named_override=True,
            note=(
                note
                or "no candidate street segment was supplied to the ZR 12-10 "
                "named-street override matcher; the exception could not be checked, "
                "so it is left unresolved (fail-closed)"
            ),
        )

    unresolved = False
    for query in segment_queries:
        result = matcher.match(query)
        if result.status is MatchStatus.MATCHED_OVERRIDE:
            prov = result.provenance
            snapshot_sha256 = prov.snapshot_sha256 if prov is not None else None
            section_anchor = prov.section_anchor if prov is not None else None
            matched_row_verbatim = (
                prov.matched_row_verbatim if prov is not None else None
            )
            reason = (
                "a candidate street segment DEFINITIVELY matched a ZR 12-10 "
                "named-street override designation (provision "
                f"{result.provision_id!r}; section anchor {section_anchor!r}; "
                f"snapshot sha256 {snapshot_sha256}); the designated-wide override "
                "is a qualified-legal determination, so the alternate/named-street "
                "width is NOT applied numerically and the wide-street FAR is "
                "withheld - professional review required (DRAFT, pending G6). "
                f"Matched designation: {matched_row_verbatim!r}"
            )
            return NamedStreetOverrideStatus(
                override_table_implemented=True,
                segment_may_touch_named_override=True,
                note=(
                    note
                    or "a candidate segment matched a ZR 12-10 named-street override "
                    "designation (professional review)"
                ),
                matched_override=MatchedNamedStreetOverride(
                    provision_id=result.provision_id,
                    snapshot_sha256=snapshot_sha256,
                    section_anchor=section_anchor,
                    matched_row_verbatim=matched_row_verbatim,
                    reason=reason,
                ),
            )
        if result.status is MatchStatus.INDETERMINATE:
            unresolved = True
            continue
        # NOT_MATCHED clears the exception for THIS segment only when the
        # candidate's locator is TYPED and fully NORMALIZED - borough/street/both
        # cross-streets non-blank strings and the community district a single int.
        # The matcher can reach NOT_MATCHED via a short-circuit (an ordinary
        # non-override street) WITHOUT inspecting the bounds, and it coerces
        # non-string inputs along the way, so the wiring re-establishes typed,
        # normalized inputs here rather than trusting that coerced NOT_MATCHED
        # (AS-4; a malformed-but-nonblank field never attests exceptions_checked).
        if not _fully_resolved_typed_inputs(query):
            unresolved = True

    if unresolved:
        return NamedStreetOverrideStatus(
            override_table_implemented=False,
            segment_may_touch_named_override=True,
            note=(
                note
                or "at least one candidate segment could not be resolved to "
                "NOT_MATCHED with fully-resolved inputs (missing community district "
                "or cross-street bounds, or an indeterminate locator); the ZR 12-10 "
                "named-street override exception is unresolved (fail-closed)"
            ),
        )

    return NamedStreetOverrideStatus(
        override_table_implemented=True,
        segment_may_touch_named_override=False,
        note=(
            note
            or "every candidate segment resolved NOT_MATCHED with fully-resolved "
            "inputs; the ZR 12-10 named-street override table was applied and no "
            "designation applies to this lot"
        ),
    )
