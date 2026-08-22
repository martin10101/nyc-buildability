#!/usr/bin/env python3
"""The S11.3 structured handoff: schema, validation, verification, export.

Split out of `rotation.py` (M0-T080) because a handoff SCHEMA and a rotation
PROTOCOL change for different reasons: the schema is a data contract the worker,
the reviewer, and the successor all read, while the protocol is when and how a
session may be replaced. `rotation.py` re-exports every name here, so
`rotation.Handoff`, `rotation.verify_handoff`, `rotation.RotationError` and the
rest keep working exactly as before (`docs/CODE_MODULARITY_POLICY.md` §6,
facade-preserving split).

Two refusals live here by construction: a handoff that automates an interactive
`/clear` (S11.3 requires a new explicitly identified session instead), and a
verification performed by `advisory_model` (S3.3 reserves this purpose).
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Mapping, Sequence

from .models import digest_of, to_utc_iso
from .policy import assert_advisory_allowed


class RotationError(Exception):
    """A rotation rule was violated. Always fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message



#: The S11.3 handoff schema, verbatim in order. Every field is REQUIRED; an
#: empty required field is an invalid handoff, not a tolerable omission.
HANDOFF_FIELDS: tuple[str, ...] = (
    "task_and_stage",
    "authoritative_shas",
    "branch",
    "worktree",
    "completed_work",
    "changed_files",
    "tests_and_ci",
    "pull_request_state",
    "reviews_and_findings",
    "open_blockers",
    "owner_gates",
    "forbidden_scope",
    "exact_next_action",
    "evidence_digests",
)

#: Fields that may legitimately be an empty COLLECTION (there may genuinely be no
#: blockers). They must still be present, and must still be the right type.
HANDOFF_MAY_BE_EMPTY: frozenset[str] = frozenset({
    "changed_files", "open_blockers", "reviews_and_findings", "owner_gates",
    "evidence_digests", "tests_and_ci",
})

#: S11.3: "Do not automate an interactive `/clear`."
_CLEAR_AUTOMATION = re.compile(r"(?<![\w/])/clear\b", re.IGNORECASE)


def assert_no_clear_automation(text: str, *, where: str) -> None:
    """Refuse any handoff or next-action text that automates `/clear` (S11.3)."""
    if _CLEAR_AUTOMATION.search(text or ""):
        raise RotationError(
            "clear_automation_forbidden",
            f"{where} tries to automate an interactive `/clear`; S11.3 requires a brand-new "
            f"explicitly identified session instead")


@dataclasses.dataclass(frozen=True)
class Handoff:
    """The structured handoff (S11.3 schema). Untrusted content, strict shape."""

    task_and_stage: str
    authoritative_shas: dict[str, str]
    branch: str
    worktree: str
    completed_work: str
    changed_files: tuple[str, ...]
    tests_and_ci: dict[str, Any]
    pull_request_state: str
    reviews_and_findings: tuple[str, ...]
    open_blockers: tuple[str, ...]
    owner_gates: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    exact_next_action: str
    evidence_digests: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        for key, value in list(data.items()):
            if isinstance(value, tuple):
                data[key] = list(value)
        return data

    def digest(self) -> str:
        return digest_of(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Handoff":
        if not isinstance(data, Mapping):
            raise RotationError("not_a_mapping", "a handoff must be a mapping")
        unknown = sorted(set(data) - set(HANDOFF_FIELDS))
        if unknown:
            raise RotationError("unknown_handoff_fields",
                                f"handoff carries unknown fields: {unknown}")
        missing = sorted(set(HANDOFF_FIELDS) - set(data))
        if missing:
            raise RotationError("incomplete_handoff",
                               f"handoff is missing required fields: {missing}")
        return cls(
            task_and_stage=str(data["task_and_stage"]),
            authoritative_shas=dict(data["authoritative_shas"] or {}),
            branch=str(data["branch"]),
            worktree=str(data["worktree"]),
            completed_work=str(data["completed_work"]),
            changed_files=tuple(data["changed_files"] or ()),
            tests_and_ci=dict(data["tests_and_ci"] or {}),
            pull_request_state=str(data["pull_request_state"]),
            reviews_and_findings=tuple(data["reviews_and_findings"] or ()),
            open_blockers=tuple(data["open_blockers"] or ()),
            owner_gates=tuple(data["owner_gates"] or ()),
            forbidden_scope=tuple(data["forbidden_scope"] or ()),
            exact_next_action=str(data["exact_next_action"]),
            evidence_digests=dict(data["evidence_digests"] or {}),
        )


def validate_handoff(handoff: Handoff) -> None:
    """Reject an incomplete or unusable handoff (S11.3, S15 'invalid handoff')."""
    for name in HANDOFF_FIELDS:
        value = getattr(handoff, name)
        if name in HANDOFF_MAY_BE_EMPTY:
            continue
        if isinstance(value, str) and not value.strip():
            raise RotationError("incomplete_handoff",
                                f"handoff field {name!r} is empty; a rotation may not proceed "
                                f"on a handoff that omits it")
        if isinstance(value, (dict, tuple)) and not value:
            raise RotationError("incomplete_handoff",
                                f"handoff field {name!r} is empty; a rotation may not proceed "
                                f"on a handoff that omits it")
    if "HEAD" not in handoff.authoritative_shas:
        raise RotationError("incomplete_handoff",
                            "authoritative_shas must name at least HEAD")
    assert_no_clear_automation(handoff.exact_next_action, where="handoff.exact_next_action")
    assert_no_clear_automation(handoff.completed_work, where="handoff.completed_work")


@dataclasses.dataclass(frozen=True)
class HandoffVerification:
    """The reviewer's verdict on a handoff, plus the model that produced it."""

    verified: bool
    model_used: str
    role: str
    reason_code: str
    reason: str
    handoff_digest: str = ""
    findings: tuple[str, ...] = ()


HANDOFF_VERIFICATION_PURPOSE = "handoff_verification"


def assert_review_model_used(*, role: str, model_used: str,
                             review_model: str, advisory_model: str = "") -> None:
    """S11.3/S3.3: handoff verification uses review_model, never advisory_model."""
    if role != "primary":
        raise RotationError(
            "advisory_model_forbidden",
            f"handoff verification ran in role {role!r}; S3.3 reserves final handoff "
            f"verification before autonomous continuation to review_model or deterministic "
            f"verification")
    if advisory_model and model_used == advisory_model and model_used != review_model:
        raise RotationError(
            "advisory_model_forbidden",
            f"handoff verification used the advisory model {model_used!r}; S3.3 forbids the "
            f"cheaper model for this purpose")
    if review_model and model_used != review_model:
        raise RotationError(
            "unexpected_verifier_model",
            f"handoff verification reported model {model_used!r} but the configured "
            f"review_model is {review_model!r}; the mismatch is never accepted silently")
    # Belt and braces: the policy engine's own refusal for this purpose.
    try:
        assert_advisory_allowed(HANDOFF_VERIFICATION_PURPOSE)
    except Exception:
        return  # Expected: the purpose is on the forbidden list. Nothing to do.
    raise RotationError(
        "advisory_purpose_not_protected",
        "handoff_verification is no longer on the advisory-forbidden list; refusing to "
        "verify a handoff under a weakened policy")


def verify_handoff(
    handoff: Handoff,
    *,
    reviewer_verdict: Mapping[str, Any],
    review_model: str,
    advisory_model: str = "",
    role: str = "primary",
) -> HandoffVerification:
    """Turn a fresh read-only reviewer's verdict into a durable verification.

    The supervisor - not the reviewer - decides what the verdict means, and the
    model identity is checked against the configured `review_model` before the
    verdict is honoured at all.
    """
    validate_handoff(handoff)
    model_used = str(reviewer_verdict.get("model_used", ""))
    assert_review_model_used(role=role, model_used=model_used,
                             review_model=review_model, advisory_model=advisory_model)

    reviewed_digest = str(reviewer_verdict.get("handoff_digest", ""))
    if reviewed_digest != handoff.digest():
        return HandoffVerification(
            False, model_used, role, "digest_mismatch",
            f"the reviewer verified a handoff whose digest ({reviewed_digest[:16]}...) is not "
            f"the one being rotated ({handoff.digest()[:16]}...)",
            handoff.digest())

    findings = tuple(str(f) for f in reviewer_verdict.get("findings", ()) or ())
    if not bool(reviewer_verdict.get("verified", False)) or findings:
        return HandoffVerification(
            False, model_used, role, "handoff_rejected",
            "the reviewer did not verify the handoff against live evidence",
            handoff.digest(), findings)
    return HandoffVerification(
        True, model_used, role, "handoff_verified",
        f"{model_used} verified the handoff against live evidence", handoff.digest())


def export_handoff_payload(handoff: Handoff, verification: HandoffVerification,
                           *, rotation_record_key: str,
                           evidence: Sequence[str] = ()) -> dict[str, Any]:
    """The bundle a fresh session receives (S11.3): handoff, packet refs, next action.

    The payload carries the supervisor-internal `rotation_record_key` so the
    successor's first checkpoint can be tied back to the rotation that produced
    it. It deliberately does NOT carry a "new session id": the successor's
    provider session identity does not exist until the provider issues it.
    """
    validate_handoff(handoff)
    assert_no_clear_automation(handoff.exact_next_action, where="exported next action")
    return {
        "rotation_record_key": rotation_record_key,
        "handoff": handoff.to_dict(),
        "handoff_digest": handoff.digest(),
        "verified_by_model": verification.model_used,
        "exact_next_authorized_action": handoff.exact_next_action,
        "evidence_refs": list(evidence),
        "required_first_response": "a structured READY checkpoint; no change before it",
        "exported_at_utc": to_utc_iso(),
    }
