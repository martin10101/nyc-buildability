"""Deterministic checks over already-validated survey facts (application-level; M2-T015 SB-S3).

Input rule (what a check may consume): ONLY the frozen typed RESOLVED results produced
by :mod:`app.documents.units` (``ValidatedDistance``, ``ValidatedBearing``,
``ValidatedArea``, ...) and :mod:`app.documents.geometry_validation`. A raw wire value,
an unvalidated number or string, an ``UnresolvedNormalizedValue``, or ANY AI-produced
output is never a check input: a check handed anything but the required resolved types
refuses to evaluate rather than coercing, re-parsing, re-validating, or guessing.

Output rule (what a check may produce): exactly one frozen typed RESULT —
:class:`CheckPassed`, :class:`CheckFailed`, or :class:`CheckUnevaluable` — and NEVER an
exception for a check-domain outcome, mirroring the refusal-as-value pattern of
:mod:`app.documents.units`: an unevaluable input condition is a routine, typed, visible
outcome the caller must surface and route to review — not a crash and not a silent
skip. No result of this package is promotable (``promotable = False`` on all three
types): a check result is deterministic evidence FOR the material-evidence promotion
gate, never itself a material buildability value.

Determinism and provenance: all check arithmetic uses :mod:`math` functions over the
already-validated numbers, every tolerance is a REQUIRED caller statement (never
defaulted or guessed), and every evaluated result carries the computed numbers and that
stated tolerance verbatim. The package extends additively only, each new check shipping
together with the deterministic code and tests that ground it (mirroring the taxonomy's
extension rule).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

__all__ = [
    "CheckFailed",
    "CheckPassed",
    "CheckResult",
    "CheckUnevaluable",
    "address_bbl_match",
    "boundary_closure",
    "calculated_vs_stated_area",
    "contradictory_dimensions",
    "elevation_consistency",
    "north_orientation_consistency",
    "scale_consistency",
    "segment_sum_consistency",
]


@dataclass(frozen=True)
class CheckPassed:
    """Typed PASS result: the check evaluated deterministically and its computed
    magnitude is within the caller-stated tolerance.

    Carries the computed numbers, the stated tolerance, and the single shared stated
    unit verbatim for provenance (``unit`` is ``None`` only for dimensionless checks).
    The payload is metadata only and safe to serialize into an API response or audit
    record.
    """

    check_name: str
    unit: str | None
    tolerance: int | float
    computed: Mapping[str, int | float]

    evaluated = True
    passed = True
    promotable = False

    def to_payload(self) -> dict:
        """Structured result payload (metadata only, JSON-serializable)."""
        return {
            "check_name": self.check_name,
            "outcome": "passed",
            "unit": self.unit,
            "tolerance": self.tolerance,
            "computed": dict(self.computed),
        }


@dataclass(frozen=True)
class CheckFailed:
    """Typed FAIL result: the check evaluated deterministically and its computed
    magnitude exceeds the caller-stated tolerance.

    A substantive finding, not an input problem: it carries the same verbatim computed
    numbers, stated tolerance, and shared stated unit as :class:`CheckPassed`, so the
    misclosure/difference itself is auditable provenance.
    """

    check_name: str
    unit: str | None
    tolerance: int | float
    computed: Mapping[str, int | float]

    evaluated = True
    passed = False
    promotable = False

    def to_payload(self) -> dict:
        """Structured result payload (metadata only, JSON-serializable)."""
        return {
            "check_name": self.check_name,
            "outcome": "failed",
            "unit": self.unit,
            "tolerance": self.tolerance,
            "computed": dict(self.computed),
        }


@dataclass(frozen=True)
class CheckUnevaluable:
    """Typed refusal to evaluate — a visible RESULT, deliberately a value and never
    raised, that can NEVER be promoted and never masquerades as PASS or FAIL.

    Produced whenever an input is not the required resolved type, units are mixed,
    counts mismatch, the input set is structurally insufficient, or the stated
    tolerance is unusable. It carries only the check name and the stated reason (with
    the offending submission described verbatim inside the reason): no computed value
    exists, so there is nothing downstream code could promote — mirroring
    ``UnresolvedNormalizedValue`` in :mod:`app.documents.units`.
    """

    check_name: str
    reason: str

    evaluated = False
    passed = False
    promotable = False
    reject_code = "check_unevaluable"

    def to_payload(self) -> dict:
        """Structured refusal payload (metadata only, JSON-serializable)."""
        return {
            "check_name": self.check_name,
            "outcome": "unevaluable",
            "reject_code": self.reject_code,
            "reason": self.reason,
        }


CheckResult = CheckPassed | CheckFailed | CheckUnevaluable


# Re-exported deterministic checks. Imported AFTER the result types above: each check
# module consumes those types from this package, so a top-of-module import would be
# circular during package initialization.
from app.documents.checks.area import (  # noqa: E402
    calculated_vs_stated_area,
    contradictory_dimensions,
)
from app.documents.checks.boundary import (  # noqa: E402
    boundary_closure,
    segment_sum_consistency,
)
from app.documents.checks.metadata import (  # noqa: E402
    address_bbl_match,
    elevation_consistency,
    north_orientation_consistency,
    scale_consistency,
)
