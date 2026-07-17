---
name: m1-t006-g3-carryforward
description: M1-T006 contract v1.1 G3 PASS (2026-07-16), zero blocking defects; carry-forwards - validator pytest suite not in CI, builder still labels 1.0.0, M2 builder must emit district maps + extend _assert_provenance_integrity
metadata:
  type: project
---

M1-T006 (property-profile contract 1.1.0, additive) G3 reviewed 2026-07-16: **PASS** at worktree head `82d43ef` (producer `32f0159` + orchestrator one-line pairing). Zero blocking defects. S1-S8 all independently reproduced; S6 verified by FULL regeneration (real connector `fetch_by_bbl` + `build_property_profile`, FakeTransport over the committed F05/F06a record for BBL 1000010010, fixed clock 2026-07-16T12:00:00Z, correlation_id `m1t006-s6-ground-truth`) → exact match with the committed 68 KB fixture.

Carry-forwards to check at the named milestones:
1. **CI wiring (orchestrator decision owed):** the 24-test suite `.github/scripts/tests/test_validate_contracts.py` (incl. forced-legacy RefResolver + fail-closed remote-$ref regression tests) is NOT in any CI job; contracts job is stdlib-only by design. Recheck at next `.github/workflows` or validator touch.
2. **M2 builder task:** when the builder starts emitting `district_provenance`/`commercial_overlay_provenance`/`special_district_provenance`, it must (a) extend `_assert_provenance_integrity` in builder.py with BOTH map rules (ref resolution + sibling-array key membership), and (b) bump `PROFILE_CONTRACT_VERSION` from "1.0.0" to "1.1.0". Today the builder legally emits 1.0.0 + additive keys (deliberate, fixture-proven).
3. **Schema-legal but policy-forbidden:** `coverage_status: "verified"` on any fact passes the schema (enum must include it per PRD 12); the guard is builder policy + G6 only. `provenance_ref_list` allows duplicate refs (no uniqueItems). Both Info-level; revisit at the next contract minor.
4. **Invariant hard-coding (extends [[m0-t009-g3-carryforward]] residual 3):** `profile_provenance_invariant` now hard-codes `lot_facts`/`existing_building_facts` + `ZONING_PROVENANCE_MAPS` + `mapped_features`; ANY new provenance_ref site in a future schema revision must extend it in the same commit.

**Why:** every fixture rejection matched its intended reason (validator prints first error; invariant errors are appended AFTER schema errors, so an invariant-message rejection proves schema-clean); adversarial probes (cross-map confusion, absent sibling array, empty ref list) all fail closed.
**How to apply:** review technique that worked - regenerate ground-truth fixtures through the real code path instead of spot-checking; force the legacy RefResolver branch with `monkeypatch.setitem(sys.modules, "referencing", None)` AFTER jsonschema is imported (unlike pre-import poisoning, this genuinely lands on the RefResolver branch under 4.26). Ruff parity check: `--config services/api/pyproject.toml` gives 28 pre-existing findings in validate_contracts.py at base AND head (zero new).
