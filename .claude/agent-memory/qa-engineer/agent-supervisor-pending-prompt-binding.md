---
name: agent-supervisor-pending-prompt-binding
description: How the supervised park->approve->resume->forward prompt binding works post-M0-T048, and how to independently non-vacuity-test it
metadata:
  type: reference
---

Supervised-loop pending-prompt binding (tools/agent_supervisor/) after M0-T048 (D-010 am.14, closes G5-C2).

**Binding model (verify before relying — read loop.py `verify_covered_instruction`, `approval_digest`, `build_forwarded_prompt`, `approve_pending_prompt`):**
- The forwarded body is a DETERMINISTIC, timestamp-free pure function of the 5 approval-covered fields (`task_id, stage, allowed_paths, requested_action, stop_conditions`), canonicalised identically to `approval_digest` (sorted paths/stops, stripped action, raw task_id/stage). `stamp_forwarded_at` appends the `FORWARDED AT:` clock only at forward time, excluded from the binding.
- Real binding = `approval_digest(approved_instruction) == operator-named digest` AND `digest_of(prompt) == digest_of(reconstruction)`. The park-time byte anchor `prompt_bytes_digest` is now OPTIONAL defense-in-depth — the APPROVED record does NOT carry it, so `verify_covered_instruction` skips the anchor branch when anchor is absent.
- `approved_digest` binds to the OPERATOR-NAMED digest itself, not a journal-resident byte anchor. Removed reason code `pending_prompt_unanchored`; new codes `pending_prompt_uncovered` (missing/malformed/non-reproducing instruction) vs `pending_prompt_tampered` (bytes/anchor mismatch).

**Non-vacuity mutation technique (proved the fix load-bearing without repo edits):** monkeypatch BOTH `loop.verify_covered_instruction` and `cli.verify_covered_instruction` to a pre-fix anchor-only emulation (`return prompt if digest_of(prompt)==anchor else raise`), then run `tools/test_agent_supervisor_c2_binding.py` via unittest loader. Under pre-fix the two-field-forgery tests turn RED: `test_two_field_forgery_at_approve` returns CLI code 0 (forgery approved), `test_..._after_approval` raises no LoopError (forgery forwarded). ClockInvariant/PostureUnchanged stay green. Note HappyPath red under the emulation is an artifact (emulation demands an anchor the approved record no longer carries), not a signal.

**Audit posture nuance:** the APPROVE path (cli `cmd_resume_pending_prompt`) writes a sealed hash-chained `operator_resume_pending_prompt_refused` event on refusal; the FORWARD path (`_resume_approved_forward`) raises `forwarded_prompt_unavailable` and halts without a dedicated audit event (chain stays intact). audit_log.py is a genuine prev_digest/sha256 chain with truncation detection — unchanged by M0-T048.
