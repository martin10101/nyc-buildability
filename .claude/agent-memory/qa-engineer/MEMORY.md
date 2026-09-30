# Memory index

- [Supervisor estop audit-chain fork](supervisor-estop-audit-fork.md) — emergency-stop is a concurrent out-of-band writer; it forks the audit hash-chain (duplicate seq), which verify_chain()/recovery-status honestly report as audit_chain_ok:false — by design, fail-closed, not a defect
