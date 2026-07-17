# 3D and Premium UI Expansion Rule

This repository contains a separately added 3D/UI expansion.

When this file is present:

1. Read all new expansion documents before planning related work.
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
11. Require visual, mathematical, performance, accessibility, and human-journey gates.
12. Follow the premium product design rules; do not ship a default dashboard template.
13. The main orchestrator must update the existing master plan and continue from the first unblocked task.
