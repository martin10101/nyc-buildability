# M4-T006 — DRAFT task packet (for owner review; NOT contracted, NOT started)

**Status:** proposal (owner-amended 2026-07-23). Not yet a contracted task — no `tasks/M4-T006.json`
exists and no work has begun until instantiated. On approval it is instantiated via
`/start-controlled-task` (`new-task`). **CP-0032 is not used. No 3D/UI. No hold release. Does not wait
on B-010.**

**Milestone:** M4 — Rule engineering and professional review.
**Title:** R5 residential **height & setback vertical-envelope draft rule family** — per-district (R5 /
R5A / R5B / R5D …) base height, building height, street wall, and setback as **separate typed
constraints**, draft / `needs_review`, extracted with provenance, fail-closed.

---

## 1. Why this task, and why it is smallest-highest-impact

The merged M5-T001 scenario foundation surfaces a draft FAR floor-area cap but marks every envelope
constraint `missing`. Its rule-coverage dependency matrix flags `height_limit`, `street_wall_base_height`,
and `setbacks_yards` as `blocks_envelope=true`. The smallest highest-impact addition is the **vertical
envelope**: base height, building height, street wall, and the setback regime above the base. This is a
**rule-engineering** task extending the M4-T001 engine/DSL (exactly like the R5 FAR rule) — NOT
scenario/UI work. A later M5 task will consume these outputs to compute a narrow bounded massing.

---

## 2. Objective (packet `objective`)

Extract, as a **draft (`needs_review`) rule family** in the existing rules engine/DSL, the current
effective R5-series **height and setback** regulations, producing deterministic outputs for **each R5
district variant scoped separately** (§3), modeled as **separate typed constraints** (§5), each fully
provenance-stamped (§4), evaluated fail-closed against a mandatory **input-readiness matrix** (§6), with
**rule-conflict fail-closed** semantics (§7). No rule is published or Verified; the regime choice and
every dimensional value are a candidate representation awaiting **G6** qualified-human legal approval.
Additive + fail-closed only; the FAR rule, evaluator core, and all canonical contracts are untouched.

---

## 3. Amendment 1 — per-district variants, NO family-wide defaults

- Scope **each exact R5 district as its own case**: R5, R5A, R5B, R5D (and any other mapped R5-series
  variant the official source defines). **Never** use an `R5*` / family-wide default and **never assume
  the variants share dimensions or applicability.** Each variant's base height, building height, street
  wall, and setback (and their applicability conditions) are extracted and encoded independently from
  the official source; where the source gives one variant a value and is silent for another, the silent
  variant is `unsupported` / `professional_review_required`, not inherited.
- A district value that is not exactly one of the encoded variants → `unsupported` (visible), never
  mapped to the "nearest" R5 variant.

## 4. Amendment 3 — per-constraint provenance record (mandatory, every constraint)

For **every** extracted constraint value, record in the rule + surface in the trace:
- **Exact official ZR section/clause** (not just the article) — the specific numbered subdivision.
- **Amendment date and effective date(s)** (`last_amended`, `effective_from`/`effective_to`).
- **Source snapshot id + content hash** — a captured official ZR snapshot (byte-identical, hash-guarded),
  mirroring the `zr-23-21` snapshot mechanism and M4-T005 package-data guard.
- **Precise applicability conditions** attached to the value: district variant, street-width class
  (wide/narrow), building type/condition, lot condition, frontage condition, ground-floor condition, and
  any special-district/overlay condition the source predicates the value on. A value whose applicability
  the source conditions on a factor NOT captured is not emitted as definitive (see §6).

## 5. Amendment 4 — separate typed constraints; preserve min & max; no envelope labeling

- Model **base height**, **building height**, **street wall**, and **setback** as **four separate typed
  constraints** — never collapsed into one number or one "envelope".
- Where the source distinguishes a **minimum and a maximum** (e.g. minimum base height and maximum base
  height, required minimum setback depth and its qualifying height), **preserve both** as typed
  min/max fields; do not reduce a range to a single value.
- **Do NOT label** any output a buildable envelope, feasible building, massing result, or building
  design. These are individual draft regulatory dimensions with provenance — nothing more. (The word
  "envelope" appears only in the task title as the constraint *family* name, never on a result value.)

## 6. Amendment 2 — input-readiness matrix (mandatory deliverable) + fail-closed inputs

Produce an **input-readiness matrix** mapping **every** rule condition/input to an **exact existing
canonical `property_profile` field (by JSON path)** — e.g. district → `zoning.districts[]`,
overlays → `zoning.commercial_overlays[]`, special districts → `zoning.special_districts[]`,
lot area → `lot_geometry.area_sq_ft`, spatial certainty → `spatial_intersection.lot_overall_class`.
For each condition classify readiness: **available** / **uncertain** / **contradictory** /
**unavailable**.
- Any condition that is **missing, uncertain, contradictory, or unavailable** in the canonical profile
  MUST produce a typed **`missing` / `unsupported` / `professional_review_required`** outcome — **never a
  guessed value**.
- **Known readiness gap to surface explicitly:** the current canonical profile exposes no dedicated
  **street-width / frontage / ground-floor** field (verified against `property_profile.schema.json` at
  proposal time). Because R5 height/setback commonly turns on **wide vs narrow street** (and post-City-
  of-Yes may turn on frontage/ground-floor conditions), any constraint the source predicates on those
  factors is **`professional_review_required`** (input unavailable) — it is NOT computed from a guessed
  street class. If the producer discovers such a field does exist, the matrix cites its exact path;
  otherwise the matrix records it as an unavailable input and the dependent constraints fail closed.

## 7. Amendment 5 — competing rules fail closed

If **two or more independently applicable rules** (e.g. a base-district rule and a special-district or
overlay modification, or two source provisions) **compete for the same constraint**, the evaluation
emits **`rule_conflict`** with **no selected value** for that constraint — never a silent precedence
pick. (Reuse the existing `rule_conflict` / competing-rules trace shape.)

## 8. Legal-scope guardrails (READ FIRST)

- **AI extracts; a qualified human decides the law at G6.** The producer captures official ZR text and
  encodes a candidate rule with provenance; legal correctness is a G6 determination, not this task's.
- **Determine the CURRENT effective regime from official sources — do not assume.** R5 height/setback
  historically ran through "height factor" vs "Quality Housing" tracks; the **City of Yes for Housing
  Opportunity** amendment (the FAR rule's `effective_from` is `2024-12-05`) changed residential bulk
  citywide. Identify the exact controlling sections/values in the **current** ZR via
  `official-source-researcher` + `legal-corpus-engineer`, capture verbatim snapshots, record
  `last_amended`. **Never carry forward a remembered pre-amendment value.**
- **Genuine-ambiguity stop condition:** if the official source is genuinely ambiguous on the regime or a
  value in a way that requires human legal interpretation (not mere engineering effort), the producer
  **stops and the orchestrator reports a blocker** — it does NOT guess, and it does NOT weaken G6.
- **No verification, no publication.** Nothing sets `verified` or publishes a rule.

## 9. Scope

**Producer:** `rules-engineer` (single writer). **Source inputs (prerequisite research, not parallel
writers):** `official-source-researcher` + `legal-corpus-engineer` supply verified official ZR
snapshots/sections; `rules-engineer` encodes the DSL. **Independent reviewers:** `code-reviewer`,
`qa-engineer`, `security-reviewer` (+ `data-contract-verifier` only if a contract change proves
necessary — not expected; rule outputs ride the open `rule_evaluation` trace `outputs` object).
**Required gates:** **G0, G2, G3, G4, G5** at one frozen SHA (mirrors M4-T003). **G6** (qualified-human
legal) REQUIRED before any publication/verification or final acceptance — **not** part of this build,
**not weakened**, independent of B-010.

**Allowed paths (proposed):**
- `services/api/app/rules/rulesets/*.rule.json` — new R5 height/setback ruleset(s) (new file(s); do not
  edit `r5_residential_far.rule.json`)
- `services/api/app/rules/schemas/v1/*.schema.json` — only if the DSL needs an additive field for a
  min/max height/setback construct (extend additively; never redefine)
- `services/api/app/_zr_snapshots/v1/*.snapshot.json` (+ the `sync_zr_snapshots` source dir) — new
  official ZR source snapshots (byte-identical + hash-guarded), packaged as data per M4-T005
- `services/api/tests/rules/**` — deterministic, fail-closed, effective-date, provenance, rule-conflict,
  and **negative-control** tests (§10) + installed-wheel deployability guard
- `project-control/reports/M4-T006-producer-report.md` (+ raw source-capture report + the input-
  readiness matrix artifact)

**Forbidden paths / actions:**
- `services/api/app/rules/evaluator.py` and engine core, `r5_residential_far.rule.json`,
  `services/api/app/profile/**`, `services/api/app/spatial/**`, `services/api/app/scenario/**`,
  `services/api/app/api/v1/**`
- Any canonical contract (`property_profile`/`rule_evaluation`/`coverage_status`/`scenario`) — no edits
- `apps/web/**`, any 3D/UI; **yards, lot coverage, parking** (explicitly out — §11)
- Publishing/Verifying any rule; emitting `verified`; inventing any dimension/condition; applying a
  remembered pre-amendment value; silent precedence between competing rules; `project-control/**`
  except own reports; `.claude/**` except own memory

## 10. Acceptance scenarios + Amendment 6 negative controls (executable pack — all required)

Positive:
- **AS-1 per-district confident:** for EACH encoded variant (R5/R5A/R5B/R5D), a supported case →
  deterministic base-height / building-height / street-wall / setback constraints (min & max preserved),
  coverage `conditional` (never `verified`), full trace with resolvable ZR citations + applicability
  conditions, `needs_review` + not-Verified disclaimer.
- **AS-2 provenance fidelity:** every emitted dimension traces to a captured ZR snapshot (exact section
  + verbatim quote + `last_amended` + hash) and carries its precise applicability conditions; a
  tampered/absent snapshot fails closed.
- **AS-3 effective-date boundary:** `as_of` immediately before vs on/after the controlling amendment →
  not-effective vs captured values (before/after fixture per affected variant).
- **AS-4 determinism:** identical input → byte-identical output (trace included).
- **AS-5 never-Verified & draft lifecycle:** every result `needs_review`, coverage ≠ `verified`,
  `rule_release` verified-ineligible.
- **AS-6 installed-wheel deployability:** the new ruleset(s) + ZR snapshots load from the installed
  wheel (`pip install --no-deps .`), guarded like M4-T005; full API suite green; FAR rule, engine core,
  and canonical contracts byte-unchanged.

Negative controls (Amendment 6 — each a distinct fail-closed test):
- **NC-1 district variant:** a value defined for one R5 variant is NOT silently applied to another; the
  silent variant → `unsupported`/`professional_review_required`.
- **NC-2 street-width class:** wide / narrow / **unknown** street — an unknown/unavailable street class
  (no canonical field) → `professional_review_required`, no computed value; a value predicated on street
  width is never emitted from a guessed class.
- **NC-3 special-district / overlay:** a special-district or commercial-overlay condition that modifies
  or competes → `rule_conflict` (§7) or `unsupported`, never a silent base-district value.
- **NC-4 building / ground-floor condition:** a relevant building-type or ground-floor condition the
  source predicates on, when unavailable in the profile → `professional_review_required`.
- **NC-5 missing input:** a required canonical field absent/null → typed `missing` outcome, no value.
- **NC-6 contradictory input:** contradictory canonical inputs (e.g. conflicting district signals) →
  `data_conflict` / `professional_review_required`, no value.
- **NC-7 mutually exclusive rules:** two independently applicable rules for the same constraint →
  `rule_conflict`, no selected value (§7).

## 11. Amendment 7 — out of scope (kept minimal)
- **Yards, lot coverage, parking, 3D, UI are OUT.** They remain the explicit next slices.
- **M5-T001 is unchanged:** it must continue to show height/setback/yard/lot-coverage/parking as
  `missing` and remain explicitly incomplete. This task adds *rules*; it does NOT wire them into the
  scenario builder (a later M5 task does that). No edit to `services/api/app/scenario/**`.

## 12. Dependencies & acceptance boundary
- **Depends on:** M4-T001 (engine + DSL + ZR snapshot mechanism) + the current official ZR. Consumes
  read-only / additively.
- **Acceptance boundary:** built + independently reviewed now (needs_review); **final acceptance and any
  publication remain gated on genuine G6 qualified-human legal approval** — not weakened, independent of
  B-010.

## 13. Ready-to-instantiate packet (created on approval)
`/start-controlled-task` mints `tasks/M4-T006.json` with objective (§2), amendments (§3–§7, §11), legal
guardrails (§8), allowed/forbidden paths (§9), AS-1..AS-6 + NC-1..NC-7 (§10), `required_gates
[G0,G2,G3,G4,G5]` (+ noted G6 legal boundary), producer `rules-engineer`, reviewers as above, and the
input-readiness matrix as an acceptance artifact. One frozen SHA carrying G3/G4/G5; installed-wheel
deployability included; evidence returned before merge. No 3D/UI; no CP-0032; no hold release; does not
wait on B-010.
