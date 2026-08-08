# D-010 — source-014 (owner amendment 14, VERBATIM): C2 decision — close before activation

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08, in response to the CP-0043 supervised-auto decision package which
presented the G5-C2 residual accept-or-close choice). Frozen base at capture: `origin/main` =
`9c2ec252b509ddf6bb067325c6aa28c2cdc6ff4d`.

Requirement IDs added by this amendment start at `D-010-R134`; no existing source file or
requirement row (D-010-R001..R133) is edited. Relationship to am.12: this amendment RESOLVES the
open C2 branch of the R131/R132 activation sequence (the "accept residual verbatim OR order the
fix" choice) in favor of CLOSE-BEFORE-ACTIVATION; the am.12 sequencing (R131 activation prohibition,
R132 return item, R133 M2-T015/T016 hold) remains binding and unchanged.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> OWNER C2 DECISION — CLOSE BEFORE ACTIVATION
>
> Do not accept the G5-C2 journal-write two-field-forgery residual.
>
> Before supervised-auto activation, close C2 with one narrowly bounded security fix.
>
> Required security property:
>
> An attacker who can modify BOTH:
> - the parked prompt bytes; and
> - prompt_bytes_digest
>
> while leaving the operator-named approval digest unchanged MUST NOT be able to cause altered prompt content to be forwarded.
>
> The forwarded content must be cryptographically bound to information independently covered by the operator-named approval_digest, rather than relying solely on mutable journal fields.
>
> Preserve the existing S13.5 timestamp/clock invariant. Use the smallest correct design — for example, generate the non-authoritative FORWARDED AT timestamp only at actual forward time, or persist/recompute the structured approved instruction at approve/resume time — whichever produces the cleanest deterministic binding.
>
> Mandatory adversarial test:
>
> 1. Park an authentic approval.
> 2. Mutate BOTH prompt and prompt_bytes_digest consistently in the journal.
> 3. Leave the operator-named approval digest unchanged.
> 4. Attempt approval/resume.
> 5. It must fail closed.
> 6. Provider calls must equal zero.
> 7. The refusal must be durably/auditably recorded.
>
> Also prove:
> - ordinary happy path still forwards exactly once;
> - clock-only differences do not invalidate the operator's approval;
> - post-approval tampering still refuses;
> - no SHADOW/supervised/limited-auto authority change is introduced.
>
> No supervisor redesign.
> No additional features.
> No new infrastructure.
> No broader cleanup.
>
> Run the normal G3/G4/G5/DCV gates and merge only after all required checks pass.
>
> After C2 is closed, return to the existing activation sequence. Do not start M2-T015 or M2-T016 yet.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
