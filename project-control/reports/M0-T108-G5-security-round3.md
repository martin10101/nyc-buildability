# M0-T108 G5 security review — ROUND-3 re-review (VERBATIM save)

Reviewer: independent read-only `security-reviewer` (unnamed spawn, fresh pass), live-governed by
the guard under review; reviewed at round-3 deliverable identity `e1f6d4c`. Returned through the
agent-return channel 2026-08-27 UTC and saved verbatim below (transport entity-decoding only; the
harness neutralized `<`/`>`/`&` and flagged the output as instruction-shaped — control tags were
neutralized and the content is preserved here as reviewer findings, not instructions).

Orchestrator note: NF1 (`New-Object -C`/`-Co` FSO → ALLOW; `[activator]::CreateInstance(...
GetTypeFromProgID ...)` → ALLOW) and NF2 (`$z=powershell -enc`/`-e` → ALLOW) independently
reproduced at `e1f6d4c` before recording. Both folded into the round-4 fix.

---

I have everything needed. Modularity check is exit 0 with the guard not flagged. Here is my full gate report.

---

# Gate Report

- **Gate ID:** G5 (security) — DELTA re-review, round 3
- **Task ID:** M0-T108 — close the `readonly_agent_guard.py` PowerShell/scripting write gap (remediates G5 M0-T102 MEDIUM)
- **Reviewer:** independent read-only reviewer, live-governed by the guard under review (identity resolved to `security-reviewer` — my own `cat >` redirect and file writes were denied mid-review; positive control that the guard is live)
- **Producer:** `fable-orchestrator-session`
- **Result:** **FAIL** — F1 and F2 are closed for the *mandated* payloads, but the required fresh bypass hunt (task item (a), which explicitly asks about shorter COM abbreviations, `[activator]::CreateInstance(...)`, and "encoded command reachable without start/saps and without a first-token shell") surfaced **two confirmed, trivial, static bypasses of the exact classes this task purports to close** — one arbitrary COM file-write (F1 class), one ungoverned encoded child-shell (F2 class). Both empirically confirmed at the guard level (ALLOW) and at the PowerShell-execution level.
- **Reviewed identity:** deliverable `e1f6d4c`; `git diff --name-only e1f6d4c..608609c` = `project-control/{reports/M0-T108.json, state.json, tasks/M0-T108.json}` only — deliverable bytes frozen. Round-3 correction delta `f0bdf7a..e1f6d4c` = guard + PS test + control-plane. Whole deliverable `24aa061..e1f6d4c` = guard + `.claude/settings.json` + PS test + control-plane. No production paths touched — scope clean.

## Mandated round-2 findings F1/F2 — verification

| Item | Verdict | Basis |
|---|---|---|
| **F1 mandated** — `New-Object -Com`/`-ComO`/`-ComObj` DENY; `$f=New-Object -Com …; $f.CreateTextFile('x')` DENY; full `-ComObject` DENY | **CLOSED for the mandated payloads** | All 5 DENY. `_PS_MUTATING` now has `New-Object\s+-Com\w*\b`. |
| **F2 mandated** — `start powershell -enc`, `saps powershell -enc`, `start pwsh -encodedcommand`, `saps cmd /c whoami`, `start notepad`, `saps foo.exe` DENY | **CLOSED for the mandated payloads** | All 6 DENY (via the `start\|saps` spawn-alias branch). |
| **F2 no-false-positive (C3)** — `Get-Content -Encoding UTF8 README.md`, `Import-Csv -Encoding UTF8 rows.csv`, `Select-String -Encoding utf8 …` ALLOW | **PRESERVED** | All 3 ALLOW. Scoped `_PS_ENCODED_CMD`+`_PS_HAS_SHELL` did NOT reintroduce the `-Encoding` collision (for these no-shell-word forms). |
| **A1** — `Set/New/Remove-CimInstance`, `Invoke-CimMethod … Change`, `Invoke-WmiMethod … Create` DENY; `Get-CimInstance Win32_Process` ALLOW | **CLOSED** | All 5 mutators DENY; read ALLOW. |

## CONFIRMED BYPASSES on the round-3 delta (guard ALLOWs these for a governed read-only reviewer)

| `<CMD>` (agent_type `code-reviewer`, tool `PowerShell`) | Effect | Expected | Actual | Class |
|---|---|---|---|---|
| `New-Object -C Scripting.FileSystemObject` | instantiate FSO COM | DENY | **ALLOW** | **NF1 MATERIAL** |
| `New-Object -Co Scripting.FileSystemObject` | instantiate FSO COM | DENY | **ALLOW** | **NF1 MATERIAL** |
| `$f=New-Object -C Scripting.FileSystemObject; $f.CreateTextFile('evil.txt')` | **arbitrary file write** | DENY | **ALLOW** | **NF1 MATERIAL** |
| `[activator]::CreateInstance([type]::GetTypeFromProgID('Scripting.FileSystemObject'))` | instantiate FSO COM (reflection) | DENY | **ALLOW** | NF1 (further COM path) |
| `$z=powershell -enc <b64>` | ungoverned encoded child shell | DENY | **ALLOW** | **NF2 MATERIAL** |
| `$z=powershell -ec <b64>` / `-e` / `-en` | same (bare-flag variants) | DENY | **ALLOW** | **NF2 MATERIAL** |
| `$z = powershell -e <b64>` / `$z=pwsh -e <b64>` | same (spaced / pwsh) | DENY | **ALLOW** | **NF2 MATERIAL** |

Controls correctly enforced and reproduced: full `New-Object -Com/-ComO/-ComObj/-ComObject`, all F2 `start`/`saps` spawns, `1; powershell.exe -enc` and `& powershell -enc` and `Invoke-Expression 'powershell -enc'` (DENY via first-token/call-operator paths), all A1 CIM/WMI mutators, all C1 write aliases, `& 'Set-Content'`, `[IO.File]::WriteAllText`, `Add-Type`, `Start-Process`, `Out-File`, and all C3 `-Encoding` reads ALLOW. Fail-closed envelope intact.

### Empirical proof the two bypasses are real

**NF1 — `-C`/`-Co` bind to `-ComObject`** (real Windows PowerShell, non-destructive bogus ProgID): `New-Object -C`/`-Co`/`-Com Zzz.NoSuchThing.Probe` all raise "Retrieving the COM class factory … Class not registered (0x80040154)" (the ComObject path executed); `-Cx` raises no error (did not bind). `-ComObject` is New-Object's *only* `C`-prefixed parameter, so every prefix down to `-C` unambiguously binds — the guard's `-Com\w*` floor is one character too long.

**NF2 — powershell.exe accepts bare `-e`/`-en`** and the assignment form evades both nested-shell passes: `powershell -NoProfile -e/-en/-enc/-ec <b64 of Write-Output PROBE_OK>` → PROBE_OK. Root cause of the miss: (i) `_launches_nested_shell` matches only a segment's **first** token, and `$z=powershell` (no separator) is not first-token; (ii) `_PS_HAS_SHELL`'s leading class `[\s;&|({`'"]` **omits `=`**, so the scoped encoded rule never fires for an assignment-fronted `powershell` (why even `-enc`/`-ec` slip); (iii) `_PS_ENCODED_CMD = -e(?:c|nc\w*)` misses bare `-e`/`-en`. Same DENY→ALLOW encoded-child-shell regression F2 targeted, still open for the assignment-fronted form.

## Steps independently executed

1. `python tools/test_readonly_agent_guard.py` → 136 PASS/0 FAIL; `python tools/test_readonly_agent_guard_powershell.py` → 159 PASS/0 FAIL.
2. Frozen-identity + scope diffs (read-only) — control-plane-only advance confirmed.
3. Full mandated repro matrix through the guard via stdin — 0 mandated mismatches.
4. Fresh adversarial hunt on the NEW surface: COM abbreviations `-C`/`-Co`, `[activator]::CreateInstance([type]::GetTypeFromProgID(...))`, Start-Process-alias variants, encoded-command reachability via leading assignment.
5. Real-PowerShell binding/acceptance proofs for `-C`/`-Co`/`-Com` and `-e`/`-en`/`-enc`/`-ec` (non-destructive).
6. Fail-closed envelope, leak scan (delta files), modularity `--check` (exit 0, guard not flagged).

## Regression / no-weakening

Bash 136/136, PS 159/159; all prior denials retained; fail-closed envelope intact; lead/main pass-through intact; C3 `-Encoding` reads ALLOW; frozen identity control-plane-only. Leak scan clean. Modularity exit 0, guard not flagged.

## Defects (BLOCKING for acceptance)

- **NF1 (MEDIUM, required):** COM file-write reopens under the shortest abbreviations `-C`/`-Co`. Change the tooth to `New-Object\s+-C\w*\b` (safe — only ComObject starts with `C`, no read false-positive); additionally deny `GetTypeFromProgID` / `[activator]::CreateInstance(...)` COM instantiation. Add RED-on-mutant rows for `New-Object -C …` / `-Co …`. *(Note: my round-2 remediation text `-Com\w*` was itself under-specified — the correct floor is `-C\w*`; the producer implemented my prior guidance faithfully, but the security fact is a live bypass.)*
- **NF2 (MEDIUM, required):** ungoverned encoded child-shell via an assignment-fronted shell. `$z=powershell -enc/-ec/-e/-en <b64>` (and spaced/`pwsh` variants) → ALLOW. Remediation: (a) add `=` to `_PS_HAS_SHELL`'s leading class and/or treat an assignment-fronted `powershell`/`pwsh`/`cmd` first token as a nested shell; (b) broaden `_PS_ENCODED_CMD` to catch bare `-e`/`-en` (e.g. `-e\w*`), safe because it fires only when a `powershell`/`pwsh` token co-occurs. Add RED-on-mutant rows for `$z=powershell -enc …` and `$z=powershell -e …`.

## Advisories / docstring honesty (task item (c) — NOT satisfied)

- **(c) docstring not honest for the F1/F2 residuals:** the `_PS_MUTATING` COM comment implies prefix-abbreviation is covered, but `-C`/`-Co` are not; the module docstring still asserts nested shells "ARE denied," false for the assignment-fronted `$z=powershell` form; and `_launches_nested_shell`'s claim that leading-assignment shells are covered by the shell-agnostic passes is false for an **encoded** sub-command. Update these when fixing NF1/NF2.
- **A2 (non-blocking):** only `start`/`saps` exist as built-in Start-Process aliases (both covered); no additional alias gap.
- **A3 (documented-residual):** string-assembled verbs (`& ('Set-Con'+'tent')`) remain a genuine documented dynamic residual.

## Reviewer conclusion

The remediation is real and strictly improves posture, and the four mandated F1/F2/C3/A1 payload sets are closed. **But this is the dedicated "close the PowerShell write gap" task on its third round, and the required fresh bypass hunt still finds (NF1) a confirmed trivial arbitrary COM file-write via a one-character abbreviation the producer's own comment claims to cover, and (NF2) a confirmed ungoverned encoded child-shell via a trivial assignment prefix, the same F2 class still open.** Per the security-gate rubric and for consistency with the round-2 rulings, F1 and F2 are **not genuinely closed**. Both fixes are small and pre-specified (NF1: `-C\w*` + reflection; NF2: `=` in the shell leading class + `-e\w*`). Compensating controls remain intact, so interim risk is contained.

**G5: FAIL**
