# M5-T036 producer report

Task: DB-016 zoning-context panel in the architect flow + DB-005 ZoLa-link unification.
Producer: frontend-engineer. Branch: task/M5-T036-context-panel. Worktree: wt-m5t036.

Honesty framing (binding): OBSERVATIONS (what I read/ran this cycle) are separated from
CONCLUSIONS (what I infer) and from REVISION HISTORY (process narrative of earlier cycles, not
re-verified state). All web runtime behavior is UNVERIFIED — this is a thin client with no
node_modules; no vitest/tsc/eslint ran locally and none is required here. Web CI on the pushed
head is the only executable authority for web behavior (M5-T023 pattern; AS-6). I do not claim
completion or compliance; the gates decide. CI capture is deferred to the orchestrator seam as
contracted.

## This cycle — evidence-DELIVERY repair only (OBSERVATION; NO implementation change)

No production `.tsx` and no test `.tsx` under allowed_paths changed this cycle. Only this report
file changed.

Root cause being repaired: a prior cycle tried to fix a truncated review packet by EMBEDDING the
full working-tree source of every changed/reference file into this report (former sections
E1–E6). That grew the report to ~890 lines, and the enlarged report was itself dropped by the
aggregate diff cap — so the reviewer received none of it. Appending more embedded source to a
report the cap omits cannot resolve the finding. This cycle therefore:

1. Strips the embedded full-file source blocks so this report stays compact and survives the diff
   cap (this is the report the reviewer must actually receive).
2. Specifies, for the orchestrator, the SEPARATELY-BOUNDED evidence the review packet must carry
   (see "Evidence-delivery plan" below). The complete panel test suite, this report, and the
   targeted ReportView/shared-contract excerpts must reach the reviewer as distinct bounded
   artifacts — not as one oversized report.

## Observable current-tree facts (OBSERVATION — read via the file tools this cycle)

Each row is what the working tree contains NOW, verified this cycle by reading the file. These are
current-tree facts, not revision-history claims. Line counts are as read this cycle.

- `apps/web/src/components/architect/ZoningContextPanel.tsx` — 129 lines, NEW (replaced the
  seeded placeholder). Renders four designation groups from `profile.zoning`: districts /
  commercial_overlays / special_districts via the shared `ZoningValueList`
  (import `@/components/property/ZoningSection`, line 1) and a landmark/historic `<dl>` built from
  `mapped_features` via `mappedFeatureView` (`@/lib/contract`, line 3). One ZoLa link via
  `zolaLotUrl(profile.identity.bbl)` (line 37): link when non-null (testid
  `zoning-context-zola-link`, lines 50–58), honest absent note when null (testid
  `zoning-context-zola-absent`, lines 60–62). Absent flags render `Unknown — not supplied`
  (line 112). Carries none of the development-limits result testids.
- `apps/web/src/components/architect/PropertyOverview.tsx` — 70 lines, MODIFIED. Imports
  `zolaLotUrl` (line 7) and `ZoningContextPanel` (line 12). DB-005: the Site-context card link is
  built from `zolaLotUrl(bbl)` (assigned line 47, rendered line 58, null → no link). Panel mounted
  at line 63 (`<ZoningContextPanel profile={profile}/>`), inside `PropertyOverview`'s returned JSX
  only.
- `apps/web/src/components/address/AddressConfirmCard.tsx` — 259 lines, MODIFIED. DB-005: local
  `ZOLA_BBL_URL_PREFIX` constant + `encodeURIComponent` template removed; link built from
  `zolaLotUrl(canonicalBbl)` (import line 7, assigned line 58, rendered lines 132–149,
  absent note lines 145–148). `canonicalBbl` already passed `validateBblInput` (a strict superset
  of `zolaLotUrl`'s canonical check), so the link renders in exactly the prior cases — an internal
  unification, not a behavior change (CONCLUSION, bounded to reading these lines).
- `apps/web/src/components/architect/__tests__/zoning-context-panel.test.tsx` — 202 lines, NEW
  (replaced the trivial placeholder). Suites AS-1..AS-4 (test names listed under "Tests").
- `apps/web/src/components/address/__tests__/address-confirm.test.tsx` — 452 lines, MODIFIED. Added
  `zolaLotUrl` import (line 4) and two DB-005 migration tests (lines 247–266).
- `apps/web/src/components/architect/__tests__/development-limits.test.tsx` — 526 lines, MODIFIED.
  Added `zolaLotUrl` import (line 16) and a `.architect-map-card`-scoped DB-005 describe block
  (lines 175–200).

Grep evidence (OBSERVATION, this cycle): `zola\.planning\.nyc\.gov` matches zero lines across the
touched `architect`/`address` components — no raw template-string ZoLa URL remains in a touched
file; all ZoLa links resolve through `@/lib/provenance-link`.

Untouched allowed_paths (OBSERVATION, git status): `ProfileViews.tsx`,
`AdditionalZoningFlags.tsx`, `__tests__/workspace.test.tsx` — not modified.

### Diff-vs-base caveat (binding on the reviewer; OBSERVATION)

The task changes are UNCOMMITTED working-tree edits on top of the claim seam `77abdd39`. After the
orchestrator commits them, `git diff HEAD` shows nothing; to see the full task diff, diff against
the pre-change base (`git diff 77abdd39 <orchestrator-commit>` or `git show <commit>`), not HEAD.

### Digest labeling (OBSERVATION — what was actually collected)

I did NOT compute sha256 digests this cycle. I am a thin-client producer limited to the packet's
one documented command; a hash command is undocumented and would stall the run. So this report
carries NO digests — none were collected. Digest binding is done by the orchestrator at the seam
(sha256, LF-normalized per the CRLF-smudge rule) and recorded with the gate/acceptance evidence.
Do not read any digest into this report; there is none to read.

## Print-exclusion decision (AS-4) — DECISION, evidence-bound (verify in source, not prose)

DECISION: the panel is EXCLUDED from the printed brief. Evidence (current tree):
- `ReportView.tsx:11` imports only `PropertyIssuesSummary` from `./PropertyOverview` — NOT the
  `PropertyOverview` component that mounts the panel. `ReportView` never renders `<PropertyOverview>`
  or `<ZoningContextPanel>`.
- The brief renders its own zoning surface instead: `ReportView.tsx:79` `<ZoningSection …/>` and
  `ReportView.tsx:80` `<AdditionalZoningFlags …/>` inside `#brief-zoning` (lines 77–81).
- Mounting the panel there would duplicate that surface in print; the brief already carries every
  designation + mapped-feature table. So the panel stays an overview affordance only.
- Repo-wide, `ZoningContextPanel` appears only in its own file, `PropertyOverview.tsx:12`+`:63`, and
  the panel test — no other mount (OBSERVATION, grep this cycle).
Both directions are asserted at runtime by the AS-4 tests (panel present via `PropertyOverview`,
absent via `ReportView`).

## Tests written (OBSERVATION — names/assertions; results UNVERIFIED until CI)

`zoning-context-panel.test.tsx` (accepted M1-T005 fixture, BBL 1000010010, Governors Island
split-zone lot):
- AS-1: both split-lot districts (R3-2 + C4-1), special district GI, landmark + historic values
  render; per-value provenance disclosures for districts and flags; a populated commercial overlay
  ("C1-4" with a mirrored `overlay1` provenance record) renders value + disclosure; none of the
  development-limits result testids appear.
- AS-2: empty commercial-overlay array → explicit empty text; all three arrays emptied → three
  empty texts; `mapped_features=[]` → two "Unknown — not supplied" rows, no disclosure offered,
  labels still visible.
- AS-3: canonical BBL → exactly `https://zola.planning.nyc.gov/bbl/1000010010`, `target=_blank`,
  `rel=noopener noreferrer`, no absent note; non-canonical BBL ("12345") → no link, absent note
  shown, no heading anchor.
- AS-4: `PropertyOverview` mounts the panel; `ReportView` does not.

DB-005 helper-migration additions (results UNVERIFIED):
- `address-confirm.test.tsx` (lines 247–266): rendered `zola-link` href == `zolaLotUrl(canonical)`;
  non-canonical BBL → `zolaLotUrl` null, no `zola-link`, `zola-link-absent` shown.
- `development-limits.test.tsx` (lines 175–200): PropertyOverview `.architect-map-card` link href
  == `zolaLotUrl(bbl)` with target/rel; non-canonical BBL → no map-card link. Scoped to
  `.architect-map-card` so it never blurs with the panel's own link (D2).

I did NOT run these tests; I cannot assert they pass. CI on the pushed head decides (AS-6).

## The one command I ran (OBSERVATION)

`python tools/modularity_check.py --check`, this cycle → `selected 441 files; failures 0;
warnings 19`. All 19 warnings name pre-existing files (api connectors, agent_supervisor, one
apps/web lib file `surveyReview/types.ts`); NONE is a file this task touched. AS-7 PASS for the
documented command (CONCLUSION, bounded to that output). This is the ONLY command I ran; no
npm/npx/node/vitest ran locally.

## Evidence-delivery plan for the review packet (COORDINATION with the orchestrator)

The prior finding was an evidence-TRANSPORT defect, not an implementation defect. To let the
reviewer evaluate provenance, absence handling, and print behavior, the review packet the
orchestrator assembles must carry these as SEPARATELY BOUNDED artifacts (not concatenated into one
oversized report that the diff cap drops):

1. The COMPLETE panel test suite `apps/web/src/components/architect/__tests__/zoning-context-panel.test.tsx`
   (202 lines) — as its own bounded artifact / direct file read, whole, not excerpted.
2. THIS compact report — small enough to pass the diff cap intact.
3. Targeted READ-ONLY excerpts the reviewer needs but which are outside allowed_paths (so they
   never appear in the task diff): `ReportView.tsx:10-11,69,77-81` (print-exclusion proof);
   `components/property/ZoningSection.tsx` `ZoningValueList` (shared list + empty text + per-value
   `ProvenanceDisclosure`); `lib/contract.ts` `mappedFeatureView`/`MappedFeatureView`;
   `lib/provenance-link.ts` `zolaLotUrl`; `lib/provenance.ts`
   `provenanceById`/`resolveFactProvenance`; `components/property/ProvenanceDisclosure.tsx` props.
   These are the exact contracts the panel consumes by import; the reviewer confirms faithful use.
4. Digests (sha256, LF-normalized) computed at the seam and recorded with the gate evidence — see
   "Digest labeling"; none are collected here.

Because items 1 and 3 are the complete suite and read-only reference files, the cleanest transport
is to let the reviewer read them directly at the pinned head rather than embed them; the point of
the finding is that embedding them in the report does not work.

## Discoveries surfaced, NOT fixed (D-069 routing — preserved verbatim)

**D1 (product):** The client profile also carries mapped features `firm07_flag`, `pfirm15_flag`,
`transitzone`, `splitzone`, `zonemap` (observed in the M1-T005 fixture `zoning.mapped_features`).
This panel scopes to districts / commercial overlays / special districts / landmark / historic per
the objective; FIRM flood flags surface today only via `AdditionalZoningFlags` (absent-only) and the
zoning-tab `ZoningSection` full table. Fuller overview parity (e.g. flood flags on the overview) is
a follow-up increment, not this packet — not plumbed here (label-display-only + no-contract-change
boundary holds). Route to `docs/DISCOVERY_BACKLOG.md` at the seam.

**D2 (UI):** The overview now shows two ZoLa affordances — the Site-context map-card link
(PropertyOverview) and the panel heading link (ZoningContextPanel), both validated via `zolaLotUrl`.
Both are kept because output 3 requires fixing the Site-context inline link AND output 1 requires the
panel's own link; whether to consolidate to one is a design-director call. Route as a discovery,
not fixed in-packet. The `development-limits.test.tsx` DB-005 tests are `.architect-map-card`-scoped
so the two affordances are asserted independently.

## Scope boundary honored (OBSERVATION)

- Edits confined to allowed_paths under `apps/web/**` plus this report. No `services/api/**` and no
  `apps/web/src/lib/**` file edited (DB-005 uses the EXISTING `zolaLotUrl` helper by import only).
  Parallel-loop isolation vs the M5-T035 api loop (D-071-R001) is intact (AS-5).
- Label-display-only boundary (owner ruling 2026-09-17) honored: no computation, inference,
  defaulting, api/contract change, or new fetch. Every value is read straight from the client-side
  `PropertyProfile`.

## Claims discipline (D-059-R006)

This panel displays designations already fetched; it does not close an MVP percentage and is not
context "parity done". FIRM/transit/split-zone/zonemap mapped features are not on this overview
panel (see D1). The computed-answer engine remains the differentiator.

## Revision history (PROCESS NARRATIVE — not re-verified current-tree state)

- Rev 1: built the panel + DB-005 unification + panel suite.
- Rev 2: added focused DB-005 migration coverage to `address-confirm.test.tsx` and
  `development-limits.test.tsx`, and a populated-overlay case to the panel suite (no production
  behavior changed).
- Rev 3: embedded full-file source (E1–E6) into this report to defeat a truncated packet — which
  instead pushed the report past the aggregate diff cap so the reviewer got nothing.
- This cycle: removed the embedded source, made the report compact, and specified the
  separately-bounded evidence plan above. No code changed.

---

END OF REPORT. Web behavior stays UNVERIFIED until the orchestrator supplies web CI results on the
pushed head tied to the resulting commit (AS-6). This cycle changed no implementation; it repairs
evidence delivery only. Do not accept or merge on this report — the gates decide.

---

## Addendum 2026-09-17 — test-query fix only (run persistent2-local-02)

OBSERVATION. Web CI on the harvested head reported ONE failing suite —
`src/components/architect/__tests__/zoning-context-panel.test.tsx` — with
`TestingLibraryElementError: Found multiple elements with the text: R3-2` (AS-1 test 1) and the same
for `C1-4` (AS-1 populated-overlay test); summary `1 failed | 40 passed (41)` test files.

ROOT CAUSE (evidence-bound, verify in source). Each designation value renders in the visible
`.zoning-chip-code` div AND in its `ProvenanceDisclosure` rows — `original_value`
(`ProvenanceDisclosure.tsx:55`) and `normalized_value` (`:57`) — so the shared list markup carries
the value text on more than one element. `getByText(<exact value>)` therefore matches multiple
elements and throws. The PRODUCTION panel is correct: the values render, which is why multiple
matched. This is a test-query defect, not a component defect.

FIX (test file only). In `zoning-context-panel.test.tsx` the six single-match designation-VALUE
queries — `R3-2`, `C4-1`, `GI` (AS-1 line ~48), `INDIVIDUAL LANDMARK`, `Governors Island Historic
District`, and `C1-4` (AS-1 populated overlay) — were changed from
`getByText(v)` → `getAllByText(v).length` asserting `toBeGreaterThanOrEqual(1)`. `getAllByText`
throws on zero matches, so each stays a REAL presence assertion; none was deleted, weakened to a
null-tolerant `queryBy` form, or otherwise relaxed. The `"Source for <value>"` disclosure-summary
labels, the honest empty-text assertions, the `getAllByText("Unknown — not supplied")` count, and
all `getByTestId`/`queryByTestId` queries are unique single matches and were left unchanged.

No production file and no other test file changed this cycle. `python tools/modularity_check.py
--check` re-run below. Web behavior stays UNVERIFIED — CI on the re-pushed head is the executable
authority.
