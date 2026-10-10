"""HTML assembly (ruling X2: the Python standard library's escaping; no template
engine; no new package).

Small builders that escape every piece of text with :func:`html.escape` and join
them into a string. ``raw`` is for already-safe markup only (a validated SVG from
the drawing kit, or a fragment this module itself built). Everything a caller
passes as text goes through escaping, including attribute values.
"""

from __future__ import annotations

import html as _stdlib_html
from collections.abc import Iterable, Mapping

__all__ = [
    "attrs",
    "el",
    "escape",
    "escape_attr",
    "raw",
    "table",
]


class _Raw(str):
    """A string that is already safe HTML; builders emit it verbatim."""


def raw(markup: str) -> _Raw:
    return _Raw(markup)


def escape(text: object) -> str:
    """Escape a text value for element content (``&``, ``<``, ``>``)."""
    return _stdlib_html.escape("" if text is None else str(text), quote=False)


def escape_attr(text: object) -> str:
    """Escape a text value for an attribute (also escapes quotes)."""
    return _stdlib_html.escape("" if text is None else str(text), quote=True)


def attrs(mapping: Mapping[str, object]) -> str:
    parts = []
    for name, value in mapping.items():
        if value is None or value is False:
            continue
        if value is True:
            parts.append(escape_attr(name))
        else:
            parts.append(f'{escape_attr(name)}="{escape_attr(value)}"')
    return (" " + " ".join(parts)) if parts else ""


def _render_child(child: object) -> str:
    if isinstance(child, _Raw):
        return str(child)
    return escape(child)


def el(tag: str, *children: object, **attributes: object) -> _Raw:
    """One element. Text children are escaped; ``raw(...)`` children are kept
    verbatim. Attribute keys ending ``_`` drop the underscore (so ``class_`` ->
    ``class``)."""
    clean = {key.rstrip("_"): value for key, value in attributes.items()}
    body = "".join(_render_child(child) for child in children)
    return _Raw(f"<{tag}{attrs(clean)}>{body}</{tag}>")


# A table with this many body rows or fewer is never split across a page break
# (it moves whole, with its heading): it is marked ``no-split`` for the print CSS.
SHORT_TABLE_MAX_ROWS = 8


def table(
    headers: Iterable[object],
    rows: Iterable[Iterable[object]],
    *,
    class_: str | None = None,
    caption: object | None = None,
) -> _Raw:
    """A table with a repeating header group (``thead``) and body rows. Header and
    body cells are escaped unless passed as ``raw(...)``. A SHORT table (at most
    ``SHORT_TABLE_MAX_ROWS`` body rows, e.g. the status-label key) is marked
    ``no-split`` so the print CSS never breaks it across a page."""
    head = el("tr", *[el("th", header) for header in headers])
    body = [el("tr", *[el("td", cell) for cell in row]) for row in rows]
    names = [class_] if class_ else []
    if len(body) <= SHORT_TABLE_MAX_ROWS:
        names.append("no-split")
    children: list[object] = []
    if caption is not None:
        children.append(el("caption", caption))
    children.append(el("thead", head))
    children.append(el("tbody", *body))
    return el("table", *children, class_=" ".join(names) or None)
