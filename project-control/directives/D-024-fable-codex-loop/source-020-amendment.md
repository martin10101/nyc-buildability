# D-024 Amendment 20 — one post-Amendment-19 live-loop attempt authorized; preflight-first, owner-executed, eight-point live proof (owner instruction 2026-08-30, via /session-handoff turnover reason)

Captured: 2026-08-30 UTC by the orchestrator (Fable 5), verbatim from the owner's
/session-handoff invocation (the turnover reason carries the directive; captured BEFORE the
handoff per D-001). Base identity at capture: branch `control/D-024-fable-codex-loop`, HEAD
`88e3093` (local == origin; tree clean; campaign seq 42, R347 stop standing; M0-T123 and
M0-T124 accepted). Amends: `source-001.md` (owner directive v4). Requirement IDs assigned:
D-024-R348..D-024-R362.

Reconciliation: the owner authorizes EXACTLY ONE new live-loop attempt following the
accepted M0-T123 repair and M0-T124 certification (R348) — this replaces nothing and grants
nothing else: the consumed R316 attempt stays consumed, and the S16.7 cumulative
owner-touch measurement and every budget stay un-reset and un-reinterpreted (R349).
Sequencing: FIRST the complete activation preflight re-runs against the then-current clean
pushed tip, every row reported, and NO recovery or start action is taken unless all rows
pass (R350). On a passing preflight the orchestrator PRESENTS both exact certified
commands — the recovery command matching the journal's current PAUSED_RECOVERY state and
the certified start — explicitly restated fresh (the owner notes a missing code block in
the prior message must not be relied on); the OWNER executes both, separately and in order
(R351). The attempt must prove eight facts from primary evidence (R352–R359): the old 640k
session is never contacted again; rotation/shedding occurs before the worker provider
launch; a distinct fresh Fable 5 session identity is created; the worker launches inside
wt-m0t107 and never the primary checkout; task, checkpoint lineage, budgets, audit
history, and exactly-once state are preserved; a valid structured checkpoint reaches the
independent Codex reviewer; Codex completes its independent review; M0-T107 actually
advances. Prohibitions (R360): no `--repin-cli-identity`, no budget resets, no history
clearing, no journal edits, no PR #241, no policy loosening. Failure protocol (R361): if
the preflight differs, or the attempt produces any post-dispatch stop or live-journey
failure — no restart, no retry, no second clear-recovery, no automatic repair window;
preserve everything and report the full system-level assessment for a NEW owner decision.
No continuous-autonomy claim unless the complete live journey succeeds (R362). Rows bind
M0-T107 (the loop packet whose lifecycle the attempt is) for verification of recording and
outcome.

Forward trace: p1 s1–2 (authorization of exactly one new attempt) → R348; p1 s3 (no
reset/erase/reinterpretation of S16.7 or any budget) → R349; p2 (preflight first, every
row reported, no action unless all pass) → R350; p3 (present both exact certified
commands fresh; owner executes separately in order) → R351; p4 list items 1–8 → R352
(old 640k session not contacted), R353 (rotation/shedding before provider launch), R354
(distinct fresh Fable 5 session identity), R355 (worker inside wt-m0t107, never primary
checkout), R356 (task/checkpoint lineage/budgets/audit/exactly-once preserved), R357
(valid structured checkpoint reaches the independent Codex reviewer), R358 (Codex
completes its independent review), R359 (M0-T107 actually advances); p5 (prohibitions) →
R360; p6 s1–2 (failure protocol: no restart/retry/clear/auto-window; preserve + full
system-level assessment for a new owner decision) → R361; p6 s3 (no continuous-autonomy
claim unless the complete journey succeeds) → R362.

Anchors: #one-attempt-authorization (p1), #preflight-first (p2), #present-both-commands
(p3), #eight-point-proof (p4), #prohibitions (p5), #failure-protocol (p6).

---VERBATIM-BEGIN---
authorize exactly one post-Amendment-19 live-loop attempt. This is a new, single attempt following the accepted M0-T123 repair and M0-T124 certification. It does not reset, erase, or reinterpret the cumulative S16.7 owner-touch measurement or any other budget.
First rerun the complete activation preflight against the then-current clean, pushed tip. Report every row and take no recovery or start action unless all rows pass.
If preflight passes, present me with the exact certified recovery command for the journal’s current PAUSED_RECOVERY state and the exact certified start command. Do not rely on the missing code block in the previous message. I will execute both owner commands myself, separately and in order.
This attempt must prove from primary evidence:
The old 640k session is not contacted again.
Rotation/shedding occurs before the worker provider launch.
A distinct fresh Fable 5 session identity is created.
The worker launches inside wt-m0t107, never the primary checkout.
The task, checkpoint lineage, budgets, audit history, and exactly-once state are preserved.
A valid structured checkpoint reaches the independent Codex reviewer.
Codex completes its independent review.
M0-T107 actually advances.
Do not use --repin-cli-identity, reset budgets, clear history, edit the journal, touch PR #241, or loosen any policy.
If preflight differs, or if this attempt produces any post-dispatch stop or live-journey failure, do not restart, retry, clear recovery again, or automatically open another repair window. Preserve everything and report the full system-level assessment for a new owner decision. Do not claim continuous autonomy unless the complete live journey succeeds
---VERBATIM-END---
