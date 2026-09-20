"""POST /api/v1/proposal-checks - proposal-conditioned rule checks (M5-T057, D-076 phase B3).

The FIRST (internal, flag-gated) HTTP seam onto the accepted B2 check engine
(:func:`app.rules.proposal_checks.check_proposal`, M5-T054). Given an editor-authored
``proposed_massing`` block plus a caller-supplied lot context and lot rule facts, it runs the
DB-034(a)/(b) input gate and the B2 engine and returns the grouped PASS / FAIL /
COULD_NOT_CHECK report (with numeric shortfalls and the could_not_check count) for the
B3-slice-2 editor UI to consume. It stores nothing and emits NO scenario document and NO
contract version (D-076-R002 / DB-034(d); BP-6): emission stays with the scenario-workspace
save path (B3 slice 2).

THIS ROUTE IS THE TRUST BOUNDARY. Every G5-recorded precondition (M5-T054 G5, BP-1..BP-7) is
enforced here, in order, fail-closed:

* BP-7 / posture - feature-flag gated OFF by default (REUSED ``INTERNAL_RULE_EVAL_ENABLED``, the
  same flag the sibling internal routes use; ``include_in_schema=False``; absent/empty/unknown ->
  a generic 404 byte-indistinguishable from an unmounted path). A bounded request body (raw-byte
  ceiling by BOUNDED STREAMING, reusing the accepted T053 primitives). This route adds NO auth
  change: authn / tenancy / per-user ownership of the supplied lot geometry arrive with the PUBLIC
  exposure packet, recorded here as a disposition, not implemented (the route is unreachable
  without the internal flag).
* BP-2 - ``scenario_label`` / ``proposal_id`` are length-capped and charset-restricted at the
  boundary (typed refusal); they are copied into every result and rendered by B3. The same label
  discipline is applied to ``proposed_massing.exterior_walls[].id`` (M5-T061 / DB-039(h)) so a
  block wall id and a street line's ``wall_id`` - which share one identity space - cannot diverge.
* BP-4 - ROUTE-LEVEL practical caps TIGHTER than the B2 library ceilings so the documented
  worst-case wall-by-segment distance-test product stays well under ~1e6 (see the arithmetic on
  :data:`ROUTE_MAX_EXTERIOR_WALLS` below). The O(n^2) outline-simplicity work is ALSO route-capped
  ([ORCH-CORRECTED per G5-F2]): :data:`ROUTE_MAX_TOTAL_OUTLINE_POSITIONS` bounds the total outline
  positions far below the inherited DB-034(a) budget, and the two CPU-bound validation/check calls
  run off the event loop via ``run_in_threadpool`` so a worst-case request cannot stall the worker
  process's other endpoints.
* BP-5 - the mapped ``lot_rule_facts`` are validated against the evaluator's OWN declared input
  vocabulary before anything is fed: a bad VALUE TYPE, a string value outside an enum-constrained
  input's declared DOMAIN, OR a numeric value outside an input's declared numeric bounds
  (minimum / maximum / exclusive_* - both DERIVED from the registry's rule input specs, never an
  invented list or limit; M5-T061 / DB-039(d)), is a typed 422 naming the exact field, refused
  BEFORE the engine runs. That whole ``lot_rule_facts`` discipline (the boundary label primitives,
  the value-type table, the fact-key bound, and the registry-derived enum/numeric checks) lives in
  the sibling :mod:`app.api.v1._proposal_fact_domains` module - extracted at the M5-T061 seam once
  the numeric-bound derivation crossed the route's modularity tier; the route imports every name it
  needs and its public surface is unchanged. An UNMAPPED key is never fed and is surfaced in the
  response's ``unmapped_lot_facts`` (the B2 engine drops it - no silent dict merge).
* BP-1 - the ONLY engine entry called is :func:`check_proposal` (never ``derive_proposal``
  directly), so the B2 wiring preconditions (list ceilings, coordinate/area finiteness) all apply.
* BP-3 - EVERY error path length-caps any embedded value: a propagated
  ``ProposalCheckError`` / ``ProposalDerivationError`` / ``ProposedMassingError`` detail (including
  the B0 validator's uncapped bad-vertex ``repr`` from G5-3) is passed through
  :func:`_bounded_message` before it can reach a client, and the refusal ``field`` key is capped
  by :func:`_bounded_field` on every response AND log path ([ORCH-CORRECTED per G3-F1/G5-F1/G5-F4]).
  The lot-side caller ids (``lot.lot_line_segments[].id`` / ``lot.street_lines[].wall_id``) are
  bounded at the boundary with the BP-2 label discipline, and the caller-supplied provenance /
  attestation objects and ``lot_rule_facts`` KEYS are size/charset-bounded too, so no unbounded
  caller string can ride a refusal field, a 200-path provenance echo, or a log record.

Every non-disabled response carries ``X-Correlation-ID``. The exact emitted (HTTP status, state)
pairs are the single source of truth :data:`PROPOSAL_CHECKS_STATUS_STATE_MATRIX`; the 200 report
carries NO ``state`` (pair ``(200, None)``), mirroring the accepted sibling routes.
"""

from __future__ import annotations

import functools
import json
import logging
import uuid
from typing import Any, cast

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

# BP-5 caller-fact vocabulary discipline (extracted at the M5-T061 seam - DB-039). The route shares
# these names so a single _FieldRefusal identity crosses both modules (the handler's ``except``
# must catch refusals raised inside the extracted validators too), and the boundary label + fact
# checks stay one cohesive responsibility. NOTHING in that module imports the route -> no cycle.
from app.api.v1._proposal_fact_domains import (
    MAX_LABEL_LEN,
    _FieldRefusal,
    _require_label,
    _validate_lot_rule_fact_domains,
    _validate_lot_rule_fact_keys,
    _validate_lot_rule_fact_types,
)

# Reuse the accepted T053 request-boundary primitives (read-only reuse per the packet): the raw
# body ceiling + bounded-streaming accumulator, the Content-Length fast-path parser, and the
# 400-char refusal-message cap. Sharing them keeps the two sibling internal routes' size/message
# discipline byte-identical rather than forking a second copy.
from app.api.v1.proposal_validation import (
    MAX_BODY_BYTES,
    _bounded_message,
    _declared_content_length,
    _read_body_within_ceiling,
)
from app.config import internal_rule_eval_enabled
from app.rules.proposal_checks import (
    ProposalCheckError,
    check_proposal,
)
from app.rules.registry import RuleRegistry
from app.scenario.derivation import (
    AttestedStreetLine,
    LotContext,
    LotLineSegment,
    ProposalDerivationError,
)
from app.scenario.proposal import ProposedMassingError

# _total_position_count is the gate's OWN O(n) position counter (read-only reuse, the same
# private-reuse pattern as the T053 body primitives above): the route's BP-4 outline cap must
# count positions EXACTLY the way the DB-034(a) budget does, never a second parallel definition.
from app.scenario.proposal_input_gate import (
    MAX_TOTAL_VERTICES,
    _total_position_count,
    validate_proposed_massing_input,
)

__all__ = [
    "MAX_BODY_BYTES",
    "MAX_FIELD_LEN",
    "MAX_LABEL_LEN",
    "MAX_PROVENANCE_BYTES",
    "PROPOSAL_CHECKS_STATUS_STATE_MATRIX",
    "ROUTE_MAX_EXTERIOR_WALLS",
    "ROUTE_MAX_LOT_LINE_SEGMENTS",
    "ROUTE_MAX_STREET_LINES",
    "ROUTE_MAX_TOTAL_OUTLINE_POSITIONS",
    "get_proposal_check_registry",
    "router",
]

logger = logging.getLogger("app.api.v1.proposal_checks_api")

router = APIRouter(prefix="/api/v1", tags=["proposal_checks"])

# --- BP-3: refusal-field + provenance-object bounds ([ORCH-CORRECTED per G3-F1/G5-F1]) ---------
#: Hard cap on the refusal ``field`` value on EVERY response and log path. A legitimate field is
#: a dotted path of literal segments, integer indexes, and (route-bounded) short ids - it can
#: never legitimately approach this length, so anything longer is truncated with a marker before
#: it can reach a client or a log record (the G3-F1/G5-F1 uncapped-reflection class).
MAX_FIELD_LEN = 200
#: Serialized-size ceiling for the small caller-supplied objects the engine republishes verbatim
#: into results (``lot.area_provenance`` -> ``provided_provenance``; each street line's
#: ``attestation``): a large/deeply nested blob is refused typed here (G5-F1 200-path exposure).
MAX_PROVENANCE_BYTES = 2048

# --- BP-4: route-level compute caps, TIGHTER than the B2 library ceilings ---------------------
# The dominating cost inside the single derive_proposal call is the wall x lot-line and
# wall x street-line distance tests (M5-T054 G5-2). The B2 library ceilings admit
# MAX_EXTERIOR_WALLS(4000) x (MAX_LOT_LINE_SEGMENTS(1000) + MAX_STREET_LINES(500)) = 6,000,000
# segment tests. These route caps bound the SAME product at
#     ROUTE_MAX_EXTERIOR_WALLS(500) x (ROUTE_MAX_LOT_LINE_SEGMENTS(800)
#                                      + ROUTE_MAX_STREET_LINES(400))
#     = 500 x 1200 = 600,000 wall-by-segment distance tests  (< ~1e6). This is a FIXED
# worst-case OPERATION-COUNT bound the route caps impose on the derivation's dominating loop,
# independent of the payload's contents - a bounded compute budget, not a wall-clock/timing
# guarantee (throughput depends on the host). Each cap is strictly below its B2 counterpart.
#
# [ORCH-CORRECTED per G5-F2] The O(n^2) outline-SIMPLICITY pass is a SECOND compute surface the
# product above does not cover, and this route runs the block validation TWICE (the explicit
# input-gate call, then check_proposal's own internal validate) - under the inherited DB-034(a)
# budget alone (MAX_TOTAL_VERTICES = 5000) that admitted ~2 x 5000^2/2 = 2.5e7 pair tests
# (~17 s measured). ROUTE_MAX_TOTAL_OUTLINE_POSITIONS caps the total outline positions at 1200,
# counted with the gate's OWN counter, so the simplicity work is bounded at
#     2 passes x 1200 x 1199 / 2  ~= 1.44e6 pair tests.
# The route's TOTAL documented worst case is therefore ~600,000 + ~1,440,000 ~= 2.0e6 bounded
# operations (~12x tighter than the inherited budget's simplicity term alone), and BOTH CPU-bound
# calls run off the event loop via run_in_threadpool so even the at-cap case cannot stall the
# worker's other endpoints.
ROUTE_MAX_EXTERIOR_WALLS = 500
ROUTE_MAX_LOT_LINE_SEGMENTS = 800
ROUTE_MAX_STREET_LINES = 400
ROUTE_MAX_TOTAL_OUTLINE_POSITIONS = 1200

# Import-time guard (same pattern as the extracted BP-5 fact-type table): the route's outline cap
# must stay STRICTLY below the inherited DB-034(a) budget or the "tighter than the library ceiling"
# claim silently rots.
if ROUTE_MAX_TOTAL_OUTLINE_POSITIONS >= MAX_TOTAL_VERTICES:
    raise ValueError(
        "ROUTE_MAX_TOTAL_OUTLINE_POSITIONS must be strictly below the inherited "
        f"MAX_TOTAL_VERTICES ({MAX_TOTAL_VERTICES})"
    )

# --- (status, state) matrix (single source of truth) ------------------------------------------
PROPOSAL_CHECKS_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # grouped proposal-check report (NO state; NO derived scenario document)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (413, "payload_too_large"),  # raw body over MAX_BODY_BYTES, before parse
        (422, "validation_error"),  # malformed/non-finite/non-encodable body OR typed refusal
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)


def get_proposal_check_registry() -> RuleRegistry | None:
    """The rule registry the checks evaluate against. Returns ``None`` so the route loads the
    production registry (via :func:`_effective_registry`); tests monkeypatch this module
    attribute to inject a synthetic fixture registry. NOT a client-controlled input - it has no
    request binding."""
    return None


#: Lazily-loaded, cached production registry (mirrors the B2 engine's own lazy load). Held here so
#: the route can resolve the engine's effective registry ONCE - to derive the BP-5 domain
#: vocabulary from AND to pass to :func:`check_proposal` - never loading it twice.
_PRODUCTION_REGISTRY: RuleRegistry | None = None


def _effective_registry() -> RuleRegistry:
    """The registry the engine will actually evaluate against: the test-injected one when
    :func:`get_proposal_check_registry` supplies it, else the lazily-loaded, cached production
    registry. Resolving it HERE (rather than passing ``None`` to :func:`check_proposal`) lets the
    route validate ``lot_rule_facts`` domains against the SAME accepted vocabulary the engine uses
    and then call :func:`check_proposal` exactly once with it (BP-1 unchanged).

    DB-039(i): this resolves the lazy global ON THE EVENT LOOP and MUST NOT be called inside a
    :func:`run_in_threadpool` hop - a first-touch race between concurrent worker threads could
    otherwise load and cache the production registry twice."""
    global _PRODUCTION_REGISTRY
    injected = get_proposal_check_registry()
    if injected is not None:
        return injected
    if _PRODUCTION_REGISTRY is None:
        _PRODUCTION_REGISTRY = RuleRegistry().load()
    return _PRODUCTION_REGISTRY


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path (fail-safe disable): no
    correlation id, no body hint that the feature exists."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _bounded_field(field: str | None) -> str | None:
    """BP-3 ([ORCH-CORRECTED per G3-F1/G5-F1]): hard-cap a refusal ``field`` before it reaches a
    client OR a log record. Legitimate dotted field paths are short; the truncation marker names
    the original length only (never more of the value)."""
    if field is None or len(field) <= MAX_FIELD_LEN:
        return field
    return field[:MAX_FIELD_LEN] + f"...<truncated; {len(field)} chars total>"


def _validation_error(
    message: str, correlation_id: str, *, field: str | None = None
) -> JSONResponse:
    """Typed (422, "validation_error") with a BOUNDED reason (BP-3), optionally naming the exact
    ``field`` (itself bounded by :func:`_bounded_field` - the G3-F1/G5-F1 class). Never a
    traceback / path / secret / internal string."""
    body: dict[str, object] = {
        "state": "validation_error",
        "message": _bounded_message(message),
        "correlation_id": correlation_id,
    }
    if field is not None:
        body["field"] = _bounded_field(field)
    return _json(422, body, correlation_id)


def _payload_too_large(correlation_id: str) -> JSONResponse:
    return _json(
        413,
        {
            "state": "payload_too_large",
            "message": f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the correlation id only (never
    ``str(exc)`` / a traceback: the request may carry untrusted strings)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _to_point(value: Any) -> Any:
    """A JSON coordinate arrives as a 2-element list; hand it on as a tuple so it matches the
    accepted LotContext shape. Any other shape is passed through unchanged for the B2 engine's own
    finiteness/shape refusal (which names the exact dotted field)."""
    if isinstance(value, list):
        return tuple(value)
    return value


def _require_bounded_object(value: dict, field: str) -> dict:
    """Size-bound a small caller-supplied object the engine republishes verbatim into results
    ([ORCH-CORRECTED per G5-F1]): refuse typed when its strict-JSON serialization exceeds
    MAX_PROVENANCE_BYTES. Never echoes the value (only the byte count)."""
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        raise _FieldRefusal(f"{field} is not strict-JSON serializable", field=field) from None
    if len(encoded) > MAX_PROVENANCE_BYTES:
        raise _FieldRefusal(
            f"{field} exceeds MAX_PROVENANCE_BYTES ({MAX_PROVENANCE_BYTES}); "
            f"got {len(encoded)} bytes",
            field=field,
        )
    return value


def _validate_exterior_wall_ids(proposed_massing: dict) -> None:
    """DB-039(h): a ``proposed_massing.exterior_walls[].id`` shares the SAME identity space as a
    street line's ``wall_id`` (already charset-bound at this boundary), so a wall id that IS a
    string gets the BP-2 label discipline here - otherwise a matching pair could DIVERGE (a wall id
    carrying markup would round-trip while the equal street ``wall_id`` is refused). A non-string /
    missing id is left to the B0 validator's own shape refusal (which names the exact field), and
    the gate's wider 512-char id ceiling remains upstream. Pre-existing block ids outside the label
    charset therefore now refuse at THIS internal (flag-gated) route - no public caller exists yet.
    Cheap O(walls) over the already-count-capped list; the refusal echoes the id's length only."""
    walls = proposed_massing.get("exterior_walls")
    if not isinstance(walls, list):
        return
    for idx, wall in enumerate(walls):
        if isinstance(wall, dict) and isinstance(wall.get("id"), str):
            _require_label(wall["id"], f"proposed_massing.exterior_walls[{idx}].id")


def _build_lot_context(lot: object) -> LotContext:
    """Construct a :class:`LotContext` from the request ``lot`` object, DEFENSIVELY: the outer
    shapes are checked here, and ([ORCH-CORRECTED per G3-F1/G5-F1]) the caller-supplied ids and
    republished objects are BOUNDED here - `lot.lot_line_segments[].id` / `street_lines[].wall_id`
    get the BP-2 label discipline (they ride engine field paths, 200-path provenance ids, and
    logs), and `area_provenance` / `attestation` get the serialized-size ceiling. Coordinate/area
    finiteness and the list-size ceilings stay with :func:`check_proposal`'s own preconditions
    (BP-1), so the deep refusals carry the engine's exact dotted fields."""
    if not isinstance(lot, dict):
        raise _FieldRefusal("lot must be an object", field="lot")
    # The values are untrusted, dynamic JSON. check_proposal enforces the REAL runtime contract
    # (list ceilings, coordinate/area finiteness, id types) via its BP-1 wiring preconditions and
    # derivation; here we only shape the outer object, so the scalars stay dynamic.
    lot = cast("dict[str, Any]", lot)
    area_provenance = lot.get("area_provenance", {})
    if not isinstance(area_provenance, dict):
        raise _FieldRefusal(
            "lot.area_provenance must be an object", field="lot.area_provenance"
        )
    _require_bounded_object(area_provenance, "lot.area_provenance")
    lot_line_raw = lot.get("lot_line_segments", [])
    if not isinstance(lot_line_raw, list):
        raise _FieldRefusal(
            "lot.lot_line_segments must be an array", field="lot.lot_line_segments"
        )
    street_raw = lot.get("street_lines", [])
    if not isinstance(street_raw, list):
        raise _FieldRefusal("lot.street_lines must be an array", field="lot.street_lines")

    segments = []
    for idx, seg in enumerate(lot_line_raw):
        if not isinstance(seg, dict):
            raise _FieldRefusal(
                f"lot.lot_line_segments[{idx}] must be an object",
                field=f"lot.lot_line_segments[{idx}]",
            )
        seg = cast("dict[str, Any]", seg)
        # [ORCH-CORRECTED per G3-F1/G5-F1]: the id rides engine refusal field paths, 200-path
        # provenance ids, and log records - BP-2 label discipline, refused typed here.
        seg_id = _require_label(seg.get("id"), f"lot.lot_line_segments[{idx}].id")
        segments.append(
            LotLineSegment(
                id=seg_id,
                start=_to_point(seg.get("start")),
                end=_to_point(seg.get("end")),
            )
        )
    streets = []
    for idx, line in enumerate(street_raw):
        if not isinstance(line, dict):
            raise _FieldRefusal(
                f"lot.street_lines[{idx}] must be an object",
                field=f"lot.street_lines[{idx}]",
            )
        line = cast("dict[str, Any]", line)
        attestation = line.get("attestation", {})
        if not isinstance(attestation, dict):
            raise _FieldRefusal(
                f"lot.street_lines[{idx}].attestation must be an object",
                field=f"lot.street_lines[{idx}].attestation",
            )
        _require_bounded_object(attestation, f"lot.street_lines[{idx}].attestation")
        # [ORCH-CORRECTED per G3-F1/G5-F1]: same BP-2 discipline as the lot-line ids above.
        wall_id = _require_label(line.get("wall_id"), f"lot.street_lines[{idx}].wall_id")
        streets.append(
            AttestedStreetLine(
                wall_id=wall_id,
                start=_to_point(line.get("start")),
                end=_to_point(line.get("end")),
                attestation=attestation,
            )
        )
    return LotContext(
        area_sq_ft=cast(float, lot.get("area_sq_ft")),
        area_provenance=area_provenance,
        lot_line_segments=tuple(segments),
        street_lines=tuple(streets),
    )


def _enforce_route_caps(proposed_massing: dict, lot: dict) -> None:
    """BP-4: refuse a payload whose wall / lot-line / street-line counts exceed the route caps,
    with a cheap O(1) ``len`` on each already-parsed list, BEFORE the gate or any derivation. A
    typed refusal names the exact cap. Non-list fields are left for the shape refusals downstream.
    """
    walls = proposed_massing.get("exterior_walls")
    if isinstance(walls, list) and len(walls) > ROUTE_MAX_EXTERIOR_WALLS:
        raise _FieldRefusal(
            f"proposed_massing.exterior_walls has {len(walls)} entries, above the route cap "
            f"ROUTE_MAX_EXTERIOR_WALLS ({ROUTE_MAX_EXTERIOR_WALLS})",
            field="proposed_massing.exterior_walls",
        )
    lot_lines = lot.get("lot_line_segments")
    if isinstance(lot_lines, list) and len(lot_lines) > ROUTE_MAX_LOT_LINE_SEGMENTS:
        raise _FieldRefusal(
            f"lot.lot_line_segments has {len(lot_lines)} entries, above the route cap "
            f"ROUTE_MAX_LOT_LINE_SEGMENTS ({ROUTE_MAX_LOT_LINE_SEGMENTS})",
            field="lot.lot_line_segments",
        )
    streets = lot.get("street_lines")
    if isinstance(streets, list) and len(streets) > ROUTE_MAX_STREET_LINES:
        raise _FieldRefusal(
            f"lot.street_lines has {len(streets)} entries, above the route cap "
            f"ROUTE_MAX_STREET_LINES ({ROUTE_MAX_STREET_LINES})",
            field="lot.street_lines",
        )
    # [ORCH-CORRECTED per G5-F2]: bound the O(n^2) outline-simplicity surface too, counted with
    # the gate's OWN counter (an O(n) len-sum - cheap), BEFORE any validation pass runs.
    total_positions = _total_position_count(proposed_massing)
    if total_positions > ROUTE_MAX_TOTAL_OUTLINE_POSITIONS:
        raise _FieldRefusal(
            f"proposed_massing outlines carry {total_positions} total positions, above the "
            f"route cap ROUTE_MAX_TOTAL_OUTLINE_POSITIONS ({ROUTE_MAX_TOTAL_OUTLINE_POSITIONS})",
            field="proposed_massing",
        )


@router.post("/proposal-checks", include_in_schema=False)
async def post_proposal_checks(request: Request) -> JSONResponse:
    """Run the proposal-conditioned rule checks over an editor payload. Feature-flag gated OFF by
    default (reuses INTERNAL_RULE_EVAL_ENABLED), mirroring the sibling internal routes."""
    # BP-7 (fail-safe disable): absent/unknown flag -> generic 404 with no hint the feature
    # exists. Checked FIRST, before a correlation id is minted or the body is read.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # BP-7 (bounded body) - raw size ceiling BEFORE parsing, via the reused bounded-streaming
    # accumulator: a declared Content-Length over the ceiling is an immediate 413 fast path, but
    # the body is then accumulated chunk-by-chunk and refused the instant the aggregate exceeds
    # MAX_BODY_BYTES, so a chunked / absent-Content-Length body is caught too and nothing is ever
    # buffered beyond the ceiling.
    declared_length = _declared_content_length(request)
    if declared_length is not None and declared_length > MAX_BODY_BYTES:
        logger.info(
            "proposal_checks_v1 payload_too_large declared_content_length=%d correlation_id=%s",
            declared_length, correlation_id,
        )
        return _payload_too_large(correlation_id)
    raw, too_large = await _read_body_within_ceiling(request.stream(), MAX_BODY_BYTES)
    if too_large:
        logger.info(
            "proposal_checks_v1 payload_too_large streamed_over_ceiling max_bytes=%d "
            "correlation_id=%s",
            MAX_BODY_BYTES, correlation_id,
        )
        return _payload_too_large(correlation_id)

    # Parse. ANY parse failure (invalid JSON, or a body too deeply nested to parse) is the
    # caller's fault -> a typed 422, never an unhandled raise.
    if not raw or not raw.strip():
        return _validation_error("request body must be a JSON object", correlation_id)
    try:
        body = json.loads(raw)
    except Exception:
        return _validation_error(
            "request body is not valid JSON (or is too deeply nested to parse)", correlation_id
        )
    if not isinstance(body, dict):
        return _validation_error("request body must be a JSON object", correlation_id)

    # Strict-JSON + renderer-parity guard: NaN/Infinity (json.loads accepts them) or a
    # non-encodable string (an unpaired surrogate the ensure_ascii=False renderer would raise on
    # mid-response) is refused here, with the SAME encoder settings the response renderer uses, so
    # the guard and the renderer can never disagree and no malformed value can reach the engine or
    # the digest inside the report.
    try:
        json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        return _validation_error(
            "request body is not strict-JSON serializable (NaN/Infinity) or contains "
            "non-encodable text (an unpaired surrogate)",
            correlation_id,
        )

    # Boundary field extraction + the BP-2 / BP-4 / BP-5-type refusals, each typed and field-named.
    # (The heavier O(n^2) input gate and _build_lot_context are deferred to AFTER the cheap
    # registry-derived domain/bounds check below - DB-039(e).)
    try:
        proposed_massing = body.get("proposed_massing")
        if not isinstance(proposed_massing, dict):
            raise _FieldRefusal(
                "proposed_massing must be an object", field="proposed_massing"
            )
        lot = body.get("lot")
        if not isinstance(lot, dict):
            raise _FieldRefusal("lot must be an object", field="lot")
        lot_rule_facts = body.get("lot_rule_facts", {})
        if not isinstance(lot_rule_facts, dict):
            raise _FieldRefusal("lot_rule_facts must be an object", field="lot_rule_facts")

        scenario_label = _require_label(body.get("scenario_label"), "scenario_label")
        proposal_id_raw = body.get("proposal_id")
        proposal_id = (
            None if proposal_id_raw is None
            else _require_label(proposal_id_raw, "proposal_id")
        )

        _enforce_route_caps(proposed_massing, lot)  # BP-4 (cheap, before any heavy work)
        _validate_exterior_wall_ids(proposed_massing)  # BP-2/DB-039(h) wall-id charset alignment
        _validate_lot_rule_fact_keys(lot_rule_facts)  # BP-2 discipline on keys ([ORCH-CORRECTED])
        _validate_lot_rule_fact_types(lot_rule_facts)  # BP-5 (mapped value types)
    except _FieldRefusal as exc:
        logger.info("proposal_checks_v1 refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(exc.message, correlation_id, field=exc.field)

    # BP-5 (domains + bounds) / DB-039(e): resolve the engine's effective registry ONCE and run the
    # CHEAP registry-derived enum-domain + numeric-bound check immediately after the value-type
    # check and BEFORE the expensive O(n^2) input gate, so a fact outside the registry's OWN
    # declared vocabulary refuses without paying for the gate. DB-039(i): _effective_registry
    # resolves the lazy global HERE, on the event loop, and NEVER inside a run_in_threadpool hop.
    # Resolution can only fail on a genuine internal defect (e.g. a missing ruleset dir) -> a
    # generic 500, never a client-shaped error (recorded at this new, earlier position).
    try:
        registry = _effective_registry()
    except Exception:
        logger.error("proposal_checks_v1 registry_unavailable correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
    try:
        _validate_lot_rule_fact_domains(lot_rule_facts, registry)
    except _FieldRefusal as exc:
        logger.info("proposal_checks_v1 domain_refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(exc.message, correlation_id, field=exc.field)

    # BP-7/BP-3: the reused DB-034(a)/(b) input gate hardens the untrusted block (global vertex
    # budget + string ceilings) THEN runs the accepted B0 validator; a refusal is a typed
    # ProposedMassingError naming the exact field with a bounded message. _build_lot_context shapes
    # the lot object (and bounds its caller ids/objects). Both run AFTER the cheap domain check.
    # [ORCH-CORRECTED per G5-F2]: CPU-bound O(n^2) work runs OFF the event loop.
    try:
        await run_in_threadpool(validate_proposed_massing_input, proposed_massing)
        lot_context = _build_lot_context(lot)
    except _FieldRefusal as exc:
        logger.info("proposal_checks_v1 lot_refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(exc.message, correlation_id, field=exc.field)
    except ProposedMassingError as exc:
        # From the input gate / B0 validator (includes the G5-3 uncapped bad-vertex repr class):
        # BP-3 caps the detail via _bounded_message.
        logger.info("proposal_checks_v1 block_refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(str(exc), correlation_id, field=exc.field)

    # BP-1: the ONLY engine entry, called EXACTLY ONCE, with that same effective registry. BP-3:
    # every propagated error detail is length-capped before it reaches the client; an unexpected
    # defect is a generic 500 (no str(exc)/traceback leak).
    # [ORCH-CORRECTED per G5-F2]: the CPU-bound engine call runs OFF the event loop.
    try:
        report = await run_in_threadpool(
            functools.partial(
                check_proposal,
                proposed_massing,
                lot_context,
                lot_rule_facts,
                scenario_label=scenario_label,
                proposal_id=proposal_id,
                registry=registry,
            )
        )
    except ProposalCheckError as exc:  # a BP-1 wiring precondition (list ceiling / finiteness)
        logger.info("proposal_checks_v1 precondition_refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(str(exc), correlation_id, field=exc.field)
    except (ProposalDerivationError, ProposedMassingError) as exc:  # degenerate/invalid geometry
        logger.info("proposal_checks_v1 derivation_refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(str(exc), correlation_id, field=exc.field)
    except Exception:
        logger.error("proposal_checks_v1 unexpected_error stage=check correlation_id=%s",
                     correlation_id)
        return _internal_error_500(correlation_id)

    # BP-6 / DB-034(d): the response is the grouped check report ONLY - no scenario document, no
    # contract version, no derived-record emission (emission stays with the B3 slice-2 save path).
    document = report.as_dict()
    document["correlation_id"] = correlation_id
    try:  # defense in depth: the body was already proven strict-JSON above
        json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        logger.error("proposal_checks_v1 serialization_unsafe correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
    return _json(200, document, correlation_id)
