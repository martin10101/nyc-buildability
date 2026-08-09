---
name: installed-package-data-schemas
description: services/api must load contract schemas from bundled package data (importlib.resources), NOT a repo-relative packages/contracts walk — non-editable installs (web-e2e, prod) have no sibling packages/ dir
metadata:
  type: project
---

The deployable FastAPI service (`services/api`) is installed NON-editable in CI and production: the `web-e2e` job runs `pip install ./services/api` (no `[dev]` extras) and imports the INSTALLED `app` from site-packages. Any runtime that resolves a repo asset via `Path(__file__).resolve().parents[N] / "packages" / ...` FAILS there with `FileNotFoundError` because `packages/` is not alongside site-packages `app/`. The `api` job masks this because its pytest imports `app` from the source tree (cwd on sys.path).

**Rule:** anything the installed `app` reads at runtime (schemas, data files) must ship as PACKAGE DATA under `services/api/app/…` and be loaded via `importlib.resources`, never a `parents[...]` walk. Register it with `[tool.setuptools.package-data]` (e.g. `"app._contract_schemas.v1" = ["*.schema.json"]`) so `pip install` includes it. Keep `packages/contracts/schemas/v1` the CANONICAL source; bundle byte-identical copies kept in sync by a stdlib `--check` script (`services/api/scripts/sync_contract_schemas.py`) + an additive CI drift job mirroring `contracts-typegen`.

**Also:** `jsonschema` is used at REQUEST time by `app/profile/contract.py::validate_profile`, so it must be a RUNTIME dependency in `[project].dependencies`, not a `[dev]` extra — the no-dev-extras install would otherwise fail the first validated request.

**Why:** M2-T003 CI web-e2e regression (2026-07-17). The `$id`/`$ref` URIs inside the schema JSON contain the substring `packages/contracts` but are opaque registry keys (referencing/RefResolver keys off `$id`), NOT filesystem paths — bundling identical content preserves $ref resolution.

**How to apply:** when adding any file the API reads at runtime, ask "does this survive a non-editable install with no repo tree?" Prove it by copying only `services/api/app` to a temp dir with NO `packages/` sibling, stripping `__pycache__`, and importing from there. Local Python is 3.11 (< the pyproject `>=3.12`) and `build`/`wheel` aren't installed, so a real wheel build isn't feasible locally — the isolated-copy import is the practical proof; CI on 3.12 is definitive. See [[env-producer-sandbox-no-exec]].
