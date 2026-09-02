# M0-T141 G4 QA review (independent qa-engineer, 2026-09-02)

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel
(transport entity-decoding only; report-preservation rule 2026-07-16). Reviewer:
foreground read-only `qa-engineer` subagent; producer = orchestrator (identities
differ, D-024-R677).

---

All review steps complete. Here is my gate report.

---

# G4 QA Gate Report — M0-T141 (Draft-7 provider-schema compatibility hotfix)

**Verdict: PASS**

**Task:** M0-T141 — D-024 Amendment 44 (R664..R683), Claude Code JSON-Schema Draft-7 provider-schema compatibility hotfix at the CLI boundary
**Reviewed head:** `71f0e063275ccc3a0e5deb3308af69a64d8bd086` (branch `candidate/D-024-mrl-option-b`)
**Reviewer:** qa-engineer (read-only, independent; producer = orchestrator)
**Frozen corrected candidate:** `2245de74232947be919b555fd061ba8a6e6438de` (commit tree `63119a9a`, subtree `edf026b3`)

## SHA / clean-tree verification (limitation noted, not blocking)

The worktree-isolation guard blocked every git command targeting the shared `ctl24` checkout (`git -C ctl24 rev-parse HEAD` and `git status --porcelain` both refused), so I verified content identity instead:

- Confirmed object `71f0e063` exists in the shared object store; it is **not** an ancestor of my isolated worktree HEAD (`d8b3899f`, unrelated M0-T077 branch).
- Computed pure-Python git blob hashes of all 9 task-relevant tracked files in the `ctl24` working tree and compared to `git ls-tree 71f0e063`: **all 9 identical**. Three (`mrl_worker_result.py`, `worker_result.schema.json`, `CONTROLLER_UPDATE_RUNBOOK.md`) matched only after CRLF→LF normalization — a Windows-checkout line-ending artifact, not a content difference (git treats them clean); the freshly-written task files matched raw (LF).
- `git diff --name-status f190c77c 71f0e063` changed-file set is entirely within `allowed_paths` (plus orchestrator-written `project-control/gates/`, `state.json`, task packet, submission record). **No forbidden path touched.**

I did not return BLOCKED on the inaccessible git preflight; the reviewed content is confirmed identical to `71f0e063` for every file that matters.

## Commands run (exit codes / counts)

| # | Command | Result |
|---|---|---|
| 1 | `python -m pytest tools/test_agent_supervisor_mrl_provider_schema.py tools/test_agent_supervisor_mrl_one_shot.py -q` | **89 passed, EXIT 0** |
| 2 | `python -m pytest tools/test_agent_supervisor*.py -q` (full supervisor suite) | **3566 passed, 2 skipped, 0 failed, EXIT 0** (exceeds freeze baseline ≥1165) |
| 3 | `python tools/modularity_check.py --check` | 353 files, **0 failures**, 12 warnings (all pre-existing modules; new module not flagged), EXIT 0 |
| 4 | `python tools/validate_directive_compliance.py --check` | **EXIT 0** |
| 5 | `powershell.exe -File tools/controller_update/ps_tests/run_ps_tests.ps1` | **7 test files passed, EXIT 0** (incl. binding/runbook/pinnedSha agreement teeth) |
| 6 | `git diff f190c77c 71f0e063 -- schemas/worker_result.schema.json mrl_worker_result.py` | **empty** (forbidden canonical files unchanged) |
| 7 | Independent mutation harness (scratchpad, mutated copies) | **M2, M3, M6 all DETECTED** |
| 8 | Adversarial probes importing the real module | walk refuses nested-newer-keyword cases; passes same-meaning keywords; no false refusal of enforcer-supported shapes |

## Proof → test mapping for (a)-(e), and whether each is non-vacuous

- **(a) canonical unchanged** → `test_canonical_in_memory_schema_is_never_mutated` (snapshots the canonical, projects, then mutates `projected["properties"]["outcome"]["enum"]`/`required`/`title` and re-asserts the canonical equals both its pre-call snapshot and a fresh disk load) + `test_canonical_schema_file_still_declares_2020_12_internally` + `git diff` empty on the schema file. **Non-vacuous** — the mutate-the-copy step actually catches a shallow-copy regression (independently: producer M5).
- **(b) provider declares Draft 7** → `test_provider_copy_declares_draft7_and_preserves_the_body` (asserts `$schema == draft-07` AND body-minus-`$schema` equals canonical-minus-`$schema`), plus `test_missing_declaration_projects_to_explicit_draft7` and `test_already_draft7_declaration_is_preserved`. **Non-vacuous** — catches the "keep 2020-12" mutant (M2).
- **(c) serialized argument carries no 2020-12** → `test_serialized_cli_argument_contains_no_2020_12_declaration` (module-level, exact runner expression) + `test_one_fresh_process_one_prompt_one_schema_bound_result` (asserts the launched **argv** value parses to draft-07 and contains no 2020-12 substring). **Non-vacuous** — module test catches M2, argv test catches call-site revert (M1).
- **(d) unknown/newer-only keywords refuse** → `test_incompatible_input_refuses_instead_of_translating` (15 params: `$defs`, `prefixItems`, `unevaluatedProperties`, `dependentRequired`, `minContains`, `deprecated`, `$ref`, `definitions`, `dependencies`, vendor key, nested unknown, nested `$schema`, array-form items, draft-04 dialect, non-object) + `test_nested_positions_are_walked` (5 params). **Non-vacuous** — each asserts `exc.value.code == "draft7_schema_incompatible"`, so a wrong error type can't false-pass; independently confirmed M3 and M6 break specific params.
- **(e) same error with guard removed** → `test_guard_removed_would_reproduce_the_exact_recorded_failure` (serializes the canonical schema the pre-fix way, asserts the URI split from `RECORDED_STDERR` equals `CANONICAL_DECLARATION` and appears in the legacy argument, and is absent from the fixed argument). **Non-vacuous** — I verified the test's `RECORDED_STDERR` constant is byte-identical to the verbatim stderr in the preserved evidence file, so it faithfully reproduces the real recorded failure.

## Independent mutation proof (method: mutated copies loaded from scratchpad, real repo untouched)

I loaded three text-mutated copies of `mrl_provider_schema.py` from scratchpad (relative import rewritten to absolute) and ran the exact suite assertions against them:
- **M2** (return `declared or DRAFT7_DECLARATION`, keeps 2020-12) → breaks `test_serialized_cli_argument_contains_no_2020_12_declaration`: **DETECTED**.
- **M3** (unknown-keyword branch `continue` instead of `_refuse`) → `unknown_vendor_keyword` no longer raises `ContractError`: **DETECTED**.
- **M6** (array-form `items` accepted) → `array_form_items` no longer raises: **DETECTED**.

## Acceptance scenarios AS-DS-1..AS-DS-7 (against observed evidence)

- **AS-DS-1** ✓ `worker_result.schema.json` byte-identical (git diff empty) + `test_canonical_in_memory_schema_is_never_mutated` passes.
- **AS-DS-2** ✓ `test_provider_copy_declares_draft7_and_preserves_the_body`; I ran the projection directly on the real canonical — passes the walk, `$schema` = `http://json-schema.org/draft-07/schema#`.
- **AS-DS-3** ✓ module + argv tests pass; argv value parses to draft-07, no 2020-12 substring.
- **AS-DS-4** ✓ 15+5 parametrized refusals; independently corroborated by adversarial probes.
- **AS-DS-5** ✓ `test_guard_removed...` passes; preserved evidence file records provider-contact count **zero** (empty `session_id`, empty `observed_models`, `processes_total` 1, exit 1) and its verbatim stderr matches the test constant and `CANONICAL_DECLARATION`.
- **AS-DS-6** ✓ mutation detection (independently reproduced), focused files green, modularity 0 failures, DCV exit 0.
- **AS-DS-7** ✓ `source_binding.json` `commit_sha=2245de74`, `commit_tree_sha=63119a9a` (== `git rev-parse 2245de74^{tree}`), `subtree_tree_sha=edf026b3` (== `git rev-parse 2245de74:tools/agent_supervisor`), `required_modules` includes both changed modules; runbook §4 (line 84) and ps_test `$pinnedSha` (line 26) both pin `2245de74`, no stale `1489879e`; `run_ps_tests.ps1` exit 0. Additionally, the reviewed head's supervisor subtree (`git rev-parse 71f0e063:tools/agent_supervisor` = `edf026b3`) is byte-identical to the pinned frozen-candidate subtree — **what I tested is what the binding installs**.

## Deliverables (all present and matching description)

All 7 `outputs` items exist: `mrl_provider_schema.py`, `mrl_one_shot.py` (single `--json-schema` call site now serializes `provider_schema_for_claude_cli(load_schema(...))`), the two test files, `M0-T141-canary-b502-schema-failure-evidence.md`, `source_binding.json` (+ runbook §4 + ps_test), and `producer-report.md` + `G2-self-check.md` (1952 B) + `evidence-map.json` (7325 B, top-level `requirements` dict) + `freeze.md`.

## Modularity

New `mrl_provider_schema.py` is 146 SLOC, single responsibility (Draft-7 boundary projection), imports only `.mrl_worker_result` for `ContractError` (no cycle), well under thresholds, not flagged by the checker. Call-site change is one expression. Clean.

## Findings

1. **MINOR / advisory (no action required).** `_SAME_MEANING` admits `format`, `contentEncoding`, `contentMediaType`, and the walk does not validate the *value shape* of same-meaning keywords. Confirmed by probe: draft-4 `exclusiveMinimum: true`, non-numeric `maximum: "oops"`, and a post-Draft-7 `format: "uuid"` all pass through unprojected. For a hypothetical *future* WorkerResult schema using these keywords the "identical meaning under Draft 7 and 2020-12" claim is slightly broader than strictly true (format assertion semantics / available format values diverged in 2019-09+). **No impact on this fix:** the actual WorkerResult schema uses only `type`/`additionalProperties:false`/`required`/`properties`/`enum`/`minLength`/`maxLength` (all unambiguously same-meaning, verified projecting cleanly), and Claude's own CLI Draft-7 validator still rejects a structurally malformed schema at the boundary. Optional hardening: guard `format`/`content*` or validate value types; not required for acceptance.

2. **MINOR / informational.** Live CLI acceptance of the Draft-7 argument is provable only by the owner-typed b5-02 successor canary (R579 boundary; no provider calls permitted in implementation/verification per R679). Appropriately deferred to the post-acceptance owner-run script (R680). The offline proofs bound every controller-side behavior. No G4 action.

**Limitation (not a finding):** could not run `git status --porcelain` / `rev-parse HEAD` on the shared checkout (worktree-isolation guard); mitigated by full content-identity verification of all tracked task files and the in-scope changed-file set.

No BLOCKING findings. Recommend the orchestrator record **G4 = PASS**.

---

*Orchestrator disposition of findings (recorded 2026-09-02): Finding 1 — accepted advisory, no action required per the reviewer; queued follow-up: consider value-shape guards for `format`/`content*`/numeric bounds if a future canonical schema adds such keywords (today's WorkerResult schema uses none of them). Finding 2 — by design; the live proof is exactly what the owner-run b5-02 successor canary performs (R680). Neither requires a change within this bounded scope.*
