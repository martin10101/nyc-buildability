"""Coverage of the promised sections (F10/A8; moved to the decision summary in
rework D9).

One place that reads, from the document and the section map, which of the nine
contents (A to I) and the six further sections the owner kept in scope (plus
context maps) are in this report, partly in it, or not yet. The decision summary
shows this as a compact block grouped by state.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import readers

__all__ = [
    "IN_REPORT",
    "NOT_YET",
    "PARTLY",
    "coverage_entries",
    "coverage_groups",
]

IN_REPORT = "In this report"
PARTLY = "Partly in this report"
NOT_YET = "Not yet in the program"
NOT_YET_REPORT = "Not yet in this report"

NINE_CONTENTS = (
    ("A", "Property facts"),
    ("B", "Applicable zoning"),
    ("C", "Development options"),
    ("D", "Estimated floors"),
    ("E", "Simple building shapes"),
    ("F", "Legal unit limits"),
    ("G", "Realistic apartment-count estimates"),
    ("H", "Option comparisons"),
    ("I", "The downloadable report"),
)

# The six further sections the owner kept in scope, plus context maps. Read from
# the section map: none is built into the report yet. ``held`` marks the owner-held
# section.
FURTHER_SECTIONS = (
    ("Comparable sales nearby", NOT_YET, "", False),
    ("Block description", NOT_YET, "", False),
    ("Parking, loading and bicycle parking", NOT_YET, "", False),
    ("Aerial and street photographs", NOT_YET, "", False),
    ("Tax abatement eligibility", NOT_YET, "", False),
    ("Financial analysis inputs", NOT_YET, "", True),
    ("Context maps", NOT_YET_REPORT, "Map data is not yet fetched for the report.", False),
)


def coverage_entries(results: Mapping) -> list[dict]:
    """Every section with its state, a short note and whether it is owner-held."""
    worked = readers.worked_buildings(results)
    n_worked = len(worked)
    has_schedule = any(b.get("floor_schedule") for b in worked)
    has_capacity = any(b.get("capacity_estimate") for b in worked)
    c_state = ((PARTLY, f"{n_worked} of 11 options worked") if n_worked
               else (NOT_YET, "no option worked"))
    d_state = ((PARTLY, "the worked building only") if has_schedule
               else (NOT_YET, "no worked building"))
    e_state = (
        (PARTLY, "lot outline and floor stack; the envelope is not drawn")
        if readers.geometry_available(results) else (NOT_YET, "no lot outline")
    )
    states = {
        "A": (IN_REPORT, ""),
        "B": (IN_REPORT, ""),
        "C": c_state,
        "D": d_state,
        "E": e_state,
        "F": (NOT_YET, "the legal unit limit is withheld"),
        "G": (PARTLY, "the worked building only") if has_capacity else (NOT_YET, "no estimate"),
        "H": (IN_REPORT, ""),
        "I": (IN_REPORT, ""),
    }
    entries: list[dict] = []
    for letter, name in NINE_CONTENTS:
        state, note = states[letter]
        entries.append({"name": name, "state": state, "note": note, "held": False})
    for name, state, note, held in FURTHER_SECTIONS:
        entries.append({"name": name, "state": state, "note": note, "held": held})
    return entries


def coverage_groups(results: Mapping) -> list[tuple[str, list[str]]]:
    """The coverage grouped by state, as at most a few compact lines (D9):
    'In this report' as plain names; 'Partly' with each short note; 'Not yet'
    (any 'Not yet …' state) as names, the owner-held one marked 'held'."""
    in_report: list[str] = []
    partly: list[str] = []
    not_yet: list[str] = []
    for entry in coverage_entries(results):
        name, state, note = entry["name"], entry["state"], entry["note"]
        if state == IN_REPORT:
            in_report.append(name)
        elif state == PARTLY:
            partly.append(f"{name} ({note})" if note else name)
        else:
            label = f"{name} (held)" if entry["held"] else name
            not_yet.append(label)
    groups = []
    if in_report:
        groups.append(("In this report", in_report))
    if partly:
        groups.append(("Partly", partly))
    if not_yet:
        groups.append(("Not yet", not_yet))
    return groups
