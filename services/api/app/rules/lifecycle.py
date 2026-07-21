"""Rule lifecycle (PRD section 10 rule lifecycle; owner directive 2026-07-20 item 5).

The lifecycle is deterministic and its ``published``/``verified`` terminus is
reachable ONLY through a recorded G6 qualified-human approval event - never by
any agent, and never by the evaluator. This mirrors the project-control gate
discipline: a worker (or the engine) may prepare and draft, but only a qualified
human publishes a legal rule.

    discovered -> extracted_draft -> needs_review -> (G6 human) -> published

Agent-settable transitions stop at ``needs_review``. ``published`` requires a
``G6Approval`` record carrying a qualified reviewer identity and an approval
timestamp; :func:`publish` refuses without one. There is no code path anywhere
in this package that sets ``published`` without such a record.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Rule statuses ---------------------------------------------------------
STATUS_DISCOVERED = "discovered"
STATUS_EXTRACTED_DRAFT = "extracted_draft"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_PUBLISHED = "published"

RULE_STATUSES = (
    STATUS_DISCOVERED,
    STATUS_EXTRACTED_DRAFT,
    STATUS_NEEDS_REVIEW,
    STATUS_PUBLISHED,
)

# Statuses an agent / the engine may author. ``published`` is deliberately
# excluded (owner directive item 5: no AI-published or auto-"Verified" rule).
AGENT_AUTHORABLE_STATUSES = frozenset(
    {STATUS_DISCOVERED, STATUS_EXTRACTED_DRAFT, STATUS_NEEDS_REVIEW}
)

# Only a published rule may ever produce a ``verified`` coverage result, and
# only when its G6 approval is attached at evaluation time.
_TRANSITIONS = {
    STATUS_DISCOVERED: {STATUS_EXTRACTED_DRAFT},
    STATUS_EXTRACTED_DRAFT: {STATUS_NEEDS_REVIEW},
    STATUS_NEEDS_REVIEW: {STATUS_PUBLISHED},
    STATUS_PUBLISHED: set(),
}


class LifecycleError(RuntimeError):
    """Raised on an illegal lifecycle transition or an unauthorized publish."""


@dataclass(frozen=True)
class G6Approval:
    """A recorded qualified-human legal-approval event (PRD G6). This is the
    ONLY key that unlocks ``published`` and, downstream, a ``verified`` coverage
    label. It is produced by a human process outside this engine and outside any
    agent's authority; the engine only *consumes* it."""

    rule_id: str
    rule_version: str
    reviewer: str  # qualified zoning professional identity (human)
    approved_at: str  # ISO-8601, supplied by the human approval process
    approval_ref: str  # pointer to the recorded approval evidence


def can_transition(current: str, target: str) -> bool:
    return target in _TRANSITIONS.get(current, set())


def assert_agent_authorable(status: str) -> None:
    """Guard used by the DSL loader: a rule file an agent authored/loaded may
    not declare a status beyond ``needs_review``."""
    if status not in RULE_STATUSES:
        raise LifecycleError(f"unknown rule status {status!r}")
    if status not in AGENT_AUTHORABLE_STATUSES:
        raise LifecycleError(
            f"status {status!r} is not agent-authorable; the engine and agents "
            f"may author only {sorted(AGENT_AUTHORABLE_STATUSES)}. "
            f"'{STATUS_PUBLISHED}' requires a recorded G6 qualified-human approval."
        )


def transition(current: str, target: str) -> str:
    if not can_transition(current, target):
        raise LifecycleError(f"illegal lifecycle transition {current!r} -> {target!r}")
    if target == STATUS_PUBLISHED:
        raise LifecycleError(
            "publish() must be used to reach 'published'; it requires a G6Approval."
        )
    return target


def publish(current: str, approval: G6Approval | None) -> str:
    """Reach ``published`` ONLY with a G6 approval record. No approval -> refuse."""
    if approval is None:
        raise LifecycleError(
            "cannot publish a rule without a recorded G6 qualified-human approval "
            "(owner directive item 5: no AI-published or automatically Verified rule)."
        )
    if not can_transition(current, STATUS_PUBLISHED):
        raise LifecycleError(
            f"illegal transition {current!r} -> {STATUS_PUBLISHED!r}; a rule must be "
            f"'{STATUS_NEEDS_REVIEW}' before publication."
        )
    return STATUS_PUBLISHED
