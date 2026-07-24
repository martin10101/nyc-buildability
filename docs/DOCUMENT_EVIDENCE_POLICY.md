# Document Evidence Policy — the evidence-state foundation for the M3-T003 evidence engine

**Status:** Canonical policy foundation (task **M3-T001**, D-002 first-wave lane 1; owner directive
2026-07-23, rev-4 §17). This document is the **policy**; the executable Document Evidence Verification
Engine (classification, native/OCR extraction, critical-token detection, cross-source comparison, the
evidence-state machine, and human-review bundles) is built by **M3-T003** and must conform to this policy.
It defines what *evidence about a document* means, why extraction is not legal verification, and the exact
boundary the rule engine may consume.

**Authority boundary (CLAUDE.md principle 1).** AI retrieves, classifies, drafts, and explains.
Deterministic code calculates. Qualified humans approve legal interpretations. The status vocabulary is
defined in [LEGAL_CORPUS_COVERAGE_MATRIX.md](LEGAL_CORPUS_COVERAGE_MATRIX.md) §2; provenance tiers in
[SOURCE_AUTHORITY_POLICY.md](SOURCE_AUTHORITY_POLICY.md) §2.

---

## 1. The three-truths accuracy boundary

There are **three separate questions**. No single OCR engine, PDF parser, AI model, or calculator resolves
all three. Conflating them is the core failure this policy exists to prevent.

| Truth | Question | Who/what can establish it | Who/what **cannot** |
|---|---|---|---|
| **Extraction truth** | What does the official document **visibly state**? | Deterministic extraction with replay to page coordinates + required cross-source reconciliation, or OCR **plus** human confirmation | OCR confidence alone; a single extractor; AI alone |
| **Legal truth** | Does that provision **apply to this property and as-of date**? | A qualified human legal reviewer at **G6**, on top of applicability closure (M3-T004) | Any extractor, parser, OCR engine, or AI; arithmetic |
| **Mathematical truth** | Was the calculation performed **correctly on approved inputs**? | The deterministic calculator (exact decimal/rational arithmetic) on already-approved inputs | Extraction accuracy; OCR agreement; AI |

**Consequence:** getting extraction right does not make a provision *apply*; getting the arithmetic right
does not make the *selected rule* correct; a human's legal approval does not fix a mis-extracted number.
Each truth is established by its own mechanism, and a value is only trustworthy when **all three** are
satisfied by their proper mechanism.

---

## 2. Evidence states are distinct — native, OCR, AI, and human are not interchangeable

An "extracted value" is meaningless without the **state** describing how it was obtained. These are
**different evidence states**, and one never silently substitutes for another:

| Evidence state | What it is | Inherent legal authority |
|---|---|---|
| **Native extraction** | Text/coordinates read from a digitally-born document's own text layer | Inherits the official document's provenance **only after** required evidence verification (§3) |
| **OCR output** | Text recognized from a page image | **None on its own.** Always begins as `ocr_draft`; has **no independent legal authority** |
| **AI extraction** | A model's proposed reading/classification/edge | **None.** A tier-7 proposal (see [SOURCE_AUTHORITY_POLICY.md](SOURCE_AUTHORITY_POLICY.md) §2); a candidate for validation, never an approval |
| **Human legal interpretation** | A qualified reviewer's judgment at G6 | The **only** state that establishes legal truth; recorded separately from extraction state |

**Rules (binding):**

1. **OCR output has no independent legal authority.** A raw or high-confidence OCR read never, by itself,
   promotes a critical legal value. A confidence number is a **model score, not a probability of
   correctness**.
2. **Extracted text inherits the official document's provenance ONLY after required evidence
   verification.** Before verification (§3), an extraction is a *draft observation about a document*, not
   an authoritative statement of what the law says.
3. **Extraction verification is NOT legal G6 verification.** Confirming *what the document says* (extraction
   truth) is a different act from confirming *that the provision applies* (legal truth). Passing extraction
   verification never satisfies G6, and G6 never substitutes for extraction verification. (The full
   evidence-state machine — `raw_captured` → `document_classified` → `native_extracted`/`ocr_draft` →
   `evidence_checked` → `cross_source_matched`/`extraction_conflict` → `human_confirmed`/`rejected`/
   `unsupported` — and its span schema are implemented in M3-T003; there is **no single vague `verified`
   flag**, and legal-review state is tracked on a separate axis.)

---

## 3. When an extraction becomes eligible (not "verified", not "approved")

An extracted field becomes **rule-draft eligible** only when **either**:

- it is **native-extracted with deterministic replay** to page coordinates **and** reconciled against the
  required independent official cross-source (e.g. HTML vs. official PDF), **or**
- it is **OCR-derived AND a qualified human explicitly confirmed** the highlighted source evidence.

**Rule-draft eligibility is not** Published, Verified, compliant, or legally approved. It only means the
extraction is trustworthy enough to seed a *draft* rule that still must pass applicability closure
(M3-T004) and **G6** legal approval. Any disagreement involving a **critical token** (section/chapter
citations, FAR values, percentages, dimensions/areas, dates & effective dates, amendment numbers, decimal
points, negative signs, fractions, units, district names/suffixes, table row/column headings, footnote
markers, and the words *not, except, unless, provided that, more than, less than, at least, no more than,
before, after, and, or*) **blocks automatic eligibility** and yields `extraction_conflict` →
`data_conflict`.

---

## 4. Prohibited claims (grep-enforced; never a system guarantee)

The following claims are **false** and must **never** appear as a system guarantee anywhere in the M3
deliverables. Each line below is a **PROHIBITED** claim, written here only to forbid it. The self-check
harness asserts that any occurrence of these phrases in any M3 deliverable sits on a line explicitly marked
as prohibited (never asserted as a guarantee). (Acceptance AS-12.)

| Marker | Claim that is FALSE and must never be emitted as a guarantee | Why it is false |
|---|---|---|
| PROHIBITED | "100% accurate OCR" | OCR accuracy on a bounded fixture set never proves universal correctness; a score is not a proof |
| PROHIBITED | "100% legally accurate" | Legal accuracy is a G6 human judgment about applicability, not a property of any extractor or calculator |
| PROHIBITED | "OCR confidence proves correctness" | Confidence is a model score, not a probability that the legal value is correct |
| PROHIBITED | "two OCR engines agreed therefore verified" | Agreement of two engines is disagreement-detection only; concurrence is not verification |
| PROHIBITED | "arithmetic consistency proves the extracted rule is correct" | Correct arithmetic on wrong or inapplicable inputs is still wrong; math never proves the selected rule applies |

**System guarantee (the honest statement).** No unverified or conflicting OCR-derived critical value may
enter a Published/Verified rule, a final constraint, a compliance conclusion, or a buildability
calculation. The calculator is only *"mathematically deterministic for its declared inputs"*; legal
correctness still requires source evidence + applicability closure + G6. No claim that bounded-fixture
performance proves universal accuracy is ever made.

---

## 5. Security posture for untrusted documents (policy pointer)

Every document — **including government-hosted PDFs** — is untrusted. Low-level document-safety primitives
are a **shared, domain-agnostic surface**: capture-time controls (approved hosts/redirects, byte/time
limits, MIME/file-signature validation, safe paths, no execution, private/quarantined storage) belong to
**M3-T002**; parser-level controls (page/stream/image/time budgets, sandboxed worker with no unnecessary
network, **no execution of PDF JavaScript/attachments/actions/macros/external references**, crash
isolation, reject encrypted/unsupported unless an approved workflow exists) belong to **M3-T003** where the
parser runs. If extracted text is ever shown to an AI, **embedded document instructions are data, never
control** (prompt-injection isolation). Eligibility policy stays **separate per document domain** (the
legal-document policy here is not shared with a future survey-document policy); only the low-level safety
surface is reused. G5 for M3-T003 must include malicious and malformed PDF fixtures.

---

## 6. Mathematical validation is supporting evidence only

The deterministic mathematical validator (M3-T003 / and the exact-arithmetic foundation in M4-T007) parses
numbers from the original strings, preserves decimal precision, uses **exact decimal/integer/rational
arithmetic (never binary float for legal thresholds)**, normalizes units explicitly, rejects unknown or
incompatible units, and emits an exact formula/unit trace. Verified sample computations (e.g. 40×125 =
5,000; 5,000×1.50 = 7,500; 7,602 − 7,500 = 102; 60%×5,000 = 3,000) demonstrate the arithmetic only.
**Arithmetic consistency is supporting evidence; it never proves that the selected FAR/coverage/yard/branch
applies. No AI-generated numeric value enters the calculator.**

---

## 7. Integration boundary — what the rule engine may consume

The pipeline is: **official source → immutable capture (M3-T002) → evidence verification (M3-T003) →
structured eligible evidence → closure / applicability (M3-T004) → draft rule → G6 human legal approval →
deterministic calculator.**

- **The rule engine never reads raw OCR strings.** It consumes only structured, eligible evidence (§3),
  never a raw extraction or a raw OCR token stream.
- If **any** preceding stage is **missing, unresolved, conflicting, stale, or out-of-scope**, the consumer
  receives one of `missing` / `not_evaluated` / `unsupported` / `data_conflict` /
  `professional_review_required` (vocabulary: [LEGAL_CORPUS_COVERAGE_MATRIX.md](LEGAL_CORPUS_COVERAGE_MATRIX.md) §2).
- The consumer **never** receives a default value, a "nearest" value, `not_applicable`, `compliant`,
  `feasible`, or `buildable` in place of one of those honest states. Downgrading an unknown to a negative
  or a default is the exact failure this boundary forbids.

This boundary is what M3-T003 (evidence engine) and M3-T004 (closure) implement against; this document
fixes the policy they conform to.
