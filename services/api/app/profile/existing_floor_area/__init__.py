"""Existing zoning floor area for one tax lot (queue item B-05; plan M2-07, section 3 step 4).

Done when (plan M2-07): "Existing floor area is never taken from DOF building area."

- ``inputs``: the only admitted sources - recorded DOB BIS job filings (``ic3t-wcy2``),
  certificate-of-occupancy rows (completion evidence only), a figure read from a
  certificate of occupancy, and a stated assumption. No building-area input exists.
- ``dob_rows``: reading served DOB row fields (identity, square-foot figures).
- ``scope``: whether a filing's figure is shown to describe one building; block rows that
  mention a zoning lot. Zoning-lot scope is never established here.
- ``dob_filings``: the zoning figure from DOB job filings for the tax lot, or why none.
- ``resolve``: precedence (certificate > DOB filing > stated assumption > unknown) and
  the site_fact v1 record with its source label.

Library only: no route and no caller outside ``app.profile.site_facts`` yet. Lane C wires
it into the study; Lane A consumes the fact (it computes nothing here).
"""

from app.profile.existing_floor_area.dob_filings import DobFilingFinding, read_dob_filings
from app.profile.existing_floor_area.inputs import (
    CERTIFICATE_DATASETS,
    JOB_FILINGS_DATASET_ID,
    CertificateOfOccupancyStatement,
    DobRecordSet,
    ExistingFloorAreaEvidence,
    StatedAssumption,
)
from app.profile.existing_floor_area.resolve import (
    BASIS_ASSUMPTION,
    BASIS_CERTIFICATE,
    BASIS_DOB_FILING,
    BASIS_LABELS,
    BASIS_UNKNOWN,
    BLOCKED_OUTPUTS,
    CERTIFICATE_DOCUMENT_DATASET,
    PRECEDENCE,
    SCOPE,
    ZONING_LOT_SCOPE,
    ExistingFloorAreaResult,
    resolve_existing_zoning_floor_area,
)

__all__ = [
    "BASIS_ASSUMPTION",
    "BASIS_CERTIFICATE",
    "BASIS_DOB_FILING",
    "BASIS_LABELS",
    "BASIS_UNKNOWN",
    "BLOCKED_OUTPUTS",
    "CERTIFICATE_DATASETS",
    "CERTIFICATE_DOCUMENT_DATASET",
    "JOB_FILINGS_DATASET_ID",
    "PRECEDENCE",
    "SCOPE",
    "ZONING_LOT_SCOPE",
    "CertificateOfOccupancyStatement",
    "DobFilingFinding",
    "DobRecordSet",
    "ExistingFloorAreaEvidence",
    "ExistingFloorAreaResult",
    "StatedAssumption",
    "read_dob_filings",
    "resolve_existing_zoning_floor_area",
]
