# M0-T049 Producer Report — PowerShell 5.1 parser defect fix in the elevated hardening script

Task: M0-T049 (owner directive D-010 source-019, requirements R173–R183).
Scope: narrowly bounded pre-activation defect fix — a demonstrated Windows PowerShell 5.1
PARSER failure in `tools/agent_supervisor/harden_controller_config.ps1`, plus the missing
parse regression test. Producer lane only; the orchestrator records the ledger/gate.

Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/orch`
Branch: `task/M0-T049-hardening-parse-fix`
Base HEAD at start: `c2981592051594670631a117b458347ede36e395` (= current main)
Environment: Windows 11, Windows PowerShell 5.1.26100.8875 (`powershell.exe`), unelevated session.

---

## 1. The defect

PowerShell parses a `:` immediately after an interpolated variable reference as a
scope/drive qualifier (e.g. `$global:`, `$env:`). So `"$UnelevatedUser:(M)"` is read as
"variable in scope `UnelevatedUser` named `(M)`", which is a hard PARSE error of the WHOLE
file — it fails before any ACL change (indeed before the elevation check) ever runs. The
owner reproduced this by running the script elevated: it failed to parse.

`env:` in this same file (`$env:USERDOMAIN`, `$env:USERNAME` at lines 40/67; `$env:SystemRoot`
at line 80) is NOT this defect — `env:` is a real, valid namespace qualifier and is the
intended way to read environment variables. Only a plain variable followed by `:` and a
non-name character is the hazard.

## 2. The four interpolation fixes (exact diff — R174/R176)

Replaced the ambiguous `"$Var:..."` with the unambiguous brace form `"${Var}:..."`. Nothing
else in the file was changed (no restructure, rename, reformat, or "improvement").

| Line | Before | After |
|------|--------|-------|
| 130 (rollback, file) | `"$UnelevatedUser:(M)"` | `"${UnelevatedUser}:(M)"` |
| 132 (rollback, dir)  | `"$UnelevatedUser:(M)"` | `"${UnelevatedUser}:(M)"` |
| 154 (apply, file)    | `"$UnelevatedUser:(RX)"` | `"${UnelevatedUser}:(RX)"` |
| 165 (apply, dir)     | `"$UnelevatedUser:(RX)"` | `"${UnelevatedUser}:(RX)"` |

`git diff` confirms exactly these four one-token changes and nothing else.

### Whole-file audit for the same defect class (R176)

Grep for `\$[A-Za-z_][A-Za-z0-9_]*:` across the file returned only:
- lines 40, 67, 80 → `$env:...` — legitimate namespace qualifier, NOT a defect;
- lines 130, 132, 154, 165 → the four fixed occurrences.

**Additional same-class occurrences beyond the four: NONE.**

## 3. Parse regression test (R177)

Added to the existing `tools/test_agent_supervisor_os_acl.py`, class `HardenScriptTests`
(matching the suite's platform-guard style):

`test_script_parses_cleanly_under_windows_powershell_51`

Design and why the parser API (not exit codes) is load-bearing:

- The prior test `test_script_refuses_to_run_unelevated` asserts only a NON-ZERO exit plus
  the word "elevated" in output. A PARSE failure ALSO exits non-zero — and the defective
  file's message happens to be unrelated — so a parse failure could masquerade as the
  intended "refuses unelevated" refusal. Exit codes cannot distinguish "parsed then refused"
  from "never parsed".
- The new test therefore invokes the Windows PowerShell 5.1 language parser API directly:
  `[System.Management.Automation.Language.Parser]::ParseFile(path,[ref]$t,[ref]$e)`, run via
  `powershell.exe` (Windows PowerShell 5.1 — NOT `pwsh`, so 5.1 tokenizer semantics apply),
  and asserts the error count is exactly `parse_errors=0`, printing every error message
  (line-prefixed) on failure for diagnosability.
- Skips gracefully off-Windows / when `powershell` is absent
  (`@unittest.skipUnless(IS_WINDOWS and shutil.which("powershell"), ...)`).

I also hardened `test_script_refuses_to_run_unelevated` with one extra assertion: the refusal
output must NOT contain "variable reference is not valid" (i.e. the refusal must be the
script's own elevation refusal, never a parse error masquerading as one).

## 4. RED-on-pre-fix proof (R177/R178)

Reconstructed the defective content OUTSIDE the repo (scratchpad) by reverting the four
brace fixes, then ran the exact parser API the new test uses:

```
=== confirm reverted lines ===
130:    Invoke-Step $Icacls @($file, "/grant", "$UnelevatedUser:(M)")
132:    Invoke-Step $Icacls @($dir, "/grant", "$UnelevatedUser:(M)")
154:    "$UnelevatedUser:(RX)")
165:    "$UnelevatedUser:(RX)")
=== PARSE PRE-FIX (defective) SCRIPT ===
parse_errors=4
130: Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to delimit the name.
132: Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to delimit the name.
154: Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to delimit the name.
165: Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to delimit the name.
```

The new test asserts the first line equals `parse_errors=0`; against the defective file it
sees `parse_errors=4`, so the test is RED on pre-fix. (Exit-code-only checks would have
stayed GREEN here.)

Corroborating: running the DEFECTIVE script unelevated fails with the parse error at line
130 and NEVER reaches the elevation refusal at line 106:

```
...prefix_defective.ps1:130 char:45
+     Invoke-Step $Icacls @($file, "/grant", "$UnelevatedUser:(M)")
+                                             ~~~~~~~~~~~~~~~~
Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to delimit the name.
```

## 5. Fixed script parses AND refuses cleanly (R174/R178)

Parser API on the FIXED (committed) script:

```
=== PARSE FIXED SCRIPT ===
parse_errors=0
```

Running the FIXED script UNELEVATED with a dummy `-ConfigPath` (session is not elevated —
`IsInRole(Administrator)` = False) refuses for the RIGHT reason: the script's OWN elevation
refusal at line 106 (`Write-Error`), which is only reachable AFTER the file fully parses. It
touched nothing.

```
harden_controller_config.ps1 : refusing to run: this script MUST run elevated (UAC). It transfers
ownership and rewrites ACLs, which requires administrative rights. Re-launch an elevated
PowerShell and run it again.
At ...\harden_controller_config.ps1:106 char:5
+     Write-Error ("refusing to run: this script MUST run elevated (UAC ...
```

## 6. Test counts (R178)

- `python -m pytest tools/test_agent_supervisor_os_acl.py -q` → **32 passed** in 2.68s.
  (New parse test confirmed RUN, not skipped, via `-v`: PASSED.)
- `python -m pytest tools/test_agent_supervisor_*.py -q` → **1381 passed, 2 skipped** in
  111.54s.
  - Baseline at c298159: 1380 passed / 2 skipped.
  - Delta: +1 passed = the single new test only. 2 skipped unchanged (the unelevated-run and
    other platform-guarded tests behave as before).

## 7. Per-requirement producer evidence (R174, R176, R177, R178)

| Req | Producer obligation (per packet) | Evidence |
|-----|----------------------------------|----------|
| R174 | Fix the demonstrated PS5.1 parse defect so the script parses & runs elevated | `harden_controller_config.ps1` lines 130,132,154,165 → `${UnelevatedUser}` brace form; parser API on fixed file → `parse_errors=0`; unelevated run reaches its own elevation refusal at line 106 (fully parsed) |
| R176 | Change ONLY those four interpolations; no other edits; audit for same-class hazard | `git diff` = exactly 4 one-token changes; whole-file grep audit → only `$env:` (legitimate) + the 4 fixed; additional same-class occurrences: NONE |
| R177 | Add a parse regression test via the PS5.1 parser API (exit codes insufficient) | `test_script_parses_cleanly_under_windows_powershell_51` in `tools/test_agent_supervisor_os_acl.py` (class `HardenScriptTests`); uses `[Parser]::ParseFile` via `powershell.exe`, asserts `parse_errors=0`; skips off-Windows; plus parse-error guard added to `test_script_refuses_to_run_unelevated` |
| R178 | Prove RED on pre-fix; re-run os_acl + full supervisor suites | RED: parser API on reconstructed defective file → `parse_errors=4` at lines 130/132/154/165. GREEN: os_acl 32 passed; full suite 1381 passed / 2 skipped (baseline 1380/2, delta +1) |

R173, R175, R179–R183 are orchestrator/owner-lane (control-plane ledger transitions, gate
adjudication, activation-package sequencing, and any owner elevated re-run on the real
config). Not producer-actionable and not touched here.

## 8. Files changed

- `tools/agent_supervisor/harden_controller_config.ps1` — 4 lines: 130, 132, 154, 165.
- `tools/test_agent_supervisor_os_acl.py` — added
  `test_script_parses_cleanly_under_windows_powershell_51` and hardened
  `test_script_refuses_to_run_unelevated` (both in class `HardenScriptTests`).
- `project-control/reports/M0-T049-producer-report.md` — this report.

No config files, ACLs, supervisor code, `model_selection.toml`, activation surfaces, or any
path outside the worktree were touched. The defective reconstruction lived only in the
session scratchpad, outside the repo.

## 9. Deviations / uncertainty

- The exact prose of R173–R183 lives in D-010 source-019; requirements above are mapped from
  the task packet's description. The producer-actionable set (R174/R176/R177/R178) is fully
  substantiated; requirement-text adjudication is the verifier/orchestrator's call.
- CRLF note: `git diff` warns "LF will be replaced by CRLF" for the `.ps1` — this is the
  repo's existing line-ending normalization, not a change introduced by this task.
- Requested status: awaiting_gate.
