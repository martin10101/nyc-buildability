# NYC Buildability — Generative Development Strategy Requirements

**Status:** Approved product requirement; not yet proof of implementation  
**Applies to:** Scenario generation, massing, layout estimation, financial feasibility, strategy, comparison, 3D, evidence, and professional review  
**Repository placement:** Project root  
**Operating rule:** Integrate additively. Do not replace accepted architecture, contracts, provenance rules, task gates, or current in-flight work.

## 1. Required outcome

NYC Buildability must become more than an accurate zoning calculator or a tool that places one conventional building inside a legal envelope. It must deliberately search a broad solution space, compare materially different lawful development concepts, and explain the strategic tradeoffs that an experienced NYC architect or developer would examine.

The system must combine five separate capabilities:

1. **Verified truth layer** — official property facts, versioned deterministic zoning and code-related rules, assumptions, conflicts, and provenance.
2. **Generative design-search engine** — creates many materially different candidate massings and development programs within explicit constraints.
3. **Deterministic evaluation engine** — tests legality, geometry, preliminary planning feasibility, constructability proxies, efficiency, and financial results.
4. **Multi-objective optimizer** — returns a Pareto set and objective-specific winners instead of pretending that one building is universally best.
5. **Developer-strategy intelligence** — proposes and explains high-value moves on top of verified calculations without changing or inventing them.

The target product is a decision-support partner that can search more combinations than a person can draw manually while remaining traceable, reproducible, and honest about uncertainty.

## 2. This requirement must not derail the current roadmap

This file does not authorize a large uncontracted implementation or a change to the current execution priority. The verified property-profile slice, official-source connectors, canonical contracts, deterministic rule engine, and canonical geometry foundation remain prerequisites.

When this file enters the repository, the orchestrator must:

1. Inventory overlap with the existing competitive-feature, 3D massing, UI, financial-feasibility, and opportunity-search documents.
2. Preserve the existing project-control lifecycle and create explicit tasks using the repository's current task-ID convention.
3. Add this capability to the roadmap in dependency order rather than attempting one monolithic implementation.
4. Update existing canonical documents instead of creating competing architectures.
5. Contract the data interfaces and acceptance fixtures before building the optimizer or strategy layer.
6. Keep current accepted and in-flight work intact unless a specific reviewed conflict is found.

## 3. Non-negotiable separation of authority

### 3.1 Deterministic legal and geometry authority

Deterministic, versioned code is the only authority for:

- Property facts and source reconciliation
- Zoning district and lot conditions
- Permitted uses and floor-area calculations
- Height, setback, street-wall, yard, court, lot-coverage, parking, loading, and other encoded constraints
- Inclusionary or affordability calculations
- Canonical parcel, envelope, and candidate geometry
- Unit conversions and financial arithmetic
- Constraint pass/fail results

No language model may silently change these values, waive a failed constraint, repair missing evidence, or relabel an unsupported conclusion as verified.

### 3.2 Strategy intelligence authority

Strategy intelligence may:

- Propose candidate parameters, typologies, search directions, and counterfactuals
- Explain why one candidate performs differently from another
- Identify information that may unlock value
- Suggest professional questions, diligence, or negotiations
- Summarize tradeoffs in plain language

Every suggestion must be passed through machine validation. If it depends on missing facts, an unsupported rule family, owner negotiations, a discretionary approval, or professional judgment, that dependency must be explicit.

### 3.3 Independent status dimensions

Never collapse the following into one confidence label:

- **Legal status:** verified as-of-right, conditional, discretionary, professional review required, unsupported, data conflict, or not applicable
- **Geometric status:** conceptual, coarse validated, detailed validated, or failed
- **Planning status:** proxy only, preliminary feasible, professional review required, or failed
- **Financial status:** assumption-based estimate, sensitivity range, or unavailable
- **Evidence status:** complete, partial, conflicting, stale suspected, or missing

A zoning-compliant envelope is not automatically a code-compliant, constructible, financeable, or marketable building.

## 4. Canonical system flow

```text
Official facts and reconciled property profile
→ Versioned deterministic constraints
→ Canonical zoning envelope
→ Candidate grammar and seeded candidate generation
→ Fast constraint pruning
→ Detailed geometry and planning evaluation
→ Cost, revenue, schedule, and risk evaluation
→ Multi-objective ranking and Pareto frontier
→ Strategic alternatives and explanations
→ Interactive comparison, 3D review, and professional sign-off
```

Every run must retain the property-profile version, rule-set version, assumption-set version, cost-model version, market-model version, candidate-generator version, optimizer version, random seed, candidate lineage, rejection reasons, and timestamps needed to reproduce it.

## 5. Candidate design grammar

The generator must not rely on free-form AI geometry. It must use a deterministic, testable vocabulary of parameters and typologies. As supported rules mature, the grammar should vary at least:

- Building footprint and lot coverage
- Street-wall position and continuity
- Rear-yard, side-yard, and court configuration
- Setback elevations and depth
- Overall height, story count, and floor-to-floor heights
- Base, podium, tower, wing, courtyard, bar, L, U, and other applicable typologies
- Floor-plate dimensions, orientation, and depth
- Core count, core position, and preliminary core geometry
- Elevator, stair, shaft, riser, and service-zone assumptions
- Structural grid, spans, transfers, cantilevers, and column regularity proxies
- Residential, commercial, community-facility, parking, amenity, and mechanical allocation
- Ground-floor lobby, retail frontage, loading, refuse, ramp, and back-of-house zones
- Unit mix, unit depth, unit frontage, and preliminary unit stacking
- Affordable-unit distribution where applicable
- Balcony, terrace, roof, and setback opportunities
- Cellar, basement, mechanical, and floor-area-exemption assumptions only where verified rules support them
- Parking layout and access concepts
- Construction phasing or occupied-site constraints where relevant

Candidate families must be extensible. A new typology or strategy must be addable without rewriting the legal engine.

## 6. Architect and developer reasoning that must be encoded

The product must progressively encode the following reasoning as transparent heuristics, metrics, constraints, search operators, or professionally approved precedents—not as hidden prompt intuition.

### 6.1 Site and urban context

- Corner versus interior lot opportunities
- Multiple frontages, wide/narrow street conditions, party walls, and street hierarchy
- Irregular, shallow, deep, narrow, sloped, split-zone, or through-lot conditions
- Existing buildings, demolition versus reuse, easements, curb cuts, and access limitations
- Adjacent buildings, lot-line windows, party-wall opportunities, sensitive adjacencies, and blocked or valuable views
- Sun, daylight, noise, privacy, flood, subsurface, transit-adjacency, and construction-staging constraints when supported by data
- Best placement of residential entrance, retail, loading, parking, refuse, and mechanical access
- Neighborhood-specific frontage, use, unit, and amenity assumptions, clearly labeled as market inputs rather than legal facts

### 6.2 Floor-plate and core intelligence

- Move or rotate the core to improve usable perimeter, net-to-gross efficiency, unit planning, egress, or structure
- Test central, side, party-wall, split, and other applicable core concepts
- Balance elevator and stair counts against height, population, travel, waiting-time, and rentable-area effects
- Reduce excessive corridors, dead ends, leftover wedges, unusable depth, and non-rentable corners
- Align cores, shafts, kitchens, bathrooms, structure, and mechanical risers vertically where possible
- Recognize when a smaller or shallower floor plate produces better daylight and more valuable units
- Recognize when a shorter, wider, simpler building may outperform a taller maximum-envelope option
- Distinguish zoning floor area, gross floor area, construction area, net rentable/sellable area, and usable residential area

Early planning metrics are proxies, not claims of final architectural or code compliance.

### 6.3 Unit and marketability intelligence

- Generate alternative unit mixes instead of treating unit count as the only residential goal
- Estimate window opportunities, perimeter efficiency, unit depth, corner-unit opportunities, and daylight proxies
- Penalize awkward proportions, deep internal zones, poor furniture zones, excessive circulation, and avoidable single-aspect compromises
- Reward useful terraces, views, corner exposure, higher floors, privacy, and efficient layouts only through explicit market assumptions
- Test whether sacrificing a small amount of gross or zoning floor area materially improves net area, unit quality, absorption, or revenue
- Model affordable-unit placement, bedroom mix, and distribution through verified program rules and explicit developer preferences
- Keep qualitative labels such as “premium” or “pleasant” tied to visible assumptions and professional review

### 6.4 Constructability and operations intelligence

- Penalize unnecessary transfers, cantilevers, setbacks, façade complexity, irregular grids, excessive structure, and difficult waterproofing
- Estimate the effects of additional elevators, deep foundations, underpinning, dewatering, flood protection, complex excavation, and tight-site logistics when data or explicit assumptions support them
- Preserve practical loading, refuse, deliveries, moving, fire-service, maintenance, and mechanical access concepts
- Account for façade-area-to-floor-area ratio, repeated versus unique floor plates, shaft continuity, and wet-stack alignment
- Identify scenarios that maximize area but create costly or risky construction
- Compare reuse, partial retention, and new construction where the property and scope make those options relevant
- Add embodied-carbon and operating-energy metrics as optional objectives when adequate data exists; do not invent precision

### 6.5 Development and entitlement strategy

The system should be able to identify and separately model opportunities such as:

- Alternative use or program mixes
- Different as-of-right building typologies
- Lot merger, zoning-lot merger, assemblage, or adjacent-parcel acquisition
- Acquisition or transfer of development rights where a verified legal path may exist
- Easement, party-wall, access, or shared-infrastructure negotiations
- Incentive, affordability, tax, or other program strategies supported by current verified rules
- Authorization, certification, special permit, variance, map change, or other discretionary paths
- Phased development or alternate construction sequence
- A smaller first project that preserves future expansion value

These items must appear in a **Strategic Upside** track, separate from the verified as-of-right result. The system must state what must be true, what evidence is missing, whose approval or agreement is needed, the estimated benefit range, the cost/time/risk range, and the next diligence step. It must never present a negotiation or discretionary approval as owned, guaranteed, or as-of-right.

## 7. Multi-objective optimization

The optimizer must preserve multiple winners and the Pareto frontier. At minimum, it should support:

1. Maximum lawful zoning floor area
2. Maximum preliminary net rentable or sellable area
3. Maximum unit count under explicit unit assumptions
4. Maximum estimated profit or risk-adjusted value
5. Best residential efficiency and planning quality proxies
6. Lowest construction complexity and execution risk
7. Fastest credible as-of-right path
8. Best mixed-use or ground-floor value
9. Strategic upside with non-as-of-right dependencies shown separately
10. Optional sustainability or reuse objective when adequately supported

The UI must allow objective weights, but it must also show the unweighted underlying metrics. A single blended score may be offered for convenience but may not hide why a candidate won.

The optimizer must use a staged search:

1. Generate broadly from a versioned candidate grammar.
2. Apply inexpensive deterministic rejection tests first.
3. Evaluate survivors with progressively more detailed geometry, planning, cost, market, schedule, and risk models.
4. Cluster candidates and preserve material diversity.
5. Refine promising regions of the search space within a recorded compute budget.
6. Stop according to explicit time, evaluation-count, convergence, or improvement criteria.

Seeded runs must be reproducible. Search methods may evolve from parameter sweeps and constraint programming to evolutionary, Bayesian, surrogate-assisted, or other algorithms, but each method must be benchmarked against simple cases where exhaustive or known-best results are available.

## 8. Prevent fake variety

Generating thousands of tiny variations is not creative search. Candidates must be clustered by meaningful characteristics such as typology, footprint, height profile, core concept, use mix, unit mix, efficiency, complexity, and financial behavior.

The comparison set must:

- Suppress near-duplicates
- Preserve objective-specific winners
- Include at least one strong simple/conservative option
- Include non-obvious options only when they survive validation
- Show near-miss candidates when a small rule or assumption change creates large value
- Explain the material geometric and financial differences between candidates

The diversity metric and similarity thresholds must be versioned and visible in evidence.

## 9. Candidate evaluation record

Every generated candidate, including rejected candidates retained for audit or learning, needs a stable ID and machine-readable record containing:

- Parent run, seed, lineage, typology, and parameter values
- Canonical geometry references
- Passed, failed, unsupported, and not-applicable constraints
- Deterministic rejection reason codes
- Floor-by-floor program and area accounting
- Zoning floor area, gross area, net area, efficiency, unit, frontage, perimeter, corridor, core, and vertical-circulation metrics as available
- Preliminary structure, façade, MEP, site-logistics, complexity, and schedule proxies
- Cost, revenue, financing, absorption, and sensitivity assumptions
- Objective scores, Pareto status, cluster, and rank
- Facts, rules, evidence, assumptions, and professional-review dependencies used
- Strategy explanation inputs and generated explanation version

Rejected candidates must not disappear without trace. Aggregated rejection counts and representative failures should help diagnose whether the search space, rules, or assumptions are too restrictive.

## 10. Explanation contract

The system must explain each selected scenario in causal, checkable terms. A useful explanation answers:

- What is the concept?
- Why did it win this objective?
- What did it sacrifice?
- Which facts and rules shaped it?
- Which assumptions materially affect the result?
- What is verified, conditional, unsupported, or subject to professional review?
- What could make the result better or worse?
- What should the user investigate next?

Weak explanation: “Option B is optimal.”

Required explanation pattern: “Option B gives up approximately X of gross area but improves estimated net efficiency by Y because the side core shortens corridors and increases usable exterior perimeter. Its profit rank depends on the stated high-floor and corner-unit premiums. Egress, structure, and market assumptions require the listed professional reviews.”

The explanation must be generated from evaluated candidate records. It may not invent geometry, laws, prices, approvals, neighbors, or benefits that are absent from the record.

## 11. Human control and professional learning

Users and reviewers must be able to:

- Lock facts, assumptions, rules, footprint edges, heights, setbacks, cores, use allocations, and unit-mix constraints where appropriate
- Ban or require typologies and strategies
- Adjust objective weights and compute budget
- Duplicate and modify a candidate
- Compare candidates and assumption sensitivities side by side
- Record why a candidate was accepted, rejected, or revised
- Mark a suggestion as already known, useful, infeasible, or needing diligence
- Route legal, architectural, structural, MEP, cost, market, environmental, and entitlement questions to the correct professional review queue

Professional decisions may become labeled precedents or approved heuristics only through a versioned review process. They must never silently become universal legal rules. The precedent library should retain geography, property type, rule vintage, assumptions, decision rationale, applicability limits, reviewer, and approval status.

## 12. Phased implementation

### Phase A — Contracts and benchmark fixtures

- Contract candidate inputs, outputs, states, metrics, rejection reasons, objectives, assumptions, lineage, strategy suggestions, and comparisons.
- Build synthetic and approved real-property benchmark fixtures covering simple, corner, irregular, split-zone, narrow, shallow, multi-frontage, missing-data, and conflict cases.
- Define reproducibility, provenance, diversity, and professional-review acceptance gates.

### Phase B — Baseline deterministic generator

- Implement a small set of parameterized typologies.
- Generate seeded candidates inside the canonical envelope.
- Apply deterministic pruning and retain rejection evidence.
- Produce at least the as-of-right maximum-area, simple/low-risk, and efficiency-oriented families.

### Phase C — Planning and financial evaluators

- Add floor-plate, core, circulation, unit, frontage, structure, façade, MEP, construction, revenue, schedule, and risk proxies in independently versioned modules.
- Make all market and cost inputs editable, dated, sourced, and sensitivity-tested.

### Phase D — Multi-objective search and diversity

- Add Pareto ranking, cluster-based diversity, compute budgets, convergence evidence, and materially different objective winners.
- Benchmark search performance and optimality gaps on cases with known or exhaustively tested answers.

### Phase E — Strategy intelligence

- Generate evidence-backed recommendations from candidate comparisons and missing-opportunity checks.
- Add the separate Strategic Upside track for assemblage, rights, incentives, negotiations, and discretionary approvals.
- Require machine validation and professional-review labeling for every recommendation.

### Phase F — Expert feedback and precedent learning

- Compare outputs against independent architect/developer baselines.
- Record missed ideas, false positives, and rejected concepts.
- Convert validated lessons into reviewed rules, heuristics, search operators, metrics, or precedents.
- Do not use opaque learning to alter legal calculations.

## 13. Minimum acceptance gates

The capability is not complete until automated and professional-review evidence demonstrates all of the following:

1. The same property profile, rule versions, assumptions, generator version, optimizer version, and seed reproduce the same results.
2. Changing the strategy model cannot change deterministic legal facts, rule outcomes, or canonical geometry without a new validated candidate record.
3. No candidate with a failed hard constraint can appear as a verified as-of-right winner.
4. Missing or unsupported rules propagate to the candidate's status and cannot be hidden by a high score.
5. A benchmark run produces materially different objective winners when the fixture is designed to contain real tradeoffs; near-duplicates are suppressed.
6. Maximum-area and other benchmark objectives match known or exhaustively calculated answers within documented tolerances on simple fixtures.
7. Every selected candidate has complete lineage, versions, metrics, assumptions, evidence references, and causal explanation inputs.
8. Strategic-upside scenarios are visually and contractually separated from verified as-of-right scenarios.
9. Financial winners change appropriately under documented cost, rent, cap-rate, financing, schedule, and absorption sensitivities.
10. Irregular geometry, split districts, boundary conflicts, stale data, missing data, and unsupported rule families fail safely and visibly.
11. An architect can lock a design decision and rerun without unrelated parameters drifting unexpectedly.
12. A professional review panel can compare system results with human baselines and record missed strategies and false positives.
13. Browser 3D remains a rendering of canonical candidate geometry and cannot mutate the source of truth.
14. Large searches run in cloud workers with explicit budgets, resumability, cancellation, checkpointing, and no dependency on the owner's local storage.

## 14. Definition of creative success

Success is not the number of candidates generated and not the fluency of an AI explanation. The system is behaving creatively only when it can repeatedly:

- Discover materially different feasible approaches
- Surface a valuable option that a normal single-envelope workflow would miss
- Explain the geometric, legal, financial, and risk tradeoffs correctly
- Show which conclusion came from a verified rule, a measured property fact, an explicit assumption, a heuristic, or professional judgment
- Learn from expert review without corrupting the deterministic truth layer
- Admit when the available data and encoded expertise are insufficient

The finished product should be described as AI-assisted development feasibility and option search. It must not claim to replace an architect, engineer, zoning professional, cost estimator, attorney, lender, broker, or public-agency determination.

## 15. Required first integration action

After this file is added to the project root, do not begin by coding the full optimizer. First return an evidence-backed integration plan that:

1. Lists existing repository documents, contracts, agents, and tasks that already cover part of this requirement.
2. Identifies true gaps without duplicating accepted work.
3. Proposes dependency-ordered tasks and gates using the existing project-control system.
4. Names the canonical contracts that must be added or extended.
5. Shows where the property profile, rules engine, geometry engine, financial engine, 3D renderer, UI, evidence system, and review workflow connect.
6. States which work belongs now, which belongs after the first property screen, and which remains later research.
7. Preserves the Render-only, browser-based, cloud-first, low-local-storage, deterministic, provenance-first architecture.

