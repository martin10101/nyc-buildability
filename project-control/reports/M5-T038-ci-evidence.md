# M5-T038 — CI evidence (orchestrator-captured)

Captured 2026-09-18 ~09:55 UTC. Executable authority for AS-8 (web suites prove ONLY in CI).

- **Material commit:** `d94bbcb65923084d61b06734fabf63dd43b4094a` (cherry-pick of the wt-m5t038
  build: 8 material web files + producer report; +730/-16).
- **First run at the material head:** 19/20 check runs success; web-e2e FAILED on exactly ONE
  Playwright journey (112 passed): `architect-workspace.spec.ts:216` asserted the pre-M5-T038
  rate-limited sentence, while DB-009 deliberately routes the failure copy through the shared
  `FULL_ADDRESS_SEARCH_LABEL` constant (copy now names the "Search this full address" button).
  Vitest was fully green (42/42 test files) — the DB-006/007/019 suites all passed.
- **Orchestrator correction (out-of-scope consumer, consumer-sweep rule):** commit `8c089343`
  `[ORCH-CORRECTED per web-e2e CI on d94bbcb6]` updates only `apps/web/e2e/architect-workspace.spec.ts`
  to the new copy (precedent: the M5-T032 `[ORCH-CORRECTED]` line in the same test). The e2e
  file is OUTSIDE the packet's allowed_paths, so the frozen submission identity at d94bbcb6 is
  byte-stable — no rework cycle required.
- **Corrected head `8c089343`: ALL 20 check runs `completed | success`**, including web-e2e
  (vitest + Playwright vs recorded-official-fixture API) — the packet's suites AND the corrected
  journey green together.
- **Harvest-local corroboration:** none for web behavior (thin client — CI is the only
  executable authority); the producer's digest-bound report sections were verified against the
  committed content at harvest.
