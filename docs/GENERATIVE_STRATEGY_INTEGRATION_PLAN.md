# Generative Development Strategy — Section 15 Integration Plan

- **Status:** DRAFT FOR OWNER REVIEW — no tasks contracted, no code authorized by this document
- **Prepared by:** orchestrator, 2026-07-16, per `GENERATIVE_DEVELOPMENT_STRATEGY_REQUIREMENTS.md` §15 (root-level approved requirement) and the owner directive of 2026-07-16
- **Evidence basis:** the accepted project-control ledger (13 accepted tasks at this writing), contracts v1 (M0-T009), the PLUTO connector (M1-T002) and property-profile API (M1-T005, in gates), accepted research M1-T001/T003/T004, `docs/3D_MASSING_ENGINE_ARCHITECTURE.md`, `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md`, PRD, `docs/IMPLEMENTATION_SEQUENCE.md`
- **Operating rule honored:** additive integration; nothing accepted is redone; nothing in flight is interrupted

## 1. Existing coverage (what the repo already provides, with evidence)

| GDS capability (§1) | Existing coverage | Status |
|---|---|---|
| 1. Verified truth layer | Canonical contracts v1 (`packages/contracts/schemas/v1/`: property_profile, source_fact, coverage_status, analysis_state) — M0-T009 ACCEPTED. PLUTO SODA connector with full provenance + typed error taxonomy — M1-T002 ACCEPTED. Property-profile API v1 with coverage/completeness statuses, conflicts visible, confidence never mapped to coverage — M1-T005 (G1-G3-G5 passed, in acceptance). Official-source research with OQ discipline — M1-T001/T003/T004. Conflict engine + user confirmation = M2 (planned, PRD §32.3). Rules DSL/evaluator/releases = M4 (planned, PRD §10–§11) | Largely built or already roadmapped; GDS adds nothing structural here |
| 2. Generative design-search engine | PRD §13 scenario engine (M5) requires materially distinct scenario families and diversity ("materially distinct, not cosmetic duplicates" = GDS §8 in embryo). `3D_MASSING_ENGINE_ARCHITECTURE.md` §1 already names the custom layer: envelope generator, floor-plate generator, FAR allocation, scenario massing generator | Partially anticipated; the **candidate grammar, seeding, lineage, and rejection-record machinery are new** |
| 3. Deterministic evaluation engine | PRD §7.2 basic code-feasibility layer (core allowance, egress flags, corridor/shaft efficiency) = the seed of GDS §6.2/§6.4 proxies. Geometry validation gates in 3D doc §10. Deterministic-calculation principle is CLAUDE.md permanent principle 1 | Partially anticipated; **independently versioned proxy modules and financial evaluators are new** |
| 4. Multi-objective optimizer | PRD §6 objective weights + §13 ranking + "never 'best' without objective". Scenario-optimizer acceptance pack (ACCEPTANCE_SCENARIO_STANDARD) requires ≥3 materially distinct outputs, stability, score-explanation sums | Partially anticipated; **Pareto frontier, clustering/diversity metrics, staged search, compute budgets, benchmarking are new** |
| 5. Developer-strategy intelligence | PRD §23 AI boundaries (propose/explain, never calculate/publish); special permits flagged as possibilities (PRD §7.1); professional_review_required status | Boundary rules exist; **Strategic Upside track, precedent library, and explanation contract are new** |
| Cross-cutting: 3D render-only truth | 3D doc §2 "canonical truth is not the Three.js scene" + §9 API contracts + GLB pipeline on Render — exactly GDS §13.13 | Already decided; GDS confirms it |
| Cross-cutting: reproducibility/jobs | PRD §22 job system (idempotency, resume, checkpoint, cancellation, budgets) = GDS §13.14 for large searches | Already roadmapped |
| Agents | scenario-optimization-engineer, rules-engineer, geospatial-engineer, ai-pipeline-engineer registered today | Cover phases B–D producers; **financial-feasibility-engineer + opportunity-search-engineer are B-005-missing** |

**Overlap-inventory caveat (blocking for completeness):** GDS §2.1 requires inventorying overlap with the competitive-feature, financial-feasibility, opportunity-search, and 3D/UI execution-plan documents — but 4 of those documents and all 5 expansion agents are still missing (B-005: `COMPETITIVE_FEATURE_EXPANSION.md`, `3D_AND_UI_EXECUTION_PLAN.md`, `3D_VISUAL_ACCEPTANCE_STANDARD.md`, `.claude/rules/3d-ui-expansion.md` + 5 agent files). This plan inventories everything that exists. **Owner decision needed:** supply the missing files, or declare GDS the superseding document for the financial/opportunity workstreams so B-005 can be re-scoped.

## 2. True gaps (new work, no duplication of accepted work)

1. **Candidate contracts** — candidate record (GDS §9: lineage, seed, parameters, constraint results, rejection reason codes, metrics, objective scores, Pareto/cluster status), typology/grammar descriptor (§5), objective set + weights (§7), versioned assumption set (dated/sourced market + cost inputs, §6.3/§12C), strategy suggestion / Strategic Upside item (§6.5), explanation record (§10). None exist in contracts v1.
2. **Five-axis status vector** (§3.3: legal/geometric/planning/financial/evidence) — coverage_status v1 covers the legal axis only. Additive contract extension.
3. **Candidate generator** (Phase B) — parameterized typologies, seeded generation inside the canonical envelope, deterministic pruning with retained rejection evidence.
4. **Evaluator proxy modules** (Phase C) — floor-plate/core/circulation/unit/frontage/structure/façade/MEP/schedule proxies + financial evaluator with sensitivity, each independently versioned.
5. **Multi-objective search** (Phase D) — Pareto ranking, diversity clustering, staged search, compute budgets, convergence evidence, benchmark harness vs known-best fixtures.
6. **Strategy intelligence** (Phase E) — machine-validated suggestions, Strategic Upside track separation, professional-review routing.
7. **Precedent/feedback system** (Phase F) — versioned reviewed precedent library; expert-baseline comparison.
8. **Benchmark fixture library** (Phase A) — extends the PRD §24 golden-property concept with synthetic tradeoff fixtures (corner/irregular/split-zone/narrow/shallow/multi-frontage/missing-data/conflict).

## 3. Proposed dependency-ordered tasks (NOT contracted — awaiting owner approval of this plan)

Existing task-ID convention; producers/reviewers per current agent registry; every task gets the standard packet + G0 and the gates shown.

| Order | Proposed task | Depends on | Gates | Producer |
|---|---|---|---|---|
| 0 (now, docs only) | **M1-T00x — contract v1.1 (already mandated by M1-T005 G3):** document coverage_status/data_completeness/reproducibility keys + district provenance linkage | M1-T005 acceptance | G0,G2,G3,G4 | backend-engineer |
| 1 (after first Property screen) | **M5-T001 — Phase A contracts + benchmark fixtures:** candidate_record v1, typology descriptor, objective_set, assumption_set, strategy_suggestion, explanation_record, 5-axis status extension (additive coverage_status v1.x); synthetic + real benchmark fixtures; reproducibility/diversity acceptance gates defined | contract v1.1; Priority 4 screen accepted | G0,G2,G3,G4 | backend-engineer + rules-engineer review |
| 2 | **M2-Txxx geometry prerequisites (already-planned M2 work, unchanged):** MapPLUTO tax-lot geometry import; zoning-features ArcGIS importer; ZTLDB connector (packets already carry the M1-T003 carry-forwards) | M1 research (done) + B-001 Supabase | G1,G3,G4,G5 | geospatial-engineer |
| 3 | **M4-Txxx rules DSL + evaluator (already-planned, unchanged)** + canonical envelope generator (the 3D doc's envelope/constraint-primitive pipeline §4, through "buildable 2D regions by elevation band") | M2 geometry; M3 corpus for real rules | G3,G4,G5,G6 | rules-engineer + geospatial-engineer |
| 4 | **M5-T002 — Phase B baseline generator:** 3–5 parameterized typologies, seeded candidates in the envelope, deterministic pruning, rejection records; produces as-of-right max-area, simple/low-risk, efficiency families | M5-T001 + envelope generator + first published rules | G0,G2,G3,G4 | scenario-optimization-engineer |
| 5 | **M5-T003 — Phase C evaluators:** planning proxies + financial evaluator, versioned modules, editable/dated/sourced assumptions, sensitivity | M5-T002 | G0,G2,G3,G4,G5 | scenario-optimization-engineer + financial-feasibility-engineer (B-005) |
| 6 | **M5-T004 — Phase D multi-objective search:** Pareto, clustering/diversity, budgets, convergence, benchmark harness (GDS §13.5/§13.6 gates) | M5-T003 | G0,G2,G3,G4 | scenario-optimization-engineer |
| 7 | **M5-T005 — Phase E strategy intelligence + Strategic Upside track** | M5-T004; ai-pipeline injection defenses (M3) | G0,G2,G3,G4,G5,G6-style human review | ai-pipeline-engineer + opportunity-search-engineer (B-005) |
| 8 (later research) | **M6/M7 — Phase F precedent learning + expert baselines** | M5-T005; client validation program (M6) | G3,G4,G5,G6,G7 | TBD |

Parallel documentation task (small, immediate on approval): update `docs/MASTER_EXECUTION_PLAN.md` + `docs/IMPLEMENTATION_SEQUENCE.md` M4/M5/M6 sections to reference GDS phases (additive notes, no re-architecture).

## 4. Canonical contracts to add or extend

**Add (new, versioned, in `packages/contracts/schemas/`):** `candidate_record`, `candidate_typology`, `objective_set`, `assumption_set`, `strategy_suggestion`, `explanation_record`, `scenario_geometry` (formalizing the object already specified in 3D doc §2 — geometry_version, CRS/units/axis/local-origin metadata per §3).

**Extend (additive minor versions):** `coverage_status` → five-axis status vector (legal/geometric/planning/financial/evidence — GDS §3.3); `property_profile` v1.1 (already mandated by the M1-T005 G3 adjudication); the M4 rule-evaluation-trace contract gains candidate-constraint-result linkage; `analysis_state` gains the candidate-search states when M5 lands (backend state machine still owns transitions, PRD §32.5).

## 5. Connection map (where each engine plugs in)

```
property-profile API (M1-T005, live)             ← official facts + provenance + conflicts
  → conflict/confirmation workflow (M2)           ← user assumptions (versioned assumption_set)
  → rules engine (M4)                             ← versioned deterministic constraints (G6-gated)
  → envelope generator (M4/M2 geometry, Render+Shapely)  ← canonical zoning envelope (scenario_geometry)
  → candidate generator (M5-T002, Render worker)  ← candidate grammar, seeds, lineage
  → pruning + evaluators (M5-T002/T003, Render workers, PRD §22 job system: budgets/resume/cancel)
  → optimizer (M5-T004)                           ← Pareto set + clusters (candidate_record)
  → strategy layer (M5-T005, ai-pipeline, schema-constrained)  ← Strategic Upside track (separate)
  → Compare/Evidence UI + 3D viewer (Three.js renders scenario_geometry; render-only per 3D doc §2)
  → professional-review queues (G6 + PRD §12)     ← precedent library (Phase F, versioned review)
```

Every arrow carries version identifiers per GDS §4 (profile/rule/assumption/generator/optimizer versions + seed); reproduction identifiers extend the existing `reproducibility` block M1-T005 already emits.

## 6. Now / after first Property screen / later

- **NOW (unchanged priorities):** finish M1-T005 acceptance; Priority 4 first Property screen; M1 research fan-out; M2 connectors when B-001 unblocks. Only GDS action now: this plan + the doc-positioning edits + contract v1.1 (already owed).
- **AFTER the first Property screen:** M5-T001 Phase A contracts + benchmark fixtures (cheap, unblocks everything later, no optimizer code); MASTER_EXECUTION_PLAN/IMPLEMENTATION_SEQUENCE additive updates; B-005 resolution decision.
- **LATER (research/implementation in milestone order):** Phase B after envelope generator + first published rules (M4); Phases C–D inside M5; Phase E after M3 injection defenses + M5 core; Phase F in M6/M7 with the client-validation program.

## 7. Architecture invariants preserved (GDS §15.7)

- **Render-only** (ADR-004): all generation/evaluation/search runs on Render workers; no new providers.
- **Browser-based, render-only 3D:** Three.js consumes canonical `scenario_geometry`/GLB; cannot mutate truth (3D doc §2 = GDS §13.13).
- **Cloud-first, low-local-storage:** searches are PRD §22 jobs with budgets/checkpoints; artifacts to Supabase Storage; nothing citywide or bulky on the owner's PC.
- **Deterministic + provenance-first:** legal/geometry/financial arithmetic stays in versioned deterministic code (GDS §3.1 = CLAUDE.md principle 1); AI proposes/explains within schemas (PRD §23); every candidate carries full lineage; coverage labels never come from model confidence (enforced pattern proven in M1-T005 G3).
- **Gate system unchanged:** GDS §13 acceptance gates map onto existing G0–G7 (G6 + qualified-human review for anything touching legal interpretation or precedents).

## 8. Approval requests to the owner

1. Approve this plan (or amend) so M5-T001 and the roadmap-doc updates can be contracted at the stated trigger points.
2. Decide the B-005 question in §1 (supply the 4 missing docs + 5 agents, or declare GDS superseding for financial/opportunity scope).
3. Confirm the doc-positioning edits (CLAUDE.md read list + IMPLEMENTATION_SEQUENCE notes) made alongside this plan.
