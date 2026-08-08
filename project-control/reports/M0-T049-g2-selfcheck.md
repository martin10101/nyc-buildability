# M0-T049 — G2 self-check (producer self-checks + orchestrator reproduction)

Recorded by the orchestrator 2026-08-08 at frozen identity `bb169e5` (code head `47a2721`).

- **Diff shape verified twice** (producer + orchestrator `git diff`): exactly the four
  interpolation lines in `harden_controller_config.ps1` (130/132 rollback `(M)`, 154/165 apply
  `(RX)`) changed to the `${UnelevatedUser}` brace form; plus one test-class addition in
  `test_agent_supervisor_os_acl.py`; plus the producer report. Nothing else.
- **Whole-file same-class sweep:** grep `\$[A-Za-z_]+:` → only `$env:` namespace uses
  (lines 40/67/80, legitimate) besides the four fixed lines. NONE additional.
- **Parse regression test** (`HardenScriptTests::test_script_parses_cleanly_under_windows_powershell_51`)
  uses the Windows PowerShell 5.1 parser API and asserts zero parse errors; confirmed RUN (not
  skipped) on this host. RED-on-pre-fix proven: reconstructed defective content outside the repo
  → `parse_errors=4`, one per affected line, each "Variable reference is not valid. ':' was not
  followed by a valid variable name character." — the exact owner-observed failure. The existing
  unelevated-refusal test is hardened to assert the refusal is NOT a parse error (the masquerade
  that let the defect slip).
- **Unelevated behavior of the FIXED script:** parses clean (`parse_errors=0`) and refuses at its
  own elevation check (line 106 Write-Error), never touching any file.
- **Suites:** `test_agent_supervisor_os_acl.py` → 32 passed. Full supervisor suite → **1381
  passed / 2 skipped** (baseline 1380/2; delta = the one new test) — producer run + independent
  orchestrator reproduction.
- **Boundaries:** no config file, ACL, activation surface, or out-of-worktree path touched;
  model_selection.toml untouched; no supervisor code change.

Self-check PASS; ready for independent G3 + G5 delta review (R179).
