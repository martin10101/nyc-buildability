---
name: rules-gate-frozen-sha-reproduction
description: How to independently reproduce the services/api rules test suite at a frozen SHA from a read-only worktree whose HEAD lacks the task files (M4 rule-family G4 gates)
metadata:
  type: feedback
---

When gating an M4 rule-family task (e.g. M4-T014 R3/R4 height/setback), the reviewer worktree HEAD is often an OLD commit that does not contain the material files. Reproduce the suite without any git write:

1. Extract the frozen tree to the scratchpad, preserving repo layout:
   `git archive --format=tar <material_sha> services/api docs/research/zr-snapshots packages/contracts/schemas > frozen.tar`
   then `cd <scratch>/reporoot && tar --force-local -xf frozen.tar` (Windows GNU tar treats `C:` as a remote host — `--force-local` is required, and run tar from INSIDE the target dir rather than `-C "C:/..."`).
2. Run: `cd <scratch>/reporoot/services/api && PYTHONPATH=. python -m pytest tests/rules -q`. There is NO conftest/pythonpath in the api pyproject; CI relies on `pip install ./services/api`, so PYTHONPATH=. is what makes `from app.rules import ...` resolve locally.

**Why:** the count reconciliation is the load-bearing G4 evidence, and a partial extraction silently under-counts.
**How to apply:**
- You MUST also extract `packages/contracts/schemas` — `test_rules_engine.py::test_coverage_and_completeness_match_canonical_contract` reads `packages/contracts/schemas/v1/coverage_status.schema.json` and will spuriously FAIL (1 failed / N-1 passed) if you only pull services/api + docs. That one file is the difference between 457 and the full count.
- The `store` fixture and bundle-guard test resolve `docs/research/zr-snapshots/v1` via `parents[4]`, so the extracted reporoot must place `docs/` and `services/` as siblings.
- Snapshot byte-identity (canonical `docs/research/zr-snapshots/v1` vs bundle `services/api/app/_zr_snapshots/v1`) is provable WITHOUT hashing: identical `git ls-tree <sha> <dir>` blob SHAs == byte-identical. The bundle also carries an extra `__init__.py` (not counted by `sync_zr_snapshots.py --check`, which reports "N file(s)" over `*.snapshot.json` only).
- Snapshot `content_digest_sha256` is genuinely `sha256(verbatim_excerpt.encode('utf-8'))` and the ruleset citations' `content_digest_sha256` must equal the snapshot's — recompute one by hand to prove the in-suite digest test isn't vacuous.

**Modularity is a non-issue for pure rule-family additions:** `tools/modularity_check.py` INCLUDE_RULES only covers `.py/.ts/.tsx` under services/tools/packages/apps, and EXCLUDED_SEGMENTS contains `"tests"` and `"schemas"`. So a task adding only `*.rule.json` + `*.snapshot.json` data files + one `tests/rules/test_*.py` file has ZERO in-scope handwritten production source — modularity_check passes trivially regardless of the test file's line count (e.g. a 660-line test pack).

**Family-membership auto-coverage mechanism (verify, don't assume):** `RuleRegistry.load()` globs ALL `*.rule.json`, raises on duplicate rule_id, and indexes by `family`. The pilot's `test_as6_every_*_rule_file_validates_via_dsl_loader` globs the whole ruleset dir, so it validates NEW files at runtime with no edit to the pilot test. A new family that reuses an existing family NAME would break the pilot's `sorted(fc["rule_ids"]) == sorted(_FAMILY_RULE_IDS)` exact-set assertion — so a distinct family name (e.g. `residential_height_setback_r3_r4` vs the R5 pilot's `residential_height_setback`) is the correct way to keep the pilot green while still being auto-covered by the glob tests + bundle guard (`bundled == canonical` membership).

**Snapshot digest is over `verbatim_excerpt` ONLY (delta-attestation shortcut):** a G3-mandated provenance correction commonly rewrites a snapshot's `notes[]` (e.g. M4-T014 346f8535: clarifying that 23-421(g) / 5-ft / 9,500-sqft detail is attributed to owner-verified external sources, NOT read by the HTML curl capture). Because `content_digest_sha256 == sha256(verbatim_excerpt)`, a notes-only edit is digest-NEUTRAL — all rule citation bindings still hold and the DSL fail-closed load check still passes. To attest a prior G4 PASS stands after such a delta: (1) blob-compare canonical vs bundle at the new SHA (`git ls-tree` — must share one blob); (2) load old+new JSON and assert `verbatim_excerpt` byte-identical AND `content_digest_sha256` unchanged AND recomputed `sha256(new.verbatim_excerpt)` still equals it AND the only differing top-level key is `notes` (also confirm `source`/`district_enumeration` unchanged); (3) re-run `pytest tests/rules` + `sync --check` on the patched scratch tree (copy the new snapshot bytes into BOTH reporoot locations first); (4) `git diff --stat <old>..<new> -- services/api docs/research/zr-snapshots` to prove no rule/test/engine/schema change. No test reads snapshot `notes`, so a notes edit cannot break the suite — but reproduce anyway.

**Mutation-resistance check:** the numeric caps (25/35 ft) are asserted as HARDCODED literals in the acceptance tests (`res.outputs == {"max_...": 25.0}`), NOT read from the ruleset — so value drift fails the test. A test that reads the expected value FROM the ruleset would be vacuous; the digest test reads recorded digests but independently recomputes sha256 of the excerpt, so it is not vacuous. See [[stale-span-inspectability-resolution]] for the general "prove the test binds" discipline.
