# M0-T064 A2 — independent re-review ROUND 1 (verbatim), verdict FAIL

Preserved verbatim per the report-preservation rule (transport decoding only).
Independent reviewer (read-only, code+QA+DCV+security dimensions), reviewing the
selective-reparse rework at HEAD 02a07a76. This round found a real byte-divergence
(tsconfig stale reuse); it was remediated at HEAD dc6a72d and re-reviewed (round 2,
PASS). This FAIL record returns the task to rework so it can be re-submitted and
re-gated at the fixed content identity.

---

# Independent Review — M0-T064 Unit A2 (incremental indexing)

**HEAD:** `02a07a76` on `task/M0-T064-incremental-index`

## VERDICT: FAIL

Byte-identity breaks under a reproducible **stale-reuse** counterexample: a change to `apps/web/tsconfig.json` (which steers TS `@/` alias resolution) concurrent with any single indexed-file content edit makes `build_incremental` take the `incremental` path and reuse stale TS bundles, yielding an export that is **not** byte-identical to a clean full rebuild. This is reachable on the real repo (185 internal `@/`-alias edges today). Per the rubric ("FAIL if byte-identity ever breaks / a stale-reuse counterexample exists"), this is a FAIL. Everything else — parity on all other change classes, telemetry, scope, modularity, the version guard, and both defect fixes — is correct.

## The defect (stale reuse → byte divergence)

**Root cause:** `tools/repo_fingerprint.py:285-292` `default_config_versions()` tracks only `fingerprint`, `eligibility`, `codegraph_schema`. It omits `apps/web/tsconfig.json` — the generator's own `CONFIG_INPUTS` (`tools/code_graph/generate.py:149`, read by `_load_ts_aliases`, lines 434-464). Because tsconfig is neither an indexed input file nor a tracked config-version, a tsconfig edit is never surfaced as a `global_invalidator` by `classify_changes` (`tools/repo_index_incremental.py:136-139`), and the `can_incremental` gate (`tools/repo_index_incremental.py:324-332`) has no other check that would catch it. `asm.drive` recomputes `aliases` (`tools/repo_index_assembly.py:273`) but only applies them to *newly extracted* files; reused TS bundles keep their old alias-resolved edges. The assembly docstring (`repo_index_assembly.py:258-265`) even states the caller "MUST guarantee … no global invalidator so the resolution index … [is] unchanged" — but `_TsResolver` depends on the tsconfig alias map, and the gate does not enforce that precondition.

**Concrete repro (executed, in a temp git repo):**
1. `apps/web/tsconfig.json` = `{"compilerOptions":{"paths":{"@/*":["./src/*"]}}}`; `apps/web/src/a.ts` = `import { x } from '@/b';`; `apps/web/src/b.ts` = `export const x = 1;`; plus `services/api/app/trigger.py`.
2. Cold `build_incremental` → `mode=full`, export == clean full (edge `a.ts → apps/web/src/b.ts`, internal/exact).
3. Edit tsconfig to `"@/*":["./src/nowhere/*"]` **and** edit `trigger.py` (`v=1`→`v=2`).
4. Rebuild → `mode=incremental`, `files_parsed=1` ("reparsed 1 of 3"), reuses `a.ts` bundle.
5. Result: incremental export has `a.ts → apps/web/src/b.ts` (internal); clean full build has `a.ts → unresolved:@/b`. **Byte divergence.** (A variant where the alias retargets to another existing file yields a *confidently-wrong internal edge*, which is worse.)

Note: a tsconfig-only edit (no input-file edit) is accidentally safe — `any_content_change()` is false so it full-rebuilds. The bug requires a tsconfig change plus at least one indexed-file content edit in the same snapshot (a normal "move a module and adjust the alias" workflow).

## Per-item findings

1. **PARITY — PASS.** `test_repo_index_assembly.py` (7) and `test_repo_index_incremental.py` (22) both pass. Independent live-repo check: cold `drive('.')` == real `serialize(build_graph)` (3,305,639 bytes), files_parsed=421/reused=0; warm no-change == real, files_parsed=0/reused=431; warm one-changed (py and ts) == real, files_parsed=1.
2. **SELECTIVE REPARSE — MIXED.** Warm no-change: `files_parsed==0`, `mode=reuse`. Single edit: `mode=incremental`, `files_parsed==1`, byte-identical. Adversarial A-imports-B (edit B): `mode=incremental`, `files_parsed=1`, export == clean full, and A correctly appears in `affected_files`. Edit-A-only, add, delete, rename all byte-identical to clean full (add/delete/rename correctly `mode=full`; rename correctly paired, not add+delete). **The stale-reuse gate analysis, however, produced the tsconfig counterexample above — the one gap in the "content change to an unchanged file can't alter another file" argument.** (`_PyIndex` is genuinely path-only; `_TsResolver` is path-**plus-alias**, and the alias input is unguarded.)
3. **GENERATOR VERSION GUARD — PASS.** With `codegraph.GENERATOR_VERSION` monkeypatched to a bogus value in-process: `asm.drive` raises `UnknownGeneratorError`; `build_incremental` falls back to `mode=full` (reason "unrecognized generator …"), export still == clean full via the real builder. Restored in-process.
4. **DEFECT FIXES — PASS.** (a) `importer_closure` (`repo_index_incremental.py:173-198`) reads `e.get("to")` against `input_files` — the real graph edge shape — confirmed by A appearing in `affected_files`. (b) Prior manifest merges `config_versions` before `classify_changes` (`repo_index_incremental.py:313-316`): two consecutive no-change builds both `reuse` (no spurious invalidator), and a content edit yields `incremental`, never `full`.
5. **TELEMETRY — PASS.** All required run-record fields present; `repo_identity` is a 64-hex sha (not a path); no absolute repo path in the record; `estimated_tokens`/`provider_tokens` null; `elapsed_seconds` present in the external record and absent from the export bytes. JSONL lives in the per-checkout cache dir outside the repo, one valid-JSON object per line, and is append-only (prior content preserved as a prefix, file grows).
6. **SCOPE + MODULARITY — PASS.** All six forbidden paths are byte-identical to `origin/main`. `modularity_check.py --check` → 0 failures (4 pre-existing warnings, none in this delta). SLOC: `repo_index_assembly.py` 317, `repo_index_incremental.py` 500. CI change is additive.
7. **EVIDENCE ACCURACY — overstatement found.** `M0-T064-producer-report.md` and `M0-T064-parity-evidence.md` assert `_TsResolver` is "a function of the file-PATH set" and a reused bundle is "provably still exact" on any content-only edit. That is false — `_TsResolver` also depends on the tsconfig alias map, which is untracked; the tsconfig counterexample disproves the "across every change class" byte-identity claim. Minor: stale count numbers; the CI step wording; the evidence-map `reviewed_sha` predates the rework.

## Recommended fix
Treat the tsconfig alias set as a global invalidator: add `apps/web/tsconfig.json` (the code-graph `CONFIG_INPUTS`) to the fingerprint as a hashed input, or have the `can_incremental` gate compare the current `_load_ts_aliases(root)` against the prior alias set and force `full` on any difference. Add a regression test that edits tsconfig `paths` concurrently with a source edit and asserts `export == clean_full_build_bytes`.
