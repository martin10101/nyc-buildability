# M4-T010 — DRAFT task packet (for owner review; NOT contracted, NOT started)

**Footprint slice 4 (final): R5 side yards — the most entangled slice.** Sequenced last; contracted
only after T009 returns its frozen SHA, gate evidence, CI, and product PR. Draft (`needs_review`)
`legal_rule`; no publication/verification/acceptance without G6. Shared basis:
`M4-footprint-input-readiness-matrix.md` · `M4-footprint-r5-11-25-applicability-decision.md` ·
`M4-footprint-source-inventory.md`. AS-1…AS-6 / NC-1…NC-8 and scope/forbidden paths **identical to
M4-T007** unless noted.

## Packet fields
- **task_id:** `M4-T010` · **task_type:** `legal_rule` (gates G0-G6) · **milestone_id:** `M4`
- **title:** "R5 side-yard draft rules (building-type-keyed regimes; QRS + narrow-lot modifiers; §23-332/§23-333/§23-334; fail-closed)"
- **producer_agent:** `rules-engineer` · **reviewers:** data-contract-verifier (G1), code-reviewer (G3), qa-engineer (G4), security-reviewer (G5)
- **required_gates:** G0,G1,G2,G3,G4,G5,G6 · **dependencies:** M4-T001; extends the consumer-boundary regression established in M4-T007.

### objective
Extract, as draft (`needs_review`) rules, the CURRENT effective **side yard** requirements
(**§23-332** basic, **§23-333** QRS modification, **§23-334** existing-narrow-lot modification) for
R5-series lots. §23-332 is **building-type-keyed**: (a) detached → two side yards; (b) semi-detached &
zero-lot-line → one side yard + open-area condition; (c) other residences (attached/MF) → none required
(with a min-width-if-provided + adjacency condition). Model side-yard **count and width(s)** as typed
constraints per regime. Per the §11-25 applicability decision, base "R5" in (a)/(b) extends to
R5A/R5B/R5D via **§11-25** (cite §11-25 + §23-332); the §23-332 **paragraph-scope** question for R5B/R5D
(listed separately only in (c)) is carried as a `documented_limitation` + professional-review note, NOT
resolved. Never label output an envelope. Full provenance + applicability trace. `[CANDIDATE]` values
pending byte-verification + G6.

### business_reason
Side yard is the most input-entangled footprint dimension (three building-type regimes + QRS + narrow-
lot + adjacency), so it is isolated as the final, smallest-coherent slice rather than bundled — keeping
each frozen-SHA gate surface reviewable and avoiding a partial legal shortcut. It reuses the pattern
proven by T007–T009.

### controlling sources (this task) — closed classification in the source inventory
§23-332, §23-333, §23-334 (captured-controlling) · §23-11 lot-area/width thresholds
(captured-controlling — supplies the §23-334 narrow-lot trigger) · §23-331 side-yard obstructions,
§23-313 measurement (captured-context-only) · §23-01 gate · §11-25, §11-122 · §12-10 {lot width,
zoning lot, qualifying residential site}. Excluded→PRR: §23-72/§23-723, §24-04/05. No `?` entries.

### distinctive fail-closed inputs (shared matrix rows)
**Building type detached / semi-detached / ZLL / other (row 8 — the DECISIVE input; unavailable, and a
proposed-building attribute)** · proposed dwelling type single/two-family vs MF (row 9) · QRS (row 10 —
§23-333) · ZR lot width vs §23-11 minimum + pre-1961 narrow-lot existence (rows 5 + 16 — §23-334) ·
adjacency (adjoining residence type/side yard → 8-ft open-area rule; off-lot).

### distinctive acceptance controls (in addition to the shared AS/NC)
- **NC-8a three-regime building-type guard:** when building type is unavailable/unresolved (row 8) NO
  side-yard regime is selected and NO width/count is emitted → `professional_review_required`; the rule
  never defaults to detached (or any) regime, and a "no side yard required" (c) outcome is never
  emitted without an established building type.
- **NC-8b §23-334 narrow-lot fail-closed:** the narrow-lot reduction (4 in/ft, floor 3 ft) requires
  ZR lot width < §23-11 minimum AND the pre-12/15/1961 existence condition (rows 5 + 16, both
  unavailable/conditional) → `documented_limitation`, no reduced value; §23-333 QRS "no side yard"
  fails closed on QRS (row 10).
- **NC-8c §23-332 paragraph-scope (§11-25):** the open question of whether §23-332(c)'s separate
  R5B/R5D listing carves them out of the bare-"R5" (a)/(b) paragraphs is carried as a
  `documented_limitation` + `professional_review_required` (cite §11-25 + §23-332), never resolved
  mechanically (see the §11-25 applicability decision).
- **Consumer-boundary regression:** EXTENDS the T007 regression with this task's side-yard
  `professional_review_required` categories; same assertions; test-only; no M5 consumption.

### ready-to-instantiate (on approval, after T009 completes)
`python tools/project_control.py new-task --task-id M4-T010 --task-type legal_rule --milestone M4
--gates G0,G1,G2,G3,G4,G5,G6 --reviewers data-contract-verifier,code-reviewer,qa-engineer,security-reviewer
--title "…" --objective "…" --depends M4-T001`.
