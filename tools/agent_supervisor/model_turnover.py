#!/usr/bin/env python3
"""Fable->Opus model-turnover DETECTION core (M0-T054, first increment).

Qualifying evidence (supervisor-freeze §2, AD-093): a *reproduced provider
incident*. D-010 source-028 / R289: Fable 5 hit its weekly usage limit and hard-
stopped with the exact message

    You've reached your Fable 5 limit. Run /usage-credits to continue or switch
    models with /model.

and the CLI's built-in `fallbackModel` did NOT auto-switch. This module is the
first, additive increment of an independently-live turnover controller. It is
PURE DETECTION only: no process launching, no config changes, no live provider
calls, no I/O, and no third-party dependencies. Launch/turnover ACTUATION is a
later increment and is intentionally absent here.

The one rule that governs every path is FAIL-CLOSED (AD-025, restated by the
supervisor-freeze lane): unknown, ambiguous, or contradictory evidence is NEVER
classified as exhaustion. A caller treats `AMBIGUOUS_FAIL_CLOSED` as "do NOT turn
over; preserve evidence and stop", exactly as it treats an unclassified failure.
Only a grounded, unambiguous signal - the exact weekly-limit message, or a typed
structured provider/CLI result that plainly denotes Fable usage-limit/quota
exhaustion - authorizes `FABLE_EXHAUSTED`.

This module never derives an action from a worker's free-text output: it only
classifies, and it returns a typed verdict plus a human-readable reason. It is
additive - it adds NO behavior to any existing frozen module (supervisor-freeze
§1); the parallel account-quota classifier in `claude_runner` is untouched.
"""
from __future__ import annotations

import dataclasses
import enum
import re
from typing import Any, Mapping


class ExhaustionClassification(enum.Enum):
    """The typed outcome of a turnover-detection decision.

    * ``FABLE_EXHAUSTED`` - a grounded, unambiguous Fable weekly-limit / quota
      exhaustion signal. This is the ONLY value that authorizes a turnover.
    * ``NOT_EXHAUSTED`` - a recognized non-exhaustion condition (normal success,
      an ordinary build/test/coding failure, or a permission denial). Proceed
      with ordinary handling; do not turn over.
    * ``AMBIGUOUS_FAIL_CLOSED`` - unknown, insufficient, contradictory, or merely
      limit-*looking* evidence. Never a guess at exhaustion: the caller must NOT
      turn over, and should preserve the evidence and stop.
    """

    FABLE_EXHAUSTED = "fable_exhausted"
    NOT_EXHAUSTED = "not_exhausted"
    AMBIGUOUS_FAIL_CLOSED = "ambiguous_fail_closed"


@dataclasses.dataclass(frozen=True)
class TurnoverEvidence:
    """The structured evidence a turnover decision is made from.

    Every field defaults to an "absent" value so a caller can supply only what it
    actually observed. `exit_code` is `None` when no exit code was observed (an
    unknown exit is never treated as success). `structured_result` is a typed
    provider/CLI result dict when one is available, else `None`.
    """

    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    structured_result: Mapping[str, Any] | None = None
    model_id: str = ""


@dataclasses.dataclass(frozen=True)
class ExhaustionVerdict:
    """A classification plus the reason it was reached."""

    classification: ExhaustionClassification
    reason: str

    @property
    def should_turn_over(self) -> bool:
        """True ONLY for a confirmed exhaustion; every other verdict is False."""
        return self.classification is ExhaustionClassification.FABLE_EXHAUSTED


#: The exact weekly-limit message substrings (D-010 source-028 / R289). Both the
#: contraction ("You've") and the expanded form ("You have") are accepted; a
#: typographic apostrophe is normalized to ASCII before matching (see
#: `_normalize`). The full phrase is required - a bare "limit" is never enough.
FABLE_EXHAUSTION_PHRASES: tuple[str, ...] = (
    "You've reached your Fable 5 limit",
    "You have reached your Fable 5 limit",
)

#: Typed structured provider/CLI codes that plainly denote a usage-limit / quota
#: exhaustion (NOT a transient rate limit - a 429/rate-limit is deliberately
#: excluded so a temporary throttle can never be read as an exhausted quota).
STRUCTURED_QUOTA_CODES: frozenset[str] = frozenset({
    "usage_limit_reached",
    "usage_limit_exceeded",
    "usage_limit",
    "weekly_limit_reached",
    "weekly_usage_limit_reached",
    "quota_exhausted",
    "account_quota_exhausted",
    "insufficient_quota",
})

#: Keys a structured result may carry its typed code under. Scanned in order; a
#: nested error object (e.g. ``{"error": {"type": ...}}``) is scanned one level.
_STRUCTURED_CODE_KEYS: tuple[str, ...] = (
    "code", "error_code", "reason", "reason_code",
    "type", "subtype", "error_type", "error", "status",
)

#: WEEKLY (7-day) markers on a stream ``rate_limit_event.rateLimitType`` (D-010
#: source-028 / R289; M0-T054 live proof real-fable-exhaustion-streamjson.txt). A
#: rejected rate-limit event carrying one of these is a WEEKLY usage exhaustion -
#: grounded and DISTINCT from a transient per-minute 429 throttle, which carries no
#: weekly marker and so stays fail-closed (AMBIGUOUS). This is the one narrow place
#: a rate-limit event is admitted as exhaustion; STRUCTURED_QUOTA_CODES still
#: excludes a bare 429/rate-limit precisely so a temporary throttle never qualifies.
_WEEKLY_RATE_LIMIT_MARKERS: tuple[str, ...] = ("seven_day", "week")

#: Limit/quota-*looking* wording that is NOT the confirmed weekly-limit phrase.
#: Its presence WITHOUT the confirmed phrase is suspicious, never confirmed, so
#: it fails closed to AMBIGUOUS - never FABLE_EXHAUSTED.
_LIMIT_HINT = re.compile(
    r"\b(limit|quota|out of credits|usage[- ]credits|rate[- ]limit(ed)?|429)\b",
    re.IGNORECASE,
)

#: Recognized connectivity/timeout wording - genuinely ambiguous as to
#: exhaustion, so it also fails closed to AMBIGUOUS (do not turn over; preserve).
_NETWORK_AMBIGUITY = re.compile(
    r"\b(timed out|timeout|connection (refused|reset|error|closed)|"
    r"network (error|unreachable|is unreachable)|etimedout|econnreset|"
    r"temporarily unavailable|502|503|504)\b",
    re.IGNORECASE,
)

#: Recognized permission-denied wording - an ordinary access failure, never
#: exhaustion. Classified NOT_EXHAUSTED (proceed with ordinary handling).
_PERMISSION_DENIED = re.compile(
    r"\b(permission denied|access is denied|operation not permitted|"
    r"not permitted|eacces|eperm)\b",
    re.IGNORECASE,
)


def _normalize(text: Any) -> str:
    """Coerce to text and fold typographic apostrophes to ASCII. Never raises."""
    if not isinstance(text, str):
        return ""
    # U+2019 RIGHT SINGLE QUOTATION MARK and U+02BC MODIFIER LETTER APOSTROPHE
    # both appear in CLI output where a plain "'" was meant. Built with `chr()`
    # rather than as literals so a non-ASCII byte is never invisible in review or
    # lost in a re-encoding (the same stance `claude_runner` takes for the BOM).
    return text.replace(chr(0x2019), "'").replace(chr(0x02BC), "'")


def _exit_state(code: Any) -> str:
    """"success" | "failure" | "unknown". A bool or non-int exit is unknown.

    A bool is an int subclass, so it is excluded explicitly - an exit code is a
    process integer, never a truthiness flag.
    """
    if isinstance(code, bool) or code is None:
        return "unknown"
    if isinstance(code, int):
        return "success" if code == 0 else "failure"
    return "unknown"


def _references_fable(result: Mapping[str, Any], model_id: str) -> bool:
    """True when the structured result / evidence is attributable to Fable."""
    if isinstance(model_id, str) and "fable" in model_id.lower():
        return True
    for key in ("model", "model_id", "model_name"):
        value = result.get(key)
        if isinstance(value, str) and "fable" in value.lower():
            return True
    return False


def _weekly_rate_limit_rejection(structured_result: Mapping[str, Any]) -> bool:
    """True when the structured result is a WEEKLY (7-day) rate-limit REJECTION.

    Grounded from the real stream shape (D-010 source-028 / R289; M0-T054 live
    proof): a ``rate_limit_event`` whose ``rateLimitType`` carries a weekly marker
    AND whose ``status`` is ``"rejected"``. Both the camelCase stream key
    (``rateLimitType``) and a snake_case mirror (``rate_limit_type``) are read, and a
    nested ``rate_limit_info`` object is scanned one level so the raw event shape
    works too. A transient per-minute 429 carries NO weekly marker, so it returns
    False and stays fail-closed - the deliberate 429-exclusion is preserved.
    """
    def _check(mapping: Mapping[str, Any]) -> bool:
        rlt = ""
        for key in ("rateLimitType", "rate_limit_type"):
            value = mapping.get(key)
            if isinstance(value, str) and value:
                rlt = value.lower()
                break
        if not any(marker in rlt for marker in _WEEKLY_RATE_LIMIT_MARKERS):
            return False
        status = mapping.get("status")
        return isinstance(status, str) and status.strip().lower() == "rejected"

    if _check(structured_result):
        return True
    nested = structured_result.get("rate_limit_info")
    return isinstance(nested, Mapping) and _check(nested)


def _structured_signal(
    structured_result: Any, model_id: str,
) -> tuple[str, str]:
    """Inspect a structured provider/CLI result for a typed quota-exhaustion signal.

    Returns ``(kind, reason)`` where `kind` is one of:
    * ``"fable_exhausted"`` - a recognized quota code OR a WEEKLY (7-day) rate-limit
      rejection, attributable to Fable;
    * ``"quota_unattributed"`` - the same recognized signal but one that CANNOT be
      tied to the Fable model (so it must not authorize a Fable turnover);
    * ``""`` - no recognized typed quota code and no weekly rate-limit rejection.
    """
    if not isinstance(structured_result, Mapping):
        return "", ""
    found = ""
    for key in _STRUCTURED_CODE_KEYS:
        value = structured_result.get(key)
        if isinstance(value, str) and value.strip().lower() in STRUCTURED_QUOTA_CODES:
            found = value.strip().lower()
            break
        if isinstance(value, Mapping):
            for nested_key in _STRUCTURED_CODE_KEYS:
                nested = value.get(nested_key)
                if isinstance(nested, str) and nested.strip().lower() in STRUCTURED_QUOTA_CODES:
                    found = nested.strip().lower()
                    break
            if found:
                break

    # A WEEKLY (7-day) rate-limit rejection is a grounded exhaustion even though a
    # bare 429/rate-limit is deliberately NOT in STRUCTURED_QUOTA_CODES: the weekly
    # marker + rejected status is what distinguishes an exhausted WEEKLY quota from a
    # transient per-minute throttle (M0-T054 live proof; the throttle carries neither
    # and remains fail-closed).
    weekly = _weekly_rate_limit_rejection(structured_result)
    if not found and not weekly:
        return "", ""

    if found:
        basis = f"structured typed code {found!r} denotes a Fable usage-limit/quota exhaustion"
        unattributed = (
            f"structured typed code {found!r} denotes a quota exhaustion but is not "
            f"attributable to the Fable model, so it cannot authorize a Fable turnover")
    else:  # weekly rate-limit rejection
        basis = ("a WEEKLY (7-day) rate-limit rejection denotes a Fable usage-limit "
                 "exhaustion (a transient 429 would carry no weekly marker)")
        unattributed = (
            "a WEEKLY (7-day) rate-limit rejection denotes a usage-limit exhaustion but "
            "is not attributable to the Fable model, so it cannot authorize a Fable "
            "turnover")

    if _references_fable(structured_result, model_id):
        return ("fable_exhausted", basis)
    return ("quota_unattributed", unattributed)


def _text_confirms_fable(text: str) -> str:
    """Return the exact matched weekly-limit phrase, or "" when none is present."""
    for phrase in FABLE_EXHAUSTION_PHRASES:
        if phrase in text:
            return phrase
    return ""


def classify_exhaustion(evidence: Any) -> ExhaustionVerdict:
    """Classify turnover evidence into a typed, fail-closed verdict.

    Decision order (fail-closed throughout):

    1. A grounded, unambiguous CONFIRMED signal - the exact Fable weekly-limit
       phrase, OR a typed structured quota code attributable to Fable:
         * co-occurring with a SUCCESS exit (0) -> AMBIGUOUS_FAIL_CLOSED, because
           a genuine exhaustion hard-stops the process; an exhaustion signal WITH
           a success exit is contradictory and is never trusted as exhaustion;
         * otherwise (a non-zero or unknown exit) -> FABLE_EXHAUSTED.
    2. A recognized quota code that CANNOT be tied to Fable -> AMBIGUOUS.
    3. A permission denial -> NOT_EXHAUSTED (ordinary access failure).
    4. Connectivity/timeout wording -> AMBIGUOUS (cannot confirm exhaustion).
    5. Limit/quota-*looking* wording WITHOUT the confirmed phrase -> AMBIGUOUS
       (a bare "limit" mention is never enough to guess exhaustion).
    6. Otherwise, on clean text: a success or an ordinary non-zero exit ->
       NOT_EXHAUSTED; an unknown exit with no signal at all -> AMBIGUOUS
       (insufficient evidence).

    Never raises: any unexpected input degrades to AMBIGUOUS_FAIL_CLOSED, because
    a classifier that crashed mid-decision would be a fail-OPEN shape.
    """
    try:
        if evidence is None:
            return ExhaustionVerdict(
                ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED,
                "no evidence object was supplied; insufficient evidence to classify")

        stdout = _normalize(getattr(evidence, "stdout", ""))
        stderr = _normalize(getattr(evidence, "stderr", ""))
        exit_code = getattr(evidence, "exit_code", None)
        structured_result = getattr(evidence, "structured_result", None)
        model_id = getattr(evidence, "model_id", "") or ""

        text = f"{stdout}\n{stderr}"
        exit_state = _exit_state(exit_code)

        matched_phrase = _text_confirms_fable(text)
        struct_kind, struct_reason = _structured_signal(structured_result, model_id)

        # 1. CONFIRMED, grounded, unambiguous signal.
        if matched_phrase or struct_kind == "fable_exhausted":
            if matched_phrase and struct_reason and struct_kind == "fable_exhausted":
                basis = (f"the exact Fable weekly-limit message ({matched_phrase!r}) and "
                         f"{struct_reason}")
            elif matched_phrase:
                basis = f"the exact Fable weekly-limit message ({matched_phrase!r})"
            else:
                basis = struct_reason
            if exit_state == "success":
                return ExhaustionVerdict(
                    ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED,
                    f"{basis} co-occurs with a SUCCESS exit code (0); a genuine exhaustion "
                    f"hard-stops the process, so this contradiction is never trusted as "
                    f"exhaustion")
            return ExhaustionVerdict(
                ExhaustionClassification.FABLE_EXHAUSTED,
                f"{basis} is an unambiguous Fable usage-limit exhaustion signal")

        # 2. A recognized quota code that cannot be attributed to Fable.
        if struct_kind == "quota_unattributed":
            return ExhaustionVerdict(
                ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED, struct_reason)

        # 3. Permission denial - an ordinary access failure, not exhaustion.
        if _PERMISSION_DENIED.search(text):
            return ExhaustionVerdict(
                ExhaustionClassification.NOT_EXHAUSTED,
                "a permission-denied signal is an ordinary access failure, not a usage-"
                "limit exhaustion")

        # 4. Connectivity/timeout - genuinely ambiguous as to exhaustion.
        if _NETWORK_AMBIGUITY.search(text):
            return ExhaustionVerdict(
                ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED,
                "connectivity/timeout wording cannot confirm a usage-limit exhaustion; "
                "fail closed and preserve evidence rather than turn over")

        # 5. Limit/quota-*looking* wording without the confirmed phrase.
        if _LIMIT_HINT.search(text):
            return ExhaustionVerdict(
                ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED,
                "limit/quota-looking wording is present but not the exact Fable weekly-"
                "limit message; a bare 'limit' mention is never enough to declare "
                "exhaustion")

        # 6. Clean text: decide from the exit state alone.
        if exit_state == "success":
            return ExhaustionVerdict(
                ExhaustionClassification.NOT_EXHAUSTED,
                "a clean success carries no exhaustion signal")
        if exit_state == "failure":
            return ExhaustionVerdict(
                ExhaustionClassification.NOT_EXHAUSTED,
                "an ordinary non-zero exit with no exhaustion signal is a build/test/"
                "coding failure, not a usage-limit exhaustion")
        return ExhaustionVerdict(
            ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED,
            "no exhaustion signal and no observed exit code; insufficient evidence to "
            "classify")
    except Exception:  # pragma: no cover - defensive: unknown, never a crash
        return ExhaustionVerdict(
            ExhaustionClassification.AMBIGUOUS_FAIL_CLOSED,
            "the evidence could not be inspected; failing closed to ambiguous")
