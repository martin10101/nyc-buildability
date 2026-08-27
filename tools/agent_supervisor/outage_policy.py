"""Provider/supervisor outage handling: bounded backoff, blocked-with-handoff,
bounded idle (D-024 Phase D, M0-T092; R033).

R033, in full: a TRANSIENT Codex transport/model/network/rate-limit failure
enters bounded backoff with jitter and durable retry state — never a busy
loop, never unlimited — and never dispatches new producer work without
supervision; the current atomic producer operation may land only under
pre-authorized deterministic rules, after which the campaign holds until the
supervisor returns. An AUTHENTICATION, BILLING, REVOKED-ACCESS, or
INCOMPATIBILITY failure is not retried: it enters blocked-with-handoff. No
eligible authorized work enters BOUNDED idle.

What already existed (R018 prove-first):

* ``resume_scheduler`` owns PROVIDER USAGE-LIMIT deadlines (a parseable reset
  time -> a durable OS wake trigger). That is a different thing from a
  transport outage: a limit notice carries its own deadline; an outage does
  not, which is exactly why R033 demands *backoff with jitter* here.
* ``codex_reviewer.provider_failure_reason`` extracts a BOUNDED, REDACTED
  failure string from the reviewer's event stream — it is this module's input,
  not its policy.
* ``circuit_breakers`` counts failures per run and pauses; it neither
  classifies causes nor schedules a retry.

Everything here is deterministic with injected time (POSIX epoch seconds) and
an injected rng, so tests never sleep and never touch a provider. The module
records and answers; it never dispatches, retries, or contacts anything.
The state machine nodes this policy drives — ``CODEX_OUTAGE_BACKOFF`` and
``NO_ELIGIBLE_WORK`` — are added by this same unit (R029/R033).

Supervisor-freeze qualifying evidence: D-024-R102.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Mapping

from .models import to_utc_iso

#: The two R033 failure classes. There is no third: an UNRECOGNIZED cause is
#: classified BLOCKING (fail closed) — an unknown failure retried forever is
#: exactly the unlimited loop R033 prohibits.
TRANSIENT = "transient"
BLOCKING = "blocking"

#: Closed cause vocabulary (R033's own list, verbatim where it names one).
TRANSIENT_CAUSES: tuple[str, ...] = (
    "rate_limit", "network", "timeout", "transport", "server_error",
    "provider_overload",
)
BLOCKING_CAUSES: tuple[str, ...] = (
    "auth", "billing", "revoked_access", "incompatibility",
)

#: Keyword maps for classifying a bounded provider-failure reason string
#: (``codex_reviewer.provider_failure_reason`` output). BLOCKING keywords are
#: scanned FIRST (M0-T092 correction F1, G3/G5 LOW-1): a mixed reason like
#: "authentication failed: connection reset" must classify BLOCKING — R033
#: never grants auth/billing/revoked/incompatibility a retry loop, so
#: ambiguity resolves toward the hold, matching the module's own
#: unknown-fails-closed stance. Matching is a convenience — a caller that
#: KNOWS the cause passes it directly to :func:`classify_cause` and never
#: sniffs text.
_BLOCKING_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("unauthorized", "auth"), ("401", "auth"), ("403", "auth"),
    ("credential", "auth"), ("api key", "auth"), ("authentication", "auth"),
    ("billing", "billing"), ("payment", "billing"),
    ("revoked", "revoked_access"),
    ("incompatib", "incompatibility"), ("unsupported version", "incompatibility"),
)
_TRANSIENT_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("rate limit", "rate_limit"), ("429", "rate_limit"),
    ("timed out", "timeout"), ("timeout", "timeout"),
    ("connection", "network"), ("network", "network"), ("dns", "network"),
    ("unreachable", "network"),
    ("overloaded", "provider_overload"), ("529", "provider_overload"),
    ("500", "server_error"), ("502", "server_error"), ("503", "server_error"),
    ("server error", "server_error"),
)
_REASON_KEYWORDS: tuple[tuple[str, str], ...] = (
    *_BLOCKING_KEYWORDS, *_TRANSIENT_KEYWORDS,
)

#: Bounded idle ceiling (R033 "bounded idle"). An idle longer than this is not
#: an idle — it is a stop that must be visible to the owner instead.
MAX_IDLE_SECONDS = 24 * 3600.0

RETRY_KEY = "codex_outage_retry"
BLOCKED_KEY = "codex_outage_blocked"
IDLE_KEY = "no_eligible_work_idle"


class OutageError(Exception):
    """An outage-policy rule was violated. Always fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def classify_cause(cause: str) -> str:
    """TRANSIENT or BLOCKING for a named cause. Unknown -> BLOCKING (closed)."""
    if cause in TRANSIENT_CAUSES:
        return TRANSIENT
    if cause in BLOCKING_CAUSES:
        return BLOCKING
    return BLOCKING


def classify_reason_text(reason: str) -> tuple[str, str]:
    """``(cause, class)`` for a bounded failure-reason string.

    An empty or unmatched reason classifies ``("unrecognized", BLOCKING)``:
    a failure the policy cannot name is never granted a retry loop.
    """
    lowered = (reason or "").lower()
    for needle, cause in _REASON_KEYWORDS:
        if needle in lowered:
            return cause, classify_cause(cause)
    return "unrecognized", BLOCKING


# --------------------------------------------------------------------------
# Bounded backoff with jitter (TRANSIENT)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class BackoffPolicy:
    """Deterministic bounded backoff. Every bound is explicit — there is no
    default that could quietly mean 'unlimited'."""

    base_seconds: float
    factor: float
    cap_seconds: float
    max_attempts: int
    jitter_fraction: float = 0.25

    def __post_init__(self) -> None:
        if not self.base_seconds > 0:
            raise OutageError("bad_backoff", "base_seconds must be positive")
        if not self.factor >= 1:
            raise OutageError("bad_backoff", "factor must be >= 1")
        if not self.cap_seconds >= self.base_seconds:
            raise OutageError("bad_backoff", "cap_seconds must be >= base_seconds")
        if isinstance(self.max_attempts, bool) \
                or not isinstance(self.max_attempts, int) or self.max_attempts < 1:
            raise OutageError(
                "bad_backoff",
                f"max_attempts must be a positive integer, got "
                f"{self.max_attempts!r}; an unbounded retry count is the "
                f"unlimited loop R033 prohibits")
        if not 0 <= self.jitter_fraction < 1:
            raise OutageError("bad_backoff", "jitter_fraction must be in [0, 1)")

    def delay_for(self, attempt: int, *, rng: Callable[[], float]) -> float:
        """The jittered delay before retry ``attempt`` (1-based).

        ``rng`` is an injected zero-argument callable returning [0, 1) —
        never the ``random`` module directly, so tests are deterministic.
        An attempt past ``max_attempts`` raises ``attempts_exhausted``.
        """
        if attempt < 1:
            raise OutageError("bad_attempt", f"attempt must be >= 1, got {attempt}")
        if attempt > self.max_attempts:
            raise OutageError(
                "attempts_exhausted",
                f"attempt {attempt} exceeds the bounded {self.max_attempts}; "
                f"the outage is now handled as blocked-with-handoff, not "
                f"retried (R033)")
        raw = min(self.base_seconds * (self.factor ** (attempt - 1)),
                  self.cap_seconds)
        jitter = self.jitter_fraction * (2.0 * float(rng()) - 1.0)
        return max(raw * (1.0 + jitter), 0.001)


@dataclasses.dataclass(frozen=True)
class RetryState:
    """The durable record of one transient-outage retry sequence."""

    cause: str
    reason: str
    attempt: int
    next_retry_at_epoch: float
    recorded_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RetryState":
        try:
            return cls(cause=str(data["cause"]), reason=str(data["reason"]),
                       attempt=int(data["attempt"]),
                       next_retry_at_epoch=float(data["next_retry_at_epoch"]),
                       recorded_at_utc=str(data.get("recorded_at_utc", "")))
        except (KeyError, TypeError, ValueError) as exc:
            raise OutageError("unreadable_retry_state",
                              f"stored retry state is malformed ({exc}); "
                              f"fail closed") from exc


def record_transient_failure(
    journal: Any, *, cause: str, reason: str, now: float,
    policy: BackoffPolicy, rng: Callable[[], float], audit: Any = None,
) -> RetryState:
    """One more transient failure: increment the durable attempt counter and
    schedule the next bounded retry. Raises ``attempts_exhausted`` when the
    bounded budget is spent — the caller then records blocked-with-handoff.

    Refuses a BLOCKING cause outright: auth/billing/revoked/incompatibility
    never enter a retry loop (R033).
    """
    if classify_cause(cause) != TRANSIENT:
        raise OutageError(
            "not_transient",
            f"cause {cause!r} is not transient; it is handled as "
            f"blocked-with-handoff, never retried (R033)")
    stored = journal.get_state(RETRY_KEY, None)
    attempt = (RetryState.from_dict(stored).attempt + 1) if stored else 1
    delay = policy.delay_for(attempt, rng=rng)  # raises when exhausted
    state = RetryState(cause=cause, reason=reason, attempt=attempt,
                       next_retry_at_epoch=float(now) + delay,
                       recorded_at_utc=to_utc_iso())
    journal.set_state(RETRY_KEY, state.to_dict())
    if audit is not None:
        audit.append("codex_outage_backoff", policy_result=cause,
                     detail={**state.to_dict(), "delay_seconds": delay,
                             "max_attempts": policy.max_attempts})
    return state


def retry_due(state: RetryState, now: float) -> bool:
    """Has the durable retry deadline arrived? Never a sleep loop: the caller
    checks at its own cadence and dwells in ``CODEX_OUTAGE_BACKOFF``."""
    return float(now) >= state.next_retry_at_epoch


def stored_retry_state(journal: Any) -> RetryState | None:
    data = journal.get_state(RETRY_KEY, None)
    return RetryState.from_dict(data) if data else None


def clear_retry_state(journal: Any, *, audit: Any = None) -> None:
    """The supervisor answered: the retry sequence is over (explicit act)."""
    journal.set_state(RETRY_KEY, None)
    if audit is not None:
        audit.append("codex_outage_recovered", detail={"cleared_at_utc": to_utc_iso()})


# --------------------------------------------------------------------------
# Blocked-with-handoff (BLOCKING) and bounded idle (no eligible work)
# --------------------------------------------------------------------------


def record_blocked_with_handoff(
    journal: Any, *, cause: str, reason: str, audit: Any = None,
) -> dict[str, Any]:
    """A blocking failure holds for the owner WITH a handoff record — it is
    never retried and never silently swallowed (R033). The record carries what
    a handoff needs to say: the cause, the bounded reason, and what resolves
    it. The caller drives ``CODEX_OUTAGE_BACKOFF -> WAIT_FOR_OWNER``."""
    if classify_cause(cause) == TRANSIENT:
        raise OutageError(
            "not_blocking",
            f"cause {cause!r} is transient; it belongs in the bounded backoff "
            f"path, not the owner queue")
    record = {
        "cause": cause,
        "reason": reason,
        "requires": "an owner action (credentials, billing, access, or a "
                    "compatible version); no retry can resolve it",
        "recorded_at_utc": to_utc_iso(),
    }
    journal.set_state(BLOCKED_KEY, record)
    if audit is not None:
        audit.append("codex_outage_blocked", policy_result=cause, detail=record)
    return record


@dataclasses.dataclass(frozen=True)
class IdleState:
    """The durable record of one bounded no-eligible-work idle."""

    idle_until_epoch: float
    reason: str
    recheck_count: int
    recorded_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def begin_bounded_idle(
    journal: Any, *, now: float, idle_seconds: float, reason: str,
    audit: Any = None,
) -> IdleState:
    """No eligible authorized work: dwell in ``NO_ELIGIBLE_WORK`` until a
    durable deadline — never a busy loop (R028/R033). The bound is enforced:
    an idle beyond ``MAX_IDLE_SECONDS`` is refused as not-an-idle."""
    if not 0 < float(idle_seconds) <= MAX_IDLE_SECONDS:
        raise OutageError(
            "idle_not_bounded",
            f"idle_seconds must be in (0, {MAX_IDLE_SECONDS}], got "
            f"{idle_seconds!r}; a longer hold is a visible stop, not an idle "
            f"(R033)")
    stored = journal.get_state(IDLE_KEY, None) or {}
    count = int(stored.get("recheck_count", 0) or 0) + 1
    state = IdleState(idle_until_epoch=float(now) + float(idle_seconds),
                      reason=reason, recheck_count=count,
                      recorded_at_utc=to_utc_iso())
    journal.set_state(IDLE_KEY, state.to_dict())
    if audit is not None:
        audit.append("no_eligible_work_idle", detail=state.to_dict())
    return state


def idle_over(state: IdleState, now: float) -> bool:
    return float(now) >= state.idle_until_epoch


# --------------------------------------------------------------------------
# What is permitted while the policy holds (R033)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class OutagePermissions:
    """R033's split verdict during an outage or idle hold."""

    may_land_current_atomic_operation: bool
    may_dispatch_new_producer_work: bool
    reason: str


def permissions_during(outage_class: str) -> OutagePermissions:
    """During ANY hold, new producer work is never dispatched unsupervised;
    only during a TRANSIENT hold may the current atomic operation land, and
    only under pre-authorized deterministic rules (R033)."""
    if outage_class == TRANSIENT:
        return OutagePermissions(
            True, False,
            "transient outage: the current atomic producer operation may land "
            "under pre-authorized deterministic rules; the campaign then "
            "holds until the supervisor returns (R033)")
    if outage_class == BLOCKING:
        return OutagePermissions(
            False, False,
            "blocking failure: nothing lands and nothing dispatches until "
            "the owner acts (R033)")
    raise OutageError("unknown_class",
                      f"{outage_class!r} is not one of ({TRANSIENT!r}, {BLOCKING!r})")
