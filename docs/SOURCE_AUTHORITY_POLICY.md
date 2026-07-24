# Source Authority Policy — provenance classification and precedence resolution

**Status:** Canonical policy (task **M3-T001**, D-002 first-wave lane 1; owner directive 2026-07-23,
amendment item 4). Establishes how the platform *classifies the provenance* of a legal or factual source
and, **separately**, how deterministic code *resolves a conflict* between two sources. These are two
different questions and this document keeps them apart on purpose.

**Authority boundary (CLAUDE.md permanent principle 1).** AI retrieves, classifies, drafts, and explains.
Deterministic code calculates. **Qualified humans approve legal interpretations.** Nothing in this policy
authorizes AI to approve a legal interpretation, set a release scope, or declare a rule verified. The
runtime status vocabulary this policy references is defined once in
[LEGAL_CORPUS_COVERAGE_MATRIX.md](LEGAL_CORPUS_COVERAGE_MATRIX.md); the document-evidence states it
references are defined once in [DOCUMENT_EVIDENCE_POLICY.md](DOCUMENT_EVIDENCE_POLICY.md).

---

## 1. Two distinct questions

| Question | What answers it | Where |
|---|---|---|
| **Provenance:** *what kind of source is this, and how much inherent authority does that kind of source carry?* | The 7-tier **provenance classification** (§2). A fixed, source-intrinsic label. | This document |
| **Precedence:** *when two sources speak to the same point and disagree, which one controls for this property, on this date?* | The **precedence-resolution rules** (§3): jurisdiction, legal status, effective/as-of date, amendment/supersession/rescission, scope specificity. | This document |

> **The tier number is a provenance class, not a conflict winner.** A higher tier number never
> "loses" a conflict *because* of its number, and a lower tier number never "wins" *because* of its
> number. Precedence is decided by §3, not by §2. (Acceptance AS-1.)

This distinction exists because a naïve "lower tier always wins" rule produces *wrong law*: an older
consolidated portal page (tier 1 kind) would defeat a later effective amendment (also tier 1 kind, but
newer), and a citywide statute (tier 1) would override a legally effective, property-specific variance
(tier 2) that actually controls the parcel. Both outcomes are legally incorrect. §3 prevents them.

---

## 2. The 7-tier provenance classification

Each tier is a **class of source**, ordered by the *kind* of authority the source category inherently
carries. The tier is assigned by *what the source is*, independent of any particular dispute.

| Tier | Provenance class | Inherent authority of the class | Representative sources |
|---|---|---|---|
| **1** | **Current enacted / adopted official law** | Primary law. Binding text as adopted. | NYC Zoning Resolution (adopted text); zoning maps; NYC Administrative Code & Construction Codes; NYC Local Laws; applicable New York State law |
| **2** | **Official amendments + project-specific legal instruments** | Primary law / legally operative instruments that modify or attach to specific property. | CPC & City Council adopted amendments; BSA variances, special permits, authorizations, certifications; recorded restrictive declarations; zoning-lot development agreements (ZLDA); easements; applicable DOB-approved project documents |
| **3** | **Official agency interpretations** | Persuasive/operative agency guidance interpreting tier-1/2 law; **not itself the statute.** | DOB Rules (RCNY); Buildings Bulletins; DOB Code Notes / directives; formal DOB interpretations (record issuing body, number, date, cited provisions, status, rescission/supersession) |
| **4** | **Official factual datasets** | Establishes *facts* (with stated limitations); does **not** state or replace legal text. | PLUTO / MapPLUTO; ZTLDB; DCP GIS zoning features; DOB NOW / BIS; LPC; FEMA / official flood data |
| **5** | **Third-party references** | **Cross-check only. Never controlling provenance.** | UpCodes and similar consolidations of code text |
| **6** | **Architect / client documents** | Project evidence and claims to be *checked*; **never general legal authority.** | The architect benchmark sheet (see [M3-T001-architect-benchmark-analysis.md](../project-control/reports/M3-T001-architect-benchmark-analysis.md)); client submissions |
| **7** | **AI output** | **No authority.** Retrieves, classifies, proposes extraction edges, drafts tests, explains deterministic results. | Any model-produced classification, extraction, or draft |

**Tier-discipline rules (binding):**

1. **Tier 5 / tier 6 are never controlling provenance.** A third-party reference (UpCodes) or a
   presentation layer (ZoLa) may be used by a human for a manual cross-check only; the machine
   provenance of any resulting fact is the *underlying official source*, never the third-party or the
   presentation layer. The platform adds **no runtime dependency** on either. (Acceptance NC-3; consistent
   with [SOURCE_ACCESS_REGISTRY.md](SOURCE_ACCESS_REGISTRY.md) governance rule 1 and the new
   third-party-reference section.)
2. **Tier 7 (AI) has no authority.** AI may *propose* a provenance classification or a precedence
   relationship; a proposal is not an approval. Every legal interpretation is approved by a qualified
   human through **G6** (see [GATES_AND_CHECKPOINTS.md](GATES_AND_CHECKPOINTS.md)).
3. **A tier-4 factual dataset never establishes a tier-1 legal conclusion.** A PLUTO tax-lot code, for
   example, never establishes a legal Zoning-Resolution lot type or district applicability by itself; it
   is a fact with a stated ±accuracy limitation, and legal applicability is resolved from tier-1/2 text.
4. **Never generalize a project-specific agency determination** (a tier-2 variance/special permit or a
   tier-3 property-specific interpretation) **to a different property** without an approved legal
   interpretation.

---

## 3. Precedence resolution — how a conflict is actually decided

When two sources address the same point and disagree, deterministic code resolves precedence by
evaluating the following factors **in the order given**. The provenance tier (§2) is context, **not** the
deciding factor.

### 3.1 Ordered resolution factors

1. **Jurisdiction.** Does the source actually govern this property's location and subject matter? A source
   that does not have jurisdiction over the point is not a competing authority at all.
2. **Legal status.** Is the source *adopted/effective law* (tier 1/2), an *agency interpretation*
   (tier 3), a *fact* (tier 4), or a *reference* (tier 5)? A factual dataset or a third-party reference
   never overrides adopted legal text on a question of law; it can only surface a possible conflict for
   review.
3. **Effective / as-of date.** Among sources of the same legal status, the one **in force for the
   property's applicable as-of date** controls. A later effective amendment supersedes earlier text as of
   its effective date; a repealed or not-yet-effective provision does not control.
4. **Explicit amendment / supersession / rescission.** An adopted amendment that expressly modifies,
   supersedes, or rescinds a provision controls over the superseded text. A rescinded Bulletin or
   interpretation no longer controls.
5. **Scope specificity.** A legally effective, property-specific instrument (variance, special permit,
   restrictive declaration, zoning-lot agreement) **may control the affected property** even though it is
   narrower than citywide law — *within the exact scope the instrument grants and no further.*

### 3.2 Consequences that the rules must produce

- **An adopted amendment becomes part of current law.** An older consolidated portal page (or an older
  snapshot, or a stale third-party consolidation) does **not** defeat a later effective amendment merely
  because it was encountered first or sits on a "tier 1" page. The newer *adopted* text controls as of its
  effective date. (Acceptance AS-8.)
- **A legally effective project-specific instrument may control the affected property.** A BSA variance or
  a recorded restrictive declaration can control this parcel against the more general citywide rule —
  scoped strictly to what the instrument covers. It is never generalized to another property. (AS-8.)
- **The seven tiers do not rank conflicts.** Two tier-1 sources can conflict (old vs. new adopted text);
  the resolution is by effective date and supersession (§3.1 factors 3–4), not by tier. A tier-2
  instrument can control over tier-1 citywide law within its scope (factor 5). (AS-1/AS-8.)

### 3.3 Unresolved precedence — fail visible, never silent

If, after applying §3.1, precedence or applicability **remains unresolved** — competing effective
instruments, an ambiguous effective date, an unresolved amendment, or a genuine question of legal
applicability — the deterministic result is:

- **`conflicting`** → surfaced to the runtime as **`data_conflict`** (identify both sources + versions,
  list the affected rules, block publication of any dependent value), **or**
- **`professional_review_required`** when the resolution needs qualified-human legal/design judgment.

**Never silently select a source. Never pick the "nearest", "newest-looking", or "highest-tier" option to
avoid returning a conflict.** The mapping of these statuses to runtime outcomes is defined once in
[LEGAL_CORPUS_COVERAGE_MATRIX.md](LEGAL_CORPUS_COVERAGE_MATRIX.md) §2. (Acceptance AS-8/AS-9.)

### 3.4 AI's role in precedence

AI (tier 7) **may propose** a precedence relationship — "this /recently-adopted entry appears to amend
§23-361 effective 2026-05-20" — as a *candidate for verification*. AI **never approves** the relationship
and never resolves a legal conflict. The proposal is validated by deterministic checks and, where it
carries legal meaning, approved by a qualified human at **G6**. An AI-proposed edge that is not yet
validated cannot produce a final value; the consumer receives `not_evaluated` or
`professional_review_required` until closure. (Cross-reference closure and edge validation are M3-T004;
the consumer boundary is [DOCUMENT_EVIDENCE_POLICY.md](DOCUMENT_EVIDENCE_POLICY.md) §7.)

---

## 4. Worked micro-examples (illustrative; not an answer key)

These illustrate the rules; they are **not** legal conclusions about any property and emit no
buildable/compliant claim.

1. **Old consolidated page vs. later amendment.** A consolidated PDF snapshot dated 2026-01 shows one
   §23-xx text; a `/recently-adopted` entry adopts an amendment effective 2026-05-20. Both are tier-1
   *kind*. Resolution: factor 3 (effective date) + factor 4 (express amendment) → the **amendment
   controls as of 2026-05-20**; the older page does not win on tier number. If the effective date cannot
   be established from official evidence → `professional_review_required`.
2. **Citywide rule vs. property-specific variance.** Citywide §23-xx (tier 1) sets a yard requirement; a
   recorded BSA variance (tier 2) grants relief for this exact lot. Resolution: factor 5 (scope
   specificity) → the **variance controls this parcel** within the granted relief; it is **not**
   generalized to neighboring lots.
3. **Third-party reference disagrees with adopted text.** UpCodes (tier 5) shows a value differing from
   the adopted ZR text (tier 1). Resolution: factor 2 (legal status) → the **adopted text is the
   authority**; the third-party disagreement is recorded as a cross-check signal and, if it touches a
   critical value, raised as `data_conflict` for official reconciliation — **UpCodes is never recorded as
   the controlling provenance.** (NC-3.)
4. **Dataset fact vs. legal lot type.** PLUTO (tier 4) carries a tax-lot code; the legal ZR lot type
   (corner/interior/through, §12-10) is a legal question. Resolution: factor 2 → the **dataset fact does
   not establish the legal lot type**; unknown legal lot type is `unsupported` /
   `professional_review_required`, **never `not_applicable` or `false`.**

---

## 5. Relationship to gates and downstream harnesses

- This policy **defines**; it does not execute. It fixes the provenance classes and the precedence
  factors that downstream harnesses (source-fidelity, cross-reference-closure, lot/applicability,
  rule-behavior, architect-benchmark, consumer-boundary) assert against.
- **G1** independently verifies source identity/access before any channel is treated as usable
  (see [SOURCE_ACCESS_REGISTRY.md](SOURCE_ACCESS_REGISTRY.md)); an unresolved source identity is
  **BLOCKED at G1**, never accepted as verified.
- **G6** remains mandatory before any rule sourced from this corpus is Published or Verified. B-011
  (construction-code release scope, [CONSTRUCTION_CODE_RELEASE_SCOPE.md](CONSTRUCTION_CODE_RELEASE_SCOPE.md))
  is a product/release-scope decision and is **independent of G6**; scope approval is not legal approval.

## 6. Change discipline

This document changes only with cited evidence and through the controlled-task lifecycle. The 7 tiers and
the 5 precedence factors are the stable interface other M3 tasks depend on; a change to either is a
material replan, not an edit.
