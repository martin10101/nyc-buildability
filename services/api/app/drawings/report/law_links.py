"""Law-link resolution for the report's evidence page (M5-T159; D-094 R027).

A cited Zoning Resolution section - as the report carries it, e.g. ``"ZR 23-52(b)"``
or ``"12-10"`` - resolves to the EXACT official section URL taken from the
repository's own law captures (``rules/snapshots.py`` ``request_url``), or to
``None`` when no capture exists. There is no reconstructed or guessed URL and the
site homepage is never a link.

A sub-paragraph such as ``23-52(b)`` links to its section page ``23-52``; the
visible section text (kept by ``page_evidence``) still shows the sub-paragraph. An
anchor is carried only when a capture records one.

Every candidate URL is validated with the SAME host/path rules the website's
source-links allowlist applies (``apps/web/src/lib/architect/source-links.ts``):
https only, host ``zoningresolution.planning.nyc.gov``, no query, no credentials,
no port, and an ``/article-<roman>/chapter-<n>[/<section>]`` path. An invalid URL
is dropped, so the section prints as plain text.

Module-level state is immutable: the section-to-URL index is built once through
the existing :class:`~app.rules.snapshots.SnapshotStore` loader and returned as a
read-only mapping.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from functools import lru_cache
from types import MappingProxyType
from urllib.parse import urlsplit

from app.rules import snapshots

from . import sources

__all__ = ["official_zoning_text_url", "section_url"]

# --- allowlist mirror of apps/web/src/lib/architect/source-links.ts -----------
_HOST = "zoningresolution.planning.nyc.gov"
_URL_PREFIX = f"https://{_HOST}/"
# Reject control characters, spaces and backslash anywhere in the raw string, as
# the website's regex /[\u0000- \u007f\\]/ does.
_FORBIDDEN_CHARS = re.compile(r"[\u0000- \u007f\\]")
# The only observed official article/chapter[/section] path form.
_PATH_RE = re.compile(r"^/article-[ivxlcdm]+/chapter-\d{1,2}(?:/\d{2}-\d{2,4})?$")
# The only anchor form the website accepts (the leading '#' is handled separately
# because urlsplit's fragment omits it).
_FRAGMENT_RE = re.compile(r"^\d{2}-\d{2,4}$")


def official_zoning_text_url(value: object) -> str | None:
    """Return ``value`` only if it passes the website source-links allowlist,
    rebuilt in its canonical host+path+anchor form; otherwise ``None``."""
    if (
        not isinstance(value, str)
        or not value.startswith(_URL_PREFIX)
        or len(value) > 500
        or _FORBIDDEN_CHARS.search(value)
    ):
        return None
    try:
        parts = urlsplit(value)
        if (
            parts.scheme != "https"
            or parts.hostname != _HOST
            or parts.username
            or parts.password
            or parts.port
            or parts.query
        ):
            return None
    except ValueError:
        # A malformed authority (e.g. an out-of-range port) is dropped, not raised.
        return None
    if not _PATH_RE.match(parts.path):
        return None
    fragment = parts.fragment
    if fragment and not _FRAGMENT_RE.match(fragment):
        return None
    anchor = f"#{fragment}" if fragment else ""
    return f"https://{_HOST}{parts.path}{anchor}"


def _last_path_segment(url: str) -> str:
    """The last path segment of a validated URL, ignoring any anchor."""
    path = url.split("#", 1)[0]
    return path.rstrip("/").rsplit("/", 1)[-1]


@lru_cache(maxsize=1)
def _section_index() -> Mapping[str, str]:
    """Build, once, an immutable ``section-page -> official URL`` mapping from the
    law captures. A snapshot is used only when its ``request_url`` passes the
    allowlist AND its last path segment equals the capture's own section page, so a
    chapter-only or wrong-host capture never becomes a section link. The first
    snapshot (by sorted id) that qualifies for a section page wins."""
    store = snapshots.SnapshotStore().load()
    index: dict[str, str] = {}
    for snapshot_id in store.ids():
        snapshot = store.get(snapshot_id)
        page = sources.zr_section_page_number(snapshot.section_number)
        if not page or page in index:
            continue
        url = official_zoning_text_url(snapshot.request_url)
        if url is None or _last_path_segment(url) != page:
            continue
        index[page] = url
    return MappingProxyType(dict(index))


def section_url(cited: object) -> str | None:
    """The exact official section URL for a cited section (sub-paragraph dropped
    for the lookup), or ``None`` when no capture records that section."""
    page = sources.zr_section_page_number(cited)
    if not page:
        return None
    return _section_index().get(page)
