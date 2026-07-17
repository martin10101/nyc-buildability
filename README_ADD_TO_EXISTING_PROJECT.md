# NYC Buildability — 3D, Competitive Features & Premium UI Expansion Pack

This is a **separate additive pack** for the existing NYC Development Feasibility Claude project.

It must not reset, replace, or recreate the existing project.

## How to add it

1. Open this expansion pack.
2. Copy its contents into the root of the existing project.
3. Allow new files to be added.
4. Do not overwrite existing files unless you intentionally compare and merge them.
5. Open Claude Code in the existing project root.
6. Paste the prompt from `CONTINUE_FROM_CURRENT_STATE_PROMPT.md`.

The new `.claude/rules/3d-ui-expansion.md` file tells the orchestrator to:

- Read the existing project-control state.
- Preserve accepted tasks and checkpoints.
- Add the new work as dependent tasks.
- Continue from the current implementation point.
- Avoid starting the project over.
- Use independent producer/reviewer gates.

## Files included

- `docs/COMPETITIVE_FEATURE_EXPANSION.md`
- `docs/3D_MASSING_ENGINE_ARCHITECTURE.md`
- `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md`
- `docs/3D_AND_UI_EXECUTION_PLAN.md`
- `docs/3D_VISUAL_ACCEPTANCE_STANDARD.md`
- `.claude/rules/3d-ui-expansion.md`
- `.claude/agents/3d-massing-engineer.md`
- `.claude/agents/product-design-director.md`
- `.claude/agents/visual-quality-reviewer.md`
- `.claude/agents/financial-feasibility-engineer.md`
- `.claude/agents/opportunity-search-engineer.md`
- `CONTINUE_FROM_CURRENT_STATE_PROMPT.md`
- `INTEGRATION_MANIFEST.json`

## Important

The 3D viewer is not a decorative rendering. Its geometry must be generated from the same verified property facts and deterministic zoning constraints used by the scenario engine.

A beautiful but legally disconnected model fails the project gate.
