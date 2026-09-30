---
name: connector-split-gotchas
description: Hard-won traps when splitting an NYC connector into a helper module behind re-exports (PKT-style modularity splits)
metadata:
  type: feedback
---

When splitting a connector (e.g. `building_footprints_arcgis.py` → a new
`*_geometry.py` behind compatibility re-exports), two repo-specific traps bite:

1. The connector's `test_as5_*_not_wired_to_any_route_or_module` test greps ALL
   `app/**/*.py` (except the connector itself) for the connector's module-name
   LITERAL. A newly extracted sibling helper module must NOT contain that literal
   anywhere — docstring/comment included — or the grep trips and reddens.
   Refer to it as "the connector" instead.
2. The connector's `test_as5_module_imports_only_stdlib_shapely_and_app` pins an
   import-root ALLOWLIST that does NOT include `re`. To strip control chars in a
   log/id sanitizer, use a `str.translate` table, never `import re`.

**Why:** both tripped during M5-T101 (PKT-C). #1 cost a test round; #2 would have
if I'd reached for `re`. The allowlist is `<=` (subset), so removing imports
(e.g. `math` after moving the numeric helpers) is safe; adding a new root is not.

**How to apply:** keep the split acyclic (connector → helper only; helper imports
nothing back), move shared low-level helpers (`_finite`, `_safe_repr`,
`_signed_area`, coordinate-bound constants) INTO the helper and re-import them, and
prove the split alone keeps all existing tests green + fixtures byte-identical
BEFORE adding riders. The connector's top-level `def`/`class` count is the
modularity "symbol_ceiling" (40, report-only warning, not a failure); SLOC hard
cap is 1000 (a non-baselined file only fails ABOVE it). See [[source-accuracy-facts]].
