"""Audit-event, recalculation-trigger, and downstream-marker shapes (M2-T016, sections 7-9).

Adversarial construction/validation coverage: audit events are attributed, timestamped,
and metadata-only; a professional event without identity is refused; the recalculation
trigger carries the un-bound-consumer seam honestly; the downstream marker speaks ONLY the
existing property_profile 1.4.0 coverage/readiness vocabulary and never downgrades to
'verified'.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.documents.review_events import (
    ANALYSIS_READINESS_BLOCKED_DATA_CONFLICT,
    COVERAGE_DATA_CONFLICT,
    COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
    DependentRecalculationRequested,
    DownstreamImpact,
    DownstreamImpactKind,
    ReviewAuditEvent,
    ReviewEventType,
)

WHEN = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
NAIVE = datetime(2026, 8, 9, 12, 0)
DIGEST = "sha256:" + "a" * 64


# --------------------------------------------------------------- audit events


def test_audit_event_is_attributed_timestamped_and_serializable():
    event = ReviewAuditEvent(
        event_type=ReviewEventType.FACT_CORRECTED,
        document_digest=DIGEST,
        occurred_at=WHEN,
        actor_role="qualified_professional",
        actor_id="pls-1",
        evidence_id="ev-1",
        reason="units were feet, not meters",
        correlation_id="corr-1",
        detail={"correction_entry": {"reason": "units were feet, not meters"}},
    )
    payload = event.to_payload()
    assert payload["event_type"] == "fact_corrected"
    assert payload["actor_id"] == "pls-1"
    assert payload["occurred_at"].startswith("2026-08-09T12:00:00")
    # Metadata only — no document bytes key of any kind.
    assert "bytes" not in payload and "content" not in payload


def test_professional_audit_event_requires_actor_id():
    with pytest.raises(ValueError, match="actor_id"):
        ReviewAuditEvent(
            event_type=ReviewEventType.DOCUMENT_CONFIRMED,
            document_digest=DIGEST,
            occurred_at=WHEN,
            actor_role="qualified_professional",
            actor_id=None,
        )


def test_user_audit_event_may_omit_actor_id():
    event = ReviewAuditEvent(
        event_type=ReviewEventType.FACT_ACCEPTED,
        document_digest=DIGEST,
        occurred_at=WHEN,
        actor_role="user",
        actor_id=None,
    )
    assert event.actor_id is None


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"occurred_at": NAIVE}, "timezone-aware"),
        ({"document_digest": ""}, "document_digest"),
        ({"actor_role": ""}, "actor_role"),
        ({"reason": "  "}, "reason"),
        ({"event_type": "fact_accepted"}, "ReviewEventType"),
        ({"detail": ["not", "a", "dict"]}, "detail"),
    ],
)
def test_audit_event_rejects_malformed_fields(kwargs, match):
    base = {
        "event_type": ReviewEventType.FACT_ACCEPTED,
        "document_digest": DIGEST,
        "occurred_at": WHEN,
        "actor_role": "user",
    }
    base.update(kwargs)
    with pytest.raises(ValueError, match=match):
        ReviewAuditEvent(**base)


# ------------------------------------------------------- recalculation trigger


def test_recalc_trigger_defaults_to_unbound_consumer_seam():
    recalc = DependentRecalculationRequested(
        document_digest=DIGEST,
        trigger=ReviewEventType.FACT_CORRECTED,
        requested_at=WHEN,
        evidence_id="ev-1",
    )
    assert recalc.consumer_bound is False  # the recompute worker is a documented seam
    assert recalc.invalidated_basis == ()
    assert recalc.to_payload()["trigger"] == "fact_corrected"


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"trigger": "fact_corrected"}, "trigger"),
        ({"requested_at": NAIVE}, "timezone-aware"),
        ({"invalidated_basis": ["", "x"]}, "invalidated_basis"),
        ({"consumer_bound": "yes"}, "consumer_bound"),
    ],
)
def test_recalc_trigger_rejects_malformed_fields(kwargs, match):
    base = {
        "document_digest": DIGEST,
        "trigger": ReviewEventType.FACT_CORRECTED,
        "requested_at": WHEN,
    }
    base.update(kwargs)
    with pytest.raises(ValueError, match=match):
        DependentRecalculationRequested(**base)


# ------------------------------------------------------- downstream markers


@pytest.mark.parametrize(
    ("kind", "coverage"),
    [
        (DownstreamImpactKind.BLOCKED, COVERAGE_DATA_CONFLICT),
        (DownstreamImpactKind.BLOCKED, COVERAGE_PROFESSIONAL_REVIEW_REQUIRED),
        (DownstreamImpactKind.PROVISIONAL, COVERAGE_PROFESSIONAL_REVIEW_REQUIRED),
    ],
)
def test_downstream_impact_speaks_existing_coverage_vocabulary(kind, coverage):
    impact = DownstreamImpact(
        impact_kind=kind,
        coverage_status=coverage,
        reason="survey evidence unresolved",
        provenance_digest=DIGEST,
        provenance_evidence_ids=("ev-1",),
        analysis_readiness=ANALYSIS_READINESS_BLOCKED_DATA_CONFLICT
        if kind is DownstreamImpactKind.BLOCKED
        else None,
    )
    assert impact.to_payload()["coverage_status"] == coverage


@pytest.mark.parametrize("bad_coverage", ["verified", "ready", "", "unknown"])
def test_downstream_impact_never_downgrades_to_verified_or_unknown(bad_coverage):
    with pytest.raises(ValueError, match="coverage_status"):
        DownstreamImpact(
            impact_kind=DownstreamImpactKind.BLOCKED,
            coverage_status=bad_coverage,
            reason="x",
            provenance_digest=DIGEST,
        )


@pytest.mark.parametrize("bad_readiness", ["ready", "not_computed", "verified"])
def test_downstream_impact_rejects_non_blocked_analysis_readiness(bad_readiness):
    with pytest.raises(ValueError, match="analysis_readiness"):
        DownstreamImpact(
            impact_kind=DownstreamImpactKind.BLOCKED,
            coverage_status=COVERAGE_DATA_CONFLICT,
            reason="x",
            provenance_digest=DIGEST,
            analysis_readiness=bad_readiness,
        )


def test_downstream_impact_requires_provenance():
    with pytest.raises(ValueError, match="provenance_digest"):
        DownstreamImpact(
            impact_kind=DownstreamImpactKind.BLOCKED,
            coverage_status=COVERAGE_DATA_CONFLICT,
            reason="x",
            provenance_digest="",
        )
