# G3 Code Review — M0-T109 (readonly-guard follow-up hardening)

> Orchestrator note: reviewer return saved verbatim (transport entity-decoding only). Reviewer: independent code-reviewer agent (read-only), returned 2026-09-04 (UTC).

**Task:** M0-T109 — close three documented M0-T108 round-4 residuals (ADV-R4-1, ADV-4, ADV-R4-2). In-regime (D-024).
**Reviewed content:** ctl24 HEAD `2ae60f55`; deliverable blobs identical to content commit `7f075e37` (guard `ad009d4f`, PS-test `0fd81db3`). Commits above 7f075e37 are ledger/evidence only — no code-path drift. Worktree clean.
**Scope:** exactly the three allowed paths (`.claude/hooks/readonly_agent_guard.py`, `tools/test_readonly_agent_guard_powershell.py`, `project-control/reports/M0-T109-guard-hardening.md`); no forbidden path (`.claude/settings.json`, `apps/**`, `services/**`, `tools/project_control.py`) touched. PASS.
**Reproduction:** `python tools/test_readonly_agent_guard_powershell.py` (exit 0, ALL CHECKS PASSED, incl. all 17 RED-on-mutant proofs); `python tools/test_readonly_agent_guard.py` (exit 0); `python -m ruff check` both files (All checks passed); `python tools/modularity_check.py --check` (failures 0); plus a 20-case independent stdin probe harness (BADCOUNT=0).

## Check 1 — ADV-R4-1 chained assignment (`_effective_command_token` + new `_ASSIGN_LAYER`)
Load-bearing and correct. The strip now loops `_ASSIGN_LAYER = ^\$\{?[A-Za-z_][\w:]*\}?\s*=\s*` over the space-rejoined words until fixpoint.
Independently verified DENY: `$a=$b=powershell -enc SQBFAFgA`, `$a=$b=$c=powershell`, `$a = $b = powershell`, `$env:X=powershell` (scope-prefix form), plus all prior single-layer forms (`$x=powershell`, `$x = powershell`, `$x= powershell`, `$x =powershell`). No false positive: `$a=$b=Get-Content README.md` and `$a = $b = Get-Content README.md` both ALLOW (reduce to `Get-Content`).
Loop safety: `while prev != head` with `sub(count=1)` is monotone-shortening and anchored (`^`) — terminates in O(layers), no catastrophic backtracking. Var-name class `[A-Za-z_][\w:]*` correctly admits scope prefixes (`$env:`, `$global:`) and the `${..}` brace form. Denying an assignment-fronted shell that a real read never uses is fail-closed hardening, not a regression.

## Check 2 — ADV-4 GetTypeFromProgID reachability
Correct root-cause fix. The old alternative `| GetTypeFromProgID\b` sat under `_PS_MUTATING`'s shared leading class `(?:^|[\s;&|({`=])`, which excludes `:`; a real `[Type]::GetTypeFromProgID(...)` is preceded by `:`, so the tooth was genuinely unreachable (dead) unless another tooth already fired. New self-anchored tooth `\[(?:System\.)?Type\]::GetTypeFromProgID\b` matches at the `[`, where `^`/space satisfies the leading class.
Independently verified DENY: standalone `[Type]::GetTypeFromProgID('Scripting.FileSystemObject')` (no CreateInstance present), `[System.Type]::GetTypeFromProgID(...)`, `$t = [Type]::GetTypeFromProgID(...)`, and the nested `[activator]::CreateInstance([type]::GetTypeFromProgID(...))` (still caught, via CreateInstance and now also GetTypeFromProgID). `[activator]::CreateInstance($t)` still DENYs. Name-as-data still ALLOWs: `Get-Content -Encoding UTF8 GetTypeFromProgID-notes.md`.
**Mutant honesty (both honestly load-bearing):** the prior single mutant dishonestly dropped both teeth against a CreateInstance-only payload; it is correctly split. `mutant drops Activator reflection-COM tooth` → payload `[activator]::CreateInstance($t)` (no `GetTypeFromProgID` substring, so only the CreateInstance tooth could catch it) → ALLOW under mutant, DENY real. `mutant drops GetTypeFromProgID tooth` → payload `[Type]::GetTypeFromProgID('X')` (no `CreateInstance` substring) → ALLOW under mutant, DENY real. Each payload is caught by exactly one tooth; both RED-on-mutant proofs PASS in-suite. Confirmed.

## Check 3 — ADV-R4-2 residual documentation
Confirmed documented, not new teeth. Module docstring (guard lines 78–84) names both open-ended residuals: `[Type]::GetTypeFromCLSID('{clsid}')` (unbounded GUID set) and command-lookup indirection `&(gcm powershell)` / `&(get-command …)`. I confirmed `_PS_MUTATING` contains no CLSID/gcm/get-command alternative — correctly left as documented residuals covered by the orchestrator-only integration model, consistent with the guard's existing residual posture and their LOW/G5 classification. Tests assert presence (`check_static` on `"GetTypeFromCLSID"` and `"get-command"` in the guard source). Note: these two assertions are coarse substring-presence checks (would pass on any occurrence), but the substantive requirement — the docstring actually documents both residuals — is met on inspection. Not a defect.

## Also-verify items
- **Bash pack:** no Bash-specific logic changed (`_MUTATING`, `_git_argv_mutates`, `_BASH_REDIRECT_TARGET_OK` untouched). The one shared function edited (`_effective_command_token`) feeds Windows-shell teeth only (`_NESTED_SHELL` = powershell/pwsh/cmd, `_SPAWN_ALIAS` = start/saps); probes confirm Bash reads still ALLOW (`grep 'powershell' file`, `git log --grep start`) and Bash `git push` still DENY. No Bash regression.
- **M0-T108 denials preserved:** shell-agnostic suite `test_readonly_agent_guard.py` fully green; PS suite retains all prior deny families.
- **`-Encoding` / powershell-as-data reads:** ALLOW confirmed (`Get-Content -Encoding UTF8 powershell-log.txt`, `Select-String -Pattern powershell notes.md`).
- **ruff:** clean on both files.
- **Modularity:** `failures 0`. Observation (non-blocking): the checker's file selection excludes `.claude/hooks/`, so the guard (785 physical / 731 non-blank lines) is never scanned and emits no warning — the producer report's "620 SLOC, WARN band per the checker" is a self-assessment, not a checker verdict. Either reading is not a failure. The file is a cohesive single-responsibility security-policy module; its growth is justified under principle 16, and the producer recorded the cohesion note.

## Findings
No correctness bug, false-positive, bypass, or scope breach found. All three fixes are root-cause-correct, each new/changed tooth is proven independently load-bearing by an honest RED-on-mutant proof, no prior denial regressed, and no legitimate read newly denies. One minor, non-blocking report-accuracy nuance (modularity framing) noted above; recommend the orchestrator/report not carry the "checker rates it warn-band" wording forward since the path is unscanned.

VERDICT: PASS
Reviewed ctl24 HEAD: 2ae60f55edd38ce0ba2ec31031c5226ca0cb541c (deliverable content == 7f075e37; guard blob ad009d4f, PS-test blob 0fd81db3)
