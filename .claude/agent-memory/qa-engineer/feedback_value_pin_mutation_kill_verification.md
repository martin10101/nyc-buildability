---
name: value-pin-mutation-kill-verification
description: How to independently confirm a "value-pin" test actually kills the claimed mutation (e.g. boundedTimestamp->boundedToken revert)
metadata:
  type: feedback
---

When a producer claims a value-pin test "kills a boundedTimestamp->boundedToken revert" (DB-036(g) class), do NOT trust the claim from the assertion alone — verify the sanitizer transform makes the two paths diverge.

**Why:** a `.toBe("2026-09-01T14:05:56Z")` pin only kills the revert if `boundedToken` actually alters that exact string. Confirmed in `apps/web/src/lib/bounded.ts`: `boundedToken` allowlist is `[A-Za-z0-9._-]`, which STRIPS `:` and `+`, turning the ISO instant into `2026-09-01T140556Z`. `boundedTimestamp` keeps `[0-9A-Za-z.:+-]`. So the revert genuinely fails both the unit `.toBe` (strict) and the render `.toHaveTextContent(...)` (substring — mutated value no longer contains the pinned colons).

**How to apply:** for any "mutation-style" pin, read the two functions the mutation swaps between and confirm they produce different output for the pinned fixture value. Also check BOTH usage sites are pinned (retrievedAt appears at `provenance.retrievedAt` AND `provenance.queries[].retrievedAt` in condo-records.ts) so a selective revert of one site is still caught. Render-level substring pins fail on a revert only when the mutated substring is not a superset — verify that.

Related gotcha: `python tools/modularity_check.py --check` file COUNT drifts with disjoint peer commits on a live head (saw 455 in producer report vs 456 at review head) — this is expected when the reviewed material files are byte-stable; judge on `failures 0` and whether any TASK file is flagged, not the raw selected-count.
