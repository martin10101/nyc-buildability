"""Hook-event catalog drift handling (D-024 Amendment 3 unit D, M0-T105;
R155 "probe and fixture" + R173 "unknown and version-drift handling").

`telemetry_hooks.KNOWN_HOOK_EVENTS` is the committed 2.1.220 catalog
(official-docs confidence). The installed runtime may add or remove events;
this module makes that drift a FACT the tests can bite on (mirroring the
M0-T104 native-adapter drift tooth):

* ``fixtures/hook_event_catalog_2_1_247.json`` freezes the catalog observed
  for the installed version, with its confidence and source recorded -- an
  event set is never guessed;
* `catalog_drift` computes the added/removed difference between any two
  catalogs; the committed fixture records the reconciled drift so a silent
  divergence between fixture and code fails a deterministic test;
* the live tooth (in the test pack) compares ``claude --version`` against the
  fixture's recorded version -- RED locally on an unrecorded upgrade, clean
  skip when the CLI is absent.

Unknown events at INGESTION time are already handled honestly by
`ingest_hook_event` (``known: false``, never dropped, never a crash); this
module handles the CATALOG-level question of what the installed version is
supposed to emit.

Supervisor-freeze qualifying evidence: D-024-R155 + D-024-R173.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
from typing import Any, Iterable

from .telemetry_hooks import KNOWN_HOOK_EVENTS

CATALOG_SCHEMA = "hook_event_catalog/v1"
# M0-T118 (D-024-R281 Amendment 13): re-pointed 2_1_248 -> 2_1_251 for the
# deliberate 2.1.251 admission (M0-T092 precedent). Unlike the identical
# 2.1.247->2.1.248 set, 2.1.251 is a REAL +2 event-set drift versus the
# 2.1.220/2.1.248 baseline (added PreModelSwitch + PostModelSwitch, 33 total);
# the fixture records the reconciled drift and the deterministic test bites on
# it. The 2_1_247/2_1_248 catalogs stay committed as append-only history.
CATALOG_FIXTURE_PATH = (pathlib.Path(__file__).resolve().parent / "fixtures"
                        / "hook_event_catalog_2_1_251.json")


class CatalogFixtureError(ValueError):
    """The committed catalog fixture is missing or malformed (fail visible)."""


@dataclasses.dataclass(frozen=True)
class CatalogDrift:
    """Set difference between an installed catalog and a baseline catalog."""

    added: tuple[str, ...]
    removed: tuple[str, ...]

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed)

    def describe(self) -> str:
        if not self.has_drift:
            return "no drift"
        parts = []
        if self.added:
            parts.append(f"added: {', '.join(self.added)}")
        if self.removed:
            parts.append(f"removed: {', '.join(self.removed)}")
        return "; ".join(parts)


def catalog_drift(installed: Iterable[str],
                  baseline: Iterable[str] = KNOWN_HOOK_EVENTS) -> CatalogDrift:
    """Events the installed catalog adds to / removes from the baseline."""
    installed_set = {name for name in installed if isinstance(name, str) and name}
    baseline_set = {name for name in baseline if isinstance(name, str) and name}
    return CatalogDrift(
        added=tuple(sorted(installed_set - baseline_set)),
        removed=tuple(sorted(baseline_set - installed_set)))


def load_catalog_fixture(path: str | os.PathLike[str] | None = None
                         ) -> dict[str, Any]:
    """The committed installed-version catalog record, schema-checked.

    Refuses (typed error, never a guess) a missing file, a wrong schema, or
    an empty/malformed event list -- a drift tooth chewing on a broken
    fixture would prove nothing.
    """
    fixture_path = pathlib.Path(path) if path is not None else CATALOG_FIXTURE_PATH
    try:
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CatalogFixtureError(
            f"cannot read catalog fixture {fixture_path.name}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CatalogFixtureError(
            f"catalog fixture {fixture_path.name} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != CATALOG_SCHEMA:
        raise CatalogFixtureError(
            f"catalog fixture must carry schema {CATALOG_SCHEMA!r}")
    events = data.get("events")
    if (not isinstance(events, list) or not events
            or not all(isinstance(name, str) and name for name in events)):
        raise CatalogFixtureError(
            "catalog fixture 'events' must be a non-empty list of event names")
    for field in ("claude_version", "confidence", "source"):
        if not isinstance(data.get(field), str) or not data[field]:
            raise CatalogFixtureError(
                f"catalog fixture missing required field {field!r}")
    return data
