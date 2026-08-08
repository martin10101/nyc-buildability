# M0-T049 — G5 security review — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel
(transport entity-decoding only: `&amp;`→`&`, `&lt;`→`<`, `&gt;`→`>`). Reviewer:
security-reviewer (read-only). Frozen review identity `bb169e58397eb968f79451d44e5204305841410f`;
script blob `ca3811cd…`. Recorded by the orchestrator 2026-08-08.

---

I have completed all verification. Let me compile the G5 report.

I independently reproduced every material claim at the frozen content identity (script blob `ca3811cd...` and test blob `6854d9b...`, both byte-stable from the frozen review SHA `bb169e5` through current HEAD `ac92558`, working tree matches with no drift). Here is my full report.

---

# G5 SECURITY REVIEW — M0-T049 (hardening-script PS 5.1 parser-defect fix)

**Task:** M0-T049 — "Fix hardening-script PS5.1 parser defect + whole-script parse regression test (owner source-019)"
**Directive:** D-010 source-019, requirements R173–R183 (in-regime; `directive_refs` present)
**Reviewed identity:** control branch `control/M0-T049-hardening-parse-fix`; frozen review SHA `bb169e58397eb968f79451d44e5204305841410f`; delta = task commit `47a2721` vs `c298159`/main
**Script blob (reviewed):** `ca3811cd7e38a044bd0e01056e95b5028b6ce615` (replaces BARRED defective `0f01d649a64a4fcb1f96b805564cc40889d9a389`)
**Reviewer:** security-reviewer (read-only); environment Windows 11, Windows PowerShell **5.1.26100.8875**, Python 3.11.9, unelevated (IsAdmin=False)
**Verdict:** **PASS** — I CLEAR the repaired script for the owner's elevated execution (conditions in §Interim-Risk).

---

## 1. Content-identity & scope verification (reproduced)

- `git rev-parse bb169e5:tools/agent_supervisor/harden_controller_config.ps1` = `ca3811cd…` ; identical at `47a2721`, at HEAD `ac92558`, and `git hash-object` of the working file = `ca3811cd…` → **no drift, material identity stable across the frozen SHA → HEAD**.
- Old defective blob at main `c298159` = `0f01d649…` (the barred blob) — confirmed.
- Implementation delta (`c298159..47a2721`) = exactly three files: `harden_controller_config.ps1` (8 lines = 4 one-token changes), `tools/test_agent_supervisor_os_acl.py` (+43), `M0-T049-producer-report.md`. No supervisor `.py`, no `.toml`, no `model_selection`, no activation surface. All within `allowed_paths`.

## 2. Charge 1 — Elevated-execution safety of the repaired script

The `git diff` shows the ONLY code change is the four interpolations moving to the brace form:

- L130 `"$UnelevatedUser:(M)"` → `"${UnelevatedUser}:(M)"` (rollback, file)
- L132 → `"${UnelevatedUser}:(M)"` (rollback, dir)
- L154 `"$UnelevatedUser:(RX)"` → `"${UnelevatedUser}:(RX)"` (apply, file)
- L165 → `"${UnelevatedUser}:(RX)"` (apply, dir)

`${UnelevatedUser}` is a name-delimiter only: it references the identical variable and produces the identical runtime value; `:(M)`/`:(RX)` are appended literally. So the four icacls argument strings render exactly `<user>:(M)` / `<user>:(RX)`. The brace form **cannot change WHO gets WHAT** — the value is unchanged, the grant target and rights are unchanged, and if the value carries spaces or a `DOMAIN\` prefix (e.g. `CORP\alice`, `MACHINE\John Doe`) it still renders as one token `CORP\alice:(RX)` (same as the already-reviewed `"NT AUTHORITY\SYSTEM:(F)"`).

End-to-end apply path traced at the frozen identity and confirmed byte-identical to the M0-T046-reviewed semantics apart from parseability:
- Elevation refusal (`Test-IsElevated` → `exit 2`) — unchanged, and only reachable after the file fully parses.
- Absolute System32 binding of `icacls.exe`/`takeown.exe` — unchanged (anti-PATH-hijack).
- Ownership → Administrators via `takeown /F <file|dir> /A` — unchanged.
- Inheritance removal `/inheritance:r` then explicit ACLs: file `Administrators:(F)`, `SYSTEM:(F)`, user `(RX)`; parent `Administrators:(OI)(CI)(F)`, `SYSTEM:(OI)(CI)(F)`, user `(RX)` — unchanged (only the user token gained braces).
- Idempotent `/grant:r`, reversible `-Rollback`, `-DryRun`, never edits contents — unchanged.

**Result: exactly the reviewed semantics with parseability the only difference.** No finding.

## 3. Charge 2 — Injection / robustness

`Invoke-Step` calls `& $Exe @Args` with `[string[]]$Args` — the arguments are **pre-tokenized array elements splatted to the call operator (no cmd.exe, no shell string)**; `$shown` is display-only. `"${UnelevatedUser}:(RX)"` is a single array element regardless of spaces/backslashes/domain prefix, so no shell-metacharacter injection into icacls is possible, and a caller-supplied value cannot inject a *separate* icacls argument (worst case a malformed principal → icacls non-zero → `Invoke-Step` throws → no bad grant applied). The brace change is a parse-time delimiter only: it **neither adds nor removes** injection surface versus the (never-executed) intended pre-defect form. `$UnelevatedUser` is owner-trusted here (elevated, owner-run script). Confirmed: arrays of pre-tokenized args, not a shell string. No finding.

## 4. Charge 3 — Defect-class completeness (independent sweep)

Whole-file regex sweep `\$[A-Za-z_][A-Za-z0-9_]*:` returned only lines 40 (doc comment), 67 (param default), 80 (`Join-Path`) — all `$env:` provider/drive-qualified uses, which are **legitimate** (not the defect class). The four `$UnelevatedUser:` occurrences no longer match (now brace-delimited). Definitive corroboration: the WinPS 5.1 parser returned **`parse_errors=0` for the entire repaired file**, which proves no `$var:` (or any other) interpolation hazard remains anywhere. **No residual occurrences.** No finding.

## 5. Charge 4 — Regression-test sufficiency (masquerade hole)

I ran the WinPS 5.1 language parser API directly against both actual git blobs (piped via stdin, no file writes):

```
DEFECTIVE blob 0f01d64 → parse_errors=4
 130: Variable reference is not valid. ':' was not followed by a valid variable name character. Consider using ${} to delimit the name.
 132: (same)   154: (same)   165: (same)
REPAIRED blob ca3811c → parse_errors=0
WinPS version: 5.1.26100.8875
```

- `test_script_parses_cleanly_under_windows_powershell_51` uses `[System.Management.Automation.Language.Parser]::ParseFile` via `powershell.exe` (WinPS 5.1 tokenizer, not pwsh) and asserts the first line == `parse_errors=0`. Because the defective blob yields `parse_errors=4`, the test is **provably RED on pre-fix behavior** — the masquerade hole (a parse failure exiting non-zero like the elevation refusal) is closed by asserting on the parser error list, not exit codes. Confirmed the test actually RAN (not skipped) on this box: `HardenScriptTests::test_script_parses_cleanly_under_windows_powershell_51 PASSED`.
- The refusal test `test_script_refuses_to_run_unelevated` now additionally asserts `assertNotIn("variable reference is not valid", combined)`. The real WinPS error string is "**Variable reference is not valid.** ':' was not followed…", so a parse error masquerading as an elevation refusal would now fail this test too. Confirmed it RAN (unelevated box): PASSED. So the refusal is asserted to come from the script's OWN elevation check (line 106), reachable only after a clean parse.

**Residual gap (Finding L-1, LOW/advisory):** both PS tests are gated by `@unittest.skipUnless(IS_WINDOWS and shutil.which("powershell"), …)`. On a runner without Windows PowerShell (Linux CI, or a Windows box where `powershell.exe` is off PATH) they **silently skip** rather than fail, so a future parse-class regression could ship green *in that environment*. Not blocking: the fix is proven here on real WinPS 5.1, the owner's elevated run is on Windows, and G3/G5 reproduce `parse_errors=0` at the frozen identity. For durable protection, enforce the parse test on a Windows CI leg (or hard-fail when powershell is expected-but-absent in the environment that gates elevation). NOTE (orchestrator): the `supervisor-bridge` CI job runs on `windows-latest`, where `powershell.exe` is present — the parse test executes there.

## 6. Charge 5 — Interim-risk statement

Measured, committed posture (`M0-T049-acl-posture-inspection.md`, reproduced-consistent): `C:\Program Files\SupervisorConfig\config.toml` is **NOT protected at the file level** (`Authenticated Users:(M)`, owner `MLFLL` unelevated — any authenticated local process can rewrite contents; owner can rewrite the DACL). The **parent is protected** (inherited Program Files DACL — no unelevated create/delete/rename/replace). Contents SHA `29eb765e…` intact; **SHADOW-ONLY, nothing activated**.

**Was waiting for this review before elevation safe? YES.** Compensating controls held the whole window: (1) supervisor is shadow-only and unactivated — no automation consumes the config to cause harm; (2) activation gating reads `controller_config_acl.protected`, which is fail-closed and honestly reports NOT_PROTECTED today, so it *blocks* activation (R595 prerequisite unmet); (3) the content-digest gate in `config.py` is fail-closed — any in-place tamper changes the SHA and is rejected; (4) the parent blocks replace-by-rename/sibling-drop, forcing any tamper to be in-place and therefore SHA-detectable. The residual "world-modifiable contents" exposure cannot silently take effect. Deferring the elevated fix to obtain G3/G5 added no material risk beyond what already existed since relocation — correct sequence.

**Required BEFORE the owner's elevated rerun (beyond G3 PASS + G5 PASS + merge):**
1. **Re-verify the config SHA-256 == `29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb` immediately BEFORE the run.** The file is world-modifiable now, so a tamper is possible; the hardening script never edits contents, so a pre-run mismatch means tamper — **STOP; do not harden a tampered file.**
2. **Re-verify the SHA is unchanged immediately AFTER** (it must be — the script does takeown/icacls only, never content).
3. Confirm the elevated run uses the **merged** blob `ca3811cd…` (not the barred `0f01d649…`).
4. Confirm `-UnelevatedUser` matches the account the ordinary unelevated supervisor actually runs as (see L-2); a `-DryRun` first will print the resolved principal and the exact icacls/takeown commands, changing nothing.
5. After the run, from an UNELEVATED shell confirm `os_acl.evaluate_controller_config_acl` reports **PROTECTED**.

**Exact elevated rerun command (supports R181), from an ELEVATED Windows PowerShell at the repo checkout:**
```
powershell -ExecutionPolicy Bypass -File "tools\agent_supervisor\harden_controller_config.ps1" -ConfigPath "C:\Program Files\SupervisorConfig\config.toml"
```
(Recommended dry run first: append `-DryRun`. If the unelevated supervisor runs as a non-owner account, add `-UnelevatedUser "<DOMAIN\account>"`.)

**Finding L-2 (LOW/operational, pre-existing — not introduced by this delta):** `-UnelevatedUser` defaults to the elevating owner's account (`$env:USERDOMAIN\$env:USERNAME`). If the ordinary supervisor runs as a *different* account, the default grants RX to the wrong principal (intended reader loses read, or a different account gains it). Verify/override via `-DryRun` before the real run.

## 7. Charge 6 — Boundary compliance (R182/R183)

**PASS.** Delta confined to the parser fix + tests + report:
- `harden_controller_config.ps1`: 4-line brace fix only (blob `0f01d64`→`ca3811c`); ACL grant semantics byte-identical otherwise → **no ACL redesign**.
- `tools/test_agent_supervisor_os_acl.py`: +43 (parse test + refusal-test hardening) → the missing regression test only.
- No file under `tools/agent_supervisor/*.py` changed → **no supervisor work**.
- No `.toml` / config data / `model_selection.toml` / activation surface touched → **R182 (model_selection unchanged & mutable) and R183 (no broadening) satisfied.**

## 8. Per-requirement (R173–R183) independent findings at frozen identity

| Req | Class | Status | Basis (reproduced) |
|-----|-------|--------|--------------------|
| R173 | hold | RESPECTED | Nothing activated; config not moved (still `…SupervisorConfig\config.toml`); contents SHA `29eb765e…` intact; delta touches no content/activation surface. |
| R174 | obligation | SATISFIED | Parse defect fixed; repaired blob → `parse_errors=0`; unelevated run reaches its own elevation refusal (post-parse). |
| R175 | obligation | SATISFIED | `M0-T049-acl-posture-inspection.md` honestly reports file NOT_PROTECTED, parent protected, SHA intact — does not assume PROTECTED. |
| R176 | obligation | SATISFIED | Exactly 4 brace-form changes; whole-file sweep + `parse_errors=0` prove every occurrence fixed, nothing else edited. |
| R177 | obligation | SATISFIED | `test_script_parses_cleanly_under_windows_powershell_51` via `Parser::ParseFile`/powershell.exe asserting `parse_errors=0`; RAN GREEN; proven RED (=4) on defective blob. |
| R178 | obligation | SATISFIED | os_acl suite **32 passed**; full supervisor suite **1381 passed, 2 skipped, 0 failures** (≥1165 freeze baseline met). |
| R179 | sequencing | IN PROGRESS | This G5 = PASS. **Elevation additionally requires G3 PASS + merge** (see verdict conditions). |
| R180 | obligation | SATISFIED | New blob `ca3811cd7e38a044bd0e01056e95b5028b6ce615`; old `0f01d649…` independently confirmed defective (parse_errors=4) — barred from elevation. |
| R181 | return | ENABLED | Exact new blob + exact elevated rerun command provided above; final return is post-merge (orchestrator/owner lane). |
| R182 | prohibition | SATISFIED | No `.toml`/`model_selection` touched. |
| R183 | prohibition | SATISFIED | No ACL redesign / supervisor `.py` change; only parser defect + regression test. |

(The formal per-requirement `verification.json` is the independent directive-compliance-verifier's record; the above are my security-lane confirmations.)

## 9. Findings by severity

- **Critical:** none.
- **High:** none.
- **Medium:** none.
- **Low L-1 (advisory):** parse regression test silently skips where Windows PowerShell is absent; enforce it on a Windows CI leg or hard-fail-when-expected so a future parse-class regression cannot ship green in a non-Windows environment. Not blocking (fix proven here; elevation path is Windows).
- **Low L-2 (operational, pre-existing):** `-UnelevatedUser` default may not match the actual unelevated supervisor account — verify via `-DryRun` before the elevated run.
- **Informational:** PS 5.1 native-argument quoting quirks exist for pathological values (embedded quotes), but args are pre-tokenized array elements via `& $Exe @Args` (no shell), `$UnelevatedUser` is owner-trusted, and the brace change does not affect this surface. Not a defect.

## 10. Clearance & verdict

I **clear the repaired script (blob `ca3811cd7e38a044bd0e01056e95b5028b6ce615`) for the owner's elevated execution**, conditioned on: (a) G3 also PASS; (b) merge to main so the elevated run uses the merged blob; (c) pre-run and post-run config SHA re-verification == `29eb765e…`; (d) `-UnelevatedUser` confirmed via `-DryRun` to match the unelevated supervisor account. The security-relevant repaired-script behavior is exactly the M0-T046-reviewed semantics with parseability the only change; the masquerade hole is closed; boundary and prohibitions (R182/R183) are honored.

**VERDICT: PASS** (with two LOW advisory notes L-1, L-2 — neither blocks this gate or the elevated rerun given the stated pre-run SHA re-verification).

Relevant files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_agent_supervisor_os_acl.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T049-acl-posture-inspection.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T049-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\source-019-amendment.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T049.json`
