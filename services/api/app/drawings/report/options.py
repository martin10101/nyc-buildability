"""The eleven development options (ruling X8), held in ONE place.

The owner-approved order and the mapping from each option to the document block
that holds its result. The option-comparison page reads its rows from here; no
other module names the option list. Figures come from the document (X7); the two
shared-limitation sentences are authored presentation and carry no figure.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import labels, readers

__all__ = [
    "ELEVEN_OPTIONS",
    "SHARED_LIMITATION_1",
    "SHARED_LIMITATION_2",
    "option_rows",
]

#: The eleven options in the owner-approved order (D-090 rows R539, R551;
#: FEASIBILITY_REPORT_SECTION_MAP section 4, row 1).
ELEVEN_OPTIONS = (
    (1, "Standard residences"),
    (2, "Qualifying affordable housing"),
    (3, "Qualifying senior housing"),
    (4, "More, smaller apartments"),
    (5, "Ground-floor shops with residences above"),
    (6, "Residences with a community facility"),
    (7, "A community facility alone"),
    (8, "A split lot with two buildings"),
    (9, "Shared housing"),
    (10, "Shared housing with the parking waiver"),
    (11, "All programs combined"),
)

#: Shared limitation 1: the lot-area basis. Stated once above the table and
#: referred to by number; the lot-area figures live on the Site and context page.
SHARED_LIMITATION_1 = (
    "These figures hold only if the recorded lot area is confirmed; the recorded lot "
    "area and the tax-map outline area disagree (see Site and context)."
)

#: Shared limitation 2: the program does not yet produce this option.
SHARED_LIMITATION_2 = "The program does not produce a result for this option on this lot yet."

_NOT_PRODUCED = "Not produced yet"


def _qualifying(fa_present: list[dict]) -> tuple[str | None, str | None, str | None]:
    """The qualifying-housing allowance figure, FAR and label from the shown
    floor-area values (keys that mention ``qualifying``)."""
    area = far = label = None
    for row in fa_present:
        key = str(row.get("key") or "")
        if "qualifying" not in key:
            continue
        if row.get("unit") == "square_feet":
            area, label = row.get("display"), row.get("status_label")
        elif row.get("unit") == "ratio":
            far = row.get("display")
    return area, far, label


def _addon_available(results: Mapping, addon_id: str) -> bool:
    for addon in results.get("addon_gains", []) or []:
        if isinstance(addon, Mapping) and addon.get("addon_id") == addon_id:
            gain = addon.get("gain")
            return isinstance(gain, Mapping) and gain.get("status") == "available"
    return False


def _standard_row(worked: list[dict]) -> dict:
    if not worked:
        return _unavailable_row()
    parts = []
    for building in worked:
        area = building.get("scheduled_display")
        name = building.get("building")
        if area and name:
            parts.append(f"Building {name}: scheduled {area} sq ft")
        elif area:
            parts.append(f"Scheduled {area} sq ft")
    return {
        "result": "; ".join(parts) if parts else _NOT_PRODUCED,
        "status_label": worked[0].get("status_label", labels.CONDITIONAL),
        "limitation": 1,
    }


def _qualifying_row(fa_present: list[dict]) -> dict:
    area, far, label = _qualifying(fa_present)
    if area is None:
        return _unavailable_row()
    result = f"Floor-area allowance {area} sq ft" + (f" (FAR {far})" if far else "")
    return {"result": result, "status_label": label or labels.CONDITIONAL, "limitation": 1}


def _unavailable_row() -> dict:
    return {"result": _NOT_PRODUCED, "status_label": labels.PENDING_VERIFICATION, "limitation": 2}


def option_rows(results: Mapping) -> list[dict]:
    """One row per option, in order: ordinal, name, result, label, limitation
    number."""
    worked = readers.worked_buildings(results)
    fa_present = readers.present_values(readers.answer_block(results, "floor_area_allowance"))
    rows: list[dict] = []
    for ordinal, name in ELEVEN_OPTIONS:
        if ordinal == 1:
            body = _standard_row(worked)
        elif ordinal in (2, 3):
            body = _qualifying_row(fa_present)
        else:
            body = _unavailable_row()
        rows.append({"ordinal": ordinal, "name": name, **body})
    return rows
