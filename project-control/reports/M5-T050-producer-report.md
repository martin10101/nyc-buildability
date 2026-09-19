# M5-T050 producer report — DB-033 confirm-arc polish + test hardening (riders a–i)

One concise evidence pass (REPORT DISCIPLINE): files + line anchors, no embedded
verbatim sections. **This checkpoint is a REVISION of rider a only** (the record-line
CLS mechanism and its tests, plus this report). It responds to the gate feedback that
the prior reservation (a) only APPROXIMATED the real line's height from a same-length
stand-in — which wraps differently at the narrow widths and still shifts the Continue
button — (b) collapsed on a delayed no-line settle, and (c) was described as
"height-equivalent" without proof. Riders b–i are UNCHANGED from the prior increment.
Web behavior is NOT claimed verified — it proves only in CI on the pushed head (thin
client, no local npm/npx/node). Riders are not claimed "all verified" here.

## IMPLEMENTATION — this revision (rider a mechanism + tests)

**Rider a (CLS) — record note moved OUT of the interactive flow; no height guess
anywhere.** `apps/web/src/components/address/AddressConfirmCard.tsx`.

What changed and why:

1. **The in-flow reservation is REMOVED entirely.** Deleted the position-4 slot +
   invisible reservation block, the `RECORD_ADDRESS_RESERVE_FALLBACK` constant, and the
   `recordReserveSample` derivation. Any reservation at that position (between the
   entered note and the Continue block) can only *approximate* the real line's wrapped
   height — the record address and how it wraps are unknown until the channel settles —
   so a same-length stand-in wraps differently at the narrow supported widths and still
   nudges Continue; and a delayed settle to no-line collapses the reservation. No
   approximation and no residual-movement bound is asserted anywhere now.
2. **The record note renders as the card's LAST child** (after the Continue /
   Not-my-property actions and the `<Meta>` correlation-id footer; `AddressConfirmCard.tsx`
   ~400–430). This is the CLS-neutral mechanism that needs no height guess and is
   correct-by-construction: a late insert placed *below* every settled/interactive
   element cannot move any of them — at ANY width, for ANY wrapping, and for a record
   address of ANY length. It is the only mechanism that satisfies BOTH required
   properties at once — stable-when-shown-including-materially-different-wrapping AND
   the clean absent presentation — because the alternatives each fail one: an in-flow
   reserve is an approximation; a max-height reserve leaves a permanent gap that
   violates the absent presentation; an in-place overlay overlaps the block below.
3. **The absent presentation is preserved byte-for-byte.** When the outcome is non-shown
   (loading / equal / absent / error / route-absent) nothing renders here at all — no
   line and no reserved box — so the card is identical to one that never carried a
   record channel. A delayed non-shown settle therefore collapses nothing (no shift).
4. `RECORD_ADDRESS_NOTE` / `RECORD_ADDRESS_WHY` constants are retained (`~28–35`), with
   the comment updated to drop the (now-gone) reservation reference; the shown line and
   the rider-d why note are byte-identical in content to the prior increment.

**Tests** — `apps/web/src/components/address/__tests__/address-confirm.test.tsx`,
S11 rider-a group. They assert the ACTUAL stability mechanism (DOM position + pure
append), not "no min-height" or "shared prose":
- **Immediate shown**: the note FOLLOWS `confirm-continue` (`compareDocumentPosition` →
  `DOCUMENT_POSITION_FOLLOWING`) AND is `card.lastElementChild`; no
  `record-address-reserved` / `record-address-slot` element exists in any state; the
  rider-d why note is intact.
- **Delayed shown**: loading has no note and no reservation; after the delayed resolve
  the Continue action is the SAME node with byte-identical `outerHTML`, the record note
  is APPENDED as the new last child, and every pre-existing direct child keeps its
  identity and order (a `childIds` helper, robust to `LotOutlineMap`'s async internals
  since its root `<section data-testid="lot-outline">` is stable) — a structural proof
  that nothing above the CTA moved.
- **Immediate absence**: no note and no reserved box (as today).
- **Delayed non-shown `it.each`** `{equal, absent, error(502), route-absent(404)}`:
  loading → settle, no note ever, no reserved box, and the card's direct children are
  byte-stable across the settle (collapse-free).

Rider a introduced no change to the record-address channel contract, the equality gate,
or the card's props/exports (byte-compatible for the architect/property consumers).

## Honest limitations (what jsdom cannot prove; a reviewer decision to weigh)

- **jsdom has no layout engine.** These tests assert the STRUCTURAL guarantee — the note
  is positioned below every settled element and arrives as a pure append — which *is*
  the mechanism (content below all settled elements cannot shift them). They do NOT
  measure pixels. The definitive proof that the Continue CTA's Y-position is byte-stable
  across the resolve at the supported narrow widths, including a long permitted record
  address, is a real-browser measurement and is OUTSTANDING (see below). No height
  equivalence and no residual-movement bound is claimed from jsdom.
- **Reading-order / IA tradeoff — surface for the visual-quality and human-journey
  reviewers.** The record note now renders as the card's LAST element (after the actions
  and the correlation-id footer), moved out of its former position among the three
  identity lines (matched / entered / city-record) that the M5-T047 HJ walkthrough
  praised. That relocation is the cost of a correct-by-construction CLS-neutral mechanism
  that also keeps the absent presentation clean. Reviewers should confirm the bottom
  placement is acceptable, or direct a different out-of-flow placement; a reserved-slot
  variant cannot meet both required properties.

## Per-rider file/line map (all nine)

- **a** CLS (REVISED this checkpoint): `AddressConfirmCard.tsx` — reservation block +
  `RECORD_ADDRESS_RESERVE_FALLBACK` + `recordReserveSample` REMOVED; record note now the
  card's last child (~400–430); `RECORD_ADDRESS_NOTE`/`WHY` (~28–35, comment updated).
  Tests `address-confirm.test.tsx` S11 rider-a group (immediate-shown last-child,
  delayed-shown pure-append, immediate-absence, delayed non-shown `it.each`).
- **b** a11y (unchanged): `AddressConfirmCard.tsx` (`role="img"` + aria-label on
  `<strong>`); tests `address-confirm.test.tsx` rider-b + S9 differ case.
- **c** copy (unchanged): `AddressConfirmCard.tsx` (conditional entered-note); tests
  `address-confirm.test.tsx` rider-c.
- **d** why-they-differ (unchanged): `AddressConfirmCard.tsx` (`record-address-why`);
  tests rider-d. (Now rendered inside the relocated record note.)
- **e** equality-gate de-vacuation + exact-512 boundary (unchanged; test-side):
  `address-search.test.ts` length-bound cases; guard `address-search.ts` (`:312-320`,
  `GEOSEARCH_RESOLVE_INPUT_MAX_LEN:220`).
- **f** stale docstring names record-address channel (unchanged; comment-only):
  `services/api/app/api/v1/lot_geometry.py` module docstring.
- **g** RA-3 binding reason (unchanged; or-tail removed): `services/api/tests/api/test_lot_geometry_api.py`
  (`test_ra3_no_record_is_honest_absence`).
- **h** six typed client error states (unchanged): `record-address.ts:36-59`; tests
  `record-address.test.ts`.
- **i** credentials `omit` + 422 json-safety parity + title/aria length bound (unchanged):
  `record-address.ts` (omit + bounded message), `AddressConfirmCard.tsx`
  (`ENTERED_TITLE_ATTR_MAX_LEN`) + the `enteredTitle` derivation; tests
  `record-address.test.ts`, `address-confirm.test.tsx` rider-i.

## Validation outcomes (actual)

This revision changed ONLY web files (`AddressConfirmCard.tsx`, `address-confirm.test.tsx`)
plus this report — no Python change — so the api ruff/pytest outcomes are unaffected by it.

- `python tools/modularity_check.py --check` — **cwd repo root**, run this revision →
  `selected 449 files; failures 0; warnings 20` (exit 0). All 20 warnings are pre-existing
  on unrelated modules; `AddressConfirmCard.tsx` is NOT among them (the rider-a edit only
  removed lines, crossing no threshold).
- `python -m ruff check .` — the approval broker accepts only the exact documented string
  and REJECTS the `cd services/api` the api CI job runs from, so the documented command
  ran from the worktree **ROOT**: 45 pre-existing findings, ALL under `tools/**` and
  `project-control/**`, **ZERO in `services/api` or `apps/web`** (the api tree is
  ruff-clean; none of the 45 were touched — unrelated repository-wide findings, left as-is
  per the requested action). This revision changed NO Python; the api-scoped ruff (cwd
  `services/api`) is unchanged and is recaptured by the supervisor with explicit cwd.
- `python -m pytest tests/api/test_lot_geometry_api.py -q` / `python -m pytest tests/api -q`
  require **cwd `services/api`** (broker blocks the `cd`). Running them from repo root is
  the known invocation artifact (`No module named 'app'` / relative path miss) that has
  faked reds, so they were NOT run from root. No Python file changed here, so both suites
  are unchanged from the prior increment (`33 passed` / `439 passed`); the supervisor
  recaptures both with explicit cwd `services/api` when assembling gate evidence.
- Web suites (`address-confirm.test.tsx` incl. the rewritten rider-a group) prove ONLY in
  CI on the pushed head — no local npm/npx/node.

## Outstanding proof + supervisor/orchestrator responsibilities

- **Browser layout measurement (required, OUT of this packet's allowed_paths).** The
  actual pixel proof — that the Continue CTA's position is byte-stable when the record
  line resolves at the supported narrow widths (**360**/768/1280), INCLUDING a long
  permitted record address, and that a delayed non-shown settle causes no movement — must
  be captured in CI Playwright. `apps/web/e2e/responsive-a11y.spec.ts` renders the Confirm
  card at those viewports but is NOT in this task's allowed_paths, so the producer cannot
  add the measurement in-scope. Flagged for the orchestrator to add/capture via a **scope
  amendment or an orchestrator-authored spec** — no e2e file was edited here.
- **Per-file patches.** Supervisor to supply complete, bounded, non-truncated per-file
  patches for all eight modified files (`lot_geometry.py`, `test_lot_geometry_api.py`,
  `AddressConfirmCard.tsx`, `address-confirm.test.tsx`, `address-search.test.ts`,
  `record-address.ts`, `record-address.test.ts`, and this report) when assembling gate
  evidence. This revision materially touched only `AddressConfirmCard.tsx`,
  `address-confirm.test.tsx`, and this report; the other five are unchanged from the prior
  increment.
- **Commands.** Supervisor recaptures ruff + both api pytest commands with explicit cwd
  `services/api`; modularity retains repo-root execution (captured above).
- **Web CI.** Commit / push / web-test capture on the pushed head is the orchestrator's
  (ADR-005).

## Scope discipline

No forbidden-path edits; `AddressResolutionScreen.tsx` untouched. Only the rider-a card
mechanism + its S11 tests + this report changed in this revision. No channel-contract or
equality-gate semantic change; riders b–i byte-unchanged; card props/exports
byte-compatible (consumers unaffected). The needed browser layout spec is out of
allowed_paths and is surfaced (not edited). No new product/domain discoveries surfaced.
Not claiming all riders verified until the CI web suites are green on the pushed head, the
browser layout measurement is captured, and the supervisor diffs/command recaptures are in
place.
