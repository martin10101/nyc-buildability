# M4-T017 G1 gate report — independent data-contract review (verbatim reviewer return)

Recorded by the orchestrator from the independent reviewer's return (reviewer != producer;
reviewer read-only, landed with pinned review HEAD confirmed). Corrections F5/F6 were applied
as tagged ORCH-CORRECTED rework immediately after this verdict; the delta-attestation from the
same reviewer covering those two edits is appended at the end.

---

**Reviewer:** data-contract-verifier (independent; not the producer)
**Task:** M4-T017 — D-045-R005 C-district research (research-only)
**Deliverable:** `project-control/reports/M4-T017-c-district-research.md`
**Pinned review HEAD:** `git rev-parse HEAD` = **939ca72bd7b7d5d374d023eb8c98b0cb161ff041** — MATCHES the pinned review head. Confirmed.

## VERDICT: PASS (with two required corrections, blocking before any C-district build packet pins this report)

Every source citation the report makes is byte-exact against the current live official source
(`zoningresolution.planning.nyc.gov`, retrieved 2026-09-13, same-day as the producer).
Interpretation discipline (S4) and scope (S5) are clean. Two non-fatal findings are recorded as
required corrections; neither is a data-contract accuracy defect.

## Findings

**F1 — S1 commercial-FAR map, byte-exact citations — PASS (with sub-finding F5).**
Method: live WebFetch of the HTML section pages the report cites.
- §33-12 title "Maximum Floor Area Ratio" — byte-exact. Opening rule "In all districts, as
  indicated, for any zoning lot, the maximum floor area ratio shall not exceed…" — byte-exact.
  Exception list 33-13/33-14/33-15/33-16 — exact. "…by more than 20 percent" sentence — exact.
  Last Amended 12/5/2024 — exact.
- §33-121 title "In districts with bulk governed by Residence District bulk regulations" —
  byte-exact. Opening rule byte-exact. Table structure (3 columns A=commercial-only,
  B=community-facility-only, C=both; keyed by underlying Residence District) — exact.
  Spot-checked rows: R1 R2 → 1.00/0.50/1.00 (exact), R9A → 2.00/7.50/7.50 (exact),
  R10 → 2.00/10.00/10.00 (exact). R8B footnote (CD8 Manhattan, 5.10) — byte-exact. Applies to
  C1-1..C1-5 / C2-1..C2-5 — exact.
Severity: none (PASS). See F5 for the standalone-half gap.

**F2 — S2 §34-111 overlay governing-rules quote — PASS.**
Method: live WebFetch of the 34-111 page.
- Title "Residential bulk regulations in C1 or C2 Districts whose bulk is governed by
  surrounding Residence District" — matches (live render shows "Cl" as an OCR/font artifact of
  "C1"; not a report defect). Last Amended 12/5/2024 — exact. Applies to C1-1..C1-5 /
  C2-1..C2-5 — exact.
- Exception (a) qualifying residential sites in the Greater Transit Zone mapped in R1–R5 → R5
  without letter suffix — confirmed. Exception (b) non-qualifying sites in R1/R2 → R3-2 —
  confirmed. Closing "…apply for the purposes of applying the provisions of Article II,
  Chapter 3…" — confirmed.
- Report correctly locates the overlay commercial FAR cap in a separate section (§33-121), and
  states the mixed-lot consequence as an explicit build requirement (§3.3: two separate
  evaluations, never substituted). S2 fully satisfied.
Severity: none (PASS).

**F3 — S3 §34-112 equivalents table — PASS (strong).**
Method: live WebFetch pulling the full table.
- Title "Residential bulk regulations in other C1 or C2 Districts or in C3, C4, C5 or C6
  Districts" — byte-exact. Establishing sentence verbatim — confirmed. Per-district lookup
  table (not name-pattern inference) — confirmed.
- **All 20 displayed rows match byte-exact**, including the load-bearing correction:
  **C4-6 → R10** (report explicitly corrects RQ-002's illustrative "C4-6 → R7" guess).
  Additional verified rows: C3 → R3-2; C4-1 → R5; C1-6/C2-6/C4-4/C4-5/C6-1 → R7-2;
  C1-7/C4-2F/C4-8/C6-2 → R8; C1-8/C2-7/C4-9/C6-3 → R9; C6-4X → R10X; C4-11/C6-11 → R11;
  C4-12/C6-12 → R12; C5 in the R10 row. No transcription discrepancy found in any row.
Severity: none (PASS). Well exceeds the ≥4-row spot-check requirement.

**F4 — S4 interpretation discipline — PASS.**
Method: full read of report §8 + DRAFT-language scan.
- Five open questions (OQ-1..OQ-5) recorded and routed; none resolved in-task. OQ-1
  (wide-street interaction) and OQ-5 (rule-architecture) routed to the architect doc / D-048.
  OQ-3 (33-121 Col B/C R9A = 7.50 vs. residential-rule R9A standard_far) is flagged as a
  **fact to verify, not adjudicated** — the report explicitly declines to decide whether it is
  a genuine two-provision difference or a drafting inconsistency. DRAFT-until-G6 posture
  preserved throughout. No place silently decides a provision's meaning.
- Reviewer independently confirmed the OQ-3 factual premise:
  `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json` sets
  `standard_far_by_district["R9A"] = 7.52`, and live §33-121 Col B/C for R9A = 7.50. The
  divergence the report flags is real and correctly characterized as a fact, not an error.
Severity: none (PASS).

**F5 — S1 completeness gap: standalone commercial FAR (§33-122/§33-123) not evidenced verbatim
— MEDIUM (required correction).**
Method: live WebFetch of 33-122 and 33-123.
- Live confirms the report's structural characterization is accurate: §33-122 "Commercial
  buildings in all other Commercial Districts" (commercial-only FAR, keyed by commercial
  district code, 0.50→15.00, Last Amended 12/5/2024); §33-123 "Community facility buildings or
  buildings used for both community facility and commercial uses in all other Commercial
  Districts" (keyed by commercial district code, 12/5/2024).
- **The report identifies §33-122/§33-123 by number and describes their structure correctly,
  but does NOT give their exact titles, verbatim opening quotes, or district-by-district FAR
  values** in the report body — even though the D-045-R005 objective bullet (1) calls for
  C1–C8 commercial FAR "with district-by-district values evidenced," and evidence-item E1
  (node 17721) is stated to include 33-122/33-123. The report defers these to build-family-2
  (§9). Additionally, §1 claims all four parts are "Answered in sections 3-6 below, each with
  section number, exact title, verbatim quote" — this over-claims relative to what is
  delivered for the standalone half, and the honest-limitations section (§7) does not disclose
  this deferral.
- This is a completeness/honesty gap, NOT an accuracy defect: everything the report does state
  about 33-122/33-123 is correct and independently confirmed.
Severity: MEDIUM. Required correction (blocking before build family 2 pins this report):
either (a) extend the report to capture §33-122/§33-123 exact titles + district-by-district
values verbatim, or (b) add an explicit honest-limitation recording the deferral and correct
the §1 completeness claim so the standalone half is stated as structural-only. The C1–C8
standalone commercial FAR values (C1-6+/C3–C8, the majority of C-districts by count) are
otherwise unpinned for downstream build work.

**F6 — Row-count miscount — LOW (required correction).**
The report/metadata state "19 rows" for both the §33-121 overlay table (§9 family 1) and the
§34-112 equivalents table (§9 / evidence-map / orchestrator log), but each displays 20 rows.
Cosmetic; contents are byte-exact. Correct the count.

**F7 — S5 research-only scope — PASS.**
Method: `git show --stat 46a8a110` and `git show --stat 9fe63924`.
- Producer commit `46a8a110` and its cherry-pick `9fe63924` each touch **exactly one file**:
  `project-control/reports/M4-T017-c-district-research.md` (440 insertions, 4 deletions — the
  4 deletions are the prior placeholder lines; still a single file). No code/schema/fixture/
  dependency change. Working-tree status shows only untracked agent-memory + scratchpad (not
  part of this deliverable). S5 satisfied.
Severity: none (PASS).

**F8 — Provenance discipline — PASS.**
- Every material claim carries a live official URL + retrieval date (2026-09-13). Evidence
  index (§6, E1–E7) records node ids, URLs, byte-size, and raw-PDF sha256 for E1–E6.
  Thin-client respected (KB-scale per-section PDFs, no bulk download). Search/HTML used only
  for discovery (E7); every substantive claim is grounded in a byte-read capture, not
  search-summary text. Retrieval-extraction failures ("binary, cannot extract") recorded
  honestly with the successful fallback. No claim is sourced from memory.
Severity: none (PASS). Note: reviewer verified the citations against the live HTML section
pages (same current official text), independently corroborating the report's PDF-channel
captures; the recorded sha256 over raw PDF bytes was not recomputed (the PDFs are
session-scratch, not committed — expected per allowed_paths).

**F9 — Honest-limitations adequacy re: image-rendered §33-121/§33-122 (mandate point 7) —
ADEQUATE.**
- §7 item 6 flags that node 17721's 33-121/33-122 tables came from an image-rendered
  (rasterized) PDF transcribed by direct visual reading, carries higher transcription risk
  than the text-layer PDFs (34-112/11-25/11-121), and must be spot-checked again by the first
  build task that codes a 33-121/33-122 numeric value. This flag is adequate: it is specific,
  names the affected sections, and prescribes a fail-closed downstream check. Reviewer
  independently de-risked it in part — the §33-121 rows checked (R1 R2, R9A, R10) and the
  footnote match the live source byte-exact — so the image-render channel produced no error in
  the sampled rows. The flag does NOT demand a FAIL.
Severity: none. See advisory A1.

## Advisories for the build packets

- **A1 (build family 1, §33-121):** Before coding any §33-121 numeric value, spot-check the
  overlay rows not independently verified against a text source — notably R7A (4.00*), R7D
  (4.66), R6 R6-1 R7-1 (4.80), R8X (6.00), R7-2 R7-3 R8 R8A (6.50), R9 R9-1 (10.00), R11
  (12.00), R12 (15.00) — because these came from the image-rendered node-17721 PDF (per F9).
- **A2 (build family 2, §33-122/§33-123):** These standalone commercial-FAR tables are the
  report's weakest-evidenced surface (F5). Capture their full district-by-district values
  verbatim from a text source in the family-2 research step; do not rely on this report for
  those numbers.
- **A3:** The §33-12 carve-outs (a)–(d) (contextual bonus prohibition; CB7 Manhattan
  R10-equivalent 10.0 cap; C6-1A +50%; C6-4X plaza-only) were not independently byte-verified;
  the §33-12 opening rule was. Verify before encoding.
- **A4:** OQ-3 (R9A 7.50 vs 7.52) and OQ-1 (wide-street interaction) are correctly routed to
  architect review; the build family must not silently resolve either.

## Summary

G1 data-contract discipline is sound: 33-12, 33-121, 34-111, 34-112, 33-122, 33-123
titles/quotes/structure and the full 34-112 equivalents table (incl. the C4-6→R10 correction)
all verified byte-exact against the current live official source; provenance, thin-client, and
interpretation discipline are clean; S5 single-file scope confirmed at the pinned HEAD.
Verdict **PASS** with two required corrections — F5 (standalone §33-122/§33-123 values
unpinned + §1 over-claim; MEDIUM, blocking before build family 2 pins this report) and F6
(20-vs-"19" row miscount; LOW) — recorded per the project-control "PASS with required
corrections" semantics for the orchestrator to track.

---

## Delta-attestation (appended by the orchestrator upon reviewer confirmation)

Received from the same reviewer (data-contract-verifier), verbatim:

> Delta verified. The `git diff 939ca72b 7c2761c2` over my two attestation-surface files shows
> exactly four changes and nothing else:
>
> 1. **§1 sentence (F5 option b)** — now discloses the standalone 33-122/33-123 half as
>    structural-only with district-by-district values deferred to build family 2, tagged
>    `[ORCH-CORRECTED per G1 F5]`. Satisfies the §1 over-claim half of F5.
> 2. **§7 new item 7 (F5)** — records the deferral and requires family-2 verbatim capture
>    before any 33-122/33-123 value is coded, citing advisory A2. Satisfies the
>    honest-limitation half of F5.
> 3. **§9 family-1 line (F6)** — "19 rows" → "20 rows [ORCH-CORRECTED per G1 F6: was 19]" for
>    the 33-121 table.
> 4. **evidence-map JSON (F6)** — "19 rows" → "20 rows per the G1 F6 count correction" for the
>    34-112 table.
>
> None of the content I verified byte-exact at 939ca72b changed: every verbatim quote (33-12,
> 33-121, 34-111, 34-112, 33-122/33-123 structure), the full 34-112 equivalents table (incl.
> C4-6→R10), the OQ set, and the provenance index are untouched. The edits are additive
> corrections only. The out-of-scope additions in 7c2761c2 (the recorded gate report,
> M4-T016's evidence map, the M4-T016 cherry-pick) are correctly outside my scoped diff and
> outside my attestation surface.
>
> ## ATTESTED
>
> Both required corrections (F5 and F6) are satisfied at
> **7c2761c2913f1809e4c923866c591b0e13716aa6**. My PASS verdict carries to this identity.
> Advisories A1–A4 remain standing guidance for the build packets (they were advisory, not
> blocking, and are unaffected by this delta).
