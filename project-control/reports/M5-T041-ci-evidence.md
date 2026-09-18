# M5-T041 — CI evidence at the material head (orchestrator-captured)

Captured 2026-09-18 (seq-118). Material commit `740b6f2f` (the M5-T041 producer material
cherry-pick; 11 files, +818/-32) was the branch head of `candidate/D-024-mrl-option-b` for
these push-triggered runs. All three workflows completed **success** (AS-7):

| Workflow | Run id | Conclusion | Duration |
|---|---|---|---|
| CI (incl. web + web-e2e jobs) | 35402081543 | success | 7m07s |
| secret-scan | 35402081496 | success | 23s |
| context-budget | 35402081495 | success | 11s |

- The CI workflow's web jobs execute the vitest suites on the pushed head — this is the
  packet's ONLY web proof channel (no local npm/node, per CODING_RULES / thin client). The
  suites carrying this packet's new assertions (address-confirm S7, zoning-context-panel
  AS-5/AS-6/DB-024(c), autocomplete DB-024(a)/(c), contract-versions DB-025(e)) ran inside
  the green CI conclusion above.
- Local proofs reproduced by the orchestrator in `wt-m5t041` at harvest:
  `python tools/modularity_check.py --check` exit 0 (0 failures).
- The two commits after `740b6f2f` on the branch at submit time (`2e6729d1` bookkeeping,
  plus this evidence commit) are control-plane/reports only — `git diff 740b6f2f..HEAD --
  apps/ services/ packages/` is empty except for nothing (no product paths), so the CI
  conclusion above speaks for the material identity under review.
