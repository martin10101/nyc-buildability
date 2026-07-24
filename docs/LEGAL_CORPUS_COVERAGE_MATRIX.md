# Legal-Corpus Coverage Matrix

**Status:** Canonical coverage matrix (task **M3-T001**, D-002 first-wave lane 1; owner directive
2026-07-23, amendment items 5 & 7). One authoritative status vocabulary (§2), and one **actionable** row
per declared legal-corpus domain (§3). This document makes completeness *auditable* instead of asserted:
no domain is silently covered, and no single aggregate "complete/compliant/buildable" label may be emitted
while any domain remains unresolved (§4).

**Task-ID note.** Rows below cite the **current five-packet M3 chain** — M3-T002 (immutable capture +
versioning), M3-T003 (Document Evidence Verification Engine), M3-T004 (cross-reference closure +
applicability), M3-T005 (Construction Code + amendment overlay) — per
[M3-CORPUS-REPLAN-PROPOSAL.md](../project-control/reports/M3-CORPUS-REPLAN-PROPOSAL.md) §17.2. This
supersedes the earlier §5B table that used pre-restructure IDs. Evidence dates are "as-of the accepted
research read" and are re-verified at each connector's G1.

---

## 1. What this matrix is (and is not)

- It records, for **every declared domain**, exactly one **status** from the vocabulary in §2 and six
  actionable columns (§3). (Acceptance AS-2, AS-3.)
- It does **not** assign legal conclusions, and it does **not** upgrade a domain to "covered" as a side
  effect of an unrelated task completing. Completing M3-T003 (evidence engine) does **not** imply any
  unrelated missing domain is covered. (Amendment item 7.)
- A domain's status is the honest current state; every non-`implemented` row carries a task, a blocker, or
  an **explicit continuing limitation** and a named next action + responsible reviewer. (AS-3.)

---

## 2. Authoritative status vocabulary (single source of truth)

There is **one** status vocabulary for the platform. Per-evaluation outcomes map to deterministic runtime
rule-evaluation results; two additional labels (`implemented`, `partial`) are used **only** for
domain-level roll-up in this matrix, never as a per-evaluation runtime result. (Acceptance AS-9.)

### 2.1 Per-evaluation statuses → runtime rule-evaluation outcomes

| Status | Meaning | Runtime mapping |
|---|---|---|
| `missing` | A required source/domain is not yet present in the corpus | No value produced; **blocks** the dependent claim |
| `not_evaluated` | In scope, but not yet assessed on this run (e.g. an AI-proposed edge not yet validated) | No value produced; **not** a negative finding |
| `unsupported` | Cannot be resolved with the current corpus / closure | Typed **unsupported** result; never a default value |
| `conflicting` | ≥2 sources disagree and precedence is unresolved (see [SOURCE_AUTHORITY_POLICY.md](SOURCE_AUTHORITY_POLICY.md) §3.3) | **`data_conflict`** (both sources + versions named; publication blocked) |
| `professional_review_required` | Needs qualified-human legal/design judgment | **PRR** result; never `verified` without G6 |
| `not_applicable` | Affirmatively resolved as not applying to this property/as-of date | Only assignable **after** applicability is resolved |

### 2.2 Domain roll-up labels (this matrix only)

| Roll-up label | Meaning |
|---|---|
| `implemented` | Domain's controlling source is present, verified, and usable end-to-end for its declared claims |
| `partial` | Some facts/sources present and accepted, but the domain is not fully usable for its declared legal claims |

### 2.3 Hard invariants (binding)

1. **`not_applicable` may be assigned only after applicability is affirmatively resolved.** Unknown or
   missing information must **never** become `not_applicable` or `false`. Absence is `missing`,
   `not_evaluated`, or `professional_review_required` — never silent negation. (AS-9; consistent with the
   absence discipline, NC-1.)
2. **Roll-up never overstates per-evaluation truth.** A `partial` domain still returns `missing` /
   `unsupported` / `not_evaluated` for the specific claims it cannot yet support.
3. **No false aggregate.** No deliverable emits a single "complete", "compliant", or "buildable" system
   label for the corpus or a property while any domain in this matrix is unresolved (any status other than
   `implemented`/`not_applicable`). Enforced by the machine check in §4.

---

## 3. Domain coverage matrix

Columns: **Status** · **Controlling official channel / unavailable-document class** · **Evidence as-of** ·
**Implementing task / human-action blocker** · **Downstream claims blocked** · **Next action (responsible
reviewer)**.

| Domain | Status | Controlling channel / unavailable-class | Evidence as-of | Implementing task / blocker | Downstream claims blocked | Next action (reviewer) |
|---|---|---|---|---|---|---|
| Zoning maps / district facts | `partial` | DCP GIS zoning features + ZTLDB (accepted connectors) | 2026-07-20 | M2 (accepted) | lot-level *legal* determination (dataset ≠ legal lot type) | carry ±20 ft limitation; lot-level legal type via closure (data-contract-verifier) |
| Zoning Resolution text | `missing` | ZR official portal (registry §8) | — | M3-T002 (capture) → M3-T003 (evidence) | every ZR rule value; any `Verified` label | immutable capture then evidence verification (data-contract-verifier; G6 for legal) |
| Amendments / effective dates | `missing` | ZR `/recently-adopted` + dated PDF snapshots; council/Legistar adoption records | — | M3-T002 (byte-level multi-signal version detection) → M3-T003 | effective-date correctness; supersession precedence | multi-signal change detection; effective-date evidence (data-contract-verifier) |
| Definitions & interpretation (§12-10, §11-25) | `missing` | ZR text via cross-reference closure | — | M3-T004 (closure graph; §11-25 suffix inheritance) | applicability / suffix scope of every dependent rule | closure graph + §11-25 edge (qa-engineer / G6 for legal) |
| Special districts / overlays | `partial` | DCP GIS (facts, accepted) + ZR text (missing) | 2026-07-20 | M2 accepted (facts) / M3-T002+T003 (override text) | override / modification resolution | ingest override text; resolve precedence (data-contract-verifier) |
| Environmental & restrictive declarations | `missing` | ACRIS / recorded instruments (unavailable-document class: recorded legal instruments) | — | **future task (unassigned)** — explicit continuing limitation | project-specific control (restrictive declarations) | scope a task (orchestrator) |
| Zoning-lot identity & recorded agreements (ZLDA) | `missing` | ZTLDB (facts) + recorded ZLDA (unavailable-document class) | — | **future task (unassigned)** — explicit continuing limitation | zoning-lot ≠ tax-lot claims; merged-lot development rights | scope a task (orchestrator) |
| CPC / BSA / DOB project-specific approvals | `missing` | BSA / CPC / DOB NOW (project-specific determinations) | — | **future task (unassigned)** — explicit continuing limitation | property-specific precedence (variances/special permits) | scope a task (orchestrator) |
| Construction Code | `missing` | DOB Construction-Code PDFs (scope-bounded) | — | M3-T005 + **B-011** (owner-approved release scope) | construction-feasibility claims | approve release scope (owner, B-011); then M3-T005 (data-contract-verifier; G6 legal) |
| DOB Rules / Bulletins / Local Laws / Code Notes | `missing` | DOB Rules (RCNY) / Buildings Bulletins / Local Law / Code Note overlay | — | M3-T005 (amendment/effective-date overlay) | code effective-text; interpretation currency | build overlay; rescission/supersession tracking (data-contract-verifier) |
| Landmarks / historic | `partial` | LPC (designation flag accepted) + requirements text (missing) | 2026-07-20 | M2 flag (accepted) / requirements **future task (unassigned)** | landmark-requirement claims | scope requirements task (orchestrator) |
| Waterfront / flood / environmental | `partial` | FEMA / official flood (flag accepted) + requirements text (missing) | 2026-07-20 (research) | M2 flag / requirements **future task (unassigned)** | waterfront / flood requirement claims | scope requirements task (orchestrator) |
| Occupancy / use / building type | `missing` | ZR (use groups) + Construction Code (occupancy) | — | M3-T004 (applicability) + downstream rule slice | use / occupancy claims; side-yard building-type branch | after M3-T003/T004 (orchestrator; G6 legal) |
| Parking / loading | `missing` | ZR parking regulations | — | **future rule slice (unassigned)** — explicit continuing limitation | parking / loading requirement claims | scope after closure (orchestrator) |
| Accessibility / fire-egress / structural | `missing` | Construction Code (scope-bounded) | — | M3-T005 + **B-011** | accessibility / egress / structural claims | approve release scope (owner, B-011); then M3-T005 (G6 legal) |

**Every non-`implemented` row above carries** either an implementing task ID, a human-action blocker
(B-011 / owner), or an **explicit continuing limitation** ("future task (unassigned)") *plus* a named
next action and responsible reviewer. No `missing` / `partial` / `conflicting` / `unsupported` /
`professional_review_required` row is left without one. (Acceptance AS-3.)

> **Absence discipline (NC-1).** No row asserts a domain or modifier is "confirmed absent". A domain that
> has not been searched to closure is `missing` / `not_evaluated` / `professional_review_required`, never
> "confirmed absent". Affirmative absence requires the complete declared search universe and
> cross-reference closure (M3-T004).

---

## 4. No-false-aggregate machine check (AS-4)

**Invariant:** while any domain in §3 is unresolved (status other than `implemented` or affirmatively
`not_applicable`), **no M3 deliverable may emit a single system-level "complete", "compliant", or
"buildable" label** for the corpus or for a property.

**How it is checked (executable, reproducible).** The self-check harness
[`packages/contracts/schemas/v1/fixtures/legal_source_manifest/check_m3_t001.py`](../packages/contracts/schemas/v1/fixtures/legal_source_manifest/check_m3_t001.py)
scans every M3-T001 deliverable for a system-guarantee assertion of an aggregate label (e.g. "the property
is buildable", "corpus is complete", "the result is compliant") and fails if any is present as a
guarantee. The current matrix has multiple `missing`/`partial` domains, so the invariant requires — and
the check confirms — the **absence** of any such aggregate guarantee. Exact command + output are recorded
in [M3-T001-producer-report.md](../project-control/reports/M3-T001-producer-report.md).

The distinction between an aggregate *guarantee* (forbidden) and *describing/forbidding* the concept
(allowed, e.g. this sentence) is that the check flags aggregate labels only when asserted **of** the
corpus/property as a system output, not when the word appears inside a prohibition or a column header.

---

## 5. Downstream mapping

- The per-evaluation statuses in §2.1 are the exact set the rule engine returns; the consumer boundary in
  [DOCUMENT_EVIDENCE_POLICY.md](DOCUMENT_EVIDENCE_POLICY.md) §7 forbids substituting a default/nearest/
  `not_applicable`/compliant/feasible/buildable value for any of them.
- Domain roll-up (`implemented`/`partial`) is a matrix bookkeeping label and is **never** returned as a
  runtime evaluation result.
- This matrix is re-finalized by the M3-T001 producer at each G1 and updated (additively, with cited
  evidence) as downstream tasks are accepted; acceptance of a downstream task updates **only** the domains
  that task actually covers.
