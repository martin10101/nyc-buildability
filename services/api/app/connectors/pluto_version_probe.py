"""PLUTO published-version probe (queue item B-06 slice 2).

Issues the recorded F09 ``$select=version&$limit=1`` query against the PLUTO
SODA resource endpoint (dataset ``64uk-42ks``) and returns the release version
the city currently publishes, with provenance. It uses the SAME transport,
bounded retry and typed error taxonomy as
:func:`app.connectors.pluto_soda.fetch_by_bbl` by delegating to that module's
``_request_with_retry`` (timeouts, bounded body read, no redirect following,
typed errors, correlation id) - nothing about those behaviours is re-implemented
or re-tuned here.

Why a probe exists: the data-version check (:mod:`app.profile.data_versions`)
can only report "Out of date" when a published version NEWER than a pinned fact
is on record. Today the only "published" observations are the retrievals
themselves (:func:`app.profile.data_versions.published_from_pins`), so every
PLUTO fact reads "current" by construction. This probe records what the city
publishes independently of any one lot retrieval, so a lot pinned to an older
release can be shown out of date.

Deterministic connector code only: no AI, no legal interpretation, no invented
values (PRD sections 2, 9, 23.2). The returned version string is validated with
the connector's :data:`~app.connectors.pluto_soda.VERSION_RE`; a drifted shape
fails closed as :class:`~app.connectors.pluto_soda.SchemaDriftError` rather than
silently polluting the version comparison. This module performs NO legal or
zoning math and never wires itself into study assembly (that is Lane C's file;
see ``docs/lanes/requests/B-4.md``).

The exact request is the one the F09 fixture recorded
(``services/api/tests/fixtures/pluto/F09_version_select.json``); it is never
guessed here.
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.connectors.pluto_soda import (
    APP_TOKEN_ENV_VAR,
    BASE_URL,
    DATASET_ID,
    SOURCE_ID,
    VERSION_RE,
    SchemaDriftError,
    SourceUnavailableError,
    _build_headers,
    _request_with_retry,
    _rfc3339,
    _utc_now,
    urllib_transport,
)
from app.resilience.transport import Transport

__all__ = [
    "VERSION_PROBE_URL",
    "PlutoPublishedVersion",
    "fetch_published_version",
]

logger = logging.getLogger("app.connectors.pluto_version_probe")

# Exactly the request the F09 fixture recorded (F09_version_select.json
# request_url): the published-version probe projects only the ``version``
# column and asks for a single row. Built from the connector's BASE_URL so the
# host/path stay the single source of truth; the query string is verbatim F09
# (literal ``$``, as the live curl capture recorded and the endpoint served 200).
VERSION_PROBE_URL = f"{BASE_URL}?$select=version&$limit=1"


@dataclass(frozen=True)
class PlutoPublishedVersion:
    """A typed observation of the PLUTO release the city currently publishes.

    Immutable and provenance-complete: ``dataset_id`` and ``version`` are the
    fact; ``seen_at`` is the retrieval moment (RFC 3339, stamped AFTER the
    successful response like ``fetch_by_bbl``); ``query_ref`` is the exact
    request issued; ``source_id`` and ``correlation_id`` tie the observation
    back to the source registry and the request's structured logs.
    """

    dataset_id: str
    version: str
    seen_at: str
    query_ref: str
    source_id: str
    correlation_id: str


def fetch_published_version(
    *,
    transport: Transport = urllib_transport,
    timeout: float = 10.0,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], datetime] = _utc_now,
    correlation_id: str | None = None,
    app_token: str | None = None,
) -> PlutoPublishedVersion:
    """Probe the newest published PLUTO release version with full provenance.

    Issues the F09 ``$select=version&$limit=1`` query through the shared PLUTO
    transport/retry/error taxonomy (:func:`app.connectors.pluto_soda._request_with_retry`).

    Raises:
        RateLimitedError / SchemaDriftError / SourceTimeoutError /
        SourceUnavailableError: the same typed failures ``fetch_by_bbl`` raises.
        A non-array body, a row shape other than exactly one object, or a
        ``version`` that fails ``VERSION_RE`` is schema drift (never guessed).

    Returns:
        PlutoPublishedVersion carrying dataset id, the validated version, the
        retrieval time, the exact query, and provenance ids.
    """
    correlation_id = correlation_id or uuid.uuid4().hex
    if app_token is None:
        app_token = os.environ.get(APP_TOKEN_ENV_VAR) or None

    url = VERSION_PROBE_URL
    logger.info(
        "pluto_version_probe fetch_published_version url=%s correlation_id=%s "
        "token_configured=%s",
        url, correlation_id, bool(app_token),
    )

    response = _request_with_retry(
        url,
        transport=transport,
        headers=_build_headers(app_token),
        timeout=timeout,
        max_attempts=max_attempts,
        backoff_base=backoff_base,
        sleep=sleep,
        correlation_id=correlation_id,
    )
    # Stamp seen_at AFTER a successful response (mirrors fetch_by_bbl G3 D3).
    seen_at = _rfc3339(clock())

    try:
        rows = json.loads(response.body)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise SourceUnavailableError(
            "PLUTO version probe returned HTTP 200 with a body that is not valid JSON",
            correlation_id=correlation_id,
            detail={"url": url, "parse_error": type(exc).__name__},
        ) from exc

    if not isinstance(rows, list):
        raise SchemaDriftError(
            "PLUTO version probe body is not a JSON array",
            correlation_id=correlation_id,
            detail={"url": url, "body_type": type(rows).__name__},
        )
    if len(rows) != 1 or not isinstance(rows[0], dict):
        raise SchemaDriftError(
            "PLUTO version probe did not return exactly one row object",
            correlation_id=correlation_id,
            detail={"url": url, "row_count": len(rows)},
        )

    version_raw = rows[0].get("version")
    if not isinstance(version_raw, str) or not VERSION_RE.match(version_raw):
        raise SchemaDriftError(
            "PLUTO version probe returned a missing or malformed version string; "
            "a published version cannot be recorded without a valid release label",
            correlation_id=correlation_id,
            detail={"url": url, "version_raw": repr(version_raw)},
        )

    logger.info(
        "pluto_version_probe ok version=%s correlation_id=%s",
        version_raw, correlation_id,
    )
    return PlutoPublishedVersion(
        dataset_id=DATASET_ID,
        version=version_raw,
        seen_at=seen_at,
        query_ref=url,
        source_id=SOURCE_ID,
        correlation_id=correlation_id,
    )
