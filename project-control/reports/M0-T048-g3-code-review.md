# G3 Code Review Gate Report — M0-T048 (owner am.14: close the G5-C2 residual)

**Reviewer:** code-reviewer (independent, read-only). **Lane:** G3 correctness / contracts / error-paths / tests (G5 owns security; G4 owns QA/evidence).

## Frozen reviewed identity (confirmed with `git rev-parse`)

- Code worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T048-c2-close`, HEAD **`ec0f55d28da90d57467321ad65c922fdde09f043`** — matches frozen ✓
- Control-plane primary checkout `...\nyc-development-feasibility-claude-pack`, branch `control/M0-T048-c2-close` @ **`ce432c1de851bc54c09d84d1adfae96c490d2fe1`** — matches frozen ✓
- Base `origin/main` = **`9c2ec252b509ddf6bb067325c6aa28c2cdc6ff4d`** (`9c2ec25`, contains accepted M0-T046) ✓. Diff = `git diff 9c2ec25..ec0f55d` → 8 files, +829/−153.

## Evidence reproduced in-sandbox

- `python -m pytest tools/test_agent_supervisor_c2_binding.py tools/test_agent_supervisor_park_approve_binding.py tools/test_agent_supervisor_pending_prompt.py tools/test_agent_supervisor_reviewer.py -q` → **112 passed in 16.72s** (matches expected 112; orchestrator-captured full suite 1374 passed / 2 skipped accepted as captured evidence).
- `git diff --name-only 9c2ec25..ec0f55d` → 8 files, all inside `allowed_paths` (`tools/agent_supervisor/{cli,codex_reviewer,loop}.py`, 4 `tools/test_agent_supervisor_*.py`, `project-control/reports/M0-T048-producer-report.md`); no forbidden path touched.
- Adversarial spot-checks (inline, no writes): park-stage two-field forgery (`prompt`+`prompt_bytes_digest`) → `verify_covered_instruction` raises `pending_prompt_tampered` ✓; post-approval `(approved_instruction, approved_digest)` self-consistent forgery → **NOT caught**, injected marker present in returned body (see MAJOR-1).

---

## Scope-item findings

### 1. Deterministic body + canonicalisation equivalence — PASS (crypto-sound)

`build_forwarded_prompt` (codex_reviewer.py:663) is now a pure, timestamp-free function of exactly the five `approval_digest`-covered fields. I verified byte-for-byte that its canonicalisation is **identical** to `approval_digest` (loop.py:567-582): paths `sorted(str(p) for p in …)`, stops `sorted(str(s) for s in …)`, action `.strip()`, task_id/stage raw; the `FORWARDED AT:` clock and the volatile `packet_reference` are removed from the body. Because both functions collapse the **same** equivalence classes (path order, stop order, action whitespace), `approval_digest(**fields) == operator_digest` cryptographically pins `build_forwarded_prompt(**fields)` to the operator-approved body (modulo SHA-256 collision). No divergence class exists → neither an availability false-refusal nor a bypass on this axis. `stamp_forwarded_at` only appends the clock at forward time and is excluded from the binding; `forward_message_id`/`_resume_forward` key exactly-once identity on the approval digest, so the clock cannot affect verified semantics or double-send. **Sound.**

### 2. Binding chain end-to-end — PASS for park→approve; MAJOR residual at approve→resume

I traced park (loop.py:1788-1866) → CLI `verify_covered_instruction` before any transition (cli.py:1704-1726) → `approve_pending_prompt` binds `approved_digest = approval_binding` = the **operator-typed** digest and persists `record["prompt"] = expected_body` (the reconstruction, never the parked bytes) (loop.py:744-758) → `_resume_approved_forward` reconstructs+re-verifies and forwards `stamp_forwarded_at(body)` (loop.py:2132-2154). The forwarded content is always the reconstruction from `approved_instruction`, never the mutable `prompt` bytes. The M0-T046 park byte anchor is retained as defense-in-depth and cross-checked (loop.py:684-693); sealed hash-chained refusals retained; the old `digest_of(prompt)==approved_digest` resume check is replaced by the strictly stronger reconstruction check. **However**, the scope directive "no path binds to a journal-resident-only value" is **not** fully satisfied at the cross-process resume (MAJOR-1 below).

### 3. Old-shape refusal (AS-6) — PASS (verified in code, not just tests)

`verify_covered_instruction` refuses `pending_prompt_uncovered` when `approved_instruction` is absent/not a `Mapping` (loop.py:659-664) **before** any anchor/journal comparison — there is no fallback to journal-resident-only verification. Confirmed reachable on all three paths: CLI approve (cli.py:1707), `approve_pending_prompt` (loop.py:747), and `_resume_approved_forward` (loop.py:2138). Malformed instruction (missing key / non-iterable) → `KeyError/TypeError` caught → `pending_prompt_uncovered` (loop.py:666-676). Covered-field tamper that breaks the digest → `pending_prompt_uncovered` (loop.py:677-682).

### 4. Error paths — PASS

Distinct honest reason codes: `pending_prompt_uncovered` (missing/malformed/digest-mismatch) vs `pending_prompt_tampered` (anchor / prompt-vs-reconstruction mismatch). No silent catch — the CLI seals an `operator_resume_pending_prompt_refused` audit event carrying `exc.code` and returns 1 with no state change; `_resume_approved_forward` re-raises as `forwarded_prompt_unavailable` preserving `exc.message`. `str(approved_digest or "")` at resume makes a missing/blank approved digest refuse (empty never matches any real digest).

### 5. Tests — PASS (non-vacuous, no weakened prior assertions)

Read `test_agent_supervisor_c2_binding.py` in full (11 tests): AS-1 at approve (`pending_prompt_tampered`, no state change, single sealed refusal, `verify_chain().ok`) and at resume (`forwarded_prompt_unavailable`, `provider_calls == 0`, chain verifies); non-vacuity test asserts the forgery satisfies **both** pre-fix predicates (anchor match + operator-digest match) and that the reconstruction can never carry the marker — a valid logical non-vacuity proof (it does not execute deleted pre-fix code, and the producer report §5 states this accurately). The 3 modified test files were **strengthened**, not weakened: `approved_digest` assertions now bind to the operator digest (was the byte anchor); `TamperAfterApproval` still tampers the approved prompt and still expects refusal; the `+78`-net `pending_prompt` changes are fixture migrations to `covered_pending()` plus the operator-digest assertions — every prior tamper/exactly-once assertion is preserved.

### 6. Packet conformance / R140 — PASS

Diff confined to `allowed_paths`; no forbidden path. All `build_forwarded_prompt` callers use the new keyword-only signature (no stale positional caller). `LoopConfig.packet_reference` (loop.py:220) is left in place, dead — removing it would be broader cleanup barred by R140; it is unreferenced by the body and poses no correctness hazard. `assert_forwarding_allowed` remains called unchanged in both forward paths (SHADOW/activation posture intact).

---

## Findings (severity-ranked)

**MAJOR-1 — the cross-process resume still roots trust in a mutable journal field (`approved_digest`); a post-approval `(approved_instruction, approved_digest)` two-field forgery forwards altered content.**
At resume, `_resume_approved_forward` passes `operator_digest = str(record.get("approved_digest") or "")` — a journal-resident value with **no** cross-check against the sealed, hash-chained `operator_resume_pending_prompt` audit event (whose `input_digest`/`prompt_digest` durably record the digest the operator actually approved). An attacker with journal write, **after** a genuine approval (state legitimately at `FORWARD_PROMPT`, `last_trigger == owner_approved_pending_prompt`), who rewrites `approved_instruction` (injecting into a covered field, e.g. `requested_action`) **and** `approved_digest = approval_digest(forged_instruction)` self-consistently, passes `verify_covered_instruction` and gets the forged body forwarded. Reproduced (function level):
- `verify_covered_instruction(forged_instr, forged_digest, forged_body, digest_of(forged_body))` returns a body containing the injected marker; `operator_approved_digest e2af931bdf48` vs `forged_self_consistent_digest 916f1ed7b378`.

Assessment: this is the **same class** as the C2 finding this task exists to close ("bind … rather than relying solely on mutable journal fields"), **relocated** from the park→approve window to the approve→resume window. It is **NOT** a regression (M0-T046 had the equivalent post-approval `prompt`+`approved_digest` forgery), and it is **outside the owner's literal required property** (R136/AS-1 name `prompt_bytes_digest` and "the parked prompt bytes" — the park stage — which is genuinely closed). But it directly matches G3 scope item #2 ("no path binds to a journal-resident-only value"), which the resume path violates. A minimal remedy exists within the fix's spirit: at resume, cross-check `approved_digest` against the sealed audit event's recorded operator digest (raising the bar to also require forging the hash-chain, which `verify_chain` detects). **Disposition:** this is a security-lane/DCV call — I route MAJOR-1 to **G5** (bypass adjudication) and **DCV** (whether R136's "rather than relying solely on mutable journal fields" is met given the resume path), and recommend it be surfaced verbatim to the owner in the activation decision exactly as the original C2 was. It does **not** break any packet AS scenario as written, the owner's mandatory AS-1 test, or any directive requirement's literal text; therefore I do not convert it into a G3 correctness FAIL, but it is **material and should block activation** until adjudicated.

**MINOR-1 — AS-4 / R139c coverage is narrower than its general wording.** The post-approval test forges only `prompt`+`prompt_bytes_digest` (caught). "Post-approval tampering still refuses" is proven for that variant, not for MAJOR-1's variant. The producer/tests do **not** overclaim (evidence map maps R139c only to the demonstrated test), so this is a coverage gap, not a false claim.

**INFO-1 — `_resume_approved_forward` return fallback `forward.sent_prompt or prompt`** (loop.py:2173) returns the raw parked `prompt` on the duplicate-suppressed path rather than the verified `body`; harmless because `verify_covered_instruction` already proved `digest_of(prompt) == digest_of(expected_body)` (bytes equal) before that point, and it affects only the in-process continuation value, not the durable send. No action needed.

**INFO-2 — `packet_reference` removed from forwarded text** slightly reduces in-prompt provenance for the downstream agent; provenance remains in the outbox payload (`task_id`, `reviewed_checkpoint_id`) and audit trail. Honestly disclosed (producer report §8.2); a G4 evidence question, not a G3 defect.

---

## Per-AS conformance vs the PACKET text

- **AS-1** (primary adversarial, R136/R138, owner-verbatim 7-step): **PASS.** Park authentic → mutate BOTH `prompt`+`prompt_bytes_digest`, leave operator digest → approve/resume FAIL CLOSED (`pending_prompt_tampered`), `provider_calls == 0`, single sealed hash-chained refusal, chain verifies, no state change, record not approved. Non-vacuous (both pre-fix predicates pass on the forgery; reconstruction never carries the marker).
- **AS-2** (R139a happy path): **PASS.** Real loop forwards exactly once; forwarded body minus the `FORWARDED AT:` stamp == `build_forwarded_prompt(**instruction)`, i.e. verifies against the approval-covered binding.
- **AS-3** (R137/R139b clock invariant): **PASS.** Executable ClockInvariant test; `approval_digest` computed from the instruction, `verify_covered_instruction` reconstructs the timestamp-free body and ignores the stamp.
- **AS-4** (R139c post-approval tamper): **PASS as written** (forge `prompt`+`prompt_bytes_digest` post-approval → `forwarded_prompt_unavailable`, no provider). See MINOR-1 / MAJOR-1 for the uncovered variant.
- **AS-5** (R139d/R140 prohibition): **PASS.** No authority/forwarding-guard/activation/tier change; `assert_forwarding_allowed` unchanged; diff confined to allowed_paths; dead `packet_reference` left in place per R140; zero new dependencies.
- **AS-6** (negative/degenerate): **PASS.** Old-shape (no `approved_instruction`), malformed, and covered-field-mismatch all refuse `pending_prompt_uncovered`; byte tamper refuses `pending_prompt_tampered` — distinct honest codes, no journal-resident-only fallback, verified in code.

## Required corrections attached to this PASS

1. **(BLOCKING for supervised-auto ACTIVATION, not for this task's G3 correctness gate) — MAJOR-1:** G5 and DCV must independently adjudicate the post-approval `(approved_instruction, approved_digest)` resume-window forgery and whether R136's "rather than relying solely on mutable journal fields" is satisfied for the cross-process resume; if judged in-scope, anchor the resume verification's operator digest to the sealed audit record (or the FORWARD_PROMPT transition detail) rather than the mutable `approved_digest`. Surface verbatim to the owner in the activation decision, mirroring the original C2 handling.

No secrets/PII introduced; no new dependencies; no manifest/lockfile edits; no SHADOW/activation weakening; canonicalisation verified sound.

**G3 VERDICT: PASS** (with MAJOR-1 attached as a required, activation-blocking disclosure to be adjudicated by the G5 security and directive-compliance lanes; MINOR-1/INFO advisory).
