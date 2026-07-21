"""Wave-connector + spatial-intersection integration into the canonical profile
(task M2-T012, contract 1.4.0).

Maps the accepted-connector and spatial-engine RESULTS into the three additive
top-level profile sections and the canonical ``source_fact`` provenance records
they reference:

- ``zoning_features`` - per-layer RETRIEVAL facts for the six DCP GIS
  zoning-features layers (task M2-T007). CITYWIDE reference data, NOT a
  lot-level zoning determination (the official use limitation is explicit).
- ``lot_geometry`` - per-BBL MapPLUTO tax-lot geometry facts (task M2-T009).
  The validity taxonomy is preserved; never a legal boundary certification.
- ``spatial_intersection`` - the task M2-T013 lot/zoning facts-with-uncertainty
  substrate, with the engine-internal ``coverage_audits`` diagnostic EXCLUDED
  (owner amendment invariant 6) and the M2-T013 uncertainty NEVER collapsed.

Hard rules (mirroring the rest of app.profile):

- Deterministic mapping only: no AI, no legal interpretation, and NO spatial
  computation here (the engine already computed the facts). This module reshapes
  accepted facts into the contract and attaches provenance; it never invents,
  adjudicates, renormalizes a share range, or labels anything ``verified``.
- Every emitted section fact carries a ``provenance_ref`` (or, for the derived
  intersection, ``provenance_refs``) that resolves to a canonical source_fact
  record this module also emits, so app.profile.builder._assert_provenance_integrity
  and the schema's referential-integrity rule both hold.
- Inputs are consumed READ-ONLY and duck-typed: each result may be the connector
  dataclass OR a plain dict (the fixture/unit-test shape), so the builder is not
  coupled to the connector/spatial import graph.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "MAPPLUTO_GEOMETRY_SOURCE_ID",
    "ZONING_FEATURES_SOURCE_ID",
    "build_wave_sections",
]

# Source-registry ids of the accepted connectors whose facts this module maps
# (used on the emitted provenance records). The spatial-intersection substrate is
# a DERIVED product; its provenance record reuses the lot-geometry source id
# unless the engine record states its own.
ZONING_FEATURES_SOURCE_ID = "nyc-dcp-zoning-features-arcgis"
MAPPLUTO_GEOMETRY_SOURCE_ID = "nyc-dcp-mappluto-arcgis"

# Stable provenance_id stems (unique within one profile; the ``wave:`` prefix
# cannot collide with the PLUTO ``pluto-...`` id scheme).
_PROV_ID_LOT_GEOMETRY = "wave:lot-geometry"
_PROV_ID_SPATIAL_INTERSECTION = "wave:spatial-intersection"


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """Read ``key`` from a dict OR an object, so callers may pass the connector
    dataclass or its dict form interchangeably."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _dataset_version(source_edit: Any, digest: Any) -> str:
    """A non-empty ``dataset_version`` for a wave provenance record.

    The ArcGIS feature services publish no SODA-style release token, so the
    source's own ``dataLastEditDate`` (source_data_last_edited) is the dataset
    version when present; otherwise the content digest identifies the exact
    retrieved version (honest content-addressed version, never invented). Both
    are non-empty strings by construction; a documented sentinel is the last
    resort so the required key is never empty."""
    if isinstance(source_edit, str) and source_edit:
        return source_edit
    if isinstance(digest, str) and digest:
        return digest
    return "unknown-no-source-version"


def _source_fact(
    *,
    provenance_id: str,
    source_id: str,
    original_field_name: str,
    original_value: Any,
    normalized_value: Any,
    retrieved_at: str,
    dataset_version: str,
    bbl: str,
) -> dict:
    """Build one canonical source_fact provenance record for a wave fact. Every
    PRD section 9 required field is present; confidence is 1.0 for a
    deterministic official retrieval (NEVER mapped to a coverage label - PRD
    section 12); the fact is unreviewed (``user_confirmed_or_overridden`` =
    ``none``) and non-conflicting here (cross-source conflicts travel through the
    profile ``conflicts`` array, not this record)."""
    return {
        "provenance_id": provenance_id,
        "source_id": source_id,
        "original_field_name": original_field_name,
        "original_value": original_value,
        "normalized_value": normalized_value,
        "retrieved_at": retrieved_at,
        "dataset_version": dataset_version,
        "effective_date": None,
        "bbl": bbl,
        "confidence": 1.0,
        "user_confirmed_or_overridden": "none",
        "conflict_status": "none",
    }


def _zoning_features_section(
    bbl: str, results: Any, fallback_retrieved_at: str
) -> tuple[dict | None, list[dict]]:
    """Map zoning-features layer results (``LayerQueryResult`` /
    ``LayerExtractResult`` / dict) onto the ``zoning_features`` section plus one
    provenance record per layer. Returns ``(None, [])`` when nothing usable is
    supplied so the builder omits the key entirely."""
    layers: list[dict] = []
    provenance: list[dict] = []
    used_ids: set[str] = set()
    for index, result in enumerate(results):
        layer = _get(result, "layer")
        if not isinstance(layer, str) or not layer:
            continue  # a malformed entry is skipped, never guessed into a fact
        prov_id = f"wave:zoning-features:{layer}"
        if prov_id in used_ids:
            prov_id = f"wave:zoning-features:{layer}:{index}"
        used_ids.add(prov_id)

        drift = list(_get(result, "drift_signals", []) or [])
        digest = _get(result, "normalized_digest")
        source_edit = _get(result, "source_data_last_edited")
        retrieved_at = _get(result, "retrieved_at") or fallback_retrieved_at
        record_count = _get(result, "record_count")
        crs = _get(result, "crs")

        entry: dict = {
            "layer": layer,
            "provenance_ref": prov_id,
            # An unreviewed official retrieval is 'conditional'; a retrieval that
            # carried a schema-drift signal is 'unsupported' (never 'verified').
            "coverage_status": "unsupported" if drift else "conditional",
        }
        if record_count is not None:
            entry["record_count"] = record_count
        if digest is not None:
            entry["normalized_digest"] = digest
        if source_edit is not None:
            entry["source_data_last_edited"] = source_edit
        if crs is not None:
            entry["crs"] = crs
        if drift:
            entry["drift_signals"] = drift
        layers.append(entry)

        provenance.append(
            _source_fact(
                provenance_id=prov_id,
                source_id=ZONING_FEATURES_SOURCE_ID,
                original_field_name=f"zoning_features:{layer}",
                original_value={
                    "layer": layer,
                    "normalized_digest": digest,
                    "record_count": record_count,
                },
                normalized_value={
                    "layer": layer,
                    "normalized_digest": digest,
                    "record_count": record_count,
                    "crs": crs,
                    "drift_signals": drift,
                },
                retrieved_at=retrieved_at,
                dataset_version=_dataset_version(source_edit, digest),
                bbl=bbl,
            )
        )
    if not layers:
        return None, []
    return {"layers": layers}, provenance


def _lot_geometry_coverage(
    outcome: Any,
    review_required: bool,
    geometry_status: Any,
    identifier_conflicts: list,
    drift: list,
) -> str:
    """Deterministic coverage_status for a lot-geometry fact (PRD section 12;
    never derived from connector confidence, never 'verified')."""
    if identifier_conflicts:
        return "data_conflict"
    if outcome == "no_feature":
        return "not_applicable"
    if (
        review_required
        or outcome == "multiple_features"
        or geometry_status in ("invalid_geometry", "review_required")
    ):
        return "professional_review_required"
    if drift:
        return "unsupported"
    return "conditional"


def _lot_geometry_section(
    bbl: str, lot_result: Any, fallback_retrieved_at: str
) -> tuple[dict, dict]:
    """Map a MapPLUTO ``LotGeometryResult`` (or dict) onto the ``lot_geometry``
    section plus its provenance record."""
    outcome = _get(lot_result, "outcome") or "no_feature"
    review_required = bool(_get(lot_result, "review_required", False))
    geometry = _get(lot_result, "geometry")
    geometry_status = _get(geometry, "status") if geometry is not None else None
    area = _get(lot_result, "area_sq_ft")
    shape_area = _get(lot_result, "shape_area_attribute_sq_ft")
    digest = _get(lot_result, "normalized_digest")
    original_geometry_digest = (
        _get(geometry, "original_geometry_digest") if geometry is not None else None
    )
    crs = _get(lot_result, "crs")
    source_edit = _get(lot_result, "source_data_last_edited")
    retrieved_at = _get(lot_result, "retrieved_at") or fallback_retrieved_at
    drift = list(_get(lot_result, "drift_signals", []) or [])
    identifier_conflicts = list(_get(lot_result, "identifier_conflicts", []) or [])
    shapely_version = _get(lot_result, "shapely_version")
    geos_version = _get(lot_result, "geos_version")

    section: dict = {
        "outcome": outcome,
        "review_required": review_required,
        "geometry_status": geometry_status,
        "area_sq_ft": area,
        "provenance_ref": _PROV_ID_LOT_GEOMETRY,
        "coverage_status": _lot_geometry_coverage(
            outcome, review_required, geometry_status, identifier_conflicts, drift
        ),
    }
    if shape_area is not None:
        section["shape_area_attribute_sq_ft"] = shape_area
    if digest is not None:
        section["normalized_digest"] = digest
    if original_geometry_digest is not None:
        section["original_geometry_digest"] = original_geometry_digest
    if crs is not None:
        section["crs"] = crs
    if source_edit is not None:
        section["source_data_last_edited"] = source_edit
    if shapely_version is not None:
        section["shapely_version"] = shapely_version
    if geos_version is not None:
        section["geos_version"] = geos_version
    if drift:
        section["drift_signals"] = drift
    if identifier_conflicts:
        section["identifier_conflicts"] = identifier_conflicts

    provenance = _source_fact(
        provenance_id=_PROV_ID_LOT_GEOMETRY,
        source_id=MAPPLUTO_GEOMETRY_SOURCE_ID,
        original_field_name="lot_geometry",
        original_value={
            "outcome": outcome,
            "original_geometry_digest": original_geometry_digest,
        },
        normalized_value={
            "outcome": outcome,
            "geometry_status": geometry_status,
            "area_sq_ft": area,
            "normalized_digest": digest,
        },
        retrieved_at=retrieved_at,
        dataset_version=_dataset_version(source_edit, digest),
        bbl=bbl,
    )
    return section, provenance


def _spatial_intersection_section(
    bbl: str,
    record: Any,
    fallback_retrieved_at: str,
    input_provenance_ids: list[str],
) -> tuple[dict, dict]:
    """Map a task M2-T013 ``LotIntersectionRecord`` (or its ``as_dict()`` form)
    onto the ``spatial_intersection`` section plus a derived-result provenance
    record. The engine-internal ``coverage_audits`` diagnostic is EXCLUDED and
    the uncertainty is passed through verbatim (never collapsed)."""
    record_dict = record.as_dict() if hasattr(record, "as_dict") else dict(record)
    # Exclude the engine-internal coverage diagnostic (owner amendment invariant
    # 6): it is deliberately NOT a published contract field.
    section = {
        key: value for key, value in record_dict.items() if key != "coverage_audits"
    }

    prov_meta = record_dict.get("provenance") or {}
    prov_id = _PROV_ID_SPATIAL_INTERSECTION
    # provenance_refs: the derived-result record FIRST, then every input fact it
    # was computed from (lot geometry, zoning features). At least [prov_id], so
    # the required non-empty list can never dangle.
    refs = [prov_id]
    for input_id in input_provenance_ids:
        if input_id not in refs:
            refs.append(input_id)
    section["provenance_refs"] = refs

    # Defensive: the engine always emits these, but a hand-built minimal record
    # in a unit test must still satisfy the required contract keys.
    section.setdefault("bbl", record_dict.get("bbl") or bbl)
    section.setdefault("lot_overall_class", record_dict.get("lot_overall_class"))
    section.setdefault(
        "professional_review_required",
        bool(record_dict.get("professional_review_required", False)),
    )

    provenance = _source_fact(
        provenance_id=prov_id,
        source_id=prov_meta.get("source_id") or MAPPLUTO_GEOMETRY_SOURCE_ID,
        original_field_name="spatial_intersection",
        original_value={
            "lot_overall_class": record_dict.get("lot_overall_class"),
            "policy": record_dict.get("policy"),
        },
        normalized_value={
            "lot_overall_class": record_dict.get("lot_overall_class"),
            "professional_review_required": record_dict.get(
                "professional_review_required"
            ),
            "coverage_note": record_dict.get("coverage_note"),
        },
        retrieved_at=prov_meta.get("retrieved_at") or fallback_retrieved_at,
        dataset_version=_dataset_version(
            prov_meta.get("source_data_last_edited"),
            prov_meta.get("normalized_digest"),
        ),
        bbl=bbl,
    )
    return section, provenance


def build_wave_sections(
    bbl: str,
    *,
    lot_geometry: Any = None,
    zoning_features: Any = None,
    spatial_intersection: Any = None,
    fallback_retrieved_at: str,
) -> tuple[dict, list[dict]]:
    """Build the additive contract-1.4.0 profile sections and their provenance
    records from the accepted wave/spatial results.

    Args:
        bbl: canonical BBL of the profile these facts belong to (stamped on every
            emitted provenance record).
        lot_geometry: MapPLUTO ``LotGeometryResult`` or dict; None to omit.
        zoning_features: iterable of zoning-features layer results (or dicts);
            None/empty to omit.
        spatial_intersection: task M2-T013 ``LotIntersectionRecord`` (or dict);
            None to omit.
        fallback_retrieved_at: RFC3339 timestamp used when a result carries no
            ``retrieved_at`` (the builder passes its own ``generated_at``).

    Returns:
        ``(sections, provenance_records)`` - ``sections`` maps each present key
        (``zoning_features`` / ``lot_geometry`` / ``spatial_intersection``) to
        its payload; ``provenance_records`` are canonical source_fact records to
        append to the profile ``provenance`` array. Both are empty when no wave
        input is supplied (a PLUTO-only build is unchanged).
    """
    sections: dict = {}
    provenance_records: list[dict] = []
    # Ids of the INPUT facts the spatial intersection was computed from, so its
    # provenance_refs can point at records that are guaranteed present.
    input_provenance_ids: list[str] = []

    if zoning_features:
        zf_section, zf_provenance = _zoning_features_section(
            bbl, zoning_features, fallback_retrieved_at
        )
        if zf_section is not None:
            sections["zoning_features"] = zf_section
            provenance_records.extend(zf_provenance)
            input_provenance_ids.extend(
                record["provenance_id"] for record in zf_provenance
            )

    if lot_geometry is not None:
        lg_section, lg_provenance = _lot_geometry_section(
            bbl, lot_geometry, fallback_retrieved_at
        )
        sections["lot_geometry"] = lg_section
        provenance_records.append(lg_provenance)
        input_provenance_ids.append(lg_provenance["provenance_id"])

    if spatial_intersection is not None:
        si_section, si_provenance = _spatial_intersection_section(
            bbl, spatial_intersection, fallback_retrieved_at, input_provenance_ids
        )
        sections["spatial_intersection"] = si_section
        provenance_records.append(si_provenance)

    return sections, provenance_records
