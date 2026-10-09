# M0-T114 — G2 producer self-check

Task: M0-T114 (residual fixes; rows R258/R272/R273). Producer:
fable-orchestrator-session. Supervisor-freeze qualifying evidence: **D-024-R258/R272**.

1. **Scope:** deliverable commit touches EXACTLY telegram_sink.py, live_observation.py,
   their two test packs, and the report — all in allowed_paths; residual 3 deliberately
   left as a documented disposition because `codex_channel.py` is outside scope (R272
   no-broadening); no dependency, policy, hook, or journal change.
2. **Method (standard §3):** per-fix RED recorded against unchanged code (both defect
   tests failed; exact selections in the report) → fixes → GREEN (L-pack 36/36, golden
   pack 41/41) → shared revert-proof recorded (stash both prod files → 2 FAIL → pop →
   2 PASS).
3. **Fix minimality (§2):** residual 1 moves ONE check after the builder and changes its
   comparison operand to the post-builder summary (the stored form) — `_already_queued`
   itself and the delivered-dedup path unchanged; residual 2 is one line reading the
   already-computed sanitized value. No new abstraction, no behavior change for
   unaltered summaries (raw == built).
4. **Semantics preserved:** at-least-once delivery intact (nothing dropped; the queued
   item still delivers); leak-refusal (builder) unchanged and still runs BEFORE any
   enqueue; the closed 8-condition vocabulary, retries, FIFO dedup bound, 3500-char cap,
   and identifier redaction all untouched (sweep 535/535 including the full L-pack and
   adversarial/endurance packs).
5. **R273:** zero runtime-journal writes; live journal untouched.
6. **R247 consequence acknowledged:** supervisor material identity moved again; M0-T116
   recertifies both units at the ONE frozen final identity next.

Self-check verdict: **PASS** — ready for independent G3/G4/G5 + DCV at the frozen tip.
