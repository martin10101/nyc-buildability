# D-024 Amendment 43 — Canary-fixture lifecycle correction (owner directive, 2026-09-02)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-042-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-02)
- **Channel:** Claude Code interactive prompt (verbatim below)
- **Context:** The owner ran the assembled M0-T136 ten-item canary block after
  CONTROLLER_VALIDATION_PASS (doctor + doctor --live exit 0). The live canary stopped safely
  before provider contact: canary-b5-01 exited 11 as expected but refused on `task_authority`
  (recover_boot classified UNSAFE_OR_DRIFTED; controller audit record sequence 13,
  2026-09-02T17:54:45.492Z), because the accepted task M0-T136 no longer confers working
  authority (`probe_task_authority` requires packet AND ledger status in
  {claimed, in_progress, awaiting_gate}; M0-T136 is `accepted` → `task_not_active`). The
  intended `launch_manifest_mismatch / clean_status` refusal was never reached; Steps C–E did
  not run; no provider was contacted. This amendment captures the owner's bounded correction:
  a dedicated canary-execution task and a corrected temporary external script.
- **Base identity at capture:** worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
  `candidate/D-024-mrl-option-b` (local only, no upstream), HEAD `21e67bb0` (M0-T139
  acceptance commit), frozen production candidate `1489879e1f6787a9d53ed74db4524b24039e03a2`
  unchanged, working tree clean, `CANARY-UNTRACKED.txt` absent. `origin/main` = `d8b3899f`
  (not the base of this candidate branch; not moved). The next unused task ID is M0-T140.

## Verbatim owner directive

> The live canary stopped safely before provider contact.
>
> Actual result:
>
> * canary-b5-01 returned the expected safety exit 11;
> * but it refused on `task_authority`, not the intended `launch_manifest_mismatch / clean_status`;
> * M0-T136 is already accepted, so it cannot serve as an executable canary task;
> * the controller entered PAUSED_RECOVERY;
> * no provider was contacted;
> * Steps C–E were not run.
>
> Treat this as one bounded canary-fixture lifecycle correction. Do not modify or reinstall controller production code, reopen M0-T136/M0-T138/M0-T139, push, merge, or interpret R603–R605.
>
> Complete the correction in one session:
>
> 1. Confirm `CANARY-UNTRACKED.txt` was removed and the repository is clean.
> 2. Preserve the failed canary result as evidence.
> 3. Trace the exact `task_authority` requirements and the canonical recovery procedure.
> 4. Check whether an existing unaccepted task is explicitly designated as the canary execution vehicle. Use it only if its recorded scope says so without interpreting R603–R605.
> 5. Otherwise create and claim one minimal, dedicated, read-only canary-execution task using the next unused task ID under the already-authorized R587–R589 canary scope. Never reopen an accepted task.
> 6. Ensure that task remains in the exact runnable/claimed state required by `task_authority` until the live canary finishes.
> 7. Regenerate the canary manifest against that dedicated task and the current clean repository HEAD.
> 8. Replace only the temporary external canary script—not the accepted controller installation or accepted M0-T136 package.
> 9. Include canonical recovery from the current PAUSED_RECOVERY state. Do not delete or hand-edit runtime state.
> 10. After b5-01 creates the deliberate dirty file, prove the refusal reaches `launch_manifest_mismatch / clean_status`, receives exit 11, and contacts no provider.
> 11. After removing the dirty file, perform whatever canonical safe recovery/revalidation is required before b5-02. Do not assume PAUSED_RECOVERY clears itself.
> 12. Then run exactly the accepted b5-02 parking/approval flow and exactly one provider one-shot.
> 13. Retain complete PASS/FAIL handling for all ten R587 items.
> 14. Parse the saved script with Windows PowerShell 5.1, verify every item 1–10 has reachable PASS and FAIL handling, and have one foreground read-only subagent independently check task authority, recovery ordering, and commands.
> 15. Do not execute the corrected canary script yourself.
>
> This message explicitly authorizes creating the minimum dedicated control-plane canary task and updating the temporary external execution script. It does not authorize production-code changes or R603–R605 decisions.
>
> Return only:
>
> * `CANARY_EXECUTION_READY` or `CANARY_EXECUTION_BLOCKED`
> * dedicated task ID and status;
> * current repository HEAD;
> * runtime recovery method included;
> * external script path and SHA-256;
> * PowerShell parser and independent-review results;
> * exactly one command for me to execute.
>
> Do not begin another broad audit or implementation tranche.

## Decomposition

Requirements D-024-R644 through D-024-R663 (see `requirements.json`), all bound to task
M0-T140, amendment_sequence 43. Forward trace: preamble/scope sentence → R644; the
prohibition sentence → R645; numbered items 1–15 → R646–R660 in order; the authorization
paragraph → R661; the return-items list → R662; the closing prohibition → R663. No source
sentence is left unmapped; no requirement is invented beyond the source text.
