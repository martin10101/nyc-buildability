# CI evidence — M4-T012 + M4-T015 material heads (orchestrator gh capture)

Captured by the orchestrator per the ADR-005 evidence-capture division (the DCV
verifier's sandbox could not query gh; this record is the in-repo artifact its
verification rows corroborate against). Repo: martin10101/nyc-buildability, branch
candidate/D-024-mrl-option-b. Query: `gh run list --branch candidate/D-024-mrl-option-b
--json headSha,status,conclusion,workflowName` (BOM-safe decode), 2026-09-13.

| head SHA | workflow | conclusion | meaning |
|---|---|---|---|
| dd7c8b74 | CI | **failure** | M4-T012 first capture: api job failed on the Ruff step with exactly the 6 findings G4 reproduced (5x E501 + 1x F841 in test_r1_r2_height_setback.py); all 17 other jobs success. Run id 34744616735; failing-job log excerpt verified by orchestrator (`gh run view 34744616735 --log-failed`). |
| dd7c8b74 | secret-scan / context-budget | success | — |
| efa0f268 | CI / secret-scan / context-budget | success | pre-capture control-plane baseline green |
| 8538c272 | CI | **success** | THE material head for both tasks (M4-T012 G4-arc rework + M4-T015 capture): all 18 jobs green, api job (ruff + pytest) included. |
| 8538c272 | secret-scan / context-budget | success | — |
| b3bc8368 | (runs triggered on push) | report-only delta | control-plane + report-text commit; no services/api or web material change vs 8538c272. |

The G4 gate arc (FAIL at dd7c8b74 → rework 4f8b093f → PASS attestation) matches these
conclusions exactly: the reviewer predicted the Ruff-step failure from config before the
run concluded, and the rework head is green.
