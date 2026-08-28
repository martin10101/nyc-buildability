"""Passive natural-event watcher + pending_live_observation register (D-024 Amendment 7).

M0-T096 unit I (qualifying evidence D-024-R106; Amendment-7 rows R224-R227).

Lane 2 of the Amendment-7 evidence split: the genuine live Fable 5 refusal /
quota / availability / model-turnover canary stays ``pending_live_observation``
until it naturally occurs (R224).  This module is the durable, bounded
detection-and-capture path (R226): it READS records the supervisor already
writes (R225 - the guardrail-refusal journal rows, the worker-turnover
transitions, the usage-limit record, the provider-abort record, and the
model-change audit list) and persists at most ONE sanitized register row per
distinct event.  It never prompts, never messages a worker, never spawns a
process, and never injects anything into any model context.

Authority boundary (unusual, so stated here): NOTHING in this module can
verify, graduate, or actuate anything.  ``verified_live`` is a constant
``False`` on every row this module writes; graduating a corpus shape remains
the owner-reviewed capture step documented in the shape fixture's own
``upgrade_procedure`` (R227 compare-then-graduate), and live 4.8-bridge
actuation stays behind ``refusal_bridge.assert_actuation_permitted``'s double
gate (measured-live shape AND R595) plus R187.  Evidence labeling (R223) is a
closed vocabulary: rows are ``injected`` (fail-closed default; anything born
of a fixture or an injected session) or ``live_candidate`` (observed during a
session declared live, still requiring owner review) - never ``live``.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from . import refusal_bridge
from .models import digest_of, to_utc_iso
from .operator_status import fact, unknown
from .outage_policy import BLOCKED_KEY as _OUTAGE_BLOCKED_KEY
from .outage_policy import RETRY_KEY as _OUTAGE_RETRY_KEY
from .preflight import probe_record
from .resume_scheduler import LIMIT_RECORD_KEY as _USAGE_LIMIT_KEY
from .rotation import PROVIDER_ABORT_KEY as _PROVIDER_ABORT_KEY
from .telemetry_redaction import sanitize_structure
from .worker_turnover import REASON_TURNOVER_LAUNCHED, REASON_TURNOVER_RECORDED

SCHEMA = "pending_live_observation/v1"

#: Register rows: ``pending_live_observation/<observation_digest>``.
OBSERVATION_KEY_PREFIX = "pending_live_observation/"
LAST_OBSERVATION_KEY = "pending_live_observation_last_digest"
#: The durable statement of WHAT is still awaited (R224).
REGISTER_KEY = "pending_live_observation_register"

# Closed event vocabulary (the Amendment-7 sentence: "quota, refusal,
# availability, or model-turnover event").
EVENT_GUARDRAIL_REFUSAL = "guardrail_refusal"
EVENT_QUOTA_EXHAUSTION = "quota_exhaustion"
EVENT_AVAILABILITY = "availability"
EVENT_MODEL_TURNOVER = "model_turnover"
EVENT_TYPES = (EVENT_GUARDRAIL_REFUSAL, EVENT_QUOTA_EXHAUSTION,
               EVENT_AVAILABILITY, EVENT_MODEL_TURNOVER)

# Closed evidence-class vocabulary (R223).  There is deliberately no "live"
# value: code cannot certify liveness, only an owner-reviewed capture can.
EVIDENCE_INJECTED = "injected"
EVIDENCE_LIVE_CANDIDATE = "live_candidate"
EVIDENCE_CLASSES = (EVIDENCE_INJECTED, EVIDENCE_LIVE_CANDIDATE)

PROVENANCE_LIVE = "live"
PROVENANCE_INJECTED = "injected"
_PROVENANCES = (PROVENANCE_LIVE, PROVENANCE_INJECTED)

#: Source records that mark themselves injected (harness reference rows and
#: any future fixture-born record) are ALWAYS classed injected, even when the
#: scanning session declares itself live (R223 fail-closed direction).
INJECTED_MARKER_KEY = "injected"
#: Harness-born records carry this marker in their text (the golden-run fakes
#: stamp every summary/refusal they emit).  Scanning for it is the mechanical
#: R223 backstop: a fixture-born event observed by a live-session scan is
#: still classed injected.  The failure direction is conservative - a natural
#: event whose text somehow contained the marker would be under-labeled
#: (injected), which can never graduate anything.
INJECTED_TEXT_MARKER = "INJECTED-GOLDEN-RUN"

#: The three observations D-024 Amendment 7 leaves pending (owner report
#: sections 2-3).  ``feature_gated`` names the ONLY capability each one gates
#: (R228); everything else in the loop proceeds on injected proof.
AWAITED_OBSERVATIONS = (
    {"observation": "live_refusal_shape_confirmation",
     "event_type": EVENT_GUARDRAIL_REFUSAL,
     "feature_gated": "recognized-refusal shape corpus graduation "
                      "(fixture upgrade_procedure; owner-reviewed)"},
    {"observation": "measured_live_bridge_precondition",
     "event_type": EVENT_GUARDRAIL_REFUSAL,
     "feature_gated": "automatic 4.8 bridge live actuation "
                      "(assert_actuation_permitted: measured-live AND R595)"},
    {"observation": "natural_quota_or_model_turnover",
     "event_type": EVENT_MODEL_TURNOVER,
     "feature_gated": "none - detect-and-hold + record-intent already proven "
                      "injected; observation is confirmatory (R228)"},
)


class ObservationError(ValueError):
    """A watcher-boundary violation (bad provenance, bad source shape)."""


def _require_provenance(session_provenance: str) -> None:
    if session_provenance not in _PROVENANCES:
        raise ObservationError(
            f"session_provenance must be one of {_PROVENANCES}, "
            f"got {session_provenance!r} (R223: labeling is never guessed)")


def installed_version_shape(journal: Any) -> str:
    """The installed-version shape (R226 field 2), from the PERSISTED probe.

    The watcher must not execute a subprocess, so this reads the capability
    probe the preflight already recorded; absent means ``unknown`` - never a
    guessed or invented version.
    """
    record = probe_record(journal, "claude_version")
    if isinstance(record, Mapping):
        value = record.get("value") or record.get("version")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


# --------------------------------------------------------------------------
# Read-only discovery over the existing durable records (R225)
# --------------------------------------------------------------------------


def discover_events(journal: Any) -> tuple[dict[str, Any], ...]:
    """Scan the EXISTING durable records for natural-event evidence.

    Read-only: getter calls only (``all_state``/``get_state``/``transitions``).
    Returns plain source descriptors; nothing is written here.
    """
    sources: list[dict[str, Any]] = []
    state = journal.all_state()

    for key, record in sorted(state.items()):
        if key.startswith(refusal_bridge.REFUSAL_RECORD_KEY_PREFIX):
            if isinstance(record, Mapping):
                sources.append({
                    "event_type": EVENT_GUARDRAIL_REFUSAL,
                    "source_record_key": key,
                    "payload": dict(record),
                    "event_identity": str(
                        record.get("request_digest", "") or key),
                })

    limit_record = state.get(_USAGE_LIMIT_KEY)
    if isinstance(limit_record, Mapping):
        sources.append({
            "event_type": EVENT_QUOTA_EXHAUSTION,
            "source_record_key": _USAGE_LIMIT_KEY,
            "payload": dict(limit_record),
            "event_identity": digest_of({
                "limit_class": limit_record.get("limit_class"),
                "recorded_at_utc": limit_record.get("recorded_at_utc"),
                "raw_notice": limit_record.get("raw_notice")}),
        })

    abort_record = state.get(_PROVIDER_ABORT_KEY)
    if isinstance(abort_record, Mapping):
        sources.append({
            "event_type": EVENT_AVAILABILITY,
            "source_record_key": _PROVIDER_ABORT_KEY,
            "payload": dict(abort_record),
            "event_identity": digest_of({
                "unit_id": abort_record.get("unit_id"),
                "recorded_at_utc": abort_record.get("recorded_at_utc")}),
        })

    for outage_key in (_OUTAGE_RETRY_KEY, _OUTAGE_BLOCKED_KEY):
        outage = state.get(outage_key)
        if isinstance(outage, Mapping):
            sources.append({
                "event_type": EVENT_AVAILABILITY,
                "source_record_key": outage_key,
                "payload": dict(outage),
                "event_identity": digest_of({
                    "key": outage_key,
                    "cause": outage.get("cause"),
                    "recorded_at_utc": outage.get("recorded_at_utc")}),
            })

    for entry in _model_change_entries(state.get("model_change_audit")):
        sources.append({
            "event_type": EVENT_MODEL_TURNOVER,
            "source_record_key": "model_change_audit",
            "payload": dict(entry),
            "event_identity": digest_of(dict(entry)),
        })

    for transition in journal.transitions():
        detail = getattr(transition, "detail", None) or {}
        if not isinstance(detail, Mapping):
            continue
        reason = str(detail.get("reason", ""))
        if reason in (REASON_TURNOVER_RECORDED, REASON_TURNOVER_LAUNCHED):
            sources.append({
                "event_type": EVENT_QUOTA_EXHAUSTION,
                "source_record_key": f"transitions/{transition.sequence}",
                "payload": {"reason": reason,
                            "turnover": detail.get("turnover"),
                            "cycle": detail.get("cycle")},
                "event_identity": digest_of({
                    "sequence": transition.sequence, "reason": reason}),
            })
    return tuple(sources)


def _model_change_entries(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, list):
        for entry in value:
            if isinstance(entry, Mapping):
                yield entry


# --------------------------------------------------------------------------
# Register rows (CAS-idempotent; sanitized at this boundary - R226)
# --------------------------------------------------------------------------


def observation_digest(source: Mapping[str, Any]) -> str:
    """Stable identity: one register row per distinct event, ever."""
    return digest_of({
        "event_type": source.get("event_type"),
        "source_record_key": source.get("source_record_key"),
        "event_identity": source.get("event_identity"),
    })


def _payload_carries_marker(value: Any, depth: int = 0) -> bool:
    if depth > 4:
        return False
    if isinstance(value, str):
        return INJECTED_TEXT_MARKER in value
    if isinstance(value, Mapping):
        return any(_payload_carries_marker(v, depth + 1)
                   for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_payload_carries_marker(v, depth + 1) for v in value)
    return False


def _evidence_class(source: Mapping[str, Any], session_provenance: str) -> str:
    payload = source.get("payload")
    marked_injected = bool(
        isinstance(payload, Mapping)
        and (payload.get(INJECTED_MARKER_KEY)
             or _payload_carries_marker(payload)))
    if session_provenance == PROVENANCE_INJECTED or marked_injected:
        return EVIDENCE_INJECTED
    return EVIDENCE_LIVE_CANDIDATE


def build_observation_record(source: Mapping[str, Any], *,
                             session_provenance: str,
                             installed_version: str) -> dict[str, Any]:
    """One register row carrying the five R226 capture fields, sanitized."""
    _require_provenance(session_provenance)
    event_type = str(source.get("event_type", ""))
    if event_type not in EVENT_TYPES:
        raise ObservationError(f"unknown event_type {event_type!r}")
    payload = source.get("payload")
    payload = dict(payload) if isinstance(payload, Mapping) else {}
    sanitized = sanitize_structure({
        "classification_decision": _classification_of(event_type, payload),
        "selected_response": _selected_response_of(event_type, payload),
        "outcome": payload,
    })
    record = {
        "schema": SCHEMA,
        "kind": "pending_live_observation",
        "observation_digest": observation_digest(source),
        "observed_event_type": event_type,
        "installed_version_shape": installed_version,
        "applicable_shape": str(payload.get("matched_shape", "") or ""),
        "applicable_shape_verified_live": bool(
            payload.get("shape_verified_live", False)),
        "classification_decision": sanitized.value["classification_decision"],
        "selected_response": sanitized.value["selected_response"],
        "sanitized_outcome": sanitized.value["outcome"],
        "redaction_count": sanitized.count,
        "evidence_class": _evidence_class(source, session_provenance),
        # Constant on every row this module can produce: graduation is an
        # owner-reviewed act (R224/R227), never a watcher side effect.
        "verified_live": False,
        "source_record_key": str(source.get("source_record_key", "")),
        "observed_at_utc": to_utc_iso(),
    }
    return record


def _classification_of(event_type: str, payload: Mapping[str, Any]) -> str:
    for key in ("condition", "classification", "reason_code", "limit_class",
                "cause"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return f"{event_type}:unclassified"


def _selected_response_of(event_type: str, payload: Mapping[str, Any]) -> str:
    if event_type == EVENT_GUARDRAIL_REFUSAL:
        return refusal_bridge.REASON_REFUSAL_RECORDED
    for key in ("reason", "resume_not_before_utc", "next_retry_at_epoch",
                "outcome"):
        value = payload.get(key)
        if isinstance(value, (str, int, float)) and value:
            return f"{key}={value}"
    return "detect-and-hold"


def record_observations(journal: Any, *,
                        session_provenance: str) -> dict[str, Any]:
    """Scan and persist: at most one CAS-written row per distinct event.

    A re-scan of the same journal writes nothing new (the CAS with
    ``expected=None`` refuses an existing key), so repeated session epilogues
    are counted no-ops - the ``external_effects``/``refusal_bridge``
    idempotency convention.
    """
    _require_provenance(session_provenance)
    ensure_register(journal)
    installed = installed_version_shape(journal)
    written: list[str] = []
    seen = 0
    for source in discover_events(journal):
        seen += 1
        record = build_observation_record(
            source, session_provenance=session_provenance,
            installed_version=installed)
        key = f"{OBSERVATION_KEY_PREFIX}{record['observation_digest']}"
        if journal.compare_and_swap_state(key, None, record):
            journal.set_state(LAST_OBSERVATION_KEY,
                              record["observation_digest"])
            written.append(record["observation_digest"])
    return {"events_seen": seen, "rows_written": len(written),
            "written_digests": written,
            "session_provenance": session_provenance}


def ensure_register(journal: Any) -> dict[str, Any]:
    """CAS-initialize the durable awaited-observation statement (R224)."""
    register = {
        "schema": SCHEMA,
        "kind": "pending_live_observation_register",
        "status": "pending_live_observation",
        "awaited": list(AWAITED_OBSERVATIONS),
        "graduation_protocol": (
            "R227: compare a live_candidate row against the injected proof "
            "for the same event type, then the owner-reviewed fixture "
            "upgrade_procedure; never automatic, never by this module"),
        "recorded_at_utc": to_utc_iso(),
    }
    journal.compare_and_swap_state(REGISTER_KEY, None, register)
    stored = journal.get_state(REGISTER_KEY, register)
    return stored if isinstance(stored, dict) else register


# --------------------------------------------------------------------------
# Read-only status, comparison (R227) and feature gating (R228)
# --------------------------------------------------------------------------


def observation_rows(journal: Any) -> tuple[dict[str, Any], ...]:
    rows = []
    for key, record in sorted(journal.all_state().items()):
        if key.startswith(OBSERVATION_KEY_PREFIX) and isinstance(record, dict):
            rows.append(record)
    return tuple(rows)


def register_status(journal: Any) -> dict[str, Any]:
    """Labeled status facts (R042 style); absent is unknown, never zero."""
    rows = observation_rows(journal)
    live = [r for r in rows
            if r.get("evidence_class") == EVIDENCE_LIVE_CANDIDATE]
    injected = [r for r in rows
                if r.get("evidence_class") == EVIDENCE_INJECTED]
    register = journal.get_state(REGISTER_KEY, None)
    return {
        "register": (fact(register.get("status"), REGISTER_KEY)
                     if isinstance(register, dict)
                     else unknown(REGISTER_KEY, "register not initialized")),
        "live_candidate_rows": fact(len(live), OBSERVATION_KEY_PREFIX),
        "injected_reference_rows": fact(len(injected),
                                        OBSERVATION_KEY_PREFIX),
        "natural_event_observed": fact(bool(live), OBSERVATION_KEY_PREFIX)
        if rows else unknown(OBSERVATION_KEY_PREFIX, "none-recorded"),
    }


def compare_with_injected_proof(live_row: Mapping[str, Any],
                                injected_row: Mapping[str, Any]) -> dict[str, Any]:
    """The R227 comparison REPORT: field-by-field live vs injected.

    Output is evidence for the owner-reviewed graduation step; producing it
    changes nothing and grants nothing.
    """
    if live_row.get("evidence_class") != EVIDENCE_LIVE_CANDIDATE:
        raise ObservationError(
            "comparison requires a live_candidate row on the live side "
            "(R223: an injected row can never graduate a live precondition)")
    if injected_row.get("evidence_class") != EVIDENCE_INJECTED:
        raise ObservationError("the reference side must be an injected row")
    fields = ("observed_event_type", "applicable_shape",
              "classification_decision", "selected_response")
    comparison = {
        field: {"live": live_row.get(field),
                "injected": injected_row.get(field),
                "matches": live_row.get(field) == injected_row.get(field)}
        for field in fields}
    return {
        "kind": "live_vs_injected_comparison",
        "schema": SCHEMA,
        "comparison": comparison,
        "all_match": all(entry["matches"] for entry in comparison.values()),
        "graduation": "owner-reviewed fixture upgrade_procedure + standard "
                      "gates + R595; NOT performed by this module",
        "compared_at_utc": to_utc_iso(),
    }


def graduation_readiness(journal: Any) -> dict[str, Any]:
    """Per-feature gating facts (R228): what live observation actually gates.

    Only the automatic 4.8 bridge's actuation is gated on measured-live
    evidence (plus R595); the general loop is independently provable and never
    blocks on this register.  Read-only; the answer can only report
    ``not_ready`` on this build because no code path here (or anywhere) can
    set ``verified_live`` true.
    """
    from .guardrail_refusal import REFUSAL_SHAPE_VERIFIED
    rows = observation_rows(journal)
    live = [r for r in rows
            if r.get("evidence_class") == EVIDENCE_LIVE_CANDIDATE]
    return {
        "general_loop": fact("not_gated_on_live_observation (R220/R228)",
                             "amendment-7"),
        "bridge_actuation": fact(
            "not_ready: measured-live shape absent "
            f"(REFUSAL_SHAPE_VERIFIED={REFUSAL_SHAPE_VERIFIED}) AND R595 "
            "owner authorization absent; fail-safe shadow-only",
            "refusal_bridge.assert_actuation_permitted"),
        "live_candidates_awaiting_review": fact(
            [r.get("observation_digest") for r in live],
            OBSERVATION_KEY_PREFIX),
    }
