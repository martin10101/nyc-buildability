"""Structural workload classifier (D-024 Phase C item 2, M0-T090).

Classifies proposed work STRUCTURALLY rather than pretending to predict an
exact token total (D-024 s5.5): the four owner-defined classes are

- ``main-session`` — quick targeted changes, work needing frequent
  back-and-forth, or several phases sharing substantial context; never spawn a
  fresh subagent merely to make one small edit or answer one local question;
- ``cohesive-subagent`` — self-contained work owning a meaningful path from
  investigation through implementation/test or evidence through a bounded
  report (the preferred subagent size);
- ``oversized-split-at-seams`` — work spanning independent components,
  unrelated hypotheses, multiple write owners, or several separately provable
  outcomes; split at natural graph/ownership/test seams BEFORE dispatch;
- ``unknown-recon-first`` — perform the cheapest bounded
  sizing/reconnaissance step first before choosing a writer assignment.

This is a DIFFERENT axis from ``rotation.py``'s SMALL/MEDIUM/LARGE session
job sizing (S11.1) and deliberately does not overload that vocabulary; it
reuses the same design discipline: objective countable features, deterministic
rules, closed vocabularies, and a conservative landing for unrecognizable
shapes (never optimistically "cohesive"). Stale or unavailable graph evidence
is REPORTED and classified as unknown, never acted on as fact (D-024-R080).

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any

MAIN_SESSION = "main-session"
COHESIVE_SUBAGENT = "cohesive-subagent"
OVERSIZED_SPLIT = "oversized-split-at-seams"
UNKNOWN_RECON = "unknown-recon-first"

#: Closed vocabulary. A class absent from this tuple cannot be produced or
#: declared; validation fails closed on anything else.
WORK_CLASSES: tuple[str, ...] = (
    MAIN_SESSION, COHESIVE_SUBAGENT, OVERSIZED_SPLIT, UNKNOWN_RECON)


class WorkloadError(ValueError):
    """Typed error for workload classification (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


#: G3 MINOR-5 (M0-T090 carried correction): the size-class vocabulary is
#: owned here, but two error surfaces report an invalid class and their code
#: strings are pinned by the accepted M0-T090 test pack — WorkloadError
#: ``bad_declared_class`` (this module and ``startup_overhead``) and
#: ContractError ``bad_size_class`` (``subagent_contracts.validate_envelope``).
#: Both codes are registered in this single closed set so a caller can treat
#: "invalid size class" as ONE condition regardless of which surface raised it.
SIZE_CLASS_ERROR_CODES: tuple[str, ...] = ("bad_declared_class", "bad_size_class")


@dataclasses.dataclass(frozen=True)
class WorkloadThresholds:
    """Owner-policy thresholds for structural classification. Configurable;
    NOT capacity claims and NOT token predictions (D-024 s5.5).

    ``oversized_breadth`` intentionally matches the existing packet-tier
    MEDIUM breadth bound (``context_pack_budget.MEDIUM_BREADTH_MAX``): work
    whose dependency neighborhood exceeds what a MEDIUM packet covers is a
    split candidate, keeping this axis consistent with the preserved tiers.
    """

    main_session_max_files: int = 2
    oversized_breadth: int = 40
    oversized_subsystems: int = 3
    oversized_outcomes: int = 1
    oversized_write_owners: int = 1

    @classmethod
    def from_controller_config(cls, config: Any) -> "WorkloadThresholds":
        """Read ``[subagent_workload]`` from the controller config, failing
        closed on unknown keys or non-positive values (rotation.py pattern)."""
        raw = getattr(config, "raw", {}) or {}
        section = raw.get("subagent_workload", {}) or {}
        if not isinstance(section, Mapping):
            raise WorkloadError("bad_section", "[subagent_workload] must be a table")
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(section) - known)
        if unknown:
            raise WorkloadError(
                "unknown_workload_key",
                f"unrecognized [subagent_workload] keys: {unknown}")
        values: dict[str, Any] = {}
        for name, value in section.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise WorkloadError(
                    "bad_threshold", f"{name} must be a positive integer, got {value!r}")
            values[name] = value
        return cls(**values)


@dataclasses.dataclass(frozen=True)
class WorkloadFeatures:
    """OBJECTIVE features of a proposed assignment (D-024 s5.5).

    Every field is countable from the task graph, code graph, acceptance
    criteria, and dependency boundaries the controller already holds; none of
    it is a token prediction. Zero on a count means "not counted", which is
    treated as MISSING evidence (conservative), never as evidence of
    smallness. ``graph_stale=True`` records that graph-derived numbers came
    from a stale index and must not be trusted as fact (D-024-R080).
    """

    file_count: int = 0
    dependency_breadth: int = 0
    write_owner_count: int = 0
    independent_outcome_count: int = 0
    subsystems_touched: int = 0
    single_small_edit: bool = False
    requires_frequent_parent_decisions: bool = False
    phases_share_substantial_context: bool = False
    end_to_end_provable: bool = False
    graph_stale: bool = False
    seam_candidates: tuple[str, ...] = ()
    declared_class: str = ""

    def __post_init__(self) -> None:
        if self.declared_class and self.declared_class not in WORK_CLASSES:
            raise WorkloadError(
                "bad_declared_class",
                f"{self.declared_class!r} is not one of {list(WORK_CLASSES)}")
        for name in ("file_count", "dependency_breadth", "write_owner_count",
                     "independent_outcome_count", "subsystems_touched"):
            if getattr(self, name) < 0:
                raise WorkloadError("negative_feature", f"{name} may not be negative")
        if not isinstance(self.seam_candidates, tuple):
            raise WorkloadError("bad_seams", "seam_candidates must be a tuple")


@dataclasses.dataclass(frozen=True)
class WorkloadClassification:
    work_class: str
    reason_code: str
    reason: str
    features_used: tuple[str, ...] = ()
    #: For oversized work: the natural graph/ownership/test seams to split at
    #: BEFORE dispatch (D-024 s5.5). Empty means the caller must propose seams
    #: from write-owner and test boundaries; the reason says so.
    split_seams: tuple[str, ...] = ()


def classify_workload(
    features: WorkloadFeatures,
    thresholds: WorkloadThresholds | None = None,
) -> WorkloadClassification:
    """Deterministic structural classification (D-024 s5.5, 16.2).

    Rule precedence (each documented in the returned reason):

    1. Stale graph evidence or no objective features -> unknown-recon-first
       (cheapest bounded sizing step first; stale data is reported, not used).
    2. Multiple write owners, several separately provable outcomes, breadth or
       subsystem spread beyond thresholds -> oversized-split-at-seams.
    3. Single small edit, frequent parent back-and-forth, or phases sharing
       substantial context -> main-session.
    4. End-to-end provable single-owner unit -> cohesive-subagent.
    5. Anything that cannot PROVE cohesion -> unknown-recon-first (a shape we
       cannot classify is never optimistically called cohesive).
    """
    th = thresholds or WorkloadThresholds()

    if features.declared_class:
        return WorkloadClassification(
            features.declared_class, "declared_class",
            f"caller declared {features.declared_class!r} explicitly; recorded "
            f"as an override, not a measurement", ("declared_class",))

    if features.graph_stale:
        return WorkloadClassification(
            UNKNOWN_RECON, "graph_stale",
            "graph-derived evidence is stale; stale data is reported and never "
            "acted on as fact (D-024-R080) - run the cheapest bounded "
            "reconnaissance step first", ("graph_stale",))

    counted = (features.file_count or features.dependency_breadth
               or features.write_owner_count or features.independent_outcome_count
               or features.subsystems_touched)
    flagged = (features.single_small_edit
               or features.requires_frequent_parent_decisions
               or features.phases_share_substantial_context
               or features.end_to_end_provable)
    if not counted and not flagged:
        return WorkloadClassification(
            UNKNOWN_RECON, "no_objective_features",
            "no objective feature was available; unknown-recon-first is the "
            "conservative classification, never an optimistic cohesive unit")

    oversized_used: list[str] = []
    if features.write_owner_count > th.oversized_write_owners:
        oversized_used.append("write_owner_count")
    if features.independent_outcome_count > th.oversized_outcomes:
        oversized_used.append("independent_outcome_count")
    if features.dependency_breadth > th.oversized_breadth:
        oversized_used.append("dependency_breadth")
    if features.subsystems_touched > th.oversized_subsystems:
        oversized_used.append("subsystems_touched")
    if oversized_used:
        seam_note = ("split at the provided seams before dispatch"
                     if features.seam_candidates else
                     "no seam candidates were provided; split at natural "
                     "write-owner and test boundaries before dispatch")
        return WorkloadClassification(
            OVERSIZED_SPLIT, "oversized",
            f"work spans independent boundaries ({', '.join(oversized_used)}); "
            f"{seam_note} (D-024 s5.5)", tuple(oversized_used),
            features.seam_candidates)

    main_used: list[str] = []
    if features.single_small_edit:
        main_used.append("single_small_edit")
    if features.requires_frequent_parent_decisions:
        main_used.append("requires_frequent_parent_decisions")
    if features.phases_share_substantial_context:
        main_used.append("phases_share_substantial_context")
    if not main_used and features.file_count and \
            features.file_count <= th.main_session_max_files \
            and not features.end_to_end_provable:
        main_used.append("file_count")
    if main_used:
        return WorkloadClassification(
            MAIN_SESSION, "main_session",
            "quick targeted work, frequent shared decisions, or shared-context "
            f"phases ({', '.join(main_used)}); do not spawn a fresh subagent "
            "merely for one small edit (D-024 s5.5)", tuple(main_used))

    if features.end_to_end_provable and features.write_owner_count == 1:
        return WorkloadClassification(
            COHESIVE_SUBAGENT, "cohesive_unit",
            "one self-contained ownership unit with a natural end-to-end proof "
            "(the preferred subagent size, D-024 s5.5)",
            ("end_to_end_provable", "write_owner_count"))

    return WorkloadClassification(
        UNKNOWN_RECON, "cohesion_unproven",
        "objective features exist but neither cohesion (end-to-end proof under "
        "one write owner) nor a main-session shape is proven; run the cheapest "
        "bounded reconnaissance step first rather than guessing")
