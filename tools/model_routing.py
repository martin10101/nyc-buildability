#!/usr/bin/env python3
"""Deterministic complexity-based model routing (M0-T074, D-017-R114..R123).

A model is CHOSEN by measured task complexity, risk, and required capability -
never by a model choosing itself. The router:

* classifies work into LOW / MEDIUM / HIGH / CRITICAL from typed deterministic
  signals (every verdict cites its determining signals - an ungrounded
  classification is impossible by construction);
* routes ONLY to models already permitted by the protected controller
  configuration, read through the frozen supervisor's own loader
  (`tools/agent_supervisor/` is never modified, and neither `config.toml` nor
  `model_selection.toml` is ever written);
* reports honestly when a provider's allowlist permits exactly one model:
  `adaptive_available` is False and the single permitted model is used - no
  pretend selection (D-017-R118);
* refuses downgrades of HIGH/CRITICAL work, allows ONE recorded escalation for
  failed LOW/MEDIUM work, and keeps quota fallback a SEPARATE recorded decision
  (D-017-R119/R120);
* records every decision (task, band, determining signals, chosen model,
  permitted-model evidence with the config digest, fallback status, context
  size, result, telemetry when available - nullable, never fabricated zeros)
  as append-only JSONL in the accepted per-checkout runtime directory, outside
  the repository (D-017-R121).

The router is consumed by the ORCHESTRATOR when it dispatches work and reviews.
The supervisor itself stays frozen; any future supervisor-side integration is
its own defect-lane task. If meaningful Claude routing needs a protected
allowlist change, that is an owner action (D-017-R123) - this module never
requests or performs it.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import pathlib
import sys
from typing import Any

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

SCHEMA_VERSION = "model_routing/v1"

LOW, MEDIUM, HIGH, CRITICAL = "LOW", "MEDIUM", "HIGH", "CRITICAL"
BANDS = (LOW, MEDIUM, HIGH, CRITICAL)

#: Deterministic ordering for KNOWN models only. strength: higher = stronger;
#: cost: higher = more expensive. An allowlisted model absent from this table
#: makes routing UNAVAILABLE for that provider (fail closed - never guess an
#: ordering). sol is the primary/stronger Codex reviewer, terra the lower-cost
#: fallback (model_selection runbook s8); opus is the sole permitted Claude.
KNOWN_MODEL_TIERS: dict[str, dict[str, int]] = {
    "gpt-5.6-terra": {"strength": 1, "cost": 1},
    "gpt-5.6-sol": {"strength": 2, "cost": 2},
    "claude-opus-4-8": {"strength": 3, "cost": 3},
}

#: Roles whose verification must use the strongest permitted independent
#: reviewer (D-017-R119).
STRONGEST_REVIEWER_ROLES = frozenset({
    "security-reviewer", "directive-compliance-verifier", "final-acceptance",
})


class RoutingError(Exception):
    """A fail-closed routing refusal."""


@dataclasses.dataclass(frozen=True)
class Signals:
    """Typed deterministic classification inputs (D-017-R116).

    Booleans default False and counts default 0 ONLY because absence of a
    signal is itself deterministic packet-derived input; `ambiguity_or_missing_
    evidence` exists precisely so unknown-ness raises the band instead of
    lowering it.
    """

    files_affected: int = 0
    subsystems_affected: int = 0
    dependency_graph_spread: int = 0
    security_or_authorization_impact: bool = False
    protected_configuration_impact: bool = False
    destructive_operations: bool = False
    control_plane_change: bool = False
    legal_or_numeric_correctness: bool = False
    external_side_effects: bool = False
    schema_or_migration_impact: bool = False
    concurrency_or_performance: bool = False
    ambiguity_or_missing_evidence: bool = False
    prior_failed_attempts: int = 0
    required_reviewer_roles: tuple[str, ...] = ()
    estimated_context_tokens: int | None = None
    packet_risk_classification: str | None = None  # low|medium|high|critical


def classify(signals: Signals) -> tuple[str, list[str]]:
    """Deterministic band + the determining signals that produced it."""
    determined: list[str] = []

    critical_flags = {
        "security_or_authorization_impact": signals.security_or_authorization_impact,
        "protected_configuration_impact": signals.protected_configuration_impact,
        "destructive_operations": signals.destructive_operations,
        "control_plane_change": signals.control_plane_change,
        "legal_or_numeric_correctness": signals.legal_or_numeric_correctness,
        "packet_risk_classification=critical":
            signals.packet_risk_classification == "critical",
        "final-acceptance role":
            "final-acceptance" in signals.required_reviewer_roles,
    }
    determined += [name for name, hit in critical_flags.items() if hit]
    if determined:
        return CRITICAL, determined

    high_flags = {
        "subsystems_affected>1": signals.subsystems_affected > 1,
        "schema_or_migration_impact": signals.schema_or_migration_impact,
        "concurrency_or_performance": signals.concurrency_or_performance,
        "dependency_graph_spread>10": signals.dependency_graph_spread > 10,
        "prior_failed_attempts>=2": signals.prior_failed_attempts >= 2,
        "packet_risk_classification=high":
            signals.packet_risk_classification == "high",
        "estimated_context_tokens>100000":
            (signals.estimated_context_tokens or 0) > 100_000,
    }
    determined = [name for name, hit in high_flags.items() if hit]
    if determined:
        band = HIGH
    else:
        medium_flags = {
            "files_affected>1": signals.files_affected > 1,
            "external_side_effects": signals.external_side_effects,
            "prior_failed_attempts=1": signals.prior_failed_attempts == 1,
            "packet_risk_classification=medium":
                signals.packet_risk_classification == "medium",
        }
        determined = [name for name, hit in medium_flags.items() if hit]
        band = MEDIUM if determined else LOW
        if band == LOW:
            determined = ["no elevating signal"]

    if signals.ambiguity_or_missing_evidence and band in (LOW, MEDIUM):
        promoted = BANDS[BANDS.index(band) + 1]
        determined.append("ambiguity_or_missing_evidence(+1 band)")
        return promoted, determined
    return band, determined


def load_permitted_models(config_path: str | os.PathLike[str]) -> dict[str, Any]:
    """Read-only permitted-model evidence from the PROTECTED controller config.

    Uses the frozen supervisor's own loader so allowlist semantics can never
    drift, and records the config bytes' sha256 as evidence. Never writes.
    """
    from tools.agent_supervisor.config import load_controller_config
    path = pathlib.Path(config_path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    config = load_controller_config(str(path))
    return {
        "config_path_sha256": digest,
        "codex": list(config.codex_allowed_models),
        "claude": list(config.claude_allowed_models),
    }


def _ordered(models: list[str]) -> list[str]:
    unknown = [m for m in models if m not in KNOWN_MODEL_TIERS]
    if unknown:
        raise RoutingError(
            f"unknown model ordering for {unknown}; routing is UNAVAILABLE for "
            f"this provider until the deterministic tier table covers them - "
            f"never guess strength or cost")
    return sorted(models, key=lambda m: KNOWN_MODEL_TIERS[m]["strength"])


def route(task_id: str, provider: str, signals: Signals,
          permitted: dict[str, Any], *,
          role: str = "worker",
          estimated_context_tokens: int | None = None) -> dict[str, Any]:
    """One deterministic routing decision. The caller persists it via
    `append_decision` and later stamps `result`/telemetry via `finalize`."""
    if provider not in ("codex", "claude"):
        raise RoutingError(f"unknown provider {provider!r}")
    allowlist = list(permitted.get(provider, ()))
    if not allowlist:
        raise RoutingError(f"the protected configuration permits NO {provider} "
                           f"models; routing cannot invent one")
    band, determining = classify(signals)
    ordered = _ordered(allowlist)
    adaptive = len(ordered) > 1
    if not adaptive:
        chosen = ordered[0]
        reason = (f"adaptive {provider} routing UNAVAILABLE: the protected "
                  f"allowlist permits exactly one model ({chosen}); using it "
                  f"honestly, not pretending selection occurred")
    elif role in STRONGEST_REVIEWER_ROLES:
        chosen = ordered[-1]
        reason = f"role {role!r} must use the strongest permitted independent reviewer"
    elif band in (HIGH, CRITICAL):
        chosen = ordered[-1]
        reason = f"band {band} uses the stronger permitted model"
    else:
        chosen = ordered[0]
        reason = f"band {band} uses the lower-cost permitted model"
    return {
        "schema": SCHEMA_VERSION,
        "kind": "routing_decision",
        "task_id": task_id,
        "provider": provider,
        "role": role,
        "complexity_band": band,
        "determining_signals": determining,
        "chosen_model": chosen,
        "selection_reason": reason,
        "adaptive_available": adaptive,
        "permitted_models_evidence": {
            "allowlist": allowlist,
            "config_path_sha256": permitted.get("config_path_sha256"),
        },
        "escalation": None,
        "quota_fallback": ("separate decision; recorded independently via "
                           "record_quota_fallback, never merged into routing"),
        "estimated_context_tokens": estimated_context_tokens,
        "result": None,
        "telemetry": {"input_tokens": None, "output_tokens": None,
                      "cost": None,
                      "note": "null means not reported; never fabricated as zero"},
    }


def escalate_after_failure(decision: dict[str, Any], reason: str,
                           permitted: dict[str, Any]) -> dict[str, Any]:
    """Failed LOW/MEDIUM work may escalate ONE level, reason recorded.
    HIGH/CRITICAL never move (and can never be downgraded anywhere: no API
    exists to select below the deterministic choice)."""
    band = decision["complexity_band"]
    if band not in (LOW, MEDIUM):
        raise RoutingError(f"band {band} is never re-routed on failure; "
                           f"HIGH/CRITICAL work is not silently downgraded or "
                           f"shuffled to save tokens")
    if not reason.strip():
        raise RoutingError("an escalation without a recorded reason is refused")
    new_band = BANDS[BANDS.index(band) + 1]
    ordered = _ordered(list(permitted[decision["provider"]]))
    new = dict(decision)
    new["complexity_band"] = new_band
    new["chosen_model"] = (ordered[-1] if new_band in (HIGH, CRITICAL)
                           else ordered[0])
    new["escalation"] = {"from_band": band, "reason": reason,
                         "previous_model": decision["chosen_model"]}
    new["result"] = None
    return new


def record_quota_fallback(task_id: str, provider: str, from_model: str,
                          to_model: str, reason: str,
                          permitted: dict[str, Any]) -> dict[str, Any]:
    """Quota fallback is a SEPARATE recorded decision class (D-017-R120)."""
    if to_model not in permitted.get(provider, ()):
        raise RoutingError(f"quota fallback to unpermitted model {to_model!r} refused")
    if not reason.strip():
        raise RoutingError("an unrecorded fallback is refused: reason required")
    return {
        "schema": SCHEMA_VERSION,
        "kind": "quota_fallback",
        "task_id": task_id,
        "provider": provider,
        "from_model": from_model,
        "to_model": to_model,
        "reason": reason,
        "permitted_models_evidence": {
            "allowlist": list(permitted.get(provider, ())),
            "config_path_sha256": permitted.get("config_path_sha256"),
        },
    }


def decisions_path(checkout: str | os.PathLike[str]) -> pathlib.Path:
    """Append-only decision log in the accepted per-checkout runtime dir
    (OUTSIDE the repository; supervisor durable-state convention)."""
    from tools.agent_supervisor.durable_state import runtime_dir_for
    return pathlib.Path(runtime_dir_for(pathlib.Path(checkout))) / "model_routing.jsonl"


def append_decision(record: dict[str, Any],
                    path: str | os.PathLike[str]) -> None:
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def finalize(decision: dict[str, Any], *, result: str,
             telemetry: dict[str, Any] | None = None) -> dict[str, Any]:
    done = dict(decision)
    done["result"] = result
    if telemetry:
        merged = dict(done["telemetry"])
        for key, value in telemetry.items():
            if value is not None:
                merged[key] = value
        done["telemetry"] = merged
    return done
