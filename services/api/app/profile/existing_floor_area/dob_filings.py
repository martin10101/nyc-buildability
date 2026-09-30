"""Existing zoning floor area from recorded DOB BIS job filings (queue item B-05; plan M2-07).

Reads rows of "DOB Job Application Filings" (``ic3t-wcy2``) for one tax lot and returns a
single zoning floor-area figure, or no figure with the plain reason. Fixed rules:

1. **Only this tax lot's filings.** A row belongs to the lot when its identity names the
   lot: the ``bbl`` column (when it is a valid 10-digit BBL) and borough/block/lot (when
   present) must both name it. The ``bbl`` column is polluted in this dataset (a BIN in
   place of the BBL; ``docs/research/dob-legacy-sources.md`` section 3.1), so an invalid
   ``bbl`` falls back to borough/block/lot. A row whose two readings disagree is set aside.
   Filings on other tax lots are never used. This module does not merge zoning lots.
2. **Only completed work.** The figure is the "Proposed Zoning Sqft" of a filing whose
   work is shown as completed: its served status description is "SIGNED OFF", or a
   recorded certificate of occupancy row names the job (``pkdm-hqz6``
   ``job_filing_name`` with status "CO Issued", or ``bs8b-p36w`` ``job_number``, a
   dataset of issued certificates). The link from a DOB NOW certificate to a BIS job
   number is documented in ``docs/research/M1-T007-dob-now-sources.md`` section 4.
   Figures on filings not shown as completed are set aside, with the reason.
3. **Demolished buildings drop out.** A BIN with a signed-off job of type ``DM``
   (demolition) no longer stands; its figures are set aside.
4. **A figure must be shown to describe one building** (``scope.scope_problem``). A
   completed filing that may carry a zoning-lot figure makes its building's figure
   unknown (fail closed), even if another filing gives one.
5. **One building, one figure, or nothing.** The lot gets a figure only when exactly one
   standing building (BIN) has one, every other standing BIN seen in the rows is
   demolished, the building's completed filings agree on the figure, and, when the city
   records give a building count for the lot, that count is 1. Otherwise there is no
   figure and the reason says why. Figures are never added, averaged or picked by date.

Zoning-lot scope is never established (``scope.ZONING_LOT_SCOPE``); rows on the block that
mention a zoning lot are returned for citation. Never read: "total construction floor
area" (not zoning floor area), any DOB NOW job filing column, and PLUTO/DOF building area.

Pure, deterministic code: no I/O.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from app.profile.existing_floor_area.dob_rows import BBL_PATTERN, area, format_area, identity, text
from app.profile.existing_floor_area.inputs import (
    BIS_CO_DATASET_ID,
    DOB_NOW_CO_DATASET_ID,
    JOB_FILINGS_DATASET_ID,
    DobRecordSet,
    dataset_name,
)
from app.profile.existing_floor_area.scope import scope_problem, zoning_lot_mentions

__all__ = ["DobFilingFinding", "read_dob_filings"]

_SIGNED_OFF = "SIGNED OFF"
_DEMOLITION = "DM"
_CO_ISSUED = "CO Issued"
_USED_FIELDS = ("bin__", "job_type", "job_status_descrp", "signoff_date",
                "existing_zoning_sqft", "proposed_zoning_sqft", "enlargement_sq_footage",
                "job_description")


@dataclass(frozen=True)
class DobFilingFinding:
    """The DOB filing figure for a tax lot, or why there is none.

    ``value`` is None when there is no figure; ``reason`` then says why. ``completion`` is
    the machine-readable evidence that the figure's work was completed. ``set_aside``
    lists every filing figure seen but not used, each with its reason.
    ``zoning_lot_mentions`` cites block rows whose text mentions a zoning lot. ``checked``
    is False when no job-filing rows were supplied at all."""

    value: int | float | None
    document_ref: str | None
    description: str | None
    record_set: DobRecordSet | None
    completion: dict | None
    reason: str | None
    set_aside: tuple[dict, ...]
    zoning_lot_mentions: tuple[dict, ...]
    checked: bool


@dataclass(frozen=True)
class _Filing:
    job: str
    doc: str
    bin: str | None
    job_type: str | None
    status: str | None
    signoff_date: str | None
    proposed: int | float | None
    problem: str | None
    scope_problem: str | None
    record_set: DobRecordSet

    @property
    def document_ref(self) -> str:
        return f"DOB BIS job {self.job}, document {self.doc}"


@dataclass(frozen=True)
class _Certificate:
    text: str
    names_lot: bool
    bin: str | None
    ref: dict


def _set_aside(document_ref: str | None, bin_: str | None, value: Any, reason: str) -> dict:
    return {"basis": "dob_job_filing", "document_ref": document_ref, "bin": bin_,
            "value": value, "reason": reason}


def _lot_filings(bbl: str, jobs: Sequence[DobRecordSet], set_aside: list[dict]
                 ) -> tuple[list[_Filing], int]:
    """This lot's filings, one per (job, document), and the count of other-lot rows."""
    grouped: dict[tuple[str, str], list[tuple[Mapping[str, Any], DobRecordSet]]] = {}
    other_lot_rows = 0
    for record_set in jobs:
        for row in record_set.rows:
            readings = identity(row)
            job, doc = text(row.get("job__")), text(row.get("doc__")) or "01"
            ref = f"DOB BIS job {job}, document {doc}" if job else None
            if bbl not in readings:
                other_lot_rows += 1
                continue
            if len(readings) > 1:
                set_aside.append(_set_aside(ref, text(row.get("bin__")), None, (
                    f"The row's BBL column and its borough/block/lot name different lots "
                    f"({', '.join(sorted(readings))}), so it is not used.")))
                continue
            if job is None:
                set_aside.append(_set_aside(None, text(row.get("bin__")), None,
                                            "The row has no job number, so it is not used."))
                continue
            grouped.setdefault((job, doc), []).append((row, record_set))

    filings = []
    for (job, doc), rows in sorted(grouped.items()):
        distinct = {tuple(row.get(column) for column in _USED_FIELDS) for row, _ in rows}
        row, record_set = rows[0]
        ref = f"DOB BIS job {job}, document {doc}"
        if len(distinct) > 1:
            set_aside.append(_set_aside(ref, text(row.get("bin__")), None, (
                "Repeated rows for this filing disagree on its status, zoning figures or "
                "text, so it is not used.")))
            continue
        proposed, problem = area(row, "proposed_zoning_sqft")
        filings.append(_Filing(
            job=job, doc=doc, bin=text(row.get("bin__")), job_type=text(row.get("job_type")),
            status=text(row.get("job_status_descrp")),
            signoff_date=text(row.get("signoff_date")), proposed=proposed, problem=problem,
            scope_problem=scope_problem(row), record_set=record_set,
        ))
    return filings, other_lot_rows


def _certificate(record_set: DobRecordSet, row: Mapping[str, Any]
                 ) -> tuple[str, str, dict] | None:
    """(job number, plain text, reference) of an issued certificate row, else None."""
    name = dataset_name(record_set.dataset_id)
    if record_set.dataset_id == DOB_NOW_CO_DATASET_ID:
        job = text(row.get("job_filing_name"))
        if job is None or row.get("c_of_o_status") != _CO_ISSUED:
            return None
        number = text(row.get("c_of_o_number"))
        issued = text(row.get("c_of_o_issuance_date"))
        kind_field = ("filing_type", row.get("c_of_o_filing_type"))
        described = (f"certificate of occupancy {number or '(no number)'} issued "
                     f"{issued or '(no date)'} ({name}, filing type {kind_field[1]!r})")
    elif record_set.dataset_id == BIS_CO_DATASET_ID:
        job = text(row.get("job_number"))
        if job is None:
            return None
        number = None
        issued = text(row.get("c_o_issue_date"))
        kind_field = ("issue_type", row.get("issue_type"))
        described = (f"certificate of occupancy issued {issued or '(no date)'} "
                     f"({name}, issue type {kind_field[1]!r})")
    else:  # pragma: no cover - ExistingFloorAreaEvidence admits no other dataset
        return None
    ref = {"kind": "certificate_of_occupancy", "dataset": name,
           "query_ref": record_set.query_ref, "retrieved_at": record_set.retrieved_at,
           "document_ref": number, "job": job, "issued": issued, kind_field[0]: kind_field[1]}
    return job, described, ref


def _certificates_by_job(bbl: str, certificates: Iterable[DobRecordSet]
                         ) -> dict[str, list[_Certificate]]:
    """Job number -> the issued certificates that name it and do not name another lot."""
    by_job: dict[str, list[_Certificate]] = {}
    for record_set in certificates:
        for row in record_set.rows:
            found = _certificate(record_set, row)
            readings = identity(row)
            if found is None or (readings and bbl not in readings):
                continue
            job, described, ref = found
            by_job.setdefault(job, []).append(_Certificate(
                text=described,
                names_lot=bbl in readings and len(readings) == 1,
                bin=text(row.get("bin")) or text(row.get("bin_number")),
                ref=ref,
            ))
    return by_job


def _completion(filing: _Filing, certificates: Mapping[str, list[_Certificate]]
                ) -> tuple[str, dict] | None:
    """How the filing's work is shown as completed (text, reference), or None."""
    if filing.status == _SIGNED_OFF:
        return (f"signed off {filing.signoff_date or '(no sign-off date)'}", {
            "kind": "dob_sign_off", "dataset": dataset_name(JOB_FILINGS_DATASET_ID),
            "query_ref": filing.record_set.query_ref,
            "retrieved_at": filing.record_set.retrieved_at,
            "document_ref": filing.document_ref, "job": filing.job,
            "signed_off": filing.signoff_date})
    for certificate in certificates.get(filing.job, ()):
        if certificate.names_lot or (certificate.bin is not None and certificate.bin == filing.bin):
            return certificate.text, certificate.ref
    return None


def _check_count(recorded_building_count: Any) -> None:
    if recorded_building_count is not None and (
        isinstance(recorded_building_count, bool)
        or not isinstance(recorded_building_count, int)
        or recorded_building_count < 0
    ):
        raise ValueError(f"recorded_building_count must be a whole number >= 0 or None, "
                         f"got {recorded_building_count!r}")


def read_dob_filings(
    bbl: str,
    jobs: Sequence[DobRecordSet],
    certificates: Sequence[DobRecordSet] = (),
    *,
    recorded_building_count: int | None = None,
) -> DobFilingFinding:
    """The DOB job-filing zoning floor area for tax lot ``bbl`` (rules in the module doc).

    Args:
        bbl: the tax lot (10-digit BBL).
        jobs: recorded ``ic3t-wcy2`` rows (any lots; other lots are ignored).
        certificates: recorded ``pkdm-hqz6`` / ``bs8b-p36w`` rows.
        recorded_building_count: the city-recorded number of buildings on the tax lot,
            or None when not available (the check is then skipped and said so).
    """
    _check_count(recorded_building_count)
    if not isinstance(bbl, str) or not BBL_PATTERN.match(bbl):
        raise ValueError(f"bbl must be a 10-digit BBL, got {bbl!r}")
    if not jobs:
        return DobFilingFinding(None, None, None, None, None,
                                "No DOB job-filing rows were supplied.", (), (), False)
    set_aside: list[dict] = []
    mentions = zoning_lot_mentions(bbl, jobs)
    filings, other_lot_rows = _lot_filings(bbl, jobs, set_aside)
    certificate_jobs = _certificates_by_job(bbl, certificates)

    demolished: dict[str, str] = {}
    for filing in filings:
        if filing.bin and filing.job_type == _DEMOLITION and filing.status == _SIGNED_OFF:
            demolished[filing.bin] = (f"demolition job {filing.job} signed off "
                                      f"{filing.signoff_date or '(no date)'}")
    standing = sorted({f.bin for f in filings if f.bin and f.bin not in demolished})
    figures: dict[str, list[tuple[_Filing, tuple[str, dict]]]] = {}
    unscoped: dict[str, list[_Filing]] = {}
    for filing in filings:
        if filing.problem is not None:
            set_aside.append(_set_aside(filing.document_ref, filing.bin, None,
                                        f"{filing.problem}, so it is not used."))
            continue
        if filing.proposed is None:
            continue
        if filing.bin is None:
            set_aside.append(_set_aside(filing.document_ref, None, filing.proposed,
                                        "The filing names no building (BIN)."))
            continue
        if filing.bin in demolished:
            set_aside.append(_set_aside(filing.document_ref, filing.bin, filing.proposed, (
                f"Building {filing.bin} was demolished ({demolished[filing.bin]}).")))
            continue
        completion = _completion(filing, certificate_jobs)
        if completion is None:
            set_aside.append(_set_aside(filing.document_ref, filing.bin, filing.proposed, (
                f"The work is not shown as completed (status {filing.status!r}; no "
                "certificate of occupancy names the job), so its proposed figure is "
                "not the existing building.")))
            continue
        if filing.scope_problem is not None:
            set_aside.append(_set_aside(filing.document_ref, filing.bin, filing.proposed,
                                        filing.scope_problem))
            unscoped.setdefault(filing.bin, []).append(filing)
            continue
        figures.setdefault(filing.bin, []).append((filing, completion))

    problems = []
    if not filings:
        problems.append(f"No DOB job filing in the supplied rows is for tax lot {bbl}"
                        f" ({other_lot_rows} rows for other or unidentified lots were not used).")
    elif not standing:
        gone = "; ".join(f"{bin_}: {why}" for bin_, why in sorted(demolished.items()))
        problems.append(f"The DOB filings for tax lot {bbl} name no standing building"
                        + (f" (demolished: {gone})." if gone else "."))
    for bin_, unclear in sorted(unscoped.items()):
        problems.append(
            f"Completed DOB filing {unclear[0].document_ref} for building {bin_} is not shown "
            f"to describe this building alone: {unclear[0].scope_problem}"
            + ("" if unclear[0].scope_problem.endswith(".") else "."))
    for bin_, found in sorted(figures.items()):
        if len({filing.proposed for filing, _ in found}) > 1:
            listed = "; ".join(f"{format_area(f.proposed)} on {f.document_ref}"
                               for f, _ in found)
            problems.append(f"Completed DOB filings for building {bin_} disagree: {listed}.")
    missing = [bin_ for bin_ in standing if bin_ not in figures and bin_ not in unscoped]
    if missing:
        problems.append("No completed DOB filing states a zoning floor area for building"
                        f"{'s' if len(missing) > 1 else ''} {', '.join(missing)}.")
    if len(figures) > 1:
        problems.append(f"DOB filings give figures for more than one standing building "
                        f"({', '.join(sorted(figures))}); a lot total is not taken from them.")
    if (figures and recorded_building_count is not None
            and recorded_building_count != len(standing)):
        problems.append(f"City records count {recorded_building_count} building(s) on the tax"
                        f" lot, but DOB filings describe {len(standing)} standing building(s).")
    if problems:
        return DobFilingFinding(None, None, None, None, None, " ".join(problems),
                                tuple(set_aside), mentions, True)

    [(bin_, found)] = figures.items()
    filing, (completion_text, completion_ref) = found[0]
    others = [f.document_ref for f, _ in found[1:]]
    description = (
        f"'Proposed Zoning Sqft' {format_area(filing.proposed)} on {filing.document_ref} "
        f"(job type {filing.job_type}, building {bin_}); work completed: {completion_text}."
        + (f" The same figure is on {', '.join(others)}." if others else "")
        + ("" if recorded_building_count is not None else
           " The city-recorded building count for the lot was not available to check.")
    )
    return DobFilingFinding(filing.proposed, filing.document_ref, description,
                            filing.record_set, completion_ref, None, tuple(set_aside),
                            mentions, True)
