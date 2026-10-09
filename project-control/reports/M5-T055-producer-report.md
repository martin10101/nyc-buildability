# M5-T055 producer report — DB-035 confirm-arc rider cluster

Task: close the four advisory DB-035 riders on the address confirm arc (from the
accepted M5-T050 wave). Scope stayed inside the packet `allowed_paths`; no api/route/
contract change; display semantics, flag gating, and every other confirm-arc behavior
preserved. Directives: D-066-R001 (code-graph consumer sweep), D-073-R006 (record =
no computed value), D-077-R002/R003.

**Resubmission note (this pass).** No code changed. The visible implementation and the
exact CTA equality assertion (`expect(ctaTopAfter).toBe(ctaTopBefore)`,
`responsive-a11y.spec.ts:277`) are preserved byte-for-byte — no implementation defect is
established in the visible code. This pass ONLY brings the report back under REPORT
DISCIPLINE: the prior pass had embedded a long verbatim diff and the `VIEWPORTS` block
to work around a packet-truncation problem. That is removed. The complete changed hunks
and the `VIEWPORTS` declaration are bounded evidence the supervisor collects
independently from the worktree diff of the four changed files listed below; this report
references them by file + line anchor only and does not restate them. Web behavior stays
explicitly PENDING CI at the pushed head.

## Implementation (by rider) — file + line anchors

Component edits: `AddressConfirmCard.tsx`. Unit tests: `address-confirm.test.tsx`
(S11 block). Pixel proof: `responsive-a11y.spec.ts` (existing M2-T002 S6 suite,
extended in place; every pre-existing S6 test byte-preserved).

- **(b) reading order** — `AddressConfirmCard.tsx:401-431`: the record note renders
  OUTSIDE the interactive block — after the Continue CTA and after the "Not my property"
  action (`:395-399`) and BEFORE the non-interactive `<Meta>` footer (`:431`,
  content-before-footer). A late insert below every settled interactive element cannot
  move either interactive element at any width or wrap; only the `<Meta>` reference-id
  footer shifts down one slot.
- **(c) accessible-name honesty** — `AddressConfirmCard.tsx:134` + `:217-220`: the
  DB-033 512-char attribute cap is removed; `enteredTitle = enteredInput` (full raw
  value), so the announced accessible name equals the full visible text in every case
  (never a truncation the eye does not show). Rationale below.
- **(d) no-street copy trim** — `AddressConfirmCard.tsx:230-232`: the `addressLine`-empty
  branch trimmed to `". The identity we carry forward is the tax lot (BBL)."` ("You
  searched for X" already states it is the entered value). The matched-present branch
  (`:231`) is byte-identical (accepted wording preserved).
- **(a) CLS pixel proof** — `responsive-a11y.spec.ts:145-292`: a per-viewport test over
  the existing `VIEWPORTS` (`:15-19`, 360/768/1280). It intercepts `**/record-address**`
  and holds it pending so the card first renders in its no-note loading shape, waits for
  the lot-outline surface to settle, measures the Continue CTA document-absolute top,
  releases a long differing record address (wraps at 360px, under the 600-char bound),
  waits for `data-record-address-status="shown"`, re-measures, and asserts the CTA top is
  byte-identical across the insert — `expect(ctaTopAfter).toBe(ctaTopBefore)` (`:277`,
  exact equality) — plus that the note sits below the CTA and above the Meta footer.

## Changed-hunk / VIEWPORTS references (bounded evidence, supervisor-collected)

Per REPORT DISCIPLINE these are referenced, not embedded; the supervisor collects the
untruncated hunks from the worktree diff of the changed files.

- Unit-test changed hunks — `address-confirm.test.tsx` S11 (`:806` describe):
  `:881-922` (rider a CLS + rider b reading order), `:924-998` (delayed-insert
  reading-order proof), `:1119-1149` (rider c/d no-street copy trim), `:1182-1204`
  (rider c a11y honesty, the 600-char equality binding that supersedes the DB-033
  rider-i 512 cap). S1–S10 unchanged.
- `VIEWPORTS` — `responsive-a11y.spec.ts:15-19` (existing constant, reused unchanged);
  the appended CLS block is `:145-292`; the pre-existing S6 loops and
  `expectNoHorizontalOverflow` (`:33` `toBeLessThanOrEqual`) are byte-preserved.

## Accessible-name boundary rationale (rider c / AS-3)

AS-3 permits either honest boundary: announce the full visible text, OR truncate BOTH
the visible text and the accessible name at the same boundary with a full-value
affordance. This packet announces the full visible text, because:

1. The visible `<strong>` text is ALREADY unbounded (`{enteredInput.trim()}`). The
   former 512 cap applied ONLY to `title`/`aria-label`, producing exactly the AS-3
   defect: the eye saw 600 chars while assistive tech announced a 513-char "…"
   truncation the eye never showed.
2. The cap was cosmetic, not a security control — the identical string is already fully
   present as visible text and React escapes attribute and text alike (inert). "Truncate
   both" would have meant truncating the visible text and adding an affordance — strictly
   worse UX for a bound that guards nothing.
3. Announcing the full raw value makes announced === seen at every length, so no boundary
   at which they diverge exists. The whitespace-honest S9/rider-b behavior is preserved.

## CLS below-CTA boundary rationale (rider a+b / AS-1)

The note inserts strictly BELOW both interactive actions in DOM order, so its
document-absolute top is greater than the CTA's and its insertion cannot change the CTA's
document top by any amount, for a record address of any length or wrap. That is why the
AS-1 assertion is exact equality (`toBe(ctaTopBefore)`), not a sub-pixel tolerance: the
honest expectation for an insert below the measured element is zero movement, and the
spec must fail if the value changes at all. Rider b moves only the non-interactive
`<Meta>` footer down one slot.

## Copy sweep (D-066-R001, AS-4) — actual commands and results

Swept across `apps/web` (`*.ts`/`*.tsx`, covering `src` + `e2e`) with native ripgrep;
CLI equivalents and current path:line hits below.

- `rg -n "We show it as the address you searched for" apps/web -g "*.{ts,tsx}"`
  → 2 hits, both in-scope, neither rendered copy:
  - `AddressConfirmCard.tsx:229` — inside the explanatory comment; no rendered branch.
  - `address-confirm.test.tsx:1141` — inside a `.not.toContain(...)` (binds the removed
    sentence ABSENT).
- `rg -n "identity we carry forward is the tax lot" apps/web -g "*.{ts,tsx}"`
  → 4 hits, all in-scope: `AddressConfirmCard.tsx:231` (matched-present, byte-identical)
  and `:232` (no-street trimmed); `address-confirm.test.tsx:1147` (trimmed present) and
  `:1154` (matched-present byte-identical).
- `rg -n "We show it alongside the city-matched address" apps/web -g "*.{ts,tsx}"`
  → 2 hits, both in-scope: `AddressConfirmCard.tsx:231`, `address-confirm.test.tsx:1154`
  (preserved matched-present wording).

CLS-tolerance sweep (confirms no sub-pixel tolerance remains):
`rg -n "toBeLessThan|toBe\(ctaTopBefore\)|Math\.abs" apps/web/e2e/responsive-a11y.spec.ts`
→ `:33` `toBeLessThanOrEqual` (pre-existing S6 horizontal-overflow helper, preserved,
unrelated) and `:277` `.toBe(ctaTopBefore)` (the CLS assertion, exact equality). No
`Math.abs(ctaTop…)` tolerance exists.

Consumer sweep for the (b) placement change: `address-resolution.test.tsx:74` references
`/record-address` only as a stubbed 404 (`if (url.includes("/lot-geometry") ||
url.includes("/record-address"))`) with no record-note position/last-child assertion —
not affected. `record-address.test.ts` and `condo-records.test.ts` test the lib, not the
card DOM. No out-of-scope red left silent; none found to route to the orchestrator.

## Acceptance scenarios

- AS-1 (CLS pixel proof): `responsive-a11y.spec.ts:145-292` — CTA document-top
  byte-identical across the long-record insert at 360/768/1280, exact equality (`:277`);
  S6 tests and `VIEWPORTS` preserved.
- AS-2 (reading order): `address-confirm.test.tsx:881-922`, `:924-998` — note follows
  both interactive actions and precedes the Meta footer; Meta is last child.
- AS-3 (accessible-name honesty): `address-confirm.test.tsx:1182-1204` — announced name
  === full visible text for a 600-char entry; no "…" marker. Rationale above.
- AS-4 (copy trim + sweep): `address-confirm.test.tsx:1119-1149` asserts the old sentence
  absent + the trimmed sentence present; copy sweep above.
- AS-5 (no behavior drift): no route/api/contract change; flag gating unchanged; S1–S11
  otherwise preserved.
- AS-6 (proof): `python tools/modularity_check.py --check` → `failures 0` (exit 0);
  vitest + Playwright prove ONLY in CI at the pushed head (thin client).

## Evidence

- `python tools/modularity_check.py --check` (documented command; re-run this pass from
  the worktree root): `selected 455 files; failures 0; warnings 20` (exit 0). All 20
  warnings are pre-existing `services/api` / `tools` files plus one `apps/web/src/lib`
  file (`surveyReview/types.ts`); none is in the four packet files.
- PENDING — CI on the pushed head (thin client; no local npm/npx/node): the vitest
  `address-confirm` suite and the Playwright `responsive-a11y` suite. Web behavior is NOT
  claimed verified from local reasoning; verification stays PENDING until the orchestrator
  commits/pushes all four files together and supplies CI evidence at that exact head, and
  the required gate evidence lands.

## Orchestrator handoff — all four modified files must land in the CI-tested commit

The working tree carries FOUR modified files; the CI-tested commit MUST include all four
together, or CI would run against a head missing the implementation:

1. `apps/web/src/components/address/AddressConfirmCard.tsx` (implementation)
2. `apps/web/src/components/address/__tests__/address-confirm.test.tsx` (unit tests)
3. `apps/web/e2e/responsive-a11y.spec.ts` (CLS pixel-proof e2e)
4. `project-control/reports/M5-T055-producer-report.md` (this report)

`apps/web/e2e/confirm-journey.spec.ts` is in `allowed_paths` but is NOT modified — it is
not part of this change. The controller fills the envelope (branch, worktree,
starting_sha, current_sha) and supplies the bounded diff/VIEWPORTS evidence and the
web-suite CI results at the pushed head.

## Discovery routing (D-069)

None. No out-of-scope finding surfaced during this cluster.
