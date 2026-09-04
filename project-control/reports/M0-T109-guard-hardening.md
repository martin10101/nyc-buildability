# M0-T109 producer report — readonly-guard follow-up hardening

- **Task:** M0-T109 (governance/security; D-024, in-regime). Closes the three documented
  M0-T108 round-4 residuals (ADV-R4-1, ADV-4, ADV-R4-2).
- **Producer:** orchestrator (acting producer in the isolated worktree wt-m0t109; one writer for
  the guard's overlapping state per the convergence rule).
- **Worktree/branch:** `wt-m0t109` / `task/M0-T109-guard-hardening` (base `1c069571`; the guard
  and its PowerShell test are byte-identical between that base and the candidate tip — zero
  drift, so adoption applies only these edits).
- **Date:** 2026-09-04 (UTC)

## 1. Deliverables (exactly the packet allowed_paths)

| Path | Change |
|---|---|
| `.claude/hooks/readonly_agent_guard.py` | ADV-R4-1 chained-assignment strip loop; ADV-4 reachable self-anchored `[Type]::GetTypeFromProgID` tooth; ADV-R4-2 residual documentation. |
| `tools/test_readonly_agent_guard_powershell.py` | Round-5 deny + no-FP rows; three RED-on-mutant proofs; existing co-removal mutant made honest. |
| `project-control/reports/M0-T109-guard-hardening.md` | This report. |

The Bash pack is byte-unchanged (git diff shows no line touching the Bash path); all M0-T108
denials are preserved (full `test_readonly_agent_guard*.py` suites green); `-Encoding` and
powershell-as-data reads remain ALLOW.

## 2. Residual closures

### ADV-R4-1 (MEDIUM, G5) — chained-assignment encoded/nested shell
`_effective_command_token` previously stripped only ONE leading `$var=` layer, so
`$a=$b=powershell -enc <b64>` resolved to `$b=powershell` (not a nested-shell token) and
ALLOWed. The strip now **loops** (`_ASSIGN_LAYER` regex, applied while the head is still an
assignment), reducing `$a=$b=$c=powershell` and `$a = $b = powershell` to `powershell` → DENY.
Docstring names "chained assignment" explicitly. No false positive: `$a=$b=Get-Content …`
reduces to `Get-Content` → ALLOW (tested).

### ADV-4 (G4) — GetTypeFromProgID tooth unreachable behind `::`
The bare `GetTypeFromProgID\b` alternative never fired, because the shared leading-delimiter
class `(?:^|[\s;&|({`=])` excludes `:`, so a real `[Type]::GetTypeFromProgID(...)` invocation
(the char before the tooth is `:`) never matched. Fixed by **self-anchoring** the tooth as
`\[(?:System\.)?Type\]::GetTypeFromProgID\b` — parallel to the reachable
`[Activator]::CreateInstance` tooth — so the belt-and-suspenders reflection-COM-setup denial is
now reachable and independently load-bearing (a standalone
`[Type]::GetTypeFromProgID('Scripting.FileSystemObject')` with no CreateInstance present DENYs).
**Co-removed mutant made honest:** the prior single mutant dropped both the CreateInstance and
the (dead) GetTypeFromProgID teeth while testing a CreateInstance-only payload; it is now split
into two honest mutants — one drops only CreateInstance (CreateInstance-only payload), one drops
only the GetTypeFromProgID tooth (GetTypeFromProgID-only payload). Each proves its tooth
load-bearing. The reachable `[activator]::CreateInstance([type]::GetTypeFromProgID(...))` nested
form still DENYs via the CreateInstance tooth (preserved).

### ADV-R4-2 (LOW, G5) — open-ended reflection/command-lookup residuals
Documented in the module docstring, not chased with more teeth (that arms-race is unwinnable):
`[Type]::GetTypeFromCLSID('{clsid}')` (the CLSID sibling — an unbounded GUID set) and
command-lookup indirection `&(gcm powershell)` / `&(get-command …)` (shell name produced by a
subexpression, not in command position). Both are covered by the orchestrator-only integration
model (only the lead commits/pushes/merges; a reviewer's local scratch never reaches a branch,
PR, or ledger). Tests assert the docstring names both residuals.

## 3. Verification (real command output)

- `python tools/test_readonly_agent_guard_powershell.py` → **ALL CHECKS PASSED** (exit 0),
  including 3 new Round-5 deny families, 3 no-FP rows, 2 residual-doc assertions, and 17
  RED-on-mutant proofs (the 3 new/updated ones: CreateInstance-only, GetTypeFromProgID-only,
  chained-assignment-loop-revert).
- `python tools/test_readonly_agent_guard.py` → **ALL CHECKS PASSED** (exit 0) — the shell-
  agnostic suite, proving all M0-T108 denials preserved.
- `python tools/modularity_check.py --check` → **failures 0** (exit 0). `readonly_agent_guard.py`
  is 620 SLOC — in the WARN band (600) but under the JUSTIFY threshold (750) and far under HARD
  (1000); not baseline-grandfathered, so warn-only, no failure. Cohesion note: the file is a
  single-responsibility security-policy module (one guard, one decision surface); its teeth are
  cohesive and a split would fragment the policy. Recorded here per principle 16 so the warn is
  not silently carried.
- `ruff check` on both files → **All checks passed**.
- `git diff` scope: exactly the two code paths; the Bash pack has no changed line.

## 4. Producer self-checks (G2)

1. Scope: changed files = the two allowed code paths (+ this report). PASS.
2. All M0-T108 denials preserved; Bash pack byte-unchanged; reads stay ALLOW. PASS.
3. Each new/updated tooth proven load-bearing by a RED-on-mutant row. PASS.
4. No forbidden path touched (`.claude/settings.json`, `apps`, `services`, `tools/project_control.py`, …). PASS.
5. Modularity: warn-only (620 < 750), cohesion justification recorded above; not a failure. PASS.

Independent G3/G4/G5 review + DCV follow (recorded separately by the orchestrator).
