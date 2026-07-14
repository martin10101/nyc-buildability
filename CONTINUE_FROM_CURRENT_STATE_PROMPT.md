You are continuing the existing NYC Buildability production project.

A separate 3D, competitive-feature, and premium-UI expansion pack has just been added to the repository.

Do not restart the project.
Do not recreate accepted tasks.
Do not reset project-control state.
Do not replace the current architecture without an approved ADR.

First:

1. Read:
   - `.claude/rules/3d-ui-expansion.md`
   - `docs/COMPETITIVE_FEATURE_EXPANSION.md`
   - `docs/3D_MASSING_ENGINE_ARCHITECTURE.md`
   - `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md`
   - `docs/3D_AND_UI_EXECUTION_PLAN.md`
   - `docs/3D_VISUAL_ACCEPTANCE_STANDARD.md`

2. Inspect:
   - `project-control/state.json`
   - `project-control/master_plan.json`
   - `docs/IMPLEMENTATION_STATUS.md`, if present
   - Existing accepted checkpoints and gate reports
   - Existing database schema, API contracts, frontend architecture, and deployment configuration

3. Verify that these project subagents are discovered:
   - `3d-massing-engineer`
   - `product-design-director`
   - `visual-quality-reviewer`
   - `financial-feasibility-engineer`
   - `opportunity-search-engineer`

4. Create an integration report at:
   - `docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md`

The report must identify:

- Which existing tasks and architectural decisions remain valid
- Which new tasks are now required
- Dependencies between current work and the new 3D/UI workstream
- New database/API contracts required
- New producer and reviewer assignments
- Which tasks can start now
- Which tasks must wait for property, rule, scenario, or provenance foundations
- Storage and cloud-processing implications
- Risks and required quality gates

5. Add the new work to the existing project-control system using new task IDs. Do not edit past accepted task results.

6. Assign:
   - Geometry and massing production to `3d-massing-engineer`
   - Product information architecture and design-system production to `product-design-director`
   - Independent visual and interaction review to `visual-quality-reviewer`
   - Financial scenario work to `financial-feasibility-engineer`
   - Citywide deal-search work to `opportunity-search-engineer`

7. Enforce producer/reviewer separation. No agent may approve its own work.

8. Use the exact 3D technology decision in the architecture document unless a documented ADR proves a materially better option:
   - Three.js + React Three Fiber + Drei for the parcel-level interactive 3D experience
   - MapLibre GL JS for property and city map interaction
   - deck.gl for large citywide analytical layers
   - PostGIS + Shapely for canonical geometry and 2D spatial calculation
   - Trimesh for mesh construction, validation, and GLB export where server-side mesh generation is needed
   - glTF/GLB as the portable runtime model format
   - CesiumJS only as an optional later city-scale/photorealistic context layer, not the core parcel editor

9. Do not generate a fake 3D building from AI prose. Every vertex, setback, height plane, footprint, and floor plate must originate from normalized geometry and a calculation trace.

10. Continue automatically from the first new unblocked task after the integration report and task-plan update are independently reviewed.
