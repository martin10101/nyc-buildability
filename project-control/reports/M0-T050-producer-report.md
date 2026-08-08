# M0-T050 producer report — dry-run argument-vector fidelity fix

Owner directive D-010 source-020 (R184–R195). SECOND demonstrated pre-activation
defect in `tools/agent_supervisor/harden_controller_config.ps1`, caught by the
owner's personal ELEVATED `-DryRun`: every dry-run line printed ONLY the
executable, with NO arguments.

- Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch
  `task/M0-T050-dryrun-args-fix`, base HEAD `1e649a8` (current main; contains the
  M0-T049 brace fix, blob `ca3811cd`, now itself demonstrated defective for this
  NEW reason).
- Environment probe: Python 3.11.9, Windows PowerShell **5.1.26100.8875**, git —
  all available. Every dynamic proof below ran on real WinPS 5.1.

## 1. Root-cause mechanics — the `$Args` automatic-variable collision

`Invoke-Step` declared `param([string]$Exe, [string[]]$Args)`. Under **Windows
PowerShell 5.1**, `$Args` is an **automatic variable**: inside every function it
is intrinsically bound to the array of *unbound* positional arguments. Declaring a
parameter literally named `$Args` does not reliably receive the caller's bound
value — the automatic meaning shadows/empties it — so inside the function body:

- `$shown = "$Exe " + ($Args -join " ")` joined an **empty** array → `$shown`
  became just the exe with a trailing space.
- `& $Exe @Args` would have splatted an **empty** vector as well (never reached in
  dry-run because the function returns first, but the same emptiness affects the
  real apply path's display and would have degraded the splat).

Because the display and the splat both read the same empty `$Args`, the dry-run
transcript showed the executable alone. Exit codes cannot catch this — a dry run
prints and returns 0 regardless.

`$CommandArgs` is not an automatic variable name, so a parameter by that name
binds the caller's value normally and cannot collide.

### Direct WinPS 5.1 proof of the mechanism (isolated demo)

Two identical functions differing only in the parameter name, both called with the
same vector `@("C:\controller\config.toml", "/inheritance:r")`:

```
[bad]  icacls.exe
[good] icacls.exe C:\controller\config.toml /inheritance:r
```

`[bad]` (param named `$Args`) drops the vector; `[good]` (param named
`$CommandArgs`) retains it. This is the collision, reproduced in a minimal scope.

## 2. Exact diff summary

`tools/agent_supervisor/harden_controller_config.ps1` (2 hunks):

- **Invoke-Step (now lines ~90–107).** `param([string]$Exe, [string[]]$Args)` →
  `param([string]$Exe, [string[]]$CommandArgs)`; both uses updated:
  `$shown = "$Exe " + ($CommandArgs -join " ")` and `& $Exe @CommandArgs`. Added
  an explanatory comment naming the collision. No other logic changed; the
  elevation refusal (still precedes DryRun), brace interpolations from M0-T049,
  and the icacls/takeown command structure are untouched.
- **Completion wording (now lines ~177–191).** The unconditional
  `Write-Host ("apply complete. …")` is wrapped in `if ($DryRun) { … } else { … }`.
  The dry-run branch prints `"dry run complete. NO changes were made: the
  icacls/takeown commands above were only PRINTED, not executed. …"`. The `else`
  (real apply) branch keeps the original "apply complete." text verbatim. Minimal
  conditional; nothing else restructured.

Old blob `ca3811cd` → new blob `9625514`. Fixed script PARSES with
`parse_errors=0` under WinPS 5.1.

## 3. Per-call-site argument-retention proof (all Invoke-Step call sites)

The parameter rename does not change positional binding: every call site passes
the exe as positional 1 (→ `$Exe`) and the array as positional 2 (→ was `$Args`,
now `$CommandArgs`). AST enumeration of the fixed script found **14** Invoke-Step
call sites (the directive said "12"; see §7 — the directive's own range
enumeration actually sums to 14, and all are covered). Line numbers are
post-edit.

| # | Line | Path | Exe | Argument array | Retained |
|---|------|------|-----|----------------|----------|
| 1 | 134 | rollback | `$Icacls` | `@($file, "/inheritance:e")` | yes |
| 2 | 135 | rollback | `$Icacls` | `@($file, "/grant", "${UnelevatedUser}:(M)")` | yes |
| 3 | 136 | rollback | `$Icacls` | `@($dir, "/inheritance:e")` | yes |
| 4 | 137 | rollback | `$Icacls` | `@($dir, "/grant", "${UnelevatedUser}:(M)")` | yes |
| 5 | 140 | rollback display | `$Icacls` | `@($file)` | yes |
| 6 | 141 | rollback display | `$Icacls` | `@($dir)` | yes |
| 7 | 150 | apply takeown | `$Takeown` | `@("/F", $file, "/A")` | yes |
| 8 | 151 | apply takeown | `$Takeown` | `@("/F", $dir, "/A")` | yes |
| 9 | 155 | apply | `$Icacls` | `@($file, "/inheritance:r")` | yes |
| 10 | 156 | apply | `$Icacls` | `@($file, "/grant:r", "BUILTIN\Administrators:(F)", "NT AUTHORITY\SYSTEM:(F)", "${UnelevatedUser}:(RX)")` | yes |
| 11 | 166 | apply | `$Icacls` | `@($dir, "/inheritance:r")` | yes |
| 12 | 167 | apply | `$Icacls` | `@($dir, "/grant:r", "BUILTIN\Administrators:(OI)(CI)(F)", "NT AUTHORITY\SYSTEM:(OI)(CI)(F)", "${UnelevatedUser}:(RX)")` | yes |
| 13 | 174 | apply display | `$Icacls` | `@($file)` | yes |
| 14 | 175 | apply display | `$Icacls` | `@($dir)` | yes |

The six **apply-path** vectors (rows 7–12) are pinned by static test B1 and
replayed dynamically by test A2. Retention is proven live: on the fixed script the
representative `icacls /grant:r` vector prints in full:

```
[dry-run] icacls.exe C:\controller\config.toml /grant:r BUILTIN\Administrators:(F) NT AUTHORITY\SYSTEM:(F) DESKTOP-ABC\owner:(RX)
```

## 4. RED-on-defective transcript (R189)

The exact same layer-A AST-extraction harness, run against the CURRENTLY MERGED
defective content reconstructed OUTSIDE the repo
(`git show 1e649a8:tools/agent_supervisor/harden_controller_config.ps1`,
`git hash-object` = `ca3811cd7e38a044bd0e01056e95b5028b6ce615`, confirming byte
identity to the merged blob), with the icacls `/grant:r` file vector:

```
=== DEFECTIVE (blob ca3811cd, git show 1e649a8) ===
[dry-run] icacls.exe
=== FIXED (worktree HEAD, M0-T050) ===
[dry-run] icacls.exe C:\controller\config.toml /grant:r BUILTIN\Administrators:(F) NT AUTHORITY\SYSTEM:(F) DESKTOP-ABC\owner:(RX)
```

The defective content drops EVERY argument (exe only). This is codified as the
permanent test `test_dryrun_line_is_red_on_the_defective_merged_content`, which
reconstructs blob `1e649a8` via `git show` and asserts `assertNotIn` for each
element on defective content AND `assertIn` on the fixed script — the test is RED
on `ca3811cd` and GREEN on the fix, proving the new fidelity assertions are
load-bearing.

## 5. Wording fix — before / after

- **Before (unconditional):** `apply complete. Verify from an UNELEVATED shell
  that the OS-ACL verdict is PROTECTED …` — printed even on a dry run, falsely
  implying changes were applied.
- **After (dry-run branch):** `dry run complete. NO changes were made: the
  icacls/takeown commands above were only PRINTED, not executed. Re-run WITHOUT
  -DryRun from an elevated shell to apply, then verify …`
- **After (apply branch):** the original "apply complete. …" text, unchanged.

Test D (`test_dryrun_completion_wording_cannot_claim_application`) statically
asserts the branch structure (`if ($DryRun)` → "dry run complete. NO changes were
made" → `} else {` → "apply complete.") and that the isolated dry-run branch never
contains "apply complete".

## 6. Test design — why AST-extraction + call-site fidelity prove the contract without elevation

The elevation refusal precedes DryRun handling (existing reviewed behavior — left
unchanged), so an unelevated process cannot run the whole script to observe a real
dry-run. The contract is instead proven in two mutually-reinforcing layers:

- **A (dynamic):** the WinPS 5.1 language parser (`Parser::ParseFile`, same API
  the suite already uses) extracts the `Invoke-Step` FunctionDefinitionAst from
  the actual script file, `Invoke-Expression` defines it in a scope where
  `$DryRun = $true`, and it is invoked with full vectors. This exercises the REAL
  function body — the `$shown` display and the DryRun branch — and asserts every
  element survives. A2 replays the script's six apply-path vectors and asserts
  every path, `/F`, `/A`, `/inheritance:r`, `/grant:r`, and every ACL principal
  (the owner's enumerated minimum) appears.
- **B (static):** the AST is parsed to enumerate every `Invoke-Step` CommandAst
  and assert the six apply-path call sites carry exactly the expected argument
  arrays, so the dynamic replay in A cannot silently drift from what the script
  actually calls. A companion check extracts the function text and asserts no
  `$Args` parameter/usage remains in the CODE (comments stripped) and that
  `$CommandArgs` is used.

Together: A proves the function emits the full vector; B proves the function is
called with the full vector at the six real apply sites — end-to-end fidelity of
the dry-run transcript without needing elevation. C proves the tests fail on the
defective merged code; D proves the completion wording cannot claim application.

## 7. Counts

- Baseline `test_agent_supervisor_os_acl.py`: **32 passed**.
- After: **38 passed** (32 + 6 new tests; 0 skipped on this Windows+PS+git host).
- Full suite `python -m pytest tools/test_agent_supervisor_*.py -q`:
  baseline **1381 passed / 2 skipped** → after **1387 passed / 2 skipped**
  (+6 = the 6 new tests only; the 2 pre-existing skips are unchanged).

New tests (all in `HardenScriptTests`):
1. `test_dryrun_emits_the_full_generic_vector` (A1)
2. `test_dryrun_replays_all_six_apply_path_vectors` (A2)
3. `test_apply_path_call_sites_carry_full_argument_arrays` (B1)
4. `test_invoke_step_has_no_args_automatic_variable_collision` (B2)
5. `test_dryrun_line_is_red_on_the_defective_merged_content` (C)
6. `test_dryrun_completion_wording_cannot_claim_application` (D — covers both the
   dry-run "cannot claim application" and the apply-path-wording-unchanged checks)

## 8. Per-requirement producer evidence (R185–R190)

| Req | Requirement (summary) | Evidence |
|-----|-----------------------|----------|
| R185 | Root-cause the dropped-argument dry-run defect | §1: `$Args` automatic-variable collision under WinPS 5.1; isolated bad/good demo |
| R186 | Rename param to `$CommandArgs`; update both uses; no `$Args` remains | §2 diff; test B2 asserts no `$Args` in code, `$CommandArgs` present |
| R187 | Preserve positional binding at every call site | §3 14-row retention table; B1 static pin; A2 live full-vector replay |
| R188 | Dynamic full-vector proof via AST extraction + six apply-path replay | Tests A1, A2; §3 live transcript |
| R189 | RED-on-defective proof against merged blob `ca3811cd` | §4 transcript; test C (`git show 1e649a8`, hash-object confirmed) |
| R190 | Dry-run completion wording cannot claim application; apply wording unchanged | §5; test D |

R184 (directive capture) and R191–R195 (gate/accept/merge/activation-lane) are
orchestrator/owner-lane — not producer-actionable here.

## 9. Deviations / uncertainty (nothing claimed unproven)

- **Call-site count discrepancy (advisory):** the directive says "12 call sites"
  but its own enumerated ranges (129–136 = 6, 145–146 = 2, 150–151 = 2, 161–162 =
  2, 169–170 = 2) sum to 14, and AST enumeration of the script confirms **14**
  Invoke-Step calls. All 14 are covered in §3; the fix is unaffected either way.
  Flagging so the reviewer is not surprised by "14" vs "12".
- **Rollback-path completion wording (out of scope, noted):** the `-Rollback`
  branch still prints `"rollback complete: the prior single-account-writable
  posture is restored."` unconditionally, so a `-Rollback -DryRun` combination
  would also read as if applied. The directive bounded the wording fix to the
  apply tail (~line 173) and said "do not restructure anything else", so I left
  the rollback message untouched. Raising it as a candidate follow-up, not a
  change made here.
- **Line-ending note:** git reports "LF will be replaced by CRLF" for the .ps1 on
  the next checkout. This is normal for a text script (not a byte-identity-locked
  lockfile); git stores LF and the diff/parse are clean. No action taken.
- No control-plane writes, git commit/push, or `gh` were run (orchestrator lane).
