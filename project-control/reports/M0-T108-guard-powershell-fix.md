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

## 4. Evidence

- `python tools/test_readonly_agent_guard.py` → 136 PASS, `ALL CHECKS PASSED`.
- `python tools/test_readonly_agent_guard_powershell.py` → 95 PASS, `ALL CHECKS PASSED`,
  including **4 RED-on-mutant proofs** (PowerShell branch removed → `Set-Content` slips;
  redirect scan removed → `> out.txt` slips; scripting pass removed → `open('f','w')` slips;
  backtick normalization removed → hidden `git push` slips — each mutant ALLOWs what the real
  guard DENIES).
- `ruff check` on both changed Python files: clean. `modularity_check --check`: guard at 589
  SLOC (below the 600 warn threshold); no new warnings.
- Machine enforcement replaces the procedural stopgap immediately on merge: reviewer spawns in
  this checkout now hit the extended guard (M0-T108's own reviewers run under it).

## 5. Scope

Only the four packet paths changed. `.claude/settings.json` change is the single matcher line.
No supervisor runtime, dependency, workflow, or policy file touched.
