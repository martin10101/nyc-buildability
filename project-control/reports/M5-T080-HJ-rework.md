# M5-T080 — human-journey re-review after rework (human-journey-reviewer "hj-t080b", fresh reviewer, read-only)

> Transmission history: pinned at f00a4745, delivered as four SendMessage parts (1/4..4/4) ending with END-OF-REPORT;
> no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only). Verdict PASS: HJ-1..HJ-9
> CLOSED, HJ-10 addressed as instructed, HJ-11 partial-acceptable; advisories ADV-1/ADV-2 routed to DB-060. Not a
> required ledger gate for M5-T080 (gates G0/G2/G3); recorded as the journey evidence for the DCV.

---

M5-T080 human-journey re-review (hj-t080b, read-only) — part 1 of 4.

PIN: live HEAD `f00a47452705f16378c08649e3dd863374d60861` at start. Source read at `a57bb8de` per instruction (report-surface files byte-identical b56f3d5b→HEAD; in-flight rows pinned b56f3d5b, checked there). Method: read both ledgers + P0-RECONCILIATION.md, then verified ~20 rows against actual apps/web source with git show, plus two whole-ledger scans.

VERDICT UP FRONT: all five BLOCKING findings (HJ-1..HJ-5) are CLOSED and substantiated at source. HJ-6..HJ-9 closed, HJ-10/HJ-11 handled as instructed. No new blocking problem. PASS.

Per-finding closure:

HJ-1 (print caveats falsely marked "no print regression") — CLOSED. The 16 architect-printing rows (LS-P03..LS-P15, LS-C17, LS-C18, LS-C19) now read "Prints in the property brief today; must stay in default print. Shared primitive (architect + legacy)", each naming its ReportView mount line. I verified every mount line against ReportView.tsx@a57bb8de: :104 PropertyFacts, :108 ZoningSection, :113 OpenIssues/ProfileViews, :115 ScenarioConstraints, :116 ScenarioAssumptions, :121 CalculationEvidence — all exact. LS-P10 honestly records the real gap (grouped missing fields sit behind a button that architect.css:140 hides in print, so paper shows the count but not the fields); LS-P15 honestly records that the nested "Full captured source record" JSON (ProvenanceDisclosure.tsx:101-110, class provenance-details, NOT architect-raw) prints by default, unlike CapturedRecord. Decisive inverse scan: of the 15 rows still saying "no print regression to preserve", 0 are a component the architect brief prints — all are legacy-compare-only (ScenarioCard/ScenarioResult/CompareScreen; ReportView imports ScenarioConstraints/ScenarioAssumptions but NOT ScenarioCard/ScenarioResult). Consequence for a real analyst: every caveat that reaches paper today is now flagged to stay in default print and routed to the P5 gate.

HJ-2 ("prints" claimed where nothing prints) — CLOSED. Whole-ledger scan: 0 rows claim "prints" without a real ReportView/layout/format/css anchor. A01 and A03 now say "Not printed today" and open explicit P5 decisions — verified against architect.css:140, which hides .architect-topbar (A01 env/do-not-share banner) and .architect-nav (A03 footnote) in print. PART A proposal/limits/drawing/check rows now correctly say "Not printed today: proposal view is not in the print tree (ReportView.tsx:67-132)". SH-09 honestly records that ScenarioFailureStates' Retry buttons print above the brief (architect.css:140 hides buttons only inside .architect-report).

Continued in part 2.

---

M5-T080 HJ re-review — part 2 of 4.

HJ-3 (E12 sends a legal caveat to the raw tier, dropping it from print) — CLOSED. E12's progressive_destination and print_destination now both route the verbatim wide_street.reason (CalculationEvidence.tsx:43) and fallback_direction_note (:45) to the readable tier that "prints by default and must stay in default print"; only internal IDs and the CapturedRecord go to raw. Verified at source: CalculationEvidence.tsx:43 is `<p>{evaluation.wide_street.reason}</p>` and :45 is `<p className="section-note">{evaluation.wide_street.fallback_direction_note}</p>` — both plain paragraphs OUTSIDE any raw disclosure, inside the non-raw brief-calculations details (ReportView.tsx:119-122, which beforeprint opens). The raw claim is exact: CapturedRecord (EvidenceRecord.tsx:9) renders `<details className="provenance-details architect-raw">`, and architect.css:188 hides .architect-raw in print unless the audit appendix is on. E12 also records the honest gap: no test yet pins that the reason/note render in the non-raw tier — routed to P5 G3/G4. Consequence: the legal-scope fallback caveat on the governing FAR now stays on the printed brief.

HJ-4 (LS-C06/LS-C27 separate the cap number from its professional-review flag) — CLOSED. LS-C06's primary_state now keeps BOTH conditional flags directly beside the value, never behind a click: the needs_review "(DRAFT — needs professional review, not Verified)" flag (ScenarioCard.tsx:67-71 — verified: it is inside the same `<p>` as scenario-cap-value) and the professional_review_required state mapped to a visible label. Its progressive_destination explicitly states "the two review flags are NOT progressive — they stay beside the value." LS-C27's replacement_ref is corrected from "LS-C06" to "LS-C06 + LS-C05": the cap+review flag lands in LS-C06, the exact not_verified_disclaimer in LS-C05 (verified ScenarioResult.tsx:212 = disclaimer, :213-217 = professional_review_required flag). A06 (the architect brief's cap via DevelopmentLimits) now names the readable per-cap status enum — Conditional / Professional review required / Data conflict / Unsupported / Not applicable — verified at DevelopmentLimits.tsx:15-21 (STATUS_LABELS) rendered :39. The proof_owner also upgrades to a visibility obligation ("assert visible beside the cap, not inside a closed disclosure — the section 8.6 string-assertion-hiding-a-warning trap"). Consequence: a flagged cap can never show its number without its review flag; the disclaimer's destination is no longer orphaned in prose.

Continued in part 3.

---

M5-T080 HJ re-review — part 3 of 4.

HJ-5 (accessibility column was one repeated sentence) — CLOSED. The cells are now row-specific (PART A: 150 distinct accessibility strings, max repeat 4; PART B every row rewritten). I verified every named alert site is real and at the exact cited line: AnalysisIdentityNotice.tsx:72, app/property/error.tsx:37, app/dashboard/error.tsx:19, CorrectionForm.tsx:90/146/151, ReasonForm.tsx:67/72, FocusedItem.tsx:166, ConfirmDocumentPanel.tsx:180, ArchitectEntry.tsx:222/234, ProposalEditor.tsx:413, ProposalCheckReport.tsx:215, and (in-flight @b56f3d5b) MaxEnvelopePanel.tsx:285 and ProposalOutlineDraw.tsx:306 (whose role is correctly noted as bridged→status / non-bridged→alert). No silent alert→polite downgrade: cells say "KEEP the alert". Same-event duplicates are recorded (A15 records the alert + rule-eval announcer double-speak; reconciliation §7 lists PE-07/PC-06/ME-06/DR-07). "Never color alone" now appears (LS-P03, LS-C06). SH-01 is correctly described as a `<footer role="contentinfo" aria-label="Required disclaimer">` landmark, "not a control" (verified app/layout.tsx:35-48). Consequence: a designer following this column keeps existing alerts and can see which region speaks and whether it duplicates.

HJ-6 (D-083 claim classes + tightenings) — CLOSED. ME-05 now pins the heading "Preliminary development limits" (h2, MaxEnvelopePanel.tsx:261) and the visible qualifier "…not a maximum permitted building" (:262-264). PC-05/PV-01 default to failed/unchecked with an explicit "Incomplete — N could not be checked" state "outside any tab or disclosure" (D-083-R004), never opening on Pass. D-083 cited on the ME rows.

HJ-7 (route/state map unfollowable) — CLOSED. §2 rebuilt as 23 rows, one per route+flag+view, ★ marking view=report. I walked the corrections that were wrong in the first pass and verified each mount site: confirm/page.tsx:24 renders the architect overview when the flag is on (so AC*/M* are NOT there); AC*/M* mount on the /property no-BBL search state (ArchitectEntry.tsx:65-67 → AddressResolutionScreen; AddressConfirmCard.tsx:305 mounts M*, :380 links Continue to /property/confirm); ME* only at view=proposal; AD* now has rows; the two unreachable legacy branches (PropertyLookup gated always-false at page.tsx:41/45) are noted. Each state is reachable by following the map.

Continued in part 4.

---

M5-T080 HJ re-review — part 4 of 4.

HJ-8 (freshness pointers) — CLOSED. §5 routes the §13 High "report freshness" finding to PC-04/PC-05/PV-01 (which now carry the "Changed since check" state), not the stale-less PE rows. PE-02 cross-references PE-10 for the sample-seed provenance.
HJ-9 (removal bookkeeping) — CLOSED. LS-C22 now keeps, as the LS-C23 survivor, the "Rule families still missing (n)" count, the named envelope-blocking families, and the empty state "No coverage-matrix family is recorded as missing…" (CoverageMatrixSection.tsx:124-128). A03/A15/E03 duplicate survivors are named (A03→SH-01 footer + per-result status; A15→first paragraph alert).
HJ-10 (drift at head) — ADDRESSED AS INSTRUCTED. In-flight flags kept on DR/ME rows and extended; the new honesty copy T078/T079 add (MaxEnvelopePanel "…withheld", ProposalOutlineDraw omitted-row hints) is listed in reconciliation §8 for the post-accept re-pin, not added now per orchestrator instruction.
HJ-11 (proof column) — PARTIAL, acceptable. Every L row now carries a phase visibility/announcement proof obligation (D-086-R003); rows citing a whole test file keep it for the owning slice's G0; PV-01..03 re-anchored; SH-01 print corrected to the root-layout footer.

THE 13 DISCOVERIES — honestly recorded; none contradicts a ledger row. Several ARE the exact nuances the rework rows document: disc 3 (failure cards + Retry print above brief) = SH-09 print cell; disc 4 (full JSON prints) = LS-P15; disc 5 (grouped missing fields vanish on paper) = LS-P10; disc 6 (F04 spatial evidence + LS-E05 server disclaimer not in default print) = F04 print cell "caveat absent from paper, P5 decision" + LS-E05 "reaches paper only inside the raw record"; disc 7 (identity mismatch spoken twice) = A15 a11y cell. Disc 1/2/8-12 (scenario-failure-not-announced, focus-not-moved, dashboard/inbox focus, tooltip-only label, legacy compare omission) are a11y/focus gaps the ledger records in a11y cells (e.g. LS-C17/18 "no scenario announcer exists") or routes to backlog — correctly NOT fixed in this docs packet. Disc 13 (L rows with no pinning test) matches the "gap" notes the rework added to proof_owner cells.

NEW FINDINGS: none blocking. Two minor ADVISORIES (do not block):
- ADV-1: E12's print cell treats CalculationEvidence:52-55 as wholly raw, but the OUTER `<details className="provenance-details">` (:51) is non-raw, so under print it opens and shows an empty "Width-policy decisions and D-052 source provenance" summary while only the inner architect-raw CapturedRecord is hidden. Cosmetic; the reason/fallback caveats print correctly.
- ADV-2: LS-C06/LS-C27 correctly say "no print regression to preserve" (legacy-compare-only, verified not imported by ReportView), but do not cross-reference that the cap+review meaning's print duty lives in A06 (which prints). A one-line cross-ref would help a P5 reader confirm nothing is lost.

CLOSURE TABLE: HJ-1 CLOSED · HJ-2 CLOSED · HJ-3 CLOSED · HJ-4 CLOSED · HJ-5 CLOSED · HJ-6 CLOSED · HJ-7 CLOSED · HJ-8 CLOSED · HJ-9 CLOSED · HJ-10 addressed-as-instructed · HJ-11 partial-acceptable.

M5-T080 HJ VERDICT: PASS

END-OF-REPORT
