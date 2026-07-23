# M3 Legal-Corpus Replan — Control-Only Package (for owner approval)

**Author:** orchestrator (main session) · **Date:** 2026-07-23 · **Branch:** `control/M3-corpus-replan-2026-07-23`
**Directive:** owner directive 2026-07-23 (repair the missing M3 legal-corpus dependency before any M4-T007+ yard/coverage work; §11-25 correction; architect benchmark; construction-code scope; deterministic completeness harnesses).
**Status of this package:** PROPOSAL, **revision 3** (owner corrections applied in-branch to PR #93 — see §15 rev-2 and §16 rev-3 amendment logs). No producer is dispatched. M4-T007/T008/T009 are NOT contracted, claimed, or started. The 3-way vs 4-way split is preserved as a downstream candidate and NOT decided here. Nothing merges to `main` until you approve.

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
- **M4 summary said "0/5"** but the ledger holds **M4-T001…T006** (six tasks). **Fixed in this PR** to "0/6" with the M4-T006 R5 height/setback family noted, and M4-T007's new dependency on accepted M3-T003 recorded.
- **All M4-T001…T006 + M5-T001 are `awaiting_gate`** — merged DRAFT (`needs_review`), **none accepted, Published, or Verified**. G6 gates the chain.
- Checkpoint is **CP-0031**; **CP-0032 remains reserved** for M0-T019 (not created here).
- Open blockers: **B-001** (Supabase management token → durable object storage; **now amended to affect M3-T002 & M3-T004** — see §15/§10A), **B-004** (Geoclient key), **B-010** (client R5 benchmark sheet absent from repo), and **B-011** (new — owner-approved construction-code release scope; gates M3-T004 readiness, see §10B).

**After this PR (control-only):** 42 accepted (unchanged) / 8 awaiting_gate / **8 backlog** (4 new M3 proposals) / 2 blocked / 1 claimed.

---

## 2. Immediate decision (directive §2)

The current 3-way footprint proposal (PR #91) is **not approved for implementation**. The downstream slices (coverage; rear/rear-equivalent; front/side) remain **candidates**; their exact boundaries must be **regenerated after the cross-reference closure graph (M3-T003) identifies the complete reachable section set.** A section list assembled by hand from one chapter is not sufficient evidence of completeness.

`/replan-project` was invoked because the owner supplied new authoritative source requirements, a client architect benchmark, a newly identified legal dependency (§11-25), a construction-code coverage requirement, and a requirement for deterministic completeness/self-check harnesses. This package is the replan output.

---

## 3. Corrections to the current legal analysis (directive §3)

### 3A. District suffix inheritance — ZR §11-25 (CORRECTION)

ZR §11-25: regulations applicable to a district designation apply to that designation **with a suffix** unless the Resolution provides separate express provisions. Therefore:

- **Do not** classify bare "R5" applicability as inherently ambiguous.
- If a section lists R5 and does **not** list separate suffix provisions → **model §11-25 inheritance** (R5A/R5B/R5D inherit).
- If the same section **expressly** lists different R5A/R5B/R5D provisions → those **express provisions control**.
- Preserve explicit exclusions such as §23-422's "except R5 Districts with a letter suffix."
- **§11-25 is added to every relevant rule's closure manifest and tests** (M3-T003 harness AS-1/AS-2/NC-3).

This corrects the earlier tendency to treat bare-R5 as ambiguous by default. It is the canonical test pair for M3-T003: §23-361/R5B **inherits** via §11-25; §23-422 **excludes** suffixed R5.

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

Do not call a modifier "confirmed absent" merely because it was not found in Article II Chapter 3. Absence may be asserted **only** if the declared search universe and cross-reference closure are complete (M3-T003). Otherwise use **`unsupported`**, **`not_evaluated`**, or **`professional_review_required`.**

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
| Definitions & interpretation (§12-10, §11-25) | missing | ZR text (closure) | — | M3-T003 | applicability / suffix scope | closure graph (qa-engineer) |
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

See §3A. §11-25 suffix inheritance is (a) a required correction to the current analysis, (b) an M3-T003 graph edge type, (c) a closure-manifest entry for every relevant rule, and (d) harness cases AS-1/AS-2/NC-3. The §23-422 express exclusion is preserved as the counter-case.

---

## 12. Revised recommendation — 3-way vs 4-way (directive §9)

**Recommendation: do not fix the number now; regenerate the slice boundaries from the M3-T003 closure set, and expect 4-way (or more) to be the floor, not 3-way.**

Rationale:
- The current 3-way grouping (coverage / rear+rear-equivalent / front+side) was assembled from a manual chapter reading. The owner's §11-25 correction and the §12-10 lot-taxonomy correction both change which sections are reachable and how R5A/R5B/R5D scope, so the *inputs* to the split decision are not yet stable.
- Front and side yards have **different** applicability drivers (side-yard count depends on building type — detached/semi-detached/zero-lot-line/attached — and may require two yards; front-yard depth interacts with the §23-423 setback offset with its 7-ft floor). Bundling front+side risks hiding a building-type branch, which is exactly the failure the benchmark (§3C item 5) exposes.
- Therefore the **4-way split** (T007 lot coverage → T008 rear + rear-equivalent → T009 front → T010 side) is the more honest **lower bound**; the closure graph may reveal a further split (e.g. open-space/FAR-interaction, or building-type-specific side-yard sub-rules).

**Concrete proposal:** keep the 4-way split as the working candidate, but **contract its exact boundaries only after M3-T003 is accepted**, when the reachable controlling-section set and the §11-25/§12-10 predicates are known. Until then M4-T007+ stays uncontracted, dependent on accepted M3-T003.

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
