# D-024 Amendment 42 — Controller-update transaction hardening (owner directive, 2026-09-02)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-041-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-02)
- **Channel:** Claude Code interactive prompt (verbatim below)
- **Context:** After M0-T136 and M0-T138 acceptance, the owner ordered a read-only preflight of
  the owner-run controller update (runbook §§3–8). The preflight adjudication (same session)
  proved the checked-in runbook §3 backup block is not fail-closed (no per-invocation
  `$LASTEXITCODE` capture; second robocopy masks the first) and surfaced coupled weaknesses in
  the backup → install → verification → rollback transaction. The owner then issued this
  directive authorizing ONE bounded follow-up task. The next unused task ID is M0-T139.
- **Base identity at capture:** worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
  `candidate/D-024-mrl-option-b` (local only, no upstream), HEAD `d4f55668` (M0-T138 acceptance
  commit), frozen production candidate `1489879e1f6787a9d53ed74db4524b24039e03a2` unchanged,
  working tree clean. `origin/main` is not the base of this candidate branch and was not moved.

## Verbatim owner directive

> Authorize one bounded follow-up task using the next unused task ID. Do not reopen or modify the accepted M0-T136 or M0-T138 evidence.
>
> This is a controller-update transaction hardening task—not Tranche C and not a broad supervisor refactor.
>
> Before editing, conduct one consolidated read-only trace of the complete backup → install → verification → rollback path. Report all coupled defects together, then implement them as one package. Do not stop after fixing only the first "$LASTEXITCODE" problem.
>
> Required outcomes:
>
> 1. Replace the manual §3 backup block with a checked-in, tested controller-owned backup phase—preferably inside "update_controller_from_candidate.ps1" unless a separate narrow script is demonstrably safer.
> 2. Each external process invocation must have its raw "$LASTEXITCODE" captured immediately. Null, malformed, or unacceptable codes must produce a typed refusal and an actual terminating failure—not merely print “stop.”
> 3. The first robocopy failure must never be overwritten or hidden by the second robocopy result.
> 4. Create a unique, previously nonexistent backup directory. Refuse reuse or collision.
> 5. Verify every source/destination is the exact approved path, contained within its approved root, and free of relevant junctions, symlinks, mount points, and reparse points immediately before copying.
> 6. After copying, prove both backups with complete bidirectional file inventories and raw SHA-256 digests. Missing, extra, or changed files must refuse.
> 7. Write an atomic backup-evidence record only after verification. Bind it to:
>    - timestamp/run identifier;
>    - exact source and backup paths;
>    - pre-update controller identity;
>    - both raw copy return codes;
>    - complete file sets and digests;
>    - PASS verdict.
> 8. The install must require and record the exact verified backup-evidence identity. It must not accept “the newest backup.”
> 9. Audit §10 rollback. It must restore from the explicitly bound verified backup, never auto-select an arbitrary newest directory.
> 10. Rollback must restore the exact previous controller file set. It cannot leave new modules or partial installation files behind. After restoration, prove bidirectional file-set and SHA-256 equality against the bound backup.
> 11. A partial/interrupted backup, decoy newer directory, tampered backup, wrong evidence file, missing file, extra file, first-copy failure followed by second-copy success, null exit code, junction substitution, or partial-install residue must all fail closed.
> 12. Recovery must never delete or mirror outside the exact controller subtree. Any destructive mirror operation requires immediate containment and reparse-point checks.
> 13. Keep owner commands short and mechanically sourced from checked-in scripts. Long hashes and runtime keys should come from validated binding data, not be manually retyped into conversational output.
> 14. Resolve the two recurring documentation inconsistencies in the same sweep without interpreting R603–R605:
>
> - stale informational model-selection hash wording;
> - clear explanation that "wt-m0t063" is the A1 historical-journal probe while the canary uses "C:\SupervisorController".
>   If governance prevents either clarification, record one explicit deferral instead of silently leaving misleading prose.
>
> 15. Add positive tests and independent mutants for every failure above, including real PowerShell 5.1 raw-exit behavior.
> 16. Run the full affected command-document, PowerShell, updater, governance, modularity, and relevant supervisor checks once at the frozen candidate.
> 17. Use foreground read-only reviewers where useful, but the producer must not self-accept.
>
> Allowed implementation scope must remain limited to the controller-update script, controller-update tests/mutants, the corresponding runbook/command-document checks, and necessary project-control evidence. Do not change live supervisor behavior, model selection, canary contents, R603–R605, GitHub, or provider state.
>
> No controller update, backup, rollback, live doctor, canary, push, PR, or merge.
>
> If successfully completed, submit awaiting independent G3/G4/DCV review and end with:
>
> "CONTROLLER_UPDATE_TRANSACTION_SUBMITTED"
>
> If the repair cannot remain bounded, make no partial fix and end with:
>
> "CONTROLLER_UPDATE_TRANSACTION_BLOCKED"

## Decomposition note

Decomposed into atomic requirements **D-024-R622 .. D-024-R643** (appended to
`requirements.json`; applicability `task_ids: ["M0-T139"]`, effective 2026-09-02). Forward
trace: every numbered outcome (1–17), the task-authorization paragraph, the pre-edit
consolidated-trace instruction, the scope-limitation paragraph, the execution prohibitions, and
both return tokens map to at least one row. Owner-only rows R603–R605 remain untouched and
uninterpreted (R637 explicitly forbids interpreting them during the documentation sweep and
provides the explicit-deferral alternative). No prior requirement is superseded. M0-T139 is
added to `manifest.json` scope/affected_tasks. The accepted M0-T136/M0-T138 evidence is not
reopened or modified (R622).
