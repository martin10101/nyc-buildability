# M0-T141 directive-compliance verification (independent DCV, 2026-09-02)

Saved VERBATIM by the orchestrator from the verifier's agent-return channel
(transport entity-decoding only; report-preservation rule 2026-07-16). Verifier:
foreground read-only `directive-compliance-verifier` subagent; producer =
orchestrator (identities differ, D-024-R677). This report is the basis of the
M0-T141 entry in `project-control/directives/D-024-fable-codex-loop/verification.json`.

---

All 16 requirements verified against primary evidence. Here is my complete independent verification report.

---

# Directive-Compliance Verification — M0-T141 (D-024 Amendment 44)

**Reviewer:** directive-compliance-verifier (read-only) · **Producer:** orchestrator (identities differ)
**Reviewed head:** `71f0e063275ccc3a0e5deb3308af69a64d8bd086` (verified `git rev-parse HEAD`; tree clean; branch `candidate/D-024-mrl-option-b`)
**Frozen candidate (content identity):** `2245de74` — `tools/agent_supervisor` subtree frozen through HEAD (`git diff 2245de74..71f0e063 -- tools/agent_supervisor` EMPTY)

## OVERALL VERDICT: PASS

Intake completeness (Amendment 44): `requirements.json` carries exactly R664–R683 (20 rows, contiguous, no extras). Each maps faithfully to a source item in `source-044-amendment.md` (item 1→R666 … item 14→R679; return-list→R682); none missing, weakened, combined, or invented. `python tools/validate_directive_compliance.py --check` exit 0 (source digests + locked ids intact). The 16-ID applicable subset for M0-T141 matches the decomposition binding exactly (R664–R672, R675–R678, R682 + cross-cutting R674, R679).

## Per-requirement verdicts (all 16)

| Req | Verdict | Primary evidence reproduced |
|---|---|---|
| **R664** | SATISFIED | `git show --stat 2245de74` = one bounded hotfix (2 prod files + 2 tests + control-plane); `git diff --name-status f190c77c..71f0e063 -- project-control/tasks/` shows ONLY `M0-T141.json`; no other tranche/audit task started. |
| **R665** | SATISFIED | `M0-T141-canary-b502-schema-failure-evidence.md` §Root cause (lines 59–72) + module docstring (lines 5–14) preserve root cause; quoted stderr URI `https://json-schema.org/draft/2020-12/schema` == test `RECORDED_STDERR` (line 41-42) == module `CANONICAL_DECLARATION` (line 37); issue #80402 cited. |
| **R666** | SATISFIED | `git diff f190c77c..71f0e063 -- tools/agent_supervisor/schemas tools/agent_supervisor/mrl_worker_result.py` EMPTY; canonical `worker_result.schema.json` `$schema` = `https://json-schema.org/draft/2020-12/schema` (read directly, unchanged); schemas/ absent from 1489879e→2245de74 subtree delta. |
| **R667** | SATISFIED | `mrl_provider_schema.py:140` `projected = copy.deepcopy(dict(schema))` — deep copy before projection; test `test_canonical_in_memory_schema_is_never_mutated` mutates the projection (lines 63–66) and re-asserts canonical; I independently reproduced M5 shallow-copy detection. |
| **R668** | SATISFIED | `DRAFT7_DECLARATION = "http://json-schema.org/draft-07/schema#"` (line 39), returned at line 145; ran real projection → `$schema = http://json-schema.org/draft-07/schema#`; `test_provider_copy_declares_draft7...` green. |
| **R669** | SATISFIED | `_walk` RAISES `ContractError` (fail closed); final `else` (line 124) refuses unknown keywords; `_REFUSED` table (lines 63–83) covers newer-draft keywords; nested `$schema` refused (lines 100–101); 15 + 5 parametrized cases raise `draft7_schema_incompatible`; I independently confirmed `$defs` refused. |
| **R670** | SATISFIED | `mrl_one_shot.py` single `--json-schema` call site wraps `provider_schema_for_claude_cli(...)` (diff); returns NEW object, canonical never mutated; `test_one_fresh_process...` asserts argv == projection, draft-07, no 2020-12. |
| **R671** | SATISFIED | All five directed proofs present in `test_agent_supervisor_mrl_provider_schema.py` (canonical-unchanged, draft-7, no-2020-12-in-arg, keyword-refuse, guard-removed-reproduces-URI) + argv assertions in `test_agent_supervisor_mrl_one_shot.py`; `pytest` both files = **89 passed**. |
| **R672** | SATISFIED | `M0-T141-canary-b502-schema-failure-evidence.md` states "provider-contact count was zero" (lines 25, 47): empty `session_id`/`observed_models`, `processes_total` 1, exit 1; `git diff --diff-filter=DR f190c77c..71f0e063` EMPTY (no prior canary evidence deleted/rewritten). |
| **R674** | SATISFIED | `M0-T140.json` status `claimed`, untouched in range; `M0-T136/T138/T139.json` + `model_selection.py` untouched (empty diff); `model_selection.py` in forbidden_paths; grep R603/R604/R605 in changed files → only report mentions, all "untouched/owner-only/uninterpreted", none in prod/test code. |
| **R675** | SATISFIED | M0-T141 = next unused ID (after M0-T140); `git show --stat 2245de74` production changes only in `mrl_provider_schema.py` + `mrl_one_shot.py` + 2 tests; subtree delta `1489879e..2245de74` = exactly those two modules. |
| **R676** | SATISFIED | Independently: `pytest` focused = 89 passed; reproduced mutation discrimination (M2 keep-2020-12, M5 shallow-copy, M4 refused-keyword all detected); `modularity_check --check` 0 failures (exit 0); `validate_directive_compliance --check` exit 0. |
| **R677** | SATISFIED | `M0-T141.json` reviewer_agents = [code-reviewer, qa-engineer, directive-compliance-verifier] — three separate identities; `producer_agent` = orchestrator, distinct from all reviewers; DCV (this pass) ≠ producer; G2 is self_check, G3/G4/DCV are the independent wave. |
| **R678** | SATISFIED | `source_binding.json` commit_sha `2245de74` == `git rev-parse 2245de74`; commit_tree_sha `63119a9a` == `2245de74^{tree}`; subtree_tree_sha `edf026b3` == `2245de74:tools/agent_supervisor` (== HEAD subtree); required_modules += both changed modules; all 10 modules exist at 2245de74; runbook §4 (line 84) + `test_runbook_parse.ps1` `$pinnedSha` (line 26) both pin 2245de74. |
| **R679** | SATISFIED | No upstream for candidate branch (`@{u}` fatal); only local branch contains HEAD; no merge commits in range; PR #241 OPEN, `mergedAt` null, headRef `task/M5-T002...` (unrelated), updated 2026-08-20 (pre-dates this work) = untouched; runtime `...\mrl` dir has only `canary-b5-01` + `canary-b5-02` (no new provider-contact run dirs); tests all offline. |
| **R682** | SATISFIED | `M0-T141-evidence-map.json` row R682 records the intended restricted return of exactly the five ordered items (token; accepted task + candidate SHA; test/review results; script path + SHA-256; one PowerShell command) matching source R682 in order; dischargeable at session end, recorded plan matches. |

## Findings

- **BLOCKING:** none.
- **MINOR (non-blocking):** The producer's full-suite claim (`3566 passed / 2 skipped`, freeze report §"Suite baseline" and producer-report s4) was NOT independently re-run in this pass (heavy suite); however every check R676 actually names — focused tests, mutation proof, modularity, governance — was independently reproduced with matching results, so R676 stands satisfied on its own named evidence.
- **NOTE (context only):** G0 `reviewed_sha` = `f190c77c` (task-creation commit) and G2 `reviewed_sha` = `39ec203b` (evidence head); the final control-plane submit commit is `71f0e063`. The reviewed content identity (agent_supervisor subtree `edf026b3`) is stable across all three, so the control-plane commits after 2245de74 do not move the reviewed code.

**Recommendation to orchestrator:** All 16 applicable Amendment-44 requirements are SATISFIED on reproduced primary evidence; no VIOLATED / UNVERIFIABLE / BLOCKED result. This directive-compliance pass is **PASS** for recording in `verification.json` (verifier ≠ producer). Independent G3/G4 verdicts in this wave remain the orchestrator's to record before acceptance.

---

*Orchestrator note (2026-09-02): the DCV's minor observation (full suite not re-run in
its pass) is discharged by the independent G3 review in the same wave, which re-ran the
full supervisor suite at the same head and reproduced 3566 passed / 2 skipped / 0 failed.*
