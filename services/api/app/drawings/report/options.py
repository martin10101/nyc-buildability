"""The eleven development options (ruling X8; rework F7), held in ONE place.

The owner-approved order and, for each option, its floor-area allowance, its
scheduled building and its material limitation. An option's limitation is the
document block's own reason where the document gives one; identical reasons
collapse to one numbered shared limitation. A reason that carries developer
wording is replaced by a clean sentence (the report shows no developer
information - ruling X6). Options with no block share one sentence. Figures come
from the document (X7).
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from . import labels, readers

__all__ = ["ELEVEN_OPTIONS", "option_rows", "shared_limitations"]

#: The eleven options in the owner-approved order (D-090 rows R539, R551).
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

_ADDON_FOR_OPTION = {
    2: "qualifying_affordable_housing",
    3: "qualifying_senior_housing",
    5: "ground_floor_commercial",
    6: "community_facility_floor_area",
}

_LOT_AREA_LIMITATION = (
    "These figures hold only if the recorded lot area is confirmed; the recorded lot "
    "area and the tax-map outline area disagree (see Site and context)."
)
_NO_RULE = "The program does not have a reviewed rule for this option yet."
_NO_OPTION = "The program does not work out this option yet."
_NOT_PRODUCED = "Not produced yet"

# A reason that carries any of these is developer wording and is not shown (X6).
_DEV = re.compile(r"[a-z]+_[a-z]+|Lane [A-Z]|\btask\b|this slice|\bA-\d|\bR\d{3}\b")


def _clean(sentence: object) -> str | None:
    text = str(sentence or "").strip()
    if not text or _DEV.search(text):
        return None
    return text


def _addon_gain(results: Mapping, addon_id: str) -> Mapping | None:
    for addon in results.get("addon_gains", []) or []:
        if isinstance(addon, Mapping) and addon.get("addon_id") == addon_id:
            gain = addon.get("gain")
            return gain if isinstance(gain, Mapping) else {}
    return None


def _qualifying(fa_present: list[dict]) -> tuple[str | None, str | None]:
    area = far = None
    label = None
    for row in fa_present:
        if "qualifying" not in str(row.get("key") or ""):
            continue
        if row.get("unit") == "square_feet":
            area, label = row.get("display"), row.get("status_label")
        elif row.get("unit") == "ratio":
            far = row.get("display")
    text = None
    if area:
        text = f"{area} (FAR {far})" if far else area
    return text, label


def _standard(worked: list[dict]) -> tuple[str | None, str | None, str | None]:
    """Allowance text, scheduled text and label for option 1."""
    if not worked:
        return None, None, None
    building = worked[0]
    allowance = building.get("scheduled_display")
    scheduled = (
        labels.scheduled_floor_area_line(allowance) if allowance
        else "Scheduled building not available"
    )
    return building.get("scheduled_display"), scheduled, building.get("status_label")


def _limitation_sentence(results: Mapping, ordinal: int) -> str:
    if ordinal == 1:
        return _LOT_AREA_LIMITATION
    if ordinal in _ADDON_FOR_OPTION:
        gain = _addon_gain(results, _ADDON_FOR_OPTION[ordinal])
        if gain is not None and gain.get("status") != "available":
            return _clean(gain.get("reason")) or _NO_RULE
        return _NO_OPTION
    if ordinal == 11:
        combo = results.get("best_combination")
        if isinstance(combo, Mapping) and combo.get("status") != "available":
            return _clean(combo.get("reason")) or _NO_OPTION
        return _NO_OPTION
    return _NO_OPTION


def _rows_and_limits(results: Mapping) -> tuple[list[dict], list[dict]]:
    worked = readers.worked_buildings(results)
    fa_present = readers.present_values(readers.answer_block(results, "floor_area_allowance"))
    std_allow, std_sched, std_label = _standard(worked)
    qual_text, qual_label = _qualifying(fa_present)

    sentences: list[str] = []

    def number_for(sentence: str) -> int:
        if sentence not in sentences:
            sentences.append(sentence)
        return sentences.index(sentence) + 1

    rows: list[dict] = []
    for ordinal, name in ELEVEN_OPTIONS:
        if ordinal == 1 and std_allow:
            allowance = f"{std_allow} sq ft (FAR {_far(fa_present, 'max_residential_far')})"
            scheduled, label = std_sched, std_label
        elif ordinal in (2, 3) and qual_text:
            far = _far(fa_present, "max_residential_far_qualifying_affordable_or_senior")
            allowance = qual_text if "FAR" in qual_text else f"{qual_text} (FAR {far})"
            scheduled, label = "None scheduled", qual_label or labels.CONDITIONAL
        else:
            allowance, scheduled = _NOT_PRODUCED, "None scheduled"
            label = labels.PENDING_VERIFICATION
        limitation = number_for(_limitation_sentence(results, ordinal))
        rows.append({
            "ordinal": ordinal, "name": name, "allowance": allowance,
            "scheduled": scheduled, "status_label": label, "limitation": limitation,
        })
    limits = [{"number": i + 1, "sentence": s} for i, s in enumerate(sentences)]
    return rows, limits


def _far(fa_present: list[dict], key: str) -> str:
    for row in fa_present:
        if row.get("key") == key and row.get("display"):
            return row["display"]
    return ""


def option_rows(results: Mapping) -> list[dict]:
    """One row per option: ordinal, name, allowance, scheduled, label, limitation
    number."""
    return _rows_and_limits(results)[0]


def shared_limitations(results: Mapping) -> list[dict]:
    """The numbered shared-limitation sentences, each stated once."""
    return _rows_and_limits(results)[1]
