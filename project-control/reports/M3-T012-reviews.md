# M3-T012 reviews (every return kept unchanged)

- One producer round (official-source-researcher, worktree): commit a9dc02c8 integrated as the cherry-pick 8891fb99 (5 files, inside the allowed paths; LF sha256 equal to the producer's return). The record was placed byte-identical to the planner's validated draft (return-plan-record-NB-07.md), re-verified field by field.
- G2 orchestrator self-check at the submit head: the task's files equal the producer's digests; nothing outside the allowed paths; research_record_check PASS; the CI run at the submit head read green before submission.
- G1 data-contract-verifier at 8891fb99: PASS (the official sources re-opened; three advisories: a disclaimer excerpt paraphrased; MapPLUTO's per-feature Version 26v2 does stamp the release; the landing page is not byte-stable). No correction required.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

G1 DATA-CONTRACT GATE REPORT — M3-T012 (NB-07 MIH/IH status; two index lines; NB-05 DB-274 half)

Reviewer: data-contract-verifier (independent, READ-ONLY). I am an AI agent; this is not a human or professional review. Pinned reviewed content: 8891fb99 on task/wave27-comparison-appendix in /root/project/w-wave20 (5 files). I confirmed all four record/index files in the live worktree (HEAD ac7b69e9) are byte-identical to 8891fb99 (git hash-object match), so my live checker run reflects the pinned content.

VERDICT: PASS (G1).

I independently re-opened the current official sources (I did not trust the packet summary or the two returns) and reproduced each fact.

F1 — Official sources re-opened, whole lot outline in EPSG:2263 (PASS).
- MapPLUTO FeatureServer/0, where BBL=4073340070, outSR=2263: 1 feature, ZoneDist1 R6B, Overlay1 C2-2, LotArea 10075, Block 7334 Lot 70, QN, "215-16 NORTHERN BOULEVARD", Version "26v2". The returned 5-vertex ring is byte-identical to the committed fixture; I recomputed the polygon centroid = (1048850.090, 216370.771) vs record E1 (1048850.089, 216370.771) and Shape__Area 10387.99 — match.
- nycmih FeatureServer/0 (serviceItemId 491d74ba…, SR 2263, maxRecordCount 195, dataLastEditDate 2026-09-30T21:33:18Z): whole-ring spatialRel=esriSpatialRelIntersects count = 0. Over all 289 features (paginated) my exact segment distance gives nearest "Douglaston Parkway Rezoning" CD 11, adopted 2019-03-13, 5925.4 ft; next "217-14 24th Avenue Rezoning" CD 11, adopted 2026-02-24, 7501.1 ft. The "…for reference only and are not intended for determining Mandatory Inclusionary Housing eligibility at the tax lot level" disclaimer verified verbatim in the official nycmih_metadata.pdf.
- nyih FeatureServer/0 (serviceItemId e0806bbb…, SR 2263, maxRecordCount 1000, dataLastEditDate 2026-09-09T15:30:53Z): whole-ring intersect count = 0; over all 55 features nearest "Jamaica" CD 12, adopted 2007-09-10, 17617.8 ft; no nyih feature in CD 11.
- ZR Appendix F Queens sub-page (…-areas-1), Last Amended 9/24/2026 — raw HTML confirms: "Community District 11 Map 1 – (3/13/19) Portion of Community District 11, Queens Map 2 - (2/24/26) Portion of Community District 11, Queens". Both portions; dates match the two CD 11 nycmih areas. (The landing-page index omits CD 11; the maps live on the borough sub-page, as E4 cites.)
All headline facts (OUT of both; nearest areas/distances; last-edit dates; disclaimer; two CD 11 portion-maps) reproduce the record exactly. Margins ~300× map tolerance — not a boundary case.

F2 — Record fields honest vs the two sealed returns and the README vocabulary (PASS). research_status answered_from_primary_source (membership is a primary-layer fact); applies conditional; 3 non-empty conditions; reading and conditions both carry the UAP/27-131/23-22/23-432 pathway explicitly as an unreviewed draft (ADR-007). promotion.requested_label Provisional; nothing Verified. agent_reviews: producer "orchestrator"; two reviewers (official-source-researcher, data-contract-verifier), both ≠ producer, both verdict "agrees", reviewed_revision 1, reviewed_code_identity {}; findings reproduce return-research-MIH.md and return-check-MIH-independent.md faithfully. professional_review null. Only E4 carries saved_copy (E1/E2/E3/E5 saved_copy and sha256 null). implementation.code_paths [] and code_identity {}.

F3 — E4 provenance (PASS). LF-normalized whole-file sha256 of docs/research/zr-snapshots/v1/zr-appendix-f.snapshot.json at 8891fb99 = 0a7952bd26c7adb509283e67d689e9ad54f16c73870594f61640c16edaa40008 = record E4.sha256.

F4 — research_record_check (PASS). `python3 tools/research_record_check.py --check` → EXIT 0, PASS, 7 records. NB-07: status=answered_from_primary_source, code_current=True, review_state=current, requested_label=Provisional.

F5 — Two index lines (PASS). RESEARCH_REQUESTS.md: exactly one NB-07 line added to the evidence-records paragraph (link + "answered from the DCP nycmih/nyih layers…unreviewed draft"); Residual OPEN unchanged. README table: exactly one NB-07 row, question text = record, status cell answered_from_primary_source = conclusion.research_status. No existing row/line changed.

F6 — NB-05 (DB-274 half) is text-only (PASS). Diff vs 8891fb99^ shows exactly two hunks: revision 6→7 and a clarification of the last dependency_assessment entry's "(revision 5)" parenthesis. No evidence, reading, measurement value, code_identity, review block, research_status or label changed. The latest agent review is reviewed_revision 3, so the review was already stale at revision 6; review_state stays stale — the producer's "checker line unchanged from the pre-edit baseline" claim holds.

ADVISORIES (non-blocking):
A1 — E2's disclaimer excerpt reads "provided for reference only and not intended…"; the official PDF reads "…for reference only and are not intended…". Semantically identical; gis_geometry excerpts are summaries, so no correction required.
A2 — E1/freshness say the live service "prints no explicit version token"; the per-feature attribute Version="26v2" does stamp the release. The record is over-conservative, not wrong; its 26v2 conclusion is correct.
A3 — The ZR landing-page HTML is not byte-stable (dynamic tokens); E4 correctly rests provenance on the committed snapshot (sha matches), the sound approach.

SCOPE NOTE: This is the G1 data-contract pass only. Packet scenario S7 (D-093/D-094 applicability append + directive_registry digest resync + audit_log in the same commit) is the directive-compliance-verifier's remit, not verified here.

END-OF-REPORT
