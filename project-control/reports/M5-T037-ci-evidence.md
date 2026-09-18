# M5-T037 — CI evidence (orchestrator-captured)

Captured 2026-09-18 ~10:05 UTC. Executable authority for AS-7 (and the AS-5/AS-6 web halves).

- **Material commit:** `a68757318958a7097a4994df48909f92661b5f28` (cherry-pick of the
  wt-m5t037 build: 16 cross-layer files; +1112/-54). Submission identity stamped at
  `f954aa59` (allowed_paths byte-stable a6875731..f954aa59, verified empty diff).
- **First run at the pushed head f954aa59:** 18/20 success; TWO jobs failed on ONE shared
  root cause — `tests/scenario/test_scenario_contract.py::test_property_profile_and_rule_evaluation_contracts_untouched`
  pins the rule_evaluation `contract_version` enum to `["1.0.0"]` (the api job ran it once,
  exact-production-install re-ran the same suite against the installed tree). 3,767 of 3,768
  backend tests passed; ruff green; every other check green.
- **Orchestrator correction (sanctioned guard update, out-of-scope consumer):** commit
  `be0a7062` `[ORCH-CORRECTED per api CI on f954aa59]` updates the guard to the sanctioned
  enum `["1.0.0","1.1.0"]` — M5-T037 IS the accepted contract task the schema's own enum
  description requires, and this guard has been updated identically at each prior
  property_profile version bump (the same assertion admits five profile versions). The test
  file is OUTSIDE the packet's allowed_paths, so the frozen submission identity at the
  material commit is preserved (no rework cycle).
- **Corrected head `be0a7062`: ALL 20 check runs `completed | success`** — including api
  (ruff + full pytest), exact-production-install (Render pip path + validate_profile +
  pip-audit + the re-run suite), contracts (JSON Schema validation), contracts-typegen
  (byte-identical TS), contracts-sync (bundled == canonical schema), web (lint + typecheck +
  build), and web-e2e (vitest + Playwright vs recorded fixtures — proving the 1.0.0-fixture
  compatibility of the strict validator and the new display/report surfaces).
- **Harvest-local corroboration (orchestrator-run in wt-m5t037):** all seven documented
  commands green (ruff clean; tests/api 426; provider 28; rules-integration 49; typegen
  --check OK; typegen tests 29; modularity failures 0).
