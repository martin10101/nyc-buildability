<!-- Saved by the orchestrator from the reviewer's hand-back; the read-only reviewer could not write files. -->
=== FULL REPORT: DCV M0-T173 ===
Independent directive-compliance verification — ledger task M0-T173 (D-091 TW3: Linux resource wiring; PR #309). Read-only; producer = backend-engineer, I am the independent directive-compliance-verifier (producer ≠ verifier).

HEAD CONFIRMED: worktree /root/project/w-M0-T173 at ec8718e1c7fa0bf1f2160dbab4ba66614238741c on task/M0-T173-linux-resource-wiring; `git status` clean. Material producer commit 7d5ea246 = exactly 3 files (resource_sampling.py, cli.py, new test). Claim seam 12364237.

CONTENT IDENTITY (reproduced): `_task_git_identity(M0-T173)` at live HEAD ec8718e1 = 626861666f4e0ade48a47d4e251e7e0a4adba002e9b93f54b8741c8d2ff10c2f — EXACTLY equals content_manifest_sha256 in the G2/G3/G4 records. Allowed-path files are byte-stable between reviewed_sha 098be433 and HEAD (`git diff --stat` empty); the only commits 098be433..ec8718e1 are gate JSONs, reports, state.json, task file (orchestrator-authored, non-material). Standard byte-stable-identity pattern. Verified.

--- REQUIREMENTS (this task's share only: R001, R007) ---

D-091-R001 (move loop to Linux cloud — wire 70% ceiling + /proc/meminfo gauge into the running loop, Windows unchanged): SATISFIED.
 - Ceiling: resource_sampling.py `posix_memory_ceiling_bytes(configured)` returns None off-POSIX, on POSIX `resolve_memory_ceiling_bytes(MemTotal)` = min(int(0.70*MemTotal), configured) (fraction MEMORY_PAUSE_FRACTION=0.70, resource_sampling.py:159/254-260). Wired at cli.py _run_loop: `_mem_ceiling = posix_memory_ceiling_bytes(config.limits.max_memory_bytes)` → `dataclasses.replace(config.limits, max_memory_bytes=_mem_ceiling)` → `CircuitBreakers(_limits)` (cli.py +diff, lines ~2753-2759). min() → a configured ceiling can only TIGHTEN. Verified in diff.
 - Gauge: `build_resource_sampler` wires `partial(linux_memory_gauge_sample, reader)` on POSIX, None off-POSIX; `ResourceSampler.sample()` substitutes the live reading for GAUGE_MEMORY_BYTES only when a gauge is wired. cli.py swaps `ResourceSampler(...)`→`build_resource_sampler(...)` (same kwargs). Verified in diff.
 - Into the RUNNING loop: _run_loop is the sole loop-build site; the other CircuitBreakers() (cli.py doctor) has no sampler. loop.py/circuit_breakers.py/run_budget.py UNTOUCHED across the whole branch (`git diff --name-only` empty). Verified.
 - Fail-closed: launch unreadable/missing/implausible /proc/meminfo → posix_memory_ceiling_bytes raises → no launch; runtime unreadable gauge → GaugeSample(known=False, structural=False) → loop pauses. Verified by tests.
 - Windows unchanged: off-POSIX None ceiling kept + no gauge attached (memory stays structural-unknown). Deterministic off-POSIX branches proven locally (RegressionTests + non_posix tests green). NOTE: authoritative whole-supervisor-glob Windows regression = CI supervisor-bridge (windows-latest), still PENDING — see Blocking B1.
 - REPRODUCED: `/root/project/lanes-runtime/venv/bin/python -m pytest -q tools/test_agent_supervisor_linux_gauge.py` → 15 passed, EXIT 0. Tests drive the REAL sampler (build_resource_sampler), REAL loop gate (lp.SupervisedLoop._check_resources) and REAL breaker (CircuitBreakers); paired over/under-ceiling tests isolate the trip to memory; mutation-sensitive.

D-091-R007 (reviewed and certified before use): SATISFIED.
 - Reviewed: G0 PASS (administrative, contract head), G2 PASS (orchestrator self-check), G3 PASS (code-reviewer, independent), G4 PASS (ci-evidence-verifier, independent). All of G2/G3/G4 reviewed_sha=098be433, content_manifest=626861...  consistent and == live identity. Verified.
 - Certified-before-use / gated: no loop started or commissioned — no systemd/runbook/start-path file touched; `source_binding.json` (controller manifest binding) UNTOUCHED; controller-manifest recertification after this cli.py edit is explicitly DEFERRED to M0-T174 (stated in producer report, evidence map, G2, G3 N2, G4 note B). No owner-typed step taken. Verified.

--- GATE RECORDS ---
 - Reviewer independence: producer backend-engineer ≠ any reviewer (orchestrator / code-reviewer / ci-evidence-verifier). Verified.
 - reviewed_sha + content_manifest_sha256 consistent across G2/G3/G4 and match live identity (above). Verified.
 - Reviewer class per gate matches packet reviewer_agents + plan TW3 (code-reviewer = correctness/G3; ci-evidence-verifier = tests/evidence/G4). Verified.

--- EVIDENCE MAP (M0-T173-evidence-map.json) — LITERALLY TRUE ---
 Every claim checked against diff/tests: ceiling resolution, build_resource_sampler wiring, unreadable-meminfo-refuses-launch, runtime outage-pauses, Windows no-change, "linux_gauge 15 passed" (reproduced), loop/circuit_breakers/run_budget untouched (verified), R007 gated/no-loop/M0-T174 deferral. No false statement found.

--- G2 HONESTY CHECK ---
The producer report claimed the whole model_chain file was "OOM-killed (signal 9)". G2 HONESTLY corrects it: server memory log never exceeded 16%, so OOM is unsupported; G3/G4 give the plausible non-OOM cause (process-group SIGKILL in real-subprocess classes) and the 5 CrashResumeTests failures were independently proven PRE-EXISTING at claim seam 12364237 (G4 re-ran a scratch checkout). Honest; the pre-existing conclusion rests on independent evidence, not the OOM narrative.

--- SCOPE ---
Material commit 7d5ea246 touches only the 4 allowed_paths' code (3 code files); no forbidden path (project-control/.claude/.github/services/apps, loop.py, circuit_breakers.py, run_budget.py, source_binding.json, other D-091 tasks all untouched). Verified.

--- HARNESS / CI ---
 - `validate_directive_compliance.py --check` → EXIT 0 (direct exit code, no pipe). 
 - `test_project_control.py` → all 23 groups OK, EXIT 0.
 - `gh pr checks 309`: 19 green incl control-plane (PASS, 5m20s) + modularity (PASS) + api/web/dep-security/model-routing/code-graph/contracts. PENDING: supervisor-bridge (windows-latest) and web-e2e. mergeable UNKNOWN (merge ref not yet computed).

--- PROHIBITED-ACTION EVIDENCE ---
Nothing merged/accepted/dispatched/deployed/installed/purchased/closed: task status=awaiting_gate (95%); PR #309 OPEN; no codex install, no loop start, no owner credential. B-026 still OPEN (not this task's requirement — R004 belongs to D-091-BOOTSTRAP) and does NOT name any M0-T17x task, so it will not trip the accept blocker-scan.

=== VERDICT: PASS (per requirement) with one blocking-for-accept condition ===
R001 (share): PASS. R007 (share): PASS.

BLOCKING ITEMS (must clear before the orchestrator accepts):
 B1. CI supervisor-bridge (windows-latest) AND web-e2e are PENDING at head ec8718e1. supervisor-bridge is the AUTHORITATIVE proof of the R001 "Windows byte-identical" constraint (whole supervisor glob on windows-latest); local reasoning does not substitute (CODING_RULES). Accept only after both conclude GREEN at the accept head. (Matches G4 note A.)

NON-BLOCKING NOTES:
 N1. (carried from G3 N1 / G2) A launch-time unreadable/implausible /proc/meminfo surfaces as a raw OSError/KeyError/ValueError rather than a typed LoopError (not in the cli.py except-guard). Still fail-closed (no dispatch); wrap as LoopError in a future TW task. Not required by the packet scenarios.
 N2. Controller-manifest recertification is correctly deferred to M0-T174 (TW4); source_binding.json untouched here.

RESTAMP PRE-AUTHORIZATION: this PASS carries UNCHANGED to a later accept-seam head H iff ALL hold:
 (a) `_task_git_identity` for M0-T173 at H == 626861666f4e0ade48a47d4e251e7e0a4adba002e9b93f54b8741c8d2ff10c2f (the G3 record);
 (b) commits ec8718e1..H are ONLY (i) a merge of origin/candidate/D-024-mrl-option-b with any disjoint peer commits it brings, (ii) state.json resolved by meaning, (iii) my report saved verbatim, (iv) the M0-T173 verification.json row filled;
 (c) `validate_directive_compliance.py --check` EXIT 0 at H;
 (d) B1 cleared: supervisor-bridge (windows-latest) + web-e2e GREEN at H.
DISJOINT-PEER TOLERANCE: I accept any disjoint peer commits from the merge that do NOT modify M0-T173's four allowed_paths (resource_sampling.py, cli.py, test_agent_supervisor_linux_gauge.py, M0-T173-producer-report.md). Any byte change to those four voids the restamp and requires re-review — predicate (a) enforces this mechanically.
=== END REPORT ===
