# M5-T042 — CI evidence at the harvest head (orchestrator-captured)

Captured 2026-09-18 (seq-118). The material `0a6c43c9` (cherry-pick of worktree commit
`224807a8`; 3 files, +1457/-10) plus the bookkeeping commit `c87aacbf` (control-plane only)
formed the pushed head for these push-triggered runs. All three workflows completed
**success** (AS-7):

| Workflow | Run id | Conclusion | Head |
|---|---|---|---|
| CI (api job runs the connectors suite) | 35407815825 | success | c87aacbf |
| secret-scan | 35407815581 | success | c87aacbf |
| context-budget | 35407815610 | success | c87aacbf |

- Local proofs orchestrator-reproduced in `wt-m5t042` at harvest: `python -m ruff check .`
  clean; `tests/connectors/test_dtm_condo_soda.py` 26 passed; `tests/connectors` 852 passed
  (no regression, leaf isolation); `python tools/modularity_check.py --check` exit 0 from
  the repo root (0 failures; `dtm_condo_soda.py` carries a warning-tier review signal,
  disclosed).
- One [ORCH-CORRECTED] edit at harvest: an inline `# gitleaks:allow` marker on the
  fixture-alias line (`test_dtm_condo_soda.py:85`) — the secret scanner false-positived on a
  fixture variable NAME (the condo-key fixture constant is assigned as an alias of the
  billing-response fixture constant; the generic-api-key rule pattern-matched the
  identifier, which contains the word KEY, against the aliased name); no credential exists
  anywhere; comment-only change, suite re-run green before commit.
- `git diff 0a6c43c9..c87aacbf -- apps/ services/ packages/` is empty (bookkeeping only), so
  the CI conclusion speaks for the material identity under review.
