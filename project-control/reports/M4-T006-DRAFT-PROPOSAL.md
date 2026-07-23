# M4-T006 — DRAFT task packet (for owner review; NOT contracted, NOT started)

**Status:** proposal only, returned for owner review. Not a contracted task — no `tasks/M4-T006.json`
exists and no work has begun. On owner approval it is instantiated via `/start-controlled-task`
(`new-task`). **CP-0032 is not used. No 3D/UI. No hold release. Does not wait on B-010.**

**Milestone:** M4 — Rule engineering and professional review.
**Title:** R5 residential **height & setback (vertical-envelope) draft rule family** (base height, max
building height, setback / street-wall above base) — draft / `needs_review`, extracted with provenance.

---

## 1. Why this task, and why it is smallest-highest-impact

The M5-T001 scenario foundation surfaces a draft **FAR floor-area cap** but marks every envelope
constraint `missing`. Its rule-coverage dependency matrix flags four `blocks_envelope=true` families
that must exist before FAR capacity can become a genuine (even narrow) R5 envelope:
`height_limit`, `setbacks_yards`, `lot_coverage_open_space`, `street_wall_base_height`.

The **highest-impact, smallest coherent** addition is the **vertical envelope**: the R5 maximum base
height, maximum building height, and the setback / sky-exposure regime above the base (which is the
same regulation that governs `street_wall_base_height`). Together with the existing FAR cap, these
turn "how much floor area" into "within what height and street-wall form" — the first time the product
can express a bounded R5 massing rather than an unbounded number. Lot coverage / open space and
rear/side **yards** (footprint constraints) are the deliberate *next* slice (§8), kept out to keep
this task minimal.

This is a **rule-engineering** task (extends the M4-T001 engine + DSL, exactly like the R5 FAR rule);
it is NOT scenario/UI work. A later M5 task will consume these rule outputs to compute a narrow
envelope.

---

## 2. Objective (packet `objective`)

Extract, as a **draft (`needs_review`) rule family** in the existing rules engine/DSL, the current
effective R5/R5A/R5B/R5D **height and setback** regulations, producing deterministic outputs
(e.g. `max_base_height_ft`, `max_building_height_ft`, and the setback / sky-exposure parameters that
bound the building above the base / street wall), each with:
- **Full provenance:** official NYC Zoning Resolution source snapshot(s) (section id, verbatim quote,
  `last_amended`), mirroring the `zr-23-21` snapshot pattern used by `r5-residential-far`.
- **Effective-date discipline:** `effective_from`/`effective_to`; evaluating `as_of` a date before the
  controlling amendment yields a visible not-effective outcome (not today's values applied to the past).
- **Fail-closed evaluation:** invalid/insufficient inputs or an unsupported R5 sub-district/condition
  yield a typed `professional_review_required` / `unsupported` outcome with NO guessed value — never a
  negative/NaN/inf or invented dimension.
- **Draft lifecycle:** `status: needs_review`, `verified`-ineligible; deterministic calculation +
  citation traces surfaced through the existing `rule_evaluation` trace (open `outputs` object — no
  canonical contract change expected).

Additive + fail-closed only: add a new ruleset (and any new ZR source snapshots) under the engine's
existing package-data locations; do NOT modify the FAR rule, the evaluator core, or any canonical
contract. **No rule is published or Verified.** The regime selection and every dimensional value are a
*candidate representation* awaiting **G6** qualified-human legal approval.

## 3. Business reason

FAR alone cannot describe a building. The vertical envelope (height + setback/street-wall) is the
single most consequential missing constraint set for R5 and the prerequisite for any honest "what can
I build" massing. Owner directive 2026-07-21 authorizes advancing rule engineering now with
`needs_review` rules; G6 (and, only for the client-validation item, B-010) gate publication/
verification and final acceptance — not this engineering build.

---

## 4. Critical legal-scope guardrails (READ FIRST)

- **AI extracts; it does not decide the law.** The producer captures the official ZR text and encodes
  a candidate rule with provenance; the *legal correctness* of the regime choice and values is decided
  by a qualified human at **G6**, not by this task.
- **Determine the CURRENT effective regime from official sources — do not assume.** R5 height/setback
  historically ran through the "height factor" vs "Quality Housing" tracks; the **City of Yes for
  Housing Opportunity** amendment (the `r5-residential-far` rule's `effective_from` is `2024-12-05`)
  changed residential bulk rules citywide. The producer MUST identify the exact controlling sections
  and values in the **current** ZR via `official-source-researcher` + `legal-corpus-engineer`, capture
  verbatim snapshots, and record `last_amended` — never carry forward a remembered pre-amendment value.
- **No invented dimensions.** If a value, condition, or sub-district treatment is not clearly in the
  captured source, it is `missing` / `professional_review_required`, never a default.
- **No verification, no publication.** Nothing in this task sets `verified` or publishes a rule.

---

## 5. Scope

**Producer:** `rules-engineer` (single writer). **Source inputs (prerequisite research, not parallel
writers):** `official-source-researcher` + `legal-corpus-engineer` supply verified official ZR
snapshots/sections; `rules-engineer` encodes the DSL. **Independent reviewers:** `code-reviewer`,
`qa-engineer`, `security-reviewer` (+ `data-contract-verifier` only if a contract change proves
necessary — not expected).
**Required gates:** **G0, G2, G3, G4, G5** at one frozen SHA (mirrors M4-T003). **G6** (qualified-human
legal) is REQUIRED before any publication/verification or final acceptance — **not** part of this
build, and **not weakened**.

**Allowed paths (proposed):**
- `services/api/app/rules/rulesets/*.rule.json` — new R5 height/setback ruleset (new file; do not edit
  `r5_residential_far.rule.json`)
- `services/api/app/rules/schemas/v1/*.schema.json` — only if the DSL needs an additive field for a
  height/setback construct (extend additively; never redefine)
- `services/api/app/_zr_snapshots/v1/*.snapshot.json` (+ the `sync_zr_snapshots` source dir) — new
  official ZR source snapshots for the height/setback sections, byte-identical + guarded, exactly as
  M4-T005 packaged them
- `services/api/tests/rules/**` — deterministic + fail-closed + effective-date + trace tests for the
  new family
- `project-control/reports/M4-T006-producer-report.md` (+ any raw source-capture report)

**Forbidden paths / actions:**
- `services/api/app/rules/evaluator.py` and the engine core (consume unchanged; the new rule is data +
  its own predicates), `r5_residential_far.rule.json`, `services/api/app/profile/**`,
  `services/api/app/spatial/**`, `services/api/app/scenario/**`, `services/api/app/api/v1/**`
- Any canonical contract (`property_profile`/`rule_evaluation`/`coverage_status`/`scenario`) — no edits
- `apps/web/**`, any 3D/UI
- Publishing/Verifying any rule; emitting `verified`; inventing any dimension/condition; applying a
  remembered pre-amendment value; `project-control/**` except own reports; `.claude/**` except own memory

## 6. Acceptance scenarios (executable pack — all required)

- **AS-1 confident R5 vertical envelope:** a supported R5 lot/condition with the captured regime →
  deterministic `max_base_height_ft` / `max_building_height_ft` / setback outputs, coverage
  `conditional` (never `verified`), full trace with resolvable ZR citations, `needs_review` +
  not-Verified disclaimer.
- **AS-2 unsupported sub-district/condition:** an R5 case the captured source does not cover →
  visible `unsupported` / `not_applicable`, no invented value.
- **AS-3 fail-closed on bad/missing input:** missing or invalid required input (or non-finite) →
  typed `professional_review_required`, NO computed dimension, no crash, no negative/NaN/inf.
- **AS-4 effective-date / temporal:** `as_of` before the controlling amendment → visible not-effective
  outcome; on/after → the captured values, proven by a before/after fixture.
- **AS-5 provenance fidelity:** every emitted dimension traces to a captured ZR snapshot (section +
  verbatim quote + `last_amended`); a tampered/absent snapshot fails closed.
- **AS-6 determinism:** identical input → byte-identical output (trace included).
- **AS-7 never-Verified & draft lifecycle:** every result carries `needs_review` + coverage ≠
  `verified`; `rule_release` shows verified-ineligible.
- **AS-8 regression + deployability:** full API suite green; the new ruleset + ZR snapshots load from
  the **installed wheel** (package-data guard, as M4-T005 established); no change to the FAR rule,
  engine core, or any canonical contract.

## 7. Dependencies & the acceptance boundary

- **Depends on:** M4-T001 (engine + DSL + ZR snapshot mechanism), and the official ZR source (current).
  Consumes them read-only / additively.
- **Feeds (future, not this task):** a later M5 task that combines the FAR cap + these height/setback
  outputs into a narrow R5 envelope scenario, and the M5 endpoint task.
- **Acceptance boundary:** may be built + independently reviewed now (needs_review); **final acceptance
  and any publication remain gated on genuine G6 qualified-human legal approval** — not weakened,
  and independent of B-010.

## 8. Explicit next slices (kept OUT of this task to stay smallest)
- Rear/side **yard** rules (`setbacks_yards` footprint side) and **lot coverage / open space** — the
  footprint constraints; a following M4 rule task.
- The M5 envelope-scenario task that consumes FAR + height/setback (+ later yards) to emit a narrow
  bounded R5 massing (still draft, still never a buildable-envelope claim until the matrix is covered).

## 9. Ready-to-instantiate packet (created only on owner approval)
On approval, `/start-controlled-task` mints `tasks/M4-T006.json` with the objective (§2), the legal
guardrails (§4), allowed/forbidden paths (§5), the AS-1..AS-8 pack (§6), `required_gates
[G0,G2,G3,G4,G5]` (+ noted G6 legal boundary), producer `rules-engineer`, reviewers as above. No
checkpoint (CP-0032 reserved). Implementation proceeds to one frozen SHA carrying G3/G4/G5; evidence
returned before any merge. No 3D/UI; no hold release; does not wait on B-010.
