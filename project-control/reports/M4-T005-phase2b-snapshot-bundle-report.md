# M4-T005 Phase 2b — bundle ZR snapshots into the installed package

Producer report. Not a completion claim: the deployability validator is CI
(web-e2e against the installed wheel) after the orchestrator pushes.

## Root cause (given, confirmed)
`services/api/app/rules/snapshots.py` resolved `DEFAULT_SNAPSHOT_DIR` via
`Path(__file__).resolve().parents[4] / "docs/research/zr-snapshots/v1"`. In an
installed wheel (`pip install --no-deps .`), `app/` lives in site-packages with
no sibling `docs/`, so the path does not exist → `SnapshotStore.load` raises
`SnapshotError` on first use → `RuleRegistry().load()` (production default and
`app/rules/integration.py:_default_registry`) fails → rule-evaluation endpoint
500s. Rulesets under `app/rules/rulesets/` were already packaged; only the ZR
snapshots under `docs/` were unpackaged.

## Fix — mirror the accepted `_contract_schemas` bundling pattern
Bundle the snapshots as package data and resolve them via
`importlib.resources`, preferring the packaged copy and falling back to the repo
`docs` source for source-only runs. The explicit `SnapshotStore(directory=...)`
override (used throughout the test suite) is unchanged.

## Files created
- `services/api/app/_zr_snapshots/__init__.py` — package docstring (build-artifact provenance).
- `services/api/app/_zr_snapshots/v1/__init__.py` — v1 subpackage marker.
- `services/api/app/_zr_snapshots/v1/zr-23-21.snapshot.json` — BYTE-IDENTICAL copy of the canonical `docs/research/zr-snapshots/v1/zr-23-21.snapshot.json` (produced by the sync script, verified with `cmp` → IDENTICAL).
- `services/api/scripts/sync_zr_snapshots.py` — write/`--check` sync, mirrors `sync_contract_schemas.py`; globs the source dir so new snapshots are auto-included; `--check` fails on missing, stale, or orphan bundled copies; write mode also prunes orphans.
- `services/api/tests/rules/test_zr_snapshot_bundle.py` — 6-test byte-identity + resolution guard (runs in the existing `api` CI job; NO new CI job).

## Files modified
- `services/api/app/rules/snapshots.py` — new `_resolve_default_snapshot_dir()`:
  `resources.files("app._zr_snapshots.v1")` → `Path(os.fspath(...))`; if it is a
  real dir carrying `*.snapshot.json`, use it; else fall back to
  `_DOCS_SNAPSHOT_DIR` (`parents[4]/docs/...`). `DEFAULT_SNAPSHOT_DIR` computed
  from it at import. `SnapshotStore.__init__` unchanged (still honors an explicit
  `directory`). Backward compatible: source and installed both resolve to the
  byte-identical packaged copy.
- `services/api/pyproject.toml` — added `"app._zr_snapshots.v1" = ["*.snapshot.json"]`
  to `[tool.setuptools.package-data]`; existing `_contract_schemas` entry and
  everything else untouched. `packages.find` `include = ["app*"]` picks up the
  new package via its `__init__.py` files.

## How resolution now works in both contexts
- Source tree: `resources.files("app._zr_snapshots.v1")` resolves to
  `services/api/app/_zr_snapshots/v1` (a real dir with the snapshot) → used.
- Installed wheel (unzipped, `pip install --no-deps .`): `resources.files` yields
  the site-packages concrete path carrying the package data → used. The former
  `docs/` fallback never fires and no longer needs to exist.
- Explicit override: `SnapshotStore(directory=...)` bypasses the default
  entirely (all existing rules tests take this path unchanged).

## Commands run + actual output

`python services/api/scripts/sync_zr_snapshots.py` (write):
```
synced zr-23-21.snapshot.json
```

`python services/api/scripts/sync_zr_snapshots.py --check`:
```
OK: runtime-bundled ZR snapshots are byte-identical to the canonical source (1 file(s)).
```

`cmp docs/.../zr-23-21.snapshot.json services/api/app/_zr_snapshots/v1/zr-23-21.snapshot.json` → `IDENTICAL` (exit 0, no diff).

`python -m ruff check services/api`:
```
All checks passed!
```

`python -m pytest services/api -q`:
```
853 passed in 19.47s
```

New guard test in isolation — `python -m pytest tests/rules/test_zr_snapshot_bundle.py -q`:
```
6 passed in 0.22s
```

Contract-layer no-disturbance:
```
python services/api/scripts/sync_contract_schemas.py --check
OK: runtime-bundled contract schemas are byte-identical to the canonical source.

python packages/contracts/scripts/generate_ts_types.py --check
OK: generated TypeScript types are up to date.
OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.
OK: generated rule_evaluation TypeScript types are up to date.
```

Installed-context proof (isolated `site-packages` copy of `app/` with NO `docs/`
sibling; the `docs` fallback path is confirmed non-existent, yet load succeeds):
```
DEFAULT_SNAPSHOT_DIR: ...\scratchpad\installed_sim\site-packages\app\_zr_snapshots\v1
docs fallback path:   ...\scratchpad\docs\research\zr-snapshots\v1
docs fallback exists? False
loaded ids from installed-layout copy: ['zr-23-21']
RuleRegistry().load() OK in installed-layout (no docs/ sibling)
```
This is the definitive local proof short of building a py3.12 wheel; web-e2e is
the final validator.

## Scope verification (non-mutating `git status --porcelain`)
```
 M services/api/app/rules/snapshots.py
 M services/api/pyproject.toml
?? services/api/app/_zr_snapshots/
?? services/api/scripts/sync_zr_snapshots.py
?? services/api/tests/rules/test_zr_snapshot_bundle.py
```
`git status --porcelain docs/research/zr-snapshots/` → empty (untouched).
`git status --porcelain .github/` → empty (untouched).
`git add -n` on the new package lists exactly the three real files
(`__init__.py`, `v1/__init__.py`, `v1/zr-23-21.snapshot.json`); `__pycache__`
is gitignored. All changes are inside the Phase-2b allowed paths.

## Deviations / blockers
None. No forbidden path modified. Cannot build a py3.12 wheel locally (owner
note acknowledged); the installed-layout simulation above stands in until CI
web-e2e confirms on the real wheel.
