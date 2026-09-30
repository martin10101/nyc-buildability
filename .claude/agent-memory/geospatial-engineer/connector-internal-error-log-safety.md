---
name: connector-internal-error-log-safety
description: Safe pattern for a connector's findable-but-non-leaky internal_error log; the shared transport sanitizer does NOT strip text
metadata:
  type: project
---

For a connector catch-all `internal_error` log that must be "findable in production" yet
"leak no upstream body text" (M5-T089 G3-A1 / DB-058(e); the M5-T100 rider), log ONLY the
exception CLASS name (`type(exc).__name__`, a Python identifier for any real exception) plus a
FIXED connector constant, each passed through the shared transport sanitizer and length-bounded.
NEVER log `str(exc)`.

**Why:** `app/resilience/transport.py` exports exactly one sanitizer in `__all__` —
`sanitize_retry_after`. It is an allowlist passthrough (`^[A-Za-z0-9,: +\-]{1,64}$`) else
`repr()`. It does NOT strip text: `sanitize_retry_after('AdminSecret123')` returns it verbatim
(allowlist-safe), and `repr()` of a long hostile body only escapes control chars and wraps it —
the text survives. So sanitizing `str(exc)` canNOT stop a leak; a genuine bug's exception message
can carry an upstream body fragment or a short secret. Excluding `str(exc)` entirely is the
load-bearing move; the sanitizer+bound is defense-in-depth on the class name (guards an exotic
`__name__` with control chars / over-length). Keep the RETURNED refusal class-name-only (the
M5-T089 G5-approved non-disclosure choice) — only the LOG gains the message.

**How to apply:** Reuse `sanitize_retry_after` read-only (never edit `app/resilience`). Prove it
with mutations: (a) log `str(exc)` -> a test injecting upstream text into the message reddens;
(b) drop the sanitize/bound wrapper -> a crafted class name `"Bad\nFORGED " + "Z"*400` reddens the
no-raw-newline and `...(truncated)` assertions; (c) `logger.error`->`logger.debug` reddens the
findability assertion. See `building_footprints_arcgis.py` `_sanitized_bounded` + the catch-all.
Related: [[project_source-accuracy-facts]].
