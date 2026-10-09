# M0-T142 producer report — settlement runtime-identity + explicit Bash restriction (D-024 Am. 45)

Producer: orchestrator (main session), 2026-09-02. Scope: exactly the packet's allowed
paths. No push, no merge, no live provider call (R685/R699 "no live launch yet"). Frozen
corrected candidate v3: **`65e43491129893fcfa49bbe7e7d4463b83336c0b`** (tree `672f00d6`,
subtree `35fa1976`); `git diff 65e43491..HEAD -- tools/agent_supervisor` EMPTY at every
later control-plane commit.

## s1. Cluster A — settlement identity (R686/R687/R690/R691)

**NEW `tools/agent_supervisor/mrl_runtime_identity.py`.** The primary model is proven from
the CLI's session transcript, a runtime source explicitly bound and tested (R690):
`project_key(cwd)` reproduces Claude Code's on-disk mapping (fixture pins the REAL
observed directory `C--Users-MLFLL-Downloads-nyc-zoning-ctl24` of the preserved canary),
the file is `<base>/projects/<key>/<session_id>.jsonl` with base from the exact child env
(`CLAUDE_CONFIG_DIR` else `USERPROFILE\.claude`), every line carrying a `sessionId` must
equal the result object's session (a foreign id refuses `transcript_uncorrelated`), and a
main-chain assistant event with a foreign `cwd` refuses. Identity holds only when every
MAIN-CHAIN assistant turn ran the pinned model — the exact id, or exactly
`pinned + "[1m]"` (the real 1M-context tier of the SAME model, R687; any other decorated
id refuses). `modelUsage` is treated as the session-wide AGGREGATE it is (R686): it must
still CONTAIN the pin (or its tier), its other keys are recorded as `auxiliary_models`
and never fail identity by themselves, and an empty aggregate refuses. Typed refusals:
`transcript_missing` / `transcript_uncorrelated` / `transcript_no_turns` /
`contract_violation` (divergent top-level model; pin absent; empty aggregate).

**`mrl_one_shot.py` settlement wiring only:** `verify_primary_model` replaces the deleted
exactly-one-`modelUsage`-key check (`mrl_exec_chain.observed_model_from_result` removed —
its contract was disproven live, R686); the version pin check is preserved verbatim; the
unit record gains `runtime_identity` (primary/auxiliary/turns/tier/transcript/session)
and `main_tool_uses` (the transcript's main-chain tool_use census — the durable
Bash-absence evidence for the canary); `model_mismatch`/`mismatch_detail` now report the
VERIFIED outcome; `session_id_missing` is checked before identity. A `transcript_base`
seam exists for tests only; production resolves from the exact child env.

## s2. Cluster B — explicit tool restriction (R688/R689/R692)

Measured 2.1.252 fact (R688): under `dontAsk`, read-only Bash EXECUTED while merely
absent from `allowedTools`. The restriction is now EXPLICIT end-to-end:
`build_restricted_profile` refuses an inventory tool that is neither allow-ruled nor
deny-ruled (typed violation citing R688/R692); the existing `deny_rules` channel
(→ `permissions.deny` + `--disallowedTools`) is proven load-bearing by AS-PB-1; the
launch-draft applies the same check at draft time (typed refusal naming
`--allow-tool`/`--deny-tool`) and its DEFAULT subagent block now denies
`Edit/Write/Bash/Agent` explicitly. Per R689 the canary uses the BARE deny (the MRL
production contract wants no Bash at all), so the corrected canary criterion proves
Bash was ABSENT and NEVER EXECUTED: `--disallowedTools` carries Bash in the launched
argv, `main_tool_uses` (correlation-bound census) has no Bash row, and
`permission_denials` has no Bash row.

## s3. Cluster C — evidence-reader corrections (R693)

Encoded in the regenerated owner script (M0-T140 continuation, post-acceptance): row 3
splits Claude auth (nonempty live `session_id`) from Codex (NOT_RUN until invoked; PASS
requires `codex_decision.json` to parse once review runs); row 8 reads the unit record's
`accounting` (`subagents_issued=2, subagents_denied=1, processes_total=3` recognized as
PASS) with the ledger file's `issued[]`/`denials[]` arrays as corroboration; row 4 reads
`runtime_identity.primary_model` + `model_mismatch` (verified semantics); row 6 uses the
bare-deny criterion above.

## s4. Regression fixtures derived from canary-b5-02r1 (R695)

`test_agent_supervisor_mrl_runtime_identity.py` (18 tests) + one-shot additions:
AS-SI-1 the EXACT live shape (valid WorkerResult + aggregate {pin, haiku, pin[1m]} +
pinned turns) SETTLES with a checkpoint, `model_mismatch` false, auxiliary={haiku},
tier=true; AS-SI-2 `pin[1m]` turn settles, foreign `[1m]` refuses; AS-SI-3 all six
refusal shapes; AS-SI-4 the real project-key + foreign-session binding proofs; AS-PB-1
bare-deny flow-through + unpinned-tool refusals (profile AND draft); AS-CX-1 the
one-shot REVIEW path proceeds to a Codex decision after a multi-key-usage settlement
(`test_agent_supervisor_mrl_one_shot_review.py` green on the shared harness with the
transcript fixture). R694 preserved surfaces: schemas/, `mrl_worker_result.py`,
`mrl_provider_schema.py`, `mrl_transport.py` untouched (forbidden paths; empty diffs).

## s5. Verification (R696: focused while editing; ONE affected-suite run)

Focused suites 402+ green during editing. Mutants **N1–N6 all DETECTED** (tier-suffix
loosened; divergent-turn tolerated; correlation dropped; aggregate-pin waived;
settlement identity replaced with a fabricated pass-through; profile guard removed);
modules restored byte-identical. ONE affected-suite verification at the frozen
candidate: **3591 passed, 2 skipped, 0 failed** (raw exit 0). `ruff` clean;
`modularity_check` 0 failures; `validate_directive_compliance` exit 0;
controller_update ps harness **7/7 PASS** (SHA-agreement tooth at `65e43491`).

## s6. Freeze + binding (pattern of R678)

`M0-T142-freeze.md` records candidate v3; binding + runbook §4 + ps_test `$pinnedSha`
all pin `65e43491…`; `required_modules` += the two new/changed identity modules.

## s7. Follow-ups (none blocking review)

- The owner-run script (R697/R699: transactional update, manifest verification,
  canonical owner switch to exact `claude-fable-5`, recovery prep, corrected canary
  with the `--model claude-fable-5` argv-proof row) is generated AFTER acceptance under
  M0-T140 — deliberately not part of this task's reviewed content.
- Live proof of the corrected settlement remains owner-typed (R699 "no live launch yet").

Self-verdict: ready for independent G3/G4/DCV at the submitted head (producer ≠ every
verifier).

## s8. Review-wave delta (resubmission at candidate v4 `f8f0f0c8`)

The independent wave at submitted head `f2e79cc5` returned G3 PASS (4 MINOR), G4 PASS
(2 MINOR), DCV PASS 14/14 — zero blocking findings. Two findings were RESOLVED in-scope
per the Amendment-44 pattern (no owner round-trip):

- **G3 Finding 1 (fail-closed hardening):** `read_transcript_turns` now catches
  `UnicodeDecodeError` alongside `OSError` (a child torn mid-write of a multibyte
  character refuses typed `transcript_missing` instead of escaping settlement as a
  crash); corrupt-encoding fixture
  `test_torn_multibyte_transcript_refuses_typed_not_crash` added.
- **G3 Finding 4 (test completeness):** dedicated combined test
  `test_review_completes_after_a_multi_key_usage_settlement` — the exact canary
  aggregate settles AND Codex review COMPLETEs on the same chain (AS-CX-1 direct).

Dispositioned WITHOUT change: G3 F2 / G4 MINOR-1 (AS-SI-1 packet text says
`auxiliary={haiku, pinned[1m]}`; the implementation records `auxiliary={haiku}` +
`context_tier_used=true` — the reviewers judged this the MORE faithful reading of R687,
intent satisfied; packet text is immutable post-claim and the divergence is documented
here); G3 F3 (disclosed trust-domain limitation); G4 MINOR-2 (DCV independently
confirmed the 14-ID applicable set). Delta verification: focused 157 passed; ONE
affected-suite run at v4 = **3593 passed, 2 skipped, 0 failed**; ruff clean;
controller_update harness 7/7 at the rebound pin. Binding/runbook/ps_test now pin
`f8f0f0c89ff9c3f7762e144d5d37874b10f2b294` (tree `23af20d5`, subtree `ffbde3b6`).
