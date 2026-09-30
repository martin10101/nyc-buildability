---
name: modularity-sloc-counts-docstrings
description: modularity_check SLOC counts docstring/string-literal lines (only blank + #-comment lines are excluded); judge a docstring-heavy file by SLOC not physical lines
metadata:
  type: project
---

`tools/modularity_check.py` `source_lines()` counts SLOC = non-blank physical lines
whose stripped form does NOT start with `#`. Python **docstrings and string literals
COUNT as SLOC** (they are code content, not comments). Thresholds: WARN 600, JUSTIFY
750, HARD 1000 (`WARN_SLOC`/`JUSTIFY_SLOC`/`HARD_SLOC`). A NEW file between WARN and
HARD with no baseline exception is a `review_signal` **warning, not a failure**; the
note escalates to "record a cohesion justification" only when SLOC > 750.

**Why:** During the M5-T042 G4 gate a producer described an 850-physical-line
connector as "warn tier, under the 750 justify threshold." Verified: physical lines
849, but SLOC = 770 non-blank − 44 comment-only = **726** — genuinely under 750, so the
claim was accurate and modularity exit 0 (warn only) was correct.

**How to apply:** Never contest a modularity claim on physical line count. Recompute
SLOC the checker's way: `git show <sha>:<path> | grep -cE '\S'` minus
`... | grep -cE '^[[:space:]]*#'`. A docstring/provenance-heavy connector can be ~120
physical lines above its SLOC. Related: [[soda-connector-error-taxonomy-at-transport]].
