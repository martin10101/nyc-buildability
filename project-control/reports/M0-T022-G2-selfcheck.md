# M0-T022 — G2 Producer Self-Check (orchestrator, self_check)

**Frozen impl SHA:** `6c501aaf1b898a11ebf1843090c6b04dca54ebb7`
**CI run:** https://github.com/martin10101/nyc-buildability/actions/runs/29976490909 — **all 11 jobs success**
**Verdict:** PASS (ready for independent gates)

## Self-verification performed

- **Product-map integrity:** `python tools/validate_product_map.py --check` → OK (10 systems, 55 tasks each mapped exactly once; eng_weight and launch_weight each sum to 100). `python tools/test_product_map.py` → 13/13 pass. Enforced in CI (`product-map` job green).
- **Engine determinism:** `apps/web` vitest green in CI (`web-e2e` job) — hand-computed Engineering 72.5→73% vs Launch 32.5→33% on the fixture; health≠completion; UNKNOWN never coerced; producer-recorded gate ignored; stale-GitHub fallback; roster-contradiction flag; real-ledger smoke.
- **Web quality:** `web` job green — eslint clean, `tsc --noEmit` clean, `next build` clean. `web-e2e` green — vitest + Playwright `dashboard.spec.ts` (tabs, SVG map nodes, drawer, keyboard, honesty) against a real `next start` with the internal flag on.
- **No regressions / zero new deps:** all pre-existing jobs green (`api`, `contracts`, `contracts-typegen`, `contracts-schema-bundle`, `control-plane`, `exact-production-install`, lock-verify, `secret-scan`); `apps/web/package.json` + `package-lock.json` byte-identical to main (no dependency added).
- **Scope discipline:** only allowed paths changed. Forbidden paths untouched (existing property/confirm screens, `services/api/**`, `packages/contracts/**`, `master_plan.json`, `tools/project_control.py`, product `globals.css`). `.github/workflows/ci.yml` change is additive (new `product-map` job); `apps/web/playwright.config.ts` change is the e2e flag (scope amendment recorded in the packet).
- **Read-only / internal:** no write paths; no `project_control.py` write calls in app code; no secret/token in the frontend; route 404s by default (fail-safe-off flag); untrusted ledger/GitHub text rendered via JSX (auto-escaped).
- **Holds honored:** nothing Published/Verified; M4 rules shown as draft; no master-plan change; no merge to protected main.

## Blocking corrections carried to independent gates

None from self-check. Independent gates G1 (data-contract), G3 (code), G4 (qa + human-journey),
G5 (security) will verify against the frozen SHA `6c501aa`.
