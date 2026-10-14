# M3-T006 reviews (every return kept unchanged)

- G1 data-contract-verifier: FAIL at 71a03977 (REQUIRED F1: options-frontier sections silently dropped cross-references; advisories A1-A3); producer rework 1 (cherry-pick 12663e29); delta review by the same reviewer: PASS at 12663e29 (zero dropped references; A1-A3 resolved).

Every reviewer is an AI agent; none is a human or professional review.

## G1

G1 REVIEW — M3-T006 (zoning-law library, documents only) — data-contract-verifier, read-only, at pinned head 71a039776 (/root/project/w-wave20). Independent of producer.

VERDICT: FAIL (one REQUIRED finding; 7 of 8 scenarios + both recorded discrepancies independently verified PASS; remediation is bounded).

=== REQUIRED ===
F1 (S2 closure — silently dropped cross-references + overstated "Followed"). My script over benchmark-r6b-sections.json + docs/research/zr-snapshots/v1/ parsed the verbatim_excerpt of all 68 captured sections and extracted every \d{2}-\d{2,3} reference. The five brief-named sections are perfect: 23-344→{23-342,23-343}, 23-432→{23-433}, 34-24→{34-11,35-62,35-63,35-71,36-64}, 35-632→{23-43,23-432,23-433,23-434,23-435}, 23-363→{23-361,23-362,23-342,23-343} all match cross_references_out exactly. BUT 11 options-frontier sections (Art 32 use, Art 33 overlay FAR, Art 25 parking) have empty/partial cross_references_out and silently drop real ZR references present in their snapshot text, absent from the entire library: 32-131/32-161 drop "Section 32-10 (USE ALLOWANCES)"; 33-12 drops 33-13/33-14/33-15/33-16; 33-121 drops 74-902/74-903; 35-31 drops 35-36; 25-211 drops 73-432/75-31; 25-221 drops 73-432/74-52; 25-212/222/232 drop 25-63; 25-231 drops 74-52. (44-45, 48-49, 51 in 32-161 are NAICS sector numbers = correctly not refs.) grep confirmed 32-10, 33-13..16, 74-902/903, 35-36, 73-432, 75-31, 74-52, 25-63 appear in ZERO library files; none is marked out-of-scope. Yet cross-reference-closure.md ("What was followed vs out of scope") lists "the options frontier above" under "Followed (captured, in scope)," overstating completeness and contradicting the file's own rule "recorded, never silently dropped" — this undercuts the library's stated purpose (stop missing rules), and several dropped refs are on-point (32-10 use allowances for option 5; 73-432/75-31/74-52 parking-removal special permits for option 10's waiver). This violates S2 ("none is silently dropped"). Bounded fix: add these refs as entries or cross_references_out with captured=false + an out-of-scope reason, and correct the "Followed" summary to exclude the options frontier's un-followed internal references. The core R6B base-envelope + overlay closure is complete and accurate.

=== ADVISORY ===
A1 (coverage §2). 34-113 is coverage_status=not_applicable, but whether the benchmark lot ever received a floor-area bonus is an unresolved property fact; matrix §2 rule 1 reserves not_applicable for affirmatively-resolved applicability (the producer correctly used not_evaluated for 23-44/35-64 special areas). Recommend not_evaluated for 34-113. The other four not_applicable (23-435 towers, 23-42 R1-R5, 34-112 other C-districts, 35-62 R1-R5 equiv) are definitionally resolved by the R6B/C2-2 designation — fine.
A2 (epoch precision). I converted rowsUpdatedAt 1790020601 = 2026-09-21T19:56:41Z UTC (not the "Jan 17 2025" the fetch model rendered; that epoch would be 1737072000). Socrata metadata for yvxd-uipr returns exactly 1790020601, name "Board of Standards and Appeals (BSA) Applications Status", attribution BSA, 25 columns — all matching the library. Producer wrote "~2026-09-20" (off ~1 day); recommend recording 2026-09-21.
A3 (BB 2014-025). Official 2016 index: BB 2016-013 rescinds 2014-025 "because NYS General City Law (GCL §36) was recently amended" — the library frames 2014-025's topic as "unmapped streets." Already marked RESCINDED + "confirm the live rule," so no action; note the rescission rationale is a GCL amendment.

=== VERIFIED PASS ===
S1: re-derived independently — all 98 captured entries (68 sections+30 terms) have a snapshot file whose stored content_digest_sha256 equals the entry's AND equals sha256(verbatim_excerpt) (checked 11-25, 23-432, 23-344, 12-10-street-wall, 34-24 recompute); snapshot_id fields consistent; no duplicate id refs; the 5 NOT CAPTURED sections (24-11, 24-111, 23-154, 77-00, shared-housing) and 8 NOT CAPTURED terms have no snapshot file. counts block exact (73/68/5/6/67/38/30/8).
S3: each R6B-applicable ruleset's applicability + citations[] read directly — r6_r12_residential_far(in_set incl R6B→23-22), r6b_qualifying_housing_far→23-22, r6b_dwelling_units→23-52/23-52(b)/11-25, r6b_lot_coverage→23-362/11-25, r6b_rear_yard_corner_waiver→23-344(a)/11-25, r6b_height→23-432 ONLY. r6b_height.computation mentions 23-432 only; 23-431 appears solely in exceptions, 23-433 in description/exceptions/limitations — producer's "handles 23-432 only" correction CONFIRMED; benchmark records 23-431/23-433/23-335/23-342/23-343/23-363/23-434 as NOT HANDLED/not_evaluated. r6_r7_r8_wide_street_conditional_far applies to R6/R7-1/R7-2/R8 (not R6B), correctly excluded. handled=6 correct. coverage_status values (partial/not_evaluated/not_applicable/missing) all in matrix §2 vocab.
S4: ELEVEN_OPTIONS (options.py:22-33) order matches options-sections.md 1-11 exactly, none skipped; spot-checked options 1/5/10 section roles against snapshot section_titles (23-22 FAR, 23-432 height, 23-362 lot coverage, 32-131 UG III, 32-161 UG VI, 33-121 overlay FAR, 25-20 required residential parking, 25-22 Outer Transit Zone, 66-11 Definitions) — all consistent.
S5: every pitfall row cites number/date/status + link; both rescinded bulletins (2014-025, 2009-030) marked RESCINDED with superseder; determinations + BSA sections carry the project-specific/never-generalized caveat. Opened 3 official index pages: BB 2019-009 (10/9/2019, mechanical/unused-space ZFA) ✓, BB 2016-013/011/012 ✓, yvxd-uipr Socrata metadata ✓.
S6: research-log.md rows carry source/query/result/missing/next-step across producer+H1/H3/H4/H6; access blocks (bulletin PDFs 716KB binary, DCP handbook >10MB+403, districts-tools 403, 23-154 403) recorded, never evaded.
S7: git diff-tree 71a039776 = only the 7 docs/zoning-law-library/* files + project-control/reports/M3-T006-producer-report.md; no snapshot/registry/coverage-matrix/report-lane file. (Worktree has unrelated uncommitted M5-T168/state.json changes — NOT part of this commit.)
S8: unreviewed-draft/ADR-007 label in all 7 files; "Verified/compliant/buildable/feasible" occur only inside prohibitions/negations; tax-lot≠zoning-lot stated (README; pitfalls BB 2020-003); "an index entry never stands for the instrument" stated.
Discrepancy 1 (NB-06 vs zr-12-10): CONFIRMED — NB-06 rev 2 line 254 says the 12-10 wide/narrow definitions are "NOT captured in the repository snapshot set," but zr-12-10.snapshot.json (section_title "Definitions - wide street and narrow street") contains "wide"/"narrow"/"75 feet", digest 23a9ccad… recomputes from verbatim. Producer correctly recorded without editing NB-06 (read-only). Conflict preserved (D-093).

=== COULD NOT CHECK ===
- Verbatim bulletin PDF bytes and individual BSA resolution PDFs (nyc.gov bot wall / project-specific; brief forbids evading) — relied on official index pages + the project-specific caveat; did not independently confirm each BSA calendar number.
- Did not re-fetch all ~68 captured ZR sections live (used repository snapshots as the captured primary sources, per brief); verified digests are internally honest.
- ZR 23-154 (UAP), 24-11/24-111, 77-00, shared-housing section numbers remain NOT CAPTURED/unresolved — correctly left unresolved by the library.

END-OF-REPORT

G1 DELTA REVIEW — M3-T006 at 12663e299 (data-contract-verifier, read-only). Re-ran my own checks against the rework commit.

VERDICT: PASS.

F1 (prior REQUIRED FAIL) — RESOLVED. I re-extracted every \d{2}-\d{2,3} reference from the verbatim_excerpt of all 68 captured sections (git show 12663e299:…benchmark-r6b-sections.json; snapshots from disk, unchanged) and compared to each entry's cross_references_out. Zero silently dropped references. The only residual is 32-161 → {44-45, 48-49}; I checked the surrounding text: "retail trade sector (sectors 44-45) of the 2022 North American Industry Cl…" and "transportation and warehousing sector (48-49), information sector…" — genuine NAICS 2022 sector codes, correctly excluded. The NAICS exclusion hides no real ZR reference: the ref I previously flagged in Article-32 (32-10 USE ALLOWANCES) is now recorded in both 32-131 and 32-161. All previously-dropped refs are now present with a reason: 33-12→33-13/14/15/16; 33-121→74-902/74-903; 35-31→35-36; 25-211→73-432/75-31; 25-221→73-432/73-433/74-52; 25-231→73-433/74-52; 25-212/222/232→25-63. Totals reconcile exactly: 162 cross_references_out entries = 104 followed (have their own catalog entry) + 58 not followed; all 58 not-followed entries carry a reason (0 missing). The counts block now records cross_references_recorded:162 / followed:104 / not_followed:58.

"Followed" summary — CORRECTED. cross-reference-closure.md now reads "Followed (captured, in scope, with its own section entry)" and adds an explicit block (lines 85-92): "Options-frontier sections: captured, catalogued — but their onward internal references are NOT all followed," listing 32/33/35/25-xx and stating they are recorded in cross_references_out with a reason and not followed to their own entry this first pass. Overstatement removed.

A1 — RESOLVED: 34-113 coverage_status now not_evaluated (not_applicable count 5→4).
A2 — RESOLVED: research-log records "1790020601 = 2026-09-21T19:56:41Z" and flags the fetch model's "Jan 17 2025" (epoch 1737072000) as wrong — matches my independent conversion exactly.
A3 — RESOLVED: pitfalls BB 2014-025 row now states rescinded by BB 2016-013 (8/24/2016) because NYS General City Law §36 was amended.

S7 — HOLDS. Commit 12663e299 alone (git diff-tree) touches only the 5 changed docs/zoning-law-library/* files + project-control/reports/M3-T006-producer-report.md. The extra files in the cumulative 71a039776..12663e299 range are disjoint peer commits (M5-T163/164/168, D-094 verification) — not this task; task identity is byte-stable.

S1 — STILL HOLDS. All 98 captured entries (68 sections + 30 terms) match their snapshot-file digests; 13 NOT CAPTURED; zero errors.

No remaining REQUIRED or ADVISORY findings.

END-OF-REPORT
