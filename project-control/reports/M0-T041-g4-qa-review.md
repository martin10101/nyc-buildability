# M0-T041 G4 QA review — verdict preserved verbatim

**Reviewer:** qa-engineer (independent, read-only for repo files; ran tests + ad-hoc probes). **Recorded by:** orchestrator.
**Reviewed:** HEAD `9a063d6` (code byte-identical to reviewed_sha `8a6dd54`; delta control-plane only). Base `f65d716`. **Result: PASS — no behavioral defects; all adversarial probes fail-closed; 3 non-blocking coverage-gap follow-ups (§6).**

---

# G4 QA Gate Report — M0-T041 (Supervisor gap-closure A)

## 1. Runs (exact counts)
- Full 23-module suite: **Ran 1189, OK (skipped=2)** — 1187/0/0/2 (matches expected exactly). Quota classifier 10/10; resource sampling 10/10; pending_prompt 4/4 (new modules introduce ZERO skips; the 2 skips are pre-existing POSIX-only guards). Authority policy 22/22. Validator exit 0. Python 3.11.9, unittest per freeze-doc invocation.

## 2. AS-1 adversarial quota classifier
20 hostile inputs vs the real classifier + production corpus (empty/whitespace/200KB garbage/exact candidate prose "usage limit reached", "quota exceeded", "429 rate limited", "plan limit hit"/case variants/one-char mutation/None rc/non-int rc/non-str stderr/unicode): **all 20 return "" (unknown); none raised** — fail-closed holds while no fixture is verified_live (AD-025). Positive guardrails with an injected verified corpus prove the machinery real: verified+match → quota_exhausted; wrong code → ""; **empty-shape verified fixture is NOT a catch-all** (matches() returns False with neither return_codes nor stderr_regex). Seam wiring proven through a real launched fake process both directions. Doctor disclosure: "Live-CLI account-quota signal status: UNVERIFIED … keeps the fail-closed pause." **No violation found.**

## 3. AS-3 adversarial sampler + host capability
11 hostile gauge returns: raise/None/NaN/±inf/str → sampling OUTAGE → conservative pause; negative/0 → known trip (floor gauge) → pause. sample() exception-safe by construction (never raised in any probe — loop cycle cannot be killed by sampler internals). gauge() never raises on hostile measured values for live gauges; unknown gauge names pre-filtered. On this Windows host: free_disk_bytes (30.8 GB) + retained_log_bytes measured; cpu/memory/process structurally unknown (never fabricated OK); capability_report()/doctor disclose exactly this split; full doctor exit 0. Loop gate proven both directions + structural-neither + within-limits + no-sampler no-op. **No fabricated-OK path, no loop-killing crash.**

## 4. AS-4 pending_prompt lifecycle
Full sequence through real CLI + loop APIs: failed resume (wrong digest) → exit 1, record SURVIVES with digest (consume not over-eager); retry correct digest → exit 0, consumed (digest dropped), state → FORWARD_PROMPT; re-approve consumed → exit 1 fail-closed; two run_ids don't cross-consume; in-loop declined approval → record survives (consume sits inside `if forward.sent:` after land(CLAUDE_RUNNING)). Ordering verified by source: CLI consumes after durable transition + audit; loop after successful forward. **Correct.**

## 5. Baseline regression
git diff f65d716..HEAD: modified sources only claude_runner/cli/loop.py; added resource_sampling.py + 3 test modules; **no pre-existing test module edited/renamed/deleted**. 1189 − 24 = 1165 baseline tests all green.

## 6. Coverage gaps (non-blocking; recommended before R595 activation)
- **AS-4 (MEDIUM):** no regression-lock that the FAILURE path preserves the record (declined approval / mismatched digest / unsent forward must not consume) — correct today, not locked.
- **AS-1 (LOW-MEDIUM):** no unit test locking the empty-shape-verified-fixture-is-not-catch-all guard (dropping the final line of matches() would go fail-open) — correct today, not locked.
- **AS-3 (LOW-MEDIUM):** (a) real ResourceSampler wiring in cli._run_loop not integration-tested (FakeSampler used in loop tests; both sides proven separately + doctor confirms real sampler); (b) WARN→notify approaching-limit path untested; (c) doctor _check_resource_sampling has no direct unit test.

None is a material gap blocking the gate: SHADOW-ONLY, fail-closed, all core behaviors tested and adversarially reproduced.

## 7. Scope notes
AS-2 (B-rows) out of QA scope (no in-lane change; no B-row regression in the green suite). D-010 per-requirement re-derivation is the DCV's lane. No control-plane regression.

**Verdict: PASS.** The §6 items are follow-up test-hardening before R595 activation, not gate blockers.
