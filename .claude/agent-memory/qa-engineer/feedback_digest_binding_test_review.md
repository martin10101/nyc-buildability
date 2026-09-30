---
name: digest-binding-test-review
description: How to judge anti-tautology and mutant-killing power when reviewing rule-citation content-digest binding tests (M4-T010 family)
metadata:
  type: feedback
---

When reviewing tests that bind a recorded content digest to a snapshot's stored digest
(dsl `_check_refs`, schema `citations[].content_digest_sha256`, pattern `^[0-9a-f]{64}$`):

- **The `match=` string is what carries mutant-killing power, not just `raises(DSLError)`.**
  A malformed-shape test (uppercase/wrong-length/non-hex) must assert the *schema-violation*
  message (`rule schema violation at citations/0`), because if someone LOOSENS the pattern the
  bad value stops being a schema error and instead reaches the load-time mismatch `DSLError`
  (`records content_digest_sha256 ... but the snapshot on disk stores`). Only a message-specific
  `match=` fails on that mutant. A generic `raises(DSLError)` would pass vacuously.
- **The mismatch test's anti-tautology** depends on using a valid-hex flipped digest (still
  matches the pattern) so it passes schema and ONLY `_check_refs` can raise — and wording the
  `match=` so a schema-shape rejection cannot satisfy it. Verified via offline jsonschema probe.

**Why:** these two guards are exactly the packet's stated risks ("mismatch test could pass
vacuously against a schema-shape rejection"; "wrong pattern breaks back-compat").

**How to apply:** confirm the flipped-digest case passes schema (jsonschema probe on the real
schema file) and that the two DSLError message shapes are mutually exclusive under the two
`match=` regexes.

One mutant is UNOBSERVABLE by construction and that is acceptable: comparing rule-side
recomputed sha256(excerpt) vs the snapshot's stored digest can never differ, because
`SnapshotStore.load`/`load_snapshot_file` set `content_digest_sha256 = sha256(verbatim_excerpt)`
and raise `SnapshotError` on any on-disk divergence — a tampered snapshot never loads, so the
two values are equal for every loadable snapshot. Note it honestly; it is not a coverage gap.
See [[probe-separator-deleting-normalizations]].
