"""Generate the recorded 215-16 Northern map_context fixture (maps step 4, D-090-R124).

NOT a test module (no ``test_`` prefix, not collected): a small generator that
builds the ONE map_context document the E-07 renderers consume from the recorded
215-16 Northern Blvd pack, replayed OFFLINE through the real connectors (no
network), and serializes it deterministically.

The committed fixture ``fixtures/recorded_215_16_northern.json`` is exactly
``serialize(build_document())``; the byte-drift test rebuilds and re-serializes
and asserts byte-for-byte equality.

The three typed connector results, the 150 ft window and the ``MapNotes`` are
built EXACTLY as the #415 builder tests do - the notes helper and the window are
imported from that module, never re-typed here, so the fixture carries the same
README-sourced attribution / accuracy / use-limitation text.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.contracts.map_context import build_map_context
from tests.contracts.test_map_context_builder import WINDOW_FT, _notes
from tests.spatial._northern_replay import (
    replay_footprints_lot_polygon,
    replay_lot_geometry,
    replay_nyzd_page,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "recorded_215_16_northern.json"


def build_document() -> dict:
    """The recorded Northern map_context document, built OFFLINE from the replay
    helpers through the real builder (no network)."""
    lot = replay_lot_geometry()
    nyzd = replay_nyzd_page()
    footprints = replay_footprints_lot_polygon()
    return build_map_context(
        lot, nyzd, footprints, window_ft=WINDOW_FT, notes=_notes(nyzd, footprints)
    )


def serialize(document: dict) -> str:
    """Canonical JSON for the fixture: stable (sorted) key order, 2-space indent,
    UTF-8 so the measurement em dash stays a character (as the other fixtures do),
    one trailing newline. The byte-drift test compares against exactly this."""
    return json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_fixture() -> None:
    FIXTURE.write_text(serialize(build_document()), encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover - regeneration entrypoint
    write_fixture()
