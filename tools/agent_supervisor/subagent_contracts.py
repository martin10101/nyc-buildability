"""Bounded subagent contracts: worker assignment + supervision envelope
(D-024 Phase C item 1, M0-T090).

Before every spawn the controller creates TWO LINKED RECORDS (D-024 s6):

- the WORKER-FACING assignment — IDs, exact change, role, permitted and
  prohibited areas, deliverable/return schema, acceptance criteria,
  checkpoints, honest-blocker reporting, extension protocol, and handoff
  duties. It NEVER contains a numeric token quota, percentage of budget,
  countdown, or conserve-tokens pressure (D-024-R045; s16.2
  no-quota-in-worker-prompt proof) — the no-quota guard here fails closed on
  any such phrasing in any worker-visible field;
- the CONTROLLER-ONLY supervision envelope — structural size class and
  cohesion rationale, graph neighborhood and ownership/write lease, startup
  overhead and packet-reuse plan, resolved model/context, telemetry sources
  and confidence, PRIVATE health bands, detectors, landing opportunities, and
  extension criteria. "Never paste the supervision envelope's numeric
  counters or thresholds into the worker prompt. It is controller policy,
  not part of the engineering problem." (s6) — enforced by the leak guard.

Records are frozen, digest-bound, and recorded before acting (the
``loop.ShadowPlan`` precedent). This module defines and validates contracts;
runtime enforcement lives in the M0-T091 runtime units (``lease_runtime`` for
serialized grants, ``runtime_health`` for live band evaluation,
``runtime_detectors``/``extension_gate``/``child_handoff`` for no-progress,
extension, landing, and turnover handling).

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import posixpath
import re
from collections.abc import Mapping
from typing import Any

from .telemetry_records import CONFIDENCE_LABELS
from .workload_classifier import COHESIVE_SUBAGENT, WORK_CLASSES

ROLE_READ_ONLY = "read_only"
ROLE_REVIEW_ONLY = "review_only"
ROLE_WRITE = "write"
ROLES: tuple[str, ...] = (ROLE_READ_ONLY, ROLE_REVIEW_ONLY, ROLE_WRITE)

#: Closed vocabulary of Phase B telemetry sources an envelope may cite.
TELEMETRY_SOURCES: tuple[str, ...] = (
    "statusline_sidecar", "subagent_status_rows", "sdk_events",
    "hook_events", "transcript_accumulator")

#: The private health-band ladder (D-024 s5.5). Band names and thresholds are
#: controller policy and must never appear in worker-facing text.
BAND_NORMAL = "normal"
BAND_OBSERVE = "observe"
BAND_PREPARE = "prepare_to_land"
BAND_LAND = "land"
BAND_EMERGENCY = "emergency_stop"
HEALTH_BAND_NAMES: tuple[str, ...] = (
    BAND_NORMAL, BAND_OBSERVE, BAND_PREPARE, BAND_LAND, BAND_EMERGENCY)

#: Producer concurrency cap: retained repository policy (D-024 s6 "Retain the
#: existing producer concurrency cap of no more than three producers at
#: once"; stated in .claude/ORCHESTRATION_POLICY.md section B, which this
#: module implements but never edits).
PRODUCER_CAP = 3

#: Default worker-facing texts for the duty fields D-024 s6 requires. They are
#: honest-behavior instructions, not telemetry.
DEFAULT_BLOCKER_REPORTING = (
    "Report any blocker, loss of coherence, or material scope discovery "
    "honestly and immediately in your return; never mask uncertainty as "
    "completion.")
DEFAULT_EXTENSION_PROTOCOL = (
    "If you reach a contract boundary, discover a materially larger problem, "
    "or want to pursue a long investigation: stop and return what you have "
    "proven, what remains uncertain, why the extra work blocks the current "
    "acceptance criterion, the least costly next experiment, the additional "
    "scope with its likely evidence sources and its natural completion "
    "point, whether resuming this context or a new bounded unit would be "
    "more coherent, the consequences of stopping now, and a durable partial "
    "checkpoint if you changed anything. Do not silently expand scope.")
DEFAULT_UNRELATED_DISCOVERY = (
    "Record unrelated discoveries as backlog notes in your return; do not "
    "investigate or fix them within this assignment.")
DEFAULT_HANDOFF_REQUIREMENTS = (
    "If the assignment cannot finish, return a durable partial handoff: what "
    "was completed, the exact repository state, verified evidence, open "
    "questions, and the exact next action.")

#: Fail-closed pattern classes for worker-facing text (D-024-R045). Any match
#: rejects the assignment; the caller rewrites the wording instead of the
#: guard guessing intent. Deliberately broad: a numeric token count in a
#: worker prompt is exactly the pressure the owner prohibited.
_QUOTA_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (label, re.compile(pattern, re.IGNORECASE)) for label, pattern in (
        ("tokens_left", r"\btokens?\s+(?:left|remaining|used)\b"),
        ("remaining_budget", r"\bremaining\s+(?:tokens?|budget|context)\b"),
        ("token_quota", r"\btoken\s+(?:budget|quota|limit|allowance|cap)s?\b"),
        ("budget_of_n", r"\b(?:budget|quota|allowance)\s+of\s+\d"),
        ("conserve", r"\bconserve\s+(?:tokens?|context)\b"),
        ("countdown", r"\bcountdown\b"),
        ("ration", r"\bration\w*\b"),
        ("numeric_tokens", r"\b\d[\d,_.]*\s*(?:k|m)?\s*tokens?\b"),
        ("percent_of_window",
         r"\b\d{1,3}\s*%\s*(?:of\s+)?(?:your\s+)?(?:context|budget|window|capacity)\b"),
        # G3 MAJOR-2 / G5 M1 (M0-T090 carried correction): a numeric
        # percentage in worker text is quota pressure regardless of spacing
        # ("70 %") or spelling ("70 percent") and regardless of the noun that
        # follows; broad by design - the caller rewrites legitimate wording.
        ("percent_numeric", r"\b\d[\d,_.]*\s*(?:%|percent(?:age)?s?\b)"),
        # G3 MAJOR-2 / MINOR-3 (carried): conserve-synonym pressure - a
        # save/spare/economize/frugal verb aimed at tokens/context/budget is
        # the same prohibited rationing instruction as "conserve tokens".
        ("conserve_synonym",
         r"\b(?:conserve|conserving|save|saving|spare|sparing|economical|"
         r"economiz\w*|frugal\w*)\b[^.\n]{0,60}?"
         r"\b(?:tokens?|context|budget|window|capacity)\b"),
        ("max_turns_spend", r"\bmax(?:imum)?\s+(?:turns?|spend|budget)\b"),
    ))


class ContractError(ValueError):
    """Typed error for contract validation (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _digest(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=True).encode("ascii", "backslashreplace")
    ).hexdigest()


def assert_worker_text_clean(field_name: str, text: str) -> None:
    """Fail closed on quota/countdown/conserve-pressure phrasing (R045)."""
    for label, pattern in _QUOTA_PATTERNS:
        match = pattern.search(text)
        if match:
            raise ContractError(
                "quota_language",
                f"worker-facing field {field_name!r} contains prohibited "
                f"pressure phrasing ({label}: {match.group(0)!r}); numeric "
                f"token quotas, percentages, countdowns, and conserve-tokens "
                f"pressure never reach a worker (D-024-R045)")


@dataclasses.dataclass(frozen=True)
class WorkerAssignment:
    """The worker-facing half of the pre-spawn record pair (D-024 s6)."""

    assignment_id: str
    parent_task_id: str
    exact_change: str
    necessity: str
    role: str
    permitted_paths: tuple[str, ...] = ()
    permitted_tools: tuple[str, ...] = ()
    prohibited_areas: tuple[str, ...] = ()
    prohibited_external_effects: tuple[str, ...] = ()
    deliverable_schema: str = ""
    acceptance_criteria: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    checkpoints: tuple[str, ...] = ()
    blocker_reporting: str = DEFAULT_BLOCKER_REPORTING
    checkpoint_commit_allowed: bool = False
    extension_protocol: str = DEFAULT_EXTENSION_PROTOCOL
    unrelated_discovery: str = DEFAULT_UNRELATED_DISCOVERY
    handoff_requirements: str = DEFAULT_HANDOFF_REQUIREMENTS

    def worker_text_fields(self) -> tuple[tuple[str, str], ...]:
        """Every string that can reach the worker, for the no-quota guard.

        Fails CLOSED on any field type it cannot scan (G5 N1, M0-T090
        carried correction): a future worker-facing field added as a dict,
        list, or nested record must force an explicit scanning decision here
        instead of silently escaping the guard. ``bool`` is the one
        explicitly non-text type (``checkpoint_commit_allowed``).
        """
        pairs: list[tuple[str, str]] = []
        for f in dataclasses.fields(self):
            value = getattr(self, f.name)
            if isinstance(value, bool):
                continue
            if isinstance(value, str):
                pairs.append((f.name, value))
                continue
            if isinstance(value, tuple):
                for i, item in enumerate(value):
                    if not isinstance(item, str):
                        raise ContractError(
                            "unscannable_field",
                            f"worker-facing field {f.name}[{i}] holds "
                            f"{type(item).__name__!r}, which the no-quota "
                            f"guard cannot scan; only strings may reach a "
                            f"worker (D-024-R045, fail closed)")
                    pairs.append((f"{f.name}[{i}]", item))
                continue
            raise ContractError(
                "unscannable_field",
                f"worker-facing field {f.name!r} holds "
                f"{type(value).__name__!r}, which the no-quota guard cannot "
                f"scan; only strings, tuples of strings, and bool flags are "
                f"permitted in the assignment (D-024-R045, fail closed)")
        return tuple(pairs)

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def digest(self) -> str:
        return _digest(self.to_dict())


#: Phrasings that mark an assignment as an open-ended project rather than an
#: exact change (s6: no vague "investigate and fix everything" instruction).
_VAGUE_MARKERS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE) for p in (
        r"\bfix\s+everything\b",
        r"\binvestigate\s+and\s+fix\b",
        r"\ball\s+(?:bugs|issues|problems)\b",
        r"\bwhatever\s+(?:needs|you\s+find)\b",
        r"\bentire\s+(?:milestone|codebase|repo(?:sitory)?)\b",
    ))


def validate_assignment(assignment: WorkerAssignment) -> None:
    """Reject unbounded, vague, or pressure-laden assignments (fail closed)."""
    if not assignment.assignment_id or not assignment.parent_task_id:
        raise ContractError("missing_ids",
                            "assignment_id and parent_task_id are required")
    if assignment.role not in ROLES:
        raise ContractError("bad_role",
                            f"role {assignment.role!r} is not one of {list(ROLES)}")
    if not assignment.exact_change.strip():
        raise ContractError("vague_assignment",
                            "exact_change is empty; a subagent never receives "
                            "an open-ended project (D-024 s6)")
    for marker in _VAGUE_MARKERS:
        match = marker.search(assignment.exact_change)
        if match:
            raise ContractError(
                "vague_assignment",
                f"exact_change reads as an open-ended project "
                f"({match.group(0)!r}); reject or split before dispatch "
                f"(D-024 s6, s16.2)")
    if not assignment.necessity.strip():
        raise ContractError("missing_necessity",
                            "why this is necessary for the current accepted "
                            "task is a required field (D-024 s6)")
    if not assignment.acceptance_criteria:
        raise ContractError("missing_acceptance",
                            "concrete good-enough acceptance criteria are "
                            "required (D-024 s6)")
    if not assignment.deliverable_schema.strip():
        raise ContractError("missing_deliverable",
                            "expected deliverable and return schema are "
                            "required (D-024 s6)")
    if assignment.role == ROLE_WRITE and not assignment.permitted_paths:
        raise ContractError("write_without_scope",
                            "a write-role assignment requires explicit "
                            "permitted files/directories (D-024 s6)")
    for field_name, text in assignment.worker_text_fields():
        assert_worker_text_clean(field_name, text)


@dataclasses.dataclass(frozen=True)
class HealthBands:
    """PRIVATE, configurable health bands (D-024 s5.5). Fractions of the
    resolved model's live context occupancy; controller policy, never
    capacity claims, never worker-visible. Ordering is enforced:
    observe < prepare_to_land < land < emergency_stop.
    """

    observe_occupancy: float = 0.50
    prepare_occupancy: float = 0.70
    land_occupancy: float = 0.85
    emergency_occupancy: float = 0.95

    def __post_init__(self) -> None:
        for name in ("observe_occupancy", "prepare_occupancy",
                     "land_occupancy", "emergency_occupancy"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not 0 < float(value) < 1:
                raise ContractError(
                    "bad_band", f"{name} must be a fraction strictly between "
                                f"0 and 1, got {value!r}")
        if not (self.observe_occupancy < self.prepare_occupancy
                < self.land_occupancy < self.emergency_occupancy):
            raise ContractError(
                "band_order",
                "bands must satisfy observe < prepare_to_land < land < "
                "emergency_stop; otherwise a later band could fire first")

    @classmethod
    def from_controller_config(cls, config: Any) -> "HealthBands":
        """Read ``[subagent_health_bands]``, failing closed on unknown keys
        (rotation.RotationThresholds pattern)."""
        raw = getattr(config, "raw", {}) or {}
        section = raw.get("subagent_health_bands", {}) or {}
        if not isinstance(section, Mapping):
            raise ContractError("bad_section",
                                "[subagent_health_bands] must be a table")
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(section) - known)
        if unknown:
            raise ContractError(
                "unknown_band_key",
                f"unrecognized [subagent_health_bands] keys: {unknown}")
        return cls(**{k: v for k, v in section.items()})

    def numeric_strings(self) -> tuple[str, ...]:
        """String forms of every threshold, for the leak guard.

        Includes the spaced ("70 %") and spelled ("70 percent") percent
        forms (G3 MINOR-3 / G5 M1, M0-T090 carried correction) so a
        threshold cannot leak merely by reformatting.
        """
        out: list[str] = []
        for f in dataclasses.fields(self):
            value = float(getattr(self, f.name))
            percent = round(value * 100)
            out.append(repr(value))
            out.append(f"{value:g}")
            out.append(f"{percent}%")
            out.append(f"{percent} %")
            out.append(f"{percent} percent")
        return tuple(dict.fromkeys(out))

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class DetectorPolicy:
    """No-progress / repeated-attempt / scope-drift detector knobs
    (D-024 s6, s6.2). Progress is defined by durable evidence, so the
    no-progress window counts minutes without NEW durable evidence, not text
    volume or tool activity."""

    no_progress_window_minutes: int = 20
    repeated_attempt_limit: int = 3
    scope_drift_outside_lease: bool = True

    def __post_init__(self) -> None:
        if self.no_progress_window_minutes <= 0:
            raise ContractError("bad_detector",
                                "no_progress_window_minutes must be positive")
        if self.repeated_attempt_limit <= 0:
            raise ContractError("bad_detector",
                                "repeated_attempt_limit must be positive")

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class SupervisionEnvelope:
    """The controller-only half of the pre-spawn record pair (D-024 s6).

    Nothing in this record is ever rendered into worker-facing text; the leak
    guard proves it for every rendered prompt. ``model_context_window=None``
    is the honest representation of "unknown", never zero.
    """

    assignment_id: str
    size_class: str
    cohesion_rationale: str
    graph_files: tuple[str, ...] = ()
    graph_symbols: tuple[str, ...] = ()
    graph_tests: tuple[str, ...] = ()
    write_lease_paths: tuple[str, ...] = ()
    lease_resources: tuple[str, ...] = ()
    startup_overhead_note: str = ""
    packet_reuse_plan: str = ""
    resolved_model: str = ""
    model_context_window: int | None = None
    telemetry_sources: tuple[str, ...] = ()
    telemetry_confidence: str = "unknown"
    health_bands: HealthBands = dataclasses.field(default_factory=HealthBands)
    detectors: DetectorPolicy = dataclasses.field(default_factory=DetectorPolicy)
    emergency_ceiling_note: str = ""
    landing_opportunities: tuple[str, ...] = ()
    extension_criteria: tuple[str, ...] = ()
    evidence_inspection_plan: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["health_bands"] = self.health_bands.to_dict()
        data["detectors"] = self.detectors.to_dict()
        return data

    def digest(self) -> str:
        return _digest(self.to_dict())


def validate_envelope(envelope: SupervisionEnvelope) -> None:
    if not envelope.assignment_id:
        raise ContractError("missing_ids", "envelope requires assignment_id")
    if envelope.size_class not in WORK_CLASSES:
        raise ContractError(
            "bad_size_class",
            f"size_class {envelope.size_class!r} is not one of "
            f"{list(WORK_CLASSES)}")
    if envelope.size_class == COHESIVE_SUBAGENT \
            and not envelope.cohesion_rationale.strip():
        raise ContractError(
            "missing_cohesion",
            "a cohesive-subagent envelope must say WHY this is one cohesive "
            "unit (D-024 s6)")
    if envelope.model_context_window is not None:
        if isinstance(envelope.model_context_window, bool) \
                or not isinstance(envelope.model_context_window, int) \
                or envelope.model_context_window <= 0:
            raise ContractError(
                "bad_context_window",
                "model_context_window must be a positive integer or None "
                "(unknown is None, never zero)")
    if not envelope.telemetry_sources:
        raise ContractError("missing_telemetry",
                            "the envelope must name its telemetry sources "
                            "(D-024 s6)")
    unknown_sources = sorted(set(envelope.telemetry_sources)
                             - set(TELEMETRY_SOURCES))
    if unknown_sources:
        raise ContractError(
            "unknown_telemetry_source",
            f"telemetry sources {unknown_sources} are not in the Phase B "
            f"closed set {list(TELEMETRY_SOURCES)}")
    if envelope.telemetry_confidence not in CONFIDENCE_LABELS:
        raise ContractError(
            "bad_confidence",
            f"telemetry_confidence {envelope.telemetry_confidence!r} is not "
            f"in the closed confidence vocabulary")
    if envelope.write_lease_paths:
        _normalized_lease(envelope.write_lease_paths)


def validate_pair(assignment: WorkerAssignment,
                  envelope: SupervisionEnvelope) -> None:
    """Validate the two linked records together (D-024 s6)."""
    validate_assignment(assignment)
    validate_envelope(envelope)
    if assignment.assignment_id != envelope.assignment_id:
        raise ContractError(
            "unlinked_records",
            f"assignment {assignment.assignment_id!r} and envelope "
            f"{envelope.assignment_id!r} are not the same pre-spawn pair")
    if assignment.role == ROLE_WRITE and not envelope.write_lease_paths:
        raise ContractError(
            "write_without_lease",
            "a write-role pair requires an ownership/write lease in the "
            "envelope (D-024 s6; never overlapping writers)")
    if assignment.role != ROLE_WRITE and envelope.write_lease_paths:
        raise ContractError(
            "lease_without_write",
            "a read-only/review-only assignment must not hold a write lease")


#: Absolute lease forms: POSIX root, UNC/backslash root, or a drive letter.
_ABSOLUTE_LEASE = re.compile(r"^(?:[/\\]|[a-z]:[/\\]?)", re.IGNORECASE)


def _normalize_lease_path(path: str) -> str:
    """Canonicalize ONE lease path, failing closed on unusable forms
    (G3 MINOR-4 + G5 M3, M0-T090 carried corrections).

    Leases are repository-relative by definition: absolute paths and
    traversal segments are rejected outright (never silently normalized into
    something grantable), dot-segments are normalized so ``./pkg`` and
    ``pkg/./sub`` cannot dodge overlap detection, and a path that normalizes
    to the repository root (``/``, ``.``, empty) is refused - a root write
    lease would previously normalize to the empty string and overlap nothing.
    """
    if not path or not path.strip():
        raise ContractError(
            "bad_lease_path", "lease path must be a non-empty string")
    raw = path.strip()
    if _ABSOLUTE_LEASE.match(raw):
        raise ContractError(
            "bad_lease_path",
            f"lease path {path!r} is absolute; write leases are "
            f"repository-relative (D-024 s6)")
    converted = raw.replace("\\", "/")
    if any(segment == ".." for segment in converted.split("/")):
        raise ContractError(
            "bad_lease_path",
            f"lease path {path!r} contains a traversal segment; leases "
            f"never escape the repository")
    normalized = posixpath.normpath(converted).strip("/").lower()
    if normalized in ("", "."):
        raise ContractError(
            "bad_lease_path",
            f"lease path {path!r} normalizes to the repository root; a "
            f"root write lease is never granted")
    return normalized


def _normalized_lease(paths: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(_normalize_lease_path(p) for p in paths)


def _scopes_overlap(a: tuple[str, ...], b: tuple[str, ...]) -> str | None:
    for pa in _normalized_lease(a):
        for pb in _normalized_lease(b):
            if pa == pb or pa.startswith(pb + "/") or pb.startswith(pa + "/"):
                return pa if len(pa) >= len(pb) else pb
    return None


def assert_grantable(envelopes: tuple[SupervisionEnvelope, ...],
                     candidate: SupervisionEnvelope) -> None:
    """Refuse overlapping write scopes and producer-cap violations.

    ``envelopes`` are the ACTIVE write-holding envelopes (including any held
    by nested children — children pass through this same check, so nesting
    cannot evade the cap or the leases; D-024 s16.2).

    SNAPSHOT, NOT A LOCK (G5 M4, M0-T090 carried correction): this function
    validates ONE candidate against a caller-supplied snapshot of the active
    set; two candidates validated against the same snapshot can both pass
    and then overlap. The runtime therefore never calls this concurrently
    against a shared snapshot — ``lease_runtime.LeaseLedger`` serializes
    grants and folds each granted envelope into the active set before the
    next candidate is checked. Any future runtime consumer must go through
    that ledger (or an equivalent serialized fold), never through bare
    snapshot validation.
    """
    active_writers = [e for e in envelopes if e.write_lease_paths]
    if candidate.write_lease_paths:
        if len(active_writers) >= PRODUCER_CAP:
            raise ContractError(
                "producer_cap",
                f"{len(active_writers)} write producers already active; the "
                f"repository cap is {PRODUCER_CAP} concurrent producers "
                f"(D-024 s6) - queue or run read-only")
        for held in active_writers:
            overlap = _scopes_overlap(held.write_lease_paths,
                                      candidate.write_lease_paths)
            if overlap:
                raise ContractError(
                    "lease_overlap",
                    f"write scope overlaps active lease held by "
                    f"{held.assignment_id!r} at {overlap!r}; overlapping "
                    f"writers are never permitted (D-024 s6)")
    shared = candidate.lease_resources and {
        r for e in active_writers for r in e.lease_resources
    } & set(candidate.lease_resources)
    if shared:
        raise ContractError(
            "resource_overlap",
            f"shared mutable resource(s) {sorted(shared)} already leased; "
            f"one writer per branch/migration/resource (D-024 s6)")


_PROMPT_TEMPLATE = """# Assignment {assignment_id} (parent task {parent_task_id})

## Exact change
{exact_change}

## Why this is necessary
{necessity}

## Role
{role}

## Permitted files/directories and tools
{permitted}

## Prohibited areas and external effects
{prohibited}

## Deliverable and return schema
{deliverable_schema}

## Acceptance criteria (good enough means exactly this)
{acceptance}

## Required tests / evidence
{evidence}

## Checkpoints
{checkpoints}

## Duties
- {blocker_reporting}
- {unrelated_discovery}
- Checkpoint/commit allowed: {commit_allowed}.
- Extension protocol: {extension_protocol}
- Handoff: {handoff_requirements}
"""


def _bullets(items: tuple[str, ...], empty: str) -> str:
    if not items:
        return empty
    return "\n".join(f"- {item}" for item in items)


def render_worker_prompt(assignment: WorkerAssignment,
                         envelope: SupervisionEnvelope) -> str:
    """Render the worker-facing prompt from the assignment ONLY, then prove
    both guards on the rendered text: no quota/countdown language (R045) and
    no leakage of the envelope's numeric bands or band vocabulary (s6)."""
    validate_pair(assignment, envelope)
    permitted = _bullets(
        assignment.permitted_paths + assignment.permitted_tools,
        "- (none granted; read the assignment)")
    prohibited = _bullets(
        assignment.prohibited_areas + assignment.prohibited_external_effects,
        "- stay strictly within the permitted scope")
    prompt = _PROMPT_TEMPLATE.format(
        assignment_id=assignment.assignment_id,
        parent_task_id=assignment.parent_task_id,
        exact_change=assignment.exact_change,
        necessity=assignment.necessity,
        role=assignment.role,
        permitted=permitted,
        prohibited=prohibited,
        deliverable_schema=assignment.deliverable_schema,
        acceptance=_bullets(assignment.acceptance_criteria, "- (missing)"),
        evidence=_bullets(assignment.required_evidence,
                          "- return the evidence your deliverable claims"),
        checkpoints=_bullets(assignment.checkpoints,
                             "- single step; no intermediate checkpoints"),
        blocker_reporting=assignment.blocker_reporting,
        unrelated_discovery=assignment.unrelated_discovery,
        commit_allowed="yes" if assignment.checkpoint_commit_allowed else "no",
        extension_protocol=assignment.extension_protocol,
        handoff_requirements=assignment.handoff_requirements,
    )
    assert_worker_text_clean("rendered_prompt", prompt)
    assert_no_envelope_leak(prompt, envelope)
    return prompt


#: Band-vocabulary leak patterns (G3 MAJOR-1 / G5 M2, M0-T090 carried
#: correction): match the qualified vocabulary tokens and band-context
#: phrases on WORD BOUNDARIES. Bare "observe"/"land" substrings are common
#: English ("landing", "island", "England", "observe the failing test") and
#: are no longer treated as leaks unless they appear in band context.
_BAND_LEAK_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE) for p in (
        r"\bprepare[\s_-]+to[\s_-]+land\b",
        r"\bemergency[\s_-]+stop\b",
        r"\b(?:health\s+)?bands?\s+(?:normal|observe|prepare|land|emergency)\w*",
        r"\b(?:normal|observe|prepare|land|emergency)[\s_-]+bands?\b",
    ))


def assert_no_envelope_leak(prompt: str,
                            envelope: SupervisionEnvelope) -> None:
    """The envelope is controller policy: none of its band names, threshold
    values, window numbers, or detector counters may appear in worker text."""
    for pattern in _BAND_LEAK_PATTERNS:
        match = pattern.search(prompt)
        if match:
            raise ContractError(
                "envelope_leak",
                f"worker prompt contains the private band vocabulary "
                f"({match.group(0)!r}); band names never reach a worker "
                f"(D-024 s6)")
    leak_values: list[str] = list(envelope.health_bands.numeric_strings())
    if envelope.model_context_window is not None:
        leak_values.append(str(envelope.model_context_window))
    leak_values.append(str(envelope.detectors.no_progress_window_minutes))
    leak_values.append(str(envelope.detectors.repeated_attempt_limit))
    for value in leak_values:
        if value and value in prompt:
            raise ContractError(
                "envelope_leak",
                f"worker prompt contains the private controller value "
                f"{value!r}; supervision numbers never reach the worker "
                f"(D-024 s6)")


@dataclasses.dataclass(frozen=True)
class ContractPair:
    """The recorded, digest-bound pre-spawn pair."""

    assignment: WorkerAssignment
    envelope: SupervisionEnvelope

    def to_dict(self) -> dict[str, Any]:
        return {
            "assignment": self.assignment.to_dict(),
            "envelope": self.envelope.to_dict(),
            "assignment_digest": self.assignment.digest(),
            "envelope_digest": self.envelope.digest(),
        }


def build_pair(assignment: WorkerAssignment,
               envelope: SupervisionEnvelope) -> ContractPair:
    validate_pair(assignment, envelope)
    return ContractPair(assignment=assignment, envelope=envelope)
