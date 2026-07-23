# M3 Legal-Corpus Replan — Control-Only Package (for owner approval)

**Author:** orchestrator (main session) · **Date:** 2026-07-23 · **Branch:** `control/M3-corpus-replan-2026-07-23`
**Directive:** owner directive 2026-07-23 (repair the missing M3 legal-corpus dependency before any M4-T007+ yard/coverage work; §11-25 correction; architect benchmark; construction-code scope; deterministic completeness harnesses).
**Status of this package:** PROPOSAL, **revision 5** (owner decision: **all PDF parsing/rendering moves into M3-T003**; §17.16 resolved). See §15 (rev-2), §16 (rev-3), **§17 (five-packet restructure — authoritative for the packet map; §17.16 records the rev-5 decision)** + §18 (rev-4 log) + §19 (rev-5 log). No producer is dispatched. M4-T007/T008/T009 are NOT contracted, claimed, or started. The 3-way vs 4-way split is preserved as a downstream candidate and NOT decided here. Nothing merges to `main` until you approve.

> **Reading order note:** §17 supersedes the four-packet structure described in §5B/§7/§8/§9/§10 below wherever they differ. Those earlier sections are retained for the corrections history; **§17 is the current packet map, dependency graph, ownership, evidence model, and harness matrix.** Renumbering: closure moved T003→**T004**; construction-code moved T004→**T005**; the new **T003** is the Document Evidence Verification Engine.

This document is the single return package the directive's section 9 asks for. It is control-only (task packets + docs); it changes no product code.

---

## 1. Live repository reconciliation (directive §1)

| Check | Result |
|---|---|
| `git fetch origin main` | fetched `origin/main` |
| Local tree | on `main` (session-start snapshot showed `control/handoff-2026-07-23-footprint`; live tree was `main`), clean except `.claude/agent-memory/**` |
| `git rev-parse HEAD` | `1acb9b510541cfa87afff6b2dc197880e01a389b` |
| `git rev-parse origin/main` | `1acb9b510541cfa87afff6b2dc197880e01a389b` — **main did NOT advance; the reviewed baseline holds** |
| `python tools/project_control.py status` | 42 accepted / 8 awaiting_gate / 4 backlog / 2 blocked / 1 claimed (before this PR) |
| `python tools/current_state.py` | checkpoint CP-0031; ledger updated 2026-07-23T04:51Z |

**Control-metadata reconciliation (directive §1 asked to check these explicitly):**

- **M3 had no tasks** (status `planned`) — the missing legal-corpus dependency. This PR adds the four proposed packets.
- **M4 summary said "0/5"** but the ledger holds **M4-T001…T006** (six tasks). **Fixed in this PR** to "0/6" with the M4-T006 R5 height/setback family noted, and M4-T007's new dependency on accepted M3-T004 recorded (closure renumbered T003->T004 in rev-4).
- **All M4-T001…T006 + M5-T001 are `awaiting_gate`** — merged DRAFT (`needs_review`), **none accepted, Published, or Verified**. G6 gates the chain.
- Checkpoint is **CP-0031**; **CP-0032 remains reserved** for M0-T019 (not created here).
- Open blockers: **B-001** (Supabase management token → durable object storage; **amended to affect M3-T002, M3-T003 & M3-T005** — the durable-storage tasks; see §17.15), **B-004** (Geoclient key), **B-010** (client R5 benchmark sheet absent from repo), and **B-011** (new — owner-approved construction-code release scope; gates **M3-T005** readiness, see §17.2). (Rev-2/rev-3 text in §10A/§15/§16 references the pre-restructure numbering; **§17 is authoritative** — closure is now T004, construction-code T005.)

**After this PR (control-only):** 42 accepted (unchanged) / 8 awaiting_gate / **8 backlog** (4 new M3 proposals) / 2 blocked / 1 claimed.

---

## 2. Immediate decision (directive §2)

The current 3-way footprint proposal (PR #91) is **not approved for implementation**. The downstream slices (coverage; rear/rear-equivalent; front/side) remain **candidates**; their exact boundaries must be **regenerated after the cross-reference closure graph (M3-T004) identifies the complete reachable section set.** A section list assembled by hand from one chapter is not sufficient evidence of completeness.

`/replan-project` was invoked because the owner supplied new authoritative source requirements, a client architect benchmark, a newly identified legal dependency (§11-25), a construction-code coverage requirement, and a requirement for deterministic completeness/self-check harnesses. This package is the replan output.

---

## 3. Corrections to the current legal analysis (directive §3)

### 3A. District suffix inheritance — ZR §11-25 (CORRECTION)

ZR §11-25: regulations applicable to a district designation apply to that designation **with a suffix** unless the Resolution provides separate express provisions. Therefore:

- **Do not** classify bare "R5" applicability as inherently ambiguous.
- If a section lists R5 and does **not** list separate suffix provisions → **model §11-25 inheritance** (R5A/R5B/R5D inherit).
- If the same section **expressly** lists different R5A/R5B/R5D provisions → those **express provisions control**.
- Preserve explicit exclusions such as §23-422's "except R5 Districts with a letter suffix."
- **§11-25 is added to every relevant rule's closure manifest and tests** (M3-T004 harness AS-1/AS-2/NC-3).

This corrects the earlier tendency to treat bare-R5 as ambiguous by default. It is the canonical test pair for M3-T004: §23-361/R5B **inherits** via §11-25; §23-422 **excludes** suffixed R5.

### 3B. Lot taxonomy — §12-10 (CORRECTION)

**Do not create a general `semi_corner` lot type.** Under §12-10 model: **corner lot; interior lot; through lot; and portions of a zoning lot subject to different classifications.** For a corner lot, preserve the **100-foot corner portion** and separately classify any remaining portion as interior or through when applicable. The classifier must use the **legal zoning-lot boundary and street lines — not merely a PLUTO tax-lot code.** (Harness: lot/applicability, assigned to the downstream M4 slice consuming M3-T003; `Unknown` must never equal `false`; a PLUTO tax-lot code never establishes legal ZR lot type by itself.)

### 3C. Architect benchmark (adversarial; NOT an answer key)

Supplied PDF SHA-256: `9442b5002e10b8ac0d9f78500db7cd4e8b34240e9155d0c61bbb51e00407ea85`. One page labeled "2 OF 2." Project/address/BBL/job/checked-by fields **blank** — **do not infer identity from PDF metadata or filename.**

Observed sheet statements (recorded, not endorsed):

| Item | Sheet statement |
|---|---|
| District | R5 |
| Lot | 40 × 125 ft = 5,000 sq ft |
| §23-361 | 60% / 3,000 sq ft allowed; 2,850 proposed |
| §23-21 | 1.50 / 7,500 sq ft allowed; **7,602 proposed** |
| §23-422 | "35ft, 45ft – with a setback of 15ft"; 35 ft proposed |
| Front yard | 10 ft |
| Rear yard | 20 ft |
| Side yards | 5 ft |

**Required system response (discrepancy/missing-input findings, NOT a forced pass):**

1. Proposed floor area **exceeds the sheet's own stated cap by 102 sq ft** (7,602 vs 7,500).
2. **No floor-area-exclusion schedule** is supplied.
3. **60% lot coverage is not selectable** until legal lot type and proposed residence type are known.
4. The **15-ft setback branch depends** on narrow-street and vertical-envelope conditions.
5. **Side-yard requirements depend** on proposed building type and may require **two** yards.
6. **Project identity and zoning-lot documentation are missing.**

The client PDF **must not be committed** without explicit owner authorization. A derived benchmark report (M3-T001 output) records the hash + observations without claiming the sheet is correct. Tracked by **B-010**.

### 3D. "Confirmed absence" (CORRECTION)

Do not call a modifier "confirmed absent" merely because it was not found in Article II Chapter 3. Absence may be asserted **only** if the declared search universe and cross-reference closure are complete (M3-T004). Otherwise use **`unsupported`**, **`not_evaluated`**, or **`professional_review_required`.**

---

## 4. Source-authority hierarchy (directive §4) — becomes `docs/SOURCE_AUTHORITY_POLICY.md` (M3-T001)

| Tier | Authority | Examples |
|---|---|---|
| 1 | Current enacted/adopted official law | Zoning Resolution; zoning maps; NYC Administrative/Construction Codes; Local Laws; applicable state law |
| 2 | Official amendments + project-specific legal instruments | CPC/City Council actions; BSA variances; special permits; authorizations; certifications; recorded restrictive declarations; zoning-lot development agreements; easements; applicable DOB-approved documents |
| 3 | Official agency interpretations | DOB Rules; Buildings Bulletins; Code Notes; directives; formal interpretations (record issuing body, number, date, cited provisions, status, rescission/supersession) |
| 4 | Official factual datasets | PLUTO/MapPLUTO; ZTLDB; DCP GIS; DOB NOW/BIS; LPC; FEMA/official flood — establish facts with limitations; do not replace legal text |
| 5 | Third-party references | UpCodes and similar — **cross-check only; never controlling provenance** |
| 6 | Architect/client documents | benchmark/project evidence — **never general legal authority** |
| 7 | AI output | **no authority** — retrieves, classifies, proposes extraction, drafts tests, explains deterministic results only |

**Rule:** never generalize a project-specific agency determination to a different property without an approved legal interpretation.

### 4A. Provenance is NOT automatic precedence (amendment item 4)

The seven tiers **classify source provenance; they are not a conflict-resolution ranking.** `SOURCE_AUTHORITY_POLICY.md` (M3-T001) must state:

- An **adopted amendment becomes part of current law**; an older consolidated portal page does **not** defeat a later effective amendment merely because of a tier number.
- A **legally effective project-specific instrument** (variance, special permit, restrictive declaration, zoning-lot agreement) **may control the affected property** even though it is narrower than citywide law.
- **Deterministic resolution must consider** jurisdiction, legal status, effective/as-of date, explicit amendment/supersession/rescission, and scope specificity.
- If precedence or applicability remains unresolved → return **`data_conflict`** or **`professional_review_required`**; **never silently select a source.**
- **AI may propose relationships but has no authority to approve a legal interpretation.**

M3-T001 AS-1/AS-8 prove these points.

---

## 5. Legal-corpus coverage matrix (directive §4/§5) — becomes `docs/LEGAL_CORPUS_COVERAGE_MATRIX.md` (M3-T001)

### 5A. Authoritative status vocabulary (amendment item 5 — reconciled)

**One** authoritative vocabulary, mapped to runtime rule-evaluation outcomes. Domain roll-up may also use `implemented`/`partial`; the per-evaluation outcomes are:

| Status | Meaning | Runtime mapping |
|---|---|---|
| `missing` | required source/domain not yet present | no value; blocks dependent claim |
| `not_evaluated` | in scope but not yet assessed this run | no value; not a negative finding |
| `unsupported` | cannot be resolved with current corpus/closure | typed unsupported result |
| `conflicting` | ≥2 sources disagree, precedence unresolved | `data_conflict` |
| `professional_review_required` | needs qualified-human legal/design judgment | PRR result, never `verified` |
| `not_applicable` | affirmatively resolved as not applying | only after applicability resolved |

**`not_applicable` may be returned only after applicability is affirmatively resolved. Unknown or missing information must NEVER become `not_applicable` or `false`.** (This adds `not_evaluated`, which the earlier draft used in prose but omitted from the vocabulary.)

### 5B. Actionable coverage matrix (amendment item 7)

Every domain row records **six columns**: status; controlling official source channel **or** unavailable-document class; evidence/as-of date; implementing task ID **or** human-action blocker; downstream claims blocked; next action + responsible reviewer. **No `missing`/`partial`/`conflicting`/`unsupported`/`professional_review_required` row may be left without a task, blocker, or explicit continuing limitation. Completing M3-T003 must not imply that unrelated missing domains were covered.** Initial orchestrator assessment (M3-T001 producer verifies + finalizes):

| Domain | Status | Controlling channel / unavailable-class | Evidence as-of | Implementing task / blocker | Downstream claims blocked | Next action (reviewer) |
|---|---|---|---|---|---|---|
| Zoning maps / district facts | partial | DCP GIS zoning-features + ZTLDB (accepted) | 2026-07-20 | M2 (accepted) | lot-level legal determination | note ±20ft limitation (data-contract-verifier) |
| Zoning Resolution text | missing | ZR portal (registry §8) | — | M3-T002 | every rule value / Verified | ingest + fidelity (data-contract-verifier) |
| Amendments / effective dates | missing | ZR /recently-adopted + PDF snapshots | — | M3-T002 | effective-date correctness | multi-signal version detect (data-contract-verifier) |
| Definitions & interpretation (§12-10, §11-25) | missing | ZR text (closure) | — | M3-T004 | applicability / suffix scope | closure graph (qa-engineer) |
| Special districts / overlays | partial | DCP GIS (facts) + ZR (text) | 2026-07-20 | M2 accepted / ZR text M3-T002 | override resolution | ingest override text (data-contract-verifier) |
| Environmental & restrictive declarations | missing | ACRIS / recorded instruments | — | future task (unassigned) | project-specific control | scope a task (orchestrator) |
| Zoning-lot identity & recorded agreements | missing | ZTLDB + recorded ZLDA | — | future task (unassigned) | zoning-lot ≠ tax-lot claims | scope a task (orchestrator) |
| CPC / BSA / DOB project-specific approvals | missing | BSA / CPC / DOB NOW | — | future task (unassigned) | property-specific precedence | scope a task (orchestrator) |
| Construction Code | missing | DOB code PDFs (scope-bounded) | — | M3-T004 + B-011 | construction-feasibility | approve scope (owner, B-011) |
| DOB Rules / Bulletins / Local Laws | missing | DOB Rules/Bulletins/LL overlay | — | M3-T004 | code effective-text | overlay build (data-contract-verifier) |
| Landmarks / historic | partial | LPC (flag) + requirements text | 2026-07-20 | M2 flag / requirements future | landmark requirement claims | scope requirements task (orchestrator) |
| Waterfront / flood / environmental | partial | FEMA/official flood (flag) + reqs | research | M2 flag / requirements future | waterfront/flood requirements | scope requirements task (orchestrator) |
| Occupancy / use / building type | missing | ZR + Construction Code | — | M3-T004 + rule slice | use/occupancy claims | after M3-T003/T004 (orchestrator) |
| Parking / loading | missing | ZR parking regs | — | future rule slice | parking claims | scope after closure (orchestrator) |
| Accessibility / fire-egress / structural | missing | Construction Code (scope-bounded) | — | M3-T004 + B-011 | accessibility/egress/structural | approve scope (owner, B-011) |

Rows marked "future task (unassigned)" carry an **explicit continuing limitation** and an orchestrator next-action; they are not silently covered by M3-T001..T004.

---

## 6. Architect-benchmark discrepancy report (directive §9)

Captured in §3C above and delivered as the M3-T001 output `project-control/reports/M3-T001-architect-benchmark-analysis.md` (hash + observations + the six required discrepancy findings; no PDF, no inferred identity). This is the seed for the **architect-benchmark harness** (§8 below): the sample must produce discrepancy/missing-input findings, never a forced pass.

---

## 7. Proposed M3 task packets + dependency order (directive §5)

IDs confirmed unused before authoring. All four are created **`backlog` / PROPOSED / not contracted** on the control branch. Full packets: `project-control/tasks/M3-T00{1..4}.json`.

| Task | Scope (one line) | Producer | Gates | Depends on |
|---|---|---|---|---|
| **M3-T001** | Authority hierarchy + coverage matrix + registry channels (Construction Code / Local Law / DOB Rule / Buildings Bulletin) + derived benchmark analysis + versioned legal-source manifest schema | official-source-researcher | G0,G1,G2,G3,G4,G5 | M1-T001 (accepted) |
| **M3-T002** | Versioned ZR ingestion (official HTML + PDF), content-addressable raw capture, full provenance fields, `raw_html_verified` discipline, **source-fidelity harness** | legal-corpus-engineer | G0,G1,G2,G3,G4,G5 | M3-T001 |
| **M3-T003** | Cross-reference **closure graph** + §11-25 suffix inheritance + per-rule **closure manifests** + **cross-reference-closure harness** (linked + unlinked + table/footnote citations) | legal-corpus-engineer | G0,G1,G2,G3,G4,G5 | M3-T002 (accepted as production corpus) |
| **M3-T004** | DOB **Construction-Code** corpus (scope-bounded PDFs) + Local Law/DOB Rule/Bulletin/Code Note **effective-date overlay** | legal-corpus-engineer | G0,G1,G2,G3,G4,G5 | M3-T001 + M3-T002 (accepted) + storage (B-001) + **approved release scope (B-011)** |

**Dependency rules (directive §5, amended per items 2 & 3), including the cross-milestone ones:**

- M3-T001 ← accepted **M1-T001** source-registry research.
- M3-T002 ← M3-T001; **reuses `app.resilience.transport`**.
- M3-T003 ← **M3-T002 accepted as the production corpus** (durable captures + fidelity evidence — a fixture-only increment does not satisfy it, item 3).
- M3-T004 ← accepted **M3-T001** + accepted **M3-T002** (imports its ingest/parser/fidelity core) + approved storage/ingestion (**B-001**) + **owner-approved construction-code release scope (B-011)**.
- **M4-T007 and every later yard/coverage/rear/front/side rule ← accepted M3-T003.**
- **Any construction-feasibility claim ← the relevant accepted M3-T004 scope (with durable captures).**
- **G6 remains mandatory** before any rule is Published or Verified.

**File-ownership correction (amendment item 2).** The earlier draft claimed disjoint trees but M3-T002 owned `services/api/app/corpus/**`, which overlaps M3-T003 and M3-T004. Corrected ownership — each tree has exactly one owning task; downstream tasks **import the shared core read-only and never mutate it** (strictly-sequential-modification rule):

| Tree | Owner | Others |
|---|---|---|
| `services/api/app/corpus/ingest/**`, `parsers/**`, `fidelity/**`, `versioning/**` | **M3-T002** (shared core) | T003/T004 import read-only |
| `services/api/app/corpus/closure/**` | **M3-T003** | excluded from T002/T004 |
| `services/api/app/corpus/construction_code/**`, `overlay/**` | **M3-T004** | excluded from T002/T003 |
| `docs/*` + `packages/contracts/schemas/**` (per-file) | **M3-T001** (policy/matrix/registry/scope/manifest); **M3-T003** (closure_manifest schema) | non-overlapping files |

M3-T002's `forbidden_paths` now explicitly exclude `closure/**`, `construction_code/**`, and `overlay/**`.

---

## 8. Harness assignments (directive §6)

| Harness | Assigned to | Key cases |
|---|---|---|
| **Source-fidelity** | M3-T002 (extended to PDF in M3-T004) | exact-bytes hash reproduces / changed bytes fail; replay to source offsets/DOM/PDF page; HTML-vs-PDF → `data_conflict`; missing version evidence blocks publication; redirects/host-change/malformed/drift fail closed |
| **Version-change-detection** (item 8) | M3-T002 | banner is one signal; changed section hash / Last-Amended / amendment feed / adopted instrument / official PDF each raise a candidate corpus version even with an unchanged banner; unchanged banner never suppresses a detected change |
| **Cross-reference-closure** | M3-T003 | §23-361/R5B imports §11-25 unless expressly overridden; §23-422 express exclusion blocks R5→R5A/R5B/R5D leakage; unresolved definition/exception/citation-candidate → no final value; cycles terminate; renumber/delete detected; single-chapter cannot satisfy absence; **linked + unlinked + table/footnote + unparseable citations cannot be silently missed; AI-extracted edges proposed until validated** (item 8) |
| **Lot/applicability** | downstream M4 slice (consumes M3-T003) | interior/corner/through/mixed portions; 135° boundary; curved-street tangent; 100-ft corner + remainder; zoning-lot ≠ tax-lot; missing zoning-lot docs; split district; wide/narrow street; detached/semi-detached/zero-lot-line/attached/multiple-dwelling; special/overlay/landmark/waterfront unknowns. `Unknown` never `false`; PLUTO code never sets legal lot type |
| **Rule-behavior** | downstream M4 slice | positive/negative/boundary/not-applicable/missing-input/conflict/exception-applies/-not/effective-date-before-after/source-tamper/competing-rule; byte-identical determinism; every value carries section+URL+raw hash+corpus version+effective date+rule version+closure-manifest ID; `Verified` structurally unreachable without G6 |
| **Architect-benchmark** | M3-T001 seed → downstream M4 slice | sample yields discrepancy/missing-input findings not a pass; 7,602 vs 7,500 surfaced; no invented exclusion; lot coverage not selected without residence+lot-type branches; no inferred address/BBL; no final buildable-envelope claim |
| **Consumer-boundary** | M3-T004 (construction-code) + existing M5 boundary | M5 rejects yards/coverage/height/setback as a complete envelope until all blocking coverage-matrix domains present; unknown rule outputs not silently consumed; no output relabeled gross/net/sellable/feasible/compliant/buildable |

**Live-source smoke tests are separate from deterministic CI.** CI runs on frozen official fixtures; scheduled smoke tests detect upstream change without making normal builds depend on live government sites.

---

## 9. Dependency plan (directive §7)

- **Reuse first:** `app.resilience.transport` (bounded HTTP); existing JSON/hash/path libs; existing `jsonschema`; existing `shapely==2.0.7` only for already-justified geometry.
- **Do NOT add:** `requests`, browser automation, an UpCodes SDK, scraping frameworks, or an AI framework.
- **`httpx` is dev/test-only** — not an approved runtime crawler dependency; do not import it in production merely because tests install it.
- The first authority/manifest + raw-**HTML** capture work should require **no new runtime dependency** — HTML uses the Python stdlib (`html.parser`). If the stdlib parser cannot safely preserve required HTML/table structure, invoke **`/dependency-security`** and select **exactly one** HTML parser — justified vs alternatives, exact-pinned, **≥7 days old**, vulnerability-audited, installed-wheel tested, in reproducibility + deployment checks.
- **PDF extraction correction (amendment item 2):** the Python **standard library does not parse PDFs**. Official **ZR PDF text extraction, page replay, and HTML-vs-PDF comparison are required by M3-T002 itself**, so **M3-T002 owns the approved PDF text-extraction adapter** (`services/api/app/corpus/parsers/pdf/**`). The underlying library is **NOT chosen in this control-only PR** — the decision is recorded as a requirement: `/dependency-security` selection, exact pinning, vulnerability review, installed-wheel verification, and **G5 evidence** before any PDF library is added. **M3-T004 imports the approved M3-T002 adapter read-only** and does not choose its own PDF library. **OCR** remains a separate conditional decision; OCR output stays **draft-only** with page/image provenance. No wording anywhere implies a stdlib PDF parser exists.
- **No paid service required** for these official sources (ZoLa/ZR/Open Data/DCP ArcGIS/DOB docs are public; Geoclient needs only a free key). If any source later requires payment, authentication, licensing, or redistribution rights → **stop and record a human-action blocker**; do not purchase, accept terms, or scrape around restrictions.

---

## 10. Storage plan + blockers (directive §7/§8)

- Bulk raw HTML/PDF artifacts are stored **content-addressably in approved cloud object storage** (Supabase Storage / Render worker). **Never** commit a citywide corpus; **never** leave bulk temp data on the owner's ~7 GB PC (thin-client policy).
- **B-001 (Supabase management token) gates durable object storage.** If it remains open, M3-T002/T004 degrade to **bounded frozen fixtures + parser + harness only**, and each report **states the limitation explicitly** (no faked durability). Recorded as a `blockers` entry on M3-T002 and M3-T004.
- **B-004** (Geoclient key) is not on the M3 path. **B-010** (client benchmark sheet) blocks committing the PDF, not the derived analysis.

### 10A. Fixture-only work must not unlock production (amendment item 3)

Explicit invariant, carried into M3-T002 and M3-T004 as an `acceptance_preconditions` block and enforced by the control CLI (accept requires **zero open blockers referencing the task**; B-001 is such a blocker):

- Fixture/parser/harness work **may be developed and gate-reviewed** while storage is blocked.
- It **must not** mark the ZR or Construction-Code corpus domain `implemented`.
- **M3-T002 does not reach `accepted`** as the production ZR corpus — and **does not satisfy M3-T003's dependency** — until durable, content-addressed official captures + required source-fidelity evidence exist.
- **M3-T004 does not reach `accepted`** for any construction-code scope, and **does not unblock any feasibility claim**, until durable official captures + overlay evidence exist.
- The distinction is expressible in the lifecycle (gate PASS on the engineering increment ≠ acceptance; B-001 blocks acceptance while open), so **no task split is required**; if evidence later shows the lifecycle cannot hold the distinction, the fallback is to split engineering/harness from production-corpus acceptance into separate tasks.

### 10B. Construction-code release scope is frozen before readiness (amendment item 6)

`"declared release scope from PRD / owner"` is not a sufficient input. **M3-T001 drafts `docs/CONSTRUCTION_CODE_RELEASE_SCOPE.md`** (code edition + as-of date; product claims supported; exact in-scope titles/chapters/domains; required LL/DOB-Rule/Bulletin/Code-Note/rescission/supersession channels; excluded domains; consumer claim each exclusion blocks). Owner approval of that document clears **B-011**. **M3-T004 stays `backlog`/blocked until B-011 clears.** AI has no authority to set release scope.

**Scope of what B-011 approval means (clarification).** Owner approval of the release-scope artifact is a **product/release-scope decision** — it fixes *which* code domains are in scope. It is **NOT** a legal approval and does not certify legal adequacy or completeness. **Qualified professionals still approve legal interpretations and release adequacy through G6**, which remains mandatory before any rule sourced from this corpus is Published/Verified. B-011 and G6 are independent gates.

**Stop-rather-than-guess conditions (directive §8)** are carried into each packet's risks: unverified endpoint/source identity; unclear licensing/terms; bot-blocked source; raw-HTML-vs-PDF disagreement; unresolvable amendment/effective date; unresolved cross-reference; unavailable legal zoning-lot geometry; tax-lot-may-not-equal-zoning-lot; a controlling project-specific approval/restrictive declaration; a conclusion needing professional legal/design judgment; unavailable durable-storage credentials.

**Gates:** M3 source/corpus work runs **G0–G5 at one frozen implementation SHA**. Rule releases additionally require genuine **G6** qualified-human review. G6 is not weakened anywhere in this plan.

---

## 11. §11-25 correction — recorded

See §3A. §11-25 suffix inheritance is (a) a required correction to the current analysis, (b) an M3-T004 graph edge type, (c) a closure-manifest entry for every relevant rule, and (d) harness cases AS-1/AS-2/NC-3. The §23-422 express exclusion is preserved as the counter-case.

---

## 12. Revised recommendation — 3-way vs 4-way (directive §9)

**Recommendation: do not fix the number now; regenerate the slice boundaries from the M3-T004 closure set, and expect 4-way (or more) to be the floor, not 3-way.**

Rationale:
- The current 3-way grouping (coverage / rear+rear-equivalent / front+side) was assembled from a manual chapter reading. The owner's §11-25 correction and the §12-10 lot-taxonomy correction both change which sections are reachable and how R5A/R5B/R5D scope, so the *inputs* to the split decision are not yet stable.
- Front and side yards have **different** applicability drivers (side-yard count depends on building type — detached/semi-detached/zero-lot-line/attached — and may require two yards; front-yard depth interacts with the §23-423 setback offset with its 7-ft floor). Bundling front+side risks hiding a building-type branch, which is exactly the failure the benchmark (§3C item 5) exposes.
- Therefore the **4-way split** (T007 lot coverage → T008 rear + rear-equivalent → T009 front → T010 side) is the more honest **lower bound**; the closure graph may reveal a further split (e.g. open-space/FAR-interaction, or building-type-specific side-yard sub-rules).

**Concrete proposal:** keep the 4-way split as the working candidate, but **contract its exact boundaries only after M3-T004 is accepted**, when the reachable controlling-section set and the §11-25/§12-10 predicates are known. Until then M4-T007+ stays uncontracted, dependent on accepted M3-T004.

---

## 13. What I did NOT do (holds preserved)

- Did **not** contract, claim, dispatch, or implement M4-T007/T008/T009.
- Did **not** ask you to choose 3-way vs 4-way (deferred to post-closure per directive).
- Did **not** commit the client PDF or infer its identity.
- Did **not** change M3 to `active` or move any M3 packet past `backlog` — approval flips them to `ready`.
- Did **not** create CP-0032 (reserved for M0-T019). No new checkpoint created; this replan is recorded in this report + the packets.
- Preserved all standing holds: G6, survey (M2-T014/T015/T016), expansion/3D-UI, credentials (B-001/B-002/B-004), thin-client, PR #64 frozen.

---

## 14. Requested approval

Please approve (or amend) this control-only package. On approval I will:
1. Merge the control-only PR (packets + docs reconciliation) to `main`.
2. Move **M3-T001 ONLY** `backlog → ready → claimed`, dispatch the producer at one frozen SHA, and return full G0–G5 evidence before starting M3-T002. **M3-T002, M3-T003, and M3-T004 stay `backlog`** — approval of this package does not move them; each is contracted only when its dependencies (and, for T002/T004, its blockers) clear.
3. Keep M4-T007+ uncontracted until M3-T003 is accepted.

No producer work starts until you approve.

---

## 15. Amendment log — PR #93 revision 2 (owner corrections 1–8)

Applied in-branch (control-only) on `control/M3-corpus-replan-2026-07-23`. No task moved, claimed, dispatched, implemented, or accepted.

| # | Correction | How implemented |
|---|---|---|
| 1 | Complete every task contract (no empty `outputs`) | All four packets now carry exact `outputs[]` artifact paths that agree with `allowed_paths`, acceptance scenarios, harness assignments, and producer-report paths (G0 inputs+outputs satisfied). |
| 2 | Correct dependencies + file ownership | M3-T004 `dependencies` = M3-T001 **+ M3-T002**; blockers add **B-011**. M3-T002 ownership narrowed to `ingest/parsers/fidelity/versioning`; `closure/**`, `construction_code/**`, `overlay/**` explicitly excluded via `forbidden_paths`. Ownership table + strictly-sequential-modification rule documented (§7). |
| 3 | Fixture-only must not unlock production | New `acceptance_preconditions` on M3-T002 & M3-T004: fixture/harness work is gate-reviewable but the task is not accepted, does not mark the domain `implemented`, and does not satisfy downstream deps until durable content-addressed captures + fidelity/overlay evidence exist. Enforced by B-001 in `blockers[]` (accept requires zero open referencing blockers). §10A. No task split needed; fallback split documented. |
| 4 | Separate source authority from legal precedence | `SOURCE_AUTHORITY_POLICY.md` requirements + M3-T001 AS-1/AS-8: tiers are provenance, not auto-precedence; amendments become current law; project-specific instruments may control; resolution by jurisdiction/legal-status/effective-date/amendment-supersession/scope; unresolved → `data_conflict`/`professional_review_required`; AI proposes only. §4A. |
| 5 | Reconcile status vocabulary | Authoritative vocabulary now includes **`not_evaluated`** and maps to runtime outcomes; `not_applicable` only after affirmative resolution; unknown/missing never → `not_applicable`/false. M3-T001 AS-9. §5A. |
| 6 | Freeze M3-T004 release scope before ready | New `docs/CONSTRUCTION_CODE_RELEASE_SCOPE.md` drafted by M3-T001 (M3-T001 AS-10); owner approval = **B-011** (new blocker); M3-T004 stays backlog/blocked until B-011 clears (M3-T004 AS-8). §10B. |
| 7 | Every coverage gap actionable | Coverage matrix expanded to six columns (status, controlling channel/unavailable-class, evidence/as-of, task/blocker, downstream claims blocked, next action + reviewer); no unresolved row without a task/blocker/explicit continuing limitation; closure ≠ covering unrelated domains. M3-T001 AS-3. §5B. |
| 8 | Strengthen source verification + version detection | **M3-T001:** registry rows for every M3-T004 channel incl. Code Notes/directives + formal DOB interpretations; ZoLa presentation-only; UpCodes reference-only with dated API-availability/subscription/pricing + 'not required'; unresolved source identity/endpoint/access/terms/URL BLOCKED at G1 (AS-5/AS-6). **M3-T002:** multi-signal version detection — banner is one signal; hash/Last-Amended/feed/instrument/PDF changes each raise a candidate version; unchanged banner never suppresses a change (AS-5). **M3-T003:** closure covers linked+unlinked+table/footnote+unparseable citation candidates; unresolved candidates block a final value; adversarial 'cannot be silently missed' tests; AI-extracted edges proposed until validated (AS-8/AS-9). |

Also created blocker **B-011** and left B-010/B-001 semantics unchanged. Ledger totals unchanged: 42 accepted / 8 backlog (4 M3 proposals) — nothing accepted.

---

## 16. Amendment log — PR #93 revision 3 (owner corrections, four final issues)

Applied in-branch (control-only). No task moved, claimed, dispatched, implemented, or accepted.

| # | Correction | How implemented |
|---|---|---|
| 1 | Make B-001 enforcement real | Amended `B-001-supabase-access-token.json` so `affects` names **M3-T002** and **M3-T004** (durable legal-corpus storage required before acceptance). The CLI blocks acceptance when a blocker's affects/detail names the task (`_blocker_references`, project_control.py:525); packet `blockers[]`/prose alone are not enforced. Added permanent control-plane regression **S9** in `tools/test_project_control.py` (the file CI's `control-plane` job runs) proving open B-001 blocks accept of both tasks, a fixtures-only marker cannot bypass, and resolving B-001 unblocks — in an isolated temp ledger that leaves real state untouched. Evidence: `project-control/reports/M3-CORPUS-B001-enforcement-evidence.md`. |
| 2 | Correct PDF-extraction plan | Removed all wording implying a stdlib PDF parser exists. HTML parsing = stdlib (`parsers/html/**`). **M3-T002 owns the approved PDF text-extraction adapter** (`parsers/pdf/**`) required for ZR PDF text + page replay + HTML-vs-PDF compare; the library is **not chosen in this control-only PR** — recorded requirement: `/dependency-security` + exact pin + vuln review + installed-wheel + **G5** evidence. **M3-T004 imports the approved adapter read-only.** OCR separate, draft-only. Report §9 corrected. |
| 3 | Restore executable schema acceptance | M3-T001 **AS-11** (legal_source_manifest): schema meta-validates; positive fixture validates; negatives missing provenance/version/hash fail; version + `$id` deterministic; not promoted to canonical cross-tier without a justified consumer. M3-T003 **AS-10** (closure_manifest): equivalent, incl. negative fixtures missing the unresolved-reference field and missing per-node source-version/hash. Positive+negative fixture paths added to both packets. |
| 4 | Synchronize review surfaces | PR #93 description updated (M3-T004 deps = M3-T001 + accepted M3-T002 + B-001 + B-011). Report: B-011 added to §1 open-blocker reconciliation; §14 clarified that approval moves **only M3-T001** toward ready/claim (T002/T003/T004 stay backlog); §10B + B-011 record that owner scope approval is a product/release-scope decision, **not** legal approval — **G6** still governs legal interpretation + release adequacy. Remote GitHub CI vs local checks are reported with separate exact counts (see return message). |

---

## 17. Five-packet restructure — Document Evidence Verification Engine (rev-4; AUTHORITATIVE packet map)

Owner directive 2026-07-23 adds a required document-evidence-verification layer and splits the over-broad former M3-T002 (storage + version + PDF + OCR + verification) into dedicated packets. This section is authoritative wherever it differs from §5B/§7–§10.

### 17.1 Fundamental accuracy boundary (three truths)

Three separate questions, none resolved by any single OCR/parser/AI/calculator:
1. **Extraction truth** — what the official document visibly states.
2. **Legal truth** — does that provision apply to this property and as-of date.
3. **Mathematical truth** — was the calculation performed correctly on approved inputs.

**Prohibited claims** (grep-enforced absent from M3 deliverables): "100% accurate OCR", "100% legally accurate", "OCR confidence proves correctness", "two OCR engines agreed therefore verified", "arithmetic consistency proves the extracted rule is correct".

**System guarantee:** no unverified or conflicting OCR-derived critical value may enter a Published/Verified rule, final constraint, compliance conclusion, or buildability calculation. The calculator is only "mathematically deterministic for its declared inputs"; legal correctness still needs source evidence + applicability closure + G6.

### 17.2 Packet map + dependency graph

| Task | Scope (one line) | Producer | Gates | Depends on | Blockers |
|---|---|---|---|---|---|
| **M3-T001** | authority hierarchy + coverage matrix + registry channels + benchmark analysis + legal_source_manifest + **DOCUMENT_EVIDENCE_POLICY** + construction-code release-scope DRAFT | official-source-researcher | G0–G5 | M1-T001 | — |
| **M3-T002** | **immutable source capture + versioning** (exact bytes, content-addressable storage, SHA-256, rendered-page derivatives, multi-signal change detection); **NO OCR/extraction** | legal-corpus-engineer | G0–G5 | M3-T001 | B-001 (accept) |
| **M3-T003** | **Document Evidence Verification Engine** (classify to native/OCR extract to critical-token to cross-source to evidence-state machine to human-review bundles; adversarial harness; PDF+OCR dependency chosen here) | legal-corpus-engineer | G0–G5 | M3-T001 + **accepted M3-T002** | B-001 (accept) |
| **M3-T004** | **cross-reference closure + applicability graph** (§11-25; closure manifests; consumes ONLY eligible verified evidence) | legal-corpus-engineer | G0–G5 | **accepted M3-T002 + accepted M3-T003** | — |
| **M3-T005** | **DOB Construction-Code + amendment overlay** (scope-bounded; **reuses** the M3-T003 engine) | legal-corpus-engineer | G0–G5 | M3-T001 + accepted M3-T002 + accepted M3-T003 + **B-001** + **B-011** | B-001, B-011 |

Dependency order: M1-T001 (accepted) then M3-T001 then M3-T002 then M3-T003 then M3-T004 then M4-T007+ (yard/coverage). M3-T005 branches off after M3-T003 and additionally needs B-001 + B-011. B-001 gates acceptance of T002, T003, T005. Any construction-feasibility claim depends on accepted **M3-T005** scope. **G6** mandatory before any rule Published/Verified.

### 17.3 Exact ownership boundaries (one owner per tree; downstream imports read-only)

| Tree | Owner |
|---|---|
| `services/api/app/corpus/ingest/**`, `storage/**`, `versioning/**` | **M3-T002** |
| `services/api/app/corpus/extractors/**`, `document_validation/**`, `evidence/**` | **M3-T003** |
| `services/api/app/corpus/closure/**` | **M3-T004** |
| `services/api/app/corpus/construction_code/**`, `overlay/**` | **M3-T005** |
| `docs/*` policy/matrix/registry/scope + `legal_source_manifest.schema.json` | **M3-T001** |
| `document_classification`/`extraction_run`/`evidence_span`/`cross_source_comparison`/`human_review_decision` schemas | **M3-T003** |
| `closure_manifest.schema.json` | **M3-T004** |

Strictly-sequential-modification rule: only the owning task edits its tree; downstream tasks import, never mutate.

### 17.4 Document classification (M3-T003)

Classes: `digitally_born` · `scanned_image` · `existing_ocr_layer` · `hybrid_text_and_image` · `classification_uncertain` · `malformed_or_unsupported`. The last two **fail closed**. Classification evidence: native-text presence, per-page text/image coverage, font/encoding anomalies, selectable-vs-visible alignment, hidden-OCR-layer presence, rotation/crop/media box/DPI, parser + classifier versions.

### 17.5 Extraction strategy (M3-T003)

- **Digitally born:** native extraction primary; preserve chars/words, page, bbox/polygon, reading order, font/encoding, table cells + row/col headings, links/citations/footnotes/superscripts/annotations, exact-raw + normalized. Do **not** OCR by default; OCR only as selective diagnostic when the text layer is corrupt/hidden/incomplete/misaligned.
- **Scanned:** OCR is always initially `ocr_draft`; per span preserve page, bbox, page-image hash, exact OCR text, engine+version, config+language, **raw confidence labeled a model score (not a probability of correctness)**, preprocessing, DPI, review status. A high score **never** auto-promotes a critical legal field.
- **Existing-OCR-layer / hybrid:** compare hidden layer vs visible render vs fresh OCR vs native, then a mismatch becomes `extraction_conflict`; never silently trust the hidden layer.

### 17.6 Critical-token specification (M3-T003)

Detected tokens: section/chapter citations; FAR values; percentages; dimensions/areas; dates + effective dates; amendment numbers; decimal points; negative signs; fractions; units; district names + suffixes; table row/col headings; footnote markers; and the words **not, except, unless, provided that, more than, less than, at least, no more than, before, after, and vs or**. Any disagreement involving a critical token **blocks automatic eligibility**. Required test mutations: `1.50` to `150`/`1.80`/`1.5O`; `15 ft` to `75 ft`; `35` to `85`; `%` omitted; minus omitted; "shall not" to "shall"; "except R5 Districts with a letter suffix" partially omitted; table value under the wrong heading; footnote modifier omitted; two-column text combined in the wrong order.

### 17.7 Evidence-state model + schema proposal (M3-T003)

**Extraction states:** `raw_captured` · `document_classified` · `native_extracted` · `ocr_draft` · `evidence_checked` · `cross_source_matched` · `extraction_conflict` · `human_confirmed` · `rejected` · `unsupported`. **No single vague `verified` flag.** Legal-review state is tracked separately.

Every **evidence span** records: source-document ID; raw SHA-256; rendered-page hash; source URL + publisher; retrieval timestamp; corpus version; page number; bbox/polygon; visible context snippet; raw text; normalized text; extraction method; engine name/version/config; criticality classification; cross-extractor results; cross-source comparison result; arithmetic/unit checks; human reviewer + date + decision (where applicable); rule-draft eligibility; legal-review status (separate).

**Rule-draft eligibility** requires either (native-extracted with deterministic replay + required official cross-source reconciliation) **or** (OCR-derived AND a human explicitly confirmed the highlighted source evidence). Eligibility is not Published/Verified/compliant/legally approved.

**New versioned internal schemas** (each: positive fixture + multiple negative fixtures; stable `$id` + version; required provenance/hashes/engine-config/page-coords; explicit unknown/conflict states; rejects missing critical evidence): `document_classification`, `extraction_run`, `evidence_span`, `cross_source_comparison`, `human_review_decision` (M3-T003); plus `legal_source_manifest` (M3-T001) and `closure_manifest` (M3-T004). Internal contracts until a justified cross-tier consumer is approved.

### 17.8 Cross-source verification (M3-T003)

HTML is the primary structured channel; official PDF is an independent presentation/archive channel. Align by article/chapter/section + effective version; preserve both raw forms; normalize **only** layout artifacts (approved whitespace/hyphenation) — never words/numbers/punctuation/negation/comparisons/units/citations in a meaning-changing way. Critical-token disagreement becomes `data_conflict` (identify both sources+versions, list affected rules, prevent publication, require official reconciliation or human review). An unchanged homepage banner never suppresses a detected PDF/HTML/section-hash/Last-Amended/amendment-feed change.

### 17.9 Mathematical validation engine (M3-T003)

Deterministic, separate from extraction and applicability: parse numbers from original strings; preserve decimal precision; **exact decimal/integer/rational arithmetic, never binary float for legal thresholds**; explicit unit normalization; reject unknown/incompatible units; formula traces; exact boundary values. Verified samples: 40x125=5,000; 5,000x1.50=7,500; 7,602-7,500=102; 60%x5,000=3,000. **Arithmetic consistency is supporting evidence only — it never proves the selected FAR/coverage/yard/branch applies. No AI-generated numeric value enters this calculator.**

### 17.10 Verification-harness matrix (M3-T003)

Bounded frozen fixtures: digitally-born PDF · scanned page · existing incorrect OCR layer · hybrid text/image · multi-column legal text · rotated page · merged-cell table · table footnote changing a value · decimal/percentage values · negation/exception language · superscript/fraction · malformed PDF · password-protected/unsupported PDF · HTML-vs-PDF agreement · HTML-vs-PDF critical conflict · OCR-engine disagreement · arithmetic inconsistency · correct arithmetic with the wrong legal branch. Public official fixtures where licensing permits + synthetic adversarial mutations; the client architect PDF is **not** committed (authorized hash + derived expectations only).

**Acceptance standard:** 100% exact critical-token match on the bounded approved golden set; zero OCR-derived critical fields auto-promoted without human confirmation; zero silent HTML/PDF critical conflicts; every extracted field replays to page coordinates; every mathematical result has an exact formula/unit trace; every malformed/uncertain/conflicting/unsupported case fails closed; **no claim that bounded-fixture performance proves universal 100% accuracy.**

### 17.11 Dependency-security decision plan (M3-T003)

**No dependency chosen or installed in this control-only PR.** During M3-T003 G0/G5: use `/dependency-security`; benchmark the native PDF parser/renderer against frozen fixtures; benchmark an OCR option only for scanned content; select the smallest justified set; exact-pin every runtime dependency; verify release age (>= 7 days), vulnerabilities, licenses, wheels, Render compatibility, deterministic output, and memory; record engine version + config in every extraction run. A second OCR engine is **disagreement detection only**, never proof of correctness. **No paid/cloud OCR by default** — if proposed, STOP and report pricing/auth/data-retention/terms/rate-limits/why-local-inadequate/owner-approval. **No AI or RAG framework** for OCR verification.

### 17.12 Integration boundary (M3-T001 policy)

official source to immutable capture (T002) to evidence verification (T003) to structured eligible evidence to closure/applicability (T004) to draft rule to G6 human legal approval to deterministic calculator. **The rule engine never reads raw OCR strings.** If any preceding stage is missing/unresolved/conflicting/stale/out-of-scope, the consumer receives `missing` / `not_evaluated` / `unsupported` / `data_conflict` / `professional_review_required` — never a default/nearest value, `not_applicable`, compliant, feasible, or buildable result.

### 17.13 Security + resource controls (all capture/extraction tasks; G5)

Every PDF (including government-hosted) is untrusted. The controls split by ownership (§17.16): **capture-time controls belong to M3-T002** — approved hosts + redirect policy, MIME + file-signature validation, byte/time limits, safe filenames/paths, no execution, private/quarantined storage; **parser-level controls belong to M3-T003** (where the parser/renderer runs) — max page count / decompressed-stream size / image dimensions / processing time, memory/CPU budgets, sandboxed worker with no unnecessary network, **no execution of PDF JavaScript/attachments/actions/macros/external references**, reject encrypted/unsupported unless an approved workflow exists, parser crash isolation, prompt-injection isolation if extracted text is ever shown to an AI (embedded document instructions are data, never control). No bulk temp files on the owner PC; sensitive-log redaction throughout. **G5 must include malicious and malformed PDF fixtures (in M3-T003).**

### 17.14 Storage + reproducibility (M3-T003)

Content-addressable in approved cloud object storage, split by ownership (§17.16): **M3-T002 stores the immutable ORIGINALS** (original PDF, original HTML) via its **generic append-only interface**; **M3-T003 appends** rendered page images, extraction result, OCR result, evidence manifest, page crops/review bundles, cross-source diff, and human decision record via that same interface (never editing T002 code or overwriting); **M3-T005 appends** the construction-code corpus + overlay. **Deduplicate by hash; never overwrite an old version.** Reproducible by: raw document hash + engine version + config hash + language pack/version + render DPI + normalization version + evidence-schema version. **An engine upgrade creates a NEW extraction run; it does not erase previous evidence.** B-001 references and blocks acceptance of every durable-storage task (T002/T003/T005) — proven by regression S9.

### 17.15 B-001 enforcement proof (rev-3 mechanism, extended)

`B-001.affects` now names **M3-T002, M3-T003, M3-T005**; the CLI blocks acceptance when a blocker's affects/detail names the task (`_blocker_references`). Control-plane regression **S9** (`tools/test_project_control.py`) proves, in an isolated temp ledger, that open B-001 blocks acceptance of all three, a `fixtures_only` marker cannot bypass, and resolving B-001 unblocks all three. Evidence: `project-control/reports/M3-CORPUS-B001-enforcement-evidence.md`.

### 17.16 Decision recorded (owner, rev-5): ALL PDF parsing/rendering lives in M3-T003

The earlier open question is **resolved**: **all PDF parsing and rendering move into M3-T003**, removing the dependency inversion (T002 could not be accepted until rendered pages existed; the renderer is selected in T003; T003 depends on accepted T002).

- **M3-T002** is a TRUE immutable-capture packet: exact bytes; raw SHA-256; content-addressable, deduplicated, never-overwrite storage exposed as a **generic append-only interface**; canonical URL / publisher / tier / retrieval timestamp / HTTP status+metadata; transport-level MIME/file-signature checks; and **byte-level** multi-signal version detection (raw HTML hash, raw PDF hash, Last-Amended, amendment feed, adopted instruments). **No** page count, rotation/crop/media box/DPI, parser/normalized-layout hashes, rendering, or page-image derivatives. T002 security is **capture-time only** (hosts/redirects, byte/time limits, MIME/signature, safe paths, no execution, private/quarantined storage). T002 is **independently acceptable** on durable original captures + hashes + version-detection evidence — **no forward dependency on T003**.
- **M3-T003** owns the **entire PDF-handling surface**: parser/renderer selection via `/dependency-security`; PDF classification + parser-derived metadata (page count, rotation, crop/media boxes, DPI); deterministic page rendering; rendered-page images + hashes; native text/layout extraction; OCR. Every rendered/parsed derivative records: original raw-document hash, page number, renderer/library name + exact version, config hash, render DPI + page geometry, rendered-page hash, creation timestamp, schema version. T003 **consumes accepted T002 originals + hashes** (not T002-rendered pages — T002 renders nothing) and **appends** its derivatives + manifests via T002's append-only interface **without editing T002 code or overwriting** existing objects.

This is the recorded decision; §17.2/§17.3/§17.5/§17.13/§17.14 are read consistently with it.

---

## 18. Amendment log — PR #93 revision 4 (five-packet Document Evidence Verification Engine)

Applied in-branch (control-only). No task moved, claimed, dispatched, implemented, or accepted.

| Area | Change |
|---|---|
| Packet split | M3 is now **five** packets (17.2). Former M3-T002 (storage+version+PDF+OCR+verify) split; closure T003 to **T004**; construction-code T004 to **T005**; new **T003** = Document Evidence Verification Engine. |
| M3-T001 | Added `docs/DOCUMENT_EVIDENCE_POLICY.md` output (three-truths boundary, distinct evidence states, OCR-has-no-authority, extraction-is-not-G6, prohibited-claims, integration boundary) + AS-12; renumbered refs (closure to T004, construction-code to T005). |
| M3-T002 | Narrowed to immutable capture + versioning only (no OCR/extraction); owns `ingest/storage/versioning`; multi-signal versioning; untrusted-PDF security; fixture-not-production via B-001. |
| M3-T003 | New evidence engine: classification, native/OCR extraction, critical-token, table/footnote, cross-extractor, HTML-vs-PDF, arithmetic validator, evidence-state machine, human-review bundles, adversarial harness, five new schemas, PDF/OCR dependency chosen here via /dependency-security. |
| M3-T004 | Closure now depends on accepted M3-T002 + M3-T003 and consumes ONLY eligible evidence (rejects ocr_draft/conflict/unresolved/unconfirmed/AI-unvalidated) — AS-9; closure_manifest gains a per-node evidence-eligibility reference. |
| M3-T005 | Construction-code reuses the accepted M3-T003 engine (no second PDF/OCR impl); deps M3-T001+T002+T003; blockers B-001+B-011. |
| B-001 | `affects` now names **M3-T002, M3-T003, M3-T005**; S9 regression extended to all three (fixtures cannot bypass; resolving unblocks all three). |
| B-011 | Retargeted from M3-T004 to **M3-T005**; scope-approval is not legal-approval wording preserved (G6 independent). |
| master_plan | M3 summary to five packets + dependency order; M4-T007+ now depends on accepted **M3-T004**. |
| Dependencies | Not chosen or installed in this control-only PR; PDF/OCR selection deferred to M3-T003 `/dependency-security` (17.11). |

Ledger totals: **42 accepted / 9 backlog** (5 M3 proposals + 4 pre-existing) — nothing accepted, moved, claimed, or dispatched.

---

## 19. Amendment log — PR #93 revision 5 (final §17.16 decision: all PDF parsing/rendering in M3-T003)

Applied in-branch (control-only). No task moved, claimed, dispatched, implemented, accepted, merged, or dependency-installed.

| Area | Change |
|---|---|
| §17.16 decision | Recorded owner decision: **all PDF parsing/rendering lives in M3-T003**; dependency inversion removed (T002 no longer needs a T003-selected library to be accepted). |
| M3-T002 | Stripped every parser/render/page-derivative element (page count, rotation/crop/media box/DPI, normalized-layout hashes, rendering, page-image derivatives/hashes, parser-dependent inspection) from objective/inputs/outputs/acceptance-preconditions/acceptance-scenarios/harnesses/risks. Now: exact bytes + raw SHA-256 + content-addressable never-overwrite storage as a **generic append-only interface** + capture metadata + transport MIME/signature + **byte-level** multi-signal version detection. Security = capture-time only. **No forward dependency on T003**; independently acceptable on durable original captures. |
| M3-T003 | Now owns the **entire PDF-handling surface**: parser/renderer selection, classification + parser-derived metadata, deterministic rendering, rendered-page images+hashes, native extraction, OCR. Added rendered-derivative provenance (raw-doc hash, page, renderer name+exact version, config hash, DPI+geometry, rendered-page hash, timestamp, schema version) + AS-1b. Input corrected to consume T002 **originals + hashes** (not rendered pages); appends derivatives via T002's append-only interface without editing T002 or overwriting. |
| B-001 | Wording reconciled to the new ownership (T002 = original captures; T003 = rendered pages + extraction/OCR evidence + review bundles; T005 = code corpus). **Removed the literal `M3-T004` token from `detail`** — it would have made the CLI also block closure acceptance (caught by the hardened S9 drift guard). Acceptance blocking for T002/T003/T005 unchanged. |
| Enforcement report | `M3-CORPUS-B001-enforcement-evidence.md` rewritten to consistently identify **M3-T002/M3-T003/M3-T005** (title, purpose, mechanism, sub-check table, run-output, isolation confirmation). |
| S9 test | Fixed the stale header comment; **hardened** to READ the real committed `B-001` JSON, assert its affects/detail reference **exactly** `{M3-T002, M3-T003, M3-T005}` (drift guard), copy that real record into the isolated temp ledger, and set only the temp copy to `resolved`. The real blocker and real task state are never mutated. |
| Security/storage (report §17.13/§17.14) | Split by ownership: capture-time controls (T002) vs parser-level controls (T003); T002 stores originals, T003/T005 append derivatives via the append-only interface. |
| PR | Title updated to "5 proposed packets"; body updated to the final ownership. |

Ledger totals: **42 accepted / 9 backlog** (5 M3 proposals + 4 pre-existing) — nothing accepted, moved, claimed, or dispatched.
