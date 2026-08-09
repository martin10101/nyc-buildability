---
name: contract-derivation-drift-verification
description: G1 technique for verifying single-source contract-version derivation + drift protection (schema enum -> client marker block + backend import-time read); byte-identity, red-path isolation, no-publication proofs
metadata:
  type: reference
---

Verified during M2-T010 G1 (2026-07-20). This repo makes the published contract-version list single-source across THREE runtime declarations, all deriving from ONE canonical enum: `packages/contracts/schemas/v1/property_profile.schema.json` -> `properties.profile_version.properties.contract_version.enum` (currently `["1.0.0","1.1.0","1.2.0","1.3.0"]`, CLOSED, ends at 1.3.0).

Derivation chains to verify when reviewing any contract-version/derivation task:
- **Client**: `generate_ts_types.py` emits a marker-delimited block (`// BEGIN GENERATED: SUPPORTED_CONTRACT_VERSIONS` .. `// END`) INTO `apps/web/src/lib/contract.ts`. `--check` extracts the committed block and byte-compares vs a fresh derivation. Block lives INSIDE contract.ts (not a separate module) to preserve M2-T002 type-only-import discipline (Next bundle compiles only apps/web files). `WEB_CONTRACT_PATH = Path(__file__).resolve().parents[3]/apps/web/...` — `__file__`-relative, so cwd-robust.
- **Backend**: `services/api/app/profile/contract.py` `_supported_versions()` reads the BUNDLED schema (`app._contract_schemas.v1` via importlib.resources) at import; `SUPPORTED_CONTRACT_VERSIONS = _supported_versions()` evaluated at import (fails fast at startup). NOT hardcoded. Bundle byte-identity enforced by `services/api/scripts/sync_contract_schemas.py --check` (contracts-schema-bundle CI job). Bundled copies are build artifacts of the canonical files (non-editable pip install needs them as package data — no sibling packages/ dir in site-packages).
- **Generated TS union**: `generate()` emits `contract_version: "1.0.0" | ... | "1.3.0"` in `packages/contracts/generated/property_profile.ts`.

Decisive G1 checks (all cheap, read-only, PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider):
- `python packages/contracts/scripts/generate_ts_types.py --check` -> rc 0 prints BOTH "generated TypeScript types are up to date" AND "client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum".
- `python -m pytest packages/contracts/scripts/tests -q` (14 tests). The load-bearing drift regression is `test_drift_schema_published_version_missing_from_client_turns_check_red`: it copies schemas to tmp, appends `1.4.0` to the enum, SATISFIES the property_profile.ts half against a fresh tmp generation, then asserts the CLIENT-block half returns rc 1 with "SUPPORTED_CONTRACT_VERSIONS block"+"out of date" — correctly ISOLATES the failure to the client block. Companion `test_drift_end_to_end...` proves drift reddens BOTH halves. Reverse-drift + mangled-marker tests too.
- Backend: `sync_contract_schemas.py --check` rc 0; `python -c "from app.profile.contract import SUPPORTED_CONTRACT_VERSIONS"` prints the tuple; `select_schema_version('1.4.0')` must raise `UnsupportedContractVersionError` (bounded, NOT coerced to a neighbor) while published versions pass through unchanged.
- No-publication proof: `grep -rn "1.4.0"` across the 4 managed artifacts (schema, generated TS, contract.ts, backend contract.py) excluding tests -> NONE. Generated union line ends at 1.3.0.
- Web vitest `contract-versions.test.ts` resolves schema via `path.resolve(process.cwd(), "../../packages/...")` — this is CORRECT because CI runs vitest with `working-directory: apps/web` (.github/workflows/ci.yml web job `npm run test`). The orchestrator changed it FROM `fileURLToPath(import.meta.url)` which throws under jsdom (import.meta.url not a file: URL). Test asserts client-list == schema-enum exactly (members+order) and exercises a schema-ahead `9.9.9` fixture through the same detector — genuine drift assertion, not a tautology.

Windows note: `core.autocrlf=true` can make write-mode rewrite generated files LF (content-identical; git normalizes). `--check` uses universal-newline read_text so comparison is EOL-safe. A transient ` M` on generated files after a write is EOL noise, not real drift — `git diff` empty confirms.
