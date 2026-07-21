---
paths:
  - "apps/web/**"
---
# 3D and Premium UI Expansion Rule

Path-scoped (2026-07-21): loads only when touching `apps/web/**`, not on every session. The
still-active owner planning hold and dispatch history live in the unconditional
`.claude/rules/expansion-agent-dispatch-hold.md`; this file holds the technical/quality rules for
3D and premium-UI work.

This repository contains a separately added 3D/UI expansion. When doing 3D/premium-UI work:

1. Read the relevant expansion documents before planning related work (`docs/3D_MASSING_ENGINE_ARCHITECTURE.md`, `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md`, `docs/3D_VISUAL_ACCEPTANCE_STANDARD.md`, `docs/3D_AND_UI_EXECUTION_PLAN.md`, `docs/COMPETITIVE_FEATURE_EXPANSION.md`).
2. Do not reset existing project-control state.
3. Preserve accepted tasks, evidence, and gates.
4. Add new work as dependent tasks with new IDs.
5. Use:
   - Three.js + React Three Fiber + Drei for parcel-level 3D
   - MapLibre GL JS for maps
   - deck.gl for large citywide analytical layers
   - PostGIS + Shapely for canonical spatial calculations
   - Trimesh for server-side mesh validation/export when needed
   - glTF/GLB for runtime model artifacts
6. Do not build WebGL or a general rendering engine from scratch.
7. Do build custom zoning-envelope, constraint-geometry, floor-plate, massing, comparison, and provenance logic.
8. Never let AI prose directly define geometry.
9. No shape is accepted without a calculation and provenance trace.
10. Apply producer/reviewer separation to all visual work.
11. Require visual, mathematical, performance, accessibility, and human-journey acceptance evidence. These are evidence requirements within the existing G3 (independent human-style walkthrough) and G4 (integration and regression) gates of the `docs/GATES_AND_CHECKPOINTS.md` G0–G7 catalog, not a parallel gate system.
12. Follow the premium product design rules; do not ship a default dashboard template.
13. Continuation onto the expansion workstream (updating the master plan and starting the first unblocked task after owner review of the integration report) is **SUSPENDED pending owner review** — see `.claude/rules/expansion-agent-dispatch-hold.md §2`. Do not start expansion tasks or change the plan on this item until the owner releases that hold.
