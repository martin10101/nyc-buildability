# NYC Buildability API (M0 placeholder)

FastAPI service skeleton. Versioned REST endpoints live under `/api/v1`
(PRD section 21). The only endpoint in M0 is the health check:

- `GET /api/v1/health` returns `{"status": "ok", "version": "<service version>"}`

## Development (remote-first)

Per `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`, dependencies are installed
and tests are executed in GitHub Actions or Codespaces — not on the owner's PC.

CI runs:

```
pip install .[dev]
ruff check .
pytest -q
```
