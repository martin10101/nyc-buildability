"""Graph-based sizing and smallest-complete packet planning
(D-024 Phase C item 5, M0-T090).

Bridges the controller's spawn planning to the EXISTING context-intelligence
deliverables without duplicating them (D-024-R081 "preserve the graph and
context-intelligence system"):

- graph evidence arrives as the plain dict shape produced by
  ``tools.repo_views.neighborhood_edges`` — adapted here by value, so the
  supervisor package stays a leaf (no import of the index/graph machinery,
  no cache side effects, testable without an index build);
- STALE graph data is carried as an explicit flag and turns sizing
  conservative; it is reported, never acted on as fact (D-024-R080);
- tier selection REUSES ``tools.context_pack_budget.select_tier`` (the
  accepted adaptive-tier amendment) via a lazy import — the tier names,
  targets, ceilings, and the medium/large-without-justification withholding
  are preserved exactly, never redefined (D-024-R081, s13);
- the packet PLAN records the smallest complete packet for the role per
  s13 — exact bounded task, authority/prohibitions, frozen evidence refs,
  graph-selected files/symbols, decisions/risks, return schema — and marks
  every omitted category with why it is not required. If sufficiency cannot
  be proven the plan says STOP rather than silently removing a constraint.

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any

#: The s13 packet categories a smallest-complete packet covers.
PACKET_CATEGORIES: tuple[str, ...] = (
    "bounded_task_and_acceptance",
    "authority_and_prohibitions",
    "frozen_identity_evidence",
    "graph_selected_files_symbols",
    "known_decisions_and_risks",
    "return_schema",
)

#: s13 categories that are NEVER omittable for any role (G4 ADV-1, M0-T090
#: carried correction): a model call without its exact bounded task and
#: acceptance criteria, its authority and prohibitions, or its requested
#: return schema cannot be correct, so no justification can omit them. The
#: remaining categories stay justified-omittable per role
#: (``graph_selected_files_symbols`` additionally carries its own
#: source-sufficiency stop).
NON_OMITTABLE_CATEGORIES: tuple[str, ...] = (
    "bounded_task_and_acceptance",
    "authority_and_prohibitions",
    "return_schema",
)


class SizingError(ValueError):
    """Typed error for sizing/packet planning (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _budget():
    """Lazy import of the accepted tier module (repo-root namespace package).

    Lazy so ``tools.agent_supervisor`` remains importable standalone (its
    ``__main__`` bootstraps sys.path); failing to find the accepted tier
    module is a typed, fail-closed error — this module never ships a
    replacement tier table (D-024-R081)."""
    try:
        from tools import context_pack_budget as budget
    except ImportError as exc:  # pragma: no cover - environment-shaped
        raise SizingError(
            "budget_unavailable",
            f"tools.context_pack_budget is not importable ({exc}); sizing "
            f"refuses to invent packet tiers (D-024-R081)") from exc
    return budget


@dataclasses.dataclass(frozen=True)
class GraphNeighborhood:
    """Graph-derived neighborhood evidence for one seed, by value.

    ``stale=True`` means the underlying index did not match the live tree
    fingerprint when the view was produced; the numbers are then treated as
    MISSING for classification (D-024-R080), and the classifier lands in
    unknown-recon-first via ``WorkloadFeatures.graph_stale``.
    """

    seed_path: str
    files: tuple[str, ...] = ()
    symbols: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    dependency_breadth: int = 0
    truncated: bool = False
    stale: bool = False
    stale_reason: str = ""

    def __post_init__(self) -> None:
        if not self.seed_path:
            raise SizingError("missing_seed", "seed_path is required")
        if self.dependency_breadth < 0:
            raise SizingError("negative_breadth",
                              "dependency_breadth may not be negative")


def neighborhood_from_view(seed_path: str, view: Mapping[str, Any], *,
                           stale: bool = False,
                           stale_reason: str = "") -> GraphNeighborhood:
    """Adapt a ``repo_views.neighborhood_edges`` result dict.

    Expected keys: ``out_edges``/``in_edges`` (lists of edge dicts with
    ``from``/``to``), ``in_edge_count``, ``out_truncation``/``in_truncation``.
    Anything malformed fails closed rather than yielding an optimistic empty
    neighborhood.
    """
    if not isinstance(view, Mapping):
        raise SizingError("bad_view", "neighborhood view must be a mapping")
    for key in ("out_edges", "in_edges"):
        if key not in view or not isinstance(view[key], (list, tuple)):
            raise SizingError(
                "bad_view", f"neighborhood view is missing list {key!r}; a "
                            f"malformed view is never treated as an empty "
                            f"neighborhood")
    files: set[str] = set()
    symbols: set[str] = set()
    tests: set[str] = set()
    importers: set[str] = set()
    for direction in ("out_edges", "in_edges"):
        for edge in view[direction]:
            if not isinstance(edge, Mapping):
                continue
            for end in ("from", "to"):
                node = edge.get(end)
                if not isinstance(node, str) or not node:
                    continue
                if "::" in node or "#" in node:
                    symbols.add(node)
                    continue
                files.add(node)
                lowered = node.lower()
                if "test" in lowered.rsplit("/", 1)[-1]:
                    tests.add(node)
            if direction == "in_edges" and isinstance(edge.get("from"), str):
                importers.add(edge["from"])
    declared = view.get("in_edge_count")
    breadth = declared if isinstance(declared, int) and declared >= 0 \
        else len(importers)
    truncated = bool(view.get("out_truncation")) or bool(view.get("in_truncation"))
    return GraphNeighborhood(
        seed_path=seed_path,
        files=tuple(sorted(files)),
        symbols=tuple(sorted(symbols)),
        tests=tuple(sorted(tests)),
        dependency_breadth=breadth,
        truncated=truncated,
        stale=stale,
        stale_reason=stale_reason,
    )


def tier_signals(neighborhood: GraphNeighborhood, *,
                 changed_files: int = 0,
                 subsystems_touched: int = 0,
                 architectural: bool = False,
                 explicit_tier: str | None = None,
                 justification: str | None = None):
    """Build ``context_pack_budget.TierSignals`` from graph evidence.

    A stale neighborhood refuses to produce signals: stale breadth silently
    fed into tier selection would be acting on stale data as fact
    (D-024-R080).
    """
    if neighborhood.stale:
        raise SizingError(
            "stale_graph",
            f"neighborhood for {neighborhood.seed_path!r} is stale "
            f"({neighborhood.stale_reason or 'fingerprint mismatch'}); "
            f"refresh the index or classify as unknown-recon-first instead "
            f"of sizing from stale data")
    budget = _budget()
    return budget.TierSignals(
        dependency_breadth=neighborhood.dependency_breadth,
        changed_files=changed_files,
        subsystems_touched=subsystems_touched,
        architectural=architectural,
        explicit_tier=explicit_tier,
        justification=justification,
    )


@dataclasses.dataclass(frozen=True)
class PacketPlan:
    """The recorded smallest-complete packet plan for one assignment role
    (s13). A plan, not an assembly: ``tools/context_pack_assembly`` remains
    the only packet builder."""

    assignment_id: str
    role: str
    tier: str
    target_tokens: int
    tier_justification: str
    withheld_larger_target: bool
    included: tuple[str, ...]
    sources: tuple[str, ...]
    omissions: tuple[tuple[str, str], ...]
    sufficient: bool
    stop_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def packet_plan(*, assignment_id: str, role: str,
                neighborhood: GraphNeighborhood,
                signals: Any,
                omissions: tuple[tuple[str, str], ...] = (),
                extra_sources: tuple[str, ...] = ()) -> PacketPlan:
    """Plan the smallest complete packet for the role at the selected tier.

    Every s13 category is either INCLUDED (with its graph-selected sources)
    or listed in ``omissions`` with why it is not required for this role. A
    category that is neither included nor justified marks the plan
    insufficient with ``stop_reason`` — "if packet sufficiency cannot be
    proven, stop rather than silently remove a required constraint" (s13).
    """
    if not assignment_id or not role:
        raise SizingError("missing_fields", "assignment_id and role are required")
    budget = _budget()
    decision = budget.select_tier(assignment_id, role, signals)
    omitted_categories = {category for category, _ in omissions}
    for category, why in omissions:
        if category not in PACKET_CATEGORIES:
            raise SizingError(
                "unknown_category",
                f"omission names unknown packet category {category!r}")
        if category in NON_OMITTABLE_CATEGORIES:
            raise SizingError(
                "non_omittable_category",
                f"packet category {category!r} is mandatory for every role "
                f"and can never be omitted, with or without justification "
                f"(s13; G4 ADV-1 carried correction)")
        if not why.strip():
            raise SizingError(
                "unjustified_omission",
                f"omitted category {category!r} must say why it is not "
                f"required (s13: explicitly mark omitted material)")
    included = tuple(c for c in PACKET_CATEGORIES if c not in omitted_categories)
    sources = tuple(dict.fromkeys(
        neighborhood.files + neighborhood.tests + extra_sources))
    sufficient = True
    stop_reason = ""
    if "graph_selected_files_symbols" in included and not sources:
        sufficient = False
        stop_reason = ("no graph-selected sources are available for an "
                       "included category; packet sufficiency cannot be "
                       "proven - stop rather than silently removing the "
                       "constraint (s13)")
    if neighborhood.truncated:
        sufficient = False
        stop_reason = (stop_reason + "; " if stop_reason else "") + (
            "the graph neighborhood was truncated, so the smallest-complete "
            "set may be incomplete; widen the view or justify the truncation "
            "before dispatch")
    return PacketPlan(
        assignment_id=assignment_id,
        role=role,
        tier=decision.tier,
        target_tokens=decision.target_tokens,
        tier_justification=decision.justification or "",
        withheld_larger_target=decision.withheld_larger_target,
        included=included,
        sources=sources,
        omissions=omissions,
        sufficient=sufficient,
        stop_reason=stop_reason,
    )
