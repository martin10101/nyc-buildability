"""Typed, append-only ``SiteDefinitionConfirmation`` records (task M5-T059, D-078).

A ``SiteDefinitionConfirmation`` is the durable, provenance-carrying record of a
HUMAN professional's decision to treat a multi-lot condominium's recorded base tax
lots as ONE development site (owner's one-click "treat lots 32+33 as one site"
flow). It is the substrate the D-078 confirmation UI writes to; it is NEVER
produced by the system on its own (D-078-R002: the system never auto-selects a
site definition, never defaults one, and never changes a confirmation's status by
any automated act - only a human does).

Slice 1 (this module) is RECORD SUBSTRATE ONLY. NO calculation path reads a
confirmation and NO code path selects a combined-land substrate from one:
calculations-on-confirmed-combined-land is a later slice. Two honest limits are
LOUD and TYPED here, never papered over:

- Identity is self-attested. The authentication scheme is deferred under blocker
  B-001, so every confirmation carries ``attestation_status =
  'unauthenticated_self_attested'`` and :attr:`SiteDefinitionConfirmation.refused_for_calculation`
  is ``True`` - a self-attested confirmation is REFUSED for any calculation use.
  Slice 1 has no calculation use at all, which the prohibition tests prove.
- Persistence is ephemeral. The store (:mod:`app.site_definition.store`) is an
  in-memory implementation on the ``documents/storage.py`` B-001 deferral
  precedent; it does not survive a process restart and the production durable
  store is deferred.

Append-only invariants (the ``documents/correction_history.py`` precedent):

- A created record is IMMUTABLE. It is never edited, deleted, reordered, or
  replaced in place; a mutation attempt is a typed refusal, not a silent write.
- The initial status of every created record is :attr:`ConfirmationStatus.ACTIVE`.
  A status change is an APPENDED :class:`StatusTransition` event, never a rewrite
  of the frozen record: the current status and the ``superseded_by_id`` back-link
  are DERIVED from the transition log (:class:`ConfirmationView`), so the immutable
  original is never touched.
- Exactly ONE active record exists per ``condo_key`` at a time. A duplicate create
  while one is active is a typed 409-class refusal; supersession is the only
  replacement path.
- Supersede yields a NEW active record chained to the old (``supersedes_id`` on the
  new, ``superseded_by_id`` derived onto the old) and requires a reason. Revoke is
  terminal and requires a reason (the ``TransitionReasonRequired`` precedent).

Parcel binding is STRICT. The confirmed ``parcels`` (a sorted tuple of base BBLs)
must equal the resolver's ``base_bbls`` at confirmation time EXACTLY - a subset,
superset, or otherwise different set is a typed refusal, because a looser binding
(confirming a site that is not the set the city records) is itself a legal
determination the system must never make. Order alone never refuses: both sides
are normalized to a sorted, de-duplicated tuple first.

If a LATER resolution returns different base lots, a consumer may surface the
factual discrepancy (recorded parcels vs current resolver output) but this module
NEVER changes a confirmation's status for it - status changes only by a human act
(D-078-R002).
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime

__all__ = [
    "SITE_DEFINITION_STATUS_CONFIRMED",
    "SITE_DEFINITION_STATUS_UNCONFIRMED",
    "AttestationStatus",
    "ConfirmationNotActiveError",
    "ConfirmationNotFoundError",
    "ConfirmationStatus",
    "ConfirmationView",
    "ConfirmerRole",
    "DuplicateActiveConfirmationError",
    "InvalidConfirmerError",
    "ParcelSetMismatchError",
    "ResolutionProvenanceSnapshot",
    "SiteConfirmer",
    "SiteDefinitionConfirmation",
    "SiteDefinitionError",
    "StatusTransition",
    "TransitionReasonRequiredError",
    "build_site_definition_block",
    "create_confirmation",
    "make_confirmer",
    "normalize_parcels",
]

# The condo-records document's ``site_definition`` block status vocabulary: a
# recorded ACTIVE confirmation makes the site CONFIRMED; the honest default (no
# active confirmation) is UNCONFIRMED. The system never moves this itself.
SITE_DEFINITION_STATUS_CONFIRMED = "confirmed"
SITE_DEFINITION_STATUS_UNCONFIRMED = "unconfirmed"


# --------------------------------------------------------------- vocabularies


@enum.unique
class ConfirmationStatus(enum.Enum):
    """Closed lifecycle status of a confirmation. ONE field, never a pair of
    booleans: a record is ACTIVE at creation and moves to SUPERSEDED or REVOKED
    only via an appended :class:`StatusTransition`, only by a human act."""

    ACTIVE = "active"
    SUPERSEDED = "superseded"
    REVOKED = "revoked"


@enum.unique
class ConfirmerRole(enum.Enum):
    """Closed HUMAN confirmer vocabulary, verbatim from the review-authz /
    correction-history precedent (``user`` / ``qualified_professional``). Exact
    match only - no AI, model, agent, service, or system identity is
    representable, so a confirmation can never be authored by an automated
    principal (CLAUDE.md principle 1; D-078-R002)."""

    USER = "user"
    QUALIFIED_PROFESSIONAL = "qualified_professional"


@enum.unique
class AttestationStatus(enum.Enum):
    """Closed attestation vocabulary. Slice 1 has exactly ONE member: the
    authentication scheme is B-001-blocked, so every confirmation is
    self-attested and LOUDLY labelled as such. The vocabulary extends ADDITIVELY
    only, with the auth design that grounds an authenticated member; until then a
    confirmation carrying this status is refused for any calculation use."""

    UNAUTHENTICATED_SELF_ATTESTED = "unauthenticated_self_attested"


# The attestation statuses that are REFUSED for any calculation use. Slice 1: the
# only status is self-attested and it is refused, so no confirmation is ever
# calculation-eligible here (there is no calculation path at all). A future
# authenticated status is added to the vocabulary, not to this refusal set.
_REFUSED_FOR_CALCULATION: frozenset[AttestationStatus] = frozenset(
    {AttestationStatus.UNAUTHENTICATED_SELF_ATTESTED}
)


# ------------------------------------------------------------------ exceptions


class SiteDefinitionError(Exception):
    """Base class for every typed site-definition refusal. Raised - never
    returned - so a caller that forgets to handle one cannot silently proceed
    with an unvalidated site definition. Each subclass carries a ``reject_code``
    the API layer serializes uniformly."""

    reject_code = "site_definition_error"


class ParcelSetMismatchError(SiteDefinitionError):
    """The confirmed parcel set does not EXACTLY equal the resolver's base lots.

    A subset, superset, or otherwise divergent set is refused: confirming a site
    that is not the set the city records is a legal determination the system must
    never make. Carries the normalized submitted and expected sets so the refusal
    names the exact mismatch (order alone never triggers it)."""

    reject_code = "parcel_set_mismatch"

    def __init__(
        self, submitted: tuple[str, ...], expected: tuple[str, ...]
    ) -> None:
        self.submitted = submitted
        self.expected = expected
        missing = tuple(bbl for bbl in expected if bbl not in submitted)
        extra = tuple(bbl for bbl in submitted if bbl not in expected)
        super().__init__(
            "confirmed parcel set must equal the resolver's recorded base lots "
            f"exactly; missing {list(missing)}, unexpected {list(extra)} - a "
            "subset, superset, or divergent set is refused (a looser site binding "
            "is a legal determination the system never makes)"
        )


class InvalidConfirmerError(SiteDefinitionError):
    """The confirmer's name or role is not the closed HUMAN vocabulary (a blank
    name, or a role outside ``user``/``qualified_professional``). An AI, model,
    agent, service, or system identity is unrepresentable and refused."""

    reject_code = "invalid_confirmer"


class DuplicateActiveConfirmationError(SiteDefinitionError):
    """A second create while one confirmation is already ACTIVE for the same
    ``condo_key`` (the 409-class refusal). Supersession is the only replacement
    path; a plain re-create is refused so there is never more than one active
    site definition per condo."""

    reject_code = "duplicate_active_confirmation"


class OrphanSupersedeError(SiteDefinitionError):
    """A ``supersedes_id``-carrying confirmation offered to ``create`` instead of
    ``supersede`` ([ORCH-CORRECTED per T059 G4-C-2]). Admitting it would mint an
    ACTIVE record whose chain reference the transition log never flipped — an
    append-only-integrity hole; the supersede operation is the only path that
    records the replaced record's status change."""

    reject_code = "supersede_via_create_refused"


class TransitionReasonRequiredError(SiteDefinitionError):
    """A supersede or revoke without a non-empty human reason (the
    ``TransitionReasonRequired`` precedent). A status change with no stated reason
    is not reviewable and is refused."""

    reject_code = "transition_reason_required"


class ConfirmationNotFoundError(SiteDefinitionError):
    """No confirmation exists for the given record id."""

    reject_code = "confirmation_not_found"


class ConfirmationNotActiveError(SiteDefinitionError):
    """The targeted confirmation is not currently ACTIVE, so it cannot be
    superseded or revoked (a superseded or revoked record is terminal for those
    operations). Fail-closed: the status is DERIVED from the transition log,
    never trusted from a caller."""

    reject_code = "confirmation_not_active"


# ------------------------------------------------------------------ value types


@dataclass(frozen=True)
class SiteConfirmer:
    """The HUMAN who confirmed the site definition. ``role`` is the closed-vocab
    member; ``name`` is the self-attested display identity (non-empty). No
    automated principal is representable."""

    name: str
    role: ConfirmerRole

    def to_payload(self) -> dict:
        return {"name": self.name, "role": self.role.value}


@dataclass(frozen=True)
class ResolutionProvenanceSnapshot:
    """A byte-copy of the resolution provenance the ``CondoResolution`` showed at
    confirmation time, so the confirmation records WHY these parcels were the site
    (the same provenance discipline every material fact carries). Recorded
    verbatim, never re-derived later - if a later resolution differs, that is a
    surfaced discrepancy, not a rewrite of this snapshot."""

    source_id: str | None
    dataset_ids: tuple[str, ...]
    retrieved_at: str | None
    resolution_path: str | None

    def to_payload(self) -> dict:
        return {
            "source_id": self.source_id,
            "dataset_ids": list(self.dataset_ids),
            "retrieved_at": self.retrieved_at,
            "resolution_path": self.resolution_path,
        }


@dataclass(frozen=True)
class SiteDefinitionConfirmation:
    """One IMMUTABLE created confirmation record.

    The frozen creation snapshot. Its lifecycle ``status`` is NOT stored here (a
    created record is always ACTIVE at creation); the current status and the
    ``superseded_by_id`` back-link are DERIVED from the append-only
    :class:`StatusTransition` log via :class:`ConfirmationView`, so the original is
    never edited in place. ``supersedes_id`` IS carried here because it is known at
    creation (the new record knows what it replaces); ``reason`` is the creation
    reason and is REQUIRED exactly when this record supersedes another.
    """

    record_id: str
    condo_key: str
    billing_bbl: str
    entered_bbl: str
    parcels: tuple[str, ...]
    confirmer: SiteConfirmer
    attestation_status: AttestationStatus
    confirmed_at: str
    provenance: ResolutionProvenanceSnapshot
    supersedes_id: str | None = None
    reason: str | None = None
    note: str | None = None

    @property
    def refused_for_calculation(self) -> bool:
        """``True`` when this confirmation's attestation status is refused for any
        calculation use. Slice 1: always ``True`` (self-attested, B-001). Slice 1
        has no calculation path, so this is a LOUD label, never a live gate."""
        return self.attestation_status in _REFUSED_FOR_CALCULATION

    def to_payload(self) -> dict:
        """Serializable snapshot of the immutable record (status/back-link are on
        :class:`ConfirmationView`, which derives them from the transition log)."""
        return {
            "record_id": self.record_id,
            "condo_key": self.condo_key,
            "billing_bbl": self.billing_bbl,
            "entered_bbl": self.entered_bbl,
            "parcels": list(self.parcels),
            "confirmer": self.confirmer.to_payload(),
            "attestation_status": self.attestation_status.value,
            "refused_for_calculation": self.refused_for_calculation,
            "confirmed_at": self.confirmed_at,
            "supersedes_id": self.supersedes_id,
            "reason": self.reason,
            "note": self.note,
            "provenance": self.provenance.to_payload(),
        }


@dataclass(frozen=True)
class StatusTransition:
    """One APPENDED lifecycle event. The record's status is the latest
    transition's ``to_status`` (or ACTIVE when none exists); a supersede
    transition also carries ``superseded_by_id`` (the new record that replaced the
    old). Immutable and never reordered - the log is the append-only source of
    truth for status, so the frozen record is never edited in place."""

    record_id: str
    from_status: ConfirmationStatus
    to_status: ConfirmationStatus
    at: str
    reason: str
    actor: SiteConfirmer
    superseded_by_id: str | None = None

    def to_payload(self) -> dict:
        return {
            "record_id": self.record_id,
            "from_status": self.from_status.value,
            "to_status": self.to_status.value,
            "at": self.at,
            "reason": self.reason,
            "actor": self.actor.to_payload(),
            "superseded_by_id": self.superseded_by_id,
        }


@dataclass(frozen=True)
class ConfirmationView:
    """A read-only VIEW combining an immutable record with its DERIVED current
    status and ``superseded_by_id`` back-link (computed from the transition log).
    This is what the store returns and what surfaces serialize: the immutable
    original stays untouched while the current lifecycle state is always derived,
    never a rewrite."""

    record: SiteDefinitionConfirmation
    status: ConfirmationStatus
    superseded_by_id: str | None = None
    transitions: tuple[StatusTransition, ...] = field(default_factory=tuple)

    def to_payload(self) -> dict:
        payload = self.record.to_payload()
        payload["status"] = self.status.value
        payload["superseded_by_id"] = self.superseded_by_id
        payload["transitions"] = [t.to_payload() for t in self.transitions]
        return payload


# --------------------------------------------------------------------- helpers


def normalize_parcels(parcels: object) -> tuple[str, ...]:
    """Normalize a parcel set to a sorted, de-duplicated tuple of non-empty BBL
    strings, so order and duplicates never affect strict-equality binding. A
    non-list/tuple, a non-string entry, or a blank entry is a typed refusal - a
    malformed parcel set can never silently become a site definition."""
    if not isinstance(parcels, (list, tuple)):
        raise InvalidConfirmerError(
            "parcels must be an array of base-lot BBL strings, got "
            f"{type(parcels).__name__}"
        )
    cleaned: set[str] = set()
    for entry in parcels:
        if not isinstance(entry, str) or not entry.strip():
            raise InvalidConfirmerError(
                "every parcel must be a non-empty base-lot BBL string; a blank or "
                "non-string parcel is not a recorded lot"
            )
        cleaned.add(entry.strip())
    if not cleaned:
        raise InvalidConfirmerError(
            "a site definition needs at least one recorded base lot; the parcel "
            "set is empty"
        )
    return tuple(sorted(cleaned))


def _validate_confirmer(name: object, role: object) -> SiteConfirmer:
    if not isinstance(name, str) or not name.strip():
        raise InvalidConfirmerError(
            "confirmer name must be a non-empty string - an anonymous self "
            "attestation is not identity evidence"
        )
    if not isinstance(role, str):
        raise InvalidConfirmerError(
            f"confirmer role must be a string, got {type(role).__name__}"
        )
    try:
        confirmer_role = ConfirmerRole(role)
    except ValueError as exc:
        supported = ", ".join(sorted(member.value for member in ConfirmerRole))
        raise InvalidConfirmerError(
            f"confirmer role {role!r} is outside the closed human vocabulary "
            f"(supported: {supported}); exact match only - no AI, model, agent, "
            "service, or system identity can author a confirmation"
        ) from exc
    return SiteConfirmer(name=name.strip(), role=confirmer_role)


def make_confirmer(name: object, role: object) -> SiteConfirmer:
    """Public constructor for a validated :class:`SiteConfirmer` (the closed human
    vocabulary). Raises :class:`InvalidConfirmerError` on a blank name or a role
    outside ``user``/``qualified_professional``. Used by the revoke path, which
    needs a validated actor without building a whole confirmation."""
    return _validate_confirmer(name, role)


def _require_reason(reason: object) -> str:
    if not isinstance(reason, str) or not reason.strip():
        raise TransitionReasonRequiredError(
            "a reason is required and must be a non-empty string - a site "
            "definition change with no stated reason is not reviewable"
        )
    return reason.strip()


def _confirmed_at_iso(confirmed_at: datetime) -> str:
    """Validate a tz-aware datetime and render its RFC 3339 wire form. A naive
    datetime is refused: a confirmation with no timezone cannot prove WHEN it was
    made."""
    if not isinstance(confirmed_at, datetime) or confirmed_at.tzinfo is None:
        raise SiteDefinitionError(
            "confirmed_at must be a timezone-aware datetime - a naive timestamp "
            "cannot honestly record when the confirmation was made"
        )
    return confirmed_at.isoformat()


def create_confirmation(
    *,
    condo_key: str,
    billing_bbl: str,
    entered_bbl: str,
    proposed_parcels: object,
    resolver_base_bbls: object,
    confirmer_name: object,
    confirmer_role: object,
    confirmed_at: datetime,
    provenance: ResolutionProvenanceSnapshot,
    note: object = None,
    reason: object = None,
    supersedes_id: str | None = None,
    record_id: str | None = None,
) -> SiteDefinitionConfirmation:
    """Build a validated, immutable :class:`SiteDefinitionConfirmation` (pure - it
    touches no store).

    Enforces the STRICT parcel binding (``proposed_parcels`` normalized must equal
    ``resolver_base_bbls`` normalized), the closed human confirmer vocabulary, the
    fixed self-attested attestation status, a tz-aware ``confirmed_at``, and - when
    ``supersedes_id`` is set - a required creation reason. Raises a typed
    :class:`SiteDefinitionError` subclass on any violation; never returns a
    partially-valid record. ``attestation_status`` is set server-side and never
    read from a caller payload (an untrusted body cannot claim authentication).
    """
    submitted = normalize_parcels(proposed_parcels)
    expected = normalize_parcels(resolver_base_bbls)
    if submitted != expected:
        raise ParcelSetMismatchError(submitted=submitted, expected=expected)
    confirmer = _validate_confirmer(confirmer_name, confirmer_role)
    if note is not None and not isinstance(note, str):
        raise SiteDefinitionError(
            f"note, when present, must be a string, got {type(note).__name__}"
        )
    creation_reason: str | None = None
    if supersedes_id is not None:
        creation_reason = _require_reason(reason)
    elif reason is not None:
        if not isinstance(reason, str):
            raise SiteDefinitionError(
                f"reason, when present, must be a string, got {type(reason).__name__}"
            )
        creation_reason = reason.strip() or None
    return SiteDefinitionConfirmation(
        record_id=record_id or uuid.uuid4().hex,
        condo_key=condo_key,
        billing_bbl=billing_bbl,
        entered_bbl=entered_bbl,
        parcels=submitted,
        confirmer=confirmer,
        attestation_status=AttestationStatus.UNAUTHENTICATED_SELF_ATTESTED,
        confirmed_at=_confirmed_at_iso(confirmed_at),
        provenance=provenance,
        supersedes_id=supersedes_id,
        reason=creation_reason,
        note=(note if isinstance(note, str) and note.strip() else None),
    )


def build_site_definition_block(
    *,
    condo_key: str | None,
    views: tuple[ConfirmationView, ...],
    resolver_base_bbls: object = None,
) -> dict:
    """Assemble the ADDITIVE ``site_definition`` block for the condo-records
    multi-lot document from the recorded confirmations (``views``, newest first).

    READ-ONLY surfacing: this reads confirmations, it never selects a site and
    never changes any status (D-078-R002). The block is CONFIRMED only when an
    ACTIVE confirmation exists; the honest default is UNCONFIRMED with an explicit
    null active confirmation. When ``resolver_base_bbls`` is supplied and an active
    confirmation exists, a factual discrepancy between the recorded parcels and the
    current resolver output is SURFACED (never used to change the confirmation's
    status - a later resolution differing is a surfaced fact, not a human act).
    """
    active = next(
        (view for view in views if view.status is ConfirmationStatus.ACTIVE), None
    )
    block: dict = {
        "condo_key": condo_key,
        "status": (
            SITE_DEFINITION_STATUS_CONFIRMED
            if active is not None
            else SITE_DEFINITION_STATUS_UNCONFIRMED
        ),
        "active_confirmation": active.to_payload() if active is not None else None,
        "confirmations": [view.to_payload() for view in views],
        "parcel_discrepancy": None,
        "note": (
            "This site definition is a recorded human confirmation. The system "
            "never selects or defaults one; when no active confirmation exists the "
            "site is unconfirmed and every calculation stays on its honest "
            "unconfirmed refusal. A self-attested confirmation is refused for any "
            "calculation use until authentication exists (B-001)."
        ),
    }
    if active is not None and resolver_base_bbls is not None:
        try:
            current = normalize_parcels(resolver_base_bbls)
        except SiteDefinitionError:
            current = None
        if current is not None and current != active.record.parcels:
            block["parcel_discrepancy"] = {
                "recorded_parcels": list(active.record.parcels),
                "current_resolver_parcels": list(current),
                "note": (
                    "The base lots the resolver returns now differ from the lots "
                    "recorded in the active confirmation. This is surfaced as a "
                    "factual discrepancy for professional review; it does NOT "
                    "change the confirmation's status, which changes only by a "
                    "human act."
                ),
            }
    return block
