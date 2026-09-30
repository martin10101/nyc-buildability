# Controller-update package + owner runbook — 2026-08-18 (D-016 Stage 7)

Prepared read-only by the overnight orchestrator. NOTHING in this runbook has been executed:
the live controller, protected config, model selection, manifest, and runtime state are all
untouched. Every step below is an owner-present action.

## 1. Current controller SHA/version
- Location: `C:\SupervisorController` (repo-tree copy; accepted PR #221 controller).
- `CONTROLLER_VERSION = "0.4.0-phase4"` (tools/agent_supervisor/__init__.py) — same string as main,
  so identity is pinned by content, not version: the live supervisor tree is byte-equal
  (CRLF-normalized) to accepted main **except** the 7 repair files in §3.
- No `controller_manifest.json` exists in the live tree (manifest was never generated for this
  deployment; generate it as part of this update, §5).

## 2. New accepted supervisor SHA/version
- origin/main `026e7cbcd937ca29b2dcc7c8dc46be3f1477cbb0` (contains accepted M0-T070 supervisor
  repair, D-014 verified 52/52; M0-T063 packet amendment PR #225).
- Still `CONTROLLER_VERSION = "0.4.0-phase4"` — the repair did not bump the version string.

## 3. Exact files added / changed / removed (live → accepted main)
CRLF-normalized content comparison, verified 2026-08-18:

CHANGED (4) — replace with main@026e7cb copies (git blob SHAs for verification):
- tools/agent_supervisor/broker.py      e05ad18168c14ed2be5ed6bc1bc67d4974267289
- tools/agent_supervisor/cli.py         9d021fa9c3b25147456b0467c6dbae556918f7a4
- tools/agent_supervisor/durable_state.py 613e67969fe03a32cc0d16b3ff9740fd5eba3d7a
- tools/agent_supervisor/policy.py      25cf16e24f67a46bad7b82a56ed361f64562b61f

ADDED (3):
- tools/agent_supervisor/schemas/task_packet_commands.schema.json 6edec2822ff97f1db48f78171b8b2abe40504e3a
- tools/agent_supervisor/fixtures/m0_t063_documented_test_command.json 58f187ec3c666161780e84c3b12a05c76b8aa947
- tools/test_agent_supervisor_command_authority.py 39ff0d48afb9621201656ada51c00d7cb193afcb

REMOVED: none.

Copy source: a clean checkout of main@026e7cb (e.g. `C:\Users\MLFLL\Downloads\nyc-zoning\wt-t063pkt`
after `git fetch && git merge --ff-only origin/main`, or a fresh `git worktree add <dir> 026e7cb`).
Verify each copied file with `git hash-object <live path>` against the blob SHAs above
(note: `git hash-object` on a CRLF checkout differs — compare via
`git diff --no-index <main-checkout-file> <live-file>` after copy instead, expect empty or CRLF-only).

## 4. Backup destination and rollback procedure
Before touching anything (controller must be stopped, §9):
1. `robocopy C:\SupervisorController\tools\agent_supervisor C:\SupervisorBackup\2026-08-18\agent_supervisor /MIR`
2. `copy C:\SupervisorController\tools\test_agent_supervisor_command_authority.py C:\SupervisorBackup\2026-08-18\ 2>NUL` (file does not exist pre-update; this documents the add)
3. Journal backup (per-checkout runtime dirs, NOT inside any repo):
   `robocopy "%LOCALAPPDATA%\NYCBuildabilitySupervisor\1854a2a4ff3baf3d1eb39d8640e27c170958ba06ea347477f5940cc464e5d262" C:\SupervisorBackup\2026-08-18\runtime-a1 /MIR`
   (A1 journal; the `9aca…` dir is the controller-checkout pilot journal — back up the same way if desired.)
ROLLBACK = stop controller (§9 step 1), restore `C:\SupervisorBackup\2026-08-18\agent_supervisor`
over `C:\SupervisorController\tools\agent_supervisor`, delete the 3 ADDED files, delete the newly
generated `controller_manifest.json`, restart in shadow, run doctor (§10). Runtime journals are
never deleted in either direction.

## 5. Manifest regeneration and verification commands
From `C:\SupervisorController` (after copying files, before restart):
```
python -c "from tools.agent_supervisor import manifest as m; import pathlib; man=m.generate_manifest(pathlib.Path('tools/agent_supervisor')); print(m.write_manifest(man, pathlib.Path('tools/agent_supervisor/controller_manifest.json')))"
python -m tools.agent_supervisor verify-controller --manifest tools\agent_supervisor\controller_manifest.json
```
(Adjust generate_manifest args to its signature if it differs — inspect
`tools/agent_supervisor/manifest.py`; `model_selection.toml` and the manifest itself are always
excluded (`EXCLUDED_NAMES`), config.toml IS covered.) The supervisor also verifies at startup and
before every forwarded action; ANY mismatch halts the run.

## 6. Protected-config hash verification
Expected UNCHANGED before and after the update:
```
certutil -hashfile "C:\Program Files\SupervisorConfig\config.toml" SHA256
```
MUST equal `6aef12a9f60a6a64d7af77de3c071289c35dfe60977239e901df8d642c3fffde` (746 bytes,
pinned read-only 2026-08-18). Content: default_mode=shadow; codex allowed gpt-5.6-sol/terra;
claude allowed ["claude-opus-4-8"].

## 7. ACL verification
- Config file (verified 2026-08-18): `icacls "C:\Program Files\SupervisorConfig\config.toml"` →
  `MLFLL:(RX)`, SYSTEM:(F), Administrators:(F) — protected posture; confirm from an unelevated
  shell with `python -m tools.agent_supervisor doctor --config "C:\Program Files\SupervisorConfig\config.toml"`
  (expect `controller_config_acl.protected: true`; UNKNOWN is never read as protected).
- Controller root: `icacls C:\SupervisorController` currently grants
  `Authenticated Users:(M)` (inherited) — WEAK for the controller code itself. Optional hardening
  while you are present: apply the same RX-only posture to `C:\SupervisorController\tools\agent_supervisor`
  (elevated), mirroring `harden_controller_config.ps1`'s pattern. Not required for shadow.

## 8. Model-selection verification
`C:\SupervisorController\model_selection.toml` sha256
`0e2432c0a25632ccb7ef35392c64dc70bd95fac16f2e136e54801e2407a66cf4` (868 bytes): codex
review gpt-5.6-sol (fallback terra); claude model = `claude-opus-4-8` (D-010-R296/R308
Fable-exhaustion fallback, still active; revert to "" on your typed "Fable is back").
It is OUTSIDE the manifest by design — updating the controller must not touch it; doctor
validates the selection against the immutable config allowlist.

## 9. Stop / update / start sequence (owner-present)
1. STOP: `python -m tools.agent_supervisor stop` from `C:\SupervisorController` (durable pause +
   cancel wake). Verify quiescent: `python -m tools.agent_supervisor status` and
   `schedule-status`; A1 checkout journal must stay PREFLIGHT; controller-checkout journal is
   COMPLETE (last pilot done) — no live children expected (`launched_child_processes: []`).
2. BACKUP: §4.
3. COPY: the 7 files of §3 from the main@026e7cb checkout into `C:\SupervisorController`.
4. VERIFY COPY: `git diff --no-index` per file (§3).
5. MANIFEST: regenerate + verify (§5).
6. CONFIG/ACL/MODEL: §6-§8 (all must be unchanged/protected).
7. DOCTOR: §10. 8. CONTROL-RESPONSE: §11. 9. A1 state: §12. 10. Only then §13.

## 10. Post-update doctor command
```
cd C:\SupervisorController
python -m tools.agent_supervisor doctor --config "C:\Program Files\SupervisorConfig\config.toml" --manifest tools\agent_supervisor\controller_manifest.json
```
Expect: manifest VERIFIED, config acl protected: true, model selection ACCEPTED, journal integrity OK.

## 11. Live control-response verification
The A1 journal already records probe `control_response_round_trip: VERIFIED`
(2026-08-18T05:15Z, argv `-p --input-format stream-json … --permission-prompt-tool stdio`,
deny echoed). After the update, re-run the same preflight probe path (it executes automatically
in `start`'s pre-dispatch sequence; a PREFLIGHT run that reaches START_CLAUDE has re-proved it).
Do not consider the update live-verified until a fresh probe records VERIFIED post-update.

## 12. A1 status / recovery verification
```
cd C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063
python -m tools.agent_supervisor status
python -m tools.agent_supervisor recovery-status
```
Expected (verified read-only 2026-08-18): current_state PREFLIGHT; limited_auto_enabled false;
last_recovery_outcome SAFE_CHECKPOINT / safe_no_auto_resume; revoke_all recorded (3 asks REVOKED,
"operator revoke-all"); high_water_sequence 5; no launched children. With the repaired
controller, `pending-approvals` must now show 0 open (revoked asks no longer display as open —
that is defect B's fix working).

## 13. Exact supervised A1 start command
From `C:\SupervisorController` (all inputs named explicitly; supervised mode holds every prompt
at WAIT_FOR_OWNER until you approve its digest — first run intentionally without
`--approve-prompt-digest`, then re-issue with the displayed digest if you choose):
```
python -m tools.agent_supervisor start --mode supervised ^
  --manifest tools\agent_supervisor\controller_manifest.json ^
  --config "C:\Program Files\SupervisorConfig\config.toml" ^
  --model-selection model_selection.toml ^
  --claude-executable <exact path you use, e.g. C:\Users\MLFLL\AppData\Roaming\npm\claude.cmd> ^
  --codex-executable <exact codex-cli 0.146.0 path> ^
  --repo C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack ^
  --worktree C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063 ^
  --branch task/M0-T063-context-index-a1 --stage claimed ^
  --task-packet C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t063\project-control\tasks\M0-T063.json ^
  --run-id run_M0_T063_A1 --max-cycles 1
```
The packet now carries the 4 documented_test_commands (PR #225), so the worker's exact test
invocations classify AUTO:documented_test_command; every altered variant stays ASK/HARD_DENY.
Executable paths are yours to fill — the CLI refuses PATH searches by design; do not guess them.

## 14. Expected owner approval touchpoints
1. UAC elevation if you harden the controller-root ACL (§7, optional).
2. Prompt-digest approval in supervised mode (§13) — every unit prompt.
3. Any ASK-tier command the worker proposes outside the 4 documented commands + enumerated
   read-only git set (answer via `pending-approvals` + the approve/deny-by-digest verbs).
4. S16.7 owner-touch budget events; `owner_cleared_pause` if a recovery pause occurs.
5. The "Fable is back" model switch-back (separate, unrelated to this update).

## 15. Exact rollback triggers
Roll back (§4) immediately if ANY of:
- manifest verification fails at §5/§10 or at any startup after the copy;
- doctor reports config ACL not protected, model selection rejected, or journal integrity error;
- the control-response probe does not record VERIFIED post-update (§11);
- A1 journal state changed by the update process itself (it must still read PREFLIGHT before start);
- the supervised A1 run's first unit shows the pre-repair symptom (documented test command
  classified ASK:undocumented_command) — that means the copy did not take effect;
- any file outside §3's list changed in `C:\SupervisorController` during the update.
