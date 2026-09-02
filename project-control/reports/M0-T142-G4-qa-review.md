# M0-T142 G4 QA review (independent qa-engineer, 2026-09-02)

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only; harness banner and neutralized angle brackets restored to plain
form; report-preservation rule 2026-07-16). Reviewer: foreground read-only `qa-engineer`
subagent; producer = orchestrator (identities differ). TWO parts: the gate review at
submitted head `f2e79cc5`, then the delta attestation at the resubmitted head `57dce1a5`.

## Part 1 — gate review at f2e79cc5 (verbatim, condensed only by removing the harness banner)

**VERDICT: PASS.** Two MINOR findings (neither blocking); no BLOCKING findings. The core
fix is proven against the REAL preserved failed run.

Content-identity provenance: the worktree-isolation guard blocked git preflight in the
reviewer sandbox; all 14 target files' git blob SHA1s (recomputed in Python from the ctl24
working files) match `git ls-tree f2e79cc5` exactly, so the reviewed content identity was
established without git access.

Commands: step-1 8-file suite **402 passed** (exit 0); `modularity_check --check` exit 0
(0 failures); `validate_directive_compliance.py --check` exit 0; controller_update
`run_ps_tests.ps1` exit 0 (7 files); ruff on 6 changed production files clean; full
supervisor suite (run ONCE) **3591 passed, 2 skipped, exit 0** — matches the
producer/freeze claim exactly; 5 targeted N5/N6 killing tests passed. Forbidden paths:
M0-T142's own commit range touches none.

Fixture-family mapping: all SEVEN Amendment-45 families present and non-vacuous (multi-key
settles; [1m] explicit; missing/different primary refuses; auxiliary never masquerades;
Bash restriction load-bearing + measured via the correlated census; rows-3/8 durable
fields all exist in the proven shapes — `runtime_identity`, `main_tool_uses`,
`accounting`, `session_id`, `codex_decision.json`; Codex review proceeds after settlement
via `test_end_to_end_worker_unit_then_review_completes` with audit ordering).

Mutation testing: scratchpad copies with rewritten imports — **N1/N2/N3/N4 all DETECTED**
(each mutant flips its killing assertion); N5/N6 confirmed by static executed-assertion
analysis + their killing tests passing on clean code.

Adversarial probes (real module, 8/8 correct): main turns lacking a model field →
`transcript_no_turns`; divergent model hidden behind `isSidechain:true` → settles
(sidechains not primary); foreign `[1m]` model → refuses; aggregate ONLY `pin[1m]` with
plain-pin turns → settles with `context_tier_used=True`; whitespace/casing pin variants →
refuse; all-tier turns → settle; uppercase `[1M]` → refuse.

**Real-canary cross-check (decisive):** `verify_primary_model` against the PRESERVED
canary-b5-02r1 artifacts (real transcript + real unit-record aggregate) **PASSES** and
returns `primary_model=claude-opus-4-8`, `primary_models_observed=('claude-opus-4-8',)`,
`auxiliary_models=('claude-haiku-4-5-20251001',)`, `context_tier_used=True`,
`assistant_turns=15`, tool census `{'Bash': 2, 'Agent': 3, 'Glob': 2,
'StructuredOutput': 1}` (Bash present, count 2 — confirms cluster B live). The exact
WorkerResult the old settlement refused now settles with the corrected semantics.

Modularity clean. Findings: **MINOR-1** AS-SI-1 text vs implementation (intent-satisfying,
implementation more correct per R687; recommend accept-time text tidy; no code change);
**MINOR-2** R697 absence from the evidence map is correct (post-acceptance owner script
under M0-T140) — flagged for DCV confirmation. Recommendation: record G4 = PASS.

## Part 2 — delta attestation at 57dce1a5 (verbatim)

**DELTA-ATTEST: PASS.** Reviewed head `57dce1a55c5126bb16593dde5fdf4eb1b0caf220`; frozen
candidate `f8f0f0c89ff9c3f7762e144d5d37874b10f2b294`.

Content identity: all 5 changed files' git blob hashes match `git ls-tree 57dce1a5`
exactly. Delta scope verified against the claim: only ONE production file changed
(`mrl_runtime_identity.py`), plus the two claimed tests, the four binding carriers, and
control-plane bookkeeping; forbidden paths empty diff; code tree frozen
`f8f0f0c8..57dce1a5`. Commands: 3-file pytest **157 passed**; `run_ps_tests.ps1` exit 0
(7 files); the 2 new delta tests pass `-v`. Binding pin `f8f0f0c8…` present in all four
carriers; the PS harness asserts SHA-agreement and passes.

Adversarial check of the new fixture CONFIRMED: `UnicodeDecodeError` is not an `OSError`
(the pre-delta guard genuinely missed it and a raw exception would have escaped
`_settle`); the fixture bytes are genuinely invalid UTF-8 (decode raises at byte 267);
the real module refuses typed `transcript_missing` via both entry points. Combined-test
non-vacuity CONFIRMED (six substantive assertions across settlement + review + audit
ordering). Prior MINOR findings unchanged and require no code action.

**My original G4 PASS verdict STANDS at reviewed head `57dce1a5`.**

---

*Orchestrator disposition (2026-09-02): MINOR-1 recorded (packet text immutable
post-claim; divergence documented in producer report s8 with the reviewers' judgment).
MINOR-2 discharged by the DCV re-verification at the same head.*
