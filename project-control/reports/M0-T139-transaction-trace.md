# M0-T139 consolidated read-only transaction trace (D-024-R623)

One pre-implementation trace of the complete backup → install → verification → rollback path,
conducted 2026-09-02 at HEAD `d4f55668` (M0-T138 accepted; frozen candidate `1489879e` unchanged;
live-machine facts re-measured in the same session). All coupled defects are reported together
here, clustered by root cause (CLAUDE.md rule 17), before any file was edited. Line numbers refer
to `docs/CONTROLLER_UPDATE_RUNBOOK.md` (RB) and
`tools/controller_update/update_controller_from_candidate.ps1` (PS1) at `d4f55668`.

## Cluster 1 — RB §3 backup is unverified prose (root cause: the backup step never became code)

- **D1** No per-invocation `$LASTEXITCODE` capture (RB 50–57; `LASTEXITCODE` appears nowhere in
  the runbook). The two robocopy invocations run back-to-back; the console's last exit status
  after the block is the SECOND robocopy's.
- **D2** No typed refusal and no terminating failure anywhere in §3 — prose cannot fail closed.
- **D3** Backup-directory uniqueness is not enforced: `$stamp` has second granularity,
  `New-Item -Force` succeeds on an existing directory, and `robocopy /E` merges into non-empty
  destinations — a collision silently merges two backups (RB 51–53).
- **D4** No approved-path/containment/reparse-point verification on either backup source or the
  backup destination before copying (nothing in RB 50–57 checks attributes).
- **D5** No post-copy verification of either backup — no inventories, no digests; a partial or
  interrupted backup passes silently.
- **D6** No backup evidence record — nothing binds a backup to an identity, so no downstream
  phase can require or verify "the backup that was actually taken".

## Cluster 2 — install is not transactional w.r.t. the backup (root cause: §4 has no backup precondition)

- **D7** `-Phase install` never requires a verified backup (PS1 294–341 references no backup):
  the `/MIR` destroys the only live pre-update controller tree with no proven backup required to
  exist.
- **D8** Install evidence records no backup identity (PS1 314–330), so the §10 rollback target is
  unbound to what install destroyed.
- **D9** Install checks robocopy `-ge 8` (PS1 310–312) but performs no immediate pre-mirror
  reparse-point/containment verification of the destination chain; the 2026-09-02 live scan was a
  manual session action, not an enforced check (owner classified a relevant reparse point as a
  hard stop).

## Cluster 3 — §10 rollback is unbound and lossy (root cause: rollback trusts directory ordering and additive copy)

- **D10** Rollback auto-selects the NEWEST directory under `C:\SupervisorBackup`
  (RB 245–247) — a decoy, partial, or unrelated newer directory silently becomes the restore
  source.
- **D11** `robocopy /E` restore is additive (RB 247): modules added by the failed install (e.g.,
  a new Tranche-B file) SURVIVE rollback — the restored tree is a hybrid, exactly the
  partial-install residue the owner forbids.
- **D12** No post-restore verification (no digest proof against the backup), no exit-code capture
  on the restore robocopy, no typed refusals (RB 244–254).
- **D13** `Remove-Item … -ErrorAction SilentlyContinue` (RB 248–249) swallows failures to remove
  the stale activation manifest/evidence — a rollback can "succeed" while the stale certification
  records survive.

## Cluster 4 — evidence-write atomicity (root cause: direct Out-File write)

- **D14** `controller_update_evidence.json` is written non-atomically (PS1 333, 407); a crash
  mid-write leaves a truncated/corrupt evidence file that `-Phase verify-manifest` later parses
  (PS1 395).

## Cluster 5 — documentation hazards (root cause: prose rows outlived machine state)

- **D15** RB §1 line 21 pins "Expected model-selection SHA-256 `FCBBF70F…`"; the live mutable
  `model_selection.toml` hashes `3A70343B…`. No §§3–8 command compares that hash (proven:
  `validate_selection` on the live pair returns ok=True; doctor validates allowlist membership,
  cli.py 567–582) — the row is stale, misleading prose. Resolution must not interpret
  R603–R605 (D-024-R637).
- **D16** RB §§2/7–9 name `wt-m0t063` without explaining it is the A1 historical-journal
  diagnostic target (checkout_key(wt-m0t063) = the §3 runtime dir `1854a2a4…`, proven
  programmatically), while the accepted M0-T136 canary `start` uses
  `--checkout C:\SupervisorController` (journal `9aca7075…`). Already flagged in seq-73
  follow-ups; needs an explanation, not silence.
- **D17** The 64-hex A1 runtime key is inline in an owner-typed §3 command (RB 55) — a
  retype/truncation hazard (reproduced in this session's transcript rendering). Long identifiers
  must come from validated binding data (D-024-R636).

## Fix shape (one package, per Amendment 42)

`-Phase backup` + `-Phase rollback` join `install`/`verify-manifest` in the one checked-in
operator script (shared refusal machinery, `Invoke-Native` raw-exit discipline, digest and
containment helpers — a separate script would duplicate exactly the fail-closed plumbing that
must not drift, so "inside the script" is the demonstrably safer choice per R624).
`source_binding.json` gains the backup root, the A1 runtime directory (64-hex tail validated),
and the backup/rollback evidence paths (schema v2). Install gains the backup precondition
(evidence required, backup re-verified, currency of the destination vs the backup proven, backup
identity recorded). Rollback restores only the bound backup, mirrors with the same
containment/reparse discipline, removes residue, proves digest equality, and removes stale
activation records with checked results. Both evidence writes become atomic
(temp-file + rename). RB §§1/2/3/4/10 are rewritten to short, mechanically-sourced owner
commands; D15/D16 wording is corrected without touching R603–R605. Every failure class gains a
positive ps_test and, where a single guard is behaviorally isolatable, an independent mutant;
layered-defense cases assert the changed refusal identity instead (documented per case).
