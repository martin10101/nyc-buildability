# M0-T048 — G5 security review (RERUN, rework delta) — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel
(transport entity-decoding only: `&lt;`→`<`, `&gt;`→`>`). Reviewer: security-reviewer
(independent, read-only; the original C2 finder). Frozen review identity
`fee612ae724085576aad23c0fd1d387fa89e800d`; code identity `9c450a5`. Recorded by the
orchestrator 2026-08-08.

---

All checks complete. I have everything needed to rule. Here is my full G5 rerun report.

---

# G5 Security Review Gate Report (RERUN) — M0-T048 rework: anchor cross-process resume to the sealed operator-approval audit evidence (owner D-010 source-015, R144–R154; closes G3 MAJOR-1)

**Reviewer:** security-reviewer (independent, read-only). I am the original C2 finder and previously ruled C2 CLOSED with INFO N-1 flagging exactly the post-approval `approved_digest`+`approved_instruction` resume-window forgery. The owner adjudicated that shape (G3 MAJOR-1) and ordered this bounded fix. This rerun re-attacks the design and re-rules N-1.

## Frozen reviewed identity (reconciled)
- Task-stated frozen identity: control-branch merge `fee612ae724085576aad23c0fd1d387fa89e800d` (`fee612a`). Confirmed it exists and is an ancestor of the current checkout.
- Current primary checkout HEAD: `9119934188abc4b36872584c99514c99dcdcc228` on `control/M0-T048-c2-close`. HEAD is 2 commits **ahead** of the frozen SHA: `fcdef80` (resubmit marker) and `9119934` (source-016 directive capture).
- **Reviewed-source identity verified byte-identical:** `git diff --stat fee612a..HEAD -- tools/` is **empty** — the two later commits touch only control-plane files (`directives/`, `state.json`, `tasks/M0-T048.json`). Everything I read from the working tree is the frozen-identity source. No advisory-only reliance.
- Rework code delta = task commit `9c450a5` (ancestor of both `fee612a` and HEAD): `tools/agent_supervisor/loop.py` (+138), `tools/test_agent_supervisor_audit_anchor.py` (+288, new), `tools/test_agent_supervisor_pending_prompt.py` (+8, setup-only), producer report. No other source touched (`codex_reviewer.py`, `cli.py`, `audit_log.py` unchanged by the rework → N-2/N-3 carry unchanged).

## Evidence reproduced in-sandbox
- Targeted pack: `python -m pytest tools/test_agent_supervisor_audit_anchor.py tools/test_agent_supervisor_c2_binding.py tools/test_agent_supervisor_park_approve_binding.py tools/test_agent_supervisor_pending_prompt.py tools/test_agent_supervisor_reviewer.py -q` → **118 passed in 21.83s**.
- Full supervisor suite: `python -m pytest tools/test_agent_supervisor_*.py -q` → **1380 passed, 2 skipped in 120.12s** — matches the orchestrator-reported 1380/2.
- The 2 skips are environment-conditional on the Windows sandbox, not stale and not masking rework behavior: `test_agent_supervisor_policy.py:449` (symlink-escape test; skips on `WinError 1314` no-symlink-privilege — runs on POSIX CI) and `test_agent_supervisor_process.py:448` (POSIX-only guard). Neither is in the reworked path.
- Rework posture scan: `git show 9c450a5 -- .../loop.py | grep '^+' | grep -iE 'assert_forwarding_allowed|forwards=|activate|supervised_auto|tier_|autonomy|SHADOW|_guard|subprocess|socket|urllib|eval(|exec(|os.system|requests.|http'` → **no matches**. No posture, activation, or network primitive introduced.

---

## RULING ON THE CENTRAL SECURITY QUESTION — the resume-window forgery class is now CLOSED (within the owner-set threat model)

**Owner property (source-015):** after a genuine approval, the resume path must NOT trust the mutable journal `approved_digest` as the sole record of what the operator approved; at resume, cross-check it against the already-sealed/hash-chained operator-approval audit evidence; fail closed; zero provider calls; durably record the refusal.

**Chain of trust the rework establishes (verified against source):**
1. Forwarded body = reconstruction from the journal `approved_instruction` (`verify_covered_instruction`, loop.py:2276), which must reproduce the journal `approved_digest` — second-preimage-hard (the C2 binding, prior task).
2. **NEW:** the journal `approved_digest` must equal the `input_digest` of a sealed `operator_resume_pending_prompt`/`decision="approve"` event for this `run_id`, in a chain that `verify_chain()` accepts (`verify_approved_digest_against_audit`, loop.py:714–795; guard at loop.py:2260–2269, inserted BEFORE `verify_covered_instruction` and BEFORE any forward).
3. That sealed `input_digest` is the operator-typed value: the CLI refuses unless `supplied == recorded` (cli.py:1688) and then seals `input_digest=recorded, decision="approve"` (cli.py:1736–1742). The event lives in the append-only hash chain (audit_log.py).

So the forwarded content is transitively pinned to the operator-typed digest that is **sealed in the hash chain, not the mutable journal**. The owner adversarial test (genuine approval → self-consistently forge `approved_instruction`+`approved_digest`+`prompt`+`prompt_bytes_digest` → leave the sealed chain unchanged → resume) fails closed: the forged `approved_digest = approval_digest(malicious)` cannot equal the genuine sealed `input_digest` without a SHA-256 second preimage → `approved_digest_audit_mismatch` → `forwarded_prompt_unavailable`, `provider_calls == 0`, outbox empty, sealed `cross_process_resume_refused` with `reason=approved_digest_audit_mismatch`, chain still valid. Reproduced (`test_two_field_plus_digest_forgery_fails_closed_no_provider`). Non-vacuity is proven independently: `test_non_vacuity_reconstruction_check_alone_would_forward` shows the C2 reconstruction check ALONE returns the malicious body; `test_red_when_crosscheck_disabled` monkeypatches the new function to a no-op and the injected `EXFILTRATE ALL SECRETS` body reaches the outbox — i.e., the refusal is caused by the new cross-check, not an incidental guard.

### Attack analysis (each charge dimension)

- **Second-preimage / canonicalisation on the digest comparison — SAFE.** The audit cross-check is a plain string equality of two hex SHA-256 strings (`input_digest == approved_digest`, loop.py:782); there is no re-hash and thus no canonicalisation surface in the comparison itself. The `approved_digest`→body binding it relies on uses the shared `canonical_json` (sorted keys, UTF-8) between `approval_digest` and `build_forwarded_prompt` already ruled injective-enough in my prior report; `input_digest` is the operator-typed digest sealed verbatim.
- **Event-selection confusion — SAFE against injection.** Filter = `event_type==operator_resume_pending_prompt` AND `decision=="approve"` AND `run_id==self.run_id`, then `input_digest==approved_digest`, then `missing`/`mismatch`/`ambiguous` disambiguation (loop.py:770–795).
  - *Refuse-then-approve / self-vouching:* the sealed refusal is `decision="refuse"` (loop.py:2192) and the refused approval attempt is `operator_resume_pending_prompt_refused` (cli.py:1712) — both excluded by the `approve` filter, so a refusal can never vouch for a forward. A later emergency stop is honored first (loop.py:2222) before the cross-check.
  - *Cross-run replay / reused run_id / approve-from-a-different-prompt:* to have any sealed `approve` event vouch, the attacker needs one whose `input_digest` equals their target digest. **The operator only ever seals genuine content**, so no sealed event names an attacker-chosen (injected) digest — cross-run/reused-run_id manipulation cannot manufacture one. Duplicate/replayed approvals of the same digest fail `ambiguous` (loop.py:790; `test_ambiguous_approval_events_refuse`); an approval the chain does not hold fails `missing` (`test_missing_approval_event_refuses`). The injection class is closed. (Residual replay of *operator-approved* content within one run is discussed as N-5 — not injection, pre-existing, and strictly narrowed by this rework.)
- **TOCTOU between cross-check and forward — SAFE.** The path is single-process synchronous. `record` (loop.py:2235) and `approved_digest` (2243) are captured once; the cross-check, `verify_covered_instruction`, and `_resume_forward` all consume those same captured in-memory values — the journal is not re-read between check and use. A concurrent external on-disk writer cannot change the already-captured snapshot the forward is built from.
- **Downgrade paths — none reach forward.** The guard is unconditional (no config flag bypasses it). `audit is None` (audit disabled/unavailable) → `approved_digest_audit_unavailable` refuse (loop.py:743). Old-shape/empty `approved_digest` → `str(... or "")` → no genuine approval has an empty `input_digest` → `mismatch`/`missing` refuse. Chain unreadable/tampered/forked/truncated → `approval_audit_unreadable` / `approval_audit_chain_invalid` refuse (loop.py:749–762). No configuration reaches the forward without a passing cross-check.

---

## Per-charge findings

**1. Threat-model adjudication:** within the owner-set journal-write-only model (attacker mutates journal fields self-consistently after a genuine approval; sealed chain unchanged), the resume-window forgery class is **CLOSED**. All second-preimage, event-selection, TOCTOU, and downgrade angles fail closed (above).

**2. Remaining trust boundary (residual for the activation record):** an adversary with **full local write** (journal + audit file + sidecar head anchor) can, because there is no signing (R140), correctly append or rewrite the hash chain — recomputing `prev_digest`/`digest` (no secret is involved) and updating `<log>.head.json` — so `verify_chain()` would accept a forged `operator_resume_pending_prompt`/`approve` event naming an attacker digest, and the cross-check would then vouch for forged content. This is the **standing trust-domain limit**, explicitly documented by the module itself (audit_log.py:24–29: the sidecar head is "a strictly weaker, same-machine anchor"; true external anchoring — Option A, push the chain head to a dedicated `supervisor-audit-anchor` branch with controller-held credentials — is deferred to Phase 3). Closing it requires exactly what R140 forbids for this task (journal/audit signing, PKI, new infrastructure). It is therefore **outside this task's owner-set boundary**, and the rework meaningfully raises the bar from "flip one journal field" (the MAJOR-1 hole) to "rewrite/extend the hash-chained audit log and its sidecar anchor." The supervisor is SHADOW-ONLY (forwards nothing in production) pending R595 activation, so this residual has no live-forwarding exposure today. Recorded here for the activation decision (N-4).

**3. Fail-closed completeness:** no fail-open or warn-only path. `verify_approved_digest_against_audit` has exactly six terminal outcomes, all `raise LoopError`, plus the success return; `verify_chain`/`read_all` exceptions are caught and converted to fail-closed `LoopError` (loop.py:749–769). The guard's `except LoopError` seals then re-raises (loop.py:2263–2269). Exception-safety: if sealing raised anything other than `AuditChainError`, it would **propagate out** of `_resume_approved_forward` (it is not caught upstream in a way that resumes the forward) — the forward is never reached, so the outcome is still fail-closed (see N-6 for the cosmetic downgrade to a raw exception). Zero-provider-calls: the guard sits before `run_cycle` (the only provider-call sites, loop.py:1631/1750) and before `_resume_forward`; reproduced `provider_calls == 0` on every refusal branch.

**4. Durable refusal:** append-through-existing-API only — `self.audit.append("cross_process_resume_refused", ..., decision="refuse")` (loop.py:2190–2197); no new store/service. The deliberately-swallowed `AuditChainError` case is acceptable: it triggers only when the chain is already un-appendable (fork/duplicate-sequence sets `load_error`, so `append` refuses, audit_log.py:189–193) — there the broken chain **is** the durable evidence and the caller still re-raises fail-closed. In the digest-mismatch tamper case, `load_error` is not set at open, so the refusal **is** appended and the tamper stays detectable (`verify_chain` still reports the earlier `digest_mismatch`) — reproduced by `test_chain_tamper_is_detected_and_refuses`.

**5. Boundary compliance (R149/R150):** CONFIRMED. No journal signing; no new store/service/daemon/PKI/identity system (reuses the existing `AuditLog`); no supervisor redesign (a small guard insertion + one module-level constant/function/method); no broadening (scoped to the cross-process resume path); SHADOW-ONLY untouched (`assert_forwarding_allowed`/`forwards=`/posture not referenced in the diff); nothing activated; no authority change; R140 preserved.

**6. N-1 re-ruling and new findings — below.**

---

## Findings (severity-ranked)

No CRITICAL, HIGH, or MEDIUM findings. No blocking corrections.

**INFO N-1 — RE-RULED CLOSED (superseded by this fix).** My prior N-1 flagged that cross-process resume anchored on the mutable journal `approved_digest`, so a post-approval rewrite of `approved_digest`+`approved_instruction` (the shape the owner later named G3 MAJOR-1) fell outside R136's premise. That is exactly what the audit cross-check now closes within the journal-write-only model. **N-1 is CLOSED.**

**INFO N-2 — stands as-is (unchanged).** Operator-covered field VALUES render inline in the forwarded body (codex_reviewer.py). Approval-covered by definition, not attacker-inducible without changing the digest → refusal. The rework did not touch `codex_reviewer.py`. Note only.

**INFO N-3 — stands as-is (unchanged).** `packet_reference` dropped from the forwarded body (codex_reviewer.py); informational, no enforcement implication. Unchanged by the rework. Product/provenance note.

**INFO N-4 — full-local-write residual is the standing trust-domain limit (activation record; not a regression).** See charge item 2. Requires signing/external anchoring explicitly excluded by R140 for this task; deferred to Phase 3 (external anchor Option A) per audit_log.py's own documentation. Outside this task's boundary; no live exposure under SHADOW-ONLY. Recorded for the activation decision.

**INFO N-5 — narrow residual: replay of *operator-approved* content within one run (pre-existing, strictly narrowed by this rework; not the MAJOR-1 injection class).** A full-journal-write attacker who re-inserts an approved-shape record whose `approved_digest` equals a *different, genuinely sealed* approval's digest from the **same** run can cause that operator-approved body to be reconstructed and (given a fresh `approval_binding`) re-forwarded. This is (i) **not** the MAJOR-1 property — the content is operator-approved, never attacker-injected; (ii) **pre-existing** — the C2 reconstruction check already permitted it, and it requires the full-journal-write residual (N-4); (iii) **strictly narrowed** by this rework — before, any self-consistent digest passed; now the digest must match a genuine sealed approval in the run. Straightforward double-forward is additionally blocked by `consume_pending_prompt` (loop.py:2309) and duplicate-message-id suppression. Outside this task's boundary; noted for the activation record.

**INFO N-6 — nit (non-blocking): an unexpected error during refusal sealing surfaces as a raw exception rather than a structured `forwarded_prompt_unavailable`.** `_seal_cross_process_resume_refusal` catches only `AuditChainError`; any other error from `audit.append` (e.g., disk/OS error) would propagate uncaught. This remains **fail-closed** (no forward, no provider call — the forward is downstream of the raise), so there is no security defect; it is only a slightly less-legible failure surface. No action required for this task.

---

## Corrections attached to this PASS
**None.** The G3 MAJOR-1 resume-window forgery is closed within the owner-set threat model; fail-closed, zero-provider-calls, and durable-refusal properties are reproduced; the six reason codes are distinct and each fails closed; the diff is confined to `loop.py` + tests with no posture/activation/network/signing/infrastructure changes; R140 and SHADOW-ONLY are preserved; nothing is activated. The full-local-write residual (N-4) and the operator-approved-content replay residual (N-5) are the standing trust-domain limits explicitly excluded by R140, recorded for the activation decision. (The DCV lane independently rules the R144–R154 requirement-wording compliance; my security ruling is that the property is genuinely and cryptographically closed within the owner's threat model.)

## Residual-risk statement for the activation decision record
Cross-process resume integrity now rests on the same-machine, hash-chained operator-approval audit log plus its sidecar head anchor. This defeats the journal-write-only adversary (MAJOR-1) and any non-recomputing tamper. It does **not** defeat a full-local-write/root adversary who rewrites or correctly extends the chain and its head anchor, because there is no cryptographic signing (R140) and external anchoring is deferred (Phase 3, Option A). Before any live supervised-auto activation (R595 path), the activation package should record this residual and the external-anchor/signing item as the remaining hardening for cross-process resume integrity. Under the current SHADOW-ONLY posture there is no live forwarding, so the residual carries no present operational exposure.

**G5 VERDICT: PASS**
