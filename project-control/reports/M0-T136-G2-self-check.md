# M0-T136 G2 producer self-check (Tranche B, frozen candidate 1489879e)

Producer: the primary session (sole integrator/committer per D-024-R524/R525).
Frozen Tranche-B candidate: `1489879e1f6787a9d53ed74db4524b24039e03a2`
(tree `0babc4691...`, branch `candidate/D-024-mrl-option-b`, LOCAL ONLY).
All gate verdicts below are `tools/gate_runner.py` raw records under
`project-control/reports/M0-T136-gates/` (indexed with SHA-256 in
`project-control/reports/M0-T136-tranche-b-evidence.json`); nothing here is a
hand-authored success claim (R592).

| Scenario | Self-check result | Primary evidence |
|---|---|---|
| AS-B0-1 modularity | PASS - baseline byte-identical to 6f5d12a6 (0-line diff, re-proven at freeze); exceptions differ ONLY by the deleted `claude_runner.py` entry; limit+SLOC proven before deletion | `b0-modularity-after-deletion.json` rc0; `b0-modularity-mutant-growth-without-exception.json` killed; `final-freeze-modularity.json` rc0 |
| AS-B0-2 guidance | PASS - CLAUDE.md principle 17 + /engineering-reliability "Defect convergence"; context budget green at B0 and at the final freeze | `b0-context-budget-after-guidance.json`, `final-freeze-context-budget.json` rc0 |
| AS-B0-3 freeze | PASS at B0 SHA 44702645 | all `b0-freeze-*.json` (root ruff rc1 = pre-existing F28, stdout byte-identical to the final-freeze run) |
| AS-B1 launch manifest | PASS - `start --launch-manifest` sole entrance; per-field paired negatives; manifest never proof | `mrl_launch_manifest.py`, `mrl_launch_path.py`, tests in `final-freeze-supervisor-suite.json` rc0 (86 modules) |
| AS-B2 exec chains | PASS - streaming SHA-256 wrapper->runtime->entrypoint before every spawn, no size/mtime cache; replacement/retarget/updater/model-version mutations covered | `mrl_exec_chain.py` + `test_agent_supervisor_mrl_exec_chain.py` (in suite) |
| AS-B3 bounded subagents | PASS - contract limits/depth/foreground/identity/accounting/denials; `--tools`-alone-grants-nothing and over-limit paired tests | `mrl_subagent_contract.py` + tests (in suite) |
| AS-B4 one-shot | PASS - one fresh process, one prompt, schema-bound WorkerResult, stdin closed, no resume/second message/background fallback (mutation tests each); accounting; descendant proof | `mrl_one_shot.py`, `mrl_descendants.py`, `mrl_one_shot_review.py` + tests (in suite) |
| AS-B5 launch path | PASS - `docs/MRL_LAUNCH_RUNBOOK.md` presents exactly ONE start (tooth-validated); CONTROLLER_UPDATE_RUNBOOK s11 OBSOLETE with no start; ps_tests preserve raw $LASTEXITCODE with $?/Tee-Object/no-exit/cmd-pipe mutants all DETECTED; ten-item canary package presented, NOT executed | `final-freeze-doc-check-*.json` rc0, `final-freeze-ps-tests.json` rc0, `final-freeze-mutation-doc-check.json` killed=true |
| AS-EV evidence | PASS - paired negatives throughout; raw gate records only; ONE final verification at 1489879e; SESSION_HANDOFF regenerated only at that freeze | `final-freeze-*.json` (17 records, all repo_head 1489879e) |
| AS-NEG restrictions | PASS - no push (branch has no upstream), remote `control/D-024-fable-codex-loop` still 6f5d12a6, PR #241 head 4174a3b2 untouched, no remote candidate branch, no merge/self-acceptance/live canary/Tranche C; one terminal token in the final report | producer report section "Protected-surface comparisons" |

Known limitations reported (not concealed): root-tree ruff rc1 is pre-existing
F28 (byte-identical stdout at B0 and final freeze; out of packet scope); live
CLI `--allowedTools`/dontAsk/`permission_denials` shapes and Windows
process-tree cleanup are provable only by the owner-run canary (R579, packet
risk 3). Producer != reviewer: this self-check authorizes nothing; G3/G4/DCV
review and acceptance remain with independent reviewers and the orchestrator.
