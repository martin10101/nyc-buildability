# D-010 — source-020 (owner amendment 20, VERBATIM): dry-run dropped all command arguments

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08 after the owner's ELEVATED `-DryRun` of the merged M0-T049 script:
the pre-run SHA matched, but every dry-run line printed only the executable with NO arguments —
the `param([string[]]$Args)` parameter collides with PowerShell's automatic `$args` variable, so
the argument vector is dropped). Frozen base at capture: `origin/main` =
`1e649a8ed37599c9e07d6b07b47404b30c5e91c5`.

Requirement IDs added by this amendment start at `D-010-R184`; no existing source file or
requirement row (D-010-R001..R183) is edited. Relationship to source-019: second demonstrated
pre-activation defect in the same script, caught by the owner's personal dry-run inspection
BEFORE any privileged command touched the ACLs; the source-019 fix (brace interpolations) remains
correct and is unaffected; blob `ca3811cd…` (which source-019 produced) is now itself
demonstrated defective and barred from elevation.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> DEMONSTRATED DEFECT — DRY-RUN DROPPED ALL COMMAND ARGUMENTS
>
> STOP. Do not activate and do not run the ACL hardening for real.
>
> I ran the reviewed script with -DryRun.
>
> The config pre-run SHA-256 was correct:
>
> 29EB765EABCE05B81DCBEA33FD4D28800479596E9B23FD4D4FA334F6EE7DA1CB
>
> But the dry-run output was:
>
> [dry-run] C:\WINDOWS\System32\takeown.exe
> [dry-run] C:\WINDOWS\System32\takeown.exe
> [dry-run] C:\WINDOWS\System32\icacls.exe
> [dry-run] C:\WINDOWS\System32\icacls.exe
> [dry-run] C:\WINDOWS\System32\icacls.exe
> [dry-run] C:\WINDOWS\System32\icacls.exe
>
> and the two final icacls displays likewise contained no arguments.
>
> This violates the script's own DryRun contract to print the exact commands that would execute.
>
> The implementation currently defines:
>
> function Invoke-Step {
>     param([string]$Exe, [string[]]$Args)
>
> and uses $Args / @Args.
>
> PowerShell has a built-in automatic variable named $args. The live Windows PowerShell 5.1 dry-run demonstrates that the intended argument forwarding is not functioning correctly.
>
> Treat this as one narrowly bounded demonstrated pre-activation defect.
>
> Required fix:
>
> 1. Do not touch or move:
>    C:\Program Files\SupervisorConfig\config.toml
>
> 2. Do not modify its contents.
>
> 3. Do not activate anything.
>
> 4. Replace the Invoke-Step argument parameter with a non-reserved unambiguous name, for example:
>
>    param(
>        [string]$Exe,
>        [string[]]$CommandArgs
>    )
>
>    and use:
>
>    $shown = "$Exe " + ($CommandArgs -join " ")
>    & $Exe @CommandArgs
>
> 5. Inspect every invocation and prove the complete argument vector is retained.
>
> 6. Add a Windows PowerShell 5.1 regression test that proves -DryRun output contains the FULL expected commands and arguments, including at minimum:
>
>    takeown /F <config> /A
>    takeown /F <parent> /A
>    icacls <config> /inheritance:r
>    icacls <config> /grant:r with Administrators, SYSTEM, and unelevated-user RX
>    icacls <parent> /inheritance:r
>    icacls <parent> /grant:r with the required principals
>
> 7. The test must fail on the currently merged defective script.
>
> 8. Also correct the misleading DryRun completion wording if necessary so a dry run cannot claim that ACL hardening was actually applied.
>
> 9. Run the affected tests and independent G3/G5 review on this delta.
>
> 10. Return a NEW reviewed Git blob identity.
>     The current ca3811cd7e38a044bd0e01056e95b5028b6ce615 is now demonstrated defective and MUST NOT be elevated for the real apply.
>
> 11. Return the exact new dry-run command first.
>     I will personally run the new dry-run and inspect that it prints the COMPLETE argument vectors before any real elevated apply.
>
> Do not broaden this into other supervisor or ACL redesign work.
>
> And this time I want one additional rule: the next dry-run must visibly show every path, /F, /A, /inheritance:r, /grant:r, and every ACL principal.
>
> Only when we see that output should you run the actual ACL change.
>
> This is annoying, but it is also valuable: the second defect was caught before a privileged command was allowed to touch the ACLs.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
