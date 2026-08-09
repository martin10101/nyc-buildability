---
name: review-environment-and-baselines
description: How visual reviews run in this project (code-level, no browser on owner PC) and where the design baseline lives
metadata:
  type: project
---

Visual reviews on the owner PC are CODE-LEVEL only: no browser can run locally, so claims must be confined to JSX structure, CSS tokens, a11y attributes, and committed Playwright e2e assertions (CI traces via the playwright-evidence artifact answer pixel questions). Always state this honest limitation and name carry-forwards for the first browser-accessible session.

**Why:** Low-storage thin-client policy (approx. 7 GB free, no local npm/Playwright); CI is the only executor. Screenshot-only approval is prohibited anyway.

**How to apply:** Design baseline = `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md` + `docs/3D_VISUAL_ACCEPTANCE_STANDARD.md`. Token vocabulary lives in `apps/web/src/app/globals.css` (hand-rolled CSS variables, single accent #1f4f82, status hues always paired with text label + symbol via `src/lib/coverage.ts`). Accepted M2-T001 Property screen components under `apps/web/src/components/property/` are the visual contract to compare against. I am read-only everywhere except `.claude/agent-memory/visual-quality-reviewer/`; verdicts return in-message per ADR-005, the orchestrator records gates.

Known open visual/a11y themes to re-check in future reviews (found M2-T002, 2026-07-17): failure/outcome states have no aria-live/role=alert and focus is dropped after retry; focus ring is 35%-alpha accent (possibly <3:1); `.secondary-button:disabled` unstyled.
