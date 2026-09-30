---
name: copy-change-old-string-sweep
description: For web copy/a11y-change tasks, sweep the WHOLE apps/web (incl. e2e/) for the OLD literals and confirm which code path each surviving assertion exercises before calling a shared-copy change safe
metadata:
  type: feedback
---

When a web task changes user-facing copy or unifies strings into a shared constant,
grep the entire `apps/web` (including `apps/web/e2e/**`, not just the packet's
allowed_paths) for the OLD literal strings AND the changed accessible names — any
consumer still asserting an old literal breaks on the pushed head.

**Why:** M5-T041 changed the AddressConfirmCard ZoLa link text ("View this lot on the
city's ZoLa map" -> "Open ZoLa"), its absent note ("...this result did not provide" ->
"...this lot did not provide"), and ZoningContextPanel ("Open in ZoLa" -> "Open ZoLa").
An out-of-scope M5-T040 test (`development-limits.test.tsx`) queried `/Open ZoLa/`
scoped to `siteCard()`, and an e2e (`architect-workspace.spec.ts:226`) asserted a full
error sentence verbatim. Both survived — but only because the nested panel renders
OUTSIDE `.architect-map-card` and the e2e mocks `/v2/autocomplete` (the TYPED path,
unchanged), never the explicit full-address `/search`. Had either exercised the changed
surface, the shared-copy change would have gone red.

**How to apply:** (1) grep OLD strings across all of `apps/web`; every hit that is a live
assertion (not a comment) is a break candidate — verify its scope/path. (2) For error/copy
that varies by code path (e.g. typed-suggestion failure vs explicit full-search failure,
selected by `fullSearchActive`), read which endpoint/action the test drives before
concluding it's unaffected. (3) A shared constant asserted via its IMPORT (`.toBe(CONST)`)
is stronger than a re-typed literal or `.toContain` — prefer/expect the import form.
Cross-file coupling (an out-of-scope test depending on the new constant's value via a raw
regex) is worth an advisory even when CI is green.
