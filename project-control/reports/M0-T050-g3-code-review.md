# M0-T050 — G3 code review — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel
(transport entity-decoding only: `&amp;`→`&`). Reviewer: code-reviewer (read-only). Frozen
review identity `60acbeb2462298d05d3b86b31b8e3633cd07bda4`; script blob `9625514e…`. Recorded by
the orchestrator 2026-08-08. Note: the report references merge commit `63aad39` (the task-branch
merge into the control branch) — an intermediate commit between `b1817ff` and `60acbeb`.

---

I have completed all behavioral verification. Here is my full G3 gate report.

---

# Gate Report

- **Gate ID:** G3 (independent code review)
- **Task ID:** M0-T050
- **Reviewer:** code-reviewer (read-only)
- **Producer:** backend-engineer
- **Result:** **PASS**
- **Clean environment/worktree used:** Reviewed at frozen review identity `60acbeb2462298d05d3b86b31b8e3633cd07bda4` (control branch `control/M0-T050-dryrun-args-fix`). Material content verified byte-stable across task commit `b1817ff`, merge `63aad39`, review commit `60acbeb`, HEAD `78a9786`, and the working tree (script blob `9625514e79a34c901258975d4964529a9c02378e`; test blob `a8cc63ca01e5016cd901da176f05720585b65299`). Base/defective = `1e649a8` (script blob `ca3811cd7e38a044bd0e01056e95b5028b6ce615`). Host: Windows 11, **Windows PowerShell 5.1.26100.8875 (Desktop edition)** — the exact WinPS 5.1 target; Python 3.11.9; git 2.47.1; shell was **UNELEVATED** (the realistic unprivileged supervisor context).

## Acceptance criteria reviewed

The task carries no `acceptance_scenarios[]`; the acceptance surface is owner directive D-010 source-020 (R184–R195, verbatim at `project-control/directives/D-010-autonomous-engineering-restructure/source-020-amendment.md`). I re-derived each requirement from that source and reproduced evidence behaviorally rather than reading signatures — per the self-reflection mandate (the prior G3/G5 read the splat and wrongly called it sound).

## Directive/requirement verification

| Requirement ID | Reviewed content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-010-R184 (HOLD: config untouched/unmoved; nothing activated) | blob `9625514` @ `60acbeb` | PASS | `git diff --stat 1e649a8..b1817ff` = 3 files (script, test, report); none is `C:\Program Files\SupervisorConfig\config.toml`; no activation code in the delta. |
| D-010-R185 (root-cause; one bounded fix) | 9625514 | PASS | Independently reproduced the root cause: extracted the **defective** `Invoke-Step` in-memory (`ParseInput` on `git show 1e649a8:…`) — it is `param([string]$Exe, [string[]]$Args)` and its dry-run emits `[dry-run] icacls.exe ` / `[dry-run] takeown.exe` (arguments dropped). Fix = one bounded change; collision documented in the script comment (lines 91-95). |
| D-010-R186 (rename → `$CommandArgs`; both uses updated; no `$Args` remains) | 9625514 | PASS | Diff shows `param(...$Args)`→`param(...$CommandArgs)`, `($Args -join)`→`($CommandArgs -join)`, `& $Exe @Args`→`& $Exe @CommandArgs` (script lines 96-103). Test B2 (`test_invoke_step_has_no_args_automatic_variable_collision`) strips comments then `(?i)\$args\b` — PASS; `$CommandArgs` present. |
| D-010-R187 (positional binding preserved at every call site) | 9625514 | PASS | My own AST enumeration = **14** `Invoke-Step` call sites (lines 134-141 rollback; 150-175 apply), each `nelems=3` (command, exe var, single positional array). Rename cannot alter positional binding (position, not name, binds). Dynamic replay confirms the vector survives. |
| D-010-R188 (dynamic full-vector proof + six apply-path replay of every path/`/F`/`/A`/`/inheritance:r`/`/grant:r`/every principal) | 9625514 | PASS | My independent AST harness on the FIXED script: `[dry-run] icacls.exe C:\controller\config.toml /grant:r BUILTIN\Administrators:(F) NT AUTHORITY\SYSTEM:(F) DESKTOP-ABC\owner:(RX)` and `[dry-run] takeown.exe /F C:\controller\config.toml /A`. Tests A1/A2 + static pin B1 reproduce this; all pass. |
| D-010-R189 (RED-on-defective vs merged blob `ca3811cd`) | 9625514 vs `ca3811cd` | PASS | Independently confirmed the same harness drops every argument on the defective merged content; test C (`test_dryrun_line_is_red_on_the_defective_merged_content`) encodes assertNotIn(defective)+assertIn(fixed) and passes. `git show 1e649a8:… | git hash-object` = `ca3811cd…` (byte identity to merged blob confirmed). |
| D-010-R190 (dry-run wording cannot claim application; apply wording unchanged) | 9625514 | PASS | Completion tail now branches `if ($DryRun){ "dry run complete. NO changes were made…" } else { "apply complete.…" }` (lines 178-190). Apply-branch printed OUTPUT is byte-identical to the original string literal. Test D passes. (Rollback residual — see Defects, advisory.) |
| D-010-R191 (run affected tests; independent G3/G5) | 9625514 | PASS | Reproduced: `test_agent_supervisor_os_acl.py` = **38 passed**; full `test_agent_supervisor_*.py` = **1387 passed / 2 skipped** (exceeds the supervisor-freeze ≥1165/0-fail baseline). This G3 review is the independent code-review leg. |
| D-010-R192 (return NEW reviewed blob; `ca3811cd` + `0f01d649` barred) | 9625514 | PASS | New blob `9625514e79a34c901258975d4964529a9c02378e` verified at reviewed identity and working tree; behaviorally superior to both barred blobs. |
| D-010-R193 (return dry-run command first; real apply waits for owner) | n/a (owner/orchestrator lane) | PASS (not producer-actionable) | Sequencing is an owner-return/orchestrator action. Exact dry-run command noted in Reviewer conclusion. |
| D-010-R194 (no broadening; bounded diff) | 9625514 | PASS | Delta = exactly 3 files, two script hunks only; elevation refusal (lines 110-115) unchanged; M0-T049 `${UnelevatedUser}` brace interpolations unchanged; icacls/takeown structure unchanged; no ACL redesign. Rollback wording bounded-out & flagged. |
| D-010-R195 (full-vector visibility machine-asserted; real change sequenced behind owner dry-run) | 9625514 | PASS | Machine assertion present (A2 asserts every owner-enumerated token across the six vectors). Real-apply sequencing is owner-lane. |

## Steps independently executed

1. **Identity/scope** — `git rev-parse`/`hash-object`/`cat-file`: confirmed reviewed script blob `9625514…` at 60acbeb/HEAD/b1817ff/merge/working-tree; base defective blob `ca3811cd…`; delta = 3 files (`git diff --stat 1e649a8..b1817ff`); full script diff = two hunks only.
2. **Fixed dry-run (behavioral)** — AST-extracted `Invoke-Step` from the real script, forced `$DryRun=$true`, invoked with full vectors → full vector printed (see Expected vs actual).
3. **Defective dry-run (behavioral)** — `ParseInput` on `git show 1e649a8:…` (no file write), extracted the real `param([string[]]$Args)` function, same harness → every argument dropped.
4. **Apply-path splat (behavioral)** — forced `$DryRun=$false`, invoked `Invoke-Step "cmd.exe" @("/c","echo","ARG1","ARG2","principal:(RX)")` → real process received `ARG1 ARG2 principal:(RX)`; proves `& $Exe @CommandArgs` forwards the vector, not just `$shown`.
5. **Call-site adjudication** — AST enumeration of every `Invoke-Step` CommandAst = 14 sites, all positional-array.
6. **Suite** — `pytest tools/test_agent_supervisor_os_acl.py -v` (38 passed) and `pytest tools/test_agent_supervisor_*.py -q` (1387 passed / 2 skipped).
7. **Structural** — confirmed one `} else {` (line 183); Invoke-Step `if ($DryRun)` (line 98) has no else; unconditional `rollback complete` at line 143.

## Expected versus actual

- **Fixed, dry-run** — Expected full vector; **Actual:** `[dry-run] icacls.exe C:\controller\config.toml /grant:r BUILTIN\Administrators:(F) NT AUTHORITY\SYSTEM:(F) DESKTOP-ABC\owner:(RX)` + `[dry-run] takeown.exe /F C:\controller\config.toml /A`. MATCH.
- **Defective merged blob, dry-run** — Expected drop; **Actual:** `[dry-run] icacls.exe ` and `[dry-run] takeown.exe` (extracted body confirmed `param([string]$Exe, [string[]]$Args)`). MATCH (reproduces the owner's demonstrated defect).
- **Fixed, apply-path splat** — Expected real process receives full vector; **Actual:** `[run] cmd.exe /c echo ARG1 ARG2 principal:(RX)` then process output `ARG1 ARG2 principal:(RX)`, `LASTEXITCODE=0`. MATCH.
- **Suites** — Expected 38 / 1387 (2 skipped); **Actual:** identical. MATCH.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1` (fixed script, blob 9625514; Invoke-Step lines 90-107; wording branch lines 178-190; rollback residual line 143).
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_agent_supervisor_os_acl.py` (six new tests, lines 605-827; class `HardenScriptTests`).
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T050-producer-report.md` and `…\M0-T050-evidence-map.json`.
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\source-020-amendment.md`.

## Human-style walkthrough findings

Not a UI task. The owner-facing "walkthrough" is the dry-run transcript: an owner running the elevated `-DryRun` will now see six fully-argumented `[dry-run]` lines plus a "dry run complete. NO changes were made…" trailer that cannot be mistaken for an applied change. Verified behaviorally.

## Regression/security/provenance findings

- **No regression:** full supervisor suite 1387 passed / 2 skipped (the 2 skips pre-exist and are unrelated). Supervisor-freeze baseline (≥1165, 0 failures) satisfied; tree-hash change is expected for a defect-lane fix (rule §4).
- **Security/scope:** elevation refusal ordering unchanged (script-level refusal at 110-115 precedes any `Invoke-Step` execution); System32-absolute tool binding unchanged; no ACL semantics altered; no config touched. The fix reduces risk (the owner now sees the exact privileged commands before authorizing the real apply).
- **Provenance:** blob identities independently verified; the two prior blobs (`ca3811cd`, `0f01d649`) are demonstrated defective; the new blob is the sole cleared candidate.

## Defects

None blocking. Advisory findings (non-blocking):

- **A1 (Low, out-of-scope-by-directive):** the `-Rollback` branch still prints `"rollback complete: the prior single-account-writable posture is restored."` unconditionally (line 143), so `-Rollback -DryRun` would misread as applied — the same defect *class* the owner just caught, on the rollback path. Producer surfaced this honestly (report §9; evidence-map R194). **Leaving it is the correct bounded call for THIS task:** directive item 8 is scoped to the apply-path "apply complete" claim, item 10/"do not broaden" bounds the change, and the real apply the owner is about to run is the APPLY path (correctly worded now). Recommend a small **follow-up task** to wrap line 143 in the same `if ($DryRun)` branch (one-line symmetric fix).
- **A2 (Low):** test C's RED-on-defective anchor is `git show 1e649a8:…`; if that commit ever becomes unreachable, test C degrades to a **visible SKIP** (not a false PASS) via `self.skipTest`. Acceptable — `1e649a8` is published `main`, and tests A1/A2/B2 independently guard the live script against any vector-dropping regression regardless of history.
- **A3 (Info):** test B2's static `$Args` check is `$Args`-specific (correct — it targets the retired defect); it would not, by itself, catch a hypothetical rename to a *different* automatic name (`$input`/`$this`). The dynamic A1/A2 tests cover that case (they fail if the live function drops the vector for any reason).
- **A4 (Info):** test D's dry-run-branch isolation regex anchors on the first `if ($DryRun)` (Invoke-Step, line 98, which has no `else`), so `dry_branch` spans lines 98→183 rather than only the completion branch. It remains **sound** — the span still encloses the real completion dry-run branch (179-182), so `assertNotIn("apply complete", dry_branch)` stays protective; only the comment's precision is looser than the span.

## Required rework

None for this gate.

## Reviewer conclusion

**PASS.** The fix is behaviorally correct, not merely signature-correct. I independently reproduced (a) the defect on the merged blob `ca3811cd` (arguments dropped), (b) the fix on blob `9625514` (full vector in the `[dry-run]` display), and — going beyond the earlier reviews — (c) the apply-path `& $Exe @CommandArgs` splat forwarding the full vector to a real process. The delta is bounded to two script hunks + tests + report; elevation ordering and M0-T049 braces are untouched; the six tests are non-vacuous and genuinely RED on defective content; suites reproduce at 38 and 1387/2.

**Clearance statement (R191):** I **clear** blob `9625514e79a34c901258975d4964529a9c02378e` for the owner's personal **DRY-RUN** inspection — the dry-run now prints the complete argument vectors (every path, `/F`, `/A`, `/inheritance:r`, `/grant:r`, and every principal). This clearance is for the DRY-RUN only; the **real elevated apply additionally waits for the owner to personally see the full vectors** (R193/R195), which is an owner-lane gate I do not authorize.

**Suggested exact new dry-run command to return to the owner first (R193, owner-lane):**
`powershell -ExecutionPolicy Bypass -File tools\agent_supervisor\harden_controller_config.ps1 -ConfigPath "C:\Program Files\SupervisorConfig\config.toml" -DryRun` (run from an ELEVATED shell).

Note to orchestrator: security-reviewer is the second required reviewer (`reviewer_agents: [code-reviewer, security-reviewer]`) and the directive-compliance-verifier must record R184–R195 in `verification.json` (producer ≠ verifier) before accept. I am read-only; please record this G3 result via `tools/project_control.py gate`.
