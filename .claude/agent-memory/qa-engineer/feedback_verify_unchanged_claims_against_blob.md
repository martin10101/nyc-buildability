---
name: verify-unchanged-claims-against-blob
description: When a producer/orchestrator claims a file is "unchanged"/"byte-identical", verify against the actual blob hash or diff, not the prose — doc-only edits still change the blob
metadata:
  type: feedback
---

When reviewing a gate, treat any "NOT modified" / "byte-UNCHANGED" / "byte-identical"
claim as a hypothesis to falsify with `git rev-parse <sha>:<path>` (blob hash) or
`git diff <base> <sha> -- <path>`, never accept the prose.

**Why:** In the M5-T034 G4 review (2026-09-17, pinned 22724f02) both the producer
report §3.3 AND the orchestrator seam-evidence artifact flatly stated the conditional-FAR
`rule.json` was "NOT modified"/"byte-UNCHANGED". The blob demonstrably changed
(682150b8 → b6872657 in material commit ae478563): a documentation-only edit
(description, parameter notes, exception note, limitations) with values/steps/conditions/
status untouched. The intended meaning ("behavior unchanged") was true; the literal claim
was false. The producer also wrote "Ten tests" for what were nine `def test_m5t034`
functions. These are honesty-bar (AS-8) accuracy misses even though they understate rather
than overclaim.

**How to apply:** For every "unchanged/identical/N tests" claim, run the blob-hash or
count check at the frozen SHA before judging AS-8. Distinguish "behavior unchanged" (verify
via values/steps diff) from "file unchanged" (verify via blob hash) — they are different
claims. Record the correction as a BLOCKING report-fix (PASS-with-required-corrections),
and flag the same inaccuracy in the orchestrator's own evidence artifact when it repeats it.
