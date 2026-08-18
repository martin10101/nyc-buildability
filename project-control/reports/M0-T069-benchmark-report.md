# Context-pipeline promotion benchmark (M0-T069 Unit F)

Schema: `context_benchmark/v1` — correctness first.

## Method

Reference = clean full rebuild by the unmodified builder (fresh-cache cold build; identical to the A1-frozen generator). New = warm incremental build over the SAME snapshot at the SAME implementation SHA. Both sides run identical accepted code over identical bytes; only cache state differs, so the implementation-SHA confound is removed (D-013-R056). Verdicts compare raw export bytes.

## Promotion evidence (D-013-R059)

- **census_accounts_every_eligible_file**: PASS
- **incremental_matches_clean_full**: PASS
- **warm_no_change_reparses_zero**: PASS
- **local_change_no_full_rebuild_without_documented_invalidator**: PASS
- **delete_rename_leave_no_stale_nodes**: PASS
- **corruption_crash_concurrency_preserve_validity**: PASS

## Correctness cases

| shape | case | byte-identical | mode | parsed | reused |
|---|---|---|---|---|---|
| single_file_bug | cold_build | yes | full | 2 | 0 |
| single_file_bug | warm_no_change | yes | reuse | 0 | 2 |
| single_file_bug | one_file_change | yes | incremental | 1 | 1 |
| single_file_bug | rename | yes | full | 2 | 0 |
| single_file_bug | delete | yes | full | 1 | 0 |
| single_file_bug | corrupt_cache_recovery | yes | full | 1 | 0 |
| single_file_bug | interrupted_write_recovery | yes | reuse | 0 | 1 |
| single_file_bug | concurrent_writer | yes | full | 2 | 0 |
| cross_module_change | cold_build | yes | full | 2 | 0 |
| cross_module_change | warm_no_change | yes | reuse | 0 | 2 |
| cross_module_change | one_file_change | yes | incremental | 1 | 1 |
| cross_module_change | dependency_change | yes | incremental | 1 | 1 |
| cross_module_change | rename | yes | full | 2 | 0 |
| cross_module_change | delete | yes | full | 1 | 0 |
| cross_module_change | corrupt_cache_recovery | yes | full | 1 | 0 |
| cross_module_change | interrupted_write_recovery | yes | reuse | 0 | 1 |
| cross_module_change | concurrent_writer | yes | full | 2 | 0 |
| frontend_backend_boundary | cold_build | yes | full | 3 | 0 |
| frontend_backend_boundary | warm_no_change | yes | reuse | 0 | 3 |
| frontend_backend_boundary | one_file_change | yes | incremental | 1 | 2 |
| frontend_backend_boundary | config_change | yes | full | 3 | 0 |
| frontend_backend_boundary | rename | yes | full | 3 | 0 |
| frontend_backend_boundary | delete | yes | full | 2 | 0 |
| frontend_backend_boundary | corrupt_cache_recovery | yes | full | 2 | 0 |
| frontend_backend_boundary | interrupted_write_recovery | yes | reuse | 0 | 2 |
| frontend_backend_boundary | concurrent_writer | yes | full | 3 | 0 |
| schema_change | cold_build | yes | full | 1 | 0 |
| schema_change | warm_no_change | yes | reuse | 0 | 2 |
| schema_change | one_file_change | yes | full | 1 | 0 |
| schema_change | rename | yes | full | 1 | 0 |
| schema_change | delete | yes | full | 1 | 0 |
| schema_change | corrupt_cache_recovery | yes | full | 1 | 0 |
| schema_change | interrupted_write_recovery | yes | reuse | 0 | 1 |
| schema_change | concurrent_writer | yes | full | 2 | 0 |
| control_plane_only | cold_build | yes | full | 1 | 0 |
| control_plane_only | warm_no_change | yes | reuse | 0 | 1 |
| control_plane_only | non_eligible_change | yes | full | 1 | 0 |
| control_plane_only | rename | yes | full | 1 | 0 |
| control_plane_only | delete | yes | full | 0 | 0 |
| control_plane_only | corrupt_cache_recovery | yes | full | 0 | 0 |
| control_plane_only | interrupted_write_recovery | yes | reuse | 0 | 0 |
| control_plane_only | concurrent_writer | yes | full | 1 | 0 |

## Measured runtime

measured wall-clock seconds; measurement evidence, never byte-identity content

- single_file_bug / reference_full: samples=1 median=0.1215s p95=0.1215s
- single_file_bug / warm_no_change: samples=3 median=0.0863s p95=0.0863s
- cross_module_change / reference_full: samples=1 median=0.121s p95=0.121s
- cross_module_change / warm_no_change: samples=3 median=0.0882s p95=0.0882s
- frontend_backend_boundary / reference_full: samples=1 median=0.1256s p95=0.1256s
- frontend_backend_boundary / warm_no_change: samples=3 median=0.0891s p95=0.0891s
- schema_change / reference_full: samples=1 median=0.1196s p95=0.1196s
- schema_change / warm_no_change: samples=3 median=0.091s p95=0.091s
- control_plane_only / reference_full: samples=1 median=0.1179s p95=0.1179s
- control_plane_only / warm_no_change: samples=3 median=0.087s p95=0.087s

## Efficiency

- provider token savings: UNMEASURED — no provider-reported usage is available in this offline benchmark; a byte estimate is never presented as token savings (D-013-R012/R053/R057)

## Threshold proposal (before the owner decision)

- **incremental_vs_full_byte_identity** — 100% of benchmark cases: correctness is absolute: any divergence means the index lies about the source (R054/R059)
- **warm_no_change_files_parsed** — 0 files: a no-change run that reparses anything defeats the incremental contract (R059)
- **recovery_validity** — 100% of corruption/crash/concurrency cases end with a valid generation: fail-closed storage is a hard precondition for trusting the cache (R036/R059)

## Promotion decision

PENDING owner/control-plane decision (D-013-R060). This benchmark changes no behavior flag; the pipeline remains exactly as accepted by its unit gates.
