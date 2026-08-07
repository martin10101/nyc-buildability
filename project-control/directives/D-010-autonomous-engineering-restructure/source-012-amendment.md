# D-010 — source-012 (owner amendment 12, VERBATIM): pre-activation decision and ordering

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator mid-session on 2026-08-07, delivered via tool-use interruption during the D-009/M0-T019/
M2-T014 batch reconciliation unit). Frozen base at capture: `origin/main` = `14ec5328efea56880555d0a32ddc90db9a5eeff2`.

Requirement IDs added by this amendment start at `D-010-R122`; no existing source file or requirement
row (D-010-R001..R121) is edited. Sequencing effect (explicit, visible supersession): for M2-T015 and
M2-T016 ONLY, this amendment supersedes the immediate product-work sequencing of R116/R121/0A.11 —
those two tasks become the supervised-auto proof tasks and may not begin before supervised-auto
activation. The pre-activation task it inserts is directive-cited work (M0-T045 G5 LOW-1 finding,
M0-T045 G4 estop audit-fork finding, activation-checklist OS-ACL item), satisfying the 0A.10
freeze/AD-093 evidence requirement.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-07)

> OWNER PRE-ACTIVATION DECISION AND ORDERING
>
> Do not interrupt the bounded unit currently in progress.
>
> Finish the current D-009 / M0-T019 / M2-T014 reconciliation and reach a clean, committed, verified seam.
>
> BEFORE beginning Product Task 1 (M2-T015), insert one narrowly bounded PRE-ACTIVATION task.
>
> That task must contain only:
>
> 1. Fix the M0-T045 G5 LOW-1 park→approve integrity issue:
>    bind the forwarded prompt bytes to the OPERATOR-NAMED approval digest at approval time, with adversarial tests.
>
> 2. Complete the M0-T045 G4 emergency-stop audit-fork follow-up:
>    add the required regression test locking the known fail-closed forked-audit-chain behavior.
>
>    OWNER ACKNOWLEDGEMENT:
>    I acknowledge that an emergency stop may leave the audit log forked/unappendable until repaired, provided the system fails closed, does not silently repair or hide the fork, clearly records the condition, and refuses unsafe continuation.
>
> 3. WINDOWS OS-ACL DECISION:
>
>    The current single-account writable ACL is NOT sufficient for activation.
>
>    Harden the immutable controller configuration before supervised-auto.
>
>    Required boundary:
>    - the normal unelevated Claude/supervisor process may READ the controller configuration;
>    - it must NOT be able to modify, overwrite, delete, rename, replace, or change ACLs on it;
>    - protect the parent directory against replacement/bypass as well as the file itself;
>    - modification must require an elevated owner action / Windows UAC boundary;
>    - retain fail-closed controller-config identity/digest verification;
>    - add bounded Windows tests/probes proving the ordinary unelevated process cannot modify, delete, replace, rename, or weaken the protected configuration;
>    - do not create a service, daemon, enterprise identity system, separate infrastructure project, or broader supervisor redesign.
>
> Keep this task strictly limited to these pre-activation requirements.
>
> Run the normal independent engineering, QA/security, and directive-compliance gates.
>
> Do NOT activate supervised-auto until this pre-activation task is accepted and all remaining activation-checklist blockers have been mechanically reconciled as satisfied.
>
> After that, present me with the exact supervised-auto activation decision line.
>
> Do NOT begin M2-T015 or M2-T016 before supervised-auto activation.
>
> Those two real product tasks are intended to be the supervised-auto proof tasks required before consideration of limited-auto.
>
> Continue the current bounded unit now. Apply this instruction at the next clean seam.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
