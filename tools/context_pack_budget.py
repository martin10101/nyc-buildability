#!/usr/bin/env python3
"""Context-pack budget + adaptive tier (M0-T065 Unit B).

Section A -- the 0A.4 budget PRIMITIVES: a LOCAL mirror of
``tools/agent_supervisor/review_packet.py`` (the frozen shadow-only supervisor).
The drift-lock test in ``tools/test_context_pack.py`` asserts these constants and
functions never diverge from that module, so NOTHING in Section A may change --
the adaptive tier in Section B layers strictly on top.

Section B -- the adaptive-tier AMENDMENT (D-013-R041 / R080; source-002 owner
decision 7). It introduces small/normal (~5K-8K), medium (explicit, justified by
dependency breadth), and large/architectural (split-first) TARGET tiers as an
EXPLICIT owner-approved amendment to the accepted context-budget contract
(32K target / 64K ordinary ceiling / 20% relative ceiling). It NEVER rewrites
that contract: the tier only sets the TARGET; the hard ceiling stays
``effective_ceiling_tokens(...) = min(ordinary, relative)`` (Section A), and the
accepted constants are physically unchanged. The amendment is recorded verbatim
(``BUDGET_AMENDMENT``) and emitted into ``context.meta.json`` so a reviewer sees
that the protected numbers were not touched.
"""
from __future__ import annotations

import dataclasses
import math

# ==========================================================================
# Section A -- 0A.4 budget primitives (drift-locked to review_packet.py).
# ==========================================================================

DEFAULT_TARGET_TOKENS = 32_000
DEFAULT_ORDINARY_CEILING_TOKENS = 64_000
DEFAULT_RELATIVE_CEILING_RATIO = 0.20
#: Deterministic bytes-per-token estimate. Four bytes/token is the conventional
#: rough English heuristic; POLICY, not a tokenizer, and configurable.
DEFAULT_BYTES_PER_TOKEN = 4.0

#: 0A.4 rules 1-4/6 overflow response, emitted with every over-ceiling refusal.
SPLIT_SUMMARIZE_GUIDANCE = (
    "split the task or the review into smaller bounded units",
    "replace full logs with deterministic summaries and exact artifact references",
    "include only the relevant changed hunks and authoritative source excerpts",
    "use bounded code-graph queries instead of any full dump",
    "never silently omit a material requirement to fit the budget",
    "never solve the overflow by opening a giant persistent conversation",
)


def estimate_tokens(size_bytes: int, bytes_per_token: float = DEFAULT_BYTES_PER_TOKEN) -> int:
    """Deterministic byte->token estimate (ceil). An ESTIMATE, not billing."""
    return math.ceil(max(0, size_bytes) / bytes_per_token)


def effective_ceiling_tokens(
    ordinary_ceiling_tokens: int,
    relative_ratio: float,
    model_context_window: int | None,
) -> dict:
    """The 0A.4 effective ceiling: the LOWER of ordinary and relative.

    When the model context window is unknown/unreported the relative ceiling
    cannot be computed and is NOT applied -- the ordinary ceiling stands and the
    record says so honestly (a window is never fabricated).
    """
    if not model_context_window or model_context_window <= 0:
        return {
            "tokens": ordinary_ceiling_tokens,
            "basis": "ordinary_only",
            "ordinary_ceiling_tokens": ordinary_ceiling_tokens,
            "relative_ceiling_tokens": None,
            "relative_applied": False,
            "model_context_window": None,
        }
    relative = int(model_context_window * relative_ratio)
    tokens = min(ordinary_ceiling_tokens, relative)
    basis = "relative_model_window" if relative < ordinary_ceiling_tokens else "ordinary"
    return {
        "tokens": tokens,
        "basis": basis,
        "ordinary_ceiling_tokens": ordinary_ceiling_tokens,
        "relative_ceiling_tokens": relative,
        "relative_applied": True,
        "model_context_window": model_context_window,
    }


# ==========================================================================
# Section B -- adaptive tier amendment (D-013-R041/R080; owner decision 7).
# ==========================================================================

SMALL = "small"
NORMAL = "normal"
MEDIUM = "medium"
LARGE = "large"
TIERS = (SMALL, NORMAL, MEDIUM, LARGE)

#: Per-tier TARGET token bands (targets, NEVER ceilings). From owner decision 7:
#: small/normal sit in the ~5K-8K band; medium is an explicit larger target
#: justified by dependency breadth and CAPPED at the accepted target (32K);
#: large/architectural keeps the normal target and prefers a split.
TIER_TARGET_TOKENS = {
    SMALL: 5_000,
    NORMAL: 8_000,
    MEDIUM: 16_000,   # explicit, justified; never above DEFAULT_TARGET_TOKENS
    LARGE: 8_000,     # split-first: target stays at normal, prefer_split set
}

#: Deterministic thresholds on the dependency-breadth signal (importer closure +
#: neighborhood size from the A1/A2 index) that PROPOSE a tier. A signal, never a
#: silent grant: medium/large still require an explicit recorded justification.
NORMAL_BREADTH_MAX = 8      # <= this many dependents -> small/normal
MEDIUM_BREADTH_MAX = 40     # <= this -> medium candidate (needs justification)
# above MEDIUM_BREADTH_MAX or architectural -> large (split-first)

#: The owner-approved amendment record, emitted verbatim into context.meta.json.
#: changes_constants is False BY CONSTRUCTION -- Section A is untouched.
BUDGET_AMENDMENT = {
    "amendment_id": "D-013-R041",
    "owner_decision": "source-002 decision 7",
    "amends": "context-budget contract (32K target / 64K ordinary / 20% relative)",
    "adds": ("adaptive TARGET tier: small/normal ~5K-8K; medium = explicit larger "
             "target justified by dependency breadth (capped at the accepted 32K "
             "target); large/architectural = split-first"),
    "changes_constants": False,
    "hard_ceiling": "unchanged: min(ordinary_ceiling, relative_ceiling)",
    "accepted_contract": {
        "target_tokens": DEFAULT_TARGET_TOKENS,
        "ordinary_ceiling_tokens": DEFAULT_ORDINARY_CEILING_TOKENS,
        "relative_ceiling_ratio": DEFAULT_RELATIVE_CEILING_RATIO,
    },
}


@dataclasses.dataclass(frozen=True)
class TierSignals:
    """Deterministic inputs to tier selection. `dependency_breadth` is the size of
    the importer closure + bounded neighborhood from the A1/A2 index; the rest are
    explicit operator inputs. No wall-clock, no randomness."""
    dependency_breadth: int = 0
    changed_files: int = 0
    subsystems_touched: int = 0
    architectural: bool = False
    explicit_tier: str | None = None
    justification: str | None = None


@dataclasses.dataclass(frozen=True)
class TierDecision:
    tier: str
    target_tokens: int
    determining_signals: tuple
    justification: str | None
    prefer_split: bool
    hard_ceiling_unchanged: bool
    withheld_larger_target: bool
    withheld_reason: str | None

    def to_dict(self) -> dict:
        return {
            "tier": self.tier,
            "target_tokens": self.target_tokens,
            "determining_signals": list(self.determining_signals),
            "justification": self.justification,
            "prefer_split": self.prefer_split,
            "hard_ceiling_unchanged": self.hard_ceiling_unchanged,
            "withheld_larger_target": self.withheld_larger_target,
            "withheld_reason": self.withheld_reason,
        }


def _candidate_tier(signals: TierSignals) -> tuple[str, tuple]:
    """Deterministically PROPOSE a tier from the signals, citing the determining
    ones. Higher breadth raises the candidate; an architectural flag forces large.
    An explicit tier request is honored as the candidate (still justification-gated
    below for medium/large)."""
    if signals.explicit_tier in TIERS:
        return signals.explicit_tier, (f"explicit_tier={signals.explicit_tier}",)
    if signals.architectural:
        return LARGE, ("architectural=true",)
    b = signals.dependency_breadth
    if b > MEDIUM_BREADTH_MAX:
        return LARGE, (f"dependency_breadth={b}>{MEDIUM_BREADTH_MAX}",)
    if b > NORMAL_BREADTH_MAX:
        return MEDIUM, (f"dependency_breadth={b}>{NORMAL_BREADTH_MAX}",)
    if b <= 1 and signals.changed_files <= 1:
        return SMALL, (f"dependency_breadth={b}", f"changed_files={signals.changed_files}")
    return NORMAL, (f"dependency_breadth={b}",)


def select_tier(task_id: str, role: str, signals: TierSignals,
                accepted_target_tokens: int = DEFAULT_TARGET_TOKENS) -> TierDecision:
    """Deterministically choose the TARGET tier for a pack.

    Fail-closed honesty (mirrors the model-routing discipline): medium/large set a
    larger target ONLY with a recorded justification. A medium/large candidate
    WITHOUT a justification does not silently grant the larger target -- it is
    recorded and the target is capped at the normal band, with the withheld larger
    target reported. The hard ceiling is never touched here (a separate function),
    so `hard_ceiling_unchanged` is always True. The target never exceeds the
    accepted target contract (never above `accepted_target_tokens`)."""
    tier, sigs = _candidate_tier(signals)
    prefer_split = tier == LARGE
    justification = signals.justification
    withheld = False
    withheld_reason = None

    if tier in (MEDIUM, LARGE) and not justification:
        # No justification -> do NOT grant a larger target. Record the withheld
        # larger target and cap at the normal band (never silently upsize).
        withheld = True
        withheld_reason = (
            f"tier {tier!r} proposed by {', '.join(sigs)} but no justification was "
            f"recorded; target held at the normal band (larger target withheld)")
        target = TIER_TARGET_TOKENS[NORMAL]
    else:
        target = TIER_TARGET_TOKENS[tier]

    # The target NEVER exceeds the accepted target contract (32K).
    target = min(target, accepted_target_tokens)
    return TierDecision(
        tier=tier, target_tokens=target, determining_signals=sigs,
        justification=justification, prefer_split=prefer_split,
        hard_ceiling_unchanged=True, withheld_larger_target=withheld,
        withheld_reason=withheld_reason)
