# M0-T114 — G0 readiness (administrative; recorded at the claim seam)

Task: M0-T114 (residual follow-up; Amendment 12 rows R272/R273 + Amendment 9 R258).
Recorded by: orchestrator (fable-orchestrator-session), 2026-08-29, campaign seq 28.
Supervisor-freeze qualifying evidence: **D-024-R258/R272** (owner-ordered residual
follow-up, executed in the Amendment-12 certification window).

1. **Authorization/sequencing:** Amendment 9 R258 carried the residuals as tracked
   follow-up work; Amendment 12 R272 orders execution NOW, in the same certification
   window as M0-T115 (accepted), as a SEPARATE bounded task with its own commits,
   evidence, and reviews; no broadening; M0-T116 recertifies both at ONE frozen identity.
2. **Bootstrap Gate 0:** re-verified — cwd IS the ctl24 root, clean tree, local == origin,
   no MCP.
3. **Dependencies:** packet lists M0-T113 — M0-T113 is `in_progress` BY DESIGN (its
   completion is the R276 resume, which sits BEHIND this unit + M0-T116 per Amendment 12).
   The dependency is superseded by the owner's Amendment-12 sequencing (R272: execute
   M0-T114 in this window; R275: recert AFTER both repair units; R276: resume last).
   Recorded here as the authoritative reading; the claim proceeds on the owner's explicit
   order.
4. **Resolver:** ok=true, 3 applicable ids (R258, R272, R273), no missing/invalid.
5. **The three residuals and their planned dispositions (scoped exactly):**
   - `telegram_sink._already_queued` digest normalization: `notify_condition` computes the
     queue-comparison digest from the RAW summary while queued items store the POST-BUILDER
     (redacted/truncated) summary — growth suppression silently misses altered summaries.
     FIX: compare like-for-like (post-builder vs post-builder) by checking the queue after
     `build_notification` using the built summary. Delivered-dedup (raw-vs-raw) is already
     consistent and stays unchanged.
   - `live_observation.py:296`: the record writes the RAW `source_record_key` although the
     sanitized value is ALREADY computed in the `sanitize_structure` input two lines above —
     one-line fix to read `sanitized.value["source_record_key"]`.
   - Unit-K boundary-queue write-only/inert notes: `codex_channel.py` is OUTSIDE this
     packet's allowed_paths — DISPOSITION ONLY (documented in the report as inert-by-design
     with the reviewers' original classification; any code change there would need its own
     packet).
6. **Method (standard §3):** red-before-green per fix with recorded observations;
   revert-proof; no journal writes (R273); packs + modularity before submit.
7. **R247 consequence:** this unit moves supervisor material identity — certification
   invalidation is EXPECTED and is exactly why M0-T116 follows.

Verdict: **PASS** (administrative readiness; independent review at G3/G4/G5 + DCV).
