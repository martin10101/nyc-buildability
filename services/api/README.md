# NYC Buildability API (M0 placeholder)

FastAPI service skeleton. Versioned REST endpoints live under `/api/v1`
(PRD section 21). Always-on endpoints:

- `GET /api/v1/health` returns `{"status": "ok", "version": "<service version>"}`
- `GET /api/v1/build-info` returns `{"commit": "<sha>|unknown", "version": "<service version>",
  "flags": {"<FLAG>": true|false, ...}}`: the deployed commit and a fixed allowlist of boolean
  flags, never a raw env value (plan M1-02; `app/api/v1/build_info.py`)

## Development (remote-first)

Per `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`, dependencies are installed
and tests are executed in GitHub Actions or Codespaces — not on the owner's PC.

CI runs:

```
pip install .[dev]
ruff check .
pytest -q
```
