#!/usr/bin/env python3
"""Shared library for the measurement-basis worked examples (M5-T126).

Test support, NOT program code. It loads the authored example data files, recomputes
every component area from the stated dimensions and every reconciliation line with
exact decimal arithmetic, and offers a tiny loader. It imports NOTHING from the rule
engine, the scenario engine or any program output: an example must never carry a
value that came from a program run, and this library must never fetch one. Pure stdlib.

The method this library encodes is the owner's (D-090 R430/R432): from ONE schedule of
measured areas, work out the residential ZONING FLOOR AREA and the total HPD
DWELLING-UNIT AREA SEPARATELY (each by inclusion, not by subtracting one from the
other), then reconcile the two line by line so nothing is deducted twice. The ratio is
total HPD-measured dwelling-unit area / residential zoning floor area, and nothing else
(R396). No estimator is built here and no percentage is validated (R436).

Layout it knows about::

    docs/measurement-basis/MEASUREMENT_BASIS.md          the record (hand-written)
    docs/measurement-basis/examples/<id>.json            the authored example data
    docs/measurement-basis/examples/<id>.md              one page per example (rendered)

Nothing here is a professional or legal determination. Per ADR-007 any reading of the
law is a labelled draft with a link to the source text; professional review is advisory.
"""
from __future__ import annotations

import json
import pathlib
from decimal import ROUND_HALF_UP, Decimal

HERE = pathlib.Path(__file__).resolve().parent
# measurement_basis / scenario / tests / api / services / <repo root>
REPO_ROOT = HERE.parents[4]
DOCS_DIR = REPO_ROOT / "docs" / "measurement-basis"
EXAMPLES_DIR = DOCS_DIR / "examples"
RECORD_PATH = DOCS_DIR / "MEASUREMENT_BASIS.md"
SNAPSHOT_DIR = REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"

# The examples, by the file stem of their data file and rendered page.
EXAMPLE_IDS = (
    "example-a-standard-residential",
    "example-b-allowances-conditions-shown",
    "example-c-mixed-use",
)

PORTIONS = ("residential", "non_residential")
ZONING_TREATMENTS = ("count", "exclude", "exclude_if_condition", "not_residential_portion")
HPD_TREATMENTS = ("count", "exclude")
CITATION_KINDS = ("captured", "guideline")
EXCLUSION_METHODS = ("none", "full", "min_of")
CANDIDATE_OPERATIONS = ("multiply", "fixed")
BRIDGE_DIRECTIONS = ("subtract", "add")

# --- the official HPD quote, read at the official source and embedded verbatim ---
# HPD Design Guidelines for New Construction, 2026 edition, subsection "UNIT AREA
# CALCULATION" (Part II, Dwelling Units). Read 2026-10-07 at the official HPD page.
HPD_SOURCE = {
    "document": "HPD Design Guidelines for New Construction, 2026 edition",
    "edition": "2026",
    "subsection": "UNIT AREA CALCULATION",
    "official_url": (
        "https://www.nyc.gov/assets/hpd/downloads/pdfs/services/"
        "hpd-design-guidelines-for-new-construction-2026.pdf"
    ),
    "date_read": "2026-10-07",
    "pdf_last_modified": "2026-09-23",
    "pdf_sha256": "309d1863649bb7ff75d38931ed610de66c8b2ff3986b0de86299212e2cddb890",
    "pdf_page": 28,
    "standing": (
        "A guideline, not law. It applies to projects developed under HPD loan programs "
        "whose initial design-consultation submission is received on or after October 1, "
        "2026; MIH/UAP incentive-only projects not subsidised through an HPD loan program "
        "are not subject to it."
    ),
}
HPD_UNIT_AREA_CALCULATION = (
    "Dwelling unit area is measured within the perimeter walls, from the finished face "
    "of all exterior walls and demising partitions. Structural members that are integral "
    "components of exterior walls or demising partitions, as well as all mechanical and "
    "plumbing chases, are excluded from unit area calculations. All other structural "
    "members — including freestanding columns and columns attached to interior "
    "partitions — are included in unit area calculations. PTACs, PTHPs, or similar "
    "through-wall equipment protruding less than 16” into the space under a window "
    "are not deducted from area calculations."
)

# Fixed key sets (strict: a stray or missing field is a defect, not a silent pass).
EXAMPLE_KEYS = {
    "example_id", "title", "mixed_use", "made_up_note", "standing_label", "building",
    "assumptions_note", "components", "reconciliation", "legal_unit_cap",
    "what_it_shows", "what_it_does_not_show", "sources", "change_log",
}
COMPONENT_KEYS = {
    "component_id", "name", "portion", "how_measured", "area_parts", "measured_area",
    "zoning", "hpd", "notes",
}
AREA_PART_KEYS = {"label", "sign", "width_ft", "depth_ft", "count"}
ZONING_KEYS = {
    "treatment", "provision", "condition", "condition_shown", "excluded_area",
    "exclusion", "citations",
}
EXCLUSION_KEYS = {"method", "candidates", "note"}
CANDIDATE_KEYS = {"label", "operation", "operands", "result"}
HPD_KEYS = {"treatment", "reason", "counted_area", "citations"}
CITATION_KEYS = {
    "kind", "section", "title", "quote", "snapshot_id", "snapshot_file",
    "content_digest", "official_url", "last_amended", "edition", "date_read",
    "status_note",
}
RECON_KEYS = {
    "residential_zoning_floor_area", "total_hpd_dwelling_unit_area", "bridge", "ratio",
}
BRIDGE_KEYS = {"component_id", "direction", "area"}
RATIO_KEYS = {"numerator", "denominator", "value"}
LEGAL_CAP_KEYS = {
    "max_residential_floor_area", "factor", "raw_quotient", "units_cap", "provision",
    "note", "citations",
}
CHANGE_LOG_KEYS = {"date", "summary", "by"}


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def example_path(example_id: str) -> pathlib.Path:
    return EXAMPLES_DIR / f"{example_id}.json"


def page_path(example_id: str) -> pathlib.Path:
    return EXAMPLES_DIR / f"{example_id}.md"


def load_example(example_id: str) -> dict:
    return json.loads(example_path(example_id).read_text())


def load_all() -> dict[str, dict]:
    return {eid: load_example(eid) for eid in EXAMPLE_IDS}


def iter_components(example: dict):
    yield from example["components"]


class ComponentNotFound(KeyError):
    """Raised when a component is asked for by an id that does not exist."""


def find_component(example: dict, component_id: str) -> dict | None:
    for comp in example["components"]:
        if comp["component_id"] == component_id:
            return comp
    return None


# --------------------------------------------------------------------------
# the arithmetic engine (exact decimal; the only place a number is recomputed)
# --------------------------------------------------------------------------
def _dec(value) -> Decimal:
    return Decimal(str(value))


def component_area(component: dict) -> Decimal:
    """Recompute a component's measured area from its stated dimensions.

    Each area part is a rectangle ``width_ft x depth_ft`` taken ``count`` times, added
    or subtracted (a subtracted part carves an inner rectangle, e.g. a wall ring)."""
    total = Decimal("0")
    for part in component["area_parts"]:
        rect = _dec(part["width_ft"]) * _dec(part["depth_ft"]) * _dec(part["count"])
        total += rect if part["sign"] == "add" else -rect
    return total


def candidate_value(candidate: dict) -> Decimal:
    op = candidate["operation"]
    operands = [_dec(o) for o in candidate["operands"]]
    if op == "multiply":
        raw = Decimal("1")
        for value in operands:
            raw *= value
        return raw
    if op == "fixed":
        return operands[0]
    raise ValueError(f"unknown candidate operation {op!r}")


def zoning_excluded(component: dict) -> Decimal:
    """The area removed from zoning floor area for this component.

    An allowance or exclusion is taken ONLY when its condition is shown (R401/R431);
    otherwise the space counts. A capped allowance (``min_of``) never exceeds the
    component's own measured area, so nothing zoning already left out is deducted
    again."""
    z = component["zoning"]
    treatment = z["treatment"]
    if treatment in ("count", "not_residential_portion"):
        return Decimal("0")
    if not z["condition_shown"]:
        return Decimal("0")
    measured = component_area(component)
    method = z["exclusion"]["method"]
    if method == "full":
        return measured
    if method == "min_of":
        values = [candidate_value(c) for c in z["exclusion"]["candidates"]] + [measured]
        return min(values)
    if method == "none":
        return Decimal("0")
    raise ValueError(f"unknown exclusion method {method!r}")


def zoning_counted(component: dict) -> Decimal:
    """The part of a component that counts toward RESIDENTIAL zoning floor area.

    A non-residential (e.g. commercial) component counts nothing toward the residential
    portion's zoning floor area (R407/R437)."""
    if component["portion"] != "residential":
        return Decimal("0")
    return component_area(component) - zoning_excluded(component)


def hpd_counted(component: dict) -> Decimal:
    """The part of a component that counts as HPD dwelling-unit area."""
    if component["portion"] != "residential":
        return Decimal("0")
    return component_area(component) if component["hpd"]["treatment"] == "count" else Decimal("0")


def bridge_contribution(component: dict) -> Decimal:
    """How much this component makes residential zoning floor area exceed HPD area."""
    return zoning_counted(component) - hpd_counted(component)


def residential_zoning_floor_area(example: dict) -> Decimal:
    return sum((zoning_counted(c) for c in example["components"]), Decimal("0"))


def total_hpd_dwelling_unit_area(example: dict) -> Decimal:
    return sum((hpd_counted(c) for c in example["components"]), Decimal("0"))


def ratio_value(example: dict) -> Decimal:
    zoning = residential_zoning_floor_area(example)
    hpd = total_hpd_dwelling_unit_area(example)
    if zoning == 0:
        raise ValueError("residential zoning floor area is zero; ratio undefined")
    return (hpd / zoning).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def legal_unit_cap_units(cap: dict) -> int:
    """ZR 23-52: max residential floor area / factor; a fraction of three-quarters or
    more counts as one unit, otherwise it is dropped. Kept SEPARATE from the physical
    estimate (R392/R404): neither is derived from the other."""
    quotient = _dec(cap["max_residential_floor_area"]) / _dec(cap["factor"])
    whole = int(quotient)
    fraction = quotient - whole
    return whole + (1 if fraction >= Decimal("0.75") else 0)
