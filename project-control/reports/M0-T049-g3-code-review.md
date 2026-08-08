# M0-T049 — G3 code review — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel (no
transport entities present). Reviewer: code-reviewer (read-only). Frozen review identity
`bb169e58397eb968f79451d44e5204305841410f`; code head `47a2721`. Recorded by the orchestrator
2026-08-08. One orchestrator accuracy note (content preserved untouched below): Advisory A3's
prose cites "source-019 **R182**" for the blob bar — the blob bar is **R180** (R182 is the
model_selection preservation row); the substance (pin `ca3811cd…`, never `0f01d649…`) is correct.

---

I have all the evidence I need. Every claim has been independently reproduced. Let me compile the G3 gate report.

---

# G3 Independent Code Review — M0-T049 (PowerShell 5.1 hardening-script parser defect fix)

**Directive:** D-010 source-019 (owner amendment 19, R173–R183)
**Reviewer role:** code-reviewer (read-only, ADR-005)
**Frozen review identity:** `bb169e58…` (control branch `control/M0-T049-hardening-parse-fix`); delta = task commit `47a2721` vs base `c298159`/main
**Verified working-tree HEAD at review:** `ac92558` (G2 PASS recorded)
**Method:** re-derived each requirement from source-019; reproduced parse behavior, tests, blob identity, and bounded diff on this machine (Windows 11, Windows PowerShell **5.1.26100.8875**, Python 3.11.9, unelevated).

## Content-identity verification (stable across control-plane commits)

All three reviewed files are byte-identical (same git blob) at the frozen review identity `bb169e5`, the task commit `47a2721`, and current HEAD `ac92558`. The post-task commits (`52cc544` merge, `bb169e5` evidence map, `c354f5f` submit, `a821354`/`ac92558` G2) are control-plane only; `git diff --name-only 47a2721..HEAD` shows **nothing outside `project-control/`**. Review content is not drifting.

- `tools/agent_supervisor/harden_controller_config.ps1` → blob `ca3811cd7e38a044bd0e01056e95b5028b6ce615` (I recomputed `git hash-object` on the working tree = identical). **Matches the candidate new blob exactly.**
- Base blob at `c298159` = `0f01d649a64a4fcb1f96b805564cc40889d9a389` — **exactly the barred defective blob.** The fix produces a genuinely new identity that supersedes it.

## Findings by severity

**No blocking (HIGH/MEDIUM) findings. Three LOW/advisory notes, none of which change the verdict.**

### 1. Correctness of the fix — PASS

The four sites (`harden_controller_config.ps1:130, 132, 154, 165`) change `"$UnelevatedUser:(M)"` / `"$UnelevatedUser:(RX)"` → `"${UnelevatedUser}:(M)"` / `"${UnelevatedUser}:(RX)"`. This is the correct WinPS 5.1 disambiguation: `${…}` delimits only the variable name, leaving `:(M)`/`:(RX)` as literal appended text. I verified the rendered strings in PS 5.1 with a sample value `DESKTOP-ABC\owner`:
- `"${UnelevatedUser}:(M)"` → `DESKTOP-ABC\owner:(M)`
- `"${UnelevatedUser}:(RX)"` → `DESKTOP-ABC\owner:(RX)`

These are the exact intended `icacls /grant` and `/grant:r` principal:rights arguments. **No semantic change beyond parseability**; the icacls call structure (rollback `/grant` Modify; apply `/grant:r` RX on file and dir) is unchanged.

### 2. Completeness of the defect-class sweep — PASS

Whole-file sweep `\$[A-Za-z_][A-Za-z0-9_]*:` returns only lines 40, 67, 80 — all `$env:…` (a legitimate namespace qualifier that parses correctly, confirmed by `parse_errors=0` on the fixed file). The four `$UnelevatedUser:` sites are the only occurrences of the defect class, and all four are fixed. Corroborating: reverting **all four** braces in-memory produced **exactly 4** parse errors (no more, no fewer) — the sweep and the error count agree.

### 3. Bounded-diff verification (R183) — PASS

`git diff c298159..47a2721` touches exactly three files and nothing else:
- `tools/agent_supervisor/harden_controller_config.ps1` — 4 one-token changes (`+4/-4`), no restructuring/reformatting/rename.
- `tools/test_agent_supervisor_os_acl.py` — `+43`: one new test method + one added assertion in the existing refusal test (both inside the pre-existing `HardenScriptTests`).
- `project-control/reports/M0-T049-producer-report.md` — new.

**No ACL redesign, no supervisor-code change, no `model_selection.toml` touch, no activation surface.** No scope creep (R183 satisfied).

### 4. Test quality — PASS (non-vacuous, proven RED on defect)

`test_script_parses_cleanly_under_windows_powershell_51` (`tools/test_agent_supervisor_os_acl.py:512`) parses the whole file via `[System.Management.Automation.Language.Parser]::ParseFile(...)` invoked through **`powershell.exe`** (WinPS 5.1 tokenizer, not `pwsh`), asserts the first output line equals `parse_errors=0`, and prints every error message line-prefixed on failure. I independently reproduced its behavior in-memory:
- Fixed content → `parse_errors=0`
- Reverted-defective content → `parse_errors=4` at lines **130, 132, 154, 165** (`Variable reference is not valid…`)

So the test would be **RED on the defective script** and exit-code-only checks would have stayed green — the test is non-vacuous and directly closes the gap the owner identified. The hardened refusal test (`:558`) adds `assertNotIn("variable reference is not valid", combined)`, which is sound: it ensures the non-zero exit is the script's own elevation refusal, not a parse failure masquerading as one. Platform guards (`skipUnless(IS_WINDOWS and shutil.which("powershell") …)`) are consistent with the suite's environment-conditional skip style. I confirmed the new test **RAN (not skipped)**: `HardenScriptTests` → 3 passed including the parse test.

*Advisory A1 (LOW, non-blocking):* the refusal test's negative assertion matches the English message text; on a localized Windows it would be weaker. The authoritative regression guard is the parse test (error-count based, locale-independent), so this is defense-in-depth only.
*Advisory A2 (LOW, non-blocking):* the parse test embeds the script path in single quotes inside the `-Command` string; a path containing a single quote would break it. The repo path is safe; test-only robustness nit.

### 5. Evidence reproduction — PASS

- `python -m pytest tools/test_agent_supervisor_os_acl.py -q` → **32 passed** (1.46s).
- `python -m pytest tools/test_agent_supervisor_*.py -q` → **1381 passed, 2 skipped** (104.84s) — matches the expected baseline at the reviewed content identity.
- PS version confirmed **5.1.26100.8875** (matches producer report; `powershell.exe`, not pwsh).
- R175 (honest ACL posture) corroborated: `project-control/reports/M0-T049-acl-posture-inspection.md` honestly reports the relocated file as **NOT protected** (`Authenticated Users:(M)` preserved by the same-volume NTFS move) with parent protected and contents digest `29eb765e…` intact — matching the owner's predicted mechanism, not assuming PROTECTED.

### 6. Per-requirement (producer-actionable set) — all PASS

- **R174** (fix parse defect so it parses/runs elevated): brace form at all 4 sites; independently reproduced `parse_errors=0`; unelevated run reaches its own elevation refusal (fully parsed). PASS.
- **R176** (change only those 4; audit same-class): diff = exactly 4 one-token changes; sweep confirms no other defect-class site. PASS.
- **R177** (parse regression via parser API; exit codes insufficient): implemented via `ParseFile` under WinPS 5.1; refusal test hardened. PASS.
- **R178** (RED on pre-fix; rerun suites): independently reproduced RED=4; os_acl 32 / full suite 1381+2. PASS.
- R173, R175, R179–R183 are orchestrator/owner-lane (ledger, gate adjudication, activation-package/blob sequencing, owner elevated run) — not producer code scope; R175 corroborated as above.

*Advisory A3 (orchestrator-lane, out of G3 code scope):* `project-control/directives/.../requirements.json:5723` (source-017 relocation preflight item 6) still names the **barred** blob `0f01d649…` as the "expected Git blob identity." This is expected append-only registry behavior — source-019 **R182** (`requirements.json:6357`) supersedes it and bars `0f01d649…`. When assembling the elevated-rerun/activation package, the orchestrator must pin the new blob **`ca3811cd…`**, never the stale `0f01d649…`. Flagging so a mechanical checklist read of the older field cannot re-introduce the defective blob.

## Bounded-diff statement

The task delta `c298159..47a2721` is confined to the 4 script interpolation lines, the two test additions (new parse test + refusal-test assertion), and the new producer report. No other file, no source/ACL/supervisor/activation change. R183 (no broadening) is satisfied.

## Clearance statement (R179)

From the G3 code-correctness standpoint I **clear this script for elevated execution**: the demonstrated WinPS 5.1 parser defect is fixed at all four — and only those four — sites, the entire file parses cleanly under Windows PowerShell 5.1 (independently reproduced `parse_errors=0`), the change is minimal with no semantic drift and no scope creep, and a non-vacuous regression test (proven RED=4 on the defective content) now prevents this defect class from recurring. This is one of the two required reviews; final elevated execution remains gated on the independent **G5** review and is an owner action, and the orchestrator must pin the new reviewed blob **`ca3811cd7e38a044bd0e01056e95b5028b6ce615`** (not the barred `0f01d649…`) for that run.

## Verdict

**PASS**

Advisories A1/A2 (test robustness, LOW) and A3 (orchestrator must pin the new blob in the activation package) are non-blocking and carry forward for the orchestrator; none affect the correctness or safety of the delta.

---

Relevant files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_agent_supervisor_os_acl.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T049-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T049-acl-posture-inspection.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\source-019-amendment.md`
