# M0-T112 — G2 producer self-check (orchestrator-as-producer, certification unit)

Task: M0-T112 (unit M, final golden re-certification; rows R231/R232/R246/R247/R248/R249).
Producer: fable-orchestrator-session. Supervisor-freeze qualifying evidence: **D-024-R247**.

1. **Scope check:** every file this unit wrote is inside allowed_paths or is a
   control-plane record the orchestrator alone writes: `M0-T112-recertification.md` (packet
   output), `M0-T096-activation-package.md` (REFRESH-ONLY, items 10–12 + the Amendment-8
   banner it governs), `M0-T112-G0-readiness.md`/this file/the evidence map (gate + submit
   evidence), and `project-control/{tasks,gates,state}` records. The golden-run pack was
   **NOT edited** (re-run only; blob `d2946392f1c1` unchanged). Zero changes under
   `tools/**`, `apps/**`, `services/**`, `.claude/**`.
2. **Certification completeness vs the packet:** FULL golden-run pack re-run (40/40);
   affected packs re-run (operator-channel, codex-channel K-pack, telegram L-pack,
   adversarial, endurance, phase1, reviewer — 493/493; notifications coverage lives inside
   the telegram/adversarial/endurance packs, verified by grep before the runs); WHOLE
   supervisor suite re-run as the freeze baseline (59 files, 4 foreground chunks:
   677+724+683+610 = 2,694 passed, 2 skipped, 0 failed); CI 20-check run on the pushed
   certification tip (pinned in progress_log at the submit seam). All runs executed at the
   frozen identity with a clean code tree; nothing mutated during any live suite.
3. **Identity discipline:** all suite runs happened at run head `a4f94b7`; the pushed tip
   adds only control-plane/report commits, so the supervisor material identity
   (`8574c58`, tree `132e698c…`) is IDENTICAL at the run head and the reviewed tip.
   Baseline delta (+4 tests vs the seq-24 figure) reconciled exactly to the accepted
   L-pack correction tests — no unexplained drift, nothing removed.
4. **Sequencing/prohibitions:** no activation, no presentation of the activation package
   (its banner explicitly conditions presentability on THIS unit's acceptance), no PR #241
   touch, no new dependency, no MCP/global-settings/Agent-SDK surface, supervisor
   SHADOW-ONLY. Residuals carried, not fixed (outside allowed_paths; documented §5 of the
   recertification report with the R247 re-trigger warning).
5. **Evidence map:** all 6 applicable rows covered (resolver-confirmed set at claim;
   no selective citation; two rows discharged at capture and marked as such).

Self-check verdict: **PASS** — ready for independent G3/G4/G5 + DCV at the frozen tip.
