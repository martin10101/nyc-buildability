---
name: guard-coverage-completeness
description: When gating a content-guard / prohibited-category enum, require a fixture for EVERY implemented category, not only the ones the acceptance-scenario text names
metadata:
  type: feedback
---

When reviewing a guard/allowlist/enum that enforces a bound safety requirement, a test that
exercises only the categories the acceptance-scenario TEXT names is insufficient if the
implementation defines MORE categories. Every implemented detection path guarding a bound
requirement needs a fixture, or a silent regression (e.g. dropping a key from the map) passes CI.

**Why:** M0-T042 (Codex ephemeral review, AD-083) implemented 6 marker categories
(`full_transcript`, `full_directive_registry`, `all_historical_reports`, `whole_repository`,
`all_logs`, `full_code_graph`) plus an `unrelated_task_packets` correlation check and a
`_scan_completeness_flags` mechanism. The AS-3 test exercised only 5 detection paths; `all_logs`,
`full_code_graph`, and the whole completeness-flag mechanism had zero coverage even though they are
directive-enumerated (0A.1/AD-083) prohibited items. The code was correct (verified by hand-running
`guard_packet`), so it was a coverage gap, not a defect — but a regression would silently violate a
bound safety requirement.

**How to apply:** For any guard/enum gate, list the categories the CODE defines (read the
map/frozenset), then confirm each has a rejecting fixture. Treat "every prohibited category has a
fixture" literally. A producer report that says the code "rejects all N categories, Evidence: AS-3
tests" is a claim to reproduce — count the fixtures, do not trust the sentence.
