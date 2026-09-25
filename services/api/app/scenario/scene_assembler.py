"""The D-087 PKT-E 3D scene payload assembler (plan section 2.1).

A PURE, deterministic assembler that turns the accepted massing truth object
(:class:`app.scenario.massing_model.MassingModel`) plus a fetched context-building
result (:func:`app.connectors.building_footprints_arcgis.fetch_context_buildings`)
into ONE renderer-agnostic scene payload the web 3D viewer draws and never becomes
the source of. It does NO network I/O itself: the caller (the UNMOUNTED
``scene_api`` route) fetches the context buildings off the event loop and hands the
result in, so the whole assembler runs offline in tests.

What the payload carries (plan section 2.1):

* every field of ``MassingModel.as_dict()`` - ``source``, ``disclosure``,
  ``coordinate_reference_system`` (with ``world_to_local``), ``parcel``,
  ``building_layer``, ``meshes``, ``plates``, ``metrics``, ``provenance`` - verbatim;
* a ``context_buildings`` layer built from the connector result, each building placed
  under ONE declared vertical datum (see :data:`GROUND_DATUM_DECISION`): its
  ``base_z_ft`` is the connector's ``relative_base_z_ft`` (``GROUND_ELEVATION`` minus
  the site ground) in the massing model's local z=0 frame, never an absolute NAVD88
  elevation and never guessed;
* the vertical unit made EXPLICIT (DB-054 (k));
* honest disclosures: per-level nesting is checked against the LOT not the floor below
  (DB-054 (l)); the mesh carries no exterior/party-wall distinction (DB-054 (n));
  MultiPolygon courtyard holes are DISCLOSED and never dropped (DB-053 (g)); zero or
  unverified ground elevations are disclosed, never treated as sea level (DB-058 (f)).

Honesty (D-083 / D-076-R002): the massing labels are the massing model's own
("Proposed - not a city record" / "Generated building option"); context footprints are
labelled an official city record (display/massing grade), never permitted, approved, or
a maximum-allowed building, and no legal conclusion is drawn.

Untrusted text (DB-058 (a)): every context-building source string (the attributes map,
``geom_source``, ``last_status_type``) is DECLARED untrusted and ESCAPED for rendering
here (HTML-entity encoded, control characters and the U+2028/U+2029 line/paragraph
separators stripped, length-bounded); the raw verbatim strings are not emitted into the
scene. No source or caller text is ever logged (this module does not log at all).

String coordinates (DB-054 (o)): a lot ring or footprint that arrives with numeric
STRING coordinates (as MapPLUTO can serialize them) is parsed to float here before the
massing model sees it; a non-numeric or non-finite coordinate fails closed as a typed
:class:`SceneAssemblyError`, never a silent default.

Deterministic and offline: standard library plus the admitted ``shapely`` (only through
the massing model / connector). No new dependency, no network, no route, no web.
"""

from __future__ import annotations

import html
import math
from collections.abc import Mapping
from typing import Any

from app.connectors.building_footprints_arcgis import (
    ContextBuilding,
    ContextBuildingsResult,
)
from app.scenario.massing_model import (
    SOURCE_PROPOSED,
    VERTICAL_UNIT,
    MassingModel,
    MassingModelError,
    build_from_generated_option,
    build_massing_model,
)

__all__ = [
    "SCENE_VERSION",
    "CONTEXT_LAYER",
    "GROUND_DATUM_DECISION",
    "SceneAssemblyError",
    "assemble_scene",
    "build_scene_massing",
    "build_scene_payload",
    "parse_ring",
]

SCENE_VERSION = "scene-1.0.0"
CONTEXT_LAYER = "context_buildings"

#: Upper bound on any single escaped untrusted source string in the payload, so a
#: hostile or broken official value cannot inflate the scene (a render/transport bound,
#: not a source fact).
MAX_UNTRUSTED_LEN = 512

#: Strip C0/C1 control characters, DEL, and the U+2028 / U+2029 line & paragraph
#: separators before HTML-escaping an untrusted source string, so no separator can break
#: a renderer's line handling even after entity encoding (mirrors the connector's
#: correlation-id hygiene, DB-073 (a)).
_RENDER_UNSAFE_DELETE = {c: None for c in [*range(0x20), 0x7F, *range(0x80, 0xA0),
                                           0x2028, 0x2029]}

#: The ONE ground datum chosen KNOWINGLY for context-building base elevations
#: (DB-058 (f), DB-053 (f)). The massing model is a relative z=0 frame whose z=0 is the
#: site ground; each context building is placed at ``GROUND_ELEVATION - site_ground`` (the
#: connector's ``relative_base_z_ft``), so the whole scene shares one local vertical frame.
#: Both official GROUND_ELEVATION definitions are disclosed and NEITHER is reconciled; the
#: NAVD88 attribution is stated exactly as the sources state it; a zero or unverified ground
#: is disclosed, never silently treated as sea level.
GROUND_DATUM_DECISION: dict[str, Any] = {
    "chosen": "local_scene_frame_relative_to_site_ground",
    "vertical_unit": VERTICAL_UNIT,
    "source_field": "GROUND_ELEVATION",
    "source": (
        "NYC OTI building-footprint layer (BUILDING_view/FeatureServer/0; NYC Open Data "
        "5zhs-2jue) GROUND_ELEVATION, as published"
    ),
    "rule": (
        "base_z_ft = GROUND_ELEVATION - site_ground_elevation_ft (the connector's "
        "relative_base_z_ft): a RELATIVE offset in the massing model's local z=0 frame "
        "(z=0 = the declared site ground), never an absolute NAVD88 elevation"
    ),
    "definitions_disclosed": {
        "city_dictionary": (
            "the lowest elevation at the building ground level, calculated from LiDAR or "
            "photogrammetrically"
        ),
        "fgdc_metadata": (
            "an interpolated bare-earth elevation at the building centroid, from the 2010 "
            "LiDAR-derived digital terrain model"
        ),
    },
    "navd88_attribution": (
        "NAVD88 is stated ONLY by the City dictionary (when collected photogrammetrically or "
        "from modern sources); the service's FGDC metadata states no datum. Neither definition "
        "is reconciled here."
    ),
    "unverified_ground_policy": (
        "a zero or otherwise unverified GROUND_ELEVATION is DISCLOSED per building and never "
        "treated as sea level; a missing ground, or a missing site ground, yields base_z_ft "
        "null with the reason disclosed, never a guessed value"
    ),
}

#: Scene-level honesty / limitation disclosures carried on every payload.
_MASSING_DISCLOSURES = (
    {
        "code": "per_level_nesting_not_asserted",
        "backlog": "DB-054 (l)",
        "detail": (
            "Each per-level outline is validated against the LOT, not nested within the floor "
            "below; cantilevers are allowed and inter-floor nesting is not asserted."
        ),
    },
    {
        "code": "no_party_wall_distinction",
        "backlog": "DB-054 (n)",
        "detail": (
            "The massing mesh carries no exterior/party (shared) wall distinction; every wall "
            "is an undifferentiated surface."
        ),
    },
)

_CONTEXT_DISCLOSURES = (
    {
        "code": "multipolygon_courtyard_holes_disclosed",
        "backlog": "DB-053 (g)",
        "detail": (
            "A context footprint may be MultiPolygon with courtyard holes; every exterior part "
            "and every hole is disclosed here and NONE is dropped. A consumer that extrudes a "
            "single ring (the massing prism builder refuses holes) must refuse or handle "
            "multipart/holes explicitly."
        ),
    },
    {
        "code": "untrusted_source_text_escaped",
        "backlog": "DB-058 (a)",
        "detail": (
            "Context-building source strings (attributes, geom_source, last_status_type) are "
            "verbatim official text; they are declared untrusted and are HTML-escaped and "
            "control-character-stripped here before rendering. The raw strings are not emitted."
        ),
    },
    {
        "code": "display_massing_grade_not_survey",
        "backlog": None,
        "detail": (
            "Context footprints are the official OTI layer's reprojected coordinates: display "
            "and massing grade, not survey grade. MapPLUTO remains the measurement channel."
        ),
    },
)

_CONTEXT_RECORD_DISCLOSURE = (
    "Official NYC building footprint (OTI) - display and massing grade, not survey grade; not a "
    "zoning determination and not a statement of what may be built."
)


class SceneAssemblyError(ValueError):
    """A typed, caller-facing scene refusal. Carries a machine-readable ``reason`` and,
    where a specific input is implicated, the dotted ``field`` path. A subclass of
    :class:`ValueError` so a caller may catch broadly; nothing is silently defaulted."""

    def __init__(self, message: str, *, reason: str, field: str | None = None) -> None:
        super().__init__(message)
        self.reason = reason
        self.field = field


# ---------------------------------------------------------------------------
# Coordinate parsing (DB-054 (o)): numeric strings -> float, or typed refusal.
# ---------------------------------------------------------------------------


def _coerce_coordinate(value: object) -> float | None:
    """A finite float from an int/float or a numeric STRING; ``None`` for a bool, a
    non-numeric string, a non-parseable value, or a non-finite result."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, str):
        try:
            number = float(value.strip())
        except (ValueError, TypeError):
            return None
        return number if math.isfinite(number) else None
    return None


def parse_ring(ring: object, field: str) -> list[list[float]]:
    """Parse a ring's coordinates to float (DB-054 (o)): a numeric STRING coordinate (as
    MapPLUTO can serialize) becomes a float; a non-numeric or non-finite coordinate fails
    closed as :class:`SceneAssemblyError`, never a default.

    A ring whose SHAPE is malformed (not a list of ``[x, y]`` pairs) is returned unchanged
    so the massing model's own typed validation names the shape fault - this parser only
    resolves string coordinates, it does not duplicate the shape contract."""
    if not isinstance(ring, (list, tuple)):
        return ring  # type: ignore[return-value]
    parsed: list[list[float]] = []
    for index, vertex in enumerate(ring):
        if not isinstance(vertex, (list, tuple)) or len(vertex) != 2:
            return ring  # type: ignore[return-value]  # defer shape refusal to the massing model
        x = _coerce_coordinate(vertex[0])
        y = _coerce_coordinate(vertex[1])
        if x is None or y is None:
            raise SceneAssemblyError(
                f"{field}[{index}] is not a finite [x, y] coordinate pair (numeric strings "
                "are parsed; a non-numeric or non-finite value is refused)",
                reason="unparseable_coordinate", field=f"{field}[{index}]")
        parsed.append([x, y])
    return parsed


def _parse_massing_coords(block: Mapping[str, Any], base_field: str) -> dict:
    """Return a copy of a ``proposed_massing`` block with every outline's coordinates
    parsed to float (DB-054 (o)). Non-geometry fields are untouched; a malformed shape is
    left for the massing model to refuse by name."""
    out = dict(block)
    outline = out.get("outline")
    if isinstance(outline, Mapping) and "vertices" in outline:
        out["outline"] = {
            **outline,
            "vertices": parse_ring(outline["vertices"], f"{base_field}.outline.vertices"),
        }
    levels = out.get("levels")
    if isinstance(levels, list):
        new_levels = []
        for i, level in enumerate(levels):
            lvl_outline = level.get("outline") if isinstance(level, Mapping) else None
            if isinstance(lvl_outline, Mapping) and "vertices" in lvl_outline:
                level = {**level, "outline": {
                    **lvl_outline,
                    "vertices": parse_ring(lvl_outline["vertices"],
                                           f"{base_field}.levels[{i}].outline.vertices")}}
            new_levels.append(level)
        out["levels"] = new_levels
    return out


# ---------------------------------------------------------------------------
# Massing build (parses string coordinates, wraps the massing refusal).
# ---------------------------------------------------------------------------


def build_scene_massing(
    *,
    lot_ring: object,
    proposed_massing: Mapping[str, Any] | None = None,
    generated_option: Mapping[str, Any] | None = None,
    scenario_id: str | None = None,
    property_geometry_version_id: str | None = None,
    rule_release_id: str | None = None,
) -> MassingModel:
    """Build the massing truth object for the scene from EXACTLY ONE of a
    ``proposed_massing`` block or a ``generated_option`` (the max-envelope engine's
    ``as_dict`` shape). String coordinates are parsed to float (DB-054 (o)) before the
    accepted builder runs; a massing quality-gate refusal is re-raised as a typed
    :class:`SceneAssemblyError` naming the same field, so the route maps one refusal family
    to a client response."""
    if (proposed_massing is None) == (generated_option is None):
        raise SceneAssemblyError(
            "exactly one of proposed_massing or generated_option is required",
            reason="invalid_source", field=None)
    parsed_lot = parse_ring(lot_ring, "lot_ring")
    try:
        if proposed_massing is not None:
            if not isinstance(proposed_massing, Mapping):
                raise SceneAssemblyError("proposed_massing must be an object",
                                         reason="invalid_source", field="proposed_massing")
            return build_massing_model(
                lot_ring=parsed_lot,
                proposed_massing=_parse_massing_coords(proposed_massing, "proposed_massing"),
                source=SOURCE_PROPOSED, scenario_id=scenario_id,
                property_geometry_version_id=property_geometry_version_id,
                rule_release_id=rule_release_id)
        if not isinstance(generated_option, Mapping):
            raise SceneAssemblyError("generated_option must be an object",
                                     reason="invalid_source", field="generated_option")
        envelope = dict(generated_option)
        candidate = envelope.get("candidate")
        if isinstance(candidate, Mapping):
            envelope["candidate"] = _parse_massing_coords(candidate,
                                                          "generated_option.candidate")
        return build_from_generated_option(
            lot_ring=parsed_lot, max_envelope=envelope, scenario_id=scenario_id,
            property_geometry_version_id=property_geometry_version_id,
            rule_release_id=rule_release_id)
    except MassingModelError as exc:
        raise SceneAssemblyError(str(exc), reason=exc.reason, field=exc.field) from exc


# ---------------------------------------------------------------------------
# Untrusted source-text escaping (DB-058 (a)).
# ---------------------------------------------------------------------------


def _escape_untrusted(value: object) -> object:
    """HTML-escape a string source value for rendering after stripping control characters
    and the U+2028/U+2029 separators, length-bounded (DB-058 (a)). Non-string values carry
    no injection risk and pass through unchanged."""
    if not isinstance(value, str):
        return value
    stripped = value.translate(_RENDER_UNSAFE_DELETE)
    escaped = html.escape(stripped, quote=True)
    if len(escaped) <= MAX_UNTRUSTED_LEN:
        return escaped
    return escaped[:MAX_UNTRUSTED_LEN] + "...(truncated)"


def _escape_attributes(attributes: Mapping[str, Any]) -> dict:
    """Escape every string VALUE of an official attributes map for rendering; keep numeric
    and null values as-is. Keys are the pinned official field names (not caller text)."""
    return {name: _escape_untrusted(value) for name, value in attributes.items()}


# ---------------------------------------------------------------------------
# Context-building assembly.
# ---------------------------------------------------------------------------


def _ground_status(building: ContextBuilding, site_ground: float | None) -> str:
    """Disclose WHY a context building's base_z is grounded or not - never a silent zero."""
    if building.ground_elevation_ft is None:
        return "ground_elevation_missing"
    if site_ground is None:
        return "site_ground_not_supplied"
    if "ground_elevation_zero_unverified" in building.flags:
        return "ground_zero_unverified"
    return "grounded"


def _context_building(building: ContextBuilding, site_ground: float | None) -> dict:
    """One context building placed under the declared datum, holes disclosed, source text
    escaped. ``base_z_ft`` / ``roof_z_ft`` are the connector's relative offsets in the local
    frame; both are null (with a disclosed status) when the ground or site ground is absent -
    never a fabricated value."""
    return {
        "object_id": building.object_id,
        "record_class": "official_city_footprint",
        "disclosure": _CONTEXT_RECORD_DISCLOSURE,
        "bin": building.bin,
        "base_bbl": building.base_bbl,
        "mappluto_bbl": building.mappluto_bbl,
        "joins_subject_lot": building.joins_subject_lot,
        "feature_code": building.feature_code,
        "feature_code_label": building.feature_code_label,
        "construction_year": building.construction_year,
        "height_roof_ft": building.height_roof_ft,
        "ground_elevation_ft": building.ground_elevation_ft,
        "base_z_ft": building.relative_base_z_ft,
        "roof_z_ft": building.relative_roof_z_ft,
        "base_z_grounded": building.relative_base_z_ft is not None,
        "ground_status": _ground_status(building, site_ground),
        "vertical_unit": VERTICAL_UNIT,
        "geometry_status": building.geometry_status,
        "geometry_findings": list(building.geometry_findings),
        "parts": [
            {"exterior": [list(pt) for pt in part.exterior],
             "holes": [[list(pt) for pt in hole] for hole in part.holes],
             "area_sq_ft": part.area_sq_ft}
            for part in building.parts
        ],
        "has_holes": "has_holes" in building.flags,
        "multipart": "multipart" in building.flags,
        "footprint_area_sq_ft": building.footprint_area_sq_ft,
        "query_relation": building.query_relation,
        "flags": list(building.flags),
        "gaps": [dict(gap) for gap in building.gaps],
        # DB-058 (a): the untrusted source strings, declared and ESCAPED for rendering.
        "untrusted_text_fields": list(building.untrusted_text_fields),
        "untrusted_text_notice": building.untrusted_text_notice,
        "geom_source_escaped": _escape_untrusted(building.geom_source),
        "last_status_type_escaped": _escape_untrusted(building.last_status_type),
        "attributes_escaped": _escape_attributes(building.attributes),
    }


def _bounded(text: object, limit: int = MAX_UNTRUSTED_LEN) -> str:
    """Bound a refusal string for the payload (AS-3): no unbounded detail is surfaced."""
    value = text if isinstance(text, str) else str(text)
    return value if len(value) <= limit else value[:limit] + "...(truncated)"


def _context_refusal_block(result: ContextBuildingsResult) -> dict | None:
    """A DISCLOSED, bounded refusal block when the connector refused - never dropped, never
    a fabricated building. Carries the typed error class, a bounded message, the server
    correlation id, the connector-built request url, and the raw-body digest."""
    refusal = result.refusal
    if refusal is None:
        return None
    return {
        "error_type": refusal.error_type,
        "message": _bounded(refusal.message),
        "correlation_id": refusal.correlation_id,
        "request_url": refusal.request_url,
        "retrieved_at": refusal.retrieved_at,
        "raw_digest": refusal.raw_digest,
    }


def _context_layer(
    result: ContextBuildingsResult | None, site_ground: float | None
) -> dict:
    """The ``context_buildings`` layer. When no context was requested the layer is present
    and honest (``status`` ``not_requested``); when the connector refused, the buildings are
    empty and the refusal is disclosed; otherwise the buildings are assembled in the
    connector's OBJECTID order."""
    layer: dict[str, Any] = {
        "layer": CONTEXT_LAYER,
        "vertical_unit": VERTICAL_UNIT,
        "ground_datum": GROUND_DATUM_DECISION,
        "disclosures": [dict(d) for d in _CONTEXT_DISCLOSURES],
    }
    if result is None:
        layer.update(status="not_requested", buildings=[], refusal=None,
                     site_ground_elevation_ft=site_ground)
        return layer
    layer.update(
        status=result.status,
        site_ground_elevation_ft=result.site_ground_elevation_ft,
        subject_bbl=result.subject_bbl,
        crs=dict(result.crs),
        drift_signals=list(result.drift_signals),
        provenance=result.provenance(),
        refusal=_context_refusal_block(result),
        buildings=[_context_building(b, result.site_ground_elevation_ft)
                   for b in result.buildings],
    )
    return layer


# ---------------------------------------------------------------------------
# The scene assembler (pure) + a route-facing orchestrator.
# ---------------------------------------------------------------------------


def assemble_scene(
    *,
    massing_model: MassingModel,
    context_result: ContextBuildingsResult | None,
    site_ground_elevation_ft: float | None,
    correlation_id: str,
) -> dict:
    """Assemble the plan section 2.1 scene payload from a built massing truth object and a
    (possibly ``None``) fetched context result. PURE and deterministic: no I/O, no logging,
    no clock. The massing fields are carried verbatim; the context layer, the explicit
    vertical unit, the scene disclosures, and the declared ground datum (recorded in
    provenance) are added."""
    scene = massing_model.as_dict()
    scene["scene_version"] = SCENE_VERSION
    scene["correlation_id"] = correlation_id
    scene["vertical_unit"] = VERTICAL_UNIT  # DB-054 (k): explicit on the payload
    scene["layers"] = [*scene.get("layers", []), CONTEXT_LAYER]
    scene["disclosures"] = [dict(d) for d in _MASSING_DISCLOSURES]
    scene["context_buildings"] = _context_layer(context_result, site_ground_elevation_ft)
    scene["provenance"] = {
        **scene.get("provenance", {}),
        "scene": {
            "scene_version": SCENE_VERSION,
            "vertical_unit": VERTICAL_UNIT,
            "ground_datum": GROUND_DATUM_DECISION,
            "context_provenance": (
                context_result.provenance() if context_result is not None else None
            ),
        },
    }
    return scene


def build_scene_payload(
    *,
    lot_ring: object,
    proposed_massing: Mapping[str, Any] | None = None,
    generated_option: Mapping[str, Any] | None = None,
    fetch,
    envelope: object = None,
    polygon: object = None,
    site_ground_elevation_ft: float | None = None,
    subject_bbl: object = None,
    page_size: int | None = None,
    deadline=None,
    correlation_id: str,
    scenario_id: str | None = None,
    property_geometry_version_id: str | None = None,
    rule_release_id: str | None = None,
) -> dict:
    """Build the massing truth object, fetch the context buildings through the injected
    ``fetch`` seam (interactive, under the caller ``deadline`` - DB-073 (c)), and assemble
    the scene. Intended to run OFF the event loop inside the route's cancellable job. When
    neither ``envelope`` nor ``polygon`` is supplied, no context fetch is made and the layer
    is an honest ``not_requested``.

    ``fetch`` is the connector seam
    (:func:`app.connectors.building_footprints_arcgis.fetch_context_buildings`); tests inject
    an offline fake so nothing touches the network."""
    massing = build_scene_massing(
        lot_ring=lot_ring, proposed_massing=proposed_massing,
        generated_option=generated_option, scenario_id=scenario_id,
        property_geometry_version_id=property_geometry_version_id,
        rule_release_id=rule_release_id)
    context_result: ContextBuildingsResult | None = None
    if envelope is not None or polygon is not None:
        context_result = fetch(
            envelope=envelope, polygon=polygon,
            site_ground_elevation_ft=site_ground_elevation_ft, subject_bbl=subject_bbl,
            page_size=page_size, interactive=True, deadline=deadline,
            correlation_id=correlation_id)
    return assemble_scene(
        massing_model=massing, context_result=context_result,
        site_ground_elevation_ft=site_ground_elevation_ft, correlation_id=correlation_id)
