# Deficit convergence — persistent-local-04 packet-collection gap (D-032-R020)

Method: `/deficit-convergence` (D-024 Amendment 51, R761-R766). Invoked under owner
directive D-032 Amendment 3 (source-003-amendment.md, R019/R020) after the run's
circuit breaker tripped. Status: evidence frozen, failure reproduced offline,
causal cluster bounded. Terminal verdict recorded in §7 when the repair closes.

## 1. Frozen evidence (rule 1)

- Run: `persistent-local-04`, task M2-T020, limited-auto, launched 2026-09-06T17:24:42Z,
  stopped 17:46:02Z on `circuit_breaker_hard_threshold` (breaker `consecutive_revision_loops`,
  threshold 4), final_state PREFLIGHT, cycles 4, elapsed 1280.6s, exit 11.
- Audit chain: `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075...\audit.jsonl`,
  sha256 `ecf013a821f1e694b604600e126bf3aacb893fc49f7fb21d77fe65e59b75a185` (81,499 bytes
  at freeze). Decision events seq 53, 66, 78, 88 — all `REVISE` by `gpt-6-astra`
  (attempts=1 each). Breaker events seq 91-93. Three exactly-once forwards
  (`fwd/1/886678c8`, `fwd/2/20940d66`, `fwd/3/537a08e2`) durable in the journal outbox.
- All four REVISE demands are materially identical: supervisor-collected, digest-bound
  contents of the untracked deliverables (`services/api/app/spatial/live_provider.py`,
  `services/api/tests/spatial/test_live_provider.py`,
  `project-control/reports/M2-T020-producer-report.md`), the canonical M2-T020 task
  contract, and separately-collected execution evidence for the two documented pytest
  commands; cycle-4 demand adds "do not stage or commit merely to make collection work"
  and "expanded worker assertions cannot replace the missing artifacts".
- Worker worktree at freeze: `wt-m2t020`, branch `task/M2-T020-live-spatial-provider`,
  HEAD = starting_sha `09524d1830c32284f5add8f293d0db39c5a8c22e`, porcelain: 2 tracked
  modifications (rule_evaluation.py, test_rule_evaluation_api.py) + the 3 untracked
  deliverables. Untouched — it is the pending M2-T020 implementation.
- Unrelated retained observation: unanswered owner ask `ask_327f3695`
  ("Approve PowerShell for M2-T020?", deferred 17:30:55Z, non-blocking; historically
  owner-denied). Not part of this cluster.

## 2. Identity record (rules 3-4)

| Surface | Identity |
|---|---|
| Control checkout | `ctl24`, branch `candidate/D-024-mrl-option-b`, capture commit `8f1af1a0` |
| Certified/installed controller | candidate `38773996`, subtree `520a4904` (== ctl24 HEAD subtree, verified byte-identical) |
| Worker worktree | `wt-m2t020` @ `09524d18` (above) |
| Provider CLIs | codex-cli 0.153.4 (`c54db675...`), claude.exe 217,406,624 B (`e713c5a6...` head+size) |
| Models | reviewer `gpt-6-astra@high` (model_selection digest `18b83e7f...`), worker `claude-fable-5` |
| Controller version | 0.4.0-phase4 |

## 3. Offline reproduction (rule 2 — no live rerun)

`evidence.build_packet` invoked directly with `loop._collect`'s exact inputs
(`EvidenceCollector(repo_root=wt-m2t020)`, git facts + project_control + checkpoint):

- Packet sections produced: `claude_checkpoint`, `directive_refs`, `git`,
  `project_control` — nothing else. No `task_packet`, no `reports`, no transcripts.
- `git.diff_content` = 12,217 bytes = the two TRACKED modifications only.
- Distinctive body-line probes from each of the three untracked deliverables:
  **0/3, 0/3, 0/3 found** anywhere in the packet. Task-contract title: absent.
- `failed_collections`: none — the omission is silent, not a collection failure.

## 4. Complete causal path (rule 5)

1. Workers operate under orchestrator-only git: deliverables NECESSARILY stay
   uncommitted; new files stay untracked for the task's whole life.
2. `loop.py::_collect` (certified subtree `520a4904`) builds the packet from
   `collect_git_facts()` + `collect_project_control()` + the bounded checkpoint only;
   `build_packet`'s `task_packet=`, `reports=`, `extra_sections=` parameters and
   `EvidenceCollector.read_file` exist but are never wired in.
3. `GIT_FACT_COMMANDS.diff_content` = `git diff --no-ext-diff --no-textconv HEAD`:
   tracked changes only. Untracked files appear as NAMES in `porcelain_status`.
4. `codex_reviewer.REVIEW_INSTRUCTIONS` (M0-T147) tells the reviewer: "EVERY fact you
   need arrives in the packet" and `git.diff_content` is "the ACTUAL patch text of
   every uncommitted change" — a FALSE premise for untracked files — and item 3
   directs "REVISE for material gaps in the WORKER's evidence".
5. The reviewer therefore correctly and deterministically REVISEs; the worker has no
   lever over packet assembly (its checkpoint `changed_files`/`reports` declarations
   are never used for collection; staging/committing is prohibited); the identical
   demand loops; `consecutive_revision_loops` trips at 4.
6. Broker approvals never capture worker-run command output (PreToolUse-shaped:
   decision only), so "supervisor-collected execution evidence" for the documented
   pytest commands does not exist anywhere the packet could cite.

Cascading (not primary): M2-T020 acceptance chain parked; run budget consumed;
one owner touch recorded. NOT-RUN: nothing — all four cycles completed cleanly.

## 5. Known-good comparison (rule 8)

M0-T147 (accepted, G3+G5 two-round PASS at `dee758f4`) certified the packet-based
contract against runs whose review surface was the ROTATE_SESSION/false-exec failure;
no certified scenario exercised a checkpoint with UNTRACKED deliverables reaching a
content verdict. persistent-local-04 is the first content-level review under the
contract — the gap is a certified-contract blind spot, not a regression.

## 6. Bounded repair cluster (rules 9-11)

ONE cluster, one root cause: **the review contract promises complete
supervisor-collected evidence; the builder omits three evidence classes.**
Repair (task M0-T148, supervisor defect lane):

1. `evidence.py`: collect `untracked_content` — bounded, digest-bound contents of
   every `??` path in porcelain (per-section byte bound, explicit truncation records,
   count cap fail-visible); collect `task_packet` — the task contract via `read_file`.
2. `loop.py::_collect`: wire both in; add `command_transcripts` — the packet-documented
   test commands executed by the SUPERVISOR via `process.run()` (bounded capture,
   argv/exit/digest recorded) in the worker worktree at review time.
3. `codex_reviewer.REVIEW_INSTRUCTIONS`: name the three sections; remove the false
   "every uncommitted change" premise (pure-ASCII, deterministic; schema unchanged —
   rule 11: provider-facing schema stays minimal).
4. `review_packet.py` guard + tests: new sections pass packet-wide immunization;
   positive/negative/mutation tests per rule 16; suite re-baseline per freeze rule.
5. Docs: this report + packet-contract description.

Qualifying evidence (AD-093 / supervisor freeze §2): reproduced defect (§3) AND
inability to complete an authorized product task (M2-T020) AND provider-boundary
evidence from a live commissioning run; directive authority D-032-R020.

Out of scope (recorded, not expanded): MRL sibling REVIEW_INSTRUCTIONS false-exec
premise (already-tracked follow-up); process.py capture-cap G5 LOW-1; queue-JSON
continuity shape-validation relocation.

## 7. Terminal verdict: VERIFIED_CLOSED (2026-09-06, M0-T148 accepted — 160th)

Closure matrix at the frozen candidate (task commit `53d642a1`, merged `7772626e`,
accept HEAD `4bb2f8f4`):

| Exit criterion | Evidence |
|---|---|
| Repair implements the full cluster | `untracked_content` + `task_packet` + `command_transcripts` sections wired via `collect_completeness`; REVIEW_INSTRUCTIONS truth-repaired (diff_content = TRACKED only) |
| Reproduction closed (S6) | The §3 reproduction re-run against the repaired builder: 9/9 deliverable content probes present (was 0/9), task contract present, both documented pytest commands supervisor-executed with digest-bound transcripts, 7 sections, 95,707 B < 262,144 cap, no stop |
| Focused + affected tests | 243 focused passed (orchestrator re-run); adjacent review-path 299 passed / 1 skipped (G3 reviewer re-run) |
| One full regression at frozen candidate | 4231 passed / 3 skipped / 1 failed; the single failure (`test_two_active_directives_validate_and_coexist`) traced to backlog packet M0-T149's then-missing allowed_paths validated live mid-run (c17), NOT to the reviewed code; fixed in `4bb2f8f4`; full directive test file re-run: 120 passed |
| Independent gates | G3 PASS (code-reviewer), G5 PASS (security-reviewer), G2 self-check, all at `7772626e`, content manifest `6723f8d8...` identical at 53d642a1/7772626e/HEAD |
| Directive verification | DCV empty-set row recorded (reviewed_sha `4bb2f8f4`, resolver-derived 20/20 D-032 rows inapplicable, no selective citation across all 30 active directives) |
| Residuals tracked, not expanded | G3 LOW-1 → backlog task M0-T149 (non-mutating command profile); G5 LOW-1/LOW-2 carried into the R247 recertification note below; LOW-3/LOW-4 informational |

No further live rerun occurred before closure (rule 20 held). **Relaunch
prerequisites now in force (R247):** the `tools/agent_supervisor` subtree changed,
so before any next launch: recertify the new accepted candidate, re-pin
`tools/controller_update/source_binding.json` via a reviewed commit, reinstall the
controller, and use a FRESH run-id (the `consecutive_invalid_outputs`/revision
breaker tallies are durable per run-id). Recertification note must retain G5
LOW-1 (untracked-content outbound surface, git-ignore + redaction mitigated) and
LOW-2 (documented-command execution of worker-authored test files at review time,
containment mitigated).
