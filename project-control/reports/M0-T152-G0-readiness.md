# M0-T152 G0 readiness (administrative, orchestrator)

- **Task:** M0-T152 — D-033 T-A: gate-wave engine + owner-gated switch scaffold.
- **Authority:** D-033 (accepted design `docs/SUPERVISOR_MANAGEMENT_LAYER_DESIGN.md` §9 T-A);
  AD-093 qualifying evidence = D-033-R001/R003/R007 (requirement explicitly listed in an owner
  directive; cite in packet + commit per the freeze rule).
- **Security conditions attached (BLOCKING at acceptance):** M0-T150-G5-security.md F1 (machine
  allow-set on the controller's project_control surface) and F2 (forgery-resistant verdict→gate
  binding with mutation test); F3/F5/F6 folded into scenarios S4/S2-S3/S1; F4/F7 belong to T-C.
- **Packet completeness:** 7 acceptance scenarios incl. OFF==today mutation proof and the two
  HIGH blocking conditions; allowed_paths (5 tracked + 2 new files); transcript-cap-safe
  documented commands; reviewers code-reviewer / security-reviewer / directive-compliance-verifier
  (≠ producer); gates G0/G2/G3/G5; in-regime `D-033:ALL` with rows R001/R003/R005/R006/R007
  bound (validator exit 0).
- **Dispatch:** queued for the supervised loop (queue v4) per D-033-R009 — the loop builds its
  own management layer. Producer worktree `wt-m0t152`.
- **Result:** PASS — contractible; the loop worker may claim.
