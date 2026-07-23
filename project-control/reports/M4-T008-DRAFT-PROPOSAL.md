# M4-T008 — DRAFT task packet (for owner review; NOT contracted, NOT started)

**Footprint slice 2: R5 rear yards + rear-yard equivalents.** Sequenced after T007; contracted only
after T007 returns its frozen SHA, full gate evidence, CI, and product PR. Draft (`needs_review`)
`legal_rule` only; no publication/verification/acceptance without G6. Shares the authoritative basis:
`M4-footprint-input-readiness-matrix.md` · `M4-footprint-r5-11-25-applicability-decision.md` ·
`M4-footprint-source-inventory.md`. AS-1…AS-6 / NC-1…NC-8 and scope/forbidden paths are **identical to
M4-T007** unless noted; only task-specific deltas are spelled out here.

## Packet fields

- **task_id:** `M4-T008` · **task_type:** `legal_rule` (gates G0-G6) · **milestone_id:** `M4`
- **title:** "R5 rear yard + rear-yard-equivalent draft rules (interior vs through lot; separate typed depth constraints; fail-closed; §23-342/§23-343/§23-344)"
- **producer_agent:** `rules-engineer` · **reviewers:** data-contract-verifier (G1), code-reviewer (G3), qa-engineer (G4), security-reviewer (G5)
- **required_gates:** G0,G1,G2,G3,G4,G5,G6 · **dependencies:** M4-T001 (engine); the consumer-boundary regression established in M4-T007 is EXTENDED here.

### objective
Extract, as draft (`needs_review`) rules, the CURRENT effective **rear yard** (**§23-342**) and
**rear-yard equivalent** (**§23-343**) regulations plus the additional modifications (**§23-344**),
for R5-series lots. These requirements are **uniform across R1–R12** (variant-independent per the
source; each R5 variant still represented explicitly, base applies via **§11-25** with no separate
suffix provision → cite §11-25 + the substantive section). Model **rear_yard_depth** (interior lots,
§23-342) and **rear_yard_equivalent_depth** (through lots, §23-343) as **SEPARATE typed constraints**
(feet), routed by lot configuration and **mutually exclusive by lot type** (interior → §23-342;
through → §23-343). Preserve the source's building-type and height distinctions. Never label output a
buildable footprint/envelope. Full provenance per constraint (section + `last_amended` + snapshot
hash + applicability trace). Fail-closed per the shared matrix. `[CANDIDATE]` values pending
byte-verification + G6.

### business_reason
Rear yard and its through-lot equivalent are the coherent lot-configuration cluster and MUST be
co-implemented (splitting the interior/through pair would leave the routing half-done — a partial legal
shortcut the owner forbids). Builds directly on the T007 pattern.

### controlling sources (this task) — closed classification in the source inventory
§23-342 (captured-controlling), §23-343 (captured-controlling), §23-344 (captured-controlling),
§23-341 obstructions (per inventory classification), §23-313 measurement basis (captured-context-only),
§12-10 interior/through/corner + zoning-lot definitions, §11-25, §23-434/§23-435 alternative RYE
locations and §23-425 large-site (per inventory classification). No `?` entries.

### distinctive fail-closed inputs (shared matrix rows)
Lot type interior↔through **routing** (row 4 — unusable from PLUTO; false-friend guard) · building
type detached/ZLL vs semi-detached/attached (row 8 — unavailable) · lot width <40 ft threshold
(row 5 — LotFront ≠ ZR lot width) · lot depth ≥190/<110/<95 ft triggers (row 6) · building height
75 ft threshold (proposed-building attribute, unavailable → PRR) · shallow-lot pre-1961 condition
(row 16) · §23-344 corner-proximity / short-block / side-lot-line-beyond-100-ft configuration.

### distinctive acceptance controls (in addition to the shared AS/NC)
- **NC-8a interior/through mis-route guard:** when lot type is unresolved (row 4) the rule emits
  NEITHER a §23-342 rear yard NOR a §23-343 equivalent as a value → `professional_review_required`; a
  §23-342 depth is never emitted for a through lot, nor a §23-343 depth for an interior lot.
- **NC-8b §23-343 shallow-reduction wording limitation:** the captured §23-343 text reads "reduced by
  one foot by which … less than 190 feet" (the parallel §23-342 uses "six inches **for each foot**").
  The producer MUST byte-verify this at G-time and, until confirmed, carry a `documented_limitation`
  that the shallow-lot reduction formula is source-ambiguous → `professional_review_required` for the
  reduced case; no computed reduced depth is emitted from an unverified formula.
- **NC-8c §23-344 modifications explicit:** corner / short-block / large-site / eligible-site
  exceptions each carry a `documented_limitation`; the base 20/30/40/60 ft is never presented as final
  when a §23-344 modification remains unresolved.
- **Consumer-boundary regression:** EXTENDS the T007 regression to add this task's rear-yard /
  rear-equivalent `professional_review_required` categories; same assertions (rows stay `missing`,
  never final geometry, never `verified`). Test-only; no M5 consumption.

### ready-to-instantiate (on approval, after T007 completes)
`python tools/project_control.py new-task --task-id M4-T008 --task-type legal_rule --milestone M4
--gates G0,G1,G2,G3,G4,G5,G6 --reviewers data-contract-verifier,code-reviewer,qa-engineer,security-reviewer
--title "…" --objective "…" --depends M4-T001`.
