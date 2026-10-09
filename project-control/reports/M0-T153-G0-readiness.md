# G0 Readiness — M0-T153 (D-033 T-B: supervisor acceptance engine + independent-verifier seam)

**Recorder:** orchestrator (G0 administrative readiness gate, 2026-09-07 ~08:55Z).

- **Packet completeness:** `project-control/tasks/M0-T153.json` carries objective (design T-B
  slice + the two routed T-A advisories), business reason, explicit allowed_paths (6 files;
  loop.py forbidden — modularity ceiling), outputs, four documented test commands (mirroring
  the proven T-A shape), required gates G0/G2/G3/G5, reviewer roster (code-reviewer,
  security-reviewer, directive-compliance-verifier), and the proven DL-2 checkpoint-envelope
  contract note for the loop worker.
- **Dependency:** M0-T152 (T-A) ACCEPTED (166th, HEAD `307bf1d2` lineage; gates G0/G2/G3/G5 +
  DCV all PASS at `26693cf7`). The gate-wave engine and the freeze-rule D-033 recognition this
  task builds on are merged and baselined (3726/2/0).
- **Design authority:** `docs/SUPERVISOR_MANAGEMENT_LAYER_DESIGN.md` T-B section (accepted via
  M0-T150) — verifier-session dispatch, row transcription (worst-of dedup, 64k ceiling),
  accept() invocation preserving preconditions, producer!=verifier mutations, identity
  re-stamp on HEAD drift (item I3). Qualifying evidence: D-033-R002, D-033-R006 (freeze-rule
  section 3; D-033 recognition amendment live since cc25bdc1).
- **Advisories folded in (explicit scope):** G5 L1 (redact G2 report body before persist) and
  G3 D-2 (wire admit_verdict_file/verify_verdict_report into the live path or record the
  rationale) — both named in the packet objective/outputs.
- **Execution plan:** supervised loop run persistent-local-10 (limited-auto, certified
  wt-controller-src cwd, max-tasks 1), worktree wt-m0t153 at the acceptance HEAD with the
  synced CLAIMED packet blob.
- **Holds:** switch-gated DEFAULT OFF discipline unchanged; R595/Option-A owner-only; no
  push/PR #241; D-033-R005 prohibition rides the applicable set.

G0 outcome: **PASS** — packet is ready to claim for the supervised loop.
