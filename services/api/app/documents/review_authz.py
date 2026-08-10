"""Per-action authorization for the survey review-action slice (M2-T016, Packet C).

Server-side, fail-closed authorization for every review action
(docs/SURVEY_REVIEW_WORKFLOW.md sections 5.1-5.3, 12). The authenticated principal
classification is resolved by the SUBMISSION CHANNEL and passed in here — it is NEVER
self-declared by the request payload — exactly as
:func:`app.documents.correction_history.validate_correcting_actor` requires. The role a
principal holds is DERIVED from that closed principal kind, never accepted from the
caller.

This module ADDS a per-action authorization layer on top of — and reusing — the shipped
closed authority model; it re-implements none of it:

- the closed principal model :class:`~app.documents.correction_history.CorrectingPrincipal`
  (``human_user`` / ``human_qualified_professional``) has NO AI/model/agent/service/system
  member, so an automated principal is unrepresentable and refused outright;
- the closed human role vocabulary
  :class:`~app.documents.correction_history.CorrectingActorRole` (``user`` /
  ``qualified_professional``) is exact-match only;
- document-lifecycle transitions still go through
  :class:`~app.documents.state.TransitionActor` /
  :func:`~app.documents.state.promotion_gated_transition` (this module never transitions
  a document — it only decides whether the principal may attempt the action).

Hard boundary (SC-S3/SC-S4): ``professionally_confirmed`` (document) and per-fact
``confirmed``/``rejected`` are reachable ONLY through the designated professional role
here. No confidence score, AI classification, or automatic path is representable — the
gate is structural, not advisory. The concrete real-world licence that qualifies as the
professional is a pending owner / qualified-human decision (workflow section 5.5, Tier D):
this module implements the closed-enum MECHANISM and gates on it; it never binds a real
licence as "granted".
"""

from __future__ import annotations

import enum

from app.documents.correction_history import CorrectingActorRole, CorrectingPrincipal
from app.documents.errors import DocumentIngestionError

__all__ = [
    "ACTION_ALLOWED_ROLES",
    "ReviewAction",
    "UnauthorizedReviewAction",
    "ValidatedReviewPrincipal",
    "authorize_review_action",
]


class UnauthorizedReviewAction(DocumentIngestionError):
    """The authenticated principal may not perform this review action (fail-closed).

    A member of the module-wide typed hierarchy (``reject_code``
    ``unauthorized_review_action``) so the API layer serializes it exactly like every
    other ingestion refusal. Raised — never returned — so a handler that forgets to
    check authority cannot silently proceed.
    """

    reject_code = "unauthorized_review_action"


@enum.unique
class ReviewAction(enum.Enum):
    """Closed set of review actions the slice authorizes (workflow section 12)."""

    READ = "read"
    ACCEPT_FACT = "accept_fact"
    CORRECT_FACT = "correct_fact"
    REJECT_FACT = "reject_fact"
    CONFIRM_DOCUMENT = "confirm_document"
    REJECT_DOCUMENT = "reject_document"
    REOPEN_DOCUMENT = "reopen_document"


_USER = CorrectingActorRole.USER
_PRO = CorrectingActorRole.QUALIFIED_PROFESSIONAL

#: The single human role each closed principal's authority grants. Mirrors
#: ``correction_history._GRANTED_ROLE`` (kept local so this module states its own
#: authority mapping); an automated principal has no entry and is unrepresentable.
_PRINCIPAL_ROLE: dict[CorrectingPrincipal, CorrectingActorRole] = {
    CorrectingPrincipal.HUMAN_USER: _USER,
    CorrectingPrincipal.HUMAN_QUALIFIED_PROFESSIONAL: _PRO,
}

#: The per-action authorization matrix (workflow section 5.2). Reading and the two
#: non-binding per-fact review decisions (accept, correct) are open to any authorized
#: human; every action that writes professional confirmation or drives a human document
#: edge (reject a fact detection into ``rejected`` confirmation, confirm/reject/reopen
#: the document) is the designated professional role ONLY. Extends only by adding an
#: action with its explicit allowed-role set — never by loosening an existing row.
ACTION_ALLOWED_ROLES: dict[ReviewAction, frozenset[CorrectingActorRole]] = {
    ReviewAction.READ: frozenset({_USER, _PRO}),
    ReviewAction.ACCEPT_FACT: frozenset({_USER, _PRO}),
    ReviewAction.CORRECT_FACT: frozenset({_USER, _PRO}),
    ReviewAction.REJECT_FACT: frozenset({_PRO}),
    ReviewAction.CONFIRM_DOCUMENT: frozenset({_PRO}),
    ReviewAction.REJECT_DOCUMENT: frozenset({_PRO}),
    ReviewAction.REOPEN_DOCUMENT: frozenset({_PRO}),
}

# Import-time completeness guard (mirrors promotion.py): a review action with no
# authorization row would fail-open at call time. Every member must be governed.
_UNGOVERNED = frozenset(ReviewAction) - frozenset(ACTION_ALLOWED_ROLES)
if _UNGOVERNED:  # pragma: no cover - structural guard
    raise RuntimeError(
        "every ReviewAction needs an explicit ACTION_ALLOWED_ROLES row; ungoverned: "
        + ", ".join(sorted(member.value for member in _UNGOVERNED))
    )


class ValidatedReviewPrincipal:
    """A principal whose closed kind, derived role, and identity satisfy an action.

    Immutable value produced only by :func:`authorize_review_action`. ``actor_id`` is
    the authenticated platform identity (required for every professional action; the
    identity scheme itself is B-001-blocked at the wire but the app rule is stricter).
    """

    __slots__ = ("_principal", "_role", "_actor_id")

    def __init__(
        self,
        principal: CorrectingPrincipal,
        role: CorrectingActorRole,
        actor_id: str | None,
    ) -> None:
        self._principal = principal
        self._role = role
        self._actor_id = actor_id

    @property
    def principal(self) -> CorrectingPrincipal:
        return self._principal

    @property
    def role(self) -> CorrectingActorRole:
        return self._role

    @property
    def actor_id(self) -> str | None:
        return self._actor_id

    @property
    def is_professional(self) -> bool:
        return self._role is CorrectingActorRole.QUALIFIED_PROFESSIONAL

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return (
            f"ValidatedReviewPrincipal(principal={self._principal.value!r}, "
            f"role={self._role.value!r}, actor_id={self._actor_id!r})"
        )


def authorize_review_action(
    action: ReviewAction,
    principal_kind: object,
    actor_id: object,
) -> ValidatedReviewPrincipal:
    """Authorize one review action for one channel-authenticated principal (fail-closed).

    ``principal_kind`` is the closed :class:`CorrectingPrincipal` wire value the
    submission channel resolved (never a payload claim); ``actor_id`` is the
    authenticated identity or ``None`` when the identity scheme cannot state one
    (B-001). Raises :class:`UnauthorizedReviewAction` when the principal is not a closed
    human member (an AI/model/agent/service/system principal, or any unknown value), when
    its derived role is not permitted for ``action``, or when a professional action lacks
    the required non-empty ``actor_id``. Returns the :class:`ValidatedReviewPrincipal`
    otherwise. Never authorizes on ambiguity.
    """
    if not isinstance(action, ReviewAction):
        raise UnauthorizedReviewAction(
            f"action must be a ReviewAction member, got {action!r}",
            action=repr(action),
        )
    if not isinstance(principal_kind, str):
        raise UnauthorizedReviewAction(
            "authenticated principal kind must be a closed CorrectingPrincipal wire "
            f"string, got {type(principal_kind).__name__}; an AI/model/agent/service/"
            "system principal is unrepresentable and can never act",
            action=action.value,
        )
    try:
        principal = CorrectingPrincipal(principal_kind)
    except ValueError:
        supported = ", ".join(sorted(member.value for member in CorrectingPrincipal))
        raise UnauthorizedReviewAction(
            f"principal {principal_kind!r} is outside the closed human-authority model "
            f"(supported: {supported}); AI, model, agent, service, and system "
            "principals can never perform a review action",
            action=action.value,
            principal_kind=principal_kind,
        ) from None
    role = _PRINCIPAL_ROLE[principal]
    allowed = ACTION_ALLOWED_ROLES[action]
    if role not in allowed:
        raise UnauthorizedReviewAction(
            f"role {role.value!r} may not perform {action.value!r}; this action is "
            "restricted to " + ", ".join(sorted(r.value for r in allowed))
            + " — the professional-confirmation and document-decision actions are the "
            "designated qualified-professional role only",
            action=action.value,
            role=role.value,
        )
    if actor_id is not None and (not isinstance(actor_id, str) or not actor_id.strip()):
        raise UnauthorizedReviewAction(
            "actor_id, when stated, must be a non-empty identifier string",
            action=action.value,
        )
    resolved_actor_id = actor_id if isinstance(actor_id, str) else None
    if role is CorrectingActorRole.QUALIFIED_PROFESSIONAL and resolved_actor_id is None:
        raise UnauthorizedReviewAction(
            f"{action.value!r} is a professional action and requires attributed "
            "actor_id identity evidence; an anonymous professional action fails closed "
            "to review",
            action=action.value,
        )
    return ValidatedReviewPrincipal(principal, role, resolved_actor_id)
