"""Street-data checks before any frontage is claimed (queue item B-03).

Frontage can only be ruled out where the street data is known to be complete. These checks
turn every gap into a plain reason ("blocker"); any blocker leaves lot type unknown and
every frontage length uncertain.
"""

from __future__ import annotations

from dataclasses import dataclass

from shapely.geometry import LineString

from .adjacency import mapped_width_ft
from .inputs import StreetCenterline, StreetData
from .outline import PreparedOutline, crs_is_measurement_grade, finite_point
from .parameters import (
    ENVELOPE_SLACK_FT,
    MAX_CENTERLINE_VERTICES,
    SEARCH_RADIUS_FT,
    STREET_CROSSES_LOT_MIN_FT,
    STREET_LINE_MATCH_TOLERANCE_FT,
)

__all__ = ["StreetCheck", "check_street_data"]


@dataclass(frozen=True)
class StreetCheck:
    """``usable`` is False when no street geometry can be read at all (no data, wrong CRS);
    then no edge is judged. ``incomplete`` lists why the street set may be missing something;
    ``crossings`` says which mapped streets run through the lot. Either leaves lot type
    unknown (``blockers``)."""

    usable: bool
    centerlines: tuple[StreetCenterline, ...]
    incomplete: tuple[str, ...]
    crossing_keys: tuple[str, ...] = ()
    crossings: tuple[str, ...] = ()

    @property
    def blockers(self) -> tuple[str, ...]:
        return self.incomplete + self.crossings


def _clean_paths(centerline: StreetCenterline):
    paths = []
    for path in centerline.paths if isinstance(centerline.paths, tuple | list) else ():
        points = [finite_point(p) for p in path] if isinstance(path, tuple | list) else [None]
        if len(points) < 2 or any(p is None for p in points):
            return None
        paths.append(tuple(points))
    return tuple(paths) if paths else None


def _covers(envelope, outline: PreparedOutline) -> bool:
    if not isinstance(envelope, tuple | list) or len(envelope) != 4:
        return False
    xmin, ymin, xmax, ymax = outline.polygon.bounds
    need = (xmin - SEARCH_RADIUS_FT, ymin - SEARCH_RADIUS_FT,
            xmax + SEARCH_RADIUS_FT, ymax + SEARCH_RADIUS_FT)
    corners = [finite_point(pair) for pair in (envelope[:2], envelope[2:])]
    if corners[0] is None or corners[1] is None:
        return False
    (ex0, ey0), (ex1, ey1) = corners
    slack = ENVELOPE_SLACK_FT
    return (ex0 <= need[0] + slack and ey0 <= need[1] + slack
            and ex1 >= need[2] - slack and ey1 >= need[3] - slack)


def _name(centerline: StreetCenterline) -> str:
    return centerline.street_name or centerline.street_key


def check_street_data(streets: StreetData | None, outline: PreparedOutline) -> StreetCheck:
    if streets is None:
        return StreetCheck(False, (), ("No city street data was provided.",), ())
    if not crs_is_measurement_grade(streets.crs):
        return StreetCheck(False, (), ("The street data is not in EPSG:2263 feet.",), ())
    incomplete = list(streets.incomplete_reasons)
    if not _covers(streets.covered_envelope, outline):
        incomplete.append(
            f"The street data does not cover {SEARCH_RADIUS_FT:.0f} ft around the lot."
        )
    usable: list[StreetCenterline] = []
    vertices = 0
    for centerline in streets.centerlines:
        paths = _clean_paths(centerline)
        if paths is None:
            incomplete.append(f"{_name(centerline)} has unusable center-line geometry.")
            continue
        vertices += sum(len(path) for path in paths)
        usable.append(StreetCenterline(
            centerline.street_key, centerline.street_name, centerline.object_id, paths,
            centerline.mapped_width_raw, centerline.status_ok, centerline.status_note))
        width = mapped_width_ft(centerline.mapped_width_raw)
        if width is not None and width / 2 + STREET_LINE_MATCH_TOLERANCE_FT > SEARCH_RADIUS_FT:
            incomplete.append(f"{_name(centerline)} is wider than the search reaches.")
    if vertices > MAX_CENTERLINE_VERTICES:
        return StreetCheck(False, (), ("The street data is too large to check.",), ())
    keys: list[str] = []
    notes: list[str] = []
    for centerline in usable:
        for path in centerline.paths:
            inside = outline.polygon.intersection(LineString(path)).length
            if inside > STREET_CROSSES_LOT_MIN_FT and centerline.street_key not in keys:
                keys.append(centerline.street_key)
                notes.append(f"A mapped street center line ({_name(centerline)}) runs "
                             "through the lot.")
    return StreetCheck(True, tuple(usable), tuple(dict.fromkeys(incomplete)), tuple(keys),
                       tuple(notes))
