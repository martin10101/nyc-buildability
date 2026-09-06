# M0-T145 — readonly-guard braced-variable residual (M0-T109 G5 MEDIUM)

Producer report — task `M0-T145` (`readonly-guard residual: braced-variable
assignment-fronted nested shell`). Producer: supervised-loop-fable-worker
(unit of run lineage `persistent-local-01`, worktree `wt-m0t145`, branch
`task/M0-T145-brace-guard`, base SHA `29f9ee7b`). Date: 2026-09-06.

## 1. Finding and root cause

`${x} = powershell -enc <b64>` (and every braced-variable assignment-fronted
nested shell/spawn, e.g. `${a-b} = pwsh -e …`, `${x} = cmd /c …`,
`${x} = start powershell …`) is ALLOWED by
`.claude/hooks/readonly_agent_guard.py` for a governed read-only role, while
the bare form `$x = powershell -enc …` is DENIED (M0-T108 NF2).

Root cause: `_SEGMENT_CHARS = ";\n|&(){}<>` + backtick`" includes both brace
characters, so `_split_command_segments` tears `${x} = powershell …` into the
segments `$`, `x`, ` = powershell …` BEFORE `_effective_command_token` can
strip the assignment layer. The RHS shell then sits behind a bare `=` in its
segment — never in first-token or assignment-RHS command position — and
launders past `_launches_nested_shell`. `_ASSIGN_LAYER`'s optional-brace
pattern (`^\$\{?…\}?`) implies brace coverage, but a braced assignment never
reaches it intact. Pre-existing since M0-T108 (not introduced by M0-T109);
found by the independent M0-T109 G5 security review (MEDIUM); bounded until
fixed by the compensating controls (removed Write/Edit tools for reviewers +
orchestrator-only integration).

## 2. Fix (validated, awaiting authorized apply)

**This producer unit cannot edit the guard.** The Edit attempt on
`.claude/hooks/readonly_agent_guard.py` was denied by the supervision broker
with (verbatim):

> .claude/hooks/readonly_agent_guard.py is a hook; that class is never
> baseline-AUTO and needs a standing grant or a stricter tier

The exact fix therefore lives as constants in
`tools/test_readonly_agent_guard_powershell.py` (single source of truth —
apply from there, not from any restatement):

- **Hunk A** — insert `M0T145_HUNK_A` verbatim immediately BEFORE the line
  `def _ps_normalize(cmd):` (`M0T145_ANCHOR`). It adds
  `_PS_BRACED_VAR = re.compile(r"\$\{([A-Za-z0-9_:.\-]+)\}")` and
  `_debrace_var()` (safe braced name → bare form: `${x}`→`$x`, `${a-b}`→`$a_b`,
  `${env:PATH}`→`$env:PATH`, `${2}`→`$_2`; chars outside `[\w:]` map to `_`,
  non-identifier leading char gains a `_` prefix — the rewritten name is only
  ever ANALYZED, never executed).
- **Hunk B** — inside `_ps_normalize`, replace the line `M0T145_OLD_WIRING`
  (`    normalized = "".join(out)`) with `M0T145_NEW_WIRING`
  (`    normalized = _PS_BRACED_VAR.sub(_debrace_var, "".join(out))`), once.

Effect: safe braced names are rewritten to bare form on the
backtick-normalized text BEFORE segment-splitting, so the assignment stays in
one segment, `_ASSIGN_LAYER` strips it (including chains), and the RHS is
judged in command/spawn position. `${null}` normalizes to `$null`, which
`_PS_REDIRECT_TARGET_OK` already allows, so the `> ${null}` discard (G4 A3)
stays ALLOWED. PowerShell-scoped by construction (runs only inside
`_ps_normalize`); Bash-tool behavior is byte-identical.

Bounded no-new-FP posture: a braced name containing anything outside
`[A-Za-z0-9_:.-]` (whitespace, quotes, backticks, braces, `$`, shell
separators) is NOT rewritten and keeps today's behavior — deliberate, to add
no false positives; see §6 residuals.

## 3. Docstring-honesty hunk (behavior-neutral, apply WITH the fix)

The guard module docstring's nested-shell bullet currently implies the brace
form is covered ("the RHS of a leading `$var =` assignment"). When Hunks A+B
are applied, replace that bullet (exact current text, guard docstring
"Documented residuals" section) —

```
- A nested Windows shell (`powershell`/`pwsh`/`cmd`, incl. `-enc` encoded
  payloads) and the Start-Process aliases (`start`/`saps`) are denied in
  COMMAND/SPAWN position — a segment's first token OR the RHS of a leading
  `$var =` assignment (round-4 NF2). The word as pure DATA (a `-Pattern`/filename
  argument) is intentionally NOT denied. A shell invoked through a form neither
  first-token nor simple-assignment (e.g. a deeply nested expansion) is a
  residual. `bash`/`sh`/`wsl` self-launch from the Bash tool is a separate
  pre-existing residual (see `_launches_nested_shell`).
```

— with:

```
- A nested Windows shell (`powershell`/`pwsh`/`cmd`, incl. `-enc` encoded
  payloads) and the Start-Process aliases (`start`/`saps`) are denied in
  COMMAND/SPAWN position — a segment's first token OR the RHS of a leading
  `$var =` assignment (round-4 NF2), INCLUDING the braced-variable form
  (`${x} = powershell -enc …`, `${a-b} = …`): _ps_normalize rewrites safe
  braced names to bare form BEFORE segment-splitting (M0-T145, closing the
  M0-T109 G5 MEDIUM residual — the brace chars in _SEGMENT_CHARS otherwise
  tore the assignment apart so the RHS shell escaped command position). The
  word as pure DATA (a `-Pattern`/filename argument) is intentionally NOT
  denied. A shell invoked through a form neither first-token nor
  simple-assignment (e.g. a deeply nested expansion) is a residual, and so
  is a braced-variable assignment whose NAME contains characters outside
  the safe charset `[A-Za-z0-9_:.-]` (such a name is deliberately not
  rewritten — see _PS_BRACED_VAR). `bash`/`sh`/`wsl` self-launch from the
  Bash tool is a separate pre-existing residual (see `_launches_nested_shell`).
```

(If for any reason the fix is rejected rather than applied, the honest edit is
instead to append to the old bullet: "The BRACED-variable assignment form
(`${x} = powershell …`) is NOT covered — a known M0-T109 G5 MEDIUM residual,
tracked as M0-T145." — the docstring must not keep implying coverage either
way.)

## 4. Post-apply test retargeting (same commit as the apply)

Apply Hunks A+B, the docstring hunk (§3), and this retarget in ONE commit —
the suite is deliberately red in any intermediate state (the two "residual
reproduces on UNPATCHED guard" rows fail loudly the moment the fix lands, so
the scaffolding cannot silently outlive it).

In `tools/test_readonly_agent_guard_powershell.py`:

1. Delete the entire section from
   `print("== M0-T145 braced-variable residual: proposed-patch validation (TEMPORARY) ==")`
   through the end of its RED-on-mutant loop (the last statement before the
   final `print()` / FAILURES tail), including the `M0T145_*` constants and
   `PATCHED` build.
2. In its place, add the same rows RETARGETED at the real guard:

```python
print("== M0-T145 braced-variable assignment-fronted nested shell (fix landed) ==")
# Round-6 (M0-T145): _ps_normalize rewrites safe braced names to bare form
# before segment-splitting, so these are judged in command position and DENY.
for cmd in [
    "${x} = powershell -enc SQBFAFgA",
    "${x}=powershell -enc SQBFAFgA",
    "${a-b} = powershell -enc SQBFAFgA",
    "${a-b}=pwsh -e SQBFAFgA",
    "${x} = cmd /c whoami",
    "${env:tmp} = powershell -enc SQBFAFgA",
    "${2} = powershell -enc SQBFAFgA",
    "${a}=${b}=powershell -enc SQBFAFgA",
    "${x} = start powershell -enc SQBFAFgA",
    "${my.var} = pwsh -c Set-Content",
]:
    check(f"M0-T145 braced-assign deny: {cmd[:36]}", "DENY", ps(ROLE, cmd))
# no-FP - braced-variable reads / discards stay ALLOWED
for cmd in [
    "${x} = Get-Content README.md",
    "${a-b} = Get-Content README.md",
    "${a}=${b}=Get-Content README.md",
    "gci > ${null}",
    "${env:PATH} -split ';'",
    "Select-String -Pattern '${x} = powershell' notes.md",
]:
    check(f"M0-T145 braced no-FP allow: {cmd[:36]}", "ALLOW", ps(ROLE, cmd))
# RED-on-mutant - both new teeth are load-bearing on the REAL guard
M0T145_MUTANTS = {
    "M0-T145 mutant drops debrace wiring -> ${x} = powershell -enc slips": (
        SRC.replace('    normalized = _PS_BRACED_VAR.sub(_debrace_var, "".join(out))',
                    '    normalized = "".join(out)'),
        ps(ROLE, "${x} = powershell -enc SQBFAFgA"),
    ),
    "M0-T145 mutant narrows braced-name charset -> ${a-b} = powershell -enc slips": (
        SRC.replace(r'_PS_BRACED_VAR = re.compile(r"\$\{([A-Za-z0-9_:.\-]+)\}")',
                    r'_PS_BRACED_VAR = re.compile(r"\$\{([A-Za-z0-9_:]+)\}")'),
        ps(ROLE, "${a-b} = powershell -enc SQBFAFgA"),
    ),
}
with tempfile.TemporaryDirectory() as td:
    for name, (mutated_src, payload) in M0T145_MUTANTS.items():
        if mutated_src == SRC:
            check_static(f"{name} [mutation applied]", False)
            continue
        mpath = Path(td) / "m0t145_mutant.py"
        mpath.write_text(mutated_src, encoding="utf-8")
        got, _ = decision(payload, guard_path=mpath)
        real, _ = decision(payload)
        check_static(name, got == "ALLOW" and real == "DENY")
```

   (`SRC` is read from the real guard earlier in the file, so post-apply it
   contains the new wiring and both mutants apply. The scaffold's
   "no-regression" section 4 is intentionally NOT retargeted: every one of its
   rows already exists verbatim in the earlier sections of this suite, which
   all run against the real guard — the whole suite IS the no-regression
   proof once the fix lands.)
3. Replace the "M0-T145 (TEMPORARY proposed-patch validation)" paragraph of
   the module docstring with a plain statement that the braced-variable
   residual is fixed in the guard (`_PS_BRACED_VAR`/`_debrace_var` in
   `_ps_normalize`) and covered by deny/no-FP/RED-on-mutant rows, with
   no-regression carried by the full suite.
4. Run the documented command and require exit 0:
   `python -m pytest tools/test_readonly_agent_guard_powershell.py -q`

## 5. Evidence (this unit, worktree `wt-m0t145` @ base `29f9ee7b`)

- **Residual reproduces + proposed patch fully validated**: the suite run on
  2026-09-06 (documented command, executed via the Bash tool after the broker
  refused to classify the PowerShell-tool form) executed all rows in 18.5s
  with zero SystemExit — i.e. every check PASSED, including: the two
  "residual reproduces on UNPATCHED guard (ALLOW)" rows; "M0-T145 patch
  applies (both hunks changed the source)"; 10 patched-copy DENY rows; 6
  patched-copy no-FP ALLOW rows; 14 patched-copy no-regression rows; and
  both M0-T145 RED-on-mutant rows (mutant ALLOWs what the patched copy
  DENIES).
- **Documented-command defect found and fixed (A1 class)**: the suite defined
  no pytest-collectable test, so the packet's documented command exited **5
  ("no tests ran")** even with every check green. Fixed in this unit by
  `test_readonly_guard_suite()` + an `if __name__ == "__main__":` exit guard
  (direct-run output and exit codes unchanged). Post-fix the documented
  command reports `1 passed` / exit 0 (see checkpoint `commands_run`).
- **Guard edit denial**: verbatim broker message in §2 — the guard file is
  byte-unchanged by this unit.

## 6. Residuals after the fix lands (honest posture)

- A braced-variable assignment whose name contains characters outside
  `[A-Za-z0-9_:.-]` is not rewritten; its assignment-fronted form remains
  covered only by the compensating controls (removed Write/Edit tools +
  orchestrator-only integration), like the other documented open-ended forms
  (deep nested expansion, `GetTypeFromCLSID`, `&(gcm …)`).
- All previously documented residuals are unchanged; no existing denial is
  removed and the Bash pack is byte-identical.

## 7. Handoff state

Deliverable 1 (guard fix): **specified + validated, application blocked** on
the security-file-class broker rule — needs the orchestrator (or an
owner-standing-grant session) to apply §2+§3+§4 in one commit.
Deliverable 2 (tests): scaffold validated green pre-apply; pytest binding
fixed; §4 gives the mechanical retarget.
Deliverable 3 (this report): complete.

## 8. Second apply attempt (2026-09-06, resuming unit, same lineage)

A second unit of run lineage `persistent-local-01` was dispatched with an
orientation packet that lists `.claude/hooks/readonly_agent_guard.py` among
this task's allowed paths, and attempted the §3 docstring hunk via the native
Edit tool. The broker denied it with the **same verbatim message** as §2:

> .claude/hooks/readonly_agent_guard.py is a hook; that class is never
> baseline-AUTO and needs a standing grant or a stricter tier

This confirms the block is enforced at the broker security-file-class level,
independent of task-packet path scope: **no worker unit can apply the fix**;
it requires the orchestrator or an owner-standing-grant session, exactly as
§7 states. Consequences drawn by this unit (no further attempts, no
workaround channel used):

- The §4 test retarget was deliberately NOT performed. It must land in the
  same commit as Hunks A+B — performed alone it turns the suite red against
  the unpatched guard (by design, so the scaffold cannot outlive the fix).
  The worktree therefore stays in the validated pre-apply handoff state.
- The documented command was re-run by this unit at base `29f9ee7b`
  (worktree `wt-m0t145`, uncommitted handoff state:
  `tools/test_readonly_agent_guard_powershell.py` modified + this report):
  `python -m pytest tools/test_readonly_agent_guard_powershell.py -q`
  → exit 0, `1 passed in 18.14s`. The scaffold, both "residual reproduces
  on UNPATCHED guard" rows, the patched-copy deny/no-FP/no-regression rows,
  and both RED-on-mutant rows all remain green.

Handoff for the orchestrator (mechanical, one commit on
`task/M0-T145-brace-guard`): apply §2 Hunks A+B (constants
`M0T145_HUNK_A`/`M0T145_OLD_WIRING`/`M0T145_NEW_WIRING` in the test file are
the single source of truth), the §3 docstring bullet replacement, and the §4
test retarget + docstring update; then run the documented command and require
exit 0 with `1 passed`.

## 6. Apply record (orchestrator, 2026-09-06)

Executed exactly per the handoff above, in one change set on `task/M0-T145-brace-guard`:
Hunks A+B applied verbatim from the test-file constants (single source of truth), the §3
docstring bullet replaced, the §4 test retarget + module-docstring update applied, scaffold
removed. Producer disclosure: fix design, hunks, and validation rows by the supervised-loop
Fable worker (run persistent-local-01); mechanical apply by the orchestrator under D-032
R005/Amendment 2, because `.claude/hooks/*` is a security file class the supervisor broker
never baseline-AUTOs and standing-grant ingestion is not yet wired (follow-up noted in the
D-032 activation transaction report). Verification at apply time: the documented pytest
command exited 0 (`1 passed`; all deny/no-FP/no-regression rows + both RED-on-mutant teeth
against the REAL guard); `ruff check` clean on both files; modularity check no failures.
