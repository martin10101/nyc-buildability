# M0-T136 directive-compliance verification (DCV) — verbatim verifier return

Recorded by the orchestrator/verifier session per the report-preservation rule
(`.claude/rules/project-control.md`): the independent verifier's return is saved
VERBATIM below (transport entity-decoding only: `&amp;`/`&gt;` decoded).
Verifier: `directive-compliance-verifier` (read-only; producer =
`mrl-tranche-b-producer`; producer != verifier). Received 2026-09-02.

The orchestrator/verifier session additionally reproduced, before this DCV ran
and independently of it (raw unpiped exit codes at HEAD `1da9d513`, production
tree byte-identical to frozen candidate `1489879e`): 77 Tranche-A cases rc 0;
the full 86-module supervisor suite rc 0 (3548 passed, 2 skipped);
modularity --check rc 0; ruff changed-files rc 0, CI scope (services/api) rc 0,
root tree rc 1 with stdout SHA-256 74680cc7... byte-identical to both frozen
records (pre-existing F28); validate_directive_compliance --check,
validate_mcp_policy, validate_product_map, context_budget_check,
campaign_continuity --status, project_control status all rc 0; doc checks
(default / MRL runbook / canary package) rc 0; ps_tests on real PowerShell 5.1
rc 0 with all three mutants DETECTED; doc-check mutation rc 1 (killed);
modularity growth mutant rc 1 (killed); all 32 gate-record SHA-256s match the
index; no mrl/ run directory under either runtime; ls-remote: no candidate/*
ref, control/D-024-fable-codex-loop = 6f5d12a6, refs/pull/241/head = 4174a3b2.

---

# DCV Gate Report — M0-T136 (D-024 Amendment 40, Tranche B)

**Reviewer:** directive-compliance-verifier (read-only, producer ≠ verifier)
**Frozen CODE candidate:** `1489879e` · **HEAD:** `1da9d513` · **Diff base:** `6f5d12a6` · **Branch:** `candidate/D-024-mrl-option-b` (no upstream)
**Applicable set:** D-024-R516 + R518..R598 = 82 rows (R515/R517/R599+ are owner-decision / M0-T137 rows, excluded — independently confirmed via requirements.json applicability).

## Independently reproduced anchors
- HEAD `1da9d513`; `git diff --name-status 1489879e..HEAD` = control-plane only (reports, `state.json`, `tasks/M0-T136.json`, `docs/SESSION_HANDOFF.md`); **no tools/ or production source after freeze**.
- `6f5d12a6` is ancestor of HEAD; 17 commits, **single committer** martin10101; chain 2f3ab124(B0 reapply)→…→1489879e(C-B5).
- **All 32 gate-record SHA-256s match the index**; 17 final-freeze records all carry `repo_head 1489879e` (reproduced with python/hashlib).
- **19 reapplied blobs byte-identical to accepted tree 5e89175d** (per-path `git rev-parse`, 0 mismatches); M0-T134 content identity `1c3078c6…` **reproduced at HEAD**.
- M0-T134 `status=accepted`; M0-T136 `status=awaiting_gate` (not self-accepted).
- ruff root stdout_sha256 `74680cc7…`(21138 B) **identical** at b0-freeze and final-freeze (F28 pre-existing, zero new lint); services/api ruff rc0.

## Per-requirement verdicts (all 82, in order)

| ID | Verdict | Primary evidence |
|---|---|---|
| R516 | PASS | One bounded B0–B5 workflow, commits 2f3ab124..1489879e (git topo, 17 commits incl B0 reapply) |
| R518 | PASS | Commit 2f3ab124 changed exactly 19 named files incl 4 individual schema files — explicit paths, not a dir checkout |
| R519 | PASS | `git rev-parse @{u}` → "no upstream"; all commits local |
| R520 | PASS | remote control/D-024-fable-codex-loop=6f5d12a6 unchanged, no remote candidate ref; status=awaiting_gate; no mrl run dirs |
| R521 | PASS | refs/pull/241/head=4174a3b2 untouched (orchestrator ls-remote) |
| R522 | PASS | No Tranche-C work on branch; producer report §10/§11 |
| R523 | PASS | canary-package.md header "NOT executed"; no mrl/canary run dirs; final-freeze-doc-check-canary.json rc0 |
| R524 | PASS | Foreground read-only tracing subagents in survey (2bcd9aa8); no writer subagents |
| R525 | PASS | `git log --format=%an` = 17× martin10101 (single integrator) |
| R526 | PASS | 30-row inventory F1–F30 in failure-surface.md §1, commit 2bcd9aa8 precedes all C-Bx commits |
| R527 | PASS | failure-surface.md §2 change-impact + §4 five clusters, each one bounded change across producers/consumers/schemas/CLI/tests/docs |
| R528 | PASS | failure-surface.md §5 cadence; only 2 full-suite records (b0-freeze @447026458, final @1489879e) |
| R529 | PASS | `git rev-parse stabilization/D-024-mrl`=76c4edff, no upstream; cross-sha-continuity.md §1 |
| R530 | PASS | Archive not in candidate ancestry, no tranche commits (git); continuity §1 |
| R531 | PASS | candidate/D-024-mrl-option-b exists uniquely from clean base (git branch); no collision (procedurally attested by unique fresh branch) |
| R532 | PASS | `git merge-base --is-ancestor 6f5d12a6 HEAD`=yes; first commit 2f3ab124; local only |
| R533 | PASS | 2f3ab124 = 19 explicit file paths incl 4 individual schemas; no directory checkout |
| R534 | PASS | **Independently confirmed all 19 blobs byte-identical to 5e89175d (0 mismatches)**; identity 1c3078c6 reproduced |
| R535 | PASS | candidate lacks ad770ad4/76c4edff in ancestry (git); registry files not copied, only deltas (continuity §3) |
| R536 | PASS | Reference-closure inventory continuity §3 precedes governance commit 1599daaf |
| R537 | PASS | Semantic state via canonical tooling + targeted edits (1599daaf); b0-freeze validators rc0 |
| R538 | PASS | continuity §4 NOT carried: M0-T133 renewal, obsolete handoff, stale next_action, ancestry |
| R539 | PASS | validate_directive_compliance --check rc0 (b0-freeze + final-freeze-directive-compliance.json) — no dangling refs |
| R540 | PASS | b0-freeze directive-compliance/mcp-policy/product-map/campaign-continuity/project-control-status/context-budget all rc0 |
| R541 | PASS | **Confirmed M0-T134 status=accepted (task+state.json); final-freeze-campaign-continuity.json rc0** (one coherent next state) |
| R542 | PASS | Explicit cross-SHA provenance record M0-T134-cross-sha-continuity.md (content identity, not commit-id pretense) |
| R543 | PASS | Deletion after M0-T134 acceptance; only the claude_runner.py entry removed (git diff exceptions.json) |
| R544 | PASS | `git diff 6f5d12a6..1489879e` exceptions.json = only that one block removed; no renew/extend/replace |
| R545 | PASS | `git diff --stat` modularity_baseline.json = empty (byte-identical) |
| R546 | PASS | baseline claude_runner.py=1258 (limit ~1383); gate green without exception proves current SLOC ≤ limit (b0-modularity-after-deletion.json rc0) |
| R547 | PASS | Only tools/agent_supervisor/claude_runner.py entry deleted (git diff) |
| R548 | PASS | b0-modularity-after-deletion.json rc0 + final-freeze-modularity.json rc0 (raw returncode, gate_runner) |
| R549 | PASS | Inert baseline-regeneration record untouched (no edit in diff) |
| R550 | PASS | Guidance via existing architecture (CLAUDE.md principle 17 + engineering-reliability SKILL.md), no new skill |
| R551 | PASS | CLAUDE.md principle 17 "Defect convergence" short always-loaded instruction (loaded in-context) |
| R552 | PASS | .claude/skills/engineering-reliability/SKILL.md §"Defect convergence" (line 21), one section |
| R553 | PASS | SKILL.md lines 26–39 name all 7: failure-surface inventory, change-impact, variant analysis, root-cause clustering, bounded repair, progressive verification, frozen-candidate regression |
| R554 | PASS | context-budget rc0 (b0-context-budget-after-guidance.json + final-freeze-context-budget.json) |
| R555 | PASS | B0 freeze @447026458: tranche-a-77, supervisor-suite, modularity, **applicable lint (services/api ruff-ci-scope rc0)**, all validators rc0 (root-tree ruff rc1 = F28, out of CI contract ci.yml:191/211) |
| R556 | PASS | Every b0-freeze record rc0 except F28 (byte-identical to base: stdout_sha256 74680cc7 identical b0/final); no unresolved B0 failure |
| R557 | PASS | mrl_launch_manifest.py/mrl_launch_path.py: `start --launch-manifest` ABSOLUTE-path one entrance (LaunchManifest.load requires absolute; cli.py:2951/3275) |
| R558 | PASS | verify_launch independently observes each field (observe()); manifest never used as observation |
| R559 | PASS | EXPECTED_FIELDS = exactly the 12 R559 fields (mrl_launch_manifest.py:45-48); observe() derives from git/fs/packet |
| R560 | PASS | verify_launch refuses on ANY mismatch; "LAUNCH REFUSED before provider launch (R560)"; preflight raises LoopError('launch_manifest_mismatch') |
| R561 | PASS | mrl_exec_chain.resolve_chain resolves wrapper→runtime→entrypoint(→vendor) for claude+codex, fail-closed |
| R562 | PASS | bind/verify_chain_now complete streaming SHA-256 immediately before spawn, no cache (docstring l.217; used in mrl_one_shot before Popen) |
| R563 | PASS | verify_child_env asserts updater-disabled on exact Popen env (exec_chain.py:238; one_shot verify_child_env(env)) |
| R564 | PASS | observe_version + observed_model_from_result + verify_runtime_identity; version mismatch raises (one_shot.py:242-245,334-337); absence fails closed |
| R565 | PASS | test_...mrl_exec_chain.py has all 5: same_size_restored_mtime, wrapper_retargeting, entrypoint_replacement, updater_reenablement, runtime_identity mismatch |
| R566 | PASS | SubagentContract admits agent_inventory; "Subagents are NOT permanently forbidden" |
| R567 | PASS | max_concurrent/max_total configurable; _deny_reason enforces both limits (contract.py:236-239) |
| R568 | PASS | MAX_DEPTH=1; _deny_reason denies depth≠1 & parent≠primary (223-226); __post_init__ refuses max_depth≠1 |
| R569 | PASS | foreground_only=True; _deny_reason denies background (227-228) |
| R570 | PASS | Contract binds task_id/repo_root/allowed_paths/tools_inventory from manifest (subagent_contract()); profile echoes them |
| R571 | PASS | SubagentLedger issues child_id=primary.cNNN bound to parent + accounting (211,274-285) |
| R572 | PASS | single-writer + max_concurrent permit parallel read-only agents (tools Read/Grep/Glob) |
| R573 | PASS | WRITER_POLICIES=("single-writer",); isolation refused fail-closed (no overlapping writers) |
| R574 | PASS | Subagents read-only (agents Read/Grep/Glob; prompt forbids edit/commit/push/PR/merge/accept); paired test |
| R575 | PASS | Complete descendant termination via mrl_descendants.prove_zero_descendants (real Toolhelp32/procfs/ps), consumed in one_shot _finish (code comments mis-tag MCP/inventory as R575 — cosmetic) |
| R576 | PASS | MCP_DENY_RULE always in denies + --strict-mcp-config + mcp allow-rule refused; out-of-inventory subagent denied (_deny_reason:233) |
| R577 | PASS | build_restricted_profile: --restricted, dontAsk, --tools inventory, --allowedTools/--disallowedTools, --strict-mcp-config, --settings; managed policy hashed into identity |
| R578 | PASS | effective_grants()=inventory∩allows−denies; "--tools alone grants nothing (R578)"; paired test |
| R579 | PASS | Capability deferred to owner-run Windows canary consistently: contract docstring l.26-27, canary items 6/8/9, producer §10.6, failure-surface F29 — offline tests not capability proof |
| R580 | PASS | mrl_one_shot.py wires WorkerResult/build_claude_checkpoint/transport/exec-chain/descendants/ledger; selected in cli._run_loop when launch present (cli.py:2742); commit 4bf845cd |
| R581 | PASS | One fresh process (_dispatched + calls>1 raise), one prompt (communicate once, stdin closed), --json-schema WorkerResult, extra_turns refused, no resume/2nd-msg/background (docstring) |
| R582 | PASS | accounting=ledger.close(); processes_total=1+issued; subagent_accounting_violation check (340-343); denials capped 50 |
| R583 | PASS | max_turns + wall_clock into build_one_shot_plan; over-limit refusals; process limit = single fresh process + accounting |
| R584 | PASS | _watch cancel/deadline→_terminate→prove_zero_descendants; proven=False fail-closed→degraded (descendants.py:152-180; one_shot:307-310) |
| R585 | PASS (scoped) | MRL_LAUNCH_RUNBOOK.md one start (line 57); CONTROLLER_UPDATE_RUNBOOK s11 "OBSOLETE" (line 221, no start); bare start refuses missing_required_inputs exit 13; legacy code path undocumented (F26); 2 out-of-packet doc surfaces disclosed as open items (§10.2) |
| R586 | PASS | ps_tests/harness.ps1 unpiped `&` + immediate $LASTEXITCODE + fail-closed; test_mutants_detected.ps1 kills 3 mutants; final-freeze-ps-tests.json rc0 |
| R587 | PASS | canary-package.md ONE package, ten R587 items verbatim + exact PowerShell (table 131-140); doc-check-canary rc0 |
| R588 | PASS | Header "NOT executed"; no mrl run dirs; producer §9 |
| R589 | PASS | Paired mutations: exec_chain(5), ps(3), doc-check killed=true, modularity-growth mutant killed=true, subagent over-limit denial |
| R590 | PASS | gate_runner.py = direct subprocess/raw exit/stdout_sha256; **all 32 record SHA-256s verified against index** |
| R591 | PASS | gate_runner "reports GENERATED FROM that record, never authored by hand"; ruff stdout_sha256 identical b0/final proves no hand-editing |
| R592 | PASS | Only 2 full-suite runs recorded (b0-freeze + final); interim focused module runs (failure-surface §5) |
| R593 | PASS | **17 final-freeze-*.json all repo_head 1489879e (verified)** — one complete affected+repo verification |
| R594 | PASS | `git diff --name-status 1489879e..HEAD` = control-plane only, no code/tests |
| R595 | PASS | SESSION_HANDOFF regenerated at final frozen candidate (seq-72 commit 0ef33868, R595-tagged); seq-71 (aa63a50f) owner-invoked & recorded; only these 2 commits touched it |
| R596 | PASS (substance) | Terminal token `TRANCHE_B_OFFLINE_COMPLETE_CANARIES_READY` durable, **exactly once**, at docs/SESSION_HANDOFF.md:27 (producer seq-72 finishing artifact at frozen candidate); CONSOLIDATED_BLOCKED absent. **Evidence-map citation is WRONG** (see discrepancies) |
| R597 | PASS | producer-report.md §1–9 = identities/continuity/commits/changed-files/clusters/tests+raw-codes/mutations/modularity-without-exception/protected-surface/canary |
| R598 | PASS | producer-report.md §10 lists all 9 blockers together; no push/real-loop/Tranche-C (verified remote+status) |

## FAIL / UNVERIFIABLE rows
**None.** All 82 applicable requirements are SATISFIED on reproduced primary evidence.

## Discrepancies found in the producer's evidence map (non-blocking)
1. **R596 — wrong citation (material to locate, not to substance).** The map states the terminal token ends "the final producer report … (producer report s11)". Reproduced: the token is **absent** from `M0-T136-producer-report.md` §11 (which reads "Producer submission only - no self-acceptance"). It appears durably exactly once at `docs/SESSION_HANDOFF.md:27` — the producer's seq-72 finishing artifact written at the frozen candidate. The requirement's substance (finish with exactly one of the two tokens; CONSOLIDATED_BLOCKED absent) is met; only the map's file pointer is incorrect.
2. **R534 — citation vs. requirement anchor.** The map proves byte-identity against reviewed commit `ad770ad4` / identity `1c3078c6`; R534 literally names accepted code tree `5e89175d`. I re-derived byte-identity **directly against 5e89175d** (0 mismatches), so the obligation holds; the two anchors are consistent (5e89175d is the reviewed code tree, ad770ad4 the reviewed commit).
3. **Code-comment mislabel (cosmetic).** `mrl_subagent_contract.py` tags MCP-denial and out-of-inventory-denial `_deny_reason` branches "(R575)"; the textual match is R576 (R575 = descendant termination). Both functions exist and pass; comment only.
4. **R585 scope honesty (already disclosed, not hidden).** Within packet scope there is one operator launch path (MRL runbook; s11 obsoleted). Two out-of-packet doc surfaces (`.claude/skills/loop-start/SKILL.md`, `.claude/hooks/loop_command_interceptor.py:202`) and the legacy explicit-flag code path (kept for the pinned test surface, refused at runtime via missing_required_inputs exit 13) still reference/permit the legacy shape — the producer records these transparently as open orchestrator items (failure-surface F22/F26, producer §10.2), so R585 as scoped is met.

## Overall DCV verdict: **PASS**

All 82 applicable D-024 requirements (R516 + R518..R598) are independently verified SATISFIED at frozen candidate `1489879e` on reproduced primary evidence (git objects, load-bearing source in `mrl_launch_manifest/mrl_launch_path/mrl_exec_chain/mrl_subagent_contract/mrl_one_shot/mrl_descendants`, `gate_runner`-recorded gate results with verified SHA-256s, and control-plane state). No production code/tests changed after the freeze (R594 intact); prohibited actions confirmed not taken (no push/PR/merge/accept/deploy/live-canary; remote base and PR #241 untouched; M0-T136 remains awaiting_gate). No VIOLATED or UNVERIFIABLE rows. The four discrepancies above are citation/comment-level and do not affect any requirement's substance.

---

Orchestrator/verifier addendum (not part of the verbatim return): two further
citation-level notes carried into the verification rows — (a) the evidence map's
R528 wording "cluster-close records under project-control/reports/M0-T136-gates/"
is inaccurate (git history shows only B0 + final-freeze records were ever
committed there; the durable halves of R528 hold); (b) producer-report s1 and
the G2 self-check abbreviate the frozen tree as `0babc4691...` while the true
tree is `0babc469a07fc9109e5f7ce18ea73bf932952801` (all 17 final-freeze machine
records carry the full correct value; the raw records win, R590/R591).
