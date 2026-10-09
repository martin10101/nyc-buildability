# D-024 Amendment 47 — Successful commissioning; M0-T140 closure; first real supervised production journey (owner directive, 2026-09-03)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-046-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-03, one message following the M0-T143
  acceptance return ending `CODEX_SCHEMA_REPAIR_READY` and the owner-typed run of
  `run_m0t143_codex_schema_repair_and_canary.ps1`)
- **Context:** the owner-run commissioning (canary-b5-02r3, 2026-09-03 00:43–00:46Z) completed
  with all ten R587 items PASS. Durable artifacts confirm the full loop: Fable-5 worker
  COMPLETED (primary `claude-fable-5`, session `44c7cce4`), Codex review returned a
  schema-valid REVISE decision (audit seq 63; `codex_decision.json` persisted; gpt-5.6-sol @
  0.146.0), supervised hold answered `deny` by the owner (audit seq 68 — the settled
  `operator_declined` close, not a defect). Journal rests at WAIT_FOR_OWNER with the ask
  answered.
- **Base identity at capture:** worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
  `candidate/D-024-mrl-option-b`, HEAD `37b2c3b611ab273db68a1b4fbbffcdc5addd0bb1`, tree clean.
  Frozen corrected candidate `3f4cee86` accepted (M0-T143) and installed live. M0-T140 still
  `claimed` (the canary authority to close under this amendment).

## Verbatim owner directive

> The owner-run M0-T143 commissioning completed with all ten R587 items PASS.
>
> Treat this as successful commissioning. Do not create another diagnostic task, rerun any
> provider canary, reinterpret `operator_declined` as a defect, or repeat completed
> verification.
>
> Now do the following in one continuous session:
>
> 1. Reconcile the live ledger and repository. Capture the existing M0-T143 live evidence and
>    complete any still-required independent G3/G4/DCV and acceptance mechanics without
>    rerunning Claude or Codex. Do not redo anything already accepted.
> 2. Close or correctly transition the claimed canary authority M0-T140 according to the
>    canonical ledger mechanics.
> 3. Record that the following production path is now live-proven:
>
>    * exact original Fable 5 pin `claude-fable-5`
>    * Claude authentication and valid WorkerResult
>    * restricted tool surface
>    * bounded subagents and over-limit denial
>    * Codex authentication and valid review decision
>    * process-tree cleanup
>    * immutable installation and manifest binding
>    * raw PowerShell exit-code preservation
>
> 4. Do not claim that GitHub push/PR/CI/merge is proven unless durable evidence already
>    proves it. State that boundary honestly.
> 5. Select one existing, genuinely ready, low-risk repository task for the first real
>    supervised production journey. Do not invent another canary or infrastructure task.
> 6. Prepare exactly one owner-run PowerShell script that:
>
>    * performs the canonical transition out of the completed canary state
>    * verifies the installed manifest and exact `claude-fable-5` pin
>    * launches one real task in supervised mode
>    * permits one Fable worker result and one Codex review
>    * preserves all existing safety boundaries
>    * performs no push, PR, merge, or deployment unless already explicitly authorized by an
>      existing owner requirement
>    * prints a concise final status and evidence paths
>
> 7. Do not execute the script. Give the owner exactly one PowerShell command, not a sequence
>    of commands.
> 8. Do not start Tranche C or another stabilization campaign. If one specific owner
>    authorization is still required for GitHub activity, identify that single decision
>    separately after preparing the local supervised journey.
>
> End with exactly `FIRST_REAL_SUPERVISED_RUN_READY`.
