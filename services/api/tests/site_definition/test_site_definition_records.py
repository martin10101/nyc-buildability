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
    SITE_DEFINITION_STATUS_CONFIRMED,
    SITE_DEFINITION_STATUS_UNCONFIRMED,
    AttestationStatus,
    ConfirmationNotActiveError,
    ConfirmationNotFoundError,
    ConfirmationStatus,
    DuplicateActiveConfirmationError,
    InMemorySiteDefinitionStore,
    InvalidConfirmerError,
    OrphanSupersedeError,
    ParcelSetMismatchError,
    ResolutionProvenanceSnapshot,
    SiteDefinitionConfirmation,
    SiteDefinitionError,
    TransitionReasonRequiredError,
    build_site_definition_block,
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


def test_normalize_parcels_rejects_malformed_sets():
    with pytest.raises(InvalidConfirmerError):
        normalize_parcels("1003030019")  # not a list/tuple
    with pytest.raises(InvalidConfirmerError):
        normalize_parcels([""])  # blank entry
    with pytest.raises(InvalidConfirmerError):
        normalize_parcels([])  # empty
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
            condo_key=CONDO_KEY,
            reason="  ",
            actor=actor,
            at=LATER_AT.isoformat(),
        )
    view = store.revoke(
        record.record_id,
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
