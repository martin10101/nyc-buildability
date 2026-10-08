"""FastAPI application entry point.

Versioned REST endpoints live under ``/api/v1`` (PRD section 21).
Legal logic belongs in the rule engine, never in routes.

DEPLOYMENT STATUS: INTERNAL/DEV ONLY — authentication is NOT enabled.
M0-T007/T008 (Supabase auth/organizations) are blocked on B-001 (owner
Supabase token). This service must NOT be publicly exposed until the
auth/organization layer lands (M1-T005 G5 condition). The CORS and
security-header baseline below (task M0-T015) is a prerequisite for that
future exposure, NOT a substitute for authentication.

CORS policy (task M0-T015; resolves M2-T001 G3 defect D8):

- Allowed origins are read ONLY from the ``API_CORS_ALLOWED_ORIGINS``
  environment variable: a comma-separated list of exact origins
  (scheme://host[:port]), e.g. the deployed ``nycdf-web`` URL.
- Unset or empty means NO cross-origin access is granted — the safe default
  for internal/dev use. Same-origin and non-browser clients are unaffected.
- This API allows credentialed requests, therefore a wildcard origin is
  REJECTED at startup: ``Access-Control-Allow-Origin: *`` combined with
  credentials is forbidden (Fetch/CORS spec; PRD section 17). The rejection
  is enforced by :func:`_parse_allowed_origins`, not by convention.
"""

import os

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.address_resolution import router as address_resolution_v1_router
from app.api.v1.build_info import router as build_info_v1_router
from app.api.v1.condo_records import router as condo_records_v1_router
from app.api.v1.evidence import router as evidence_v1_router
from app.api.v1.hidden_issue_flags_read import router as hidden_issue_flags_read_v1_router
from app.api.v1.lot_geometry import router as lot_geometry_v1_router
from app.api.v1.parity_read import router as parity_read_v1_router
from app.api.v1.properties import router as properties_v1_router
from app.api.v1.proposal_checks_api import router as proposal_checks_v1_router
from app.api.v1.proposal_validation import router as proposal_validation_v1_router
from app.api.v1.results_read import router as results_read_v1_router
from app.api.v1.rule_evaluation import router as rule_evaluation_v1_router
from app.api.v1.scenario import router as scenario_v1_router
from app.api.v1.scenario_analysis import router as scenario_analysis_v1_router
from app.api.v1.site_definition import router as site_definition_v1_router
from app.api.v1.site_definition import site_definition_write_enabled
from app.api.v1.study_read import router as study_read_v1_router
from app.api.v1.transit_parking_read import router as transit_parking_read_v1_router

API_VERSION = "0.1.0"

# Environment variable holding the comma-separated CORS origin allowlist.
# Declared (name only, value environment-scoped) on the nycdf-api service in
# render.yaml and documented in docs/DEPLOYMENT_AND_ROLLBACK.md.
CORS_ORIGINS_ENV_VAR = "API_CORS_ALLOWED_ORIGINS"

# Baseline security headers applied to every response (task M0-T015).
# This service returns JSON only, so a deny-all CSP and frame denial are safe
# and also protect auto-generated error pages. HSTS is meaningful because TLS
# terminates at Render's edge in every deployed environment.
SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
    "Cache-Control": "no-store",
}

# The interactive documentation pages are HTML that loads Swagger/ReDoc
# assets; the deny-all CSP would blank them. They are exempted from CSP ONLY
# (all other headers still apply). They disappear from public exposure with
# the rest of the service until auth lands (see module docstring).
_CSP_EXEMPT_PATHS = frozenset({"/docs", "/redoc"})


def _parse_allowed_origins(raw: str | None) -> list[str]:
    """Parse the CORS allowlist env var into exact origins.

    Raises ``RuntimeError`` for any wildcard entry: this API allows
    credentialed requests, and wildcard origins combined with credentials are
    forbidden. Startup failure is deliberate — a misconfigured deploy must
    fail health checks rather than silently open cross-origin access.
    """
    origins = [origin.strip() for origin in (raw or "").split(",") if origin.strip()]
    for origin in origins:
        if "*" in origin:
            raise RuntimeError(
                f"{CORS_ORIGINS_ENV_VAR} must list exact origins "
                f"(scheme://host[:port]); wildcard origins are forbidden "
                f"because this API allows credentialed requests. Got: {origin!r}"
            )
    return origins


def create_app() -> FastAPI:
    """Application factory. Reads CORS configuration from the environment."""
    allowed_origins = _parse_allowed_origins(os.environ.get(CORS_ORIGINS_ENV_VAR))

    application = FastAPI(
        title="NYC Buildability API",
        version=API_VERSION,
        description=(
            "Preliminary NYC development feasibility and zoning intelligence API. "
            "INTERNAL/DEV: no authentication yet - not for public exposure."
        ),
    )

    # CORS: exact-origin allowlist only (see module docstring). Added BEFORE
    # the security-header middleware so the header middleware wraps it and
    # stamps preflight responses too (Starlette: later-added runs outermost).
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @application.middleware("http")
    async def security_headers(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        response: Response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            if (
                header == "Content-Security-Policy"
                and request.url.path in _CSP_EXEMPT_PATHS
            ):
                continue
            response.headers.setdefault(header, value)
        return response

    application.include_router(properties_v1_router)
    # Internal, feature-flag-gated rule-evaluation endpoint (task M4-T005). The
    # route is ALWAYS registered but is unreachable (generic 404, no OpenAPI
    # entry) unless INTERNAL_RULE_EVAL_ENABLED is explicitly true; absent/unknown
    # -> disabled (fail safe). See app.api.v1.rule_evaluation.
    application.include_router(rule_evaluation_v1_router)
    # Internal, feature-flag-gated scenario endpoint (task M5-T003). Same posture
    # as rule-evaluation: ALWAYS registered but unreachable (generic 404, no
    # OpenAPI entry) unless INTERNAL_SCENARIO_ENABLED is explicitly true;
    # absent/unknown -> disabled (fail safe). See app.api.v1.scenario.
    application.include_router(scenario_v1_router)
    # Internal, feature-flag-gated scenario OPTIMIZATION-TOOLKIT endpoints (task
    # M5-T012): sensitivity / ranking / comparison / threshold. SAME posture as the
    # scenario route above - ALWAYS registered but unreachable (generic 404, no
    # OpenAPI entry) unless INTERNAL_SCENARIO_ENABLED is explicitly true; absent/
    # unknown -> disabled (fail safe). Reuses the same flag. See
    # app.api.v1.scenario_analysis.
    application.include_router(scenario_analysis_v1_router)
    # Internal, feature-flag-gated EVIDENCE / provenance endpoint (task M5-T013).
    # SAME posture as the scenario / rule-evaluation routes above - ALWAYS
    # registered but unreachable (generic 404, no OpenAPI entry) unless the
    # EXISTING INTERNAL_RULE_EVAL_ENABLED flag is an explicit true token (it
    # surfaces that route's trail verbatim, so it reuses that flag and adds no new
    # one); absent/unknown -> disabled (fail safe). See app.api.v1.evidence.
    application.include_router(evidence_v1_router)
    # Internal, feature-flag-gated ADDRESS-RESOLUTION endpoint (task M2-T022).
    # SAME posture as the routes above - ALWAYS registered but unreachable
    # (generic 404, no OpenAPI entry) unless the EXISTING
    # INTERNAL_RULE_EVAL_ENABLED flag is an explicit true token (address entry
    # is the entry step of the same internal property flow, and app.config is
    # out of the packet's scope, so it reuses that flag and adds no new one);
    # absent/unknown -> disabled (fail safe). See app.api.v1.address_resolution.
    application.include_router(address_resolution_v1_router)
    # Internal, feature-flag-gated DISPLAY-ONLY LOT-GEOMETRY endpoint (task
    # M5-T020, D-040-R001). SAME posture as the routes above - ALWAYS registered
    # but unreachable (generic 404, no OpenAPI entry) unless the EXISTING
    # INTERNAL_RULE_EVAL_ENABLED flag is an explicit true token (the lot outline
    # is part of the same internal property flow and app.config is out of the
    # packet's scope, so it reuses that flag and adds no new one); absent/unknown
    # -> disabled (fail safe). Serves an approximate EPSG:4326 GeoJSON outline for
    # the address confirm card; measurement stays owned by the EPSG:2263 path. See
    # app.api.v1.lot_geometry.
    application.include_router(lot_geometry_v1_router)
    # Internal, feature-flag-gated CONDO-RECORDS endpoint (task M5-T052, DB-031).
    # SAME posture as the routes above - ALWAYS registered but unreachable
    # (generic 404, no OpenAPI entry) unless the EXISTING INTERNAL_RULE_EVAL_ENABLED
    # flag is an explicit true token (the condo records view is part of the same
    # internal property flow and app.config is out of the packet's scope, so it
    # reuses that flag and adds no new one); absent/unknown -> disabled (fail
    # safe). Surfaces the recorded base-lot(s) of a multi-lot condo as RECORDS
    # under the professional-review fail-safe; makes no zoning determination and
    # computes no allowance. See app.api.v1.condo_records.
    application.include_router(condo_records_v1_router)
    # Internal, feature-flag-gated PROPOSAL-VALIDATION endpoint (task M5-T053, D-076 phase
    # B3-scaffold slice 1). SAME posture as the routes above - ALWAYS registered but
    # unreachable (generic 404, no OpenAPI entry) unless the EXISTING INTERNAL_RULE_EVAL_ENABLED
    # flag is an explicit true token (the proposal editor is part of the same internal property
    # flow and app.config is out of the packet's scope, so it reuses that flag and adds no new
    # one); absent/unknown -> disabled (fail safe). Stateless VALIDATION ONLY: it runs the
    # DB-034(a)/(b) input gate + the accepted proposed-massing validator over an editor-authored
    # proposed_massing block and returns typed field refusals or an acceptance echo (block
    # digest + the literal kind 'proposed'); it stores nothing and derives no allowance
    # (D-076-R002). See app.api.v1.proposal_validation.
    application.include_router(proposal_validation_v1_router)
    # Internal, feature-flag-gated PROPOSAL-CHECKS endpoint (task M5-T057, D-076 phase B3 slice
    # 1). SAME posture as the routes above - ALWAYS registered but unreachable (generic 404, no
    # OpenAPI entry) unless the EXISTING INTERNAL_RULE_EVAL_ENABLED flag is an explicit true token
    # (the proposal editor is part of the same internal property flow and app.config is out of the
    # packet's scope, so it reuses that flag and adds no new one); absent/unknown -> disabled (fail
    # safe). It runs the DB-034(a)/(b) input gate + the accepted B2 check engine
    # (app.rules.proposal_checks.check_proposal) over an editor-authored proposed_massing block
    # plus a caller lot context and lot rule facts, and returns the grouped PASS/FAIL/
    # COULD_NOT_CHECK report with numeric shortfalls; it is the trust boundary carrying every
    # G5-recorded precondition BP-1..BP-7. It stores nothing, derives no city record, and emits NO
    # scenario document or contract version (D-076-R002 / DB-034(d)). See
    # app.api.v1.proposal_checks_api.
    application.include_router(proposal_checks_v1_router)
    # Internal, DEFAULT-OFF, flag-gated WRITE route for multi-lot site-definition
    # confirmations (task M5-T062, D-078 slice 2a, DB-040(f)). UNLIKE the routes
    # above (always registered, gated only at the handler by INTERNAL_RULE_EVAL_ENABLED),
    # this WRITE route's REGISTRATION is gated on a DEDICATED default-off flag
    # (SITE_DEFINITION_WRITE_ENABLED): production sets nothing, so the route is
    # ABSENT from the app entirely - any site-definition path hits FastAPI's generic
    # 404, byte-identical to an unmounted path. It stays off until B-001
    # authentication and a durable store land: it records self-attested identity on
    # an ephemeral store, so mounting it unauthenticated in production would ship
    # self-attested personal data with no read-authorization (the DB-040(f) posture
    # stays deferred BEHIND this flag). Turning ON the general INTERNAL_RULE_EVAL_ENABLED
    # flag (for the read surfaces) does NOT expose it - the write route needs BOTH
    # this registration flag AND that handler flag to serve. See
    # app.api.v1.site_definition.
    if site_definition_write_enabled():
        application.include_router(site_definition_v1_router)
    # Internal, feature-flag-gated STUDY-READ endpoint (lane C, request D-1 slice 1). SAME
    # posture as the condo-records / rule-evaluation reads above - ALWAYS registered but
    # unreachable (generic 404, no OpenAPI entry) unless the NEW default-off
    # INTERNAL_STUDY_READ_ENABLED flag is an explicit true token (a DISTINCT flag so this
    # surface is enabled independently); absent/unknown -> disabled (fail safe). It returns the
    # lot-choice + site-facts SETUP half of a study (study.schema.json property/lots/
    # lot_selection/site) for one confirmed BBL: lots and lot_selection come verbatim from
    # B-07's study adapters, site.facts from B-02/B-03, through an injected provider so tests
    # run offline. It computes NO allowance, capacity or rule output and invents no option. The
    # lot choice is Lane B behaviour, produced only when LANE_B_ENABLED is also on, so
    # production (neither flag set) keeps the route a 404. See app.api.v1.study_read.
    application.include_router(study_read_v1_router)
    # Internal, feature-flag-gated §8a HIDDEN-ISSUE-FLAGS read (lane C, packet W2; mounted W5).
    # SAME posture as study-read above - ALWAYS registered but a generic 404 (no OpenAPI entry)
    # unless the NEW default-off INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED flag is an explicit
    # true token; absent/unknown -> disabled (fail safe). Self-gated at the handler in this
    # order: flag-off 404, then per-caller 429, then typed 422, then 503 when inputs are
    # unavailable or Lane B is off. Its data is Lane B behaviour, so production (neither flag
    # set) keeps the route a 404. See app.api.v1.hidden_issue_flags_read.
    application.include_router(hidden_issue_flags_read_v1_router)
    # Internal, feature-flag-gated TRANSIT/PARKING-ZONE read (lane C, packet W3; mounted W5). SAME
    # posture as study-read above - ALWAYS registered but a generic 404 (no OpenAPI entry) unless
    # the NEW default-off INTERNAL_TRANSIT_PARKING_READ_ENABLED flag is an explicit true token;
    # absent/unknown -> disabled (fail safe). Self-gated at the handler (flag-off 404 -> 429 ->
    # 422 -> 503 when the status is unavailable or Lane B is off). Carries the zone only, never a
    # parking outcome; its data is Lane B behaviour, so production keeps it a 404. See
    # app.api.v1.transit_parking_read.
    application.include_router(transit_parking_read_v1_router)
    # Internal, feature-flag-gated PARITY-DATA read (lane C, packet W4; mounted W5). SAME posture
    # as study-read above - ALWAYS registered but a generic 404 (no OpenAPI entry) unless the NEW
    # default-off INTERNAL_PARITY_READ_ENABLED flag is an explicit true token; absent/unknown ->
    # disabled (fail safe). Self-gated at the handler (flag-off 404 -> 429 -> 422 -> the Lane B
    # gate 503 BEFORE any live DOF call -> 503 on upstream/no-subject). Carries recorded sales
    # and a "Not confirmed" capacity line only, no valuation; production keeps it a 404. See
    # app.api.v1.parity_read.
    application.include_router(parity_read_v1_router)
    # Internal, feature-flag-gated RESULTS route (R6B results-connection work order, Part A; task
    # M5-T138). SAME posture as the study-read / lane C reads above - ALWAYS registered but a
    # generic 404 (no OpenAPI entry) unless the NEW default-off INTERNAL_RESULTS_ENABLED flag is an
    # explicit true token; absent/unknown -> disabled (fail safe). It runs the accepted engine chain
    # for one lot (study-inputs provider -> study-setup bridge -> evaluator inputs -> the entry that
    # takes evidence) and returns the emitted contract-1.3.0 three-way results document, never the
    # engine's inner 1.2.0 document. Self-gated at the handler (flag-off 404 -> per-caller 429 ->
    # BBL 422 -> body 422 -> 503 when inputs are unavailable or a recorded condition cannot be
    # confirmed -> 500 on a built-document contract failure). The engine's own Lane A gate stays
    # separate and off in production, so production (neither flag set) keeps the route a 404 and
    # turns no zoning computation on. See app.api.v1.results_read.
    application.include_router(results_read_v1_router)
    # Read-only build-info record (queue C-02, plan M1-02). Ungated like health: it returns
    # only the deployed commit SHA, API_VERSION and a fixed allowlist of flags as booleans,
    # and reads no other env var. See app.api.v1.build_info.
    application.include_router(build_info_v1_router)

    @application.get("/api/v1/health")
    def health() -> dict[str, str]:
        """Liveness endpoint. No database or external dependency is touched."""
        return {"status": "ok", "version": API_VERSION}

    return application


app = create_app()
