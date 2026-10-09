# M0-T136 G4 independent QA review (verbatim reviewer return)

Recorded by the orchestrator/verifier session per the report-preservation rule
(`.claude/rules/project-control.md`): the reviewer's return is saved VERBATIM below
(transport entity-decoding only: `&lt;`/`&gt;` decoded to `<`/`>`). Reviewer:
`qa-engineer` (read-only, independent; producer = `mrl-tranche-b-producer`).
Received 2026-09-02. The reviewer's sandbox was an isolated worktree at a stale
base; it therefore read ALL reviewed content from committed blobs in the shared
git object DB (`git show <sha>:<path>`), so every verdict below binds to the
committed identities, not to any working tree.

---

# GATE REPORT — G4 QA Review (qa-engineer, read-only)

**Task:** M0-T136 — D-024 Amendment 40, MRL Tranche B (B0 consolidation + B1–B5 one-shot launch path), offline, no live launch
**Reviewed identity:** frozen production candidate `1489879e` (submit HEAD `1da9d513`; production diff `6f5d12a6..1489879e`)
**Method:** authoritative content via `git show <sha>:<path>` against the shared object DB (the review agent is isolated in a stale worktree at `d8b3899f`; the working tree is NOT trustworthy — all content and hashes were read from committed blobs). No implementation files were edited; no `project_control.py`/push/PR/merge/provider ops were run.

## VERDICT: PASS (with 2 minor provenance corrections; non-blocking)

All ten acceptance scenarios and every named deliverable are present, non-trivial, and substantively satisfy their contracts with reproducible, hash-verified evidence. Findings below are MINOR/NOTE only — none is a false-green and none blocks acceptance.

---

## Evidence integrity (verified)

- `M0-T136-tranche-b-evidence.json` indexes exactly **32 records**; the gates dir contains exactly **32** JSON files — 1:1, no hidden/un-indexed record.
- `record_sha256` == sha256 of the committed gate-record file — spot-checked 3, all matched exactly: `final-freeze-ps-tests` (13dceb2b…), `final-freeze-supervisor-suite` (8f3e267d…), `b0-modularity-mutant-growth-without-exception` (5aadb599…).
- Every `final-freeze-*.json` carries `repo_head 1489879e1f6787a9d53ed74db4524b24039e03a2` (confirmed in the index and in full record reads).
- Production tree is intact after the freeze: `git diff --name-only 1489879e 1da9d513` touches ONLY control-plane artifacts (reports, gates, state.json, task packet, SESSION_HANDOFF) — no `tools/**` or production source changed after freeze, so the single final verification is not invalidated (AS-EV).
- Records are legitimate `gate_runner.py` outputs (direct-subprocess argv lists, raw returncode, stdout/stderr sha256). No gate record's argv contradicts its filename. The two `returncode:1` non-mutation records (`b0/final-freeze-ruff`) are the disclosed pre-existing F28; the two `returncode:1` mutation records carry `mutation.killed=true, ok=true` (intended kills).

## Findings

1. **[MINOR] Terminal-token citation is inaccurate.** `project-control/reports/M0-T136-evidence-map.json:244` claims the single terminal token `TRANCHE_B_OFFLINE_COMPLETE_CANARIES_READY` ends "producer report s11", but `M0-T136-producer-report.md` contains no terminal token (it ends "…belong to independent reviewers and the orchestrator."). The token in fact appears once, in `docs/SESSION_HANDOFF.md:27`. AS-NEG ("final report ends with exactly one terminal token") is substantively met — exactly one token exists, in the regenerated final handoff, and `CONSOLIDATED_BLOCKED` is absent — but the evidence-map citation should point at SESSION_HANDOFF or the producer report should carry the token verbatim. Scenario: AS-NEG. Non-blocking.

2. **[NOTE] `loop.py` not modified though packet outputs list "cli.py + loop.py wiring".** The ONE launch entrance is delivered via `tools/agent_supervisor/cli.py` (`--launch-manifest` at cli.py:3275; `apply_launch_manifest`/`preflight_launch` at cli.py:256, 2951) plus the new `mrl_launch_path.py` module. Given loop.py's zero modularity headroom (2082/2088, packet risk note), extraction-into-new-module is the correct choice; deliverable intent (the single entrance) is met. Scenario: AS-B1. Non-blocking.

3. **[NOTE] `writer_policy="isolated-worktrees"` (a R572 alternative) is deliberately not implemented and refused** (`mrl_subagent_contract.py`, `WRITER_POLICIES=("single-writer",)`, fail-closed). Honest, disclosed limitation; R572 is satisfied via single-writer. Scenario: AS-B3.

4. **[NOTE] "No resume" (B4) is covered by an inline argv-composition assertion** (`test_agent_supervisor_mrl_one_shot.py:275` asserts the launch argv never contains `--resume/--continue/-r/-c/--fork-session/--bg/--background`) plus the structural one-shot design, whereas "no second message" and "no background fallback" each have dedicated refusal tests. Adequate; AS-B4 "mutation tests for each" substantively met. Scenario: AS-B4.

5. **[NOTE — by design, not a defect] Live-capability boundary.** Live CLI honoring of `--allowedTools`/dontAsk/`permission_denials` shapes and real Windows process-tree cleanup are provable only by the owner-run canary (R579). Offline tests inject a spawn seam but still exercise real refusal logic and real process-table snapshots (`test_real_process_table_sees_this_interpreter_alive`, `…proves_a_reaped_child_gone` spawn live subprocesses; ps mutant tests use real `python -c "sys.exit(7)"`). This is the authorized offline scope, honestly disclosed in the failure surface (F29) and G2 self-check.

## Scenario verdicts

- **AS-B0-1 (modularity) PASS** — `git diff 6f5d12a6 1489879e -- tools/modularity_exceptions.json` shows ONLY the `claude_runner.py` file-exception entry removed; baseline untouched; `b0-modularity-after-deletion.json` rc0 (gate green without the exception) and `b0-modularity-mutant-growth-without-exception.json` killed prove the limit is real; `final-freeze-modularity.json` rc0.
- **AS-B0-2 (guidance) PASS** — `CLAUDE.md` principle 17 (always-loaded, concise) + `engineering-reliability/SKILL.md` "Defect convergence" section (change-impact, variant analysis, root-cause clustering, progressive verification); context budget rc0 at B0 and final.
- **AS-B0-3 (freeze) PASS** — full `b0-freeze-*` battery recorded; changed-files ruff rc0 and CI-scope (services/api) ruff rc0; root-tree `ruff check .` rc1 is pre-existing F28 (52 findings, `b0-freeze-ruff` and `final-freeze-ruff` `stdout_sha256` byte-identical = `74680cc7…`; F28 documents them byte-identical to base 6f5d12a6 in files the producer did not touch).
- **AS-B1 PASS** — `mrl_launch_manifest.py` observes all 12 R559 fields independently (git/fs/packet, never the manifest), `verify_launch` collects ALL mismatches, `require_verified` refuses before any provider contact; 12/12 per-field paired mutation tests present (`test_mutation_{repo_root,origin_url,task_id,task_packet_sha256…,mode_cli_disagrees}`), plus `test_manifest_values_never_used_as_observations` and `test_all_mismatches_reported_together`.
- **AS-B2 PASS** — `mrl_exec_chain.py` resolves wrapper→runtime→entrypoint→vendor, `bind_chain_now`/`verify_chain_now` re-hash the whole chain immediately before spawn with no cache; all 5 named test classes present: `test_same_size_restored_mtime_replacement_is_detected`, `test_wrapper_retargeting_is_detected`, `test_entrypoint_replacement_is_detected`, `test_updater_reenablement_refuses`, `test_verify_runtime_identity_pass_and_mismatches`, plus `test_every_call_rehashes_no_cache`.
- **AS-B3 PASS** — `mrl_subagent_contract.py`: configurable concurrent/total limits, depth fixed at 1, foreground-only, MCP always denied, out-of-inventory denied, controller-issued ids + accounting; `effective_grants()` = inventory∩allows−denies; paired tests `test_tools_alone_grants_nothing`, `test_over_limit_denied`, `test_mcp_allow_refuses`, `test_allow_outside_inventory_refuses`, `test_pre_from_a_subagent_is_depth_two_and_denied`.
- **AS-B4 PASS** — `mrl_one_shot.py` enforces one fresh process/one prompt/schema-bound WorkerResult/stdin-closed/spawns-once; refusals `test_second_dispatch_is_refused_without_a_spawn`, `test_transport_second_spawn_is_refused`, background denial (ledger `background=True`); `mrl_descendants.py` uses stdlib Toolhelp32 (Windows)/procfs/ps (no psutil) with `test_timeout_terminates_the_tree_and_proves_it_empty` and real-process-table tests.
- **AS-B5 PASS** — `docs/MRL_LAUNCH_RUNBOOK.md` is the single path; `docs/CONTROLLER_UPDATE_RUNBOOK.md` §11 is prominently "OBSOLETE (superseded…)" with no `start`; `run_ps_tests.ps1` reads raw `$LASTEXITCODE` unpiped and fail-closed; `test_mutants_detected.ps1` asserts `$?`/Tee-Object-no-exit/cmd-pipe mutants are DETECTED against a control that preserves raw 7; `final-freeze-ps-tests.json` rc0, `final-freeze-mutation-doc-check.json` killed; canary package lists all ten R587 items verbatim with exact PowerShell and per-item expected results, explicitly NOT executed (no run artifacts in the tree — `git ls-tree` for `one_shot_unit.json`/`canary-b5`/`subagent_ledger` = empty).
- **AS-EV PASS** — every positive contract paired; all verdicts from raw `gate_runner.py` records; one final freeze at 1489879e; SESSION_HANDOFF regenerated only at the freeze.
- **AS-NEG PASS** — `git ls-remote`: PR head `refs/pull/241/head = 4174a3b2…` (untouched), `refs/heads/control/D-024-fable-codex-loop = 6f5d12a6…` (clean base), `refs/heads/candidate/* = (none)`; candidate branch has no upstream, nothing pushed; exactly one terminal token (see Finding 1).

## Deliverables checklist (outputs array → status)

1. `tools/modularity_exceptions.json` (only claude_runner.py entry deleted; baseline unchanged) — **FOUND** (diff proves single-entry deletion).
2. `CLAUDE.md` + `engineering-reliability/SKILL.md` defect-convergence guidance — **FOUND**.
3. `tools/agent_supervisor/mrl_launch_manifest.py` (B1, 387 ln) — **FOUND**.
4. `tools/agent_supervisor/mrl_exec_chain.py` (B2, 304 ln) — **FOUND**.
5. `tools/agent_supervisor/mrl_subagent_contract.py` (B3, 432 ln) — **FOUND**.
6. `mrl_one_shot.py` (536) + `mrl_descendants.py` (180) + `mrl_one_shot_review.py` (349) + `test_…_one_shot_review.py` — **FOUND**.
7. `cli.py` + loop.py wiring of `start --launch-manifest` — **FOUND (cli.py wired; loop.py untouched — see Finding 2)**.
8. 5 paired test modules (`_mrl_launch_manifest/_mrl_exec_chain/_mrl_subagent_contract/_mrl_one_shot/_mrl_launch_path`) — **FOUND** (all in `final-freeze-supervisor-suite` rc0).
9. `ps_tests/*.ps1` (harness + runner + 3 tests + 3 mutants) — **FOUND** (harness.ps1, run_ps_tests.ps1, test_raw_exit/test_doc_check/test_mutants_detected + mutants/{cmd_pipe,dollar_q,tee_no_exit}).
10. `MRL_LAUNCH_RUNBOOK.md` (single path) + CONTROLLER §11 obsoleted + `mrl_launch_draft.py` + `command_docs.py` + their tests — **FOUND**.
11. `M0-T136-failure-surface.md` (30-item F1–F30 inventory + change-impact) — **FOUND**.
12. `M0-T136-canary-package.md` (10 items, NOT executed) — **FOUND**.
13. `M0-T136-tranche-b-evidence.json` (32 records) + G2-self-check.md + producer-report.md — **FOUND**.
14. `M0-T136-gates/*.json` (32 raw records) — **FOUND** (hashes verified).

## Summary

M0-T136 is a genuine, high-quality Tranche-B delivery: the B0 clean-base consolidation deletes only the stale `claude_runner.py` modularity exception (baseline byte-identical, gate green unpiped without it), and the B1–B5 clusters are real, non-trivial modules that implement the pinned contracts — a 12-field pre-dispatch launch-manifest verifier that never trusts the manifest, immediate-before-spawn streaming full-chain SHA-256 with no cache, a controller-owned bounded-subagent contract where `--tools` alone grants nothing, a one-shot dispatch path with stdin-closed/no-resume/no-second-message/no-background semantics and a stdlib process-table descendant proof, and a single tooth-validated operator runbook plus raw-exit PowerShell tests whose piping/Tee-Object mutants are provably detected. Every positive contract has a locatable paired negative/mutation test; all verdicts derive from `gate_runner.py` raw records whose `record_sha256` I re-verified against the committed files; every final-freeze record carries `repo_head 1489879e`; and no production source changed after the freeze. AS-NEG is confirmed by `git ls-remote` (PR #241 at 4174a3b2, control at 6f5d12a6, no remote candidate). The two provenance nits (evidence-map's terminal-token citation; the loop.py wiring note) are minor and non-blocking. I return **PASS**; the DCV `directive-compliance-verifier` should still perform the independent requirement-by-requirement R515–R598 pass, which is outside this QA scope.
