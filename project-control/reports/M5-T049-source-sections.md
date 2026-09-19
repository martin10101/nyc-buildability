# M5-T049 source-sections index (frozen submission identity)

Material commit: `d52b1402e8a494ebc7b4e94a596b19d96172f2f1` (task branch, runs 52–53
build, orchestrator-committed) → cherry-pick `b5d3343f3c630b31f096a67561b52cdd854ff4f5`
on candidate/D-024-mrl-option-b. CI at the cherry-pick head: run 35435873943, ALL 12
jobs success (see M5-T049-ci-evidence.md).

SHA-256 digests are LF-normalized (CRLF→LF before hashing), pasted verbatim from the
computing tool's output.

| sha256 (LF-normalized) | file |
|---|---|
| `4e1e850ffdfc35bbb825d1e44e7b504069873b0a0e5e4c9aa50ea58195eba7c1` | services/api/app/rules/named_street_override.py (79-line compatibility facade) |
| `c812b6a29356f21534eafc50b572e645053980d3dcaa07f04d7f7785bf060a58` | services/api/app/rules/named_street_override_table.py (value layer: data model + normalization vocabulary) |
| `3464cc8247d22eb263c7fa99ea6f89cd98bb3e162efeca2cd125df96490335f0` | services/api/app/rules/named_street_override_matching.py (stateful engine) |
| `59f551de293d26ca96dab726ed2761c4609f79cad82e861ceb54892e3cbebe40` | services/api/tests/rules/test_named_street_override.py (UNCHANGED M5-T039/T040 acceptance suite — the byte-identity behavior proof; in the diff only never) |
| `e836755da2440b8af3ab7b4be0ae399ff52aab91e41909f3435448c2a42992cf` | services/api/tests/rules/test_named_street_override_table.py (12 focused tests; carries the one [ORCH-CORRECTED, mechanical] ruff import-sort) |
| `db1d699f1e0f4dc4dbe5e45af0cb81d839269732818e07313c32ecef3951d10b` | services/api/tests/rules/test_named_street_override_matching.py (2 focused tests incl. the re-export identity proof) |
| `5882fb4384ec422e002bc2c0983689dbfd9578b59d4c6b821cf0cd27f1ebd2d8` | project-control/reports/M5-T049-producer-report.md (producer evidence, verbatim from the worktree) |

Orchestrator-reproduced before commit (in wt-m5t049, cwd services/api): ruff clean;
pytest tests/rules 697 passed; tests/spatial 93 passed; tests/api 439 passed;
modularity `selected 449 files; failures 0; warnings 20`, exit 0, no named_street
warning. The one orchestrator correction is the single `ruff --fix` import-sort on the
moved table test (mechanical, zero behavior), tagged in the material commit message.
