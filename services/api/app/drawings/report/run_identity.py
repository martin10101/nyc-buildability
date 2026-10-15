"""The report's run identity: a document fingerprint, the deployed code commit and
the result revision (M5-T169; D-094 R028/R038/R058).

Why it exists: the appendix must let a reader tell what produced a report and prove
that every figure and diagram on the page came from ONE result revision of ONE
document (R038/R058). The fingerprint is a short hash OVER THE DOCUMENT'S VALUES: it
is stable for the same document (so re-running without a change reproduces it) and
changes when any value changes, but it excludes ``results_id`` and ``computed_at``
(the run timestamp and id, which differ between otherwise-identical runs).

The deployed commit is read from the SAME environment variables the build-info route
reads, with the same fail-safe rule ("unknown" unless a hex git id is set). It is read
here (a tiny self-contained helper) rather than by importing the API router module
``app.api.v1.build_info`` into the report layer, so the report does not depend on a
route; the live route may still pass an explicit ``commit`` through
:func:`app.drawings.report.build_report_html` (report_read.py)."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping

__all__ = [
    "COMMIT_ENV_VARS",
    "UNKNOWN_COMMIT",
    "deployed_commit",
    "document_fingerprint",
    "run_identity",
]

UNKNOWN_COMMIT = "unknown"

#: The env vars that may carry the deployed commit, in priority order. The same names
#: and order the build-info route uses; kept in step by a test. (RENDER_GIT_COMMIT is
#: Render's variable; GIT_COMMIT_SHA a generic fallback a deploy may set.)
COMMIT_ENV_VARS: tuple[str, ...] = ("RENDER_GIT_COMMIT", "GIT_COMMIT_SHA")

# A git object id: SHA-1 (40) or SHA-256 (64) hex, or an abbreviation of at least 7.
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{7,64}")

# Top-level fields excluded from the fingerprint: the run id and the run timestamp.
# Two runs of the SAME document differ only in these, so the fingerprint is stable
# across them and changes with any other value (S7/R038).
_FINGERPRINT_EXCLUDE = ("results_id", "computed_at")


def deployed_commit(env: Mapping[str, str] | None = None) -> str:
    """The deployed commit from ``env`` (default ``os.environ``): the first
    ``COMMIT_ENV_VARS`` value that is a hex git id, else ``"unknown"``."""
    source = os.environ if env is None else env
    for name in COMMIT_ENV_VARS:
        value = (source.get(name) or "").strip().lower()
        if _COMMIT_PATTERN.fullmatch(value):
            return value
    return UNKNOWN_COMMIT


def document_fingerprint(results: Mapping, *, length: int = 12) -> str:
    """A short, stable sha256 fingerprint of the document's VALUES, excluding
    ``results_id`` and ``computed_at``. Stable for the same document; changes when any
    other value changes (S7). ``length`` is how many leading hex characters to show."""
    payload = {k: v for k, v in results.items() if k not in _FINGERPRINT_EXCLUDE} \
        if isinstance(results, Mapping) else {}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), default=str)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return digest[:max(1, length)]


def run_identity(results: Mapping, *, env: Mapping[str, str] | None = None,
                 commit: str | None = None) -> dict:
    """The run identity for the appendix: the document fingerprint, the deployed code
    commit (the explicit ``commit`` when the route passes one, else read from ``env``),
    the result revision and the computed date. The revision and computed date come from
    the document; the fingerprint proves the figures and diagrams share one document."""
    results = results if isinstance(results, Mapping) else {}
    resolved_commit = commit if (isinstance(commit, str) and commit) else deployed_commit(env)
    return {
        "fingerprint": document_fingerprint(results),
        "commit": resolved_commit,
        "revision": results.get("revision"),
        "computed_at": results.get("computed_at"),
    }
