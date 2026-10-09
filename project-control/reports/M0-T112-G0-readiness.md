# M0-T112 — G0 readiness (administrative; recorded at the claim seam)

Task: M0-T112 (unit M: final golden re-certification at the FINAL frozen post-addition
identity; D-024 Amendment 8, rows R231/R232/R246/R247/R248/R249).
Recorded by: orchestrator (fable-orchestrator-session), 2026-08-28, campaign seq 25.
Supervisor-freeze qualifying evidence: **D-024-R247** (packet-named, Amendment 8).

1. **Bootstrap Gate 0 (R125–R128):** passed at session start and re-verified at this seam:
   primary cwd IS the worktree root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch
   `control/D-024-fable-codex-loop`, NO MCP tools attached, clean tree, local == origin at
   `a2aec11` (CI **20/20 green** on that tip, confirmed via check-runs API this seam).
2. **Dependencies:** M0-T110 (unit K) `accepted` and M0-T111 (unit L) `accepted` — both
   verified live in the ledger this seam; campaign seq 25 names M0-T112 as the authorized
   NEXT (M0-T107 unit J trails non-blocking).
3. **Packet integrity:** outputs/allowed/forbidden paths present; directive_refs `D-024:ALL`;
   `evaluate_task_refs` resolves ok=true, **6 applicable ids** (R231, R232, R246, R247,
   R248, R249) — exactly the campaign-predicted set — no missing/invalid/unresolved
   (selective-citation guard satisfied at claim). This is a governance/certification unit:
   the executable acceptance harness IS the existing golden-run pack
   (`tools/test_agent_supervisor_golden_run.py`) plus the affected packs and the whole
   supervisor suite, re-run at the final frozen identity (R247).
4. **Scope sanity:** allowed_paths are the golden-run pack (listed in case a re-run exposes
   an identity-stamp defect; **no behavioral edit is planned — a re-run-only unit is the
   goal**), the new `M0-T112-recertification.md` report, and
   `M0-T096-activation-package.md` for a **REFRESH-ONLY** edit of items 10–12
   (identity/evidence). No `tools/agent_supervisor/**` source is in scope: certification
   must not mutate what it certifies.
5. **Pinned residuals considered at this seam (all non-blocking, reviewer-converged):**
   the `_already_queued` digest-normalization note (stored post-builder summary digest vs
   raw notify-time digest — best-effort growth suppression for redaction/truncation-altered
   summaries; inherited S13.10 queue behavior, at-least-once preserved), the unit-I
   `live_observation.py:296` raw `source_record_key` one-liner, and the unit-K write-only
   boundary-queue notes. **Disposition: carried, not fixed here.** Fixing them requires
   supervisor-source edits outside this packet's allowed_paths and would move the very
   identity this unit freezes; they were unanimously judged non-blocking at the T111 delta
   re-attestations. They will be documented in the recertification report as known
   characteristics of the certified identity, with a follow-up task recommended after this
   unit (any post-certification supervisor change re-triggers R247 by rule).
6. **Sequencing discipline staged (R232/R246/R247):** the re-run happens AT the final
   frozen post-addition identity (supervisor material identity unchanged since the T111
   correction commit; control-plane commits do not move it); CI runs on the pushed SHA;
   ONLY AFTER this unit is accepted may the R187/R595 activation package be PRESENTED —
   presentation and activation remain owner-gated acts this unit never performs.
7. **Prohibitions staged (R248):** no continuous-mode activation, no live 4.8 bridge, no
   PR #241 touch, no Agent SDK admission, no new MCP servers, no global Claude settings
   modification, no owner-boundary crossing; supervisor stays SHADOW-ONLY; `.claude/hooks`
   untouchable (G5-gated, and not in scope).
8. **Environment discipline:** long pytest runs foreground-chunked (validator pack split
   4-way when the workstation is slow); never mutate the tree during a live suite; registry
   JSON LF; `modularity_check` after `git add`.

Verdict: **PASS** (administrative readiness; independent review comes at G3/G4/G5 + DCV).
