"""Document lifecycle state machine (SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md section 4).

The six lifecycle states and the explicit allowed-transition table are transcribed
verbatim from the architecture document's section-4 table; any edge not in that table is
refused with the typed :class:`IllegalTransition`. The backend state machine is the only
transition authority: every transition is recorded with timestamp and actor, no state is
skippable, and ``rejected`` is terminal (a corrected upload is a NEW document with its
own digest identity).

Hard AI boundary: no AI/model-derived input can drive a transition. The mechanism is
structural, not advisory —

- :class:`ActorKind` is a CLOSED two-member enum (``deterministic_pipeline``,
  ``qualified_human``) with deliberately no AI/model/agent member;
- :class:`TransitionActor` refuses any kind that is not an :class:`ActorKind` member, so
  an AI label cannot be smuggled in as a string;
- :func:`transition` accepts no confidence, score, or model-output parameter of any
  kind — there is no channel through which a model's confidence could promote a state
  (fail-closed principle, contract section 6).

Entry into the machine is not a transition: the S1 upload gate creates the document
record already in ``uploaded`` (:data:`INITIAL_STATE`); a stream-cap failure before
durable storage is a typed API error with no record at all.

Error-hierarchy reconciliation: the state machine's refusals are MEMBERS of the
module-wide typed hierarchy in ``errors.py``, not a parallel one. Each class below
subclasses its ``errors.py`` counterpart (:class:`IllegalTransition` IS the raised form
of :class:`~app.documents.errors.IllegalTransitionError`, and so on), so one defect has
one class: state-machine callers catch the specific names here, API-layer callers catch
the ``errors.py`` names or ``DocumentIngestionError`` and serialize ``reject_code``
payloads — both catch the same raised object.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType

from app.documents.errors import (
    DocumentIngestionError,
    IllegalTransitionError,
    TransitionReasonRequiredError,
    UnauthorizedTransitionActorError,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "INITIAL_STATE",
    "TERMINAL_STATES",
    "ActorKind",
    "DocumentState",
    "DocumentStateError",
    "IllegalTransition",
    "TransitionActor",
    "TransitionReasonRequired",
    "TransitionRecord",
    "TransitionRule",
    "UnauthorizedTransitionActor",
    "allowed_transitions_from",
    "is_terminal",
    "transition",
]


class DocumentState(str, Enum):
    """The six document lifecycle states — exactly the architecture section-4 set."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    AUTO_EXTRACTED = "auto_extracted"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"
    PROFESSIONALLY_CONFIRMED = "professionally_confirmed"


#: A document record is born ``uploaded`` (created by the S1 gate after the original is
#: stored immutably and its digest recorded). There is no pre-``uploaded`` state.
INITIAL_STATE = DocumentState.UPLOADED

#: ``rejected`` is terminal (architecture section 4): no outgoing edges exist.
TERMINAL_STATES = frozenset({DocumentState.REJECTED})


class ActorKind(str, Enum):
    """CLOSED enum of transition authorities. Deliberately contains NO AI member.

    Only deterministic pipeline events and qualified-human actions exist. Adding any
    AI/model/agent member is a doctrine violation (architecture section 1 item 3 and
    section 4: "AI cannot trigger, veto, or propose any transition") and requires the
    same review a doctrine change requires.
    """

    DETERMINISTIC_PIPELINE = "deterministic_pipeline"
    QUALIFIED_HUMAN = "qualified_human"


class DocumentStateError(DocumentIngestionError):
    """Base class for typed state-machine refusals.

    Subclasses :class:`~app.documents.errors.DocumentIngestionError` so every
    state-machine refusal belongs to the single module-wide typed hierarchy (with a
    machine-readable ``reject_code`` payload) while remaining catchable as the
    state-machine family through this class.
    """


class IllegalTransition(IllegalTransitionError, DocumentStateError):
    """Requested edge is not in the section-4 allowed-transition table.

    The one concrete class for this defect: it IS the ``errors.py``
    :class:`~app.documents.errors.IllegalTransitionError` (``reject_code``
    ``illegal_transition``). Carries the edge as :class:`DocumentState` members on
    ``from_state``/``to_state`` and their string values in the structured payload.
    """

    def __init__(self, from_state: DocumentState, to_state: DocumentState) -> None:
        super().__init__(
            f"illegal document state transition: {from_state.value!r} -> {to_state.value!r} "
            "is not an edge of the section-4 transition table",
            from_state=from_state.value,
            to_state=to_state.value,
        )
        self.from_state = from_state
        self.to_state = to_state


class UnauthorizedTransitionActor(UnauthorizedTransitionActorError, DocumentStateError):
    """Actor is malformed, not a closed-enum member, or lacks authority for this edge.

    IS the ``errors.py`` :class:`~app.documents.errors.UnauthorizedTransitionActorError`
    (``reject_code`` ``unauthorized_transition_actor``).
    """


class TransitionReasonRequired(TransitionReasonRequiredError, DocumentStateError):
    """This edge requires a stated, non-empty reason (typed rejection / audited reopening).

    IS the ``errors.py`` :class:`~app.documents.errors.TransitionReasonRequiredError`
    (``reject_code`` ``transition_reason_required``).
    """


@dataclass(frozen=True)
class TransitionActor:
    """Who is driving a transition — a deterministic pipeline event or a qualified human.

    ``kind`` must be an :class:`ActorKind` member; any other value (including strings
    such as ``"ai"`` or ``"deterministic_pipeline"``) is refused, so no AI-labelled or
    string-smuggled actor can ever reach the transition table. Qualified-human actions
    must be attributed: ``actor_id`` is mandatory for ``QUALIFIED_HUMAN`` (the platform
    id whose licensure records live with the B-001-blocked auth design). For pipeline
    events ``actor_id`` optionally names the deterministic job/worker.
    """

    kind: ActorKind
    actor_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ActorKind):
            raise UnauthorizedTransitionActor(
                f"actor kind {self.kind!r} is not a member of the closed ActorKind enum; "
                "only deterministic_pipeline and qualified_human exist — there is no AI actor"
            )
        if self.actor_id is not None and (
            not isinstance(self.actor_id, str) or not self.actor_id.strip()
        ):
            raise UnauthorizedTransitionActor("actor_id, when given, must be a non-empty string")
        if self.kind is ActorKind.QUALIFIED_HUMAN and self.actor_id is None:
            raise UnauthorizedTransitionActor(
                "qualified-human transitions must be attributed: actor_id is required"
            )


@dataclass(frozen=True)
class TransitionRule:
    """One edge of the allowed-transition table."""

    trigger: str
    allowed_actor_kinds: frozenset[ActorKind]
    requires_reason: bool


_PIPELINE = frozenset({ActorKind.DETERMINISTIC_PIPELINE})
_HUMAN = frozenset({ActorKind.QUALIFIED_HUMAN})
_PIPELINE_OR_HUMAN = _PIPELINE | _HUMAN

#: The section-4 table, edge for edge. Rejections always carry a typed reason; the
#: ``professionally_confirmed`` reopening and the ``auto_extracted`` demotion are audited
#: with a stated reason ("visible and audited, never silent"). The fail-closed routing
#: ``processing -> needs_review`` needs no separate reason string because the reasons are
#: the typed ``validation_results`` on the affected facts.
ALLOWED_TRANSITIONS: MappingProxyType[
    tuple[DocumentState, DocumentState], TransitionRule
] = MappingProxyType(
    {
        (DocumentState.UPLOADED, DocumentState.PROCESSING): TransitionRule(
            trigger="worker claims the extraction job",
            allowed_actor_kinds=_PIPELINE,
            requires_reason=False,
        ),
        (DocumentState.UPLOADED, DocumentState.REJECTED): TransitionRule(
            trigger=(
                "security screen / structural validation failure (S2), unapproved format "
                "(S3), or integrity failure (section 6) — always with a typed reason"
            ),
            allowed_actor_kinds=_PIPELINE,
            requires_reason=True,
        ),
        (DocumentState.PROCESSING, DocumentState.REJECTED): TransitionRule(
            trigger=(
                "security screen / structural validation failure (S2), unapproved format "
                "(S3), or integrity failure (section 6) — always with a typed reason"
            ),
            allowed_actor_kinds=_PIPELINE,
            requires_reason=True,
        ),
        (DocumentState.PROCESSING, DocumentState.AUTO_EXTRACTED): TransitionRule(
            trigger=(
                "extraction completed; every executed check on every material fact is "
                "pass; no material advisory-only lineage"
            ),
            allowed_actor_kinds=_PIPELINE,
            requires_reason=False,
        ),
        (DocumentState.PROCESSING, DocumentState.NEEDS_REVIEW): TransitionRule(
            trigger=(
                "extraction completed with any fail/unresolved on a material fact, any "
                "material advisory-only or AI-classified value, or any tax-lot "
                "divergence — the fail-closed routing"
            ),
            allowed_actor_kinds=_PIPELINE,
            requires_reason=False,
        ),
        (DocumentState.AUTO_EXTRACTED, DocumentState.NEEDS_REVIEW): TransitionRule(
            trigger=(
                "later divergence (e.g. cross-check against newly accepted tax-lot "
                "geometry), a submitted correction, or a reviewer pulling it in"
            ),
            allowed_actor_kinds=_PIPELINE_OR_HUMAN,
            requires_reason=True,
        ),
        (DocumentState.AUTO_EXTRACTED, DocumentState.PROCESSING): TransitionRule(
            trigger=(
                "re-extraction: a new run with a new extraction_run_id; existing "
                "evidence records are never mutated"
            ),
            allowed_actor_kinds=_PIPELINE,
            requires_reason=False,
        ),
        (DocumentState.NEEDS_REVIEW, DocumentState.PROCESSING): TransitionRule(
            trigger=(
                "re-extraction: a new run with a new extraction_run_id; existing "
                "evidence records are never mutated"
            ),
            allowed_actor_kinds=_PIPELINE,
            requires_reason=False,
        ),
        (DocumentState.AUTO_EXTRACTED, DocumentState.PROFESSIONALLY_CONFIRMED): TransitionRule(
            trigger="qualified professional confirms the document after per-fact review",
            allowed_actor_kinds=_HUMAN,
            requires_reason=False,
        ),
        (DocumentState.NEEDS_REVIEW, DocumentState.PROFESSIONALLY_CONFIRMED): TransitionRule(
            trigger="qualified professional confirms the document after per-fact review",
            allowed_actor_kinds=_HUMAN,
            requires_reason=False,
        ),
        (DocumentState.NEEDS_REVIEW, DocumentState.REJECTED): TransitionRule(
            trigger=(
                "professional rejects the document (not a survey, wrong property per "
                "SB-S7, unusable)"
            ),
            allowed_actor_kinds=_HUMAN,
            requires_reason=True,
        ),
        (DocumentState.PROFESSIONALLY_CONFIRMED, DocumentState.NEEDS_REVIEW): TransitionRule(
            trigger=(
                "a post-confirmation contradiction is discovered — reopening is visible "
                "and audited, never silent"
            ),
            allowed_actor_kinds=_PIPELINE_OR_HUMAN,
            requires_reason=True,
        ),
    }
)


@dataclass(frozen=True)
class TransitionRecord:
    """One recorded transition: edge, actor, timestamp, and (when required) reason.

    Immutable once created; the document record accumulates these append-only
    (architecture section 4: "every transition is recorded with timestamp and actor").
    """

    from_state: DocumentState
    to_state: DocumentState
    actor: TransitionActor
    occurred_at: datetime
    reason: str | None = None


def _require_state(value: object, param: str) -> DocumentState:
    if not isinstance(value, DocumentState):
        raise TypeError(f"{param} must be a DocumentState member, got {value!r}")
    return value


def _require_actor(value: object) -> TransitionActor:
    if not isinstance(value, TransitionActor):
        raise UnauthorizedTransitionActor(
            f"actor must be a TransitionActor, got {value!r}; free-form actors "
            "(including any AI/model label) are never accepted"
        )
    return value


def _require_aware(value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.tzinfo.utcoffset(value) is None
    ):
        raise ValueError("occurred_at must be a timezone-aware datetime")
    return value


def transition(
    current: DocumentState,
    to: DocumentState,
    *,
    actor: TransitionActor,
    occurred_at: datetime,
    reason: str | None = None,
) -> TransitionRecord:
    """Validate one requested transition against the table and return its record.

    Raises :class:`IllegalTransition` for any non-table edge,
    :class:`UnauthorizedTransitionActor` for a malformed actor or an actor kind without
    authority over this edge, and :class:`TransitionReasonRequired` when a mandatory
    reason is absent or blank. Deliberately accepts NO confidence/score/model-output
    argument: an AI input has no channel into this function.
    """
    _require_state(current, "current")
    _require_state(to, "to")
    _require_actor(actor)
    rule = ALLOWED_TRANSITIONS.get((current, to))
    if rule is None:
        raise IllegalTransition(current, to)
    if actor.kind not in rule.allowed_actor_kinds:
        raise UnauthorizedTransitionActor(
            f"actor kind {actor.kind.value!r} has no authority for "
            f"{current.value!r} -> {to.value!r}; allowed: "
            f"{sorted(k.value for k in rule.allowed_actor_kinds)}"
        )
    if rule.requires_reason and (reason is None or not reason.strip()):
        raise TransitionReasonRequired(
            f"{current.value!r} -> {to.value!r} requires a stated reason"
        )
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        raise TransitionReasonRequired("reason, when given, must be a non-empty string")
    _require_aware(occurred_at)
    return TransitionRecord(
        from_state=current,
        to_state=to,
        actor=actor,
        occurred_at=occurred_at,
        reason=reason,
    )


def allowed_transitions_from(state: DocumentState) -> frozenset[DocumentState]:
    """Target states reachable from ``state`` per the table (empty for terminal states)."""
    _require_state(state, "state")
    return frozenset(to for (frm, to) in ALLOWED_TRANSITIONS if frm is state)


def is_terminal(state: DocumentState) -> bool:
    """True when ``state`` has no outgoing edge (exactly the ``rejected`` state)."""
    _require_state(state, "state")
    return state in TERMINAL_STATES
