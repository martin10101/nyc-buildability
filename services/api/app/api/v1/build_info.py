"""GET /api/v1/build-info - read-only runtime configuration record (queue C-02, plan M1-02).

Returns exactly three keys and nothing else:

- ``commit``: the deployed git commit SHA, or ``"unknown"``.
- ``version``: the API version, the same value ``GET /api/v1/health`` reports.
- ``flags``: a FIXED allowlist of boolean feature flags, each ``true`` or ``false``.

Why it is served without a flag or authentication, like ``/health``: it is the record the
owner reads after a deploy (M1-02 "Deployed SHAs and flags recorded"), and it cannot leak:

- Only the env vars named in :data:`COMMIT_ENV_VARS` and :data:`FLAG_ENV_VARS` are read.
  No other variable is ever looked at, so a secret cannot appear in the response.
- A flag is reported as a boolean, never its raw value, parsed with the same fail-safe rule
  as ``app.config``: an explicit true token is ``true``; absent / empty / unknown is ``false``.
- The commit value is echoed only when it is a hex git object id (7-64 chars); anything
  else reads ``"unknown"``.
- No database, network or file access; nothing is written.

Commit source, first valid value wins:

- ``RENDER_GIT_COMMIT``: Render's built-in variable for the deployed commit. TO CONFIRM: the
  name is not yet verified against a Render doc cited in this repo. The first request after
  the next deploy confirms it (a hex SHA instead of ``"unknown"``).
- ``GIT_COMMIT_SHA``: generic fallback an operator or the deploy workflow can set.

Web-side flags (``apps/web``) are read by the web service, not by this API, so they are not
reported here.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping

from fastapi import APIRouter, Request

__all__ = [
    "COMMIT_ENV_VARS",
    "FLAG_ENV_VARS",
    "UNKNOWN_COMMIT",
    "build_info_payload",
    "router",
]

router = APIRouter(prefix="/api/v1", tags=["build_info"])

UNKNOWN_COMMIT = "unknown"

#: Env vars that may carry the deployed commit, in priority order (see module docstring).
COMMIT_ENV_VARS: tuple[str, ...] = ("RENDER_GIT_COMMIT", "GIT_COMMIT_SHA")

#: The ONLY flags reported, in response order. Each name is owned by the module noted beside
#: it; tests pin every name to its owner's constant and reader so the two cannot drift.
FLAG_ENV_VARS: tuple[str, ...] = (
    "INTERNAL_RULE_EVAL_ENABLED",  # app.config
    "INTERNAL_SCENARIO_ENABLED",  # app.config
    "INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED",  # app.config (lane C W0)
    "INTERNAL_TRANSIT_PARKING_READ_ENABLED",  # app.config (lane C W0)
    "INTERNAL_PARITY_READ_ENABLED",  # app.config (lane C W0)
    "SITE_DEFINITION_WRITE_ENABLED",  # app.api.v1.site_definition (route registration)
    "DXF_IMPORT_ENABLED",  # app.api.v1.dxf_import_api (route unmounted)
    "LIVE_SPATIAL_PROVIDER_ENABLED",  # app.spatial.live_provider
    "LIVE_WIDE_STREET_PROVIDER_ENABLED",  # app.spatial.wide_street_live_provider
    "LANE_A_ENABLED",  # lane flags (M0-T164, docs/lanes/OWNERSHIP.yaml)
    "LANE_B_ENABLED",
    "LANE_C_ENABLED",
    "LANE_D_ENABLED",
    "LANE_E_ENABLED",
)

# Same closed token set as app.config: anything else - unset, "", "0", "off", a typo - is off.
_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})

# A git object id: SHA-1 (40) or SHA-256 (64) hex, or an abbreviation of at least 7 chars.
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{7,64}")


def _flag_on(raw: str | None) -> bool:
    return raw is not None and raw.strip().lower() in _TRUE_TOKENS


def _deployed_commit(env: Mapping[str, str]) -> str:
    for name in COMMIT_ENV_VARS:
        value = (env.get(name) or "").strip().lower()
        if _COMMIT_PATTERN.fullmatch(value):
            return value
    return UNKNOWN_COMMIT


def build_info_payload(version: str, env: Mapping[str, str] | None = None) -> dict[str, object]:
    """The build-info document for ``env`` (default ``os.environ``), read on every call."""
    source = os.environ if env is None else env
    return {
        "commit": _deployed_commit(source),
        "version": version,
        "flags": {name: _flag_on(source.get(name)) for name in FLAG_ENV_VARS},
    }


@router.get("/build-info")
def get_build_info(request: Request) -> dict[str, object]:
    """Deployed commit, API version and the allowlisted boolean flags. Read-only."""
    return build_info_payload(version=request.app.version)
