# Controller-update runbook (regenerated from merged source — M0-T072, D-017 Stage 1)

This runbook is generated from the merged M0-T072 source, not from remembered commands.
It supersedes `C:\Users\MLFLL\Downloads\nyc-zoning\CONTROLLER_UPDATE_RUNBOOK_2026-08-18.md`,
whose §5 manifest command covered the controller package but NOT the external protected
config it claimed to cover, and whose commands used CMD-style caret continuation.

Everything here is PowerShell-native (backtick continuation, no CMD carets). All paths are
resolved; verify identity before use, never trust a listing. Owner-only touchpoints are
marked **OWNER**. Everything else is executable by the authorized orchestrator under D-017.

## 1. Fixed identities

| What | Value |
|---|---|
| Live controller | `C:\SupervisorController` |
| Protected config (immutable, never modified) | `C:\Program Files\SupervisorConfig\config.toml` |
| Expected protected-config SHA-256 (raw bytes, `Get-FileHash`) | `A1F995016B541B9D69F8D78249ED4EF15563B9D7FF59B027ED3B04C1F41D1436` |
| Expected protected-config SHA-256 (LF-normalized, as the MANIFEST records it) | `4c67875b24be66c3e257270126ee8b109e69542c944f4fb18c48a5e7e3f9e75f` |
| Mutable model selection (outside the manifest by design; owner-mutable, its digest is recorded with every decision — deliberately **no pinned expected hash**: no §3–§8 step compares one, §7's doctor validates the live file against the config allowlists, and its content awaits the owner-only rows R603–R605 / M0-T137, uninterpreted here) | `C:\SupervisorController\model_selection.toml` |
| A1 worktree / journal checkout | `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063` |
| Claude executable (verify with `--version` before use) | `C:\Users\MLFLL\.local\bin\claude.exe` |
| Codex executable (verify with `--version` before use) | `C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd` |
| Backup root (never mirror-deleted; populated ONLY by §3's checked-in `-Phase backup`, one unique run directory per backup) | `C:\SupervisorBackup` |
| Controller-update source binding (immutable accepted candidate; D-024 Am. 41 + Am. 42 schema v2 — also carries the backup root, the A1 runtime-journal directory, and the evidence paths, so no long hash or runtime key is ever retyped into a command) | `tools/controller_update/source_binding.json`; evidence at `$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\` — `controller_update_evidence.json`, `controller_backup_evidence.json`, `controller_rollback_evidence.json` |

## 2. Preconditions (all read-only)

```powershell
Set-Location C:\SupervisorController
python -m tools.agent_supervisor status                # controller checkout journal: COMPLETE, no children
python -m tools.agent_supervisor status `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063   # A1 journal: PREFLIGHT, 0 pending
Get-FileHash "C:\Program Files\SupervisorConfig\config.toml" -Algorithm SHA256
Get-FileHash C:\SupervisorController\model_selection.toml -Algorithm SHA256
```

Every `status` or `stop` MUST name the intended `--checkout`; without it the command
addresses the journal of the current directory's checkout, which may be the wrong runtime.

Why `wt-m0t063` appears throughout §§2/7–9: it is the A1 unit's task worktree, and its runtime
journal — the `a1_runtime_dir` recorded in `tools/controller_update/source_binding.json`,
addressed by sha256(checkout) — is the historical A1 journal that §3 backs up and §9 proves
unchanged by the update. The doctor/status commands here deliberately address THAT journal.
The M0-T136 canary `start` is a different checkout by design: it runs with
`--checkout C:\SupervisorController` (the controller checkout's own journal). The §8
`doctor --live` probe record is per-checkout, opt-in diagnostic evidence; `start` never
consumes it, so the checkout named in §§7–8 gates nothing downstream.

Stop only if a run is live:

```powershell
python -m tools.agent_supervisor stop --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
```

## 3. Verified backup — ONE checked-in fail-closed command (non-destructive; no /MIR)

The former manual two-robocopy block is retired (D-024 Amendment 42): it captured no exit
codes (the second copy silently masked a failed first copy), enforced no uniqueness, verified
nothing, and inlined the 64-hex A1 runtime key by hand. The checked-in backup phase now does
all of it, fail closed: it verifies every source and the backup root (exact bound paths,
containment, **no junctions/symlinks/mount points anywhere** — robocopy would follow one),
creates a **unique, previously nonexistent** run directory (collision refused), copies the
live controller subtree and the A1 runtime journal with each robocopy's **raw exit code
captured immediately** (an unacceptable first code refuses before the second copy ever runs),
proves **both** backups by complete bidirectional raw SHA-256 comparison, and only then
atomically records `controller_backup_evidence.json` — run id, exact paths, the pre-update
controller identity (every file digest), both raw copy codes, and the PASS verdict. §4's
install REQUIRES that evidence. ONE owner command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1 -Phase backup
```

Expect `BACKUP VERIFIED run <timestamp-id>` with both file counts and both raw robocopy
codes; any failure prints one typed `REFUSED reason_code` line and exits nonzero with no
evidence written. `robocopy /E` never deletes at the destination, every run gets a fresh
directory, and runtime journals are never deleted in either direction. All paths — including
the A1 runtime-journal directory — come from the reviewed binding contract, never retyped.

## 4. Install the accepted controller from the frozen candidate (immutable source binding)

The copy source is pinned to the immutable accepted production candidate commit
`1489879e1f6787a9d53ed74db4524b24039e03a2` (M0-T136; D-024 Amendment 41 R608) by the
checked-in binding contract `tools/controller_update/source_binding.json`. The installer
never resolves a mutable ref — not a branch, not HEAD, not a remote-tracking name — and
refuses any binding value that is not a full 40-hex commit SHA. Before copying it
verifies, fail closed (R609): the source repository and normalized origin identity; that
the full 40-character commit exists; that its commit tree and `tools\agent_supervisor`
subtree match the accepted evidence; that every required Tranche-B module (including
the MRL launch-draft module) exists at that exact commit; and that the fresh source
worktree is DETACHED at exactly that commit and clean. It then mirrors the accepted
subtree into `C:\SupervisorController\tools\agent_supervisor` and proves the
installation by a complete bidirectional per-file SHA-256 comparison against the
accepted source (R610), recording `controller_update_evidence.json` (source
commit/tree/subtree plus every installed-file digest) at the certified activation
location.

The install is also TRANSACTIONAL (Amendment 42, R631): it refuses without §3's verified
backup evidence (`backup_evidence_missing`), re-verifies the bound backup against that
evidence (`backup_tampered`), proves the live controller unchanged since the backup was
taken (`backup_stale` — re-run §3 after any change), re-checks destination containment and
reparse-freedom immediately before the mirror, removes stale cache residue after it, and
records the exact backup identity (run id + evidence-file digest) into
`controller_update_evidence.json`. It never selects "the newest backup" — only the recorded
evidence binds a backup. Any failed check prints one typed `REFUSED reason_code` line and
exits nonzero with nothing further executed. ONE owner command, no substitution (R607/R612):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1 -Phase install
```

If it refuses `source_worktree_exists`, remove the stale source worktree and re-run:

```powershell
git -C C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack worktree remove --force C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src
```

Compare the identity the installer prints (commit, commit tree, subtree tree) against
the acceptance record (`project-control/reports/M0-T136-producer-report.md`; D-024
Amendment 41 header) before continuing. The binding contract changes only through a
reviewed commit; the negative and mutation tests live in
`tools/controller_update/ps_tests/` (run `run_ps_tests.ps1` there from a repo checkout).

## 5. Record the manifest — binding the external protected config

The former runbook's generation command produced a manifest that silently omitted the
protected config. The repaired CLI records it correctly and refuses to accept anything
less:

```powershell
Set-Location C:\SupervisorController
python -m tools.agent_supervisor record-manifest `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --out "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json"
```

The manifest is written OUTSIDE the repo tree, at the certified activation location
`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json`
(M0-T113 §1 item 10), so the certified git tree stays clean and no manifest is ever
committed into `tools\agent_supervisor\`. Create the directory first if absent
(`New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation" | Out-Null`).
The manifest stores the config under its stable logical name `config.toml` with its
digest; the absolute private path is never written into the manifest.
`model_selection.toml` stays excluded by design: a model change never invalidates the
controller — and `record-manifest` REFUSES a source file named `model_selection.toml`
or `controller_manifest.json`, so a mistyped path cannot bind the wrong file.

NOTE on digests: the manifest records the LF-NORMALIZED SHA-256 of every covered file
(so CRLF and LF checkouts agree). For the protected config that is the second value in
§1's table — it deliberately differs from `Get-FileHash`'s raw-byte value on a CRLF
file. Do not "correct" a healthy manifest because the two differ.

## 5a. Prove the recorded manifest matches the accepted source

Recording a manifest from the destination is not provenance (D-024-R610): §5 generates
it from whatever is installed, so a self-consistent but wrong installation would
certify. This step proves the recorded manifest AND the live installation both match
the exact ACCEPTED source: it re-verifies the source identity, re-compares every
installed file against the detached source worktree, cross-checks every
manifest-covered digest (LF-normalized, the manifest's own algorithm) against the
accepted source tree, and binds the result into `controller_update_evidence.json`
(R611). A manifest recorded from the wrong installed tree refuses
`manifest_digest_mismatch` / `manifest_key_set_mismatch`; an installed file changed
after §4 refuses `content_mismatch`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1 -Phase verify-manifest
```

Keep the detached source worktree until §§6–8 pass; then it may be removed with the
same `git worktree remove` command shown in §4.

## 6. Verify the controller — manifest AND external config

```powershell
python -m tools.agent_supervisor verify-controller `
  --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" `
  --config "C:\Program Files\SupervisorConfig\config.toml"
```

Expect `controller verified, including the external config.toml binding.`
`verify-controller` without `--manifest` now fails closed: nothing verified is never
reported ok. Production dispatch fails closed on: a manifest omitting `config.toml`
(`manifest_missing_config`), a missing config path, a digest mismatch, coverage
patterns that differ from the canonical set (`manifest_patterns_mismatch`), or a
stale manifest (`manifest_stale`: wrong controller version, or a recorded digest
that no longer matches the manifest's own recorded content — a SELF-CONSISTENCY
check that catches accidental or partial edits; deliberate tampering is caught by
the digests no longer matching the live tree, plus review of any manifest change).

## 7. Full doctor

```powershell
python -m tools.agent_supervisor doctor `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json"
```

Expect: `controller_manifest` ok including the external `config.toml` binding; config
ACL posture protected; model selection accepted; journal integrity ok.

## 8. Bounded live control-response probe — doctor --live, never start

`doctor --live` is the ONLY intentional bounded live control-response probe. `start` is
never used as a probe: a start that reaches the provider is a real run, not a probe.

```powershell
python -m tools.agent_supervisor doctor --live `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" `
  --claude-executable C:\Users\MLFLL\.local\bin\claude.exe
```

Expect the control-response round-trip to record VERIFIED (one disclosed allow-and-deny
round-trip, nothing forwarded to any real task).

## 9. Post-update state checks

```powershell
python -m tools.agent_supervisor status --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
python -m tools.agent_supervisor recovery-status --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
python -m tools.agent_supervisor pending-approvals --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
```

Expect: A1 still PREFLIGHT; no live children; revoked asks NOT shown as open;
limited-auto disabled. The update itself must not have changed any journal.

## 9a. Leaving a blocking state — explicit, audited owner recovery

A run that stopped in a blocking or terminal state (`PAUSED_RECOVERY`,
`WAIT_FOR_OWNER`, `HALTED`, `EMERGENCY_STOPPED`) is NOT left by `start`: leaving is
a deliberate, audited owner act, one fail-closed command per state. Each clears NO
flag, resets NO budget, and dispatches NOTHING; it transitions the state exactly
once and appends a durable audited owner-recovery record. The next `start` then
re-runs the full S11.5/preflight gate — including the live provider-CLI drift probe
— before any provider is contacted. Recovery from `HALTED`/`EMERGENCY_STOPPED` in
particular is an explicit owner decision, never automatic.

| From | Command |
|---|---|
| `PAUSED_RECOVERY` | `python -m tools.agent_supervisor clear-recovery --checkout <wt>` |
| `WAIT_FOR_OWNER` (held prompt) | `... resume-pending-prompt --approve-prompt-digest <digest> --checkout <wt>` |
| `WAIT_FOR_OWNER` (question, after answering) | `... resume-after-answer --checkout <wt>` |
| `HALTED` | `... owner-restart --checkout <wt>` |
| `EMERGENCY_STOPPED` | `... acknowledge-emergency-stop --acknowledge-emergency-stop --confirm-emergency-token <token> --checkout <wt>` |

`owner-restart` fires `HALTED -> IDLE`; it REFUSES on `EMERGENCY_STOPPED`. The
stronger `acknowledge-emergency-stop` fires `EMERGENCY_STOPPED -> IDLE` and needs
BOTH the explicit `--acknowledge-emergency-stop` flag AND the journal's
`--confirm-emergency-token` (run it once without a token to have the required token
printed), so an emergency stop is never left by a default or a script. All of these
refuse while a durable emergency stop is set (clear it with `stop --clear` first),
from any state other than their own, and while an owner ask is open, an external
effect is unreconciled, a child is unaccounted for, the provider identity drifted,
or recovery has not classified the checkpoint `SAFE_CHECKPOINT`. This is an
`orchestrator`/`OWNER` action; it is never delegated to a worker and never fires on
its own.

## 10. Rollback (exact, bound, verified)

Roll back immediately if: manifest verification fails at §6, §7, or any later startup;
doctor reports config ACL unprotected, model selection rejected, or journal integrity
error; the §8 probe does not record VERIFIED; the A1 journal state changed during the
update; or any file outside the accepted delta changed in `C:\SupervisorController`.

The former "newest directory" restore is retired (D-024 Amendment 42, R632/R633): rollback
now restores ONLY the backup bound by `controller_backup_evidence.json` — never an
auto-selected newest name, so a decoy or partial newer directory can never become the restore
source. The bound backup is first re-verified against its evidence (a tampered backup is
never restored), the destination chain is containment- and reparse-checked immediately before
the mirror, the mirror restores the **exact** pre-update file set (new modules and
partial-install residue cannot survive; stale caches are removed), the restored tree is then
proven bidirectionally digest-equal to the bound evidence, the invalidated
`controller_manifest.json` and `controller_update_evidence.json` are removed with **checked**
results, and `controller_rollback_evidence.json` is written atomically. Journals are never
touched. ONE owner command, then the doctor:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\update_controller_from_candidate.ps1 -Phase rollback
```

Expect `ROLLBACK VERIFIED to backup run <id>`; any failure is one typed
`REFUSED reason_code` line, exit nonzero, nothing further executed. Then:

```powershell
python -m tools.agent_supervisor doctor `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml
```

(Restoring an OLDER run than the bound one is a deliberate manual owner decision outside
this command — `controller_backup_evidence.json` is script-written, never hand-edited. In
that rare case copy the chosen run's tree by hand, then re-run the full §§3–8 chain from a
fresh verified backup.)

## 11. Supervised start — OBSOLETE (superseded by the MRL launch runbook)

> **OBSOLETE (M0-T136 C-B5; D-024-R586).** This section previously presented the
> legacy explicit-flag `start` command. There is now exactly ONE operator launch
> path — the manifest form documented in `docs/MRL_LAUNCH_RUNBOOK.md` — and this
> runbook deliberately presents NO `start` command any more, so a second copy can
> never drift from the live contract. Sections 1–10 (update, verification,
> rollback, recovery) remain current.

How the launch shape changed: the legacy form typed every dispatch input as a
flag, and the five load-bearing flags (`--checkout --repo --branch --worktree
--max-cycles`) had to be pinned explicitly because each silent default was a
named hazard (D-024-R372; M0-T125 D1/D14/D15). In the manifest form those inputs
— the executables, controller `--manifest`, config, model selection, task
packet, repo/worktree/branch, turn and timeout bounds, and the subagent contract
— are drafted into ONE reviewed `launch_manifest.json` by
`tools/agent_supervisor/mrl_launch_draft.py`, and `start` takes
`--launch-manifest` plus only what the manifest cannot carry: `--checkout` (the
runtime journal is addressed by `sha256(checkout)`), `--mode` (must equal the
manifest's authorized mode), and `--max-cycles 1` (a manifest binds exactly one
task to one fresh process for one cycle). The manifest is never proof: every
expected identity in it is re-observed at PREFLIGHT and any disagreement refuses
at exit 11 before a provider launches. A typed flag that disagrees with the
manifest is refused (`launch_manifest_conflict`) rather than silently preferred.
The exact drafting command, the one fenced start, the refusal and exit-code
tables, and the WAIT_FOR_OWNER recovery path live in `docs/MRL_LAUNCH_RUNBOOK.md`.

## 12. Owner touchpoints

1. **OWNER** — prompt-digest approval in supervised mode (every unit prompt; a
   digest-bound approval is never replaced by any directive text).
2. **OWNER** — UAC elevation only if hardening the controller-root ACL (optional; not
   required for shadow or supervised operation).
3. **OWNER** — any ASK-tier command the worker proposes outside the documented set.
4. Everything else in this runbook is executable by the authorized orchestrator under
   D-017 (capture: `project-control/directives/D-017-a-to-z-completion-authorization/`).

## 13. Claude Code version admission events (autoupdater control)

Source: D-024 Amendment 13 (R278/R280/R286/R287/R288), task M0-T117. The controller is
certified against ONE exact Claude CLI identity; a silent CLI auto-update breaks it (seq-30
reproduced installed `2.1.251` vs certified `2.1.248`). A Claude Code upgrade is therefore a
**deliberate admission event**, never a background event.

**Background updates stay disabled for every claude child the supervisor launches with a
CONSTRUCTED environment (R286).** Each such child is started with `DISABLE_AUTOUPDATER=1`
forced into its environment, unconditionally (`tools/agent_supervisor/process.py::claude_child_env`,
applied *after* the env allowlist and any config `extra_env`, so neither can drop or override it).
This is claude-scoped; codex children are untouched. `DISABLE_AUTOUPDATER` blocks only the
*background* update attempt — the manual `claude update` still works. **`DISABLE_UPDATES` is
deliberately NOT used** (R280): it would also block a manual, intentional update, and intentional
updates are the whole point.

Exactly which claude launches are injection-forced (every one that builds its env through
`claude_child_env`): the **worker launch** (`claude_runner.ClaudeRunner.run_unit`), the
**model-availability probe** (`claude_runner.probe_model_launch`), the **`doctor --live`
control-response probe** run inside the certification window
(`preflight.control_response_round_trip`), and the **turnover successor launch** — worker
redispatch AND orchestrator/handoff start alike
(`turnover_adapters.SupervisorLauncher._build_invocation`).

NOT injection-forced (and why they are still covered): two seams launch the CLI as a bare
`claude --version` / `claude --help` capability probe and inherit the FULL parent environment
rather than a supervisor-constructed one — `capability_probe.py::_run` (~line 99, no `env=`) and
`native_runtime.py::_run` (~line 101, `env=None`). A version/help check needs the real PATH, so
they are deliberately not env-stripped and the forced injection does not reach them; they are
covered instead by the owner **machine-scope** variable below when it is set. The precise truth:
*every claude child launched with a supervisor-constructed environment is injection-forced; the
two bare version/help probes inherit the parent environment and rely on the owner belt.*

Why the code-side injection has to exist at all (G3 Finding-4): `minimal_env`'s allowlist STRIPS
`DISABLE_AUTOUPDATER` (it is not on `DEFAULT_ENV_ALLOWLIST`), so a supervisor-constructed child
would lose even a machine-scope value through the allowlist. `claude_child_env` re-forces it for
those launches; the two belts are complementary — allowlist stripping is exactly why the code-side
injection is needed, and the bare probes are exactly why the machine-scope belt still matters.

**Admitting a new version — ordered (R287):**

1. Update the CLI on purpose (`claude update`, or install the new build).
2. Recapture the measured fixture pack at the new version.
3. Run the full recertification: fixtures, drift teeth, live probes, golden suites, gates,
   independent review, manifest binding, frozen-identity certification.
4. **Only then** repin the CLI identity with `--repin-cli-identity` and verify the new
   executable digest. Never repin first; never silently accept version drift.

**OWNER — workstation-scope machine environment variable (R288).** If the certification window
also needs `DISABLE_AUTOUPDATER=1` at Windows *machine* scope (belt-and-braces, so no terminal
anywhere can trigger a background update while certification runs), this is an OWNER action in an
**Administrator PowerShell**. An agent never sets a machine-scope environment variable itself.
The forced per-child injection above does not depend on this; machine scope is defense in depth.

```powershell
# 1. Set (Administrator PowerShell):
[Environment]::SetEnvironmentVariable('DISABLE_AUTOUPDATER', '1', 'Machine')

# 2. Verify the stored value (any NEW PowerShell window) — must print 1:
[Environment]::GetEnvironmentVariable('DISABLE_AUTOUPDATER', 'Machine')

# 3. Verify inheritance (any NEW terminal) — must print 1:
$env:DISABLE_AUTOUPDATER
```

Behavioral check: `claude doctor` reports the result of the most recent update attempt.
Already-running terminals keep their old environment and must be **restarted** to pick up the
new machine-scope value.

---

## The launch seam: worktree binding and the rotation ceiling (M0-T123, D-024 Amendment 19)

Every `start` (ordinary, recovery, or after `owner-restart`) now passes through one
pre-provider-contact enforcement seam (`tools/agent_supervisor/launch_seam.py`) that binds the
worker's working directory to the packet's isolated worktree and evaluates the 400k
context-rotation ceiling **before any provider is contacted**. This closes the reproduced cycle-2
defect, where a certified start launched the worker in the orchestrator's PRIMARY control checkout
(`…/ctl24`) instead of the packet worktree (`wt-m0t107`) and continued an over-ceiling session that
ran to 640k tokens and died with no checkpoint.

**Always pass `--worktree`** pointing at the packet's isolated worktree. If you omit it, the
worktree defaults to the checkout and the seam refuses (the run never dispatches). The seam emits
typed, fail-closed refusals — none of which clear a flag, reset a budget, or touch the audit chain:

| Refusal code | What it means | What to do |
|---|---|---|
| `cwd_primary_checkout` | the bound worktree is the primary control checkout, not the packet's isolated worktree | re-run `start` with `--worktree <the packet's isolated worktree>` |
| `cwd_mismatch` | the bound worktree is not the isolated worktree the packet declares | pass the `--worktree` that matches the packet's `worktree` field |
| `cwd_unbound` | no worktree was bound / the cwd is empty | pass `--worktree` |
| `over_ceiling_resume_forbidden` | the recorded session is at/above the 400k ceiling | none — the run sheds it and starts a fresh session at the safe seam automatically |
| `ceiling_telemetry_missing` | a resume was requested but the session's usage is unknown | none — the run fails closed rather than resuming an unmeasured session |

When a start crosses a rotation ceiling, the loop **sheds** the over-ceiling session (the old
oversized transcript receives no further events) and dispatches a fresh, distinct session in the
packet worktree — this is the normal, expected behavior for a run that grew past 400k, and needs no
operator action. A durable `rotation_pending=context_threshold` left over from a prior halt is
consumed by the same shed at the next start.

> **Note (frozen-identity recertification).** This change touches `tools/agent_supervisor/**`, so it
> invalidates the current frozen-identity certification and requires the R247 recertification window
> (Amendment 19 R330/R346) before any further live start — recapture the fixture pack, re-run the
> full recertification, then the R276 preflight, and present the exact live-start package for a
> separate owner decision (R347).
