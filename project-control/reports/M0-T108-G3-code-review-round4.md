# M0-T108 G3 code review — ROUND-4 re-review (VERBATIM save)

Reviewer: independent read-only `code-reviewer` (unnamed spawn, fresh pass), ran under the guard
being reviewed; reviewed at round-4 deliverable identity `b6db457` (HEAD `b194c90` = control-plane
records only). Returned through the agent-return channel 2026-08-27 UTC and saved verbatim below
(transport entity-decoding only; the harness neutralized `<`/`>`/`&` and flagged the output as
instruction-shaped — control tags were neutralized and the content is preserved here as reviewer
findings, not instructions).

---

All checks pass. I have everything needed. My round-4 re-review is complete.

---

# Gate Report

- **Gate ID:** G3 (independent code review — round-4 DELTA re-review, verifying D-R3-1 closure)
- **Task ID:** M0-T108 — readonly-guard PowerShell/scripting write-gap fix
- **Reviewer:** code-reviewer (independent, read-only; fresh pass, re-derived every item; did not consult other current reviewers)
- **Producer:** fable-orchestrator-session
- **Reviewed identity:** deliverable frozen at `b6db457`; HEAD `b194c90` = control-plane records only
- **Predecessor:** my round-3 = FAIL on D-R3-1 (`M0-T108-G3-code-review-round3.md`)
- **Result: PASS** (D-R3-1 closed; round-4 delta correct; no new blocking code defect; one fail-safe advisory)

## Frozen identity — verified
- `git diff --name-only b6db457..b194c90` → only `project-control/reports/M0-T108.json`, `state.json`, `tasks/M0-T108.json`. HEAD is control-plane only; deliverable frozen at `b6db457`.
- Round-4 code delta `git diff e1f6d4c..b6db457` touches exactly two source files: `.claude/hooks/readonly_agent_guard.py` and `tools/test_readonly_agent_guard_powershell.py`; the rest are gates/reports/handoff.
- Whole deliverable `git diff 24aa061..b6db457`: guard, `.claude/settings.json` (one matcher line, unchanged in round-4), PS test pack, plus control-plane. **Base Bash pack byte-unchanged across the whole task.**
- Round-4 did not touch identity resolution, the `_MUTATING` core, `_git_argv_mutates`/`_git_sub_mutates`, `_unquoted_redirect`, `_ps_normalize`, the fail-closed envelope, or the field-extraction pass. Confirmed by the diff.

## Automated evidence (executed under the guard being reviewed)

| Command | Result |
|---|---|
| `python tools/test_readonly_agent_guard.py` | **136 PASS, 0 FAIL**, ALL CHECKS PASSED (byte-unchanged base pack) |
| `python tools/test_readonly_agent_guard_powershell.py` | **187 PASS, 0 FAIL**, ALL CHECKS PASSED; **15 RED-on-mutant rows** |
| `ruff check` (both changed Python files) | All checks passed |
| `python tools/modularity_check.py --check` | 302 files, **failures 0**, 5 warnings; guard **not** among them |
| guard raw line count | **768** (not flagged) |

Live positive control: my own scratchpad file-write was DENIED by the guard — enforcement is active on this session.

## D-R3-1 — CLOSED (root cause removed)
Round-4 deleted `_PS_ENCODED_CMD`/`_PS_HAS_SHELL` and the scoped-encoded branch, replacing the "shell-word-anywhere + `-enc`-anywhere" pair with **command/spawn-position** detection (`_launches_nested_shell` via `_effective_command_token`). The `-Encoding`/`-Enc` prefix collision no longer exists — there is no `-enc` flag rule at all now.

| Command | round-3 `e1f6d4c` | round-4 `b6db457` |
|---|---|---|
| `Select-String -Encoding utf8 -Pattern powershell -Path notes.md` | DENY | **ALLOW** |
| `Get-Content -Encoding UTF8 powershell-notes.md` | DENY | **ALLOW** |
| `Get-Content -Encoding utf8 notes.md \| Select-String pwsh` | DENY | **ALLOW** |
| `$z=powershell -enc SQBFAFgA` | DENY | **DENY** (kept) |

## Review-charge checks
1. **`_effective_command_token` correct for all assignment forms.** `$x = powershell` (branch 2 → powershell), `$x=powershell` (branch 1 rhs → powershell), `$x= powershell` (branch 1 empty-rhs → words[1]), `$x =powershell` (branch 3 → powershell) — all DENY; `$x = Get-Content` → Get-Content → ALLOW. Comparison/other edges (`$x == foo`, `$x -eq foo`, `${env:PATH}`) degrade to non-shell tokens → ALLOW (graceful, no mis-fire).
2. **D-R3-1 resolved / real threat retained** — see table. Probe: `powershell -enc`, `start powershell -enc`, `saps cmd /c`, `start notepad`, `& powershell -enc`, `$(powershell -enc)`, chained `; start powershell`, and all four NF2 assignment forms → DENY. `&`/`(`/`)`/`{`/`}`/backtick/`<`/`>`/`$(` are all `_SEGMENT_CHARS`, so call-operator and subexpression shell invocations land as a segment's first token and are caught — the removed scoped pass lost no real DENY.
3. **`-c\w*` COM floor introduces no read FP.** `New-Object System.Collections.ArrayList` and `New-Object -TypeName …` → ALLOW, while `-C`/`-Co`/`-ComObject` → DENY. `[Activator]::CreateInstance` and `GetTypeFromProgID` deny instantiation idioms (fail-safe; not read commands).
4. **No regression.** Base Bash pack byte-unchanged, 136/0. Identity/pass-through and field-extraction mutants still RED. Envelope untouched. Moving `start`/`saps` out of `_PS_MUTATING` into command-position `_SPAWN_ALIAS` additionally **fixes a latent FP** (`Select-String -Pattern start` now ALLOWs — ADV-1) with no lost spawn denial.
5. **15 mutants load-bearing.** Each real string DENIes and the mutated guard ALLOWs; every target substring exists verbatim in the guard (`New-Object\s+-c\w*\b`, `\[(?:System\.)?Activator\]::CreateInstance\b`, `GetTypeFromProgID\b`, `or _SPAWN_ALIAS.match(tok)`, `tok = _effective_command_token(words)`).

## Advisory (non-blocking, fail-safe)
- **A-R4-1:** A bare single-token assignment of an exact shell-executable name — `$p = "powershell.exe"`, `$p = "cmd"`, `$p = powershell` — is now DENIED. This over-blocks the quoted **string-assignment** variant, which `shlex` cannot distinguish from the unquoted **invocation** variant `$p = powershell` (which PowerShell *does* execute and *should* be denied). Not a realistic reviewer read (performs no read and no write); fails safe. Multi-word RHS (`$cl = "powershell -File b.ps1"`) correctly ALLOWs. Advisory, not a correction; does **not** re-open D-R3-1.

## Directive verification (scope note)
In-regime. Authoritative applicable-set resolution and `verification.json` are the `directive-compliance-verifier`'s responsibility, not G3. No code-review contradiction observed; allowed-path scope respected.

## Conclusion
The round-4 delta removes the D-R3-1 root cause and replaces it with correct command/spawn-position detection that also closes G5 NF1 (COM `-c` floor + reflection) and NF2 (assignment-fronted encoded shell), and fixes latent FP ADV-1. All realistic `-Encoding`/powershell-as-data reads now ALLOW; every previously-denied laundering form still DENIes; base Bash pack byte-unchanged and green; PS pack 187/0 with 15 load-bearing mutants; ruff clean; modularity 0 failures. The only new behavior change is a contrived, fail-safe over-block of a bare shell-name string assignment (advisory A-R4-1). **D-R3-1 is closed and the round-4 delta is correct with no new blocking code defect.**

**G3: PASS**

Reviewed identity `b6db457` (HEAD `b194c90` = control-plane only).
