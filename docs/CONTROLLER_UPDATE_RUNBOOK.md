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
| Expected protected-config SHA-256 | `6aef12a9f60a6a64d7af77de3c071289c35dfe60977239e901df8d642c3fffde` |
| Mutable model selection (outside the manifest by design) | `C:\SupervisorController\model_selection.toml` |
| Expected model-selection SHA-256 | `0e2432c0a25632ccb7ef35392c64dc70bd95fac16f2e136e54801e2407a66cf4` |
| A1 worktree / journal checkout | `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063` |
| Claude executable (verify with `--version` before use) | `C:\Users\MLFLL\.local\bin\claude.exe` |
| Codex executable (verify with `--version` before use) | `C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd` |
| Backup root (never mirror-deleted) | `C:\SupervisorBackup` |

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

Stop only if a run is live:

```powershell
python -m tools.agent_supervisor stop --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
```

## 3. Unique timestamped backup (non-destructive; no /MIR, no /PURGE)

```powershell
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = "C:\SupervisorBackup\$stamp"
New-Item -ItemType Directory -Force "$backup\agent_supervisor" | Out-Null
robocopy C:\SupervisorController\tools\agent_supervisor "$backup\agent_supervisor" /E /R:2 /W:2
robocopy "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\1854a2a4ff3baf3d1eb39d8640e27c170958ba06ea347477f5940cc464e5d262" `
  "$backup\runtime-a1" /E /R:2 /W:2
```

`robocopy /E` copies without deleting anything at the destination; a fresh `$stamp`
directory guarantees no earlier backup is touched. Runtime journals are never deleted
in either direction.

## 4. Copy the accepted controller delta

Derive the delta from a clean checkout of the accepted merge commit, then copy ONLY the
files that differ (CRLF-normalized comparison), and verify each copied file:

```powershell
$src = "C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t072\tools\agent_supervisor"
git -C C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t072 diff --no-index --name-only `
  C:\SupervisorController\tools\agent_supervisor $src
```

Copy each differing file with `Copy-Item`, then re-run the same `git diff --no-index`
per file and expect empty (or CRLF-only) output.

## 5. Record the manifest — binding the external protected config

The former runbook's generation command produced a manifest that silently omitted the
protected config. The repaired CLI records it correctly and refuses to accept anything
less:

```powershell
Set-Location C:\SupervisorController
python -m tools.agent_supervisor record-manifest `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --out tools\agent_supervisor\controller_manifest.json
```

The manifest stores the config under its stable logical name `config.toml` with its
digest; the absolute private path is never written into the manifest.
`model_selection.toml` stays excluded by design: a model change never invalidates the
controller.

## 6. Verify the controller — manifest AND external config

```powershell
python -m tools.agent_supervisor verify-controller `
  --manifest tools\agent_supervisor\controller_manifest.json `
  --config "C:\Program Files\SupervisorConfig\config.toml"
```

Expect `controller verified, including the external config.toml binding.`
`verify-controller` without `--manifest` now fails closed: nothing verified is never
reported ok. Production dispatch fails closed on: a manifest omitting `config.toml`
(`manifest_missing_config`), a missing config path, a digest mismatch, or a stale
manifest (`manifest_stale`: wrong controller version or an edited manifest file).

## 7. Full doctor

```powershell
python -m tools.agent_supervisor doctor `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --manifest tools\agent_supervisor\controller_manifest.json
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
  --manifest tools\agent_supervisor\controller_manifest.json `
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

## 10. Rollback (exact)

Roll back immediately if: manifest verification fails at §6, §7, or any later startup;
doctor reports config ACL unprotected, model selection rejected, or journal integrity
error; the §8 probe does not record VERIFIED; the A1 journal state changed during the
update; or any file outside the accepted delta changed in `C:\SupervisorController`.

```powershell
$backup = "C:\SupervisorBackup\<the stamp created in step 3>"
robocopy "$backup\agent_supervisor" C:\SupervisorController\tools\agent_supervisor /E /R:2 /W:2
Remove-Item C:\SupervisorController\tools\agent_supervisor\controller_manifest.json -ErrorAction SilentlyContinue
python -m tools.agent_supervisor doctor `
  --checkout C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml
```

(The step-3 `$stamp` value is echoed by step 3 when it runs; substitute the concrete
directory name printed there. Restoring copies over the live tree without deleting
anything else; journals are untouched.)

## 11. Supervised A1 start (after a fully verified update)

```powershell
Set-Location C:\SupervisorController
python -m tools.agent_supervisor start --mode supervised `
  --manifest tools\agent_supervisor\controller_manifest.json `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection model_selection.toml `
  --claude-executable C:\Users\MLFLL\.local\bin\claude.exe `
  --codex-executable C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd `
  --repo C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack `
  --worktree C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 `
  --branch task/M0-T063-context-index-a1 --stage claimed `
  --task-packet C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063\project-control\tasks\M0-T063.json `
  --run-id run_M0_T063_A1 --max-cycles 1
```

`--manifest` is now a REQUIRED dispatch input: `start` without it refuses to dispatch,
and `start` with it verifies the package tree AND the external config before any
provider contact. The packet's four `documented_test_commands` classify AUTO; altered
variants stay ASK/HARD_DENY.

## 12. Owner touchpoints

1. **OWNER** — prompt-digest approval in supervised mode (every unit prompt; a
   digest-bound approval is never replaced by any directive text).
2. **OWNER** — UAC elevation only if hardening the controller-root ACL (optional; not
   required for shadow or supervised operation).
3. **OWNER** — any ASK-tier command the worker proposes outside the documented set.
4. Everything else in this runbook is executable by the authorized orchestrator under
   D-017 (capture: `project-control/directives/D-017-a-to-z-completion-authorization/`).
