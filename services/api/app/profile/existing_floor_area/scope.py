"""Whether a DOB filing's zoning figure is shown to describe one building (B-05; M2-07).

A zoning lot can span several tax lots, and a DOB filing can carry the figure for the whole
zoning lot. The recorded benchmark shows it: DOB BIS job 421803891 (tax lot 4073340001) is
an alteration "TO REFLECT ONE (1) ZONING LOT AND (2) TAX LOTS (LOT #1 & #70). NO WORK TO
BE DONE", with existing 9,100 and proposed 39,772 zoning sq ft and no enlargement.

Two rules, both fail closed (they only ever withhold a figure):

- :func:`scope_problem` - a filing whose own text mentions a zoning lot, or that states no
  work, or an alteration that changes the zoning figure while stating no enlargement, is
  not shown to describe one building, so its figure is not used.
- :func:`zoning_lot_mentions` - every supplied row on the same tax block whose text
  mentions a zoning lot. When there is one, ``dob_filings`` sets the DOB figure aside (it
  may cover the whole zoning lot) and cites the rows, so the value stays unknown until the
  architect confirms it; a later zoning-lot step (B-07, B-09, B-11) gets the citations.

Zoning-lot scope is never established here: DOB job filings do not state which tax lots a
figure covers. Text is matched only to withhold or cite, never to derive a number.

Pure, deterministic code: no I/O.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from app.profile.existing_floor_area.dob_rows import area, identity, text
from app.profile.existing_floor_area.inputs import DobRecordSet

__all__ = ["ZONING_LOT_SCOPE", "scope_problem", "zoning_lot_mentions"]

ZONING_LOT_SCOPE = "not_established"
_ZONING_LOT = re.compile(r"\bZONING\s+LOTS?\b", re.IGNORECASE)
_NO_WORK = re.compile(r"\bNO\s+WORK\b", re.IGNORECASE)
_NEW_BUILDING = "NB"
_QUOTE_CHARS = 200


def _quote(description: str) -> str:
    return description if len(description) <= _QUOTE_CHARS else (
        description[:_QUOTE_CHARS] + "...")


def scope_problem(row: Mapping[str, Any]) -> str | None:
    """Why the row's zoning figure is not shown to describe one building, or None."""
    description = text(row.get("job_description")) or ""
    if _ZONING_LOT.search(description):
        return ("Its text mentions a zoning lot, so its figure may cover a zoning lot of "
                f"several tax lots rather than this building: '{_quote(description)}'")
    existing, _ = area(row, "existing_zoning_sqft")
    proposed, _ = area(row, "proposed_zoning_sqft")
    if proposed is None or proposed == existing:
        return None
    if _NO_WORK.search(description):
        return ("It states no work but changes the zoning figure from "
                f"{existing or 0:,} to {proposed:,} sq ft, so it may be a zoning-lot figure: "
                f"'{_quote(description)}'")
    enlargement, _ = area(row, "enlargement_sq_footage")
    job_type = text(row.get("job_type"))
    if job_type != _NEW_BUILDING and enlargement is None:
        return (f"The {job_type or 'alteration'} filing states no enlargement but changes the "
                f"zoning figure from {existing or 0:,} to {proposed:,} sq ft, so its figure "
                "is not shown to describe this building alone (it may be a zoning-lot figure).")
    return None


def zoning_lot_mentions(bbl: str, jobs: Sequence[DobRecordSet]) -> tuple[dict, ...]:
    """Rows on tax lot ``bbl``'s block whose text mentions a zoning lot, one per filing:
    ``{document_ref, tax_lots, text, query_ref, retrieved_at}``."""
    found: dict[str, dict] = {}
    for record_set in jobs:
        for row in record_set.rows:
            description = text(row.get("job_description"))
            if description is None or not _ZONING_LOT.search(description):
                continue
            readings = identity(row)
            if not any(reading[:6] == bbl[:6] for reading in readings):
                continue
            job, doc = text(row.get("job__")), text(row.get("doc__")) or "01"
            ref = f"DOB BIS job {job}, document {doc}" if job else "DOB BIS job (no number)"
            entry = found.setdefault(ref, {
                "document_ref": ref, "tax_lots": [], "text": description,
                "query_ref": record_set.query_ref, "retrieved_at": record_set.retrieved_at,
            })
            entry["tax_lots"] = sorted(set(entry["tax_lots"]) | readings)
    return tuple(found[ref] for ref in sorted(found))
