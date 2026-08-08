# LIVE ACTIVATION PROOF — controller config PROTECTED (D-010 R208–R211; M0-T046 AS-4 live leg)

Orchestrator-captured 2026-08-08, UNELEVATED, immediately after the owner's elevated apply of the
merged reviewed script blob `b6ee6589d93b4cd95283ce6d45c22f7010aba56a` (M0-T051) under the R195
dry-run-first rule. Raw doctor JSON: `M0-T036-PROTECTED-live-proof.json` (committed alongside).

## All eight owner-required conditions PASS (R209)

| Condition | Result |
|---|---|
| `controller_config_acl.protected == true` | **PASS** |
| `controller_config_acl.state == "PROTECTED"` | **PASS** |
| `controller_config_acl.file.state == "PROTECTED"` | **PASS** |
| `controller_config_acl.parent.state == "PROTECTED"` | **PASS** |
| Protected config remains readable (unelevated) | **PASS** (712 bytes read) |
| Config SHA-256 unchanged | **PASS** — `29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb` |
| `model_selection.toml` writable by the ordinary unelevated account | **PASS** (r+b open succeeded at `C:\SupervisorController\model_selection.toml`; no bytes written) |
| No activation has occurred yet | **PASS** — SHADOW-ONLY posture intact; no activation record in the ledger; the R131 owner-typed decision has not been given; M2-T015/T016 remain backlog/held |

Doctor overall `ok: true`; exit 0. Command (exact, unelevated):
`python -m tools.agent_supervisor doctor --config "C:\Program Files\SupervisorConfig\config.toml" --model-selection "C:\SupervisorController\model_selection.toml" --json`

## Final live posture (owner-observed, orchestrator-confirmed via doctor evidence)

- FILE `C:\Program Files\SupervisorConfig\config.toml`: `MLFLL:(RX)`, `SYSTEM:(F)`,
  `Administrators:(F)` — the former `Authenticated Users:(M)` ACE is GONE.
- PARENT `C:\Program Files\SupervisorConfig`: `MLFLL:(RX)`, `SYSTEM:(OI)(CI)(F)`,
  `Administrators:(OI)(CI)(F)`.
- This closes the M0-T036 activation-checklist item "elevated ACL apply + live PROTECTED capture"
  (M0-T046 AS-4 live leg / R128 UAC clause) after three owner-caught script defects were fixed,
  reviewed, and merged (M0-T049 parser, M0-T050 argument-drop, M0-T051 explicit-ACE survival).

## Standing residual disclosures carried to the activation decision (unchanged)

G5 N-4 (full-local-write chain rewrite — R140-excluded, Phase 3 Option A), G5 N-5 (same-run
approved-content replay — narrowed), G3 MINOR-2 (fail-closed ambiguity edge) — see
`M0-T048-g5-rework-review.md` / `M0-T048-g3-rework-review.md` verbatim.

⛔ Nothing is activated by this proof. Activation requires the owner-typed decision line (R131);
M2-T015/T016 stay held until it is typed (R213).
