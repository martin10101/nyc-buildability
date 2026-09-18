# M5-T036 CI evidence (orchestrator-captured; AS-6 executable authority)

## Run at the harvested build head 657b238dce8af8df1bfff2e22e454caab1749413

GitHub Actions "CI" run 35287678106: 17 of 18 jobs SUCCESS (contracts, contracts-typegen,
contracts-schema-bundle, product-map, control-plane, context-pipeline, web lint+typecheck+
build, exact-production-install, api ruff+pytest, api-lock verifies, code-graph,
web-dependency-security, model-routing, supervisor-bridge, modularity, context-index-a1);
ONE failure: **web-e2e (vitest)** — FAIL src/components/architect/__tests__/
zoning-context-panel.test.tsx: `TestingLibraryElementError: Found multiple elements with
the text: R3-2` (AS-1 test 1) and the same for `C1-4` (AS-1 populated-overlay test);
summary "Test Files 1 failed | 40 passed (41)". The web job's HTMLCanvasElement.getContext
lines are the documented jsdom/MapLibre noise (CODING_RULES), not the failure. Notably the
`web (lint + typecheck + build)` job PASSED at this head — tsc/type-check green.

Diagnosis (verified in source + confirmed by all five reviewers' delta-attestations): a
TEST-QUERY defect only — each designation value legitimately renders both as its visible
value and inside its provenance-disclosure original/normalized rows, so single-match
getByText was ambiguous. No production defect.

## Run at the corrected head 8214312480e80e2ce10abbbc423ff590afe4651b

Rework commit 82143124 (test-only: getAllByText counted presence assertions + report
addendum). GitHub Actions "CI" completed **SUCCESS — all jobs green, including web-e2e**
(orchestrator watch captured "CI completed success"; context-budget and secret-scan
workflows also success). AS-6 satisfied at the frozen submission identity.
