# M0-T143 — G4 independent QA verification, preserved VERBATIM

Returned by the read-only `qa-engineer` agent through the agent-return channel on 2026-09-03;
saved verbatim by the orchestrator (transport entity-decoding only: `&amp;`/`&lt;` decoded).

---

# G4 QA Gate Report — M0-T143 (D-024 Amendment 46: Codex `--output-schema` strict-subset repair)

## VERDICT: PASS

Reviewer: qa-engineer (independent, read-only). All commands executed independently against the reviewed-head content in `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`. Local Python 3.11.9.

## Identity / freeze confirmation

- Reviewed head `59f572c1410cd25df520bb9b58ffd75695fb7b2e` confirmed present in the shared object store.
- `git diff --quiet 3f4cee86 59f572c1 -- tools/agent_supervisor` → **exit 0** (empty): reviewed head's supervisor code == frozen code commit `3f4cee86`.
- `ctl24` is a linked worktree on branch `candidate/D-024-mrl-option-b`, which has advanced past the reviewed head to `3ddc6594`. The two later commits (`257b02cf` submitted→awaiting_gate, `3ddc6594` submission record) are **control-plane only**: `git diff --name-status 59f572c1 3ddc6594` = `project-control/reports/M0-T143.json`, `project-control/state.json`, `project-control/tasks/M0-T143.json`. No code/test drift. Supervisor material identity (subtree tree `209026fd...`) is stable.
- `ctl24` working tree verified content-identical to reviewed-head blobs for all 10 touched code/test files via pure-Python git-blob hashing. One file (`test_agent_supervisor_mrl_codex_decision.py`) is checked out CRLF while committed LF; newline-normalized bytes are identical (INFO, not drift).
- `source_binding.json`: `commit_sha=3f4cee8680ba5c9a167327507af387d316f5dbc3`, `commit_tree_sha=04688351...`, `subtree_tree_sha=209026fd...` — all three **independently confirmed authentic** against `git rev-parse 3f4cee86`, `^{tree}`, and `:tools/agent_supervisor`.

## Task-step execution (raw command tails)

**Step 1 — focused suites**
`cd ctl24 && python -m pytest tools/test_agent_supervisor_mrl_provider_schema.py tools/test_agent_supervisor_mrl_codex_decision.py tools/test_agent_supervisor_mrl_one_shot_review.py tools/test_agent_supervisor_reviewer.py tools/test_agent_supervisor_ephemeral_review.py tools/test_agent_supervisor_codex_channel.py tools/test_agent_supervisor_mrl_worker_result.py -q`
→ `339 passed in 41.95s` (exit 0).

**Step 2 — owner-error regression subset + fixture**
`python -m pytest tools/test_agent_supervisor_mrl_one_shot_review.py -q -k "provider_rejection or no_decision or spawn or tails or redacted or truncated"`
→ `18 passed, 63 deselected in 7.80s` (exit 0).
Fixture `tools/agent_supervisor/fixtures/codex_schema_probe_20260902.jsonl`: 877 bytes, **UTF-8 (0 CR)**, 4 non-empty JSONL lines all parse. Lines 3 (`error`) and 4 (`turn.failed`) each carry `invalid_json_schema`, `'uniqueItems' is not permitted`, `text.format.schema`, `400`. The fixture-driven test `test_provider_rejection_surfaces_parsed_error_and_tails` asserts exact facts: `error_code == "provider_rejected_request"`, `returncode == 1`, `"invalid_json_schema"`, `"'uniqueItems' is not permitted"`, `"returncode 1"`, `"stdout tail:"` + `"stderr tail:"`, and audit row `error_category == "provider_rejected_request"` with `returncode == 1`.

**Step 3 — mutation-detection spot check (read-only)**
All named tests exist and assert the specific guarantees:
- `test_lengths_and_cardinality_rejected` (codex_decision:67) — rejects overlong rationale, empty ids, duplicate ids, overlong item.
- `M0T143ControllerEnforcedBoundsTests` (codex_decision:167) — boundary accepts (4096/64/128), empty/overlong rationale, empty id, duplicate ids named, wrong item type, non-object payloads. **pytest collects 8 tests from this class** (confirmed via `--co`).
- `test_each_nonstructural_keyword_is_refused` (provider_schema:247) — parametrized over uniqueItems/minLength/maxLength/minItems/maxItems/pattern/format/allOf/anyOf/oneOf/not/patternProperties, each raising `ContractError(code="codex_schema_unsupported_keyword")`.
- `test_unsupported_schema_keyword_refuses_before_any_spawn` (one_shot_review:764) — asserts `error_code == "codex_schema_unsupported_keyword"`, `"uniqueItems"` in message, and **`rh.calls == [] and rh.version_calls == []`** (no child, not even `--version`).
- `ReviewVerdict.from_provider` (mrl_codex_decision.py:55-111) enforces every removed bound controller-side: nonempty rationale, `≤4096`, `1..64` ids, per-id nonempty `≤128`, **uniqueness (line 98-103)**, issued-ids-only. The uniqueness check is exactly the mutation-pair target (disabling it breaks `test_lengths_and_cardinality_rejected` + `test_duplicate_ids_name_the_duplicates` — matching the producer's recorded 2-failed→2-passed pair).

**Step 4 — full affected suite (one run, reviewed head)**
`python -m pytest tools/test_agent_supervisor_*.py -q`
→ `3626 passed, 2 skipped in 359.62s (0:05:59)` (exit 0). **Exact match to the claimed 3626/2/0**; ≥1165 freeze baseline re-established. (Timing differs from producer's 288s — environmental only.)

**Step 5 — PS harness**
`powershell -NoProfile -ExecutionPolicy Bypass -File tools/controller_update/ps_tests/test_runbook_parse.ps1`
→ all PASS, `test_runbook_parse: runbook and operator script parse-clean and concrete`, `PS-EXIT=0`. Includes `PASS binding contract pins the immutable accepted SHA` and `PASS runbook section 4 states the same immutable SHA`.

**Step 6 — negative checks**
- Retyped test `test_no_json_object_is_missing_decision_file_with_tails` asserts strictly **MORE** than its predecessor: predecessor `test_no_json_object_is_no_decision` had a single assertion (`error_code == "no_decision"`); the retype asserts `error_code == "missing_decision_file"`, `"returncode 3"`, `"boom"`, `"stdout tail:"` + `"stderr tail:"`, `returncode == 3`, `argv[1] == "exec"`. Strengthened, not weakened.
- No live provider call: `grep -E "subprocess|Popen|os.system|shutil.which|check_output|communicate"` over the three touched test files → **no matches**. Every Codex process goes through the injected `ReviewHarness`; the fixture is a static file.

**Step 7 — acceptance scenarios + deliverables**
- **AS-CS-1** (R702): `review_verdict.schema.json` contains only structural keywords (`$schema,$id,title,description,type,additionalProperties,required,properties,enum,items`); none of uniqueItems/minLength/maxLength/minItems/maxItems remain. `git log` shows the flatten in a single commit `3f4cee86`. `test_flattened_review_verdict_carries_no_banned_keyword` guards it. PASS.
- **AS-CS-2** (R703/R704): controller-side rejection of overlong rationale, overlong id, too many/too few ids, duplicate ids, fabricated ids, wrong types, bad enum, extra fields, non-object payloads — all present in `from_provider` + `M0T143ControllerEnforcedBoundsTests`/`ReviewVerdictContractTests`, green. PASS.
- **AS-CS-3** (R705): pre-spawn inspection wired on **both** paths — `mrl_one_shot_review.py:219` (OneShotReviewer) and `codex_reviewer.py:558` (legacy CodexReviewer), each before the `_invoke` spawn loop; sweep test `test_every_provider_facing_schema_passes_its_provider_inspection` covers worker_result (Draft-7), review_verdict + codex_decision (strict subset). PASS.
- **AS-CS-4** (R706/R710): fixture-as-stdout + exit 1 → `provider_rejected_request` with parsed `invalid_json_schema`/400/first message + returncode + both bounded redacted tails; truncation marker (`test_oversized_failure_stream_is_truncated_with_marker`, message <3000, noise absent); redaction (`test_credential_shaped_output_is_redacted_in_tails`, `[REDACTED:` present); no live provider call. PASS (see MINOR-1 re: the "no_decision" wording).
- **AS-CS-5** (R707): M0-T143 code diff (`3f4cee86~1..3f4cee86`) touches no model-selection surface; `grep -iE "fable|claude-fable|review_model|approved_models|model_selection|settings"` over the code diff → **no matches**. Owner script verifies (never edits) `model = "claude-fable-5"` via the doctor `model_selection` row and forbids `claude-fable-5-1`/`fable`. PASS.
- **AS-CS-6** (R708/R709): evidence report §6 states the recovery-path determination explicitly — no safe review-resume path (CLI evidence: `loop.py CYCLE_ENTRY_STATES = {PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING}`; WAIT_FOR_OWNER exits) → **one successor full canary `canary-b5-02r3`**; §7 records corrected canary semantics (Claude auth PASS, Fable WorkerResult PASS, Codex the only failed leg, item 8 PASS, item 10 NOT_RUN). PASS.
- **AS-CS-7** (R710): focused suites pass (339) and one complete affected-suite run passes (3626/2/0 ≥ 1165). PASS.
- **AS-CS-8** (R711/R712): `source_binding.json commit_sha == 3f4cee86` (verified authentic); owner script `run_m0t143_codex_schema_repair_and_canary.ps1` deployed at `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\`, **Get-FileHash SHA256 = `096ee3ea749ca3b8654561a20aa442b0bac472ad6f1635e430da0116ebfed5de`** — exact match to the claimed hash (28013 bytes); the session did not execute/push/merge. PASS.
- Fixture provenance: committed fixture SHA256 = `3c40d9e9af9e228cebd0ec0f9c89627372dfccb262125abf494bc6b0405e60a0` — exact match to the evidence report's recorded value.

**Modularity** (production source changed): `python tools/modularity_check.py --check` → `failures 0; warnings 12`, exit 0. `codex_reviewer.py` grew 800→854 lines (+54) — carries a pre-existing review-signal warning, no hard-threshold breach, cohesive growth (failure-observability belongs with the reviewer spawn path).

## Numbered findings

1. **MINOR** — AS-CS-4's literal text says an unparseable nonzero exit "still records `no_decision` plus both bounded tails," but the implementation types that case `missing_decision_file` (test `test_no_json_object_is_missing_decision_file_with_tails`). This is a **strict observability improvement**, not a weakening: both bounded tails are preserved and no known provider error is ever a bare `no_decision` (the substantive R706 guarantee). The producer documented the retype in evidence §4. Non-blocking; noted for the DCV's per-requirement pass.
2. **MINOR** — Packet `outputs` #4 names a new module `tools/agent_supervisor/mrl_reviewer_failure.py`; that module does not exist. The failure-observability was folded into `codex_reviewer.py` (`bounded_stream_tail`/`failure_tails`) — consistent with `allowed_paths` (which never listed the module) and the modularity "reuse the owning boundary" preference. Behavior is fully delivered; only the outputs-description name is stale.
3. **MINOR** — Evidence report §5 states modularity has "3 pre-existing warnings in untouched files"; in fact `codex_reviewer.py` is a touched file that carries a pre-existing review-signal warning (grew 800→854). Still 0 modularity failures and no NEW finding introduced. Accuracy nit only.
4. **MINOR (cosmetic)** — `M0T143ControllerEnforcedBoundsTests` is defined AFTER the `if __name__ == "__main__": unittest.main()` guard in `test_agent_supervisor_mrl_codex_decision.py`. Under pytest (the harness used) it is collected and run (confirmed 8 tests); running the file directly with `python file.py` would skip it.
5. **INFO** — `test_agent_supervisor_mrl_codex_decision.py` is checked out CRLF in `ctl24` while committed LF; newline-normalized content is byte-identical. No material difference for Python execution or content identity.

No BLOCKING findings.

## Note for the orchestrator

- Record this gate against the live HEAD (`3ddc6594`), whose supervisor material identity (subtree tree `209026fd`) equals the frozen candidate `3f4cee86`; the two post-submission commits are control-plane only.
- The `directive-compliance-verifier` per-requirement pass over D-024-R700..R713 (written to the directive `verification.json`) is a separate required input; this QA gate independently covered the acceptance scenarios, behavior, red/green+mutation proof, regression, provenance, and modularity.

Relevant files (absolute):
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T143.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T143-evidence.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\schemas\review_verdict.schema.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\mrl_codex_decision.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\mrl_provider_schema.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\codex_reviewer.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\mrl_one_shot_review.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\source_binding.json`
