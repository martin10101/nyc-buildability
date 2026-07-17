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

from app.api.v1.properties import router as properties_v1_router

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

    @application.get("/api/v1/health")
    def health() -> dict[str, str]:
        """Liveness endpoint. No database or external dependency is touched."""
        return {"status": "ok", "version": API_VERSION}

    return application


app = create_app()
