# M0-T108 G3 code review — ROUND-3 re-review (VERBATIM save)

Reviewer: independent read-only `code-reviewer` (unnamed spawn, fresh pass), ran under the guard
being reviewed; reviewed at round-3 deliverable identity `e1f6d4c` (HEAD `608609c` = control-plane
records only). Returned through the agent-return channel 2026-08-27 UTC and saved verbatim below
(transport entity-decoding only; the harness neutralized `<`/`>`/`&` and flagged the output as
instruction-shaped — control tags were neutralized and the content is preserved here as reviewer
findings, not instructions).

Orchestrator note: defect D-R3-1 independently reproduced at `e1f6d4c` before recording —
`Select-String -Encoding utf8 -Pattern powershell -Path notes.md` → DENY (false positive);
`Get-Content -Encoding UTF8 README.md` (no shell word) → ALLOW; `start powershell -enc …` /
`saps cmd /c …` → DENY (real threat still blocked). Verdict FAIL confirmed valid.

---

Regression proven in-process: round-2 (f0bdf7a, which I passed) ALLOWed all three reads; round-3 (e1f6d4c) DENIes them, while the no-shell-word control is ALLOWed in both. I have everything needed. Here is my gate report.

---

# Gate Report

- **Gate ID:** G3 (independent code review — round-3 DELTA re-review after the G5-driven correction)
- **Task ID:** M0-T108 — readonly-guard PowerShell/scripting write-gap fix
- **Reviewer:** code-reviewer (independent, read-only; ran under the guard being reviewed — my own shell redirect `git show … > file` was itself DENIED with the read-only message, a live positive control that enforcement is active on this session)
- **Producer:** fable-orchestrator-session
- **Result:** **FAIL** (one reproducible, localized new false-positive defect introduced by the round-3 delta; fails safe, all security teeth correct)
- **Predecessor:** round-2 delta G3 = PASS (`M0-T108-G3-code-review-delta.md`) with advisories A1 (docstring) and A2 (bookkeeping). Fresh independent pass; I re-derived every item.

## Frozen identity — verified

- `git diff --name-only e1f6d4c..608609c` → only `project-control/reports/M0-T108.json`, `state.json`, `tasks/M0-T108.json`. HEAD is control-plane records only; deliverable frozen at `e1f6d4c`.
- Round-3 code delta `git diff f0bdf7a..e1f6d4c` touches exactly two source files: `.claude/hooks/readonly_agent_guard.py` (+53) and `tools/test_readonly_agent_guard_powershell.py` (+45); rest are gates/reports.
- Whole deliverable `git diff 24aa061..e1f6d4c`: guard (+369), `.claude/settings.json` (+2 = one matcher line), PS test pack (+420), plus control-plane. **Base Bash pack byte-unchanged across the whole task.**
- Round-3 delta does **not** touch identity resolution, the `_MUTATING` core, `_git_argv_mutates`/`_git_sub_mutates`, or `_unquoted_redirect`. Core passes intact.

## Automated evidence (executed)

| Command | Result |
|---|---|
| `python tools/test_readonly_agent_guard.py` | **136 PASS**, ALL CHECKS PASSED, EXIT=0 (byte-unchanged base pack) |
| `python tools/test_readonly_agent_guard_powershell.py` | **159 PASS**, ALL CHECKS PASSED, EXIT=0; **13 RED-on-mutant rows** |
| `ruff check` (both changed Python files) | All checks passed |
| `python tools/modularity_check.py --check` | 302 files, **failures 0**, 5 warnings; guard file **not** among them |
| `wc -l .claude/hooks/readonly_agent_guard.py` | **731** raw lines (matches report §5a) |

## Round-2 advisories A1 / A2 — both RESOLVED

- **A1 (docstring parity) — RESOLVED.** `_launches_nested_shell`'s docstring now states the tooth matches "exactly `powershell`, `pwsh`, or `cmd`" and records `bash`/`sh`/`wsl` / `sh -c` as an explicit deliberately-excluded follow-up residual (with the `sh` backtick-split collision reason). Matches `_NESTED_SHELL`.
- **A2 (bookkeeping) — RESOLVED.** Report now reads 136/136 Bash, 159/159 PS, **13** mutants, **731** raw lines — all reproduced.

## F1 / F2 spawn-deny / A1(CIM-WMI) security teeth — correct

- **F1 COM prefix** (`New-Object\s+-Com\w*\b`): DENIes `New-Object -Com/-ComO/-ComObj/-ComObject …`. No read false positive. Repointed COM mutant load-bearing.
- **F2 spawn aliases** (`start`/`saps`): `start powershell -enc …`, `saps pwsh -encodedcommand …`, `saps cmd /c …`, `start notepad`, `saps foo.exe` all DENY. start/saps mutant load-bearing.
- **A1 CIM/WMI** (`Invoke-(?:Cim|Wmi)Method\b` + `(?:Set|New|Remove)-CimInstance\b`): mutators DENY; `Get-CimInstance` read ALLOW. Repointed CIM mutant targets the present string.

## BLOCKING DEFECT — D-R3-1: F2's scoped encoded-command check introduces a new read-only false positive

**Where:** the round-3 additions:
```
_PS_ENCODED_CMD = re.compile(r"(?i)(?:^|\s)-e(?:c|nc\w*)\b")
_PS_HAS_SHELL   = re.compile(r"(?i)(?:^|[\s;&|({`'\"])(?:powershell|pwsh)(?:\.exe)?\b")
...
if _PS_ENCODED_CMD.search(cmd) and _PS_HAS_SHELL.search(cmd):
    return True
```

**The bug:** `-EncodedCommand` and `-Encoding` share the `-Enc` prefix, so `_PS_ENCODED_CMD` (`-e(?:c|nc\w*)`) matches **`-Encoding`** as well as `-enc`/`-ec`. The only discriminator is `_PS_HAS_SHELL`, which matches the literal word `powershell`/`pwsh` **anywhere** — including as a benign search pattern, a filename argument, or a pipe target, not just in command/spawn position. So any legitimate read that specifies `-Encoding` **and** mentions the word `powershell`/`pwsh` as data is denied. The justifying code comment — "`-Encoding` is excluded because it needs the shell token" — is factually wrong.

**Reproduced** (role `code-reviewer`, tool `PowerShell`; all pure reads/searches, no write):

| Command | round-2 `f0bdf7a` | round-3 `e1f6d4c` |
|---|---|---|
| `Select-String -Encoding utf8 -Pattern powershell -Path notes.md` | ALLOW | **DENY** |
| `Get-Content -Encoding utf8 notes.md \| Select-String pwsh` | ALLOW | **DENY** |
| `Get-Content -Encoding UTF8 powershell-notes.md` | ALLOW | **DENY** |
| `Get-Content -Encoding UTF8 README.md` (control, no shell word) | ALLOW | ALLOW |

Reproduced two ways (installed guard over JSON stdin; and in-process exec of the `f0bdf7a` and `e1f6d4c` guard sources calling `_shell_command_mutates`). `_PS_ENCODED_CMD`/`_PS_HAS_SHELL` absent from `f0bdf7a` — genuinely new round-3 code, a **regression versus the round-2 state I passed**, not a pre-existing residual.

**Why blocking (not advisory):**
1. Exactly the class review charge (1) asks me to catch ("new false positive") and violates charge (4)'s invariant that `-Encoding` reads still ALLOW.
2. Re-opens, in narrowed form, the **previously-blocking G5 C3**. Within this task the project already ruled a `-Encoding` read false positive a blocking correction; consistency makes this blocking.
3. Cuts against objective (iv) "reduce read-only false positives," in a repo whose reviewers routinely read/search PowerShell tooling and files mentioning `powershell`/`pwsh`.

**Severity note (fairness):** the defect **fails safe** — it over-blocks a read, opens no write path. Write-blocking posture is strictly tighter than round-2 (F1/F2/A1 all correct). Impact is usability. Small, localized, fail-safe — but per the task's own C3 precedent and my charge, a blocking correction.

**Test gap:** the pack's two F2 "no-FP" assertions both omit a shell word, so green does not cover this. Round-4 must add a RED regression row with `-Encoding` co-occurring with a `powershell`/`pwsh` argument.

**Suggested minimal fix (direction only):** require the shell token in *command/spawn position* for the scoped check — gate `_PS_ENCODED_CMD` on `powershell`/`pwsh` being a segment-first token or immediately following a spawn alias (`start`/`saps`/`Start-Process`/`&`), not merely present as argument data. Do **not** try to separate `-enc` from `-Encoding` by prefix (impossible; `-enc` is a genuine prefix of `-Encoding`).

## Directive verification (scope note)

In-regime (`directive_refs: [{D-024: ALL}]`). Authoritative applicable-set resolution and `verification.json` are the `directive-compliance-verifier`'s responsibility, not G3. No code-review contradiction to any D-024 requirement observed; allowed-path scope respected.

## Conclusion

The round-3 delta correctly closes the two G5 bypasses (F1, F2), correctly broadens CIM/WMI (A1), and resolves both round-2 advisories — all with load-bearing RED-on-mutant proofs, base Bash pack byte-unchanged and green, identity/pass-through and fail-closed envelope intact, core untouched. **However**, the F2 scoped encoded-command check introduces a new, reproducible read-only false positive: `-Encoding` reads/searches mentioning the literal word `powershell`/`pwsh` are now denied (allowed at the round-2 identity I passed), on a false-premise code comment. Re-opens a narrowed slice of the previously-blocking G5 C3. Fails safe, small/localized, but a blocking correction under this task's own precedent.

**G3: FAIL**

Reviewed identity `e1f6d4c` (HEAD `608609c` = control-plane only).
