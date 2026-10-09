# M0-T108 — readonly-guard PowerShell/scripting write-gap fix (producer report)

Producer: Fable 5 orchestrator session (claimed `fable-orchestrator-session`), 2026-08-27 UTC.
Origin: G5 M0-T102 MEDIUM advisory — a reviewer agent could mutate the working tree through the
harness's Windows PowerShell tool because the PreToolUse matcher and guard code covered Bash only.

## 1. Deliverables

| Deliverable | Path |
|---|---|
| Guard: PowerShell branch + quote-aware redirect + scripting pass | `.claude/hooks/readonly_agent_guard.py` |
| Matcher extension (reviewed config change) | `.claude/settings.json` (`Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`) |
| Regression pack (95 checks incl. 4 RED-on-mutant) | `tools/test_readonly_agent_guard_powershell.py` |
| This report | `project-control/reports/M0-T108-guard-powershell-fix.md` |

## 2. What changed (objective items i–iv)

**(i) Matcher** now routes the PowerShell tool through the guard. `SHELL_TOOLS` in the guard
mirrors the matcher's shell list; the test pack asserts both stay in sync.

**(ii) PowerShell denylist** (`_shell_command_mutates(powershell=True)`):
1. **Backtick normalization first** (`_ps_normalize`): PowerShell escapes with a backtick, so
   `git pu` + backtick + `sh` executes `git push`; normalization resolves escapes (and
   backtick-newline continuations) outside single-quoted spans before any pass runs.
2. **The existing shell-agnostic passes run for PowerShell too**: `_MUTATING` (git/gh/
   control-plane/npm/pip/`rm`/`mv`/`cp`/`tee`…) and the quoting-aware `_git_argv_mutates`
   argv pass — so `& git -C "spaced path" push` and `git.exe add` are denied identically.
3. **`_PS_MUTATING` additions**: write cmdlets (`Set/Add/Clear-Content`, `Out-File`,
   `New/Remove/Move/Copy/Rename/Set-Item[Property]`, `Tee-Object`, `Export-Csv/Clixml/…`,
   `Compress/Expand-Archive`, `Set-Acl`, `Set-ExecutionPolicy`), their one-token aliases
   (`sc ni ri rd del erase md cpi rni ren move copy`), .NET IO writers
   (`[IO.File]::Write*`-class via a read-method negative lookahead, `[IO.Directory]::Create…`,
   `StreamWriter/FileStream/BinaryWriter`, `[IO.Path]::GetTempFileName`), `-OutFile` anywhere,
   mutating web methods (`Invoke-WebRequest/RestMethod … -OutFile|-Method POST/PUT/PATCH/DELETE`),
   registry/task/ACL writers (`reg add…`, `schtasks /create…`, `icacls /grant…`), and the
   dynamic-execution vectors: `Invoke-Expression`/`iex`, `Invoke-Item`, `Start-Process`,
   `Add-Type`, nested shells (`powershell|pwsh|cmd …`), encoded commands (`-enc…`), and the
   call operator on a variable (`& $var`). Same fail-closed envelope: unparseable payloads and
   guard-internal errors still deny (unchanged `main()` wrapper).
4. **PowerShell redirect rule**: unquoted `>`/`>>` denies unless the target is `$null` or a
   stream merge (`2>&1`); `2>$null` and `*> $null` stay allowed.

**(iii) Scripting-language class, treated generally**: a best-effort `_SCRIPT_WRITE` pass runs
for BOTH shells and denies inline write idioms even though quoted — mode-gated
`open(...,'w'|'a'|'x'|'+')`, `.write_text/.write_bytes`, `os.remove/rename/makedirs/…`,
`shutil.copy*/move/rmtree/…`, `.unlink(`, node `fs.write*`. **Residual documented honestly**
(guard docstring): a dynamically composed write (string-built mode, exec of assembled source)
is not statically resolvable; PowerShell's dynamic vectors are themselves denied, and the
remainder stays covered by the removed Write/Edit tools plus the orchestrator-only integration
model (a reviewer's local scratch never reaches a branch, PR, or the ledger).

**(iv) Read-only false-positive reduction**: redirect detection is now **quote-aware**
(`_unquoted_redirect` replaces the raw-text `_REDIRECT` regex). A literal `>` inside a quoted
string — `python -c "1 if x>0 else 2"`, `-> int` annotations, `grep 'a->b'` — no longer denies;
every unquoted redirect denial is retained (proven by tests and by a RED-on-mutant that strips
the scan). Pure-read `open(f)`/`open(f,'r')` (the observed M0-T102 reviewer false-positive
class) are explicitly asserted ALLOWED.

## 3. Behavior invariants

- Lead/main session (no identity keys): **pass-through unchanged** (asserted).
- Roster producers (e.g. `backend-engineer`, unnamed spawn): pass-through unchanged (asserted).
- Named/unknown spawn identities: fail closed, now for PowerShell too (asserted).
- The full pre-existing Bash pack passes byte-for-byte unmodified: **136/136** — no existing
  denial removed, no existing allow removed.

## 4. Evidence (final, post round-3 — supersedes the round-1 numbers; see §5/§5a for the history)

- `python tools/test_readonly_agent_guard.py` → **136 PASS**, `ALL CHECKS PASSED` (byte-unchanged
  from base — no existing denial/allow removed).
- `python tools/test_readonly_agent_guard_powershell.py` → **159 PASS**, `ALL CHECKS PASSED`,
  including **13 RED-on-mutant proofs** (each mutant ALLOWs what the real guard DENIES; the pack's
  `mutated_src == SRC` no-op guard fails any dead mutation): PowerShell branch, redirect scan,
  scripting-write pass, backtick normalization, nested-shell pass, call-operator unwrap, `::new()`
  constructors, COM, CIM/WMI, alias `ac`, defensive field extraction, COM-prefix (F1), and
  start/saps+encoded (F2).
- `ruff check` on both changed Python files: clean. `modularity_check --check`: **0 failures**;
  the guard file is **not** among the warnings (its SLOC is below the 600 warn threshold — the
  731 raw lines include a ~130-line docstring/comments); no new warnings.
- Machine enforcement replaces the procedural stopgap immediately on merge: reviewer spawns in
  this checkout now hit the extended guard (M0-T108's own three review rounds ran under it —
  each reviewer's own write/redirect attempts were denied mid-review, a live positive control).

## 5. Correction round (G3 FAIL → addressed; G5 C1–C4; G4 A1–A3)

Round-1 independent review found real, reproducible write bypasses. All are now closed and proven
by new RED-on-mutant rows (each mutant ALLOWs what the corrected guard DENIEs):

| Finding | Fix | Proof |
|---|---|---|
| G3 D1 / G5 C1 / G4 A2 — write-cmdlet aliases `ac`/`clc`/`mi`/`epcsv`/`sp`/`rp`/`mkdir` bypass | added to the `_PS_MUTATING` alias set (+`spps`/`rbp`/`swmi`/`icm`) | 7 DENY assertions + `ac` mutant |
| G3 D2 — `.NET` `::new()` writer constructors bypass | added `[IO.(StreamWriter\|FileStream\|BinaryWriter)]::new` branch | 3 DENY assertions + `::new` mutant |
| G5 C2 — COM `New-Object -ComObject` + CIM/WMI `Win32_Process.Create` bypass | added `New-Object -ComObject` and `Invoke-(Cim\|Wmi)Method … Create` branches | 4 DENY assertions + ComObject + CIM/WMI mutants |
| G3 D3 — nested-shell laundering (`powershell -Command` via the **Bash** tool) | extracted `_launches_nested_shell` (segment-first-token) applied to BOTH shells | 4 DENY assertions + nested-shell mutant |
| G4 A1 — call-operator/dot-source quoted literal (`& 'Set-Content'`, `& 'gh'`) bypass | `_ps_normalize` unwraps `[&.] 'literal'` → bare invocation before the denylists | 6 DENY assertions + call-operator mutant |
| G5 C3 — NEW false-positive: `-Encoding` reads denied by `_PS_ENCODED` | removed `_PS_ENCODED` entirely (encoded commands already denied by the nested-shell pass) | 3 ALLOW assertions |
| G4 A3 — `> ${null}` false-positive | `_PS_REDIRECT_TARGET_OK` accepts the `${null}` brace form | 1 ALLOW assertion |
| G3 D4 / G5 minor — PowerShell `tool_input` field name unevidenced (fail-open risk) | `_shell_command_text` scans `command` PLUS every other string leaf in `tool_input`; malformed `tool_input` fails closed explicitly | 3 assertions (write-in-`script` DENY, read-in-`script` ALLOW, malformed DENY) + defensive-extraction mutant |
| G5 C4 — residual docstring overstated coverage | rewrote the module docstring's residual paragraph to enumerate exactly what is uncovered (dynamic assembly; the Bash-side quoted call-operator for `gh`/cmdlets as a pre-existing residual; the non-exhaustive alias table; env/clipboard/dot-source out-of-model side effects) | docstring |

**Nested-shell precision:** `_launches_nested_shell` matches only `powershell`/`pwsh`/`cmd` as a
**segment-first token**, so a read that merely mentions the word (`echo cmd`, `grep pwsh file`) is
allowed — asserted. The set is intentionally `powershell|pwsh|cmd` (the named Windows laundering
vectors); `sh`/`bash` are not included (avoids colliding with the backtick-split fragment of
`git pu`+backtick+`sh`, and keeps the backtick-normalization mutant load-bearing).

**Deliberately-retained residuals (honest, G5 C4):** the Bash-tool `'gh' pr create` quoted-literal
(pre-existing in the shared `_MUTATING` core; not closed by broadening the Bash leading class,
which would deny reads like `grep 'git push' file` — recommended as a follow-up hardening task);
the non-exhaustive PowerShell alias table; dynamically-assembled writes; and non-repo-write side
effects (`[Environment]::SetEnvironmentVariable`, `Set-Clipboard`, dot-sourcing a pre-existing
script). One accepted false-positive of the standard quoted-text posture remains
(`Write-Output 'the Set-Content cmdlet'` denies), identical in kind to the existing Bash
`_MUTATING` behavior (fail-closed).

## 5a. Round-3 correction (G5 delta FAIL F1/F2; A1; G3 delta A1/A2)

Round-2 delta review: G3 PASS, G4 PASS, **G5 FAIL** — the G5 security delta found two confirmed
material bypasses the round-2 delta itself shipped. Both closed:

| Finding | Fix | Proof |
|---|---|---|
| **G5 F1 (MEDIUM)** — COM `New-Object -Com`/`-ComO`/`-ComObj` (PowerShell parameter-prefix abbreviation of `-ComObject`) bypassed the `-ComObject\b` match → arbitrary file write via FSO | broadened to `New-Object\s+-Com\w*\b` | 5 DENY assertions + repointed COM mutant |
| **G5 F2 (MEDIUM)** — `start`/`saps` (Start-Process aliases) fronting `powershell`/`pwsh`/`cmd` (with `-enc`) spawned an ungoverned child shell; a DENY→ALLOW regression from removing `_PS_ENCODED` wholesale | added `start`/`saps` to the `_PS_MUTATING` spawn-alias branch, **and** re-added a SCOPED encoded-command check (`_PS_ENCODED_CMD` + `_PS_HAS_SHELL`) that fires only when an `-enc`/`-encodedcommand` flag co-occurs with a `powershell`/`pwsh` token — so `start powershell -enc <b64>` DENIes while `Get-Content -Encoding UTF8 f` (no shell token) stays ALLOW | 6 DENY + 2 no-FP ALLOW assertions + start/saps mutant |
| **G5 A1 (advisory→closed)** — CIM/WMI mutators beyond `Win32_Process.Create` | deny all `Invoke-CimMethod`/`Invoke-WmiMethod` and `Set`/`New`/`Remove-CimInstance`; read `Get-CimInstance` stays allowed | 5 DENY + 1 ALLOW assertions + repointed CIM mutant |
| **G3 A1 (advisory→closed)** — `_launches_nested_shell` docstring over-listed `bash/sh/wsl` (code matches only `powershell/pwsh/cmd`) | docstring rewritten to state the exact set and record `bash/sh/wsl`/`sh -c` as an explicit follow-up residual (why `sh` is excluded — the backtick-split collision) | docstring |
| **G3 A2 (advisory→closed)** — report mutant-count/line bookkeeping | corrected here (see below) | this report |

**Deliberately-retained residuals (honest):** the Bash-tool `'gh' pr create` quoted-literal
(pre-existing in the shared `_MUTATING` core); the Bash-tool self-launch of another POSIX shell
(`sh -c '…'` / `bash -c '…'` / `wsl …`) — covered by the orchestrator-only integration model and
recommended for a follow-up hardening pass; the string-assembled dynamic verb
(`& ('Set-Con'+'tent')`); a command nested in a `tool_input` sub-object (no known harness uses
this shape); and non-repo-write side effects (`[Environment]::SetEnvironmentVariable`,
`Set-Clipboard`, dot-sourcing a pre-existing script). One accepted false-positive of the standard
quoted-text posture remains (`Write-Output 'the Set-Content cmdlet'` denies), identical in kind to
the existing Bash `_MUTATING` behavior (fail-closed).

**Post-correction evidence (round 3):** PS pack **159/159** (**13** RED-on-mutant, all
load-bearing — the 4 original + 9 correction-round teeth incl. F1 COM-prefix and F2
start/saps+encoded); Bash pack **136/136 unchanged**; ruff clean; guard **731 raw lines** (SLOC
below the modularity WARN threshold — the checker reports 0 failures and does not flag this file;
the growth is additional denylist rules within the guard's single responsibility, no
responsibility mixing).

## 5b. Round-4 correction (G5 round-3 NF1/NF2; G3 round-3 D-R3-1; G4 ADV-1)

Round-3 delta review: G4 PASS, but **G3 FAIL** (D-R3-1) and **G5 FAIL** (NF1/NF2). All three
findings shared one root cause — regexes matched tokens as **data** anywhere rather than in
**command/spawn position**. Round-4 fixes that root cause; all closed with RED-on-mutant proofs:

| Finding | Fix | Proof |
|---|---|---|
| **G5 NF1 (MEDIUM, fail-open)** — COM `New-Object -C`/`-Co` bind to `-ComObject` (its only C-param) and bypassed the `-Com\w*` floor → arbitrary file write; also `[activator]::CreateInstance([type]::GetTypeFromProgID(...))` reflection | COM floor lowered to `New-Object\s+-c\w*\b` (covers `-c`/`-co`/`-com…`); added `[Activator]::CreateInstance` + `GetTypeFromProgID` reflection denials | 7 DENY + non-COM `New-Object System.Collections.ArrayList` ALLOW; NF1-floor + activator mutants |
| **G5 NF2 (MEDIUM, fail-open)** — `$z=powershell -enc/-e` (assignment-fronted) spawned an ungoverned encoded child shell that both first-token nested-shell and the scoped encoded pass missed | `_launches_nested_shell` now checks the **effective command token** (`_effective_command_token` skips a leading `$var =` / `$var=` assignment); the fragile `_PS_ENCODED_CMD`/`_PS_HAS_SHELL` pair is REMOVED | 6 DENY (`$z=powershell -enc/-e/-en`, spaced, pwsh, cmd); assignment-RHS mutant |
| **G3 D-R3-1 + G4 ADV-2 (blocking FP)** — the removed scoped encoded pass false-positived `-Encoding` reads that mentioned `powershell`/`pwsh` as DATA | fixed by the same removal + command-position model: a shell word as an argument value is no longer a shell invocation | 4 ALLOW (`Select-String -Encoding … -Pattern powershell`, pipe read, filename, plain) |
| **G4 ADV-1 (fail-safe over-block)** — `start`/`saps` in the `_PS_MUTATING` alias list denied the word "start" as data | `start`/`saps` moved out of the alias list into a command-position `_SPAWN_ALIAS` checked by `_launches_nested_shell` | 2 ALLOW (`Select-String -Pattern start`, `git log --grep start`); spawn-alias mutant |
| **G5 item (c) — docstring honesty** | module docstring residuals rewritten: nested-shell/spawn detection is command-position (first-token OR assignment-RHS); COM covered down to `-c` + reflection; bash/sh/wsl self-launch a named residual | docstring |

**Command-position model (round-4 core):** `_launches_nested_shell` denies `powershell`/`pwsh`/
`cmd` and `start`/`saps` when they are a segment's first token OR the RHS of a leading `$var =`
assignment — closing the assignment-fronted encoded-shell vector (NF2) while allowing the shell
word as pure argument data (D-R3-1/ADV-1/ADV-2 false positives fixed). This removed the fragile
`-enc`/`-Encoding` prefix collision entirely.

**Post-correction evidence (round 4):** PS pack **187/187** (**15** RED-on-mutant, all
load-bearing — incl. NF1 COM-floor, NF1 activator/reflection, NF2 assignment-RHS, spawn-alias);
Bash pack **136/136 unchanged**; ruff clean; guard 756 raw lines (SLOC below the modularity WARN
threshold — checker reports 0 failures, guard not flagged).

## 6. Scope

Only the four packet paths changed. `.claude/settings.json` change is the single matcher line.
No supervisor runtime, dependency, workflow, or policy file touched.
