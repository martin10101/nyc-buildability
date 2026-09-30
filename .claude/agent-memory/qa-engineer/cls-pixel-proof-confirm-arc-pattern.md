---
name: cls-pixel-proof-confirm-arc-pattern
description: How the address confirm-arc proves CLS-free late inserts (DB-033/DB-035) and what a G4 reviewer must check on that pattern
metadata:
  type: project
---

The confirm-arc (AddressConfirmCard) proves a late async insert (record-address note)
causes zero CLS by measuring the element's DOCUMENT-ABSOLUTE top (`rect.top + scrollY`)
of an element rendered STRICTLY BELOW the insert in DOM order, and asserting exact
equality (`toBe`, not a tolerance) across the insert. jsdom unit tests bind the
structural guarantee (child order: note follows both interactive actions, precedes the
`<Meta>` footer which is `card.lastElementChild`); the real-browser pixel proof lives in
`apps/web/e2e/responsive-a11y.spec.ts` (the M2-T002 S6 suite, extended in place).

**Why exact equality is correct, not over-strict:** an insert strictly below the measured
element cannot change that element's document-absolute top UNLESS above-content reflows.
The spec removes the reflow sources by waiting for deterministic settle signals BEFORE
each measurement: `data-record-address-status` (loading→shown) and the lot-outline surface
terminal testid (`lot-outline-map`/`-webgl-unavailable`/`-empty`/`-review`/`-unavailable`).

**How to apply (G4 review of any confirm-arc CLS rider):**
- Verify the assertion is CURRENTLY exact equality — a "tolerance added" mutation is a
  mutation of the test itself and no test can self-guard it; the reviewer's job is to
  confirm no `Math.abs`/`toBeLessThan` tolerance on the measured coordinate right now.
- Residual environmental risk is a scrollbar-threshold toggle: if the insert pushes the
  page past the scroll threshold, a classic (space-taking) scrollbar shrinks width and
  reflows above-CTA content → the CTA moves. That is a REAL, deterministic shift the exact
  assertion correctly catches, not a flake. Font-swap between the two measures is a low
  residual because both measures happen after full card + lot-outline settle.
- Web behavior proves ONLY in CI at the pushed head (thin client) — the actual green run is
  the orchestrator-captured AS-6 artifact, never claimed from local reading.

Consumer sweep note: `address-resolution.test.tsx` touches `/record-address` only as a
stubbed 404 and reads `correlation-id` by text-content, never by DOM position — so the
Meta-footer reading-order move (record note now BEFORE `<Meta>`) does not break it.
