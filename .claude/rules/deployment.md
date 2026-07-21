---
paths:
  - ".github/workflows/**"
  - "render.yaml"
  - "infra/**"
---
# Deployment / CI rule — loads only when editing workflows, render.yaml, or infra

- **Protected-main, PR-only.** Never push to `main`. Task/control branch → push → `gh pr create` →
  required checks green → `gh pr merge --merge --delete-branch --match-head-commit <FULL-40-char-SHA>`
  (a short SHA errors "Could not coerce value to GitObjectID") → `git fetch` + reconcile. Only the
  orchestrator merges/integrates.
- **Deploy model of record (ADR-003/ADR-004):** all Render services `autoDeployTrigger: off` in
  production; deploys run only from the Actions deploy workflow after migration validation →
  production migrations → required checks → **human production approval**, via secret deploy hooks
  pinned to a validated SHA. Frontend gated identically. Details: `docs/DEPLOYMENT_AND_ROLLBACK.md`.
- **Supply-chain (permanent, no waiver):** SHA-pin every third-party Action; every admitted package
  version ≥ 7 complete days old (604800 s passes, 604799 fails) with registry timestamp + integrity
  evidence; fail closed on missing/malformed/outage evidence. Policy: `.claude/ORCHESTRATION_POLICY.md`
  §G; enforced by `services/api/scripts/dependency_age_gate.py` (Python) and the committed-npm-lockfile
  age gate.
- **Thin client:** builds, full test suites, lockfile regeneration, and GIS/data imports run on
  GitHub Actions / Render, never on the owner's PC (`docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`).
- Secrets: service-role keys only in trusted backend/worker env; never in frontend or logs.
