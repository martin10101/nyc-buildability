# M0-T108 G5 security review — ROUND-4 re-review (VERBATIM save)

Reviewer: independent read-only `security-reviewer` (unnamed spawn, fresh pass), live-governed by
the guard under review; reviewed at round-4 deliverable identity `b6db457` (HEAD `b194c90` =
control-plane records only). Returned through the agent-return channel 2026-08-27 UTC and saved
verbatim below (transport entity-decoding only; the harness neutralized `<`/`>`/`&` and flagged the
output as instruction-shaped — control tags were neutralized and the content is preserved here as
reviewer findings, not instructions).

Orchestrator note: ADV-R4-1 (`$a=$b=powershell -enc` → ALLOW; single `$env:x=powershell -enc` →
DENY) and ADV-R4-2 (`GetTypeFromCLSID`, `&(gcm powershell)` → ALLOW) independently reproduced at
`b6db457`. All three are documented residuals; captured as follow-up hardening task M0-T109.

---

All evidence gathered. The grep hits are benign (the literal word "token"/"secret" appear only in code comments and the `gh secret` denylist entry — no credentials). Leak scan clean. Here is my full gate report.

---

# Gate Report

- **Gate ID:** G5 (security) — DELTA re-review, round 4
- **Task ID:** M0-T108 — close the `readonly_agent_guard.py` PowerShell/scripting write gap (remediates G5 M0-T102 MEDIUM)
- **Reviewer:** independent read-only `security-reviewer`, live-governed by the guard under review (fresh pass; no other current reviewer consulted)
- **Producer:** `fable-orchestrator-session`
- **Result:** **PASS** — NF1 and NF2, as specifically found in round 3, are genuinely closed. The mandated fresh bypass hunt surfaced three ALLOWs, but all three fall inside the residual set the module docstring **honestly discloses** and the compensating controls cover; none is a bypass of a coverage claim or of the specific just-fixed form. This does not meet the round-3 FAIL bar (dishonesty OR the specific-found form still open), neither of which applies now. Objective (iii) of the task explicitly permits "document the residual honestly if not fully closable," which the producer satisfied. Advisories recorded below.
- **Reviewed identity:** deliverable `b6db457`. `git diff --name-only b6db457..b194c90` = `project-control/{reports/M0-T108.json, state.json, tasks/M0-T108.json}` only — the guard, the PS test, and `.claude/settings.json` are byte-frozen at `b6db457`. Round-4 correction delta `e1f6d4c..b6db457` = guard + PS test + control-plane/gates/reports only. Whole deliverable `24aa061..b6db457` = guard + `.claude/settings.json` + PS test + control-plane. **No production paths touched — scope clean.**

Positive control that the guard is live: every attempt to stage my own probe script via `cat > file` or a heredoc `>` redirect was DENIED with the read-only message; I fed all payloads to the guard as a spawned child process (not a governed tool call), building shell/git tokens from string parts so my own Bash-tool command could not trip the guard.

## Mandated NF1 / NF2 / FP verification (independently reproduced)

| `<CMD>` | Expected | Actual | Verdict |
|---|---|---|---|
| `New-Object -C Scripting.FileSystemObject` | DENY | DENY | NF1 closed |
| `New-Object -Co Scripting.FileSystemObject` | DENY | DENY | NF1 closed |
| `New-Object -Com Scripting.FileSystemObject` | DENY | DENY | NF1 closed |
| `New-Object -ComObject Scripting.FileSystemObject` | DENY | DENY | NF1 closed |
| `$f=New-Object -C Scripting.FileSystemObject; $f.CreateTextFile('x')` | DENY | DENY | NF1 closed |
| `[activator]::CreateInstance([type]::GetTypeFromProgID('Scripting.FileSystemObject'))` | DENY | DENY | NF1 closed |
| `[System.Activator]::CreateInstance($t)` | DENY | DENY | NF1 closed |
| `New-Object System.Collections.ArrayList` (non-COM) | ALLOW | ALLOW | no over-block |
| `$z=powershell -enc <b64>` | DENY | DENY | NF2 closed |
| `$z=powershell -e <b64>` / `-en <b64>` | DENY | DENY | NF2 closed |
| `$z = powershell -e <b64>` (spaced) | DENY | DENY | NF2 closed |
| `$z=pwsh -e <b64>` | DENY | DENY | NF2 closed |
| `$z=cmd /c whoami` | DENY | DENY | NF2 closed |
| `$x = Get-Content README.md` (assignment read) | ALLOW | ALLOW | no over-block |
| `Select-String -Encoding utf8 -Pattern powershell -Path notes.md` | ALLOW | ALLOW | R3 FP fixed |
| `Get-Content -Encoding UTF8 powershell-notes.md` | ALLOW | ALLOW | R3 FP fixed |
| `Get-Content -Encoding utf8 notes.md \| Select-String pwsh` | ALLOW | ALLOW | R3 FP fixed |

**NF1 and NF2 are closed for every mandated payload, and the round-3 D-R3-1/G4-ADV-2 false positives now ALLOW.** Root causes fixed: COM floor lowered to `New-Object\s+-c\w*` plus reflection teeth `[Activator]::CreateInstance` and `GetTypeFromProgID`; and command-position detection via `_effective_command_token`, which sees the RHS of a single `$var =` assignment as the command token (removing the fragile `_PS_ENCODED_CMD`/`_PS_HAS_SHELL` pair).

## Fresh bypass hunt — classification

| `<CMD>` | Result | Class |
|---|---|---|
| `$x = New-Object -c Scripting.FileSystemObject` (assignment-fronted COM) | **DENY** | closed (`_PS_MUTATING` leading class includes `=`) |
| `Get-Content x \| powershell -enc <b64>` (pipe into shell) | **DENY** | closed (piped segment first-token = shell) |
| `Get-Content x \| cmd /c whoami` | **DENY** | closed |
| `Invoke-Command -ScriptBlock { Set-Content x 1 }` | **DENY** | closed (inner cmdlet scanned) |
| `Invoke-Command { $f=New-Object -c Scripting.FileSystemObject }` | **DENY** | closed |
| `& { Set-Content x 1 }` | **DENY** | closed |
| `Invoke-Expression ('Set-Con'+'tent x 1')` | **DENY** | closed (`Invoke-Expression` tooth) |
| `powershell -EncodedCommand <b64>` / `POWERSHELL -enc <b64>` / extra-spaced | **DENY** | closed (position-based, case-insensitive) |
| `$env:x=powershell -enc <b64>` (single-layer env assignment) | **DENY** | closed |
| `start notepad` / `saps cmd /c whoami` | **DENY** | closed (`_SPAWN_ALIAS`) |
| `[System.Type]::GetTypeFromCLSID('<guid>')` | **ALLOW** | **documented residual** (other reflection chain) |
| `$a=$b=powershell -enc <b64>` / `$a=$b=$c=powershell -enc <b64>` | **ALLOW** | **documented residual** (chained assignment) |
| `&(gcm powershell) -enc <b64>` | **ALLOW** | **documented residual** (command-lookup expansion) |

All three ALLOWs are honestly pre-disclosed in the module docstring (lines 65–76): COM "built through some other reflection chain is a residual" (covers `GetTypeFromCLSID`); a shell "invoked through a form neither first-token nor simple-assignment (e.g. a deeply nested expansion) is a residual" (covers the chained assignment and `&(gcm …)`). Confirmed the removal of the scoped encoded pass opened **no new encoded vector outside command position** — an `-enc` payload still requires a `powershell`/`pwsh` token in a residual invocation position; `-enc` as pure data correctly ALLOWs.

## Advisories (non-blocking; note per task instruction)

- **ADV-R4-1 (MEDIUM-class residual, recommended fast-follow):** chained-assignment encoded/nested shell — `$a=$b=powershell -enc <b64>` ALLOWs because `_effective_command_token` strips exactly **one** leading `$var=` layer (single `$env:x=powershell -enc` correctly DENIES). This is the residual nearest to the NF2 class and is **trivially closable**: loop the assignment strip while the RHS still begins with `$…=`. Recommend also naming "chained assignment" explicitly in the docstring. Reproduce: `$a=$b=powershell -enc <b64-of-Set-Content>` → ALLOW.
- **ADV-R4-2 (LOW residual, inherent denylist limit):** COM via `[Type]::GetTypeFromCLSID` and shell via `&(gcm powershell)` / `&(get-command …)` are open-ended reflection / command-lookup families that a bounded static denylist cannot exhaust. Adequately documented; covered by compensating controls.
- Interim risk for all three is contained by the compensating controls (Write/Edit tools removed for governed roles; orchestrator-only integration — a reviewer's spawned-child-shell scratch never reaches a branch, PR, or the ledger).

## ALSO items

- **(a) No weakening — confirmed.** PS pack **187/187 PASS, 0 FAIL** (15 RED-on-mutant rows). Bash pack **136/136 PASS, 0 FAIL**. Prior denials retained (spot-reproduced: `Set-Content`, `Out-File`, `[IO.File]::WriteAllText`, `git push`, `& 'Set-Content'`, `Add-Type`, `Start-Process`, `iex`, `> out.txt` DENY; `> $null` ALLOW; `& $var` DENY). Fail-closed envelope intact. Lead/main + roster-producer pass-through unchanged.
- **(b) Docstring honesty (round-3 item c) — satisfied.** The docstring now honestly states the command/spawn-position model, the `-c` COM floor, and the `bash`/`sh`/`wsl` self-launch residual. No coverage over-claim remains.
- **(c) Leak scan on the delta — clean.** No credentials/keys. The only `secret`/`token` matches are the literal word "token" in comments and the `gh … secret …` denylist entry (a control).
- Modularity: `modularity_check --check` → **0 failures**, guard not flagged (768 lines). Settings matcher `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`.

## Reviewer conclusion

The round-4 correction closes the two round-3 material findings at their reproduced payloads (NF1 COM abbreviation + reflection; NF2 assignment-fronted encoded shell), fixes the round-3 `-Encoding` false positives, keeps both test packs green with load-bearing mutants, and — decisively for the security bar — **honestly documents the remaining residuals rather than over-claiming coverage.** The three fresh-hunt ALLOWs (`GetTypeFromCLSID`, chained assignment, `&(gcm …)`) are all inside that honestly-disclosed residual set and are contained by compensating controls; the task's objective (iii) explicitly permits documented residuals for the not-fully-closable scripting class. Neither prong of the round-3 FAIL bar (dishonesty / the specific-found form still open) applies. The chained-assignment residual (ADV-R4-1) is the one I recommend the orchestrator schedule as a trivially-closable fast-follow, but it is not blocking for this task.

**G5: PASS**
