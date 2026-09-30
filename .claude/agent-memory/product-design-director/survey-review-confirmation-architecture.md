---
name: survey-review-confirmation-architecture
description: The two-layer survey state model, the H5 confirmation gate, and why the profile has no home for authoritative survey geometry facts
metadata:
  type: project
---

Survey review (Packet C / M2-T016) rests on a **two-layer** state model that is easy to
conflate and must be kept explicit in any UI or API design:

- **Document lifecycle** — `state.py` `DocumentState`: `uploaded / processing / auto_extracted
  / needs_review / rejected / professionally_confirmed`. These map 1:1 (exact wire strings) to
  the packet's named states — no renaming needed. `ALLOWED_TRANSITIONS` is the authoritative
  12-edge table; `rejected` is terminal; a corrected upload is a NEW document (new digest).
- **Per-fact confirmation** — `correction_history.py` `ProfessionalConfirmationState`:
  `unconfirmed / confirmed / rejected`. Every fact is born `unconfirmed` regardless of method/
  confidence/passing checks. A `professionally_confirmed` DOCUMENT still shows each fact's own
  confirmation state.

**Why:** conflating the two layers is the classic way a survey UI implies confirmation that did
not happen. `auto_extracted` means deterministic evidence-completeness promotion (H5 gate), NOT
human confirmation — such facts must read "Unconfirmed evidence" everywhere, never "Verified."

**How to apply:**
- The ONLY path to `professionally_confirmed` (edges 9/10) is an explicit `qualified_human`
  action (attributed `actor_id`) past the H5 `promotion_gated_transition` precondition (a
  `PromotionAllowed` verdict for EVERY material fact). No AI/confidence/automatic channel exists
  in `state.py`/`promotion.py` — it is structural (closed enums with no automated member, no
  confidence parameter). WHO qualifies (which license) is a Tier-D owner decision, NOT ours;
  recommended-default proposal = NY-licensed Land Surveyor for boundary/geometry facts.
- A submitted correction is edge 6 (`auto_extracted → needs_review`, +reason), NOT re-extraction.
  Re-extraction (edges 7/8) mints a new `extraction_run_id` and NEW evidence records; corrections
  append to `correction_history` and never touch `original_value` or the original bytes.
- **Profile integration (contract 1.4.0) has NO home for an authoritative survey geometry fact.**
  `lot_geometry` is explicitly MapPLUTO-derived; `status_dimensions.geometry_validity` only emits
  `missing`/`not_computed`. Survey state reaches the profile ONLY as honesty signals through
  existing surfaces (coverage_status downgrade to `professional_review_required`/`data_conflict`,
  `review_required`/`professional_review_required` booleans, provenance_refs). Promoting a
  confirmed survey boundary as authoritative would need a NEW additive contract version — that is
  a new contracted decision, a STOP, not something to design inside a consumer task.

Canonical spec: `docs/SURVEY_REVIEW_WORKFLOW.md`.
