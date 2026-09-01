#!/usr/bin/env python3
"""MRL ReviewVerdict contract + controller-authoritative, git-bound CodexDecision
(M0-T134 / D-024 Amendment 39 R502/R503/R504/R505; C9).

Trust boundary (owner correction E): Codex returns ONLY an untrusted
``ReviewVerdict`` - a verdict enum, a bounded rationale, and references to
CONTROLLER-ISSUED evidence ids, and nothing else. The controller alone constructs
the authoritative ``CodexDecision`` and binds the git identity (normalized remote
URL, expected base ref, freshly observed base SHA, task branch, task HEAD SHA,
observation timestamp).

Two invariants the owner named explicitly:

* Option-B neutral (R505): the base ref is always data, never a hard-coded
  ``origin/main``; the legacy ``verified_origin_main`` field is never referenced or
  repurposed here.
* APPROVE is only an opinion (R504): ``decision == "COMPLETE"`` is produced ONLY
  when the reviewer APPROVED *and* every controller invariant and gate passed.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Iterable, Mapping

from .mrl_remote import RemoteObservation
from .mrl_worker_result import ContractError, load_schema, validate_instance

_SHA40 = re.compile(r"^[0-9a-f]{40}$")

#: The controller's decision space. COMPLETE is the only one that advances; HOLD is
#: "reviewer approved but the controller is not satisfied" (R504).
DECISIONS = ("COMPLETE", "REVISE", "HALT", "HOLD")


@dataclasses.dataclass(frozen=True)
class ReviewVerdict:
    """The untrusted MRL reviewer return. Exactly three fields; nothing factual."""

    verdict: str
    rationale: str
    evidence_ref_ids: tuple[str, ...]

    @classmethod
    def from_provider(cls, raw: Any, *, issued_evidence_ids: Iterable[str]) -> "ReviewVerdict":
        """Validate a raw provider payload and bind it to controller-issued evidence.

        Fail-closed on any schema violation (unknown field, wrong type, bad enum,
        length, duplicate id) AND on any evidence_ref_id the controller did not
        issue for this review (R502).
        """
        if not isinstance(raw, Mapping):
            raise ContractError("contract_violation",
                                f"ReviewVerdict must be a JSON object, got {type(raw).__name__}")
        validate_instance(dict(raw), load_schema("review_verdict.schema.json"), "review_verdict")
        ids = list(raw["evidence_ref_ids"])
        issued = set(issued_evidence_ids)
        unknown = [i for i in ids if i not in issued]
        if unknown:
            raise ContractError(
                "contract_violation",
                f"evidence_ref_ids {unknown} were not issued by the controller for this "
                f"review (R502); a reviewer may only cite controller-issued ids")
        return cls(raw["verdict"], raw["rationale"], tuple(ids))


@dataclasses.dataclass(frozen=True)
class GitBinding:
    """The controller-observed git identity bound into a decision (Option-B neutral)."""

    normalized_remote_url: str
    expected_base_ref: str
    observed_base_sha: str
    task_branch: str
    task_head_sha: str
    observed_at_utc: str


def git_binding_from_observation(
    observation: RemoteObservation, *, task_branch: str, task_head_sha: str
) -> GitBinding:
    """Build a GitBinding from a fresh RemoteObservation plus the task branch/HEAD."""
    return GitBinding(
        normalized_remote_url=observation.normalized_remote_url,
        expected_base_ref=observation.base_ref,
        observed_base_sha=observation.base_sha,
        task_branch=task_branch,
        task_head_sha=task_head_sha,
        observed_at_utc=observation.observed_at_utc,
    )


@dataclasses.dataclass(frozen=True)
class CodexDecision:
    """The controller-authoritative, git-bound decision (see module docstring)."""

    decision: str
    verdict: str
    rationale: str
    evidence_ref_ids: tuple[str, ...]
    git: GitBinding
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "verdict": self.verdict,
            "rationale": self.rationale,
            "evidence_ref_ids": list(self.evidence_ref_ids),
            "git": {
                "normalized_remote_url": self.git.normalized_remote_url,
                "expected_base_ref": self.git.expected_base_ref,
                "observed_base_sha": self.git.observed_base_sha,
                "task_branch": self.git.task_branch,
                "task_head_sha": self.git.task_head_sha,
                "observed_at_utc": self.git.observed_at_utc,
            },
            "reason": self.reason,
        }


def _validate_git_binding(git: GitBinding) -> None:
    for name, value in (("normalized_remote_url", git.normalized_remote_url),
                        ("expected_base_ref", git.expected_base_ref),
                        ("task_branch", git.task_branch),
                        ("observed_at_utc", git.observed_at_utc)):
        if not isinstance(value, str) or not value.strip():
            raise ContractError("contract_violation", f"git binding {name} is required (fail closed)")
    for name, value in (("observed_base_sha", git.observed_base_sha),
                        ("task_head_sha", git.task_head_sha)):
        if not isinstance(value, str) or not _SHA40.match(value.lower()):
            raise ContractError("contract_violation",
                                f"git binding {name} must be a 40-hex sha (got {value!r}); fail closed")


def build_codex_decision(
    review_verdict: ReviewVerdict,
    git: GitBinding,
    *,
    invariants_ok: bool,
    gates_ok: bool,
    reason: str = "",
) -> CodexDecision:
    """Construct the controller-authoritative decision from an untrusted verdict.

    R504: APPROVE alone never produces COMPLETE - COMPLETE requires APPROVE AND
    invariants_ok AND gates_ok; an APPROVE with an unmet controller gate becomes
    HOLD. R505: the git binding is validated (well-formed SHAs, present ref/url);
    a malformed or missing binding fails closed.
    """
    if not isinstance(review_verdict, ReviewVerdict):
        raise ContractError("contract_violation", "review_verdict must be a ReviewVerdict")
    _validate_git_binding(git)
    verdict = review_verdict.verdict
    if verdict == "HALT":
        decision = "HALT"
    elif verdict == "REVISE":
        decision = "REVISE"
    elif verdict == "APPROVE":
        # Strict `is True` (not mere truthiness): a controller flag that is a truthy
        # non-bool must NOT be able to produce COMPLETE - fail closed to HOLD.
        decision = "COMPLETE" if (invariants_ok is True and gates_ok is True) else "HOLD"
    else:  # pragma: no cover - from_provider already constrains the enum
        raise ContractError("contract_violation", f"unknown verdict {verdict!r}")

    if not reason:
        if decision == "COMPLETE":
            reason = "reviewer APPROVED and every controller invariant and gate passed"
        elif decision == "HOLD":
            reason = (f"reviewer APPROVED but a controller check is unmet "
                      f"(invariants_ok={invariants_ok}, gates_ok={gates_ok}); "
                      f"COMPLETE withheld (R504)")
        elif decision == "REVISE":
            reason = "reviewer requested revision"
        else:
            reason = "reviewer halted the loop"

    decision_obj = CodexDecision(
        decision=decision,
        verdict=verdict,
        rationale=review_verdict.rationale,
        evidence_ref_ids=review_verdict.evidence_ref_ids,
        git=git,
        reason=reason,
    )
    validate_instance(decision_obj.as_dict(),
                      load_schema("mrl_codex_decision.schema.json"), "codex_decision")
    return decision_obj
