# M5-T052 producer report — DB-031 multi-lot condo records-view channel + display

One concise evidence pass (report discipline: file:line anchors, no long verbatim
sections). All anchors are at the worktree head. This is a REVISION resubmission:
the prior unit left the printed brief on a SEPARATE profile-only records path; this
revision reconciles the brief and the screen onto the ONE shared outcome ruling,
removes allowance-class vocabulary from the printed records section, and reconciles
the validation evidence to the contract's `services/api` working directory.

§1 is the load-bearing guard-coherence ruling (AS-1, documented FIRST, before any
implementation — see the timing note); §2 is THIS revision unit; §3–§4 are the
channel and display; §5 is preservation + the out-of-scope test routed to the
orchestrator; §6 is proof (command cwd + actual results, worker vs supervisor);
§7 discovery.

## 1. AS-1 — the guard-coherence ruling (the T045 G3-A2 answer, documented FIRST)

ONE derived state, not three parallel conditionals. The outcome token crosses the
api/web boundary as a single literal vocabulary, pinned by tests on both sides.

**When it was recorded (AS-1 timing):** the ruling was written into the CONTRACT
before any implementation checkpoint — the objective + the AS-1 acceptance scenario
in `project-control/tasks/M5-T052.json` ("DESIGN ANSWER REQUIRED FIRST … BEFORE any
implementation checkpoint"), committed at the contract seam `caed4644` (2026-09-19,
"M5-T052 contracted"), which precedes the claim seam `75650f7f` and all code. §1
here re-states that same ruling; it did not originate with the code.

- **Single source of truth (BOTH surfaces):** `deriveCondoSurface(profile, outcome)`
  (`PropertyOverview.tsx:197`) folds the accepted profile fail-safe guard
  (`condoWithholdsAllowances` → `deriveCondoDisplay`, `PropertyOverview.tsx:165,143`)
  and the production per-BBL channel state (`deriveCondoChannelState` /
  `channelWithholdsAllowances`, `condo-records.ts:496,546`) into ONE decision
  (`withholdAllowances`, `showRecords`, `showSubstitution`, `conflict`). The SCREEN
  (`PropertyOverview.tsx:283`) and the printed BRIEF (`ReportView.tsx:46`) BOTH read
  this one function and render the SAME `CondoRecordsChannelSection`
  (`PropertyOverview.tsx:219`, mounted at `PropertyOverview.tsx:311` and
  `ReportView.tsx:97`), so they can never disagree.
- **Ruling by outcome:**
  - resolved single → allow path: substitution proceeds, allowances render, the
    substitution is EXPLAINED as a matched-identity record (entered vs analyzed),
    not a computation.
  - multi-lot → the withhold guard governs; the records view shows the recorded
    base lots UNDER the unchanged fail-safe.
  - unresolved / error → withhold, **no records section, honest absence.**
- **Monotonicity (no weakening of the accepted guard):** the channel may only ADD
  withholding (`withholdAllowances = profileWithholds || channelWithholds`,
  `PropertyOverview.tsx:206`); the profile guard `condoWithholdsAllowances` is
  byte-unchanged and stays fully authoritative. A transport failure / absent route
  is `unavailable`, which never withholds on its own; a profile↔channel
  disagreement fails safe (withhold) and is surfaced (`conflict`).
- **Cross-boundary token pin:** the api emits the resolver's own
  `app.connectors.condo_base_lot.OUTCOME_*` (`condo_records.py:77-84`); the web
  vocabulary equals those literals (`condo-records.ts:43-56`), pinned on both sides —
  `tests/api/test_condo_records_api.py` and web `condo-records.test.ts:135-143`.

## 2. THIS revision unit — the printed brief reconciled to the shared ruling

**The defect this revision fixes.** The prior unit made the SCREEN coherent but left
the printed brief on a SEPARATE, profile-only path: `ReportView` withheld via
`condoWithholdsAllowances(profile)` (profile only) and rendered a bespoke
`CondoResolutionRecords({profile})` component that read the profile multi-lot
CONFLICT alone. That path (a) never consulted the live channel, so a profile↔channel
disagreement and a channel-only multi-lot/unresolved/error were invisible on the
brief, and (b) still spoke allowance-class wording ("no computed allowance",
"allowances are calculated only for an established base lot"). The brief and the
screen therefore keyed records off DIFFERENT sources — the exact G3-A2 incoherence.

**The reconciliation (in-scope files only):**

- `ReportView` now computes the SAME shared decision the screen uses:
  `const condoOutcome = useCondoRecords(bbl); const condo =
  deriveCondoSurface(profile, condoOutcome);` (`ReportView.tsx:45-46`). The withhold
  is now `condo.withholdAllowances` (`ReportView.tsx:47`) — the accepted profile
  guard folded with the channel, monotonic, never weakened.
- `ReportView` renders the SAME `CondoRecordsChannelSection decision={condo}`
  (`ReportView.tsx:97`) the screen renders, placed UNDER `DevelopmentLimits`
  (`ReportView.tsx:91`) so the professional-review fail-safe is ABOVE the records
  section on the brief exactly as on the screen. This section handles all four
  cases from ONE decision: multi-lot records, the allow-path substitution record,
  the profile/channel disagreement notice (`condo-records-conflict`), and honest
  absence (null).
- The bespoke profile-only `CondoResolutionRecords` and its `conflictValueRecordedZoning`
  helper are REMOVED from `PropertyOverview.tsx` (with their now-unused
  `formatValue` / `conflictValueDerivation` / `ConflictValue` imports), collapsing
  the brief and the screen to one records component. The allowance-class vocabulary
  that lived only in that removed component is gone; the surviving
  `CondoRecordsChannelSection` carries RECORD-class wording only (asserted by the
  grep-style negative test, §4).
- `AnalysisIdentityNotice.tsx` unchanged; `condoWithholdsAllowances` /
  `deriveCondoDisplay` byte-unchanged (still the accepted profile fail-safe the fold
  reads).

### Focused disagreement + coherence assertions, `condo-resolution-display.test.tsx`

The former `CondoResolutionRecords`-direct describe block is replaced by a
`CondoRecordsChannelSection`-on-the-brief block driven by `deriveCondoSurface`
(`condo-resolution-display.test.tsx:333-473`):

- multi-lot channel → records section; RECORD-class heading; `not.toMatch(/allowance/i)`;
  no analysis/result words; no computed decimal.
- resolved-single channel → allow path: the substitution record (entered vs
  analyzed), NO records section.
- unresolved / resolver-error channel → honest absence (null).
- **NEW disagreement case:** profile withholds (multi-lot conflict) but the channel
  reports a benign single → `withholdAllowances === true`, `conflict === true`, the
  `condo-records-conflict` notice renders ("differ on this condo",
  "professional-review determination above governs"), and NO records / substitution.
- **NEW coherence case:** a channel-only multi-lot the profile does not carry →
  `conflict === false`, the brief prints those city records (no false disagreement).
- note-only profiles (resolved-single, unresolved, missing-token, unknown-token)
  with a route-absent channel → honest absence, matching the screen.

## 3. SCOPE 1 — channel (AS-2..AS-5); no change this unit

- Route `services/api/app/api/v1/condo_records.py` — `GET /api/v1/properties/{bbl}/condo-records`,
  `include_in_schema=False`, gated on the EXISTING `INTERNAL_RULE_EVAL_ENABLED`
  (absent → generic 404, `condo_records.py:403,177`); ONE mount line in
  `services/api/app/main.py:174` (`include_router`), imported at `main.py:32`.
- BBL normalized BEFORE any I/O (`normalize_bbl`, `condo_records.py:410`); malformed
  → typed 422. Resolver consumed READ-ONLY via injected seams (billing
  `resolve_condo_billing`; UNIT-class BBL via `dtm_condo_soda.resolve` mapped onto the
  SAME outcome vocabulary, `_resolution_from_unit_result`, `condo_records.py:217`).
  No connector edited; no network in tests.
- Document = the route's OWN report shape (no contract change): outcome token,
  billing BBL, every base lot as a RECORD with `recorded_zoning: null`
  (`condo_records.py:289`), the substrate-record of a substitution
  (`_substitution_record`, `condo_records.py:319`), provenance quintuple
  (`_provenance`, `condo_records.py:296`), divergent-zoning notice on multi-lot only.
  A typed resolver failure is a NORMAL 200 `error` document, never a 5xx.

## 4. SCOPE 2 — records-view display (AS-2, AS-3, AS-6)

- Typed client `apps/web/src/lib/condo-records.ts` — `credentials:"omit"`, bounded
  reflected strings, time-bounded + cancellable, fail-closed on unknown outcome /
  undocumented (status,state). Mirrors `record-address.ts`. Suite
  `condo-records.test.ts` (token pin, full transport matrix, provenance carriage,
  the three distinct identifiers, the pure reducer).
- Screen + Brief: the SAME `CondoRecordsChannelSection` (`PropertyOverview.tsx:219`)
  — multi-lot renders "City records for this condo" (RECORD class, no allowance
  vocabulary — the D-073-R006 grep gate, HJ-A3 heading semantics); single renders
  the substitution record; disagreement renders the honest `condo-records-conflict`
  notice; unresolved/error/unavailable → honest absence. Mounted on the screen at
  `PropertyOverview.tsx:311` and on the brief at `ReportView.tsx:97`.

## 5. Preservation / compatibility (AS-7) + out-of-scope routing

- `PropertyOverview` / `AnalysisIdentityNotice` remain importable by their six/three
  named consumers; the only export removed (`CondoResolutionRecords`) was consumed
  ONLY by `ReportView.tsx` (in scope, updated) and the two condo test files —
  never by the five non-test PropertyOverview consumers. The fail-safe guard
  semantics (`condoWithholdsAllowances`) are byte-unchanged — records never unlock
  allowances (AS-6).
- **Consumer sweep (native tools):** the consumers of the condo records testids are
  `PropertyOverview.tsx` (scope), `ReportView.tsx` (scope),
  `condo-resolution-display.test.tsx` (scope, updated), and
  `apps/web/src/components/architect/__tests__/report-view.test.tsx`
  (**OUT of allowed_paths**).
- **ROUTED TO ORCHESTRATOR (known-red until applied) — `report-view.test.tsx`:** its
  "M5-T045 — condo billing-BBL records reach the printed brief" describe block
  (report-view.test.tsx:320-398) asserts the OLD profile-only brief behavior and
  DOES NOT stub the condo-records channel. Because `ReportView` now reads the live
  channel via `useCondoRecords`, these tests must be updated to the shared-decision
  behavior (stub `fetch`, assert under `waitFor`). Exact updates the orchestrator
  should apply, mirroring `condo-resolution-display.test.tsx`:
  1. "prints the resolved single base-lot record AND the computed allowance"
     (~:331): stub the channel `resolved_single_base_lot`; the substitution record
     (`condo-substitution-record`) shows and the computed `wide-street-result`
     still prints; there is NO `condo-resolution-records` on the allow path. (Or
     stub route-absent + keep only the allowance-shows assertion.)
  2. "withholds … MISSING outcome token" (~:349) and "… UNKNOWN outcome token"
     (~:363): stub route-absent so ONLY the profile guard decides; assert
     `wide-street-result` is null (withheld) and NO `condo-resolution-records`
     (honest absence — a note-only profile is not a records case).
  3. "prints the multi-lot condo records …" (~:375): stub the channel
     `multi_lot_set`; assert `condo-resolution-records` + two
     `condo-base-lot-record` under `waitFor`, and the withheld allowance.
  4. The non-condo test (~:393) stays green with a route-absent stub.
  The stale comment at report-view.test.tsx:320-324 (naming `CondoResolutionRecords`)
  should be updated to `CondoRecordsChannelSection` / the shared decision.
- Non-condo render consumers (`development-limits.test.tsx`, `entry.test.tsx`,
  `zoning-context-panel.test.tsx`) use non-condo profiles → channel
  `unavailable`/route-absent → no withhold, no records section → unaffected.

## 6. Proof (AS-8) — documented commands, actual results, with cwd

**Worker validation (THIS session, run from the contract's documented cwd).** All
five documented_test_commands, ruff + api pytest from `services/api` (the api CI
job's cwd), the modularity check from repo root:

- cwd `services/api`: `python -m ruff check .` → **All checks passed!**
- cwd `services/api`: `python -m pytest tests/api/test_condo_records_api.py -q` → **14 passed**.
- cwd `services/api`: `python -m pytest tests/api -q` → **453 passed**.
- cwd `services/api`: `python -m pytest tests/rules -q` → **697 passed**.
- cwd repo root: `python tools/modularity_check.py --check` → **selected 452 files;
  failures 0; warnings 20** (exit 0). None of the 20 warnings are this task's files:
  `PropertyOverview.tsx` (which SHRANK — a component removed), `ReportView.tsx`,
  `condo_records.py`, and `condo-records.ts` are all absent from the list.

**Reconciliation with the supplied supervisor executions (AS-8 honesty).** Any
earlier supervisor execution of the rules/api suites that came back UNSUCCESSFUL is
an invocation artifact, NOT a code failure and NOT a worker pass: `python -m pytest
tests/rules` (and `tests/api`) collected from the REPO ROOT fails with
`No module named 'app'` (the documented cwd artifact — `.claude/rules/CODING_RULES.md`,
last rule). The authoritative evidence is the worker run above, which was executed
from `services/api` and is reproducible this session; the supervisor's wrong-cwd
runs neither confirm nor contradict it. These are held as distinct: unsuccessful
supervisor executions (invocation artifacts) ≠ the worker passes above.

**Root-level lint is out of scope.** `ruff check .` from `services/api` is clean;
this unit did not touch and does not repair any unrelated root-level lint finding
outside `services/api`.

**Web suites — UNVERIFIED locally by policy (thin client; no local npm/npx/node).**
They prove ONLY in CI on the orchestrator's pushed head:
`condo-records.ts` + `condo-records.test.ts`,
`PropertyOverview.tsx` + `ReportView.tsx` + `AnalysisIdentityNotice.tsx` +
`condo-resolution-display.test.tsx`. Web compatibility remains PENDING
orchestrator-captured CI on the pushed head; CI web is EXPECTED RED on
`report-view.test.tsx` until the §5 routed updates are applied by the orchestrator.

## 7. Discovery routing (D-069)

No new out-of-scope product/domain findings this unit. The per-base-lot
recorded-zoning live-propagation remains the documented out-of-scope item carried
from M5-T045 (surfaces as `recorded_zoning: null` honestly today).
