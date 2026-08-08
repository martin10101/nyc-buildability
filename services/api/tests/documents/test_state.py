"""Unit tests for the document lifecycle state machine (M2-T015 unit 3a).

Proves, against docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md section 4:

1. the transition table is EXACTLY the documented edge set over the six documented
   states, and every table edge succeeds for every actor kind it authorizes;
2. every non-table ordered pair — checked exhaustively, all 36 combinations — raises the
   typed ``IllegalTransition`` (``rejected`` terminal, no skipped states, no self-loops);
3. authority and reason rules hold edge by edge (human-only confirmation/rejection,
   pipeline-only processing, mandatory reasons on rejection/demotion/reopening);
4. no AI/model-sourced event is accepted through ANY channel: the actor-kind enum is
   closed with no AI member, AI-labelled strings and free-form actors are refused typed,
   and the transition function exposes no confidence/score parameter at all;
5. the ``DocumentIngestionRecord`` evolves only through the state machine and keeps an
   append-only audit chain that replays exactly to its current state;
6. the state machine's refusals are ONE typed hierarchy with ``errors.py``, not a
   parallel one: each refusal IS its ``errors.py`` counterpart (``IllegalTransition``
   is-a ``IllegalTransitionError`` and so on), catchable as ``DocumentIngestionError``,
   with the documented ``reject_code`` and a metadata-only structured payload.
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from app.documents.errors import (
    DocumentIngestionError,
    IllegalTransitionError,
    TransitionReasonRequiredError,
    UnauthorizedTransitionActorError,
)
from app.documents.models import DocumentIngestionRecord
from app.documents.state import (
    ALLOWED_TRANSITIONS,
    INITIAL_STATE,
    TERMINAL_STATES,
    ActorKind,
    DocumentState,
    DocumentStateError,
    IllegalTransition,
    TransitionActor,
    TransitionReasonRequired,
    UnauthorizedTransitionActor,
    allowed_transitions_from,
    is_terminal,
    transition,
)

WHEN = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)

PIPELINE = TransitionActor(kind=ActorKind.DETERMINISTIC_PIPELINE, actor_id="worker-job-0001")
HUMAN = TransitionActor(kind=ActorKind.QUALIFIED_HUMAN, actor_id="professional-0001")
_ACTORS = {ActorKind.DETERMINISTIC_PIPELINE: PIPELINE, ActorKind.QUALIFIED_HUMAN: HUMAN}

S = DocumentState

#: The section-4 table, transcribed independently of state.py so a drifting table fails.
EXPECTED_EDGES = {
    (S.UPLOADED, S.PROCESSING),
    (S.UPLOADED, S.REJECTED),
    (S.PROCESSING, S.REJECTED),
    (S.PROCESSING, S.AUTO_EXTRACTED),
    (S.PROCESSING, S.NEEDS_REVIEW),
    (S.AUTO_EXTRACTED, S.NEEDS_REVIEW),
    (S.AUTO_EXTRACTED, S.PROCESSING),
    (S.NEEDS_REVIEW, S.PROCESSING),
    (S.AUTO_EXTRACTED, S.PROFESSIONALLY_CONFIRMED),
    (S.NEEDS_REVIEW, S.PROFESSIONALLY_CONFIRMED),
    (S.NEEDS_REVIEW, S.REJECTED),
    (S.PROFESSIONALLY_CONFIRMED, S.NEEDS_REVIEW),
}


# ----------------------------------------------------------------- states and table


def test_states_are_exactly_the_six_documented() -> None:
    assert {state.value for state in DocumentState} == {
        "uploaded",
        "processing",
        "auto_extracted",
        "needs_review",
        "rejected",
        "professionally_confirmed",
    }
    assert INITIAL_STATE is S.UPLOADED


def test_transition_table_is_exactly_the_documented_edge_set() -> None:
    assert set(ALLOWED_TRANSITIONS) == EXPECTED_EDGES


def test_rejected_is_the_only_terminal_state() -> None:
    assert TERMINAL_STATES == frozenset({S.REJECTED})
    assert allowed_transitions_from(S.REJECTED) == frozenset()
    for state in DocumentState:
        assert is_terminal(state) is (state is S.REJECTED)


# ------------------------------------------------------------------- legal edges


def test_every_legal_transition_succeeds_for_every_authorized_actor_kind() -> None:
    for (frm, to), rule in ALLOWED_TRANSITIONS.items():
        for kind in rule.allowed_actor_kinds:
            actor = _ACTORS[kind]
            reason = "stated test reason" if rule.requires_reason else None
            record = transition(frm, to, actor=actor, occurred_at=WHEN, reason=reason)
            assert record.from_state is frm
            assert record.to_state is to
            assert record.actor is actor
            assert record.occurred_at == WHEN
            assert record.reason == reason


def test_optional_reason_is_accepted_on_edges_that_do_not_require_one() -> None:
    record = transition(
        S.UPLOADED,
        S.PROCESSING,
        actor=PIPELINE,
        occurred_at=WHEN,
        reason="worker claim annotated for audit",
    )
    assert record.reason == "worker claim annotated for audit"


# ------------------------------------------------------------------ illegal edges


def test_every_non_table_ordered_pair_raises_illegal_transition() -> None:
    """Exhaustive complement: all 36 ordered pairs, minus the 12 table edges."""
    checked = 0
    for frm in DocumentState:
        for to in DocumentState:
            if (frm, to) in ALLOWED_TRANSITIONS:
                continue
            with pytest.raises(IllegalTransition) as excinfo:
                transition(frm, to, actor=PIPELINE, occurred_at=WHEN, reason="x")
            assert excinfo.value.from_state is frm
            assert excinfo.value.to_state is to
            checked += 1
    assert checked == 36 - len(EXPECTED_EDGES)


@pytest.mark.parametrize(
    ("frm", "to"),
    [
        (S.UPLOADED, S.AUTO_EXTRACTED),  # skipping processing
        (S.UPLOADED, S.PROFESSIONALLY_CONFIRMED),  # skipping every review state
        (S.PROCESSING, S.PROFESSIONALLY_CONFIRMED),  # confirmation without review state
        (S.AUTO_EXTRACTED, S.REJECTED),  # rejection must pass through needs_review
        (S.NEEDS_REVIEW, S.AUTO_EXTRACTED),  # no promotion out of review
        (S.PROFESSIONALLY_CONFIRMED, S.REJECTED),  # reopening goes to needs_review only
        (S.REJECTED, S.PROCESSING),  # terminal: a corrected upload is a NEW document
        (S.PROCESSING, S.PROCESSING),  # no self-loops
    ],
)
def test_representative_illegal_transitions_raise(frm: DocumentState, to: DocumentState) -> None:
    with pytest.raises(IllegalTransition):
        transition(frm, to, actor=HUMAN, occurred_at=WHEN, reason="x")


def test_non_state_inputs_are_refused() -> None:
    with pytest.raises(TypeError):
        transition(
            "uploaded",  # type: ignore[arg-type]
            S.PROCESSING,
            actor=PIPELINE,
            occurred_at=WHEN,
        )
    with pytest.raises(TypeError):
        allowed_transitions_from("rejected")  # type: ignore[arg-type]


# ---------------------------------------------------------------------- authority


def test_human_only_edges_reject_the_pipeline_actor() -> None:
    for frm, to, reason in [
        (S.AUTO_EXTRACTED, S.PROFESSIONALLY_CONFIRMED, None),
        (S.NEEDS_REVIEW, S.PROFESSIONALLY_CONFIRMED, None),
        (S.NEEDS_REVIEW, S.REJECTED, "not a survey"),
    ]:
        with pytest.raises(UnauthorizedTransitionActor):
            transition(frm, to, actor=PIPELINE, occurred_at=WHEN, reason=reason)


def test_pipeline_only_edges_reject_the_human_actor() -> None:
    for frm, to, reason in [
        (S.UPLOADED, S.PROCESSING, None),
        (S.UPLOADED, S.REJECTED, "failed security screen"),
        (S.PROCESSING, S.REJECTED, "failed structural validation"),
        (S.PROCESSING, S.AUTO_EXTRACTED, None),
        (S.PROCESSING, S.NEEDS_REVIEW, None),
        (S.AUTO_EXTRACTED, S.PROCESSING, None),
        (S.NEEDS_REVIEW, S.PROCESSING, None),
    ]:
        with pytest.raises(UnauthorizedTransitionActor):
            transition(frm, to, actor=HUMAN, occurred_at=WHEN, reason=reason)


def test_qualified_human_actor_requires_attribution() -> None:
    for bad_id in (None, "", "   "):
        with pytest.raises(UnauthorizedTransitionActor):
            TransitionActor(kind=ActorKind.QUALIFIED_HUMAN, actor_id=bad_id)


# ----------------------------------------------------------------- reason rules


def test_reason_required_edges_refuse_missing_or_blank_reasons() -> None:
    required = [(edge, rule) for edge, rule in ALLOWED_TRANSITIONS.items() if rule.requires_reason]
    assert {edge for edge, _ in required} == {
        (S.UPLOADED, S.REJECTED),
        (S.PROCESSING, S.REJECTED),
        (S.AUTO_EXTRACTED, S.NEEDS_REVIEW),
        (S.NEEDS_REVIEW, S.REJECTED),
        (S.PROFESSIONALLY_CONFIRMED, S.NEEDS_REVIEW),
    }
    for (frm, to), rule in required:
        actor = _ACTORS[next(iter(rule.allowed_actor_kinds))]
        for bad_reason in (None, "", "   "):
            with pytest.raises(TransitionReasonRequired):
                transition(frm, to, actor=actor, occurred_at=WHEN, reason=bad_reason)


def test_blank_reason_is_refused_even_where_a_reason_is_optional() -> None:
    with pytest.raises(TransitionReasonRequired):
        transition(S.UPLOADED, S.PROCESSING, actor=PIPELINE, occurred_at=WHEN, reason="   ")


# --------------------------------------------------- the hard AI boundary (no channel)


def test_actor_kind_enum_is_closed_with_no_ai_member() -> None:
    assert set(ActorKind) == {ActorKind.DETERMINISTIC_PIPELINE, ActorKind.QUALIFIED_HUMAN}
    assert {kind.value for kind in ActorKind} == {"deterministic_pipeline", "qualified_human"}


@pytest.mark.parametrize(
    "ai_kind",
    [
        "ai",
        "model",
        "llm",
        "agent",
        "ai_assisted_classification",
        "deterministic_pipeline",  # even the right VALUE as a raw string is refused
        "qualified_human",
    ],
)
def test_ai_labelled_or_string_smuggled_actor_kinds_are_refused(ai_kind: str) -> None:
    with pytest.raises(UnauthorizedTransitionActor):
        TransitionActor(kind=ai_kind, actor_id="whoever")  # type: ignore[arg-type]


@pytest.mark.parametrize("bad_actor", ["ai-agent", None, {"kind": "ai"}, 0.98])
def test_free_form_actors_never_reach_the_table(bad_actor: object) -> None:
    with pytest.raises(UnauthorizedTransitionActor):
        transition(
            S.UPLOADED,
            S.PROCESSING,
            actor=bad_actor,  # type: ignore[arg-type]
            occurred_at=WHEN,
        )


def test_model_confidence_has_no_parameter_channel_into_transitions() -> None:
    """The fail-closed principle, structurally: transition() has no confidence/score
    argument, so a model's confidence cannot even be EXPRESSED to the state machine."""
    with pytest.raises(TypeError):
        transition(  # type: ignore[call-arg]
            S.PROCESSING,
            S.AUTO_EXTRACTED,
            actor=PIPELINE,
            occurred_at=WHEN,
            confidence=0.99,
        )


# ------------------------------------------------------------- record discipline


def test_naive_timestamps_are_refused() -> None:
    with pytest.raises(ValueError):
        transition(
            S.UPLOADED,
            S.PROCESSING,
            actor=PIPELINE,
            occurred_at=datetime(2026, 8, 8, 12, 0, 0),  # noqa: DTZ001 - naive on purpose
        )


def test_transition_records_are_immutable() -> None:
    record = transition(S.UPLOADED, S.PROCESSING, actor=PIPELINE, occurred_at=WHEN)
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.to_state = S.REJECTED  # type: ignore[misc]


# --------------------------------------- ingestion record evolves only via the machine


def _record() -> DocumentIngestionRecord:
    return DocumentIngestionRecord(
        document_digest="sha256:" + "ab" * 32,
        target_bbl="1000470001",
        original_filename="synthetic-survey.pdf",
        declared_document_class="property_survey",
        sniffed_mime_type="application/pdf",
        size_bytes=1024,
        uploaded_at=WHEN,
    )


def test_record_walks_a_full_legal_lifecycle_with_replayable_history() -> None:
    doc = _record()
    assert doc.state is S.UPLOADED
    assert doc.state_history == ()

    doc = doc.apply_transition(S.PROCESSING, actor=PIPELINE, occurred_at=WHEN)
    doc = doc.apply_transition(
        S.NEEDS_REVIEW, actor=PIPELINE, occurred_at=WHEN + timedelta(minutes=1)
    )
    doc = doc.apply_transition(
        S.PROFESSIONALLY_CONFIRMED, actor=HUMAN, occurred_at=WHEN + timedelta(minutes=2)
    )
    assert doc.state is S.PROFESSIONALLY_CONFIRMED
    assert [(r.from_state, r.to_state) for r in doc.state_history] == [
        (S.UPLOADED, S.PROCESSING),
        (S.PROCESSING, S.NEEDS_REVIEW),
        (S.NEEDS_REVIEW, S.PROFESSIONALLY_CONFIRMED),
    ]
    # The B-001-honest fields: no storage binding exists, the digest is the identity.
    assert doc.document_ref is None
    assert doc.storage_ref is None


def test_record_refuses_illegal_edges_through_the_same_typed_error() -> None:
    with pytest.raises(IllegalTransition):
        _record().apply_transition(S.PROFESSIONALLY_CONFIRMED, actor=HUMAN, occurred_at=WHEN)


def test_record_born_past_uploaded_without_history_is_refused() -> None:
    with pytest.raises(ValueError):
        dataclasses.replace(_record(), state=S.AUTO_EXTRACTED)


def test_record_with_history_that_does_not_replay_to_state_is_refused() -> None:
    doc = _record().apply_transition(S.PROCESSING, actor=PIPELINE, occurred_at=WHEN)
    with pytest.raises(ValueError):
        dataclasses.replace(doc, state=S.NEEDS_REVIEW)


def test_record_refuses_a_malformed_digest() -> None:
    with pytest.raises(ValueError):
        dataclasses.replace(_record(), document_digest="md5:abc")


# ---------------------------- one typed hierarchy with errors.py (reconciliation)


def test_state_refusals_are_the_errors_module_classes_not_parallel_types() -> None:
    """One class per defect: each state.py refusal IS its errors.py counterpart."""
    assert issubclass(DocumentStateError, DocumentIngestionError)
    assert issubclass(IllegalTransition, IllegalTransitionError)
    assert issubclass(IllegalTransition, DocumentStateError)
    assert issubclass(UnauthorizedTransitionActor, UnauthorizedTransitionActorError)
    assert issubclass(UnauthorizedTransitionActor, DocumentStateError)
    assert issubclass(TransitionReasonRequired, TransitionReasonRequiredError)
    assert issubclass(TransitionReasonRequired, DocumentStateError)


def test_illegal_transition_is_catchable_by_errors_name_with_structured_payload() -> None:
    with pytest.raises(IllegalTransitionError) as excinfo:
        transition(S.REJECTED, S.PROCESSING, actor=PIPELINE, occurred_at=WHEN)
    err = excinfo.value
    assert isinstance(err, IllegalTransition)  # the same raised object, not a sibling type
    assert err.reject_code == "illegal_transition"
    payload = err.to_payload()
    assert payload["reject_code"] == "illegal_transition"
    assert payload["from_state"] == "rejected"
    assert payload["to_state"] == "processing"
    # Typed DocumentState members stay available for state-machine callers.
    assert err.from_state is S.REJECTED
    assert err.to_state is S.PROCESSING


def test_actor_and_reason_refusals_carry_their_documented_reject_codes() -> None:
    with pytest.raises(UnauthorizedTransitionActorError) as actor_refusal:
        transition(S.UPLOADED, S.PROCESSING, actor=HUMAN, occurred_at=WHEN)
    assert actor_refusal.value.reject_code == "unauthorized_transition_actor"

    with pytest.raises(TransitionReasonRequiredError) as reason_refusal:
        transition(S.UPLOADED, S.REJECTED, actor=PIPELINE, occurred_at=WHEN)
    assert reason_refusal.value.reject_code == "transition_reason_required"


def test_every_state_refusal_is_catchable_as_document_ingestion_error() -> None:
    with pytest.raises(DocumentIngestionError):
        transition(S.REJECTED, S.PROCESSING, actor=PIPELINE, occurred_at=WHEN)
    with pytest.raises(DocumentIngestionError):
        transition(S.UPLOADED, S.PROCESSING, actor=HUMAN, occurred_at=WHEN)
    with pytest.raises(DocumentIngestionError):
        transition(S.UPLOADED, S.REJECTED, actor=PIPELINE, occurred_at=WHEN)
    with pytest.raises(DocumentIngestionError):
        TransitionActor(kind="ai", actor_id="whoever")  # type: ignore[arg-type]
