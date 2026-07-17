# 3D/UI Expansion Pack — Integration Report (M0-T010 Phase 2)

- **Status:** Producer deliverable submitted for independent gate (G3). Task M0-T010, producer `cloud-architect`, reviewer `code-reviewer`.
- **Required by:** `CONTINUE_FROM_CURRENT_STATE_PROMPT.md` item 4 and the M0-T010 task packet (`project-control/tasks/M0-T010.json`, outputs Phase 2).
- **Pack provenance:** owner-recovered `nyc-buildability-3d-ui-expansion-pack.zip`, sha256 `0C89C2B14F3F9CC93D412FB237E80ECD51C6F8FADEB49EEEFA5A30D5E0FB146A` (M0-T010 packet, inputs). Phase 1 integrated it additively at commit `d25d2b2` on branch `task/M0-T010-expansion-integration`: 11 new files at exact manifest paths, 3 pre-existing files verified byte-identical (`git diff --stat d25d2b2^ d25d2b2` over the 3 files is empty), all 14 manifest/README-listed entries present (verification command output in `project-control/reports/M0-T010-producer-report.md`).
- **Operating constraints honored:** pack `INTEGRATION_MANIFEST.json` (`merge_mode: additive`, `overwrite_existing_files: false`, `continuation_behavior: preserve project-control history and add dependent tasks`); `CONTINUE_FROM_CURRENT_STATE_PROMPT.md` lines 5–8 (do not restart, recreate, reset, or replace without an approved ADR); `.claude/rules/3d-ui-expansion.md` items 2–4; `GENERATIVE_DEVELOPMENT_STRATEGY_REQUIREMENTS.md` (GDS) §2.
- **Nothing in this report contracts a task, edits the ledger, or edits `docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md`.** All new tasks and all GDS-plan changes are proposals for the orchestrator and owner. Section 7 contains the exact old-text→new-text proposals for owner review.

---

## 1. Validity of existing accepted and in-flight work

Ledger basis: `project-control/state.json` at 2026-07-17T08:14Z — 18 accepted (M0×11, M1×6, M2×1), active M0-T010 + M1-T007, blocked M0-T007/M0-T008.

**Verdict: every accepted task remains valid. Nothing accepted is invalidated by the pack.** The pack is explicitly additive (manifest `merge_mode: additive`; prompt lines 5–8). Per-task assessment:

| Task(s) | What it delivered | Pack impact | Verdict |
|---|---|---|---|
| M0-T000…T006, T012 (control plane, CI, secrets, ADRs, SHA-pinning) | Engineering control plane | None; pack rule file 3d-ui-expansion.md item 3 requires preserving it | VALID |
| M0-T009 Canonical contracts v1 (`packages/contracts/schemas/v1/`: property_profile, source_fact, coverage_status, analysis_state, analysis_state_transition, common) | Truth-layer contracts | Pack adds a NEW contract need (`scenario_geometry`, 3D doc §2) — additive, no v1 change (see §3) | VALID |
| M0-T011 ADR-004 Render-only frontend (Vercel dropped) | Hosting decision | Pack's stack (Three.js/R3F/Drei, MapLibre, deck.gl — `INTEGRATION_MANIFEST.json` `recommended_3d_stack`) is browser-library-only; server side is Render Python (Shapely/Trimesh, 3D doc "Deterministic geometry processing"/"Mesh creation") | VALID — no hosting conflict |
| M1-T001…T004, T007 (source research) / M1-T002 PLUTO connector / M1-T005 property-profile API / M1-T006 contract v1.1 | Verified truth layer | Pack consumes these (geometry truth model, 3D doc §2, requires "Property geometry version, Source facts, Rule-evaluation trace"); it does not modify them | VALID |
| M2-T001 first Property screen (accepted) | Browser Property screen against property-profile API v1.1 | `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md` post-dates it. The screen was built before the design system existed. **Flag, do not rework**: pack prompt line 8 forbids replacing accepted work without an approved ADR, and no verified regression exists. Design-system conformance applies prospectively — first to the imminent M2 Confirm screen (`docs/IMPLEMENTATION_SEQUENCE.md` M2: "Crisp Property and Confirm screens") — with any retrofit of the accepted Property screen contracted later as its own reviewed task if the visual-quality gate finds concrete defects | VALID, with prospective design-system flag |
| M0-T007 / M0-T008 (blocked on B-001 Supabase token) | Supabase migrations, auth/RLS | Pack **raises the value** of unblocking B-001: PostGIS is the pack's canonical spatial store (3D doc "Canonical spatial storage") and opportunity search requires PostGIS indexes (opportunity-search-engineer agent file). No content change to the tasks | VALID, still blocked on B-001 |
| M1-T007 DOB NOW research (in flight, 75%) | Source research | Out of pack scope; unaffected | VALID |
| M0-T010 (this task) | Integration report | This document | in flight |

**Architectural decisions check** (prompt item "Which existing tasks and architectural decisions remain valid"):
- ADR-004 Render-only: preserved (above).
- ADR-005 orchestrator-only ledger/git (`.claude/rules/project-control.md`): preserved; the pack's agent files do not encode it — reported as a conflict in §4, not silently fixed.
- Contracts-first modular monorepo (`docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md` "Complexity containment"): preserved; the pack adds modules, not services.
- Deterministic-truth principle: the pack itself restates it (prompt item 9: "Do not generate a fake 3D building from AI prose"; 3D doc §2: "The canonical truth is not the Three.js scene").
- Task-ID convention: the pack's execution plan uses `3D-xxx`/`UI-xxx`/`COMP-xxx` IDs (`docs/3D_AND_UI_EXECUTION_PLAN.md`), which **conflicts** with the repository convention `M<milestone>-T<number>` (`docs/PROJECT_CONTROL_PROTOCOL.md` task packet fields; GDS §2.2 "using the repository's current task-ID convention"). Resolution: pack IDs are treated as workstream labels and re-keyed at contracting time (§2 mapping). The prompt itself permits this (item 5: "using new task IDs").

---

## 2. New dependent tasks in dependency order

Proposals only — the orchestrator contracts, numbers, and sequences (`docs/AGENT_OPERATING_SYSTEM.md` §1.1). Milestone mapping per `docs/IMPLEMENTATION_SEQUENCE.md`: design-system guidance lands in M2 (Confirm screen is on the M2 critical path); 3D geometry/viewer, interactive assumptions, and financial evaluation land in M5; professional-review packaging in M6; citywide opportunity search, external API, and schematic-massing extensions in M7 ("Schematic massing and visualizations" is an M7 bullet; the M5 Compare/Evidence screens carry the first massing views). Where a pack task overlaps a GDS-plan proposed task (`docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md` §3), they are merged, not duplicated.

**Ordering note:** this respects the pack's own sequencing rule (`docs/3D_AND_UI_EXECUTION_PLAN.md` "First recommended unblocked work": ADR → IA → schema → tokens → backend geometry only after contracts stabilize → viewer only after fixtures; "Do not let the viewer team invent geometry").

| # | Pack ID | Proposed repo task (final ID assigned by orchestrator) | Milestone | Depends on | Producer → Reviewer(s) | Gates |
|---|---|---|---|---|---|---|
| 1 | — | Agent-roster conformance for the 5 pack agent files (see §4; small, unblocks safe dispatch) | M0 | M0-T010 accepted | orchestrator or cloud-architect → code-reviewer | G0,G2,G3 |
| 2 | UI-001 | Product information architecture (Property/Potential/Scenarios/3D/Financials/Evidence/Review nav per design doc §2; progressive disclosure per §1) | M2 | none (docs-only) | product-design-director → human-journey-reviewer | G0,G2,G3 |
| 3 | UI-002 | Design tokens + component specification (design doc §5–§8); **feeds the imminent Confirm screen** | M2 | UI-001 | product-design-director → frontend-engineer + visual-quality-reviewer | G0,G2,G3 |
| 4 | UI-003/UI-004 | Application shell + Property/Confirm flow implementation to the token spec (the Confirm screen task already on the M2 plan absorbs this; do not create a duplicate) | M2 | UI-002; property-profile API (accepted) | frontend-engineer → visual-quality-reviewer + human-journey-reviewer | G0,G2,G3,G4 |
| 5 | 3D-001 | 3D architecture ADR (technology decision per manifest stack, deployment boundary, geometry truth model, API contracts, storage strategy incl. GLB bucket, performance budgets, licensing inventory) | M5 (doc can be authored any time; cheap) | ADR set M0-T006; contracts v1 | cloud-architect → code-reviewer | G0,G2,G3 |
| 6 | 3D-002 | `scenario_geometry` contract + golden fixtures — **merged into GDS-plan M5-T001 Phase A contracts** (the GDS plan §4 already names `scenario_geometry`); fixture set per exec-plan 3D-002 tests (normal/irregular/hole/split/assemblage/invalid/unit-mismatch) + `docs/3D_VISUAL_ACCEPTANCE_STANDARD.md` golden scenes | M5 (Phase A; trigger already met — M1-T006 and M2-T001 accepted) | 3D-001; M1-T006 | backend-engineer + 3d-massing-engineer → geospatial-engineer + rules-engineer | G0,G2,G3,G4 |
| 7 | — | M2 geometry prerequisites (MapPLUTO tax-lot geometry, zoning features, ZTLDB) — **already planned M2 work, unchanged** (GDS plan §3 order 2) | M2 | B-001 (blocked) | geospatial-engineer → data-contract-verifier | G1,G3,G4,G5 |
| 8 | 3D-010 | Constraint-primitive generator (yards, setbacks, height bands, street-wall, buildable polygons; every primitive links to a rule-evaluation trace — exec-plan gate) | M5 | M2 geometry; first M4 published rules; envelope generator (GDS plan §3 order 3) | 3d-massing-engineer → rules-engineer | G0,G2,G3,G4 |
| 9 | 3D-011 | Floor-plate + FAR allocator (floor area reconciles with scenario metrics within documented tolerance — exec-plan gate) | M5 | 3D-010 | 3d-massing-engineer → scenario-optimization-engineer | G0,G2,G3,G4 |
| 10 | 3D-012 | Mesh/GLB pipeline (Trimesh on Render; validation; compression decision; Supabase Storage artifacts; cache/version keys) | M5 | 3D-011; B-001, B-002 | 3d-massing-engineer → qa-engineer | G0,G2,G3,G4 |
| 11 | 3D-020 | Viewer foundation (R3F canvas, camera presets, layers, selection, inspector sync, loading/error) — starts only from versioned 3D-002 fixtures | M5 | 3D-002 fixtures; UI-002 tokens; 3D-012 for live data | frontend-engineer + 3d-massing-engineer → visual-quality-reviewer | G0,G2,G3,G4 |
| 12 | 3D-021/022/023 | Scenario comparison; floor stack/cutaway; geometry-evidence drill-down | M5 | 3D-020 | frontend-engineer → visual-quality-reviewer / human-journey-reviewer / data-contract-verifier + rules-engineer (per exec plan) | G0,G2,G3,G4 |
| 13 | COMP-001 | Interactive assumptions/incentive toggles (backend state machine recalculates; AI never mutates scenario values — `docs/COMPETITIVE_FEATURE_EXPANSION.md` §1.2) | M5 | M4 rules engine; M5 scenario engine core | scenario-optimization-engineer → rules-engineer | G0,G2,G3,G4 |
| 14 | COMP-003 | Financial feasibility — **merged into GDS-plan M5-T003 Phase C financial evaluator** (single workstream; versioned editable assumptions, sensitivity, never presented as official fact — expansion doc §1.5 = GDS Phase C) | M5 | M5-T002 Phase B generator | financial-feasibility-engineer (+ scenario-optimization-engineer) → qa-engineer | G0,G2,G3,G4,G5 |
| 15 | COMP-002 | Assemblage/air-rights analysis — deterministic adjacency/unused-rights geometry (geospatial) feeding the **GDS Strategic Upside track** (GDS §6.5, Phase E / M5-T005); transferability status always explicit (expansion doc §1.3) | M5 (geometry) + M5-T005 (strategy) | M2 geometry; M4 rules; M5-T004 | geospatial-engineer (geometry) + ai-pipeline-engineer (strategy) → rules-engineer + professional-review gate | G0,G2,G3,G4,G6-style human review |
| 16 | COMP-006 | Professional-review escalation package (freeze reproducible analysis version; reviewer workflow — expansion doc §1.9) | M6 | M5 core; reports pipeline | backend-engineer + frontend-engineer → security-reviewer + human-journey-reviewer | G0,G2,G3,G4,G5 |
| 17 | COMP-004 | Citywide opportunity search (reverse workflow; PostGIS-scale filters; deck.gl map) — **outside GDS scope; new M7 workstream** | M7 | citywide M2 data; M4 rule coverage; M5 scoring | opportunity-search-engineer → data-contract-verifier + qa-engineer | G0,G1,G2,G3,G4,G5 |
| 18 | COMP-005 | Explainable opportunity score (all components visible — expansion doc §1.8) | M7 | COMP-004 | opportunity-search-engineer → human-journey-reviewer | G0,G2,G3,G4 |
| 19 | COMP-007 | External API surface (provenance + coverage status in every response — expansion doc §1.10) | M7 | M5/M6 stable contracts | backend-engineer → security-reviewer + code-reviewer | G0,G2,G3,G4,G5 |

UI-005 (scenario/evidence flows) folds into the M5 Compare/Evidence screen tasks; UI-006 (accessibility/responsive) is not a standalone task — its checks become mandatory G3 criteria for every UI task (exec-plan "Every premium UI task requires" list + `docs/ACCEPTANCE_SCENARIO_STANDARD.md` UI human-journey pack).

**What can start now vs. must wait** (prompt item):
- **Now (no blockers):** #1 roster conformance; #2 UI-001; #3 UI-002; #5 3D-001 ADR. All docs-only, negligible disk, on the owner PC or Codespaces.
- **Now, trigger already met:** #6 Phase A contracts incl. scenario_geometry (M1-T006 + M2-T001 accepted — the GDS plan's stated trigger).
- **Waits for B-001/B-002:** #7 geometry imports, #10 GLB pipeline (Supabase + Render credentials).
- **Waits for M4 first published rules:** #8–#9 (constraint primitives must link to real rule-evaluation traces), #13.
- **Waits for M5 core:** #11–#15. **Waits for M5/M6:** #16. **M7:** #17–#19.
- **Critical-path protection:** none of the above may delay the M2 Confirm screen; UI-001/UI-002 are the only pack tasks on that path and exist to serve it.

---

## 3. Canonical contracts touched or needed (names and homes only — no schema authoring here)

Home for all: `packages/contracts/schemas/` (versioned, additive), same tree as contracts v1 (`packages/contracts/schemas/v1/`, M0-T009). Per `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md` "Canonical contracts", frontend, API, workers, and reports consume the same contracts.

**New contracts required by the pack:**
| Contract | Source requirement | Notes |
|---|---|---|
| `scenario_geometry` | 3D doc §2 (versioned geometry object: scenario_id, geometry_version, CRS, property_geometry_version_id, rule_release_id, generator_version, footprints, floors, constraint_surfaces, existing_building, metrics, source_links, coverage_status) + §3 CRS/unit/axis/local-origin metadata | Already named in GDS plan §4; pack 3D-002 merges into Phase A |
| `geometry_artifact` (GLB reference) | 3D doc "Runtime format" + exec-plan 3D-012 (artifact storage, cache/version keys); expansion doc §1.10 "GLB/scene artifact" | Storage key, content hash, generator version, compression, linked scenario_geometry version — the browser never treats the GLB as truth |
| `floor_stack` | Expansion doc §1.6 (floor-by-floor stack; "The floor stack and 3D model must use the same scenario data object") | Likely a section of `scenario_geometry`/candidate record rather than standalone — decision belongs to the Phase A contracts task |
| `assumption_set` (financial + development assumptions, versioned/dated/sourced) | Expansion doc §1.5 ("editable, versioned, and clearly separated from official property facts") = GDS §6.3/§12C | Already named in GDS plan §4 — one contract, not two |
| `financial_result` | Expansion doc §1.5 outputs (NOI, yield, margin, sensitivity, risk-adjusted score) | Separate from official facts; carries assumption_set version |
| `assemblage_analysis` (zoning-lot combination record) | Expansion doc §1.3 (component lots, built/unused FAR by lot, transferability status enum: mathematically-unused / legally-transferable / requires-approval / not-evaluated) | Feeds Strategic Upside items (GDS `strategy_suggestion`) |
| `opportunity_query` / `opportunity_result` / `opportunity_score` | Expansion doc §1.4 + §1.8 (filters, ranked results, explainable score components, data-completeness) | M7; tenant-scoped saved searches |
| `review_package` | Expansion doc §1.9 (frozen reproducible analysis version + reviewer actions) | M6 |

**Contracts extended (additive minor versions only):** `coverage_status` → five-axis status vector (GDS §3.3; also needed by 3D geometry status); `scenario`/`candidate_record` (GDS plan §4) gains geometry + floor-stack + financial references; `analysis_state` gains geometry-generation states when M5 lands (backend state machine still owns transitions, PRD §32.5). **No change to v1 contracts already accepted.**

---

## 4. Agent assignments and roster-convention conflicts

**Assignments (per prompt item 6 and exec-plan producers/reviewers):** geometry/massing → `3d-massing-engineer`; product IA/design system → `product-design-director`; independent visual/interaction review → `visual-quality-reviewer`; financial scenarios → `financial-feasibility-engineer`; citywide deal search → `opportunity-search-engineer`. Existing roster carries the rest (frontend-engineer, geospatial-engineer, rules-engineer, scenario-optimization-engineer, backend-engineer, qa-engineer, data-contract-verifier, human-journey-reviewer, security-reviewer, code-reviewer, cloud-architect, ai-pipeline-engineer — all present in `.claude/agents/`). Producer/reviewer separation holds in every §2 row; `visual-quality-reviewer` is never a producer (its own file: "Never use as the producer of the same UI").

**Conflicts found (REPORTED ONLY — the 5 pack files were not modified, per the M0-T010 packet risk note "report, do not silently rewrite"):**

| # | Conflict | Evidence | Impact |
|---|---|---|---|
| C1 | All 5 pack agents lack `memory: project` frontmatter | Pack files have only `name/description/tools/model`; every roster agent carries `permissionMode: default` + `memory: project` (e.g. `cloud-architect.md`, `code-reviewer.md`) | The agent-memory clarification in `.claude/rules/project-control.md` (2026-07-16 owner audit) presupposes `memory: project`; without it the write-scope rule for `.claude/agent-memory/<name>/` has no anchor |
| C2 | All 5 lack `permissionMode: default` | Same comparison | Divergent permission behavior vs roster |
| C3 | The 4 producer-type pack agents lack `isolation: worktree` | Roster producers (cloud-architect, scenario-optimization-engineer, etc.) all declare it | Violates worktree-isolation practice (CLAUDE.md principle 10) if dispatched as-is |
| C4 | None of the 5 carry the ADR-005 protocol section | Roster producers embed "## Ledger and integration protocol (process decision ADR-005…)"; roster reviewers embed "## Gate reporting protocol…" (see `security-reviewer.md`, `human-journey-reviewer.md`) | A pack agent dispatched as-is could run `tools/project_control.py`/git push contrary to ADR-005 (all 5 have Bash except product-design-director) |
| C5 | `visual-quality-reviewer` (a reviewer) lacks the read-only gate-reporting discipline, the `Write` tool for report drafting, and `skills: run-quality-gate` | Compare `visual-quality-reviewer.md` (tools: Read, Grep, Glob, Bash; no skills block) with `code-reviewer.md`/`security-reviewer.md` | Its body does say "Do not edit implementation files during final review", but the ADR-005 return-verdict protocol is absent |
| C6 | None of the 5 have the `Skill` tool | All roster agents list `Skill` | Cannot invoke run-quality-gate/submit-checkpoint skills |
| C7 | Task-ID convention: exec plan uses 3D-/UI-/COMP- prefixes | `docs/3D_AND_UI_EXECUTION_PLAN.md` vs `docs/PROJECT_CONTROL_PROTOCOL.md` | Resolved by re-keying at contracting (§1, §2) — the doc itself is guidance, not ledger |

**Recommendation (task #1 in §2):** one small M0 conformance task that adds the missing frontmatter keys and ADR-005 sections to the 5 files without altering their domain content, reviewed by code-reviewer. Until it is accepted, the orchestrator must not dispatch the 5 pack agents.

---

## 5. Storage and cloud-processing implications

Constraints: `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` (owner PC ~7 GB free, thin client; ≥4 GB preserved; ≤2 GB incremental), ADR-004 Render-only hosting, PRD §14/§16.

- **Server-side geometry (Render workers):** Shapely (2D constraint geometry) and Trimesh (mesh construction/validation/GLB export) run in the Render Python service per 3D doc "Deterministic geometry processing"/"Mesh creation and validation". Geometry generation is a PRD §22 job type (idempotent, resumable, bounded temp space, cleanup on success/failure). **No 3D toolchain is ever installed on the owner PC.**
- **Canonical spatial data (Supabase PostGIS):** tax-lot geometry, district intersections, adjacency discovery, geometry versions, citywide search indexes (3D doc "Canonical spatial storage"). Blocked on B-001 today.
- **GLB/scene artifacts (Supabase Storage):** a new private bucket (working name `geometry-artifacts`) with signed URLs, version-keyed caching, retention limits — an additive extension to the PRD §16 bucket list that the 3D-001 ADR must record. GLBs are derived artifacts, reproducible from `scenario_geometry` + generator version; retention policy can therefore be aggressive.
- **Browser-side (rendering only):** Three.js/R3F/Drei, MapLibre GL JS, deck.gl are frontend npm dependencies. Builds run in GitHub Actions/Codespaces only — never `npm install` on the owner PC (low-storage policy "Prohibited local operations"). The browser scene renders canonical geometry and "cannot mutate the source of truth" (GDS §13.13; 3D doc §2).
- **Citywide layers:** deck.gl consumes server-prepared tiles/aggregates from PostGIS; users never download citywide datasets (PRD §35; low-storage policy "User-device experience"). Tiling strategy is a 3D-001 ADR item.
- **Performance/payload budgets:** scene payload size, time-to-parcel, scenario-switch duration, peak browser memory are mandatory recorded evidence (`docs/3D_VISUAL_ACCEPTANCE_STANDARD.md` "Performance evidence"; 3D doc §8).
- **CesiumJS:** deferred optional context layer only (manifest `optional_future_context`); adopting it later requires its own ADR.
- **This task's own footprint:** Phase 1 + Phase 2 wrote only KB-scale text files inside repo worktrees; no installs, no datasets; disk budget untouched.

---

## 6. Risks and required gates per workstream

| Workstream | Key risks | Required gates |
|---|---|---|
| Design system / UI (UI-001…004, M2) | Delaying the Confirm-screen critical path; accepted Property screen drifting from new tokens (flagged §1, no rework without reviewed defect); default-template appearance (design doc §5 prohibition) | G0, G2, G3 (visual-quality-reviewer + human-journey-reviewer; five-second hierarchy, keyboard, reduced-motion, narrow-width per exec-plan UI gate list), G4 on integration |
| 3D architecture (3D-001) | Licensing inventory incomplete; storage-bucket decision skipped; scope creep into implementation | G0, G2, G3 (code-reviewer) |
| Geometry contracts + fixtures (3D-002/Phase A) | Contract churn if authored before envelope-generator design settles; CRS/unit mistakes (geospatial scenario pack applies) | G0, G2, G3, G4; geospatial-engineer review mandatory |
| Backend geometry (3D-010…012) | Geometry without rule-trace linkage (hard exec-plan gate: "Every primitive links to a rule-evaluation trace"); FAR reconciliation drift; B-001/B-002 credential blockers; temp-mesh cleanup on Render | G0, G2, G3, G4; G5 for storage/signed URLs; G6 governs the upstream rules (M4), not the deterministic geometry code |
| Viewer (3D-020…023) | Viewer team inventing geometry while waiting (pack's explicit warning) — mitigated by fixture-only development; performance budget misses; evidence-panel desync | G0, G2, G3 (visual-quality-reviewer runs `3D_VISUAL_ACCEPTANCE_STANDARD.md` golden scenes + human walkthrough; qa-engineer verifies reproducibility; producer cannot run final visual acceptance), G4 |
| Interactive assumptions (COMP-001) | AI mutating scenario values (forbidden — expansion doc §1.2); silent defaults changing scenarios (PRODUCT_FLOW UI rules) | G0, G2, G3, G4 |
| Financial (COMP-003/Phase C) | Financial estimates presented as official facts (expansion doc §1.5 prohibition); unsourced market values (agent file prohibition); tenant leakage of assumptions | G0, G2, G3, G4, G5 |
| Assemblage/air-rights (COMP-002) | Presenting transferable rights as owned/as-of-right (GDS §6.5 prohibition); split-lot geometry errors | G0, G2, G3, G4; professional-review (G6-style human) gate before any user-facing transferability claim |
| Professional-review package (COMP-006) | Frozen-version reproducibility failures; cross-tenant exposure of review artifacts | G0, G2, G3, G4, G5 |
| Opportunity search (COMP-004/005) | Dataset licensing/terms at citywide scale; hidden score components (expansion doc §1.8); labeling properties "developable" from screening scores (agent file prohibition); PostGIS query cost | G0, G1, G2, G3, G4, G5 |
| External API (COMP-007) | Provenance-stripped responses; rate-limit/auth surface | G0, G2, G3, G4, G5 |
| Cross-cutting | Dual planning documents (pack exec plan vs GDS plan) drifting apart — mitigated by §7 merging the pack into the GDS plan as the single M5 sequence; 5 non-conformant agent files dispatched prematurely (§4) | — |

---

## 7. Refreshed GDS overlap inventory and EXACT proposed changes to `docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md`

**PROPOSALS ONLY — the plan file has not been edited. Owner reviews and approves; the orchestrator applies.**

### 7.1 Refreshed overlap inventory (pack ↔ GDS)

The GDS plan was written 2026-07-16 while 11 of 14 pack files were missing (its §1 caveat, B-005). With the full pack now integrated, the refreshed comparison:

**Overlaps (merge, do not duplicate):**
1. **Financial feasibility:** pack COMP-003 (`3D_AND_UI_EXECUTION_PLAN.md`) ≡ GDS Phase C financial evaluator (GDS §12C; plan §3 order 5, M5-T003). Same producer (`financial-feasibility-engineer`), same versioned-assumption requirements (expansion doc §1.5 = GDS §6.3). One workstream.
2. **Assemblage/air-rights:** pack COMP-002 + expansion doc §1.3 ≡ GDS §6.5 entitlement-strategy items (lot merger, TDR, ZLDA) in the Strategic Upside track (Phase E, plan §3 order 7). The pack adds the deterministic geometry half (adjacency, unused-rights math) that GDS assumes.
3. **Interactive assumptions:** pack COMP-001 (expansion doc §1.2) is the UI/state-machine surface of the GDS `assumption_set` contract (plan §4); backend-controlled recalculation in both.
4. **Scenario geometry:** pack 3D-002 ≡ the `scenario_geometry` contract the plan §4 already lists — the plan anticipated this merge.
5. **Floor stacking:** expansion doc §1.6 ≡ GDS §9 "floor-by-floor program and area accounting" in `candidate_record`.
6. **Render-only 3D truth:** pack 3D docs §2/§9 ≡ GDS §13.13 — identical decision, no conflict.
7. **Explainability style:** expansion doc §1.8 explainable score ≡ GDS §10 explanation contract pattern (visible components, no lone unexplained number).

**Gaps (pack covers what GDS does not):** citywide opportunity search + saved searches + alerts (expansion doc §1.4 — GDS is per-property; the reverse citywide workflow is new, M7); premium design system and visual acceptance standard (design doc + visual standard — GDS has no UI-quality layer); professional-review escalation packaging (expansion doc §1.9 — GDS routes questions but does not define the frozen review package); external API product (expansion doc §1.10); the five concrete specialist agents.

**Gaps (GDS covers what the pack does not):** candidate grammar/seeded generation/lineage/rejection records (GDS §5, §9); Pareto multi-objective search, clustering, diversity metrics, compute budgets, benchmarking (GDS §7–§8); five-axis status vector (§3.3); precedent learning (Phase F); explanation contract (§10).

**Conflicts:** (a) task-ID convention — pack 3D-/UI-/COMP- vs repo `M<milestone>-T<number>`; resolved by re-keying (§1). (b) Producer overlap on assemblage: pack names geospatial-engineer, GDS Phase E names ai-pipeline + opportunity-search engineers; resolved by splitting deterministic geometry (geospatial-engineer) from strategy framing (Phase E). (c) The plan's several "B-005-missing" statements are now stale. No substantive architectural conflict was found: the pack and GDS prescribe the same truth model, the same Render/Supabase placement, and the same gate discipline.

### 7.2 Exact old-text → new-text proposals (8 changes)

**P1 — Status line (plan line 3).**
OLD:
```
- **Status:** DRAFT FOR OWNER REVIEW — no tasks contracted, no code authorized by this document
```
NEW:
```
- **Status:** DRAFT FOR OWNER REVIEW — no tasks contracted, no code authorized by this document. Overlap inventory refreshed 2026-07-17 after the complete 3D/UI expansion pack was integrated additively (M0-T010 Phase 1, commit d25d2b2, ZIP sha256 0C89C2B1…FB146A); refresh details: docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md §7.
```

**P2 — Agents row of the §1 table (plan line 19).**
OLD:
```
| Agents | scenario-optimization-engineer, rules-engineer, geospatial-engineer, ai-pipeline-engineer registered today | Cover phases B–D producers; **financial-feasibility-engineer + opportunity-search-engineer are B-005-missing** |
```
NEW:
```
| Agents | scenario-optimization-engineer, rules-engineer, geospatial-engineer, ai-pipeline-engineer registered; financial-feasibility-engineer, opportunity-search-engineer, 3d-massing-engineer, product-design-director, visual-quality-reviewer added 2026-07-17 (M0-T010 Phase 1) | All GDS phase producers and reviewers now exist. The 5 pack agent files still need roster-convention alignment (memory/permissionMode/isolation frontmatter + ADR-005 protocol sections) before first dispatch — see docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md §4 |
```

**P3 — §1 overlap-inventory caveat paragraph (plan line 21, the full bold paragraph beginning "Overlap-inventory caveat (blocking for completeness):").**
OLD (full paragraph):
```
**Overlap-inventory caveat (blocking for completeness):** GDS §2.1 requires inventorying overlap with the competitive-feature, financial-feasibility, opportunity-search, and 3D/UI execution-plan documents — but 4 of those documents and all 5 expansion agents are still missing (B-005: `COMPETITIVE_FEATURE_EXPANSION.md`, `3D_AND_UI_EXECUTION_PLAN.md`, `3D_VISUAL_ACCEPTANCE_STANDARD.md`, `.claude/rules/3d-ui-expansion.md` + 5 agent files). This plan inventories everything that exists. **Owner decision needed:** supply the missing files, or declare GDS the superseding document for the financial/opportunity workstreams so B-005 can be re-scoped.
```
NEW:
```
**Overlap-inventory caveat — RESOLVED 2026-07-17:** the owner recovered the complete pack ZIP and it was integrated additively at manifest paths (M0-T010 Phase 1, commit d25d2b2); the owner decision of 2026-07-16 (B-005 audit log) stands: GDS does NOT supersede the pack — they are complementary. Refreshed inventory (full version: docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md §7.1): pack COMP-003 financial feasibility = GDS Phase C financial evaluator (one workstream, M5-T003); pack COMP-002 assemblage/air-rights supplies the deterministic geometry feeding the GDS §6.5 Strategic Upside track (Phase E, M5-T005); pack COMP-001 interactive assumptions is the UI/state-machine surface of the assumption_set contract; pack 3D-002 scenario-geometry schema is absorbed into M5-T001 Phase A (scenario_geometry, §4 below); pack Workstreams A–C implement the render-only geometry pipeline GDS §13.13 assumes; pack COMP-004/COMP-005 citywide opportunity search + explainable score are OUTSIDE GDS scope and form a separate M7 workstream; the premium design system applies to the imminent M2 Confirm screen. Pack task IDs (3D-/UI-/COMP-) are workstream labels only and are re-keyed to M<milestone>-T<number> at contracting.
```

**P4 — §3 table, order-1 row (plan line 41).**
OLD:
```
| 1 (after first Property screen) | **M5-T001 — Phase A contracts + benchmark fixtures:** candidate_record v1, typology descriptor, objective_set, assumption_set, strategy_suggestion, explanation_record, 5-axis status extension (additive coverage_status v1.x); synthetic + real benchmark fixtures; reproducibility/diversity acceptance gates defined | contract v1.1; Priority 4 screen accepted | G0,G2,G3,G4 | backend-engineer + rules-engineer review |
```
NEW:
```
| 1 (READY — both triggers met: M1-T006 contract v1.1 and M2-T001 first Property screen accepted) | **M5-T001 — Phase A contracts + benchmark fixtures:** candidate_record v1, typology descriptor, objective_set, assumption_set, strategy_suggestion, explanation_record, 5-axis status extension (additive coverage_status v1.x), scenario_geometry + geometry_artifact (absorbs pack task 3D-002 and its fixture pack incl. 3D_VISUAL_ACCEPTANCE_STANDARD golden scenes); synthetic + real benchmark fixtures; reproducibility/diversity acceptance gates defined | M1-T006 (accepted); M2-T001 (accepted); 3D-001 architecture ADR | G0,G2,G3,G4 | backend-engineer + 3d-massing-engineer; geospatial-engineer + rules-engineer review |
```

**P5 — §3 table, order-5 row (plan line 45).**
OLD:
```
| 5 | **M5-T003 — Phase C evaluators:** planning proxies + financial evaluator, versioned modules, editable/dated/sourced assumptions, sensitivity | M5-T002 | G0,G2,G3,G4,G5 | scenario-optimization-engineer + financial-feasibility-engineer (B-005) |
```
NEW:
```
| 5 | **M5-T003 — Phase C evaluators:** planning proxies + financial evaluator, versioned modules, editable/dated/sourced assumptions, sensitivity (merges pack COMP-003 financial feasibility — one workstream) | M5-T002 | G0,G2,G3,G4,G5 | scenario-optimization-engineer + financial-feasibility-engineer |
```

**P6 — §3 table, order-7 row (plan line 47).**
OLD:
```
| 7 | **M5-T005 — Phase E strategy intelligence + Strategic Upside track** | M5-T004; ai-pipeline injection defenses (M3) | G0,G2,G3,G4,G5,G6-style human review | ai-pipeline-engineer + opportunity-search-engineer (B-005) |
```
NEW:
```
| 7 | **M5-T005 — Phase E strategy intelligence + Strategic Upside track** (consumes pack COMP-002 assemblage/air-rights: deterministic adjacency/unused-rights geometry produced by geospatial-engineer feeds this phase; transferability status always explicit) | M5-T004; ai-pipeline injection defenses (M3); M2 adjacency geometry | G0,G2,G3,G4,G5,G6-style human review | ai-pipeline-engineer + opportunity-search-engineer |
```

**P7 — §6 second bullet (plan line 78).**
OLD:
```
- **AFTER the first Property screen:** M5-T001 Phase A contracts + benchmark fixtures (cheap, unblocks everything later, no optimizer code); MASTER_EXECUTION_PLAN/IMPLEMENTATION_SEQUENCE additive updates; B-005 resolution decision.
```
NEW:
```
- **AFTER the first Property screen (trigger met — M2-T001 accepted):** M5-T001 Phase A contracts + benchmark fixtures (cheap, unblocks everything later, no optimizer code); MASTER_EXECUTION_PLAN/IMPLEMENTATION_SEQUENCE additive updates; M2 design-system tasks (pack UI-001/UI-002, re-keyed) ahead of the Confirm screen; 3D-001 architecture ADR; agent-roster conformance for the 5 pack agent files. B-005 resolution is closed (pack integrated 2026-07-17).
```

**P8 — §8 item 2 (plan line 92).**
OLD:
```
2. Decide the B-005 question in §1 (supply the 4 missing docs + 5 agents, or declare GDS superseding for financial/opportunity scope).
```
NEW:
```
2. RESOLVED 2026-07-17: the owner supplied the complete pack ZIP; all 14 files integrated additively (M0-T010 Phase 1, commit d25d2b2). GDS does not supersede the pack (owner decision 2026-07-16, recorded in the B-005 audit log). Remaining ask: approve the refreshed overlap changes P1–P8 in docs/3D_UI_EXPANSION_INTEGRATION_REPORT.md §7.2.
```

---

## 8. Summary for the orchestrator

1. Accept/record: all 18 accepted tasks valid; pack integrates without invalidating anything; M2-T001 gets a prospective design-conformance flag only.
2. Immediate small work: roster conformance for the 5 agent files (before any dispatch of them); UI-001/UI-002 to serve the Confirm screen; 3D-001 ADR; Phase A contracts trigger is already met.
3. Owner review needed: GDS plan proposals P1–P8 (§7.2); the `geometry-artifacts` bucket addition to the PRD §16 list via the 3D-001 ADR.
4. B-005 can be closed once the orchestrator records the manifest-completeness verification (task packet output 3): all 14 entries present at exact paths, 3 pre-existing byte-identical, evidence in the producer report.
5. Blockers unchanged: B-001 (Supabase) and B-002 (Render) now also gate the geometry/GLB pipeline; B-001 remains the highest-leverage human action.
