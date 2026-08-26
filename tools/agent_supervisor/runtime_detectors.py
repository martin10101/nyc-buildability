"""No-progress, repeated-attempt, and scope-drift detection
(D-024 Phase C item 4, s6.2, M0-T091).

Progress is DURABLE EVIDENCE: a narrowed hypothesis, reproduced failure,
passing/failing regression test, reviewed design decision, bounded diff,
completed graph node, reconciled external effect, or verified checkpoint.
Text volume and tool activity alone are never progress (s6.2).

The monitor watches externally observable activity — repeated commands,
repeated hypotheses, cycling test failures, unbounded searches, successive
summaries with no new evidence, and writes outside the granted lease — and
raises controller-side findings that trigger landing/extension review
REGARDLESS of how many tokens the task has used. Low usage never buys an
unlimited investigation; high usage alone never condemns verified progress
(s5.4).

Every clock input is an injected ``at_minutes`` float, so a forty-minute
low-value investigation is detectable in accelerated test time (s16.2).
Findings are controller records: they carry no worker-visible text, no
countdown, and no counter addressed to the worker (D-024-R045). The outside
controller decides; the worker is never told to ration itself.

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses

from .subagent_contracts import DetectorPolicy, _normalize_lease_path


class DetectorError(ValueError):
    """Typed error for runtime detection (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


#: The s6.2 durable-evidence vocabulary — the ONLY events that count as
#: progress and reset the no-progress window.
DURABLE_EVIDENCE_KINDS: tuple[str, ...] = (
    "narrowed-hypothesis",
    "reproduced-failure",
    "regression-test",
    "reviewed-design-decision",
    "bounded-diff",
    "completed-graph-node",
    "reconciled-external-effect",
    "verified-checkpoint",
)

#: Observable activity kinds (closed set).
EVENT_KINDS: tuple[str, ...] = (
    "command", "hypothesis", "test-run", "search", "summary", "file-write",
    "evidence")

#: Finding kinds (closed set) and what each requires of the controller.
FINDING_REPEATED = "repeated-attempts"
FINDING_CYCLING_TESTS = "cycling-test-failures"
FINDING_NO_PROGRESS = "no-progress"
FINDING_UNBOUNDED_SEARCH = "unbounded-search"
FINDING_STALLED_SUMMARIES = "stalled-summaries"
FINDING_SCOPE_DRIFT = "scope-drift"
FINDING_KINDS: tuple[str, ...] = (
    FINDING_REPEATED, FINDING_CYCLING_TESTS, FINDING_NO_PROGRESS,
    FINDING_UNBOUNDED_SEARCH, FINDING_STALLED_SUMMARIES,
    FINDING_SCOPE_DRIFT)

REQUIRES_EXTENSION_REVIEW = "extension-review"
REQUIRES_LANDING_REVIEW = "landing-review"

#: Scope drift produces an extension request, not silent continuation
#: (s16.2); the exhaustion-shaped findings go to landing review.
_FINDING_REQUIRES: dict[str, str] = {
    FINDING_REPEATED: REQUIRES_LANDING_REVIEW,
    FINDING_CYCLING_TESTS: REQUIRES_LANDING_REVIEW,
    FINDING_NO_PROGRESS: REQUIRES_LANDING_REVIEW,
    FINDING_UNBOUNDED_SEARCH: REQUIRES_LANDING_REVIEW,
    FINDING_STALLED_SUMMARIES: REQUIRES_LANDING_REVIEW,
    FINDING_SCOPE_DRIFT: REQUIRES_EXTENSION_REVIEW,
}


@dataclasses.dataclass(frozen=True)
class ActivityEvent:
    """One externally observed activity, on the injected clock.

    ``signature`` is the normalized identity used for repetition detection
    (a command line, a hypothesis statement, a test id, a search query).
    Only ``kind="evidence"`` events carry an ``evidence_kind``.
    """

    at_minutes: float
    kind: str
    signature: str
    evidence_kind: str | None = None
    outcome: str = ""
    paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.at_minutes < 0:
            raise DetectorError("bad_clock",
                                "at_minutes may not be negative")
        if self.kind not in EVENT_KINDS:
            raise DetectorError(
                "bad_event_kind",
                f"event kind {self.kind!r} is not in {list(EVENT_KINDS)}")
        if not self.signature.strip():
            raise DetectorError("missing_signature",
                                "every event needs a normalized signature")
        if self.kind == "evidence":
            if self.evidence_kind not in DURABLE_EVIDENCE_KINDS:
                raise DetectorError(
                    "bad_evidence_kind",
                    f"evidence kind {self.evidence_kind!r} is not durable "
                    f"evidence; the closed set is "
                    f"{list(DURABLE_EVIDENCE_KINDS)} (s6.2)")
        elif self.evidence_kind is not None:
            raise DetectorError(
                "bad_evidence_kind",
                f"a {self.kind!r} event never carries an evidence_kind; "
                f"activity alone is not progress (s6.2)")


@dataclasses.dataclass(frozen=True)
class DetectorFinding:
    """A controller-side finding. Contains NO worker-visible text: the
    controller routes it to landing/extension review; the worker never sees
    a counter or countdown (D-024-R045)."""

    assignment_id: str
    kind: str
    detail: str
    at_minutes: float
    requires: str

    def __post_init__(self) -> None:
        if self.kind not in FINDING_KINDS:
            raise DetectorError("bad_finding_kind",
                                f"unknown finding kind {self.kind!r}")
        if self.requires not in (REQUIRES_EXTENSION_REVIEW,
                                 REQUIRES_LANDING_REVIEW):
            raise DetectorError("bad_requires",
                                f"unknown requirement {self.requires!r}")


class AssignmentMonitor:
    """Per-assignment activity monitor on an injected clock.

    Fires each finding kind once per dry spell; durable evidence resets the
    window and the repetition counters (a worker that produced evidence is
    making progress by definition, s6.2). ``check(at_minutes)`` supports
    clock ticks without any event — silence is also a no-progress signal.
    """

    def __init__(self, assignment_id: str, policy: DetectorPolicy,
                 *, lease_paths: tuple[str, ...] = (),
                 started_at_minutes: float = 0.0) -> None:
        if not assignment_id:
            raise DetectorError("missing_ids",
                                "monitor requires assignment_id")
        self._assignment_id = assignment_id
        self._policy = policy
        self._lease = tuple(_normalize_lease_path(p) for p in lease_paths)
        self._last_evidence_at = started_at_minutes
        self._signature_counts: dict[tuple[str, str], int] = {}
        self._failed_tests: dict[str, int] = {}
        self._searches_since_evidence = 0
        self._summaries_since_evidence = 0
        self._fired: set[str] = set()

    def _finding(self, kind: str, detail: str,
                 at_minutes: float) -> DetectorFinding | None:
        if kind in self._fired:
            return None
        self._fired.add(kind)
        return DetectorFinding(
            assignment_id=self._assignment_id, kind=kind, detail=detail,
            at_minutes=at_minutes, requires=_FINDING_REQUIRES[kind])

    def _reset_on_evidence(self, at_minutes: float) -> None:
        self._last_evidence_at = at_minutes
        self._signature_counts.clear()
        self._failed_tests.clear()
        self._searches_since_evidence = 0
        self._summaries_since_evidence = 0
        self._fired.discard(FINDING_NO_PROGRESS)
        self._fired.discard(FINDING_UNBOUNDED_SEARCH)
        self._fired.discard(FINDING_STALLED_SUMMARIES)
        self._fired.discard(FINDING_REPEATED)
        self._fired.discard(FINDING_CYCLING_TESTS)

    def check(self, at_minutes: float) -> tuple[DetectorFinding, ...]:
        """Evaluate the no-progress window at a bare clock tick."""
        found: list[DetectorFinding] = []
        window = self._policy.no_progress_window_minutes
        if at_minutes - self._last_evidence_at >= window:
            finding = self._finding(
                FINDING_NO_PROGRESS,
                f"no durable evidence since minute "
                f"{self._last_evidence_at:g}; text volume and tool "
                f"activity alone are not progress (s6.2)", at_minutes)
            if finding:
                found.append(finding)
        return tuple(found)

    def observe(self, event: ActivityEvent) -> tuple[DetectorFinding, ...]:
        """Feed one observed activity; return any NEW findings."""
        found: list[DetectorFinding] = []
        limit = self._policy.repeated_attempt_limit
        if event.kind == "evidence":
            self._reset_on_evidence(event.at_minutes)
            return ()
        if event.kind in ("command", "hypothesis"):
            key = (event.kind, event.signature)
            self._signature_counts[key] = self._signature_counts.get(key, 0) + 1
            if self._signature_counts[key] >= limit:
                finding = self._finding(
                    FINDING_REPEATED,
                    f"{event.kind} {event.signature!r} repeated "
                    f"{self._signature_counts[key]} times without new "
                    f"durable evidence", event.at_minutes)
                if finding:
                    found.append(finding)
        elif event.kind == "test-run" and event.outcome == "failed":
            self._failed_tests[event.signature] = \
                self._failed_tests.get(event.signature, 0) + 1
            if self._failed_tests[event.signature] >= limit:
                finding = self._finding(
                    FINDING_CYCLING_TESTS,
                    f"test {event.signature!r} failed "
                    f"{self._failed_tests[event.signature]} times in a "
                    f"cycle", event.at_minutes)
                if finding:
                    found.append(finding)
        elif event.kind == "search":
            self._searches_since_evidence += 1
            if self._searches_since_evidence >= limit:
                finding = self._finding(
                    FINDING_UNBOUNDED_SEARCH,
                    f"{self._searches_since_evidence} searches with no "
                    f"durable evidence between them", event.at_minutes)
                if finding:
                    found.append(finding)
        elif event.kind == "summary":
            self._summaries_since_evidence += 1
            if self._summaries_since_evidence >= 2:
                finding = self._finding(
                    FINDING_STALLED_SUMMARIES,
                    f"{self._summaries_since_evidence} successive summaries "
                    f"with no new evidence", event.at_minutes)
                if finding:
                    found.append(finding)
        if event.kind == "file-write" \
                and self._policy.scope_drift_outside_lease and self._lease:
            for path in event.paths:
                normalized = _normalize_lease_path(path)
                inside = any(normalized == held
                             or normalized.startswith(held + "/")
                             for held in self._lease)
                if not inside:
                    finding = self._finding(
                        FINDING_SCOPE_DRIFT,
                        f"write to {path!r} is outside the granted lease; "
                        f"scope drift requires an extension request, never "
                        f"silent continuation (s6, s16.2)",
                        event.at_minutes)
                    if finding:
                        found.append(finding)
                    break
        found.extend(self.check(event.at_minutes))
        return tuple(found)
