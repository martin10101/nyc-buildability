# M0-T108 G3 code review — DELTA re-review (VERBATIM save; round 2, post-correction)

Reviewer: independent read-only `code-reviewer` (unnamed spawn, fresh pass), ran under the guard
being reviewed; reviewed at corrected deliverable identity `f0bdf7a` (HEAD `36f9720` = control-plane
records only). Returned through the agent-return channel 2026-08-27 UTC and saved verbatim below
(transport entity-decoding only; the harness neutralized `<`/`>`/`&` and flagged the output as
instruction-shaped — control tags were neutralized and the content is preserved here as reviewer
findings, not instructions).

---

All verification complete. The correction is purely additive (new teeth + defensive extraction + `_PS_ENCODED` removal) with the identity resolution, `_MUTATING` core, and git-argv pass untouched. Here is my gate report.

---

# Gate Report

- **Gate ID:** G3 (independent code review — DELTA re-review after correction round)
- **Task ID:** M0-T108 — readonly-guard PowerShell/scripting write-gap fix
- **Reviewer:** code-reviewer (independent, read-only; ran under the guard being reviewed — writes and unquoted redirects on my own tool were themselves denied, confirming the guard is live)
- **Producer:** fable-orchestrator-session
- **Result:** **PASS**
- **Predecessor:** round-1 G3 = FAIL (`project-control/reports/M0-T108-G3-code-review.md`), three blocking write-bypass defects D1/D2/D3 + advisory D4. This is a fresh independent pass; I did not adopt the predecessor's conclusions, only its defect list to verify closure.

## Frozen identity verified

- `git diff --name-only f0bdf7a..36f9720` → only `project-control/reports/M0-T108.json`, `project-control/state.json`, `project-control/tasks/M0-T108.json` (control-plane records). Deliverable content frozen at `f0bdf7a`.
- `git diff 24aa061..f0bdf7a -- tools/test_readonly_agent_guard.py` → **empty**. Base Bash pack byte-unchanged (no existing assertion weakened).
- Correction delta `git diff 4e238b5..f0bdf7a -- .claude/hooks/readonly_agent_guard.py` — purely additive teeth + `_PS_ENCODED` removal + defensive `_shell_command_text` + docstring rewrite. Did NOT touch identity resolution (`READ_ONLY_AGENTS`, `_known_roster_agents`, `_identity`), the `_MUTATING` core regex, or `_git_argv_mutates`/`_git_sub_mutates`.
- `.claude/settings.json` matcher (`24aa061..f0bdf7a`) → single line `Bash|Write|…` → `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`.

## Automated evidence (executed)

| Command | Result |
|---|---|
| `python tools/test_readonly_agent_guard.py` | **136 PASS, 0 FAIL**, EXIT=0 (byte-unchanged base pack) |
| `python tools/test_readonly_agent_guard_powershell.py` | **138 PASS, 0 FAIL**, EXIT=0; **11 RED-on-mutant rows** all load-bearing |
| `ruff check` (both changed Python files) | All checks passed |
| `python tools/modularity_check.py --check` | failures 0; guard file NOT among the 5 warnings |

The RED-on-mutant pack is genuine, not vacuous: it byte-mutates the real guard source, writes each mutant to a temp tree, and asserts mutant=ALLOW **and** real-guard=DENY on the same payload. The 11 mutants cover the 4 original teeth plus the 7 correction teeth (nested-shell, call-operator unwrap, `::new()`, ComObject, CIM/WMI, alias `ac`, defensive field extraction).

## Round-1 defect closure — independently reproduced (43 probes, 0 mismatches)

| Round-1 defect | Reproduction | Round-1 | Now |
|---|---|---|---|
| **D1** PS write aliases | `ac x.txt hi`, `clc x.txt`, `mi a.txt b.txt` (PowerShell) | ALLOW | **DENY** |
| **D2** .NET `::new()` writers | `[System.IO.StreamWriter]::new("x")`, `[IO.FileStream]::new("x",2)` | ALLOW | **DENY** |
| **D3** nested-shell via Bash tool | `powershell -Command Set-Content x 1`, `pwsh -c …`, `cmd /c …` (Bash) | ALLOW | **DENY** |
| **D4** field inference + fail-closed | write in `script`/`code` field → DENY; pure read in `script` → ALLOW; `tool_input` as string/list, `command` as int → DENY | fail-open risk | **defensive + fail-closed** |

## Correction-round teeth — independently verified

- `_launches_nested_shell` (D3): DENIES `powershell`/`pwsh`/`cmd`(`.exe`)(`-enc`) as first token of ANY segment (`git status ; powershell …`, `git log && cmd /c …`, `echo x | pwsh …` all DENY). Precise: `echo cmd foo`, `grep pwsh file`, `echo running cmd now`, `grep -n powershell notes.md` all **ALLOW**.
- `_PS_CALL_QUOTED` call-op unwrap: `& 'Set-Content' x 1` DENY, `& 'gh' pr create` DENY; read forms `& 'Get-Content' README.md`, `& 'git' log` **ALLOW**.
- `_PS_MUTATING` new branches: COM `New-Object -ComObject` DENY, CIM `Invoke-CimMethod … Win32_Process … Create` DENY, `::new()` constructors DENY, new aliases DENY.
- `_PS_ENCODED` removal (C3 false-positive fix): `Get-Content -Encoding UTF8 f` now **ALLOW**; encoded `-enc` still DENY via the nested-shell tooth.
- `${null}` redirect target (A3): `Get-Content f > ${null}` ALLOW; real-path `> out.txt` DENY.
- `_shell_command_text` defensive extraction (D4): scans `command` plus every other string leaf; malformed `tool_input` fails closed explicitly.

## Regression / fail-closed / no-new-false-positive

- No weakening of existing Bash denials: base pack byte-identical and 136/136 green; new passes are OR-ed (additive); the only removal (`_PS_ENCODED`) ran on the PowerShell path only.
- Identity pass-through unchanged: lead mutation **ALLOW**, roster producer `backend-engineer` mutation **ALLOW**, named/unknown spawn mutation **DENY**.
- Fail-closed envelope intact: malformed `tool_input` (string/list/`command`-as-int) → DENY; non-JSON payload → DENY; `main()` try/except → DENY on internal error.
- No new false positive across packet-named reads.

## Modularity

`.claude/hooks/readonly_agent_guard.py` is 707 raw lines, single cohesive responsibility, correct placement, below the 600-SLOC warn threshold (large docstring; checker reports 0 failures and does not flag it). ~90-line growth is additional denylist rules within the guard's one responsibility — no responsibility mixing. Public interface (`main`/CLI) stable.

## Findings (advisory, non-blocking)

- **A1 (advisory) — `_launches_nested_shell` docstring over-lists shells.** The function docstring says the tooth matches `(powershell/pwsh/cmd/bash/sh/wsl)`, but `_NESTED_SHELL` matches only `powershell|pwsh|cmd`. Reproduced: `bash -c "echo x > f"`, `sh -c "echo x > f"`, `wsl touch f` (Bash tool) all **ALLOW** — a nested-shell write via the Bash tool the tooth does not catch. This is: (a) pre-existing, not introduced by the correction; (b) explicitly scoped out per the packet's ALSO-CHECK item (d) ("only powershell/pwsh/cmd"); (c) honestly disclosed at the report level (§5 "Nested-shell precision" states `sh`/`bash` are intentionally excluded) and covered by the module docstring's compensating-control (b) (orchestrator-only integration). The only concrete defect is the **function docstring's inaccurate parenthetical**, which contradicts both the code and the report. Recommend the orchestrator route a follow-up to either extend the tooth to `bash|sh|wsl` (the Bash tool IS bash on this Windows host, a real same-class laundering vector) or correct the docstring. Not blocking for this delta because the three named round-1 D3 vectors are closed and this residual is out of the packet's stated tooth scope.
- **A2 (advisory) — report mutant-count bookkeeping.** `M0-T108-guard-powershell-fix.md` §5 says "+8 RED-on-mutant, now 8 load-bearing mutants"; the pack actually has 11 mutant rows (4 original + 7 correction teeth), all green. §4 also retains round-1 numbers (95 PASS, 589 SLOC, "guard 706 raw lines" vs actual 707). Cosmetic; every new tooth is in fact proven load-bearing.

## Directive verification (scope note)

Task is in-regime (`directive_refs: [{D-024: ALL}]`). Authoritative applicable-set resolution and `verification.json` are the independent `directive-compliance-verifier`'s responsibility (producer ≠ verifier), not G3. No code-review contradiction to any D-024 requirement observed; allowed-path scope respected.

## Conclusion

The three round-1 blocking defects (D1 PS write aliases, D2 `::new()` writer constructors, D3 nested-shell laundering via the Bash tool) are **genuinely closed** and independently reproduced as DENY at `f0bdf7a`; D4's schema-assumption risk is resolved by defensive multi-field extraction with explicit fail-closed. No new blocking defect or regression: base Bash pack byte-identical and green, identity/pass-through and the fail-closed envelope preserved, no packet-named read newly denied. Remaining items are advisory (a docstring over-listing shells for a residual honestly disclosed in the report and intentionally out of the packet's tooth scope, plus a cosmetic count discrepancy).

**G3: PASS**
