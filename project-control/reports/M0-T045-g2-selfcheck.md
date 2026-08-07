# M0-T045 G2 producer self-check (administrative record)

Producer self-checks completed before submit (recorded by the orchestrator; G2 never satisfies an independent gate):
- Increment 1 (hardening, `4db6a71`): producer ran the full suite -> 1307/2 (+36), validator exit 0; orchestrator reproduced 1307/2 independently before commit.
- Increment 2 (R595-F1 fix, `afc2da5`): producer ran the full suite -> 1317/2 (+10), validator exit 0; orchestrator reproduced 1317/2 independently before commit.
- Rehearsal legs self-verified at execution time from primary outputs (park state, digest, forward id, rotation record, estop recovery snapshot) before sealing; 26-file SHA-256 manifest computed at seal.
- Scope self-check: `git status`/`show --stat` confirmed only allowed paths touched by producer commits.

**G2 result: PASS (self-check complete; independent gates G3/G4/G5 recorded separately).**
