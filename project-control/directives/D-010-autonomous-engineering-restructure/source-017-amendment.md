# D-010 — source-017 (owner amendment 17, VERBATIM): authorize safe controller-config relocation

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08, in response to the orchestrator's pre-hardening report that the live
config's parent `C:\SupervisorController` is the full controller checkout — not dedicated — with
the deliberately-mutable `model_selection.toml` in the same parent). Frozen base at capture:
`origin/main` = `49a0a48f52df63e18550762526afa494c63882e0`.

Requirement IDs added by this amendment start at `D-010-R157`; no existing source file or
requirement row (D-010-R001..R156) is edited. Relationship to source-015: this amendment inserts an
owner-authorized SAFE RELOCATION step into the activation package BEFORE the elevated OS-ACL apply
(source-015 item "elevated OS-ACL apply + protected:true proof"); the activation decision (R131)
and the M2-T015/T016 hold (R133/R143/R153) remain unchanged and are re-affirmed below.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> OWNER DECISION — AUTHORIZE SAFE CONTROLLER-CONFIG RELOCATION
>
> Proceed with the relocation, but DO NOT apply ACL hardening and DO NOT activate anything yet.
>
> First reach a quiescent state:
> - no child agents;
> - no background writer;
> - no process modifying C:\SupervisorController;
> - no new task dispatch.
>
> Then perform this read-only preflight:
>
> 1. Confirm:
>    old config =
>    C:\SupervisorController\config.toml
>
>    new config =
>    C:\SupervisorConfig\config.toml
>
>    mutable model selection remains =
>    C:\SupervisorController\model_selection.toml
>
> 2. Confirm config.toml is not a tracked repository file.
>    If it is tracked, STOP and report before moving it.
>
> 3. Record the exact SHA-256 of the current config.toml contents.
>
> 4. Verify there are no hard-coded runtime/scheduled-task dependencies requiring the old config path.
>
> 5. Inspect the effective ACL posture of the GRANDPARENT C:\.
>
>    Specifically determine whether my ordinary unelevated identity, Users,
>    Authenticated Users, or Everyone has a grant through C:\ that would permit
>    deleting/renaming/replacing C:\SupervisorConfig itself via DeleteChild /
>    DeleteSubdirectoriesAndFiles / Modify / FullControl.
>
>    This check is read-only.
>
>    If such a right exists, or the result is ambiguous, STOP.
>    Do not weaken or rewrite C:\ ACLs.
>    Return the smallest safe alternative location/design.
>
> 6. Verify the local elevated hardening script:
>
>    C:\SupervisorController\tools\agent_supervisor\harden_controller_config.ps1
>
>    is byte-identical to the script on merged main.
>
>    Expected Git blob identity:
>    0f01d649a64a4fcb1f96b805564cc40889d9a389
>
>    Do not execute an elevated script if this identity does not match.
>
> If all preflight checks pass, I authorize these UNELEVATED relocation steps:
>
> 7. Create only:
>    C:\SupervisorConfig
>
> 8. Move ONLY:
>    C:\SupervisorController\config.toml
>    to:
>    C:\SupervisorConfig\config.toml
>
> 9. Do not move or modify model_selection.toml.
>
> 10. Verify the config SHA-256 after the move is byte-identical to the recorded pre-move SHA-256.
>
> 11. Run the normal unelevated sanity check using BOTH independent paths:
>
>    python -m tools.agent_supervisor doctor --config "C:\SupervisorConfig\config.toml" --model-selection "C:\SupervisorController\model_selection.toml" --json
>
> Before hardening, controller_config_acl may honestly report NOT_PROTECTED.
> That is expected.
>
> The important pre-hardening checks are:
> - config parses correctly;
> - model selection parses correctly;
> - controller/config identity checks remain valid;
> - nothing points to the obsolete config location;
> - no other safety check regresses.
>
> 12. Do not modify config contents merely to accommodate the move.
>
> 13. Stop after the relocation and sanity proof.
>
> Return:
> - config SHA-256 before and after;
> - C:\ grandparent DeleteChild/effective-rights conclusion;
> - local hardening-script Git blob identity;
> - doctor result;
> - confirmation model_selection.toml remains at the old mutable location;
> - and the exact elevated PowerShell command I must personally run.
>
> Do not activate supervised-auto.
> Do not begin M2-T015 or M2-T016.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
