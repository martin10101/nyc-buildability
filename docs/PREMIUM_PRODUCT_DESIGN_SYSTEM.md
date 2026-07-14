# Premium Product Design System

## Product-quality objective

The application must feel like a modern premium decision product, not legacy municipal software, a crowded GIS dashboard, or an engineering control panel.

The design target is:

- Calm
- Precise
- Spacious
- Obvious
- Trustworthy
- Fast
- Visually refined
- Accessible
- Consistent

“Apple-grade” means disciplined hierarchy and interaction quality, not copying Apple branding.

---

## 1. Core interface rule

Show the user only what is needed for the current decision.

Use progressive disclosure:

```text
Simple summary
    ↓
Scenario comparison
    ↓
Detailed metrics
    ↓
Calculation trace
    ↓
Exact legal source
```

Do not place all layers, filters, legal sections, assumptions, maps, and warnings on one screen.

---

## 2. Primary product navigation

Use a restrained structure:

1. **Property**
2. **Potential**
3. **Scenarios**
4. **3D**
5. **Financials**
6. **Evidence**
7. **Review**

Administrative functions live separately.

Each area has a clear purpose.

### Property
Official facts, conflicts, missing information, and assumptions.

### Potential
Headline buildability metrics and constraints.

### Scenarios
Comparison and selection.

### 3D
Envelope, massing, layers, floor inspection, and measurements.

### Financials
Editable business assumptions and sensitivity.

### Evidence
Calculations, rule sections, source versions, and provenance.

### Review
Professional-review status, questions, and sign-off.

---

## 3. Page composition

Use a consistent shell:

- Slim top bar
- Narrow optional left navigation
- Main content canvas
- Contextual right inspector
- One dominant action per view

For the 3D page:

```text
┌──────────────────────────────────────────────────────────┐
│ Property / Scenario selector              Export / Share │
├───────────┬──────────────────────────────┬───────────────┤
│ Minimal   │                              │ Contextual    │
│ tool rail │         3D canvas            │ inspector     │
│           │                              │               │
├───────────┴──────────────────────────────┴───────────────┤
│ Optional scenario/floor timeline                          │
└──────────────────────────────────────────────────────────┘
```

The 3D canvas remains visually dominant.

---

## 4. Control design

### Dropdowns
- Short, categorized lists
- Search only when needed
- Current choice clearly visible
- No giant ungrouped list
- Explanations for complex choices
- Safe defaults
- “Not sure” where legally meaningful

### Toggles
Use toggles only for true on/off states.

Do not use a switch for:
- Selecting one of five scenarios
- Choosing a zoning district
- Setting a numeric value

### Segmented controls
Use for:
- Existing / Envelope / Proposed
- 2D / 3D
- Summary / Detail
- Gross / Net

### Sliders
Use only when continuous adjustment is meaningful, with:
- Numeric input
- Unit
- Default marker
- Reset
- Valid range
- Effect preview

### Tooltips
Use sparingly for interface behavior, not to hide required legal information.

---

## 5. Design system foundation

Recommended frontend foundation:

- Radix UI primitives for accessible, unstyled behavior
- A carefully customized shadcn-style component codebase
- Tailwind/CSS variables for tokens and layout
- Motion for subtle production-grade transitions
- React Three Fiber for 3D
- A dedicated internal component library

Do not ship the default appearance of a component template.

Every component must be intentionally restyled to the product’s design tokens.

---

## 6. Tokens

Define central tokens for:

- Spacing
- Radius
- Border
- Surface
- Type scale
- Shadow
- Motion
- Focus ring
- Status
- 3D use colors
- Chart colors

### Spacing
Use a restrained scale and generous whitespace.

### Radius
Use a small number of radii:
- Small controls
- Standard cards
- Large panels/modals

### Shadows
Subtle depth only.
Avoid heavy floating-card shadows everywhere.

### Borders
Use quiet separators.
Avoid boxing every line of content.

---

## 7. Typography

Use one highly legible interface typeface.

Hierarchy:

- Property/scenario title
- Headline metric
- Section title
- Body
- Label
- Metadata

Numbers need:
- Tabular alignment where useful
- Clear units
- Consistent precision
- No unnecessary decimal noise

Example:

```text
40,000
sq. ft. maximum zoning floor area
```

Not:

```text
Maximum Zoning Floor Area: 40000.000000 SF
```

---

## 8. Status system

Status must be communicated by:

- Label
- Icon
- Color
- Explanation

Statuses:

- Verified
- Conditional
- Review required
- Data conflict
- Unsupported
- Not applicable

Never rely on color alone.

Avoid excessive red. Red is reserved for a real failed constraint or destructive action.

---

## 9. Scenario cards

Each scenario card should show:

- Scenario name
- Objective
- 3–5 headline metrics
- One concise advantage
- One concise concern
- Coverage status
- Small massing preview
- Compare/select action

Do not show 30 metrics in the collapsed card.

Details open in:
- Expanded panel
- Comparison table
- 3D view
- Evidence view

---

## 10. Evidence experience

The evidence viewer must be understandable to both professionals and clients.

Display:

1. Conclusion
2. Inputs
3. Formula
4. Result
5. Applicability reason
6. Rule source
7. Source version/effective date
8. Assumptions
9. Coverage status
10. Open official source

The legal text is available but not the first thing shown.

---

## 11. Motion

Use motion to explain state change:

- Scenario transition
- Inspector opening
- Floor isolation
- Result update
- Loading progress
- Success confirmation

Motion rules:

- Short
- Smooth
- Reversible
- No decorative bouncing
- Respect reduced-motion settings
- Never delay critical information

---

## 12. Empty, loading, and error states

### Loading
Show the actual pipeline:

- Resolving address
- Retrieving property facts
- Checking zoning layers
- Evaluating rules
- Generating scenarios
- Building 3D model

### Empty
Explain the next action.

### Error
State:
- What failed
- What remains available
- Whether retry is safe
- Whether user input is required

Do not show raw backend errors to users.

---

## 13. Responsive behavior

Desktop is the primary scenario-analysis environment.

Tablet:
- Full review and presentation support
- Simplified tool rail
- Collapsible inspector

Phone:
- Property summary
- Scenario cards
- Report/review
- Simplified 3D viewer
- Not the primary complex editing environment

---

## 14. Accessibility

Required:

- Keyboard navigation
- Visible focus
- Screen-reader labels
- Semantic controls
- Reduced motion
- Sufficient contrast
- No color-only status
- Accessible data tables
- Alternative text summary for 3D findings
- Keyboard-accessible layer and camera controls

---

## 15. Anti-clutter rules

Prohibited:

- More than one primary action per panel
- Unorganized filter walls
- Permanent display of all advanced assumptions
- More than three nested panel levels
- Tiny text to fit more data
- Icon-only controls without clear labels/tooltips
- Multiple competing accent colors
- Large legal paragraphs in the main scenario view
- Raw GIS layer names shown to end users
- Multiple modal dialogs stacked on each other

---

## 16. Visual acceptance

A screen fails visual review when:

- The main decision is not obvious in five seconds
- A user cannot identify the selected property/scenario
- More than one area appears visually dominant
- Controls are not grouped by task
- Status is ambiguous
- A dropdown contains an unstructured long list
- The 3D viewer has unexplained controls
- Layout shifts significantly while loading
- Mobile behavior hides critical warnings
- Design-system components drift between pages

The independent `visual-quality-reviewer` owns this gate.
