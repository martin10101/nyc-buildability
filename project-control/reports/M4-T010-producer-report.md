# M4-T010 producer report — rule-citation content-digest binding (schema + loader)

Producer: rules-engineer/orchestrator. One bounded change; ENGINEERING_RELIABILITY_STANDARD
§2 (owning boundary: the rule-definition contract + `_check_refs`, the module that already
does fail-closed reference validation at load), §3 (red/green below), §7 (typed `DSLError`,
message names the rule id, the snapshot id, and both digests; no body/legal text echoed).

## What was authored

1. `services/api/app/rules/schemas/v1/rule_definition.schema.json` — ADDITIVE optional
   `citations[].content_digest_sha256`, pattern `^[0-9a-f]{64}$`. Every committed rule
   (none carries the field yet) stays valid; `additionalProperties: false` retained.
2. `services/api/app/rules/dsl.py::_check_refs` — the citations loop now keeps the resolved
   snapshot and, when the citation records a digest, compares it to the snapshot's STORED
   `content_digest_sha256`, raising `DSLError` on disagreement (fail-closed AT LOAD; the rule
   never becomes evaluable). Absent field: exactly the prior behavior. Resolution order
   unchanged — a missing snapshot still raises `SnapshotError` first (S5).
3. `services/api/tests/rules/test_rule_citation_digest.py` — 8 collected cases: S1 back-compat
   enumeration (floor 11 files, every one loads), S2 matching digest loads (expected digest
   LOADED from the snapshot and cross-checked against sha256(verbatim_excerpt) — never a
   literal), S3 mismatch fails closed with a mismatch-specific `match=` (a schema-shape
   rejection cannot satisfy it), S4 four malformed-shape rejections at the schema, S5
   missing-snapshot precedence.

## Red/green record (§3.1)

RED — tests written first, run against the UNCHANGED schema/loader
(`python -m pytest tests/rules/test_rule_citation_digest.py -q` from `services/api`):
**3 failed, 5 passed** — S2 failed (schema rejected the field wholesale), S3 failed (the
schema-violation message does not match the mismatch pattern), S5 failed (schema rejection
preempted snapshot resolution). S1/S4 passed pre-change by design (S1 asserts the unchanged
inventory; S4's schema-violation match is satisfied by the additionalProperties rejection too).

GREEN — after the schema + loader change: full suite
`python -m pytest services/api/tests/rules` → **367 passed** (359 existing + 8 new, zero
regressions); `ruff check services/api/app/rules services/api/tests/rules` → All checks
passed; `python tools/modularity_check.py --check` → exit 0 (dsl.py 288→~300 lines, far
under thresholds).

## Scenario mapping

S1→test_s1 (back-compat), S2→test_s2 (matching loads; the red anchor), S3→test_s3
(fail-closed mismatch), S4→test_s4[4 ids] (schema pattern), S5→test_s5 (resolution
precedence), S6→command-level: the diff touches exactly the four allowed paths (no engine,
no rulesets, no requirements change); the documented commands above are the executable form.

## Deliberate non-changes

- No ruleset adopts the digest here: family adoption is M4-T009's AS-5 unit (rulesets/** is
  forbidden for this packet precisely to keep the scopes disjoint).
- No recomputation rule-side and no alternate digest basis: comparison is strictly against the
  snapshot's stored v1 digest (= sha256(verbatim_excerpt), asserted in-test before use).
- `evaluation_trace.schema.json` untouched: the trace's resolved provenance digest already
  exists and is tested by the M4-T009 provenance pack; this unit binds the RULE FILE side only.
