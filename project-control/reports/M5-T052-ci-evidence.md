# M5-T052 CI evidence (orchestrator-captured)

Corrected head: `a6f35a0f` (material 365f492f + tagged consumer-sweep 46bf1105 + tagged
timestamp fix a6f35a0f; the M5-T053 contract-seam commits between them are disjoint
control-plane + seeds).

- Workflow **CI** run **35451055372** — completed **success**; **0 non-success jobs**
  (full matrix incl. web + web-e2e: 1151 vitest — the shared-decision display suites,
  the rewritten report-view brief suite, and the client suite with the timestamp
  round-trip — plus Playwright; api ruff+pytest re-proving the route suites; modularity;
  contracts; typegen; code-graph; dependency/lock/install jobs; secret-scan green).
- Prior round (root-caused, corrected): run **35449971976** at 46bf1105 — web-e2e FAILED
  exactly 2/1151: the client tests binding the ISO dataset-version round-trip caught
  boundedToken stripping the colons ('2026-08-30T000000Z'). Fixed as tagged b41bf913
  (boundedTimestamp helper, ISO charset, all three timestamp sites). The
  [ORCH-CORRECTED consumer sweep] report-view rewrite passed on its FIRST CI run.

Orchestrator-reproduced at harvest (wt-m5t052, documented cwds): ruff clean; 15 route +
454 api + 697 rules tests; modularity exit 0.
