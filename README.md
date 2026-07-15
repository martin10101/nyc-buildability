# NYC Buildability

NYC Development Feasibility & Zoning Intelligence Platform — monorepo.

> This platform provides preliminary development and zoning feasibility
> information based on available public records, user-provided assumptions,
> and the platform’s current rule coverage. It is not a legal opinion,
> architectural or engineering certification, DOB determination, permit
> approval, or guarantee that a proposed development will be approved.
> Results must be reviewed by qualified New York professionals before
> reliance, acquisition, design, filing, financing, or construction.

## Monorepo layout

| Path | Contents | Deploy target |
| --- | --- | --- |
| `apps/web` | Next.js 15 App Router frontend (placeholder) | Vercel |
| `services/api` | FastAPI service, `/api/v1/*` endpoints | Render |
| `packages/contracts` | Versioned canonical JSON Schema contracts (v1) plus test fixtures | shared |
| `supabase/migrations` | Database migrations (empty placeholder) | Supabase |
| `.github/workflows` | CI: web lint/typecheck/build, api ruff/pytest, contracts schema validation | GitHub Actions |
| `docs/`, `project-control/` | Operating documents and delivery control plane | — |

## Remote-first development (low-storage policy)

The owner's PC is a thin client (`docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`):

- Do **not** run `npm install`, `pip install`, builds, or test suites locally.
- All dependency installation, linting, testing, and building happens in
  GitHub Actions (see `.github/workflows/ci.yml`) or Codespaces.
- No `node_modules/`, virtualenvs, `.next/`, or datasets may be committed or
  kept in the local checkout (see `.gitignore`).
- Persistent data lives in Supabase; deployments run on Vercel and Render.

## CI

Every push and pull request runs four jobs (no secrets required):

1. **web** — Node 22: `npm ci` (lockfile generated remotely by
   `generate-lockfile.yml`), `eslint`, `tsc --noEmit`, `next build`.
2. **api** — Python 3.12: `pip install .[dev]`, `ruff check`, `pytest`.
3. **contracts** — `python3 .github/scripts/validate_contracts.py`: meta-schema
   validation of every contract schema (draft 2020-12; strict stdlib structural
   layer always on, `jsonschema` engine added automatically when importable),
   fixture validation (`fixtures/valid/` must pass, `fixtures/invalid/` and
   `fixtures/invalid_schemas/` must fail), and the property-profile
   provenance-ref integrity invariant. No pip installs required.
4. **control-plane** — `tools/test_project_control.py` workflow regression
   test (ADR-005 authority rules and control-plane defect regressions).

## Delivery control

Work is tracked through `project-control/` (tasks, gates, checkpoints,
reports). See `CLAUDE.md` and `docs/PROJECT_CONTROL_PROTOCOL.md`.
