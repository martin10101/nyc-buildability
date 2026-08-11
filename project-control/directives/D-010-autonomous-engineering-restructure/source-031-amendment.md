# D-010 source-031 — OWNER R595 BUILD DIRECTIVE: order of operations, safety scope, and the permission boundary (owner, 2026-08-11)

Captured verbatim from the owner's session-start message (session 14, 2026-08-11). This amends
source-030 (the R595 activation authorization): source-030 answered *whether* to build; this message
directs *how*, *in what order*, and *where the loop must stop for the owner*. Frozen base SHA
`37667ff` (origin/main at capture, unchanged from source-030's capture).

## Verbatim owner text (session-start directive, session 14)

> You are the lead orchestrator for the NYC Buildability platform (read CLAUDE.md and the
> project-control ledger as usual). MISSION THIS SESSION: get us to fully autonomous, supervised
> operation — where I give one command and the Codex supervisor runs the engineering loop for days
> (dispatching workers, committing, pushing, opening/merging PRs, accepting green work, and
> auto-restarting a fresh session when tokens run out) while respecting every safety boundary. This
> is the R595 activation I already authorized (D-010 source-030), implemented as task M0-T056.
>
> START HERE (do the full start-of-session routine first; do not skip):
> 1. Run `python tools/project_control.py status` and `python tools/current_state.py`, and read
>    docs/SESSION_HANDOFF.md (the SESSION 13 block is current). Reconcile against origin/main — trust
>    NO SHA written anywhere as still-current; verify live.
> 2. Read tasks M0-T054 (turnover watchdog, accepted), M0-T056 (R595 activation, backlog), the D-010
>    source-030-amendment.md (my R595 authorization + its exact scope), docs/AGENT_OPERATING_SYSTEM.md,
>    ADR-006 (autonomy tiers), and .claude/ORCHESTRATION_POLICY.md.
>
> ORDER OF OPERATIONS:
> 1. FIRST land the finished work from the prior session: accept M0-T055, then finalize + accept
>    M2-T016 (transcribe its 77-row DCV verification — project-control/reports/M2-T016-DCV-verification.json
>    — into the D-010 registry, record gates G0/G2/G3/G4/G5 at the integration HEAD, merge PR #216 after
>    CI is green, create the B-001-blocked survey-review HTTP-route/production-ReviewStore follow-up task,
>    then accept). If `python tools/project_control.py accept` is denied by the permission classifier,
>    STOP and ask me to allow it (see PERMISSIONS) — that is the single gate.
> 2. Complete the R595 capture: append requirements R344–R351 to the D-010 registry (source-030 already
>    names them; the requirements.json/manifest.json append is owed) and validate with
>    tools/validate_directive_compliance.py --check. Durable-before-action for M0-T056.
> 3. Invoke /directive-compliance to bind the R595 build directive to M0-T056.
> 4. Build M0-T056 through full gates: (a) an independently-live watchdog OUTSIDE the Claude session that
>    detects a quota hard stop and auto-launches exactly one claude-opus-4-8 successor loading the durable
>    handoff + safe checkpoint; (b) enable the worker-layer auto-redispatch (flip
>    default_actuation_authorization + wire the real controller/launcher), REUSING the accepted M0-T054
>    mechanism unchanged; (c) a bounded live continuous proof on an ISOLATED, non-product runtime (real
>    exhaustion → real successor auto-launches, no owner /model), touching no production data. Gates
>    G0/G2/G3/G5 + an independent directive-compliance verification.
> 5. Only AFTER the isolated proof + gates pass, flip to production actuation. Report the exact actuation
>    channel wired, the exactly-once/no-duplicate evidence + audit link, and confirm no other hold moved.
>
> SAFETY — non-negotiable (this is source-030's exact scope):
> - R595 lifts EXACTLY ONE thing: the turnover auto-launch actuation channel. It does NOT weaken any other
>   hold — protected config/ACLs, command/path/credential protections, LIMITED-AUTO for non-turnover
>   actions, five-borough scope, and the history-rewrite/evidence-deletion prohibitions all remain.
> - The loop can never self-approve its own work: every task passes an INDEPENDENT reviewer gate
>   (producer ≠ approver); directive verification is producer ≠ verifier.
> - Tier-D / Section-20 hard stops are permanent: secrets/credentials, payments, verification codes,
>   production approval, legal/zoning sign-off. The loop PARKS these for me and continues other unblocked
>   work — it never does them itself.
> - Single-instance, exactly-once, no duplicate workers/commits, audit-linked, fail-closed on any
>   ambiguity. Any protected-config edit strictly needed for the channel follows the protected-config
>   procedure (doctor proof, owner-visible).
>
> PERMISSIONS (the crux of autonomy):
> - For an unattended loop the runner must be ALLOWED to run the control commands
>   (`python tools/project_control.py accept`, `git push`, `gh` merge) without a per-command prompt. Today
>   the auto-mode classifier blocks `accept`. When you hit a step that needs this, STOP and give me the
>   EXACT settings allow-rule to add (or the exact command to run), in plain English + the exact line. Do
>   NOT try to bypass the classifier.
>
> ENVIRONMENT LANDMINES:
> - The supervisor lives at C:/SupervisorController/ with a protected config (config.toml allowed_models +
>   ACLs), shadow/supervised modes, LIMITED-AUTO off. Reuse the accepted M0-T054 controller/adapters/
>   detection unchanged.
> - This sandbox is Python 3.11; services/api needs 3.12 (PEP 695) — verify via captured CI evidence, not
>   local pytest. CI pins ruff 0.13.0 (`pip install ruff==0.13.0`); local ruff may be stale.
> - Directive-registry Bash writes AND `accept` are gated by the classifier — use the Edit tool for
>   registry files and ask me for `accept`/permission changes.
> - Never `git init` for a new repo (use new-repo.ps1); never local-npm; thin client (~7 GB free).
>
> Work continuously; keep dispatching until a gated step genuinely needs me, then surface it in plain
> English with the exact line to type. End state: I give one command and the supervised loop runs for
> days — pushing/merging/accepting green Tier-A work, auto-restarting on token-out, parking Tier-D for me.

## Interpretation (no genuine ambiguity)

The message reaffirms source-030's scope word-for-word and adds four things source-030 did not carry:
an explicit **order of operations**, an explicit **M2-T016 finalization checklist**, an explicit
**permission boundary** (the classifier must be widened by the owner, never bypassed by the agent),
and an explicit **end-state definition** for the supervised loop. The safety section is a restatement
of source-030's scope, already carried by R347/R348; it is not re-decomposed into duplicate rows.

## Decomposition → requirements

R352 (order of operations / sequencing), R353 (M2-T016 finalization checklist), R354 (permission
boundary — stop-and-surface, never bypass), R355 (end-state definition for the supervised loop),
R356 (environment constraints), R357 (supervisor-runtime reuse). Effective 2026-08-11.

### Binding note (deliberate, and why)

R352–R357 bind **M0-T056 only**, via `applicability.task_ids`.

The order-of-operations (R352) and M2-T016-finalization (R353) instructions do textually concern
M0-T055 and M2-T016. They are **not** bound as new requirement rows onto those two packets, because
both already carry frozen independent directive-compliance verification at a fixed applicable set
(M0-T055: 21 requirements at its reviewed identity; M2-T016: 77 rows in
`project-control/reports/M2-T016-DCV-verification.json`). Growing either applicable set would mark
that verification incomplete and block the very acceptances this directive orders FIRST — the
instruction would defeat itself.

Nothing is lost by this choice: the instructions are captured verbatim above, they are being executed
in this session, and their evidence lands in each task's `progress_log` plus the acceptance artifacts.
This note exists so the choice is visible and reviewable rather than silent. If an independent
reviewer judges that R352/R353 must additionally bind M0-T055 / M2-T016, the correct remedy is a
delta independent verification adding those rows — not a quiet re-scoping.
