# M5-T001 — DRAFT task packet (for owner review; NOT contracted, NOT started)

**Status:** proposal only. This document is returned for owner review. It is **not** a
contracted task — no `tasks/M5-T001.json` has been created and no work has begun. On owner
approval it is instantiated via `/start-controlled-task` (`new-task`), which mints the tracked
packet and G0 readiness. Nothing here starts M5 implementation.

**Milestone:** M5 — Scenario and optimization engine (`depends_on [M2, M4]`).
**Title:** Deterministic, coverage-aware scenario/envelope **foundation** (FAR-capacity only).

---

## 1. Framing (what this is, and explicitly is NOT)

This first M5 slice builds the deterministic scaffold that turns *rule-evaluation outputs* into a
*typed, provenance-preserving scenario object* — **not** a complete zoning envelope and **not** a
feasible building. The only zoning rule family that exists today is **R5 residential FAR**
(`r5-residential-far`, draft/`needs_review`, emitting `max_residential_far`). Every other legal
constraint that a real buildable envelope requires — height, setbacks, yards, lot coverage, open
space, parking, street wall, use group, overlays — **does not exist as a rule yet** and MUST NOT be
invented or defaulted.

Therefore the deliverable is deliberately bounded:

- It **consumes** the canonical `property_profile` (1.4.0) and `rule_evaluation` (1.0.0) contracts
  read-only.
- It computes, **only where FAR and lot area are both known and confident**, a clearly-labeled
  **preliminary FAR-capacity scenario** (`max residential zoning floor area = max_residential_far ×
  lot_area`).
- It **refuses to produce any scenario** when evidence or controlling rules conflict, when spatial
  assignment is uncertain, or when inputs are malformed.
- It **never** describes FAR-only output as a buildable envelope or a feasible building, and **never**
  emits a Verified result.

The valuable payoff: a strict, honest data structure the later M5/M6 work (and eventually 3D) can
build on — while structurally preventing a FAR number from being presented as a building design.

---

## 2. Objective (packet `objective`)

Create a deterministic, strict-JSON, coverage-aware **scenario foundation** at the service layer that
consumes a canonical property profile (`property_profile` 1.4.0: `zoning_features`, `lot_geometry`,
`spatial_intersection`) and a `rule_evaluation` 1.0.0 result (draft R5 FAR family), and produces a
typed **scenario object** with an explicit **constraint/completeness model**. The scenario:

1. Classifies every candidate input constraint into a typed completeness state (§4).
2. Uses the R5 `max_residential_far` output **only where applicable** (supported, confident, no
   conflict) to compute a **FAR-capacity** figure, labeled preliminary and non-final.
3. Produces **no scenario** on spatial conflict, controlling-rule conflict, professional-review-
   required, or malformed/non-finite input — returning a typed no-scenario outcome with reasons, not
   a guessed building.
4. Preserves provenance from **every** input constraint into **every** derived value in the scenario.
5. Carries the draft/`needs_review` lifecycle and a not-Verified disclaimer end-to-end; no field ever
   equals `verified`.
6. Emits a **rule-coverage dependency matrix** (§7) naming the additional rule families required
   before any scenario can become a real buildable-envelope result.

Additive + fail-closed only. Consume profile/rule-evaluation/spatial contracts read-only; do not
modify the profile builder, spatial engine, rule engine, or any canonical contract. No rule is
published or Verified; no scenario is ever Verified.

## 3. Business reason

M4 delivers draft rule evaluation; M5 is where evaluation becomes *feasibility*. The single highest-
value next step is the deterministic scaffold that assembles constraints into a scenario **honestly**
— so the product can show "here is your FAR capacity, and here is everything still unknown before this
is a real envelope" instead of overclaiming. Doing the completeness model and coverage matrix first
prevents the most dangerous failure mode: a FAR calculation presented as a complete building.

---

## 4. Typed constraint / completeness model (core deliverable)

A `ConstraintCompleteness` enum + per-constraint record. Every constraint the scenario *could* use is
represented with exactly one state — nothing is silently absent:

| State | Meaning | Source of truth | Scenario effect |
|---|---|---|---|
| `known` | Value present from an accepted/authoritative source | e.g. `lot_area` from PLUTO / lot geometry | usable as a hard input |
| `draft` | Value from a `needs_review` rule (never Verified) | e.g. R5 `max_residential_far` | usable, but taints result as draft/non-final |
| `missing` | No rule family or datum provides it | — | **may not be invented**; recorded as a gap, blocks buildable-envelope claim |
| `conflicting` | Sources/rules disagree (`data_conflict`) | rule_evaluation `rule_conflict` / spatial crosscheck | **blocks any scenario** |
| `unsupported` | District/rule family not implemented | rule_evaluation `unsupported` / `family_coverage` | visible unsupported; no capacity computed |
| `professional_review_required` | Spatial uncertainty or fail-safe; no definitive value | rule_evaluation `professional_review_required` / `spatial_uncertainty` | **blocks any scenario** |

Each constraint record carries: `key`, `state`, `value` (nullable), `unit`, `provenance` (propagated
verbatim from the source contract — rule citation(s), `rule_id`/`rule_version`/`rule_status`, or
profile field + source dataset), and `note`. The model is the single gate that decides whether a
scenario may be produced (§5).

---

## 5. Deterministic scenario decision logic

```
INPUT: property_profile (1.4.0), rule_evaluation (1.0.0)
1. Build the constraint/completeness set (§4) from both contracts (read-only, provenance-preserved).
2. HARD STOP → NO SCENARIO (typed no_scenario outcome + reasons) if ANY:
     - rule_evaluation.coverage_status == data_conflict, OR any constraint == conflicting
     - rule_evaluation.professional_review_required == true, OR spatial_uncertainty present,
       OR any constraint == professional_review_required
     - malformed / non-finite / non-JSON-safe numeric input anywhere (fail-closed, no crash)
     - required controlling inputs absent (e.g. lot_area missing/None)
3. UNSUPPORTED → NO CAPACITY: district/family unsupported or not_applicable → typed
   unsupported/not_applicable scenario stub (reasons only, no computed capacity).
4. PRELIMINARY FAR-CAPACITY SCENARIO — permitted ONLY when ALL hold:
     - R5 family applicable & confident (coverage_status == conditional), max_residential_far is a
       finite draft value
     - lot_area known & finite
     - no conflict / no professional-review flag (from step 2)
   → compute max_residential_zfa = max_residential_far * lot_area (strict finite arithmetic)
   → label: "PRELIMINARY — FAR capacity only. NOT a buildable envelope, NOT a feasible building.
     Height, setbacks, yards, lot coverage, open space, parking, and street-wall constraints are
     UNKNOWN (see coverage matrix). Draft rules, requires professional review. Not Verified."
   → coverage_status carried through (never verified); needs_review + not_verified_disclaimer present
5. Deterministic ordering: constraints, reasons, and any scenario list are emitted in a stable,
   documented sort (byte-identical output for identical input).
```

**Invariants enforced by tests (§6):** no invented constraint defaults; FAR-capacity never relabeled
as envelope/feasible/complete; no scenario on conflict/uncertainty/malformed input; provenance present
on every derived value; strict-JSON (finite numbers only); never `verified`.

---

## 6. Acceptance scenarios (executable pack — all required)

- **AS-1 confident R5 FAR-capacity:** single-district-confident R5 profile + `conditional` R5
  evaluation with finite `max_residential_far` and known `lot_area` → one PRELIMINARY FAR-capacity
  scenario with `max_residential_zfa = far*area`, the non-envelope label, full provenance, coverage
  `conditional` (never `verified`), needs_review + disclaimer present.
- **AS-2 unsupported district:** non-R5 / unimplemented family → typed `unsupported` scenario stub,
  no capacity computed, visible reason (not silence).
- **AS-3 missing constraint:** required datum absent (e.g. `lot_area` None) → NO scenario; typed
  no-scenario outcome naming the missing constraint; nothing invented.
- **AS-4 spatial uncertainty:** boundary/split-lot/sliver/invalid-geometry or
  `professional_review_required` → NO scenario; share ranges / review flags surfaced, never collapsed.
- **AS-5 legal-rule conflict:** `data_conflict` / `rule_conflict` present → NO scenario; conflict
  surfaced with competing-rule provenance.
- **AS-6 malformed / non-finite inputs:** NaN / ±inf / huge-int / wrong-type FAR or area → fail-closed
  typed outcome, **no crash**, no negative/NaN/inf capacity, strict-JSON preserved.
- **AS-7 deterministic ordering:** identical input → byte-identical output (constraints, reasons,
  scenarios, traces).
- **AS-8 never-Verified:** exhaustive check that no field anywhere equals `verified`; disclaimer and
  `needs_review` lineage present on every produced scenario and on the FAR-capacity value.
- **AS-9 provenance preservation:** every derived value (incl. `max_residential_zfa`) carries
  provenance traceable to its input constraint(s) — rule citation(s) + `rule_id/version/status` for
  the FAR term, profile field + dataset for lot area.
- **AS-10 regression:** full repository CI green; zero modification to profile / spatial / rule-engine
  / canonical-contract code.

---

## 7. Rule-coverage dependency matrix (required deliverable)

What must exist before a scenario may be presented as a **real buildable envelope**. Only the first
row exists today; everything else is `missing` and MUST NOT be defaulted.

| Constraint family | Governs | Rule status today | Blocks buildable-envelope? |
|---|---|---|---|
| Residential FAR (R5) | max residential zoning floor area | **DRAFT** (M4-T001 `r5-residential-far`, needs_review) | Provides FAR capacity **only** |
| Height limit / sky-exposure plane | max building height / stories | **MISSING** | **YES** |
| Front / side / rear yard setbacks | buildable footprint | **MISSING** | **YES** |
| Lot coverage / open-space ratio | footprint ↔ FAR interaction | **MISSING** | **YES** |
| Street wall / base height | lower-massing form | **MISSING** | **YES** |
| Parking / loading | ground/cellar program | **MISSING** | Affects feasibility |
| Use group / commercial overlay | permitted use mix | **MISSING** | Affects program |
| Special districts / mapped overlays | modifications to base rules | **MISSING** | **YES** if present on lot |
| Density bonuses (e.g. inclusionary housing) | FAR bonus | **MISSING** | Optional uplift |
| Higher-density bulk/tower (non-R5) | tower massing | **MISSING / out of R5 scope** | N/A for R5 |

**Rule:** a scenario may be labeled a real buildable envelope only when the height, setback/yard, and
lot-coverage/open-space rows (at minimum) are `known`/`draft` and non-conflicting. Until then, output
is FAR-capacity only.

---

## 8. Scope

**Producer:** `scenario-optimization-engineer`. **Reviewers (independent):** `code-reviewer`,
`qa-engineer`, `security-reviewer` (+ `data-contract-verifier` if a new scenario contract is authored).
**Required gates:** G0, **G1** (if a new additive `scenario` output contract is created), G3, G4, G5.
No G6 for the scenario engine itself — but it inherits the M4 draft lineage and may not be accepted
until its dependencies clear G6 (see §9).

**Allowed paths (proposed):**
- `services/api/app/scenario/**` (new deterministic foundation module + typed constraint model)
- `services/api/tests/scenario/**` (acceptance pack AS-1..AS-10)
- `packages/contracts/schemas/v1/scenario_envelope.schema.json` **only if** a new additive draft
  output contract is authored (never redefining `coverage_status`; reference it, narrowed to exclude
  `verified`, exactly as `rule_evaluation` does) + its typegen/bundle/fixtures
- `project-control/reports/M5-T001-producer-report.md`

**Forbidden paths:**
- `services/api/app/profile/**`, `services/api/app/spatial/**`, `services/api/app/rules/**` (consume
  read-only; no modification)
- Any existing canonical contract (`property_profile`, `rule_evaluation`, `coverage_status`) — no edits
- `services/api/app/api/v1/**` / any new public endpoint (service-layer only this slice)
- `apps/web/**`, any 3D rendering, any polished UI — **excluded** (3D/UI expansion holds active; no
  ledger slice authorizes UI here)
- Publishing/Verifying any rule; emitting `verified`; inventing any legal constraint default;
  collapsing spatial uncertainty; `project-control/**` except the producer report; `.claude/**`

---

## 9. Holds, dependencies, and the acceptance boundary

- **Dependencies:** M4-T005 (`rule_evaluation` contract + serializer), M4-T002 (integration),
  M2-T012 (profile), M2-T013 (spatial) — all merged as **draft** (none accepted).
- Per owner directive 2026-07-21, engineering may proceed on `needs_review` rules. **But** M5-T001
  **cannot be accepted** until its M4 dependencies are accepted, which is blocked on **G6** qualified-
  human legal approval of M4-T001 (+ B-010 client benchmark). So: build + independent review now;
  **final acceptance waits on the genuine G6 legal boundary.**
- Nothing in this task Publishes, Verifies, or makes anything legally final. Every scenario is draft.

---

## 10. Ready-to-instantiate packet (created only on owner approval)

On approval, `/start-controlled-task` mints `tasks/M5-T001.json` with: the objective (§2), the
allowed/forbidden paths (§8), the AS-1..AS-10 acceptance pack (§6), `required_gates`
`[G0,(G1),G3,G4,G5]`, producer `scenario-optimization-engineer`, reviewers as above, and the coverage
matrix (§7) as an acceptance artifact. No checkpoint is created (CP-0032 remains reserved). No M5
implementation begins until the packet is contracted and claimed.
