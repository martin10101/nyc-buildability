# M0-T064 A2 — independent re-review ROUND 2 (verbatim), verdict PASS

Preserved verbatim per the report-preservation rule (transport decoding only).
Independent reviewer (read-only; code + QA + directive-compliance + scope/security
dimensions), verifying the tsconfig stale-reuse fix at HEAD dc6a72d. This is the
authoritative independent verification for M0-T064 acceptance (producer = orchestrator
≠ verifier). Substantiates gates G3 (code), G4 (QA), G5 (scope/provenance) and the
D-013/D-001 directive verification.

---

# Re-review at NEW HEAD `dc6a72d0` — fix verification

## VERDICT: PASS

The stale-reuse byte-divergence I reported is fixed correctly, entirely within A2 scope, with no new stale-reuse vector and no over-invalidation regression. Verified by running code, not by reading.

## The fix (reviewed)
- `tools/repo_index_assembly.py:71-92` — new `config_inputs_version(root)`: sha256 over the generator's `cg.CONFIG_INPUTS` (apps/web/tsconfig.json), hashed via the generator's own `cg._fingerprint_entry` (CRLF→LF), domain-tagged, absent-file-safe.
- `tools/repo_index_incremental.py:267-276` — new `_fingerprint(root)` calls `rf.compute_fingerprint(root, config_versions={"codegraph_config_inputs": asm.config_inputs_version(root)})`; `build_incremental` now uses it (line 294). The override merges into A1's `versions` (repo_fingerprint.py:310-312), so it (a) moves the snapshot key → cache miss, and (b) surfaces in `classify_changes` as a `global_invalidator` → `is_structural()` → full rebuild. No A1 change required.

## Verification results

**1. Original counterexample + retarget variant (ran):**
- S8a (retarget `@/*`→nonexistent + source edit): `mode=full`, reason `global_invalidator: codegraph_config_inputs:<old>-><new>`, edge `@/b → unresolved:@/b`, export **== clean_full**.
- S8b (retarget `@/*`→another *existing* dir `src/alt/` + source edit — the "confidently-wrong internal edge" case): `mode=full`, edge correctly `@/b → apps/web/src/alt/b.ts`, export **== clean_full**. The stale `src/b.ts` edge is gone.
- S8c (committed tsconfig-only edit, no source change): not served stale — `mode=full`, export **== clean_full**.

**2. No other unguarded input.** Audited `tools/code_graph/generate.py`: the only reads feeding the graph export are input source files (captured by A1's manifest/snapshot) and `CONFIG_INPUTS` = `apps/web/tsconfig.json` (read by `_load_ts_aliases:441-444`, now guarded). `_PyIndex` and `_TsResolver` structure is path-only; schema nodes come from indexed schema files. The `os.environ` reads (`CODEGRAPH_CACHE_DIR`/`LOCALAPPDATA`, lines 835/839) are only in `default_out_dir` (output location), never in `build_graph`. The generator's "pure function of input file bytes plus CONFIG_INPUTS" claim is complete — no residual stale-reuse vector.

**3. No over-invalidation (ran):** plain `.py` edit with tsconfig unchanged → `mode=incremental`, `files_parsed==1`, export == clean; plain non-`@/` `.ts` edit → `mode=incremental`, `files_parsed==1`, export == clean. `config_inputs_version` is stable for an unchanged tsconfig and changes when it is added/removed.

**4. Suites + real-repo (ran):** `test_repo_index_assembly.py` → 7 passed; `test_repo_index_incremental.py` → 25 passed (the 3 new `TsconfigInvalidation` tests included). Real repo: cold `mode=full`, `files_parsed=421`, export == clean_full (8580 nodes / 3499 edges); warm `mode=reuse`, `files_parsed=0`, export == clean_full.

**5. Evidence + scope:** The item-7 overstatement is corrected — producer-report.md:52-53 and parity-evidence.md:22-23 now state `_TsResolver` depends on "the TS file-PATH set **plus the tsconfig alias map** (`code_graph.CONFIG_INPUTS`)", and both docs document the config-input guard and the FAIL→resolved fix. All six forbidden paths remain byte-identical to `origin/main` (`git diff origin/main HEAD` diff-lines=0 each), including **`tools/repo_fingerprint.py`**; `tools/agent_supervisor/**` unchanged. The delta since the prior head is confined to the two A2 modules + one A2 test + evidence docs. Modularity: 0 failures. SLOC: assembly 341, incremental 512.

## Residual observation (non-blocking, under PASS)
`project-control/reports/M0-T064-evidence-map.json` `reviewed_sha` is still `a89682c` — now two rework generations stale (HEAD is `dc6a72d`). Same evidence-hygiene nit; it does not affect correctness. Recommend stamping it to the final code identity. (Orchestrator note: the authoritative reviewed identity is stamped by project_control into the submit record + directive verification.json at dc6a72d; the evidence-map's internal field is non-authoritative and is left as-is so the accepted content equals the independently reviewed content.)
