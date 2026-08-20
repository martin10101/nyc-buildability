"""Internal feature-flag configuration (task M4-T005 phase 2).

Fail-safe environment flags for internal/dev-only endpoints. The single rule:
an ABSENT or UNKNOWN value resolves to DISABLED. A production deploy that never
sets the flag therefore keeps the gated endpoint unreachable (fail safe), and a
typo / stray value ("maybe", "0", "") is treated as disabled rather than
silently enabling an unauthenticated internal endpoint (CLAUDE.md permanent
principle 6/13; M1-T005 no-auth deployment status).

Only an EXPLICIT, unambiguous true token enables a flag; everything else is off.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

__all__ = [
    "INTERNAL_RULE_EVAL_ENABLED_ENV_VAR",
    "INTERNAL_SCENARIO_ENABLED_ENV_VAR",
    "internal_rule_eval_enabled",
    "internal_scenario_enabled",
]

# Env var gating the internal GET /properties/{bbl}/rule-evaluation endpoint.
# Declared here (name only; the value is environment-scoped and unset by default
# on every deployed service) so there is ONE source of truth for the flag name.
INTERNAL_RULE_EVAL_ENABLED_ENV_VAR = "INTERNAL_RULE_EVAL_ENABLED"

# Env var gating the internal GET /properties/{bbl}/scenario endpoint (task
# M5-T002). Same single-source-of-truth discipline and the SAME fail-safe
# semantics as the rule-evaluation flag: unset by default on every deployed
# service, so a production deploy that never sets it keeps the scenario endpoint
# unreachable.
INTERNAL_SCENARIO_ENABLED_ENV_VAR = "INTERNAL_SCENARIO_ENABLED"

# The closed set of tokens that mean "enabled". Anything not in this set - unset,
# empty, "0", "false", "off", or an unrecognized value - is DISABLED (fail safe).
_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})


def internal_rule_eval_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the internal rule-evaluation endpoint is enabled.

    Reads the flag from ``env`` (defaults to ``os.environ``) each call, so a
    test can flip it with ``monkeypatch.setenv`` without rebuilding the app.
    Returns True ONLY for an explicit true token; absent/empty/unknown -> False.
    """
    source = os.environ if env is None else env
    raw = source.get(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUE_TOKENS


def internal_scenario_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the internal scenario endpoint is enabled (task M5-T002).

    Byte-for-byte the same fail-safe semantics as
    :func:`internal_rule_eval_enabled`: reads the flag from ``env`` (defaults to
    ``os.environ``) each call, returns True ONLY for an explicit true token, and
    treats absent / empty / unknown as False (fail safe).
    """
    source = os.environ if env is None else env
    raw = source.get(INTERNAL_SCENARIO_ENABLED_ENV_VAR)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUE_TOKENS
