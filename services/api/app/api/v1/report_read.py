"""POST /api/v1/properties/{bbl}/report - the internal report route (task M5-T151).

For one confirmed BBL it produces the full current-scope feasibility report as a
printable HTML document, built on the server from the SAME results document the
results route emits.

REUSE, NOT COPY (ruling X9 d). This route does not re-implement the request body,
the gating or the engine call: it delegates to the accepted results route
(:func:`app.api.v1.results_read.post_results`) for the whole flow - the feature
flag, the per-caller rate limit, the BBL and body validation, the injected
study-inputs provider, the engine chain and the contract guard. Every non-200 is
returned verbatim, so the report route's gating and refusals are byte-identical
to the results route's (flag off is the same 404; a malformed BBL, a refused
body, a rate-limit, an unavailable input and an internal error are the same typed
JSON). On 200 it renders the emitted results document into the report and answers
``text/html; charset=utf-8``.

IDENTITY. The running identity (borough, block, lot, district, overlay, lot
selection) is read from the emitted results document. The street address is NOT
in that document and is not reachable on this reuse path without a second call,
so the header uses the borough/block/lot display (producer report, M5-T151).

MAPS. The map connectors the map document needs (zoning features, building
footprints) are not produced on the results-inputs path, so no map document is
built here and the report is produced without maps (never an error page); the
site page states that briefly and the coverage inventory does not claim maps.
"""

from __future__ import annotations

import json
import logging
import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response

from app.drawings.report import build_report_html

from .results_read import get_results_study_inputs_provider, post_results
from .study_inputs import StudyInputsProvider

__all__ = ["router"]

logger = logging.getLogger("app.api.v1.report_read")

router = APIRouter(prefix="/api/v1", tags=["report_read"])

# A caller-supplied display address for the report title (F2): the website sends
# the confirmed address, which is not in the results document. It is accepted only
# when short and made of ordinary address characters; anything else is ignored
# (the report then titles itself with the borough/block/lot).
_ADDRESS_MAX = 120
_ADDRESS_ALLOWED = re.compile(r"^[A-Za-z0-9 \-.,'#/&]+$")


def _clean_address(raw: str | None) -> str | None:
    if not raw:
        return None
    trimmed = raw.strip()
    if not trimmed or len(trimmed) > _ADDRESS_MAX or not _ADDRESS_ALLOWED.match(trimmed):
        return None
    return trimmed


@router.post("/properties/{bbl}/report", include_in_schema=False)
async def post_report(
    request: Request,
    bbl: str,
    provide_inputs: StudyInputsProvider = Depends(get_results_study_inputs_provider),  # noqa: B008
) -> Response:
    """Run the accepted engine chain for one BBL (via the results route) and
    return the full report as HTML. Same flag, gating and refusals as the results
    route; feature-flag gated OFF by default (INTERNAL_RESULTS_ENABLED)."""
    # Delegate the entire flag/gating/engine flow to the results route. Any
    # non-200 (404 flag-off, 422, 429, 503, 500) is returned verbatim.
    results_response = await post_results(request, bbl, provide_inputs)
    if results_response.status_code != 200:
        return results_response

    correlation_id = results_response.headers.get("X-Correlation-ID")
    address = _clean_address(request.query_params.get("address"))
    try:
        document = json.loads(bytes(results_response.body))
        html = build_report_html(document, identity={"address": address})
    except Exception:
        logger.error("report_v1 render_failed correlation_id=%s", correlation_id)
        # Reuse the results route's typed internal-error refusal shape.
        from .results_read import _internal_error_500

        return _internal_error_500(correlation_id or "")

    headers = {"X-Correlation-ID": correlation_id} if correlation_id else {}
    return HTMLResponse(content=html, status_code=200, headers=headers)
