# D-010 — source-015 (owner amendment 15, VERBATIM): G3 MAJOR-1 decision — close before acceptance

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08, at session-7 open, in response to the session-6 close block which
routed the M0-T048 G3 MAJOR-1 (cross-process resume-window `approved_digest` forgery) vs G5 N-1
divergence to DCV adjudication). Frozen base at capture: `origin/main` =
`9c2ec252b509ddf6bb067325c6aa28c2cdc6ff4d`.

Requirement IDs added by this amendment start at `D-010-R144`; no existing source file or
requirement row (D-010-R001..R143) is edited. Relationship to am.14: this amendment ADJUDICATES the
G3-MAJOR-1 open item on the am.14 C2-closure task (M0-T048) — the owner orders a second bounded fix
(resume-window trust anchor) BEFORE acceptance, replacing the session-7 plan's "DCV adjudicates
first" branch; DCV still runs, after the fix, at the new frozen identity. The am.14 rows
(R134–R143) remain binding and unchanged, including R140 (no supervisor redesign / no new
infrastructure), which this amendment explicitly preserves.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> OWNER DECISION — CLOSE M0-T048 G3 MAJOR-1 BEFORE ACCEPTANCE
>
> Do not accept or merge M0-T048 yet.
>
> Close the cross-process resume-window MAJOR-1 with the smallest bounded fix.
>
> Required property:
>
> After a genuine operator approval, the resume path must NOT trust the mutable journal's approved_digest as the sole record of what the operator approved.
>
> At resume, cross-check the journal's approved_digest against the already-sealed/hash-chained operator approval audit evidence, or an equivalently existing durable operator-approval record.
>
> Adversarial test:
>
> 1. Perform a genuine operator approval.
> 2. After approval, mutate in the journal:
>    - approved_instruction;
>    - approved_digest;
>    - prompt and prompt_bytes_digest as needed,
>    all self-consistently.
> 3. Leave the sealed operator-approval audit record unchanged.
> 4. Resume.
> 5. Resume must fail closed.
> 6. Provider calls must equal zero.
> 7. The mismatch/refusal must be durably recorded.
> 8. Existing C2, happy-path, exactly-once, clock-invariant, and shadow-posture tests must remain green.
>
> BOUNDARY:
>
> - Do NOT add journal signing.
> - Do NOT build a service, daemon, PKI, enterprise identity system, or new infrastructure.
> - Do NOT redesign the supervisor.
> - Do NOT broaden this task beyond the resume-window trust anchor.
> - Preserve R140.
> - Preserve SHADOW-ONLY.
> - Do not activate anything.
>
> After the bounded fix, rerun the affected G3/G4/G5 reviews and DCV at the new frozen identity.
>
> If all gates pass:
> - accept M0-T048;
> - merge through the normal Tier A path;
> - then return to the existing activation package:
>   1. elevated OS-ACL apply + protected:true proof;
>   2. final supervised-auto activation decision;
>   3. M2-T015 and M2-T016 as the two supervised-auto product proof tasks.
>
> Proceed without another routine approval.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
