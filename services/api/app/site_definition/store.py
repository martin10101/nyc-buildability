"""Abstract site-definition store + in-memory implementation (task M5-T059).

The store owns the APPEND-ONLY lifecycle of :class:`SiteDefinitionConfirmation`
records: it enforces the ONE-active-per-``condo_key`` invariant, records status
changes as APPENDED :class:`StatusTransition` events (never an edit of a frozen
record), and derives each record's current status and ``superseded_by_id``
back-link from that append-only log.

B-001 honesty (the ``app.documents.storage.py`` precedent): the production durable
store is DEFERRED under blocker B-001. :class:`InMemorySiteDefinitionStore` here is
the CI/local implementation ONLY - a plain in-process dictionary with NO database,
NO persistence, and NO concurrency safety. Its confirmations DO NOT survive a
process restart. Production code binds to the :class:`SiteDefinitionStore`
interface; the durable implementation (and the authentication that lets a
confirmation carry more than a self-attested identity) lands when B-001 resolves,
and the write-shaped API route stays UNMOUNTED until then - production-unreachable
is the safe state for a write endpoint with an ephemeral store and no auth.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.site_definition.records import (
    ConfirmationNotActiveError,
    ConfirmationNotFoundError,
    ConfirmationStatus,
    ConfirmationView,
    DuplicateActiveConfirmationError,
    OrphanSupersedeError,
    SiteConfirmer,
    SiteDefinitionConfirmation,
    StatusTransition,
    TransitionReasonRequiredError,
)

__all__ = [
    "InMemorySiteDefinitionStore",
    "SiteDefinitionStore",
    "default_site_definition_store",
]


class SiteDefinitionStore(ABC):
    """Append-only store of site-definition confirmations.

    Implementations MUST: refuse a duplicate create while one confirmation is
    active for a ``condo_key`` (typed 409-class), record every status change as an
    appended transition (never an in-place edit), derive the current status and
    ``superseded_by_id`` from the transition log, and require a non-empty reason on
    supersede and revoke.
    """

    @abstractmethod
    def create(self, confirmation: SiteDefinitionConfirmation) -> ConfirmationView:
        """Append a NEW confirmation as ACTIVE; typed refusal if one is already
        active for its ``condo_key``."""

    @abstractmethod
    def get(self, record_id: str) -> ConfirmationView:
        """Return the view for ``record_id`` (typed not-found refusal if absent)."""

    @abstractmethod
    def list_for_condo_key(self, condo_key: str) -> tuple[ConfirmationView, ...]:
        """Every confirmation for ``condo_key`` (active, superseded, and revoked),
        newest first."""

    @abstractmethod
    def supersede(
        self, old_id: str, new_confirmation: SiteDefinitionConfirmation
    ) -> ConfirmationView:
        """Supersede the ACTIVE record ``old_id`` with ``new_confirmation`` (which
        must carry ``supersedes_id == old_id`` and a creation reason); append the
        new record and the old record's superseded transition. Returns the NEW
        record's view."""

    @abstractmethod
    def revoke(
        self,
        record_id: str,
        *,
        condo_key: str,
        reason: str,
        actor: SiteConfirmer,
        at: str,
    ) -> ConfirmationView:
        """Revoke the ACTIVE record ``record_id`` (reason required); append a
        terminal revoked transition. Returns the revoked record's view.

        [ORCH-CORRECTED per T059 G3-C1/G5-F1] ``condo_key`` BINDS the revocation
        to the condo the caller addressed: implementations MUST refuse (typed
        not-found, mirroring :meth:`supersede`'s binding) when the stored record's
        ``condo_key`` differs — the path identity is the route's only resource
        scoping, and an unbound revoke is a cross-property IDOR at mount time."""


class InMemorySiteDefinitionStore(SiteDefinitionStore):
    """CI/local-only in-memory store (see module docstring re B-001). Not
    concurrency-safe and not durable; acceptable only for single-process
    CI/local use."""

    def __init__(self) -> None:
        # Insertion-ordered immutable records, and the append-only transition log.
        self._records: dict[str, SiteDefinitionConfirmation] = {}
        self._transitions: list[StatusTransition] = []
        # [ORCH-CORRECTED per T059 G4-C-1] monotone insertion sequence: the
        # deterministic tie-breaker that makes "newest first" TRUE on a
        # same-instant confirmed_at pair (Python's stable sort preserves
        # insertion order for equal keys, so a timestamp alone cannot honor
        # the ABC's newest-first contract on a tie).
        self._insertion_seq: dict[str, int] = {}
        self._next_seq = 0

    # -- derivation (the append-only log is the source of truth for status) ---
    def _current_status(self, record_id: str) -> ConfirmationStatus:
        status = ConfirmationStatus.ACTIVE
        for transition in self._transitions:
            if transition.record_id == record_id:
                status = transition.to_status
        return status

    def _superseded_by(self, record_id: str) -> str | None:
        for transition in self._transitions:
            if (
                transition.record_id == record_id
                and transition.to_status is ConfirmationStatus.SUPERSEDED
            ):
                return transition.superseded_by_id
        return None

    def _transitions_for(self, record_id: str) -> tuple[StatusTransition, ...]:
        return tuple(t for t in self._transitions if t.record_id == record_id)

    def _view(self, record: SiteDefinitionConfirmation) -> ConfirmationView:
        return ConfirmationView(
            record=record,
            status=self._current_status(record.record_id),
            superseded_by_id=self._superseded_by(record.record_id),
            transitions=self._transitions_for(record.record_id),
        )

    def _active_record_for(
        self, condo_key: str
    ) -> SiteDefinitionConfirmation | None:
        for record in self._records.values():
            if (
                record.condo_key == condo_key
                and self._current_status(record.record_id) is ConfirmationStatus.ACTIVE
            ):
                return record
        return None

    def _require_active(self, record_id: str) -> SiteDefinitionConfirmation:
        record = self._records.get(record_id)
        if record is None:
            raise ConfirmationNotFoundError(
                f"no site-definition confirmation exists for record id {record_id!r}"
            )
        if self._current_status(record_id) is not ConfirmationStatus.ACTIVE:
            raise ConfirmationNotActiveError(
                f"confirmation {record_id!r} is "
                f"{self._current_status(record_id).value!r}, not active; a "
                "superseded or revoked confirmation cannot be superseded or revoked"
            )
        return record

    # -- operations ----------------------------------------------------------
    def _record_insert(self, confirmation: SiteDefinitionConfirmation) -> None:
        self._records[confirmation.record_id] = confirmation
        self._insertion_seq[confirmation.record_id] = self._next_seq
        self._next_seq += 1

    def create(self, confirmation: SiteDefinitionConfirmation) -> ConfirmationView:
        # [ORCH-CORRECTED per T059 G4-C-2] a supersedes_id-carrying record MUST
        # go through supersede() (which flips the old record's status as an
        # appended transition); admitting it here would create an ACTIVE record
        # whose chain reference points at nothing the log ever flipped — an
        # append-only-integrity hole at the public ABC boundary.
        if confirmation.supersedes_id is not None:
            raise OrphanSupersedeError(
                "a confirmation that supersedes another record "
                f"({confirmation.supersedes_id!r}) cannot be created directly; "
                "use the supersede operation so the superseded record's status "
                "change is appended to the transition log"
            )
        active = self._active_record_for(confirmation.condo_key)
        if active is not None:
            raise DuplicateActiveConfirmationError(
                "an active site-definition confirmation already exists for condo "
                f"key {confirmation.condo_key!r} (record {active.record_id!r}); "
                "supersede it instead of creating a duplicate - only one site "
                "definition is active per condo at a time"
            )
        self._record_insert(confirmation)
        return self._view(confirmation)

    def get(self, record_id: str) -> ConfirmationView:
        record = self._records.get(record_id)
        if record is None:
            raise ConfirmationNotFoundError(
                f"no site-definition confirmation exists for record id {record_id!r}"
            )
        return self._view(record)

    def list_for_condo_key(self, condo_key: str) -> tuple[ConfirmationView, ...]:
        views = [
            self._view(record)
            for record in self._records.values()
            if record.condo_key == condo_key
        ]
        # Newest first: by confirmed_at (RFC 3339 sorts lexically) with the
        # insertion sequence as the deterministic secondary key, so a
        # same-instant pair lists the LATER-inserted record first — the
        # newest-first contract holds even on a timestamp tie.
        # [ORCH-CORRECTED per T059 G4-C-1: the prior comment claimed reverse
        # insertion order on ties, but a stable reverse sort preserves it.]
        views.sort(
            key=lambda view: (
                view.record.confirmed_at,
                self._insertion_seq.get(view.record.record_id, -1),
            ),
            reverse=True,
        )
        return tuple(views)

    def supersede(
        self, old_id: str, new_confirmation: SiteDefinitionConfirmation
    ) -> ConfirmationView:
        old = self._require_active(old_id)
        if new_confirmation.supersedes_id != old_id:
            raise ConfirmationNotFoundError(
                "the superseding confirmation must reference the record it "
                f"supersedes ({old_id!r}); it references "
                f"{new_confirmation.supersedes_id!r}"
            )
        if new_confirmation.reason is None:
            # create_confirmation guarantees this when supersedes_id is set; guard
            # anyway so a hand-built record can never skip the required reason.
            raise TransitionReasonRequiredError(
                "a superseding confirmation must carry the reason for the change"
            )
        if new_confirmation.condo_key != old.condo_key:
            raise ConfirmationNotFoundError(
                "a superseding confirmation must belong to the same condo key as "
                "the record it supersedes"
            )
        self._record_insert(new_confirmation)
        self._transitions.append(
            StatusTransition(
                record_id=old_id,
                from_status=ConfirmationStatus.ACTIVE,
                to_status=ConfirmationStatus.SUPERSEDED,
                at=new_confirmation.confirmed_at,
                reason=new_confirmation.reason,
                actor=new_confirmation.confirmer,
                superseded_by_id=new_confirmation.record_id,
            )
        )
        return self._view(new_confirmation)

    def revoke(
        self,
        record_id: str,
        *,
        condo_key: str,
        reason: str,
        actor: SiteConfirmer,
        at: str,
    ) -> ConfirmationView:
        if not isinstance(reason, str) or not reason.strip():
            raise TransitionReasonRequiredError(
                "a reason is required to revoke a site-definition confirmation"
            )
        record = self._require_active(record_id)
        # [ORCH-CORRECTED per T059 G3-C1/G5-F1] the revocation is BOUND to the
        # condo the caller addressed, mirroring supersede's binding: a record
        # belonging to a different condo is a typed not-found, never revoked.
        if record.condo_key != condo_key:
            raise ConfirmationNotFoundError(
                "the confirmation being revoked must belong to the same condo "
                "key as the property addressed by the request path"
            )
        self._transitions.append(
            StatusTransition(
                record_id=record_id,
                from_status=ConfirmationStatus.ACTIVE,
                to_status=ConfirmationStatus.REVOKED,
                at=at,
                reason=reason.strip(),
                actor=actor,
            )
        )
        return self._view(self._records[record_id])


# The SINGLE process-wide default store binding. Both API modules - the
# (unmounted) write API (:mod:`app.api.v1.site_definition`) and the read-only
# condo-records document (:mod:`app.api.v1.condo_records`) - bind to THIS one
# object, so a confirmation created through the write path is visible on the read
# document without a durable store: one store, one truth. Unifying the binding
# here (rather than each route owning its own :class:`InMemorySiteDefinitionStore`)
# is what makes write-then-read coherent; a per-route store would silently split
# the record set in two.
#
# It is still the B-001-deferred CI/local implementation (see the class docstring):
# ephemeral, single-process, not concurrency-safe. The write route stays UNMOUNTED
# until a durable store and authentication exist, so this shared default is never
# reachable in production. Tests override the per-route dependency with a fresh
# store for isolation.
_DEFAULT_STORE: SiteDefinitionStore = InMemorySiteDefinitionStore()


def default_site_definition_store() -> SiteDefinitionStore:
    """Return the one process-wide default site-definition store both API modules
    consume, so a written confirmation is visible on the read document through the
    same binding. B-001-deferred and ephemeral (see module docstring)."""
    return _DEFAULT_STORE
