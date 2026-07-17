# 3D Visual Acceptance Standard

## Purpose

Require the 3D system to pass both mathematical and human-style review.

A screenshot that “looks correct” is insufficient.

---

## Required golden scenes

1. Rectangular interior lot
2. Corner lot
3. Irregular polygon
4. Through lot
5. Courtyard/hole geometry
6. Multiple height bands
7. Upper-floor setback
8. Existing building enlargement
9. Demolition/new building
10. Mixed-use stack
11. Assemblage
12. Split zoning district
13. Data-conflict case
14. Missing critical input
15. Deterministic violation
16. Conditional geometry

---

## Mathematical checks

For every scene verify:

- Parcel coordinates
- Area
- Perimeter where relevant
- CRS and units
- Buildable region
- Setback distances
- Yard dimensions
- Base and maximum height
- Floor elevations
- Floor-plate area
- Total zoning floor area
- Use allocations
- Scenario metrics
- Rule trace IDs

---

## Human walkthrough

The reviewer must:

1. Open the property.
2. Identify existing building, envelope, and proposed massing without instructions.
3. Switch scenarios.
4. Select a floor.
5. Toggle a constraint.
6. Open its evidence.
7. Verify the displayed formula/source matches the selected geometry.
8. Use top, front, and isometric views.
9. Measure one known height and one known setback.
10. Trigger a missing-data state.
11. Trigger a violation state.
12. Confirm conditional geometry is not presented as verified.
13. Use keyboard navigation.
14. Use reduced motion.
15. Test a narrow viewport.

---

## Visual criteria

Pass only when:

- Property remains centered and understandable
- Camera never clips or loses the site during normal use
- Layer names are client-friendly
- Colors remain restrained
- Selected object is obvious
- Evidence panel does not cover critical geometry unnecessarily
- Status can be understood without color
- Scenario change is smooth and not disorienting
- Context buildings do not overpower the site
- Labels do not overlap excessively
- Controls are grouped by task
- Loading is progressive and informative
- Errors preserve already-loaded useful information

---

## Performance evidence

Record:

- Scene payload size
- Time to parcel display
- Time to primary massing display
- Scenario-switch duration
- Peak browser memory
- Interaction stability
- Geometry generation duration
- Cache behavior

---

## Reviewer independence

The producer cannot run the final visual acceptance gate.

The `visual-quality-reviewer` performs final visual acceptance.

The `qa-engineer` verifies reproducibility.

The orchestrator alone accepts the task.
