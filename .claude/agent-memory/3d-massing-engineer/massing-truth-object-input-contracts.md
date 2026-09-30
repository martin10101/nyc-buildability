---
name: massing-truth-object-input-contracts
description: Input-shape contracts and geometry invariants for the server-side massing truth object (M5-T082 massing_model.py) that future 3D/CAD packets consume
metadata:
  type: project
---

The deterministic massing truth object lives in
`services/api/app/scenario/massing_model.py` (`build_massing_model`,
`build_from_generated_option`, `MassingModel`); it is the server-side geometry truth
that every 3D view and the CAD export read (architecture doc sections 2-4, 10).

**Why:** these input-shape facts are not obvious from a single file read and are the
seams the next massing/CAD/wiring packets must mirror exactly (guessing shapes fails
closed).

**How to apply** when extending massing / wiring a route / building CAD export:
- The B0 proposal contract (`app/scenario/proposal.py`, read-only) DOES carry
  per-floor heights: `levels[].floor_count` identical floors of
  `levels[].floor_to_floor_ft`. No separate floor-stack input is needed - expand
  levels into a per-floor band stack (z from 0). A level may carry its own `outline`
  (setback/tower band).
- The max-envelope generated option is `MaxEnvelope.as_dict()["candidate"]`, itself a
  B0 `proposed_massing` block (outline/levels/exterior_walls/provenance); `candidate`
  is `None` when the engine emitted a typed placement gap -> refuse
  `no_generated_candidate`, never fabricate.
- Canonical MapPLUTO ring (connector) is OPEN + exterior-CCW; the B0 outline is
  EXPLICITLY closed (`vertices[0]==vertices[-1]`). `_prepare_ring` normalizes both
  (drop closing dup, reorient CCW, collapse collinear straight vertices so caps and
  side walls share one boundary).
- Honesty vocabulary (D-076-R002/D-083): the ONLY building labels are `proposed`
  ("Proposed - not a city record") and `generated_option` ("Generated building
  option"). The words permitted / approved / maximum-allowed are banned everywhere in
  the module (a test greps the source).
- Geometry invariants proven by tests: per-floor closed prisms are checked via
  directed-edge-uniqueness (each directed edge once, its reverse once) - this is what
  catches a reversed face winding; outward orientation == signed volume > 0 (reduced
  in LOCAL coords for conditioning at NYC 1e6 magnitudes); ear-clip cap area == shapely
  area and prism volume == plate_area x height, both to 1e-9 relative.
- Coordinates stored in authoritative world 2263; `coordinate_reference_system`
  carries the local origin (near centroid) + exact world->local offset + precision
  grid (1e-6 ft, 6-dp quantization) so the golden sha256 is cross-runner stable.
- Refusals are typed `MassingModelError(reason=...)`; footprint-outside-lot is
  `shapely lot.buffer(tol).contains(floor)` and is NEVER clipped.
