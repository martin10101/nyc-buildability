# D-086 P0 reconciliation — UI deep-dive assessment vs the current head

Task **M5-T080** (D-086 phase P0, docs only), branch `task/M5-T080-p0-reconcile`, worktree `wt-m5t080`.
This file carries the GLOBAL reconciliation items. The row-by-row disclosure-migration ledger is
`disclosure-ledger-a.json` (sections 4–6 families, PART A) and `disclosure-ledger-b.json` (sections 7–9
families, PART B).

**Pins.** First pass: producer pin **`b56f3d5b40171bcb6b760f97eb0eef574995f8ae`**. Rework A (G3 cr-p0 +
HJ hj-p0 findings): verified at **`a57bb8dec34129a86e5c9bfe6ea2d2be1f5dfc1d`**. How the two pins relate is
in §1; the in-flight re-pin register is §8.

**Spec source (binding, input not authorization — D-086-R001):** `docs/UI_DEEP_DIVE_ASSESSMENT.md`,
frozen at `dc5a763e`, LF-normalized sha256 `c6d1b25779c2dd3fb4699d6a99ca50d9695d82f7afc05986fe58de5cf8504b84`
(matches D-086-R001; checked with `tr -d '\r' < docs/UI_DEEP_DIVE_ASSESSMENT.md | sha256sum`). The on-disk
CRLF sha differs (`ed94df52…`); that is the Windows checkout, not drift.

---

## 1. Per-cited-file drift

**Step 1, `dc5a763e` → `b56f3d5b`:** `git diff --name-only dc5a763e b56f3d5b -- apps/web | wc -l` = **0**.
Every inventory span and cited test lives under `apps/web/**`, so no cited file changed between the audit
and the producer pin.

**Step 2, `b56f3d5b` → `a57bb8de` (rework head):** `git diff --stat b56f3d5b a57bb8de -- apps/web` =
**11 files**, all from the two in-flight lane units, both **in rework** at `a57bb8de`:

| File | Lane | PART A rows that cite it |
|---|---|---|
| `components/architect/ProposalOutlineDraw.tsx` | M5-T078 (`5879cdfa`) | DR-01…DR-07 (span); DR-10…DR-23 (renders/announces) |
| `components/architect/ProposalOutlineMap.tsx` | M5-T078 | DR-08, DR-09 |
| `components/architect/__tests__/proposal-outline-draw.test.tsx` | M5-T078 | proof DR-01…DR-07, DR-10…DR-23 |
| `components/architect/__tests__/proposal-outline-map.test.tsx` | M5-T078 | proof DR-08, DR-09 |
| `components/address/__tests__/lot-outline-map.test.tsx` | M5-T078 | proof M01…M13 (line anchors in M01, M02, M05, M07, M11) |
| `e2e/proposal-editor.spec.ts` | M5-T079 | authority + proof ME-03 |
| `components/architect/__tests__/entry.test.tsx` | M5-T079 | none |
| `components/architect/MaxEnvelopePanel.tsx` | M5-T079 (`006f3589`) | ME-01…ME-07 |
| `lib/architect/max-envelope-api.ts` | M5-T079 | ME-08…ME-17 |
| `components/architect/__tests__/max-envelope-panel.test.tsx` | M5-T079 | proof ME-01…ME-17 |
| `lib/architect/__tests__/max-envelope-api.test.ts` | M5-T079 | none |

**Pin of record.** Every other `apps/web` file is byte-identical at `dc5a763e`, `b56f3d5b` and `a57bb8de`,
so rows citing only those files are valid at the rework head. Rows citing an in-flight file keep their
spans, test anchors and accessibility cells **pinned at `b56f3d5b`** (the last head before the lane units),
with drift recorded against that pin, an `in-flight (M5-T078/T079)` flag in `open_question`, and the
observed `a57bb8de` location as information only. They are **re-pinned after M5-T078/T079 are accepted**
(§8); rows for copy those lanes add are created then, not now.

**Method limit (G3-A7).** `unchanged` is inferred from blob identity. That proves nothing changed since
`dc5a763e`; it does not prove each assessment span was right. Rework A content-checked these spans and
corrected four: SH-02 (`page.tsx:5`, not `:6`), ZC-04 (`ZoningContextControl.tsx:30-47`; the file has 49
lines), M08 (`LotOutlineMap.tsx:694-702`, text on 699) and every new test/PRD anchor (§6). The first pass
wrongly credited the assessment with a "byte-identical" note it does not contain; that claim is removed.

**Non-`apps/web` files the reconciliation relies on:**

| File | `dc5a763e`→`b56f3d5b` | `b56f3d5b`→`a57bb8de` | Note |
|---|---|---|---|
| `docs/DISCOVERY_BACKLOG.md` | +8 lines (DB-051, DB-052, sweeps 256th–259th) | +10 lines (DB-053…DB-056, sweeps 260th–264th) | §3 |
| `.claude/rules/expansion-agent-dispatch-hold.md` | + §2.3 (D-087, names D-082 inline) | unchanged | §4 |
| `project-control/directives/` | + D-086, D-087 | D-087 source-002 amendment | §4 |

No source, test, copy, rule or assessment file is edited by this task; only the `allowed_paths` change.

---

## 2. Reachable route + state map (one row per route + flag + view)

Flag = `ruleEvaluationSurfaceEnabled({ruleeval})` (`lib/rule-evaluation`). With the flag on, every
workspace link is `/property?ruleeval=on&bbl=…&view=…` (`navigation.ts:13-17`); `/property/confirm` and
`/property/compare` mount the same `ArchitectEntry` with `requireBbl` and a different default view. Families
are taken from the mount sites named. **★ = the one printing view.**

| # | Route · flag · view/state | Mount site | PART A families | PART B families | Print |
|---|---|---|---|---|---|
| 1 | every route | root layout footer `app/layout.tsx:35-48` | SH-01 | — | footer prints on every printed page |
| 2 | `/` | `app/page.tsx:5` | SH-02 | — | not a print surface |
| 3 | `/property` · off | `page.tsx:42-47` → InternalBanner + PropertyLookup | SH-04, SH-11, SH-12, SH-13, SH-15 | LS-P (InternalBanner, shared facts/coverage/conflict/zoning), LS-F (OutcomeFailureStates `PropertyLookup.tsx:355`) | none |
| 4 | `/property` · on · no `bbl` (search) | `ArchitectEntry.tsx:221-228` → PropertySearch `:52-82` | SH-03, SH-04, SH-15; AD01–AD28 (`AddressResolutionScreen`, `:67`); AC01–AC11 after resolve (`AddressResolutionScreen.tsx:247`); M01–M13 (`AddressConfirmCard.tsx:305`); ZC-04 (`LotOutlineMap.tsx:625`) | A01–A03 (ArchitectShell) | none |
| 5 | `/property` · on · invalid `bbl` | same, plus `role=alert` card `:222-227` | SH-10 + row 4 | A01–A03 | none |
| 6 | any flag-on route · valid `bbl` · profile loading / mismatch / failure | `ArchitectEntry.tsx:229-242` | SH-05, SH-10 | A01–A03, LS-F (`:240`) | none |
| 7 | view=`overview` (default for `/property`, `/property/confirm`) | PropertyOverview `ArchitectEntry.tsx:116` | SH-05, SH-08, SH-09; M01–M13 (`PropertyOverview.tsx:382`); ZC-01–ZC-03 (`:386`); ZC-04 | A01–A15 (issues summary `:362`, DevelopmentLimits, site context, identity notices `ArchitectEntry.tsx:192-196`), C01–C11 (`PropertyOverview.tsx:385`) | none |
| 8 | view=`facts` | PropertyFacts `:119` + EvidenceInspector `:199` | SH-05, SH-08 | F01–F03, E01–E07, LS-P | none |
| 9 | view=`zoning` | ZoningView `:122` | SH-05, SH-08, SH-09 | A05–A12, F04, F05, F08, LS-P (ZoningSection), LS-E (RuleEvaluationResult `ProfileViews.tsx:51`), E01–E07 | none |
| 10 | view=`scenarios` (default for `/property/compare`) | issues summary + ScenarioWorkspace `:125-128` | SH-05, SH-08, SH-09, SW-01–SW-03 | A04, LS-C children | none |
| 11 | view=`proposal` | ProposalSurface `:44-50,162-164` → MaxEnvelopePanel + ProposalEditor → ProposalOutlineDraw → ProposalOutlineMap → LotOutlineMap; ProposalCheckReport; ProposalVariations | SH-05, SH-08; ME-01–ME-17; PE-01–PE-10; DR-01–DR-23; PC-01–PC-06; PV-01–PV-03; M01–M13 (`ProposalOutlineMap.tsx:160` @b56f3d5b); ZC-04 | A01–A03 | none (not in the brief) |
| 12 | view=`evidence` | EvidenceWorkspace `:131` | SH-05, SH-08, SH-09 | E04–E16 | none |
| 13 | view=`documents` | survey on: ReviewInbox `:152-153`; off: card `:154-157` | SH-07 (off) | SR inbox rows (on) | none |
| 14 | view=`issues` | OpenIssues + "Analysis issues" `:134-149` | SH-06, SH-09 | F06, LS-P (conflicts, missing inputs, unsupported, professional review, legend) | none |
| 15 ★ | view=`report` | ReportView `:160` | SH-01 (footer), SH-05, SH-09 (loading/failure print when present); SW-01 headline via DevelopmentLimits; SH-08 header **hidden** | R01–R03, A05–A12, A14–A15, C01–C11, F01–F03, F08, E11–E16, LS-P03–LS-P15, LS-C17–LS-C19 | **yes**: tree `ReportView.tsx:67-132`; `beforeprint` opens every non-raw `<details>` (`:53-65`); print rules `architect.css:140,187-188` |
| 16 | view=`envelope`/`units`/`financials` | PlannedView `:165` | SH-05, SH-08 | F07, A02 | none |
| 17 | `/property/confirm` · off | ConfirmEntry → ConfirmScreen | LC01–LC22, SH-15 | LS-P (InternalBanner `ConfirmScreen.tsx:489`, shared), LS-F (`:466`) | none |
| 18 | `/property/confirm` · on | `ArchitectEntry defaultView=overview requireBbl` | no `bbl` → SH-10 alert + row 4; `bbl` → rows 6–16 | as rows 4–16 | view=report only |
| 19 | `/property/compare` · off | CompareEntry → CompareScreen | SH-15 | LS-C01–LS-C28, LS-F, InternalBanner (`CompareScreen.tsx:168`) | none |
| 20 | `/property/compare` · on | `ArchitectEntry defaultView=scenarios requireBbl` | as row 18 (default row 10) | as rows 4–16 | view=report only |
| 21 | `/property` error boundary | `app/property/error.tsx` | SH-14 | LS-T15, InternalBanner (`:38`) | none |
| 22 | `/survey/review`, `/survey/review/[documentId]` | SurveyWorkspace | SH-15 | SR01–SR62, A01–A03 | none |
| 23 | `/dashboard` (+ `error.tsx`) | dashboard components | — | DB01–DB22 | none |

Route-map corrections versus the first pass (G3-F3, HJ-7): AC\* and M\* render on the `/property`
no-BBL search state (`ArchitectEntry.tsx:65-67`; `AddressResolutionScreen.tsx:247`;
`AddressConfirmCard.tsx:305`), not on `/property/confirm`; the confirm card's Continue link only navigates
to `/property/confirm?bbl=…&ruleeval=on` (`AddressConfirmCard.tsx:380`), which with the flag on is the
architect overview (`confirm/page.tsx:24`). ME\* mounts only at view=`proposal`; ZC-01–ZC-03 only in the
overview. AD\* and the no-BBL search state now have rows. Two legacy branches are unreachable at the head
(`PropertyLookup.tsx:165` RuleEvaluationPanel and `:265` AddressResolutionScreen, both gated by a prop that
is always false at the only mount, `app/property/page.tsx:41,45`); see the producer report DISCOVERIES.

---

## 3. Latest DISCOVERY_BACKLOG disposition for every DB item the assessment cites (§10.4)

Read from `docs/DISCOVERY_BACKLOG.md` at the rework head `a57bb8de` (rows plus all later sweep lines; a later
sweep overrides an earlier cell, per D-069), through the **264th** acceptance seam. These are backlog
`DB-0xx` items, distinct from the §9.8 dashboard rows DB01–DB22. The status column quotes the row's own
status cell; closed sub-items are listed after it.

| DB item | Row status (head) | Latest disposition relevant to P0 |
|---|---|---|
| DB-001 | OPEN | Split-lot apportionment; legal-research class. Keep unresolved scope + all districts. |
| DB-002 | RESOLVED | Research + resolver M5-T042 (225th); live wiring via DB-029 (230th). |
| DB-003 | WATCH | Source-stale dataset; freshness cue must survive. |
| DB-005 | RESOLVED | ZoLa-link unification (M5-T036). |
| DB-006 / DB-007 / DB-009 | RESOLVED | Address retry/label + tests (M5-T038). |
| DB-008 | WATCH | 6 s address deadline vs slow-but-healthy latency. |
| DB-010 | RESOLVED | Named-street override matcher (M5-T039) + wiring (M5-T040). |
| DB-011 | WATCH | Tangency legal tolerance; G6 queue. |
| DB-014 / DB-015 / DB-020 | RESOLVED | Wide-street serialization + provider (M5-T035/T037). |
| DB-016 | RESOLVED | Zoning-context panel (M5-T036) — governs ZC-01. |
| DB-017 | OPEN | Flood/transit/split-zone flag carrier decision (design). |
| DB-018 | OPEN | Two ZoLa affordances consolidation (design). |
| DB-019 | RESOLVED | aria-hidden glyphs + honest null-BBL note (M5-T038). |
| DB-021 / DB-023 | RESOLVED | M5-T040 (legal halves fold into DB-011 at G6). |
| DB-024 | RESOLVED | Circular-recovery copy (M5-T041) — governs AD12. |
| DB-025 | RESOLVED | (a-d) M5-T040; (e) M5-T041; owner-question rider persists as DB-030(a). |
| DB-026 | RESOLVED | Address→lot identity (M5-T046, 228th); residual = DB-032. |
| DB-027 | OPEN | Small a11y/test polish riders. |
| DB-028 | RESOLVED | Wiring hardening (M5-T043); riders → DB-030. |
| DB-029 | RESOLVED | Condo billing-BBL live wiring (M5-T044/T045, 230th). |
| DB-030 | OPEN | (f) closed (M5-T049, 231st); (a) owner question + (b)-(e) watch remain. |
| DB-031 | RESOLVED | Multi-lot condo records view (M5-T052, 234th) — governs PART B C\*. |
| DB-032 | RESOLVED | Record-address channel (M5-T047, 229th); polish → DB-033. Governs AC10. |
| DB-033 | RESOLVED | T047-wave polish (M5-T050, 233rd). Governs AC02. |
| DB-035 | RESOLVED | CLS/late-insert riders (M5-T055, 238th). |
| DB-036 | RESOLVED | (a)+(e) closed at the 245th; the rest earlier. Governs ZC-02 and PART B condo rows. |
| DB-037 | OPEN | (a)/(b) rode T057; (d) slice 1 = T059; confirm-UX/map/combined-land slices remain. |
| DB-038 | OPEN | (b)/(c) closed at the 245th; (f) rode T059's accepted wave (243rd sweep); **(a) bbl.py precondition, (d) future-sink bound, (e) rename-carry remain**. |
| DB-040 | OPEN | api-side closed (246th/249th/252nd); (f) auth deferred (B-001), (m)/(o)/(p) confirm-UX slice, (t) posture remain. |
| DB-042 | OPEN | (c)/(d)/(e) closed at the 245th; (a)/(b) bound to the T059 slice-2/mount packet. |
| DB-043 | OPEN | **(a) closed** (focus remedy applied in T065; formally closed at the 247th). **(b)-(k) remain** for one editor polish/test-hardening packet, whose gating owner checkpoint has **PASSED** (D-082-R001) but which is **not yet contracted**. (b) is the §13 High freshness finding. Governs PE/DR/PV. |
| DB-044 | OPEN | T063 announcer riders. |
| DB-045 | OPEN | (a) real-parcel bridge delivered bounded (M5-T073, 259th; 3/8 pass); (c) server-500 proof (M5-T074, 257th); riders folded for the mount packet. Governs DR/ME mount. |
| DB-046 | **OPEN** (row status) | **(a)-(f) RESOLVED** at the 251st (M5-T068); **(g)/(h) WATCH**; **(i) routed to the public-exposure packet**. The first pass wrongly marked the whole row RESOLVED (G3-F3). |
| DB-047 | OPEN | (d)/(e) closed (253rd, T071); (a)-(c),(f)-(j) remain. Governs DR-05/DR-08. |
| DB-048 | RESOLVED | Flaky AS-1 sync spec rewritten (M5-T071, 253rd). |
| DB-049 | OPEN | Drawing-surface a11y/disclosure cluster; (a)-(f) are the **M5-T078 lane, in rework** at `a57bb8de`; (g)/(h) next lot-outline-map touch; (i) next e2e increment. Governs DR-05, DR-08, DR-09, M13. |
| DB-050 | OPEN | (a) its own pre-mount packet (geometry threading: M5-T076 accepted 256th, then DB-051); (b)-(m) are the **M5-T079 lane, in rework**; split-district disclosure required pre-mount. Governs ME/DR mount. |
| DB-051 | OPEN (row status) | **(a)-(e) RESOLVED at the 264th** (M5-T077 accepted at `114e5e56`, after the first pass); (f)+(g) remain for the mount packet. |
| DB-052 | OPEN | Local directive-harness slowness; not a UI item. |

**Head-new since the first pass (not cited by the assessment, none UI-facing):** DB-053 (PDF sheet-writer
riders), DB-054 (massing truth-object riders), DB-055 (architect-sheet PDF reader riders), DB-056 (M5-T077
route riders on the still-unmounted max-envelope route). The generated-option mount is still not proven:
split-district disclosure and DB-051(f)/(g) remain pre-mount.

---

## 4. D-040 / D-076 / D-082 / D-087 boundary check

Verified against `.claude/rules/expansion-agent-dispatch-hold.md` (§2, §2.1–§2.3; unchanged
`b56f3d5b`→`a57bb8de`) and the directive records under `project-control/directives/`.

| Boundary | Hold section | Released scope | P0 compliance |
|---|---|---|---|
| §2 base hold | §2 (2026-07-17) | 19-task pack, 9 contracts, GDS P1–P8 and pack-driven master-plan changes all SUSPENDED | P0 contracts none, authors no contract, applies no GDS proposal, changes no master plan. ✓ |
| D-040 | §2.1 (2026-09-12) | ONE increment: address-flow lot outline (MapPLUTO connector + confirm-card outline, MapLibre) | Implemented (`LotOutlineMap`, `AddressConfirmCard`); M\*/AC\* describe that surface. ✓ |
| D-076 | §2.2 (2026-09-19) | Proposal-editor phased plan + phase-B flat editor increments; later work waited for the post-B3 owner checkpoint | B0–B3 accepted (through the 244th). **The D-076-R003 post-B3 checkpoint PASSED — D-082-R001 ("Post-B3 checkpoint PASSED", 2026-09-20).** The first pass wrongly said "owner review QUEUED" (G3-F3). PE/DR/PC/PV describe the existing flat editor. ✓ |
| D-082 | named inline in §2.3 + `project-control/directives/D-082-max-envelope-first-and-map-drawing/` | Max-envelope-first + map drawing (phase C/D NOT released) | T064/T065/T066/T070 accepted; T078/T079 in rework. ME/DR describe these surfaces. The assessment's "hold has no D-082 subsection" item (§11) is reconciled: §2.3 names D-082 and the record exists. ✓ |
| D-087 | §2.3 (2026-09-24) + `project-control/directives/D-087-parallel-build-3d-cad-pdf/` | 3D massing, CAD/DXF export, phase-C PDF blueprints, CAD write/edit/export as orchestrator packets | Post-dates the assessment. The D-087 packets at `a57bb8de` touch no `apps/web` file (the `b56f3d5b`→`a57bb8de` web diff is only the 11 T078/T079 files). The ledger has no 3D/CAD/PDF rows. ✓ |

P0 is docs-only; it starts no held work and stays within §2 and the releases §2.1–§2.3.

---

## 5. Section-13 verification matrix (finding → fixture/steps → owning later slice)

Assessment §13 lists source-grounded risks to verify **before or alongside** layout work; none is a
claimed live reproduction. Fixtures named below exist at the head unless marked "add".

| §13 finding | Priority | Existing fixture · steps | Owning slice · ledger rows |
|---|---|---|---|
| Report freshness (`ProposalEditor.tsx:73-79,105-137,195-403`) | High | `proposal-editor.test.tsx` stub `stubFetch(checkResponse(attestedReportBody(), 200))` (:20). Steps: Run check → edit a vertex / level / attestation → inspect the report → save and re-select a variation → edit while a check is in flight (add a deferred fetch stub). Expect the stale result to be visibly marked and never saved as current. Verify before repair. | **P4 behaviour task** before visual polish (DB-043(b)). Rows **PC-04, PC-05, PV-01** (the "Changed since check" states); PE-08 (announcements). |
| Sample attribution (`ProposalEditor.tsx:73`; `proposal-draft.ts:421-449`) | High | `rectangleSampleDraft()` rendered by `<ProposalEditor bbl="1000010010">` and a second test BBL (e.g. `1008350041`, used in `lot-outline-map.test.tsx`). Expect identical R5 / wide / 8,000 sq ft seeds today. | **P4 behaviour task.** Rows **PE-10**, PE-02 (cross-ref), PE-01. |
| Generated-option mount (DB-050) | High before mount | `max-envelope-panel.test.tsx` `envelopeBody()` + `REQUEST`, and the production-reachable `lot_geometry_unsupported` / no-candidate test (:231 @b56f3d5b); `e2e/proposal-editor.spec.ts` intercepted routes (stubs, not deployed proof). | **Mount packet** (DB-050(a), DB-051(f)/(g), DB-045). Rows ME-03, ME-04, DR-08. |
| Null-end "in effect … to present" (`RuleEvaluationResult.tsx:279-280`; NoScenarioBlock intro) | Medium | `components/rule-evaluation/__tests__/rule-evaluation.test.tsx` competing-rule fixtures with `effective_to` null. | **P3/P5 + G6 legal review.** PART B LS-E10, LS-C10. |
| Manual fallback copies the query into Street (`AddressResolutionScreen.tsx:220-229`) | Medium | `autocomplete.test.tsx:114` ("routes a source failure to the prefilled manual/Geoclient fallback with the typed text intact"). | **P2 address slice.** Rows AD04, AD01, AD09 (and AD14's dead BBL link, DISCOVERIES). |
| DB-049 drawing issues | Medium | `proposal-outline-draw.test.tsx`, `proposal-outline-map.test.tsx` (both in-flight in M5-T078). Steps: mixed complete/incomplete rows; map loading / fallback / selection; keyboard-only Convert. | **M5-T078 (in rework)**, then P4. Rows DR-05, DR-08, DR-09, M13. |
| Survey no-facts fallback; `DocumentOverlay` null `imageRef` (`lib/surveyReview/model.ts:130-145`) | Medium | `lib/surveyReview/__tests__/model.test.ts` with a zero-fact document; add a null-preview overlay fixture. | **P6 survey.** PART B SR11, SR27. |
| Static "Every value … official-source fact" + shared coverage glosses | Medium | No dedicated `lib/coverage.ts` unit test exists at the head (`lib/__tests__` has none) — add fact / rule / scenario / human-confirmation fixtures at P3 G0. | **P3/P5 vocabulary review.** PART B LS-P13, F03. |
| Print opens non-raw disclosures; mobile hides env/nav-footnote; tiny map attribution (`ReportView.tsx:53-65`; CSS :138, :74-77) | Medium | `e2e/architect-workspace.spec.ts:185-214` already emulates print on view=report (beforeprint, `emulateMedia("print")`, audit-appendix toggle). Extend it with the §7 print-gate assertions. | **P5 report + P7.** Rows SH-01, SH-08, SW-01, SW-02, M01, M11; decisions P5-D1…P5-D6 (§7). |
| Duplicated ZoLa links, location narration, empty success cards, internal strings, legacy future-Evidence | Low | `address-confirm.test.tsx:465-487` (shared ZoLa label + absent-BBL note). | **Cross-cut P2–P6.** Rows AC05, ZC-01; PART B LS-C28. |

---

## 6. Ledger summary + completeness proof

**Exact enumeration command** (worktree root; sections 4–9 = lines 57–923; every table row whose first cell
starts with an inventory id):

```
sed -n '57,923p' docs/UI_DEEP_DIVE_ASSESSMENT.md \
  | grep -oE '^\|[[:space:]]*(SH-|PE-|DR-|PC-|PV-|ME-|SW-|ZC-|LS-P|LS-C|LS-E|LS-F|LS-T|AD|AC|LC|SR|DB|M|A|C|F|E|R)[0-9]+' \
  | sed -E 's/^\|[[:space:]]*//' | sort
```

Total **381**, zero duplicates. Per family:

| Part | Family (section) | Count | | Part | Family (section) | Count |
|---|---|---|---|---|---|---|
| A | SH (§4) | 15 | | B | A (§7.2) | 15 |
| A | PE (§5.2) | 10 | | B | C (§7.3) | 11 |
| A | DR (§5.3) | 23 | | B | F (§7.4) | 8 |
| A | PC (§5.4) | 6 | | B | E (§7.5) | 16 |
| A | PV (§5.5) | 3 | | B | R (§7.5) | 5 |
| A | ME (§5.6) | 17 | | B | LS-P (§8.1) | 16 |
| A | SW (§5.7) | 3 | | B | LS-C (§8.2) | 28 |
| A | ZC (§5.8) | 4 | | B | LS-E (§8.3) | 11 |
| A | AD (§6.1) | 28 | | B | LS-F (§8.4) | 17 |
| A | AC (§6.2) | 11 | | B | LS-T (§8.6) | 15 |
| A | M (§6.3) | 13 | | B | SR (§9.2–9.6) | 62 |
| A | LC (§6.4) | 22 | | B | DB (§9.8) | 22 |
| | **PART A** | **155** | | | **PART B** | **226** |

**PART A after rework A:** 155 rows, id set a bijection with the enumerated PART A ids; all 18 keys in the
packet order on every row; marks, sections, dispositions (16 keep, 139 convert) and replacement refs
unchanged; every L-marked row has non-empty primary state, progressive destination, accessibility, print
destination and proof owner; `python -m json.tool` exits 0. Changed cells: accessibility 155, print 155,
proof_owner 139, open_question 51, protected_meaning 10, primary_state 5, authority 4, current_source 3,
assessed_source 1.

**New anchors verified at the heads** (commands and outputs in the producer report, "Rework A"):
SH-02 `page.tsx:5`; PE-07 `proposal-editor.test.tsx:83-88`; AD15 `PRD.md:96` (§5 step 5); M07
`lot-outline-map.test.tsx:349-360` @b56f3d5b (`:362-373` @a57bb8de); M05 `:418` @b56f3d5b (`:431`); M08
`LotOutlineMap.tsx:694-702`/699; ZC-04 file length 49; ME-05 `max-envelope-panel.test.tsx:120-129` and
`:18`, `:274-291` @b56f3d5b; SH-14 `property-error-boundary.test.tsx:96`; PV-02 `proposal-editor.test.tsx:40-42`;
PV-01/PV-03 `:91-103`; SH-07 `e2e/architect-workspace.spec.ts:126`.

Cross-file completeness (381 ids exactly once across both ledgers, zero orphaned consolidate/retire rows) is
re-checked by the orchestrator at harvest; PART B is owned by a separate producer.

---

## 7. Print and accessibility legend (rework A, HJ-2 / HJ-5)

**What prints today.** The only designed print surface is view=`report`: `ReportView.tsx:67-132`. Print
opens every non-raw `<details>` (`:53-65`); `architect.css:140` hides `.architect-topbar`, `.architect-nav`,
`.architect-property-header`, the inspector, the skip link and buttons inside `.architect-report`;
`architect.css:188` hides the raw tier and audit appendix unless "Include full audit appendix" is checked.
These are the only print rules in `apps/web`. The root-layout disclaimer footer is outside all of them and
prints on every page. A browser print of any other view is not a designed print surface: it applies only the
chrome-hiding rules and opens no disclosures. Each PART A row now says either "Printed today via …",
"Not printed today: …", "Split/partly …" or "Not applicable". PART A result: 3 printed (SH-01, SH-09 when
present, LC22), 3 split/partly (SW-01…SW-03), 11 not applicable (live-region / name / instruction rows),
1 not a designed print element (SH-15), 137 not printed today (proposal, limits, drawing, check, variation,
address, confirm-card, map, legacy-confirm and entry surfaces are not in the brief).

**Explicit P5 decisions (real gaps, not defects fixed here):**

| Id | Gap (source) | Rows |
|---|---|---|
| P5-D1 | The internal-environment identity ("Internal development build" + InternalBanner) sits in `.architect-topbar`, hidden in print (`architect.css:140`), and `.architect-environment` is hidden at ≤700px (`:138`). The "must not be shared outside the engineering team" restriction never reaches paper. | PART B A01, LS-P01; PART A SH-02 |
| P5-D2 | The nav footnote "Preliminary analysis / Professional review required" (`ArchitectShell.tsx:47`) is hidden in print (`.architect-nav`, `:140`) and at ≤700px (`.architect-nav-footnote`, `:138`). | PART B A03 |
| P5-D3 | The property header is hidden in print (`:140`): "Draft analysis", the borough line and the alias "Searched address retained · PLUTO representative address" (`ArchitectEntry.tsx:182`) do not print, while the brief title is the searched label (`:106` → `ReportView.tsx:72`). Draft scope still prints via DevelopmentLimits' "Draft" status. | SH-08 (AC10 related) |
| P5-D4 | No proposal / limits / drawing / check / variation print or export exists. If P5 adds one, each row's print cell lists what it must carry. | PE, DR, PC, PV, ME rows |
| P5-D5 | The single-preliminary-scenario scope sentence, objective and cap_provenance note (`ScenarioWorkspace.tsx:21-26`) do not print; the cap headline does. | SW-01 |
| P5-D6 | The brief prints ScenarioConstraints (`ReportView.tsx:115`) and the remainder's scope note and formula (`CalculationEvidence.tsx:141-148`) without the "association not confirmed / not promoted as property limits" label the scenarios view puts on the same figures (`ScenarioWorkspace.tsx:32-37`). | SW-02 (PART B E16 related) |

**P5 print-gate recipe:** extend `e2e/architect-workspace.spec.ts:185-214` — after `emulateMedia("print")`
on view=report, assert every "printed today" row is visible (e.g. `getByRole("contentinfo", { name:
"Required disclaimer" })`), and record each P5-D decision as an explicit assertion once decided. Not run in
P0 (thin client; no npm/node).

**Accessibility cells.** Each row names what exists (role/name, keyboard/touch path, the region that speaks,
alert vs status, focus rule) and prefixes any proposal with "P0-proposed". Speaking regions in PART A:

| Region | Source | Kind |
|---|---|---|
| Property announcer / rule-eval announcer | `ArchitectEntry.tsx:220` / `:168` | OutcomeAnnouncer (status, polite, atomic) |
| Address announcer | `AddressResolutionScreen.tsx:299` | OutcomeAnnouncer |
| Autocomplete status | `AddressAutocomplete.tsx:217` | visible role=status |
| Editor announcer | `ProposalEditor.tsx:180` | OutcomeAnnouncer |
| Draw announcer / drawing map status | `ProposalOutlineDraw.tsx:178`, `ProposalOutlineMap.tsx:168` (@b56f3d5b) | OutcomeAnnouncer / hidden role=status |
| Max-envelope announcer | `MaxEnvelopePanel.tsx:259` (@b56f3d5b) | OutcomeAnnouncer |
| LotOutlineMap summary + layer status | `LotOutlineMap.tsx:627-629`, `:626` | hidden role=status / visible role=status |
| Legacy lookup / confirm announcers | `PropertyLookup.tsx:260`, `ConfirmScreen.tsx:448` | OutcomeAnnouncer |

**Existing `role=alert` sites — kept as alert unless a reviewed change says otherwise:**
`ArchitectEntry.tsx:222`, `:234`; `AnalysisIdentityNotice.tsx:72`; `app/property/error.tsx:37`;
`ProposalEditor.tsx:413`; `ProposalCheckReport.tsx:215`; `MaxEnvelopePanel.tsx:285` and
`ProposalOutlineDraw.tsx:306` (non-bridged) @b56f3d5b. Several of these also speak through a polite
announcer for the same event (PE-07, PC-06, ME-06, DR-07/DR-11…DR-22): the rows record the duplicate and
allow removal only through a reviewed assistive-technology test. The PART B survey alerts are PART B's.

---

## 8. In-flight re-pin register (G3-A1, HJ-10)

M5-T078 and M5-T079 are in rework at `a57bb8de`; their copy will change again. PART A therefore keeps
these rows pinned at `b56f3d5b` with the flag in `open_question` and re-pins them after each lane is
accepted. No rows are added now for copy still changing.

| Rows | Lane | What is re-pinned |
|---|---|---|
| DR-01…DR-09 | M5-T078 | span, test anchors, accessibility cell (observed `a57bb8de` locations in each row) |
| DR-10…DR-23 | M5-T078 | accessibility cell and proof file (`outline-bridge-api.ts` itself unchanged) |
| ME-01…ME-17 | M5-T079 | span, test anchors (incl. ME-03's e2e authority), accessibility cell |
| M01, M02, M05, M07, M11 | M5-T078 (test file) | proof/authority line anchors in `lot-outline-map.test.tsx` (shift +10…+36 at `a57bb8de`) |

**Copy already visible at `a57bb8de` that will need rows at re-pin (not added now):**
MaxEnvelopePanel "Could not check — this development limit's response broke the binding-or-gap data
contract and was withheld." (`:115-116`) and "…so the value is withheld and this preliminary picture stays
incomplete." (`:144`), plus the aggregate's new "withheld" clause (`:216`); ProposalOutlineDraw's omitted-row
hint ("Convert will include N point(s)… not filled in and will not be included", `:198-204`), "Conversion is
already in progress." (`:206`) and the post-convert omitted-row clause (`:392-393`); ProposalOutlineMap
"Point {i} is selected but has no coordinates yet…" (`:181`).

---

*P0 does not redesign and changes no source/test/copy/rule/assessment file. This reconciliation is the
current baseline; the ledger is the no-loss contract for P1–P7 (assessment §14). Phase labels are the
assessment's; the orchestrator assigns canonical task ids.*
