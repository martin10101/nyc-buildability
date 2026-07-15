"""FastAPI application entry point (M0 skeleton).

Versioned REST endpoints live under ``/api/v1`` (PRD section 21).
Legal logic belongs in the rule engine, never in routes.
"""

from fastapi import FastAPI

API_VERSION = "0.1.0"

app = FastAPI(
    title="NYC Buildability API",
    version=API_VERSION,
    description=(
        "Preliminary NYC development feasibility and zoning intelligence API. "
        "M0 skeleton: health check only."
    ),
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    """Liveness endpoint. No database or external dependency is touched."""
    return {"status": "ok", "version": API_VERSION}
