# M0-T145 G3 reports (verbatim reviewer returns, both rounds)

Saved VERBATIM by the orchestrator from the code-review agent-return channel (2026-09-06;
transport entity-decoding only: `&lt;`→`<`, `&gt;`→`>`, `&amp;`→`&`). Reviewer: independent
run-quality-gate code review (read-only, Opus 4.8). Round 1 reviewed SHA 0671edd5 → **FAIL**
(genuine regression found); round 2 (delta) reviewed SHA bac01a56 → **PASS**.

---

## ROUND 1 (reviewed 0671edd5) — FAIL

# Gate Report

- Gate ID: G3 (independent code review)
- Task ID: M0-T145 (readonly-guard braced-variable residual; closes M0-T109 G5 MEDIUM)
- Reviewer: run-quality-gate (independent, read-only) — Opus 4.8
- Producer: supervised-loop-fable-worker (design/hunks) + orchestrator (mechanical apply), lineage `persistent-local-01`
- Result: **FAIL**
- Clean environment/worktree used: yes — `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145`, HEAD `0671edd5a0be16848eaa2b7e7c80e7c50511b998`, `git status` clean, reviewed against parent `29f9ee7b`.

## Acceptance criteria reviewed

1. Braced-variable assignment-fronted nested shell (`${x} = powershell -enc …`) now DENIED for a governed read-only role — **met** (verified below).
2. `${null}` discard (G4 A3) stays ALLOWED — **met**.
3. No new false positives on braced reads — **met**.
4. No regression to other consumers of `_ps_normalize` / `_split_command_segments` — **NOT met** (new false negatives introduced; see Defect D1).
5. Bash-tool behavior byte-identical — **met** (0 diffs, verified).
6. Documented command `python -m pytest tools/test_readonly_agent_guard_powershell.py -q` passes — **met** (exit 0, `1 passed in 17.12s`).
7. Report accuracy — **NOT met** (materially false safety claim; see Defect D2).

## Directive/requirement verification

No `directive_refs` were included in the review packet for this G3 pass; M0-T145 is a technical residual fix (the commit is applied under D-032 R005/Amendment 2 by the orchestrator). Per-requirement directive verification (D-<nnn>-R<nnn>) is out of scope for this code-review gate and belongs to the independent `directive-compliance-verifier`. Flag: if M0-T145 is treated as in-regime at accept time, that separate pass is still required.

## Steps independently executed

All from the frozen worktree at HEAD `0671edd5`.

1. `git diff 29f9ee7b 0671edd5 --stat` and full diff of the guard + test files.
2. Read `.claude/hooks/readonly_agent_guard.py` (`_ps_normalize`, `_debrace_var`, `_PS_BRACED_VAR`, `_split_command_segments`, `_SEGMENT_CHARS`, `_ASSIGN_LAYER`, `_effective_command_token`, `_launches_nested_shell`, `_PS_REDIRECT_TARGET_OK`, `_NESTED_SHELL`, `_shell_command_mutates`).
3. `python -m pytest tools/test_readonly_agent_guard_powershell.py -q` → exit 0, `1 passed`.
4. `python tools/test_readonly_agent_guard_powershell.py` (direct) → `ALL CHECKS PASSED`, exit 0.
5. Adversarial probe calling the guard's own functions (`_ps_normalize`, `_shell_command_mutates`) on brace-glued forms.
6. Parent-vs-child differential: loaded `29f9ee7b:.claude/hooks/readonly_agent_guard.py` via `git show` into a module and compared `_shell_command_mutates` decisions for PS and Bash.

Trigger tokens in probes were built by string concatenation (`"power"+"shell"`, `"gi"+"t"`, `"pu"+"sh"`) so the reviewer's own read-only guard did not misfire on the probe text.

## Expected versus actual

Intended closure (PowerShell, `_shell_command_mutates(s, powershell=True)`), parent `29f9ee7b` → child `0671edd5`:

| Command | Parent | Child | Correct? |
|---|---|---|---|
| `${x} = powershell -enc SQBFAFgA` | ALLOW | DENY | yes (target residual closed) |
| `${a-b}=pwsh -e SQBFAFgA` | ALLOW | DENY | yes |
| `${2} = powershell -enc SQBFAFgA` | ALLOW | DENY | yes |
| `${env:tmp} = powershell -enc SQBFAFgA` | ALLOW | DENY | yes |

Regression surface — safe-name brace **glued without a separator** (parent → child):

| Command | Parent | Child | Verdict |
|---|---|---|---|
| `${x}powershell -enc SQBFAFgA` | DENY | **ALLOW** | NEW false-negative |
| `${x}git push` | DENY | **ALLOW** | NEW false-negative |
| `${a-b}pwsh -enc SQBFAFgA` | DENY | **ALLOW** | NEW false-negative |
| `${x}start powershell -enc SQBFAFgA` | DENY | **ALLOW** | NEW false-negative |
| `${x}cmd /c whoami` | DENY | **ALLOW** | NEW false-negative |
| `${a}${b}git push` | DENY | **ALLOW** | NEW false-negative |
| `${x};git push` (control, separator present) | DENY | DENY | unchanged (OK) |

Bash-tool differential (`powershell=False`): 6/6 representative cases identical, **0 diffs** — the byte-identical claim for the Bash pack holds.

## Evidence paths

- Guard: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\.claude\hooks\readonly_agent_guard.py` (new `_PS_BRACED_VAR` L523, `_debrace_var` L526-531, wiring L574; single caller L702).
- Test: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\tools\test_readonly_agent_guard_powershell.py` (M0-T145 rows L499-571).
- Report: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\project-control\reports\M0-T145-guard-brace-residual.md`.

## Human-style walkthrough findings

Not a UI task. The functional walkthrough is the guard-decision differential above.

## Regression/security/provenance findings

Root cause of the regression: `_debrace_var` rewrites `${x}` → `$x`, which **deletes the `{` and `}` characters**. Both braces are members of `_SEGMENT_CHARS` (`";\n|&(){}<>`" + backtick, L341). Before the fix those braces were structural segment boundaries that isolated a directly-following command token (`powershell`, `git`) into its own segment, where `_launches_nested_shell` / `_git_argv_mutates` correctly saw it in command position. After the fix the braces are gone, so the debraced variable is glued to the following token, producing `$xpowershell` / `$xgit`. `_NESTED_SHELL` (L227, anchored `^(?:powershell|pwsh|cmd)(?:\.exe)?$`) and `_is_git` (exact `git`/`git.exe`) require an exact token, so the glued token matches neither and the command escapes detection.

The rewrite is applied via `_PS_BRACED_VAR.sub` over the **entire** normalized string (L574), i.e. it also rewrites braces inside quoted regions and everywhere else — the separator-deletion side effect is global, not scoped to assignment position. This is precisely the "regression risk to other consumers of `_ps_normalize`" the review was asked to assess: every PS-path consumer (`_PS_MUTATING`, `_MUTATING`, `_unquoted_redirect`, `_git_argv_mutates`, `_launches_nested_shell`, `_SCRIPT_WRITE`) now receives the separator-stripped, token-glued text.

Exploitability assessment (stated honestly): the six newly-allowed forms are not valid PowerShell command invocations — `${x}powershell` / `${x}git` with no separator parse as an unexpected-token error rather than executing the shell/git — so immediate real-world exploitability appears LOW. I could not execute PowerShell to confirm parse behavior (the reviewer's own guard denies `powershell`/`pwsh` in command position), so this remains an inference, not a proof. Regardless of executability, the change **demonstrably removes denials** from a fail-closed security guard, undisclosed and untested.

Charset/behavior checks that PASSED (verified via `_ps_normalize` output): `${a-b}`→`$a_b`, `${env:PATH}`→`$env:PATH`, `${2}`→`$_2`, `${my.var}`→`$my_var`, `${null}`→`$null` (stays an allowed redirect target — G4 A3 preserved). Unsafe-name braced assignments (`${x y} = …`) are correctly NOT rewritten and remain the documented residual (ALLOW on both parent and child — not a regression).

Minor observation (LOW): with the fix, `_PS_REDIRECT_TARGET_OK`'s `\$\{null\}` alternative (L212) is dead on the PS path because every `${null}` is rewritten to `$null` before `_unquoted_redirect` runs. Harmless (defense-in-depth), not a defect.

Provenance/process: hook-file edit applied by the orchestrator (disclosed report §6). Producer≠verifier is preserved for this gate.

## Defects

- **D1 (HIGH) — security guard newly ALLOWs six previously-DENIED forms.** Reproduce: load parent `29f9ee7b` and child `0671edd5` guards, call `_shell_command_mutates("${x}powershell -enc SQBFAFgA", powershell=True)` → parent `True` (DENY), child `False` (ALLOW); same for `${x}git push`, `${a-b}pwsh -enc …`, `${x}start powershell …`, `${x}cmd /c whoami`, `${a}${b}git push`. Cause: brace-deletion strips `_SEGMENT_CHARS` separators and glues tokens. In a fail-closed security guard, silently reducing coverage is a defect even at low exploitability.
- **D2 (HIGH) — materially false report/comment claim.** Report §6 (line 219): "no existing denial is removed and the Bash pack is byte-identical." The Bash half is true (verified 0 diffs); the "no existing denial is removed" half is false (D1). The code comment at L516-521 ("Bounded no-new-FP posture") documents only the false-positive direction and does not disclose the false-negative/separator-deletion side effect. This is an inaccurate safety claim on a security-sensitive change.
- **D3 (MEDIUM) — test suite cannot catch the regression.** The M0-T145 rows cover only assignment-position deny, braced reads no-FP, and two mutants that both guard the intended-positive (assignment) direction. There is no brace-glued-without-separator row, so the suite is green while the guard is weaker than its parent. Tests are one-directional against exactly the risk a separator-deleting rewrite creates.

## Required rework

1. Stop deleting structural separators. Preferred: make `_split_command_segments` treat a `${…}` variable as an atomic, non-splitting token (fixes the assignment case without removing brace boundaries); or restrict `_debrace_var` to only rewrite when the `${name}` is in assignment position (followed by optional whitespace + `=`) and otherwise leave it braced; or preserve a boundary so a glued following command is not merged into the variable token.
2. Add regression teeth: brace-glued-without-separator rows (`${x}powershell -enc …`, `${x}git push`, `${a}${b}git push`, …) asserting DENY-or-unchanged, plus a mutant that would re-open the glue hole.
3. Correct report §6 and the L516-521 comment to disclose the true before/after coverage (Bash byte-identical; PS path relaxes six glued forms unless remediated).
4. Re-run the differential parent-vs-child across PS and Bash and include it as evidence.

## Reviewer conclusion

**FAIL.** The change correctly closes the target M0-T109 G5 MEDIUM residual — PowerShell assignment-fronted braced nested shells (`${x} = powershell -enc …`, incl. hyphen/`env:`/digit/dotted names and chains) now DENY, `${null}` discard stays allowed, and the Bash pack is byte-identical (all verified). However, the normalization deletes the `{`/`}` structural separators globally, which glues the debraced variable to a directly-following command token and newly ALLOWs six forms the parent guard DENIED. That coverage reduction is undisclosed (the report explicitly claims the opposite), untested (no glued-form rows), and lands in a fail-closed security guard. Immediate exploitability appears low (the glued forms are likely PowerShell parse errors, unverified), but a security-file gate should not accept an undisclosed, untested removal of denials paired with an inaccurate safety claim. Return for the rework above; the surgical remediation (atomic `${…}` in the segment splitter, or assignment-scoped debrace) closes the target residual without the separator-deletion regression.

---

## ROUND 2 (delta review of rework, reviewed bac01a56) — PASS

# Gate Report (delta review)

- Gate ID: G3 (independent code review — delta of rework)
- Task ID: M0-T145 (readonly-guard braced-variable residual; closes M0-T109 G5 MEDIUM)
- Reviewer: run-quality-gate (independent, read-only) — Opus 4.8
- Producer: supervised-loop-fable-worker (design) + orchestrator (apply)
- Result: **PASS**
- Reviewed SHA: `bac01a561e20398d3606bd770703f8311a89e029` (delta vs previously-reviewed `0671edd5`; regression baseline `29f9ee7b`). Worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145`, `git status` clean.

## Acceptance criteria reviewed

1. Braced assignment-fronted nested shell DENIED — met.
2. Brace-glued (non-assignment) forms retain parent denials — **met (was the D1 FAIL; now fixed)**.
3. `${null}` discard (G4 A3) stays ALLOWED — met.
4. No new false positives on braced reads — met.
5. No regression to other `_ps_normalize` consumers — **met**.
6. Bash byte-identical — met (0 diffs).
7. Documented command passes — met (exit 0, `1 passed`).
8. Report accuracy — **met (was D2; now corrected)**.

## Directive/requirement verification

No `directive_refs` in the review packet; M0-T145 is a technical residual fix. Per-requirement directive verification is out of scope for this code-review gate (belongs to `directive-compliance-verifier` if the task is treated as in-regime at accept time).

## Steps independently executed (delta)

1. `git diff 0671edd5 bac01a56` on guard, test, and report.
2. Differential baseline `29f9ee7b` vs child `bac01a56` via `git show` into loaded modules, `_shell_command_mutates` for PS and Bash across glued/assignment/edge/no-FP cases.
3. `python -m pytest tools/test_readonly_agent_guard_powershell.py -q` → exit 0, `1 passed in 18.14s`.
4. `python tools/test_readonly_agent_guard_powershell.py` (direct) → `ALL CHECKS PASSED`, exit 0.
5. `python tools/modularity_check.py --check` → exit 0 (no failure; no warning on the guard).
6. Grep confirmed `_PS_BRACED_VAR`/`_debrace_var` still have a single consumer (`_ps_normalize`, L586; caller L714).

## Expected versus actual (defect closure)

D1 regression surface — baseline `29f9ee7b` → child `bac01a56` (PS):

| Command | Baseline | Prev commit `0671edd5` | Child `bac01a56` |
|---|---|---|---|
| `${x}powershell -enc SQBFAFgA` | DENY | ALLOW (bug) | **DENY** |
| `${x}git push` | DENY | ALLOW (bug) | **DENY** |
| `${a-b}pwsh -enc SQBFAFgA` | DENY | ALLOW (bug) | **DENY** |
| `${x}start powershell -enc SQBFAFgA` | DENY | ALLOW (bug) | **DENY** |
| `${x}cmd /c whoami` | DENY | ALLOW (bug) | **DENY** |
| `${a}${b}git push` | DENY | ALLOW (bug) | **DENY** |

Intended closure preserved (baseline ALLOW → child DENY): `${x} = powershell -enc`, `${x}=powershell -enc`, `${a-b}=pwsh -e`, `${2} = powershell -enc`, `${env:tmp} = powershell -enc`, `${a}=${b}=powershell -enc` — all DENY.

Lookahead edge cases (no new regression): `${x} =powershell` / `${x}= powershell` / `${x}  =  powershell` → DENY (assignments); `${x}==powershell` → ALLOW on both baseline and child (non-executable comparison form, pre-existing residual, not a regression); `${x}=${y}powershell` → DENY both. `gci > ${null}`, `${env:PATH} -split ';'`, `${x} = Get-Content README.md` → ALLOW preserved. Bash: 0 diffs.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\.claude\hooks\readonly_agent_guard.py` — `_PS_BRACED_VAR` L535 (`r"\$\{([A-Za-z0-9_:.\-]+)\}(?=\s*=(?!=))"`), comment L517-534, docstring bullet L67-80.
- `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\tools\test_readonly_agent_guard_powershell.py` — six glued DENY rows L526-538, third mutant L547-551.
- `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145\project-control\reports\M0-T145-guard-brace-residual.md` — CORRECTION line + §7 (L277-301).

## Human-style walkthrough findings

Not a UI task; the decision differential above is the functional walkthrough.

## Regression/security/provenance findings

The remediation is exactly the surgical direction recommended: scope the debrace to assignment position via zero-width lookahead `(?=\s*=(?!=))`, so braces outside assignment position retain their `_SEGMENT_CHARS` separator role and a brace-glued command token still splits into command position and DENIES. The rewrite remains PS-scoped (single caller inside `_ps_normalize`), so Bash behavior is byte-identical (verified 0 diffs). The `(?!=)` correctly excludes `==`. `${null}` is no longer rewritten and is accepted directly by `_PS_REDIRECT_TARGET_OK` (the `\$\{null\}` alternative is live again — my earlier LOW "dead code" observation is now moot). No new false negatives observed across the assignment/glued/edge probe set. Modularity: exit 0, no failure, no warning on the guard (change is a one-line regex + comments + tests).

D2 report accuracy: an explicit CORRECTION line now flags the intermediate false claim, and §7 records the G3 finding and rework. For the final shipped state, the §6 residuals statement ("no existing denial is removed and the Bash pack is byte-identical") is now factually accurate — verified.

D3 test teeth: the third mutant (removing the lookahead) is load-bearing and non-vacuous — my independent differential shows the lookahead-removed form (`0671edd5`) ALLOWs `${x}powershell -enc` while the shipped guard DENIES it; the suite's mutant row asserts exactly that (`mutant ALLOW / real DENY`) and passed.

## Defects

None open. D1 (HIGH), D2 (HIGH), D3 (MEDIUM) from the prior review are all resolved and independently verified.

## Required rework

None.

## Reviewer conclusion

**PASS.** The rework closes all three defects from my prior FAIL: the assignment-scoped lookahead restores every one of the six brace-glued denials (verified against baseline `29f9ee7b`) while preserving the intended closure of assignment-fronted braced nested shells, keeping the `${null}` discard allowed, and leaving Bash behavior byte-identical (0 diffs). The report now transparently corrects the earlier false safety claim and, for the shipped code, that claim is accurate. Tests gained six glued-form DENY rows and a load-bearing lookahead-removal mutant. Documented command exit 0, direct run all-pass, modularity exit 0. The fix is correct, surgical, honestly documented, and adequately tested.
