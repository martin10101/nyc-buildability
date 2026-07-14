# 3D Massing Engine Architecture

## Decision

Do **not** create a low-level 3D rendering engine from scratch.

Create the domain-specific **zoning geometry and massing engine** from scratch, using proven open-source rendering and geometry foundations.

The recommended stack is:

### Parcel-level 3D product experience

- **Three.js**
- **React Three Fiber**
- **Drei**

Use this for:

- Maximum zoning envelope
- Proposed massing
- Floors
- Setbacks
- Yards
- constraint planes
- Scenario comparison
- Smooth client-facing interaction
- Apple-grade camera and selection behavior

### Map and site selection

- **MapLibre GL JS**

Use this for:

- Address/property map
- Parcel selection
- Adjacent-lot selection
- Zoning overlays
- Landmark/flood/special-district layers
- Search result maps

### Citywide analytical visualization

- **deck.gl**

Use this for:

- Thousands or millions of property features
- Opportunity heatmaps
- Large polygon and point layers
- GPU-based filtering/highlighting
- Citywide deal-search visualization

### Canonical spatial storage and analysis

- **PostGIS in Supabase**

Use this for:

- Tax-lot geometry
- District/overlay intersections
- Adjacent-parcel discovery
- Spatial indexes
- Geometry versions
- Citywide search

### Deterministic geometry processing

- **Shapely in the Render Python service**

Use this for:

- Buffers
- Insets
- Setbacks
- Intersections
- Differences
- Unions
- Floor footprints
- Boundary validation
- 2D rule geometry

### Mesh creation and validation

- **Trimesh in the Render Python service**

Use when required for:

- Extruding floor footprints
- Mesh validation
- Watertight surfaces
- Export
- GLB generation
- Geometry metrics
- Server-generated model artifacts

### Runtime format

- **glTF/GLB**

Use GLB for portable, compact scene delivery and caching.

### Optional future city-scale context

- **CesiumJS**

Use only if the product later requires:

- Massive 3D Tiles streaming
- Globe-scale visualization
- Photorealistic city context
- Large external 3D city datasets

CesiumJS is not the primary parcel scenario editor because the product needs tightly controlled, minimal, custom interaction around one property and its development scenarios.

---

## 1. What is custom versus open source

### Open-source foundation

The team does not need to build:

- WebGL renderer
- Camera math
- Scene graph
- Material system
- Map renderer
- Polygon intersection engine
- Spatial database
- Mesh file format
- Generic orbit controls

### Custom product logic

The team must build:

- Zoning envelope generator
- Applicability-to-geometry translator
- Height-plane generator
- Yard/setback generator
- Floor-plate generator
- FAR allocation engine
- Use stacking
- Scenario massing generator
- Constraint visualization
- Existing-versus-potential comparison
- Assemblage geometry
- Rule-to-shape provenance
- Geometry verification
- Client-friendly interaction model

This custom layer is the defensible product.

---

## 2. Geometry truth model

The canonical truth is not the Three.js scene.

The canonical truth is a versioned scenario-geometry object generated from:

- Property geometry version
- Source facts
- User assumptions
- Rule-release version
- Rule-evaluation trace
- Scenario inputs
- Geometry-generator version

Example:

```json
{
  "scenario_id": "uuid",
  "geometry_version": 3,
  "coordinate_reference_system": "projected-local-crs",
  "property_geometry_version_id": "uuid",
  "rule_release_id": "uuid",
  "generator_version": "massing-1.0.0",
  "footprints": [],
  "floors": [],
  "constraint_surfaces": [],
  "existing_building": {},
  "metrics": {},
  "source_links": [],
  "coverage_status": "conditional"
}
```

Three.js renders this object. It does not invent or become the source of the geometry.

---

## 3. Coordinate strategy

Government GIS geometry should remain in its authoritative/projected CRS in storage.

For browser rendering:

1. Select a stable local origin near the parcel centroid.
2. Transform geometry into local meter- or foot-based coordinates.
3. Preserve the transformation metadata.
4. Render close to the local origin to avoid floating-point jitter.
5. Convert measurements back to official units for display and reports.

All geometry APIs must state:

- CRS
- Horizontal unit
- Vertical unit
- Axis order
- Local-origin transform
- Precision grid

---

## 4. Massing-generation pipeline

```text
Official lot geometry
        ↓
Geometry validity and CRS normalization
        ↓
Applicable rule evaluation
        ↓
Constraint primitives
  - yards
  - setbacks
  - street wall
  - height zones
  - lot coverage
        ↓
Buildable 2D regions by elevation band
        ↓
Floor plate generation
        ↓
FAR allocation and floor stacking
        ↓
Mesh construction
        ↓
Geometry validation
        ↓
Scenario metrics
        ↓
GLB + structured geometry JSON
        ↓
Three.js viewer
```

---

## 5. Core scene layers

Every layer is independently toggleable.

1. `parcel`
2. `neighbor_parcels`
3. `existing_building`
4. `maximum_envelope`
5. `proposed_massing`
6. `floor_plates`
7. `setback_planes`
8. `yard_zones`
9. `street_wall`
10. `height_limits`
11. `use_colors`
12. `unused_volume`
13. `noncompliant_volume`
14. `uncertain_geometry`
15. `context_buildings`
16. `measurements`
17. `selection_highlight`

No raw legal text is drawn in the scene. Selecting a shape opens a structured evidence panel.

---

## 6. Visual language

### Existing building
- Neutral matte gray
- Low visual priority

### Maximum envelope
- Transparent cool boundary
- Thin precise edges

### Proposed scenario
- Solid refined material
- Color by use only when needed

### Constraint
- Subtle line/plane by default
- Stronger on selection

### Violation
- Red only for actual failed deterministic constraints

### Conditional/uncertain
- Amber with dashed or patterned visual treatment

Do not use a rainbow GIS palette.

---

## 7. Required interactions

### Camera
- One-button reset
- Fit property
- Fit selected object
- Isometric preset
- Top plan
- Front/side
- Smooth transitions
- Sensible zoom limits
- No disorienting free-flight by default

### Selection
- Hover feedback
- Click selection
- Clear selected state
- Keyboard escape
- Selection sync between 3D, floor stack, and evidence panel

### Scenario comparison
- Side-by-side
- Ghost overlay
- Animated morph only when topology permits
- Metric-difference panel

### Floor inspection
- Floor slider
- Cutaway
- Exploded stack
- Isolate floor
- Use-based filter

### Measurement
- Height
- Horizontal distance
- Area
- Elevation
- Clear measurement

---

## 8. Performance budgets

Target on a normal modern browser:

- Viewer shell interactive quickly
- Progressive context loading
- Parcel and main massing prioritized
- Avoid loading an entire city 3D scene for one-property analysis
- Use instancing for repeated context buildings
- Use level of detail
- Compress GLB where useful
- Dispose meshes, materials, textures, and event listeners
- Pause rendering when viewer is not visible where safe
- Avoid expensive shadows by default
- Use subtle ambient/contact shadow rather than cinematic rendering
- Maintain responsive interaction during scenario changes

Set explicit performance tests for:

- Initial scene load
- Camera movement frame stability
- Scenario switch
- Layer toggling
- Large floor count
- Assemblage case
- Context-building count
- Mobile/tablet fallback

---

## 9. API contracts

Suggested endpoints:

- `GET /api/v1/scenarios/{id}/geometry`
- `GET /api/v1/scenarios/{id}/model.glb`
- `GET /api/v1/properties/{bbl}/context-geometry`
- `POST /api/v1/scenarios/{id}/regenerate-geometry`
- `POST /api/v1/geometry/measure`
- `GET /api/v1/scenarios/{id}/geometry-evidence`

Structured geometry JSON is required even if GLB is available.

---

## 10. Geometry quality gates

A scenario geometry cannot be accepted unless:

- Lot geometry matches the stored source version
- Geometry uses declared units and CRS
- Polygon operations are valid
- Floor plates remain within the applicable buildable region
- Height does not exceed the evaluated constraint
- Zoning floor area reconciles with the scenario calculation within documented tolerance
- Use allocation reconciles with the floor stack
- Mesh has no unexplained inverted or missing faces
- Visual selection links to the correct evidence record
- A reviewer runs the acceptance scenes in `3D_VISUAL_ACCEPTANCE_STANDARD.md`

---

## 11. Non-goals

The first 3D engine is not:

- Photorealistic architectural rendering
- Finished façade design
- Permit-ready BIM
- Structural analysis
- Mechanical design
- A replacement for Revit
- A generative art tool

Its job is accurate, attractive, interactive development massing and constraint communication.
