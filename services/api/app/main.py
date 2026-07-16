"""FastAPI application entry point.

Versioned REST endpoints live under ``/api/v1`` (PRD section 21).
Legal logic belongs in the rule engine, never in routes.

DEPLOYMENT STATUS: INTERNAL/DEV ONLY - no authentication is wired yet
(M0-T007/T008 blocked on the Supabase token). Do not expose this service
publicly until the auth/organization layer lands (M1-T005 G5 condition).
"""

from fastapi import FastAPI

from app.api.v1.properties import router as properties_v1_router

API_VERSION = "0.1.0"

app = FastAPI(
    title="NYC Buildability API",
    version=API_VERSION,
    description=(
        "Preliminary NYC development feasibility and zoning intelligence API. "
        "INTERNAL/DEV: no authentication yet - not for public exposure."
    ),
)

app.include_router(properties_v1_router)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    """Liveness endpoint. No database or external dependency is touched."""
    return {"status": "ok", "version": API_VERSION}
