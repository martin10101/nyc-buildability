---
name: m2-t010-g3-carryforward
description: M2-T010 contract-publication tooling (client SUPPORTED_CONTRACT_VERSIONS codegen + drift regression + contract.py docstring fix) G3+G4 PASS at 555d68a; closes M2-T006 R-NEW-1 and LOW-D1; 1.4.0 publication friction is intended
metadata:
  type: project
---

M2-T010 reviewed 2026-07-20: G3 PASS + G4 PASS at merge 555d68a (PR #51; producer worktree impl + orchestrator fixup 6e9d8b1). Zero defects. This CLOSES two [[m2-t006-g3-carryforward]] residuals: R-NEW-1 (client version array now derived from schema enum) and LOW-D1 (contract.py docstring now says 1.3.0).

**Why:** carry-forward for the eventual 1.4.0 publication (M2-T012) and future typegen touches.

Reproduced independently (all green): `packages/contracts` typegen pytest = **14 passed**; `generate_ts_types.py --check` rc=0 (BOTH artifacts OK); `services/api` ruff on contract.py clean; `tests/api` = **79 passed**; full api suite = **538 passed**; `sync_contract_schemas.py --check` rc=0; backend derived tuple = `('1.0.0','1.1.0','1.2.0','1.3.0')`; schema enum on disk = `['1.0.0','1.1.0','1.2.0','1.3.0']` (unchanged). Merge diff = exactly 6 files, all inside allowed_paths; NO schema JSON or generated artifact change; contract.py diff is docstring-only.

**How to apply:**
- Mechanism: client `SUPPORTED_CONTRACT_VERSIONS` is a marker-delimited GENERATED block (lines 86-99 of `apps/web/src/lib/contract.ts`) spliced by `generate_ts_types.py` from `property_profile.schema.json` profile_version.contract_version enum. `--check` byte-compares it (run by the existing `contracts-typegen` CI job — no workflow edit). Exactly one BEGIN/END marker pair; write mode idempotent. This is the SECOND managed artifact in that script (first = generated/property_profile.ts).
- Orchestrator vitest fixup (6e9d8b1) VERDICT: correct & meaningful, NOT weakened. Original `fileURLToPath(import.meta.url)` threw ERR_INVALID_URL_SCHEME under jsdom; fix uses `path.resolve(process.cwd(), "../../packages/contracts/schemas/v1/property_profile.schema.json")`. CI runs vitest with `working-directory: apps/web` (ci.yml ~line 77) and vitest.config.ts sets no custom `root`, so cwd=apps/web and the path resolves to the real schema. Positive lock (exact-equality vs on-disk schema enum) + negative regression (schema-ahead 9.9.9 via same `omittedVersions` detector) both intact. Broken cwd would make readFileSync THROW (loud fail), never a false green.
- 1.4.0 publication FRICTION IS INTENDED (producer report §10, task input 5): future publication must update TWO hardcoded pins — `test_schema_enum_is_closed_at_1_3_0` in test_generate_ts_types.py and the "exactly 1.0.0-1.3.0" vitest case — plus pre-existing pins (test_contract_schema_packaging.py, validate-profile.test.ts). This is the "no silent publication" property M2-T012 must satisfy, NOT a maintenance hazard. Do not treat these pins as a defect at 1.4.0.
- Web vitest/Playwright suites are CI-deferred (no local node_modules per low-storage policy) — established division of labor; orchestrator captures on PR. Not a reviewer BLOCKED condition.
- autocrlf note: on Windows checkouts write mode may rewrite contract.ts/property_profile.ts LF; content-identical, git normalizes. `git checkout --` restores. Not a real diff. [[m2-t003-g3-carryforward]]
