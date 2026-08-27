# M0-T108 G5 security review (VERBATIM save)

Reviewer: independent read-only `security-reviewer` (unnamed spawn), governed live by the guard
under review; reviewed at frozen deliverable identity `4e238b5` (HEAD `ded625a` = control-plane
records only). Returned through the agent-return channel 2026-08-27 UTC and saved verbatim below
(transport entity-decoding only; the harness neutralized `<`/`>`/`&` and flagged the output as
instruction-shaped — control tags were neutralized and the content is preserved here as reviewer
findings, not instructions).

---

All mandated checks complete. Every fail-closed case denies; the PowerShell branch cannot fail open. Here is my full gate report.

---

# Gate Report

- **Gate ID:** G5 (security)
- **Task ID:** M0-T108 — close the `readonly_agent_guard.py` PowerShell/scripting write gap (remediates the G5 M0-T102 MEDIUM advisory)
- **Reviewer:** independent read-only `security-reviewer` (unnamed spawn), governed live by the guard under review
- **Producer:** `fable-orchestrator-session`
- **Result:** PASS (with required corrections C1–C4 that are BLOCKING for acceptance)
- **Clean environment/worktree used:** reviewed at frozen content identity `4e238b5`; confirmed `git diff --name-only 4e238b5..ded625a` advances control-plane records only (gates/reports/state/task), deliverable bytes frozen. Deliverable diff = `git diff 24aa061..4e238b5`.

## Acceptance criteria reviewed

The four M0-T102 remediation criteria (from `project-control/reports/M0-T102-G5-security.md`), plus the six mandated bypass/hardening checks.

| Criterion | Verdict | Basis |
|---|---|---|
| (i) matcher extends to every write-capable Windows shell tool | PASS | settings.json changed ONLY the matcher line to `Bash\|PowerShell\|Write\|Edit\|MultiEdit\|NotebookEdit`; `SHELL_TOOLS` mirrors it; test asserts sync; live-governed. |
| (ii) PowerShell mutation/redirect denylist mirroring Bash (enumerated cmdlets + `>`/`>>` + git-via-PS, fail-closed envelope) | PASS for every enumerated item; INCOMPLETE beyond it | All objective-named cmdlets deny by full name; but default *aliases* `ac/clc/mi/epcsv/sp/rp` and the COM channel bypass it — C1/C2. |
| (iii) treat scripting class generally + honest residual doc | PARTIAL | scripting-write pass works both shells; residual doc overstates coverage — C4. |
| (iv) reduce read-only false positives (quoted `>` / pure `open(` reads) | PASS for the targeted class; but a NEW FP introduced | quoted-`>` and pure-read FPs fixed and verified; `-Encoding` reads now wrongly denied — C3. |

## Directive/requirement verification

M0-T108 is in-regime (`directive_refs: [{D-024, ALL}]`). The authoritative requirement-by-requirement pass is owned by the independent `directive-compliance-verifier` (producer ≠ verifier, recorded in `verification.json`); I verify the security-relevant D-024 prohibitions and the security substance.

| Requirement class | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024 R146-class prohibitions (no MCP/config, no Agent SDK, no dependency/lockfile, no permission-bypass flags, no protected-PR/`.github` change) | `4e238b5` | PASS | Deliverable file set = guard + settings.json (single matcher line) + test + report; `git diff 24aa061..4e238b5` shows no `.mcp.json`/`mcpServers`/SDK/`package.json`/lockfile/`bypassPermissions`/`--dangerously-skip-permissions`/`.github` delta. |
| D-024 full requirement matrix (ALL) | `4e238b5` | DEFERRED to DCV | Owned by `directive-compliance-verifier`; out of the G5 security lane. |

## Steps independently executed

All from repo root; the guard governs my own tool calls live (identity `security-reviewer`), so my `cat > file` and PowerShell writes were denied during this review — a live positive control.

1. Frozen-identity + deliverable diffs.
2. Reran both regression suites: `python tools/test_readonly_agent_guard.py` → 136 PASS / 0 FAIL; `python tools/test_readonly_agent_guard_powershell.py` → 95 PASS / 0 FAIL (incl. 4 RED-on-mutant proofs).
3. Independent adversarial bypass probe (feeding crafted payloads to the actual guard as `agent_type:"code-reviewer"`): PowerShell write cmdlets/aliases, COM, CIM/WMI, env-persistence, dot-source, redirects.
4. Redirect no-weakening batch (22 forms; `_REDIRECT`→`_unquoted_redirect`).
5. False-positive batch (`-Encoding` reads).
6. Fail-closed envelope batch (malformed JSON, non-object, int/list/string `tool_input`, named/unknown spawn).
7. Leak scan over the four deliverable files; modularity check; captured-payload confirmation of `tool_name=="PowerShell"` casing.

## Expected versus actual

**Confirmed bypasses — guard ALLOWs these for a governed read-only reviewer** (`{"tool_name":"PowerShell","agent_type":"code-reviewer","tool_input":{"command":"<CMD>"}}`; empty stdout = ALLOW = bypass):

| `<CMD>` | Effect | Expected | Actual |
|---|---|---|---|
| `ac x.txt hi` | Add-Content alias — append repo file | DENY | **ALLOW** |
| `clc x.txt` | Clear-Content alias — truncate repo file | DENY | **ALLOW** |
| `mi a.txt b.txt` | Move-Item alias — move/rename repo file | DENY | **ALLOW** |
| `epcsv -Path r.csv -InputObject foo` | Export-Csv alias — write CSV | DENY | **ALLOW** |
| `sp -Path HKCU:Soft -Name v -Value 1` | Set-ItemProperty alias | DENY | **ALLOW** |
| `rp -Path x -Name y` | Remove-ItemProperty alias | DENY | **ALLOW** |
| `$f=New-Object -ComObject Scripting.FileSystemObject; $f.CreateTextFile('x.txt')` | COM — arbitrary file write | DENY | **ALLOW** |
| `$s=New-Object -ComObject Shell.Application; $s.ShellExecute('cmd.exe')` | COM — process exec | DENY | **ALLOW** |
| `Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine='calc'}` | CIM — process spawn | DENY | **ALLOW** |
| `Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList 'calc'` | WMI — process spawn | DENY | **ALLOW** |

**New false-positive — guard DENYs legitimate reads (C3):** `Get-Content -Encoding UTF8 README.md`, `Import-Csv -Encoding UTF8 rows.csv`, `Select-String -Encoding utf8 -Path x.py -Pattern TODO` → all **DENY** (expected ALLOW). Cause: `_PS_ENCODED = (?i)(?:^|\s)-e(?:c|nc\w*)\b` matches `-Encoding` (`-e`+`nc`+`oding`).

**Correctly enforced (spot of the many verified):** `sc`, `ni`, `cpi`, Set/Add/Clear-Content, Out-File, `*-Item[Property]`, Tee-Object, Export-Csv/Clixml, `New-Object …StreamWriter`/`[IO.File]::WriteAllText`, `-OutFile`, `iex`/Invoke-Expression, Start-Process, Add-Type, nested `powershell/pwsh/cmd`, `reg add`, `schtasks /create`, `icacls /grant`, `git push/commit/add` incl. backtick-hidden `git pu`+backtick+`sh` → all DENY. Redirects: `>f`,`>>f`,`&>f`,`&>>f`,`1>f`,`2>realpath`,`3>f`,`*> f`,`>'quoted target'` → DENY; `> $null`,`2>$null`,`*>&1`,`2>&1`,`>&2`,`2>/dev/null` → ALLOW. Quoted `>` (`python -c "1 if 2>1 else 0"`, `-> int`, `grep 'a->b'`) → ALLOW. Fail-closed: malformed JSON, non-object array, int/list/string `tool_input`, named/unknown spawn → all DENY (rc 0, deny decision); the PowerShell branch is pure string ops wrapped by `main()` try/except and cannot throw-and-fail-open.

## Evidence paths

- `.claude/hooks/readonly_agent_guard.py`
- `.claude/settings.json` (matcher line only)
- `tools/test_readonly_agent_guard_powershell.py`
- `tools/test_readonly_agent_guard.py`
- `project-control/reports/M0-T108-guard-powershell-fix.md`
- `tool_name=="PowerShell"` casing confirmed in `project-control/reports/ACTIVATION-2026-08-08-supervised-auto/pending-approvals-post-u1.json:40` and `project-control/reports/M0-T045-r595-rehearsal/estop-run/audit.jsonl:6`

## Human-style walkthrough findings

Live confirmation of machine enforcement: as a governed `security-reviewer`, my `cat > probe.py` and crafted PowerShell/Bash write attempts were denied by the guard mid-review; a benign heredoc (read redirect) and read-only git diffs were allowed — matching intended posture. Lead (no identity) and roster producer `backend-engineer` retain full pass-through (no privilege escalation or de-escalation). Enforcement engages immediately on the extended matcher, replacing the procedural stopgap.

## Regression/security/provenance findings

- No weakening: existing Bash suite 136/136; every prior redirect denial retained under the `_REDIRECT`→`_unquoted_redirect` replacement (22/22 adversarial forms). Frozen identity intact.
- settings.json: no model/env/permissions/statusLine/MCP delta — the single matcher line only.
- Leak scan (guard, PS test, report, settings): no secrets/tokens/home-paths/session-ids/emails; the only match is a legitimate control-command test payload string (`project_control.py accept ...`) the guard must deny.
- Modularity: `python tools/modularity_check.py --check` → 0 failures; guard 589 lines (< 600 warn); not among the 5 pre-existing unrelated warnings.
- Provenance: producer report §2 precisely enumerates covered aliases (`sc ni ri rd del erase md cpi rni ren move copy`), so C1 is an incompleteness, not a false claim; but the docstring's "write cmdlets **and their aliases**" and "its execution vectors ... **are themselves denied**" overstate vs. the confirmed C1/C2 residuals (C4).

## Defects

- **C1 (MEDIUM, required):** `_PS_MUTATING` alias set omits default write aliases `ac` (Add-Content), `clc` (Clear-Content), `mi` (Move-Item), `epcsv` (Export-Csv), `sp` (Set-ItemProperty), `rp` (Remove-ItemProperty) — confirmed trivial repo-file writes for a read-only reviewer, even though the underlying cmdlets are blocked by full name. Add them (and audit the full default-alias table for write cmdlets already covered by name).
- **C2 (MEDIUM, required; task-flagged vector):** COM channel uncovered — `New-Object -ComObject Scripting.FileSystemObject` (`.CreateTextFile`/`.OpenTextFile(...,8)`) writes arbitrary files; `Shell.Application.ShellExecute` and CIM/WMI `Win32_Process.Create` spawn processes (same dynamic-execution class as the already-denied `Start-Process`/nested shells). Deny `New-Object\s+-ComObject` and the CIM/WMI `Create` methods, or document them as explicit residuals (objective iii).
- **C3 (MEDIUM, required):** NEW false-positive contrary to objective (iv). `_PS_ENCODED` denies legitimate reads using `-Encoding` (`Get-Content`/`Import-Csv`/`Select-String -Encoding`). It is also redundant for the real threat (an encoded command executes only via `powershell`/`pwsh`, already denied by the nested-shell rule). Scope it to fire only after a `powershell`/`pwsh` token, or remove it.
- **C4 (LOW, required):** Make residual documentation honest — the docstring's "and their aliases" / "execution vectors ... are themselves denied" overstate; either close C1/C2 or enumerate the alias-subset and COM/CIM/dot-source residuals explicitly.

Non-blocking advisories (note only, out of the repo-write core scope): `[Environment]::SetEnvironmentVariable(...,'Machine'/'User')` persists env/registry state; `Set-Clipboard` writes the clipboard; dot-source / `./script.ps1` executes a pre-existing script (a reviewer cannot create one, so low practical risk). Minor residual: `tool_name=="PowerShell"` casing is confirmed from supervisor/audit captures but not from a PreToolUse-specific payload — opportunistically capture one (as M0-T028 did for Bash).

## Required rework

Apply C1–C3 (and C4) and add analogous RED-on-mutant regression cases: assert `ac/clc/mi/epcsv/sp/rp` DENY, `New-Object -ComObject`/CIM-WMI `Create` DENY-or-documented, and `Get-Content -Encoding UTF8 f` ALLOW. Re-gate. Rationale for keeping these BLOCKING-for-acceptance: this is the dedicated "close the PowerShell write gap" task; accepting it while `ac x.txt hi` and a COM `CreateTextFile` still write would record "gap closed" in the ledger contrary to the project's provenance principle.

## Reviewer conclusion

The remediation is fundamentally sound and strictly improves posture: the matcher + `SHELL_TOOLS` branch, the named-cmdlet/.NET/redirect/git-via-PowerShell denylist, the quote-aware redirect FP fix, the both-shell scripting-write pass, and the fail-closed envelope are all correct and independently reproduced, with the existing Bash pack unweakened (136/136) and no leaks or modularity regressions. Machine enforcement is confirmed active and correctly casing-matched. No BLOCKING security defect exists in the strict sense: the confirmed residual (alias/COM/CIM writes) is a strict subset of the surface the M0-T102 G5 already rated MEDIUM-not-blocking, and it remains compensated by the documented orchestrator-only integration model. However, the dedicated fix ships with demonstrable, trivial bypasses (C1/C2), a new fail-safe false-positive (C3), and an over-stated residual claim (C4), which must be corrected before this task is ACCEPTED as "gap closed."

**G5: PASS** (required corrections C1–C4 are blocking for the next gate and for acceptance, per the project gate-verdict semantics — record via `progress --message`, do not accept until applied, validated, and committed).
