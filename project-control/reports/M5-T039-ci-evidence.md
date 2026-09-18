# M5-T039 — CI evidence at the material head (orchestrator-captured)

Captured 2026-09-18 ~09:20 UTC per the evidence-capture division of labor. Executable
authority for AS-6.

- **Material commit:** `1564e5094c8adf53e96a8a3dd87c364ae2c811e4` (cherry-pick of the
  wt-m5t039 build: matcher + 40-test suite + both repaired snapshot copies + producer report
  v6; +1609/-36) on `candidate/D-024-mrl-option-b`, pushed 2026-09-18 ~09:09 UTC.
- **Check runs on commit 1564e509 (gh api …/check-runs): all 20 `completed | success`** —
  including api (ruff + pytest, which runs the new named-street suite), contracts +
  contracts-sync (the repaired bundled snapshot ships inside the api package), web-e2e,
  modularity, control-plane, secret-scan, context-budget.
- **Identity note:** live HEAD at review time (44649797) differs from the material commit only
  by control-plane submit side effects; `git diff 1564e509..HEAD -- services/ docs/research/`
  is empty (verified independently by all three reviewers and the orchestrator).
