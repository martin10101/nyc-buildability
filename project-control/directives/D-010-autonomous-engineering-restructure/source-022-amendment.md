# D-010 — source-022 (owner amendment 22, VERBATIM): corrected apply succeeded — run the live activation proof

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08 after the owner's elevated apply of merged blob `b6ee6589…` under the
R195 dry-run-first rule). Frozen base at capture: `origin/main` =
`a1b127e2bc2c549b4423a5ea52cfad4c028715b3`.

Requirement IDs added by this amendment start at `D-010-R208`; no existing source file or
requirement row (D-010-R001..R207) is edited. Relationship to source-021: closes the R206 loop
(apply succeeded, clean three-ACE DACLs, poison gone, SHA unchanged) and orders the live
unelevated activation proof + durable capture + the activation-decision-line return; the R213
product-proof hold continues R133/R143/R153/R167/R196.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> The corrected elevated ACL hardening completed successfully.
>
> Observed final ACLs:
>
> FILE:
> LAPTOP-M7D730QA\MLFLL:(RX)
> NT AUTHORITY\SYSTEM:(F)
> BUILTIN\Administrators:(F)
>
> PARENT:
> LAPTOP-M7D730QA\MLFLL:(RX)
> NT AUTHORITY\SYSTEM:(OI)(CI)(F)
> BUILTIN\Administrators:(OI)(CI)(F)
>
> The former Authenticated Users:(M) ACE is gone.
>
> Post-apply config SHA-256 is still exactly:
>
> 29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb
>
> Now run the live UNELEVATED activation proof:
>
> python -m tools.agent_supervisor doctor --config "C:\Program Files\SupervisorConfig\config.toml" --model-selection "C:\SupervisorController\model_selection.toml" --json
>
> Require all of the following:
>
> - controller_config_acl.protected == true
> - controller_config_acl.state == "PROTECTED"
> - controller_config_acl.file.state == "PROTECTED"
> - controller_config_acl.parent.state == "PROTECTED"
> - the protected config remains readable
> - the config SHA remains unchanged
> - model_selection.toml remains writable by the ordinary unelevated account
> - no activation has occurred yet
>
> Capture the live proof durably through the normal control-plane path.
>
> If ANY ACL verdict is not PROTECTED, STOP and report it.
>
> If all prerequisites pass, return the exact owner-typed supervised-auto activation decision line. Do not begin any product proof task before I type that line.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
