# Survey Review Workflow (canonical)

**Status:** Canonical, implementation-ready workflow specification for the survey **review
experience, correction workflow, and profile integration** — owner directive 2026-07-20 section 3,
survey workstream **Packet C**, task **M2-T016**. This is the foundational design unit that the
frontend producer (`apps/web`) and the backend review-action slice (`services/api/app/documents`)
both build against. It is a **specification** (states, transitions, roles, audit, integration, UX
contract), not code.

**Design authority reconciliation.** Where this document names a state, transition, actor rule,
reason requirement, correction rule, or promotion precondition, the SHIPPED CODE is the authority
and this document transcribes it — it never renames a shipped state or invents an edge. On any
conflict, the shipped module wins and this document has a defect. The load-bearing shipped sources:

| Concern | Shipped authority |
|---|---|
| Document lifecycle states + allowed transitions | `services/api/app/documents/state.py` (`DocumentState`, `ALLOWED_TRANSITIONS`, `PROMOTION_GATED_TRANSITIONS`) |
| Document record + append-only state history | `services/api/app/documents/models.py` (`DocumentIngestionRecord.state_history`, `apply_transition`) |
| Per-fact correction history + professional confirmation | `services/api/app/documents/correction_history.py` (`CorrectingActorRole`, `CorrectingPrincipal`, `ProfessionalConfirmationState`) |
| Deterministic promotion precondition (H5 gate) | `services/api/app/documents/promotion.py` (`evaluate_promotion`, `PromotionAllowed`) |
| Per-fact evidence provenance (immutable original, checks, history) | `docs/SURVEY_EVIDENCE_CONTRACT.md` + `packages/contracts/schemas/v1/survey_evidence.schema.json` (1.0.0) |
| Pipeline stages S1–S9 + state-machine narrative | `docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md` |
| Profile integration surface (consumed, never changed) | `services/api/app/profile/contract.py` (property_profile 1.4.0) |
| Product/UX doctrine | `docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md`, `docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md` |

**Companions:** `docs/SURVEY_EVIDENCE_CONTRACT.md`, `docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md`,
`docs/SURVEY_FIXTURE_MATRIX.md` (M2-T015 evidence contract, ingestion architecture, fixtures).

---

## 1. Purpose and scope

The M2-T015 pipeline turns an uploaded document into per-fact `survey_evidence` records and moves the
document through a deterministic lifecycle. **This workflow is what turns those machine-extracted
facts into auditable, human-controlled evidence.** Without it, extracted output could masquerade as
boundary truth. The workflow governs four things the directive names:

1. **Review screen** — clean, progressively disclosed; shows the original document with extracted
   lines, boundaries, labels, and measurements overlaid; highlights uncertain/conflicting values;
   lets an **authorized** user accept, correct, or reject each material item.
2. **Corrections** — every correction is auditable (who/when/what/why), reruns dependent
   calculations, and **never** overwrites the immutable source file or erases the original
   extraction.
3. **States** — the explicit six-state lifecycle, with `professionally_confirmed` reachable **only**
   through one specifically-designated licensed/professional role — never an automatic or AI path.
4. **Downstream honesty** — buildability conclusions blocked or provisional because survey evidence
   is unresolved are shown as exactly that; unresolved items propagate visibly; no silent defaults.

### 1.1 Hard boundaries (do not cross)

These are contract-level and doctrine-level; the design encodes them and the implementation must not
weaken them.

- **No automatic path to `professionally_confirmed`.** No AI agent, no confidence score, no passing
  deterministic check, and no automatic pipeline transition may grant professional confirmation.
  Only an explicit, attributed action by the designated qualified-human role does (§5).
- **Immutability is contract-level.** The original uploaded bytes and each fact's `original_value`
  are immutable forever. Corrections append; they never mutate or delete an original (§6).
- **No profile-contract change.** The workflow **consumes** the property_profile 1.4.0 surface; it
  does not change it. If a survey-facts contract surface is genuinely needed, the design **STOPs and
  flags it** as a new contracted decision (§9.3) — it does not design the change.
- **No production storage/auth assumption.** B-001 blocks production private storage and auth
  provisioning. The design runs against the storage abstraction, local/CI auth fixtures, and
  synthetic documents. It never assumes a public bucket, a provisioned production bucket, or a
  provisioned production identity/licensure directory.
- **AI boundary.** AI retrieves, classifies, drafts, and explains. Deterministic code calculates and
  validates. Qualified humans approve. The review UI may *display* AI-suggested labels and
  plain-language explanations, clearly marked as AI-drafted; it may never let AI accept, correct,
  reject, confirm, or transition anything.

---

## 2. Two state layers (this is the crux of the model)

The workflow operates on **two distinct, related state layers**. Conflating them is the most common
way a survey review UI lies to a user, so they are kept explicit everywhere.

| Layer | What it describes | Vocabulary | Shipped home |
|---|---|---|---|
| **A. Document lifecycle** | The whole uploaded document's processing/review status | `uploaded / processing / auto_extracted / needs_review / rejected / professionally_confirmed` | `DocumentState` in `state.py` |
| **B. Per-fact confirmation** | One extracted fact's human-approval status | `unconfirmed / confirmed / rejected` | `ProfessionalConfirmationState` in `correction_history.py`; `professional_confirmation.state` in the evidence contract |

**Relationship (verbatim from the ingestion architecture §4):** document state is distinct from
per-fact `professional_confirmation`. A `professionally_confirmed` **document** asserts that review
completed; **each material fact still carries its own confirmation state.** A document cannot become
`professionally_confirmed` while a material fact still needs a decision — the H5 promotion gate (§4.3)
enforces this deterministically: every material fact must carry a `PromotionAllowed` verdict before
the confirmation edge is even offered.

The review screen shows layer A as the document's headline status and layer B as the per-item status
inside the fact list. Both are always visible; neither is inferred from the other in the UI.

### 2.1 State reconciliation (spec name → shipped `state.py` name)

The packet's named states map **1:1, exact wire string, no renaming**, to the shipped `DocumentState`
enum. There is **no divergence** to reconcile away.

| Packet / spec state | Shipped `DocumentState` member | Wire string | Meaning in the review UI |
|---|---|---|---|
| `uploaded` | `DocumentState.UPLOADED` | `"uploaded"` | Original stored immutably, digest recorded; not yet processed. Extraction may be disabled (parser-isolation hold, §11) — the document rests here honestly. |
| `processing` | `DocumentState.PROCESSING` | `"processing"` | Extraction/verification job running (or re-extraction). Read-only in the UI. |
| `auto_extracted` | `DocumentState.AUTO_EXTRACTED` | `"auto_extracted"` | Clean digitally-authored path: every executed check passed, no advisory-only/AI material lineage. **Facts are still `unconfirmed` evidence** — see §5.4. |
| `needs_review` | `DocumentState.NEEDS_REVIEW` | `"needs_review"` | The fail-closed routing: any fail/unresolved on a material fact, any advisory-only/AI-classified material value, or any tax-lot divergence. **The primary entry state for this workflow.** |
| `rejected` | `DocumentState.REJECTED` | `"rejected"` | Terminal. Screening/format/integrity rejection (pipeline) or professional rejection of the document (human). A corrected upload is a NEW document with its own digest. |
| `professionally_confirmed` | `DocumentState.PROFESSIONALLY_CONFIRMED` | `"professionally_confirmed"` | Review completed by the designated qualified professional after per-fact review. Reachable only through §5's mechanism; never automatic. |

`INITIAL_STATE = uploaded`; `TERMINAL_STATES = {rejected}`. Per-fact confirmation vocabulary is
`unconfirmed` (born state of every fact regardless of method/confidence/passing checks), `confirmed`,
`rejected`.

---

## 3. User journeys

Three journeys, each with one dominant decision (Premium Design System §1, §3, §16). All live under
the **Review** navigation area (Premium Design System §2); normal analyst users do not see ingestion
internals (Product Flow §"UI rules").

### 3.1 Reviewer journey (primary — SC-S1)

The designated qualified professional (or an authorized preparer, per §5's per-action authorization)
opens a `needs_review` document.

```
Review inbox ──▶ Survey review screen ──▶ per-fact decisions ──▶ document decision
 (queue of        (overlay + fact list,     (accept / correct /    (confirm document |
  documents by     one item in focus)        reject each item)      reject document |
  status)                                                            leave in review)
```

1. **Open.** The reviewer selects a document from the Review inbox (filtered by document state).
2. **Orient.** The screen shows the original document page with extracted geometry/labels/measurements
   overlaid, and a fact list ordered by *decision urgency* (unresolved/conflicting first).
3. **Decide per item.** For each material fact: **Accept** (affirm the extracted value),
   **Correct** (change the normalized value/units, with a required reason), or **Reject** (mark the
   detection unusable, with a required reason). The dominant next action is always "resolve the
   highest-priority open item."
4. **Recalculate.** Each correction/rejection triggers dependent buildability recalculation (§7); the
   downstream-impact indicator updates.
5. **Confirm or reject the document.** Once every material fact is resolved and each carries a
   `PromotionAllowed` verdict (§4.3), the reviewer may **confirm the document** (→
   `professionally_confirmed`) or **reject the document** (→ `rejected`). Either action is attributed,
   timestamped, and audited.

### 3.2 Preparer/analyst journey (correction without confirmation authority)

A non-professional authorized user (`user` role) may submit corrections (append-only, attributed as
`corrected_by_role: user`) and view state, but **cannot** grant professional confirmation and
**cannot** reject the document at the professional-authority level (§5.2). Their corrections still
route the document to `needs_review` and rerun downstream calcs; the professional decision remains
outstanding and visibly so.

### 3.3 Consumer/client journey (read-only honesty)

A client viewing buildability results never sees the raw review screen. They see the **downstream
honesty surface** (§7): which conclusions are blocked/provisional because survey evidence is
unresolved, in plain language, with a link into the Evidence view. They can never accept, correct,
reject, or confirm.

---

## 4. State machine and transition table

The document lifecycle transitions are **exactly** the `ALLOWED_TRANSITIONS` table in `state.py`.
Every edge not in this table is refused with the typed `IllegalTransition` (fail-closed). The
backend state machine is the **only** transition authority; the UI proposes an action, the backend
decides. Illegal transitions never round-trip through the UI.

### 4.1 Transition table (all 12 edges — transcribed from `state.py`)

Actor kinds are the closed `ActorKind` enum: **P** = `deterministic_pipeline`, **H** =
`qualified_human`. There is deliberately **no AI actor kind** and no confidence/score channel into
`transition()`.

| # | From → To | Trigger | Actor | Reason req. | Auto / Human | H5-gated |
|---|---|---|---|---|---|---|
| 1 | `uploaded` → `processing` | Worker claims the extraction job | P | no | Automatic | no |
| 2 | `uploaded` → `rejected` | S2 security/structural failure, S3 unapproved format, or §6 integrity failure | P | **yes** | Automatic | no |
| 3 | `processing` → `rejected` | Same failure classes as #2 | P | **yes** | Automatic | no |
| 4 | `processing` → `auto_extracted` | Extraction done; every executed check on every material fact is `pass`; no material advisory-only lineage | P | no | Automatic | **yes** |
| 5 | `processing` → `needs_review` | Extraction done with any `fail`/`unresolved` on a material fact, any material advisory-only or AI-classified value, or any tax-lot divergence (fail-closed routing) | P | no | Automatic | no |
| 6 | `auto_extracted` → `needs_review` | Later divergence (e.g. cross-check vs newly accepted tax-lot geometry), a submitted correction, or a reviewer pulling it in | P or H | **yes** | Either | no |
| 7 | `auto_extracted` → `processing` | Re-extraction: a new run with a new `extraction_run_id`; existing evidence never mutated | P | no | Automatic | no |
| 8 | `needs_review` → `processing` | Re-extraction (new `extraction_run_id`) | P | no | Automatic | no |
| 9 | `auto_extracted` → `professionally_confirmed` | Qualified professional confirms the document after per-fact review | **H only** | no | **Human** | **yes** |
| 10 | `needs_review` → `professionally_confirmed` | Qualified professional confirms the document after per-fact review | **H only** | no | **Human** | **yes** |
| 11 | `needs_review` → `rejected` | Professional rejects the document (not a survey, wrong property per SB-S7, unusable) | **H only** | **yes** | **Human** | no |
| 12 | `professionally_confirmed` → `needs_review` | A post-confirmation contradiction is discovered — reopening is visible and audited, never silent | P or H | **yes** | Either | no |

**Notes that the UI and API must honor:**

- **Reason discipline.** Edges 2, 3, 6, 11, 12 require a non-empty reason (`TransitionReasonRequired`
  otherwise). The UI must collect a reason before offering these actions; the reason is stored on the
  `TransitionRecord`.
- **Human-only edges.** Edges 9, 10, 11 accept **only** `qualified_human` and require an attributed
  `actor_id` (`TransitionActor.__post_init__` mandates `actor_id` for `QUALIFIED_HUMAN`). Edge 12
  may be human (professional reopening) or pipeline (a later automatic contradiction, e.g. a
  divergence discovered by re-run cross-check).
- **A submitted correction is edge 6**, not a re-extraction. Correcting a fact on an
  `auto_extracted` document moves the document to `needs_review` with the correction as the audited
  reason. Re-extraction (edges 7/8) is a separate pipeline action that mints a **new**
  `extraction_run_id` and **new** evidence records — it never edits existing records.
- **Terminality.** `rejected` has no outgoing edges. The recovery path is a NEW upload (new digest,
  new document), never a resurrection of the rejected document.

### 4.2 State diagram (informative — the table above is authoritative)

```
             (S1 gate)
                │  original stored immutably, digest recorded
                ▼
            ┌────────┐   claim job (P)   ┌────────────┐
            │uploaded│ ────────────────▶ │ processing │◀──┐ re-extraction (P, new run id)
            └───┬────┘                   └──────┬─────┘   │  (edges 7, 8)
                │ screen/format/            all │ pass    │
                │ integrity fail (P,+reason)    │ (P, H5) │ any fail/unresolved/
                ▼                               ▼         │ advisory/AI/tax-lot (P)
            ┌────────┐                   ┌───────────────┐│        ┌──────────────┐
            │rejected│◀──────────────────│auto_extracted │┼───────▶│ needs_review │
            └────────┘  prof. rejects    └──────┬────────┘│  edge 6└──────┬───────┘
             (terminal) document (H,+reason)    │         │(P or H,+reason)│
                ▲   (edge 11, from needs_review) │ confirm │                │ confirm
                │                                │(H only, │                │(H only, H5)
                │                                │  H5)    │                ▼
                │                                ▼         │        ┌────────────────────────┐
                └────────────────────────────── (edges 9, 10) ─────▶│professionally_confirmed│
                                                                     └───────────┬────────────┘
                                          post-confirmation contradiction        │
                                          (P or H, +reason, edge 12)             │
                                                     ◀───────────────────────────┘
                                                             back to needs_review
```

### 4.3 The H5 promotion gate (deterministic precondition on three edges)

Edges 4, 9, 10 (`PROMOTION_GATED_TRANSITIONS`) carry a **precondition on top of the authority check**:
`promotion_gated_transition()` refuses the edge unless the caller proves the evidence by submitting a
frozen typed `PromotionAllowed` verdict for **every** material fact (`evaluate_promotion` output).
Consequences the UI/API must respect:

- The gate **adds a precondition, never a new authority**. Edge legality, actor authority, and reason
  requirements remain decided by the section-4 table. The gate weighs only an `isinstance` check
  against the deterministic gate's own allowed verdict — **no confidence, classification, or model
  output can trigger or veto a transition.** A high-confidence AI value with an unresolved check
  simply fails the gate and the edge is refused with the same typed `IllegalTransition`.
- Therefore the **Confirm document** action (edges 9/10) is only *offered* by the UI when every
  material fact has a `PromotionAllowed` verdict. Until then, the UI shows exactly which facts still
  block confirmation and why (their unresolved/failed checks), and the confirm action is disabled with
  a plain-language explanation — never silently hidden.
- `auto_extracted` (edge 4) is likewise gated: the pipeline reaches it only when every material fact
  promotes deterministically. This is why the clean-path `auto_extracted` document still carries
  **unconfirmed** facts — automatic promotion of *evidence completeness* is not human confirmation.

---

## 5. Role authorization model and the professional-confirmation mechanism

### 5.1 Closed authority model (shipped)

Two independent closed enums, neither with any automated member, govern who may act:

- **Document lifecycle** (`state.py` `ActorKind`): `deterministic_pipeline`, `qualified_human`.
  Human edges (9, 10, 11) require `qualified_human` **with an attributed `actor_id`**.
- **Per-fact correction/confirmation** (`correction_history.py`):
  - `CorrectingActorRole`: `user`, `qualified_professional` (exact match; no aliasing/case-folding).
  - `CorrectingPrincipal`: `human_user`, `human_qualified_professional` — **deliberately no AI/model/
    agent/service/system member.** A principal claiming a role its authority does not grant is
    impersonation and is refused (`validate_correcting_actor`).

The authenticated principal classification is resolved by the **submission channel**, never
self-declared by the payload. An AI, model, agent, service, or system principal is *unrepresentable*
as a correcting or confirming authority and can never author or impersonate a human action.

### 5.2 Per-material-item authorization matrix

| Action | `user` (authorized preparer/analyst) | `qualified_professional` (designated role, §5.3) | Deterministic pipeline | AI / model / agent |
|---|---|---|---|---|
| View document + facts + overlay | yes (authorized org users) | yes | n/a | n/a (may draft explanations only) |
| **Accept** a fact (affirm value) | yes | yes | never | never |
| **Correct** a fact (value/units + reason) | yes (`corrected_by_role: user`) | yes (`corrected_by_role: qualified_professional`, requires `corrected_by` identity) | never (re-extraction mints new records, not corrections) | never |
| **Reject** a fact detection | yes | yes | never | never |
| Set per-fact `professional_confirmation` → `confirmed`/`rejected` | **no** | **yes only** (requires non-empty `actor_id`) | never | never |
| Reject the **document** (edge 11) | **no** | **yes only** (`qualified_human`, +reason) | never | never |
| Confirm the **document** (edges 9/10) | **no** | **yes only** (`qualified_human`, H5-gated) | never | never |
| Trigger re-extraction (edges 7/8) | request only (orchestrated job runs it) | request only | executes | never |

Authorization is enforced server-side on every review action (fail-closed): the backend re-derives
the authenticated principal and refuses any action outside that principal's granted authority with a
typed error, independent of what the UI offered. The UI mirrors the same rules by disabling
unavailable actions with a plain-language reason — but the UI is never the enforcement point.

### 5.3 The professional-confirmation MECHANISM (SC-S3, SC-S4)

`professionally_confirmed` (document) and per-fact `confirmed` are reachable **only** through this
mechanism, which is already structural in the shipped code:

1. **Closed human authority.** The confirmation edges accept only `qualified_human` (document) /
   `human_qualified_professional` (per-fact). No enum member represents AI or any automated actor.
2. **Mandatory attribution.** The acting professional's platform identity is required
   (`TransitionActor.actor_id` for edges 9/10/11; `corrected_by`/`confirmed_by` for per-fact
   professional actions). An anonymous professional action fails closed to review.
3. **Deterministic precondition.** The H5 gate (§4.3) requires a `PromotionAllowed` verdict for every
   material fact before the confirmation edge is legal. Confidence — however high — promotes nothing.
4. **No automatic or AI path anywhere.** There is no code channel by which a passing check, a
   confidence score, an AI classification, or an automatic transition sets a fact to `confirmed` or a
   document to `professionally_confirmed`. Every extracted fact is born `unconfirmed` regardless of
   method, confidence, or passing checks.

The UI expresses this mechanism honestly: the **Confirm** control is present **only** for the
designated professional role, is enabled **only** when the H5 precondition is met, and always records
attribution and timestamp.

### 5.4 Everywhere `auto_extracted` facts display as unconfirmed evidence (SC-S4)

An `auto_extracted` fact has passed deterministic promotion but is **not confirmed**. Every surface
that shows such a fact — the review screen, the Evidence view, any buildability conclusion that cites
it — labels it **"Unconfirmed evidence"** (per-fact `professional_confirmation.state = unconfirmed`),
never "Verified." "Verified" is exclusively an M4 published-rule + G6 professional outcome
(consistent with the profile contract's `coverage_note` doctrine) and is never asserted here by
extraction status alone.

### 5.5 ROLE-IDENTITY: pending owner / qualified-human decision (Tier D / G6-adjacent)

**This spec defines the MECHANISM. It does NOT decide which real-world license or designation
qualifies as the `qualified_professional`.** That is a legal/professional-authority determination —
a Tier D hard stop and a G6-adjacent boundary — and must be made by the owner or a qualified human
before `professionally_confirmed` can be granted in production.

> **OPEN DECISION — OWNER / QUALIFIED-HUMAN SIGN-OFF REQUIRED (do not implement as decided):**
> Which specific licensed/designated professional role may grant survey professional confirmation?
>
> **Recommended default for owner review (a PROPOSAL, not a decision):** a **New York State licensed
> Land Surveyor (PLS)** for boundary/geometry/measurement facts (lot boundary dimensions, bearings,
> stated/calculated area, reconstructed polygon, closure, scale, north orientation, elevation), on
> the reasoning that under NY Education Law Article 145 boundary determination is the practice of land
> surveying. For any survey-derived fact that is **not** boundary/geometry (e.g. an address/BBL text
> match used only for association), the owner may designate a broader authorized-professional set. The
> platform must bind confirmation authority to a verifiable licensure/designation record (an
> auth-design concern under B-001), not merely a role label.
>
> **Until the owner records this decision:** the mechanism is fully implemented and testable against
> local/CI auth fixtures using the closed `qualified_professional` / `human_qualified_professional`
> role, but production grant of `professionally_confirmed` remains gated on the recorded owner
> decision plus the B-001 identity/licensure binding. No default is treated as authoritative.

---

## 6. Correction model (append-only, immutable, auditable)

Every correction is one append-only entry on the fact's `correction_history` (evidence contract §4.6),
validated by `correction_history.py`. The UI and API must produce entries that the shipped validators
resolve.

### 6.1 What a correction is and is not

- A correction changes **`normalized_value` and/or `units` only.** It **never** touches
  `original_value` (immutable forever) and **never** touches the immutable original document bytes.
  `validate_correction_history` fails closed as *tampered* if the record's `original_value` no longer
  matches the independently held original.
- A correction is **not** a re-extraction. Deterministic re-extraction mints NEW evidence records
  under a new `extraction_run_id`; it never writes a `correction_history` entry.
- A "no-op correction" (neither value nor units changed) is refused — affirming an unchanged value is
  *professional confirmation*, not a correction.

### 6.2 Correction entry shape (who / when / what / why)

Each appended entry carries, verbatim per the contract and `_validate_entry`:

| Field | Rule |
|---|---|
| `corrected_at` | RFC 3339, strictly chronological (oldest first); a back-dated/reordered/same-instant pair fails closed. |
| `corrected_by_role` | `user` or `qualified_professional` (exact match; no automated role exists). |
| `corrected_by` | Actor identity. **Required** when role is `qualified_professional` (a professional correction must be attributable); optional-but-non-empty otherwise (identity scheme is B-001-blocked at the wire, stricter at the app level). |
| `previous_normalized_value` / `previous_units` | The state *before* this correction; must chain-match exactly the preceding entry's corrected state (or the stated pre-correction baseline for the first entry). |
| `corrected_normalized_value` / `corrected_units` | The state *after*; the latest entry's corrected state must equal the record's current `normalized_value`/`units`. |
| `reason` | Non-empty human-readable reason. A correction with no stated reason is refused (not reviewable). |

### 6.3 Append-only integrity

`validate_history_extension` proves the accepted (stored) history is an exact, position-preserving
prefix of the submission: fewer entries is deletion, a differing prefix entry is
edit/reorder/replace/insert — **all refused as tampering.** The API applies a correction by
**appending** to the stored history and re-validating the whole record; it never rewrites an existing
entry. Concurrent-edit safety uses optimistic concurrency on the fact's accepted-history length +
content (a submission whose accepted prefix no longer matches is rejected and the reviewer is asked to
re-open the current state).

### 6.4 Immutability side-by-side (SC-S2)

The review UI presents, for any corrected fact, the **original extraction** (`original_value`, and the
original normalized value/units as the pre-correction baseline) **side by side** with the current
corrected value and the full correction chain. The immutable original document page is always
openable at the exact `page_number`. After any number of corrections, `original_value` and the
original document digest are unchanged and viewable — this is a first-class UI affordance, not a
buried audit log.

---

## 7. Rerun semantics and downstream honesty (SC-S5, SC-S6)

### 7.1 A correction/rejection reruns dependent calculations

Any accept-with-change (correction), rejection, or newly-surfaced unresolved item **triggers rerun of
the dependent buildability calculations** that consume that fact. The rerun is deterministic
(CLAUDE.md principle 1: deterministic code calculates); the review action records which downstream
computations were invalidated, and the recompute is enqueued. The UI reflects "recalculating…" then
the updated conclusion. No downstream value is silently left stale.

### 7.2 Unresolved survey items propagate visibly (no silent defaults)

A material survey fact that is unresolved (`validation_results` carrying `fail`/`unresolved`, or a
detection `rejected` by a professional, or a fact still `unconfirmed` that a conclusion depends on)
propagates to **every buildability conclusion that depends on it** as a **blocked** or **provisional**
result — never a silently-defaulted number. Concretely:

- A conclusion that *cannot* be computed without the unresolved fact is **blocked**: shown as
  "Blocked — needs survey resolution," naming the exact unresolved item(s), with no fabricated value.
- A conclusion that *can* be computed on a provisional basis is **provisional**: shown with the
  provisional value clearly labeled, the assumption stated, and a link to the blocking item. It is
  never presented as final.
- The conclusion carries the honest coverage status (§9.2) — `professional_review_required` or
  `data_conflict` — never `verified`.

### 7.3 Resolving an item clears the flag through rerun (SC-S5)

When the reviewer resolves the item (accept, or correct-and-the-check-now-passes, or the professional
confirms), the dependent calculations rerun and the blocked/provisional flag **clears through that
rerun** — not by a manual UI dismissal. The flag is a computed consequence of evidence state; it can
only be cleared by changing evidence state, never by clicking it away.

### 7.4 Conflicts are unresolvable-by-click (SC-S6)

A deterministic-check failure (e.g. `area_vs_stated` mismatch, `contradictory_dimensions`,
`scale_consistency` failure with two scale statements) is displayed as a **conflict** with a
plain-language explanation of what disagrees and by how much (using the check's `expected_value` /
`observed_value`). A conflict is **not dismissible**: the only resolutions are **correct** the
offending fact (with reason) or **reject** the detection (with reason). There is no "acknowledge/
ignore" affordance that would let a conflict disappear without an audited decision.

---

## 8. Audit event model

Every review, correction, and confirmation action is an append-only, attributed, timestamped record.
The workflow reuses the shipped audit shapes rather than inventing a parallel one.

### 8.1 Event shapes (consistent with shipped models)

| Event | Shape (shipped source) | Persistence |
|---|---|---|
| Document lifecycle transition | `TransitionRecord{ from_state, to_state, actor{kind, actor_id}, occurred_at, reason? }` (`state.py`) | Appended to `DocumentIngestionRecord.state_history` (`models.py`), which must replay `uploaded → … → current` (a record whose history does not reproduce its state is refused at construction). |
| Per-fact correction | One `correction_history` entry (contract §4.6; validated by `correction_history.py`) | Appended to the fact's `survey_evidence.correction_history`. Append-only; never rewrites an entry. |
| Per-fact confirmation/rejection | `professional_confirmation{ state, confirmed_by, confirmed_at, note? }` (contract §4.7; `validate_professional_confirmation`) | Set on the fact's `survey_evidence.professional_confirmation`. `unconfirmed` carries no evidence; `confirmed`/`rejected` require non-empty `confirmed_by` + well-formed `confirmed_at`. |
| Promotion verdict (evidence) | `PromotionAllowed` / `PromotionRefused` (`promotion.py`, metadata-only payloads) | Recorded as the deterministic grounds/refusal for the transition that consumed it; refusals are serialized into the audit record (`to_payload()`). |

### 8.2 Audit properties (invariants)

- **Attribution.** Every human action carries the acting principal's identity (`actor_id` /
  `corrected_by` / `confirmed_by`). Pipeline events carry the deterministic job/worker id where
  applicable.
- **Reasoned where required.** Every rejection, reopening, and correction carries a non-empty reason
  (enforced by the shipped validators).
- **Append-only and replayable.** No event is edited, deleted, reordered, or displaced. The document's
  state history must replay to its current state; a fact's correction chain must chain-match and end
  at the current value.
- **Metadata only.** Audit payloads carry metadata and stated reasons — never document bytes.
  (`PromotionRefused.to_payload`, `UnresolvedCorrectionHistory.to_payload`, and the `state.py`
  payloads are all metadata-only and safe to serialize.)

### 8.3 B-001 honesty

Production private-object storage and the auth/identity/licensure directory are unprovisioned (no
bucket, no credentials, no migration). The audit model binds to the **digest** as content identity
and to **optional** `document_ref`/`storage_ref`/`corrected_by`/`confirmed_by` identity fields — all
of which stay `None` while B-001 is open. The design proves against the storage abstraction, a
bounded temp-dir test implementation, local/CI auth fixtures, and synthetic documents. **No design
element assumes a public bucket, a provisioned production bucket, or a provisioned production
identity.** When B-001 clears, identities and storage refs bind additively without changing these
shapes.

---

## 9. Profile integration surface (consume 1.4.0 — never change it)

### 9.1 The consumption rule

The workflow **consumes** the property_profile 1.4.0 contract surface (`profile/contract.py`,
`SUPPORTED_CONTRACT_VERSIONS`). It does **not** add, rename, or restructure any profile key.
Everything below uses **existing** fields and **existing** enum values.

### 9.2 How survey state reaches the profile (existing surfaces only)

Survey review does not inject unconfirmed machine output into the profile as authoritative fact.
Instead it propagates **honesty signals** through surfaces the 1.4.0 contract already exposes:

- **Coverage status downgrade.** Any profile fact/result whose derivation depends on an unresolved or
  unconfirmed survey item carries `coverage_status` = `professional_review_required` (unresolved/
  unconfirmed) or `data_conflict` (a failing deterministic check / survey-vs-tax-lot divergence) —
  both are members of the existing `coverage_status.schema.json` enum. It is **never** `verified`
  while survey evidence is unresolved.
- **Review-required flags.** `lot_geometry.review_required` and
  `spatial_intersection.professional_review_required` (existing booleans) are set true when survey
  evidence routes the lot to professional review; `spatial_intersection.review_reasons` /
  `notes` (existing arrays) carry the plain-language reason strings the UI shows.
- **Status dimension.** `status_dimensions.analysis_readiness` reflects
  `blocked_data_conflict` / `blocked_missing_critical` when an unresolved survey item touches a
  critical basis, using the existing closed enum; `geometry_validity` stays `not_computed` for
  survey-derived geometry until the confirming pipeline exists (see §9.3).
- **Provenance.** Every survey-derived signal that appears in the profile references a provenance
  record via the existing `provenance_ref` / `provenance_refs` mechanism; the survey document digest
  and `evidence_id` are the joinable provenance identity. A survey signal with no provenance record is
  a defect (backend-api rule: provenance is mandatory).

Net effect: an unresolved survey item makes the dependent profile results **honestly worse-covered
and review-required**, with provenance — using only fields and enum values that already exist in
1.4.0. This is the profile-side expression of §7's downstream honesty.

### 9.3 STOP / flag: authoritative survey-fact surface is a NEW contracted decision

The profile's `lot_geometry` is explicitly **MapPLUTO-derived** geometry provenance, and
`status_dimensions.geometry_validity` currently emits only `missing` / `not_computed` (its
description states `valid`/`invalid`/`repaired` "land additively with that pipeline"). Therefore:

> **STOP / FLAG (do not design here):** Writing a **professionally-confirmed survey boundary/area** as
> an **authoritative** profile geometry input (i.e. a survey-sourced `lot_geometry`-equivalent fact
> or a `geometry_validity: valid` upgrade) has **no home in the 1.4.0 contract** and would require a
> new additive contract version (a survey-facts surface). Per the forbidden-paths rule, this is a
> **new contracted decision** and is **not** designed in this task. Until such a surface is accepted,
> confirmed survey facts remain **evidence attached to the document** and reach the profile only as
> the honesty signals of §9.2 — they do not replace or upgrade the MapPLUTO-derived geometry fact.

This keeps the current task strictly a **consumer** of 1.4.0 while recording the genuine future need
for owner/orchestrator sequencing.

---

## 10. UX contract for the review screen

The information architecture the frontend implements. Grounded in Premium Design System (§1 progressive
disclosure, §3 one dominant action, §8 status system, §12 states, §13 responsive, §14 accessibility,
§15 anti-clutter, §16 visual acceptance) and Product Flow ("one clear next action," "never legal
certainty by color alone," "conflicts remain visible," "no silent defaults").

### 10.1 Layout (consistent product shell)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Document title · target BBL · DOCUMENT STATE badge          [primary CTA] │  slim top bar
├───────────────────────────────┬──────────────────────────────────────────┤
│                               │  FACT LIST (ordered by decision urgency)  │
│      ORIGINAL DOCUMENT        │   ▸ open/conflicting items first          │
│      with overlay of          │   ▸ each row: label · value · per-fact    │
│      lines / boundaries /     │     status · check summary · action set   │
│      labels / measurements    │                                           │
│      (page navigator,         │  ┌─ FOCUSED ITEM (one at a time) ───────┐  │
│      zoom, layer toggles)     │  │ original vs current · check detail   │  │
│                               │  │ plain-language conflict explanation  │  │
│                               │  │ [Accept] [Correct…] [Reject…]        │  │
│                               │  └──────────────────────────────────────┘  │
├───────────────────────────────┴──────────────────────────────────────────┤
│ Downstream impact strip: N conclusions blocked/provisional on these items │
└──────────────────────────────────────────────────────────────────────────┘
```

The **original document with overlay is visually dominant** (like the 3D canvas in the design system).
The right column is the decision surface. Only **one focused item** is expanded at a time (progressive
disclosure; no wall of open panels — anti-clutter §15).

### 10.2 Overlay of extracted geometry (the directive's core affordance)

- Render the original document page and overlay the extracted **lines, boundaries, labels, and
  measurements**, each anchored to its evidence `location` (`bounding_box` in `raster_pixels` or
  `pdf_user_space_points`, or `vector_object` object reference) at the correct `page_number`. The
  overlay coordinate space is taken from `location.bounding_box.coordinate_space` — never guessed.
- Selecting an overlay element focuses its fact row, and vice versa (bi-directional highlight).
- **Uncertain / conflicting values are highlighted** distinctly from clean ones: an unresolved or
  failing check, an advisory-only lineage (`ocr_text` / `line_symbol_detection`), or an AI-classified
  value (`ai_assisted_classification`) is visually marked **and labeled in text** — never by color
  alone (§10.6). Deterministic, digitally-authored values are shown plainly.
- Page space is **never** presented as survey/world coordinates (architecture §8): the overlay is a
  document annotation, not a georeferenced map.

### 10.3 One dominant decision per view

The dominant action is always **"resolve the highest-priority open item"** while facts remain
unresolved, and **"confirm or reject the document"** once all material facts are resolved and the H5
precondition is met. The primary CTA in the top bar reflects whichever is current. There is never
more than one primary action per panel (anti-clutter §15).

### 10.4 Per-item accept / correct / reject

- **Accept** — affirm the extracted value. For an already-passing fact this is a lightweight
  confirmation of the value (distinct from *professional confirmation*, which is the §5 role action).
- **Correct** — opens a focused editor: shows `original_value` (immutable, read-only), the current
  normalized value/units, an input for the corrected value + units, and a **required reason** field.
  On submit, appends a `correction_history` entry (§6) and triggers rerun (§7). Unit changes are
  explicit (both sides shown) so a decimal/unit-ambiguity fix is always visible.
- **Reject** — marks the detection unusable with a **required reason**; sets the fact's
  `professional_confirmation` to `rejected` when performed by the professional role. Propagates as a
  blocking downstream item (§7) until re-extraction or a corrected new upload supplies a usable value.
- Actions the current principal is not authorized for are **disabled with a plain-language reason**
  (e.g. "Only a designated professional can confirm"), never silently absent (§5.2). Server-side
  enforcement is independent of the UI.

### 10.5 State visibility (both layers, always)

- The **document state** (§2.1) is a persistent top-bar badge with label + icon + explanation.
- Each fact row shows its **per-fact confirmation state** (`unconfirmed` / `confirmed` / `rejected`)
  and a **check summary** (pass / fail / unresolved counts). `auto_extracted` facts read
  **"Unconfirmed evidence"** everywhere (§5.4) — never "Verified."
- The **Confirm document** control shows its precondition status: when the H5 gate is unmet, it is
  disabled and names the exact facts still blocking confirmation and why (§4.3).

### 10.6 Status communication — never certainty by color alone

Every status uses the full quadruple **label + icon + color + explanation** (Premium Design System §8).
Color never carries legal/confirmation meaning by itself (accessibility §14; visual acceptance §16).
Red is reserved for a real failed constraint or destructive action (e.g. reject), not for routine
"needs review." Statuses used here map to the existing product vocabulary: *Unconfirmed evidence*,
*Review required*, *Data conflict*, *Provisional*, *Blocked*, *Confirmed*, *Rejected*.

### 10.7 Progressive disclosure

Layered exactly as the design system prescribes: fact summary → focused item detail → check detail
(`expected_value`/`observed_value`) → correction history → open the immutable original page. Large
legal/technical paragraphs never sit in the main list. Normal analyst/client users never see ingestion
internals (parser stages, isolation, temp discipline) — those are operational, not review, concerns.

### 10.8 Empty / loading / error states (Premium Design System §12)

- **Empty** — no documents in review: explain the next action ("Upload a survey to begin," or "All
  documents resolved"). Never a blank canvas.
- **Loading** — show the actual pipeline stage honestly (e.g. "Extracting…", "Running deterministic
  checks…", "Recalculating dependent conclusions…"). If extraction is disabled by the parser-isolation
  hold (§11), the document rests in `uploaded` and the UI says so plainly ("Extraction is temporarily
  unavailable; the document is stored safely and unprocessed") — it never fakes progress.
- **Error** — recoverable API failure mid-review (SC-S7): state **what failed**, **what remains
  available** (the document and prior decisions are safe — corrections are append-only, so no partial
  write corrupts state), **whether retry is safe** (yes — idempotent submission keyed on the accepted
  history), and **whether user input is required**. Never show a raw backend error. A correction that
  fails to persist leaves the prior state intact and re-presents the reviewer's unsaved input for
  retry.

### 10.9 Accessibility (SC-S7; Premium Design System §14)

- Full keyboard navigation: move between fact rows, open the focused editor, submit accept/correct/
  reject, page the document, toggle overlay layers, and operate zoom — all keyboard-reachable with
  visible focus.
- Screen-reader labels on every control and every overlay element (each overlay element exposes its
  fact label, value, units, and status as text). An **alternative text summary** of the overlay
  findings is provided (analogous to the 3D findings alt-summary), so a non-visual user gets the same
  conflict/uncertainty information the overlay conveys.
- Semantic, accessible data tables for the fact list and correction history; sufficient contrast;
  reduced-motion honored (motion only explains state change — recalculation, item resolution — never
  decorative, never delaying critical information).
- No color-only status (§10.6). Icon-only controls always carry a label/tooltip.

### 10.10 Responsive behavior (Premium Design System §13)

- **Desktop** — primary review environment: overlay + fact list + focused editor side by side.
- **Tablet** — full review supported; overlay and fact list stack or use a collapsible split; focused
  editor as a panel. Critical warnings (conflicts, blocked conclusions) are never hidden.
- **Phone** — review triage and read: document state, prioritized open-item list, per-item detail, and
  the downstream-impact summary. Complex multi-item correction is not the phone's primary job, but a
  single correction with reason and the immutable-original view remain possible; no critical warning
  is ever hidden to save space (§16).

---

## 11. Operational honesty: extraction availability (parser-isolation hold)

Per architecture §5, parsing (S2–S8) is **disabled** until the kernel-enforced parser-isolation
boundary is verified on the substrate; documents rest in `uploaded` with a typed
`isolation_unavailable` outcome. The review workflow honors this without pretending: when extraction
has not run, the document shows `uploaded`, the review screen shows the stored original with **no
fabricated overlay/facts**, and the UI states extraction is unavailable (§10.8). The review workflow
itself (states, correction, confirmation, audit, profile signals) is fully specified and testable now
against synthetic evidence fixtures and the storage abstraction; it activates end-to-end when
extraction is enabled. No part of this design provisions or assumes that boundary.

---

## 12. API surface for review actions (implementation-ready, disclosed backend slice)

The frontend needs a small, typed action surface over `services/api/app/documents/**` (the disclosed
backend slice; the orchestrator may split it to a backend engineer at G0 to preserve exclusive file
scopes). Each action is server-authorized (§5.2), validates against the shipped validators, and emits
the audit events of §8. Endpoints are described by contract, not implemented here.

| Action | Input (validated) | Effect | Refusal (fail-closed) |
|---|---|---|---|
| Read document + facts | document id/digest | Returns document state, state history, and each fact's evidence (original, normalized, checks, correction history, confirmation state, `location`) | Not-found / unauthorized read |
| Accept fact | fact `evidence_id`, principal | Records the reviewer's affirmation of the current value | Unauthorized principal → typed error |
| Correct fact | `evidence_id`, corrected value + units, reason, principal, accepted-history fingerprint | Appends a `correction_history` entry (§6); routes doc `auto_extracted → needs_review` (edge 6) with the correction as reason; enqueues rerun (§7) | Any `UnresolvedCorrectionHistory` refusal (tamper/chain/append-only/actor) → typed error, no write; **on a `professionally_confirmed` document → `PostConfirmationEditRefused` (`post_confirmation_edit_refused`) — an explicit audited `reopen_document` (edge 12) is required first** |
| Reject fact | `evidence_id`, reason, professional principal | Sets `professional_confirmation.state = rejected`; propagates blocking downstream item | Non-professional principal → typed error; **on a `professionally_confirmed` document → `post_confirmation_edit_refused` (reopen first)** |
| Reject document | document id, reason, `qualified_human` | Edge 11 `needs_review → rejected` (+reason) | Non-professional / illegal source state → `IllegalTransition` / `UnauthorizedTransitionActor`; empty reason → `TransitionReasonRequired` |
| Confirm document | document id, `qualified_human`, per-fact `PromotionAllowed` verdicts | Edges 9/10 `→ professionally_confirmed`, H5-gated; per-fact `professional_confirmation.state = confirmed` | **Any material fact with `professional_confirmation.state == rejected` → `ConfirmationRejected` (`confirmation_rejected`, `detail.rejected_fact_ids`), refused BEFORE the H5 gate**; any material fact lacking `PromotionAllowed` → `IllegalTransition` (gate refusal); non-professional → `UnauthorizedTransitionActor` |
| Reopen document | document id, reason, `qualified_human` | Edge 12 `professionally_confirmed → needs_review` (+reason); audited — the required first step before editing any fact of a confirmed document | Non-professional / illegal source state → `UnauthorizedTransitionActor` / `IllegalTransition`; empty reason → `TransitionReasonRequired` |

All refusals are the shipped typed errors with machine-readable `reject_code`s; the UI maps them to
plain-language messages (§10.8) and never shows raw payloads.

### 12.1 Reconciliation with the implemented slice (M2-T016)

The disclosed backend slice (`services/api/app/documents/review_{actions,authz,events}.py`) refines
this table on two points, and this spec adopts the refinement (which favors §7.2 / §10.4 over the
literal confirmation table):

1. **A professionally-rejected material fact permanently blocks document confirmation.** Because a
   deterministic-validator verdict can be `PromotionAllowed` even for a fact a professional has
   `rejected`, `confirm_document` performs an explicit pre-H5 check and refuses with
   `confirmation_rejected` (naming `detail.rejected_fact_ids`); the read model lists such facts in
   `blocking_fact_ids` with `confirm_precondition_met == false`. A rejected detection is **never**
   relabeled `confirmed`; it clears only through re-extraction or a corrected new upload.
2. **Post-confirmation edits are never silent.** `correct_fact` / `reject_fact` on a
   `professionally_confirmed` document are refused (`post_confirmation_edit_refused`); the reviewer
   must `reopen_document` (edge 12, audited) first — "reopening is visible and audited, never silent."

Wire contract (implemented): endpoints are digest-keyed (`sha256:<64hex>`) under
`/api/v1/documents/{digest}/…`; mutating handlers return a `ReviewActionResult` (the client re-reads
`GET …/review` for the settled view). Full endpoint/field/error mapping: `M2-T016-backend-return.md`.
Read-model fields the route must still assemble (tracked follow-up, B-001 route/store task): the
per-fact `history_fingerprint`, a per-action principal-capability surface, per-check
`expected`/`observed`, and a review-inbox endpoint.

---

## 13. Acceptance-scenario mapping (SC-S1 … SC-S8)

Each packet scenario maps to the spec sections it is satisfied by and the testable assertion the
human-journey / visual / code / security reviewers verify.

| Scenario | Spec sections | Testable assertion |
|---|---|---|
| **SC-S1** primary journey | §3.1, §4, §6, §7, §10 | Reviewer opens a `needs_review` document, sees overlay + highlighted uncertain values, accepts some facts, corrects one (with reason), rejects one; the audit trail (state history + correction history + confirmation) is complete; dependent calcs rerun; states transition per the §4 table. |
| **SC-S2** immutability | §1.1, §6.1, §6.4 | After corrections, the original file digest and each fact's `original_value` + original baseline remain intact and are viewable side by side with the corrections. |
| **SC-S3** authorization | §5.1, §5.2, §5.3, §12 | An unauthorized principal cannot accept/correct/reject or confirm; the confirm/document-reject actions are available only to the designated professional role (server-enforced, UI-mirrored). |
| **SC-S4** no-auto-verified | §4.3, §5.3, §5.4 | Nothing reaches `professionally_confirmed` (or per-fact `confirmed`) without the explicit professional action past the H5 gate; `auto_extracted` facts display as "Unconfirmed evidence" everywhere they appear. |
| **SC-S5** downstream honesty | §7.1–§7.3, §9.2 | A property with unresolved survey items shows exactly which buildability conclusions are blocked/provisional; resolving the item clears the flag **through rerun**, not by dismissal. |
| **SC-S6** conflict display | §7.4, §10.2, §10.6 | A deterministic-check failure (e.g. `area_vs_stated` mismatch) is visible, plain-language explained (with `expected`/`observed`), and unresolvable-by-click — it requires correction or rejection, never a dismissal. |
| **SC-S7** recovery + a11y | §10.8, §10.9, §10.10 | A recoverable API failure mid-review preserves prior state and offers safe retry; keyboard navigation and the a11y pack pass on the new screens; layout is responsive at supported viewports with no hidden critical warnings. |
| **SC-S8** regression | §1, §12 (contract-only consumption; no profile-contract change) | Full repository CI green on both events; existing web e2e suites green; no change to `services/api/app/profile/**` beyond consuming 1.4.0. |

---

## 14. Summary of decisions and flags

- **States reconcile 1:1** with `state.py` `DocumentState` — no renaming, no divergence (§2.1).
- **Two state layers** (document lifecycle vs per-fact confirmation) are kept explicit; a
  `professionally_confirmed` document still shows each fact's own confirmation state (§2).
- **Transition table** transcribed verbatim from `ALLOWED_TRANSITIONS`; three edges are H5-gated;
  human-only confirmation/rejection edges require attributed `qualified_human` (§4).
- **Professional-confirmation mechanism** is structural and shipped (closed human-only enums, mandatory
  attribution, H5 precondition, no AI/automatic path). The **role identity** (which license qualifies)
  is a **pending owner / qualified-human decision** with a labeled *recommended default (NY-licensed
  Land Surveyor for boundary/geometry facts) — a proposal, not a decision* (§5.5).
- **Corrections** are append-only, immutable-original-preserving, reasoned, attributed, and rerun
  dependent calcs (§6, §7).
- **Downstream honesty** propagates unresolved items as blocked/provisional with no silent defaults;
  conflicts are unresolvable-by-click (§7).
- **Profile integration consumes 1.4.0 only** via existing coverage-status downgrades, review-required
  flags, status dimensions, and provenance refs. Writing confirmed survey geometry as an
  **authoritative** profile input is **flagged as a new contracted decision (STOP)** — not designed
  here (§9).
- **B-001 honesty** throughout: no production storage/auth assumed; digest is the content identity;
  identity/storage refs stay optional (§8.3, §11).
