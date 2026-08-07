#!/usr/bin/env python3
"""Review-packet admission: the 0A.4 token budget and the AD-083 content guard.

Two gates stand between a built evidence packet and a fresh ephemeral Codex
review. Both run BEFORE any process starts, and both fail closed.

**The 0A.4 budget (token size).** 0A.4 fixes a configurable budget on every
review packet:

    target review packet: <= 32,000 estimated input tokens
    ordinary hard ceiling: <= 64,000 estimated input tokens
    relative hard ceiling: <= 20% of the reported Codex model context window
    effective hard ceiling: the LOWER of the ordinary and relative ceilings

These are engineering-policy numbers, not claims about provider billing (0A.4
says so). Token counts are ESTIMATES from a deterministic bytes->tokens
heuristic; this module never pretends to know the provider's real tokenizer. When
a packet exceeds the effective ceiling it is REFUSED with split/summarize guidance
and an explicit record. 0A.4 rule 5 is absolute: a material requirement is NEVER
silently omitted to fit the budget. Every assessment records estimated tokens,
bytes, included sources, omissions, and truncation status.

**The AD-083 content guard (what may appear).** 0A.1 lists material a normal
review must NEVER receive - the whole transcript, the full directive registry,
every historical report, unrelated task packets, the entire repository, all logs,
a full code-graph dump. The guard detects each category and either REJECTS the
packet (fail-closed default) or STRIPS the offending section, recording a finding
either way. It never edits a packet silently.

The key-name/completeness-flag detection is STRUCTURAL: it catches whole material
carried under a known key or self-declared complete, but it cannot see a whole
transcript smuggled as a string VALUE under an innocuous key (G5 M0-T042 I-1). The
primary control against that is `evidence.build_packet` remaining the SOLE packet
constructor on the review path (it never emits transcripts), locked by a structural
test. As defense-in-depth the guard also enforces a conservative STRUCTURAL byte
cap (`DEFAULT_GUARD_MAX_PACKET_BYTES`) on the serialized packet, BEFORE the 0A.4
token budget: it is far above any legitimate bounded packet, so it never trips a
normal review, but it refuses an oversized packet outright - the one size signal a
value-smuggled dump cannot hide behind an innocuous key name.
"""
from __future__ import annotations

import dataclasses
import math
from typing import Any, Mapping, Sequence

from .models import canonical_json

# ==========================================================================
# 0A.4 - review packet budget
# ==========================================================================

DEFAULT_TARGET_TOKENS = 32_000
DEFAULT_ORDINARY_CEILING_TOKENS = 64_000
DEFAULT_RELATIVE_CEILING_RATIO = 0.20
#: Deterministic bytes-per-token estimate. Four bytes/token is the conventional
#: rough English heuristic; POLICY, not a tokenizer, and configurable.
DEFAULT_BYTES_PER_TOKEN = 4.0


class BudgetError(ValueError):
    """A budget configuration was invalid. Fail closed rather than guess."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class EffectiveCeiling:
    """The resolved 0A.4 ceiling and how it was derived (for the record)."""

    tokens: int
    basis: str
    ordinary_ceiling_tokens: int
    relative_ceiling_tokens: int | None
    relative_applied: bool
    model_context_window: int | None

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class ReviewBudget:
    """The configurable 0A.4 review-packet budget.

    Defaults are exactly the 0A.4 policy numbers. `from_mapping` makes the budget
    configurable (e.g. from controller config) while rejecting unknown keys and
    validating the ordering, so a misconfiguration fails closed instead of
    silently disabling a ceiling.
    """

    target_tokens: int = DEFAULT_TARGET_TOKENS
    ordinary_ceiling_tokens: int = DEFAULT_ORDINARY_CEILING_TOKENS
    relative_ceiling_ratio: float = DEFAULT_RELATIVE_CEILING_RATIO
    bytes_per_token: float = DEFAULT_BYTES_PER_TOKEN

    def __post_init__(self) -> None:
        if self.target_tokens <= 0 or self.ordinary_ceiling_tokens <= 0:
            raise BudgetError("bad_budget", "token ceilings must be positive")
        if self.target_tokens > self.ordinary_ceiling_tokens:
            raise BudgetError("bad_budget",
                              "target must not exceed the ordinary hard ceiling")
        if not 0 < self.relative_ceiling_ratio <= 1:
            raise BudgetError("bad_budget", "relative ceiling ratio must be in (0, 1]")
        if self.bytes_per_token <= 0:
            raise BudgetError("bad_budget", "bytes_per_token must be positive")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ReviewBudget":
        allowed = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise BudgetError("unknown_budget_key",
                              f"unrecognized budget key(s): {unknown}")
        return cls(**data)

    def estimate_tokens(self, size_bytes: int) -> int:
        """Deterministic byte->token estimate (ceil). An ESTIMATE, not billing."""
        return math.ceil(max(0, size_bytes) / self.bytes_per_token)

    def effective_ceiling(self, model_context_window: int | None) -> EffectiveCeiling:
        """The 0A.4 effective ceiling: the LOWER of ordinary and relative.

        When the model context window is unknown/unreported the relative ceiling
        cannot be computed and is NOT applied - the ordinary ceiling stands, and
        the assessment records honestly that the relative ceiling was skipped
        because the window was unknown (never fabricates a window).
        """
        if not model_context_window or model_context_window <= 0:
            return EffectiveCeiling(
                tokens=self.ordinary_ceiling_tokens, basis="ordinary_only",
                ordinary_ceiling_tokens=self.ordinary_ceiling_tokens,
                relative_ceiling_tokens=None, relative_applied=False,
                model_context_window=None)
        relative = int(model_context_window * self.relative_ceiling_ratio)
        tokens = min(self.ordinary_ceiling_tokens, relative)
        basis = ("relative_model_window"
                 if relative < self.ordinary_ceiling_tokens else "ordinary")
        return EffectiveCeiling(
            tokens=tokens, basis=basis,
            ordinary_ceiling_tokens=self.ordinary_ceiling_tokens,
            relative_ceiling_tokens=relative, relative_applied=True,
            model_context_window=model_context_window)


#: The 0A.4 rules 1-4/6 overflow response. Emitted with every over-ceiling refusal
#: so the caller knows how to make the review fit WITHOUT dropping a material
#: requirement (rule 5) or opening a persistent session (rule 6).
SPLIT_SUMMARIZE_GUIDANCE: tuple[str, ...] = (
    "split the task or the review into smaller bounded units",
    "replace full logs with deterministic summaries and exact artifact references",
    "include only the relevant changed hunks and authoritative source excerpts",
    "use bounded code-graph queries instead of any full dump",
    "never silently omit a material requirement to fit the budget",
    "never solve the overflow by opening a giant persistent Codex conversation",
)


@dataclasses.dataclass(frozen=True)
class BudgetAssessment:
    """The recorded outcome of assessing one packet against the budget (0A.4)."""

    within_ceiling: bool
    within_target: bool
    estimated_tokens: int
    size_bytes: int
    target_tokens: int
    effective_ceiling: EffectiveCeiling
    included_sources: tuple[str, ...]
    omissions: tuple[dict[str, Any], ...]
    truncated_sections: tuple[str, ...]
    guidance: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "within_ceiling": self.within_ceiling,
            "within_target": self.within_target,
            "estimated_tokens": self.estimated_tokens,
            "size_bytes": self.size_bytes,
            "target_tokens": self.target_tokens,
            "effective_ceiling": self.effective_ceiling.to_dict(),
            "included_sources": list(self.included_sources),
            "omissions": [dict(o) for o in self.omissions],
            "truncated_sections": list(self.truncated_sections),
            "guidance": list(self.guidance),
        }


def assess_packet_budget(
    *,
    size_bytes: int,
    included_sources: Sequence[str],
    budget: ReviewBudget,
    model_context_window: int | None,
    omissions: Sequence[Mapping[str, Any]] = (),
    truncated_sections: Sequence[str] = (),
) -> BudgetAssessment:
    """Assess a packet's size against the 0A.4 budget and record the result.

    Records estimated tokens, bytes, included sources, omissions, and truncation
    status (0A.4 final paragraph). When the estimate exceeds the effective ceiling
    the assessment is `within_ceiling=False` and carries split/summarize guidance;
    the CALLER must then refuse the review rather than send an oversized packet.
    """
    estimated = budget.estimate_tokens(size_bytes)
    ceiling = budget.effective_ceiling(model_context_window)
    within_ceiling = estimated <= ceiling.tokens
    return BudgetAssessment(
        within_ceiling=within_ceiling,
        within_target=estimated <= budget.target_tokens,
        estimated_tokens=estimated,
        size_bytes=size_bytes,
        target_tokens=budget.target_tokens,
        effective_ceiling=ceiling,
        included_sources=tuple(included_sources),
        omissions=tuple(dict(o) for o in omissions),
        truncated_sections=tuple(truncated_sections),
        guidance=() if within_ceiling else SPLIT_SUMMARIZE_GUIDANCE,
    )


def packet_size_bytes(packet: Mapping[str, Any]) -> int:
    """The on-the-wire size of the packet as the reviewer will send it."""
    recorded = packet.get("size_bytes")
    if isinstance(recorded, int) and recorded > 0:
        return recorded
    return len(canonical_json(packet))


def packet_included_sources(packet: Mapping[str, Any]) -> tuple[str, ...]:
    sections = packet.get("sections")
    if isinstance(sections, Mapping):
        return tuple(sorted(str(k) for k in sections))
    return ()


def packet_omissions(packet: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """Material the packet could NOT establish - never a silent gap (0A.4 rule 5)."""
    failed = packet.get("failed_collections")
    if isinstance(failed, list):
        return tuple(dict(f) for f in failed if isinstance(f, Mapping))
    return ()


def packet_truncations(packet: Mapping[str, Any]) -> tuple[str, ...]:
    trunc = packet.get("truncations")
    if isinstance(trunc, list):
        return tuple(str(t) for t in trunc)
    return ()


def assess_evidence_packet(
    packet: Mapping[str, Any],
    *,
    budget: ReviewBudget,
    model_context_window: int | None,
    extra_omissions: Sequence[Mapping[str, Any]] = (),
) -> BudgetAssessment:
    """Assess an already-built evidence packet (dict form) against the budget."""
    return assess_packet_budget(
        size_bytes=packet_size_bytes(packet),
        included_sources=packet_included_sources(packet),
        budget=budget,
        model_context_window=model_context_window,
        omissions=tuple(packet_omissions(packet))
        + tuple(dict(o) for o in extra_omissions),
        truncated_sections=packet_truncations(packet),
    )


# ==========================================================================
# AD-083 - prohibited-content guard
# ==========================================================================

#: Category id -> section/top-level KEY names that signal the whole-material a
#: normal review must never receive (0A.1). Matched case-insensitively.
PROHIBITED_MARKER_KEYS: Mapping[str, frozenset[str]] = {
    "full_transcript": frozenset({
        "transcript", "full_transcript", "claude_transcript", "conversation",
        "messages", "chat_history", "full_conversation"}),
    "full_directive_registry": frozenset({
        "directive_registry", "all_directives", "directives_full",
        "complete_directive_registry", "full_directive_registry"}),
    "all_historical_reports": frozenset({
        "all_reports", "report_history", "reports_full",
        "complete_report_history", "all_historical_reports"}),
    "whole_repository": frozenset({
        "repository", "repo_dump", "repository_dump", "whole_repository",
        "repo_tree", "repository_tree", "full_repository"}),
    "all_logs": frozenset({"all_logs", "logs_full", "complete_logs", "full_logs"}),
    "full_code_graph": frozenset({
        "full_code_graph", "code_graph_dump", "code_graph_full", "graph_dump"}),
}

#: I-1 defense-in-depth: a conservative STRUCTURAL byte cap enforced at the guard
#: itself, before the 0A.4 token budget. It is far above any legitimate bounded
#: packet (the 0A.4 ordinary ceiling is ~64k tokens ~= 256 KB) so it never trips a
#: normal review, but it refuses a whole transcript / repository dump smuggled as a
#: string VALUE under an innocuous key - the exact gap the key-name/flag guard
#: cannot see - by size (fail closed).
DEFAULT_GUARD_MAX_PACKET_BYTES = 8_000_000

#: A boolean flag inside a section that self-declares it carries whole material.
COMPLETENESS_FLAGS: tuple[str, ...] = (
    "complete", "full", "complete_history", "all_history", "complete_registry",
    "full_registry", "whole_repository", "entire_repository")


@dataclasses.dataclass(frozen=True)
class GuardFinding:
    """One detected prohibited-content category, its location, and the action."""

    category: str
    location: str
    action: str  # "rejected" | "stripped"
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class GuardError(Exception):
    """A packet carried prohibited content and could not be trusted as-is."""

    def __init__(self, code: str, message: str,
                 findings: tuple[GuardFinding, ...] = ()) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.findings = findings


@dataclasses.dataclass(frozen=True)
class GuardResult:
    """The guard's verdict: whether the packet is clean (or was sanitized)."""

    ok: bool
    findings: tuple[GuardFinding, ...]
    packet: dict[str, Any] | None

    @property
    def rejected(self) -> bool:
        return not self.ok


def _scan_marker_keys(container: Mapping[str, Any], scope: str,
                      findings: list[GuardFinding], action: str) -> None:
    for key in list(container):
        if not isinstance(key, str):
            continue
        for category, names in PROHIBITED_MARKER_KEYS.items():
            if key.lower() in names:
                findings.append(GuardFinding(
                    category=category, location=f"{scope}.{key}", action=action,
                    detail=f"a section named {key!r} carries whole material a "
                           f"normal review must never receive (0A.1)"))


def _scan_unrelated_task_packets(sections: Mapping[str, Any], current_task_id: str,
                                 findings: list[GuardFinding], action: str) -> None:
    packets = sections.get("task_packets")
    if not isinstance(packets, list):
        return
    for index, entry in enumerate(packets):
        if not isinstance(entry, Mapping):
            continue
        task_id = entry.get("task_id")
        if isinstance(task_id, str) and current_task_id and task_id != current_task_id:
            findings.append(GuardFinding(
                category="unrelated_task_packets",
                location=f"sections.task_packets[{index}]", action=action,
                detail=f"packet for {task_id!r} is unrelated to the checkpoint "
                       f"under review ({current_task_id!r})"))


def _scan_completeness_flags(sections: Mapping[str, Any],
                            findings: list[GuardFinding], action: str) -> None:
    """A section that self-declares completeness (e.g. reports with all_history)."""
    watch = {"reports": "all_historical_reports",
             "directives": "full_directive_registry",
             "logs": "all_logs"}
    for name, category in watch.items():
        section = sections.get(name)
        if not isinstance(section, Mapping):
            continue
        for flag in COMPLETENESS_FLAGS:
            if bool(section.get(flag)):
                findings.append(GuardFinding(
                    category=category, location=f"sections.{name}.{flag}",
                    action=action,
                    detail=f"section {name!r} declares {flag}=true, i.e. the whole "
                           f"history/registry rather than the bounded slice a review needs"))
                break


def _scan_packet_size(packet: Mapping[str, Any], max_bytes: int,
                      findings: list[GuardFinding], action: str) -> None:
    """A serialized packet over the structural byte cap is refused (I-1).

    This is the one signal a whole-material dump smuggled as a string VALUE under
    an innocuous key cannot hide: its SIZE. The cap is far above any legitimate
    bounded packet, so a normal review never trips it.
    """
    if max_bytes <= 0:
        return
    size = len(canonical_json(packet))
    if size > max_bytes:
        findings.append(GuardFinding(
            category="oversized_packet", location="packet", action=action,
            detail=f"the serialized packet is {size} bytes, over the structural guard "
                   f"cap of {max_bytes}; whole material may be smuggled as a string "
                   f"value under an innocuous key (0A.1/AD-083 I-1)"))


def guard_packet(packet: Mapping[str, Any], *, current_task_id: str,
                 strip: bool = False,
                 max_packet_bytes: int = DEFAULT_GUARD_MAX_PACKET_BYTES) -> GuardResult:
    """Detect (and optionally strip) prohibited whole-material (AD-083 / 0A.1).

    Default (`strip=False`) is fail-closed: any finding REJECTS the packet
    (`ok=False`, `packet=None`) so it can never reach a review. `strip=True`
    returns a sanitized copy with the offending sections/keys removed and each
    removal recorded as a `stripped` finding. Either way nothing is dropped
    silently - every category caught is a recorded `GuardFinding`.

    A conservative STRUCTURAL byte cap (`max_packet_bytes`) is enforced here too,
    catching whole material smuggled as a string value under an innocuous key -
    the I-1 gap the key-name/flag detection cannot see - by size (fail closed).
    """
    action = "stripped" if strip else "rejected"
    findings: list[GuardFinding] = []
    sections = packet.get("sections")
    sections = sections if isinstance(sections, Mapping) else {}
    _scan_marker_keys(packet, "packet", findings, action)
    _scan_marker_keys(sections, "sections", findings, action)
    _scan_unrelated_task_packets(sections, current_task_id, findings, action)
    _scan_completeness_flags(sections, findings, action)
    _scan_packet_size(packet, max_packet_bytes, findings, action)
    if not findings:
        return GuardResult(ok=True, findings=(), packet=dict(packet))
    if not strip:
        return GuardResult(ok=False, findings=tuple(findings), packet=None)
    return GuardResult(ok=True, findings=tuple(findings),
                       packet=_apply_strip(packet, findings, current_task_id))


def _apply_strip(packet: Mapping[str, Any], findings: Sequence[GuardFinding],
                 current_task_id: str) -> dict[str, Any]:
    """Remove every flagged location; recompute-sensitive meta is dropped so a
    downstream digest/size reflects the sanitized packet, not the original."""
    result = dict(packet)
    sections = dict(result["sections"]) if isinstance(result.get("sections"), Mapping) else {}
    for finding in findings:
        parts = finding.location.split(".")
        if parts[0] == "packet" and len(parts) >= 2:
            result.pop(parts[1], None)
        elif parts[0] == "sections":
            if finding.category == "unrelated_task_packets":
                kept = [p for p in sections.get("task_packets", [])
                        if not (isinstance(p, Mapping)
                                and p.get("task_id") not in ("", None, current_task_id))]
                if kept:
                    sections["task_packets"] = kept
                else:
                    sections.pop("task_packets", None)
            elif len(parts) >= 2:
                sections.pop(parts[1].split("[")[0], None)
    if isinstance(result.get("sections"), Mapping):
        result["sections"] = sections
    # A strip changes content: drop stale identity/size so callers recompute.
    result.pop("packet_digest", None)
    result.pop("size_bytes", None)
    return result
