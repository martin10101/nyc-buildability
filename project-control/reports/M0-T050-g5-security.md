# M0-T050 — G5 security review — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel (transport
entity-decoding only: `&amp;`→`&`, `&lt;`→`<`, `&gt;`→`>`). Reviewer: security-reviewer
(read-only). Frozen review identity `60acbeb2462298d05d3b86b31b8e3633cd07bda4`; script blob
`9625514e…`. Recorded by the orchestrator 2026-08-08. CORRECTION NOTE: the first committed
version of this file (commit 99fe467) was accidentally truncated to the header by a transcript-
extraction error; this commit restores the full verbatim content. The G3/G5 gate records and
verdicts are unaffected (the verdict and content came through the agent-return channel).

---

I have completed all independent verification. Every claim has been reproduced under real Windows PowerShell 5.1 (5.1.26100.8875) at the frozen content identity. Here is my G5 report.

---

# Gate Report

- **Gate ID:** G5 (security)
- **Task ID:** M0-T050 (in-regime; directive D-010, source-020, R184–R195)
- **Reviewer:** security-reviewer (read-only)
- **Producer:** backend-engineer
- **Result:** **PASS** (with 3 LOW advisories; none blocking this gate or the owner's dry-run)
- **Clean environment/worktree used:** Reviewed control branch `control/M0-T050-dryrun-args-fix` at HEAD `78a9786`; working tree clean for the reviewed files; content identity re-verified below. Host: Windows 11, Windows PowerShell **5.1.26100.8875**, Python 3.11.9, git present, unelevated (IsAdmin=False).

## Content identity (frozen, independently confirmed)

- Fixed script blob at HEAD **and** at task commit `b1817ff` = `9625514e79a34c901258975d4964529a9c02378e` (the candidate). Test blob = `a8cc63ca01e5016cd901da176f05720585b65299` at both. Working tree clean.
- Defective merged blob (`1e649a8`/main) = `ca3811cd7e38a044bd0e01056e95b5028b6ce615` (barred). Prior defective `0f01d649` (source-019) also barred.
- Implementation delta `1e649a8..HEAD` = exactly `harden_controller_config.ps1` + `test_agent_supervisor_os_acl.py`. All other changed files are orchestrator/control-plane artifacts (directive capture, G0/G2 gate records, state.json) — no producer scope creep.

## Self-reflection on the prior G5 miss (required)

My M0-T049 G5 wrote, of `Invoke-Step`: "`& $Exe @Args` with `[string[]]$Args` — pre-tokenized array elements splatted to the call operator … Confirmed: arrays of pre-tokenized args, not a shell string. No finding." That security conclusion (no shell injection) was correct in isolation, but it was a **signature-level reading** that never exercised the code, and so it missed that `$Args` is a WinPS 5.1 **automatic variable**: a `param([string[]]$Args)` does not receive the caller's bound value, leaving **both** `$shown` and the splat empty. This review executed every relevant path instead of reading it. Recorded lesson: for PowerShell (and any language with implicit/automatic identifiers), every parameter/variable name must be checked against the reserved/automatic set **and** exercised at runtime.

## Directive/requirement verification (each ID re-derived from source at blob `9625514`)

| Requirement ID | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-010-R184 (HOLD: config untouched/unmoved, contents unchanged, nothing activated) | live + blob 9625514 | PASS | `Get-FileHash` of `C:\Program Files\SupervisorConfig\config.toml` = `29EB765EABCE05B81DCBEA33FD4D28800479596E9B23FD4D4FA334F6EE7DA1CB` (exact match, read-only). ACL still grants `Authenticated Users: Modify` → **not protected → nothing activated**. Delta touches no config path. |
| D-010-R185 (treat as ONE bounded pre-activation defect; root-cause the automatic-`$args` collision) | 9625514 | PASS | Reproduced the collision in an isolated 2-function scope: `param $Args` → `[bad ] icacls.exe ` (empty); `param $CommandArgs` → `[good] icacls.exe C:\controller\config.toml /inheritance:r`. Documented in the in-code comment at Invoke-Step. |
| D-010-R186 (rename param to `$CommandArgs`; use in `$shown` join and `& $Exe @CommandArgs`) | 9625514 | PASS | Diff shows `param([string]$Exe, [string[]]$CommandArgs)`, `$shown = "$Exe " + ($CommandArgs -join " ")`, `& $Exe @CommandArgs`. No `$Args` remains in code (test B2 + my grep). |
| D-010-R187 (inspect EVERY invocation; prove full vector retained end-to-end) | 9625514 | PASS | AST count = **14** call sites (producer honestly flags directive's "12"). Dynamically replayed all 6 apply vectors + 2 rollback-grant + single-arg display through the real extracted `Invoke-Step`; every element retained. |
| D-010-R188 (WinPS 5.1 test proving FULL dry-run vectors incl. takeown /F …/A, icacls /inheritance:r, /grant:r with Administrators+SYSTEM+unelevated RX for file and parent) | 9625514 | PASS | Independently replayed the six apply vectors: every path, `/F`, `/A`, `/inheritance:r`, `/grant:r`, `BUILTIN\Administrators:(F)`/`(OI)(CI)(F)`, `NT AUTHORITY\SYSTEM:(F)`/`(OI)(CI)(F)`, and `<user>:(RX)` printed in full. Tests A1/A2 assert the owner's enumerated minimum. |
| D-010-R189 (test FAILS on merged defective blob ca3811cd) | 9625514 vs ca3811cd | PASS | Reproduced defective content via `git show 1e649a8:… | ParseInput`: `[dry-run] icacls.exe` (all args dropped). Test C asserts `assertNotIn` on defective / `assertIn` on fixed. |
| D-010-R190 (dry-run completion wording cannot claim application; apply wording unchanged) | 9625514 | PASS | Apply-path completion is now `if ($DryRun) {"dry run complete. NO changes were made…"} else {"apply complete.…"}`. Dynamic dry-run prints the "NO changes were made" branch; apply text byte-unchanged. Test D asserts branch + absence of "apply complete" in the dry branch. |
| D-010-R191 (run affected tests; independent G3 + G5 on the delta) | process | PASS (this G5) | os_acl 38 passed; full supervisor suite **1387 passed / 2 skipped / 0 failures** (reproduced here). G3 is the code lane; this is the independent G5. |
| D-010-R192 (return NEW reviewed blob; ca3811cd barred) | 9625514 | PASS | New blob `9625514e79a34c901258975d4964529a9c02378e`; `ca3811cd` and `0f01d649` recorded defective and barred. |
| D-010-R193 (return exact new DRY-RUN command FIRST; owner personally inspects full vectors before any real apply) | process | PASS (owner/orchestrator lane) | Exact command supplied in "Pre-apply conditions" below; sequencing is honored by returning it ahead of any apply authorization. |
| D-010-R194 (do not broaden into other supervisor/ACL redesign) | 9625514 | PASS | Delta = Invoke-Step rename + wording branch + 6 tests + report. Rollback-path wording correctly left unchanged (see L-1). No ACL structure, principals, or rights changed. |
| D-010-R195 (standing rule: next dry-run must visibly show every path, /F, /A, /inheritance:r, /grant:r, every principal; only then run the real change) | 9625514 | PASS | Machine-asserted by A1/A2; visibility reproduced here; the real apply remains sequenced behind the owner's personal full-vector dry-run. |

## Security charge — findings for the record

**1. Behavioral adjudication — was the defective real apply dangerous or merely broken?**
Reproduced both blobs. Defective (`ca3811cd`): dry-run emits `[dry-run] icacls.exe` (empty argv). The real apply path (`& $Exe @Args`) would splat an **empty** array. The first apply command is `takeown` (line 150). I ran `takeown.exe` and `icacls.exe` with no arguments: exit codes **1** and **160** respectively, and both only print usage/error and **modify nothing**. Because `$LASTEXITCODE -ne 0` throws under `$ErrorActionPreference=Stop`, the sequence would **abort on the first takeown before any icacls ran**. Verdict for the record: **the defective real apply would have been MERELY BROKEN — a no-op that aborts on the first command — NOT dangerous** (no ownership transfer, no ACL change, no config modification, no security weakening). The genuine risk was to the **dry-run verification contract**: the owner approves the real apply by inspecting the dry-run, and a dry-run that hid the argv *and* printed "apply complete." would have defeated that inspection. The owner correctly caught it; the fix restores the contract.

**2. Fix safety — any behavioral difference beyond restoring the vector? other automatic-variable hazards?**
No difference beyond restoring the vector. Verified: binding (positional exe→`$Exe`, array→`$CommandArgs` unchanged; all 14 sites retain), splatting (`& $Exe @CommandArgs` emits the full vector in run-mode too), escaping (array-splat to call operator, no shell — unchanged from M0-T046), empty-array display case (`@()` → `[dry-run] foo.exe ` with trailing space, identical to before). `$CommandArgs` is **not** an automatic/preference variable. Swept every param and assignment target in the file: `$ConfigPath, $UnelevatedUser, $Rollback, $DryRun, $Exe, $CommandArgs, $fileItem, $file, $dir, $System32, $Icacls, $Takeown, $identity, $principal, $shown` — **none collide** with an automatic variable. `$ErrorActionPreference` is an intended preference assignment; `$LASTEXITCODE` is only read. **No residual `$input/$this/$error/$host/$matches/$args`-class shadowing remains.**

**3. Failure containment — fail-closed chain intact.**
Verified on the fixed script (run mode): `cmd /c exit 3` → throws `command failed (exit 3): cmd.exe /c exit 3` and aborts; `cmd /c exit 0` proceeds. Partial-apply semantics are unchanged from the reviewed M0-T046 behavior; the rename does not touch the `$LASTEXITCODE` check.

**4. Dry-run contract (R190/R195) — side-effect-free end-to-end.**
The only external-process execution in the file is `& $Exe @CommandArgs` (line 103), and it is the file's **only** use of the `&` call operator. It sits behind `if ($DryRun) { Write-Host …; return }` inside `Invoke-Step`. Every one of the 14 tool invocations routes through `Invoke-Step`; `$Icacls`/`$Takeown` are never invoked directly. Therefore `$DryRun` gates **every** execution and no call site bypasses the guard. Completion wording branch verified: dry-run cannot claim application.

**5. Regression-test sufficiency.**
A1/A2 (dynamic full-vector replay against the **real** extracted function) + B2 (no `$Args`, uses `$CommandArgs`) durably close the argument-drop class: a future re-drop inside `Invoke-Step` turns A1/A2 RED and B2 RED. B1 (static call-site fidelity, exact-array match) catches a drop at a call site. C is the RED-on-defective proof; D is the wording proof. All 6 GREEN on the fix; C proven RED on defective (reproduced here). Prior L-1 (skip-when-no-powershell): the ubuntu `api` leg (`working-directory: services/api`) does not collect `tools/` tests at all; the dedicated **`supervisor-bridge` leg runs `pytest tools/test_agent_supervisor_*.py` on `windows-latest`**, where `powershell.exe` and `git` are present, so A1/A2/B1/B2/(C) **execute, not skip** — L-1 is mitigated for these tests.

**6/7. Interim risk + boundary compliance.** Config untouched (SHA exact match, still not protected); no activation; no broadening; SHADOW-ONLY posture intact.

## Findings / Defects

- **CRITICAL: none. HIGH: none. MEDIUM: none.**
- **LOW L-1 (rollback-path dry-run wording; = producer's bounded-out flag).** `-Rollback` prints `"rollback complete: the prior single-account-writable posture is restored."` unconditionally (line 143), so `-Rollback -DryRun` would falsely read as applied — the same misleading-wording class R190 fixed on the apply path. **Adjudication:** side-effect-free (all rollback `Invoke-Step` calls respect `$DryRun` — verified), not on the imminent apply path, and rollback is irrelevant while the config is still unprotected. Fixing it here would violate R194 ("do not broaden … do not restructure anything else"), so leaving it is **correct**; **deferring is safe.** Recommend a bounded follow-up task to branch the rollback tail on `$DryRun`. Not blocking.
- **LOW L-2 (carry-forward, operational).** `-UnelevatedUser` defaults to `$env:USERDOMAIN\$env:USERNAME`. If the ordinary supervisor runs as a different account, the default grants RX to the wrong principal. This fix now makes the principal **visible in the dry-run**, so the owner can verify it — resolve by inspection before the real apply. Not blocking.
- **LOW L-3 (test-durability nuance).** Test C depends on `git show 1e649a8` reachability; under a shallow `windows-latest` checkout it may `skipTest` rather than run. The forward-looking guards (A1/A2/B1/B2) do not depend on git and execute on `windows-latest`, so durable protection against a future re-drop is CI-enforced; C is a historical proof (independently reproduced here). Also informational: B1 uses a subset assertion and does not forbid a *new* tool call that bypasses `Invoke-Step` (none exists today — verified). Not blocking.

## Required rework
None for this gate. L-1/L-2/L-3 are advisory; L-1 should become a bounded follow-up task rather than an expansion of M0-T050.

## Clearance statement (for the owner's DRY-RUN of blob `9625514e…`)
I **clear blob `9625514e79a34c901258975d4964529a9c02378e` for the owner's elevated `-DryRun` inspection.** The dry-run is provably side-effect-free, emits the complete argument vector for all six apply-path commands, and its completion wording can no longer claim application. Clearance for the **real** elevated apply remains conditioned on the owner's personal full-vector dry-run inspection plus the pre-apply conditions below (and G3 PASS + merge so the elevated run uses the merged blob).

## Pre-apply conditions (must all hold before the REAL elevated apply)
1. Exact **new dry-run command** (run FIRST, from an **ELEVATED** WinPS — the elevation refusal precedes DryRun by design):
   `powershell -ExecutionPolicy Bypass -File "tools\agent_supervisor\harden_controller_config.ps1" -ConfigPath "C:\Program Files\SupervisorConfig\config.toml" -DryRun`
   (if the unelevated supervisor runs as a different account, add `-UnelevatedUser "<DOMAIN\account>"` — L-2).
2. Owner personally confirms all six lines show every path, `/F`, `/A`, `/inheritance:r`, `/grant:r`, and every principal (`BUILTIN\Administrators`, `NT AUTHORITY\SYSTEM`, `<user>:(RX)`), plus the "dry run complete. NO changes were made" wording — **not** "apply complete." (R193/R195).
3. Pre-run config SHA re-verify == `29EB765E…`; post-run SHA unchanged.
4. Only the merged blob `9625514e…` is elevated; `ca3811cd` and `0f01d649` stay barred (R192).
5. After the real apply, verify from an **unelevated** shell that the OS-ACL verdict is PROTECTED.

## Boundary statement
Config `C:\Program Files\SupervisorConfig\config.toml` untouched and unmoved: contents SHA re-verified `29EB765E…` (exact match, read-only), file still `Authenticated Users: Modify` (not protected → nothing activated). No activation, no broadening, no ACL/principal/right changes. SHADOW-ONLY posture intact. Reviewer performed no writes outside `.claude/agent-memory/security-reviewer/` and ran no control-plane/git/gh write commands.

---

**VERDICT: PASS** (3 LOW advisories: L-1 rollback-path dry-run wording — safe to defer, recommend bounded follow-up; L-2 `-UnelevatedUser` default — verify via dry-run; L-3 test-durability nuance. None blocks this gate or the owner's dry-run.)

Key file paths:
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1` (blob `9625514e…`)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_agent_supervisor_os_acl.py` (blob `a8cc63c…`)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T050-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\source-020-amendment.md`
