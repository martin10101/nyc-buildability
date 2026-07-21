---
paths:
  - "apps/web/**"
---
# Frontend (apps/web) rule — loads only when editing the Next.js app

The analyst experience is four crisp stages: **Property → Confirm → Compare → Evidence**. Full flow
and UI rules: `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`. Design system: `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md`.

- Keep legal text and legal logic out of components. Consume the canonical contracts in
  `packages/contracts/**`; never invent a competing property schema.
- Progressive disclosure: analysts never see ingestion internals. Advanced source/rule/connector
  operations belong in the admin/reviewer area.
- Never show "best" without naming the optimized objective. Never encode legal certainty by color
  alone. Keep conflicts, unsupported checks, and professional-review flags visible in results.
- Never silently apply a default that materially changes a scenario.
- Accessibility (keyboard nav, announcements, labels), responsive layout, and a real browser
  walkthrough are G3 human-journey **acceptance evidence**, not extras. Use Playwright + an
  independent reviewer walkthrough (`docs/ACCEPTANCE_SCENARIO_STANDARD.md`, UI human-journey pack).
- No API secrets in frontend code; no service-role key; browser holds only session/form state/HTTP cache.
- 3D / massing / map work: see `.claude/rules/3d-ui-expansion.md` (same path scope).
