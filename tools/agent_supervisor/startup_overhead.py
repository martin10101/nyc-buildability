"""Startup/read-in overhead measurement and sizing calibration
(D-024 Phase C item 3, M0-T090).

Claude Code's documented startup behavior matters (D-024 s6): a fresh
non-fork subagent has an isolated context and reloads its task message,
CLAUDE.md hierarchy, agent prompt/skills, and git snapshot instead of
inheriting the parent's already-read conversation. This module MEASURES that
repeated loading cost so future sizing optimizes the combined cost of startup
plus productive work (s5.5 "Use historical observations to improve future
sizing: initial packet size, repeated required documents, startup tokens/
time, files reopened, graph retrieval breadth, implementation/test effort,
compactions, and the eventual outcome").

Observations are objective and honest: an unmeasured number is ``None``
(never zero), medians are computed only over known values, and calibration
with no observations says so instead of inventing an estimate. Observations
convert to ``TelemetryRecord`` so the accepted Phase B journal/sidecar
sanitization pipeline is reused, not rebuilt.

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses
import statistics
from typing import Any

from .telemetry_records import Measurement, TelemetryRecord
from .workload_classifier import WORK_CLASSES, WorkloadError

RECORD_TYPE = "startup_overhead"

#: Closed outcome vocabulary for a finished observation. "unknown" is the
#: honest default while the assignment is still running.
OUTCOMES: tuple[str, ...] = (
    "completed", "extended", "landed", "stopped", "failed", "unknown")

DEFAULT_MAX_OBSERVATIONS = 512


class OverheadError(ValueError):
    """Typed error for overhead measurement (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class StartupObservation:
    """One spawn's measured startup/read-in overhead (D-024 s5.5, s6).

    ``None`` means "not measured" and is never encoded as zero; counts are
    non-negative integers because they were actually counted.
    """

    assignment_id: str
    size_class: str
    resolved_model: str = ""
    packet_tier: str = ""
    packet_bytes: int = 0
    startup_tokens: int | None = None
    startup_seconds: float | None = None
    files_reopened: int = 0
    repeated_documents: int = 0
    time_to_first_evidence_seconds: float | None = None
    outcome: str = "unknown"
    recorded_at_utc: str = ""

    def __post_init__(self) -> None:
        if not self.assignment_id:
            raise OverheadError("missing_id", "assignment_id is required")
        if self.size_class not in WORK_CLASSES:
            raise WorkloadError(
                "bad_declared_class",
                f"{self.size_class!r} is not one of {list(WORK_CLASSES)}")
        if self.outcome not in OUTCOMES:
            raise OverheadError(
                "bad_outcome",
                f"outcome {self.outcome!r} is not one of {list(OUTCOMES)}")
        for name in ("packet_bytes", "files_reopened", "repeated_documents"):
            if getattr(self, name) < 0:
                raise OverheadError("negative_count",
                                    f"{name} may not be negative")
        for name in ("startup_tokens", "startup_seconds",
                     "time_to_first_evidence_seconds"):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool) or value < 0):
                raise OverheadError(
                    "bad_measurement",
                    f"{name} must be None (unmeasured) or non-negative")

    def to_record(self, *, now_utc_iso: str | None = None) -> TelemetryRecord:
        """Convert to a telemetry record so the accepted sanitize-first
        journal/sidecar surfaces persist it (reuse, not rebuild)."""

        def _measure(value: int | float | None, detail: str) -> Measurement:
            if value is None:
                return Measurement.unknown("cumulative", detail=detail)
            return Measurement(value=value, label="estimated",
                               category="cumulative", detail=detail)

        measurements = {
            "startup_overhead_tokens": _measure(
                self.startup_tokens,
                "measured startup/read-in tokens for this spawn"),
            "startup_overhead_seconds": _measure(
                self.startup_seconds, "wall seconds from spawn to ready"),
            "startup_time_to_first_evidence_seconds": _measure(
                self.time_to_first_evidence_seconds,
                "seconds until the first durable productive evidence"),
            "startup_packet_bytes": Measurement(
                value=self.packet_bytes, label="estimated",
                category="cumulative", detail="initial context packet size"),
            "startup_files_reopened": Measurement(
                value=self.files_reopened, label="estimated",
                category="cumulative",
                detail="files the child re-read that the parent had read"),
            "startup_repeated_documents": Measurement(
                value=self.repeated_documents, label="estimated",
                category="cumulative",
                detail="required documents loaded again at startup"),
        }
        return TelemetryRecord(
            record_type=RECORD_TYPE,
            timestamp_utc=now_utc_iso or self.recorded_at_utc or "",
            measurements=measurements,
            task_id=self.assignment_id,
            attributes={
                "size_class": self.size_class,
                "resolved_model": self.resolved_model,
                "packet_tier": self.packet_tier,
                "outcome": self.outcome,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class OverheadCalibration:
    """Aggregate over KNOWN values only; ``None`` means no observation
    measured that quantity (unknown never zero, D-024 s5.4 discipline)."""

    observations: int
    median_startup_tokens: float | None
    median_startup_seconds: float | None
    median_time_to_first_evidence_seconds: float | None
    median_packet_bytes: float | None
    size_class: str = ""
    resolved_model: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class OverheadLedger:
    """Bounded in-memory ledger of startup observations.

    Bounded exactly like the accepted trackers (oldest-first eviction with a
    counted ``evicted_observations``), so a long-running controller cannot
    grow it without bound.
    """

    def __init__(self, *, max_observations: int = DEFAULT_MAX_OBSERVATIONS) -> None:
        if max_observations < 1:
            raise OverheadError("bad_bound", "max_observations must be >= 1")
        self._max = max_observations
        self._observations: list[StartupObservation] = []
        self._evicted = 0

    @property
    def evicted_observations(self) -> int:
        return self._evicted

    def __len__(self) -> int:
        return len(self._observations)

    def record(self, observation: StartupObservation) -> None:
        self._observations.append(observation)
        while len(self._observations) > self._max:
            self._observations.pop(0)
            self._evicted += 1

    def calibration(self, *, size_class: str = "",
                    resolved_model: str = "") -> OverheadCalibration:
        """Median calibration for the matching observations (all when no
        filter). Filters are exact matches; medians skip unmeasured values."""
        if size_class and size_class not in WORK_CLASSES:
            raise WorkloadError(
                "bad_declared_class",
                f"{size_class!r} is not one of {list(WORK_CLASSES)}")
        selected = [
            o for o in self._observations
            if (not size_class or o.size_class == size_class)
            and (not resolved_model or o.resolved_model == resolved_model)]

        def _median(values: list[int | float]) -> float | None:
            return statistics.median(values) if values else None

        return OverheadCalibration(
            observations=len(selected),
            median_startup_tokens=_median(
                [o.startup_tokens for o in selected
                 if o.startup_tokens is not None]),
            median_startup_seconds=_median(
                [o.startup_seconds for o in selected
                 if o.startup_seconds is not None]),
            median_time_to_first_evidence_seconds=_median(
                [o.time_to_first_evidence_seconds for o in selected
                 if o.time_to_first_evidence_seconds is not None]),
            median_packet_bytes=_median(
                [float(o.packet_bytes) for o in selected if o.packet_bytes]),
            size_class=size_class,
            resolved_model=resolved_model,
        )
