#!/usr/bin/env python3
"""The FIT check for the measurement-basis examples (M5-T133, D-090 R510, R511).

The owner's outside reviewer found a worked example whose arithmetic reconciled while
the building did not fit: per upper floor the apartment rooms already filled the whole
stated inside outline, and partitions, corridors, stairs, the elevator and chases were
then listed on top, so the components totalled far more than the stated outside outline.
The old test recomputed the areas and the reconciliation but never the FIT, so it passed.

This module proves the fit. For every example it checks, floor by floor, that:

* the floor has a stated outside outline (a non-empty list of rectangles with dimensions);
* the components that lie on that floor - the exterior wall ring among them - add up to
  EXACTLY the outline's area, by exact decimal arithmetic;
* the per-floor statement is consistent with the schedule (the sum of a component's
  per-floor footprints times the floor count equals its measured_area), so a changed
  dimension cannot hide; and
* the apartment ROOMS do not by themselves fill the inside outline (outline minus the
  exterior wall ring) while other interior components are also listed on that floor.

Pure stdlib. It imports only :mod:`measurement_basis_lib`; it never touches the rule or
scenario engine or any program output. Nothing here is a professional or legal
determination (ADR-007).
"""
from __future__ import annotations

import pathlib
import sys
from decimal import Decimal

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import measurement_basis_lib as lib  # noqa: E402


# --------------------------------------------------------------------------
# shape of the floor model
# --------------------------------------------------------------------------
def floor_structural_errors(example_id: str, example: dict) -> list[str]:
    """Problems that make the deeper checks unsafe (malformed floor keys/types/dimensions).
    A floor that is well-formed but simply has an EMPTY outline is NOT reported here - that
    is a soft 'no outline' problem (see :func:`missing_outline_errors`), so the per-floor fit
    can still run and report overflows on the floors that DO have an outline (G4 note F1)."""
    errs: list[str] = []
    floors = example.get("floors")
    if not isinstance(floors, list) or not floors:
        return [f"{example_id}: floors must be a non-empty list of floor types"]
    seen: set[str] = set()
    for floor in floors:
        if not isinstance(floor, dict) or set(floor) != lib.FLOOR_KEYS:
            errs.append(f"{example_id}: a floor's keys differ from the fixed set")
            continue
        fid = floor["floor_id"]
        if fid in seen:
            errs.append(f"{example_id}: duplicate floor id {fid!r}")
        seen.add(fid)
        if not str(floor["label"]).strip():
            errs.append(f"{example_id}/{fid}: a floor needs a label")
        if not isinstance(floor["count"], int) or floor["count"] < 1:
            errs.append(f"{example_id}/{fid}: a floor count must be a positive integer")
        parts = floor["outline_parts"]
        if not isinstance(parts, list):
            errs.append(f"{example_id}/{fid}: outline_parts must be a list")
            continue
        for part in parts:  # an empty list is a soft 'no outline', reported elsewhere
            if set(part) != lib.OUTLINE_PART_KEYS:
                errs.append(f"{example_id}/{fid}: an outline rectangle's keys differ from the set")
            elif lib._dec(part["width_ft"]) <= 0 or lib._dec(part["depth_ft"]) <= 0:
                errs.append(f"{example_id}/{fid}: an outline rectangle must have positive sides")
    return errs


def missing_outline_errors(example_id: str, example: dict) -> list[str]:
    """A well-formed floor that states no outside outline. Reported on its own so it does NOT
    stop the per-floor fit from running on the other floors (G4 note F1)."""
    errs: list[str] = []
    for floor in example.get("floors", []):
        if isinstance(floor, dict) and isinstance(floor.get("outline_parts"), list) \
                and not floor["outline_parts"]:
            errs.append(f"{example_id}/{floor['floor_id']}: the floor has no stated outside "
                        "outline")
    return errs


def floor_shape_errors(example_id: str, example: dict) -> list[str]:
    """All floor-shape problems (structural + missing-outline), kept for callers that want a
    single list; the fit entry points below treat the two kinds differently."""
    errs = floor_structural_errors(example_id, example)
    if not errs:
        errs += missing_outline_errors(example_id, example)
    return errs


def floor_area_reference_errors(example_id: str, example: dict) -> list[str]:
    errs: list[str] = []
    known = set(lib.floors_by_id(example))
    for comp in example["components"]:
        cid = comp.get("component_id", "?")
        floor_areas = comp.get("floor_areas")
        if not isinstance(floor_areas, list) or not floor_areas:
            errs.append(f"{example_id}/{cid}: floor_areas must be a non-empty list "
                        "(state on which floor(s) the component lies)")
            continue
        for entry in floor_areas:
            if set(entry) != lib.FLOOR_AREA_KEYS:
                errs.append(f"{example_id}/{cid}: a floor_areas entry's keys differ from the set")
                continue
            if entry["floor_id"] not in known:
                errs.append(f"{example_id}/{cid}: floor_areas names unknown floor "
                            f"{entry['floor_id']!r}")
            if lib._dec(entry["area"]) < 0:
                errs.append(f"{example_id}/{cid}: a floor_areas area may not be negative")
    return errs


# --------------------------------------------------------------------------
# the fit itself
# --------------------------------------------------------------------------
def consistency_errors(example_id: str, example: dict) -> list[str]:
    """Each component's per-floor footprints, summed over the floors, must equal its
    measured_area recomputed from the stated dimensions. A dimension changed by a foot
    breaks this."""
    errs: list[str] = []
    floors = lib.floors_by_id(example)
    for comp in example["components"]:
        cid = comp["component_id"]
        measured = lib.component_area(comp)
        per_floor = lib.component_floor_area_total(comp, floors)
        if per_floor != measured:
            errs.append(f"{example_id}/{cid}: the per-floor footprints sum to {per_floor} "
                        f"across the floors but the schedule measures {measured} "
                        "(the per-floor statement and the schedule disagree)")
    return errs


def floor_fit_errors(example_id: str, example: dict) -> list[str]:
    """For every floor: the components on it add up to the outline exactly, and the rooms
    do not fill the inside outline with other interior components on top."""
    errs: list[str] = []
    for floor in example["floors"]:
        fid = floor["floor_id"]
        if not floor["outline_parts"]:
            continue  # already reported by floor_shape_errors
        outline = lib.outline_area(floor)
        total = lib.floor_component_total(example, fid)
        if total != outline:
            errs.append(f"{example_id}/{fid}: the components on this floor add up to {total} "
                        f"sq ft but the stated outside outline is {outline} sq ft "
                        f"(difference {total - outline})")
        errs += rooms_fill_errors(example_id, example, floor, outline)
    return errs


def rooms_fill_errors(example_id: str, example: dict, floor: dict, outline: Decimal) -> list[str]:
    """Fail when the apartment rooms already fill the inside outline (outline minus the
    exterior wall ring) yet other interior components are also listed on the same floor -
    the exact defect the reviewer found in Example C."""
    fid = floor["floor_id"]
    ring = Decimal("0")
    rooms = Decimal("0")
    other_interior = Decimal("0")
    for comp in example["components"]:
        area = lib.component_floor_area(comp, fid)
        if area == 0:
            continue
        if comp["component_id"] == lib.EXTERIOR_WALL_ID:
            ring += area
        elif comp["component_id"] == lib.APARTMENT_INTERIOR_ID:
            rooms += area
        else:
            other_interior += area
    inside = outline - ring
    if rooms > 0 and other_interior > 0 and rooms >= inside:
        return [f"{example_id}/{fid}: the apartment rooms ({rooms} sq ft) already fill the "
                f"inside outline ({inside} sq ft = outline {outline} minus the exterior wall "
                f"ring {ring}) while {other_interior} sq ft of other interior components are "
                "listed on the same floor (the floor cannot hold them)"]
    return []


# --------------------------------------------------------------------------
# shared-floor-area attribution (ZR 23-20) - a required step, recomputed here
# --------------------------------------------------------------------------
def shared_floor_area_errors(example_id: str, example: dict) -> list[str]:
    errs: list[str] = []
    shared = example.get("shared_floor_area")
    if not isinstance(shared, dict) or set(shared) != lib.SHARED_FLOOR_AREA_KEYS:
        return [f"{example_id}: shared_floor_area keys differ from the fixed set"]
    if not isinstance(shared["present"], bool):
        return [f"{example_id}: shared_floor_area.present must be a boolean"]
    ids_marked_shared = [c["component_id"] for c in example["components"]
                         if c["portion"] == "shared"]
    if shared["present"]:
        if sorted(shared["shared_component_ids"]) != sorted(ids_marked_shared):
            errs.append(f"{example_id}: shared_component_ids must list exactly the components "
                        f"whose portion is 'shared' (got {shared['shared_component_ids']}, "
                        f"components marked shared {ids_marked_shared})")
        shared_sum = sum((lib.component_area(c) for c in example["components"]
                          if c["portion"] == "shared"), Decimal("0"))
        if shared_sum != lib._dec(shared["shared_total"]):
            errs.append(f"{example_id}: shared_total {shared['shared_total']} does not equal the "
                        f"measured shared components {shared_sum}")
        res_excl = lib.residential_zoning_floor_area(example)
        if lib._dec(shared["residential_exclusive_floor_area"]) != res_excl:
            errs.append(f"{example_id}: residential_exclusive_floor_area must equal the "
                        f"residential zoning floor area {res_excl}")
        total = (lib._dec(shared["residential_exclusive_floor_area"])
                 + lib._dec(shared["commercial_exclusive_floor_area"])
                 + lib._dec(shared["shared_total"]))
        if lib._dec(shared["total_floor_area_zoning_lot"]) != total:
            errs.append(f"{example_id}: total_floor_area_zoning_lot must equal residential + "
                        f"commercial exclusive + shared ({total})")
        base = lib._dec(shared["total_floor_area_zoning_lot"]) - lib._dec(shared["shared_total"])
        if lib._dec(shared["attribution_base"]) != base:
            errs.append(f"{example_id}: attribution_base must be the total floor area less the "
                        f"shared floor area ({base})")
        want_share = lib.residential_share(shared).quantize(Decimal("0.0001"))
        if Decimal(str(shared["residential_share_value"])) != want_share:
            errs.append(f"{example_id}: residential_share_value recomputes to {want_share}")
        want_res = lib.shared_attributed_to_residential(shared)
        if Decimal(str(shared["attributed_to_residential"])) != want_res:
            errs.append(f"{example_id}: attributed_to_residential recomputes to {want_res}")
        want_comm = (lib._dec(shared["shared_total"]) - want_res).quantize(Decimal("0.01"))
        if Decimal(str(shared["attributed_to_commercial"])) != want_comm:
            errs.append(f"{example_id}: attributed_to_commercial recomputes to {want_comm}")
        if not isinstance(shared["capture"], dict):
            errs.append(f"{example_id}: a shared attribution must cite a capture (ZR 23-20)")
        if "not captured yet" not in str(shared["conditional_note"]).lower():
            errs.append(f"{example_id}: the shared attribution must say the mixed-building "
                        "combination text is not captured yet (conditional)")
    else:
        if ids_marked_shared:
            errs.append(f"{example_id}: no component may be marked 'shared' when "
                        "shared_floor_area.present is false")
        if lib._dec(shared["shared_total"]) != 0 or shared["capture"] is not None:
            errs.append(f"{example_id}: a single-use example must carry no shared floor area")
    return errs


# --------------------------------------------------------------------------
# top-level
# --------------------------------------------------------------------------
def geometry_fit_errors(example_id: str, example: dict) -> list[str]:
    """The pure FIT: a stated outline on every floor, the components (the ring among them)
    adding up to it, consistency with the schedule, and no rooms-fill-the-floor overflow.

    This is the check the owner's reviewer required and the one the red proof runs on the
    examples 'as they are'. It does NOT include the ZR 23-20 shared-area attribution, which
    is a separate repair (C3). A floor missing its outline no longer stops the per-floor fit
    from running on the other floors, so an overflow elsewhere is reported in the same run
    (G4 note F1)."""
    hard = floor_structural_errors(example_id, example)
    hard += floor_area_reference_errors(example_id, example)
    if hard:
        return hard  # the deeper checks assume a well-formed floor model
    errs = missing_outline_errors(example_id, example)
    errs += consistency_errors(example_id, example)
    errs += floor_fit_errors(example_id, example)
    return errs


def fit_errors(example_id: str, example: dict) -> list[str]:
    """The full fit check: the geometry fit plus the shared-floor-area attribution."""
    hard = floor_structural_errors(example_id, example)
    hard += floor_area_reference_errors(example_id, example)
    if hard:
        return hard  # the deeper checks assume a well-formed floor model
    errs = missing_outline_errors(example_id, example)
    errs += consistency_errors(example_id, example)
    errs += floor_fit_errors(example_id, example)
    errs += shared_floor_area_errors(example_id, example)
    return errs


def fit_errors_all() -> list[str]:
    errs: list[str] = []
    for example_id in lib.EXAMPLE_IDS:
        errs += fit_errors(example_id, lib.load_example(example_id))
    return errs
