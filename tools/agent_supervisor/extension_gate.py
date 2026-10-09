"""The s6.1 extension gate at runtime (D-024 Phase C item 4, M0-T091).

A subagent may not silently expand scope or extend itself indefinitely. At a
contract boundary it returns the s6.1 items — what is proven, what remains
uncertain, why the extra work blocks the current acceptance criterion, the
least costly next experiment, the additional scope with its LIKELY EVIDENCE
SOURCES and natural completion point, resume-vs-new coherence, consequences
of stopping, and a durable partial checkpoint if anything changed. The
read-only Codex supervisor then approves or denies ONLY that bounded
extension — by producing a decision RECORD, never by editing code.

Default: a discovery is deferred into the task graph/backlog unless it
blocks correctness, security, data integrity, or the current acceptance
criterion. "I found another problem" is not an unlimited renewal (s6); an
approval grants exactly one bounded addition with a named completion point.
This is how the system prevents an agent from spending forty minutes
investigating something merely interesting — combined with the
``runtime_detectors`` no-progress findings, a low-value investigation is
denied or landed in accelerated time (s16.2).

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses

from .runtime_detectors import DetectorFinding


class ExtensionError(ValueError):
    """Typed error for the extension gate (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


#: The ONLY discovery classes that justify extending instead of deferring
#: (s6.1). Everything else defaults to the backlog.
BLOCKING_KINDS: tuple[str, ...] = (
    "correctness", "security", "data-integrity",
    "current-acceptance-criterion")
NON_BLOCKING = "none"

RESUME_THIS_CONTEXT = "resume-this-context"
NEW_BOUNDED_UNIT = "new-bounded-unit"
RESUME_CHOICES: tuple[str, ...] = (RESUME_THIS_CONTEXT, NEW_BOUNDED_UNIT)

DECISION_APPROVE = "approve-bounded"
DECISION_DENY_BACKLOG = "deny-defer-to-backlog"
DECISIONS: tuple[str, ...] = (DECISION_APPROVE, DECISION_DENY_BACKLOG)


@dataclasses.dataclass(frozen=True)
class ExtensionRequest:
    """The s6.1 return items, validated fail-closed — a request missing an
    item is not reviewable and is refused outright."""

    assignment_id: str
    proven: str
    uncertain: str
    why_blocking: str
    least_costly_next_experiment: str
    additional_scope: str
    likely_evidence_sources: tuple[str, ...]
    natural_completion_point: str
    resume_vs_new: str
    consequences_of_stopping: str
    blocking_kind: str = NON_BLOCKING
    changed_anything: bool = False
    partial_checkpoint_ref: str = ""

    def __post_init__(self) -> None:
        required = (
            ("proven", self.proven),
            ("uncertain", self.uncertain),
            ("why_blocking", self.why_blocking),
            ("least_costly_next_experiment",
             self.least_costly_next_experiment),
            ("additional_scope", self.additional_scope),
            ("natural_completion_point", self.natural_completion_point),
            ("consequences_of_stopping", self.consequences_of_stopping),
        )
        if not self.assignment_id:
            raise ExtensionError("missing_ids",
                                 "extension request needs assignment_id")
        for name, value in required:
            if not value.strip():
                raise ExtensionError(
                    "incomplete_request",
                    f"s6.1 item {name!r} is empty; an extension request "
                    f"must carry every return item (D-024 s6.1)")
        if not self.likely_evidence_sources \
                or not all(s.strip() for s in self.likely_evidence_sources):
            raise ExtensionError(
                "incomplete_request",
                "s6.1 requires the LIKELY EVIDENCE SOURCES of the "
                "additional scope (D-024-R063)")
        if self.resume_vs_new not in RESUME_CHOICES:
            raise ExtensionError(
                "bad_resume_choice",
                f"resume_vs_new must be one of {list(RESUME_CHOICES)}")
        if self.blocking_kind != NON_BLOCKING \
                and self.blocking_kind not in BLOCKING_KINDS:
            raise ExtensionError(
                "bad_blocking_kind",
                f"blocking_kind {self.blocking_kind!r} is not in "
                f"{list(BLOCKING_KINDS)} (or {NON_BLOCKING!r})")
        if self.changed_anything and not self.partial_checkpoint_ref.strip():
            raise ExtensionError(
                "missing_checkpoint",
                "a request that changed anything must reference its durable "
                "partial checkpoint (s6.1)")


@dataclasses.dataclass(frozen=True)
class ExtensionDecision:
    """The supervisor's record. It has no apply/execute surface by design:
    Codex approves or denies WITHOUT editing code (s16.2); the controller
    enforces the decision through the ordinary contract machinery."""

    assignment_id: str
    decision: str
    reasons: tuple[str, ...]
    bounded_addition: str = ""
    completion_point: str = ""

    def __post_init__(self) -> None:
        if self.decision not in DECISIONS:
            raise ExtensionError("bad_decision",
                                 f"unknown decision {self.decision!r}")
        if self.decision == DECISION_APPROVE:
            if not self.bounded_addition.strip() \
                    or not self.completion_point.strip():
                raise ExtensionError(
                    "unbounded_approval",
                    "an approval names exactly ONE bounded addition and its "
                    "natural completion point; open-ended renewals are "
                    "never granted (s6.1)")


@dataclasses.dataclass(frozen=True)
class BacklogEntry:
    """A deferred discovery: the task-graph/backlog default (s6.1)."""

    assignment_id: str
    summary: str
    created_from: str
    at_minutes: float

    def __post_init__(self) -> None:
        if self.created_from not in ("unrelated-discovery",
                                     "denied-extension"):
            raise ExtensionError(
                "bad_backlog_source",
                f"unknown backlog source {self.created_from!r}")
        if not self.summary.strip():
            raise ExtensionError("missing_summary",
                                 "a backlog entry needs a summary")


def decide_extension(request: ExtensionRequest,
                     *,
                     findings: tuple[DetectorFinding, ...] = (),
                     at_minutes: float = 0.0,
                     ) -> tuple[ExtensionDecision, BacklogEntry | None]:
    """Approve or deny ONE bounded extension (s6.1 default: defer).

    A non-blocking request is denied and deferred to the backlog — this is
    the forty-minute-investigation stop. A blocking request is approved for
    the LEAST COSTLY next experiment only, bounded by the request's own
    natural completion point; standing no-progress findings are recorded in
    the reasons so later calibration can learn from the decision (s5.5).
    """
    reason_list = [f"blocking_kind={request.blocking_kind}"]
    for finding in findings:
        reason_list.append(
            f"standing finding {finding.kind} at minute "
            f"{finding.at_minutes:g}")
    if request.blocking_kind == NON_BLOCKING:
        reason_list.append(
            "discovery does not block correctness, security, data "
            "integrity, or the current acceptance criterion - deferred to "
            "the backlog by default (s6.1)")
        decision = ExtensionDecision(
            assignment_id=request.assignment_id,
            decision=DECISION_DENY_BACKLOG,
            reasons=tuple(reason_list))
        entry = BacklogEntry(
            assignment_id=request.assignment_id,
            summary=request.additional_scope,
            created_from="denied-extension",
            at_minutes=at_minutes)
        return decision, entry
    reason_list.append(
        "blocking discovery - approve the least costly bounded experiment "
        "only; not an unlimited renewal (s6.1)")
    decision = ExtensionDecision(
        assignment_id=request.assignment_id,
        decision=DECISION_APPROVE,
        reasons=tuple(reason_list),
        bounded_addition=request.least_costly_next_experiment,
        completion_point=request.natural_completion_point)
    return decision, None


def backlog_unrelated_discovery(assignment_id: str, summary: str,
                                *, at_minutes: float = 0.0) -> BacklogEntry:
    """Record an unrelated discovery straight to the backlog (s16.2)."""
    return BacklogEntry(
        assignment_id=assignment_id, summary=summary,
        created_from="unrelated-discovery", at_minutes=at_minutes)
