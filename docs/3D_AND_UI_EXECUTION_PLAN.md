# 3D and Premium UI Execution Plan

## Continuation rule

This plan is added to the existing project-control system.

It must not replace previous task history.

The orchestrator must:

1. Read current state.
2. Identify dependencies.
3. Add new task IDs.
4. Preserve accepted work.
5. Start only unblocked tasks.
6. Replan after every accepted task.

---

## Workstream A — Architecture and contracts

### 3D-001: 3D architecture ADR
Producer: cloud-architect  
Reviewer: code-reviewer

Deliverables:
- Technology decision
- Deployment boundary
- Geometry truth model
- API contracts
- Storage strategy
- Performance risks
- Licensing inventory

Acceptance:
- No render engine built from scratch
- Canonical geometry remains server/domain data
- Browser scene is not source of truth
- Low-storage policy preserved

### 3D-002: Scenario geometry schema
Producer: 3d-massing-engineer  
Reviewer: geospatial-engineer

Deliverables:
- JSON schema
- Versioning
- CRS/unit contract
- Geometry/source trace
- Example fixtures

Tests:
- Normal parcel
- Irregular parcel
- Hole/courtyard
- Split lot
- Assemblage
- Invalid geometry
- Unit mismatch

---

## Workstream B — Backend geometry

### 3D-010: Constraint primitive generator
Producer: 3d-massing-engineer  
Reviewer: rules-engineer

Generate:
- Yard regions
- Setback regions
- Height bands
- Street-wall lines
- Buildable polygons

Gate:
Every primitive links to a rule-evaluation trace.

### 3D-011: Floor plate and FAR allocator
Producer: 3d-massing-engineer  
Reviewer: scenario-optimization-engineer

Gate:
Floor area reconciles with scenario metrics within documented tolerance.

### 3D-012: Mesh/GLB pipeline
Producer: 3d-massing-engineer  
Reviewer: qa-engineer

Deliverables:
- Mesh generation
- Validation
- GLB export
- Compression decision
- Artifact storage
- Cache/version keys

---

## Workstream C — Viewer

### 3D-020: Viewer foundation
Producer: frontend-engineer + 3d-massing-engineer  
Reviewer: visual-quality-reviewer

Implement:
- React Three Fiber canvas
- Camera presets
- Layer system
- Selection
- Inspector sync
- Loading/error fallback

### 3D-021: Scenario comparison
Producer: frontend-engineer  
Reviewer: human-journey-reviewer

Implement:
- Existing/envelope/proposed
- Side-by-side
- Overlay
- Metric differences

### 3D-022: Floor stack and cutaway
Producer: frontend-engineer  
Reviewer: visual-quality-reviewer

Implement:
- Floor slider
- Isolate
- Exploded stack
- Stack chart sync

### 3D-023: Geometry evidence
Producer: frontend-engineer  
Reviewer: data-contract-verifier + rules-engineer

Gate:
Selected geometry opens the correct source and calculation trace.

---

## Workstream D — Premium product system

### UI-001: Product information architecture
Producer: product-design-director  
Reviewer: human-journey-reviewer

### UI-002: Token and component specification
Producer: product-design-director  
Reviewer: frontend-engineer + visual-quality-reviewer

### UI-003: Application shell
Producer: frontend-engineer  
Reviewer: visual-quality-reviewer

### UI-004: Property and potential flows
Producer: frontend-engineer  
Reviewer: human-journey-reviewer

### UI-005: Scenario and evidence flows
Producer: frontend-engineer  
Reviewer: visual-quality-reviewer + rules-engineer

### UI-006: Accessibility and responsive gate
Producer: frontend-engineer  
Reviewer: qa-engineer + visual-quality-reviewer

---

## Workstream E — Competitive capabilities

### COMP-001: Interactive assumptions
Producer: scenario-optimization-engineer  
Reviewer: rules-engineer

### COMP-002: Assemblage and air-rights analysis
Producer: geospatial-engineer  
Reviewer: rules-engineer + professional-review gate

### COMP-003: Financial feasibility
Producer: financial-feasibility-engineer  
Reviewer: qa-engineer

### COMP-004: Opportunity search
Producer: opportunity-search-engineer  
Reviewer: data-contract-verifier + qa-engineer

### COMP-005: Explainable opportunity score
Producer: opportunity-search-engineer  
Reviewer: human-journey-reviewer

### COMP-006: Professional-review package
Producer: backend-engineer + frontend-engineer  
Reviewer: security-reviewer + human-journey-reviewer

### COMP-007: External API surface
Producer: backend-engineer  
Reviewer: security-reviewer + code-reviewer

---

## Gate requirements

Every 3D task requires:

- Producer examples
- Automated geometry tests
- Golden-scene fixture
- Calculation reconciliation
- Independent visual walkthrough
- Performance evidence
- Accessibility evidence
- Error-state evidence
- Storage cleanup evidence
- Orchestrator acceptance

Every premium UI task requires:

- Task-based walkthrough
- Five-second hierarchy test
- Keyboard flow
- Reduced-motion test
- Narrow-width test
- Loading/error/empty states
- Visual regression evidence
- No default template appearance

---

## First recommended unblocked work

The orchestrator must decide based on current project state.

Typical order:

1. 3D-001 architecture ADR
2. UI-001 information architecture
3. 3D-002 schema
4. UI-002 tokens/components
5. Backend geometry only after property/rule/scenario contracts stabilize
6. Viewer only after a stable geometry fixture exists

Do not let the viewer team invent geometry while waiting.
Use versioned fixtures created by 3D-002.
