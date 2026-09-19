# M5-T043 — CI evidence at the combined harvest head (orchestrator-captured)

Captured 2026-09-19 (seq-118). Material `f6e88222` (cherry-pick of worktree `342df579`;
7 files, +829/-249). The pushed head `a380a956` additionally carries the DISJOINT M5-T044
material `1fd07e9a` (condo connector + its test — zero path overlap with M5-T043) and
control-plane bookkeeping; `git diff f6e88222..a380a956` touches no M5-T043 allowed_path.
All three workflows completed **success** at `a380a956` (AS-8):

| Workflow | Run id | Conclusion |
|---|---|---|
| CI (incl. web + web-e2e jobs) | 35412920210 | success |
| secret-scan | 35412920196 | success |
| context-budget | 35412920224 | success |

- The CI web jobs execute the report-view suite carrying the AS-6 assertion (the null-FAR
  fallback renders "Not calculated" and no professional-review phrase on a non-review state)
  on the pushed head — the packet's only web proof channel.
- Local proofs orchestrator-reproduced in `wt-m5t043` at harvest: ruff clean; 101 passed
  (wiring + matcher suites, up from 98); 39 passed (provider suite, up from 38); 475 passed
  (tests/api + test_rules_integration — consumers green with ZERO consumer edits, proving the
  facade); modularity exit 0 with BOTH rules modules dropped off the warn list (the
  extraction's measurable outcome). An earlier CI run at the M5-T043-only head `876ea2b8` was
  superseded/cancelled by the M5-T044 harvest push; the combined-head run above is the
  authoritative conclusion for both materials.
