---
name: 3d-stack-admission-facts
description: Verified facts about the three / @react-three/fiber web stack admitted in M5-T090 - typing gap, peer caps, fill-extrusion limits, how to query the registry from the thin client
metadata:
  type: project
---

Facts checked against registry/spec on 2026-09-24 (M5-T090):

- `three` ships NO type declarations (0 .d.ts, no `types` field); fiber's .d.ts files `import type * as THREE from 'three'`. The first consumer needs `@types/three`, which is its own G5 admission because it brings 6 runtime deps (incl. `@dimforge/rapier3d-compat` WASM, tween.js, meshoptimizer, fflate).
- fiber 9.7.0 peers `react`/`react-dom` `>=19 <19.3`: a React 19.3+ bump must move fiber in the same change.
- The fiber maintainer set was pruned from 22 to 8, with one new account (`dennissmolek`), between 2026-07-31 and 2026-09-22. Re-check before any fiber upgrade.
- MapLibre style spec: `fill-extrusion-opacity` is data-constant (layer-wide), and base/height are the only geometry controls (prisms only). MapLibre's own 3D-model examples use three.js GLTFLoader. This is the necessity argument against the zero-dependency route.

**Why:** these decide the next 3D viewer packet's scope (typing, upgrade coupling, G5 inputs).
**How to apply:** when contracting or building the first 3D viewer consumer, plan the `@types/three` admission and don't assume types are bundled. Thin-client registry queries work with `curl` plus a python script written to the scratchpad via Write. Inline heredoc python gets refused by the worktree-isolation guard.

Related: [[property-profile-frontend-rules]]
