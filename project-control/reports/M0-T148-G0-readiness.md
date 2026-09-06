# M0-T148 G0 readiness (administrative, orchestrator)

- **Task:** M0-T148 — evidence-packet completeness repair (persistent-local-04 breaker convergence).
- **Authority:** owner directive D-032 Amendment 3 (D-032-R020, source-003-amendment.md,
  sha256 c49efd41...); mandatory method already run to evidence-freeze + bounded-cluster
  stage (`project-control/reports/D-032-pl04-packet-collection-convergence.md`).
- **Supervisor defect-lane qualifying evidence (AD-093 §2):** reproduced defect
  (offline packet build, convergence report §3: 0/9 deliverable content probes present,
  no failed_collections); inability to complete authorized product task M2-T020
  (4x REVISE → `circuit_breaker_hard_threshold`, audit seq 53/66/78/88, 92); live
  provider-boundary evidence from commissioning run persistent-local-04.
- **Packet completeness:** objective, business reason, 7 acceptance scenarios
  (S1-S7 incl. negative + mutation coverage), allowed_paths (7 files, all inside the
  supervisor lane + producer report), documented_test_commands (2 focused pytest
  suites), reviewers (code-reviewer, security-reviewer, directive-compliance-verifier;
  all ≠ producer backend-engineer), gates G0/G2/G3/G5 per the supervisor-freeze rule.
- **Directive regime:** in-regime, `D-032:ALL` stamped; registry validator exit 0 at
  capture commit `8f1af1a0`.
- **Dependencies:** none (the convergence record is committed at base `83594de2`;
  producer worktree `wt-m0t148` created at that SHA on branch
  `task/M0-T148-packet-completeness`).
- **Result:** PASS — the packet is contractible and the producer may claim.
