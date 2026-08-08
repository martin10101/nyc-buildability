# D-010 — source-019 (owner amendment 19, VERBATIM): demonstrated hardening-script parser defect

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08 after the owner's elevated relocation session: the move + SHA
verification succeeded, but the hardening script failed PowerShell 5.1 PARSING before making any
ACL change). Frozen base at capture: `origin/main` = `c2981592051594670631a117b458347ede36e395`.

Requirement IDs added by this amendment start at `D-010-R173`; no existing source file or
requirement row (D-010-R001..R172) is edited. Relationship to source-017/018: the relocation leg
completed (new config location `C:\Program Files\SupervisorConfig\config.toml`, SHA verified);
the hardening leg is now BLOCKED on this narrowly bounded pre-activation defect fix; all standing
prohibitions (no activation, no further config moves/content changes, model_selection mutable)
remain in force.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> DEMONSTRATED PRE-ACTIVATION DEFECT — HARDENING SCRIPT PARSER FAILURE
>
> STOP activation. Do not move the controller config again and do not modify its contents.
>
> The elevated relocation completed through the post-move SHA-256 verification:
>
> C:\Program Files\SupervisorConfig\config.toml
>
> Expected and observed config SHA-256:
> 29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb
>
> The old path was moved successfully.
>
> However, ACL hardening DID NOT RUN.
>
> PowerShell failed while parsing:
> tools\agent_supervisor\harden_controller_config.ps1
>
> Parser errors occur at the interpolations:
>
> "$UnelevatedUser:(M)"
> "$UnelevatedUser:(RX)"
>
> because ':' immediately after an interpolated variable is parsed as part of the variable reference.
>
> This is a demonstrated defect in the reviewed hardening script.
>
> Treat it as a narrowly bounded pre-activation defect fix.
>
> Required remediation:
>
> 1. Do not move config.toml again.
> 2. Do not activate anything.
> 3. First perform read-only inspection of the CURRENT file and parent ACLs at:
>
>    C:\Program Files\SupervisorConfig\config.toml
>    C:\Program Files\SupervisorConfig
>
>    Report the present posture honestly. Do not assume PROTECTED.
>
> 4. Correct ONLY the PowerShell interpolation defect using an unambiguous form such as:
>
>    "${UnelevatedUser}:(M)"
>    "${UnelevatedUser}:(RX)"
>
>    at every affected occurrence.
>
> 5. Add a test that actually PARSES the entire hardening script under Windows PowerShell 5.1 semantics, so this class of parser failure cannot pass again.
>
>    The prior unelevated-execution test was insufficient because it did not catch this whole-script parsing defect.
>
> 6. Re-run the existing OS-ACL/hardening tests plus the new parse test.
>
> 7. Require independent G3 and G5 review of this delta before I execute any repaired script elevated.
>
> 8. Produce a NEW reviewed Git blob identity for harden_controller_config.ps1. The old expected blob:
>    0f01d649a64a4fcb1f96b805564cc40889d9a389
>    is now known defective and MUST NOT be used for elevation.
>
> 9. Return to me only after the corrected script is committed, reviewed, merged, and the exact new blob identity plus exact elevated rerun command are available.
>
> 10. Preserve:
>    C:\SupervisorController\model_selection.toml
>    unchanged and mutable.
>
> Do not broaden this into ACL redesign or supervisor work. This is only the demonstrated parser defect plus the missing regression test.
> One useful read-only check right now
>
> Claude should inspect the current ACLs because the file has already been moved. Do not assume it is safe merely because it is under Program Files.
>
> There are two reasons:
>
> The new parent directory likely inherited Program Files protections.
> But a same-volume NTFS move can preserve aspects of the moved file's existing security descriptor, so the file itself may still have the old writable permissions.
>
> Therefore the only honest current state is:
>
> relocated, but protection status unknown until measured.
>
> This is not a disaster. The file contents are intact, your hash verification succeeded, nothing activated, and the script failed before making partial ACL changes.
>
> Also, this is exactly why all these fail-closed checks are valuable: a parser bug that slipped through the test suite was discovered before the automation was activated, not afterward.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
