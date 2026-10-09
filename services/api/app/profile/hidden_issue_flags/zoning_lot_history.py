"""The §8a zoning-lot-history hidden-issue group (queue item B-09, slice 2; plan L-11).

Plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` section 8a, "Zoning-lot history" row, and
plan P-2 ("Sold or merged development rights" - *Decided: a reminder only; no records
check*). Four items, each a flag or "Check needed" (never a guess, never an opportunity, and
never ``not_flagged``):

1. **Recorded zoning-lot descriptions or mergers.**
2. **Floor area already transferred** (the P-2 development-rights history).
3. **(D) and other restrictive declarations.**
4. **E-designations (environmental testing).**

This group is **flag only** (plan P-2): it never verifies a zoning lot and never clears one.
It only ever *reminds* the architect what recorded sources are on file to check, or says the
source is not connected. So it uses exactly two statuses - ``flag`` (a reminder that records
are on file) and ``check_needed`` (no connected source) - and never ``opportunity`` or
``not_flagged``: a cleared determination would require a records check this group does not do.

What it surfaces is only what the recorded sources already say, as a reminder:

- **B-05 DOB zoning-lot mentions** (``ExistingFloorAreaResult.zoning_lot_mentions``): DOB
  filings on the block whose text mentions a zoning lot or other tax lots. These back item 1.
- **Recorded zoning-lot documents** the caller supplies (``recorded_documents``): ACRIS index
  metadata already recorded by B-01/B-08 (and any other recorded instruments), in the same
  ``{document_ref, tax_lots, text, query_ref, retrieved_at}`` shape the multi-lot zoning-lot
  reminder uses (``app.spatial.multi_lot_site.zoning_lot``). These back items 1-3. The
  ``text`` is carried through verbatim in each reminder flag's ``evidence`` (so the reviewer
  can read it at the source) and is **never read here**: no ACRIS ``doc_type`` or other
  recorded code is interpreted, and no lot number is parsed from the text, so a reminder never
  decides that a document *is* a merger, a development-rights transfer or a declaration -
  that is for the reviewer to confirm at the source. The one-line detail lists only the
  document references (plan section 5a); the verbatim text lives in the evidence.

Item 4 (E-designations) has no Lane B source at all - E-designations come from the zoning
map's E-designation list / ZR Appendix C and CEQR records, none connected, and ACRIS
instruments never establish one - so it is always "Check needed" naming the missing source.

Nothing here concludes what the zoning lot is, claims a combined zoning lot is verified, or
computes anything (floor area, transfers, FAR). Pure, deterministic code: no I/O, no clock,
no legal logic.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from app.profile.existing_floor_area import ExistingFloorAreaResult
from app.profile.hidden_issue_flags.model import (
    STATUS_CHECK_NEEDED,
    STATUS_FLAG,
    FlagGroup,
    HiddenIssueFlag,
)

__all__ = ["GROUP_ID", "GROUP_TITLE", "RECORD_KEYS", "zoning_lot_history_group"]

GROUP_ID = "zoning_lot_history"
GROUP_TITLE = "Zoning-lot history"

_BBL = re.compile(r"^[1-5][0-9]{9}$")

# The recorded zoning-lot document shape, identical to the multi-lot zoning-lot reminder
# (app.spatial.multi_lot_site.zoning_lot.MENTION_KEYS) so one vocabulary describes a recorded
# zoning-lot document across the codebase. Kept local to keep this package's boundary clean.
RECORD_KEYS = ("document_ref", "tax_lots", "text", "query_ref", "retrieved_at")

# At most this many document references are spelled out in a one-line reminder (plan section
# 5a: one line, never a wall of warnings); the count is always stated in full.
_LIST_CAP = 6

# The constant caution shared by every reminder: this group never verifies the zoning lot and
# the recorded text is never read. Mirrors app.spatial.multi_lot_site.zoning_lot (B-07, P-2).
_NOT_VERIFIED = (
    "This does not verify the zoning lot: no source read here establishes it. The recorded "
    "text is carried verbatim in the evidence, not read for lot numbers or document meaning."
)


def _record(mapping: Mapping[str, object]) -> dict[str, object]:
    """Validate a supplied recorded zoning-lot document and normalize its tax-lot list."""
    if not isinstance(mapping, Mapping):
        raise ValueError(f"a recorded zoning-lot document must be a mapping, got {mapping!r}")
    missing = [key for key in RECORD_KEYS if key not in mapping]
    if missing:
        raise ValueError(f"a recorded zoning-lot document needs {list(RECORD_KEYS)}; "
                         f"missing {missing}")
    if not isinstance(mapping["tax_lots"], list | tuple):
        raise ValueError("a recorded zoning-lot document's tax_lots must be a list")
    return {key: (sorted(str(t) for t in mapping["tax_lots"]) if key == "tax_lots"
                  else mapping[key])
            for key in RECORD_KEYS}


def _dedupe(records: Sequence[Mapping[str, object]]) -> tuple[dict[str, object], ...]:
    """Validated records, one per ``document_ref``, tax-lot lists unioned, sorted by ref."""
    found: dict[str, dict[str, object]] = {}
    for record in records:
        normal = _record(record)
        ref = str(normal["document_ref"])
        entry = found.setdefault(ref, normal)
        entry["tax_lots"] = sorted(set(entry["tax_lots"]) | set(normal["tax_lots"]))
    return tuple(found[ref] for ref in sorted(found))


def _mentions(efa: ExistingFloorAreaResult | None) -> tuple[dict[str, object], ...]:
    if efa is None:
        return ()
    return _dedupe(efa.zoning_lot_mentions)


def _evidence(records: Sequence[Mapping[str, object]]) -> tuple[dict, ...]:
    # The recorded ``text`` is carried through verbatim (as B-07's zoning_lot.py returns the
    # full mentions): surfaced for the reviewer, never read, parsed or interpreted here.
    return tuple({
        "label": str(record["document_ref"]),
        "source": {"query_ref": record.get("query_ref"),
                   "retrieved_at": record.get("retrieved_at"),
                   "tax_lots": list(record["tax_lots"]),
                   "text": record.get("text")},
    } for record in records)


def _listed(records: Sequence[Mapping[str, object]]) -> str:
    shown = []
    for record in records[:_LIST_CAP]:
        lots = ", ".join(record["tax_lots"])
        suffix = f" (filed on tax lot {lots})" if lots else ""
        shown.append(f"{record['document_ref']}{suffix}")
    listing = "; ".join(shown)
    extra = len(records) - len(shown)
    if extra > 0:
        listing += f"; and {extra} more"
    return listing


def _reminder(
    item_id: str,
    title: str,
    typical: str,
    lead: str,
    records: Sequence[Mapping[str, object]],
    *,
    fact_refs: tuple[str, ...] = (),
) -> HiddenIssueFlag:
    """A reminder flag when records are on file, else "Check needed" naming the source."""
    full_id = f"{GROUP_ID}.{item_id}"
    if records:
        count = len(records)
        noun = "record" if count == 1 else "records"
        detail = (f"{lead} {count} recorded {noun} on file to check: {_listed(records)}. "
                  f"{_NOT_VERIFIED}")
        return HiddenIssueFlag(full_id, GROUP_ID, title, STATUS_FLAG, detail, typical,
                               _evidence(records), fact_refs)
    detail = (f"No source is connected to check this, so a reviewer must check it; it is "
              f"never guessed. Look in: {typical}.")
    return HiddenIssueFlag(full_id, GROUP_ID, title, STATUS_CHECK_NEEDED, detail, typical,
                           (), fact_refs)


def _recorded_descriptions_or_mergers(
    mentions: Sequence[Mapping[str, object]],
    acris: Sequence[Mapping[str, object]],
    fact_refs: tuple[str, ...],
) -> HiddenIssueFlag:
    records = _dedupe((*mentions, *acris))
    return _reminder(
        "recorded_descriptions_or_mergers",
        "Recorded zoning-lot descriptions or mergers",
        "ACRIS recorded documents (flag only, P-2); DOB filings that mention a zoning lot; "
        "ZR Appendix C",
        "A reminder: recorded documents may describe or merge a zoning lot for this lot -",
        records,
        fact_refs=fact_refs if mentions else (),
    )


def _floor_area_transferred(acris: Sequence[Mapping[str, object]]) -> HiddenIssueFlag:
    return _reminder(
        "floor_area_transferred",
        "Floor area already transferred",
        "ACRIS recorded documents (flag only, P-2: a reminder, never a records check)",
        "A reminder (P-2): development rights may have been sold or merged; this is never "
        "verified here -",
        acris,
    )


def _restrictive_declarations(acris: Sequence[Mapping[str, object]]) -> HiddenIssueFlag:
    return _reminder(
        "restrictive_declarations",
        "(D) and other restrictive declarations",
        "ACRIS recorded documents (flag only, P-2); ZR Appendix D",
        "A reminder: a (D) or other restrictive declaration may be recorded for this lot -",
        acris,
    )


def _e_designations() -> HiddenIssueFlag:
    return HiddenIssueFlag(
        f"{GROUP_ID}.e_designations", GROUP_ID,
        "E-designations (environmental testing)",
        STATUS_CHECK_NEEDED,
        "No source is connected to check this, so a reviewer must check it; it is never "
        "guessed. An E-designation comes from the zoning map's E-designation list (ZR "
        "Appendix C) and CEQR records, not from ACRIS, and none is connected.",
        "Zoning map E-designation list (ZR Appendix C); CEQR records",
    )


def zoning_lot_history_group(
    bbl: str,
    *,
    existing_floor_area: ExistingFloorAreaResult | None = None,
    recorded_documents: Sequence[Mapping[str, object]] = (),
) -> FlagGroup:
    """The §8a zoning-lot-history flag group for tax lot ``bbl`` (items in the module doc).

    The group is flag only (plan P-2): every item is a reminder (``flag``) when recorded
    sources are on file to check, or ``check_needed`` naming the missing source; nothing is
    verified, concluded or computed.

    Args:
        bbl: the tax lot (10-digit BBL).
        existing_floor_area: the B-05 result for the lot, read only for its
            ``zoning_lot_mentions`` (DOB filings mentioning a zoning lot / other tax lots);
            None when it was not resolved.
        recorded_documents: recorded zoning-lot documents (ACRIS index metadata recorded by
            B-01/B-08, and any other recorded instruments), each a mapping with the keys in
            :data:`RECORD_KEYS`. The ``text`` is shown verbatim and never interpreted.

    Raises:
        ValueError: ``bbl`` is not a 10-digit BBL, an input is of the wrong type, or a
            recorded document is missing a required key.
    """
    if not isinstance(bbl, str) or not _BBL.match(bbl):
        raise ValueError(f"bbl must be a 10-digit BBL, got {bbl!r}")
    if existing_floor_area is not None and not isinstance(
        existing_floor_area, ExistingFloorAreaResult
    ):
        raise ValueError("existing_floor_area must be an ExistingFloorAreaResult or None")

    mentions = _mentions(existing_floor_area)
    acris = _dedupe(recorded_documents)
    fact_id = (existing_floor_area.fact.get("fact_id")
               if existing_floor_area is not None else None)
    fact_refs = (fact_id,) if isinstance(fact_id, str) else ()

    flags = (
        _recorded_descriptions_or_mergers(mentions, acris, fact_refs),
        _floor_area_transferred(acris),
        _restrictive_declarations(acris),
        _e_designations(),
    )
    return FlagGroup(GROUP_ID, GROUP_TITLE, bbl, flags)
