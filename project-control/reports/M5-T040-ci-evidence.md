# M5-T040 — CI evidence at the harvest head (orchestrator-captured)

Captured 2026-09-18 (seq-118). The run-46 material `751a1826` (cherry-pick of worktree commit
`42b72b10`; 9 files, +961/-190) plus the bookkeeping commit `4d8847c6` (control-plane only)
formed the pushed head for these runs. All three workflows completed **success** (AS-7):

| Workflow | Run id | Conclusion | Duration |
|---|---|---|---|
| CI (incl. web + web-e2e jobs) | 35407153078 | success @ 4d8847c6 | ~6m |
| secret-scan | 35407153073 | success | 22s |
| context-budget | 35407153117 | success | 11s |

- The CI web jobs execute the repaired report-view parity suite and the DB-025(a-c)
  display-gating assertions on the pushed head — the packet's only web proof channel.
- The run-45 material `987930a2` (DB-023 hardening + DB-021 a/b/c) was proven by the earlier
  green run at head `740b6f2f`-era (CI run 35402081543 success covered the tree carrying
  987930a2, which merged before it).
- Local proofs orchestrator-reproduced in `wt-m5t040` at harvest: ruff clean; 98 passed
  (matcher + wiring suites); 38 passed (provider suite); 475 passed (tests/api +
  test_rules_integration); modularity exit 0 from the repo root (0 failures;
  `wide_street_wiring.py` above the warning threshold — cohesion signal disclosed for review).
- `git diff 751a1826..4d8847c6 -- apps/ services/ packages/` is empty (bookkeeping only), so
  this CI conclusion speaks for the material identity under review.
