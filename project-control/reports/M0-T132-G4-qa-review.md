# GATE REPORT — M0-T132 (G4 QA, independent) — verbatim reviewer return

**Task:** M0-T132 — D-024 Amendment 34/35: Claude Code 2.1.252 admission + combined R247 recertification
**Gate:** G4 (independent QA / reviewer, read-only)
**Reviewer:** qa-engineer (independent; producer = `orchestrator-admission-runner`)
**Frozen reviewed SHA:** `d743ad24` (tip of `control/D-024-fable-codex-loop`)
**Verification method:** clean-room extraction of the frozen tree via `git archive d743ad24 | tar -x` into a scratch dir (no `.git`); mutation done in a SEPARATE extracted copy so it never touched the repo or the count run. Windows, Python 3.11.9, `PYTHONPATH=.`. Installed CLI verified `claude --version` → `2.1.252 (Claude Code)`.

## VERDICT: PASS

All three producer claims reproduce, the admission's drift-resolution is confirmed, the drift teeth are proven removal-sensitive (red-on-mutant, 4 teeth), and the shell_routing fixture matches its claims. No test was removed and no new failure was introduced.

## Reproduced counts

| Claim | Producer | Independent result | Status |
|---|---|---|---|
| 1. Golden pack (`test_agent_supervisor_golden_run.py`) | 42 passed | **42 passed** (51.21s) | MATCH |
| 2. Four re-pointed packs (event_bus, capability_probe, native_adapter, routing_probe) | 150 passed | **150 passed** (21.69s) | MATCH |
| 3. WHOLE supervisor suite (`test_agent_supervisor_*.py`) | 3,043 passed / 2 skipped / 0 failed (3,045 collected) | **3,041 passed / 4 skipped / 0 failed** (3,045 collected; 574.82s; exit 0) | MATCH after clean-room reconciliation |

**Clean-room count reconciliation:** the `git archive` clean-room has no `.git`, so the two
`test_agent_supervisor_os_acl.py` "defective blob unreachable" tests (lines 787, 1033) hit `skipTest`
(`defective blob 1e649a8 unreachable: fatal: not a git repository` / `33b2e24 script`). In the
producer's `ctl24` checkout (which has `.git`) these two resolve the blob and PASS — precisely the
`-2 passed / +2 skipped` delta. Same **3,045 collected**, **0 failed** on both sides. The producer's
3,043 / 2 / 0 is confirmed.

## Key verification — drift resolution (the admission's whole point)
- The three CLI-drift live teeth that FAILED in accepted M0-T131 at 2.1.251 now **PASS** at 2.1.252
  (ran by name, all 3 PASSED in 7.80s): `capability_probe::test_live_reprobe_claude_version_matches_fixture`,
  `event_bus::test_s8_live_version_matches_catalog_fixture`,
  `native_adapter::test_live_detection_matches_committed_fixture`.
- Baseline math holds: M0-T131 = 3,040 passed / 2 skipped / **3 failed** (3,045 collected) → M0-T132 =
  3,040 + 3 = **3,043 passed, 0 failed**, same 3,045 collected. **No test removed** (diff
  `1d4a6212..d743ad24` shows only `event_drift.py` re-point + 4 NEW fixtures + 4 test re-points — no
  deletions), **no new failure**.

## Red-on-mutant (removal-sensitivity)
Pristine four teeth GREEN (4 passed). Mutating every committed fixture's version 2.1.252 → 2.1.999
(capability `body.probes.claude_version.first_line`; catalog `claude_version`; native `claude_version`;
routing `claude_version` + `claude_version_line`) → **4 failed** (routing tooth
`probe_shell_routing_evidence(installed_version="2.1.252")` → AssertionError; three live teeth fail on
the mutated fixture vs installed 2.1.252). Same shape as the un-admitted M0-T131 drift → the teeth
genuinely bite version drift, not vacuously green.

## shell_routing fixture
`measured: true`; `routing_summary.verdict: native_preferred` (3 native, 0 shell); `cli_identity:
e713c5a6c8bc71afbc149988c0d7ac4e313bf371316ed2b34e261e34c785a883`; `capture_model: claude-opus-4-8`
(honestly recorded with a `capture_note` on the Fable 7-day cap; gate keys on the `e713c5a6` digest,
which is stamped). Version fields `2.1.252` / `2.1.252 (Claude Code)`.

## Scope / provenance
- Only production-source change is `event_drift.py` (`CATALOG_FIXTURE_PATH` re-point + comment) — no
  check weakened (mutant proved the S8 tooth still bites). Test re-points honest (assertions
  2.1.251→2.1.252, task→M0-T132; structural checks retained; one justified loosening
  `assertEqual→assertIn` for the descriptive `requirement` string). Everything outside `tools/` is
  control-plane evidence only.

## Notes / non-blocking
- Producer's honest disclosures (doctor --live control-response FAILED as a Fable-cap artifact;
  routing on opus not Fable; journal probe-record refreshed while transitions=35/audit=85 unchanged)
  are outside the G4 test-count/drift scope and consistent with observations.
- Scope boundary: independent directive-compliance verification of all 18 requirements (R431–R448) is
  the separate DCV pass (producer ≠ verifier), not covered here.

## Blocking gaps
None. **G4 verdict: PASS.**
