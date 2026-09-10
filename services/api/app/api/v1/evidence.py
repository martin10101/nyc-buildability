"""GET /api/v1/properties/{bbl}/evidence - internal evidence / provenance trail
(task M5-T013).

Surfaces the provenance trail ALREADY carried by the accepted profile /
rule_evaluation documents so a user can see WHERE every number came from and WHAT
is (not) legally settled. Posture mirrors the accepted M5-T003 rule-evaluation
route exactly:

- Feature-flag gated OFF by default: reachable ONLY when the EXISTING
  ``INTERNAL_RULE_EVAL_ENABLED`` flag is an explicit true token (it surfaces that
  route's trail verbatim, so it REUSES that flag - app.config is NOT modified and
  NO new flag is added). Absent/empty/unknown -> a generic ``404 Not Found``
  byte-indistinguishable from an unmounted path (no correlation header, no hint
  the feature exists). ``include_in_schema=False`` so it never appears in OpenAPI.
- No authentication yet (service is internal/dev only, must not be public).

TRANSPORT, NEVER INTERPRET. It rebuilds the profile AND its rule_evaluation
SERVER-SIDE over the SAME injected seams the accepted routes use
(``get_pluto_fetcher`` -> ``build_property_profile`` -> ``evaluate_property`` ->
``serialize_rule_evaluation``, with ``get_spatial_substrate_provider``), then
ASSEMBLES a versioned ``evidence`` @ 1.0.0 document from what those already-
validated documents carry: every profile provenance record, every rule citation
with its own source-snapshot provenance, the input provenance for the evaluated
inputs, and a per-claim DRAFT-vs-Verified status. Every material value is
transported VERBATIM (a deep copy); nothing is recomputed, re-evaluated,
rewritten, or summarised in a meaning-changing way. It adds NO new legal rule
(not G6-blocked).

BODY-LESS by design: only the ``bbl`` path parameter, so the untrusted-input
surface is exactly zero (M5-T012 accepted a body and the gate wave found two
blocking defects in that boundary).

HONEST ABOUT GAPS: an absent / N-A / conflicting / review-needed source is a TYPED
marker carrying a transported reason, never silently omitted or invented; a thin
trail is a NORMAL 200 typed document. NEVER VERIFIED unless the source literally
says so (:func:`_verification_status`); the draft contract structurally excludes
``verified`` today, so every server-authored claim is ``draft`` and
``not_verified_disclaimer`` is carried verbatim (scope in ``verification_scope_note``).

FAIL-CLOSED (applying M5-T012's gate findings up front): the rebuild, assembly and
final-serialisation stages each sit inside an exception guard, so no unhandled
raise escapes as an untyped text/plain 500 (M5-T012 G1/G5 HIGH-1).
:func:`_assert_json_safe` runs BOTH ``json.dumps(doc, allow_nan=False)`` and
``json.dumps(doc, ensure_ascii=False, allow_nan=False).encode('utf-8')`` before
send - they disagree about unpaired surrogates and the renderer uses the second
(M5-T012 G5 BLOCKING-1) - and fails closed to a typed 500.

``STATUS_STATE_MATRIX`` below is the single source of truth for every emitted
(HTTP status, state) pair; it equals the mirrored rule-evaluation route's emitted
set (all internal-document defects collapse into the shared
``internal_contract_error`` 500 pair), so it introduces NO new pair.
"""

from __future__ import annotations

import copy
import json
import logging
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.v1.properties import (
    _DEFAULT_ERROR_STATUS,
    _ERROR_STATUS,
    PlutoFetcher,
    get_pluto_fetcher,
)
from app.api.v1.rule_evaluation import (
    SpatialSubstrateProvider,
    get_spatial_substrate_provider,
)
from app.config import internal_rule_eval_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.pluto_soda import DATASET_ID, SOURCE_ID, PlutoConnectorError
from app.profile.builder import build_property_profile
from app.profile.contract import (
    ContractValidationError,
    UnsupportedContractVersionError,
    validate_profile,
)
from app.rules.integration import evaluate_property
from app.rules.response import (
    RuleEvaluationContractError,
    serialize_rule_evaluation,
    validate_rule_evaluation_document,
)

__all__ = ["EVIDENCE_CONTRACT_VERSION", "STATUS_STATE_MATRIX", "router"]

logger = logging.getLogger("app.api.v1.evidence")

router = APIRouter(prefix="/api/v1", tags=["evidence"])

# Version of THIS endpoint's assembled evidence document. It is a route-local
# transport shape (it embeds already-validated canonical sub-documents verbatim),
# NOT a competing packages/contracts schema, so it is versioned here rather than
# forking a shared contract.
EVIDENCE_CONTRACT_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every emission path below is
# enumerated here; it equals the SET the rule-evaluation route this endpoint
# mirrors actually emits. The three internal-defect branches (rebuilt profile
# contract failure, rebuilt rule_evaluation contract failure, and the assembled
# document failing its serialisation safety check before send) all collapse into
# the shared ``internal_contract_error`` 500 pair, so this matrix introduces NO
# status/state pair the mirrored route does not already document.
# ---------------------------------------------------------------------------
STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # evidence document (serialisation-checked before send)
        (422, "validation_error"),  # malformed BBL, no connector call
        (404, "no_match"),  # valid BBL, no PLUTO record (a result)
        (502, "schema_drift"),  # dataset contract breakage
        (503, "rate_limited"),  # SODA throttling after retry budget
        (503, "source_unavailable"),  # SODA outage after retry budget
        (504, "timeout"),  # SODA timeout after retry budget
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # a built document failed its contract
    }
)

# Server-authored verification vocabulary. NEVER 'verified' unless the underlying
# accepted document literally says so (see _verification_status).
_VERIFICATION_DRAFT = "draft"
_VERIFICATION_VERIFIED = "verified"

# Typed evidence-completeness markers (honest classification of an ALREADY-present
# machine-readable outcome; never a new legal fact).
_COMPLETENESS_COMPLETE = "complete"
_COMPLETENESS_THIN = "thin"
_COMPLETENESS_CONFLICTING = "conflicting"
_COMPLETENESS_PROFESSIONAL_REVIEW = "professional_review_required"

# Typed gap-marker kinds (a source that is absent / N-A / needs a human / conflicts
# is NAMED, never silently dropped).
_GAP_NOT_AVAILABLE = "not_available"
_GAP_NOT_APPLICABLE = "not_applicable"
_GAP_PROFESSIONAL_REVIEW = "professional_review_required"
_GAP_DATA_CONFLICT = "data_conflict"

_VERIFICATION_SCOPE_NOTE = (
    "Verification status in this document is SERVER-AUTHORED and derived solely "
    "from the accepted rule_evaluation coverage vocabulary, which structurally "
    "excludes 'verified' for draft-integration results, so every server-authored "
    "claim here is 'draft'. Free-prose text transported VERBATIM inside a citation "
    "quote may itself contain the word 'Verified'; that transported text is never "
    "a server-authored verification status and never up-labels a claim (a blanket "
    "token scan is falsifiable and free prose cannot be caught by value equality - "
    "M5-T012 reviewer finding, documented rather than chased)."
)


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. Carries
    NO correlation id and NO body hint, so a disabled feature is indistinguishable
    from a route that does not exist (fail-safe production disable)."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the type +
    correlation id only (no str(exc)/traceback: the chain may embed untrusted
    upstream strings - M1-T002 G5 F5 payload-only logging policy)."""
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
    """Documented typed 500 for a built document (rebuilt profile, rebuilt
    rule_evaluation, or the assembled evidence document) that FAILED its
    canonical-contract or serialisation-safety check before send. A document that
    does not honor its contract is an internal defect - an invalid 200 is
    impossible - never a raw 500 stack."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "an internal document failed canonical-contract or serialisation "
                "validation and was not sent; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _verification_status(coverage_status: object) -> str:
    """Server-authored per-claim status. 'verified' ONLY when the underlying
    accepted document's coverage_status is literally 'verified' (case-insensitive)
    - impossible in the never-Verified draft rule_evaluation contract today - and
    'draft' in every other case. This function is the ONLY place a claim can be
    labelled verified, and it can only echo what the source already says."""
    if isinstance(coverage_status, str) and coverage_status.strip().lower() == "verified":
        return _VERIFICATION_VERIFIED
    return _VERIFICATION_DRAFT


def _completeness_marker(rule_evaluation: dict) -> str:
    """Classify the ALREADY-present machine outcome into one honest completeness
    label. Pure classification of transported fields - no new legal fact."""
    coverage = str(rule_evaluation.get("coverage_status", "")).strip().lower()
    if coverage == "data_conflict":
        return _COMPLETENESS_CONFLICTING
    if coverage == "professional_review_required" or rule_evaluation.get("needs_review"):
        return _COMPLETENESS_PROFESSIONAL_REVIEW
    if (
        rule_evaluation.get("fail_safe")
        or coverage in ("unsupported", "not_applicable")
        or not rule_evaluation.get("evaluations")
    ):
        return _COMPLETENESS_THIN
    return _COMPLETENESS_COMPLETE


def _gap_markers(profile: dict, rule_evaluation: dict) -> list[dict]:
    """Name every gap in the trail as a TYPED marker carrying a reason drawn from
    the underlying machine fields (transported) or a fixed descriptive slug. A gap
    is never silently omitted and never invented."""
    coverage = str(rule_evaluation.get("coverage_status", "")).strip().lower()
    gaps: list[dict] = []
    if rule_evaluation.get("fail_safe"):
        gaps.append(
            {
                "kind": _GAP_NOT_AVAILABLE,
                "subject": "rule_evaluation",
                "reason": rule_evaluation.get("fail_safe_reason"),
            }
        )
    if not rule_evaluation.get("evaluations"):
        gaps.append(
            {
                "kind": _GAP_NOT_AVAILABLE,
                "subject": "evaluation_trace",
                "reason": "no_evaluation_trace_present",
            }
        )
    if coverage == "data_conflict":
        gaps.append(
            {"kind": _GAP_DATA_CONFLICT, "subject": "coverage", "reason": coverage}
        )
    if coverage == "professional_review_required" or rule_evaluation.get("needs_review"):
        gaps.append(
            {
                "kind": _GAP_PROFESSIONAL_REVIEW,
                "subject": "coverage",
                "reason": coverage or "needs_review",
            }
        )
    if coverage in ("unsupported", "not_applicable"):
        gaps.append(
            {"kind": _GAP_NOT_APPLICABLE, "subject": "coverage", "reason": coverage}
        )
    if not profile.get("provenance"):
        gaps.append(
            {
                "kind": _GAP_NOT_AVAILABLE,
                "subject": "profile_provenance",
                "reason": "no_provenance_records",
            }
        )
    return gaps


def assemble_evidence_document(
    profile: dict, rule_evaluation: dict, *, bbl: str
) -> dict:
    """Assemble the versioned evidence document from the ALREADY-validated profile
    and rule_evaluation. Every material value is transported VERBATIM (a deep copy
    of the source sub-structure); nothing is recomputed, re-evaluated, rewritten,
    or summarised in a meaning-changing way."""
    evaluated_input = rule_evaluation["evaluated_input"]

    rule_citations: list[dict] = []
    for trace in rule_evaluation.get("evaluations", []):
        rule_citations.append(
            {
                "rule_id": trace["rule_id"],
                "rule_version": trace["rule_version"],
                "family": trace["family"],
                "rule_status": trace["rule_status"],
                # Transported verbatim from the rebuilt rule_evaluation trace.
                "coverage_status": trace["coverage_status"],
                # SERVER-AUTHORED, derived only by echoing the source coverage.
                "claim_verification_status": _verification_status(
                    trace["coverage_status"]
                ),
                # The canonical outputs (incl. any max_residential_floor_area cap)
                # and the citations WITH their own source-snapshot provenance, both
                # transported verbatim - a material value never leaves without it.
                "outputs": copy.deepcopy(trace["outputs"]),
                "citations": copy.deepcopy(trace["citations"]),
            }
        )

    return {
        "contract_version": EVIDENCE_CONTRACT_VERSION,
        "document_kind": "evidence_trail",
        "bbl": bbl,
        # Server-authored overall status: never verified unless the source says so.
        "overall_verification_status": _verification_status(
            rule_evaluation["coverage_status"]
        ),
        # The permanent honest disclaimer, transported verbatim (present while draft).
        "not_verified_disclaimer": rule_evaluation["not_verified_disclaimer"],
        "verification_scope_note": _VERIFICATION_SCOPE_NOTE,
        # The rule_evaluation's own machine-readable outcome fields, verbatim - the
        # single source of the coverage / review / fail-safe posture the evidence
        # trail is honest about.
        "source_coverage": {
            "coverage_status": rule_evaluation["coverage_status"],
            "coverage_source": rule_evaluation["coverage_source"],
            "data_completeness": copy.deepcopy(rule_evaluation["data_completeness"]),
            "needs_review": rule_evaluation["needs_review"],
            "professional_review_required": rule_evaluation[
                "professional_review_required"
            ],
            "fail_safe": rule_evaluation["fail_safe"],
            "fail_safe_reason": copy.deepcopy(rule_evaluation["fail_safe_reason"]),
            "rule_lifecycle_statuses": copy.deepcopy(
                rule_evaluation["rule_lifecycle_statuses"]
            ),
            "reasons": copy.deepcopy(rule_evaluation["reasons"]),
            "family_coverage": copy.deepcopy(rule_evaluation["family_coverage"]),
        },
        # Which profile provenance records back each evaluated input, BY REFERENCE
        # exactly as the accepted rule_evaluation carries them - transported verbatim.
        "evaluated_input": {
            "bbl": evaluated_input["bbl"],
            "profile_contract_version": evaluated_input["profile_contract_version"],
            "input_fingerprint": evaluated_input["input_fingerprint"],
            "input_provenance": copy.deepcopy(evaluated_input["input_provenance"]),
        },
        # Every profile provenance record, verbatim (source id, dataset identity,
        # retrieval timestamp, and whatever else the closed record already carries).
        "profile_provenance": copy.deepcopy(profile["provenance"]),
        # Every rule citation with its own provenance + a per-claim DRAFT status.
        "rule_citations": rule_citations,
        # Honest, typed completeness + gap markers over the transported machine fields.
        "evidence_completeness": _completeness_marker(rule_evaluation),
        "gaps": _gap_markers(profile, rule_evaluation),
    }


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send.

    ``json.dumps(doc, allow_nan=False)`` rejects NaN/Infinity; the
    ``ensure_ascii=False`` + ``.encode('utf-8')`` form is EXACTLY what Starlette's
    ``JSONResponse.render`` uses and is the one that raises on an unpaired
    surrogate. The two disagree about unpaired surrogates and the renderer uses the
    second (M5-T012 G5 BLOCKING-1), so running BOTH here lets the caller fail closed
    to a typed 500 instead of an untyped ASGI 500."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


@router.get("/properties/{bbl}/evidence", include_in_schema=False)
def get_evidence(
    bbl: str,
    fetcher: PlutoFetcher = Depends(get_pluto_fetcher),  # noqa: B008
    substrate_provider: SpatialSubstrateProvider = Depends(  # noqa: B008
        get_spatial_substrate_provider
    ),
) -> JSONResponse:
    """Rebuild the profile + rule_evaluation server-side, assemble the evidence
    trail transported verbatim from them, and return an evidence @ 1.0.0 document.
    Feature-flag gated OFF by default (reuses INTERNAL_RULE_EVAL_ENABLED)."""
    # Guard 1 (fail-safe production disable): absent/unknown flag -> 404 with no
    # hint the feature exists. Checked FIRST, before a correlation id is minted or
    # any input is touched.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 1. Validate the BBL BEFORE any connector call (typed 422; zero network I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "evidence_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _json(
            422,
            {
                "state": "validation_error",
                "message": payload["message"],
                "correlation_id": correlation_id,
                "detail": {"code": payload["code"], "raw_value": payload["raw_value"]},
            },
            correlation_id,
        )

    # 2. Fetch through the injected connector; map typed failures to the SAME
    #    documented HTTP semantics as the property / rule-evaluation routes.
    try:
        result = fetcher(normalized.canonical, correlation_id)
    except PlutoConnectorError as exc:
        payload = exc.to_payload()
        logger.warning(
            "evidence_v1 connector_error state=%s correlation_id=%s",
            payload["error_type"], correlation_id,
        )
        status_code = _ERROR_STATUS.get(payload["error_type"], _DEFAULT_ERROR_STATUS)
        return _json(
            status_code,
            {
                "state": payload["error_type"],
                "message": payload["message"],
                "correlation_id": payload["correlation_id"],
                "source_id": payload["source_id"],
                "dataset_id": payload["dataset_id"],
                "detail": payload["detail"],
            },
            correlation_id,
        )
    except Exception:
        logger.error(
            "evidence_v1 unexpected_error stage=fetch correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    # 3. Everything after the fetch - the rebuild stage, the assembly stage and the
    #    final serialisation - runs inside ONE generic-500 guard so ANY unexpected
    #    exception honors the documented contract, never Starlette's plain-text 500
    #    with full-traceback logging (M5-T012 G1/G5 HIGH-1 was an unguarded stage).
    try:
        # no_match is a RESULT, not an error: the property does not exist in the
        # official dataset, so there is no trail to assemble. Same 404 + machine
        # state shape as the property / rule-evaluation routes.
        if result.status == "no_match":
            return _json(
                404,
                {
                    "state": "no_match",
                    "bbl": result.bbl,
                    "message": result.no_match_explanation,
                    "correlation_id": result.correlation_id,
                    "source_id": SOURCE_ID,
                    "dataset_id": DATASET_ID,
                    "request_url": result.request_url,
                    "retrieved_at": result.retrieved_at,
                },
                correlation_id,
            )

        # --- Rebuild stage: the SAME trusted server-side path the accepted routes
        # use. The spatial substrate comes from the injected server-side provider,
        # never the request. A None substrate is exactly the PLUTO-only build.
        substrate = substrate_provider(normalized.canonical, correlation_id)
        profile = build_property_profile(result, spatial_intersection=substrate)

        try:
            validate_profile(profile)
        except (UnsupportedContractVersionError, ContractValidationError):
            logger.error(
                "evidence_v1 profile_contract_error correlation_id=%s", correlation_id
            )
            return _internal_contract_error_500(correlation_id)

        evaluation = evaluate_property(profile)
        rule_evaluation = serialize_rule_evaluation(
            evaluation,
            profile_contract_version=profile["profile_version"]["contract_version"],
        )
        try:
            validate_rule_evaluation_document(rule_evaluation)
        except RuleEvaluationContractError as exc:
            logger.error(
                "evidence_v1 rule_evaluation_contract_error location=%s correlation_id=%s",
                exc.location, correlation_id,
            )
            return _internal_contract_error_500(correlation_id)

        # --- Assembly stage: transport the trail verbatim (no interpretation).
        evidence = assemble_evidence_document(
            profile, rule_evaluation, bbl=normalized.canonical
        )

        # --- Final serialisation stage: the assembled document MUST survive both
        # json.dumps renderings before send (fail closed to a typed 500, never an
        # untyped ASGI 500, for non-finite / unpaired-surrogate transported content).
        try:
            _assert_json_safe(evidence)
        except Exception:
            logger.error(
                "evidence_v1 serialization_unsafe correlation_id=%s", correlation_id
            )
            return _internal_contract_error_500(correlation_id)

        return _json(200, evidence, correlation_id)
    except Exception:
        logger.error(
            "evidence_v1 unexpected_error stage=assemble correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)
