"""GET /api/v1/properties/{bbl}/study - internal read of a study SETUP (lane C,
request D-1 slice 1).

Transports the lot-choice + site-facts SETUP half of a study for one confirmed
BBL, shaped to ``packages/contracts/schemas/v1/study.schema.json``:

- ``property`` (bbl + confirmed address, null when reached by BBL only);
- ``lots`` and ``lot_selection`` - VERBATIM from B-07's study adapters
  (``app.spatial.multi_lot_site.study_lots`` / ``study_lot_selection``) for the
  default "use all" selection, so the combination status and its plain-English
  reason, and the exact statement "Based on the lots you selected - the app does
  not verify the zoning lot", are B-07's words, never re-derived here;
- ``site.facts`` - B-02/B-03 ``site_fact`` v1 documents with their measurement
  rank, label and source, carried verbatim.

It is NOT a full study.schema.json Study: a study also requires options (program,
floor-to-floor heights, goal), and the plan forbids the backend inventing those
(``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` M1-06 "no example data in real
work"; the study store "never invents option inputs ... they come from the
caller"). Options are chosen later in the flow; the web adapter composes the full
Study by adding the architect's option to this setup (request D-1 slice 1 item 2).
``document_kind`` is ``study_setup`` so the shape is explicit.

Route posture mirrors the accepted flag-gated internal reads
(``app.api.v1.condo_records`` / ``app.api.v1.rule_evaluation``):

- A NEW default-off flag ``INTERNAL_STUDY_READ_ENABLED`` (``app.config``). The
  route is ALWAYS registered but, when the flag is absent/empty/unknown, returns
  a generic ``404 Not Found`` byte-indistinguishable from an unmounted path.
  ``include_in_schema=False`` so it never appears in OpenAPI. The flag gates
  REACHABILITY; the lot choice itself is Lane B behaviour and is produced only
  when LANE_B_ENABLED is also on (``app.api.v1.study_inputs``), so production
  (neither flag set) keeps the route a 404.
- No authentication yet (service is internal/dev only).
- The BBL flows through ``normalize_bbl`` BEFORE any provider call, so a
  malformed BBL is a typed ``422`` with zero I/O.
- The study inputs come through an INJECTED provider (``get_study_inputs_provider``)
  so the tests run fully offline on recorded fixtures (the 215-16 Northern pack).
  Live city data is reached ONLY through the existing connectors behind that seam.

ZONING MATH STAYS OFF (plan / lane rule). This route carries NO allowance,
capacity, FAR or rule output: a study setup holds the user's lot selection plus
B-07's combination check and the sourced site facts, nothing computed.

CONTRACT-GUARDED BEFORE SEND. Every emitted site fact is validated against
``site_fact.schema.json`` and every lot / the lot_selection against the
``study.schema.json`` ``$defs`` before the 200 is returned; a built document that
fails is a ``500 internal_contract_error`` (an invalid 200 is impossible, the
properties-route posture). ``STUDY_READ_STATUS_STATE_MATRIX`` is the single
source of truth for every emitted (HTTP status, state) pair.
"""

from __future__ import annotations

import json
import logging
import uuid
from functools import lru_cache
from importlib import resources

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.config import internal_study_read_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.contracts.study_contracts import StudyContractError, validate_site_fact_document
from app.spatial.multi_lot_site import study_lot_selection, study_lots

from .study_inputs import (
    StudyInputs,
    StudyInputsProvider,
    StudyInputsUnavailableError,
    default_study_inputs_provider,
)

__all__ = [
    "STUDY_READ_STATUS_STATE_MATRIX",
    "get_study_inputs_provider",
    "router",
]

logger = logging.getLogger("app.api.v1.study_read")

router = APIRouter(prefix="/api/v1", tags=["study_read"])

DOCUMENT_KIND = "study_setup"

# Defense-in-depth length cap for the reflected raw_value repr in a 422 detail
# (the condo-records / proposal bounded-repr class). The repr is already
# repr()-sanitized in app.connectors.bbl; this only bounds its LENGTH.
MAX_RAW_VALUE_REPR_CHARS = 256
_RAW_VALUE_TRUNCATION_MARKER = "...[truncated]"

# Bundled canonical schemas (byte-identical to packages/contracts/schemas/v1,
# kept so by services/api/scripts/sync_contract_schemas.py). Loaded read-only via
# importlib.resources, the same package-data path app.contracts.study_contracts
# uses, so it works from a non-editable install with no packages/ sibling.
_SCHEMA_PACKAGE = "app._contract_schemas.v1"
_STUDY_SCHEMA_ID = (
    "https://github.com/martin10101/nyc-buildability/packages/contracts/schemas/v1/"
    "study.schema.json"
)

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every success is a 200 with NO
# ``state`` field (the document speaks for itself); the disabled sentinel is a
# 404 with NO state (byte-identical to an unmounted path). A malformed BBL is a
# typed 422; inputs that cannot be produced (upstream unavailable, the Lane B
# gate off, or the live fetch shell not wired yet) are a bounded 503; an
# unexpected defect is a generic 500; a built document that fails its contract
# before send is a typed 500 (an invalid 200 is impossible).
# ---------------------------------------------------------------------------
STUDY_READ_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # study-setup document
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL, no provider call
        (503, "inputs_unavailable"),  # inputs could not be produced (fail safe)
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # built document failed its contract
    }
)


def get_study_inputs_provider() -> StudyInputsProvider:
    """Dependency returning the study-inputs provider (test override point).

    The default fails safe (the live fetch shell is a later slice); tests inject
    a fixture-backed provider so the whole suite runs offline."""
    return default_study_inputs_provider


@lru_cache(maxsize=1)
def _study_defs_registry():
    """A referencing registry over the bundled study + site_fact + common schemas,
    so a study.schema.json ``$defs`` subschema resolves its $refs."""
    from referencing import Registry, Resource

    names = ("study.schema.json", "site_fact.schema.json", "common.schema.json")
    docs = [
        json.loads(resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8"))
        for name in names
    ]
    return Registry().with_resources(
        [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
    )


@lru_cache(maxsize=4)
def _study_defs_validator(ref: str):
    """A Draft 2020-12 validator for one study.schema.json ``$defs`` entry
    (e.g. ``"#/$defs/lot"``), built once from the bundle."""
    import jsonschema

    return jsonschema.Draft202012Validator(
        {"$ref": _STUDY_SCHEMA_ID + ref}, registry=_study_defs_registry()
    )


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. No
    correlation id and no body hint, so a disabled feature is indistinguishable
    from a route that does not exist (fail-safe disable)."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _capped_raw_value(raw_value_repr: str) -> str:
    if len(raw_value_repr) <= MAX_RAW_VALUE_REPR_CHARS:
        return raw_value_repr
    return raw_value_repr[:MAX_RAW_VALUE_REPR_CHARS] + _RAW_VALUE_TRUNCATION_MARKER


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the type +
    correlation id only (no str(exc)/traceback: the chain may embed untrusted
    upstream strings)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_contract_error_500(correlation_id: str) -> JSONResponse:
    """A built study-setup document failed its contract before send. An invalid
    200 is impossible; the defect is internal, so the body is generic."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "the study setup failed its contract checks before send and was not "
                "delivered; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _inputs_unavailable_503(correlation_id: str) -> JSONResponse:
    """The study inputs could not be produced (upstream unavailable, the Lane B
    gate off, or the live fetch shell not wired yet). Fail safe: no study is
    fabricated. The ``reason`` is a bounded platform token, never upstream text."""
    return _json(
        503,
        {
            "state": "inputs_unavailable",
            "message": (
                "the study setup is not available for this property right now; nothing "
                "was fabricated and this is safe to retry"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send:
    ``allow_nan=False`` rejects NaN/Infinity, and the ``ensure_ascii=False``
    utf-8 form is what Starlette renders and raises on an unpaired surrogate."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


def _build_document(canonical_bbl: str, inputs: StudyInputs) -> dict:
    """Shape the study-setup document from the domain inputs. Lots and
    lot_selection come VERBATIM from B-07's adapters; the facts are carried as
    emitted by B-02. Nothing is computed here."""
    lots = study_lots(inputs.lot_choice, inputs.site.selected_bbls)
    lot_selection = study_lot_selection(inputs.site)
    facts = [dict(fact) for fact in inputs.site_facts]
    return {
        "document_kind": DOCUMENT_KIND,
        "bbl": canonical_bbl,
        "property": {"bbl": canonical_bbl, "address": inputs.address},
        "lots": lots,
        "lot_selection": lot_selection,
        "site": {"facts": facts},
    }


def _contract_guard(document: dict) -> None:
    """Validate the study-setup document against the contract before send. Every
    site fact against site_fact.schema.json; every lot and the lot_selection
    against the study.schema.json $defs. Raises StudyContractError on any defect
    so an invalid 200 is impossible."""
    for fact in document["site"]["facts"]:
        validate_site_fact_document(fact)
    for index, lot in enumerate(document["lots"]):
        errors = sorted(
            _study_defs_validator("#/$defs/lot").iter_errors(lot),
            key=lambda err: list(err.path),
        )
        if errors:
            raise StudyContractError(
                f"lot {index} failed the study contract: {errors[0].message}",
                contract="study",
                location=f"lots/{index}",
            )
    # lot_selection is defined INLINE under properties (study.schema.json has no
    # $defs/lot_selection), so the ref points at the property subschema; its own
    # $ref to $defs/combination still resolves in the registry.
    sel_errors = sorted(
        _study_defs_validator("#/properties/lot_selection").iter_errors(
            document["lot_selection"]
        ),
        key=lambda err: list(err.path),
    )
    if sel_errors:
        raise StudyContractError(
            f"lot_selection failed the study contract: {sel_errors[0].message}",
            contract="study",
            location="lot_selection",
        )


@router.get("/properties/{bbl}/study", include_in_schema=False)
def get_study(
    bbl: str,
    provide_inputs: StudyInputsProvider = Depends(get_study_inputs_provider),  # noqa: B008
) -> JSONResponse:
    """Read the study setup (lot choice + site facts) for one BBL. Feature-flag
    gated OFF by default (INTERNAL_STUDY_READ_ENABLED), mirroring the sibling
    internal reads."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> 404 with no hint the
    # feature exists. Checked FIRST, before a correlation id is minted.
    if not internal_study_read_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 1. Validate the BBL BEFORE any provider call (typed 422; zero I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "study_read_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _json(
            422,
            {
                "state": "validation_error",
                "message": payload["message"],
                "correlation_id": correlation_id,
                "detail": {
                    "code": payload["code"],
                    "raw_value": _capped_raw_value(payload["raw_value"]),
                },
            },
            correlation_id,
        )

    canonical = normalized.canonical

    # 2. Produce the inputs through the injected provider. A typed unavailability
    #    is a bounded 503 (fail safe, nothing fabricated); any other exception is
    #    a generic 500.
    try:
        inputs = provide_inputs(canonical, correlation_id)
    except StudyInputsUnavailableError as exc:
        logger.info(
            "study_read_v1 inputs_unavailable reason=%s correlation_id=%s",
            exc.reason, correlation_id,
        )
        return _inputs_unavailable_503(correlation_id)
    except Exception:
        logger.error(
            "study_read_v1 unexpected_error stage=provide correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 3. Shape the document, contract-guard it, and guard its serialisation
    #    before send. A built document that fails the contract is a typed 500.
    try:
        document = _build_document(canonical, inputs)
        _contract_guard(document)
        _assert_json_safe(document)
    except StudyContractError:
        logger.error(
            "study_read_v1 contract_invalid correlation_id=%s", correlation_id
        )
        return _internal_contract_error_500(correlation_id)
    except Exception:
        logger.error(
            "study_read_v1 serialization_unsafe correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    return _json(200, document, correlation_id)
