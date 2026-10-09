# M5-T011 — Directive-Compliance Verification (DCV) vs D-038 (verbatim reviewer return)

Verifier: **directive-compliance-verifier** (independent ≠ producer scenario-optimization-engineer, ≠ orchestrator). Reviewed SHA `bbf3267f8be2444c5460742e22792698bdc1307f`; material identity `fd2e89098562c16bcca5950801b1fecec3f44cc03bae0cadd4bbfd113edfd46d`.

---

## DCV REPORT — task M5-T011 vs directive D-038 (independent)

**Verdict: PASS**

**reviewed_sha:** `bbf3267f8be2444c5460742e22792698bdc1307f`
**reviewed_manifest_sha256:** `fd2e89098562c16bcca5950801b1fecec3f44cc03bae0cadd4bbfd113edfd46d`
**Verifier:** directive-compliance-verifier (≠ producer scenario-optimization-engineer / run persistent-local-27; ≠ orchestrator). Read-only. Python 3.11.9, pytest 8.4.2.

### Scope / diff identity (reproduced)
`git show --name-only bbf3267f` → exactly 4 files, all inside allowed_paths, no forbidden path: breakeven.py (new), __init__.py (additive facade), test_scenario_breakeven.py (new), M5-T011-producer-report.md. The eight forbidden sibling sources (derive/builder/models/constants/contract/ranking/sensitivity/comparison/_json_safety) and packages/contracts/**, apps/web/**, tools/** are byte-unchanged. Parent = b9d4f03f.

### Applicable-requirement sweep — CONFIRMED {D-038-R003, D-038-R004}
- requirements.json lists M5-T011 in applicability.task_ids of R003 and R004 only; R001/R002/R005/R006/R007 bind sentinel D-038-BOOTSTRAP. Applicable set = exactly {R003, R004}.
- directive_refs = D-038:ALL ⊇ applicable → selective-citation guard satisfied.
- Cross-registry sanity scan: D-004-R222/R240 and D-007-R610 surfaced via the shared project-control/reports/ path but each requires task_types=['governance']/milestones=['M0'] (conjunction) — M5-T011 is backend/M5, none attaches.

### Integrity — CONFIRMED
- validate_directive_compliance.py --check → EXIT 0.
- sha256(requirements.json) = 37035a7db4db9dd71c6eba561e877cb440e4ea29a78e43c8eec5827d9c6f8a75 == manifest.requirements_content_digest_sha256. ✓
- sha256(source-001.md) = a237dd50... == manifest.sources[0].content_digest_sha256 (source unchanged). ✓
- locked_requirement_ids = R001..R007 (unchanged). ✓
- audit_log[-1] = 2026-09-09T05:40:00Z applicability_appended recording M5-T011 append + digest resync 2e904ad6 → 37035a7d. ✓

### Content-identity — CONFIRMED
Producer report §7.2 embeds breakeven.py verbatim; byte-consistent with the working-tree file, line refs resolve. No producer-report ↔ code drift.

### Requirement rows

**D-038-R003 (positive product deliverable) — PASS**
- breakeven.py:612 defines public find_scenario_threshold(scenario_document, variable, target, domain, response_metric=…); docstring "Deterministic OFFLINE scenario break-even / threshold FINDER … Fifth and final optimization-side brick under M5". Packet milestone M5, backend, product-only allowed_paths. NOT the M0 self-infra line.
- Contracted G0 packet project-control/gates/M5-T011-G0.json result=PASS.
- AS-1..AS-7 map to real passing tests; reproduced pytest test_scenario_breakeven.py → 61 passed; full tests/scenario → 384 passed (323 pre-existing + 61 new, 0 regression).
- Cap verbatim + never-Verified: candidate components.canonical_cap_sq_ft is derived.get("canonical_cap_sq_ft") (breakeven.py:371) — transported, no legal recompute; _bounded_coverage_status caps verified→conditional (:229-230); _base_lineage stamps needs_review=True + NOT_VERIFIED_DISCLAIMER (:244-248); THRESHOLD_LABEL ends "… NOT Verified." (:160). Asserted by test_as1_* and test_as3_result_is_never_verified_and_honestly_labelled.
- modularity --check EXIT 0, failures 0; breakeven.py carries a NON-blocking review_signal warning (above ~600 warn, under 1000 hard) with a cohesion justification in producer report §5.

**D-038-R004 (no Supabase / no live Geoclient, offline) — PASS**
- Imports only stdlib + local: breakeven.py:36-50 = copy, json, math, enum.Enum, typing.Any + ._json_safety (_json_safe) + .constants (NOT_VERIFIED_DISCLAIMER) + .derive (RECOGNIZED_FACTOR_TYPES, DerivedRangeKind, derive_practical_usable_range). No network/storage/env import.
- Negative grep supabase|geoclient|requests|httpx|socket|urllib|aiohttp|boto3|psycopg|sqlalchemy|os.environ|getenv|open(|subprocess|.connect(|import os over the module AND its transitive deps (breakeven.py, derive.py, _json_safety.py, constants.py) → only match is breakeven.py:32 (a docstring line); zero code matches in the call path.
- Pure dict→dict, no persistence/network/address resolution; input consumed READ-ONLY — test_as7_inputs_are_byte_unchanged_and_not_aliased proves inputs byte-unchanged and un-aliased.
- Offline verified: test_as7_runs_fully_offline_socket_blocked replaces socket.socket with a raising stub and the finder still returns a scanned result; whole suite runs on fixtures, no cloud. dependencies=[M5-T010] only; no deferred credentials.
- Shared sanitizer not re-duplicated: test_as5_uses_shared_sanitizer_not_a_local_duplicate asserts `from ._json_safety import _json_safe` present and local sanitizer defs absent — passes.

**Overall: VERDICT PASS.** Both applicable requirements independently reproduced SATISFIED at reviewed_sha bbf3267f; integrity EXIT 0 with digests/locks/source/audit all matching; no forbidden-path edits; no code↔report drift. Only non-blocking observation: the breakeven.py modularity review_signal warning (justified in report §5, under the hard threshold, --check passes).
