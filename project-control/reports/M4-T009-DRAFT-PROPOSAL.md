# M4-T009 — DRAFT task packet (for owner review; NOT contracted, NOT started)

**Footprint slice 3: R5 front yards.** Sequenced after T008; contracted only after T008 returns its
frozen SHA, gate evidence, CI, and product PR. Draft (`needs_review`) `legal_rule`; no
publication/verification/acceptance without G6. Shared basis:
`M4-footprint-input-readiness-matrix.md` · `M4-footprint-r5-11-25-applicability-decision.md` ·
`M4-footprint-source-inventory.md`. AS-1…AS-6 / NC-1…NC-8 and scope/forbidden paths **identical to
M4-T007** unless noted.

## Packet fields
- **task_id:** `M4-T009` · **task_type:** `legal_rule` (gates G0-G6) · **milestone_id:** `M4`
- **title:** "R5 front-yard draft rule (per-variant depths; corner/QRS/adjacency modifiers as explicit fail-closed conditions; §23-321)"
- **producer_agent:** `rules-engineer` · **reviewers:** data-contract-verifier (G1), code-reviewer (G3), qa-engineer (G4), security-reviewer (G5)
- **required_gates:** G0,G1,G2,G3,G4,G5,G6 · **dependencies:** M4-T001; extends the consumer-boundary regression established in M4-T007.

### objective
Extract, as a draft (`needs_review`) rule, the CURRENT effective **front yard** requirement
(**§23-321**) for R5-series lots. Model **front_yard_depth** (feet) as a typed constraint. Per the
§11-25 applicability decision, §23-321 **separately lists the suffixes**, so each variant emits its own
listed value and cites **§23-321 directly** (NOT via §11-25): R5 = 10, R5A = 10, **R5B = 5, R5D = 5**
ft `[CANDIDATE]`. Represent each variant explicitly. The corner one-front-yard reduction, the QRS
≥150-ft-width reduction, the adjacent-front-yard / prevailing-street-wall line-up, and the street-wall
articulation allowance are modeled as EXPLICIT conditions that fail closed (never a silent base value).
Measurement basis per §23-313. Full provenance + applicability trace. Never label output an envelope.

### business_reason
Front yard is a compact per-variant slice with concrete listed values but several off-lot / lot-type
fail-closed modifiers — a good mid-sequence consolidation of the pattern before the most entangled
side-yard slice.

### controlling sources (this task) — closed classification in the source inventory
§23-321 (captured-controlling) · §23-313 measurement, §23-312 front-yard-parking context
(captured-context-only) · §23-01 gate · §11-25 (cited only where applicable — front-yard values are
separately listed, so §11-25 is NOT the citation basis here; recorded for completeness) · §12-10
{corner lot, lot width, zoning lot, qualifying residential site}. Excluded→PRR: §23-72/§23-723,
§24-04/05. No `?` entries.

### distinctive fail-closed inputs (shared matrix rows)
Corner status (row 4 — lot type unusable from PLUTO, false-friend guard) · QRS ≥150-ft lot width
(rows 5 + 10 — LotFront ≠ ZR lot width; QRS geography unavailable) · **adjacent-front-yard /
prevailing-street-wall line-up (row 15 — off-lot facts, no canonical source)** · overlay/special/
historic modifiers (rows 11–13).

### distinctive acceptance controls (in addition to the shared AS/NC)
- **NC-8a corner reduction fail-closed:** the one-front-yard 5-ft reduction for a corner lot is emitted
  only on a professional lot-type determination; unresolved lot type → base depth with
  `professional_review_required` on the corner-modified value, never a silently reduced front yard.
- **NC-8b adjacent line-up → PRR:** the R4B/R5B "no deeper than deepest / no shallower than shallowest
  adjacent" and the general "shallowest adjacent (floor 5 ft)" line-up depend on neighboring buildings'
  street-wall positions (off-lot) → `professional_review_required`; no line-up depth is computed from
  on-lot canonical inputs.
- **NC-8c QRS reduction fail-closed:** the ≥150-ft-width QRS −5-ft reduction fails closed on QRS
  geography (row 10) and ZR lot width (row 5); `documented_limitation`, no reduced value emitted.
- **Consumer-boundary regression:** EXTENDS the T007 regression with this task's front-yard
  `professional_review_required` categories; same assertions; test-only; no M5 consumption.

### ready-to-instantiate (on approval, after T008 completes)
`python tools/project_control.py new-task --task-id M4-T009 --task-type legal_rule --milestone M4
--gates G0,G1,G2,G3,G4,G5,G6 --reviewers data-contract-verifier,code-reviewer,qa-engineer,security-reviewer
--title "…" --objective "…" --depends M4-T001`.
