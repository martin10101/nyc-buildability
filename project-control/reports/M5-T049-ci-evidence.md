# M5-T049 CI evidence (orchestrator-captured)

Head: `b5d3343f3c630b31f096a67561b52cdd854ff4f5` (cherry-pick of material commit
d52b1402 onto candidate/D-024-mrl-option-b).

- Workflow **CI** run **35435873943** — completed **success**. All 12 jobs success:
  - api (ruff + pytest) — the packet's documented ruff + tests/rules + tests/spatial +
    tests/api proof at the pushed head (thin-client rule: this is the authoritative run)
  - modularity (deterministic size/responsibility regression gate) — the AS-3 proof at CI
  - web (lint + typecheck + build); web-e2e (vitest + Playwright vs recorded fixtures)
  - contracts-typegen (byte-identical); code-graph (determinism --check + fixture tests)
  - api-lock-verify; api-tooling-lock-verify; web-dependency-security;
    exact-production-install; product-map; context-pipeline
- Workflow **context-budget** — completed success. Workflow **secret-scan** — completed
  success (gitleaks: no leaks).

Producer-side validation posture (per the producer report §Validation): the worker
could not execute ruff/pytest in-run (approval runner rejects the `cd services/api`
prefix); the orchestrator reproduced all documented suites in the worktree before
committing (697/93/439 passed + ruff clean + modularity exit 0) and this CI run is the
independent proof at the pushed head.
