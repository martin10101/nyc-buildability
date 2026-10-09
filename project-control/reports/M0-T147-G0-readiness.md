# M0-T147 G0 readiness (definition-of-ready) — 2026-09-06

Administrative G0 recorded by the orchestrator under D-032 R001/R005 (deficit-convergence
closure of the loop's blocking defect).

- **Failure surface bounded** (deficit-convergence rules 1–9): 4× reproduced ROTATE_SESSION
  across runs persistent-local-01/02/03, all with the same rotation_reason (reviewer execution
  environment failure); root cause proven by a minimal rule-7 probe at the exact reviewer argv
  on codex-cli 0.153.4/Windows: ALL command execution rejected ("blocked by policy"), exec tool
  string-only + PowerShell-wrapped, no file-read tool. The M0-T131 measured boundary (reads
  allowed, measured on 0.146.0) no longer holds; the contract's promise is false on the
  installed CLI.
- **Cluster is complete and minimal** (rule 10): one collector addition (`diff_content`) closes
  the only packet gap in the contract's live-verify list (touched-file content — branch/head/
  cleanliness/changed-files/diff-stat already collected); one contract rewrite aligns the
  instructions with the true boundary; tests prove both load-bearing. No schema change (rule 11);
  bounds enforced controller-side.
- **Scope**: 4 code/test paths + report; forbidden paths fence the rest of the supervisor.
- **Producer**: orchestrator under the D-032 R005 owner authorization (M0-T146 precedent);
  gates G0/G2/G3/G5 + DCV; freeze-rule qualifying evidence = D-032-R005 / D-024 source-054.
- **Directive refs**: D-032:ALL; resolver evaluation ok (sentinel-bound rows; empty applicable set).

Verdict: PASS — ready to claim.
