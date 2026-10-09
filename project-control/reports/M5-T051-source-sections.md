# M5-T051 source-sections index (frozen submission identity)

Material: commit `8d879a9525fdd6c19b32ea022ef01405a2f8e626` (task branch, runs 15–18 build
across four model-downgrade collision stops, orchestrator-committed) → cherry-pick
`f1ec64a81b4b5aca3cc348012b8196bd963480b8` on candidate/D-024-mrl-option-b.
CI at that head: run **35455214032**, ALL jobs success (0 non-success) —
M5-T051-ci-evidence.md.

SHA-256 digests are LF-normalized (CRLF→LF before hashing), pasted verbatim.

| sha256 (LF-normalized) | file |
|---|---|
| `c7b1b07bb28db390d13ae2005e0838f919df70a8da036a1b2fcac799c9ffaf4d` | services/api/app/scenario/derivation.py (NEW: pure/typed/bounded derivation of proposal FACTS with frozen EvidenceRecords, source_class 'proposed_derivation'; caller-supplied LotContext — no fetching/connector import) |
| `bca8deb8e5a5c3879ab2e1c87086f84fda1d39619d2a35cc521b3575dfc1266d` | services/api/app/scenario/proposal.py (DB-034(c) degenerate-wall closure ONLY; B0 semantics otherwise byte-preserved) |
| `b28a6d24fbf4dcefce8eac47a82d1b62680ca3746e25d88f12b22ea7c3ba7db7` | services/api/tests/scenario/test_scenario_derivation.py (hand-computed property tests: exact areas/coverage/setbacks, rotation/translation invariance, typed refusals, honest street absence) |
| `b069cdca56542b730509b5e10cb39cefaa1368e63cefc0b164450ad48518b994` | services/api/tests/scenario/test_scenario_proposal.py (adds the DB-034(c) degenerate-wall test + the DB-034(e) collinear-branch test) |
| `f70760ce5eb45c30f3a0317a8c1c279dddd78c8ca961cf483379a99433d2df52` | services/api/tests/scenario/fixtures/derivation/README.md (fixture arithmetic shown) |
| `1c3bf9a3afeb49bade0364ba0dab60f8b3f4e6cda7ab1b7800d6b22421a8fcb3` | services/api/tests/scenario/fixtures/derivation/rectangle_100x80.json |
| `b786af0aaaa32fee7decc4c390a8a8e9d8b19c580e060ebad50cd223d0a2e290` | services/api/tests/scenario/fixtures/derivation/l_shape_multilevel.json |
| `1d3886718cd61ea206824d8da5be780098cf170e9877ceca4ff0f90e8e7d1b8f` | services/api/tests/scenario/fixtures/derivation/wall_setback.json |
| `f19e3e53d53e46204dca5630eb45338ffc5ff8af9cc95653a67ac765dce520bc` | project-control/reports/M5-T051-producer-report.md (producer evidence, verbatim from the worktree) |

Orchestrator reproduced at harvest (wt-m5t051, documented cwds): ruff clean; pytest
tests/scenario 568 passed; tests/api 439 passed IN THE WORKTREE ([ORCH-CORRECTED per G4-1]: the stale worktree-base count; the TRUE count at the frozen head is 497 - see M5-T051-G2.md); modularity exit 0. Note the run history:
four of the five runs ended at provider-side model-downgrade rotation collisions (runs
15/17/18) or a supervisor crash (run 16) — never a build failure; the work accumulated
across runs and the drills preserved it (recorded in the backlog sweeps).
