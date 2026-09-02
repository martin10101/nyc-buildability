# M0-T140 — preserved evidence: canary-continuation attempt 2 refusal (owner-typed, 2026-09-02 ~20:06Z)

Owner ran `run_m0t141_hotfix_and_canary.ps1` (SHA-256 `77705bc3…`). Result: safe fail-fast
stop at the install phase; ZERO provider contact; ten-row table printed with row 2 PASS
(reused b5-01) and rows 1/3–10 NOT-RUN; token `CANARY_PACKAGE_BLOCKED`.

## What happened (owner transcript, verbatim load-bearing lines)

- `-Phase backup` → `BACKUP VERIFIED run 20260902-160603236-6b0e0f89` (controller 196 files
  raw exit 1; runtime-a1 3 files raw exit 1), exit 0.
- `-Phase install` → `REFUSED source_worktree_exists: a source worktree already exists at
  'C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src'; remove it first: git -C
  C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack worktree
  remove --force C:\Users\MLFLL\Downloads\nyc-zoning\wt-controller-src`, exit 1 — a typed
  refusal BEFORE any destructive mirror.
- Script executed the bound transactional rollback per R681:
  `ROLLBACK VERIFIED to backup run 20260902-160603236-6b0e0f89` (196 files restored,
  digest-proven equal to the minutes-old backup of the UNCHANGED controller; raw exit 2;
  `stale records 2 removed` = the invalidated `controller_manifest.json` +
  `controller_update_evidence.json`, per runbook §10 design; `Journals were not touched`).
- Post-rollback §10 doctor: `overall: PASS` (the `controller_manifest` row ran without
  `--manifest` by design; A1 journal integrity ok, audit chain ok head 12).

## Root cause

The morning install chain (13:13, candidate `1489879e`) created the detached source
worktree `wt-controller-src`, and runbook §5a instructs keeping it until §§6–8 pass —
nothing later removes it. The installer deliberately fail-closes on a pre-existing source
worktree (`source_worktree_exists`) instead of reusing it. The script's P0 preflight did
not include this documented stale-state check — an orchestrator omission, not a product
defect and not a schema-hotfix defect. The hotfix code was never installed or exercised in
this attempt.

## State after the attempt (verified)

Controller tree = pre-update `1489879e` content (rollback restored a byte-identical copy of
the just-taken backup). Journals untouched (controller canary journal still
PAUSED_RECOVERY; A1 journal PREFLIGHT). Activation dir: `controller_manifest.json` and
`controller_update_evidence.json` removed by rollback (re-recorded by the next run's
P3/P4); fresh `controller_backup_evidence.json` + `controller_rollback_evidence.json`
present. b5-01 PASS evidence and the preserved failed `canary-b5-02` run untouched; no
`canary-b5-02r1` run dir exists. Repo `ctl24` clean; frozen candidate `2245de74` and its
binding unchanged.

## Correction (R680 deliverable repaired; no new directive requirement introduced)

`run_m0t141_hotfix_and_canary.ps1` P0 now removes a stale `wt-controller-src` up front
using the runbook §4 remedy VERBATIM (`git -C <primary repo> worktree remove --force …`),
fail-fast if removal does not stick, before the backup phase — so the install phase can no
longer refuse `source_worktree_exists` mid-transaction. Redeployed to the same path;
PS 5.1 parser 0 errors; new SHA-256
`a4a3a347690c6ea965f5bc4f0c822f1d20c10612e68c1e47a2a55d4732ee1404` (supersedes
`77705bc3…`). All other behavior unchanged (one canary-b5-02r1 provider one-shot; rollback
only on install/doctor failure; b5-01 reused).
