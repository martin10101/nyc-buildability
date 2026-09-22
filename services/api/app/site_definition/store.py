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
    ListResultTooLargeError,
    OrphanSupersedeError,
    RecordIdCollisionError,
    SiteConfirmer,
    SiteDefinitionConfirmation,
    StatusTransition,
    SupersessionChainTooDeepError,
    TransitionReasonRequiredError,
)

__all__ = [
    "MAX_CONFIRMATIONS_PER_CONDO_KEY",
    "MAX_LIST_RESULTS",
    "InMemorySiteDefinitionStore",
    "SiteDefinitionStore",
    "default_site_definition_store",
]

# [DB-040(d) / T059 G5-F3] Bounds on a single condo_key's confirmation chain and
# on a list response, so the process-wide store cannot grow (or serialize) an
# unbounded set. The chain cap counts EVERY record recorded for a condo (active,
# superseded, revoked) and is enforced at the single insertion point
# (:meth:`_record_insert`), so it binds create AND supersede alike - the bound
# cannot be bypassed by revoking and re-creating, because revoke frees no slot in
# an append-only store. The list cap is defense-in-depth on the response and a
# ``list`` that would exceed it is a TYPED refusal (never a silent truncation).
#
# INVARIANT: MAX_CONFIRMATIONS_PER_CONDO_KEY <= MAX_LIST_RESULTS, so a single
# condo's list can never legitimately exceed the list cap; the list refusal is a
# durable-implementation backstop, not a path the in-memory store can trip.
MAX_CONFIRMATIONS_PER_CONDO_KEY = 200
MAX_LIST_RESULTS = 200

# [DB-040(r)/(s) — M5-T067/T069] The ONE byte-identical not-found-class refusal
# text shared by BOTH revoke and supersede. Every not-found-class refusal on either
# operation — a missing record id, an existing-but-foreign record, and (supersede
# only) a supersedes_id mismatch — raises ConfirmationNotFoundError with THIS exact
# text and NO id echo, so no refusal message discloses whether a probed id exists or
# which property it belongs to. Both operations reference this single constant so
# the branches cannot drift apart; the store- and route-level equality tests
# (test_*_not_found_*_identical_for_missing_and_foreign_ids) guard against any
# divergence or re-introduced id echo.
_NOT_FOUND_FOR_ADDRESSED_PROPERTY = (
    "no site-definition confirmation matching that record id exists "
    "for the property addressed by the request path"
)


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
        addressed_bbl: str,
        condo_key: str | None,
        reason: str,
        actor: SiteConfirmer,
        at: str,
    ) -> ConfirmationView:
        """Revoke the ACTIVE record ``record_id`` (reason required); append a
        terminal revoked transition. Returns the revoked record's view.

        [DB-040(a)/(b)] The revocation is SCOPED to the property the caller
        addressed, and the scope is evaluated BEFORE the ACTIVE-status check so a
        record belonging to another property is an indistinguishable ``404``
        whatever its status (a status-before-scope order leaks a cross-property
        status oracle — 409 for a non-active foreign record vs 404 for an active
        one). The scope is a DETERMINISTIC association that does NOT require a
        healthy live resolution:

        - ``condo_key`` is the resolved condo grouping when live resolution is
          HEALTHY; then it is authoritative and the stored record must belong to
          it (mirrors :meth:`supersede`'s binding).
        - ``condo_key`` is ``None`` only when the caller's resolver DEGRADED
          (unresolved / typed error / raised) and produced no condo id. This is
          NEVER permission to skip property scoping: implementations MUST fall
          back to the property identity the confirmation RECORDED at creation — the
          ``addressed_bbl`` (always available from the request path) must equal the
          record's own ``billing_bbl`` / ``entered_bbl``. A foreign-property probe
          then still fails to match (a different property carries a different BBL),
          while a legitimate withdrawal at the record's own property still
          succeeds. Refusing a withdrawal because the resolver is unhealthy is the
          WRONG fail-direction (D-051); revoke is the only human path to undo a
          confirmation and must stay available under a degraded resolver."""


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
        # [DB-040(d) / T059 G5-F3] Indexes replacing the O(n) full scans: record
        # ids per condo_key (insertion order) and transitions per record. Without
        # them _current_status/_superseded_by scan the whole transition log per
        # record, making list_for_condo_key O(n^2) on the process-wide store.
        self._by_condo_key: dict[str, list[str]] = {}
        self._transitions_by_record: dict[str, list[StatusTransition]] = {}

    # -- derivation (the append-only log is the source of truth for status) ---
    # [DB-040(d)] Each reads the per-record transition index, not the whole log.
    def _current_status(self, record_id: str) -> ConfirmationStatus:
        record_transitions = self._transitions_by_record.get(record_id)
        if not record_transitions:
            return ConfirmationStatus.ACTIVE
        return record_transitions[-1].to_status

    def _superseded_by(self, record_id: str) -> str | None:
        for transition in self._transitions_by_record.get(record_id, ()):
            if transition.to_status is ConfirmationStatus.SUPERSEDED:
                return transition.superseded_by_id
        return None

    def _transitions_for(self, record_id: str) -> tuple[StatusTransition, ...]:
        return tuple(self._transitions_by_record.get(record_id, ()))

    def _append_transition(self, transition: StatusTransition) -> None:
        """Append to both the flat log and the per-record index (kept in sync)."""
        self._transitions.append(transition)
        self._transitions_by_record.setdefault(transition.record_id, []).append(
            transition
        )

    def _view(self, record: SiteDefinitionConfirmation) -> ConfirmationView:
        return ConfirmationView(
            record=record,
            status=self._current_status(record.record_id),
            superseded_by_id=self._superseded_by(record.record_id),
            transitions=self._transitions_for(record.record_id),
        )

    def _records_for_condo_key(
        self, condo_key: str
    ) -> list[SiteDefinitionConfirmation]:
        # [DB-040(d)] index lookup, not a full-store scan.
        return [self._records[rid] for rid in self._by_condo_key.get(condo_key, ())]

    def _active_record_for(
        self, condo_key: str
    ) -> SiteDefinitionConfirmation | None:
        for record in self._records_for_condo_key(condo_key):
            if self._current_status(record.record_id) is ConfirmationStatus.ACTIVE:
                return record
        return None

    # -- operations ----------------------------------------------------------
    def _record_insert(self, confirmation: SiteDefinitionConfirmation) -> None:
        # The SINGLE insertion point for both create and supersede, so every
        # append-only guard lives here ONCE and neither path can bypass it. Both
        # guards raise BEFORE any mutation, so a refused insert leaves the records,
        # transitions, and indexes byte-unchanged.
        #
        # [DB-040(e) / T059 G5-F4] collision guard: an id already present would
        # otherwise silently overwrite a frozen, immutable original.
        if confirmation.record_id in self._records:
            raise RecordIdCollisionError(
                "a site-definition confirmation already exists for record id "
                f"{confirmation.record_id!r}; the store is append-only and never "
                "overwrites an immutable record"
            )
        # [DB-040(d) / T059 G5-F3] chain-depth cap counting EVERY record for the
        # condo. Enforced here (not only in supersede) so create cannot grow the
        # chain past the bound by revoke-then-recreate cycles: revoke frees no
        # slot in an append-only store, so the cap counts total records.
        if (
            len(self._by_condo_key.get(confirmation.condo_key, ()))
            >= MAX_CONFIRMATIONS_PER_CONDO_KEY
        ):
            raise SupersessionChainTooDeepError(
                "this condo has reached the maximum of "
                f"{MAX_CONFIRMATIONS_PER_CONDO_KEY} recorded site-definition "
                "confirmations; no further confirmation can be recorded for it "
                "(the store is append-only, so revoking does not free a slot)"
            )
        self._records[confirmation.record_id] = confirmation
        self._insertion_seq[confirmation.record_id] = self._next_seq
        self._next_seq += 1
        self._by_condo_key.setdefault(confirmation.condo_key, []).append(
            confirmation.record_id
        )

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
        # [DB-040(d)] index lookup, not a full-store scan.
        record_ids = self._by_condo_key.get(condo_key, ())
        # [DB-040(d)] defense-in-depth cap on the response size, as a TYPED REFUSAL
        # rather than a silent truncation: a truncated list would hide
        # legally-sensitive records with no signal that history was dropped. The
        # in-memory store cannot trip this (the chain cap is <= the list cap), so
        # it is a durable-implementation backstop at the store boundary.
        if len(record_ids) > MAX_LIST_RESULTS:
            raise ListResultTooLargeError(condo_key, len(record_ids), MAX_LIST_RESULTS)
        views = [self._view(self._records[rid]) for rid in record_ids]
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
        # [DB-040(a)/(q) — M5-T067] SCOPE before STATUS, mirroring :meth:`revoke`.
        # Look the record up DIRECTLY (never a status-first existence+ACTIVE
        # helper) so the property/condo scope binding is evaluated BEFORE the
        # ACTIVE-status check: a cross-property probe of a KNOWN foreign record is
        # then an indistinguishable 404 whatever the record's status, closing the
        # 409(non-active)-vs-404(active) status oracle the status-first order
        # leaked. The 409 conflict stays reachable only on the record's OWN binding.
        old = self._records.get(old_id)
        if old is None:
            # [DB-040(s) — M5-T069] SAME unified not-found text (no id echo) as the
            # foreign-scope branch below and revoke's two branches, so a missing id
            # is byte-indistinguishable from an existing one. KEEP IN SYNC via the
            # shared _NOT_FOUND_FOR_ADDRESSED_PROPERTY constant.
            raise ConfirmationNotFoundError(_NOT_FOUND_FOR_ADDRESSED_PROPERTY)
        if new_confirmation.supersedes_id != old_id:
            # [DB-040(s)] This mismatch branch fires ONLY when the record EXISTS
            # (old is not None above), so any divergent message here would itself be
            # an existence signal. It shares the identical unified text and echoes
            # neither id, so it discloses no existence for missing vs existing (AS-2).
            raise ConfirmationNotFoundError(_NOT_FOUND_FOR_ADDRESSED_PROPERTY)
        if new_confirmation.reason is None:
            # create_confirmation guarantees this when supersedes_id is set; guard
            # anyway so a hand-built record can never skip the required reason.
            raise TransitionReasonRequiredError(
                "a superseding confirmation must carry the reason for the change"
            )
        # SCOPE: the superseding confirmation's condo grouping (server-resolved
        # from the addressed property) must match the stored record's; a
        # foreign-property probe carries a different condo_key and is a 404 HERE,
        # before the status read below.
        if new_confirmation.condo_key != old.condo_key:
            # [DB-040(s) — M5-T069] SAME unified not-found text (no id echo) as the
            # missing-record branch above, so a foreign-property probe of a KNOWN
            # record is byte-identical to a missing id — the supersede existence
            # oracle the M5-T067 G5 review surfaced (LOW-1) is closed (AS-1).
            raise ConfirmationNotFoundError(_NOT_FOUND_FOR_ADDRESSED_PROPERTY)
        # STATUS: checked AFTER the scope check, so a non-active OWN record is the
        # 409 conflict while every foreign-property probe already 404'd above.
        if self._current_status(old_id) is not ConfirmationStatus.ACTIVE:
            raise ConfirmationNotActiveError(
                f"confirmation {old_id!r} is "
                f"{self._current_status(old_id).value!r}, not active; a "
                "superseded or revoked confirmation cannot be superseded or revoked"
            )
        # [DB-040(d)] the per-condo chain-depth cap is enforced in
        # :meth:`_record_insert` (the single insertion point), which raises BEFORE
        # any mutation - so an over-cap supersede appends neither the new record
        # nor the old record's superseded transition (state stays unchanged).
        self._record_insert(new_confirmation)
        self._append_transition(
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

    def _matches_addressed_property(
        self,
        record: SiteDefinitionConfirmation,
        *,
        addressed_bbl: str,
        condo_key: str | None,
    ) -> bool:
        """Deterministic association between the addressed property and a stored
        record, holding even when live resolution DEGRADES ([DB-040(a)/(b)]).

        - Healthy resolution (``condo_key`` present): the resolved condo grouping
          is authoritative; the record must belong to it (mirrors supersede).
        - Degraded resolution (``condo_key`` is ``None``): fall back to the
          property identity the confirmation RECORDED at creation - the
          ``addressed_bbl`` from the request path must equal the record's own
          ``billing_bbl`` / ``entered_bbl``. This needs NO live resolver, so a
          foreign-property probe (a different BBL) cannot match while a legitimate
          withdrawal at the record's own property still succeeds. ``condo_key`` of
          ``None`` is NEVER treated as permission to skip property scoping."""
        if condo_key is not None:
            return record.condo_key == condo_key
        return addressed_bbl in (record.billing_bbl, record.entered_bbl)

    def revoke(
        self,
        record_id: str,
        *,
        addressed_bbl: str,
        condo_key: str | None,
        reason: str,
        actor: SiteConfirmer,
        at: str,
    ) -> ConfirmationView:
        if not isinstance(reason, str) or not reason.strip():
            # Checked BEFORE the record lookup, so it discloses nothing about
            # whether a record id exists or which property it belongs to.
            raise TransitionReasonRequiredError(
                "a reason is required to revoke a site-definition confirmation"
            )
        # [DB-040(a)] SCOPE before STATUS. Look the record up directly so the
        # property scoping is evaluated first: a record of another property is an
        # indistinguishable not-found whatever its status, so no cross-property
        # status oracle (409-active vs 404-non-active) leaks.
        record = self._records.get(record_id)
        if record is None:
            # [DB-040(r) — M5-T067] IDENTICAL not-found text to the foreign-scope
            # branch below, and (M5-T069) to supersede's not-found branches — now
            # enforced structurally by the shared _NOT_FOUND_FOR_ADDRESSED_PROPERTY
            # constant. Given a known, unguessable record id, a missing id and a
            # foreign id must be indistinguishable, so the message must NOT disclose
            # existence. The equality tests test_revoke_not_found_message_* guard it.
            raise ConfirmationNotFoundError(_NOT_FOUND_FOR_ADDRESSED_PROPERTY)
        # [DB-040(a)/(b)] the revocation is SCOPED to the property the caller
        # addressed, by a deterministic association that survives a degraded
        # resolver (see :meth:`_matches_addressed_property`). A degraded resolver
        # never blocks the only human withdrawal path (D-051), and condo_key=None
        # is never permission to skip scoping.
        if not self._matches_addressed_property(
            record, addressed_bbl=addressed_bbl, condo_key=condo_key
        ):
            # [DB-040(r) — M5-T067] IDENTICAL not-found text to the missing-record
            # branch above (shared _NOT_FOUND_FOR_ADDRESSED_PROPERTY constant, see
            # that branch's note) so a foreign record cannot be distinguished from a
            # non-existent one by the message wording alone.
            raise ConfirmationNotFoundError(_NOT_FOUND_FOR_ADDRESSED_PROPERTY)
        # Status check AFTER the scope check, so a non-active OWN record is the 409
        # conflict while every foreign-property probe is already a 404 above.
        if self._current_status(record_id) is not ConfirmationStatus.ACTIVE:
            raise ConfirmationNotActiveError(
                f"confirmation {record_id!r} is "
                f"{self._current_status(record_id).value!r}, not active; a "
                "superseded or revoked confirmation cannot be superseded or revoked"
            )
        self._append_transition(
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
