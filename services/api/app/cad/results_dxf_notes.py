"""Annotation lines of the results-driven DXF (task E-03; plan section 3 step 7,
section 4 "How labels carry through"; M1-22).

Every line is read from the results document, except fixed wording that
carries no result figure. In drawing order:

1. the option and revision (``option_id``, ``revision``) - never fixed text;
2. the results id and computed time (the file is bound to one results document);
3. the "Needs street width" case, when the results are one case of that set;
4. the measurement-status note - see :func:`measurement_notes`;
5. each drawing layer the results mark not available, with the results' reason
   (so a lot-only DXF says why the envelope or floor plates are missing);
6. "Out of date" with the results' reason, when the results are out of date;
7. the coordinates (from ``geometry.crs``) and the units (feet at 1:1);
8. "Not a city record".

The measurement-status note (plan section 3 step 7: "When measurements are not
from a survey, the DXF carries a note on the drawing, for example 'Approximate
- city tax map, not a survey'"): each drawn part of the drawing carries the
results' own measurement label - the lot outline ``geometry.measurement``; the
yards, setback lines and envelope the ``permitted_envelope`` answer's
weakest-input label (plan section 5: yards and setbacks are part of the
envelope); the floor plates the ``building_option`` answer's. The
plan ranks survey > city records > tax map but gives no order between those
and "entered" / "assumed", so the DXF does not pick one "weakest": it prints
one line per distinct label that is not a survey, naming the parts it applies
to. A drawn part whose answer is not available has no label in the results; it
is noted as not known to be from a survey. When every drawn part is from a
survey, there is no note.

ASCII: the R12 stream carries printable ASCII only (``dxf_writer``'s single
sanitizer). Typographic punctuation the results use (the em dash of "Not
available - ...") is folded to ASCII by a closed table; any other character,
and the AutoCAD TEXT control prefixes ``%%`` and ``\\``, fail closed.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.cad.claim_words import contains_claim_word
from app.drawings.kit.errors import DrawingInputError
from app.drawings.kit.model import DrawingInput, LayerUnavailable

__all__ = [
    "MEASUREMENT_NOTE_TEXT",
    "NOT_A_CITY_RECORD",
    "NOT_STATED_NOTE_TEXT",
    "UNITS_NOTE",
    "DxfNote",
    "annotation_notes",
    "ascii_text",
    "measurement_notes",
]

#: Note text per measurement rank that is not a survey (site_fact.schema.json
#: measurement ranks, in the schema's order). The tax-map text is the plan's
#: own example (section 3 step 7); the others are the rank's label (section 4
#: table, task M1-07) followed by the same ", not a survey".
MEASUREMENT_NOTE_TEXT: dict[str, str] = {
    "city_records": "City records, not a survey",
    "approximate_tax_map": "Approximate \u2014 city tax map, not a survey",
    "entered": "Entered, not a survey",
    "assumed": "Assumed, not a survey",
}
SURVEY_RANK = "survey_entered"
NOT_STATED_NOTE_TEXT = "Measurement status not stated in the results, not known to be a survey"

UNITS_NOTE = "Units: feet, 1 drawing unit = 1 ft (scale 1:1)"
NOT_A_CITY_RECORD = "Not a city record - drawn from the results"
_CRS_NOTE = {
    "EPSG:2263": "Coordinates: EPSG:2263 NAD83 New York Long Island, US survey feet",
    "local_feet": (
        "Coordinates: local plane in feet, origin at a lot corner, "
        "axes parallel to the EPSG:2263 grid"
    ),
}

#: Closed ASCII folding of the typographic punctuation results text uses.
_FOLD = {
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u00a0": " ", "\u00b7": "-", "\u2026": "...", "\u00d7": "x",
}


@dataclass(frozen=True)
class DxfNote:
    """One annotation line: its printed ASCII text, its role, and the results
    values it prints (JSON pointers; ``units`` = the fixed feet-at-1:1 statement)."""

    text: str
    role: str
    sources: tuple[str, ...]


def ascii_text(text: str, location: str) -> str:
    """``text`` as printable ASCII, or a typed refusal naming ``location``."""
    folded = "".join(_FOLD.get(ch, ch) for ch in text)
    bad = next((ch for ch in folded if not 0x20 <= ord(ch) <= 0x7E), None)
    if bad is not None:
        raise DrawingInputError("text_not_representable",
                                f"character U+{ord(bad):04X} has no ASCII form in the DXF",
                                location=location)
    if "%%" in folded or "\\" in folded:
        raise DrawingInputError("text_control_code",
                                "text would be read as an AutoCAD control code",
                                location=location)
    return folded


def _fixed(text: str) -> str:
    barred = contains_claim_word(text)
    if barred is not None:  # the platform's own wording never claims approval (D-083)
        raise DrawingInputError("claim_class_word", f"fixed note text contains {barred!r}")
    return ascii_text(text, "")


def _drawn(layer) -> bool:
    return not isinstance(layer, LayerUnavailable) and len(layer) > 0


def _answer_rank(results: Mapping, key: str) -> tuple[str | None, str]:
    answer = results["answers"][key]
    pointer = f"/answers/{key}"
    if answer["status"] != "available":
        return None, f"{pointer}/status"
    return answer["measurement"]["rank"], f"{pointer}/measurement/rank"


def measurement_notes(results: Mapping, data: DrawingInput) -> list[DxfNote]:
    """The measurement-status note lines (none when every drawn part is surveyed)."""
    parts: list[tuple[str, str | None, str]] = [
        ("lot outline", results["geometry"]["measurement"]["rank"], "/geometry/measurement/rank")
    ]
    for name, layer, answer in (
        ("yards", data.yards, "permitted_envelope"),
        ("setback lines", data.setback_lines, "permitted_envelope"),
        ("envelope", data.envelope, "permitted_envelope"),
        ("floor plates", data.floor_plates, "building_option"),
    ):
        if _drawn(layer):
            parts.append((name, *_answer_rank(results, answer)))
    for _name, rank, source in parts:
        if rank is not None and rank != SURVEY_RANK and rank not in MEASUREMENT_NOTE_TEXT:
            raise DrawingInputError("measurement_rank_unknown",
                                    f"no note for measurement rank {rank!r}", location=source)
    notes: list[DxfNote] = []
    for rank in (*MEASUREMENT_NOTE_TEXT, None):
        group = [(name, source) for name, r, source in parts if r == rank]
        if not group:
            continue
        text = MEASUREMENT_NOTE_TEXT[rank] if rank is not None else NOT_STATED_NOTE_TEXT
        applies = ", ".join(name for name, _ in group)
        sources = tuple(dict.fromkeys(source for _, source in group))
        notes.append(DxfNote(f"{_fixed(text)} ({applies})", "measurement_note", sources))
    return notes


def _value(results: Mapping, pointer: str) -> str:
    node = results
    for part in pointer.strip("/").split("/"):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return ascii_text(str(node), pointer)


def _line(results: Mapping, role: str, *pieces: str) -> DxfNote:
    """Pieces starting with ``/`` are results pointers; others are fixed words."""
    words, sources = [], []
    for piece in pieces:
        if piece.startswith("/"):
            words.append(_value(results, piece))
            sources.append(piece)
        else:
            words.append(_fixed(piece))
    return DxfNote(" ".join(words), role, tuple(sources))


def _case_notes(results: Mapping) -> list[DxfNote]:
    case = results["street_width_case"]
    if case is None:
        return []
    base = "/street_width_case"
    notes = [_line(results, "case", f"{base}/marker")]
    for i in range(len(case["assumptions"])):
        notes.append(_line(results, "case", f"{base}/assumptions/{i}/street",
                           "width assumed", f"{base}/assumptions/{i}/assumed"))
    return notes


def _unavailable_notes(results: Mapping, data: DrawingInput) -> list[DxfNote]:
    return [
        _line(results, "not_available", f"{layer.source}/reason")
        for layer in (data.yards, data.setback_lines, data.envelope, data.floor_plates)
        if isinstance(layer, LayerUnavailable)
    ]


def annotation_notes(results: Mapping, data: DrawingInput) -> list[DxfNote]:
    """Every annotation line of the DXF, in drawing order."""
    if data.crs not in _CRS_NOTE:
        raise DrawingInputError("crs_unknown", f"no coordinates note for {data.crs!r}",
                                location="/geometry/crs")
    notes = [
        _line(results, "option", "Option", "/option_id", "- revision", "/revision"),
        _line(results, "results", "Results", "/results_id", "- computed", "/computed_at"),
        *_case_notes(results),
        *measurement_notes(results, data),
        *_unavailable_notes(results, data),
    ]
    if results["out_of_date"]:
        notes.append(_line(results, "out_of_date", "Out of date:", "/out_of_date_reason"))
    notes.append(DxfNote(_fixed(_CRS_NOTE[data.crs]), "crs", ("/geometry/crs",)))
    notes.append(DxfNote(_fixed(UNITS_NOTE), "units", ("units",)))
    notes.append(DxfNote(_fixed(NOT_A_CITY_RECORD), "provenance", ()))
    return notes
