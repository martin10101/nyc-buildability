"""Small recurring presentation fragments shared by the page modules.

These compose :mod:`.html` builders into the pieces every page reuses - a page
section, a label chip, an answer block, a short limitation line, a figure or its
one-line fallback - so each page module stays about its own content.
"""

from __future__ import annotations

from .drawings_embed import Embedded
from .html import el, raw

__all__ = [
    "answer_block",
    "figure",
    "label_chip",
    "page_section",
    "short_line",
]


def label_chip(label: object) -> raw:
    return el("span", label, class_="label-chip")


def page_section(page_id: str, title: str, question: str, *children: object) -> str:
    head = [
        el("h2", title),
        el("p", question, class_="reader-question"),
    ]
    return str(el("section", *head, *children, class_="report-page", id=page_id))


def answer_block(
    title: str, value_text: str | None, label: object, exception: object = None
) -> raw:
    value = value_text if value_text is not None else "Not available"
    parts = [
        el("h3", title),
        el("p", raw(f'<span class="answer-value">{value}</span>'), label_chip(label)),
    ]
    if exception:
        parts.append(el("p", exception, class_="limitation"))
    return el("div", *parts, class_="answer")


def short_line(text: object) -> raw:
    return el("p", text, class_="short-line")


def figure(embedded: Embedded, fallback_caption: str) -> raw:
    if embedded.is_drawing:
        caption = embedded.caption or fallback_caption
        return el(
            "figure",
            raw(embedded.svg or ""),
            el("figcaption", caption),
        )
    return short_line(embedded.short_line or fallback_caption)
