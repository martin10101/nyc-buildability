# M0-T086 — G0 readiness (administrative)

Task: D-024 A1 — live baseline, installed-capability probes, deterministic fixtures.
Recorded by: orchestrator (G0 administrative class). Date: 2026-08-25.

- Directive: D-024 captured at `0d9f6b1` (v4, sha256 `0611bb45…`, 128 requirements); campaign
  re-sized to 11 tasks; this is the first unit (no dependencies).
- Packet valid: `evaluate_task_refs` ok:True, applicable=33, missing=[], unresolved=[] (verified at
  capture). Governance scope binding present in the D-024 manifest (s19/R118 guard satisfied —
  proven by the successful M0-T097 claim under the same guard).
- Bootstrap Gate 0 (D-024-R125–R128) passed by this session before any write: primary cwd
  `ctl24`, branch `control/D-024-fable-codex-loop`, `/mcp` = no servers; recorded in the D-024
  manifest audit_log.
- Scope collision-free: allowed_paths (supervisor fixtures dir, capability_probe module + test,
  supervisor-freeze rule, two M0-T086 reports) overlap no claimed task; M0-T087..T096 backlog;
  M0-T097 accepted (its paths disjoint).
- Supervisor-freeze (AD-093): this task carries the freeze-rule amendment recognizing cited D-024
  requirement IDs as qualifying evidence, authorized by D-024 §1 ("amend or supersede the rule
  transparently under this directive's authority"); qualifying evidence for this task = D-024-R099
  (Phase A capability fixtures requirement, explicitly listed in the directive).
- Pre-claim live probes already on file (scratchpad): `claude 2.1.220`, `codex-cli 0.146.0`, dual
  claude install (PATH-order fact to fixture).
- Blockers: none. Dependencies: none.

Result: PASS — backlog → ready.
