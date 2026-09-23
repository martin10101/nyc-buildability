"""Site-definition confirmation RECORD + STORE acceptance pack (M5-T059, D-078).

Fully offline and deterministic (pure record/store logic; no FastAPI, no network,
no clock). Proves the typed, append-only substrate the D-078 confirmation flow
writes to:

- AS-1: a create with the resolver's EXACT base-lot set carries the confirmer, the
  self-attested attestation status, a tz-aware confirmed_at, the byte-copied
  resolution provenance, the FULL parcel set (never a single chosen lot), and is
  refused-for-calculation.
- AS-2: a subset / superset / divergent parcel set is a typed ParcelSetMismatch;
  order alone never refuses (sorted-tuple normalization).
- AS-3: append-only lifecycle — one active per condo_key (duplicate = typed
  refusal), supersede requires a reason and chains a NEW active while the frozen
  original is untouched (status derived from the appended transition), revoke is
  terminal and requires a reason, and a non-active record cannot be superseded or
  revoked.
- AS-4: a self-attested confirmation is refused for calculation, and the block
  assembly only ever SURFACES a recorded human confirmation — it never selects a
  site (status is CONFIRMED only when a human record is active; a later differing
  resolver set is a surfaced discrepancy, never a status change).

Realistic FRACTIONAL-SECOND timestamps are used throughout so the record proves it
carries a real ``datetime.now(UTC)``-class instant, not a fixture trimmed to dodge
a display gate.
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from app.site_definition import (
    MAX_CONFIRMATIONS_PER_CONDO_KEY,
    MAX_CONFIRMER_NAME_CHARS,
    MAX_LIST_RESULTS,
    MAX_NOTE_CHARS,
    SITE_DEFINITION_STATUS_CONFIRMED,
    SITE_DEFINITION_STATUS_UNCONFIRMED,
    AttestationStatus,
    ConfirmationNotActiveError,
    ConfirmationNotFoundError,
    ConfirmationStatus,
    ConfirmationView,
    DuplicateActiveConfirmationError,
    FieldTooLongError,
    InMemorySiteDefinitionStore,
    InvalidConfirmerError,
    ListResultTooLargeError,
    OrphanSupersedeError,
    ParcelSetMismatchError,
    ParcelShapeError,
    RecordIdCollisionError,
    ResolutionProvenanceSnapshot,
    SiteConfirmer,
    SiteDefinitionConfirmation,
    SiteDefinitionError,
    StatusTransition,
    SupersessionChainTooDeepError,
    TransitionReasonRequiredError,
    build_site_definition_block,
    confirmed_at_display,
    create_confirmation,
    make_confirmer,
    normalize_parcels,
)

CONDO_KEY = "103344"
BILLING_BBL = "1003037502"
PARCELS = ("1003030019", "1003030025")
# A realistic tz-aware instant WITH fractional seconds (what datetime.now(UTC)
# produces) - never a fixture trimmed to whole seconds to dodge a display gate.
CONFIRMED_AT = datetime(2026, 9, 20, 8, 23, 30, 89123, tzinfo=UTC)
LATER_AT = CONFIRMED_AT + timedelta(minutes=7, microseconds=451)


def _provenance() -> ResolutionProvenanceSnapshot:
    return ResolutionProvenanceSnapshot(
        source_id="nyc-dof-dtm-condo-soda",
        dataset_ids=("p8u6-a6it",),
        retrieved_at="2026-09-01T14:05:56.732000Z",
        resolution_path="billing",
    )


def _make(**overrides: object) -> SiteDefinitionConfirmation:
    params: dict[str, object] = {
        "condo_key": CONDO_KEY,
        "billing_bbl": BILLING_BBL,
        "entered_bbl": BILLING_BBL,
        "proposed_parcels": list(PARCELS),
        "resolver_base_bbls": list(PARCELS),
        "confirmer_name": "Dana Reviewer",
        "confirmer_role": "qualified_professional",
        "confirmed_at": CONFIRMED_AT,
        "provenance": _provenance(),
    }
    params.update(overrides)
    return create_confirmation(**params)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AS-1: a valid create carries the full provenance-bearing record
# ---------------------------------------------------------------------------
def test_create_carries_confirmer_attestation_and_provenance():
    record = _make()
    assert record.condo_key == CONDO_KEY
    assert record.confirmer.name == "Dana Reviewer"
    assert record.confirmer.role.value == "qualified_professional"
    # Attestation is server-set and self-attested (auth B-001-blocked), and a
    # self-attested confirmation is refused for any calculation use.
    assert record.attestation_status is AttestationStatus.UNAUTHENTICATED_SELF_ATTESTED
    assert record.refused_for_calculation is True
    # The FULL base-lot set is recorded - never a single chosen substrate lot.
    assert record.parcels == PARCELS
    # The resolution provenance is byte-copied from the snapshot.
    assert record.provenance == _provenance()
    # confirmed_at is a tz-aware RFC 3339 instant that PRESERVES fractional seconds.
    assert record.confirmed_at == "2026-09-20T08:23:30.089123+00:00"
    assert record.confirmed_at.endswith("+00:00")
    assert "." in record.confirmed_at.split("+", 1)[0]
    payload = record.to_payload()
    assert payload["attestation_status"] == "unauthenticated_self_attested"
    assert payload["refused_for_calculation"] is True
    assert payload["parcels"] == list(PARCELS)
    assert payload["confirmed_at"] == "2026-09-20T08:23:30.089123+00:00"


def test_attestation_is_server_set_not_taken_from_a_payload():
    # There is no create parameter to raise the attestation; it is always the
    # self-attested member. (An untrusted body cannot claim authentication.)
    record = _make()
    assert record.attestation_status is AttestationStatus.UNAUTHENTICATED_SELF_ATTESTED
    # And the closed vocabulary has exactly one member in slice 1.
    assert [m.value for m in AttestationStatus] == ["unauthenticated_self_attested"]


def test_naive_confirmed_at_is_refused():
    with pytest.raises(SiteDefinitionError):
        _make(confirmed_at=datetime(2026, 9, 20, 8, 23, 30))  # naive on purpose


def test_blank_name_and_bad_role_are_typed_confirmer_refusals():
    with pytest.raises(InvalidConfirmerError):
        _make(confirmer_name="   ")
    with pytest.raises(InvalidConfirmerError):
        _make(confirmer_role="ai_agent")
    with pytest.raises(InvalidConfirmerError):
        make_confirmer("", "user")


# ---------------------------------------------------------------------------
# AS-2: strict parcel binding (order never refuses, a divergent set always does)
# ---------------------------------------------------------------------------
def test_reordered_but_equal_parcel_set_is_accepted():
    record = _make(proposed_parcels=[PARCELS[1], PARCELS[0]])
    assert record.parcels == PARCELS  # normalized to a sorted tuple


def test_subset_superset_and_divergent_parcel_sets_refuse():
    with pytest.raises(ParcelSetMismatchError):
        _make(proposed_parcels=[PARCELS[0]])  # subset
    with pytest.raises(ParcelSetMismatchError):
        _make(proposed_parcels=[*PARCELS, "1003030099"])  # superset
    with pytest.raises(ParcelSetMismatchError):
        _make(proposed_parcels=["1003030019", "1003030088"])  # divergent


def test_parcel_mismatch_names_the_exact_missing_and_extra_lots():
    with pytest.raises(ParcelSetMismatchError) as exc:
        _make(proposed_parcels=["1003030019", "1003030088"])
    assert exc.value.submitted == ("1003030019", "1003030088")
    assert exc.value.expected == PARCELS


def test_normalize_parcels_rejects_malformed_sets_with_a_parcel_shape_error():
    # [DB-040(i) / T059 G3-F-2/A-6] a malformed parcel value is its OWN
    # ParcelShapeError (reject_code parcel_set_shape), NEVER mislabelled as an
    # InvalidConfirmerError - a parcel defect must not name the confirmer.
    with pytest.raises(ParcelShapeError):
        normalize_parcels("1003030019")  # not a list/tuple
    with pytest.raises(ParcelShapeError):
        normalize_parcels([""])  # blank entry
    with pytest.raises(ParcelShapeError):
        normalize_parcels([])  # empty
    # A parcel-shape defect is NOT a confirmer defect (distinct classes).
    assert not issubclass(ParcelShapeError, InvalidConfirmerError)
    assert ParcelShapeError.reject_code == "parcel_set_shape"
    assert normalize_parcels(["b", "a", "a"]) == ("a", "b")  # sorted + de-duped


# ---------------------------------------------------------------------------
# AS-3: append-only lifecycle in the store
# ---------------------------------------------------------------------------
def test_created_record_is_active_and_listed():
    store = InMemorySiteDefinitionStore()
    view = store.create(_make())
    assert view.status is ConfirmationStatus.ACTIVE
    listed = store.list_for_condo_key(CONDO_KEY)
    assert [v.record.record_id for v in listed] == [view.record.record_id]


def test_duplicate_active_create_is_a_typed_refusal():
    store = InMemorySiteDefinitionStore()
    store.create(_make())
    with pytest.raises(DuplicateActiveConfirmationError):
        store.create(_make())


def test_supersede_requires_a_reason_at_construction():
    # create_confirmation enforces the reason the instant supersedes_id is set.
    with pytest.raises(TransitionReasonRequiredError):
        _make(supersedes_id="prior-id")


def test_supersede_chains_a_new_active_and_leaves_the_frozen_original_untouched():
    store = InMemorySiteDefinitionStore()
    original = store.create(_make()).record
    superseding = _make(
        confirmed_at=LATER_AT,
        supersedes_id=original.record_id,
        reason="corrected the recorded confirmer",
    )
    new_view = store.supersede(original.record_id, superseding)
    assert new_view.status is ConfirmationStatus.ACTIVE
    assert new_view.record.supersedes_id == original.record_id
    # The old record's status is DERIVED to superseded via an appended transition;
    # the frozen original object is byte-unchanged (no in-place edit).
    old_view = store.get(original.record_id)
    assert old_view.status is ConfirmationStatus.SUPERSEDED
    assert old_view.superseded_by_id == superseding.record_id
    assert old_view.record is original  # same immutable object, never rewritten
    assert old_view.record.supersedes_id is None
    # Exactly one active remains, and the full chain is listable newest-first.
    chain = store.list_for_condo_key(CONDO_KEY)
    assert [v.record.record_id for v in chain] == [
        superseding.record_id,
        original.record_id,
    ]
    assert sum(1 for v in chain if v.status is ConfirmationStatus.ACTIVE) == 1


def test_the_record_is_immutable_a_mutation_attempt_raises():
    record = _make()
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.parcels = ("9999999999",)  # type: ignore[misc]


def test_revoke_requires_a_reason_and_is_terminal():
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "qualified_professional")
    with pytest.raises(TransitionReasonRequiredError):
        store.revoke(
            record.record_id,
            addressed_bbl=BILLING_BBL,
            condo_key=CONDO_KEY,
            reason="  ",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    view = store.revoke(
        record.record_id,
        addressed_bbl=BILLING_BBL,
        condo_key=CONDO_KEY,
        reason="parcels no longer treated as one site",
        actor=actor,
        at=LATER_AT.isoformat(),
    )
    assert view.status is ConfirmationStatus.REVOKED
    # Terminal: a revoked record cannot be revoked or superseded again.
    with pytest.raises(ConfirmationNotActiveError):
        store.revoke(
            record.record_id,
            addressed_bbl=BILLING_BBL,
            condo_key=CONDO_KEY,
            reason="again",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    with pytest.raises(ConfirmationNotActiveError):
        store.supersede(
            record.record_id,
            _make(
                confirmed_at=LATER_AT,
                supersedes_id=record.record_id,
                reason="cannot supersede a revoked record",
            ),
        )


def test_after_revoke_a_fresh_create_is_allowed_again():
    store = InMemorySiteDefinitionStore()
    first = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "user")
    store.revoke(
        first.record_id,
        addressed_bbl=BILLING_BBL,
        condo_key=CONDO_KEY,
        reason="start over",
        actor=actor,
        at=LATER_AT.isoformat(),
    )
    # No active record now, so a new create is not a duplicate.
    second = store.create(_make(confirmed_at=LATER_AT)).record
    assert second.record_id != first.record_id
    chain = store.list_for_condo_key(CONDO_KEY)
    assert len(chain) == 2


def test_supersede_or_revoke_of_an_unknown_record_is_not_found():
    store = InMemorySiteDefinitionStore()
    actor = make_confirmer("Dana Reviewer", "user")
    with pytest.raises(ConfirmationNotFoundError):
        store.revoke(
            "nope",
            addressed_bbl=BILLING_BBL,
            condo_key=CONDO_KEY,
            reason="x",
            actor=actor,
            at=LATER_AT.isoformat(),
        )


# ---------------------------------------------------------------------------
# AS-4: the block only SURFACES a human confirmation - never selects a site
# ---------------------------------------------------------------------------
def test_block_is_unconfirmed_with_no_active_record():
    block = build_site_definition_block(condo_key=CONDO_KEY, views=())
    assert block["status"] == SITE_DEFINITION_STATUS_UNCONFIRMED
    assert block["active_confirmation"] is None
    assert block["confirmations"] == []
    assert block["parcel_discrepancy"] is None


def test_block_is_confirmed_only_when_a_human_record_is_active():
    store = InMemorySiteDefinitionStore()
    store.create(_make())
    views = store.list_for_condo_key(CONDO_KEY)
    block = build_site_definition_block(condo_key=CONDO_KEY, views=views)
    assert block["status"] == SITE_DEFINITION_STATUS_CONFIRMED
    active = block["active_confirmation"]
    assert active["status"] == "active"
    assert active["refused_for_calculation"] is True
    # Never a single selected substrate: the recorded set is the FULL parcel list.
    assert active["parcels"] == list(PARCELS)


def test_block_with_only_revoked_history_is_unconfirmed_but_lists_the_chain():
    # This is exactly the web "unconfirmed WITH history" case: a record existed and
    # was revoked, so the block is unconfirmed yet confirmationCount > 0.
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "user")
    store.revoke(
        record.record_id,
        addressed_bbl=BILLING_BBL,
        condo_key=CONDO_KEY,
        reason="withdrawn",
        actor=actor,
        at=LATER_AT.isoformat(),
    )
    views = store.list_for_condo_key(CONDO_KEY)
    block = build_site_definition_block(condo_key=CONDO_KEY, views=views)
    assert block["status"] == SITE_DEFINITION_STATUS_UNCONFIRMED
    assert block["active_confirmation"] is None
    assert len(block["confirmations"]) == 1  # the revoked record is still recorded


def test_a_later_differing_resolver_set_is_a_surfaced_discrepancy_not_a_status_change():
    store = InMemorySiteDefinitionStore()
    store.create(_make())
    views = store.list_for_condo_key(CONDO_KEY)
    block = build_site_definition_block(
        condo_key=CONDO_KEY,
        views=views,
        resolver_base_bbls=("1003030019", "1003030099"),  # differs from recorded
    )
    # The confirmation's status is UNCHANGED (only a human act moves it); the
    # difference is SURFACED as a factual discrepancy for professional review.
    assert block["status"] == SITE_DEFINITION_STATUS_CONFIRMED
    assert block["parcel_discrepancy"]["recorded_parcels"] == list(PARCELS)
    assert block["parcel_discrepancy"]["current_resolver_parcels"] == [
        "1003030019",
        "1003030099",
    ]


# ---------------------------------------------------------------------------
# [ORCH-CORRECTED per T059 G3-C1, G4-C-1, G4-C-2] rework bindings (seq 122)
# ---------------------------------------------------------------------------
def test_revoke_is_bound_to_the_condo_key_of_the_addressed_property():
    # G3-C1/G5-F1: a revoke addressed at a DIFFERENT condo is a typed not-found
    # and the record stays ACTIVE - mirroring supersede's binding.
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "qualified_professional")
    with pytest.raises(ConfirmationNotFoundError):
        store.revoke(
            record.record_id,
            addressed_bbl=BILLING_BBL,
            condo_key="some-other-condo",
            reason="cross-condo attempt",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    assert store.get(record.record_id).status is ConfirmationStatus.ACTIVE


def test_same_instant_pair_lists_newest_first():
    # G4-C-1: on a confirmed_at TIE the later-inserted (newer) record lists
    # first - the ABC's newest-first contract, now deterministic by the
    # insertion-sequence secondary key.
    store = InMemorySiteDefinitionStore()
    first = store.create(_make()).record
    superseding = _make(
        supersedes_id=first.record_id,
        reason="tie-break probe: replace at the same instant",
    )
    # Same confirmed_at as the record it supersedes (a coarse-clock durable
    # store can produce this legally).
    assert superseding.confirmed_at == first.confirmed_at
    second = store.supersede(first.record_id, superseding).record
    chain = store.list_for_condo_key(CONDO_KEY)
    assert [view.record.record_id for view in chain] == [
        second.record_id,
        first.record_id,
    ]
    assert chain[0].status is ConfirmationStatus.ACTIVE


def test_create_refuses_a_supersedes_id_carrying_record():
    # G4-C-2: create() is not a supersession path - an orphan supersedes_id
    # would mint an ACTIVE record whose chain reference the transition log
    # never flipped.
    store = InMemorySiteDefinitionStore()
    orphan = _make(
        supersedes_id="some-other-record",
        reason="orphan probe",
    )
    with pytest.raises(OrphanSupersedeError):
        store.create(orphan)


# ---------------------------------------------------------------------------
# M5-T062 — DB-040 mount-precondition hardening (store + record layer)
# ---------------------------------------------------------------------------
# AS-1 (no oracle): scope is evaluated BEFORE status, so every cross-property
# probe reads 404 whatever the record's status; the 409-class response is
# reachable only on the record's OWN binding.
def test_revoke_binds_scope_before_status_so_a_foreign_non_active_record_is_404():
    # [DB-040(a) / T059 G3-delta F-9 + G5-delta INFO] a status-before-scope order
    # would leak "this record exists and is non-active" (409) for a foreign
    # property vs 404 for an active one - a cross-property status oracle. Binding
    # scope first makes every foreign probe an indistinguishable 404.
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "user")
    # Withdraw at the OWN property so the record becomes NON-ACTIVE.
    store.revoke(
        record.record_id,
        addressed_bbl=BILLING_BBL,
        condo_key=CONDO_KEY,
        reason="withdraw at the addressed property",
        actor=actor,
        at=LATER_AT.isoformat(),
    )
    # FOREIGN-condo probe of the now-revoked record -> 404-class NotFound
    # (scope-before-status), NOT the 409-class NotActive.
    with pytest.raises(ConfirmationNotFoundError):
        store.revoke(
            record.record_id,
            addressed_bbl="9999999999",
            condo_key="some-other-condo",
            reason="cross-property probe of a non-active record",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    # OWN-property probe of the SAME non-active record IS the 409-class NotActive,
    # so the 409 is reachable only on the record's own binding.
    with pytest.raises(ConfirmationNotActiveError):
        store.revoke(
            record.record_id,
            addressed_bbl=BILLING_BBL,
            condo_key=CONDO_KEY,
            reason="own probe of a non-active record",
            actor=actor,
            at=LATER_AT.isoformat(),
        )


# AS-2 (degraded-safe revoke): condo_key=None models a degraded resolver; it is
# NEVER "skip scoping" - it falls back to the record's own addressed BBL.
def test_revoke_survives_a_degraded_resolver_via_the_addressed_bbl_fallback():
    # [DB-040(b) / D-051] refusing withdrawal because the resolver is unhealthy is
    # the WRONG fail-direction; the only human undo path must stay available.
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "user")
    view = store.revoke(
        record.record_id,
        addressed_bbl=BILLING_BBL,
        condo_key=None,
        reason="withdraw under a degraded resolver",
        actor=actor,
        at=LATER_AT.isoformat(),
    )
    assert view.status is ConfirmationStatus.REVOKED


def test_degraded_revoke_still_rejects_a_foreign_property_probe():
    # Degraded (condo_key=None) is not unscoped: a foreign addressed BBL cannot
    # match the record's own BBL -> 404, and the record stays ACTIVE.
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    actor = make_confirmer("Mallory", "user")
    with pytest.raises(ConfirmationNotFoundError):
        store.revoke(
            record.record_id,
            addressed_bbl="9999999999",
            condo_key=None,
            reason="foreign probe under a degraded resolver",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    assert store.get(record.record_id).status is ConfirmationStatus.ACTIVE


def test_degraded_revoke_matches_either_the_billing_or_the_entered_bbl():
    # [DB-040(n) / T059 G4-A-3] entered != billing: the degraded fallback binds the
    # request-path BBL against EITHER recorded property identity and refuses one
    # matching NEITHER - so a unit-entry path (entered != billing) can still
    # withdraw its own confirmation, without a foreign probe ever matching.
    actor = make_confirmer("Dana Reviewer", "user")
    # addressed == billing_bbl binds.
    s1 = InMemorySiteDefinitionStore()
    r1 = s1.create(_make(billing_bbl="1000010001", entered_bbl="2000020002")).record
    assert (
        s1.revoke(
            r1.record_id,
            addressed_bbl="1000010001",
            condo_key=None,
            reason="via billing",
            actor=actor,
            at=LATER_AT.isoformat(),
        ).status
        is ConfirmationStatus.REVOKED
    )
    # addressed == entered_bbl (NOT billing) still binds.
    s2 = InMemorySiteDefinitionStore()
    r2 = s2.create(_make(billing_bbl="1000010001", entered_bbl="2000020002")).record
    assert (
        s2.revoke(
            r2.record_id,
            addressed_bbl="2000020002",
            condo_key=None,
            reason="via entered",
            actor=actor,
            at=LATER_AT.isoformat(),
        ).status
        is ConfirmationStatus.REVOKED
    )
    # addressed matching NEITHER is refused.
    s3 = InMemorySiteDefinitionStore()
    r3 = s3.create(_make(billing_bbl="1000010001", entered_bbl="2000020002")).record
    with pytest.raises(ConfirmationNotFoundError):
        s3.revoke(
            r3.record_id,
            addressed_bbl="3000030003",
            condo_key=None,
            reason="matches neither recorded bbl",
            actor=actor,
            at=LATER_AT.isoformat(),
        )


# AS-3 (caps / guards): each refuses TYPED without touching store state.
def test_over_length_note_is_a_typed_field_too_long_refusal():
    # [DB-040(c) / T059 G5-F2] a note past the cap is a typed refusal (never a
    # silent truncation of a legally-sensitive record); AT the cap is accepted.
    with pytest.raises(FieldTooLongError) as exc:
        _make(note="N" * (MAX_NOTE_CHARS + 1))
    assert exc.value.field == "note"
    assert exc.value.limit == MAX_NOTE_CHARS
    assert _make(note="N" * MAX_NOTE_CHARS).note is not None


def test_over_length_confirmer_name_is_a_typed_confirmer_refusal():
    # [DB-040(c)] a confirmer name past the cap is a confirmer refusal (distinct
    # from a parcel/field defect); AT the cap is accepted.
    with pytest.raises(InvalidConfirmerError):
        _make(confirmer_name="Q" * (MAX_CONFIRMER_NAME_CHARS + 1))
    assert _make(confirmer_name="Q" * MAX_CONFIRMER_NAME_CHARS).confirmer.name


def test_chain_cap_is_within_the_list_cap_invariant():
    # The in-memory store can never legitimately trip the list cap: a single
    # condo's chain is capped at or below the list cap, so the list refusal is a
    # durable-implementation backstop, not a path the in-memory store can reach.
    assert MAX_CONFIRMATIONS_PER_CONDO_KEY <= MAX_LIST_RESULTS


def test_chain_depth_cap_refuses_typed_without_touching_store_state(monkeypatch):
    # [DB-040(d) / T059 G5-F3] the cap counts EVERY recorded record and refuses at
    # the single insertion point BEFORE any mutation, so an over-cap supersede
    # leaves records/transitions unchanged. Exercised at a small cap.
    monkeypatch.setattr(
        "app.site_definition.store.MAX_CONFIRMATIONS_PER_CONDO_KEY", 2
    )
    store = InMemorySiteDefinitionStore()
    first = store.create(_make()).record
    second = store.supersede(
        first.record_id,
        _make(confirmed_at=LATER_AT, supersedes_id=first.record_id, reason="one"),
    ).record
    before = store.list_for_condo_key(CONDO_KEY)  # 2 records: at the cap
    with pytest.raises(SupersessionChainTooDeepError):
        store.supersede(
            second.record_id,
            _make(
                confirmed_at=LATER_AT, supersedes_id=second.record_id, reason="two"
            ),
        )
    after = store.list_for_condo_key(CONDO_KEY)
    assert [v.record.record_id for v in after] == [
        v.record.record_id for v in before
    ]
    assert store.get(second.record_id).status is ConfirmationStatus.ACTIVE


def test_over_cap_list_is_a_typed_refusal_never_a_silent_truncation(monkeypatch):
    # [DB-040(d) / T059 G5-F3] the durable-store backstop: rather than silently
    # truncating a legally-sensitive record set, an over-cap list refuses typed.
    store = InMemorySiteDefinitionStore()
    first = store.create(_make()).record
    store.supersede(
        first.record_id,
        _make(confirmed_at=LATER_AT, supersedes_id=first.record_id, reason="one"),
    )
    monkeypatch.setattr("app.site_definition.store.MAX_LIST_RESULTS", 1)
    with pytest.raises(ListResultTooLargeError) as exc:
        store.list_for_condo_key(CONDO_KEY)
    assert exc.value.actual == 2
    assert exc.value.limit == 1


def test_record_id_collision_is_a_typed_refusal_without_overwriting():
    # [DB-040(e) / T059 G5-F4] the append-only store never overwrites a frozen
    # original: a second record reusing an existing id is a typed refusal. Reached
    # via two DIFFERENT condos so the duplicate-active guard does not fire first.
    store = InMemorySiteDefinitionStore()
    store.create(_make(record_id="dup", condo_key="condo-x"))
    with pytest.raises(RecordIdCollisionError):
        store.create(_make(record_id="dup", condo_key="condo-y"))
    # The original is intact and no condo-y record was recorded.
    assert store.get("dup").record.condo_key == "condo-x"
    assert store.list_for_condo_key("condo-y") == ()


def test_list_for_condo_key_isolates_by_condo_key():
    # [T059 A-7] a record under one condo neither appears under another nor blocks
    # the other's create; the keyed lookup path is proven by the isolation (a
    # full-store scan would leak across condos).
    store = InMemorySiteDefinitionStore()
    a = store.create(_make(condo_key="condo-a")).record
    b = store.create(_make(condo_key="condo-b")).record
    assert [v.record.record_id for v in store.list_for_condo_key("condo-a")] == [
        a.record_id
    ]
    assert [v.record.record_id for v in store.list_for_condo_key("condo-b")] == [
        b.record_id
    ]
    assert store.list_for_condo_key("condo-c") == ()


# AS-4 (typed shape refusals + frozen-ness + display): the value types are
# immutable and the fractional-second display form is decimal-free.
def test_value_types_are_frozen_dataclasses():
    # [T059 A-7] every value type is an immutable frozen dataclass; a mutation
    # attempt raises, so no recorded confirmation, transition, view, confirmer, or
    # provenance snapshot can be edited in place.
    store = InMemorySiteDefinitionStore()
    view = store.create(_make())
    assert isinstance(view, ConfirmationView)
    confirmer = view.record.confirmer
    assert isinstance(confirmer, SiteConfirmer)
    provenance = view.record.provenance
    transition = StatusTransition(
        record_id=view.record.record_id,
        from_status=ConfirmationStatus.ACTIVE,
        to_status=ConfirmationStatus.REVOKED,
        at=LATER_AT.isoformat(),
        reason="probe",
        actor=confirmer,
    )
    for frozen_obj, attr, value in (
        (view, "status", ConfirmationStatus.REVOKED),
        (view.record, "note", "x"),
        (transition, "reason", "y"),
        (confirmer, "name", "z"),
        (provenance, "source_id", "w"),
    ):
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(frozen_obj, attr, value)


def test_confirmed_at_display_drops_fractional_seconds_while_the_record_keeps_them():
    # [DB-040(l) / T059 G3-F-6] the record keeps the full-precision instant; the
    # display form drops the fractional part so it can render inside the
    # decimal-gated records section. A non-parseable value returns unchanged.
    record = _make()
    assert record.confirmed_at == "2026-09-20T08:23:30.089123+00:00"
    display = confirmed_at_display(record.confirmed_at)
    assert display == "2026-09-20T08:23:30+00:00"
    assert "." not in display
    assert record.to_payload()["confirmed_at_display"] == display
    assert confirmed_at_display("not-a-timestamp") == "not-a-timestamp"


# ---------------------------------------------------------------------------
# M5-T067 — DB-040(q)/(r) store hardening residuals (M5-T062 G5 LOW-1/LOW-2)
# ---------------------------------------------------------------------------
# (q) supersede now binds SCOPE before STATUS, exactly mirroring revoke, so a
# cross-property probe of a KNOWN foreign record reads an indistinguishable 404
# whatever the record's status; the 409-class NotActive is reachable only on the
# record's OWN binding. (r) revoke's two not-found branches emit byte-identical
# message text, so the message cannot distinguish a missing id from a foreign one.
def _foreign_supersede_probe(old_id: str) -> SiteDefinitionConfirmation:
    # A superseding confirmation whose condo_key is FOREIGN to the probed record.
    # The route resolves condo_key server-side from the ADDRESSED property, so a
    # cross-property probe necessarily carries a different condo_key.
    return _make(
        condo_key="some-other-condo",
        supersedes_id=old_id,
        reason="cross-property supersede probe",
    )


# AS-1 (supersede oracle closed) + AS-2 (mutation sensitivity q): reverting the
# reorder (status check first) reddens the superseded/revoked cases below, which
# would then raise the 409-class ConfirmationNotActiveError instead of the
# 404-class ConfirmationNotFoundError.
@pytest.mark.parametrize("status_label", ["active", "superseded", "revoked"])
def test_supersede_foreign_probe_is_404_whatever_the_record_status(status_label):
    store = InMemorySiteDefinitionStore()
    original = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "user")
    if status_label == "superseded":
        store.supersede(
            original.record_id,
            _make(
                confirmed_at=LATER_AT,
                supersedes_id=original.record_id,
                reason="own supersede at the addressed property",
            ),
        )
    elif status_label == "revoked":
        store.revoke(
            original.record_id,
            addressed_bbl=BILLING_BBL,
            condo_key=CONDO_KEY,
            reason="own revoke at the addressed property",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    before = [v.record.record_id for v in store.list_for_condo_key(CONDO_KEY)]
    # FOREIGN-condo supersede probe -> 404-class NotFound (scope-before-status),
    # NEVER the 409-class NotActive, for every one of the three statuses.
    with pytest.raises(ConfirmationNotFoundError):
        store.supersede(
            original.record_id, _foreign_supersede_probe(original.record_id)
        )
    # The refused probe mutated NOTHING: neither the addressed condo's chain nor
    # the foreign condo gained a record (the scope check raises before any insert).
    after = [v.record.record_id for v in store.list_for_condo_key(CONDO_KEY)]
    assert after == before
    assert store.list_for_condo_key("some-other-condo") == ()


def test_supersede_of_a_non_active_own_record_is_still_the_409_conflict():
    # AS-1: the 409 NotActive stays reachable ONLY on the record's OWN binding - a
    # SAME-condo supersede of a non-active record passes the scope check, so the
    # status check fires and it is the typed conflict (never a 404).
    store = InMemorySiteDefinitionStore()
    original = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "user")
    store.revoke(
        original.record_id,
        addressed_bbl=BILLING_BBL,
        condo_key=CONDO_KEY,
        reason="own revoke",
        actor=actor,
        at=LATER_AT.isoformat(),
    )
    with pytest.raises(ConfirmationNotActiveError):
        store.supersede(
            original.record_id,
            _make(
                supersedes_id=original.record_id,
                reason="own supersede of a revoked record",
            ),
        )


# AS-3 (message unification) + AS-4 (mutation sensitivity r): revoke's
# non-existent-id and existing-but-foreign-id branches return byte-identical
# message text AND reject_code. Diverging either literal reddens the equality
# assertion below.
def test_revoke_not_found_message_is_identical_for_missing_and_foreign_ids():
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    actor = make_confirmer("Dana Reviewer", "user")
    # Branch 1: a NON-EXISTENT record id at the OWN condo (healthy scope).
    with pytest.raises(ConfirmationNotFoundError) as missing:
        store.revoke(
            "does-not-exist",
            addressed_bbl=BILLING_BBL,
            condo_key=CONDO_KEY,
            reason="probe a non-existent id",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    # Branch 2: an EXISTING but FOREIGN record id (foreign condo scope).
    with pytest.raises(ConfirmationNotFoundError) as foreign:
        store.revoke(
            record.record_id,
            addressed_bbl="9999999999",
            condo_key="some-other-condo",
            reason="probe a foreign id",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    # Byte-identical message text AND reject_code -> no existence oracle via text.
    assert str(missing.value) == str(foreign.value)
    assert missing.value.reject_code == foreign.value.reject_code
    # And the unified text echoes NEITHER probed id (it discloses no existence).
    assert "does-not-exist" not in str(missing.value)
    assert record.record_id not in str(foreign.value)
    # [M5-T072 / T069 G3-A2] cross-op pin: revoke text == the shared unified constant.
    assert str(missing.value) == _UNIFIED_NOT_FOUND_TEXT


# ---------------------------------------------------------------------------
# M5-T069 — DB-040(s) supersede not-found message unification (M5-T067 G5 LOW-1)
# ---------------------------------------------------------------------------
# The last known store existence oracle: supersede's not-found branches emitted
# DIVERGENT text (the missing-record branch echoed old_id; the foreign-scope branch
# and the supersedes_id-mismatch branch used distinct static text that fired only
# when the record existed). All not-found-class supersede refusals now raise the
# SAME byte-identical text as revoke — one shared constant, NO id echo — so no
# supersede refusal distinguishes a missing id from an existing one. Mirrors the
# accepted revoke pair (test_revoke_not_found_message_is_identical_for_missing_and_foreign_ids).
_UNIFIED_NOT_FOUND_TEXT = (
    "no site-definition confirmation matching that record id exists "
    "for the property addressed by the request path"
)


# AS-1 (supersede oracle closed) + AS-3 (mutation sensitivity): a missing old_id
# and an existing-but-foreign record return byte-identical class, reject_code AND
# message, echoing neither id. Diverging any unified literal, or re-introducing an
# id echo, reddens an assertion below.
def test_supersede_not_found_message_is_identical_for_missing_and_foreign_ids():
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    # Branch 1: a NON-EXISTENT old_id (the superseding record references it, so it
    # passes the supersedes_id check and the missing-record branch fires first).
    with pytest.raises(ConfirmationNotFoundError) as missing:
        store.supersede(
            "does-not-exist",
            _make(supersedes_id="does-not-exist", reason="probe a non-existent id"),
        )
    # Branch 2: an EXISTING but FOREIGN record (foreign condo scope); supersedes_id
    # matches old_id, so it passes the mismatch check and reaches the scope branch.
    with pytest.raises(ConfirmationNotFoundError) as foreign:
        store.supersede(record.record_id, _foreign_supersede_probe(record.record_id))
    # Byte-identical message AND reject_code -> no existence oracle via text.
    assert str(missing.value) == str(foreign.value)
    assert missing.value.reject_code == foreign.value.reject_code
    # The unified text echoes NEITHER probed id, and equals revoke's unified text
    # byte-for-byte (both operations share the ONE constant).
    assert "does-not-exist" not in str(missing.value)
    assert record.record_id not in str(foreign.value)
    assert str(missing.value) == _UNIFIED_NOT_FOUND_TEXT


# AS-2 (third branch): the supersedes_id-mismatch refusal fires ONLY when the
# record EXISTS, so a divergent message there would itself be an existence signal.
# It shares the identical unified text and responds identically for a mismatch on
# an existing record vs a missing old_id — no existence signal either way.
def test_supersede_supersedes_id_mismatch_shares_the_unified_not_found_text():
    store = InMemorySiteDefinitionStore()
    record = store.create(_make()).record
    # Existing old_id, but the superseding record references a DIFFERENT id.
    with pytest.raises(ConfirmationNotFoundError) as mismatch:
        store.supersede(
            record.record_id,
            _make(supersedes_id="a-different-id", reason="supersedes_id mismatch probe"),
        )
    # A MISSING old_id whose superseding record references that same missing id.
    with pytest.raises(ConfirmationNotFoundError) as missing:
        store.supersede(
            "no-such-id", _make(supersedes_id="no-such-id", reason="missing probe")
        )
    # Byte-identical text AND reject_code for the mismatch (record exists) and the
    # missing (record absent) -> the mismatch branch discloses no existence.
    assert str(mismatch.value) == str(missing.value) == _UNIFIED_NOT_FOUND_TEXT
    assert mismatch.value.reject_code == missing.value.reject_code
    # No id echo: neither the probed old_id nor the mismatched supersedes_id leaks.
    assert record.record_id not in str(mismatch.value)
    assert "a-different-id" not in str(mismatch.value)
