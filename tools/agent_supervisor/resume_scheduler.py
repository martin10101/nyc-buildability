#!/usr/bin/env python3
"""Usage-limit waiting and durable wake scheduling (D-007 S11.4).

The shape of this module follows S11.4 exactly:

1. **Distinct limit classes.** Five-hour/session, weekly, model-specific, API
   429, API 529, and provider outage are SEPARATE conditions with separate
   handling - never collapsed into "rate limited".
2. **Structured metadata first.** `detect_limit` reads provider-structured
   fields before it will look at prose. The strict notice parser is a FALLBACK
   only, is version-stamped (`PARSER_VERSION`), and recognizes only the
   enumerated documented forms. Anything else is `AMBIGUOUS` -> ASK.
3. **Never guess a timer.** Ambiguous, implausible, expired, nonexistent (DST
   gap), or doubly-defined (DST fold) times all return an ASK outcome. There is
   no code path that invents a deadline.
4. **Durable, OS-level wake.** No sleep loop, no polling, no "ask a model
   whether it is time yet". The plan layer emits the exact `schtasks` argv and
   task XML; the mutation itself is an explicit owner-gated act.
5. **Fixed action.** The scheduled action is a constant template invoking a
   manifest-verified launcher with fixed arguments. `assert_fixed_action`
   refuses anything else, so a model-generated command can never become a
   scheduled task.

Honest scope note: this module PLANS and VERIFIES the OS task. It executes a
`schtasks` mutation only through `AutostartInstaller`, which requires an explicit
operator confirmation token bound to the plan digest, and which is driven with an
injected executable path so tests use a fake and never touch the real scheduler.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import os
import re
import time
import zoneinfo
from typing import Any, Mapping, Sequence
from xml.sax.saxutils import escape as _xml_escape

from .models import digest_of, to_utc_iso
from .process import assert_argv_safe

# --------------------------------------------------------------------------
# Limit classes (S11.4: "distinct conditions")
# --------------------------------------------------------------------------

LIMIT_FIVE_HOUR = "five_hour_session"
LIMIT_WEEKLY = "weekly"
LIMIT_MODEL_SPECIFIC = "model_specific"
LIMIT_API_429 = "api_429"
LIMIT_API_529 = "api_529"
LIMIT_PROVIDER_OUTAGE = "provider_outage"

LIMIT_CLASSES: tuple[str, ...] = (
    LIMIT_FIVE_HOUR, LIMIT_WEEKLY, LIMIT_MODEL_SPECIFIC,
    LIMIT_API_429, LIMIT_API_529, LIMIT_PROVIDER_OUTAGE,
)

#: Classes whose reset time, when trustworthy, justifies a durable wake.
SCHEDULABLE_CLASSES: frozenset[str] = frozenset({
    LIMIT_FIVE_HOUR, LIMIT_WEEKLY, LIMIT_MODEL_SPECIFIC, LIMIT_API_429,
})

#: Classes with no meaningful reset time: retry policy, never a scheduled wake
#: derived from prose.
UNSCHEDULABLE_CLASSES: frozenset[str] = frozenset({LIMIT_API_529, LIMIT_PROVIDER_OUTAGE})

SOURCE_STRUCTURED = "structured_metadata"
SOURCE_NOTICE_PARSER = "notice_parser"
SOURCE_NONE = "none"

CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_NONE = "none"

#: Bumped whenever a notice pattern changes. Persisted with every record so a
#: later controller can tell which parser produced a stored deadline.
PARSER_VERSION = "1.0.0"

#: A reset further out than this is implausible for any documented limit class.
MAX_PLAUSIBLE_WAIT = _dt.timedelta(days=8)
#: A "reset" already in the past by more than this is expired, not a deadline.
EXPIRED_GRACE = _dt.timedelta(minutes=1)


class ScheduleError(Exception):
    """A scheduling rule was violated. Never degrades into a guess."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Structured-metadata detection (preferred path)
# --------------------------------------------------------------------------

#: Candidate structured keys, in preference order. These are DOCUMENTED
#: CANDIDATES, not verified field names: the Phase 1 probe observed a
#: `rate_limit_event` on the stream but its exact payload keys were not
#: captured. `StructuredKeys` therefore lets the caller supply the mapping it has
#: actually verified, and every record states which key it read.
DEFAULT_RESET_KEYS: tuple[str, ...] = (
    "resets_at", "resetsAt", "reset_at", "resetAt", "reset_time_utc",
)
DEFAULT_RETRY_AFTER_KEYS: tuple[str, ...] = (
    "retry_after_seconds", "retryAfterSeconds", "retry_after",
)
DEFAULT_CLASS_KEYS: tuple[str, ...] = ("limit_type", "limitType", "scope", "class")
DEFAULT_STATUS_KEYS: tuple[str, ...] = ("status", "status_code", "statusCode", "http_status")


@dataclasses.dataclass(frozen=True)
class StructuredKeys:
    """Which structured keys this controller trusts, and their verification status."""

    reset_keys: tuple[str, ...] = DEFAULT_RESET_KEYS
    retry_after_keys: tuple[str, ...] = DEFAULT_RETRY_AFTER_KEYS
    class_keys: tuple[str, ...] = DEFAULT_CLASS_KEYS
    status_keys: tuple[str, ...] = DEFAULT_STATUS_KEYS
    #: False until a capability probe confirms the installed CLI's real payload.
    verified_against_installed_cli: bool = False


DEFAULT_STRUCTURED_KEYS = StructuredKeys()

_CLASS_HINTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(five[_\- ]?hour|5[_\- ]?hour|session)\b", re.I), LIMIT_FIVE_HOUR),
    (re.compile(r"\bweek(ly)?\b", re.I), LIMIT_WEEKLY),
    (re.compile(r"\b(model|per[_\- ]?model)\b", re.I), LIMIT_MODEL_SPECIFIC),
    (re.compile(r"\b(outage|unavailable|service[_\- ]?down)\b", re.I), LIMIT_PROVIDER_OUTAGE),
)


def _first_present(data: Mapping[str, Any], keys: Sequence[str]) -> tuple[str, Any]:
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return key, data[key]
    return "", None


def classify_limit(
    metadata: Mapping[str, Any] | None = None,
    notice: str = "",
) -> tuple[str, str]:
    """Classify the limit condition. Returns (class, evidence). Never guesses a time."""
    metadata = dict(metadata or {})

    status_key, status = _first_present(metadata, DEFAULT_STATUS_KEYS)
    if status is not None:
        try:
            code = int(status)
        except (TypeError, ValueError):
            code = 0
        if code == 429:
            return LIMIT_API_429, f"{status_key}=429"
        if code == 529:
            return LIMIT_API_529, f"{status_key}=529"
        if code in (500, 502, 503, 504):
            return LIMIT_PROVIDER_OUTAGE, f"{status_key}={code}"

    class_key, declared = _first_present(metadata, DEFAULT_CLASS_KEYS)
    if isinstance(declared, str):
        if declared in LIMIT_CLASSES:
            return declared, f"{class_key}={declared}"
        for pattern, limit_class in _CLASS_HINTS:
            if pattern.search(declared):
                return limit_class, f"{class_key}={declared!r}"

    text = notice or ""
    if re.search(r"\b529\b", text):
        return LIMIT_API_529, "notice mentions 529"
    if re.search(r"\b429\b", text) or re.search(r"\brate limit(ed)?\b", text, re.I):
        api_hit = LIMIT_API_429
        # A weekly/session phrase is more specific than a bare "rate limited".
        for pattern, limit_class in _CLASS_HINTS:
            if pattern.search(text):
                return limit_class, f"notice matched {limit_class}"
        return api_hit, "notice mentions a rate limit"
    for pattern, limit_class in _CLASS_HINTS:
        if pattern.search(text):
            return limit_class, f"notice matched {limit_class}"
    if re.search(r"\busage limit\b", text, re.I):
        return LIMIT_FIVE_HOUR, "notice mentions a usage limit with no finer class"
    return LIMIT_PROVIDER_OUTAGE, "no class evidence; treated as an outage-class hold"


# --------------------------------------------------------------------------
# Reset-time parsing
# --------------------------------------------------------------------------

RESET_OK = "ok"
RESET_AMBIGUOUS = "ambiguous"
RESET_IMPLAUSIBLE = "implausible"
RESET_EXPIRED = "expired"
RESET_UNPARSEABLE = "unparseable"
RESET_ABSENT = "absent"

#: Outcomes that must queue an ASK rather than schedule anything.
RESET_ASK_OUTCOMES: frozenset[str] = frozenset({
    RESET_AMBIGUOUS, RESET_IMPLAUSIBLE, RESET_EXPIRED, RESET_UNPARSEABLE,
})


@dataclasses.dataclass(frozen=True)
class ResetParse:
    """The result of trying to establish a trustworthy reset instant."""

    outcome: str
    deadline_utc: str = ""
    source: str = SOURCE_NONE
    confidence: str = CONFIDENCE_NONE
    parser_version: str = PARSER_VERSION
    matched_form: str = ""
    detail: str = ""

    @property
    def trustworthy(self) -> bool:
        return self.outcome == RESET_OK and bool(self.deadline_utc)

    @property
    def requires_ask(self) -> bool:
        return self.outcome in RESET_ASK_OUTCOMES


#: The documented notice forms this parser recognizes, each with a name so a
#: stored record says exactly which form matched. Anything not listed here is
#: UNPARSEABLE - the parser never falls back to "find a number that looks like a
#: time" in arbitrary model text (S11.4).
_NOTICE_FORMS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # "resets 2026-08-04T07:00:00Z" / "resets at 2026-08-04 07:00 UTC"
    ("iso_utc", re.compile(
        r"\bresets?\s*(?:at\s*)?(?P<date>\d{4}-\d{2}-\d{2})[T ]"
        r"(?P<hour>\d{2}):(?P<minute>\d{2})(?::\d{2})?\s*(?:Z|UTC)\b", re.I)),
    # "resets at 2026-08-04 07:00" (local, no zone marker)
    ("iso_local", re.compile(
        r"\bresets?\s*(?:at\s*)?(?P<date>\d{4}-\d{2}-\d{2})[T ]"
        r"(?P<hour>\d{2}):(?P<minute>\d{2})(?::\d{2})?\s*$", re.I | re.M)),
    # "resets at 3pm" / "resets 3:30 pm"
    ("clock_12h", re.compile(
        r"\bresets?\s*(?:at\s*)?(?P<hour>1[0-2]|0?[1-9])(?::(?P<minute>[0-5]\d))?\s*"
        r"(?P<meridiem>am|pm)\b", re.I)),
    # "resets at 15:00". The negative lookahead is load-bearing: without it
    # "resets 3:30 pm" matched BOTH this form and clock_12h, and the
    # more-than-one-form guard then rejected a perfectly documented notice as
    # ambiguous (caught by test_12_hour_clock_with_minutes).
    ("clock_24h", re.compile(
        r"\bresets?\s*(?:at\s*)?(?P<hour>[01]?\d|2[0-3]):(?P<minute>[0-5]\d)\b"
        r"(?!\s*(?:am|pm)\b)", re.I)),
)

#: Explicit zone suffix, e.g. "resets at 3pm (America/New_York)".
_ZONE_SUFFIX = re.compile(r"\(([A-Za-z]+/[A-Za-z_+\-0-9]+)\)")


def _tz_or_error(name: str) -> _dt.tzinfo:
    try:
        return zoneinfo.ZoneInfo(name)
    except Exception as exc:  # zoneinfo raises several types; all mean "unusable"
        raise ScheduleError("unknown_timezone",
                            f"timezone {name!r} is not resolvable: {exc}") from exc


def local_timezone_name() -> str:
    """The best available IANA name for the local zone ('' when unknown)."""
    override = os.environ.get("SUPERVISOR_LOCAL_TZ", "")
    if override:
        return override
    try:
        name = _dt.datetime.now().astimezone().tzname() or ""
    except Exception:  # pragma: no cover - platform dependent
        name = ""
    return name


def _dst_verdict(naive: _dt.datetime, tz: _dt.tzinfo) -> str:
    """'' when the local time is well defined; a reason when it is not.

    A DST spring-forward gap makes a local time NONEXISTENT; a fall-back overlap
    makes it AMBIGUOUS (it happens twice). S11.4 forbids guessing either way.
    """
    early = naive.replace(tzinfo=tz, fold=0)
    late = naive.replace(tzinfo=tz, fold=1)
    # ORDER MATTERS. Under PEP 495 the two folds carry different UTC offsets in
    # BOTH a gap and an overlap, so the fold test alone reports every gap as an
    # overlap. Only a gap fails to round-trip, so the round-trip test runs first.
    round_tripped = early.astimezone(_dt.timezone.utc).astimezone(tz)
    if round_tripped.replace(tzinfo=None) != naive:
        return "the local time does not exist on this date (a DST spring-forward gap)"
    if early.utcoffset() != late.utcoffset():
        return ("the local time occurs twice on this date (a DST fall-back overlap); "
                "which occurrence is meant is not determinable")
    return ""


def parse_reset_notice(
    notice: str,
    *,
    now_utc: _dt.datetime,
    local_tz_name: str,
) -> ResetParse:
    """Strict, version-stamped fallback parser for DOCUMENTED reset notices.

    Handles: explicit dates; 12- and 24-hour clocks; midnight/day rollover;
    DST transitions; explicit zone suffixes. Rejects everything else.
    """
    if now_utc.tzinfo is None:
        raise ScheduleError("naive_now", "now_utc must be timezone-aware")
    text = (notice or "").strip()
    if not text:
        return ResetParse(RESET_ABSENT, detail="no notice text was supplied")

    zone_match = _ZONE_SUFFIX.search(text)
    tz_name = zone_match.group(1) if zone_match else local_tz_name
    matches = [(name, pattern.search(text)) for name, pattern in _NOTICE_FORMS]
    matches = [(name, m) for name, m in matches if m is not None]
    if not matches:
        return ResetParse(
            RESET_UNPARSEABLE, source=SOURCE_NOTICE_PARSER,
            detail="the notice does not match any documented reset form; a timer is never "
                   "extracted from arbitrary model text (S11.4)")
    if len({name for name, _ in matches}) > 1 and \
            not {name for name, _ in matches} <= {"iso_utc", "iso_local"}:
        return ResetParse(
            RESET_AMBIGUOUS, source=SOURCE_NOTICE_PARSER,
            matched_form=",".join(sorted(name for name, _ in matches)),
            detail="the notice matches more than one documented reset form; refusing to "
                   "choose one")

    form, match = matches[0]

    if form == "iso_utc":
        date = _dt.date.fromisoformat(match.group("date"))
        candidate = _dt.datetime(date.year, date.month, date.day,
                                 int(match.group("hour")), int(match.group("minute")),
                                 tzinfo=_dt.timezone.utc)
        return _finish(candidate, now_utc, form, CONFIDENCE_HIGH)

    if not tz_name:
        return ResetParse(
            RESET_AMBIGUOUS, source=SOURCE_NOTICE_PARSER, matched_form=form,
            detail="a local reset time was given but the local timezone is unknown; the "
                   "instant is not determinable")
    try:
        tz = _tz_or_error(tz_name)
    except ScheduleError as exc:
        return ResetParse(RESET_AMBIGUOUS, source=SOURCE_NOTICE_PARSER, matched_form=form,
                          detail=exc.message)

    now_local = now_utc.astimezone(tz)

    if form == "iso_local":
        date = _dt.date.fromisoformat(match.group("date"))
        naive = _dt.datetime(date.year, date.month, date.day,
                             int(match.group("hour")), int(match.group("minute")))
    else:
        hour = int(match.group("hour"))
        minute = int(match.group("minute") or 0)
        if form == "clock_12h":
            meridiem = match.group("meridiem").lower()
            if meridiem == "pm" and hour != 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
        naive = now_local.replace(tzinfo=None, hour=hour, minute=minute,
                                  second=0, microsecond=0)
        if naive <= now_local.replace(tzinfo=None):
            # Midnight / day rollover: the next occurrence is tomorrow.
            naive = naive + _dt.timedelta(days=1)

    dst_problem = _dst_verdict(naive, tz)
    if dst_problem:
        return ResetParse(RESET_AMBIGUOUS, source=SOURCE_NOTICE_PARSER, matched_form=form,
                          detail=dst_problem)

    candidate = naive.replace(tzinfo=tz).astimezone(_dt.timezone.utc)
    confidence = CONFIDENCE_HIGH if form == "iso_local" else CONFIDENCE_MEDIUM
    return _finish(candidate, now_utc, form, confidence)


def _finish(candidate: _dt.datetime, now_utc: _dt.datetime, form: str,
            confidence: str) -> ResetParse:
    delta = candidate - now_utc
    if delta < -EXPIRED_GRACE:
        return ResetParse(RESET_EXPIRED, source=SOURCE_NOTICE_PARSER, matched_form=form,
                          detail=f"the parsed reset {to_utc_iso(candidate)} is already in "
                                 f"the past")
    if delta > MAX_PLAUSIBLE_WAIT:
        return ResetParse(RESET_IMPLAUSIBLE, source=SOURCE_NOTICE_PARSER, matched_form=form,
                          detail=f"the parsed reset is {delta} away, beyond the "
                                 f"{MAX_PLAUSIBLE_WAIT} plausibility bound")
    return ResetParse(RESET_OK, to_utc_iso(candidate), SOURCE_NOTICE_PARSER, confidence,
                      PARSER_VERSION, form, "parsed from a documented notice form")


def reset_from_metadata(
    metadata: Mapping[str, Any],
    *,
    now_utc: _dt.datetime,
    keys: StructuredKeys = DEFAULT_STRUCTURED_KEYS,
) -> ResetParse:
    """Read a reset instant from provider STRUCTURED metadata (the preferred path)."""
    key, raw = _first_present(metadata, keys.reset_keys)
    if key:
        candidate: _dt.datetime | None = None
        if isinstance(raw, (int, float)) and not isinstance(raw, bool):
            try:
                candidate = _dt.datetime.fromtimestamp(float(raw), _dt.timezone.utc)
            except (OverflowError, OSError, ValueError):
                candidate = None
        elif isinstance(raw, str):
            try:
                parsed = _dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                parsed = None
            if parsed is not None:
                candidate = (parsed if parsed.tzinfo is not None
                             else parsed.replace(tzinfo=_dt.timezone.utc))
        if candidate is None:
            return ResetParse(RESET_UNPARSEABLE, source=SOURCE_STRUCTURED,
                              matched_form=key,
                              detail=f"structured field {key!r} carried {raw!r}, which is "
                                     f"not a usable instant")
        result = _finish(candidate, now_utc, key, CONFIDENCE_HIGH)
        return dataclasses.replace(result, source=SOURCE_STRUCTURED)

    key, raw = _first_present(metadata, keys.retry_after_keys)
    if key:
        try:
            seconds = float(raw)
        except (TypeError, ValueError):
            return ResetParse(RESET_UNPARSEABLE, source=SOURCE_STRUCTURED, matched_form=key,
                              detail=f"structured field {key!r} carried {raw!r}")
        if seconds < 0:
            return ResetParse(RESET_IMPLAUSIBLE, source=SOURCE_STRUCTURED, matched_form=key,
                              detail="a negative retry-after is not a deadline")
        result = _finish(now_utc + _dt.timedelta(seconds=seconds), now_utc, key,
                         CONFIDENCE_HIGH)
        return dataclasses.replace(result, source=SOURCE_STRUCTURED)

    return ResetParse(RESET_ABSENT, source=SOURCE_STRUCTURED,
                      detail="no structured reset field was present")


def detect_reset(
    *,
    metadata: Mapping[str, Any] | None,
    notice: str,
    now_utc: _dt.datetime,
    local_tz_name: str,
    keys: StructuredKeys = DEFAULT_STRUCTURED_KEYS,
) -> ResetParse:
    """Structured metadata FIRST; the strict notice parser only as a fallback."""
    if metadata:
        structured = reset_from_metadata(metadata, now_utc=now_utc, keys=keys)
        if structured.outcome != RESET_ABSENT:
            return structured
    return parse_reset_notice(notice, now_utc=now_utc, local_tz_name=local_tz_name)


# --------------------------------------------------------------------------
# The durable limit record (S11.4 step 2)
# --------------------------------------------------------------------------

LIMIT_RECORD_KEY = "usage_limit_record"
TRIGGER_KEY = "scheduled_trigger"
RESUME_NOT_BEFORE_KEY = "resume_not_before_utc"
CODEX_HOLD_KEY = "codex_rate_limit_hold"


@dataclasses.dataclass(frozen=True)
class LimitRecord:
    """Everything S11.4 step 2 requires to be persisted. No secrets."""

    limit_class: str
    raw_notice: str
    parser: str
    parser_version: str
    source: str
    confidence: str
    local_timezone: str
    observed_wall_clock_utc: str
    parsed_deadline_utc: str
    session_id: str
    pending_unit: str
    resume_not_before_utc: str
    margin_seconds: int
    class_evidence: str = ""
    provider: str = "claude"

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def digest(self) -> str:
        return digest_of(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LimitRecord":
        known = {f.name for f in dataclasses.fields(cls)}
        missing = sorted(known - set(data) - {"class_evidence", "provider"})
        if missing:
            raise ScheduleError("incomplete_limit_record",
                                f"persisted limit record is missing {missing}")
        return cls(**{k: v for k, v in data.items() if k in known})


DEFAULT_POST_RESET_MARGIN_SECONDS = 120


def build_limit_record(
    *,
    limit_class: str,
    raw_notice: str,
    parse: ResetParse,
    local_tz_name: str,
    session_id: str,
    pending_unit: str,
    now_utc: _dt.datetime,
    margin_seconds: int = DEFAULT_POST_RESET_MARGIN_SECONDS,
    class_evidence: str = "",
    provider: str = "claude",
    redactor: Any = None,
) -> LimitRecord:
    """Assemble the durable record. Refuses to build one without a trustworthy time."""
    if limit_class not in LIMIT_CLASSES:
        raise ScheduleError("unknown_limit_class",
                            f"{limit_class!r} is not one of {list(LIMIT_CLASSES)}")
    if not parse.trustworthy:
        raise ScheduleError(
            "no_trustworthy_deadline",
            f"refusing to persist a wait record without a trustworthy reset time "
            f"({parse.outcome}: {parse.detail}); S11.4 queues an ASK instead of guessing")
    if margin_seconds < 0:
        raise ScheduleError("bad_margin", "the post-reset margin may not be negative")

    deadline = _dt.datetime.fromisoformat(parse.deadline_utc.replace("Z", "+00:00"))
    resume_at = deadline + _dt.timedelta(seconds=margin_seconds)
    notice = raw_notice
    if redactor is not None:
        notice = redactor(raw_notice)
    return LimitRecord(
        limit_class=limit_class,
        raw_notice=notice,
        parser=parse.source,
        parser_version=parse.parser_version,
        source=parse.source,
        confidence=parse.confidence,
        local_timezone=local_tz_name,
        observed_wall_clock_utc=to_utc_iso(now_utc),
        parsed_deadline_utc=parse.deadline_utc,
        session_id=session_id,
        pending_unit=pending_unit,
        resume_not_before_utc=to_utc_iso(resume_at),
        margin_seconds=margin_seconds,
        class_evidence=class_evidence or parse.matched_form,
        provider=provider,
    )


# --------------------------------------------------------------------------
# Fixed scheduled action and the OS task plan
# --------------------------------------------------------------------------

#: The ONE named wake task. Never per-run, never model-named: "model-created
#: scheduled tasks never accumulate" (S11.4).
WAKE_TASK_NAME = "NYCBuildabilitySupervisorWake"
BOOT_TASK_NAME = "NYCBuildabilitySupervisorBoot"

#: The fixed action arguments. The launcher is invoked with these and nothing
#: else - no repository-supplied paths, no stored credentials, no model text.
FIXED_ACTION_ARGUMENTS: tuple[str, ...] = ("--resume-scheduled-wake",)
FIXED_BOOT_ARGUMENTS: tuple[str, ...] = ("--recover-boot",)


@dataclasses.dataclass(frozen=True)
class LauncherSpec:
    """The immutable launcher the OS task runs, plus its recorded digest.

    `launch_arguments` is the FIXED prefix a launcher needs to reach the
    controller (for example `-m tools.agent_supervisor` for a Python launcher).
    It is part of the spec, so it is fixed and digest-recorded at plan time - it
    is never assembled from repository text at run time.
    """

    path: str
    digest_sha256: str
    manifest_digest: str = ""
    launch_arguments: tuple[str, ...] = ()
    working_directory: str = ""

    def __post_init__(self) -> None:
        if not self.path:
            raise ScheduleError("missing_launcher", "a launcher path is required")
        if len(self.digest_sha256) != 64:
            raise ScheduleError("bad_launcher_digest",
                                "the launcher digest must be a full SHA-256 hex digest")
        for argument in self.launch_arguments:
            if not isinstance(argument, str) or not argument:
                raise ScheduleError("bad_launch_argument",
                                    "every fixed launch argument must be a non-empty string")


def assert_fixed_action(argv: Sequence[str], launcher: LauncherSpec,
                        *, boot: bool = False) -> list[str]:
    """Refuse any scheduled action that is not the fixed launcher + fixed arguments."""
    expected = [launcher.path, *launcher.launch_arguments,
                *(FIXED_BOOT_ARGUMENTS if boot else FIXED_ACTION_ARGUMENTS)]
    actual = list(argv)
    if actual != expected:
        raise ScheduleError(
            "non_fixed_scheduler_action",
            f"the scheduled action must be exactly the manifest-verified launcher with its "
            f"fixed arguments {expected}; got {actual}. A model-generated command, a "
            f"repository-supplied path, or a stored credential may never become a scheduled "
            f"task action (S11.4)")
    return assert_argv_safe(actual)


@dataclasses.dataclass(frozen=True)
class AutostartPlan:
    """A read-only plan for the OS task. Producing it mutates nothing."""

    task_name: str
    kind: str
    launcher: LauncherSpec
    action_argv: tuple[str, ...]
    trigger_kind: str
    trigger_time_utc: str
    wake_to_run: bool
    task_xml: str
    create_argv: tuple[str, ...]
    delete_argv: tuple[str, ...]
    query_argv: tuple[str, ...]

    def digest(self) -> str:
        return digest_of({
            "task_name": self.task_name, "kind": self.kind,
            "launcher": dataclasses.asdict(self.launcher),
            "action_argv": list(self.action_argv),
            "trigger_kind": self.trigger_kind,
            "trigger_time_utc": self.trigger_time_utc,
            "wake_to_run": self.wake_to_run,
            "task_xml_digest": digest_of(self.task_xml),
        })

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        for key, value in list(data.items()):
            if isinstance(value, tuple):
                data[key] = list(value)
        data["plan_digest"] = self.digest()
        return data


_TASK_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>{description}</Description>
    <URI>\\{task_name}</URI>
  </RegistrationInfo>
  <Triggers>
{trigger_xml}
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <WakeToRun>{wake_to_run}</WakeToRun>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <ExecutionTimeLimit>PT4H</ExecutionTimeLimit>
    <Priority>7</Priority>
    <DeleteExpiredTaskAfter>PT1H</DeleteExpiredTaskAfter>
  </Settings>
  <Actions>
    <Exec>
      <Command>{command}</Command>
      <Arguments>{arguments}</Arguments>
      <WorkingDirectory>{working_directory}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""

_TIME_TRIGGER_XML = """    <TimeTrigger>
      <StartBoundary>{start_boundary}</StartBoundary>
      <Enabled>true</Enabled>
      <EndBoundary>{end_boundary}</EndBoundary>
    </TimeTrigger>"""

_BOOT_TRIGGER_XML = """    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>"""


def build_autostart_plan(
    *,
    launcher: LauncherSpec,
    kind: str = "wake",
    trigger_time_utc: str = "",
    wake_to_run: bool = True,
    local_tz_name: str = "",
) -> AutostartPlan:
    """Build the read-only plan: exact argv, exact task XML, nothing executed.

    `kind='wake'` is the one named one-shot wake task; `kind='boot'` is the fixed
    startup/logon task that launches the immutable supervisor at next boot so it
    can resume immediately if the deadline has already passed (S11.4 step 4).
    """
    if kind not in ("wake", "boot"):
        raise ScheduleError("unknown_task_kind", f"{kind!r} is not 'wake' or 'boot'")
    boot = kind == "boot"
    task_name = BOOT_TASK_NAME if boot else WAKE_TASK_NAME
    action_argv = tuple(assert_fixed_action(
        [launcher.path, *launcher.launch_arguments,
         *(FIXED_BOOT_ARGUMENTS if boot else FIXED_ACTION_ARGUMENTS)],
        launcher, boot=boot))

    if boot:
        trigger_xml = _BOOT_TRIGGER_XML
        trigger_kind = "LogonTrigger"
        start_local = ""
    else:
        if not trigger_time_utc:
            raise ScheduleError("missing_trigger_time",
                                "a wake task needs the exact resume_not_before instant")
        moment = _dt.datetime.fromisoformat(trigger_time_utc.replace("Z", "+00:00"))
        tz: _dt.tzinfo = _dt.timezone.utc
        if local_tz_name:
            try:
                tz = _tz_or_error(local_tz_name)
            except ScheduleError:
                tz = _dt.timezone.utc
        local = moment.astimezone(tz)
        start_local = local.strftime("%Y-%m-%dT%H:%M:%S")
        end_local = (local + _dt.timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S")
        trigger_xml = _TIME_TRIGGER_XML.format(start_boundary=start_local,
                                               end_boundary=end_local)
        trigger_kind = "TimeTrigger"

    task_xml = _TASK_XML_TEMPLATE.format(
        description=_xml_escape(
            "NYC Buildability supervisor: fixed, manifest-verified launcher. "
            "Created only by an explicit owner-approved setup act (D-007 S11.4)."),
        task_name=_xml_escape(task_name),
        trigger_xml=trigger_xml,
        wake_to_run="true" if (wake_to_run and not boot) else "false",
        command=_xml_escape(action_argv[0]),
        arguments=_xml_escape(" ".join(action_argv[1:])),
        working_directory=_xml_escape(launcher.working_directory),
    )

    create_argv = ("schtasks", "/Create", "/TN", task_name, "/XML", "<task-xml-file>", "/F")
    delete_argv = ("schtasks", "/Delete", "/TN", task_name, "/F")
    query_argv = ("schtasks", "/Query", "/TN", task_name, "/XML")

    return AutostartPlan(
        task_name=task_name,
        kind=kind,
        launcher=launcher,
        action_argv=action_argv,
        trigger_kind=trigger_kind,
        trigger_time_utc=trigger_time_utc if not boot else "",
        wake_to_run=bool(wake_to_run and not boot),
        task_xml=task_xml,
        create_argv=create_argv,
        delete_argv=delete_argv,
        query_argv=query_argv,
    )


def verify_installed_definition(plan: AutostartPlan, installed_xml: str) -> tuple[bool, str]:
    """Verify an installed task against the accepted plan (S11.4: before AND after).

    The time trigger is the ONLY setting a later update may change, so this
    compares every non-time setting exactly and reports a time difference
    separately.
    """
    def _extract(tag: str, text: str) -> str:
        match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.S)
        return (match.group(1).strip() if match else "")

    for tag in ("Command", "Arguments", "WorkingDirectory", "WakeToRun",
                "MultipleInstancesPolicy", "ExecutionTimeLimit", "Enabled"):
        expected = _extract(tag, plan.task_xml)
        actual = _extract(tag, installed_xml)
        if expected != actual:
            return False, (f"installed task setting <{tag}> is {actual!r}, the accepted "
                           f"definition says {expected!r}; only the TIME TRIGGER may differ")
    expected_start = _extract("StartBoundary", plan.task_xml)
    actual_start = _extract("StartBoundary", installed_xml)
    if expected_start != actual_start:
        return True, (f"non-time settings match; the time trigger differs "
                      f"({actual_start!r} vs {expected_start!r}) - that is the only "
                      f"permitted difference")
    return True, "the installed definition matches the accepted plan exactly"


class AutostartInstaller:
    """The owner-gated OS mutation. Refuses to act without an explicit command.

    The `schtasks` path is INJECTED so tests drive a fake executable; nothing in
    this class discovers or hard-codes the real scheduler.
    """

    def __init__(self, *, schtasks_path: str, runner: Any = None) -> None:
        self.schtasks_path = schtasks_path
        self._runner = runner

    def _run(self, argv: Sequence[str]) -> Any:
        from . import process as _process

        run = self._runner or _process.run
        return run(assert_argv_safe(list(argv)), timeout=60)

    @staticmethod
    def assert_owner_command(plan: AutostartPlan, confirmation: str,
                             *, operator_command: bool) -> None:
        """Refuse unless the owner ran the command AND quoted the plan digest."""
        if not operator_command:
            raise ScheduleError(
                "not_an_operator_command",
                "creating, changing, or deleting the OS task is a separate one-time "
                "owner-approved setup act; it never happens as a side effect of a run "
                "(S11.4)")
        if confirmation != plan.digest():
            raise ScheduleError(
                "confirmation_digest_mismatch",
                f"the confirmation must quote the displayed plan digest "
                f"{plan.digest()}; got {confirmation!r}")

    def install(self, plan: AutostartPlan, *, xml_path: str, confirmation: str,
                operator_command: bool = False) -> dict[str, Any]:
        """Create/replace the ONE named task, then verify the installed definition."""
        self.assert_owner_command(plan, confirmation, operator_command=operator_command)
        argv = [self.schtasks_path, "/Create", "/TN", plan.task_name, "/XML", xml_path, "/F"]
        result = self._run(argv)
        record: dict[str, Any] = {
            "action": "install",
            "task_name": plan.task_name,
            "argv": argv,
            "returncode": getattr(result, "returncode", 1),
            "plan_digest": plan.digest(),
            "at_utc": to_utc_iso(),
        }
        if record["returncode"] != 0:
            record["verified"] = False
            record["detail"] = "schtasks reported a failure; nothing is assumed installed"
            return record
        query = self._run([self.schtasks_path, "/Query", "/TN", plan.task_name, "/XML"])
        installed_xml = getattr(query, "stdout", "") or ""
        ok, detail = verify_installed_definition(plan, installed_xml)
        record["verified"] = ok
        record["detail"] = detail
        return record

    def uninstall(self, plan: AutostartPlan, *, confirmation: str,
                  operator_command: bool = False) -> dict[str, Any]:
        self.assert_owner_command(plan, confirmation, operator_command=operator_command)
        argv = [self.schtasks_path, "/Delete", "/TN", plan.task_name, "/F"]
        result = self._run(argv)
        return {
            "action": "uninstall",
            "task_name": plan.task_name,
            "argv": argv,
            "returncode": getattr(result, "returncode", 1),
            "plan_digest": plan.digest(),
            "at_utc": to_utc_iso(),
        }


# --------------------------------------------------------------------------
# The durable schedule in the journal
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ScheduledTrigger:
    """The durable record of the one scheduled wake."""

    task_name: str
    trigger_identity: str
    resume_not_before_utc: str
    limit_record_digest: str
    created_at_utc: str
    replaced_count: int = 0
    consumed_at_utc: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class ResumeScheduler:
    """Durable usage-limit wait and wake scheduling over the journal."""

    def __init__(self, journal: Any, *, audit: Any = None) -> None:
        self.journal = journal
        self.audit = audit

    # -- persistence ---------------------------------------------------------

    def record(self) -> LimitRecord | None:
        data = self.journal.get_state(LIMIT_RECORD_KEY)
        return LimitRecord.from_dict(data) if isinstance(data, dict) else None

    def trigger(self) -> ScheduledTrigger | None:
        data = self.journal.get_state(TRIGGER_KEY)
        if not isinstance(data, dict):
            return None
        known = {f.name for f in dataclasses.fields(ScheduledTrigger)}
        return ScheduledTrigger(**{k: v for k, v in data.items() if k in known})

    def persist_limit(self, record: LimitRecord) -> LimitRecord:
        """Persist the S11.4 step-2 record and `resume_not_before_utc`."""
        self.journal.set_state(LIMIT_RECORD_KEY, record.to_dict())
        self.journal.set_state(RESUME_NOT_BEFORE_KEY, record.resume_not_before_utc)
        self._audit("usage_limit_recorded", {
            "limit_class": record.limit_class,
            "parser": record.parser,
            "parser_version": record.parser_version,
            "source": record.source,
            "confidence": record.confidence,
            "deadline_utc": record.parsed_deadline_utc,
            "resume_not_before_utc": record.resume_not_before_utc,
            "record_digest": record.digest(),
        })
        return record

    def schedule(self, record: LimitRecord, *, trigger_identity: str) -> ScheduledTrigger:
        """Create or idempotently REPLACE the one durable wake (S11.4 step 3/5).

        A duplicate limit event carrying the same deadline produces no second
        wake; a NEW deadline replaces the existing trigger in place under the
        same task name, so tasks never accumulate.
        """
        existing = self.trigger()
        if existing is not None and existing.consumed_at_utc == "" \
                and existing.resume_not_before_utc == record.resume_not_before_utc:
            self._audit("wake_schedule_deduplicated",
                        {"task_name": existing.task_name,
                         "resume_not_before_utc": existing.resume_not_before_utc})
            return existing
        replaced = (existing.replaced_count + 1) if existing is not None else 0
        created = ScheduledTrigger(
            task_name=WAKE_TASK_NAME,
            trigger_identity=trigger_identity,
            resume_not_before_utc=record.resume_not_before_utc,
            limit_record_digest=record.digest(),
            created_at_utc=to_utc_iso(),
            replaced_count=replaced,
        )
        self.journal.set_state(TRIGGER_KEY, created.to_dict())
        self._audit("wake_scheduled", {"task_name": created.task_name,
                                       "resume_not_before_utc": created.resume_not_before_utc,
                                       "replaced_count": replaced})
        return created

    def cancel(self, *, reason: str) -> bool:
        """Cancel the scheduled resume (emergency stop, owner command, completion)."""
        existing = self.trigger()
        if existing is None:
            return False
        self.journal.set_state(TRIGGER_KEY, None)
        self.journal.set_state(RESUME_NOT_BEFORE_KEY, "")
        self._audit("wake_cancelled", {"task_name": existing.task_name, "reason": reason})
        return True

    def mark_consumed(self) -> ScheduledTrigger | None:
        """Disable/delete the expired one-shot trigger after a successful wake."""
        existing = self.trigger()
        if existing is None:
            return None
        consumed = dataclasses.replace(existing, consumed_at_utc=to_utc_iso())
        self.journal.set_state(TRIGGER_KEY, consumed.to_dict())
        self._audit("expired_trigger_cleanup", {"task_name": consumed.task_name})
        return consumed

    def _audit(self, event: str, detail: Mapping[str, Any]) -> None:
        if self.audit is not None:
            self.audit.append(event, detail=dict(detail))


# --------------------------------------------------------------------------
# Gates: no provider contact before the deadline; suppression; revalidation
# --------------------------------------------------------------------------


def assert_may_contact_provider(journal: Any, *, now_utc: _dt.datetime) -> None:
    """Hard gate: no provider call before `resume_not_before_utc` (S11.4 step 1)."""
    raw = journal.get_state(RESUME_NOT_BEFORE_KEY, "") or ""
    if not raw:
        return
    deadline = _dt.datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    if now_utc < deadline:
        raise ScheduleError(
            "before_resume_deadline",
            f"no provider work, retry, poll, or reviewer call may happen before "
            f"{raw} (now {to_utc_iso(now_utc)}); S11.4 forbids spinning and forbids asking "
            f"a model whether it is time yet")


EMERGENCY_STOP_KEY = "emergency_stop"
MANUAL_PAUSE_KEY = "manual_pause"


@dataclasses.dataclass(frozen=True)
class Suppression:
    suppressed: bool
    reason_code: str = ""
    reason: str = ""


def wake_suppressed(journal: Any) -> Suppression:
    """Durable emergency-stop and manual-pause flags suppress any wake (S11.5)."""
    if bool(journal.get_state(EMERGENCY_STOP_KEY, False)):
        return Suppression(True, "emergency_stop",
                           "a durable emergency stop is set; a scheduled resume never fires "
                           "and never clears it")
    if bool(journal.get_state(MANUAL_PAUSE_KEY, False)):
        return Suppression(True, "manual_pause",
                           "a durable manual pause is set; the wake is suppressed until the "
                           "owner resumes explicitly")
    return Suppression(False)


#: The full revalidation set S11.4 step 5 requires BEFORE contacting Claude.
WAKE_REVALIDATION_STEPS: tuple[str, ...] = (
    "controller_manifest",
    "clock",
    "single_instance_lock",
    "task_authority",
    "worktree",
    "git_and_remote_state",
    "auth",
    "pending_action",
    "external_effect_journal",
)


@dataclasses.dataclass(frozen=True)
class WakeRevalidation:
    ok: bool
    failed_steps: tuple[str, ...] = ()
    missing_steps: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    reason: str = ""


def revalidate_at_wake(results: Mapping[str, bool], *,
                       notes: Sequence[str] = ()) -> WakeRevalidation:
    """Every step must be present AND true. A missing step fails closed."""
    missing = tuple(step for step in WAKE_REVALIDATION_STEPS if step not in results)
    failed = tuple(step for step in WAKE_REVALIDATION_STEPS
                   if step in results and not results[step])
    unknown = sorted(set(results) - set(WAKE_REVALIDATION_STEPS))
    if unknown:
        raise ScheduleError("unknown_revalidation_step",
                            f"unrecognized revalidation steps: {unknown}")
    if missing or failed:
        return WakeRevalidation(
            False, failed, missing, tuple(notes),
            f"wake revalidation refused: failed={list(failed)} missing={list(missing)}; "
            f"S11.4 requires the full set to pass BEFORE contacting the provider")
    return WakeRevalidation(True, notes=tuple(notes),
                            reason="every revalidation step passed")


#: Wall clock moving BACKWARDS relative to the observation, beyond this
#: tolerance, means the system clock jumped and a stored deadline can no longer
#: be compared safely.
CLOCK_JUMP_TOLERANCE = _dt.timedelta(minutes=5)


@dataclasses.dataclass(frozen=True)
class ClockCheck:
    ok: bool
    reason_code: str = ""
    detail: str = ""
    timezone_changed: bool = False


def check_clock(record: LimitRecord, *, now_utc: _dt.datetime,
                current_tz_name: str = "",
                monotonic_elapsed: float | None = None,
                wall_elapsed: float | None = None) -> ClockCheck:
    """Detect a clock jump and a timezone change at wake time (S11.4).

    A timezone change does NOT move the deadline - it was stored as a UTC instant
    precisely so it could not - but it is recorded. A clock that has moved
    BACKWARDS fails closed, because the deadline comparison can no longer be
    trusted.
    """
    observed = _dt.datetime.fromisoformat(record.observed_wall_clock_utc.replace("Z", "+00:00"))
    tz_changed = bool(current_tz_name and record.local_timezone
                      and current_tz_name != record.local_timezone)
    if now_utc + CLOCK_JUMP_TOLERANCE < observed:
        return ClockCheck(False, "clock_moved_backwards",
                          f"the system clock now reads {to_utc_iso(now_utc)}, earlier than "
                          f"the {record.observed_wall_clock_utc} recorded when the limit was "
                          f"observed; refusing to compare a deadline against a jumped clock",
                          tz_changed)
    if monotonic_elapsed is not None and wall_elapsed is not None:
        drift = abs(wall_elapsed - monotonic_elapsed)
        if drift > CLOCK_JUMP_TOLERANCE.total_seconds():
            return ClockCheck(False, "clock_jump",
                              f"wall-clock elapsed ({wall_elapsed:.0f}s) and monotonic "
                              f"elapsed ({monotonic_elapsed:.0f}s) differ by {drift:.0f}s; "
                              f"the system clock jumped during the wait", tz_changed)
    detail = "clock consistent with the observation"
    if tz_changed:
        detail += (f"; the local timezone changed from {record.local_timezone!r} to "
                   f"{current_tz_name!r}, which does not move the stored UTC deadline")
    return ClockCheck(True, "clock_ok", detail, tz_changed)


class MonotonicLease:
    """A lease measured with `time.monotonic` (S13.5: never wall clock).

    A DST change or a manual clock adjustment cannot extend or shorten a lease
    held through this class, because it never reads the wall clock at all.
    """

    def __init__(self, seconds: float, *, clock: Any = None) -> None:
        if seconds <= 0:
            raise ScheduleError("bad_lease", "a lease must be a positive number of seconds")
        self._clock = clock or time.monotonic
        self.seconds = float(seconds)
        self.started = self._clock()

    def remaining(self) -> float:
        return max(0.0, self.seconds - (self._clock() - self.started))

    def expired(self) -> bool:
        return self.remaining() <= 0.0

    def assert_valid(self, what: str) -> None:
        if self.expired():
            raise ScheduleError("lease_expired",
                                f"the {what} lease expired after {self.seconds}s of "
                                f"monotonic time")


# --------------------------------------------------------------------------
# Codex rate limiting (S11.4 final paragraph)
# --------------------------------------------------------------------------


def hold_for_codex_rate_limit(journal: Any, *, checkpoint_id: str, packet_digest: str,
                              resume_not_before_utc: str, audit: Any = None) -> dict[str, Any]:
    """Hold Claude at the completed checkpoint; schedule a FRESH review later.

    Never continue unreviewed, and never resume a partial review: the persisted
    packet is rerun from scratch when the reviewer is available again (S9/S11.4).
    """
    record = {
        "checkpoint_id": checkpoint_id,
        "packet_digest": packet_digest,
        "resume_not_before_utc": resume_not_before_utc,
        "recorded_at_utc": to_utc_iso(),
        "claude_held_at_checkpoint": True,
        "review_restart_policy": "fresh_process_from_persisted_packet",
        "continue_unreviewed": False,
    }
    journal.set_state(CODEX_HOLD_KEY, record)
    journal.set_state(RESUME_NOT_BEFORE_KEY, resume_not_before_utc)
    if audit is not None:
        audit.append("codex_rate_limit_hold", detail=dict(record))
    return record


#: S11.4 names these as environment switches an installed Claude version MAY
#: document. They are recorded for reverification and are NEVER set by this
#: build: enabling them is an optimization that requires capability tests first,
#: and the supervisor's durable deadline and journal remain authoritative.
DOCUMENTED_WATCHDOG_ENV: tuple[str, ...] = (
    "CLAUDE_CODE_RETRY_WATCHDOG",
    "CLAUDE_CODE_RESUME_INTERRUPTED_TURN_MAX_AGE_MS",
    "CLAUDE_CODE_RESUME_PROMPT",
)
WATCHDOG_ENV_VERIFIED_AGAINST_INSTALLED_CLI = False


def assert_no_model_switch_to_evade_limit(*, current_model: str, candidate_model: str,
                                          approved_chain: Sequence[str]) -> None:
    """Never silently switch model/account/plan to evade a limit (S11.4)."""
    if candidate_model == current_model:
        return
    if candidate_model not in tuple(approved_chain):
        raise ScheduleError(
            "unapproved_limit_evasion",
            f"switching from {current_model!r} to {candidate_model!r} to get around a usage "
            f"limit requires the owner-approved fallback list; silently changing model, "
            f"account, or plan - or purchasing usage - is forbidden (S11.4)")
