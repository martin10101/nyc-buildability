"""The only inputs existing zoning floor area may come from (queue item B-05; plan M2-07).

Plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` section 3 step 4: existing zoning floor
area comes from "a Buildings Department filing or certificate of occupancy" or "a value
the architect enters as a stated assumption". City-recorded building area is never used.

This module admits exactly those inputs and nothing else:

- :class:`DobRecordSet` - recorded rows of one DOB dataset query, with its provenance.
  Job filings must come from DOB BIS "DOB Job Application Filings" (``ic3t-wcy2``), the
  only DOB dataset with zoning floor-area columns ("Existing Zoning Sqft", "Proposed
  Zoning Sqft"; ``docs/research/dob-legacy-sources.md`` section 3.1). Certificate rows
  (``pkdm-hqz6``, ``bs8b-p36w``) carry no floor area; they only show that a job's work
  received a certificate of occupancy. Any other dataset id is refused, including PLUTO
  (``64uk-42ks``, whose BldgArea is DOF building area) and DOB NOW job filings
  (``w9ak-ipjd``, which has only "total construction floor area").
- :class:`CertificateOfOccupancyStatement` - a zoning floor area read from a certificate
  of occupancy document, with the certificate number. No certificate dataset has a
  floor-area column, so the figure is transcribed from the document.
- :class:`StatedAssumption` - a value the architect enters, with the assumption stated.

Nothing here accepts a building-area input, so PLUTO/DOF building area has no path in.

Pure, deterministic code: no I/O.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

__all__ = [
    "CERTIFICATE_DATASETS",
    "JOB_FILINGS_DATASET_ID",
    "CertificateOfOccupancyStatement",
    "DobRecordSet",
    "ExistingFloorAreaEvidence",
    "StatedAssumption",
    "dataset_name",
]

JOB_FILINGS_DATASET_ID = "ic3t-wcy2"
DOB_NOW_CO_DATASET_ID = "pkdm-hqz6"
BIS_CO_DATASET_ID = "bs8b-p36w"
CERTIFICATE_DATASETS = frozenset({DOB_NOW_CO_DATASET_ID, BIS_CO_DATASET_ID})

# Official dataset titles (docs/research/dob-legacy-sources.md section 2,
# docs/research/M1-T007-dob-now-sources.md section 2), with the id in brackets.
_DATASET_NAMES: Mapping[str, str] = MappingProxyType({
    JOB_FILINGS_DATASET_ID: "DOB Job Application Filings (ic3t-wcy2)",
    DOB_NOW_CO_DATASET_ID: "DOB NOW: Certificate of Occupancy (pkdm-hqz6)",
    BIS_CO_DATASET_ID: "DOB Certificate Of Occupancy (bs8b-p36w)",
})

# Datasets that look like floor-area sources but are not, with the reason they are refused.
_REFUSED: Mapping[str, str] = MappingProxyType({
    "64uk-42ks": (
        "PLUTO building area (BldgArea) is DOF building area, not zoning floor area; "
        "it is shown for reference only and never used as existing zoning floor area."
    ),
    "w9ak-ipjd": (
        "DOB NOW job filings carry no zoning floor-area column; their 'total "
        "construction floor area' is not zoning floor area."
    ),
})

# common.schema.json $defs date_time (RFC 3339 with an explicit offset).
_DATE_TIME = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"
)


def dataset_name(dataset_id: str) -> str:
    return _DATASET_NAMES[dataset_id]


def _require_text(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{what} must be non-empty text, got {value!r}")
    return value


def _require_date_time(value: Any, what: str) -> str:
    if not isinstance(value, str) or not _DATE_TIME.match(value):
        raise ValueError(f"{what} must be an RFC 3339 date-time with an offset, got {value!r}")
    return value


def _require_area(value: Any, what: str) -> int | float:
    if (
        not isinstance(value, int | float)
        or isinstance(value, bool)
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValueError(
            f"{what} must be a positive number of square feet, got {value!r}; a site "
            "without a building uses the study's 'no existing building' option, never 0"
        )
    return value


@dataclass(frozen=True)
class DobRecordSet:
    """Rows of one recorded DOB dataset query, as served, with their provenance.

    Attributes:
        dataset_id: ``ic3t-wcy2`` (job filings) or ``pkdm-hqz6`` / ``bs8b-p36w``
            (certificates of occupancy). Anything else is refused.
        rows: the response rows, unchanged (SODA text values).
        retrieved_at: when the query was sent (RFC 3339).
        query_ref: the exact request URL.
    """

    dataset_id: str
    rows: tuple[Mapping[str, Any], ...]
    retrieved_at: str
    query_ref: str

    def __post_init__(self) -> None:
        if self.dataset_id in _REFUSED:
            raise ValueError(f"dataset {self.dataset_id!r} refused: {_REFUSED[self.dataset_id]}")
        if self.dataset_id not in _DATASET_NAMES:
            raise ValueError(
                f"dataset {self.dataset_id!r} is not a DOB job-filing or certificate "
                f"dataset; expected one of {sorted(_DATASET_NAMES)}"
            )
        if isinstance(self.rows, str | bytes | Mapping) or not isinstance(self.rows, Sequence):
            raise ValueError("rows must be a sequence of response rows")
        rows = tuple(self.rows)
        if not all(isinstance(row, Mapping) for row in rows):
            raise ValueError("every row must be a mapping (one SODA response row)")
        object.__setattr__(self, "rows", rows)
        _require_date_time(self.retrieved_at, "retrieved_at")
        _require_text(self.query_ref, "query_ref")


@dataclass(frozen=True)
class CertificateOfOccupancyStatement:
    """Zoning floor area as stated on a certificate of occupancy document.

    Attributes:
        value_sq_ft: the zoning floor area the certificate states, in square feet.
        co_number: the certificate number (for example ``4623241-0000001``).
        read_at: when the figure was read from the document (RFC 3339).
    """

    value_sq_ft: int | float
    co_number: str
    read_at: str

    def __post_init__(self) -> None:
        _require_area(self.value_sq_ft, "value_sq_ft")
        _require_text(self.co_number, "co_number")
        _require_date_time(self.read_at, "read_at")


@dataclass(frozen=True)
class StatedAssumption:
    """A zoning floor area the architect enters as a stated assumption.

    Attributes:
        value_sq_ft: the assumed zoning floor area, in square feet.
        statement: the assumption in plain English (shown with the value).
        entered_at: when it was entered (RFC 3339).
    """

    value_sq_ft: int | float
    statement: str
    entered_at: str

    def __post_init__(self) -> None:
        _require_area(self.value_sq_ft, "value_sq_ft")
        _require_text(self.statement, "statement")
        _require_date_time(self.entered_at, "entered_at")


@dataclass(frozen=True)
class ExistingFloorAreaEvidence:
    """Everything existing zoning floor area may be taken from, for one tax lot.

    Attributes:
        dob_job_filings: recorded ``ic3t-wcy2`` query results (for example one per BIN).
        certificates: recorded ``pkdm-hqz6`` / ``bs8b-p36w`` query results; used only to
            show that a job's work received a certificate of occupancy.
        co_statement: a figure read from a certificate of occupancy document.
        assumption: a figure the architect enters as a stated assumption.
    """

    dob_job_filings: tuple[DobRecordSet, ...] = field(default=())
    certificates: tuple[DobRecordSet, ...] = field(default=())
    co_statement: CertificateOfOccupancyStatement | None = None
    assumption: StatedAssumption | None = None

    def __post_init__(self) -> None:
        jobs = tuple(self.dob_job_filings)
        certificates = tuple(self.certificates)
        for record_set in jobs:
            if not isinstance(record_set, DobRecordSet):
                raise ValueError("dob_job_filings holds DobRecordSet values only")
            if record_set.dataset_id != JOB_FILINGS_DATASET_ID:
                raise ValueError(
                    f"dob_job_filings must come from {JOB_FILINGS_DATASET_ID}, "
                    f"got {record_set.dataset_id!r}"
                )
        for record_set in certificates:
            if not isinstance(record_set, DobRecordSet):
                raise ValueError("certificates holds DobRecordSet values only")
            if record_set.dataset_id not in CERTIFICATE_DATASETS:
                raise ValueError(
                    f"certificates must come from {sorted(CERTIFICATE_DATASETS)}, "
                    f"got {record_set.dataset_id!r}"
                )
        if self.co_statement is not None and not isinstance(
            self.co_statement, CertificateOfOccupancyStatement
        ):
            raise ValueError("co_statement must be a CertificateOfOccupancyStatement")
        if self.assumption is not None and not isinstance(self.assumption, StatedAssumption):
            raise ValueError("assumption must be a StatedAssumption")
        object.__setattr__(self, "dob_job_filings", jobs)
        object.__setattr__(self, "certificates", certificates)
