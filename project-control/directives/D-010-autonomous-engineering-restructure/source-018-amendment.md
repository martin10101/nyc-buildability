# D-010 — source-018 (owner amendment 18, VERBATIM): final pre-hardening config-content check

Captured per `.claude/skills/directive-compliance` §1. Channel: owner_message (typed to the
orchestrator on 2026-08-08, in response to the am.17 preflight STOP report, which proposed the
`C:\Program Files\SupervisorConfig` alternative). Frozen base at capture: `origin/main` =
`bbd176a398430719c390551b6494b1885c322c39`.

Requirement IDs added by this amendment start at `D-010-R168`; no existing source file or
requirement row (D-010-R001..R167) is edited. Relationship to source-017: approves the proposed
alternative location IN PRINCIPLE and inserts one further read-only precondition (config-content
correctness for supervised-auto) BEFORE the elevated relocation/hardening session; all source-017
prohibitions remain in force.

## THE DIRECTIVE (verbatim from the owner message, 2026-08-08)

> ONE FINAL PRE-HARDENING CHECK — DO NOT MOVE OR HARDEN YET
>
> The proposed dedicated location C:\Program Files\SupervisorConfig is approved in principle, subject to this final check.
>
> The current config at:
> C:\SupervisorController\config.toml
>
> is the old shadow-pilot config and reportedly has:
> - controller.default_mode = "shadow"
> - claude.allowed_models = []
>
> Before I make this file immutable under UAC, determine whether its CURRENT CONTENTS are actually correct for the supervised-auto activation we are about to perform.
>
> Read the current controller/config semantics and the activation path.
>
> Answer specifically:
>
> 1. Does supervised-auto require controller.default_mode to remain "shadow", change to "supervised", or is supervised-auto activation represented somewhere else entirely?
>
> 2. Does the supervised-auto product-task pipeline require launching Claude through this controller?
>
> 3. If yes, is claude.allowed_models = [] valid?
>    Note that config.py defines an empty provider allowlist as "no explicit selection permitted."
>
> 4. Compare the current config against the actual model_selection.toml and the intended M2-T015/M2-T016 supervised-auto execution path.
>
> 5. List every immutable config field that would need to change BEFORE supervised-auto can operate correctly.
>
> 6. Do not change any config yet.
>
> 7. If the existing config is already exactly correct, state that explicitly and prove why.
>
> 8. If any immutable config change is required, STOP and present the smallest exact owner-reviewed config diff BEFORE relocation/hardening.
>
> Do not activate.
> Do not move the config.
> Do not apply ACLs.
> Do not begin M2-T015/M2-T016.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
