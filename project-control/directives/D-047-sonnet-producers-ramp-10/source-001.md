# D-047 source-001 (original, verbatim) — owner directive, interactive chat (companion session), 2026-09-13

Capture head: `e0e59772fbbb2796632265045c70eed7a6128a0f` (branch `candidate/D-024-mrl-option-b`).
Frozen origin/main baseline: `d8b3899f61efa6620e18a26541ced96020f5bef9`.
Captured by the companion session (ctl24-8e) per the Part-0 working model; D-042..D-046
peer-capture precedent. Given ~10 minutes after D-046 (parallel family production, ceiling 3).

## owner-message-verbatim

Directive (owner, verbatim):

> Can we add that it should use sonnet modle for the build since its a cheaper model also maybe we
> should let it run like 10 20 subagents so alot more can be done at ones

## scope-clarification-verbatim (structured questions, same session, 2026-09-13)

The companion session presented current pricing (claude-sonnet-5 $2/$10 per MTok vs the producers'
current claude-opus-4-8 $5/$25 — 60% cheaper) and pushed back on 10–20 with the pipeline-bottleneck
analysis (single orchestrator, review gates, CI, usage caps; past ~6 producers extra agents mostly
queue). Two structured questions were asked; options and selections verbatim:

**Q1: "Where should the cheaper Sonnet 5 model be used?"**

1. **Builders only (Recommended)** — "Producers switch to Sonnet 5 (60% cheaper). Reviewers and the
   orchestrator stay on the strong models you approved earlier — they're the safety net that
   catches a cheaper builder's mistakes. Escalation rule: a task that fails review twice gets
   rebuilt on Opus."
2. **Builders + reviewers** — "Everything switches to Sonnet 5. Maximum saving, but the safety net
   weakens at the same time the builders get cheaper — in a legally sensitive product I don't
   recommend weakening both ends at once."

Owner's selection: **"Builders only (Recommended)"**.

**Q2: "How many builders should run at once?"**

1. **Up to 6, ramped (Recommended)** — "Start at 3–4, widen to 6 while reviews and CI keep up.
   Matches the pipeline's real capacity — nearly all the speed of 20 agents at a third of the burn
   rate."
2. **Up to 10, ramped** — "Same ramp rule but a higher ceiling. Some queueing waste likely; useful
   if many small disjoint tasks pile up (e.g., many rule families at once)."
3. **Keep 3** — "The ceiling we set an hour ago. Safest, slowest of the three."
4. **Full 20** — "What you asked about. Honest warning: past ~6 the extra agents mostly wait in
   line behind the single orchestrator, reviews, and CI — you'd spend roughly 3x faster for little
   added speed, and usage-cap stalls become likely."

Owner's selection: **"Up to 10, ramped"**.

## capture-context

- MODEL: writing PRODUCERS for campaign work switch to exact model id `claude-sonnet-5` (never an
  alias). Gate reviewers and the orchestrator are EXPLICITLY UNCHANGED — the D-004 pinned set
  (claude-fable-5 six-file set, R734–R742) and the standing Fable→opus-4-8 xhigh reviewer-fallback
  rule stay as the owner previously decided. D-004 is superseded ONLY for producer-agent model
  keys, nothing else.
- ESCALATION (part of the selected Q1 option text): a task that fails independent review twice on
  Sonnet-built material is rebuilt with a `claude-opus-4-8` producer.
- CONCURRENCY: the D-046 ceiling of 3 is SUPERSEDED by a ceiling of 10 concurrent writing
  producers with a MANDATORY RAMP — start at 3–4 and widen only while review latency and CI
  throughput stay healthy; back off under resource pressure. Everything else in D-046 (mandatory
  disjointness R002, no quality relaxation R003, backpressure posture R004, quiet monitoring)
  remains fully in force.
- The owner's "10 20" was resolved to 10 by explicit selection after the tradeoffs were presented;
  20 was offered and not chosen.
- Cost facts presented: Sonnet 5 $2/$10, Opus 4.8 $5/$25, Fable 5 $10/$50 per MTok (claude-api
  skill, cached 2026-06-24).
- Model changes are owner-authorized settings changes to the producer agent files; this directive
  IS that authorization. Exact-id discipline applies (`claude-sonnet-5`, `claude-opus-4-8`).
