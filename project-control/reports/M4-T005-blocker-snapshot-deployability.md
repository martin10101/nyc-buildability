# M4-T005 — discovered blocker: rule-engine ZR-snapshot deployability gap

**Discovered:** 2026-07-22, during CI validation of PR #84 (web-e2e).
**Status:** blocks the rule-evaluation endpoint from functioning when the API runs as an **installed package** (web-e2e, and the real Render deploy). Contract (Phase 1) and frontend (Phase 3) are unaffected. All non-endpoint CI green.

## Symptom
`web` (lint+typecheck+build), `api`, `contracts*`, `exact-production-install`: **PASS**. `web-e2e`: the 5 `rule-evaluation.spec.ts` journeys **FAIL**; the endpoint returns a safe generic `500 internal_error` on every call (the flag/frontend/serializer wiring all work — flag-OFF specs pass).

## Root cause (definitive — captured via temporary `logger.exception`, since reverted)
```
app.rules.snapshots.SnapshotError: snapshot directory not found:
  /opt/hostedtoolcache/Python/3.12.13/x64/lib/docs/research/zr-snapshots/v1
```
`services/api/app/rules/snapshots.py:26` computes `DEFAULT_SNAPSHOT_DIR = Path(__file__).resolve().parents[4] / "docs/research/zr-snapshots/v1"`. From the **source tree** `parents[4]` is the repo root, so the path exists — which is why Phase-2 pytest and local repro pass. web-e2e runs the API from an **installed wheel** (`pip install --no-deps .`); `docs/` is not part of the `app` package, so from `site-packages/app/rules/snapshots.py` the path resolves to `.../lib/docs/...` and does not exist. `RuleRegistry.load()` calls `snapshots.load()` unconditionally → throws on first registry use.

- Rulesets live under `app/rules/rulesets/` (packaged, fine). Only the **ZR snapshots under `docs/`** are unpackaged.
- The property endpoint never uses the registry, so it was unaffected — the rule-evaluation endpoint is the **first runtime consumer of the rule registry in an installed context**, exposing a latent M4-T001 gap. The same gap would break the real Render deploy (the `exact-production-install` job does not exercise rule evaluation, so it never caught it).

## This is out of M4-T005's declared scope
The fix must make the ZR snapshot files resolvable from an installed package. That touches paths **forbidden in the M4-T005 packet**: `services/api/app/rules/snapshots.py` (directory resolution) and `services/api/pyproject.toml` (package-data), plus a new bundled copy under `app/` and a byte-identity guard. It is a rule-engine **deployability** fix (copying snapshot files byte-identically + resolution), NOT a change to rule content or lifecycle — nothing is Published/Verified and no legal rule text changes. Per the owner "no scope change" directive it needs an explicit scope decision.

## Recommended fix (mirrors the accepted `_contract_schemas` bundle pattern)
1. Sync a byte-identical copy of `docs/research/zr-snapshots/v1/*.snapshot.json` into the package (e.g. `app/_zr_snapshots/v1/`), included via `pyproject.toml` package-data glob (exactly like `app._contract_schemas.v1`).
2. `snapshots.py` resolves the packaged location via `importlib.resources`, falling back to the repo `docs/` path for source runs.
3. Add a byte-identity drift guard (a `sync_*`+`--check` step and/or a contract-style test), mirroring `contracts-schema-bundle`.
4. Re-run full CI; then freeze.

## Options for the owner
- **A (recommended):** authorize the minimal in-task deployability fix above (adds `snapshots.py` + `pyproject.toml` + a new bundled dir + guard to M4-T005 scope). Keeps the vertical slice honest and end-to-end green.
- **B:** split the fix into a new controlled task (e.g. M4-T006 "rule-engine snapshot bundling for deployment"); M4-T005 waits on it (endpoint stays non-deployable until then).
- **C:** point the snapshot dir via config/env at the source `docs/` path for e2e only — **rejected**: it would make e2e green while the real deploy stays broken (dishonest), so not offered as viable.
