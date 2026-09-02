# M0-T136 producer report - D-024 Amendment 40 Tranche B (R515-R598)

Producer/integrator: the primary session (sole committer, D-024-R524/R525).
Everything below is offline; NOTHING was pushed, merged, launched, or executed
against a live provider (R520-R523). This report carries every R597 item and
every blocker together.

## 1. Identities

- **Archive identity (Tranche A):** branch `stabilization/D-024-mrl` @ `76c4edff`,
  reviewed content `ad770ad4`, material identity `1c3078c6` - accepted as M0-T134.
- **Clean-base identity:** `candidate/D-024-mrl-option-b` based at
  `6f5d12a6` (= remote `control/D-024-fable-codex-loop`, still at that SHA);
  Tranche-A tools reapply `2f3ab124`; governance continuity `1599daaf`.
- **Governance continuity mapping:** `project-control/reports/M0-T134-cross-sha-continuity.md`
  - all 22 Tranche-A blobs at the candidate base byte-identical to `ad770ad4`;
  material identity `1c3078c6` reproduced at the reapply.
- **Frozen B0 candidate:** `44702645` (records `b0-freeze-*.json`).
- **Frozen Tranche-B candidate (FINAL):** `1489879e1f6787a9d53ed74db4524b24039e03a2`
  (tree `0babc4691...`). The single complete affected + repository verification
  (R593) ran once at this SHA (`final-freeze-*.json`); any later code change
  invalidates it (R594). Evidence/report commits after it are control-plane
  only (reports + SESSION_HANDOFF), no production code or tests.

## 2. Exact commits (base -> candidate)

`895cfbe5` B0 freeze -> `2bcd9aa8` failure-surface survey -> `0e37e115` C-B1
launch manifest -> `9c8be98d` C-B2 exec chains -> `0e0c4bcc` + `5319c50a` C-B3
bounded subagents -> `4bf845cd` C-B4 one-shot wiring -> `a57802cc`/`472ae045`
packet scope (orchestrator capacity) -> `d39c49bb` C-B5 part 1 -> `aa63a50f`
owner-invoked handoff -> `1489879e` C-B5 part 2 (frozen candidate) -> one
evidence commit after it (reports + regenerated SESSION_HANDOFF only).

## 3. Changed files

100 paths vs base `6f5d12a6` (`git diff --name-status 6f5d12a6..1489879e`).
Groups: new `tools/agent_supervisor/mrl_*.py` modules (launch manifest, exec
chain/identity, subagent contract + hook, one-shot + descendants + review,
transport, worker result, codex decision, remote, launch draft, launch path)
with `tools/agent_supervisor/schemas/*.json`; `tools/gate_runner.py`; paired
test modules `tools/test_agent_supervisor_mrl_*.py`, `_command_docs.py`,
`_checkpoint_extraction_split.py`, `test_gate_runner.py`;
`tools/agent_supervisor/ps_tests/**` (harness, runner, 3 tests, 3 mutants);
wiring edits to `cli.py`, `loop.py`-adjacent seams (`start_gate.py`,
`claude_runner.py`, `checkpoint_extraction.py` split), `command_docs.py`,
`mrl_launch_path.py`; docs (`MRL_LAUNCH_RUNBOOK.md` new,
`CONTROLLER_UPDATE_RUNBOOK.md` s11 obsoleted, package README pointer,
CLAUDE.md principle 17, engineering-reliability skill); control-plane
(M0-T134 acceptance artifacts, packets M0-T134..T137, amendments 38-40
captures, campaign/state - orchestrator capacity);
`tools/modularity_exceptions.json` (ONLY the claude_runner.py deletion).

## 4. Root-cause clusters

`project-control/reports/M0-T136-failure-surface.md`: 30-row inventory
(F1-F30), change-impact and variant analyses, five clusters C-B1..C-B5 each
repaired as ONE bounded change, closure at the frozen candidate in section 6.
One additional in-cluster mismatch converged during C-B5 part 2:
`apply_launch_manifest` collapsed `launch_manifest_base_ref_missing` into
`launch_manifest_invalid`; repaired with its paired test (C-B1 contract).
F28/F29 remain out of cluster (recorded, untouched).

## 5. Tests and raw return codes (final frozen verification, R593)

All from `tools/gate_runner.py` raw records at repo_head `1489879e`, indexed in
`M0-T136-tranche-b-evidence.json` (32 records total: 15 B0 + 17 final):

| Gate | Record | rc |
|---|---|---|
| 77 Tranche-A cases (7 modules) | `final-freeze-tranche-a-77.json` | 0 |
| Full affected supervisor suite (86 modules, `-q -p no:cacheprovider`) | `final-freeze-supervisor-suite.json` | 0 |
| Modularity `--check` (unpiped) | `final-freeze-modularity.json` | 0 |
| Ruff, changed files | `final-freeze-ruff-changed-files.json` | 0 |
| Ruff, CI scope (`services/api`) | `final-freeze-ruff-ci-scope.json` | 0 |
| Ruff, root tree | `final-freeze-ruff.json` | 1 (pre-existing F28; stdout SHA-256 byte-identical to `b0-freeze-ruff.json`) |
| validate_directive_compliance --check | `final-freeze-directive-compliance.json` | 0 |
| validate_mcp_policy / validate_product_map | `final-freeze-mcp-policy.json` / `final-freeze-product-map.json` | 0 / 0 |
| campaign_continuity --status / project_control status | `final-freeze-campaign-continuity.json` / `final-freeze-project-control-status.json` | 0 / 0 |
| context_budget_check | `final-freeze-context-budget.json` | 0 |
| Command-doc tooth: default docs / MRL runbook / canary package | `final-freeze-doc-check-{default,mrl-runbook,canary}.json` | 0 / 0 / 0 |
| ps_tests runner (3 test files, real powershell.exe -File) | `final-freeze-ps-tests.json` | 0 |

## 6. Mutation results

- `final-freeze-mutation-doc-check.json`: runbook copy stripped of the pinned
  `--checkout` lines -> tooth FAILS -> mutation `killed=true, ok=true`.
- `b0-modularity-mutant-growth-without-exception.json`: growth without an
  exception FAILS the checker -> killed.
- Inside `final-freeze-ps-tests.json` (asserted by `test_mutants_detected.ps1`):
  `$?`-after-cmdlet greens a child exit 7 (DETECTED), `-File` script ending
  `native | Tee-Object` without `exit` reports 0 (DETECTED), `cmd /c` pipe
  destroys the 7 into findstr's 1 (DETECTED); the real harness preserves 7
  (control).
- Every B1-B5 positive contract carries its paired negative/mutation test in
  the suite (per-field manifest mismatches, chain replacement/retarget,
  updater re-enablement, model/version mismatch, `--tools`-alone,
  over-limit fan-out, resume/second-message/background-fallback refusals,
  base_ref-missing specific refusal, pinned-flag removal).

## 7. Modularity without the exception

The stale `tools/agent_supervisor/claude_runner.py` exception entry was deleted
after its baseline limit (1410) and observed SLOC were proven
(`b0-modularity-after-deletion.json` rc0); `tools/modularity_baseline.json` is
byte-identical to `6f5d12a6` (0-line diff, re-proven at the final freeze);
`final-freeze-modularity.json` rc0 with warn-only pre-existing signals.

## 8. Protected-surface comparisons (final)

- `git status -sb` -> `## candidate/D-024-mrl-option-b` (NO upstream: never pushed).
- `git ls-remote origin`: `control/D-024-fable-codex-loop` = `6f5d12a6`
  (untouched base); `refs/pull/241/head` = `4174a3b2` (PR #241 untouched, still
  never merged); NO remote `candidate/*` ref exists.
- Forbidden paths: `tools/modularity_baseline.json` byte-identical; control-plane
  files (`project-control/tasks|directives|gates|state|campaigns`) changed only
  in orchestrator-capacity commits per ADR-005; no `.github/workflows/**`,
  `.claude/settings.json`, hooks, or rules edits.
- Working tree after the evidence commit: clean.

## 9. Owner-run canary package

`project-control/reports/M0-T136-canary-package.md` - ONE package, the ten
R587 items verbatim, exact PowerShell, NOT executed (R523). Supervised mode
stated as the deliberate canary mode; every `start` manifest-form with distinct
`--run-id canary-b5-NN` and `--max-cycles 1`; prerequisites = owner-typed
controller update from the frozen candidate (CONTROLLER_UPDATE_RUNBOOK s3-s8)
and a draft re-run after the final commit; evidence map bound to
`one_shot_unit.json` / `subagent_ledger.json` / `codex_decision.json` fields;
tooth-validated (`final-freeze-doc-check-canary.json` rc0).

## 10. Blockers and follow-ups (all together; none stopped Tranche B)

1. `tools/supervisor_command_doc_check.py` `DEFAULT_DOCS` does not include the
   MRL runbook (file not in packet scope); CI covers it only via `--doc` -
   orchestrator follow-up to add it.
2. `.claude/skills/loop-start/SKILL.md` and
   `.claude/hooks/loop_command_interceptor.py:202` still reference the legacy
   launch shape (out of packet scope; F22 residue).
3. ps_tests are not wired into CI (`.github/workflows/**` forbidden here).
4. `docs/CONTROLLER_UPDATE_RUNBOOK.md` s9/s10 still name the retired
   `wt-m0t063` identities.
5. The amendment is silent on the canary `--mode`; supervised was chosen and is
   stated in the package.
6. Live CLI `--allowedTools`/dontAsk/`permission_denials` shapes and Windows
   process-tree cleanup are proven only by the owner-run canary (R579).
7. R595-vs-handoff timing: seq-71 handoff was owner-invoked mid-tranche; the
   frozen-candidate regeneration (this freeze) is the R595-conformant one.
8. Root-tree ruff F28 (52 pre-existing findings, byte-identical to base) is
   outside the CI contract and untouched.
9. M0-T137 (model-selection addendum) stays BACKLOG on owner rows
   R603/R604/R605 - never interpreted.

## 11. Terminal status

Producer submission only - no self-acceptance (R596-R598). G3/G4/DCV review and
the gate/accept decisions belong to independent reviewers and the orchestrator.
