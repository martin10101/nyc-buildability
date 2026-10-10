"""Plain-words captions for the site-context maps (M5-T156 rework 1; rulings Y7, X6).

One short "Sources: ..." line composed from the map document's OWN provenance -
each layer the drawing shows named with a readable title (:mod:`.sources`) and its
last-edited date once - followed by the drawing's own short notes (the rotation
and the "nothing is surveyed" honesty line). No dataset id, no "via NYC Open Data"
phrase, no terms-of-use text, and no doubled date ever appears.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from . import sources

__all__ = [
    "BLOCK_LAYERS",
    "NEIGHBOURHOOD_LAYERS",
    "SITE_LAYERS",
    "figure_caption",
    "source_lines",
    "source_sentence",
]

# The layers each drawing shows, in caption order (tax lots, buildings, streets).
_ORDER = ("tax_lots", "building_footprints", "streets")
SITE_LAYERS = ("tax_lots", "building_footprints", "streets")
BLOCK_LAYERS = ("tax_lots", "building_footprints", "streets")
NEIGHBOURHOOD_LAYERS = ("streets",)


def _readable_date(iso: object) -> str | None:
    """``"2026-09-09"`` -> ``"9 Sep 2026"`` (plain, no leading zero), or ``None``."""
    try:
        parsed = date.fromisoformat(str(iso)[:10])
    except (TypeError, ValueError):
        return None
    return f"{parsed.day} {parsed.strftime('%b')} {parsed.year}"


def _available_layer(map_context: object, key: str) -> Mapping | None:
    mc = map_context.get("map_context") if isinstance(map_context, Mapping) else None
    layer = mc.get(key) if isinstance(mc, Mapping) else None
    if isinstance(layer, Mapping) and layer.get("status") == "available":
        return layer
    return None


def source_lines(map_context: object, layers: tuple[str, ...]) -> list[str]:
    """One readable "<title> (edited <date>)" line per AVAILABLE layer the drawing
    shows (each date once; no dataset id or terms-of-use text)."""
    lines: list[str] = []
    for key in _ORDER:
        if key not in layers:
            continue
        layer = _available_layer(map_context, key)
        if layer is None:
            continue
        title = sources.map_source_title(key)
        provenance = layer.get("provenance")
        provenance = provenance if isinstance(provenance, Mapping) else {}
        edited = _readable_date(provenance.get("source_data_last_edited"))
        lines.append(f"{title} (edited {edited})" if edited else title)
    return lines


def source_sentence(map_context: object, layers: tuple[str, ...]) -> str | None:
    """The "Sources: ...; ...." sentence, or ``None`` when no layer is available."""
    lines = source_lines(map_context, layers)
    return "Sources: " + "; ".join(lines) + "." if lines else None


def _tail_notes(result: object) -> list[str]:
    """The drawing's own short notes (rotation, honesty), each a full sentence. The
    source-attribution and measurement-basis note labels are dropped - the
    "Sources:" sentence already names those in plain words."""
    out: list[str] = []
    for label in getattr(result, "labels", ()) or ():
        if getattr(label, "role", None) != "note":
            continue
        source = str(getattr(label, "source", ""))
        if source.endswith("/attribution") or source == "/map_context/measurement/label":
            continue
        text = str(getattr(label, "text", "")).strip()
        if text:
            out.append(text if text.endswith((".", ":")) else text + ".")
    return out


def figure_caption(result: object, map_context: object, layers: tuple[str, ...]) -> str | None:
    """The full caption for one site-context drawing: the "Sources:" sentence then
    the drawing's short notes."""
    parts: list[str] = []
    sentence = source_sentence(map_context, layers)
    if sentence:
        parts.append(sentence)
    parts.extend(_tail_notes(result))
    return " ".join(parts) or None
