# D-010 — source-021 (owner amendment 21, VERBATIM): extra explicit Modify ACE survived the apply

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08 after the owner's REAL elevated apply of merged blob `9625514e…`: the
apply executed and the config SHA is unchanged, but the file's pre-existing EXPLICIT
`Authenticated Users:(M)` ACE — preserved by the earlier same-volume move — survived, because
`/inheritance:r` strips only inherited ACEs and `/grant:r` replaces grants only for the named
principals). Frozen base at capture: `origin/main` = `33b2e24be81d38d20423b91702c78d7105053b8a`.

Requirement IDs added by this amendment start at `D-010-R196`; no existing source file or
requirement row (D-010-R001..R195) is edited. Relationship to source-019/020: THIRD demonstrated
pre-activation defect in the same hardening script, each caught by the owner's fail-closed
inspection discipline before activation; blob `9625514e…` is now itself insufficient (its apply
does not remove unrelated explicit ACEs) and a new reviewed blob is required before any further
elevated apply.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> DEMONSTRATED PRE-ACTIVATION ACL DEFECT — EXTRA EXPLICIT MODIFY ACE SURVIVED APPLY
>
> STOP activation.
>
> The real elevated ACL apply executed successfully and the controller-config content SHA remained unchanged:
>
> 29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb
>
> However, the resulting FILE ACL is NOT safe.
>
> Actual post-apply file ACL:
>
> C:\Program Files\SupervisorConfig\config.toml
>     LAPTOP-M7D730QA\MLFLL:(RX)
>     NT AUTHORITY\Authenticated Users:(M)
>     NT AUTHORITY\SYSTEM:(F)
>     BUILTIN\Administrators:(F)
>     BUILTIN\Users:(RX)
>
> Actual parent ACL:
>
> C:\Program Files\SupervisorConfig
>     LAPTOP-M7D730QA\MLFLL:(RX)
>     NT AUTHORITY\SYSTEM:(OI)(CI)(F)
>     BUILTIN\Administrators:(OI)(CI)(F)
>
> The blocker is:
>
> NT AUTHORITY\Authenticated Users:(M)
>
> My ordinary account is an Authenticated Users member, so the effective ACL still permits unelevated modification of the immutable config.
>
> This violates the required controller-config boundary and must be treated as NOT_PROTECTED.
>
> Do not activate.
> Do not dispatch M2-T015 or M2-T016.
> Do not modify or move config.toml.
> Do not manually repair the ACL outside the reviewed hardening path.
>
> FIRST, from an UNELEVATED process, capture the current doctor result:
>
> python -m tools.agent_supervisor doctor --config "C:\Program Files\SupervisorConfig\config.toml" --model-selection "C:\SupervisorController\model_selection.toml" --json
>
> It should fail closed / report controller_config_acl.protected == false or NOT_PROTECTED because Authenticated Users holds M. Capture that as primary evidence.
>
> Then contract ONE narrowly bounded hardening-script defect fix:
>
> Required property:
>
> After the elevated apply, the effective FILE and PARENT DACLs must contain no non-elevated principal with any write/modify/delete/rename/replace/WriteDAC/WriteOwner right.
>
> The apply must not merely replace grants for the three intended principals while leaving unrelated explicit ACEs behind.
>
> Required adversarial regression:
>
> 1. Create a disposable test config and dedicated parent with an extra explicit:
>    NT AUTHORITY\Authenticated Users:(M)
>    on the file.
>
> 2. Run the real hardening behavior against that disposable fixture under Windows.
>
> 3. Verify the extra explicit Modify ACE is removed or otherwise cannot grant effective modification rights.
>
> 4. From an unelevated probe, require:
>    controller_config_acl / evaluator == PROTECTED.
>
> 5. Prove the intended final effective posture:
>    - Administrators: Full Control
>    - SYSTEM: Full Control
>    - ordinary supervisor identity: RX only
>    - no other non-elevated principal has dangerous rights.
>
> 6. Preserve ordinary read access.
>
> 7. Preserve config contents byte-for-byte.
>
> 8. Preserve the dedicated parent protections.
>
> 9. Make the fix idempotent.
>
> 10. Add RED-on-current-cleared-blob proof against:
>     9625514e79a34c901258975d4964529a9c02378e
>
> 11. Run G3/G5/DCV on the narrow delta and return a NEW reviewed Git blob identity before I run another elevated apply.
>
> Do not broaden this into ACL architecture or supervisor redesign.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
