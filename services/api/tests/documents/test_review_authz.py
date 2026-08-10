"""Authorization matrix for the survey review-action slice (M2-T016, SC-S3/SC-S4).

Adversarial, parameterized coverage of docs/SURVEY_REVIEW_WORKFLOW.md sections 5.1-5.3:
every action is authorized fail-closed server-side; the professional-confirmation and
document-decision actions are the designated professional role ONLY; no AI/model/agent/
service/system principal — and no unknown, empty, or non-string principal — can perform
any action; professional actions require attributed identity. The principal kind is the
CHANNEL-authenticated classification, never a payload claim.
"""

from __future__ import annotations

import pytest

from app.documents.correction_history import CorrectingActorRole, CorrectingPrincipal
from app.documents.review_authz import (
    ACTION_ALLOWED_ROLES,
    ReviewAction,
    UnauthorizedReviewAction,
    authorize_review_action,
)

USER = CorrectingPrincipal.HUMAN_USER.value
PRO = CorrectingPrincipal.HUMAN_QUALIFIED_PROFESSIONAL.value

# Actions any authorized human may perform, and the professional-only actions.
_HUMAN_OPEN = [ReviewAction.READ, ReviewAction.ACCEPT_FACT, ReviewAction.CORRECT_FACT]
_PROFESSIONAL_ONLY = [
    ReviewAction.REJECT_FACT,
    ReviewAction.CONFIRM_DOCUMENT,
    ReviewAction.REJECT_DOCUMENT,
    ReviewAction.REOPEN_DOCUMENT,
]


def test_every_review_action_has_an_authorization_row():
    assert frozenset(ACTION_ALLOWED_ROLES) == frozenset(ReviewAction)
    for allowed in ACTION_ALLOWED_ROLES.values():
        assert allowed  # no empty (fail-open) row
        assert allowed <= frozenset(CorrectingActorRole)


@pytest.mark.parametrize("action", list(ReviewAction))
def test_professional_may_perform_every_action(action):
    principal = authorize_review_action(action, PRO, "pls-12345")
    assert principal.is_professional
    assert principal.role is CorrectingActorRole.QUALIFIED_PROFESSIONAL
    assert principal.actor_id == "pls-12345"


@pytest.mark.parametrize("action", _HUMAN_OPEN)
def test_user_may_perform_open_actions(action):
    principal = authorize_review_action(action, USER, "analyst-1")
    assert not principal.is_professional
    assert principal.role is CorrectingActorRole.USER


@pytest.mark.parametrize("action", _HUMAN_OPEN)
def test_user_open_actions_do_not_require_actor_id(action):
    # Identity is B-001-blocked at the wire for the user role; open actions still resolve.
    principal = authorize_review_action(action, USER, None)
    assert principal.actor_id is None


@pytest.mark.parametrize("action", _PROFESSIONAL_ONLY)
def test_user_is_refused_professional_only_actions(action):
    with pytest.raises(UnauthorizedReviewAction) as exc:
        authorize_review_action(action, USER, "analyst-1")
    assert exc.value.reject_code == "unauthorized_review_action"


@pytest.mark.parametrize("action", _PROFESSIONAL_ONLY)
def test_professional_only_actions_require_attributed_identity(action):
    with pytest.raises(UnauthorizedReviewAction):
        authorize_review_action(action, PRO, None)


# Any principal string outside the closed human model — an AI/model/agent/service/system
# label, an unknown role, an empty string, or a non-string — is refused for EVERY action.
@pytest.mark.parametrize(
    "bad_principal",
    [
        "ai",
        "ai_assisted_classification",
        "model",
        "agent",
        "service",
        "system",
        "deterministic_pipeline",
        "qualified_professional",  # a ROLE string is not a PRINCIPAL kind
        "",
        "   ",
        None,
        123,
        object(),
    ],
)
@pytest.mark.parametrize("action", list(ReviewAction))
def test_non_human_or_unknown_principal_is_refused_everywhere(action, bad_principal):
    with pytest.raises(UnauthorizedReviewAction):
        authorize_review_action(action, bad_principal, "id-1")


@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_actor_id_is_refused(blank):
    with pytest.raises(UnauthorizedReviewAction):
        authorize_review_action(ReviewAction.ACCEPT_FACT, USER, blank)


def test_action_must_be_a_review_action_member():
    with pytest.raises(UnauthorizedReviewAction):
        authorize_review_action("accept_fact", USER, "analyst-1")  # type: ignore[arg-type]


def test_no_automated_principal_member_exists():
    # Structural: the closed principal model has ONLY human members.
    assert {m.value for m in CorrectingPrincipal} == {
        "human_user",
        "human_qualified_professional",
    }
