# M5-T001 — DRAFT task packet (for owner review; NOT contracted, NOT started)

**Status:** proposal only, returned for owner review. Not a contracted task — no `tasks/M5-T001.json`
exists and no work has begun. On owner approval it is instantiated via `/start-controlled-task`
(`new-task`), which mints the tracked packet and G0 readiness. **CP-0032 is not used.**

**Milestone:** M5 — Scenario and optimization engine (`depends_on [M2, M4]`).
**Title:** Deterministic, coverage-aware scenario **foundation** consuming the canonical draft
zoning-floor-area cap (no independent legal calculation).

---

## 1. Framing (what this is, and explicitly is NOT)

This first M5 slice builds the deterministic scaffold that assembles *existing* rule-evaluation
output into a *typed, provenance-preserving scenario object*. It performs **no legal calculation of
its own**. The only implemented zoning rule family is **R5 residential FAR** (`r5-residential-far`,
draft / `needs_review`), whose evaluation trace already emits the canonical output
**`max_residential_floor_area_sq_ft`** (with `max_residential_far`, citations to ZR §23-21, effective
window, and lifecycle status). M5 **consumes that value and its trace**; it does not recompute
`FAR × lot_area` as a second legal path.

`max_residential_floor_area_sq_ft` is a **draft maximum residential zoning-floor-area cap** under ZR
§23-21 — a regulatory ceiling on countable zoning floor area. It is **explicitly NOT**: gross building
area, net area, sellable/rentable area, feasible floor area, a construction quantity, or any part of a
buildable envelope. Every other envelope constraint (height, stories, setbacks, yards, lot coverage,
open space, parking, street wall, use group, overlays) **does not exist as a rule** and MUST NOT be
inferred, defaulted, or estimated.

The payoff: a strict, honest structure that later M5/M6 work builds on — while structurally
preventing a floor-area cap from being presented as a building.

---

## 2. Objective (packet `objective`)

Create a deterministic, strict-JSON, coverage-aware **scenario foundation** at the service layer that
consumes a canonical `property_profile` (1.4.0) and a `rule_evaluation` (1.0.0) result read-only, and
produces a typed **scenario object** with an explicit **constraint/completeness model**. The scenario:

1. Classifies every candidate input constraint into a typed completeness state (§4), preserving
   provenance and completeness status on each.
2. **Consumes** the canonical `max_residential_floor_area_sq_ft` output and its evaluation trace from
   `rule_evaluation` — **only where applicable** (R5, `conditional`, no conflict/uncertainty) — and
   surfaces it as a **draft zoning-floor-area cap** with the §1 label. It does not re-derive the value.
3. Produces **no scenario** on spatial conflict, controlling-rule conflict, professional-review-
   required, or malformed/non-finite input — returning a typed no-scenario outcome with reasons.
4. Carries the draft / `needs_review` lifecycle and a not-Verified disclaimer end-to-end; no field
   ever equals `verified`.
5. Emits the **rule-coverage dependency matrix** (§7) naming the rule families still required before
   any scenario may be called a buildable-envelope result.

Additive + fail-closed only. Consume profile/rule-evaluation/spatial contracts read-only; do not
modify the profile builder, spatial engine, rule engine, or any canonical contract. No rule is
published or Verified; no scenario is ever Verified.

## 3. Business reason

M4 delivers draft rule evaluation; M5 is where evaluation becomes *feasibility framing*. The highest-
value next step is the deterministic scaffold that assembles the canonical draft output **honestly** —
showing "here is your draft zoning-floor-area cap, and here is everything still unknown before this is
a real envelope" — instead of overclaiming. Doing the completeness model and coverage matrix first
prevents the most dangerous failure mode: a floor-area cap presented as a complete building.

---

## 4. Typed constraint / completeness model (core deliverable)

A `ConstraintCompleteness` enum + per-constraint record. Every constraint the scenario *could* use is
represented with exactly one state — nothing silently absent:

| State | Meaning | Source of truth | Scenario effect |
|---|---|---|---|
| `known` | Value present from an accepted/authoritative source | e.g. `lot_area` from PLUTO / lot geometry | usable as a hard input |
| `draft` | Value from a `needs_review` rule (never Verified) | R5 `max_residential_floor_area_sq_ft` (+ trace) | usable, taints result as draft/non-final |
| `missing` | No rule family or datum provides it | height, setbacks, yards, lot coverage, parking, etc. | **may not be inferred**; recorded as a gap; blocks any buildable-envelope claim |
| `conflicting` | Sources/rules disagree (`data_conflict`) | rule_evaluation `rule_conflict` / spatial crosscheck | **blocks any scenario** |
| `unsupported` | District/rule family not implemented | rule_evaluation `unsupported` / `family_coverage` | visible unsupported; no cap surfaced |
| `professional_review_required` | Spatial uncertainty or fail-safe; no definitive value | rule_evaluation `professional_review_required` / `spatial_uncertainty` | **blocks any scenario** |

Each record carries: `key`, `state`, `value` (nullable), `unit`, `provenance` (propagated verbatim —
rule citation(s), `rule_id`/`rule_version`/`rule_status` for the cap; profile field + dataset for lot
area), and `note`. Provenance and completeness state are preserved on **every** constraint **and every
output** of the scenario.

---

## 5. Deterministic scenario decision logic

```
INPUT: property_profile (1.4.0), rule_evaluation (1.0.0)   [both read-only]
1. Build the constraint/completeness set (§4) from both contracts, provenance preserved.
2. HARD STOP -> NO SCENARIO (typed no_scenario outcome + reasons) if ANY:
     - rule_evaluation.coverage_status == data_conflict, OR any constraint == conflicting
     - professional_review_required == true, OR spatial_uncertainty present,
       OR any constraint == professional_review_required
     - malformed / non-finite / non-JSON-safe numeric anywhere (fail-closed, no crash)
     - required controlling inputs absent
3. UNSUPPORTED -> NO CAP: district/family unsupported/not_applicable -> typed stub, reasons only.
4. PRELIMINARY SCENARIO — permitted ONLY when ALL hold:
     - R5 family applicable & confident (coverage_status == conditional)
     - rule_evaluation trace carries a finite draft max_residential_floor_area_sq_ft
     - no conflict / no professional-review flag (from step 2)
   -> SURFACE the canonical draft cap verbatim from the trace (do NOT recompute):
        draft_zoning_floor_area_cap_sq_ft = <trace.outputs.max_residential_floor_area_sq_ft>
      with provenance = the rule citation(s) + rule_id/version/status from the same trace.
   -> LABEL (mandatory, attached to the value):
        "DRAFT maximum residential ZONING-FLOOR-AREA CAP under ZR 23-21. NOT gross, net, sellable, or
         feasible floor area; NOT a buildable envelope. Height, stories, setbacks, yards, lot
         coverage, open space, parking, and street-wall constraints are UNKNOWN (see coverage
         matrix). Draft rule (needs_review); requires professional review; NOT Verified."
   -> coverage_status carried through (never verified); needs_review + not_verified_disclaimer present.
5. OPTIONAL integrity check (verification-only): the engine MAY recompute far*lot_area purely to
   COMPARE against the canonical trace value. It MUST NOT replace or override the canonical value, and
   MUST FAIL CLOSED (emit a data_conflict no-scenario outcome) on any disagreement beyond a documented
   tolerance. The surfaced value is always the canonical trace output, never a locally derived one.
6. Deterministic ordering: constraints, reasons, scenarios, and traces emit in a stable documented
   sort (byte-identical output for identical input).
```

### 5a. Hard prohibitions (enforced by tests)
- **No independent legal calculation.** The cap is consumed from the canonical trace; any recompute is
  verification-only per step 5 and never the surfaced value.
- **No inference** of height, story count, setbacks, yards, parking, lot coverage, efficiency, unit
  count, gross-to-net ratio, or constructability — from the cap or anything else. These are `missing`.
- **No relabeling** of the cap as gross/net/sellable/feasible floor area or as an envelope/building.
- **No hidden utilization or optimization defaults.** A preliminary scenario equals the raw draft cap.
  Any variant (e.g. an efficiency or utilization factor) exists **only** as an *explicit typed
  assumption* on the scenario, defaulting to none; there are no implicit percentages, yields, or
  optimization defaults anywhere in the path.
- **Never `verified`.** No scenario, value, or field is Verified.

---

## 6. Acceptance scenarios (executable pack — all required)

- **AS-1 confident R5 cap:** single-district-confident R5 profile + `conditional` R5 evaluation whose
  trace carries a finite `max_residential_floor_area_sq_ft` → one PRELIMINARY scenario surfacing that
  **canonical** value verbatim with the §5.4 label, full provenance, coverage `conditional` (never
  `verified`), needs_review + disclaimer present. Test asserts the surfaced value equals the trace
  value (not a locally recomputed one).
- **AS-2 unsupported district:** non-R5 / unimplemented family → typed `unsupported` stub, no cap, a
  visible reason (not silence).
- **AS-3 missing constraint:** required datum absent → NO scenario; typed outcome naming the missing
  constraint; nothing inferred.
- **AS-4 spatial uncertainty:** boundary/split-lot/sliver/invalid-geometry or
  `professional_review_required` → NO scenario; share ranges / review flags surfaced, never collapsed.
- **AS-5 legal-rule conflict:** `data_conflict` / `rule_conflict` → NO scenario; conflict surfaced with
  competing-rule provenance.
- **AS-6 malformed / non-finite inputs:** NaN / ±inf / huge-int / wrong-type cap or area → fail-closed
  typed outcome, **no crash**, no negative/NaN/inf value, strict-JSON preserved.
- **AS-7 integrity disagreement fails closed:** a fixture where a verification recompute disagrees with
  the canonical trace value → engine emits a `data_conflict` no-scenario outcome and never surfaces
  either number as a result (proves step-5 fail-closed, canonical-value-not-replaced behavior).
- **AS-8 deterministic ordering:** identical input → byte-identical output.
- **AS-9 never-Verified:** exhaustive check no field equals `verified`; disclaimer + `needs_review`
  lineage on every produced scenario and on the cap value.
- **AS-10 provenance & completeness preserved:** every constraint and every output carries its
  completeness state and provenance traceable to source (rule citation(s)+rule_id/version/status for
  the cap; profile field+dataset for lot area).
- **AS-11 explicit-assumption-only variation:** a preliminary scenario with no assumptions equals the
  raw draft cap; a variant differs from it **only** by an explicitly declared typed assumption — a test
  proves no hidden utilization/efficiency/optimization factor is ever applied.
- **AS-12 regression:** full repository CI green; zero modification to profile / spatial / rule-engine /
  canonical-contract code.

---

## 7. Rule-coverage dependency matrix (required deliverable)

What must exist before a scenario may be presented as a **real buildable envelope**. Only the first row
exists today; everything else is `missing` and MUST NOT be inferred or defaulted.

| Constraint family | Governs | Rule status today | Blocks buildable-envelope? |
|---|---|---|---|
| Residential FAR / floor-area cap (R5) | draft max residential zoning floor area | **DRAFT** (`r5-residential-far`, needs_review) | Provides the draft cap **only** |
| Height limit / sky-exposure plane | max height / story count | **MISSING** | **YES** |
| Front / side / rear yard setbacks | buildable footprint | **MISSING** | **YES** |
| Lot coverage / open-space ratio | footprint ↔ FAR interaction | **MISSING** | **YES** |
| Street wall / base height | lower-massing form | **MISSING** | **YES** |
| Parking / loading | ground/cellar program | **MISSING** | Affects feasibility |
| Use group / commercial overlay | permitted use mix | **MISSING** | Affects program |
| Special districts / mapped overlays | modifications to base rules | **MISSING** | **YES** if present |
| Density bonuses (e.g. inclusionary housing) | FAR bonus | **MISSING** | Optional uplift |
| Higher-density bulk/tower (non-R5) | tower massing | **MISSING / out of R5 scope** | N/A for R5 |
| Gross-to-net / efficiency, unit count, constructability | usable/feasible area, yield | **NOT a zoning rule — out of scope** | Never inferred here |

**Rule:** a scenario may be called a real buildable envelope only when at least the height,
setback/yard, and lot-coverage/open-space rows are `known`/`draft` and non-conflicting. Until then,
output is the draft zoning-floor-area cap only.

---

## 8. Scope

**Producer:** `scenario-optimization-engineer`. **Independent reviewers:** `data-contract-verifier`
(new scenario output contract), `code-reviewer`, `qa-engineer`, `security-reviewer`.
**Required gates (one frozen SHA):** **G0, G1, G3, G4, G5.** No G6 for the scenario engine itself — but
it inherits the M4 draft lineage and cannot be *accepted* until its dependencies clear G6 (§9).

**Allowed paths (proposed):**
- `services/api/app/scenario/**` (new deterministic foundation module + typed constraint model;
  consume profile/rule-evaluation via read-only imports only)
- `services/api/tests/scenario/**` (acceptance pack AS-1..AS-12)
- `packages/contracts/schemas/v1/scenario.schema.json` (new **additive draft** output contract;
  reference `coverage_status` narrowed to exclude `verified`, never redefined — exactly as
  `rule_evaluation` does) + its typegen/bundle/fixtures
- `project-control/reports/M5-T001-producer-report.md`

**Forbidden paths / actions:**
- `services/api/app/profile/**`, `services/api/app/spatial/**`, `services/api/app/rules/**` (read-only)
- Any existing canonical contract (`property_profile`, `rule_evaluation`, `coverage_status`) — no edits
- `services/api/app/api/v1/**` / any new public endpoint (service-layer only this slice)
- `apps/web/**`, any 3D rendering, any polished UI — **excluded** (expansion/3D holds active; no ledger
  slice authorizes UI here)
- Independent legal recomputation as the surfaced value; inferring height/setback/yard/parking/lot-
  coverage/efficiency/unit-count/gross-to-net/constructability; relabeling the cap; hidden utilization
  or optimization defaults; emitting `verified`; publishing/Verifying any rule; collapsing spatial
  uncertainty; `project-control/**` except the producer report; `.claude/**`

---

## 9. Draft-M4 authorization, dependencies, and the acceptance boundary

- **M5 engineering is explicitly authorized against the merged M4 artifacts in their DRAFT /
  `needs_review` state, WITHOUT treating M4 as accepted, Published, or Verified** (owner directives
  2026-07-21 / 2026-07-22). M5-T001 consumes M4-T005's `rule_evaluation` contract + M4-T002's
  integration as draft engineering inputs.
- **Dependencies:** M4-T005 (`rule_evaluation` contract + serializer), M4-T002 (integration),
  M2-T012 (profile), M2-T013 (spatial) — M2 accepted; M4 merged as **draft** (none accepted).
- **Acceptance boundary:** M5-T001 may be built and independently reviewed now, but its **final
  acceptance** waits until its M4 dependencies are accepted, which is blocked on the genuine **G6**
  qualified-human legal approval of M4-T001. **G6 is not weakened.** **B-010** (client R5 benchmark)
  is NOT a blocker for this task or M5 engineering — it scopes only the client R5 benchmark-validation
  item.
- **Control-model note:** if `/start-controlled-task` (`new-task`/`claim`) refuses to contract M5-T001
  because its M4 dependencies are unaccepted, **stop and report the control-model blocker** — do NOT
  mark M4 accepted and do NOT weaken G6. (A dependency-*acceptance* precondition is enforced by the CLI
  only on `accept`, not expected on `new-task`/`claim`; this is the fallback if that assumption is
  wrong.)
- Nothing in this task Publishes, Verifies, or makes anything legally final. Every scenario is draft.

---

## 10. Ready-to-instantiate packet (created only on owner approval)

On approval, `/start-controlled-task` mints `tasks/M5-T001.json` with: the objective (§2), allowed/
forbidden paths (§8), the AS-1..AS-12 pack (§6), `required_gates [G0,G1,G3,G4,G5]`, producer
`scenario-optimization-engineer`, reviewers as above, and the coverage matrix (§7) as an acceptance
artifact. Implementation proceeds to **one frozen SHA** carrying G1/G3/G4/G5, and the evidence packet
is returned **before** any M5 product merge. **CP-0032 is not used;** UI and 3D stay out of this slice.
