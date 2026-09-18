# M5-T035 — CI evidence at the material head (orchestrator-captured)

Captured 2026-09-18 ~06:29 UTC by the orchestrator per the evidence-capture division of labor
(.claude/rules/project-control.md). Executable authority for AS-7.

- **Material commit:** `97fa2eea5d63b5b036055b10ad1902155f8a4be1` (cherry-pick of the
  wt-m5t035 build, 10 files, +2238/-54) on `candidate/D-024-mrl-option-b`, pushed
  2026-09-18T06:21:54Z.
- **Workflow runs on the push (gh run list):** CI run 35314557906 → **success** (6m11s);
  context-budget 35314557990 → success; secret-scan 35314558152 → success.
- **All check runs on commit 97fa2eea (gh api …/check-runs), every one `completed | success`:**
  modularity; supervisor-bridge; model-routing; web-e2e (vitest + Playwright vs
  recorded-official-fixture API); contracts (JSON Schema validation); exact-production-install
  (Render pip install path + validate_profile + pip-audit); code-graph; product-map;
  api-tooling-lock-verify; contracts-typegen (TS drift, byte-identical); context-pipeline;
  **api (ruff + pytest)**; api-lock-verify; control-plane (ADR-005 workflow regression);
  context-index-a1.
- **Identity note:** live HEAD at review time (3ce7b87d) differs from the material commit only
  by control-plane submit side effects; `git diff 97fa2eea..HEAD -- services/ apps/
  docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` is empty (allowed_paths byte-stable).
- **Harvest-local corroboration (orchestrator-run in wt-m5t035 at the same tree):**
  `python -m ruff check services/api` clean; pytest suites 76 (spatial) + 69 (dcm connector)
  + 54 (buffer engine) + 38 (rule-evaluation api) all pass; `python tools/modularity_check.py
  --check` failures 0.
