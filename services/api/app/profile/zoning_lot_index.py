"""Zoning-lot index classifier (backlog DB-232; task M5-T158; record NB-01).

A PURE classifier over the ACRIS recorded-document INDEX for one tax lot
(:class:`app.connectors.acris_index_soda.AcrisZoningLotIndexResult`). It decides, from the
index metadata alone, whether the lot's recorded zoning-lot description names ANOTHER lot - and
so whether every lot-area figure the report gives for this lot must be labelled conditional on
the zoning lot. It carries the document ids, City Register file numbers, dates, the other lots
on the same block, the lots on another block, and the index "up to date through" date.

It NEVER reads a document, NEVER picks a "latest" document, and NEVER concludes what the zoning
lot is. An index entry does not establish an instrument's contents (D-093; NB-01 stays
``access_blocked``); the downstream wording labels the figures as unreviewed conditional drafts
with a direct link to the recorded documents (ADR-007).

Five states:

- ``NOT_CHECKED``  - no provider was bound (the production default); the output is unchanged.
- ``NOT_READ``     - the index could not be read (connector failed closed); figures conditional.
- ``NONE_FOUND``   - no zoning-lot description (ZONE) is indexed against this lot; no condition.
- ``SINGLE_LOT_ONLY`` - a ZONE is indexed against this lot alone (entire); no condition.
- ``OTHER_LOTS_NAMED`` - a ZONE names this lot together with another lot on the same block, or
  marks this lot as a PARTIAL lot; every lot-area figure carries the zoning-lot condition.

:func:`figures_conditional` is True exactly in ``OTHER_LOTS_NAMED`` and ``NOT_READ`` - the two
states in which part B attaches the condition (owner row D-093-R062 guard).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.connectors.acris_index_soda import (
    AcrisDocument,
    AcrisZoningLotIndexResult,
)

__all__ = [
    "NamedLot",
    "ZoningLotDocument",
    "ZoningLotIndex",
    "ZoningLotIndexState",
    "classify_zoning_lot_index",
    "not_checked",
    "not_read",
]

# ZR 12-10 "zoning lot", repository law capture:
# docs/research/zr-snapshots/v1/zr-12-10-zoning-lot.snapshot.json (snapshot_id
# "zr-12-10-zoning-lot"; engine copy services/api/app/_zr_snapshots/v1/same name; NB-01 E6).
ZR_12_10_CAPTURE_ID = "zr-12-10-zoning-lot"

_ZONE = "ZONE"
_REMINDER_TYPES = ("DECL", "CERT")


class ZoningLotIndexState(str, Enum):
    """The five classifier states (see the module docstring)."""

    NOT_CHECKED = "not_checked"
    NOT_READ = "not_read"
    NONE_FOUND = "none_found"
    SINGLE_LOT_ONLY = "single_lot_only"
    OTHER_LOTS_NAMED = "other_lots_named"


@dataclass(frozen=True)
class NamedLot:
    """A lot named on a recorded document (other than the subject lot)."""

    bbl: str | None
    borough: str
    block: str
    lot: str
    partial_lot: str | None  # "P" (partial) / "E" (entire) / None
    same_block: bool


@dataclass(frozen=True)
class ZoningLotDocument:
    """One recorded document carried in the index (ZONE, or a DECL/CERT reminder). The document
    itself is never read; these are index facts only."""

    document_id: str
    doc_type: str
    crfn: str | None
    document_date: str | None
    recorded_datetime: str | None
    subject_partial_lot: str | None


@dataclass(frozen=True)
class ZoningLotIndex:
    """The classifier's result for one subject tax lot.

    ``reasons`` names why the figures are conditional (``"other_same_block_lots"`` and/or
    ``"partial_lot"``); it is empty unless the state is ``OTHER_LOTS_NAMED``.
    """

    state: ZoningLotIndexState
    subject_bbl: str | None = None
    zone_documents: tuple[ZoningLotDocument, ...] = ()
    reminder_documents: tuple[ZoningLotDocument, ...] = ()
    other_same_block_lots: tuple[NamedLot, ...] = ()
    other_block_lots: tuple[NamedLot, ...] = ()
    as_of_date: str | None = None
    reasons: tuple[str, ...] = ()
    not_read_reason: str | None = None
    provenance: dict = field(default_factory=dict)

    @property
    def figures_conditional(self) -> bool:
        """Whether every lot-area figure must carry the zoning-lot condition. True exactly in
        ``OTHER_LOTS_NAMED`` and ``NOT_READ`` (owner row D-093-R062)."""
        return self.state in (
            ZoningLotIndexState.OTHER_LOTS_NAMED,
            ZoningLotIndexState.NOT_READ,
        )


def not_checked() -> ZoningLotIndex:
    """The default when no provider is bound (production): nothing was read, nothing changes."""
    return ZoningLotIndex(state=ZoningLotIndexState.NOT_CHECKED)


def not_read(
    subject_bbl: str | None, *, reason: str, as_of_date: str | None = None
) -> ZoningLotIndex:
    """The index could not be read. Figures are conditional ("could not be read"), never
    reported as "none found". ``reason`` is the connector's typed error type (observability)."""
    return ZoningLotIndex(
        state=ZoningLotIndexState.NOT_READ,
        subject_bbl=subject_bbl,
        as_of_date=as_of_date,
        not_read_reason=reason,
    )


def _summarise(document: AcrisDocument) -> ZoningLotDocument:
    return ZoningLotDocument(
        document_id=document.document_id,
        doc_type=document.doc_type or "",
        crfn=document.crfn,
        document_date=document.document_date,
        recorded_datetime=document.recorded_datetime,
        subject_partial_lot=document.subject_partial_lot,
    )


def _other_lots(document: AcrisDocument, subject_bbl: str, subject_bl: str) -> list[NamedLot]:
    """The lots a document is indexed against OTHER than the subject lot. ``subject_bl`` is the
    subject's borough+block key (canonical BBL prefix) used to decide "same block"."""
    others: list[NamedLot] = []
    for lot in document.indexed_lots:
        bbl = lot.bbl
        if bbl is not None and bbl == subject_bbl:
            continue  # the subject lot itself
        same_block = bbl is not None and bbl[:6] == subject_bl
        others.append(
            NamedLot(
                bbl=bbl,
                borough=lot.borough,
                block=lot.block,
                lot=lot.lot,
                partial_lot=lot.partial_lot,
                same_block=same_block,
            )
        )
    return others


def classify_zoning_lot_index(result: AcrisZoningLotIndexResult) -> ZoningLotIndex:
    """Classify the ACRIS index read into one of the five states per draft rule DB232-R1.

    DRAFT reading (NOT reviewed; a labelled unreviewed interpretation, ADR-007). Grounded in
    the ACRIS Document Control Codes (NB-01 E3: ZONE = "ZONING LOT DESCRIPTION", DECL =
    "DECLARATION", CERT = "CERTIFICATE") and ZR 12-10 "zoning lot" (capture
    :data:`ZR_12_10_CAPTURE_ID`). A reviewer must open those sources themselves; this is not a
    title search and does not establish the zoning lot.

    DB232-R1:
      (a) A ZONE indexed against the subject AND another lot on the SAME borough and block gives
          OTHER_LOTS_NAMED. Reason: the codes table names ZONE a "zoning lot description", and
          ZR 12-10 requires the zoning lot's description (and each declaration) to be recorded
          against every lot of record in it, within a single block (paragraphs (b)-(d)).
      (b) DECL and CERT are WEAKER reminders only - listed beside a ZONE or in the existing
          zoning-lot-history flags, never a warning on their own. Reason: their code
          descriptions are generic (a DECL may be a restrictive or easement declaration, not a
          ZR 12-10(d) zoning-lot declaration). Reviewer counterexample: a ZR 12-10(d)
          declaration typed DECL with no ZONE would be missed here; the existing generic
          zoning-lot statement still covers that case.
      (c) Lots on ANOTHER block are listed for checking but never trigger the same-block
          warning (ZR 12-10 (b)-(d): "located within a single block").
      (d) A subject row marked partial_lot "P" on a ZONE also makes the figures conditional (the
          description covers only part of the tax lot, so the lot-area basis is uncertain).
      (e) The program never picks the "latest" document and never concludes what the zoning lot
          is: ALL ZONE documents are considered and only an index-level observation is made.
    """
    subject_bbl = result.subject_bbl
    subject_bl = subject_bbl[:6]

    zone_documents: list[ZoningLotDocument] = []
    reminder_documents: list[ZoningLotDocument] = []
    same_block: dict[str | None, NamedLot] = {}
    other_block: dict[str | None, NamedLot] = {}
    partial_subject = False

    for document in result.documents:
        doc_type = (document.doc_type or "").strip().upper()
        if doc_type == _ZONE:
            zone_documents.append(_summarise(document))
            # (e) consider EVERY zone document, never a single "latest".
            if (document.subject_partial_lot or "").strip().upper() == "P":
                partial_subject = True  # (d)
            for other in _other_lots(document, subject_bbl, subject_bl):
                bucket = same_block if other.same_block else other_block  # (a) vs (c)
                bucket.setdefault(other.bbl or f"{other.borough}-{other.block}-{other.lot}", other)
        elif doc_type in _REMINDER_TYPES:
            reminder_documents.append(_summarise(document))  # (b)

    if not zone_documents:
        # No zoning-lot description. DECL/CERT (if any) are reminders only (b); no condition (c).
        state = ZoningLotIndexState.NONE_FOUND
        reasons: tuple[str, ...] = ()
    else:
        reason_list: list[str] = []
        if same_block:
            reason_list.append("other_same_block_lots")  # (a)
        if partial_subject:
            reason_list.append("partial_lot")  # (d)
        if reason_list:
            state = ZoningLotIndexState.OTHER_LOTS_NAMED
        else:
            # A ZONE on this lot alone (entire), possibly also on another block (c).
            state = ZoningLotIndexState.SINGLE_LOT_ONLY
        reasons = tuple(reason_list)

    return ZoningLotIndex(
        state=state,
        subject_bbl=subject_bbl,
        zone_documents=tuple(zone_documents),
        reminder_documents=tuple(reminder_documents),
        other_same_block_lots=tuple(same_block.values()),
        other_block_lots=tuple(other_block.values()),
        as_of_date=result.as_of_date,
        reasons=reasons,
        provenance=dict(result.provenance),
    )
