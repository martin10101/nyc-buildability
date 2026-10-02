# M0-T171 G2 — producer self-check after rework 1 (recorded by the orchestrator)

Head `bec407ae`; identity `f2d74128`.

Why: CI supervisor-bridge (windows-latest) failed `test_lock_error_fails_closed` at the first accept head (Windows raises PermissionError for a directory at the lock path, so the product refuses at once with slot_lock_error; POSIX refuses at the timeout with slot_lock_timeout). The premature acceptance (d6c47fd2) was reverted before merge, and the task walked awaiting_gate → rework → in_progress → submit.

Rework (producer commit f95b4e25, test-only): the test pins each platform's fail-closed reason code and asserts reservation is None. `review_slots.py` is byte-identical to the reviewed version.

Reproduced by the orchestrator: `python -m pytest -q tools/test_agent_supervisor_review_slots.py` → 13 passed. The Windows proof is CI supervisor-bridge at the pushed head.

Delta attestations: G3/G4 carry (M0-T171-G3G4-delta.md); G5 carries (M0-T171-G5-delta.md).

Follow-up (non-blocking, G3/G4 delta (d)): on Windows, acquire() refuses at once on a PermissionError. During contention with a delete-pending lock file, this may give a one-shot refusal where a short wait would do (liveness only, never over-admission). Optional hardening: retry PermissionError within the deadline on nt.

Self-check result: PASS.
