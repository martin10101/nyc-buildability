"""Deterministic correction-history integrity validation for survey facts (app-level; M2-T015 H4).

Proves, with deterministic code and no AI judgment, that a survey fact's recorded
correction history is exactly what the provenance doctrine requires
(``packages/contracts/schemas/v1/survey_evidence.schema.json`` ``correction_history``,
contract 1.0.0):

- ``original_value`` is IMMUTABLE: a correction changes ``normalized_value``/``units``
  only, an entry can never carry (let alone rewrite) the original detection, and a
  record whose original no longer matches the independently held original fails closed
  as tampered.
- The history is APPEND-ONLY: an accepted entry is never edited, deleted, reordered,
  replaced, or displaced by insertion (:func:`validate_history_extension`).
- Entries are strictly chronological, oldest first; a back-dated, reordered, or
  same-instant pair cannot prove its own sequence and fails closed.
- The states CHAIN: every ``previous_normalized_value``/``previous_units`` must equal
  exactly the state the immediately preceding correction produced (or the stated
  pre-correction baseline for the first entry), every corrected value/units becomes the
  next state, and the latest corrected value/units must equal the record's current
  ``normalized_value``/``units`` — nothing else may have written the current state.
- Correcting authority is a CLOSED HUMAN model: the role vocabulary is exactly
  ``user`` / ``qualified_professional`` (exact match, no aliases), and the principal
  model (:class:`CorrectingPrincipal`) has NO automated member at all, so an AI, model,
  agent, service, or system principal is unrepresentable as a correcting authority and
  can never author or impersonate a human correction (CLAUDE.md principle 1;
  deterministic re-extraction mints new evidence records, never corrections).
- Qualified-professional corrections and confirmations carry required IDENTITY and
  TIME evidence: a professional correction without ``corrected_by``, and a
  confirmed/rejected state without a non-empty ``confirmed_by`` and a well-formed
  ``confirmed_at``, fail closed to review. (The wire keeps ``corrected_by`` optional
  because the identity scheme is B-001-blocked; this application rule is stricter
  WITHOUT changing the wire.)

NOTHING here changes the wire contract: no wire field, type, or pattern moves. This
module is the application-level authority on correction-history integrity — exactly the
role :mod:`app.documents.units` plays for normalized values, whose typed-result pattern
(frozen value results, refusal-as-value, exact match only) it reuses.

Fail-closed rule: a malformed, ambiguous, inconsistent, or tampered history can NEVER
resolve. Every such submission yields the typed, visible
:class:`UnresolvedCorrectionHistory` RESULT — a value, deliberately not an exception —
carrying only the verbatim submission (``repr``) and a stated reason, and no validated
state at all, so downstream code has nothing it could ever promote. Timestamps are
compared as parsed RFC 3339 instants (offset-aware, so an offset can never mask a
reversal); values are compared with strict JSON equality in which a boolean is never
equal to a number.
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone

__all__ = [
    "CorrectingActorRole",
    "CorrectingActorValidation",
    "CorrectingPrincipal",
    "CorrectionHistoryValidation",
    "HistoryExtensionValidation",
    "NormalizationBaseline",
    "OriginalValueReference",
    "ProfessionalConfirmationState",
    "ProfessionalConfirmationValidation",
    "RFC3339_DATE_TIME_PATTERN",
    "UnresolvedCorrectionHistory",
    "ValidatedCorrectingActor",
    "ValidatedCorrectionEntry",
    "ValidatedCorrectionHistory",
    "ValidatedHistoryExtension",
    "ValidatedProfessionalConfirmation",
    "validate_correcting_actor",
    "validate_correction_history",
    "validate_history_extension",
    "validate_professional_confirmation",
]

#: RFC 3339 wire form of survey_evidence.schema.json / common.schema.json date_time,
#: with capture groups so parsing is deterministic and version-independent.
RFC3339_DATE_TIME_PATTERN = re.compile(
    r"^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})"
    r"(?:\.([0-9]+))?(Z|[+-][0-9]{2}:[0-9]{2})$"
)


@enum.unique
class CorrectingActorRole(enum.Enum):
    """Closed role vocabulary of ``corrected_by_role`` (wire enum, verbatim).

    Exactly the two HUMAN authorities of the confirm/correct flow. Exact match only —
    no case folding, aliasing, or interpretation — so any AI, model, agent, system, or
    service identity is refused, never coerced into a human role.
    """

    USER = "user"
    QUALIFIED_PROFESSIONAL = "qualified_professional"


@enum.unique
class CorrectingPrincipal(enum.Enum):
    """Closed model of authenticated principals that may author a correction.

    DELIBERATELY has no automated member: an AI, model, agent, service, or system
    principal is unrepresentable as a correcting authority, so it can never author a
    correction under any claimed role. The vocabulary extends ADDITIVELY only, with the
    auth design that grounds a new HUMAN member (identity scheme: B-001).
    """

    HUMAN_USER = "human_user"
    HUMAN_QUALIFIED_PROFESSIONAL = "human_qualified_professional"


#: The single role each principal's authority grants — claiming any other role is
#: impersonation and is refused.
_GRANTED_ROLE = {
    CorrectingPrincipal.HUMAN_USER: CorrectingActorRole.USER,
    CorrectingPrincipal.HUMAN_QUALIFIED_PROFESSIONAL: CorrectingActorRole.QUALIFIED_PROFESSIONAL,
}


@enum.unique
class ProfessionalConfirmationState(enum.Enum):
    """Closed state vocabulary of ``professional_confirmation.state`` (wire enum,
    verbatim). Only a qualified human — never AI, never a confidence score, never a
    passing check alone — moves a fact out of ``unconfirmed``."""

    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


_ENTRY_REQUIRED_KEYS = frozenset(
    {
        "corrected_at",
        "corrected_by_role",
        "previous_normalized_value",
        "corrected_normalized_value",
        "previous_units",
        "corrected_units",
        "reason",
    }
)
_ENTRY_OPTIONAL_KEYS = frozenset({"corrected_by"})

_CONFIRMATION_REQUIRED_KEYS = frozenset({"state", "confirmed_by", "confirmed_at"})
_CONFIRMATION_OPTIONAL_KEYS = frozenset({"note"})


# --------------------------------------------------------------- caller references


@dataclass(frozen=True)
class OriginalValueReference:
    """Independently held copy of the immutable original detection (e.g. from the
    stored immutable original / a prior accepted snapshot of this evidence record),
    supplied so the validator can prove the record's ``original_value`` was never
    touched. Wrapping the value keeps 'no reference available' (``None`` argument)
    distinct from 'the original is JSON null'."""

    original_value: object


@dataclass(frozen=True)
class NormalizationBaseline:
    """The deterministic PRE-correction normalization state of the record (the
    ``normalized_value``/``units`` produced by extraction-path normalization before any
    human correction). Both fields are stated together — even a unitless baseline
    states ``units`` as an explicit ``None`` — mirroring the wire's rule that absence
    of units is always a visible statement."""

    normalized_value: object
    units: str | None


# ------------------------------------------------------------------ typed results


@dataclass(frozen=True)
class ValidatedCorrectionEntry:
    """One RESOLVED correction entry, exactly as recorded — nothing normalized,
    trimmed, or converted; ``corrected_by_role`` is the typed closed-vocabulary
    member."""

    corrected_at: str
    corrected_by_role: CorrectingActorRole
    corrected_by: str | None
    previous_normalized_value: object
    corrected_normalized_value: object
    previous_units: str | None
    corrected_units: str | None
    reason: str

    resolved = True


@dataclass(frozen=True)
class ValidatedCorrectionHistory:
    """Typed RESOLVED correction history: every entry well-formed, strictly
    chronological, chain-consistent, and in agreement with the record's current
    state. ``correction_count`` is a lossless read of ``len(entries)``."""

    entries: tuple[ValidatedCorrectionEntry, ...]
    correction_count: int

    resolved = True


@dataclass(frozen=True)
class ValidatedHistoryExtension:
    """Typed RESOLVED append-only extension: the accepted history is an exact,
    untouched prefix of the submission; only appended entries follow it."""

    accepted_entry_count: int
    appended_entry_count: int

    resolved = True


@dataclass(frozen=True)
class ValidatedCorrectingActor:
    """Typed RESOLVED correcting actor: a human principal whose granted authority
    exactly matches the claimed role, with identity evidence where required."""

    role: CorrectingActorRole
    actor_id: str | None

    resolved = True


@dataclass(frozen=True)
class ValidatedProfessionalConfirmation:
    """Typed RESOLVED professional-confirmation state, exactly as recorded, with the
    identity/time evidence rule for confirmed/rejected states already proven."""

    state: ProfessionalConfirmationState
    confirmed_by: str | None
    confirmed_at: str | None

    resolved = True


@dataclass(frozen=True)
class UnresolvedCorrectionHistory:
    """Typed refusal of a correction history, extension, actor claim, or confirmation
    that cannot be proven intact — a visible RESULT that can NEVER be promoted.

    Deliberately a value, not a ``DocumentIngestionError`` subclass and never raised
    (mirrors :class:`app.documents.units.UnresolvedNormalizedValue`): a malformed,
    inconsistent, or tampered history is a routine fail-closed outcome the caller must
    handle and surface — typed rejection, route to review — not a crash. The result
    carries ONLY the verbatim submission (``repr``) and the stated reason: it has no
    validated entries, no actor authority, and no confirmation state, so there is
    nothing downstream code could promote into a material buildability input. The
    payload is metadata only and safe to serialize into an API response or audit
    record.
    """

    submitted: str
    reason: str

    resolved = False
    promotable = False
    reject_code = "unresolved_correction_history"

    def to_payload(self) -> dict:
        """Structured refusal payload (metadata only, JSON-serializable)."""
        return {
            "reject_code": self.reject_code,
            "submitted": self.submitted,
            "reason": self.reason,
        }


CorrectionHistoryValidation = ValidatedCorrectionHistory | UnresolvedCorrectionHistory
HistoryExtensionValidation = ValidatedHistoryExtension | UnresolvedCorrectionHistory
CorrectingActorValidation = ValidatedCorrectingActor | UnresolvedCorrectionHistory
ProfessionalConfirmationValidation = (
    ValidatedProfessionalConfirmation | UnresolvedCorrectionHistory
)


# ---------------------------------------------------------------------- helpers


def _refuse(submitted: object, reason: str) -> UnresolvedCorrectionHistory:
    return UnresolvedCorrectionHistory(submitted=repr(submitted), reason=reason)


def _json_equal(a: object, b: object) -> bool:
    """Strict JSON-value equality: a boolean is NEVER equal to a number (Python's
    ``True == 1`` would silently conflate distinct JSON values), numbers compare by
    numeric value, containers compare recursively, everything else requires identical
    types. Used for every chain/prefix/original comparison so a type-swapped tamper
    can never pass as 'equal'."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if type(a) is not type(b):
        return False
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_json_equal(a[key], b[key]) for key in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b, strict=False))
    return a == b


def _parse_rfc3339(value: object, field: str) -> datetime | str:
    """The offset-aware parsed instant, or the refusal reason string.

    Deterministic component parsing (no version-dependent ``fromisoformat`` dialects).
    Fractional digits beyond microseconds are truncated for comparison, so two
    timestamps equal at microsecond precision are treated as the same instant — which
    the chronology rule then refuses as ambiguous, fail-closed.
    """
    if not isinstance(value, str):
        return (
            f"{field} must be an RFC 3339 date-time string, got {type(value).__name__}"
        )
    match = RFC3339_DATE_TIME_PATTERN.fullmatch(value)
    if match is None:
        return (
            f"{field} {value!r} is not the RFC 3339 wire form required by "
            "survey_evidence.schema.json (e.g. '2026-08-01T12:00:00Z')"
        )
    year, month, day, hour, minute, second = (int(match.group(i)) for i in range(1, 7))
    fraction = match.group(7)
    microsecond = int((fraction + "000000")[:6]) if fraction else 0
    offset_text = match.group(8)
    try:
        if offset_text == "Z":
            tzinfo = UTC
        else:
            sign = 1 if offset_text[0] == "+" else -1
            delta = timedelta(
                hours=int(offset_text[1:3]), minutes=int(offset_text[4:6])
            )
            tzinfo = timezone(sign * delta)
        return datetime(year, month, day, hour, minute, second, microsecond, tzinfo)
    except ValueError:
        return f"{field} {value!r} is not a real calendar date-time"


def _validate_entry(
    entry: object, index: int
) -> tuple[ValidatedCorrectionEntry, datetime] | str:
    """One entry's internal shape: the typed entry with its parsed instant, or the
    refusal reason. Chain and chronology checks against neighbours live in
    :func:`validate_correction_history`."""
    prefix = f"correction_history[{index}]"
    if not isinstance(entry, dict):
        return (
            f"{prefix} must be a correction-entry object, got {type(entry).__name__} "
            "— a non-object entry cannot be a recorded human correction"
        )
    keys = set(entry)
    missing = _ENTRY_REQUIRED_KEYS - keys
    if missing:
        return (
            f"{prefix} is missing required key(s) {sorted(missing)}: every correction "
            "states its time, authority, both states, both unit statements, and its "
            "reason — a partial entry is not reconstructable and fails closed"
        )
    unknown = keys - _ENTRY_REQUIRED_KEYS - _ENTRY_OPTIONAL_KEYS
    if unknown:
        return (
            f"{prefix} carries key(s) {sorted(unknown)} outside the closed "
            "correction-entry contract: an undocumented key can smuggle state "
            "(including any attempt to rewrite original_value, which no correction "
            "may ever touch) and is refused as tampering"
        )
    parsed_at = _parse_rfc3339(entry["corrected_at"], f"{prefix}.corrected_at")
    if isinstance(parsed_at, str):
        return parsed_at
    role_value = entry["corrected_by_role"]
    if not isinstance(role_value, str):
        return (
            f"{prefix}.corrected_by_role must be a string role, got "
            f"{type(role_value).__name__}"
        )
    try:
        role = CorrectingActorRole(role_value)
    except ValueError:
        supported = ", ".join(sorted(member.value for member in CorrectingActorRole))
        return (
            f"{prefix}.corrected_by_role {role_value!r} is outside the closed "
            f"human-authority vocabulary (supported: {supported}); exact match only — "
            "no AI, model, agent, system, or service identity can ever author a "
            "correction, and deterministic re-extraction mints NEW evidence records "
            "instead of corrections"
        )
    if "corrected_by" in entry:
        submitted_by = entry["corrected_by"]
        if not isinstance(submitted_by, str) or not submitted_by.strip():
            return (
                f"{prefix}.corrected_by, when present, must be a non-empty actor "
                "identifier string — a null or blank identity is not identity evidence"
            )
        corrected_by: str | None = submitted_by
    else:
        corrected_by = None
    if role is CorrectingActorRole.QUALIFIED_PROFESSIONAL and corrected_by is None:
        return (
            f"{prefix} claims qualified_professional authority without corrected_by "
            "identity evidence: a professional correction must be attributable to the "
            "specific qualified human who made it, so it fails closed to review"
        )
    previous_units = entry["previous_units"]
    corrected_units = entry["corrected_units"]
    for key, value in (
        ("previous_units", previous_units),
        ("corrected_units", corrected_units),
    ):
        if value is not None and not isinstance(value, str):
            return (
                f"{prefix}.{key} must be the stated unit string or an explicit null "
                f"(the visible 'unitless' statement), got {type(value).__name__}"
            )
    reason = entry["reason"]
    if not isinstance(reason, str) or not reason.strip():
        return (
            f"{prefix}.reason must be a non-empty human-readable reason: a correction "
            "with no stated reason is not reviewable and is refused"
        )
    previous_value = entry["previous_normalized_value"]
    corrected_value = entry["corrected_normalized_value"]
    if _json_equal(previous_value, corrected_value) and previous_units == corrected_units:
        return (
            f"{prefix} changes neither the normalized value nor the units: a no-op "
            "'correction' is ambiguous (affirming an unchanged value is professional "
            "confirmation, not a correction) and fails closed"
        )
    return (
        ValidatedCorrectionEntry(
            corrected_at=entry["corrected_at"],
            corrected_by_role=role,
            corrected_by=corrected_by,
            previous_normalized_value=previous_value,
            corrected_normalized_value=corrected_value,
            previous_units=previous_units,
            corrected_units=corrected_units,
            reason=reason,
        ),
        parsed_at,
    )


# ------------------------------------------------------------------- validators


def validate_correction_history(
    *,
    original_value: object,
    normalized_value: object,
    units: object,
    correction_history: object,
    expected_original: OriginalValueReference | None = None,
    baseline: NormalizationBaseline | None = None,
) -> CorrectionHistoryValidation:
    """Validate one record's ``correction_history`` integrity against its current state.

    The first four keyword-only arguments are the record's own wire fields, verbatim.
    ``expected_original``, when the caller holds an independent copy of the immutable
    original detection, proves ``original_value`` was never touched. ``baseline``, when
    the caller can state the deterministic pre-correction normalization state, anchors
    the FIRST entry's previous value/units (and, for a never-corrected record, the
    current value/units) to it; both cross-checks are corroboration — the internal
    chain, chronology, and latest-state agreement are always enforced.

    Returns :class:`ValidatedCorrectionHistory` only when every entry is well-formed
    against the closed entry contract, entries are strictly chronological, every
    ``previous_*`` matches the immediately preceding state, every corrected state
    becomes the next state, and the latest corrected value/units equal the record's
    current ``normalized_value``/``units``. Never raises — every malformed,
    inconsistent, or tampered submission becomes the typed
    :class:`UnresolvedCorrectionHistory`, so a broken history can never resolve, crash
    ingestion, or slip through as a material buildability input.
    """
    if units is not None and not isinstance(units, str):
        return _refuse(
            units,
            "the record's units must be the stated unit string or an explicit null, "
            f"got {type(units).__name__} — a non-wire units shape cannot anchor the "
            "history's latest-state agreement",
        )
    if expected_original is not None and not _json_equal(
        original_value, expected_original.original_value
    ):
        return _refuse(
            original_value,
            "original_value is immutable: the record's original detection no longer "
            "matches the independently held original; corrections may change "
            "normalized_value and units only, never the original detection — refused "
            "as tampering",
        )
    if not isinstance(correction_history, list):
        return _refuse(
            correction_history,
            "correction_history must be the wire array of correction entries (an "
            f"empty array means 'never corrected'), got {type(correction_history).__name__}",
        )
    validated: list[ValidatedCorrectionEntry] = []
    instants: list[datetime] = []
    for index, entry in enumerate(correction_history):
        result = _validate_entry(entry, index)
        if isinstance(result, str):
            return _refuse(correction_history, result)
        entry_result, at = result
        if instants and at <= instants[-1]:
            return _refuse(
                correction_history,
                f"correction_history[{index}] at {entry_result.corrected_at!r} does "
                f"not strictly follow correction_history[{index - 1}] at "
                f"{validated[-1].corrected_at!r}: entries must be strictly "
                "chronological, oldest first — a reordered, back-dated, or "
                "same-instant pair cannot prove which state came first and fails "
                "closed",
            )
        if validated:
            prior = validated[-1]
            if not _json_equal(
                entry_result.previous_normalized_value, prior.corrected_normalized_value
            ):
                return _refuse(
                    correction_history,
                    f"correction_history[{index}].previous_normalized_value does not "
                    f"match correction_history[{index - 1}].corrected_normalized_value: "
                    "every correction must start from exactly the state the preceding "
                    "correction produced — a broken chain means an entry was edited, "
                    "deleted, inserted, or forged, and the history fails closed",
                )
            if entry_result.previous_units != prior.corrected_units:
                return _refuse(
                    correction_history,
                    f"correction_history[{index}].previous_units does not match "
                    f"correction_history[{index - 1}].corrected_units: every "
                    "correction must start from exactly the units the preceding "
                    "correction produced — a broken chain fails closed",
                )
        elif baseline is not None:
            if not _json_equal(
                entry_result.previous_normalized_value, baseline.normalized_value
            ):
                return _refuse(
                    correction_history,
                    "correction_history[0].previous_normalized_value does not match "
                    "the stated pre-correction baseline: the first correction must "
                    "start from exactly the deterministic normalization state — a "
                    "mismatch means a leading entry was deleted or the history was "
                    "forged, and it fails closed",
                )
            if entry_result.previous_units != baseline.units:
                return _refuse(
                    correction_history,
                    "correction_history[0].previous_units does not match the stated "
                    "pre-correction baseline units — fails closed like a baseline "
                    "value mismatch",
                )
        validated.append(entry_result)
        instants.append(at)
    if not validated:
        if baseline is not None and (
            not _json_equal(normalized_value, baseline.normalized_value)
            or units != baseline.units
        ):
            return _refuse(
                correction_history,
                "a never-corrected record's current normalized_value/units must still "
                "be its deterministic pre-correction baseline: a changed value with an "
                "empty correction_history means the state was written without a "
                "recorded correction, and it fails closed",
            )
        return ValidatedCorrectionHistory(entries=(), correction_count=0)
    latest = validated[-1]
    if not _json_equal(latest.corrected_normalized_value, normalized_value):
        return _refuse(
            correction_history,
            "the latest correction's corrected_normalized_value does not match the "
            "record's current normalized_value: the current state must be exactly the "
            "state the last recorded correction produced — nothing else may have "
            "written it, and a trailing entry may never be deleted — so the history "
            "fails closed",
        )
    if latest.corrected_units != units:
        return _refuse(
            correction_history,
            "the latest correction's corrected_units does not match the record's "
            "current units: the current units must be exactly the units the last "
            "recorded correction produced, so the history fails closed",
        )
    return ValidatedCorrectionHistory(
        entries=tuple(validated), correction_count=len(validated)
    )


def validate_history_extension(
    accepted_history: object, submitted_history: object
) -> HistoryExtensionValidation:
    """Prove a submitted history is an APPEND-ONLY extension of the accepted one.

    The accepted history (the last accepted/stored state of the record's
    ``correction_history``) must be an exact, position-preserving prefix of the
    submission under strict JSON equality: fewer entries is deletion, a differing
    prefix entry is an edit/reorder/replacement/insertion, and all are refused as
    tampering. This function proves ONLY append-only integrity; the full record — with
    the appended entries — must still resolve through
    :func:`validate_correction_history`, so a well-appended but chain-breaking or
    back-dated entry still fails closed there. Never raises.
    """
    if not isinstance(accepted_history, list):
        return _refuse(
            accepted_history,
            "the accepted history must be the recorded wire array of correction "
            f"entries, got {type(accepted_history).__name__}",
        )
    if not isinstance(submitted_history, list):
        return _refuse(
            submitted_history,
            "the submitted history must be the wire array of correction entries, got "
            f"{type(submitted_history).__name__}",
        )
    if len(submitted_history) < len(accepted_history):
        return _refuse(
            submitted_history,
            f"append-only violated: the accepted history has {len(accepted_history)} "
            f"entr(y/ies) but the submission has {len(submitted_history)} — deleting "
            "or truncating an accepted correction is refused as tampering",
        )
    for index, accepted_entry in enumerate(accepted_history):
        if not _json_equal(accepted_entry, submitted_history[index]):
            return _refuse(
                submitted_history,
                f"append-only violated at accepted entry {index}: accepted entries "
                "are immutable and keep their position; an edited, reordered, "
                "replaced, or displaced (inserted-before) entry is refused as "
                "tampering",
            )
    return ValidatedHistoryExtension(
        accepted_entry_count=len(accepted_history),
        appended_entry_count=len(submitted_history) - len(accepted_history),
    )


def validate_correcting_actor(
    claimed_role: object, principal_kind: object, actor_id: object
) -> CorrectingActorValidation:
    """Validate one correction submission's actor against the closed authority model.

    ``claimed_role`` is the ``corrected_by_role`` the submission wants to record;
    ``principal_kind`` is the authenticated principal classification the submission
    channel resolved (NEVER self-declared by the payload); ``actor_id`` is the
    authenticated actor identifier, or ``None`` when the identity scheme cannot state
    one (B-001). The parameters deliberately have no defaults — even an absent
    identity must be stated explicitly.

    The principal model contains only human members, so an AI, model, agent, service,
    or system principal is refused outright — it can never author or impersonate a
    human correction. A human principal claiming a role its authority does not grant
    (either direction) is impersonation and is refused. A qualified-professional
    principal must carry a non-empty ``actor_id`` (identity evidence); the same closed
    model gates professional confirmations, so no automated principal can confirm a
    fact either. Never raises.
    """
    submitted = (claimed_role, principal_kind, actor_id)
    if not isinstance(principal_kind, str):
        principal: CorrectingPrincipal | None = None
    else:
        try:
            principal = CorrectingPrincipal(principal_kind)
        except ValueError:
            principal = None
    if principal is None:
        supported = ", ".join(sorted(member.value for member in CorrectingPrincipal))
        return _refuse(
            submitted,
            f"correcting principal {principal_kind!r} is outside the closed "
            f"human-authority model (supported: {supported}); AI, model, agent, "
            "service, and system principals are unrepresentable as correcting "
            "authorities and can never author or impersonate a human correction",
        )
    if not isinstance(claimed_role, str):
        return _refuse(
            submitted,
            "claimed correction role must be a string role, got "
            f"{type(claimed_role).__name__}",
        )
    try:
        role = CorrectingActorRole(claimed_role)
    except ValueError:
        supported = ", ".join(sorted(member.value for member in CorrectingActorRole))
        return _refuse(
            submitted,
            f"claimed correction role {claimed_role!r} is outside the closed role "
            f"vocabulary (supported: {supported}); exact match only — no alias, case, "
            "or whitespace interpretation",
        )
    if _GRANTED_ROLE[principal] is not role:
        return _refuse(
            submitted,
            f"principal {principal.value!r} does not hold {role.value!r} authority: "
            "writing a correction under another authority's role is impersonation "
            "and is refused",
        )
    if actor_id is not None and (not isinstance(actor_id, str) or not actor_id.strip()):
        return _refuse(
            submitted,
            "actor_id, when stated, must be a non-empty identifier string — a blank "
            "or non-string identity is not identity evidence",
        )
    if principal is CorrectingPrincipal.HUMAN_QUALIFIED_PROFESSIONAL and actor_id is None:
        return _refuse(
            submitted,
            "a qualified-professional correction or confirmation requires actor "
            "identity evidence (a non-empty actor_id); anonymous professional "
            "authority fails closed to review",
        )
    return ValidatedCorrectingActor(role=role, actor_id=actor_id)


def validate_professional_confirmation(
    confirmation: object,
) -> ProfessionalConfirmationValidation:
    """Validate one record's ``professional_confirmation`` identity and time evidence.

    ``unconfirmed`` must carry NO evidence (``confirmed_by`` and ``confirmed_at`` both
    null — an unconfirmed fact claiming evidence is inconsistent and refused as
    tampering). ``confirmed``/``rejected`` must carry BOTH: a non-empty
    ``confirmed_by`` identity and a well-formed RFC 3339 ``confirmed_at``. The state
    vocabulary and key set are closed: only a qualified human — never AI, never a
    confidence score, never a passing check alone — moves a fact out of
    ``unconfirmed``, and the submission channel gates that authority through the same
    closed principal model as :func:`validate_correcting_actor`. Never raises.
    """
    if not isinstance(confirmation, dict):
        return _refuse(
            confirmation,
            "professional_confirmation must be the wire confirmation object, got "
            f"{type(confirmation).__name__}",
        )
    keys = set(confirmation)
    missing = _CONFIRMATION_REQUIRED_KEYS - keys
    if missing:
        return _refuse(
            confirmation,
            f"professional_confirmation is missing required key(s) {sorted(missing)}: "
            "the confirmation state is always fully stated, never inferred",
        )
    unknown = keys - _CONFIRMATION_REQUIRED_KEYS - _CONFIRMATION_OPTIONAL_KEYS
    if unknown:
        return _refuse(
            confirmation,
            f"professional_confirmation carries key(s) {sorted(unknown)} outside the "
            "closed confirmation contract — an undocumented key can smuggle state and "
            "is refused as tampering",
        )
    state_value = confirmation["state"]
    if not isinstance(state_value, str):
        return _refuse(
            confirmation,
            "professional_confirmation.state must be a string state, got "
            f"{type(state_value).__name__}",
        )
    try:
        state = ProfessionalConfirmationState(state_value)
    except ValueError:
        supported = ", ".join(
            sorted(member.value for member in ProfessionalConfirmationState)
        )
        return _refuse(
            confirmation,
            f"professional_confirmation.state {state_value!r} is outside the closed "
            f"state vocabulary (supported: {supported}); exact match only — no AI, "
            "score, or check outcome can define a confirmation state",
        )
    confirmed_by = confirmation["confirmed_by"]
    confirmed_at = confirmation["confirmed_at"]
    if "note" in confirmation:
        note = confirmation["note"]
        if note is not None and not isinstance(note, str):
            return _refuse(
                confirmation,
                "professional_confirmation.note, when present, must be a string or "
                f"null, got {type(note).__name__}",
            )
    if state is ProfessionalConfirmationState.UNCONFIRMED:
        if confirmed_by is not None or confirmed_at is not None:
            return _refuse(
                confirmation,
                "an unconfirmed fact cannot carry confirmed_by/confirmed_at evidence: "
                "confirmation evidence exists exactly when a qualified professional "
                "has acted, so an inconsistent state is refused as tampering",
            )
        return ValidatedProfessionalConfirmation(
            state=state, confirmed_by=None, confirmed_at=None
        )
    if not isinstance(confirmed_by, str) or not confirmed_by.strip():
        return _refuse(
            confirmation,
            f"a {state.value!r} state requires confirmed_by identity evidence (a "
            "non-empty qualified-professional identifier); anonymous professional "
            "authority fails closed to review",
        )
    parsed_at = _parse_rfc3339(confirmed_at, "professional_confirmation.confirmed_at")
    if isinstance(parsed_at, str):
        return _refuse(
            confirmation,
            f"a {state.value!r} state requires well-formed time evidence: {parsed_at}",
        )
    return ValidatedProfessionalConfirmation(
        state=state, confirmed_by=confirmed_by, confirmed_at=confirmed_at
    )
