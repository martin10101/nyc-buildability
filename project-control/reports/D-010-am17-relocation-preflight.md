# D-010 source-017 — controller-config relocation preflight (STOPPED at item 5, per owner rule)

Orchestrator-executed 2026-08-08 under owner amendment source-017 (R157–R167). Read-only
throughout; **no move performed, nothing created, no ACL touched anywhere**. Quiescence held for
the whole preflight: no child agents (all session subagents completed), no background writer, no
process with `SupervisorController` in its command line (Win32_Process scan), no new task dispatch.

## Outcome: STOP at preflight item 5 (a disqualifying right EXISTS through C:\)

Owner rule: "If such a right exists, or the result is ambiguous, STOP. Do not weaken or rewrite
C:\ ACLs. Return the smallest safe alternative location/design." The right exists — see item 5.
Steps 7–13 (create/move/verify) were therefore NOT executed. `C:\` was not modified.

## Preflight results

**1. Paths — CONFIRMED.** Old config `C:\SupervisorController\config.toml` exists (712 bytes,
2026-08-04). New target `C:\SupervisorConfig` does NOT exist (nothing created). Mutable
`C:\SupervisorController\model_selection.toml` exists in place (423 bytes) and was not touched.

**2. Tracking — PASS (not tracked).** In the `C:\SupervisorController` checkout:
`git ls-files --error-unmatch config.toml` → "did not match any file(s) known to git" (exit 1);
`git status --porcelain -- config.toml` → `?? config.toml` (untracked, not ignored;
`check-ignore` exit 1). Safe to move as a non-repository file.

**3. Pre-move SHA-256 — RECORDED.**
`29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb`
Re-hashed after the preflight: identical (file untouched, still in place — no move occurred).

**4. Hard-coded old-path dependencies — NONE FOUND.** Scheduled tasks (`schtasks /query /fo csv
/v`): zero rows matching `SupervisorController` or `config.toml`. HKCU/HKLM Run keys: no matching
values. Startup folder: empty (desktop.ini only). No `.ps1/.bat/.cmd` wrapper in the controller
root. `mission-control.ps1`: no config reference. All known invocations pass `--config`
explicitly per launch (pilot evidence: `--config "C:/SupervisorController/config.toml"`).

**5. Grandparent `C:\` effective ACL — DISQUALIFYING RIGHT EXISTS → STOP.** `icacls C:\`:

```
NT AUTHORITY\Authenticated Users:(AD)
NT AUTHORITY\Authenticated Users:(OI)(CI)(IO)(M)
NT AUTHORITY\SYSTEM:(OI)(CI)(F)
BUILTIN\Administrators:(OI)(CI)(F)
BUILTIN\Users:(OI)(CI)(RX)
```

Analysis: `C:\` itself grants no DeleteChild to non-admin identities (Authenticated Users hold
only AD = create-subdirectory on `C:\` itself). **But the inherit-only ACE
`Authenticated Users:(OI)(CI)(IO)(M)` propagates Modify to every newly created, inheritance-
enabled child of `C:\`** (this is the Windows-default root DACL). A freshly created
`C:\SupervisorConfig` would therefore carry `Authenticated Users: Modify` — which includes
DELETE on the folder and write/delete within it — until the hardening script strips inheritance.
Combined with `(AD)` on `C:\` (recreate a deleted name), ANY unelevated authenticated identity
could delete/rename/replace `C:\SupervisorConfig` itself during the unelevated window between
step 7 and the elevated hardening. That is squarely inside the owner's enumerated
disqualifiers ("Modify" reachable through `C:\`), so the STOP branch applies. `C:\` ACLs were
not weakened, rewritten, or touched.

**6. Hardening-script identity — VERIFIED on main + dev copy; controller copy ABSENT
(deviation, disclosed).**
- `origin/main` blob: `0f01d649a64a4fcb1f96b805564cc40889d9a389` — matches the owner-expected
  identity exactly (`git ls-tree origin/main -- tools/agent_supervisor/harden_controller_config.ps1`).
- Dev checkout working copy (`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1`): `git hash-object --path …` =
  `0f01d649a64a4fcb1f96b805564cc40889d9a389` — **byte-identical to merged main**.
- `C:\SupervisorController\tools\agent_supervisor\harden_controller_config.ps1`: **does not
  exist.** The controller checkout is pinned at the pilot-era task branch (owner-created
  2026-08-04), which predates M0-T046 (the task that added the script). Per the owner's rule, no
  elevated execution of an unverified copy: the elevated command below names ONLY the verified
  dev-checkout copy. (Alternative if preferred: update `C:\SupervisorController` to main first,
  then use its copy — a larger change, not required.)

**Doctor baseline (read-only, current paths; post-move doctor N/A since no move occurred):**
`python -m tools.agent_supervisor doctor --config "C:\SupervisorController\config.toml"
--model-selection "C:\SupervisorController\model_selection.toml" --json` → overall `ok: true`;
`controller_config` ok (codex allowlist gpt-5.6-sol/terra, claude allowlist [], default_mode
shadow); `model_selection` ok; `model_selection_allowlists` ok (every selection in its own
provider's allowlist); `controller_manifest` ok (47 files, model_selection deliberately
excluded). No safety check regresses. Config contents were not modified (R165).

## Smallest safe alternative location/design (returned per the STOP rule)

**Place the dedicated parent under a root that already denies unelevated writes, and do the
create + move + harden in ONE elevated session (zero unelevated exposure window; no `C:\` ACL
changes; exactly one UAC prompt — which the hardening already required):**

Proposed location: `C:\Program Files\SupervisorConfig\config.toml`
(`C:\Program Files` has the protected TrustedInstaller-owned DACL: Users/Authenticated Users =
Read+Execute only, no inherited Modify, unelevated creation impossible — the exposure that
disqualified `C:\SupervisorConfig` does not exist there even transiently.)

Owner-run, single ELEVATED PowerShell session (pending owner approval of the location — nothing
below has been executed):

```
New-Item -ItemType Directory "C:\Program Files\SupervisorConfig"
Move-Item "C:\SupervisorController\config.toml" "C:\Program Files\SupervisorConfig\config.toml"
powershell -ExecutionPolicy Bypass -File "C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1" -ConfigPath "C:\Program Files\SupervisorConfig\config.toml"
```

After that, the orchestrator (unelevated) verifies: post-move SHA-256 equals
`29eb765e…da1cb`; `doctor --config "C:\Program Files\SupervisorConfig\config.toml"
--model-selection "C:\SupervisorController\model_selection.toml" --json` →
`controller_config_acl.protected: true`; files the proof as committed evidence.
`model_selection.toml` stays at `C:\SupervisorController\model_selection.toml` (unelevated-
writable, outside the hardened parent) — unchanged from the owner's design.

## Prohibitions honored
No ACL hardening applied; nothing activated; M2-T015/T016 untouched; config contents unmodified;
`C:\` untouched; model_selection.toml untouched; stopped exactly at the owner's STOP branch.
