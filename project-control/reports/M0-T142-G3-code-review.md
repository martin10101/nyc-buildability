# M0-T142 G3 code review (independent code-reviewer, 2026-09-02)

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only; a harness banner and neutralized angle brackets in the original
return are transport artifacts, restored to plain form here; report-preservation rule
2026-07-16). Reviewer: foreground read-only `code-reviewer` subagent; producer =
orchestrator (identities differ). TWO parts: the gate review at submitted head
`f2e79cc5`, then the delta attestation at the resubmitted head `57dce1a5`.

## Part 1 — gate review at f2e79cc5 (verbatim)

I have completed my independent review. All verification is done: HEAD/freeze identity confirmed, full change set inspected, attack surface analyzed, tests reproduced (focused 200 passed; full supervisor suite 3591 passed / 2 skipped / 0 failures), one code concern reproduced in-memory, and modularity checked (0 failures).

**Task:** M0-T142 — D-024 Amendment 45: settlement runtime-identity + explicit Bash restriction corrective package
**Reviewed head:** `f2e79cc5df67ebef58a49b00f6e817eea841ce03` (branch `candidate/D-024-mrl-option-b`)
**Frozen corrected candidate:** `65e43491129893fcfa49bbe7e7d4463b83336c0b` (tree `672f00d6…`, subtree `35fa1976…`)
**Verdict: PASS** — 4 MINOR findings, 0 BLOCKING. None block acceptance; Finding 1 warrants a tracked follow-up.

Identity/integrity verified by direct evidence: HEAD == `f2e79cc5`, tree clean; frozen candidate tree + subtree match the packet; subtree byte-identical at reviewed HEAD; R694 forbidden paths byte-identical over M0-T142's own span (`mrl_provider_schema.py` change belongs to accepted M0-T141); scope inside allowed_paths; supervisor-freeze §3 citation duty met (packet + commit `65e43491`); freeze rebind carriers agree; `required_modules` gains the two identity modules.

Behavior verified: identity proven from the correlation-bound transcript with typed refusals for divergent top-level model, missing/uncorrelated/empty transcript, zero turns, foreign sessionId/cwd, pinned-absent aggregate; tier handling exact (`pin` or `pin+"[1m]"` only; `pin[2m]`, `other[1m]`, prefix tricks refuse); trust-domain limitation correctly disclosed (transcript authored by the CLI child — defends against stale/cross-session/cross-project transcripts and naive multi-key aggregates, not a fully compromised child); no hole found where a divergent primary settles under an honest child. R686/R687 faithful; R690 binding added AND tested (real project-key fixture; config_base override/fallback/fail-closed); permission guard at both build sites with deny flow-through proven; MCP denial + hook chain unchanged; version pin preserved; `session_id_missing` before identity; no provider contact added; `observed_model_from_result` fully deleted. Tests: required subset 200 passed; full suite 3591 passed / 2 skipped; red/green coverage matches the attack surface; modularity 0 failures.

Findings: **1 MINOR (fail-closed hardening; recommend follow-up)** — `read_transcript_turns` guarded only by `except OSError`; a torn multibyte transcript raises `UnicodeDecodeError` (a `ValueError`), escaping `_settle` uncaught: worst case a crash, never a checkpoint, but violates the module's own contract; fix by catching `(OSError, UnicodeDecodeError)` + a corrupt-encoding fixture. **2 MINOR** — AS-SI-1 text says `auxiliary={haiku, pinned[1m]}` vs implementation `auxiliary={haiku}` + `context_tier_used=True`; implementation is the MORE faithful reading of R687; intent satisfied; recommend wording tidy. **3 MINOR** — turns that omit `message.model` are skipped, so the proven guarantee is "every main-chain turn that reports a model matched the pin, and ≥1 such turn exists" — equal to R691 for an honest CLI; within the disclosed trust boundary. **4 MINOR** — AS-CX-1 proven indirectly; a dedicated combined multi-key + review-path test would be a nice-to-have. Scope boundary noted: AS-MD-1/R699 (owner script) belongs to the M0-T140 continuation/DCV, not this G3.

**Overall: PASS.**

## Part 2 — delta attestation at 57dce1a5 (verbatim)

**DELTA-ATTEST: PASS** — reviewed head `57dce1a55c5126bb16593dde5fdf4eb1b0caf220`

I verified the delta entirely from git and a test rerun, treating the producer's description as claims to reproduce. HEAD is `57dce1a5` with a clean tree; the frozen candidate moved to `f8f0f0c8` (tree `23af20d5`, matching `source_binding.commit_tree_sha`), and `tools/agent_supervisor` is byte-identical from `f8f0f0c8` to HEAD (subtree `ffbde3b6…`). The diff `f2e79cc5..57dce1a5` matches the description exactly: the **only** production change under the supervisor tree is `mrl_runtime_identity.py` (the read guard becomes `except (OSError, UnicodeDecodeError)` with the Finding-1 rationale in a comment), plus the two test additions, the binding/runbook/ps_test rebind, and control-plane freeze/report/state/task records — no other production change, and all five forbidden paths remain byte-identical across the delta. **Finding 1 is correctly and completely resolved:** `UnicodeDecodeError` (confirmed a `ValueError`, not an `OSError`) is now caught at the sole bytes-to-str decode in the read path and converted to the typed `transcript_missing` `ContractError`, so it can no longer escape `_settle`; the new fixture `test_torn_multibyte_transcript_refuses_typed_not_crash` genuinely writes torn multibyte bytes (a valid line minus its last byte plus an incomplete `\xe2\x80` continuation) and asserts the typed refusal. **Finding 4 is resolved non-vacuously:** `test_review_completes_after_a_multi_key_usage_settlement` drives the exact canary multi-key aggregate `{pin, haiku, pin[1m]}` through settlement (asserting `ok`, `model_mismatch False`, `auxiliary==(haiku,)`) and then through the Codex reviewer to a `COMPLETE` decision on the same chain, with the `mrl_one_shot_settled` audit event ordered before `codex_review_decision`. Binding SHA carriers all agree on `f8f0f0c8`. `pytest` runtime_identity + one_shot_review → **93 passed**. My original G3 PASS verdict stands at this head with Findings 1 and 4 resolved; the remaining Finding 2 (AS-SI-1 scenario-text wording) and Finding 3 (documented same-trust-domain limitation) are non-blocking and required no code change.

---

*Orchestrator disposition (2026-09-02): Findings 1 and 4 RESOLVED in the review-wave delta
(commit `f8f0f0c8`) and re-attested above. Finding 2 — accepted advisory: the packet text
is immutable post-claim; the divergence and the reviewers' more-faithful-reading judgment
are recorded in producer report s8. Finding 3 — accepted disclosed limitation (same trust
domain as the result object).*
