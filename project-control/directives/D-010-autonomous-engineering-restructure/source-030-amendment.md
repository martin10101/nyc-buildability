# D-010 source-030 — OWNER R595 ACTIVATION AUTHORIZATION: build the turnover auto-launch in production (owner, 2026-08-09)

Captured verbatim from the owner's session-start message (2026-08-09). This is a **new owner decision
requiring pre-action durability** (R324 carve-out) and a **Tier-D posture flip** (D-010-R111 / ADR-006):
it authorizes R595 production activation of the unattended turnover auto-launch, which the prior handoff
surfaced as an open owner-only decision and which R343 (source-029) had, absent that decision, resolved
as "keep record-intent-only; do NOT self-authorize R595 activation." The owner has now decided: **yes,
build it.** Frozen base SHA `37667ff` (origin/main at capture).

## Verbatim owner text (session-start directive, 2026-08-09)

The owner's answer is embedded mid-sentence in the surfaced decision. Captured exactly as received
(including the interleaved answer clause and original spacing):

> One decision is yours whenever you want it (not blocking): authorize R595 production auto-launch for the turnover my answer yes lets get it build  watchdog (follow-up M0-T056), or keep it record-intent-only. Everything else proceeds under standard gates.

Surrounding operating instruction from the same message (context; not a new product requirement):

> Work continuously from the SESSION_HANDOFF; do not stop to hand off; keep dispatching producers until the work is done.

## Interpretation (no genuine ambiguity)

The owner posed the two options — (a) authorize R595 production auto-launch for the turnover watchdog
(follow-up **M0-T056**), or (b) keep it record-intent-only — and answered inline: **"my answer yes lets
get it build."** The only coherent reading is option (a): **authorize R595 production activation of the
turnover auto-launch; build M0-T056.** No alternative reading exists (option (b) is the rejected branch).

## Scope of the authorization (precise; nothing broader)

This lifts EXACTLY ONE thing: the shadow-only / LIMITED-AUTO-off / no-activation-change posture is
flipped **only** for the **turnover auto-launch actuation channel** (main-orchestrator watchdog +
worker-layer auto-redispatch), so a confirmed Fable/quota exhaustion may **actually launch** exactly one
`claude-opus-4-8` xhigh successor in production. To the precise extent needed for that channel, this
amendment supersedes R343's "record-intent-only / do-NOT-self-authorize-R595" resolution and narrows
R341's "change supervised-auto activation" prohibition. **Every other hold remains in force** — protected
config/ACL scope, command/path/credential protections, LIMITED-AUTO for any non-turnover autonomous
action, five-borough scope, history-rewrite and evidence-deletion prohibitions, and the Tier-D legal /
production-approval hard stops. The M0-T054 controller/adapters/detection are reused unchanged; the
mechanism's proven invariants (single-instance, exactly-once, no duplicate workers/commits, audit-linked,
fail-closed, durable across the terminal/session boundary) are binding, not optional. Production actuation
is enabled only after a bounded live continuous proof on an ISOLATED non-product runtime and all required
gates pass; the proof must not touch M2-T015 or any production data.

## Decomposition → requirements

R344 (authorization), R345 (orchestrator-layer deliverable), R346 (worker-layer deliverable),
R347 (safety invariants), R348 (bounded prohibition — no other hold weakened), R349 (acceptance harness /
isolated live proof + gates + DCV), R350 (dependency/sequencing), R351 (return). All applicable to
**M0-T056** at lifecycle events create/dispatch/accept, effective 2026-08-09. Amends source-029.
