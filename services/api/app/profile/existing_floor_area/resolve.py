"""Existing zoning floor area as one site_fact v1 record, by precedence (B-05; plan M2-07).

Precedence (strongest first; the first one present is used):

1. **Certificate of occupancy** - a figure read from a certificate of occupancy document
   (rank ``city_records``, source kind ``city_filing``, document_ref = the certificate).
2. **DOB job filing** - the figure from recorded DOB BIS job filings
   (``app.profile.existing_floor_area.dob_filings``; rank ``city_records``, source kind
   ``city_filing``, document_ref = the job and document number).
3. **Stated assumption** - a value the architect enters with the assumption stated
   (rank ``assumed``, source kind ``assumption``).
4. **Unknown** - value null, rank ``unknown``, ``blocks`` = remaining floor area and the
   existing-building paths, and a note that says why.

A certificate outranks a job filing because it certifies the completed building, while a
filing states the figures filed for the work. City records outrank a stated assumption,
as in the site_fact rank order (``app.profile.measurement``). Both placements are
conservative defaults for owner confirmation (B-05 report), not plan text. A candidate
that is not used is listed in ``considered`` with the reason, and a differing value is
also named in the note, so a disagreement stays visible.

City-recorded building area (PLUTO/DOF BldgArea) is not an input here at all
(``inputs`` admits no such value). The value is stated for one tax lot as filed or
given; whether it covers only that tax lot or a zoning lot of several tax lots is not
established (``zoning_lot_scope`` = ``not_established``). When a supplied block row
mentions a zoning lot, the DOB figure is set aside (value unknown; the figure, its source
and the citations stay in ``considered``) until the architect confirms it as a stated
assumption. A zoning-lot step (B-07, B-09, B-11) must not add these values across tax
lots without establishing their scope. This module does not merge zoning lots.

Pure, deterministic code: no I/O.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from app.profile.existing_floor_area.dob_filings import read_dob_filings
from app.profile.existing_floor_area.inputs import (
    JOB_FILINGS_DATASET_ID,
    ExistingFloorAreaEvidence,
    dataset_name,
)
from app.profile.existing_floor_area.scope import ZONING_LOT_SCOPE
from app.profile.measurement import RANK_ASSUMED, RANK_CITY_RECORDS, RANK_UNKNOWN, measurement

__all__ = [
    "BASIS_ASSUMPTION",
    "BASIS_CERTIFICATE",
    "BASIS_DOB_FILING",
    "BASIS_LABELS",
    "BASIS_UNKNOWN",
    "BLOCKED_OUTPUTS",
    "CERTIFICATE_DOCUMENT_DATASET",
    "KEY",
    "PRECEDENCE",
    "SCOPE",
    "ZONING_LOT_SCOPE",
    "ExistingFloorAreaResult",
    "resolve_existing_zoning_floor_area",
]

KEY = "existing_zoning_floor_area"
SITE_FACT_CONTRACT_VERSION = "1.0.0"
# Plan section 3 step 4: without it, remaining capacity is not available; the full-site
# allowance still shows (site_fact blocked_output vocabulary).
BLOCKED_OUTPUTS: tuple[str, ...] = ("remaining_floor_area", "existing_building_paths")

BASIS_CERTIFICATE = "certificate_of_occupancy"
BASIS_DOB_FILING = "dob_job_filing"
BASIS_ASSUMPTION = "stated_assumption"
BASIS_UNKNOWN = "unknown"
PRECEDENCE: tuple[str, ...] = (BASIS_CERTIFICATE, BASIS_DOB_FILING, BASIS_ASSUMPTION)
BASIS_LABELS = MappingProxyType({
    BASIS_CERTIFICATE: "Certificate of occupancy",
    BASIS_DOB_FILING: "DOB job filing",
    BASIS_ASSUMPTION: "Stated assumption",
    # The site_fact 'unknown' measurement label (plan section 4), so both read the same.
    BASIS_UNKNOWN: "Unknown — enter",
})
SCOPE = "tax_lot_as_stated"
CERTIFICATE_DOCUMENT_DATASET = "DOB certificate of occupancy (document)"

_BBL = re.compile(r"^[1-5][0-9]{9}$")
_NEEDS = (
    "Needs existing zoning floor area: from a Buildings Department filing or certificate "
    "of occupancy, or entered as a stated assumption. City-recorded building area is "
    "never used for it."
)
_REFERENCE_ONLY = (
    "City-recorded building area is shown for reference only and is never used for it."
)


@dataclass(frozen=True)
class ExistingFloorAreaResult:
    """The existing zoning floor area fact for one tax lot, with how it was chosen.

    Attributes:
        fact: the site_fact v1 document (key ``existing_zoning_floor_area``).
        basis: which source was used (one of :data:`PRECEDENCE`) or ``unknown``.
        basis_label: its plain label (:data:`BASIS_LABELS`).
        reason: why the value is unknown; None when it is known.
        considered: every figure seen but not used, each ``{basis, document_ref, bin,
            value, reason}``.
        completion: for a DOB filing, the machine-readable evidence that its work was
            completed (the sign-off or the certificate row, with dataset and query);
            otherwise None.
        zoning_lot_mentions: supplied DOB rows on the block whose text mentions a zoning
            lot, each ``{document_ref, tax_lots, text, query_ref, retrieved_at}``.
        scope: ``tax_lot_as_stated``: the value is stated for this tax lot.
        zoning_lot_scope: ``not_established``: whether the value covers only this tax lot
            or a zoning lot of several tax lots is not known.
    """

    fact: dict
    basis: str
    basis_label: str
    reason: str | None
    considered: tuple[dict, ...]
    completion: dict | None = None
    zoning_lot_mentions: tuple[dict, ...] = ()
    scope: str = SCOPE
    zoning_lot_scope: str = ZONING_LOT_SCOPE


@dataclass(frozen=True)
class _Candidate:
    basis: str
    value: int | float
    rank: str
    source: dict
    document_ref: str | None
    description: str


def _area(value: int | float) -> str:
    return f"{value:,} sq ft"


def _source(kind: str, retrieved_at: str, *, dataset: str | None = None,
            query_ref: str | None = None, document_ref: str | None = None,
            statement: str | None = None) -> dict:
    return {"kind": kind, "dataset": dataset, "dataset_version": None,
            "retrieved_at": retrieved_at, "query_ref": query_ref,
            "document_ref": document_ref, "statement": statement}


def _candidates(evidence: ExistingFloorAreaEvidence, dob: Any) -> list[_Candidate]:
    """The available candidates, in precedence order."""
    found = []
    statement = evidence.co_statement
    if statement is not None:
        ref = f"Certificate of occupancy {statement.co_number}"
        found.append(_Candidate(
            BASIS_CERTIFICATE, statement.value_sq_ft, RANK_CITY_RECORDS,
            _source("city_filing", statement.read_at, dataset=CERTIFICATE_DOCUMENT_DATASET,
                    document_ref=ref),
            ref,
            f"{_area(statement.value_sq_ft)} read from certificate of occupancy "
            f"{statement.co_number} (transcribed from the document: no certificate dataset "
            "has a floor-area column).",
        ))
    if dob.value is not None:
        found.append(_Candidate(
            BASIS_DOB_FILING, dob.value, RANK_CITY_RECORDS,
            _source("city_filing", dob.record_set.retrieved_at,
                    dataset=dataset_name(JOB_FILINGS_DATASET_ID),
                    query_ref=dob.record_set.query_ref, document_ref=dob.document_ref),
            dob.document_ref,
            dob.description,
        ))
    assumption = evidence.assumption
    if assumption is not None:
        found.append(_Candidate(
            BASIS_ASSUMPTION, assumption.value_sq_ft, RANK_ASSUMED,
            _source("assumption", assumption.entered_at, statement=assumption.statement),
            None,
            f"{_area(assumption.value_sq_ft)} entered as a stated assumption: "
            f"{assumption.statement}",
        ))
    return found


def _fact(bbl: str, *, value: Any, rank: str, source: dict | None, note: str) -> dict:
    known = value is not None
    return {
        "contract_version": SITE_FACT_CONTRACT_VERSION,
        "fact_id": f"{bbl}:{KEY}",
        "key": KEY,
        "lot_bbl": bbl,
        "street": None,
        "value": value,
        "unit": "square_feet" if known else None,
        "measurement": measurement(rank),
        "source": source,
        "blocks": [] if known else list(BLOCKED_OUTPUTS),
        # Plan section 3 step 3: the architect may edit it; an edit becomes a new fact.
        "editable": True,
        "note": note,
    }


def resolve_existing_zoning_floor_area(
    bbl: str,
    evidence: ExistingFloorAreaEvidence | None = None,
    *,
    recorded_building_count: int | None = None,
) -> ExistingFloorAreaResult:
    """Existing zoning floor area for tax lot ``bbl`` (precedence in the module doc).

    Args:
        bbl: the tax lot (10-digit BBL).
        evidence: the DOB rows, certificate statement and stated assumption supplied;
            None means nothing was supplied.
        recorded_building_count: the city-recorded number of buildings on the tax lot
            (a completeness check on DOB filings only; never an area), or None.

    Raises:
        ValueError: ``bbl`` is not a 10-digit BBL, or an input is malformed.
    """
    if not isinstance(bbl, str) or not _BBL.match(bbl):
        raise ValueError(f"bbl must be a 10-digit BBL, got {bbl!r}")
    evidence = evidence if evidence is not None else ExistingFloorAreaEvidence()
    if not isinstance(evidence, ExistingFloorAreaEvidence):
        raise ValueError("evidence must be an ExistingFloorAreaEvidence")
    dob = read_dob_filings(bbl, evidence.dob_job_filings, evidence.certificates,
                           recorded_building_count=recorded_building_count)
    considered = list(dob.set_aside)
    candidates = _candidates(evidence, dob)
    mentions = dob.zoning_lot_mentions
    scope = " ".join([
        f"Scope: stated for tax lot {bbl}; whether the figure covers only this tax lot or a "
        "zoning lot of several tax lots is not established.",
        *(f"{m['document_ref']} (tax lot {', '.join(m['tax_lots'])}) mentions a zoning lot: "
          f"'{m['text']}'." for m in mentions),
    ])

    if not candidates:
        reason = " ".join([
            f"DOB filings: {dob.reason}" if dob.checked else "No DOB job-filing rows were "
            "supplied.",
            "No certificate of occupancy figure or stated assumption was entered.",
        ])
        note = " ".join([_NEEDS, reason, *(
            f"{m['document_ref']} (tax lot {', '.join(m['tax_lots'])}) mentions a zoning lot: "
            f"'{m['text']}'." for m in mentions)])
        fact = _fact(bbl, value=None, rank=RANK_UNKNOWN, source=None, note=note)
        return ExistingFloorAreaResult(fact, BASIS_UNKNOWN, BASIS_LABELS[BASIS_UNKNOWN],
                                       reason, tuple(considered), None, mentions)

    used, *others = candidates
    also = []
    for other in others:
        differs = other.value != used.value
        considered.append({
            "basis": other.basis, "document_ref": other.document_ref, "bin": None,
            "value": other.value,
            "reason": f"Not used: {BASIS_LABELS[used.basis]} comes first"
                      + (" and gives a different value." if differs else
                         " and gives the same value."),
        })
        if differs:
            also.append(f"{BASIS_LABELS[other.basis]} gives {_area(other.value)} (not used).")
    if used.basis != BASIS_DOB_FILING and dob.checked and dob.value is None:
        also.append(f"DOB filings gave no figure: {dob.reason}")
    note = " ".join([used.description, *also, scope, _REFERENCE_ONLY])
    fact = _fact(bbl, value=used.value, rank=used.rank, source=used.source, note=note)
    completion = dob.completion if used.basis == BASIS_DOB_FILING else None
    return ExistingFloorAreaResult(fact, used.basis, BASIS_LABELS[used.basis], None,
                                   tuple(considered), completion, mentions)
