---
name: url-aware-fetch-dispatcher-preserves-spy-counts
description: When a new nested fetch (e.g. lot-geometry) is added under a screen an existing vitest suite spies on, wrap fetch in a URL-aware dispatcher so the new call never consumes the resolution spy's queued responses/call-count
metadata:
  type: feedback
---

When a component adds a NEW nested fetch under a screen whose existing vitest tests assert on a
fetch spy's call order/count (e.g. M5-T023 mounted `LotOutlineMap` inside the address confirm card,
which fetches `/lot-geometry`), replacing `vi.stubGlobal("fetch", spy)` directly will break those
tests: the new fetch consumes a `mockResolvedValueOnce` slot and perturbs call counts.

The correct, non-weakening fix used in `address-confirm.test.tsx` and `address-resolution.test.tsx`:
wrap fetch in a URL-aware dispatcher (`installFetch`) that intercepts the new URL to a benign stub
(here the flag-off 404 → `route_absent`) and delegates only OTHER URLs to the original spy. The
resolution spy's queue and call-count stay unchanged; full coverage of the new surface lives in its
own suite (`lot-outline-map.test.tsx`).

**Why:** this preserved the S7 sequencing tests and the flag-off/flag-on "no fetch until submit"
assertions verbatim — the only sanctioned assertion change was placeholder→new-surface testid.

**How to apply / caveat:** the flag-off "no fetch" assertion then becomes INDIRECT — a hypothetical
intercepted call would bypass the inner spy, so it no longer directly proves "zero fetches". It is
sound only because a sibling assertion proves the whole flag-gated tree (`address-resolution-screen`)
never mounts, so the nested component cannot fire. Keep that structural mount assertion; don't rely
on the spy alone for the flag gate. (G1 recorded this as an observation on M5-T023.)
