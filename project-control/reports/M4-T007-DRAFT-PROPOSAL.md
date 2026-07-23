# M4-T007 — DRAFT task packet (for owner review; NOT contracted, NOT started)

**Lead footprint slice: R5 maximum lot coverage.** First of four sequenced `legal_rule` footprint
tasks (T007 → T008 → T009 → T010), one frozen-SHA task at a time. Draft (`needs_review`) rule
engineering only; no publication/verification/acceptance without G6. This packet is a proposal — on
approval the orchestrator instantiates `project-control/tasks/M4-T007.json` via `/start-controlled-task`.

Shared basis (do not duplicate — these are authoritative):
`M4-footprint-input-readiness-matrix.md` · `M4-footprint-r5-11-25-applicability-decision.md` ·
`M4-footprint-source-inventory.md`.

## Packet fields (map directly to tasks/M4-T007.json on contracting)

- **task_id:** `M4-T007`
- **title:** "R5 maximum lot-coverage draft rule (per-district; interior/through vs corner as separate typed constraints; fail-closed; §23-361/§23-363)"
- **task_type:** `legal_rule`  *(config.json → required_gates_by_task_type = [G0,G1,G2,G3,G4,G5,G6])*
- **milestone_id:** `M4`
- **producer_agent:** `rules-engineer` · **reviewer_agents:** `data-contract-verifier` (G1), `code-reviewer` (G3), `qa-engineer` (G4), `security-reviewer` (G5)
- **required_gates:** `G0, G1, G2, G3, G4, G5, G6` (G6 deliberately pending; blocks publication/verification/acceptance, not this draft build)
- **dependencies:** `M4-T001` (rules engine/DSL). Regression references the merged `M5-T001` scenario builder (on main; not a contracting dependency).

### objective
Extract, as a draft (`needs_review`) rule in the existing rules engine/DSL, the CURRENT effective
R5-series **maximum lot coverage** regulation per **§23-361** (+ **§23-363** special rules for certain
interior/through lots), scoped per R5 district variant SEPARATELY (R5/R5A/R5B/R5D; no family-wide
default — **§11-25** governs base→suffix inheritance, see the applicability decision). Model
**interior/through** coverage and **corner** coverage as SEPARATE typed constraints (percent of
zoning-lot area), preserving the source's lot-type distinction; never label any output a buildable
footprint / envelope / feasible floor area. Every constraint records exact ZR section/clause +
`last_amended`/effective date + source snapshot id+hash + precise applicability conditions (variant via
§11-25, lot type, dwelling type, large-site, shallow/corner/short-block modifiers). Consume the SHARED
input-readiness matrix; missing/uncertain/contradictory/unavailable inputs → typed
`missing`/`unsupported`/`rule_conflict`/`professional_review_required`, NEVER a guessed value. Competing
independently-applicable rules for the same constraint → `rule_conflict`, no selected value.
Effective-date discipline. No rule published or Verified; additive/fail-closed only — FAR rule,
evaluator core, and all canonical contracts untouched. **Establishes the negative M5 consumer-boundary
regression** (see below). Candidate values `[CANDIDATE]` pending byte-verification + G6.

### business_reason
Lot coverage is the smallest self-contained footprint slice and the lowest-risk place to validate the
full footprint pattern (new §23-3xx snapshots, the lot-type false-friend fail-closed, the zoning-lot
proxy policy, the `legal_rule` G0-G6 wave, and the consumer-boundary regression) before the larger
yard slices. Owner directive 2026-07-21 authorizes advancing draft rule engineering; G6 gates
publication/verification/acceptance, not this build.

### scope — allowed_paths
- `services/api/app/rules/rulesets/*.rule.json` — NEW lot-coverage ruleset file(s); **do NOT edit** existing `r5_*.rule.json`.
- `services/api/app/rules/schemas/v1/*.schema.json` — ONLY if an additive DSL field is required (extend additively, never redefine).
- `services/api/app/_zr_snapshots/v1/*.snapshot.json` + `services/api/scripts/sync_zr_snapshots.py` source dir — NEW official ZR snapshots (byte-identical + hash-guarded, package-data per M4-T005), for the sections classified **captured-controlling/captured-context-only** in the source inventory.
- `services/api/tests/rules/**` — deterministic / fail-closed / effective-date / provenance / rule-conflict / NC / installed-wheel deployability tests.
- `services/api/tests/scenario/**` — the consumer-boundary regression ONLY (**test-only**; no scenario app-code, contract, or endpoint change).
- `project-control/reports/M4-T007-producer-report.md`, `-input-readiness-matrix.md` (task-specific application of the shared matrix), `-source-capture.md`.

### scope — forbidden_paths
Evaluator/engine core (`services/api/app/rules/evaluator.py`); existing `r5_*.rule.json`;
`services/api/app/{profile,spatial,scenario,api}/**` **application code** (scenario is test-only);
any canonical contract (`property_profile`/`rule_evaluation`/`coverage_status`/`scenario`);
`apps/web/**` + any 3D/UI; publishing/Verifying; inventing any dimension/condition; applying a
remembered pre-amendment value; silent precedence between competing rules; **wiring rules into the
scenario builder** (M5 consumption is out); `project-control/**` except own reports; `.claude/**`
except own agent-memory.

### controlling sources (this task) — see source inventory for the closed classification
§23-361, §23-363 (captured-controlling) · §23-01 applicability gate, §11-25 (applicability), §12-10
{corner lot, interior lot, through lot, lot width, zoning lot, qualifying residential site},
§11-122 (context/defs). Excluded→PRR: §23-425 large-site (incl. the 50% MF coverage cap), §23-362
(R6–R12, not R5), §24-04/05 (community-facility bulk). No `?` entries; every cross-reference is
classified in `M4-footprint-source-inventory.md`.

### acceptance_scenarios (AS/NC — executable pack)
Shared AS-1…AS-6 / NC-1…NC-8 (below) plus this task's distinctive controls.
- **AS-1 per-variant confident:** for each supported variant a case → deterministic SEPARATE
  interior/through and corner max-coverage % constraints, exact unit (percent of zoning-lot area) +
  measurement basis + resolvable ZR citations (incl. §11-25 for any suffix-derived value) +
  applicability trace; `needs_review`, never `verified`.
- **AS-2 provenance fidelity:** every % traces to a captured snapshot (section + verbatim quote +
  `last_amended` + hash) with its applicability conditions; tampered/absent snapshot fails closed.
- **AS-3 effective-date boundary** · **AS-4 determinism (byte-identical)** · **AS-5 never-Verified /
  draft lifecycle** · **AS-6 installed-wheel deployability** (pip install --no-deps; full API suite
  green; FAR rule/engine core/canonical contracts byte-unchanged).
- **NC-1** variant isolation (a value for one variant never silently applied to another).
- **NC-2** lot-type unusable → `professional_review_required`, no value; **false-friend guard** (PLUTO
  `LotType` 6 "Interior" must NEVER map to ZR interior; corner/through never inferred from PLUTO).
- **NC-3** overlay/special-district/historic modifier present → `professional_review_required` /
  `rule_conflict`, never a silent base value.
- **NC-4** proposed dwelling type (1–2-family vs multiple-dwelling) unavailable → `professional_review_required`.
- **NC-5** missing canonical input → typed `missing`, no value.
- **NC-6** contradictory inputs → `data_conflict` / `professional_review_required`.
- **NC-7** competing independently-applicable rules → `rule_conflict`, no selected value.
- **NC-8** modification unresolved surfaced EXPLICITLY, base value never final: large-site (§23-425)
  50% cap, shallow-lot/corner/short-block increases (§23-363), and the R2X/R3A/R3X
  "remainder-after-yards" limitation each carry a `documented_limitation`; the base 60%/80% is never
  presented as the final applicable coverage when a modification remains unresolved.
- **NC-9 (task-specific) zoning-lot area:** a tax-lot↔zoning-lot mismatch signal →
  `professional_review_required`; a two-source (`lotarea` vs `lot_geometry.area_sq_ft`) difference
  WITHIN the documented tolerance → NOT `data_conflict`; only OUT-of-tolerance → `data_conflict`.
- **CONSUMER-BOUNDARY REGRESSION (control #7; established here):** feed a `rule_evaluation`
  containing these draft coverage outputs (each flag category) into the existing `build_scenario(...)`
  and assert the `lot_coverage_open_space` (and `setbacks_yards`) coverage-matrix rows stay `missing` /
  `blocks_buildable_envelope:true`; `data_completeness` stays `missing_critical`; no `coverage_status
  == verified`; nothing labeled footprint/massing/envelope/feasible; and the three categories
  —`section_23_423_modifications_unresolved`, R5A sloping-plane geometry, and any yard/coverage
  `professional_review_required` condition— are each refused as final geometry. **Test-only; no M5
  consumption.**

### risks
LEGAL BOUNDARY (candidate regime + every value `needs_review`, G6 required; not weakened; independent
of B-010) · GENUINE-AMBIGUITY STOP (if the source is legally ambiguous, blocker not guess) · CURRENT
regime only (§23-3xx; legacy §23-14 is STALE) · per-variant via §11-25, no family default · fail-closed
inputs per the shared matrix · separate typed constraints, never envelope-labeled · additive +
installed-wheel deployability guarded.

### ready-to-instantiate (on approval; orchestrator only)
`python tools/project_control.py new-task --task-id M4-T007 --task-type legal_rule --milestone M4
--gates G0,G1,G2,G3,G4,G5,G6 --reviewers data-contract-verifier,code-reviewer,qa-engineer,security-reviewer
--title "…" --objective "…" --depends M4-T001` (then claim to `rules-engineer` in an isolated worktree).
