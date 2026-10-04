"""Thread B-03 single-lot site geometry into the study-read site facts (lane C).

Journey wave 1 item 1 (``docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md`` §5):
the study read currently shows ``lot_type`` as unknown and carries no per-street
frontage, even though the accepted B-03 engine
(``app.spatial.site_geometry.derive_site_geometry``) can compute the geometric
lot type, the frontage on each street, and (where definable) the lot depth from
the tax-map outline. This module is the pure adapter that carries B-03's result
onto the B-02 site facts the study read already emits.

It is a BRIDGE, not an engine: it computes no geometry and invents no value. It
reads an already-derived :class:`~app.spatial.site_geometry.results.SiteGeometry`
and re-expresses the three facts the contract has a key for -- ``lot_type``,
``lot_frontage`` (per street), ``lot_depth`` -- as ``site_fact.schema.json`` v1
documents, mapping B-03's §4 measurement label one-to-one onto the site_fact
measurement rank (``Approximate — tax map`` -> ``approximate_tax_map``, source
kind ``tax_map_computation`` sourced from the MapPLUTO lot-outline provenance
B-03 carries). Everything B-03 cannot state stays unknown, with B-03's own plain
reason carried in the fact ``note``. No zoning math, no legal text, no fabricated
value.

Rules (faithful to B-03 and to the contract):

- ``lot_type``: a known geometric kind (corner / interior / through, B-03's
  ``LotType.kind``) becomes a known ``approximate_tax_map`` fact ONLY when the
  label maps to a contract rank AND a complete ``tax_map_computation`` source can
  be built from the lot-outline provenance; otherwise the fact stays unknown with
  the reason. An unknown / refused B-03 lot type stays unknown, carrying B-03's
  reason.
- ``lot_frontage``: one fact per B-03 street frontage. A confirmed frontage
  carries B-03's measured length (its ``SourcedValue`` rank/label/source); an
  uncertain frontage stays unknown with B-03's reason. A refused geometry has no
  frontages, so none are added.
- ``lot_depth``: replaced with B-03's single lot depth ONLY when B-03 gives one
  (a corner lot gives none -- its depth is per street). The displaced PLUTO depth
  is kept verbatim in the fact ``note`` (the only reference slot the single-fact
  contract has), so its provenance is never dropped.

Pure, deterministic, no I/O. The study-inputs assembly
(``app.api.v1.study_inputs.assemble_study_inputs``) calls this once, AFTER the
B-06 version-check bridge, so the PLUTO-sourced facts keep their version_check
and the tax-map facts carry none (they are not a versioned city dataset here).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from app.profile.measurement import (
    RANK_APPROXIMATE_TAX_MAP,
    RANK_UNKNOWN,
    measurement,
)
from app.profile.site_facts import BLOCKS, SITE_FACT_CONTRACT_VERSION
from app.spatial.site_geometry.labels import (
    LABEL_CITY_RECORDS,
    LABEL_SURVEY,
    LABEL_TAX_MAP,
    LABEL_UNKNOWN,
    SourcedValue,
)
from app.spatial.site_geometry.results import (
    LotType,
    SiteGeometry,
    StreetFrontage,
)

__all__ = ["thread_site_geometry"]

# B-03 §4 label -> site_fact v1 measurement rank, one-to-one (the labels are the
# exact contract wording; app.profile.measurement owns the canonical rank/label
# tie). A label this map does not cover leaves the value unknown.
_RANK_BY_LABEL: Mapping[str, str] = {
    LABEL_TAX_MAP: RANK_APPROXIMATE_TAX_MAP,
    LABEL_CITY_RECORDS: "city_records",
    LABEL_UNKNOWN: RANK_UNKNOWN,
    LABEL_SURVEY: "survey_entered",
}

# B-03 SourcedValue unit -> site_fact unit (lengths only; areas are not threaded
# here -- the study read keeps the PLUTO lot_area fact).
_UNIT_BY_SOURCEDVALUE_UNIT: Mapping[str, str] = {"ft": "feet"}

# The only rank this adapter can emit as a KNOWN fact: it is the only one B-03
# produces (every outline-derived value is "Approximate — tax map") and the only
# one whose contract source kind (tax_map_computation) we can build from the
# lot-outline provenance. Any other mapped rank keeps the value unknown.
_KNOWN_RANK = RANK_APPROXIMATE_TAX_MAP


def _tax_map_source(provenance: Mapping[str, object] | None) -> dict | None:
    """A ``site_fact`` ``tax_map_computation`` source from the B-03 lot-outline
    provenance, or None when the dataset name, request URL, or retrieval time is
    missing (a known value is never given an incomplete source)."""
    if not isinstance(provenance, Mapping):
        return None
    lot_outline = provenance.get("lot_outline")
    if not isinstance(lot_outline, Mapping):
        return None
    dataset = lot_outline.get("source")
    query_ref = lot_outline.get("request_url")
    retrieved_at = lot_outline.get("retrieved_at")
    if not (_text(dataset) and _text(query_ref) and _text(retrieved_at)):
        return None
    dataset_version = lot_outline.get("dataset_version")
    return {
        "kind": "tax_map_computation",
        "dataset": dataset,
        "dataset_version": dataset_version if _text(dataset_version) else None,
        "retrieved_at": retrieved_at,
        "query_ref": query_ref,
        "document_ref": None,
        "statement": None,
    }


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _known_rank_for(label: str) -> str | None:
    """The contract rank for a KNOWN B-03 value, or None if the label has no
    contract rank or a rank this adapter cannot source as a known fact."""
    rank = _RANK_BY_LABEL.get(label)
    return rank if rank == _KNOWN_RANK else None


def _record(
    *,
    bbl: str,
    fact_id: str,
    key: str,
    value: object,
    unit: str | None,
    rank: str,
    source: dict | None,
    note: str,
    street: str | None = None,
) -> dict:
    known = rank != RANK_UNKNOWN
    return {
        "contract_version": SITE_FACT_CONTRACT_VERSION,
        "fact_id": fact_id,
        "key": key,
        "lot_bbl": bbl,
        "street": street,
        "value": value if known else None,
        "unit": unit if known else None,
        "measurement": measurement(rank),
        "source": source,
        "blocks": [] if known else list(BLOCKS[key]),
        "editable": True,
        "note": note,
    }


def _lot_type_fact(bbl: str, lot_type: LotType, source: dict | None) -> dict:
    """The B-03 geometric lot type as a ``lot_type`` site fact (replacing the
    unknown PLUTO fact). Known only for a corner/interior/through kind whose label
    maps to a contract rank and for which a tax-map source is available."""
    fact_id = f"{bbl}:lot_type"
    rank = _known_rank_for(lot_type.label)
    is_known_kind = lot_type.kind in {"corner", "interior", "through"}
    if is_known_kind and rank is not None and source is not None:
        relations = ". ".join(r.reason for r in lot_type.relations)
        note = lot_type.basis + ((". " + relations) if relations else "") + "."
        return _record(
            bbl=bbl, fact_id=fact_id, key="lot_type", value=lot_type.kind,
            unit=None, rank=rank, source=source, note=note,
        )
    reason = lot_type.reason or "The lot type could not be determined from the tax-map outline."
    if is_known_kind:
        reason = (
            f"A geometric {lot_type.kind} lot type was computed from the tax-map outline, "
            "but it is not carried as a sourced value because its measurement source could "
            "not be recorded; enter the lot type instead."
        )
    return _record(
        bbl=bbl, fact_id=fact_id, key="lot_type", value=None, unit=None,
        rank=RANK_UNKNOWN, source=source, note=reason,
    )


def _frontage_facts(
    bbl: str, frontages: Iterable[StreetFrontage], source: dict | None
) -> list[dict]:
    facts: list[dict] = []
    for frontage in frontages:
        length = frontage.length
        street = frontage.street_name
        fact_id = f"{bbl}:lot_frontage:{street}"
        rank = _known_rank_for(length.label)
        unit = _UNIT_BY_SOURCEDVALUE_UNIT.get(length.unit or "")
        known = length.value is not None and rank is not None and unit is not None
        if known and source is not None:
            facts.append(_record(
                bbl=bbl, fact_id=fact_id, key="lot_frontage", value=length.value,
                unit=unit, rank=rank, source=source, note=length.basis, street=street,
            ))
        else:
            note = length.reason or length.basis or "Frontage could not be measured."
            facts.append(_record(
                bbl=bbl, fact_id=fact_id, key="lot_frontage", value=None, unit=None,
                rank=RANK_UNKNOWN, source=source, note=note, street=street,
            ))
    return facts


def _depth_fact(
    bbl: str, depth: SourcedValue, original: Mapping[str, object], source: dict | None
) -> dict | None:
    """B-03's single lot depth as a ``lot_depth`` fact, keeping the displaced
    PLUTO depth verbatim in the note; or None when B-03 gives no single depth or
    it cannot be sourced (then the original PLUTO fact is kept unchanged)."""
    rank = _known_rank_for(depth.label)
    unit = _UNIT_BY_SOURCEDVALUE_UNIT.get(depth.unit or "")
    if depth.value is None or rank is None or unit is None or source is None:
        return None
    reference = _displaced_reference(original)
    note = depth.basis + ". " + reference if depth.basis else reference
    return _record(
        bbl=bbl, fact_id=f"{bbl}:lot_depth", key="lot_depth", value=depth.value,
        unit=unit, rank=rank, source=source, note=note,
    )


def _displaced_reference(original: Mapping[str, object]) -> str:
    """Plain-English reference line preserving the displaced PLUTO lot depth."""
    value = original.get("value")
    source = original.get("source")
    dataset = source.get("dataset") if isinstance(source, Mapping) else None
    if isinstance(value, int | float) and not isinstance(value, bool):
        dataset_text = f" ({dataset})" if _text(dataset) else ""
        return (
            f"City records give lot depth {value} feet{dataset_text}, kept here as a "
            "reference and not replaced in place."
        )
    return "City records give no usable lot depth value for this lot."


def thread_site_geometry(
    facts: Iterable[Mapping[str, object]], geometry: SiteGeometry
) -> tuple[dict, ...]:
    """New site facts carrying B-03's ``geometry`` onto the B-02 ``facts``.

    Returns one tuple of plain dicts: the ``lot_type`` fact is replaced with
    B-03's geometric type, per-street ``lot_frontage`` facts are added (inserted
    after ``lot_area`` for a natural read order), and ``lot_depth`` is replaced
    only when B-03 gives a single depth. Every other fact is carried byte-for-byte
    (a deep-copied dict). Input facts are never changed.
    """
    bbl = _resolve_bbl(facts, geometry)
    source = _tax_map_source(geometry.provenance)
    lot_type_fact = _lot_type_fact(bbl, geometry.lot_type, source)
    frontage_facts = _frontage_facts(bbl, geometry.frontages, source)

    new_facts: list[dict] = []
    frontages_inserted = False
    for fact in facts:
        key = fact.get("key")
        if key == "lot_frontage":
            # Supersede any pre-existing (unknown) per-street frontage facts with
            # B-03's; the study read assembles with no frontage streets, so in
            # practice there are none here.
            continue
        new_facts.append(dict(fact))
        if key == "lot_type":
            new_facts[-1] = lot_type_fact
        elif key == "lot_depth":
            depth_fact = _depth_fact(bbl, geometry.lot_depth, fact, source)
            if depth_fact is not None:
                new_facts[-1] = depth_fact
        if key == "lot_area":
            new_facts.extend(frontage_facts)
            frontages_inserted = True
    if not frontages_inserted:
        new_facts.extend(frontage_facts)
    return tuple(new_facts)


def _resolve_bbl(facts: Iterable[Mapping[str, object]], geometry: SiteGeometry) -> str:
    """The lot BBL for the threaded facts: the B-02 facts' ``lot_bbl`` (they all
    share it), falling back to the B-03 provenance when no fact carries one."""
    for fact in facts:
        bbl = fact.get("lot_bbl")
        if _text(bbl):
            return bbl  # type: ignore[return-value]
    provenance = geometry.provenance
    lot_outline = provenance.get("lot_outline") if isinstance(provenance, Mapping) else None
    bbl = lot_outline.get("bbl") if isinstance(lot_outline, Mapping) else None
    if _text(bbl):
        return bbl  # type: ignore[return-value]
    raise ValueError("cannot thread site geometry: no lot BBL on the facts or the geometry")
