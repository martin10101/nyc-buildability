"""The ACRIS zoning-lot scope row and its per-state plain-words statement (engine-side
isolation, task M5-T167 G-6; moved verbatim out of :mod:`three_way_document`).

Backlog DB-232. The row is appended to the emitted document's scope block in every citation
state except not_checked; :mod:`three_way_document` keeps importing
:data:`ZONING_LOT_SCOPE_KEY`, :data:`ZONING_LOT_SCOPE_VALUE`, :data:`_NOT_A_TITLE_SEARCH`,
:func:`_zoning_lot_scope_statement` and :func:`_apply_zoning_lot_scope_row` from here (a
compatibility facade), so the call site and the emitted document are byte-identical. The
transform (:func:`three_way_document.emit_three_way_document`) still calls
:func:`_apply_zoning_lot_scope_row` unchanged; nothing else moves (NB-01 revision 5)."""

from __future__ import annotations

from .result_way_inputs import (
    ZONING_LOT_NONE_FOUND,
    ZONING_LOT_NOT_READ,
    ZONING_LOT_OTHER_LOTS_NAMED,
    ZONING_LOT_SINGLE_LOT_ONLY,
    ZoningLotCitation,
)

__all__ = [
    "ZONING_LOT_SCOPE_KEY",
    "ZONING_LOT_SCOPE_VALUE",
    "_apply_zoning_lot_scope_row",
    "_zoning_lot_scope_statement",
]

# The ACRIS zoning-lot scope row (backlog DB-232). Built in this module (it already names the
# decision module's citation states and the scope value) rather than in three_way_scope_lines.py,
# which the import guard keeps free of the decision module. Emitted in every state except
# not_checked.
ZONING_LOT_SCOPE_KEY = "zoning_lot"
ZONING_LOT_SCOPE_VALUE = "Not confirmed"
_NOT_A_TITLE_SEARCH = "This is not a title search; the app does not verify the zoning lot."


def _zoning_lot_scope_statement(cit: ZoningLotCitation) -> str:
    """The state-specific plain-words scope statement. The value is always "Not confirmed"; the
    detail for the conditional states lives in the figure condition, so this stays a concise
    summary. Uses the bridge-rendered phrases, so no list is joined here."""
    recorded = f" (recorded {cit.zone_recorded_date})" if cit.zone_recorded_date else ""
    if cit.state == ZONING_LOT_OTHER_LOTS_NAMED:
        if cit.other_same_block_phrase:
            body = (
                "The city's register of recorded documents lists a zoning lot description filed "
                f"on this lot together with {cit.other_same_block_phrase} on the same "
                f"block{recorded}, so the zoning lot may include it; the documents were not read."
            )
        else:
            body = (
                "The city's register of recorded documents lists a zoning lot description filed on "
                f"only part of this lot{recorded}, so whether this whole tax lot is the zoning lot "
                "is not confirmed; the documents were not read."
            )
        return f"{body} {_NOT_A_TITLE_SEARCH}"
    if cit.state == ZONING_LOT_NOT_READ:
        return (
            "The city's register of recorded documents could not be read, so whether a recorded "
            f"zoning lot description names other lots is not known. {_NOT_A_TITLE_SEARCH}"
        )
    if cit.state == ZONING_LOT_NONE_FOUND:
        through = f", up to date through {cit.as_of_date}," if cit.as_of_date else ""
        return (
            f"The city's register of recorded documents{through} lists no zoning lot description "
            f"filed on this lot together with other lots. {_NOT_A_TITLE_SEARCH}"
        )
    if cit.state == ZONING_LOT_SINGLE_LOT_ONLY:
        single = (
            f" (recorded {cit.single_lot_recorded_date})" if cit.single_lot_recorded_date else ""
        )
        body = (
            "The city's register of recorded documents lists a zoning lot description filed on "
            f"this lot alone{single}; it was not read."
        )
        if cit.other_block_phrase:
            body += (
                f" It is also filed on {cit.other_block_phrase}, on another block; check what it "
                "covers."
            )
        return f"{body} {_NOT_A_TITLE_SEARCH}"
    return _NOT_A_TITLE_SEARCH  # pragma: no cover - not_checked emits no row (guarded by caller)


def _apply_zoning_lot_scope_row(doc: dict, zoning_lot: ZoningLotCitation | None) -> None:
    """Append the ACRIS zoning-lot scope row (backlog DB-232) to the scope block, in every state
    except not_checked. not_checked (no provider bound - the production default) appends nothing, so
    the emitted document is byte-identical to the pre-wiring slice. Nothing else in the scope block
    changes; the row is a schema-valid assumption (key zoning_lot, value 'Not confirmed', unit null,
    basis city_records, the state statement)."""
    if zoning_lot is None or not zoning_lot.shows_scope_row:
        return
    scope = doc.get("scope")
    if not isinstance(scope, dict):
        return
    assumptions = scope.get("assumptions")
    if not isinstance(assumptions, list):
        return
    assumptions.append({
        "key": ZONING_LOT_SCOPE_KEY,
        "value": ZONING_LOT_SCOPE_VALUE,
        "unit": None,
        "basis": "city_records",
        "statement": _zoning_lot_scope_statement(zoning_lot),
    })
