# M0-T101 — G0 readiness (administrative)

**Task:** D-027 follow-up: admit `statusLine` into the MCP-policy validator shape table.
**Recorded by:** orchestrator · 2026-08-26 UTC · session `session_01HfptKuEs3RDxaxsSHJjc7t`.

- **Discovery evidence:** full-suite chunk run for the M0-T090 baseline duty →
  `tools/test_mcp_policy.py` **5 failed** (`test_committed_settings_pass`,
  `test_extra_deny_rules_alongside_wildcard_pass`, `test_intact_fixture_passes_in_temp_dir`,
  `test_main_check_exit_zero`, `test_valid_default_mode_passes`); live
  `python tools/validate_mcp_policy.py --check` → `p9 unknown settings key 'statusLine'`.
- **Root cause:** accepted M0-T100 (D-027) added the `statusLine` key to `.claude/settings.json`
  without the validator's required same-change `KNOWN_KEY_SHAPES` extension. Post-acceptance
  discovery ⇒ NEW bounded follow-up task; the accepted M0-T100 record is immutable and untouched.
- **Fix path is the validator's own designed extension** (its p9 message and docstring lines
  39–50 prescribe exactly this reviewed change). No MCP rule weakened; the new shape is strict
  and pins the exact D-027-authorized command string (fail closed on any variation).
- **Citations:** `D-020:ALL;D-027:ALL` — `evaluate_task_refs` ok, applicable set empty (all
  rows bind their original tasks/sentinels), no missing ids. Bootstrap Gate 0 unchanged this
  session (verified at M0-T100-G0). Dependency M0-T100 accepted. Suite context: baseline
  currently 5 failed / 2523 passed / 3 skipped on the non-directive chunk; this task must
  return `test_mcp_policy.py` to green and unblock the M0-T090 baseline duty.
- Gates: G0 (this record) → G2 → independent G5 (security-reviewer) + DCV → accept.

**G0 verdict: PASS — packet ready to claim.**
