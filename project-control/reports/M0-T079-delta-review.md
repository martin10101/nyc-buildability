# M0-T079 round-3 delta review, G3 code + G5 security (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t079-delta-review (independent). Verdict PASS — the
round-3 delta (D1/D3 + 3 minors) is correct, both round-1 must-fix remain closed, no new
must-fix/important. Reviewed identity ca6f4a8ae998719f81148faaff8cc544fde11439.

---

DELTA REVIEW M0-T079 ROUND 3 (G3 code + G5 security) — VERDICT: PASS

The round-3 delta is correct, both round-1 must-fix remain closed, and no new must-fix or important issue was introduced. Two residual minors, neither blocking.

== D1 — operator-facing --run-id remedy + dispatched:false: CORRECT, and effective in production ==

report() now carries exhausted_dimension, exhausted_counters, and exit_detail, with the right precedence: the durable record["exit_detail"] wins, falling back to the live verdict.reason only when the record has none. The wall-clock verdict gained the "--run-id <fresh-id>" sentence; the counter verdict already had it, so both dimensions are covered. dispatched_run_refusal builds the message from the report and adds remedy + cycles_executed to the detail.

I checked the piece the new test cannot prove on its own — that run_dispatched reads keys that actually exist on the real payload. _run_loop returns LoopRun.to_dict() (loop.py:464), which emits "cycles" as a list and "run_budget" as a dict-or-None, so D1 is live in cmd_start, not just under the test's hand-built dict. The truth table narrows exactly one case: no cycles AND stopped == "budget_exhausted" gives False; everything else, including an empty dict, stays True as before. It cannot mislabel a run that really dispatched.

Degradation is safe: with no ledger the report is {}, the dimension label falls back to the generic "budget", and the static part of the message still names the remedy — and in any case budget_stop returns "" when run_budget is None, so that branch is unreachable.

NO SECRET OR UNREDACTED CONTENT IS NEWLY EMITTED. exit_detail is written only by RunBudgetLedger.finalize(detail=...), and there are exactly two non-test callers: loop_breakers.py:174 passes verdict.reason (budget-derived text only — counter names, wall seconds, elapsed, started_at_utc) and loop.py:2792 passes nothing. No journal, probe, or provider content can reach that field. exhausted_dimension is a three-value vocabulary and exhausted_counters is restricted to names present in budget.counter_limits. Both emission boundaries still redact: refusals.emit (refusals.py:164,167) runs redact_structure over both to_dict() and lines(), and cli._emit does the same over payload and lines. The only _emit change in this commit is docstring prose; the body is untouched, so the C2/M2 fix stands.

== D3 — required budget_digest: STRICTLY ADDITIVE, no false-refusal path ==

The new branch raises budget_record_malformed on a falsy digest and sits BEFORE the tampered and conflict checks, so it can only add a refusal — no existing accept path widens. _first_launch (run_budget.py:450-467) unconditionally writes budget_digest = self.budget.digest(), a digest_of hexdigest that is never empty, so a legitimate record cannot lack one. There is also no back-compat exposure: git log -S shows budget_digest was introduced in e830c4b, the round-1 commit of this same unmerged task, so no persisted record predates the field. The honest same-bounds resume is unaffected (17 resume tests pass) and the round-2 refusals are intact (BudgetSelfResetTests 13/13, covering budget_conflict, budget_record_tampered, and budget_record_unreadable). The new refusal is audited through the standard _refuse -> _audit("run_budget_refused") path like every other.

== Minors — all three confirmed ==

The removed _ok/_fail/_unknown were genuinely dead: the only two importers of probe_result (probe_control_plane.py:24 and recovery_probes.py:66) take the public ok_probe/fail_probe/unknown_probe, and nothing anywhere references the underscore names. The _unknown in os_acl.py is an unrelated module-local function.

Both cli.py changes are non-functional prose, and the new comment at 3115 is accurate — a missing input is stale_state/13 since C7, not the exit 0 the stale comment claimed.

The .strip() at probe_control_plane.py:137 now matches project_control.py:1240 exactly, and I checked the direction: it only TIGHTENS. A padded " open " or a whitespace-only status previously failed the `not in ("open", "")` test and was silently skipped — fail-open — and both now register as blocking. A padded " closed " was skipped before and after. No fail-open is introduced.

== Extraction, tests, and round-2 properties ==

run_dispatched imports cleanly (verified by live import of start_gate.run_dispatched, dispatched_run_refusal, cli, and the probe_result publics). modularity_check --check reports failures 0 with 5 warnings, all pre-existing signals on files this delta did not touch.

SUITE: 1757 passed, 2 skipped, 0 failed (555 deselected, 152s) — matches expectations exactly. All 5 named round-3 tests pass individually. The test-file diff has ZERO deleted lines — pure addition, so no existing test was weakened.

The round-2 clearances hold. Grepping the full round-3 diff for owner_enable, LoopConfig, and containment returns nothing, so the activation surface is untouched; process.py and loop.py are not among the six touched files, so containment is untouched; audit_log.py is untouched and the audit chain is intact. M1 (budget self-reset) stays closed because _resume() still cannot fall through to _first_launch — the `existing is _ABSENT` branch is unchanged and D3 only hardens that path further. M2 (credential leak) stays closed with 53 redaction/credential tests passing.

== Residual minors (new, non-blocking) ==

1. cli.py has ZERO modularity headroom. Its sloc is 2953 against a grandfathered baseline limit of 2953 — margin exactly zero. The check passes, but the next line added to cli.py fails it. The next task touching that file must extract before it adds.

2. exit_detail is now operator-visible but is not covered by budget_digest, which protects only the budget block. A raw-DB writer could put misleading prose into the refusal an operator reads. This does not bypass redaction, so it is a spoof rather than an exfiltration, and it sits inside the raw-DB threat model round 2 already deferred to journal-DB ACL hardening — but the delta does widen that adversary's reach from "the durable record" to "the text the operator reads", so it is worth adding to the deferred item's description rather than leaving implicit.

== Reviewed identity and commands ==

Reviewed identity: ca6f4a8ae998719f81148faaff8cc544fde11439 (round-3 task commit 0ab986b). Working tree confirmed clean; no writes, no git mutations, no project_control.py.

Commands: git rev-parse/log/status/show (whole + scoped + --name-only + -S'"budget_digest"'); pytest -k agent_supervisor (1757/2/0); the 5 round-3 tests -v (5 passed); BudgetSelfReset (13) + resume (17) + redact/credential/token/secret (53); modularity_check --check (failures 0); Python import smoke test + run_dispatched truth table + modularity source_lines figures.
