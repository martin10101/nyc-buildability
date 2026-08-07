# Gate Report

- **Gate ID:** G4 (QA)
- **Task ID:** M0-T042 — Codex ephemeral review integration (0A.8 item 4; AD-081..AD-088) + minimal root AGENTS.md
- **Reviewer:** qa-engineer (independent; not the producer)
- **Producer:** backend-engineer
- **Result: FAIL** (narrowly scoped, easily remediated — see Required rework; implementation itself is correct)
- **Clean environment/worktree used:** Yes — reviewed at frozen head `fa69f9e5600e390750fada345f33713261438de1` in worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T042-codex-review`, diff base `0ed2cdb`. I ran nothing that mutates state; no `project_control.py`/`git`/`gh` write commands.

## Summary verdict rationale

This is a genuinely strong submission: all five acceptance scenarios **as written in the packet** are backed by real, executed, deterministic, non-flaky tests; the two flagged producer deviations are correct and strengthen (not weaken) their scenarios; regression safety is clean; and every bound directive requirement is actually satisfied in the shipped code. I verified all of that independently.

The FAIL is on one specific, checkable QA duty: **"AS-3: every prohibited category has a fixture that actually rejects/strips."** The guard implements seven prohibited-content detection paths, but the AS-3 test exercises only five. Two directive-enumerated categories (`all_logs`, `full_code_graph`) and the entire completeness-flag mechanism (`_scan_completeness_flags`) have **zero** test coverage. These guard a bound safety requirement (D-010-R083 / AD-083 — preventing prohibited material from reaching an external model), so a silent regression to those paths would pass CI. The producer report also leaves the impression that AS-3 covers all seven categories when it covers five. Per instruction I am not softening this. The remediation is ~3 assertions.

## Acceptance criteria reviewed

All commands below are ones I executed myself in the orch worktree at the frozen head.

**(a) New module, verbose:** `python -m unittest tools.test_agent_supervisor_ephemeral_review -v`
→ **Ran 23 tests in 0.425s — OK** (0 fail, 0 skip). 23 test methods, matching the claim.

**(b) Full suite:** `python -m unittest discover -s tools -p "test_agent_supervisor_*.py"`
→ **Ran 1212 tests in 72.489s — OK (skipped=2)** ⇒ **1212 run / 1210 pass / 0 fail / 2 skip**. Exactly matches the claimed after-state; delta 1212 − 1189 = 23 (all from the new module), internally consistent with the stated 1189 baseline.

**(c) Second run of new module (flakiness):** → Ran 23 in 0.417s — OK. **Third run:** → Ran 23 in 0.428s — OK. No flakiness.

**Isolation slices:** `AS1EndToEnd` (3/OK), `AS2Budget` (4/OK), `RolesAndUsage` (3/OK) each pass in isolation — no order dependence.

## Directive/requirement verification (QA lens — authoritative directive pass is the directive-compliance-verifier's)

| Requirement ID | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-010-R027 (fresh/ephemeral, no shared state) | fa69f9e | PASS | `test_a_second_review_shares_no_state_with_the_first`: distinct packet_digests, distinct `verified_facts.packet_bytes` from two real subprocess runs. Note: `fresh_process_per_review`/`shares_conversation_state` are hardcoded record constants (self-asserted), but the differing packet_bytes give real independence evidence. |
| D-010-R041 (root AGENTS.md exists) | fa69f9e | PASS | AGENTS.md present; I measured 78 lines / 3893 bytes; all 14 Section-11.1 topics present. |
| D-010-R042 (no CLAUDE.md duplication) | fa69f9e | PASS | I re-measured: AGENTS 3893 B / 78 lines < CLAUDE 8227 B / 112 lines; **0** shared ≥40-char lines. |
| D-010-R081 (ephemeral review is default) | fa69f9e | PASS | `conduct_ephemeral_review` runs only the fresh read-only reviewer; no persistent path; AS-1 green. |
| D-010-R082 (no persistent controller) | fa69f9e | PASS (structural) | Each review = one fresh subprocess (fake-codex), discarded; no session resume. |
| D-010-R083 (content guard) | fa69f9e | **PARTIAL / FAIL (coverage)** | Code rejects all 7 categories (I ran `guard_packet` on `all_logs`, `full_code_graph`, `code_graph_dump`, and 3 completeness-flag fixtures — all reject correctly). BUT the AS-3 tests cover only 5 detection paths; `all_logs`, `full_code_graph`, and `_scan_completeness_flags` are untested. Bound-requirement path without a fixture. |
| D-010-R084 (meaningful-checkpoint cadence) | fa69f9e | PASS | AS-4 both directions: all 7 triggers → review; deterministic-pass-only → no review; trigger beats coincident pass; no-signal → no review. |
| D-010-R085 (token/relative ceilings) | fa69f9e | PASS | AS-2 ceiling math + I re-derived: window None→64000, 400k→64000 (ordinary wins), 200k→40000 (relative), estimate(400k B)=100000. |
| D-010-R086 (split oversized, no giant session) | fa69f9e | PASS (minor note) | Over-ceiling refusal carries `SPLIT_SUMMARIZE_GUIDANCE` incl. "never open a giant persistent Codex conversation." Test asserts guidance is truthy but does not assert that specific line individually. |
| D-010-R087 (no duplicate investigation) | fa69f9e | PASS | AS-1: `reopened_sources` contains `services/api/app/rules/engine.py` (cited but not in packet) and excludes the supplied `tasks/M0-T042.json`. |
| D-010-R088 (worker fallback recorded, never activated) | fa69f9e | PASS | Role guard raises `role_not_activatable`; `record_worker_fallback` builds a WORKER-role record that verifies; loop only ever runs reviewer. |
| D-010-R093 (no speculative feature) | fa69f9e | UNVERIFIABLE (QA lens) | Judgment/traceability requirement; each module maps to a named requirement by inspection. Defer to directive-compliance-verifier. |
| D-010-R116 (session-2 re-dispatch / wave-1 resume) | fa69f9e | UNVERIFIABLE (QA lens) | Process/lifecycle, not unit-testable. Defer to control-plane-verifier / directive-compliance-verifier. |

## Steps independently executed

1. Confirmed frozen head `fa69f9e…` on `task/M0-T042-codex-review`.
2. Ran the three required test invocations + two extra module reruns + three class-slice isolation runs (all above).
3. **AS-2 arithmetic re-derived** by building the real packet: `packet_size_bytes = 652`, `estimate_tokens = 163`. At window 1000 the ceiling is 200 → 163 ≤ 200 = **within budget (no refusal)**, so the staged window-1000 test would indeed have FAILED to exercise the refusal. At window 100 the ceiling is 20 → 163 > 20 = **refuses**. The producer's 1000→100 deviation is arithmetically correct and **strengthens** the scenario (genuine refusal, robust to small packet drift). Verified.
4. **AS-5 re-measured** independently (not via the test): AGENTS 3893 B / 78 lines, CLAUDE 8227 B / 112 lines, 0 shared ≥40-char lines, all 14 topics present. Verified.
5. **AS-3 completeness check:** ran `guard_packet` directly on the two untested marker categories and the completeness-flag mechanism — all reject correctly (so the code is right), confirming the gap is coverage, not a defect.
6. Confirmed no other test file references `guard_packet`/`review_packet` (the sole match in `test_agent_supervisor_reviewer.py` is an unrelated `max_review_packet_bytes` config constant).
7. Regression: `git diff 0ed2cdb..fa69f9e --name-status -- tools/test_*.py` → only `A tools/test_agent_supervisor_ephemeral_review.py`. No existing test modified/deleted. `codex_reviewer.py` diff is additive (the one "deletion" is the import line gaining `USAGE_UNKNOWN`).

## Expected versus actual

| Check | Expected | Actual (my run) |
|---|---|---|
| New module count | 23 | 23, OK |
| Full suite | 1212 / 1210 / 0 / 2 | **1212 / 1210 / 0 / 2** |
| Baseline delta | +23 | +23 (1212−1189) |
| Flakiness (3 runs) | stable | stable |
| AS-2 packet | 652 B / 163 tok | 652 B / 163 tok |
| AS-2 refusal @ window 100 | refuses (ceiling 20) | refuses, `within_ceiling=False`, `effective_ceiling.tokens=20` |
| AS-5 sizes | AGENTS<CLAUDE, <120 lines, ≤2 shared | 3893<8227, 78<120, 0 shared |
| Guard categories rejecting | 7 in code | 7 in code; **5 have fixtures** |

## Evidence paths

- `tools/test_agent_supervisor_ephemeral_review.py` (new, 23 tests)
- `tools/agent_supervisor/ephemeral_review.py`, `review_packet.py`, `review_cadence.py` (new)
- `tools/agent_supervisor/codex_reviewer.py` (additive: `parse_usage_telemetry`, `usage_telemetry` field)
- `AGENTS.md`, `CLAUDE.md` (root)
- `project-control/tasks/M0-T042.json`, `project-control/reports/M0-T042-producer-report.md`

## Human-style walkthrough findings

Not a UI task — no walkthrough applicable. Reading AGENTS.md as a Codex would: it is a coherent, concise, genuinely non-duplicative brief; defers to CLAUDE.md/project-control on conflict; the six decision enum values match the schema; routed doc paths exist (spot-confirmed by the producer and consistent with repo layout).

## Regression/security/provenance findings

- **Regression: CLEAN.** Only additive changes; no existing test touched; full suite green (1210 pass, 0 fail). The project-control/state.json, gates, and evidence-map changes in the diff are orchestrator ledger writes (ADR-005), not producer implementation — outside QA scope and expected.
- **Determinism: CLEAN.** Fake Codex is a local Python script (no network, no real `codex` binary, no tokens). Wall-clock only feeds `created_at_utc`, on which no assertion depends; record digests differ per run but no test asserts a fixed digest — three runs identical.
- **Security-relevant:** the content guard is the mechanism that keeps prohibited whole-material away from an external model. That is exactly why its untested detection paths matter (below).

## Defects

**D1 (MUST-ADD — blocking this gate). AS-3 / D-010-R083 coverage incomplete for a bound safety requirement.** The guard implements seven detection paths; `test_each_prohibited_category_is_rejected` exercises four marker categories plus one correlation check (five total). **Untested:** the `all_logs` marker category, the `full_code_graph` marker category (both directive-enumerated AD-083 prohibited items per the module's own 0A.1 reading), and the entire `_scan_completeness_flags` mechanism (reports/directives/logs completeness flags). I verified the code rejects all of these correctly, so this is a coverage gap, not a live defect — but a future edit dropping a key from `PROHIBITED_MARKER_KEYS` or breaking `_scan_completeness_flags` would pass CI while silently violating AD-083. The producer report's R083 row implies AS-3 covers all seven categories; it covers five. Reproduction: `test_each_prohibited_category_is_rejected` has only 4 `cases` keys; no fixture names `all_logs`, `full_code_graph`, or a completeness flag.

## Coverage gaps (non-blocking)

- **NICE-TO-HAVE 1 — AS-2 boundary at exactly the ceiling** (`estimated_tokens == ceiling.tokens`, `<=` semantics). Off-by-one at the ceiling is untested.
- **NICE-TO-HAVE 2 — `CheckpointSignals.from_mapping` validation** (`unknown_signal`, `non_boolean_signal`) is untested, even though the analogous `ReviewBudget.from_mapping` bad-key path IS tested — an asymmetry.
- **NICE-TO-HAVE 3 — `parse_usage_telemetry` peak-across-multiple-events and the `JSONDecodeError` branch.** Only a single usage event and a non-`{` "no json" line are tested; a malformed `{`-line mixed with a valid usage event (the except path) and the peak-selection logic are unexercised.
- **NICE-TO-HAVE 4 — tampered-journal-row path** (`ReviewJournal.verify()` returning False). In-memory tamper is tested (`test_a_tampered_record_fails_verification`); the on-disk journal False path is a trivial `all()` wrapper but unexercised.
- **NICE-TO-HAVE 5 — top-level (non-`sections`) marker key** and **strip mode for marker categories other than transcript/task_packets** are unexercised.
- **Observation (not a gap):** the `independence` proof fields `fresh_process_per_review`/`shares_conversation_state` are hardcoded constants the tests assert tautologically; real freshness rests on `codex_reviewer.review()` spawning per-attempt subprocesses (covered by the existing reviewer suite) plus the differing packet_bytes evidence.

## Required rework

Add to `test_agent_supervisor_ephemeral_review.py` (roughly three assertions, no production-code change needed since the guard already works):
1. A rejection fixture for `all_logs` and for `full_code_graph` (extend the `cases` dict in `test_each_prohibited_category_is_rejected`).
2. At least one completeness-flag fixture (e.g. `{"sections": {"reports": {"all_history": True}}}` → rejected with category `all_historical_reports`) to cover `_scan_completeness_flags`.

Optional but recommended: AS-2 exact-boundary test and a `CheckpointSignals.from_mapping` validation test.

## Reviewer conclusion

**FAIL** — solely on the AS-3 / D-010-R083 coverage gap (two directive-enumerated prohibited categories and the completeness-flag mechanism have no fixtures guarding a bound safety requirement, and the producer report overstates AS-3 coverage). Everything else is strong and independently verified: 1212/1210/0/2 full suite, 23 new tests, no flakiness, additive-only, deterministic, AS-1/AS-2/AS-4/AS-5 proven, both flagged deviations correct and scenario-strengthening, and the guard code itself is correct across all seven categories. The remediation is small (≈3 test assertions, no implementation change). The orchestrator may reasonably choose rework-then-accept or accept-with-an-immediate-follow-up; on the evidence and my explicit AS-3 duty, my gate verdict is FAIL. Nothing here is BLOCKED — I executed every required command myself.

Unverifiable from the QA lens (deferred to the named specialist reviewers, not blockers for G4): D-010-R093 (no-speculative-feature judgment) and D-010-R116 (session-2 re-dispatch lifecycle) are process/traceability requirements outside unit-test scope; the authoritative directive pass belongs to the directive-compliance-verifier.
