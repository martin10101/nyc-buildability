"""Internal feature-flag configuration (task M4-T005 phase 2; M5-T003).

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
    "INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR",
    "INTERNAL_PARITY_READ_ENABLED_ENV_VAR",
    "INTERNAL_RULE_EVAL_ENABLED_ENV_VAR",
    "INTERNAL_SCENARIO_ENABLED_ENV_VAR",
    "INTERNAL_STUDY_READ_ENABLED_ENV_VAR",
    "INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR",
    "LANE_FLAG_ENV_VARS",
    "internal_hidden_issue_flags_read_enabled",
    "internal_parity_read_enabled",
    "internal_rule_eval_enabled",
    "internal_scenario_enabled",
    "internal_study_read_enabled",
    "internal_transit_parking_read_enabled",
    "lane_enabled",
]

# Env var gating the internal GET /properties/{bbl}/rule-evaluation endpoint.
# Declared here (name only; the value is environment-scoped and unset by default
# on every deployed service) so there is ONE source of truth for the flag name.
INTERNAL_RULE_EVAL_ENABLED_ENV_VAR = "INTERNAL_RULE_EVAL_ENABLED"

# Env var gating the internal GET /properties/{bbl}/scenario endpoint (task
# M5-T003). Same fail-safe posture and default-off semantics as the
# rule-evaluation flag; a distinct name so the two internal endpoints are
# enabled independently.
INTERNAL_SCENARIO_ENABLED_ENV_VAR = "INTERNAL_SCENARIO_ENABLED"

# Env var gating the internal GET /properties/{bbl}/study endpoint (lane C,
# request D-1 slice 1). This read-only route returns the lot-choice + site-facts
# setup half of a study (study.schema.json property/lots/lot_selection/site) for
# one BBL. A DISTINCT name so this surface is enabled independently of the
# rule-evaluation / scenario reads; same fail-safe posture as every flag here
# (absent/empty/unknown -> disabled). It gates REACHABILITY only: even when on,
# the lot choice is Lane B behaviour and is computed only when LANE_B_ENABLED is
# also on (see app.api.v1.study_inputs), so production (neither flag set) keeps
# the route a generic 404.
#
# ENABLEMENT CHECKLIST (before this route serves real traffic in production, all
# REQUIRED): enabling the study read, once LANE_B_ENABLED is also on, now fires an
# OUTBOUND PLUTO version-probe call during assembly (request B-4), on top of the
# PLUTO record fetch. So before production:
#   1. Authentication / authorization on the route (blocker B-001: the API ships
#      with no auth; this internal read must not be reachable unauthenticated).
#   2. The resilient PLUTO data path (properties.get_pluto_fetcher()), never an
#      unguarded direct connector call; the version probe is guarded by
#      app.api.v1.pluto_version_cache.CachedVersionProbe (single attempt, 5 s
#      timeout, 15-min success cache + 60 s negative cache/breaker, B-4 rework 1).
#   3. A concurrency bound for the study route (route-local rate limit already
#      present, plus job slots or a request deadline) so a burst cannot stack the
#      record fetch + version probe outbound calls.
# Until these exist, this flag stays OFF in production (security review).
INTERNAL_STUDY_READ_ENABLED_ENV_VAR = "INTERNAL_STUDY_READ_ENABLED"

# Env vars gating the three lane C packet-W0 §8a / check-C-8 / section-11b read
# surfaces: the hidden-issue flag layer, the transit/parking status, and the
# parity data (comparable sales + unused floor area). Each gates REACHABILITY
# only, with the same fail-safe posture as every flag here (absent/empty/unknown
# -> disabled), and a distinct name so each surface is enabled independently. The
# data they read is Lane B behaviour, computed only when LANE_B_ENABLED is also
# on, so production (neither flag set) keeps each route a generic 404.
#
# ENABLEMENT CHECKLIST (before any of these routes serves real traffic in
# production, all three are REQUIRED, none is built in packet W0):
#   1. Authentication / authorization on the route (blocker B-001: the API ships
#      with no auth; these internal reads must not be reachable unauthenticated
#      in production).
#   2. A route-local rate limit (the app.resilience.rate_limit SlidingWindowRateLimiter
#      export_api.py pattern) - parity makes live DOF SODA calls per request.
#   3. The resilient fetcher (properties.get_pluto_fetcher()) for the live data
#      path, never an unguarded direct connector call.
# Until all three exist, these flags stay OFF in production (security review NB2).
INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR = "INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED"
INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR = "INTERNAL_TRANSIT_PARKING_READ_ENABLED"
INTERNAL_PARITY_READ_ENABLED_ENV_VAR = "INTERNAL_PARITY_READ_ENABLED"

# One flag per parallel-build lane (task M0-T164, D-090; docs/lanes/PARALLEL_BUILD_PLAN.md §7).
# New lane behavior ships behind its lane's flag; production never sets these until the owner
# releases that lane's work, so absent means off like every flag here. Nothing reads them yet.
LANE_FLAG_ENV_VARS: Mapping[str, str] = {
    lane: f"LANE_{lane}_ENABLED" for lane in ("A", "B", "C", "D", "E")
}

# The closed set of tokens that mean "enabled". Anything not in this set - unset,
# empty, "0", "false", "off", or an unrecognized value - is DISABLED (fail safe).
_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})


def _flag_enabled(env_var: str, env: Mapping[str, str] | None) -> bool:
    """Whether ``env_var`` holds an explicit true token in ``env`` (defaults to
    ``os.environ``). Absent/empty/unknown -> False (fail safe). Read each call so
    a test can flip it with ``monkeypatch.setenv`` without rebuilding the app."""
    source = os.environ if env is None else env
    raw = source.get(env_var)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUE_TOKENS


def internal_rule_eval_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the internal rule-evaluation endpoint is enabled.

    Returns True ONLY for an explicit true token; absent/empty/unknown -> False.
    """
    return _flag_enabled(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, env)


def internal_scenario_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the internal scenario endpoint is enabled (task M5-T003).

    Returns True ONLY for an explicit true token; absent/empty/unknown -> False
    (fail safe), so the route is unreachable unless explicitly turned on.
    """
    return _flag_enabled(INTERNAL_SCENARIO_ENABLED_ENV_VAR, env)


def internal_study_read_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the internal study-read endpoint is enabled (lane C, request D-1).

    Returns True ONLY for an explicit true token; absent/empty/unknown -> False
    (fail safe), so the route is a generic 404 unless explicitly turned on.
    """
    return _flag_enabled(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, env)


def internal_hidden_issue_flags_read_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the internal hidden-issue-flags read endpoint is enabled (lane C, W0).

    Returns True ONLY for an explicit true token; absent/empty/unknown -> False
    (fail safe), so the route is a generic 404 unless explicitly turned on.
    """
    return _flag_enabled(INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED_ENV_VAR, env)


def internal_transit_parking_read_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the internal transit/parking read endpoint is enabled (lane C, W0).

    Returns True ONLY for an explicit true token; absent/empty/unknown -> False
    (fail safe), so the route is a generic 404 unless explicitly turned on.
    """
    return _flag_enabled(INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR, env)


def internal_parity_read_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the internal parity read endpoint is enabled (lane C, W0).

    Returns True ONLY for an explicit true token; absent/empty/unknown -> False
    (fail safe), so the route is a generic 404 unless explicitly turned on.
    """
    return _flag_enabled(INTERNAL_PARITY_READ_ENABLED_ENV_VAR, env)


def lane_enabled(lane: str, env: Mapping[str, str] | None = None) -> bool:
    """Whether parallel-build lane ``lane`` ("A".."E") has its flag explicitly on.

    Absent/empty/unknown -> False (fail safe). An unknown lane name raises ValueError so a
    typo can never read as "off" by accident.
    """
    try:
        env_var = LANE_FLAG_ENV_VARS[lane]
    except KeyError:
        raise ValueError(f"unknown lane {lane!r}; expected one of A, B, C, D, E") from None
    return _flag_enabled(env_var, env)
