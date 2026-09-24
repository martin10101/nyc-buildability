# M5-T080 — G3 re-review after rework (code-reviewer "cr-t080b", fresh reviewer, read-only)

> Transmission history: pinned at f00a4745, delivered as three SendMessage parts (1/3..3/3) ending with
> END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only).
> Verdict PASS: first-round F1/F2/F3/A3/A4 all CLOSED at the byte level; 381-row bijection and the 4-path
> docs-only scope hold; nothing weakened. Fadv-1 (architect.css missing from the in-flight re-pin register;
> verified immaterial) is routed to DB-060 (h). The first-round FAIL report M5-T080-G3.md stays as history.

---

M5-T080 G3 RE-REVIEW (code-reviewer cr-t080b, read-only) — part 1/3. Verdict PASS (full line in 3/3).

PIN: HEAD f00a47452705f16378c08649e3dd863374d60861. Ledger apps/web pin-of-record a57bb8de (= dc5a763e = b56f3d5b for non-in-flight files); in-flight rows pinned b56f3d5b. First-round content = the a57bb8de ledger blobs (rework commits land after it). I read every cited span myself.

PER-FINDING CLOSURE TABLE (first-round F1,F2,F3,A3,A4):

F1 (11 rows wrong current_source) — CLOSED.
- SH-02 → page.tsx:5 (line 5 holds the whole HomePage body: "Internal development build" + "Preliminary results require professional review" + "Open workspace" link; line 6 = `}`).
- SR11, SR52-56, SR58-61 → apps/web/src/lib/surveyReview/{model,labels,errorCopy}.ts. The wrong `components/survey-review/lib` path is entirely gone (grep = NONE). model.ts:130-145 shows the SR11 "All material facts are resolved" text; labels.ts/errorCopy.ts exist; SR11's 2nd path (SurveyReviewScreen.tsx:291-293) is now full.

F2 (9 authority cells + E13 pin) — CLOSED. Each re-anchor verified in source:
- PE-07 → proposal-editor.test.tsx:83-88 (blocks bad-charset, names _LABEL_CHARSET, check-summary null).
- AD15 → PRD 5 step 5 (PRD.md:96 = "System displays possible matches if ambiguous"); DB refs dropped.
- M07 → lot-outline-map.test.tsx:349-360 @b56f3d5b (asserts "condominium unit lot"); DB-002/DB-032 dropped; in-flight anchor noted (:362-373 @a57bb8de).
- R01 → workspace.test.tsx:56-85 + e2e:185-213 (print + audit-appendix + expand/restore); honest gap: no test pins the identity / "not saved automatically" line.
- R03 → source-links.test.tsx:35 ("may differ from captured evidence") + :60-68 (appendix retains captured values).
- C01 → condo-resolution-display.test.tsx:410-419,548-563,781-792 (entered-vs-analyzed substitution + real h2).
- C10 → :435-455 (profile-withhold vs benign single: disagreement surfaced, limits govern, no records).
- E08 → implementation-only prose + gap (EvidenceWorkspace.tsx:22-34 index exists, no test); E13 → workspace.test.tsx:36-50 (applicable determination first).
- LS-C03 → compare-entry.test.tsx:42-76 + compare-journey.spec.ts:147-150 ("No property selected", way out, no fetch).

F3 (P0-RECONCILIATION facts) — CLOSED.
- D-076: §4 "checkpoint PASSED" verified against D-082-R001 text ("Post-B3 checkpoint PASSED").
- DB-046: §3 = OPEN row, (a)-(f) resolved 251st, (g)/(h) WATCH, (i) public-exposure — matches DISCOVERY_BACKLOG @a57bb8de lines 169/175.
- Route map: AC*/M* on the /property search state (ArchitectEntry.tsx:67; AddressResolutionScreen.tsx:247; AddressConfirmCard.tsx:305), Continue → /property/confirm (:380) — verified in source.

(continues 2/3)

---

M5-T080 G3 RE-REVIEW — part 2/3 (A3/A4 closure + structural checks + in-flight handling).

A3 (authority form) — CLOSED.
- SH-07 → implementation-only prose; proof_owner notes architect-workspace.spec.ts:126 covers only the survey-enabled inbox-empty (verified), not the Documents-off card.
- B-001 no longer "reviewer finding": A01/LS-P01/DB01 now cite exact-copy tests (survey-review-inbox / honesty / dashboard specs).
- Single authority class on ALL 381 rows: keyword scan = 0 multi-class, 0 no-class.
- A05 → development-limits.test.tsx:457-466 ("Rule details incomplete", captured record, cap "Not calculated"). LS-C05 → compare-screen.test.tsx:125-133 (data_completeness "missing_critical"). SR24 → implementation-only prose + named gap (old :71-84 didn't assert it).

A4 (span precision) — CLOSED.
- LS-T02/04/06 disjoint spans restored (e.g. 90-120,125-180 not merged 90-180).
- ZC-04 → 30-47 (file is 49 lines, verified). M08 → 694-702, no-feature text on line 699 (verified).
- DB05 → full path MissionControl.tsx; DB08 → full path dashboard/ui.tsx:120-127 (Freshness, verified); SR11 2nd path full.

STRUCTURAL
AS-1 (completeness): exact 381 bijection. Independent enumeration of assessment lines 57-923 = 381 unique ids; md5 of that set == md5 of the 381 ledger ids (both 28cbd515…). 155 A + 226 B, 0 dups, 0 A/B overlap. Every row carries exactly the 18 packet keys in packet order.
AS-2 (no-loss): 344 L rows, none missing primary_state / progressive_destination / accessibility / print_destination / proof_owner. 4 consolidations resolve — LS-C08→LS-C24, LS-C23→LS-C22, LS-C27→"LS-C06 + LS-C05" (the '+' split resolves both), SR27→SR12; no retire rows; no stray refs on keep/convert. No mark/disposition/phase/section/drift weakened vs a57bb8de (git diff on those five fields = empty in both ledgers); the ONLY replacement_ref change is LS-C27 gaining "+ LS-C05" (HJ-4 strengthening).
AS-5 (scope): both ledgers valid JSON (json.load OK). The 3 rework content commits (6644f93f / d5209b4e / d8df2674) touch EXACTLY the 4 allowed paths — P0-RECONCILIATION.md, disclosure-ledger-a.json, disclosure-ledger-b.json, M5-T080-producer-report.md; no forbidden/source/test/copy/rule/assessment edit. (f00a4745 = orchestrator resubmit bookkeeping: G2 / evidence-map / state / task json — expected, not producer content.)

IN-FLIGHT (your item 1): 12 apps/web files changed a57bb8de→HEAD = the 10 M5-T078/T079 lane source/test files + package.json/package-lock.json + architect.css. Rows citing lane source are pinned at b56f3d5b and flagged in-flight in open_question: DR-01..23, ME-01..17 (verified DR-05, ME-03), M01/02/05/07/11 (verified M07).

(continues 3/3)

---

M5-T080 G3 RE-REVIEW — part 3/3 (sample breadth, new findings, verdict).

architect.css is the ONE in-flight file NOT in the re-pin register (§1/§8 list 11). Checked directly: its a57bb8de→HEAD diff is a single hunk at ~line 42; lines 140/187/188 (the print rules the print cells cite) are byte-identical at a57bb8de and HEAD (both files 232 lines). So no print citation is stale — the omission is immaterial.

SAMPLE BREADTH (~49 rows across every family, weighted to rework-changed rows): current_source drift, single-class authority + anchor, print truth, proof anchors/gaps all held. Print cells are truthful and per-surface, not boilerplate — PART A accessibility 150 distinct / 155 (max repeat 4); the residual repeats are legitimate shared surfaces (28 AD rows, 62 SR rows, 14 LS-F rows each share ONE true status). Verified print claims against source: LC22 "prints via format.ts" (true); SW-01 "partly printed" — cap via DevelopmentLimits, scope note not (true); PC-05 / PV-01 / ME-03 / DR-05 "not printed — proposal view not in the ReportView tree" (true).

FOLDED HJ FIXES (HJ-1..5 blocking; print-truth is in the sample scope), spot-verified in source:
- HJ-1: the 16 shared LS rows now say "prints today; must stay in default print; shared primitive" — ReportView.tsx:53-66 opens every non-raw <details> on print; :113 OpenIssues, :115 ScenarioConstraints render.
- HJ-3: E12 reason (CalculationEvidence.tsx:43) + fallback_direction_note (:45) are plain paragraphs that print by default; only CapturedRecord (:52-55) is in a raw disclosure — the legal-scope caveat no longer drops from print.
- HJ-4: LS-C06 keeps both review flags beside the value; LS-C27 → "LS-C06 + LS-C05".
First-round advisories A1/A2/A5/A6/A7 (outside your set) are also addressed: §8 re-pin register; de-boilerplating; §5 named fixtures + DB-038/043 corrected + false "byte-identical" claim removed; LS-C27 two-target.

NEW FINDINGS: none blocking.
- Fadv-1 (LOW / informational, no consequence today): architect.css is absent from the in-flight re-pin register though it is one of the 12 post-pin edits. Verified immaterial — its print-rule lines 140/187/188 are unmoved at HEAD. Would matter only if a later architect.css edit shifts those lines and the register is trusted as the complete in-flight list. Repro: `git diff a57bb8de HEAD -- apps/web/src/app/property/architect.css` (one hunk @ ~42) and compare `sed -n '140p;187,188p'` at both shas.

Every F1/F2/F3/A3/A4 defect is fixed at the byte level with a supporting primary source or an honestly-named gap; the 381-row structure and the 4-path docs-only scope hold; nothing was weakened.

M5-T080 G3 VERDICT: PASS

END-OF-REPORT
