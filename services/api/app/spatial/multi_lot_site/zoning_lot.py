"""Zoning-lot status of a lot selection: always "Check needed" (B-07; plan §3 step 2, P-2).

The selection is the architect's statement of the site; results carry "Based on the lots
you selected — the app does not verify the zoning lot". No official source read here
verifies which tax lots form the zoning lot, so the status is "Check needed" with the
reason, whatever the records say. Records that mention a zoning lot (B-05's DOB filing
citations, or documents the caller supplies, such as recorded ACRIS documents) are listed as
a reminder only (plan P-2).

The reminder names every tax lot a record points to that the architect did not select, so
the shared zoning lot can be checked before any combined capacity is worked out (owner,
2026-10-01): the lots the record is filed on (its BBL fields), and the lots its text names
as "LOT #n" on the record's own block (``lots_named_in_text``). The text is read only for
those lot numbers, only to widen the reminder; never for areas, approval or the status.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from .inputs import SiteLot
from .results import (
    SELECTION_STATEMENT,
    ZONING_LOT_CHECK_NEEDED,
    ZONING_LOT_CHECK_NEEDED_LABEL,
    ZoningLotStatus,
)

__all__ = ["MENTION_KEYS", "UNVERIFIED_REASON", "lots_named_in_text", "zoning_lot_status"]

MENTION_KEYS = ("document_ref", "tax_lots", "text", "query_ref", "retrieved_at")
UNVERIFIED_REASON = (
    "The selected lots are your statement of the site. The app does not verify the zoning "
    "lot: no official source read here establishes which tax lots form it. Records that "
    "mention a zoning lot are a reminder only and do not verify it."
)


# "LOT #1", "TAX LOTS (LOT #1 &amp; #70)": a phrase that starts with LOT or LOTS followed by
# '#'-numbers of 1-4 digits joined by &, "&amp;" (as DOB serves it), a comma or AND. A job
# number ("APPLICATION #440608941") follows no LOT and has more than 4 digits: never read.
_LOT_PHRASE = re.compile(
    r"\bLOTS?\s*\(?\s*(?:LOT\s*)?#\s*\d{1,4}\b"
    r"(?:\s*(?:&amp;|&|,|AND)\s*(?:LOT\s*)?#\s*\d{1,4}\b)*", re.IGNORECASE)
_LOT_NUMBER = re.compile(r"#\s*(\d{1,4})\b")


def lots_named_in_text(text: object, tax_lots: Sequence[str]) -> list[str]:
    """BBLs of the "LOT #n" numbers in ``text``, on the block of the record's own tax lots;
    empty when the record's lots are on more than one block (the block is then unclear)."""
    blocks = {str(lot)[:6] for lot in tax_lots}
    if not isinstance(text, str) or len(blocks) != 1:
        return []
    (block,) = blocks
    numbers = {int(number) for phrase in _LOT_PHRASE.finditer(text)
               for number in _LOT_NUMBER.findall(phrase.group(0))}
    return sorted(f"{block}{number:04d}" for number in numbers if number > 0)


def _mention(record: Mapping[str, object]) -> dict[str, object]:
    missing = [key for key in MENTION_KEYS if key not in record]
    if missing or not isinstance(record.get("tax_lots"), list | tuple):
        raise ValueError(f"a zoning-lot record needs {list(MENTION_KEYS)}; missing {missing}")
    return {key: (sorted(record[key]) if key == "tax_lots" else record[key])
            for key in MENTION_KEYS}


def zoning_lot_status(
    lots: Sequence[SiteLot],
    *,
    recorded_documents: Sequence[Mapping[str, object]] = (),
) -> ZoningLotStatus:
    """The zoning-lot status for the selected ``lots``; never verified."""
    found: dict[str, dict[str, object]] = {}
    records = [m for lot in lots if lot.existing_floor_area
               for m in lot.existing_floor_area.zoning_lot_mentions]
    for record in (*records, *recorded_documents):
        mention = _mention(record)
        entry = found.setdefault(str(mention["document_ref"]), mention)
        entry["tax_lots"] = sorted(set(entry["tax_lots"]) | set(mention["tax_lots"]))
    for entry in found.values():
        entry["lots_named_in_text"] = lots_named_in_text(entry["text"], entry["tax_lots"])
    mentions = tuple(found[ref] for ref in sorted(found))
    selected = {lot.bbl for lot in lots}
    filed = {str(t) for m in mentions for t in m["tax_lots"]} - selected
    in_text = {t for m in mentions for t in m["lots_named_in_text"]} - selected - filed
    reason = UNVERIFIED_REASON
    if mentions:
        listed = "; ".join(f"{m['document_ref']} (tax lot {', '.join(m['tax_lots'])})"
                           for m in mentions)
        reason += f" Records that mention a zoning lot: {listed}."
    if filed:
        reason += (f" They are filed on tax lot {', '.join(sorted(filed))}, which you did not "
                   "select.")
    if in_text:
        reason += (f" Their text names tax lot {', '.join(sorted(in_text))} (as \"LOT #\" on "
                   "the record's own block), which you did not select.")
    return ZoningLotStatus(ZONING_LOT_CHECK_NEEDED, ZONING_LOT_CHECK_NEEDED_LABEL,
                           SELECTION_STATEMENT, reason, mentions,
                           tuple(sorted(filed | in_text)))
