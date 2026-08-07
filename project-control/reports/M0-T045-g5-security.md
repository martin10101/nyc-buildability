# G5 Security Review Gate Report — M0-T045 (R595 supervised rehearsal + Section 16.2 promotion evidence)

**Reviewer:** security-reviewer (independent, read-only). **Frozen reviewed SHA:** `f29decc` (code head `afc2da5`).
**Lane scope:** security only (G3 PASS covers correctness; G4 PASS covers QA/evidence integrity).

## Per-lane results (all PASS)
1. **Cross-process resume surface:** held prompt text parks ONLY in the sqlite journal (git-ignored, never committed; evidence carries digests + redaction_count/injection_labels, never raw text). Digest binding checked at resume (`digest_of(prompt) == approved_digest`, loop.py:2005) before any provider call; `approved_digest` written only by `approve_pending_prompt` (sole caller: the digest-bound CLI approval). Journal was already the trust domain for checkpoints/decisions/emergency-stop — no trust-boundary widening. See LOW-1.
2. **Privilege/activation:** SHADOW-ONLY intact — `_resume_forward`'s first statement is `assert_forwarding_allowed()` (shadow forwards nothing regardless of record validity); no activation flag flips; zero new subprocess/socket/eval/exec/shell primitives; only internal imports; forbidden paths untouched.
3. **Fail-closed:** emergency-stop checked FIRST in `_resume_approved_forward`, then last-trigger, record, prompt bytes, digest — all before the sender; six degenerate entries refuse with 0 provider calls; the 5.2/5.4 catch-all is DERIVED (`SECURITY_RELEVANT_CLASSES - explicit - owner_stop`), so a future class added to SECURITY_RELEVANT_CLASSES automatically fails TOWARD review, never Tier A; permission/hook Tier D owner-stop no review clears; estop overrides autostart (recovery snapshot: "autostart refused").
4. **Secrets/PII:** no real credentials in either diff or ANY committed evidence (only concatenation-built synthetic fixtures proving the redaction path, and the substring "token" in context_tokens telemetry); owner config referenced as a PATH only — no contents copied into evidence; sqlite journals excluded from git (hashes only).
5. **Supply chain:** zero new dependencies; no manifest/lockfile edits.
6. **Live-run posture:** exactly ONE forward (`run_r595_rehearsal_b/fwd/1/a4c3d170…`, id keyed to the operator-approved digest); throwaway workload (packet allowed_paths README.md + docs/** only; repo under Temp); no real-repo write surface; re-approval refused live.

## Findings
- **LOW-1 (pre-activation checklist item; does NOT block shadow-only acceptance):** park->approve integrity rests on the journal filesystem ACL, not the operator-named digest — `approve_pending_prompt` freezes `approved_digest = digest_of(parked prompt bytes)` without cross-checking the operator-supplied `--approve-prompt-digest` serialization against the prompt bytes. An attacker WITH JOURNAL WRITE who tampers the `prompt` field between park and approval gets tampered bytes forwarded under a self-consistent digest. Same access already forges checkpoints/decisions/flags — no new privilege escalation; SHADOW-ONLY forwards nothing regardless. **Before supervised/limited-auto activation:** bind the forwarded bytes to the operator-named approval at approval time (re-verify prompt <-> approval digest, or set approved_digest from the operator-supplied value). loop.py:626-654 + cli.py:1628-1662.
- **INFO-1:** `audit_chain_ok:false` in the sealed estop recovery snapshot — evidence-completeness artifact of the hard-killed run (G4's material finding; QA lane), not a defect in the reviewed commits; security-relevant estop behavior fully proven.
- **INFO-2:** rehearsal report header staleness (G3 INFO-2); documentation only.

No HIGH or MEDIUM findings. No secrets, no new dependencies, no activation weakening, no SHADOW-ONLY bypass.

**G5 VERDICT: PASS**
