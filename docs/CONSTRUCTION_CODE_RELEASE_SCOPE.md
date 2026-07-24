# Construction-Code Release Scope — DRAFT for owner approval (B-011)

> **THIS IS A DRAFT. IT CARRIES NO AUTHORITY.** It proposes *which* construction-code domains the platform
> should treat as in scope, so completeness can be judged against a frozen target instead of an open-ended
> "all of the code". **AI has no authority to set release scope.** Owner approval of this artifact clears
> **B-011** and is a prerequisite for **M3-T005** (the DOB Construction-Code corpus task) to leave backlog.
> Until the owner approves, nothing here is in force and M3-T005 stays blocked.

**Task:** M3-T001 (D-002 first-wave lane 1; owner directive 2026-07-23, amendment item 6 / rev-4 §17).
**Approval mechanism:** B-011 (owner). **Not a legal approval.** B-011 fixes the *product/release scope*
(which code domains are in scope); it does **not** certify legal adequacy or completeness. Qualified
professionals still approve legal interpretations and release adequacy through **G6**, which remains
mandatory before any rule sourced from this corpus is Published or Verified. **B-011 and G6 are
independent gates.**

---

## 1. Proposed code edition + as-of date — TO VERIFY AT G1 (not yet established from accepted research)

| Field | Proposed value (candidate) | Verification status |
|---|---|---|
| Code family | NYC Construction Codes (Title 28 NYC Administrative Code + the referenced Building/Plumbing/Mechanical/Fuel Gas/Energy Codes) | **to verify at G1** — confirm the exact adopted edition and its effective date from the official DOB/NYC source before any ingestion |
| Candidate edition | The current adopted NYC Construction Codes edition | **to verify at G1** — the specific edition label and effective date are **not** yet established from accepted repository research and must not be asserted until read from the official source |
| As-of date | The homepage/official "current as of" date at capture time | **to verify at G1** — captured with the corpus, stamped per M3-T002 versioning |

**Discipline:** the exact edition string and effective date are **not guessed** here (CLAUDE.md principle
3). M3-T005 records them from the official DOB source at its G1, and the immutable capture (M3-T002) stamps
the as-of/version signals. This draft fixes *scope*, not the version label.

---

## 2. Product claims this scope is meant to support (grounded in PRD §7.2)

The construction-code corpus exists to support the PRD **"basic code-feasibility layer"** (PRD §7.2) — just
enough non-zoning feasibility logic to avoid presenting an impossible envelope as a practical building. The
supported claims are **preliminary feasibility flags**, never plan-level compliance:

- Approximate building **core** allowance (stairs/elevators/shafts) as a feasibility flag.
- **Exit / stair count** flags (does the massing plausibly admit required egress count).
- **Elevator** assumption flag.
- **Corridor and shaft efficiency** assumptions.
- **Lot-line window** limitations (interacts with zoning yards).
- **Basic light-and-air** feasibility flags.
- Approximate **floor-to-floor** heights.
- **Accessibility** allowance flag.
- **Construction / occupancy type** questions where they materially affect feasibility.

Every such output is a **preliminary decision-support flag** subject to the platform disclaimer (PRD §1
intro boundary + §29 Required disclaimer): *not a permit approval, legal opinion, architectural or
engineering certification, DOB determination, or guarantee of approval.* No output is relabeled gross/net/sellable/feasible/compliant/buildable
(consumer-boundary discipline, [DOCUMENT_EVIDENCE_POLICY.md](DOCUMENT_EVIDENCE_POLICY.md) §7).

---

## 3. Proposed IN-SCOPE titles / chapters / domains (for owner decision)

Proposed in-scope, aligned to the PRD §7.2 feasibility flags. Exact chapter/section numbers are confirmed
against the approved edition at M3-T005 G1 (§1) — the list below fixes **domains**, not verified citations.

| In-scope domain | Why (which §7.2 flag it supports) | Confirm at G1 |
|---|---|---|
| Occupancy classification (use/occupancy groups) | Construction/occupancy-type feasibility questions | chapter/section per approved edition |
| Means of egress — required exit/stair **count** & occupant-load basis (preliminary) | Exit/stair count flags | egress chapter (count-level only) |
| Vertical circulation — elevator & shaft feasibility (preliminary) | Elevator + shaft efficiency assumptions | relevant chapters |
| Accessibility allowance (preliminary) | Accessibility allowance flag | accessibility chapter |
| Light & air / lot-line window limitations (preliminary) | Lot-line window + light-and-air flags | relevant provisions |
| Height / story & floor-to-floor feasibility inputs (preliminary) | Approximate floor-to-floor heights | height/area provisions |
| Definitions needed to interpret the above | correct application of the flags | definitions chapter |

---

## 4. Required amendment / currency channels (must be tracked before any in-scope value is trusted)

For every in-scope domain, the following official channels must be captured and overlaid so the corpus
reflects **currently effective** text, per [SOURCE_ACCESS_REGISTRY.md](SOURCE_ACCESS_REGISTRY.md) (new DOB
channel sections):

- **Local Laws** amending Title 28 / the Construction Codes (effective dates).
- **DOB Rules (RCNY)** interpreting or implementing the code.
- **Buildings Bulletins**.
- **DOB Code Notes / directives**.
- **Formal DOB interpretations**.
- **Rescission / supersession** records for any of the above (a rescinded Bulletin/interpretation no longer
  controls — [SOURCE_AUTHORITY_POLICY.md](SOURCE_AUTHORITY_POLICY.md) §3.1 factor 4).

An in-scope value whose amendment currency is not established is `missing` / `professional_review_required`
— never trusted as current. (M3-T005 owns the overlay; the channels are registered by M3-T001.)

---

## 5. Proposed EXCLUDED domains — and the consumer claim each exclusion blocks

Exclusions are **explicit**: each names the exact downstream claim it blocks, so an excluded domain can
never be silently treated as covered. (Aligned to PRD §7.3, which places detailed plan-code compliance
outside the first engine.)

| Excluded domain | Consumer claim this exclusion BLOCKS |
|---|---|
| Detailed egress **geometry** (travel distance, corridor widths, stair geometry) | "egress design complies" / any egress-geometry compliance claim |
| Room-by-room / plan-level compliance | "the plan complies with the building code" |
| Fire-rating & fire-protection **design** | "fire-rating/fire-protection is satisfied" |
| Structural **design** & loads | "the structure is adequate / complies" |
| Mechanical, plumbing, fuel-gas, electrical **design** | "MEP complies" |
| Energy code compliance calculation | "the design meets the energy code" |
| Construction-document approval / DOB filing acceptance | "DOB will approve" / "permit-ready" |
| Fire Code (FDNY) operational provisions | "FDNY/Fire-Code compliant" |
| Any occupancy/use outside the confirmed in-scope set | feasibility claims for that occupancy/use |

Each excluded domain resolves to a typed `unsupported` / `not_evaluated` result at runtime, never a
default, `not_applicable`, or `compliant` value ([DOCUMENT_EVIDENCE_POLICY.md](DOCUMENT_EVIDENCE_POLICY.md)
§7). No single "complete/compliant/buildable" label is emitted while any domain is unresolved
([LEGAL_CORPUS_COVERAGE_MATRIX.md](LEGAL_CORPUS_COVERAGE_MATRIX.md) §4).

---

## 6. What owner approval of this draft means (and does not)

**Approving (clearing B-011) means:** the owner fixes the in-scope domains (§3), the required currency
channels (§4), and the excluded domains (§5) as the frozen target for M3-T005; M3-T005 may then leave
backlog **subject to its other blockers** (B-001 durable storage) and its accepted dependencies (M3-T002,
M3-T003).

**Approving does NOT mean:** any legal adequacy certification; any waiver of **G6**; any authorization to
Publish/Verify a rule; or acceptance of a specific code edition/effective date (that is confirmed from the
official source at M3-T005 G1, §1).

**Open owner decisions to confirm on approval:** (a) confirm/adjust the in-scope domain set (§3); (b)
confirm the excluded set (§5) and the blocked claims are acceptable for the first release; (c) confirm the
candidate code family (§1) and authorize G1 verification of the exact edition/effective date.
