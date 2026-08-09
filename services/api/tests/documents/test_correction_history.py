"""Tests for app.documents.correction_history (M2-T015 unit 3e-2; H4 correction-history integrity).

Adversarial coverage required by the unit: deletion, reordering, insertion, timestamp
reversal, mismatched previous values, mismatched latest values, actor spoofing, and
history mutation — every one must yield the typed refusal, never an exception — plus
fully valid histories that resolve.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

from app.documents.correction_history import (
    CorrectingActorRole,
    NormalizationBaseline,
    OriginalValueReference,
    ProfessionalConfirmationState,
    UnresolvedCorrectionHistory,
    ValidatedCorrectingActor,
    ValidatedCorrectionHistory,
    ValidatedHistoryExtension,
    ValidatedProfessionalConfirmation,
    validate_correcting_actor,
    validate_correction_history,
    validate_history_extension,
    validate_professional_confirmation,
)

# ------------------------------------------------------------------ fixtures


def _entry(**overrides):
    """A valid user correction: 100.0 feet -> 100.5 feet."""
    base = {
        "corrected_at": "2026-08-01T12:00:00Z",
        "corrected_by_role": "user",
        "previous_normalized_value": 100.0,
        "corrected_normalized_value": 100.5,
        "previous_units": "feet",
        "corrected_units": "feet",
        "reason": "OCR misread the final digit against the drawn dimension text",
    }
    base.update(overrides)
    return base


def _professional_entry(**overrides):
    """A valid qualified-professional correction: 100.5 feet -> 100.25 feet."""
    base = _entry(
        corrected_at="2026-08-02T09:30:00Z",
        corrected_by_role="qualified_professional",
        corrected_by="reviewer:ls-049112",
        previous_normalized_value=100.5,
        corrected_normalized_value=100.25,
        reason="Licensed-surveyor re-measurement of the plat dimension",
    )
    base.update(overrides)
    return base


def _validate(history, **overrides):
    """Run the full-record validator with a consistent valid record around history."""
    kwargs: dict[str, Any] = dict(
        original_value="100 FT.",
        normalized_value=100.25,
        units="feet",
        correction_history=history,
        expected_original=OriginalValueReference(original_value="100 FT."),
        baseline=NormalizationBaseline(normalized_value=100.0, units="feet"),
    )
    kwargs.update(overrides)
    return validate_correction_history(**kwargs)


def _refused(result, *phrases):
    """Assert the typed visible refusal (never an exception) carrying each phrase."""
    assert isinstance(result, UnresolvedCorrectionHistory)
    assert result.resolved is False
    assert result.promotable is False
    for phrase in phrases:
        assert phrase in result.reason
    return result


# ------------------------------------------------- fully valid histories resolve


def test_fully_valid_history_resolves():
    result = _validate([_entry(), _professional_entry()])
    assert isinstance(result, ValidatedCorrectionHistory)
    assert result.resolved is True
    assert result.correction_count == 2
    assert result.entries[0].corrected_by_role is CorrectingActorRole.USER
    assert result.entries[0].corrected_by is None
    assert result.entries[1].corrected_by_role is CorrectingActorRole.QUALIFIED_PROFESSIONAL
    assert result.entries[1].corrected_by == "reviewer:ls-049112"
    assert result.entries[1].corrected_normalized_value == 100.25


def test_never_corrected_record_resolves():
    result = _validate([], normalized_value=100.0)
    assert isinstance(result, ValidatedCorrectionHistory)
    assert result.correction_count == 0
    assert result.entries == ()


def test_valid_history_resolves_without_optional_cross_checks():
    result = _validate(
        [_entry(), _professional_entry()], expected_original=None, baseline=None
    )
    assert isinstance(result, ValidatedCorrectionHistory)


def test_units_only_correction_is_a_real_correction():
    # A decimal/unit-ambiguity fix can change units while the number stands.
    history = [
        _entry(
            previous_normalized_value=100.0,
            corrected_normalized_value=100.0,
            previous_units="feet",
            corrected_units="square_feet",
            reason="The detection was the stated lot area, not a boundary distance",
        )
    ]
    result = _validate(history, normalized_value=100.0, units="square_feet")
    assert isinstance(result, ValidatedCorrectionHistory)


def test_cross_offset_chronology_resolves():
    # 14:00-04:00 == 18:00Z, strictly after 12:00Z despite the differing offsets.
    later = _professional_entry(corrected_at="2026-08-01T14:00:00-04:00")
    result = _validate([_entry(), later])
    assert isinstance(result, ValidatedCorrectionHistory)


# ------------------------------------------------------- chronology (reversal)


def test_timestamp_reversal_refused():
    reversed_entry = _professional_entry(corrected_at="2026-08-01T09:00:00Z")
    _refused(_validate([_entry(), reversed_entry]), "strictly chronological")


def test_equal_timestamps_refused_as_ambiguous():
    same_instant = _professional_entry(corrected_at="2026-08-01T12:00:00Z")
    _refused(_validate([_entry(), same_instant]), "strictly chronological")


def test_offset_masked_reversal_refused():
    # 13:00+02:00 == 11:00Z: later as a string, earlier as an instant.
    masked = _professional_entry(corrected_at="2026-08-01T13:00:00+02:00")
    _refused(_validate([_entry(), masked]), "strictly chronological")


def test_reordered_history_refused():
    _refused(_validate([_professional_entry(), _entry()]))


# --------------------------------------------- chain (mismatched previous state)


def test_mismatched_previous_value_refused():
    broken = _professional_entry(previous_normalized_value=999.0)
    _refused(_validate([_entry(), broken]), "previous_normalized_value")


def test_mismatched_previous_units_refused():
    broken = _professional_entry(previous_units=None)
    _refused(_validate([_entry(), broken]), "previous_units")


def test_first_entry_must_match_baseline():
    # Deleting the leading entry leaves the survivor starting from 100.5, not 100.0.
    _refused(_validate([_professional_entry()]), "baseline")


def test_baseline_units_mismatch_refused():
    _refused(
        _validate(
            [_entry()],
            normalized_value=100.5,
            baseline=NormalizationBaseline(normalized_value=100.0, units=None),
        ),
        "baseline",
    )


def test_boolean_never_equals_number_in_chain():
    first = _entry(corrected_normalized_value=1)
    forged = _professional_entry(previous_normalized_value=True)
    _refused(_validate([first, forged]), "previous_normalized_value")


def test_empty_history_with_drifted_current_value_refused():
    _refused(_validate([], normalized_value=123.0), "never-corrected")


# ------------------------------------------------- latest-state agreement


def test_latest_value_disagreement_refused():
    _refused(
        _validate([_entry(), _professional_entry()], normalized_value=999.9),
        "current normalized_value",
    )


def test_latest_units_disagreement_refused():
    _refused(_validate([_entry(), _professional_entry()], units="square_feet"), "current units")


def test_deleting_trailing_entry_is_visible_as_latest_disagreement():
    # Record state came from the (deleted) second correction; the survivor disagrees.
    _refused(_validate([_entry()]), "current normalized_value")


# ------------------------------------------------- original_value immutability


def test_mutated_original_value_refused():
    _refused(
        _validate([_entry(), _professional_entry()], original_value="99 FT."),
        "original_value is immutable",
    )


def test_entry_smuggling_original_value_refused():
    tampered = _professional_entry(original_value="99 FT.")
    _refused(_validate([_entry(), tampered]), "closed", "original_value")


# ------------------------------------------------- entry shape / malformed input


@pytest.mark.parametrize(
    "history",
    [
        "not-a-list",
        {"0": _entry()},
        None,
        42,
        ["not-an-entry"],
        [_entry(), ["nested"]],
    ],
    ids=["str", "dict", "none", "int", "str-entry", "list-entry"],
)
def test_non_wire_history_shapes_refused(history):
    _refused(_validate(history))


def test_missing_required_key_refused():
    partial = _entry()
    del partial["reason"]
    _refused(_validate([partial]), "missing required key")


def test_unknown_key_refused_as_tampering():
    _refused(_validate([_entry(note="sneaky sidechannel")]), "tampering")


@pytest.mark.parametrize(
    "corrected_at",
    [1234, None, "08/01/2026", "2026-08-01 12:00:00",
     "2026-08-01T12:00:00", "2026-13-01T00:00:00Z"],
    ids=["int", "none", "us-date", "no-T", "no-offset", "month-13"],
)
def test_malformed_corrected_at_refused(corrected_at):
    _refused(_validate([_entry(corrected_at=corrected_at)]))


@pytest.mark.parametrize("reason", ["", "   ", None, 7])
def test_unreviewable_reason_refused(reason):
    _refused(_validate([_entry(reason=reason)]))


@pytest.mark.parametrize("units_value", [5, True, ["feet"]])
def test_non_wire_entry_units_refused(units_value):
    _refused(_validate([_entry(previous_units=units_value)]))


def test_non_wire_record_units_refused():
    _refused(_validate([_entry(), _professional_entry()], units=5))


def test_noop_correction_refused():
    noop = _entry(corrected_normalized_value=100.0)
    _refused(_validate([noop]), "no-op")


# ---------------------------------------------- append-only extension integrity


def test_extension_append_resolves():
    result = validate_history_extension([_entry()], [_entry(), _professional_entry()])
    assert isinstance(result, ValidatedHistoryExtension)
    assert result.resolved is True
    assert result.accepted_entry_count == 1
    assert result.appended_entry_count == 1


def test_extension_unchanged_resolves():
    accepted = [_entry(), _professional_entry()]
    result = validate_history_extension(accepted, [_entry(), _professional_entry()])
    assert isinstance(result, ValidatedHistoryExtension)
    assert result.appended_entry_count == 0


def test_extension_deletion_refused():
    _refused(
        validate_history_extension([_entry(), _professional_entry()], [_entry()]),
        "append-only",
    )


def test_extension_full_wipe_refused():
    _refused(validate_history_extension([_entry()], []), "append-only")


def test_extension_reordering_refused():
    accepted = [_entry(), _professional_entry()]
    _refused(
        validate_history_extension(accepted, [_professional_entry(), _entry()]),
        "append-only",
    )


def test_extension_insertion_refused():
    forged = _entry(
        corrected_at="2026-08-01T12:30:00Z",
        corrected_normalized_value=555.0,
        reason="forged mid-history correction",
    )
    accepted = [_entry(), _professional_entry()]
    _refused(
        validate_history_extension(accepted, [_entry(), forged, _professional_entry()]),
        "append-only",
    )


def test_extension_mutation_of_accepted_entry_refused():
    mutated = _entry(reason="rewritten after acceptance")
    _refused(
        validate_history_extension(
            [_entry(), _professional_entry()], [mutated, _professional_entry()]
        ),
        "append-only",
    )


@pytest.mark.parametrize("bad", ["x", None, {"0": []}])
def test_extension_non_list_inputs_refused(bad):
    _refused(validate_history_extension(bad, []))
    _refused(validate_history_extension([], bad))


# --------------------------------------------- actor authority model / spoofing


def test_human_user_actor_resolves():
    result = validate_correcting_actor("user", "human_user", None)
    assert isinstance(result, ValidatedCorrectingActor)
    assert result.role is CorrectingActorRole.USER
    assert result.actor_id is None


def test_qualified_professional_actor_resolves():
    result = validate_correcting_actor(
        "qualified_professional", "human_qualified_professional", "reviewer:ls-049112"
    )
    assert isinstance(result, ValidatedCorrectingActor)
    assert result.role is CorrectingActorRole.QUALIFIED_PROFESSIONAL
    assert result.actor_id == "reviewer:ls-049112"


@pytest.mark.parametrize(
    "principal_kind",
    ["ai_agent", "model", "system", "service_account", "extraction_pipeline", "", None, 3],
    ids=["ai", "model", "system", "service", "pipeline", "empty", "none", "int"],
)
def test_automated_or_unknown_principal_can_never_author(principal_kind):
    result = validate_correcting_actor("user", principal_kind, None)
    _refused(result, "never author or impersonate")


def test_user_principal_cannot_impersonate_professional():
    result = validate_correcting_actor(
        "qualified_professional", "human_user", "someone"
    )
    _refused(result, "impersonation")


def test_professional_principal_cannot_write_under_user_role():
    result = validate_correcting_actor(
        "user", "human_qualified_professional", "reviewer:ls-049112"
    )
    _refused(result, "impersonation")


@pytest.mark.parametrize("role", ["admin", "User", "USER", " user", "ai", None, 1])
def test_unknown_or_uncanonical_role_refused(role):
    _refused(validate_correcting_actor(role, "human_user", None))


@pytest.mark.parametrize("actor_id", [None, "", "   "])
def test_professional_without_identity_evidence_refused(actor_id):
    result = validate_correcting_actor(
        "qualified_professional", "human_qualified_professional", actor_id
    )
    _refused(result)


@pytest.mark.parametrize("spoofed_role", ["ai", "ai_assisted_classification", "system", "model"])
def test_entry_claiming_ai_authorship_refused(spoofed_role):
    _refused(
        _validate([_entry(corrected_by_role=spoofed_role)]),
        "closed",
    )


def test_professional_entry_without_identity_refused():
    anonymous = _professional_entry(
        previous_normalized_value=100.0, corrected_normalized_value=100.25
    )
    del anonymous["corrected_by"]
    _refused(_validate([anonymous]), "identity evidence")


@pytest.mark.parametrize("corrected_by", [None, "", "   ", 7])
def test_blank_correction_identity_refused(corrected_by):
    _refused(_validate([_entry(corrected_by=corrected_by)]))


# -------------------------------------- professional confirmation evidence


def test_confirmed_state_with_full_evidence_resolves():
    result = validate_professional_confirmation(
        {
            "state": "confirmed",
            "confirmed_by": "reviewer:ls-049112",
            "confirmed_at": "2026-08-03T10:00:00Z",
            "note": "Matches the recorded plat.",
        }
    )
    assert isinstance(result, ValidatedProfessionalConfirmation)
    assert result.state is ProfessionalConfirmationState.CONFIRMED
    assert result.confirmed_by == "reviewer:ls-049112"


def test_unconfirmed_state_with_null_evidence_resolves():
    result = validate_professional_confirmation(
        {"state": "unconfirmed", "confirmed_by": None, "confirmed_at": None}
    )
    assert isinstance(result, ValidatedProfessionalConfirmation)
    assert result.state is ProfessionalConfirmationState.UNCONFIRMED


def test_unconfirmed_state_claiming_evidence_refused():
    result = validate_professional_confirmation(
        {"state": "unconfirmed", "confirmed_by": None, "confirmed_at": "2026-08-03T10:00:00Z"}
    )
    _refused(result, "tampering")


@pytest.mark.parametrize("confirmed_by", [None, "", "   ", 9])
def test_confirmation_without_identity_evidence_refused(confirmed_by):
    result = validate_professional_confirmation(
        {"state": "rejected", "confirmed_by": confirmed_by, "confirmed_at": "2026-08-03T10:00:00Z"}
    )
    _refused(result, "identity evidence")


@pytest.mark.parametrize("confirmed_at", [None, "yesterday", "2026-13-01T00:00:00Z"])
def test_confirmation_without_time_evidence_refused(confirmed_at):
    result = validate_professional_confirmation(
        {"state": "confirmed", "confirmed_by": "reviewer:ls-049112", "confirmed_at": confirmed_at}
    )
    _refused(result, "time evidence")


@pytest.mark.parametrize("state", ["approved", "CONFIRMED", "ai_confirmed", None, True])
def test_confirmation_outside_closed_state_vocabulary_refused(state):
    result = validate_professional_confirmation(
        {"state": state, "confirmed_by": None, "confirmed_at": None}
    )
    _refused(result)


def test_confirmation_unknown_key_refused_as_tampering():
    result = validate_professional_confirmation(
        {
            "state": "confirmed",
            "confirmed_by": "reviewer:ls-049112",
            "confirmed_at": "2026-08-03T10:00:00Z",
            "approved_by_model": "claude",
        }
    )
    _refused(result, "tampering")


def test_confirmation_missing_key_refused():
    _refused(validate_professional_confirmation({"state": "unconfirmed"}))


def test_non_object_confirmation_refused():
    _refused(validate_professional_confirmation("confirmed"))


# ---------------------------------------------- refusal-value semantics


def test_refusal_is_a_frozen_visible_value_never_raised():
    result = _validate("tampered")
    assert isinstance(result, UnresolvedCorrectionHistory)
    assert result.reject_code == "unresolved_correction_history"
    payload = result.to_payload()
    assert payload["reject_code"] == "unresolved_correction_history"
    assert set(payload) == {"reject_code", "submitted", "reason"}
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.reason = "rewritten"


def test_refusal_carries_verbatim_submission_only():
    result = validate_correcting_actor("user", "ai_agent", None)
    assert isinstance(result, UnresolvedCorrectionHistory)
    assert "ai_agent" in result.submitted
    assert not hasattr(result, "entries")
    assert not hasattr(result, "role")


def test_resolved_history_is_frozen():
    result = _validate([_entry(), _professional_entry()])
    assert isinstance(result, ValidatedCorrectionHistory)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.correction_count = 0
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.entries[0].corrected_normalized_value = 999.0
