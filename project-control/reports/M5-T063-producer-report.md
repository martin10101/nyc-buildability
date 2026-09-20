# M5-T063 producer report — web condo rider cluster

Task: DB-036(a) `boundedZoningDistrict` sanitizer precondition + DB-036(e)/DB-038(c)
recorded-zoning status parsing & divergence/gap gating + DB-042 (c)/(d)/(e) announcer &
wording riders + DB-038(b) label hygiene. Frontend packet; additive-only to the shared
sanitizer lib.

Base (claim seam): `ae8be2ed`. Scope: the 11 allowed paths only; PropertyOverview.tsx is in
scope but its logic is UNCHANGED (its export surface/props stay byte-compatible for the
ArchitectEntry / ProfileViews / PropertyFacts / ReportView / ScenarioWorkspace consumers and
the LIVE M5-T060 lane). `services/api/**`, `packages/contracts/**`, `apps/web/src/test-support/`,
and every T060-lane file are read-only and untouched. No new dependency.

Revision note — THIS unit is REPORT-ONLY and is an EVIDENCE REPAIR. It touches NO source or test
file. The prior revision embedded the full verbatim review spans INTO this report; that pushed the
report's own contents beyond the aggregate patch cap (and violated the packet's REPORT DISCIPLINE
input, which forbids embedding long verbatim sections). This revision removes those duplicated
excerpts and instead SPECIFIES the replacement supervisor packet — four separately bounded,
digest-bound sections the supervisor assembles at harvest as their own artifact (see "Replacement
supervisor packet" below), keeping this report lean. The anchors-only handoff before that failed the
opposite way (nothing to inspect); this specification is the third, cap-safe form. A PRIOR revision
fixed ONE incorrect test assertion in `bounded.test.ts` (hostile-markup case) — the sanitizer charset
was already correct and is UNCHANGED; only the expectation was wrong. That corrected assertion is
PRESERVED unchanged here; this unit re-touches neither `bounded.ts` nor `bounded.test.ts`. Detail
under "Rework correction" below.

## IMPLEMENTATION

1. **DB-036(a) sanitizer precondition** — `apps/web/src/lib/bounded.ts`
   - New `MAX_ZONING_DISTRICT_LENGTH = 32` (:22), `NON_ZONING_DISTRICT_CHARS` regex (:35),
     and `boundedZoningDistrict(value, max)` (:90–99). Charset `[A-Za-z0-9/-]` ADMITS the
     slash a mixed-use district carries (`M1-5/R7-2`) plus hyphen and suffix letters
     (`R10H`, `C6-4`); anything else is dropped, the result is length-capped, empty → `null`.
   - Every pre-existing helper (`boundedText`, `boundedToken`) is byte-unchanged — verified
     by the AS-1 spec-pin test that `boundedToken("M1-5/R7-2")` STILL strips the slash
     (`bounded.test.ts` "still strips the '/' …", :64). This is the whole point of the
     new helper: identifiers and districts are different vocabularies (the same
     sanitizer-boundary lesson as `boundedTimestamp`).
   - Wired in `apps/web/src/lib/condo-records.ts` `baseLotRecords()` (:346–349): recorded
     zoning now flows through `boundedZoningDistrict(record.recorded_zoning, 32)` (:349),
     NOT `boundedToken` (which would strip the slash and corrupt the district).

2. **DB-036(e)/DB-038(c) status parsing + honest gating**
   - `condo-records.ts` already parses per-lot `recorded_zoning_status` (:350–355, falls
     back to `"recorded"`/`"unknown"` derived from the district) and top-level
     `recorded_zoning_dependency` (:535–538). This packet REWORDED the
     `divergentZoningNotice` interface doc (:210–216) from "permanent no-collapse boundary
     notice" to "dormant unless zoning is ACTUALLY recorded" — matching the existing
     PropertyOverview gate, which is unchanged.
   - The divergence/gap GATING lives in `PropertyOverview.tsx` (:273–320, unchanged):
     `anyZoningRecorded` / `anyZoningUnknown` derive from the parsed per-lot status; the
     divergent notice renders only when zoning is actually recorded (:319) and the ZTLDB
     gap note only when at least one lot's zoning is unknown (:320), with partial-vs-total
     copy (:285–287).

3. **DB-042(c)/HJ-3 announcer specificity** — `apps/web/src/lib/rule-evaluation.ts`
   - New `CONDO_BASE_LOT_UNRESOLVED_ANNOUNCEMENT` (:517–518) and a reworked
     `announcementForRuleEvaluation` "evaluation" branch (:520–548): a well-formed
     `substrate_substitution` stamp (real, different analyzed base lot) announces the
     entered-vs-analyzed base-lot specifics; a `fail_safe_reason === "condo_base_lot_unresolved"`
     announces the condo/site-confirmation specifics; everything else falls back to the
     generic classifier. Screen-reader text no longer trails the visible label.

4. **DB-042(d)/(e) wording + inline definitions** — `apps/web/src/components/architect/AnalysisIdentityNotice.tsx`
   - The substitution `<p>` (:66) now defines "condo billing lot (the single tax lot a condo
     is billed under)" and "the land parcel the city records as this condo's base" inline on
     first use, and uses the consistent-domain "a city record of the documented resolution,
     not a computed allowance" framing shared with the condo-records section. The
     `stampLegitimate` correspondence gating and the `role="alert"` withhold branch are
     BEHAVIORALLY UNCHANGED (copy-only edit inside the already-legitimate stamp branch).

5. **DB-038(b) label hygiene** — `apps/web/src/components/address/__tests__/address-confirm.test.tsx`
   - The S11 `describe` label (:809) now names its true scope (rider-i's title/aria length
     cap was superseded by rider-c a11y honesty), and the block comment is corrected.

## Rework correction (this revision)

- `bounded.test.ts`, "strips the markup delimiters …" case (:83–90): the previous expectation
  `boundedZoningDistrict("<script>M1-5/R7-2</script>") === "scriptM1-5/R7-2script"` was
  WRONG. The charset `[A-Za-z0-9/-]` intentionally admits `/`, so the `/` inside the
  closing tag `</script>` survives: the true residue is `scriptM1-5/R7-2/script`. The
  markup DELIMITERS `<` and `>` are still stripped (no tag can form; React escapes the
  reflected text regardless), so the residue is inert plain text.
- Fix is TEST-ONLY: the expectation is corrected to `scriptM1-5/R7-2/script` (:90) with a
  comment explaining why the closing-tag slash survives. `bounded.ts` is NOT changed —
  dropping the slash would break the required mixed-use behavior (AS-1) and the byte-exact
  `M1-5/R7-2` rendering the two other suites pin. This corrected assertion is PRESERVED.

## Boundary answers (acceptance scenarios)

- **AS-1 (sanitizer):** admits `M1-5`, `R7-2`, `R6`, `R10H`, `C6-4`, and `M1-5/R7-2`
  (slash byte-exact); bounds/rejects markup, control chars, over-length, non-strings, empty
  (`bounded.test.ts` boundedZoningDistrict suite). Existing helpers byte-unchanged
  (boundedToken slash-strip pin). PASS by spec (CI proves the run — see verification).
- **AS-2 (honest gating):** no recorded zoning → divergent notice ABSENT + ZTLDB gap note
  in plain language (`condo-resolution-display.test.tsx` "(e) NO recorded zoning", :754–764);
  recorded present → district renders slash-intact and the divergent notice gates on ACTUAL
  divergence with a partial gap note ("(e) MIXED zoning", :766–779).
- **AS-3 (announcer):** condo_base_lot_unresolved names "condo billing lot" +
  "site-definition confirmation"; substitution names both BBLs + "not a computed allowance";
  both are strictly more specific than the generic strings and carry no "verified"/"best"
  wording (`rule-evaluation.test.ts` :498–539).
- **AS-4 (wording/defs):** both base-lot surfaces use consistent "city record" domain
  wording; billing/base defined inline on first use; the withhold guard direction and
  `stampLegitimate` gating are behaviorally unchanged (the record branch fires NO
  `role="alert"` — `analysis-identity-substitution.test.tsx` :75–92; the pre-existing
  both-directions withhold specs in that file, :94–170, are untouched).
- **AS-5 (hygiene):** the S11 describe names its true scope; no empty spec files were added;
  DOM access uses typed testid queries (`getAllByTestId` → `HTMLElement[]`, `.textContent`),
  no `querySelectorAll` needing an explicit generic.
- **AS-6 (preservation):** PropertyOverview.tsx logic and export surface unchanged (props
  byte-compatible; not in the modified-file set); modularity exit 0 (my run below). Full web
  suites green in CI is PENDING the controller's CI run at the pushed head (thin client — not
  claimed here).

## Evidence — attributed

- **My own command (this run), cwd `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t063`:**
  `python tools/modularity_check.py --check` → `selected 467 files; failures 0; warnings 20`
  (re-confirmed this run; unchanged — this unit edits only this Markdown report, which
  modularity does not gate). All 20 warnings are pre-existing files OUTSIDE this packet's
  scope (surveyReview/types.ts, services/api/**, tools/agent_supervisor/**, etc.); none is a
  file this task edited. This is the packet's only documented local command.
- **NOT run by me (thin client, forbidden):** no `npm`/`npx`/`node`. The web vitest suites
  (bounded, condo-records, rule-evaluation, condo-resolution-display,
  analysis-identity-substitution, address-confirm) are NOT executed locally; their behavior is
  asserted by the mutation-sensitive specs mapped below and PROVES ONLY in CI on the pushed head.
  Any earlier "successful modularity" evidence produced by the supervisor during the build is
  the SUPERVISOR's run, not mine; the run recorded in this report is my own, above.
- **Web verification: PENDING.** Do not treat web behavior as verified until the authorized
  controller supplies the CI result for the pushed candidate SHA.

## Missing evidence for supervisor harvest — section map (BLOCKS resubmission; supervisor-assembled at harvest)

This report ALONE does not satisfy the harvest, and neither does a section map or a bare file-digest
list: the harvest packet must carry the ACTUAL bounded CONTENTS of Sections A–C below (each file's
real bounded diff — relevant spans, never a whole-file dump — plus, for Section C, the relevant test
assertions), each bound to its file's LF-normalized sha256. The two prior handoffs failed in opposite
directions — anchors-only (nothing to inspect), then full verbatim spans embedded INTO this report
(over the aggregate patch cap). A producer cannot resolve the remainder here: this is a SINGLE report
file (embedding all of A–C repeats the over-cap failure), a thin client cannot pin the LF-normalized
post-checkout sha256 the sections must bind to (CRLF smudge — CODING_RULES), and no additional artifact
path is in scope. So Sections A–C must be assembled by the supervisor at harvest as their own
separately bounded artifact(s) (the `M5-T053-source-sections.md` division of labor). This report is
Section D. Resubmission is HELD until the harvest actually INCLUDES Sections A–C's contents. All
anchors below are vs the claim-seam base `ae8be2ed` and were re-verified against the working tree this
run (bounded.ts, condo-records.ts, rule-evaluation.ts, PropertyOverview.tsx spans confirmed).

- **Section A — sanitizer additive diff** (`apps/web/src/lib/bounded.ts`): THREE added spans only —
  `MAX_ZONING_DISTRICT_LENGTH` (:22), the `NON_ZONING_DISTRICT_CHARS` comment+regex (:32–35), and the
  complete `boundedZoningDistrict` helper incl. JSDoc (:75–99). Bound the section to those three
  spans. Every pre-existing export is byte-unchanged and needs no excerpt: `MAX_REFLECTED_TEXT_LENGTH`
  (:20), `MAX_TOKEN_LENGTH` (:21), `CONTROL_CHARS` (:27–30), `boundedText` (:41–57), `boundedToken`
  (:64–73) — the `boundedToken` slash-strip spec-pin (Section C) proves the token helper is untouched.

- **Section B — condo-records + rule-evaluation changes**:
  - `apps/web/src/lib/condo-records.ts`: import add (:38); `divergentZoningNotice` interface-doc
    reword permanent→dormant-unless-recorded (:210–216); `baseLotRecords()` zoning wiring + status
    derivation (:346–355); `documentView` `recordedZoningDependency` parse (:535–538).
  - `apps/web/src/lib/rule-evaluation.ts`: `CONDO_BASE_LOT_UNRESOLVED_ANNOUNCEMENT` (:517–518) + the
    reworked `announcementForRuleEvaluation` "evaluation" branch (:520–548).
  - `apps/web/src/components/architect/AnalysisIdentityNotice.tsx`: copy-only substitution `<p>` with
    inline billing/base definitions + consistent "city record … not a computed allowance" wording
    (:64–68); the `stampLegitimate` correspondence gate (:54–61) and the `role="alert"` withhold
    branch (:72–79) are BEHAVIORALLY UNCHANGED (copy edited only inside the already-legitimate branch).

- **Section C — existing status/dependency parser + PropertyOverview divergence/gap gates, with the
  relevant assertions**:
  - `apps/web/src/components/architect/PropertyOverview.tsx` (export surface/props byte-compatible;
    NOT in the modified set — cited so the reviewer confirms the parsed per-lot status feeds the
    gates): `anyZoningRecorded`/`anyZoningUnknown` derivation + `zoningGapNote` partial-vs-total copy
    (:273–287); render gates — divergent notice on `anyZoningRecorded`, gap note on `anyZoningUnknown`
    (:319–320).
  - Mutation-sensitive assertions, each bounded to its `it(...)`/`describe(...)` block:
    `bounded.test.ts` boundedToken slash-strip pin (:64–66) + the PRESERVED corrected markup assertion
    + caps/null cases (:83–104); `condo-records.test.ts` per-lot status/dependency parse (:439–461) +
    the slash-survives revert-killer (:463–479); `rule-evaluation.test.ts` announcer specificity /
    not-generic / no "verified"/"best" (:512–541); `condo-resolution-display.test.tsx` (e) NO-zoning
    (notice absent + total gap) and (e) MIXED-zoning (notice present + partial gap) (:754–779);
    `analysis-identity-substitution.test.tsx` inline-defs + consistent wording + NO `role="alert"` on
    the record branch (:75–91), with the both-directions withhold specs (:94–170) untouched;
    `address-confirm.test.tsx` S11 describe scope (:809). Fixtures
    (`test-support/rule-evaluation-fixtures.ts`: `condoUnresolvedDoc`, `substitutionStampDoc`,
    `SUBSTITUTION_*_BBL`) are READ-ONLY and pre-existing — not added here.

- **Section D — this producer report**, in full.

**Digest binding (supervisor step, at harvest).** Thin client: the producer pastes no raw sha256 — a
checkout smudges CRLF, so every digest must be LF-normalized at the harvest checkout (CODING_RULES),
which the harvest owns. At harvest the supervisor pins the LF-normalized sha256 of each file below, in
section order, and binds each bounded section to its file digest:
`apps/web/src/lib/bounded.ts`, `apps/web/src/lib/condo-records.ts`,
`apps/web/src/lib/rule-evaluation.ts`,
`apps/web/src/components/architect/AnalysisIdentityNotice.tsx`,
`apps/web/src/components/architect/PropertyOverview.tsx`,
`apps/web/src/lib/__tests__/bounded.test.ts`, `apps/web/src/lib/__tests__/condo-records.test.ts`,
`apps/web/src/lib/__tests__/rule-evaluation.test.ts`,
`apps/web/src/components/architect/__tests__/condo-resolution-display.test.tsx`,
`apps/web/src/components/architect/__tests__/analysis-identity-substitution.test.tsx`,
`apps/web/src/components/address/__tests__/address-confirm.test.tsx`, and this report.

## Handoff

Base (claim seam): `ae8be2ed`.

**Cumulative working-tree state vs base (NOT all this unit's):** the working tree carries 10 modified
source/test files — `bounded.ts`, `condo-records.ts`, `rule-evaluation.ts`, `AnalysisIdentityNotice.tsx`,
their five test files, and `address-confirm.test.tsx` — PLUS this report. Those 10 code/test files are
the CUMULATIVE build from the prior build unit(s). No prior-unit baseline commit was supplied, so this
report does NOT re-attribute the 10 files to this unit; they are presented as the cumulative tree, and
the section map above documents them for review.

**This unit's claim (report-only):** it changed ONLY this producer report — reframing the section map
to IDENTIFY the missing harvest evidence and record why the producer cannot supply Sections A–C's
digest-bound contents here (single report + aggregate patch cap + thin-client LF-normalized-digest
limit + no additional artifact path in scope), and marking the unit BLOCKED pending that supervisor
harvest-assembly. It re-touched no source or test file, so the corrected `bounded.test.ts` markup
assertion and the accepted withhold-guard direction are preserved as-is. Modularity re-confirmed exit
0 this run (467 files / 0 failures / 20 warnings, all pre-existing out-of-scope).

Envelope fields carry the exact claim-seam identity per the S8.3 checkpoint contract: this is a
report-only unit, so HEAD is unmoved and `current_sha` == `starting_sha` == the claim seam
`ae8be2ed2e62b4d578b35416df0fd56e455cb7a8` (the cumulative code/test changes are the working tree, not
a new commit). Supervisor-owned remaining steps: assemble Sections A–C as separately bounded,
digest-bound artifacts and pin each cited file's LF-normalized sha256 at harvest (list above); commit +
push; run the web CI at the pushed candidate SHA to satisfy AS-6 (thin client — web behavior proves
ONLY in CI); then G0/G2/G3/G4 + the reviewer wave; resubmit only once the harvest includes Sections
A–C. **Web verification is PENDING that controller CI at the pushed candidate SHA — not claimed here;
no local web commands were run; no self-accept.**

## Discovery routing (D-069)

No out-of-scope findings surfaced during this rework.
