# M0-T108 G3 code review (VERBATIM save)

Reviewer: independent read-only `code-reviewer` (unnamed spawn), ran under the guard being
reviewed; reviewed at frozen deliverable identity `4e238b5` (HEAD `ded625a` = control-plane
records only). Returned through the agent-return channel 2026-08-27 UTC and saved verbatim below
(transport entity-decoding only; the harness neutralized `<`/`>`/`&` in transit and flagged the
output as instruction-shaped — the control tags were neutralized and the content is preserved
here as reviewer findings, not instructions).

---

Confirmed: the pre-fix guard had zero nested-shell coverage, so this task added nested-shell
detection only on the PowerShell path (asymmetric). I have everything needed. Here is my gate
report.

---

# Gate Report

- **Gate ID:** G3 (independent code review)
- **Task ID:** M0-T108 — readonly-guard PowerShell/scripting write-gap fix
- **Reviewer:** code-reviewer (independent, read-only; ran under the guard being reviewed)
- **Producer:** fable-orchestrator-session
- **Result:** **FAIL**
- **Clean environment/worktree used:** Reviewed at frozen content identity commit `4e238b5`,
  branch `control/D-024-fable-codex-loop`. Verified `git diff --name-only 4e238b5..ded625a`
  touches only control-plane records (gates/reports/state/task JSON) — deliverable content is
  frozen as claimed. Deliverable diff reviewed: `git diff 24aa061..4e238b5`.

## Acceptance criteria reviewed

Task packet `project-control/tasks/M0-T108.json` has `acceptance_scenarios: []`; the objective
enumerates items (i)–(iv). I verified each against the actual diff and by executing the guard
directly.

- (i) Matcher covers every write-capable shell tool — PARTIAL (see Defect D3).
- (ii) PowerShell mutation/redirection denylist mirroring the Bash pass, same fail-closed
  envelope — INCOMPLETE (Defects D1, D2).
- (iii) Scripting-language class treated generally, residual documented honestly — residual real
  but disclosure is incomplete (see D3, D4).
- (iv) Regression tests RED-on-mutant + reduce read-only false positives — the redirect
  false-positive fix and RED-on-mutant proofs are genuine and correct (verified).

## Directive/requirement verification

Task is in-regime (`directive_refs: [{D-024: ALL}]`). The submit snapshot (`b6165ec`) and
`M0-T108-evidence-map.json` record an **empty applicable set** ("D-024:ALL resolves empty" for
these allowed_paths, explicit empty-set row convention). Authoritative applicable-set resolution
and `verification.json` are the independent `directive-compliance-verifier`'s responsibility
(producer ≠ verifier), not G3.

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024 : ALL (resolved applicable set) | `4e238b5` | UNVERIFIABLE-by-G3 (defer to DCV) | Evidence map claims empty applicable set for allowed_paths `.claude/hooks`, `.claude/settings.json`, `tools/test_readonly_agent_guard_powershell.py`, report. G3 does not carry directive-resolution authority; DCV must confirm the empty-set resolution independently. No code-review contradiction observed. |

## Steps independently executed

1. `git diff --name-only 4e238b5..ded625a` → control-plane records only (frozen identity confirmed).
2. `git diff 24aa061..4e238b5 -- .claude/settings.json` → single matcher line
   `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit` (correct, minimal).
3. Full read of `.claude/hooks/readonly_agent_guard.py` at HEAD; analyzed `_ps_normalize`,
   `_unquoted_redirect`, `_PS_MUTATING`, `_PS_OUTFILE`, `_PS_ENCODED`, `_SCRIPT_WRITE`,
   `_shell_command_mutates`, `_main`.
4. `python tools/test_readonly_agent_guard_powershell.py` → **95 PASS, 0 FAIL, ALL CHECKS
   PASSED** (EXIT=0), including the 4 RED-on-mutant proofs.
5. `python tools/test_readonly_agent_guard.py` → **136 PASS, ALL CHECKS PASSED** (EXIT=0);
   `git diff --stat 24aa061..4e238b5 -- tools/test_readonly_agent_guard.py` empty (Bash pack
   byte-unchanged — no existing denial removed).
6. Provenance of the PowerShell tool: found a real recorded harness event
   `project-control/reports/M0-T045-r595-rehearsal/estop-run/audit.jsonl` seq 6 with
   `"tool_name":"PowerShell"`, and `ACTIVATION-2026-08-08-supervised-auto/pending-approvals-post-u1.json`
   confirming two snapshot agents wrote files via `[IO.File]` through the PowerShell tool.
   `tool_name="PowerShell"` is observed, not guessed. `M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md`
   confirms the **Bash** tool uses `tool_input.command`; no captured payload documents the
   **PowerShell** tool's input field.
7. Direct guard probes (payloads fed to the guard on stdin) to test denylist completeness and
   cross-tool laundering.

## Expected versus actual

| Payload (governed role `code-reviewer`) | Tool | Expected | Actual |
|---|---|---|---|
| `Set-Content x.txt hi` | PowerShell | DENY | DENY (control) |
| `ac notes.txt hello` (Add-Content alias) | PowerShell | DENY | **ALLOW** (D1) |
| `mi a.txt b.txt` (Move-Item alias) | PowerShell | DENY | **ALLOW** (D1) |
| `clc x.txt` (Clear-Content alias) | PowerShell | DENY | **ALLOW** (D1) |
| `[System.IO.StreamWriter]::new("C:/x.txt")` | PowerShell | DENY | **ALLOW** (D2) |
| `[IO.FileStream]::new("x",2)` | PowerShell | DENY | **ALLOW** (D2) |
| `powershell -Command "Set-Content x.txt hi"` | Bash | DENY | **ALLOW** (D3) |
| `pwsh -c …` / `cmd //c …` | Bash | DENY | **ALLOW** (D3) |
| quoted `>` reads (`python -c "print(1 if 2>1 else 0)"`) both shells | Bash/PS | ALLOW | ALLOW (fix correct) |
| `open('f')` / `open('f','r')` pure reads | Bash/PS | ALLOW | ALLOW (fix correct) |

## Evidence paths

- `.claude/hooks/readonly_agent_guard.py` (lines 174–226 `_PS_MUTATING`/`_SCRIPT_WRITE`;
  498–514 `_shell_command_mutates` — the PS-only nested-shell branch)
- `tools/test_readonly_agent_guard_powershell.py`
- `.claude/settings.json` (matcher line)
- `project-control/reports/M0-T108-guard-powershell-fix.md`
- `project-control/reports/M0-T045-r595-rehearsal/estop-run/audit.jsonl` (tool_name="PowerShell" provenance)
- `project-control/reports/M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md` (Bash `tool_input.command` shape)

## Regression/security/provenance findings

**Sound (verified, not regressed):**
- Fail-closed envelope preserved: unparseable/non-dict payload → deny; `main()` try/except →
  deny on any internal error. `_shell_command_mutates` adds no new throw path.
- Identity resolution unchanged (lead pass-through / roster-producer pass-through / named-spawn
  fail-closed) — asserted and reproduced.
- Redirect false-positive fix (`_unquoted_redirect`) is correct: quote-aware, preserves every
  unquoted-redirect denial (analyzed against the removed `_REDIRECT`; only the intended
  quoted-`>` and backslash-escaped literals are newly allowed, matching real shell semantics).
  `2>&1`, `> /dev/null`, `> $null` allowed; `1>out.txt`, `>>out` denied.
- `_ps_normalize` backtick resolution correctly reveals hidden verbs (single-quote spans
  preserved) and cannot hide a mutation (errs toward deny). RED-on-mutant for it passes.
- Best-effort `_SCRIPT_WRITE` mode-gating is correct: `open(f)`/`open(f,'r')`/`json.load(open(f))`
  stay allowed; `open(...,'w'|'a'|'x'|'+')`, `write_text/bytes`, `os.remove/…`, `shutil.rmtree`
  denied.
- Existing Bash pack unmodified (136/136); no existing denial weakened.

**Minor (advisory, not blocking):**
- `_SCRIPT_WRITE` introduces a *new* quoted-text false-positive class that cuts against objective
  (iv): a read such as `grep -rn "os.remove" tools/` or `grep "shutil.rmtree" …` now denies
  because the write idiom appears in the quoted pattern. Same "quoted-text posture" as the
  existing `_MUTATING`, so disclosed in kind, but it partially offsets the redirect-FP reduction.
  Acceptable tradeoff; worth a doc note.

## Defects

**D1 (blocking) — PowerShell write-alias denylist is incomplete; common write aliases bypass the
guard.** `_PS_MUTATING` enumerates aliases `sc ni ri rd del erase md cpi rni ren move copy` but
omits the standard write aliases `ac` (Add-Content), `mi` (Move-Item), and `clc` (Clear-Content).
A governed read-only reviewer on the PowerShell tool writes/creates a file with `ac file "text"`
(ALLOW, reproduced) or clears one with `clc file` (ALLOW). Objective (ii) explicitly names
Add-Content and Move-Item; their standard aliases defeat the control. Alias denylisting is
inherently leaky (PowerShell has many more write aliases, e.g. `rp`, `epal`), so an
enumerated-alias approach cannot mirror the Bash pass reliably.

**D2 (blocking) — .NET `::new()` writer constructors bypass the guard.** The `[IO.File|Directory]::`
static branch and the `New-Object …IO.StreamWriter/FileStream/BinaryWriter` branch do not cover
the modern PowerShell 5+ constructor form. `[System.IO.StreamWriter]::new("x.txt")` and
`[IO.FileStream]::new("x",2)` open/create files for writing and are ALLOWED (reproduced). Same
write surface the `New-Object` branch was meant to close, reached via a different syntax.

**D3 (blocking) — nested-shell laundering is defended asymmetrically; the reviewer-can-mutate
threat remains open via the Bash tool.** `_PS_MUTATING` treats `powershell|pwsh|cmd` as a
"laundering vector" and denies it — but only on the PowerShell path (`powershell=True`). Through
the **Bash** tool (the shell tool every reviewer has), `powershell -Command "Set-Content x.txt
hi"`, `pwsh -c …`, and `cmd //c …` are all ALLOWED (reproduced), letting a governed reviewer
spawn a nested shell to perform any write. This is the same class the task exists to close ("a
reviewer agent could mutate the working tree"). The pre-fix guard had no nested-shell token
(confirmed at `24aa061`), so this is a not-closed gap that the fix half-addresses on one tool
while leaving the more common one open — and it is not disclosed as a residual. Net effect:
objective (i) ("cover every write-capable shell") and the task's security goal are not achieved.

**D4 (advisory) — PowerShell tool input field (`tool_input.command`) is inferred, not evidenced.**
`tool_name="PowerShell"` is confirmed by a captured event, but no captured PreToolUse payload in
the repo documents the PowerShell tool's command parameter name. The guard reads
`tool_input.command` (the Bash convention). If the PowerShell tool names its parameter
differently, the guard reads `""` and fails **open** for every PowerShell command — the pre-fix
status quo (no regression), but the fix silently delivers nothing while the test pack (which
hard-codes `command`) stays green, masking it. This is a schema assumption under Permanent
Principle #3; it should be evidenced by one captured live PowerShell PreToolUse payload, and the
assumption disclosed in the report/docstring.

## Required rework

1. Cover the missing PowerShell write aliases (at minimum `ac`, `mi`, `clc`; audit the full
   write-alias set) — or, more robustly, match write cmdlets by their resolved verb-noun and
   reduce reliance on an enumerated alias list.
2. Cover `::new()` constructors for `StreamWriter`/`FileStream`/`BinaryWriter` (and any writer
   whose constructor opens a file), not only the `New-Object` form.
3. Apply nested-shell/laundering detection (`powershell|pwsh|cmd`, and encoded/`-Command` forms)
   on the **Bash** path too — symmetric with the PowerShell path — or explicitly document
   (docstring + report) that Bash→nested-shell is an accepted residual covered only by the
   orchestrator-only integration model. As written, the code implies nested shells are handled
   while leaving the common vector open.
4. Add RED-on-mutant regression rows for D1/D2/D3 so the teeth are proven (the current pack
   passes because it never exercises `ac`/`mi`/`clc`, `::new()`, or Bash→nested-shell).
5. Evidence the PowerShell tool's input field with one captured live PreToolUse payload; disclose
   the assumption if it cannot be captured. Orchestrator-captured evidence is acceptable here.

## Reviewer conclusion

The change is well-engineered in its correct parts: the quote-aware redirect fix is sound and
genuinely reduces the observed false positives, the fail-closed envelope and identity resolution
are preserved, the Bash pack is byte-unchanged (136/136), and the RED-on-mutant proofs are real.
However, the deliverable does **not** achieve its stated security objective. A governed read-only
reviewer can still write to the working tree through at least three trivial, static
(non-dynamic) idioms that reproduce at the frozen SHA: PowerShell write aliases `ac`/`mi`/`clc`
(D1), `[IO.StreamWriter]::new(...)`/`[IO.FileStream]::new(...)` (D2), and `powershell
-Command`/`cmd //c` launched from the Bash tool (D3). These are not the documented "dynamically
composed" residual; they are direct write vectors the denylist purports to cover, and D3 is the
very nested-shell laundering vector the code claims to defend, left open on the tool reviewers
actually use. Combined with the unevidenced PowerShell input-field assumption (D4), the control
does not yet replace the procedural stopgap.

**G3: FAIL**
