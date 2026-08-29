# M0-T113 — G0 readiness (administrative; recorded at the claim seam)

Task: M0-T113 (unit N: R187/R595 limited-auto activation act + first-loop operation proof;
D-024 Amendment 9, rows R250–R260). Recorded by: orchestrator (fable-orchestrator-session),
2026-08-29, campaign seq 28. Supervisor-freeze qualifying evidence: **D-024-R250**.

1. **Authorization provenance (R250/R251):** the owner TYPED the activation authorization in
   the interactive session on 2026-08-29, immediately after the activation package was
   presented (seq 27). Captured verbatim as `source-009-amendment.md`; rows R250–R260;
   validator EXIT=0; capture committed and pushed at `a87b407` BEFORE any activation step
   (pre-action durability satisfied).
2. **Bootstrap Gate 0 (R125–R128):** passed at session start and re-verified: primary cwd IS
   `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `control/D-024-fable-codex-loop`,
   NO MCP tools attached, clean tree, local == origin.
3. **Dependencies:** M0-T112 `accepted` (the R247 certification this activation relies on);
   the activation package was PRESENTED at seq 27 before the owner authorized.
4. **Packet integrity:** path-free governance packet (`path_free_governance: true` — the act
   writes only NEW evidence reports; R258 prohibits touching certified supervisor code);
   directive_refs `D-024:ALL`; `evaluate_task_refs` ok=true, **11 applicable ids**
   (R250–R260), no missing/invalid/unresolved.
5. **Preflight staged (R252/R254/R259):** the unit proceeds strictly preflight-first — repo
   clean/synced; certified identity anchors intact at HEAD; CI 20/20 on the capture tip;
   executables verified; protected config + model-selection digests verified against
   `docs/CONTROLLER_UPDATE_RUNBOOK.md` §1; manifest recorded for THIS certified tree and
   `verify-controller` + `doctor` green — and on ANY mismatch it stops and reports exactly,
   with no improvisation and no partial activation.
6. **Exclusions re-affirmed (R257):** no autostart, no PR #241, no production/credentials/
   payments/legal, no OS-ACL change, no C1 canary, no Telegram live send, no natural-event
   graduation, no live 4.8 actuation (bridge stays shadow-only). The ONLY authorized new
   act is the certified item-3 start command with `--mode limited-auto
   --owner-enable-bounded-auto`.

Verdict: **PASS** (administrative readiness; independent review at G3/G4/G5 + DCV after the
act, on the recorded evidence).
