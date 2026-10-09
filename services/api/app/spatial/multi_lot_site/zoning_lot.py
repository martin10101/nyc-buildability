"""Zoning-lot status of a lot selection: always "Check needed" (B-07; plan §3 step 2, P-2).

The selection is the architect's statement of the site; results carry "Based on the lots
you selected — the app does not verify the zoning lot". No official source read here
verifies which tax lots form the zoning lot, so the status is "Check needed" with the
reason, whatever the records say. Records that mention a zoning lot (B-05's DOB filing
citations, or documents the caller supplies, such as recorded ACRIS documents) are listed as
a reminder only (plan P-2).

The reminder lists the tax lots a record is filed on (its BBL fields) that the architect did
not select. A record's text is kept as recorded and shown, but it is never read for lot
numbers: phrases such as "ZONING LOT #2", "PARKING LOT #3" or "LOT #5 OF BLOCK 7335" would
name the wrong tax lot. The reason instead tells the architect to check which tax lots the
text names, so the shared zoning lot is checked before any combined capacity is worked out
(owner, 2026-10-01). Nothing here sets areas, approval or the status from a record.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from .inputs import SiteLot
from .results import (
    SELECTION_STATEMENT,
    ZONING_LOT_CHECK_NEEDED,
    ZONING_LOT_CHECK_NEEDED_LABEL,
    ZoningLotStatus,
)

__all__ = ["MENTION_KEYS", "TEXT_NOT_READ", "UNVERIFIED_REASON", "zoning_lot_status"]

MENTION_KEYS = ("document_ref", "tax_lots", "text", "query_ref", "retrieved_at")
UNVERIFIED_REASON = (
    "The selected lots are your statement of the site. The app does not verify the zoning "
    "lot: no official source read here establishes which tax lots form it. Records that "
    "mention a zoning lot are a reminder only and do not verify it."
)
TEXT_NOT_READ = (
    "Their text is shown as recorded and is not read for lot numbers: check which tax lots "
    "it names. Check needed."
)


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
    mentions = tuple(found[ref] for ref in sorted(found))
    selected = {lot.bbl for lot in lots}
    filed = tuple(sorted({str(t) for m in mentions for t in m["tax_lots"]} - selected))
    reason = UNVERIFIED_REASON
    if mentions:
        listed = "; ".join(f"{m['document_ref']} (filed on tax lot {', '.join(m['tax_lots'])})"
                           for m in mentions)
        reason += f" Records that mention a zoning lot: {listed}."
    if filed:
        reason += f" They are filed on tax lot {', '.join(filed)}, which you did not select."
    if mentions:
        reason += " " + TEXT_NOT_READ
    return ZoningLotStatus(ZONING_LOT_CHECK_NEEDED, ZONING_LOT_CHECK_NEEDED_LABEL,
                           SELECTION_STATEMENT, reason, mentions, filed)
