# Competitive Feature Expansion

## Purpose

Expand NYC Buildability from a property calculator into a complete, traceable development-intelligence platform that competes with zoning, massing, assemblage, air-rights, and property-opportunity products.

The goal is not to copy competitors' visual language or proprietary logic. The goal is to adopt the strongest product patterns while preserving this platform's differentiator:

> Every property fact, rule, number, scenario, shape, assumption, and warning must be traceable to an official source and a versioned calculation.

---

## 1. Core features to add

### 1.1 Interactive 3D zoning and massing

Make 3D a primary product surface, not a late decorative feature.

Required layers:

- Tax-lot geometry
- Existing building mass
- Maximum zoning envelope
- Selected proposed massing
- Alternate scenario massings
- Required yards and setbacks
- Base-height and maximum-height zones
- Street-wall lines
- Lot-line/window-risk zones
- Surrounding buildings for context
- Use-based coloring
- Floor plates
- Constraint overlays
- Unused development potential
- Noncompliant geometry

Required interactions:

- Orbit
- Pan
- Zoom
- Reset camera
- Top/front/side/isometric presets
- Select a floor
- Select a constraint plane
- Isolate a use
- Toggle existing/proposed/envelope
- Compare two scenarios
- Animate between scenarios
- Cutaway/floor-stack mode
- Measure distance, height, and area
- Open the evidence panel for a selected geometric constraint

---

### 1.2 Interactive assumptions and incentive toggles

Users must be able to switch relevant development assumptions on and off and immediately see recalculated results.

Examples:

- Residential only
- Mixed use
- Ground-floor commercial
- Affordable-housing option
- Transit-related provision
- Adjacent-lot assemblage
- Air-rights transfer
- Enlargement versus demolition/new building
- Conservative versus maximum envelope
- Discretionary approval path
- Alternate floor-to-floor height
- Different core/efficiency assumptions

Changing a toggle must update:

- Rule applicability
- Calculated development capacity
- 3D geometry
- Floor-by-floor stack
- Unit estimate
- Financial result
- Risk status
- Required professional-review items

The backend state machine controls changes. AI does not directly mutate scenario values.

---

### 1.3 Air-rights and assemblage analysis

Support:

- Adjacent-lot selection
- Hypothetical zoning-lot combinations
- Existing built FAR by component lot
- Unused development rights
- Potential transferable rights
- Ownership differences
- Split-district conditions
- Zoning-lot-development-agreement warning
- Landmark-transfer flag
- Before/after comparison
- Combined massing
- Acquisition assumptions
- Professional-review requirements

The system must distinguish:

- Physically adjacent parcels
- Parcels potentially usable in one zoning lot
- Rights that are mathematically unused
- Rights that are legally transferable
- Rights requiring special approvals
- Rights not yet evaluated

---

### 1.4 Citywide opportunity search

Add the reverse workflow:

> Find properties that satisfy a development strategy.

Search filters may include:

- Borough/neighborhood/map area
- Zoning district
- Lot area and width
- Existing FAR utilization
- Unused floor area
- Minimum height potential
- Transit proximity
- Landmark exclusion
- Flood exclusion
- Special-district exclusion/inclusion
- Ownership
- Existing use/building class
- Estimated acquisition range
- Assemblage potential
- Air-rights potential
- Minimum opportunity score
- Data completeness

Results:

- Map
- Ranked list
- Explainable opportunity score
- Saved search
- Export
- Open full property analysis
- Alert when official data changes

---

### 1.5 Financial feasibility

Every physical scenario should optionally include:

- Acquisition price
- Hard cost
- Soft cost
- Financing and carry
- Demolition
- Affordable-housing assumptions
- Net/gross efficiency
- Rent or sale assumptions
- Vacancy
- Operating costs
- NOI
- Yield
- Estimated profit
- Margin
- Return on cost
- Sensitivity analysis
- Risk-adjusted score

All financial assumptions must be editable, versioned, and clearly separated from official property facts.

The system must never present a financial estimate as an official government fact.

---

### 1.6 Floor stacking

Every scenario should include a floor-by-floor stack:

- Floor number/elevation
- Use
- Gross floor plate
- Zoning floor area
- Estimated net area
- Unit range
- Commercial/community-facility area
- Core/corridor/shaft assumption
- Parking/mechanical/cellar allocation
- Setback transition
- Terrace/open area
- Verification status

The floor stack and 3D model must use the same scenario data object.

---

### 1.7 Existing versus potential

Required visual comparison:

- Existing building: neutral gray
- Maximum envelope: translucent boundary
- Proposed scenario: solid surface
- Unused feasible volume: optional translucent layer
- Noncompliant portion: red/error pattern
- Data-uncertain portion: amber/dashed treatment

Required metrics:

- Existing floor area
- Existing FAR
- Permitted/conditional FAR
- Unused capacity
- Enlargement potential
- Demolition/new-build potential
- Existing legal-noncompliance warning
- Source confidence

---

### 1.8 Explainable opportunity score

Create a score only when every component is visible.

Possible components:

- Unused development capacity
- Lot configuration
- Assemblage potential
- Zoning complexity
- Transit accessibility
- Existing-building burden
- Landmark/flood/special constraints
- Financial margin
- Data completeness
- Professional-review burden

Never show only one unexplained number.

---

### 1.9 Professional-review escalation

Add a controlled workflow:

1. User requests review.
2. System freezes a reproducible analysis version.
3. Reviewer receives:
   - Property profile
   - Source snapshots
   - Applied rule versions
   - Assumptions
   - Calculations
   - Scenarios
   - 3D geometry
   - Floor stack
   - Financial model
   - Unresolved questions
4. Reviewer can:
   - Confirm
   - Modify
   - Reject
   - Ask a question
   - Request a source refresh
5. The original automated result remains preserved.

---

### 1.10 API product

Plan a public/private API layer for:

- Property profile
- Zoning capacity
- Rule evaluation
- Scenario generation
- Massing metadata
- GLB/scene artifact
- Opportunity search
- Report generation
- Professional-review status

API clients must receive provenance and coverage status, not only final numbers.

---

## 2. Competitive differentiation

Do not compete only on:

- Fast reports
- Attractive 3D blocks
- Maximum FAR
- A proprietary score

Compete on:

- Source-level provenance
- Historical reproducibility
- Data-conflict detection
- Versioned legal corpus
- Human-approved machine rules
- Independent quality gates
- Practical code-feasibility flags
- Custom objectives
- Financial and physical integration
- Explainable geometry
- Professional-review workflow
- API access
- Future Revit connection

---

## 3. Product rule

No competitor-derived feature may bypass the established legal and data controls.

For example:

- A beautiful massing with no calculation trace is invalid.
- An opportunity score with hidden components is invalid.
- An AI recommendation with no applicable-rule set is invalid.
- An air-rights number without transferability status is invalid.
- A financial projection without versioned assumptions is invalid.
